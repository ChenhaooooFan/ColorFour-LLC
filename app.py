import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

try:
    import streamlit as st
except ModuleNotFoundError:
    raise ModuleNotFoundError("Streamlit is not installed. Please install it using 'pip install streamlit' before running this application.")

# ========== 页面设置 ==========
st.set_page_config(
    page_title="NailVesta Weekly Analysis Tool",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ========== 插入 Logo + 多图展示 ==========
st.markdown("""
    <style>
    .main {
        background-color: #fafafa;
    }
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        padding-left: 3rem;
        padding-right: 3rem;
    }
    h1, h2, h3 {
        color: #ff69b4;
    }
    .stButton > button {
        background-color: #ff69b4;
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        font-weight: bold;
        border-radius: 0.5rem;
    }
    .stDownloadButton > button {
        background-color: #1f77b4;
        color: white;
        font-weight: bold;
        border-radius: 0.5rem;
        padding: 0.4rem 1rem;
    }
    </style>
""", unsafe_allow_html=True)

st.image("/mnt/data/Screenshot 2025-04-24 at 12.37.02 PM.png", width=280)

st.title("💅 NailVesta Weekly Analysis Tool")
st.caption("Empowering beautiful nails with smart data 💖")

# ========== 上传文件 ==========
st.sidebar.header("📤 上传数据文件")
this_week_file = st.sidebar.file_uploader("上传本周数据", type="csv", key="this")
last_week_file = st.sidebar.file_uploader("上传上周数据", type="csv", key="last")
inventory_file = st.sidebar.file_uploader("上传在仓在途库存表", type="csv", key="inventory")

# ========== 数据清洗函数 ==========
def clean_variation(df):
    df = df.dropna(subset=['Variation'])
    df['Variation Name'] = df['Variation'].astype(str).str.replace("’", "'").str.rsplit(',', n=1).str[0].str.strip()
    df['Variation Name'] = df['Variation Name'].str.replace(r'\s+', ' ', regex=True).str.lower().str.title()
    return df

# ========== 绘图函数 ==========
def plot_bar(data, title, xlabel, ylabel):
    fig, ax = plt.subplots(figsize=(10, len(data) * 0.5 + 1))
    sns.barplot(x=data.values, y=data.index, ax=ax, palette='pastel')
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title, fontsize=14, fontweight='bold', color='#e75480')
    for i, v in enumerate(data.values):
        ax.text(v, i, f'{v:.2f}' if isinstance(v, float) else str(v), va='center', ha='left')
    st.pyplot(fig)

# ========== 展示所有图像示意图 ==========
with st.expander("🖼 查看品牌图片"):
    st.image([
        "/mnt/data/Screenshot 2025-04-24 at 12.37.02 PM.png",
        "/mnt/data/Screenshot 2025-04-24 at 12.18.02 PM.png",
        "/mnt/data/Screenshot 2025-04-24 at 12.20.14 PM.png",
        "/mnt/data/Screenshot 2025-04-24 at 12.32.31 PM.png"
    ], width=280, caption=["Logo", "上传操作界面", "仓库首页", "上传提示样式预览"])
