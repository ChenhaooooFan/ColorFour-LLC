import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import datetime
import zipfile
import io
import os

# ========== 页面设置 ==========
st.set_page_config(page_title="NailVesta Weekly Analysis Tool！", layout="wide")
st.title("NailVesta Weekly Analysis Tool")
st.caption("Empowering beautiful nails with smart data 💖")

# ========== 粉色美学风格 ==========
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap');
    html, body, [class*="css"]  {
        font-family: 'Roboto', sans-serif;
        background-color: #f9f7fb;
        color: #111111;
    }
    .main {
        background-color: #f9f7fb;
        padding: 2rem;
    }
    h1, h2, h3 {
        color: #e91e63;
        font-weight: 700;
        text-shadow: 0 1px 2px rgba(0,0,0,0.05);
    }
    .stButton > button {
        background: linear-gradient(to right, #f06292, #ec407a);
        color: white;
        font-weight: bold;
        border: 2px solid transparent;
        border-radius: 12px;
        padding: 0.6rem 1.2rem;
        box-shadow: 0 4px 10px rgba(233,30,99,0.3);
        transition: all 0.3s ease-in-out;
    }
    .stButton > button:hover {
        background: linear-gradient(to right, #ec407a, #f06292);
        transform: scale(1.03);
    }
    .stDownloadButton > button {
        background: linear-gradient(to right, #ba68c8, #7b1fa2);
        color: white;
        font-weight: bold;
        border-radius: 10px;
        padding: 0.5rem 1.2rem;
    }
    .stSidebar > div:first-child {
        background-color: #ffe3f2;
        padding: 1.2rem;
        border-radius: 1rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    .stDataFrame th {
        background-color: #fce4ec;
        color: #c2185b;
    }
    .stDataFrame td {
        background-color: #fff0f5;
        color: #333;
    }
    .stMarkdown {
        background-color: white;
        border-radius: 1rem;
        padding: 1rem 1.5rem;
        box-shadow: 0 2px 10px rgba(0,0,0,0.03);
        margin-bottom: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

# ========== 文件上传 ==========
this_week_file = st.sidebar.file_uploader("📁 上传本周数据", type="csv")
last_week_file = st.sidebar.file_uploader("📁 上传上周数据", type="csv")
inventory_file = st.sidebar.file_uploader("📁 上传库存表", type="csv")

# ========== 主逻辑 ==========
if st.button("🚀 点击生成分析报表") and this_week_file and last_week_file:
    df_this = pd.read_csv(this_week_file)
    df_last = pd.read_csv(last_week_file)

    def clean_variation(df):
        df = df.dropna(subset=['Variation'])
        df['Variation Name'] = (
            df['Variation'].astype(str)
            .str.replace("’", "'")
            .str.rsplit(',', n=1).str[0]
            .str.strip()
            .str.replace(r'\s+', ' ', regex=True)
            .str.lower()
            .str.title()
        )
        return df

    df_this = clean_variation(df_this)
    df_last = clean_variation(df_last)

    df_this['SKU Unit Original Price'] = pd.to_numeric(df_this['SKU Unit Original Price'], errors='coerce').fillna(0)
    df_last['SKU Unit Original Price'] = pd.to_numeric(df_last['SKU Unit Original Price'], errors='coerce').fillna(0)
    sold_this = df_this[df_this['SKU Unit Original Price'] > 0]['Variation Name'].value_counts()
    zero_price = df_this[df_this['SKU Unit Original Price'] == 0]['Variation Name'].value_counts()
    sold_last = df_last[df_last['SKU Unit Original Price'] > 0]['Variation Name'].value_counts()
    total_count = sold_this.add(zero_price, fill_value=0)

    summary_df = pd.DataFrame({
        'Sold Count': sold_this,
        'Zero Price Count': zero_price,
        'Total Count': total_count,
        'Last Week Sold Count': sold_last
    }).fillna(0).astype(int)

    summary_df['Zero Price Percentage'] = (summary_df['Zero Price Count'] / summary_df['Total Count'].replace(0, 1)) * 100
    summary_df['Growth Rate'] = (
        (summary_df['Sold Count'] - summary_df['Last Week Sold Count']) /
        summary_df['Last Week Sold Count'].replace(0, 1)
    ) * 100
    summary_df = summary_df.sort_values(by='Total Count', ascending=False)

    st.subheader("📦 补货建议表")
    production_days = 6
    shipping_days = 12
    safety_days = 12
    total_days = production_days + shipping_days + safety_days
    summary_df['Daily Avg'] = summary_df['Total Count'] / 7
    summary_df['Growth Multiplier'] = 1 + summary_df['Growth Rate'] / 100
    overall_growth = 1 + summary_df['Growth Rate'].mean() / 100
    summary_df.loc[summary_df['Growth Multiplier'] > 1.8, 'Growth Multiplier'] = overall_growth
    summary_df['Restock Qty'] = (summary_df['Daily Avg'] * total_days * summary_df['Growth Multiplier']).round().astype(int)
    summary_df['未来三周赠送量'] = (summary_df['Zero Price Count'] / 7 * 21).round().astype(int)
    summary_df['总补货需求'] = summary_df['Restock Qty'] + summary_df['未来三周赠送量']

    if inventory_file:
        inventory_df = pd.read_csv(inventory_file)
        inventory_df = inventory_df.rename(columns={
            'Name': 'Variation Name',
            'In_stock': 'In Stock',
            'On_the_way': 'On The Way'
        })
        inventory_df['库存数量'] = inventory_df['In Stock'].fillna(0) + inventory_df['On The Way'].fillna(0)

        # 从 Seller SKU 提取 Size
        inventory_df['Size'] = inventory_df['Seller SKU'].str.extract(r'-(S|M|L)$')
        summary_df = summary_df.reset_index().rename(columns={'index': 'Variation Name'})
        if 'Seller SKU' in df_this.columns:
            summary_df['Seller SKU'] = df_this['Seller SKU']
            summary_df['Size'] = summary_df['Seller SKU'].str.extract(r'-(S|M|L)$')
        else:
            summary_df['Size'] = summary_df['Variation Name'].str.extract(r'(S|M|L)$')

        stock_by_size = inventory_df.groupby('Size')['库存数量'].sum().reindex(['S', 'M', 'L']).fillna(0)
        demand_by_size = summary_df.groupby('Size')['总补货需求'].sum().reindex(['S', 'M', 'L']).fillna(0)

        S0, M0, L0 = stock_by_size['S'], stock_by_size['M'], stock_by_size['L']
        total_demand = demand_by_size.sum()

        x = (total_demand + M0 + L0 - 1.5 * S0) / 2.5
        y = x + S0 - M0
        z = (x + S0) / 2 - L0

        x = max(round(x), 0)
        y = max(round(y), 0)
        z = max(round(z), 0)

        balanced_result = pd.DataFrame({
            '当前库存': [S0, M0, L0],
            '原始需求': demand_by_size,
            '建议补货量': [x, y, z],
            '补完后库存': [S0 + x, M0 + y, L0 + z],
        }, index=['S', 'M', 'L'])

        balanced_result['补完后比例'] = (
            balanced_result['补完后库存'] /
            balanced_result['补完后库存'].sum()
        ).apply(lambda r: f"{r:.1%}")

        st.subheader("🧵 调整后补货建议（目标比例 S:M:L = 2:2:1）")
        st.dataframe(balanced_result)

        today = datetime.date.today().strftime("%Y-%m-%d")
        restock_csv = summary_df.to_csv(index=False).encode('utf-8-sig')
        balanced_csv = balanced_result.to_csv().encode('utf-8-sig')

        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as zipf:
            zipf.writestr(f"restock_summary_{today}.csv", restock_csv)
            zipf.writestr(f"balanced_size_restock.csv", balanced_csv)
        zip_buffer.seek(0)

        st.download_button("📦 下载全部补货数据（ZIP 包）", data=zip_buffer, file_name="NailVesta_Restock_Report.zip", mime="application/zip")
