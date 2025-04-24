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

# ========== 插入 Logo ==========
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

st.image("https://raw.githubusercontent.com/ChenhaooooFan/ColorFour-LLC/main/logo.png", width=280)
st.title("💅 NailVesta Weekly Analysis Tool")
st.caption("Empowering beautiful nails with smart data 💖")

# 你的完整逻辑代码可以插入这里...
# （为简洁这里只保留头部结构）

