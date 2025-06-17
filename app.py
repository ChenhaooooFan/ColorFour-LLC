import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

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

# ========== 上传 ==========
st.sidebar.markdown("### 📁 数据上传")
this_week_file = st.sidebar.file_uploader("上传本周数据", type="csv")
last_week_file = st.sidebar.file_uploader("上传上周数据", type="csv")
inventory_file = st.sidebar.file_uploader("上传库存表", type="csv")

st.sidebar.markdown("### ⏱️ 补货时间设置")
production_days = st.sidebar.number_input("生产周期（天）", min_value=0, max_value=60, value=6, step=1)
shipping_days = st.sidebar.number_input("运输周期（天）", min_value=0, max_value=60, value=12, step=1)
safety_days = st.sidebar.number_input("安全库存天数", min_value=0, max_value=60, value=12, step=1)

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

    df_this['Size'] = df_this['Variation'].astype(str).str.rsplit(',', n=1).str[1].str.strip()

    # Calculate Zero Price Count average and future giveaways
    zero_price = df_this[df_this['SKU Unit Original Price'] == 0]['Variation Name'].value_counts()
    daily_zero_price = zero_price / 7
    future_gift_qty = (daily_zero_price * 21).round().astype(int)

    summary_df = pd.DataFrame({
        'Sold Count': df_this[df_this['SKU Unit Original Price'] > 0]['Variation Name'].value_counts(),
        'Zero Price Count': zero_price,
        'Last Week Sold Count': df_last[df_last['SKU Unit Original Price'] > 0]['Variation Name'].value_counts()
    }).fillna(0).astype(int)

    summary_df['Total Count'] = summary_df['Sold Count'] + summary_df['Zero Price Count']
    summary_df['Zero Price Percentage'] = (summary_df['Zero Price Count'] / summary_df['Total Count'].replace(0, 1)) * 100
    summary_df['Growth Rate'] = ((summary_df['Sold Count'] - summary_df['Last Week Sold Count']) / summary_df['Last Week Sold Count'].replace(0, 1)) * 100
    summary_df['Daily Avg'] = summary_df['Total Count'] / 7
    summary_df['Growth Multiplier'] = 1 + summary_df['Growth Rate'] / 100
    summary_df.loc[summary_df['Growth Multiplier'] > 1.8, 'Growth Multiplier'] = 1 + summary_df['Growth Rate'].mean() / 100

    total_days = production_days + shipping_days + safety_days
    summary_df['Restock Qty'] = (summary_df['Daily Avg'] * total_days * summary_df['Growth Multiplier']).round().astype(int)

    # 加入未来赠送量
    summary_df['未来赠送量'] = summary_df.index.map(future_gift_qty).fillna(0).astype(int)
    summary_df['补货总量含赠送'] = summary_df['Restock Qty'] + summary_df['未来赠送量']

    if inventory_file:
        inventory_df = pd.read_csv(inventory_file)
        inventory_df = inventory_df.rename(columns={
            'Name': 'Variation Name',
            'In_stock': 'In Stock',
            'On_the_way': 'On The Way'
        })
        inventory_df['库存数量'] = inventory_df['In Stock'].fillna(0) + inventory_df['On The Way'].fillna(0)
        inventory_df['Variation Name'] = inventory_df['Variation Name'].astype(str).str.replace("’", "'").str.replace(r'\s+', ' ', regex=True).str.strip().str.lower().str.title()
        stock_map = inventory_df.groupby('Variation Name')['库存数量'].sum()
        summary_df['当前库存'] = summary_df.index.map(stock_map).fillna(0).astype(int)
        summary_df['最终补货量'] = (summary_df['补货总量含赠送'] - summary_df['当前库存']).clip(lower=0)

        # 计算每个款式 S/M/L 分布 + 安全库存预警
        st.subheader("📐 按尺码比例分配补货量（2:2:1）")
        size_inventory_df = df_this[df_this['Variation Name'].isin(summary_df.index)]
        size_inventory_df['Size'] = size_inventory_df['Variation'].astype(str).str.rsplit(',', n=1).str[1].str.strip()
        size_stock_map = size_inventory_df.groupby(['Variation Name', 'Size']).size().unstack(fill_value=0)
        size_stock_map['总库存'] = size_stock_map.sum(axis=1)
        size_stock_map['总补货量'] = summary_df['最终补货量']

        def allocate(size_row):
            current_s = size_row.get('S', 0)
            current_m = size_row.get('M', 0)
            current_l = size_row.get('L', 0)
            total_current = current_s + current_m + current_l
            total_future = total_current + size_row['总补货量']
            s_target = round(total_future * 2 / 5)
            m_target = round(total_future * 2 / 5)
            l_target = total_future - s_target - m_target
            warn = []
            if current_s + (s_target - current_s) < safety_days:
                warn.append('S')
            if current_m + (m_target - current_m) < safety_days:
                warn.append('M')
            if current_l + (l_target - current_l) < safety_days:
                warn.append('L')
            return pd.Series({
                '补S': max(s_target - current_s, 0),
                '补M': max(m_target - current_m, 0),
                '补L': max(l_target - current_l, 0),
                '⚠️库存预警': ', '.join(warn) if warn else ''
            })

        allocation_df = size_stock_map.apply(allocate, axis=1)
        result_with_sizes = pd.concat([summary_df, allocation_df], axis=1)

        st.dataframe(result_with_sizes[["最终补货量", "未来赠送量", "补S", "补M", "补L", "⚠️库存预警"]])
        st.download_button("📥 下载尺码补货建议", result_with_sizes.to_csv().encode('utf-8-sig'), "size_restock_summary.csv", "text/csv")

    restock_table = summary_df[["Sold Count", "Last Week Sold Count", "Growth Rate", "Daily Avg", "Growth Multiplier", "Restock Qty", "未来赠送量", "补货总量含赠送", "当前库存", "最终补货量"]]
    st.dataframe(restock_table)
    st.download_button("📥 下载补货建议", restock_table.to_csv().encode('utf-8-sig'), "restock_summary.csv", "text/csv")
