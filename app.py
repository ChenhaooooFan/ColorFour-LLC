
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

# ========== 页面设置 ==========
st.set_page_config(
    page_title="NailVesta Weekly Analysis Tool",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ========== 自定义样式 ==========
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap');

    html, body, [class*="css"]  {
        font-family: 'Roboto', sans-serif;
    }
    .main {
        background-color: #f9f7fb;
        padding: 2rem;
    }
    h1, h2, h3 {
        color: #e91e63;
        font-weight: 700;
    }
    .stButton > button {
        background-color: #e91e63;
        color: white;
        font-weight: bold;
        border: none;
        border-radius: 0.5rem;
        padding: 0.6rem 1.2rem;
    }
    .stDownloadButton > button {
        background-color: #7b1fa2;
        color: white;
        font-weight: bold;
        border-radius: 0.5rem;
        padding: 0.5rem 1.2rem;
    }
    .stDataFrame th, .stDataFrame td {
        font-size: 14px;
    }
    .stSidebar > div:first-child {
        background-color: #ffe3f2;
        padding: 1rem;
        border-radius: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

# ========== 插入 Logo + 标题 ==========
st.image("https://raw.githubusercontent.com/ChenhaooooFan/ColorFour-LLC/main/logo.png", width=220)
st.title("💅 NailVesta Weekly Analysis Tool")
st.caption("Empowering beautiful nails with smart data 💖")

# ========== 文件上传 ==========
st.sidebar.header("📤 上传数据文件")
this_week_file = st.sidebar.file_uploader("📁 上传本周数据 (WEEK_16.csv)", type="csv")
last_week_file = st.sidebar.file_uploader("📁 上传上周数据 (WEEK_15.csv)", type="csv")
inventory_file = st.sidebar.file_uploader("📁 上传库存数据 (库存.csv)", type="csv")

# ========== 占位符 ========== 
st.info("✨ 请在侧边栏上传所有文件后，即可生成分析报表。页面样式已升级，现代化更专业 💼")

# ========== 销售增长图函数 ==========
def plot_growth_and_free_ratio(summary_df):
    st.subheader("📈 Week-over-Week Sales + Free Sample Analysis")
    summary_df = summary_df.sort_values(by='Total Count', ascending=False)
    fig, ax = plt.subplots(figsize=(16, len(summary_df) * 0.4 + 3))
    ax.barh(summary_df.index, summary_df['Sold Count'], color='blue', label='Sold')
    ax.barh(summary_df.index, summary_df['Zero Price Count'],
            left=summary_df['Sold Count'], color='red', alpha=0.6, label='Free')

    for index, (name, sold, zero, total, percentage, growth) in enumerate(zip(
        summary_df.index,
        summary_df['Sold Count'],
        summary_df['Zero Price Count'],
        summary_df['Total Count'],
        summary_df['Zero Price Percentage'],
        summary_df['Growth Rate']
    )):
        if growth > 0:
            growth_text = f' ↑ {growth:.1f}%'
            color = '#2ecc71'
        elif growth < 0:
            growth_text = f' ↓ {abs(growth):.1f}%'
            color = '#e74c3c'
        else:
            growth_text = ' → 0.0%'
            color = 'gray'

        ax.text(-5, index, f"{name}{growth_text}", va='center', ha='right',
                 fontsize=10, color=color, fontweight='bold')

        free_text = f'{zero}/{total} ({(zero / total * 100):.1f}%)' if total > 0 else f'{zero}/0 (0.0%)'
        ax.text(sold + zero + 2, index, free_text, va='center', ha='left',
                 color='red' if percentage > 65 else 'black',
                 fontsize=10,
                 fontweight='bold' if percentage > 65 else 'normal')

    ax.set_xlabel('Count')
    ax.set_title('Week 16 vs Week 15: Sales + Growth + Free Sample Rate', fontsize=14, fontweight='bold')
    ax.legend()
    ax.set_yticks([])
    ax.invert_yaxis()
    st.pyplot(fig)
