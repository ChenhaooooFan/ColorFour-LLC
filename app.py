import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

# ====== Streamlit Configuration ======
st.set_page_config(page_title="NailVesta Weekly Analysis Tool", layout="wide")
st.title("NailVesta Weekly Analysis Tool")
st.caption("Empowering beautiful nails with smart data 💖")

# ====== Custom Styles ======
def load_styles():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap');
    html, body, [class*="css"] {
        font-family: 'Roboto', sans-serif;
        background-color: #f9f7fb;
        color: #111;
    }
    h1, h2, h3 { color: #e91e63; font-weight: 700; }
    .stButton > button { background: linear-gradient(to right, #f06292, #ec407a); color: #fff; border-radius: 12px; }
    .stButton > button:hover { transform: scale(1.03); }
    .stSidebar { background-color: #ffe3f2; padding: 1rem; border-radius: 1rem; }
    .stDataFrame th { background-color: #fce4ec; color: #c2185b; }
    .stDataFrame td { background-color: #fff0f5; color: #333; }
    </style>
    """, unsafe_allow_html=True)

load_styles()

# ====== Cached Data Loaders ======
@st.cache_data
def load_csv(file):
    return pd.read_csv(file)

@st.cache_data
def clean_variation(df: pd.DataFrame) -> pd.DataFrame:
    df = df.dropna(subset=['Variation'])
    df['Variation Name'] = (
        df['Variation'].astype(str)
        .str.replace("’", "'", regex=False)
        .str.replace(r'\s+', ' ', regex=True)
        .str.rsplit(',', n=1).str[0]
        .str.strip().str.title()
    )
    return df

# ====== Sidebar Uploads ======
this_week_file = st.sidebar.file_uploader("📁 Upload This Week Data", type="csv")
last_week_file = st.sidebar.file_uploader("📁 Upload Last Week Data", type="csv")
inventory_file = st.sidebar.file_uploader("📁 Upload Inventory Data", type="csv")

if st.sidebar.button("🚀 Generate Report"):
    if not (this_week_file and last_week_file):
        st.sidebar.error("Please upload both CSV files.")
    else:
        df_this = clean_variation(load_csv(this_week_file))
        df_last = clean_variation(load_csv(last_week_file))

        # Helper: plot bar chart
        def plot_bar(counts, title, xlabel, ylabel):
            fig, ax = plt.subplots(figsize=(10, 4))
            ax.barh(counts.index, counts.values)
            ax.set_title(title)
            ax.set_xlabel(xlabel)
            ax.set_ylabel(ylabel)
            for i, v in enumerate(counts.values):
                ax.text(v + max(counts.values)*0.01, i, f"{v:.1f}" if v < 100 else str(int(v)), va='center')
            st.pyplot(fig)

        # ====== Variation Frequency ======
        variation_counts = df_this['Variation Name'].value_counts()
        plot_bar(variation_counts, 'Variation Frequency', 'Count', 'Variation')

        # ====== Size Distribution ======
        df_this['Size'] = df_this['Variation'].astype(str).str.rsplit(',', n=1).str[1].str.strip()
        size_pct = df_this['Size'].value_counts(normalize=True)*100
        plot_bar(size_pct, 'Size Frequency (%)', 'Percentage', 'Size')

        # ====== Shape Distribution ======
        shape_map = {'F': 'Rectangle', 'X': 'Almond', 'J': 'Pointed'}
        df_this['Shape'] = df_this['Seller SKU'].astype(str).str[2].map(shape_map)
        shape_pct = df_this['Shape'].value_counts(normalize=True)*100
        plot_bar(shape_pct, 'Shape Frequency (%)', 'Percentage', 'Shape')

        # ====== Sales vs Free Samples ======
        for df in (df_this, df_last):
            df['SKU Price'] = pd.to_numeric(df['SKU Unit Original Price'], errors='coerce').fillna(0)
        sold_this = df_this[df_this['SKU Price'] > 0]['Variation Name'].value_counts()
        free_this = df_this[df_this['SKU Price'] == 0]['Variation Name'].value_counts()
        sold_last = df_last[df_last['SKU Price'] > 0]['Variation Name'].value_counts()

        summary = pd.DataFrame({
            'Sold': sold_this,
            'Free': free_this,
            'Prev Sold': sold_last
        }).fillna(0).astype(int)
        summary['Total'] = summary['Sold'] + summary['Free']
        summary['Free %'] = (summary['Free']/summary['Total']*100).round(1)
        summary['Growth %'] = ((summary['Sold'] - summary['Prev Sold'])/summary['Prev Sold'].replace(0,1)*100).round(1)
        summary = summary.sort_values('Total', ascending=False)

        st.subheader("Sales vs Free Sample Analysis")
        st.dataframe(summary)

        # ====== Restock Recommendation ======
        days = 6 + 12 + 12
        summary['Daily Avg'] = (summary['Total']/7).round(2)
        summary['Growth Factor'] = (1 + summary['Growth %']/100).clip(lower=1)
        summary['Restock Qty'] = (summary['Daily Avg'] * days * summary['Growth Factor']).round().astype(int)

        if inventory_file:
            inv = load_csv(inventory_file)
            inv['Variation Name'] = (inv['Name'].astype(str)
                                      .str.replace("’", "'", regex=False)
                                      .str.replace(r'\s+', ' ', regex=True)
                                      .str.title())
            inv['Stock'] = inv[['In_stock','On_the_way']].fillna(0).sum(axis=1)
            stock_map = inv.groupby('Variation Name')['Stock'].sum()
            summary['On Hand'] = summary.index.map(stock_map).fillna(0).astype(int)
            summary['To Restock'] = (summary['Restock Qty'] - summary['On Hand']).clip(lower=0).astype(int)

        st.subheader("📦 Restock Recommendations")
        st.dataframe(summary[['Daily Avg','Restock Qty','On Hand','To Restock']])
        st.download_button("📥 Download Restock CSV", summary.to_csv(index=True).encode('utf-8-sig'),"restock.csv","text/csv")
