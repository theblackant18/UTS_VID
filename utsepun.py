import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
import numpy as np

# ===============================
# ⚙️ KONFIGURASI DASAR
# ===============================
st.set_page_config(page_title="UTS VID - A", layout="wide")

# 🌌 CSS: Desain Transparan Futuristik
st.markdown("""
    <style>
        /* === Background utama === */
        .stApp {
            background: linear-gradient(135deg, rgba(14,17,23,0.95), rgba(0,0,0,0.9));
            color: #EAEAEA;
            font-family: 'Poppins', sans-serif;
        }

        h1, h2, h3, h4 {
            color: #00FFFF;
            font-weight: 700;
        }

        /* === Elemen transparan (Glassmorphism) === */
        div[data-baseweb="select"],
        .stTextInput > div > div > input,
        .stNumberInput > div > input,
        .stSlider > div,
        .stMultiSelect,
        .stRadio,
        .stTextInput {
            background: rgba(255,255,255,0.05) !important;
            backdrop-filter: blur(12px);
            border-radius: 12px;
            border: 1px solid rgba(255,255,255,0.15);
            color: #EAEAEA !important;
        }

        /* === Tombol toggle (radio dan select) === */
        .stRadio label, .stSelectbox label, .stMultiSelect label {
            color: #00FFFF !important;
            font-weight: 600;
        }

        /* === Tabs styling === */
        .stTabs [role="tablist"] button {
            color: #00FFFF;
            font-weight: 600;
            background: rgba(255,255,255,0.05);
            border-radius: 12px;
            margin-right: 4px;
        }
        .stTabs [role="tablist"] button[aria-selected="true"] {
            border-bottom: 3px solid #39FF14;
            color: #39FF14 !important;
            background: rgba(0,255,255,0.08);
        }

        /* === Sidebar transparan === */
        section[data-testid="stSidebar"] {
            background: rgba(20,20,20,0.5);
            backdrop-filter: blur(15px);
            border-right: 1px solid rgba(255,255,255,0.1);
        }

        /* === DataFrame dan plot transparan === */
        .stDataFrame, .plotly {
            background: rgba(0,0,0,0.2);
            border-radius: 12px;
        }

        /* === Metric text color === */
        [data-testid="stMetricValue"] {
            color: #39FF14;
            font-weight: bold;
        }

        /* === Slider track === */
        .stSlider > div > div > div {
            background: linear-gradient(90deg, #00FFFF, #39FF14) !important;
        }

    </style>
""", unsafe_allow_html=True)

# ===============================
# 🧠 JUDUL UTAMA
# ===============================
st.title("💫 UTS VID - A ")
st.caption("UTS Visualisasi & Interpretasi Data ")

# ===============================
# 📥 LOAD DATA OTOMATIS
# ===============================
@st.cache_data
def load_data():
    path = Path(__file__).parent / "Copy of finalProj_df - 2022.csv"
    df = pd.read_csv(path)

    df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")
    df = df.dropna(subset=["order_date"])
    df["year"] = df["order_date"].dt.year
    df["month"] = df["order_date"].dt.strftime("%b")
    df["period"] = df["order_date"].dt.to_period("M")

    df["revenue"] = df.get("after_discount", df.get("before_discount", 0))
    df["cogs"] = pd.to_numeric(df.get("cogs", 0), errors="coerce").fillna(0)
    df["profit"] = df["revenue"] - df["cogs"]
    df["qty_ordered"] = pd.to_numeric(df.get("qty_ordered", 0), errors="coerce").fillna(0).astype(int)

    if "region" not in df.columns:
        np.random.seed(42)
        df["region"] = np.random.choice(["Jakarta", "Jawa Barat", "Jawa Tengah", "Jawa Timur", "Bali"], len(df))

    return df

df = load_data()

# ===============================
# 🎛️ SIDEBAR FILTER TRANSPARAN
# ===============================
st.sidebar.header("⚙️ Filter Data")

years = sorted(df["year"].unique())
categories = sorted(df["category"].dropna().unique().tolist()) if "category" in df.columns else []

selected_year = st.sidebar.selectbox("📆 Pilih Tahun:", years, index=len(years)-1)
selected_cats = st.sidebar.multiselect("🏷️ Pilih Kategori Produk:", categories, default=categories)
min_profit, max_profit = st.sidebar.slider("💰 Rentang Profit:", 
                                           float(df["profit"].min()), 
                                           float(df["profit"].max()), 
                                           (0.0, float(df["profit"].max())), 
                                           step=10000.0)

filtered_df = df[df["year"] == selected_year]
if selected_cats:
    filtered_df = filtered_df[filtered_df["category"].isin(selected_cats)]
filtered_df = filtered_df[(filtered_df["profit"] >= min_profit) & (filtered_df["profit"] <= max_profit)]

# ===============================
# 🧭 NAVIGASI TAB UTAMA
# ===============================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📈 Tren Penjualan",
    "👥 Analisis Pelanggan",
    "🗺️ Distribusi Wilayah",
    "🏆 Produk Terlaris",
    "⚔️ Bandingkan Produk"
])

# === Fungsi agar chart transparan ===
def dark_chart(fig):
    fig.update_layout(
        template="plotly_dark",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#EAEAEA", family="Poppins"),
        title_font=dict(color="#00FFFF", size=18),
        margin=dict(t=60, l=40, r=40, b=40),
        hoverlabel=dict(bgcolor="#111", font_size=13)
    )
    return fig

# ===============================
# TAB 1 - TREN PENJUALAN
# ===============================
with tab1:
    st.header("📈 Tren Penjualan Bulanan")
    view_mode = st.radio("🔘 Mode Tampilan:", ["📊 Grafik", "📋 Tabel"], horizontal=True)

    monthly = filtered_df.groupby("month").agg(
        Revenue=("revenue", "sum"),
        Profit=("profit", "sum"),
        Orders=("id", "nunique")
    ).reset_index()

    if view_mode == "📊 Grafik":
        fig = px.line(monthly, x="month", y=["Revenue", "Profit"], markers=True,
                      color_discrete_sequence=["#00FFFF", "#39FF14"],
                      title="Tren Bulanan Revenue & Profit")
        st.plotly_chart(dark_chart(fig), use_container_width=True)
    else:
        st.dataframe(monthly.style.background_gradient(cmap="plasma"), height=350)

# ===============================
# TAB 2 - ANALISIS PELANGGAN
# ===============================
with tab2:
    st.header("👥 Segmentasi & Perilaku Pelanggan")

    cust = filtered_df.groupby("customer_id").agg(
        Revenue=("revenue", "sum"),
        Profit=("profit", "sum"),
        Orders=("id", "nunique")
    ).reset_index()
    cust["Segment"] = pd.cut(cust["Orders"], bins=[0, 1, 3, 10, 999],
                             labels=["Baru", "Aktif", "Loyal", "Super Loyal"])

    col1, col2 = st.columns(2)
    seg = cust["Segment"].value_counts().reset_index()
    seg.columns = ["Segment", "Jumlah"]

    with col1:
        fig_pie = px.pie(seg, values="Jumlah", names="Segment",
                         color_discrete_sequence=["#00FFFF", "#39FF14", "#FFD700", "#FF5733"],
                         title="Proporsi Segmen Pelanggan", hole=0.4)
        st.plotly_chart(dark_chart(fig_pie), use_container_width=True)

    with col2:
        cust["Profit_Pos"] = cust["Profit"].clip(lower=0)
        fig_scatter = px.scatter(
            cust, x="Orders", y="Revenue", size="Profit_Pos", color="Segment",
            title="Hubungan Orders vs Revenue per Pelanggan",
            color_discrete_sequence=px.colors.sequential.Plasma,
            hover_data=["Profit", "Segment"]
        )
        st.plotly_chart(dark_chart(fig_scatter), use_container_width=True)

# ===============================
# TAB 3 - DISTRIBUSI WILAYAH
# ===============================
with tab3:
    st.header("🗺️ Analisis Wilayah Penjualan")

    region = filtered_df.groupby("region").agg(
        Revenue=("revenue", "sum"),
        Profit=("profit", "sum")
    ).reset_index()

    fig_map = px.treemap(region, path=["region"], values="Revenue", color="Profit",
                         color_continuous_scale="RdYlGn", title="Distribusi Revenue per Wilayah")
    st.plotly_chart(dark_chart(fig_map), use_container_width=True)

# ===============================
# TAB 4 - PRODUK TERLARIS
# ===============================
with tab4:
    st.header("🏆 Top Produk Berdasarkan Revenue")

    search = st.text_input("🔍 Cari Produk:", "")
    prod = filtered_df.groupby("sku_name").agg(
        Category=("category", "first"),
        Revenue=("revenue", "sum"),
        Profit=("profit", "sum")
    ).reset_index().sort_values("Revenue", ascending=False)

    if search:
        prod = prod[prod["sku_name"].str.contains(search, case=False, na=False)]

    fig_bar = px.bar(prod.head(15), x="Revenue", y="sku_name", color="Profit",
                     orientation="h", text_auto=True, color_continuous_scale="Blues",
                     title="Top 15 Produk Berdasarkan Revenue")
    st.plotly_chart(dark_chart(fig_bar), use_container_width=True)

# ===============================
# TAB 5 - BANDINKAN PRODUK
# ===============================
with tab5:
    st.header("⚔️ Bandingkan Dua Produk")

    all_products = sorted(filtered_df["sku_name"].dropna().unique().tolist())
    p1 = st.selectbox("🅰️ Produk 1:", all_products)
    p2 = st.selectbox("🅱️ Produk 2:", all_products, index=1 if len(all_products) > 1 else 0)

    prod_trend = filtered_df[filtered_df["sku_name"].isin([p1, p2])]
    trend = prod_trend.groupby(["period", "sku_name"])["revenue"].sum().reset_index()
    trend["period"] = trend["period"].astype(str)

    fig_comp = px.line(trend, x="period", y="revenue", color="sku_name", markers=True,
                       title=f"Perbandingan Revenue: {p1} vs {p2}",
                       color_discrete_sequence=["#00FFFF", "#39FF14"])
    st.plotly_chart(dark_chart(fig_comp), use_container_width=True)
