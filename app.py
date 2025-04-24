import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

# ========== 页面设置 ==========
st.set_page_config(
    page_title="NailVesta Weekly Analysis Console",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ========== 高科技暗色风格样式 ==========
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    html, body, [class*="css"]  {
        font-family: 'Inter', sans-serif;
        background-color: #0f1117;
        color: #EDEDED;
    }
    .stApp {
        background: linear-gradient(145deg, #0f1117 0%, #1a1c23 100%);
        padding: 2rem;
    }
    h1, h2, h3 {
        color: #00FFC6 !important;
        font-weight: 700;
    }
    .stButton > button {
        background: linear-gradient(to right, #00FFC6, #0057FF);
        color: black;
        font-weight: 600;
        border: none;
        border-radius: 8px;
        padding: 0.6rem 1.4rem;
        transition: all 0.3s ease-in-out;
    }
    .stButton > button:hover {
        transform: scale(1.05);
    }
    .stDownloadButton > button {
        background: linear-gradient(to right, #6C63FF, #3F51B5);
        color: white;
        font-weight: bold;
        border-radius: 8px;
        padding: 0.5rem 1.2rem;
    }
    .stSidebar > div:first-child {
        background-color: #1f222c;
        border-radius: 1rem;
        padding: 1.2rem;
        color: #ccc;
    }
    .stDataFrame th {
        background-color: #272b36;
        color: #00ffc6;
    }
    .stDataFrame td {
        color: #ffffff;
        background-color: #121212;
    }
    </style>
""", unsafe_allow_html=True)

# ========== 页面标题 ==========
st.markdown("""<h1 style='font-size: 40px; margin-bottom: 0;'>🧠 NailVesta Analysis Console</h1>
<p style='color:#B0BEC5;'>Real-time intelligence for smart nail decisions ✨</p>""", unsafe_allow_html=True)