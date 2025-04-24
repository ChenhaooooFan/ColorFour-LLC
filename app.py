import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

try:
    import streamlit as st
except ModuleNotFoundError:
    raise ModuleNotFoundError("Streamlit is not installed. Please install it using 'pip install streamlit' before running this application.")

st.set_page_config(page_title="Nail Weekly Report", layout="wide")
st.title("💅 Nail Style Weekly Analysis Tool")

# ========== 上传文件 ========== 
this_week_file = st.file_uploader("📤 Upload This Week's CSV", type="csv", key="this")
last_week_file = st.file_uploader("📤 Upload Last Week's CSV", type="csv", key="last")
inventory_file = st.file_uploader("📤 Upload Inventory CSV", type="csv", key="inventory")

# ========== 数据清洗函数 ==========
def clean_variation(df):
    df = df.dropna(subset=['Variation'])
    df['Variation Name'] = df['Variation'].astype(str).str.replace("’", "'").str.rsplit(',', n=1).str[0].str.strip()
    df['Variation Name'] = df['Variation Name'].str.replace(r'\s+', ' ', regex=True).str.lower().str.title()
    return df

# ========== 绘图函数 ==========
def plot_bar(data, title, xlabel, ylabel):
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(x=data.values, y=data.index, ax=ax, palette='viridis')
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    for i, v in enumerate(data.values):
        ax.text(v, i, f'{v:.2f}' if isinstance(v, float) else str(v), va='center')
    st.pyplot(fig)

# ========== 主程序逻辑 ==========
if this_week_file and last_week_file and inventory_file:
    df_this = pd.read_csv(this_week_file, usecols=['Variation', 'Seller SKU', 'SKU Unit Original Price'])
    df_last = pd.read_csv(last_week_file, usecols=['Variation', 'SKU Unit Original Price'])
    df_this = clean_variation(df_this)
    df_last = clean_variation(df_last)
    df_this['SKU Unit Original Price'] = pd.to_numeric(df_this['SKU Unit Original Price'], errors='coerce').fillna(0)
    df_last['SKU Unit Original Price'] = pd.to_numeric(df_last['SKU Unit Original Price'], errors='coerce').fillna(0)

    sold_this = df_this[df_this['SKU Unit Original Price'] > 0]['Variation Name'].value_counts()
    zero_price = df_this[df_this['SKU Unit Original Price'] == 0]['Variation Name'].value_counts()
    sold_last = df_last[df_last['SKU Unit Original Price'] > 0]['Variation Name'].value_counts()
    total_count = sold_this.add(zero_price, fill_value=0)

    summary = pd.DataFrame({
        'Sold Count': sold_this,
        'Zero Price Count': zero_price,
        'Total Count': total_count,
        'Last Week Sold Count': sold_last
    }).fillna(0).astype(int)

    summary['Zero Price Percentage'] = (summary['Zero Price Count'] / summary['Total Count'].replace(0, 1)) * 100
    summary['Growth Rate'] = ((summary['Sold Count'] - summary['Last Week Sold Count']) / summary['Last Week Sold Count'].replace(0, 1)) * 100

    production_days = 7
    shipping_days = 14
    safety_days = 7
    total_days = production_days + shipping_days + safety_days

    summary['Daily Avg'] = summary['Total Count'] / 7
    summary['Growth Multiplier'] = 1 + summary['Growth Rate'] / 100
    overall_growth = 1 + summary['Growth Rate'].mean() / 100
    summary['Use Avg Growth'] = summary['Growth Multiplier'] > 1.8
    summary.loc[summary['Use Avg Growth'], 'Growth Multiplier'] = overall_growth
    summary['Restock Qty'] = (summary['Daily Avg'] * total_days * summary['Growth Multiplier']).round().astype(int)

    inventory_df = pd.read_csv(inventory_file)
    inventory_df = inventory_df.rename(columns={'Name': 'Variation Name', 'In_stock': 'In Stock', 'On_the_way': 'On The Way'})
    inventory_df['库存数量'] = inventory_df['In Stock'].fillna(0) + inventory_df['On The Way'].fillna(0)
    inventory_df['Variation Name'] = (
        inventory_df['Variation Name'].astype(str)
        .str.replace("’", "'")
        .str.replace(r'\s+', ' ', regex=True)
        .str.strip()
        .str.lower()
        .str.title()
    )
    stock_map = inventory_df.groupby('Variation Name')['库存数量'].sum()
    summary['当前库存'] = summary.index.map(stock_map).fillna(0).astype(int)
    summary['最终补货量'] = (summary['Restock Qty'] - summary['当前库存']).clip(lower=0)

    st.subheader("📊 Top Selling Variations")
    plot_bar(summary.sort_values(by='Total Count', ascending=False)['Total Count'].head(10),
             'Top 10 Variations by Total Count', 'Total Count', 'Variation')

    st.subheader("📦 Restock Suggestions")
    restock_table = summary[[
        'Sold Count', 'Last Week Sold Count', 'Growth Rate',
        'Daily Avg', 'Growth Multiplier', 'Restock Qty',
        '当前库存', '最终补货量'
    ]].rename(columns={
        'Sold Count': '本周销量',
        'Last Week Sold Count': '上周销量',
        'Growth Rate': '增长率(%)',
        'Daily Avg': '日均销量',
        'Growth Multiplier': '增长系数',
        'Restock Qty': '建议补货量'
    })

    st.dataframe(restock_table)

    st.download_button(
        label="💾 Download Restock Table as CSV",
        data=restock_table.to_csv(index=True).encode('utf-8-sig'),
        file_name='restock_summary.csv',
        mime='text/csv'
    )
