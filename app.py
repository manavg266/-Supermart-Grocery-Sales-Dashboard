
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

st.set_page_config(
    page_title="Sapphire IQ | Supermart Analytics",
    page_icon="💠",
    layout="wide",
    initial_sidebar_state="expanded",
)

DATA_PATH = Path(__file__).parent / "data" / "Supermart Grocery Sales - Retail Analytics Dataset.csv"

# -----------------------------
# Theme / UI
# -----------------------------
st.markdown("""
<style>
html, body, [class*="css"] { font-family: Arial, Helvetica, sans-serif; }
.stApp { background: #f7f7f7; }
.block-container { padding: 1.25rem 2.2rem 2.5rem 2.2rem; max-width: 1500px; }

section[data-testid="stSidebar"] {
    background: #1f2937;
    border-right: 1px solid #374151;
}
section[data-testid="stSidebar"] * { color: #f3f4f6 !important; }
section[data-testid="stSidebar"] .stRadio label {
    padding: .35rem .45rem; border-radius: 4px;
}
section[data-testid="stSidebar"] .stRadio label:hover { background: #374151; }

.hero {
    background: #ffffff;
    padding: 1.15rem 1.35rem;
    border: 1px solid #d9dde3;
    border-left: 5px solid #1f6f5b;
    border-radius: 5px;
    color: #20252b;
    margin-bottom: 1rem;
}
.hero h1 { margin: 0; font-size: 1.65rem; letter-spacing: -0.02em; }
.hero p { margin: .3rem 0 0; color: #68717c; font-size: .9rem; }

.section-title { font-size: 1rem; font-weight: 700; color: #252a30; margin: .7rem 0 .65rem; }
.muted { color: #737b85; font-size: .85rem; }

.kpi {
    background: #ffffff; border: 1px solid #d9dde3; border-radius: 5px;
    padding: .85rem .95rem; min-height: 105px;
    box-shadow: 0 1px 3px rgba(0,0,0,.04);
}
.kpi-label { color:#6b7280; font-size:.7rem; font-weight:700; text-transform:uppercase; letter-spacing:.05em; }
.kpi-value { color:#20252b; font-size:1.45rem; font-weight:700; margin-top:.35rem; }
.kpi-sub { color:#8a929c; font-size:.72rem; margin-top:.2rem; }

.card {
    background:#ffffff; border:1px solid #d9dde3; border-radius:5px;
    padding:.9rem; box-shadow:0 1px 3px rgba(0,0,0,.03);
}

div[data-testid="stMetric"] {
    background: #ffffff; border:1px solid #d9dde3; padding: .8rem;
    border-radius: 5px; box-shadow:none;
}
button[kind="secondary"] { border-radius: 4px; }
.stDownloadButton button { width:100%; border-radius:4px; }
hr { border:0; border-top:1px solid #d9dde3; margin:1rem 0; }
</style>
""", unsafe_allow_html=True)

# -----------------------------
# Data
# -----------------------------
@st.cache_data(show_spinner=False)
def load_data():
    df = pd.read_csv(DATA_PATH)
    df["Order Date"] = pd.to_datetime(df["Order Date"], dayfirst=True, errors="coerce")
    for col in ["Sales", "Discount", "Profit"]:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
    df["Year"] = df["Order Date"].dt.year
    df["Month"] = df["Order Date"].dt.to_period("M").dt.to_timestamp()
    df["Profit Margin %"] = np.where(df["Sales"] != 0, df["Profit"] / df["Sales"] * 100, 0)
    df["Discount %"] = df["Discount"] * 100
    return df.dropna(subset=["Order Date"])

df = load_data()

# -----------------------------
# Helpers
# -----------------------------
def money(v):
    v = float(v)
    if abs(v) >= 1e7: return f"₹{v/1e7:.2f} Cr"
    if abs(v) >= 1e5: return f"₹{v/1e5:.2f} L"
    if abs(v) >= 1e3: return f"₹{v/1e3:.1f}K"
    return f"₹{v:,.0f}"

def pct(v):
    return f"{v:.1f}%"

def kpi(label, value, sub):
    st.markdown(f"""
    <div class="kpi">
      <div class="kpi-label">{label}</div>
      <div class="kpi-value">{value}</div>
      <div class="kpi-sub">{sub}</div>
    </div>
    """, unsafe_allow_html=True)

def plotly_base(fig, height=360):
    fig.update_layout(
        height=height, margin=dict(l=10,r=10,t=45,b=10),
        paper_bgcolor="white", plot_bgcolor="white",
        font=dict(family="Inter", color="#334155"),
        title_font=dict(size=15, color="#0f172a"),
        legend=dict(orientation="h", y=1.08, x=0),
        hoverlabel=dict(bgcolor="white"),
    )
    fig.update_xaxes(showgrid=False, linecolor="#e2e8f0")
    fig.update_yaxes(gridcolor="#eef2f7", zeroline=False)
    return fig

def filtered_data():
    return st.session_state.get("filtered_df", df)

# -----------------------------
# Sidebar
# -----------------------------
with st.sidebar:
    st.markdown("## SAPPHIRE IQ")
    st.caption("Supermart Retail Intelligence")
    st.divider()

    page = st.radio(
        "Navigation",
        ["Executive Overview", "Product Performance", "Profit & Discount",
         "Geographic Intelligence", "Data Explorer"],
        label_visibility="collapsed"
    )

    st.divider()
    st.markdown("### Global Filters")

    years = sorted(df["Year"].dropna().unique())
    selected_years = st.multiselect("Year", years, default=years)

    categories = sorted(df["Category"].dropna().unique())
    selected_categories = st.multiselect("Category", categories, default=categories)

    regions = sorted(df["Region"].dropna().unique())
    selected_regions = st.multiselect("Region", regions, default=regions)

    min_date, max_date = df["Order Date"].min().date(), df["Order Date"].max().date()
    date_range = st.date_input("Order date", (min_date, max_date), min_value=min_date, max_value=max_date)

    st.divider()
    st.caption("Internal Management Reporting")
    st.caption("Built with Streamlit + Plotly")

# Apply filters
start_date, end_date = date_range if isinstance(date_range, tuple) and len(date_range) == 2 else (min_date, max_date)
f = df[
    df["Year"].isin(selected_years)
    & df["Category"].isin(selected_categories)
    & df["Region"].isin(selected_regions)
    & (df["Order Date"].dt.date >= start_date)
    & (df["Order Date"].dt.date <= end_date)
].copy()
st.session_state["filtered_df"] = f

# -----------------------------
# Header
# -----------------------------
st.markdown("""
<div class="hero">
  <h1>Supermart Sales Performance</h1>
  <p>Management dashboard for sales, profit, product and regional performance.</p>
</div>
""", unsafe_allow_html=True)

if f.empty:
    st.warning("No records match the current filters. Please broaden the selection.")
    st.stop()

# -----------------------------
# Executive Overview
# -----------------------------
if page == "Executive Overview":
    st.markdown('<div class="section-title">Executive Snapshot</div>', unsafe_allow_html=True)
    c = st.columns(5)
    total_sales, total_profit = f["Sales"].sum(), f["Profit"].sum()
    margin = total_profit / total_sales * 100 if total_sales else 0
    orders = f["Order ID"].nunique()
    avg_order = total_sales / orders if orders else 0
    with c[0]: kpi("Total Sales", money(total_sales), f"{orders:,} orders")
    with c[1]: kpi("Total Profit", money(total_profit), f"{margin:.1f}% margin")
    with c[2]: kpi("Profit Margin", pct(margin), "Profit ÷ Sales")
    with c[3]: kpi("Avg. Order Value", money(avg_order), "Sales ÷ orders")
    with c[4]: kpi("Avg. Discount", pct(f["Discount"].mean()*100), "Across filtered sales")

    st.markdown("<br>", unsafe_allow_html=True)
    a,b = st.columns([1.55,1])
    with a:
        monthly = f.groupby("Month", as_index=False)[["Sales","Profit"]].sum()
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=monthly["Month"], y=monthly["Sales"], name="Sales", mode="lines+markers", line=dict(width=3)))
        fig.add_trace(go.Scatter(x=monthly["Month"], y=monthly["Profit"], name="Profit", mode="lines", line=dict(width=3)))
        fig.update_layout(title="Sales & Profit Trend", yaxis_title="Value (₹)", xaxis_title=None)
        st.plotly_chart(plotly_base(fig, 390), use_container_width=True)
    with b:
        cat = f.groupby("Category", as_index=False).agg(Sales=("Sales","sum"), Profit=("Profit","sum"))
        fig = px.bar(cat.sort_values("Sales"), x="Sales", y="Category", orientation="h", text_auto=".2s",
                     title="Sales by Category")
        st.plotly_chart(plotly_base(fig, 390), use_container_width=True)

    a,b = st.columns(2)
    with a:
        reg = f.groupby("Region", as_index=False).agg(Sales=("Sales","sum"), Profit=("Profit","sum"))
        fig = px.bar(reg.sort_values("Sales"), x="Region", y="Sales", text_auto=".2s", title="Regional Sales")
        st.plotly_chart(plotly_base(fig, 330), use_container_width=True)
    with b:
        top = f.groupby("Sub Category", as_index=False).agg(Sales=("Sales","sum"), Profit=("Profit","sum"))
        top["Margin"] = np.where(top["Sales"]!=0, top["Profit"]/top["Sales"]*100,0)
        top = top.sort_values("Sales", ascending=False).head(10)
        fig = px.scatter(top, x="Sales", y="Profit", size="Sales", color="Margin",
                         hover_name="Sub Category", title="Top Sub-Categories: Sales vs Profit",
                         color_continuous_scale="Blues")
        st.plotly_chart(plotly_base(fig, 330), use_container_width=True)

    # Management insights
    best_cat = cat.loc[cat["Sales"].idxmax(), "Category"]
    best_reg = reg.loc[reg["Sales"].idxmax(), "Region"]
    low_profit = f.groupby("Category").agg(Sales=("Sales","sum"), Profit=("Profit","sum")).reset_index()
    low_profit["Margin"] = low_profit["Profit"]/low_profit["Sales"]*100
    risk_cat = low_profit.loc[low_profit["Margin"].idxmin(), "Category"]
    st.markdown("### Management Signals")
    x,y,z = st.columns(3)
    x.info(f"**Sales leader:** {best_cat} contributes the largest category sales in the current filter.")
    y.success(f"**Regional leader:** {best_reg} is the highest-sales region.")
    z.warning(f"**Margin watch:** {risk_cat} has the lowest category profit margin in the current view.")

# -----------------------------
# Product Performance
# -----------------------------
elif page == "Product Performance":
    st.markdown("### Product Performance", unsafe_allow_html=True)
    st.caption("Identify category leaders, profitable products and high-sales / low-profit opportunities.")

    cat = f.groupby(["Category"], as_index=False).agg(Sales=("Sales","sum"), Profit=("Profit","sum"))
    cat["Margin %"] = cat["Profit"]/cat["Sales"]*100
    sub = f.groupby(["Category","Sub Category"], as_index=False).agg(Sales=("Sales","sum"), Profit=("Profit","sum"))
    sub["Margin %"] = np.where(sub["Sales"]!=0, sub["Profit"]/sub["Sales"]*100,0)

    a,b = st.columns(2)
    with a:
        fig = px.bar(cat.sort_values("Sales"), x="Sales", y="Category", color="Profit",
                     orientation="h", title="Category Sales & Profit", color_continuous_scale="Blues")
        st.plotly_chart(plotly_base(fig, 390), use_container_width=True)
    with b:
        fig = px.scatter(sub, x="Sales", y="Profit", size="Sales", color="Margin %",
                         hover_name="Sub Category", title="Sub-category Portfolio",
                         color_continuous_scale="Blues")
        st.plotly_chart(plotly_base(fig, 390), use_container_width=True)

    st.markdown("### High Sales, Low Profit — Opportunity Monitor")
    threshold_sales = st.slider("Minimum sales threshold", 0, int(max(1000, sub["Sales"].max())), int(sub["Sales"].quantile(.60)), step=500)
    threshold_margin = st.slider("Maximum profit margin %", 0.0, 50.0, 12.0, 0.5)
    opportunities = sub[(sub["Sales"] >= threshold_sales) & (sub["Margin %"] <= threshold_margin)].sort_values("Sales", ascending=False)
    if opportunities.empty:
        st.success("No sub-categories currently meet both risk thresholds.")
    else:
        st.dataframe(opportunities.style.format({"Sales":"₹{:,.0f}","Profit":"₹{:,.0f}","Margin %":"{:.1f}%"}),
                     use_container_width=True, hide_index=True)

# -----------------------------
# Profit & Discount
# -----------------------------
elif page == "Profit & Discount":
    st.markdown("### Profit & Discount Intelligence")
    st.caption("Understand margin structure and the relationship between discounting and profitability.")

    margin = f["Profit"].sum()/f["Sales"].sum()*100
    a,b,c = st.columns(3)
    with a: kpi("Portfolio Margin", pct(margin), "Filtered profit / sales")
    with b: kpi("Highest Discount", pct(f["Discount"].max()*100), "Maximum observed")
    with c: kpi("Discounted Sales", money(f.loc[f["Discount"]>0,"Sales"].sum()), "Sales with discount > 0")

    a,b = st.columns([1.1,1])
    with a:
        bins = pd.cut(f["Discount"], bins=[-0.001,.10,.20,.30,.40,1], labels=["0–10%","10–20%","20–30%","30–40%","40%+"])
        d = f.assign(Band=bins).groupby("Band", observed=False).agg(Sales=("Sales","sum"), Profit=("Profit","sum")).reset_index()
        fig = px.bar(d, x="Band", y=["Sales","Profit"], barmode="group", title="Sales & Profit by Discount Band")
        st.plotly_chart(plotly_base(fig, 380), use_container_width=True)
    with b:
        sample = f.sample(min(3500, len(f)), random_state=42)
        fig = px.scatter(sample, x="Discount %", y="Profit", size="Sales",
                         hover_data=["Category","Sub Category","Region"],
                         title="Discount vs Profit", trendline="ols")
        st.plotly_chart(plotly_base(fig, 380), use_container_width=True)

    cat = f.groupby("Category", as_index=False).agg(Sales=("Sales","sum"), Profit=("Profit","sum"), Discount=("Discount","mean"))
    cat["Margin %"] = cat["Profit"]/cat["Sales"]*100
    fig = px.bar(cat.sort_values("Margin %"), x="Category", y="Margin %", color="Discount",
                 title="Category Profit Margin vs Average Discount", color_continuous_scale="Blues")
    st.plotly_chart(plotly_base(fig, 350), use_container_width=True)

# -----------------------------
# Geographic
# -----------------------------
elif page == "Geographic Intelligence":
    st.markdown("### Geographic Intelligence")
    st.caption("Compare regions, states and cities to identify concentration and low-profit pockets.")

    reg = f.groupby("Region", as_index=False).agg(Sales=("Sales","sum"), Profit=("Profit","sum"), Orders=("Order ID","nunique"))
    reg["Margin %"] = reg["Profit"]/reg["Sales"]*100
    a,b = st.columns(2)
    with a:
        fig = px.bar(reg.sort_values("Sales"), x="Sales", y="Region", orientation="h",
                     color="Margin %", title="Regional Sales with Margin", color_continuous_scale="Blues")
        st.plotly_chart(plotly_base(fig, 370), use_container_width=True)
    with b:
        city = f.groupby("City", as_index=False).agg(Sales=("Sales","sum"), Profit=("Profit","sum"))
        city["Margin %"] = city["Profit"]/city["Sales"]*100
        fig = px.scatter(city, x="Sales", y="Profit", size="Sales", color="Margin %",
                         hover_name="City", title="City Performance Map", color_continuous_scale="Blues")
        st.plotly_chart(plotly_base(fig, 370), use_container_width=True)

    city = f.groupby(["State","City"], as_index=False).agg(Sales=("Sales","sum"), Profit=("Profit","sum"), Orders=("Order ID","nunique"))
    city["Margin %"] = np.where(city["Sales"]!=0, city["Profit"]/city["Sales"]*100,0)
    st.markdown("### Location Opportunity Monitor")
    low = city.sort_values(["Sales","Margin %"], ascending=[False, True]).head(15)
    st.dataframe(low.style.format({"Sales":"₹{:,.0f}","Profit":"₹{:,.0f}","Margin %":"{:.1f}%"}),
                 use_container_width=True, hide_index=True)

# -----------------------------
# Data Explorer
# -----------------------------
else:
    st.markdown("### Data Explorer")
    st.caption("Inspect the filtered dataset, validate data quality and export the exact management view.")
    a,b,c,d = st.columns(4)
    with a: kpi("Rows", f"{len(f):,}", "Filtered records")
    with b: kpi("Customers", f"{f['Customer Name'].nunique():,}", "Unique customers")
    with c: kpi("Products", f"{f['Sub Category'].nunique():,}", "Sub-categories")
    with d: kpi("Date Range", f"{f['Order Date'].min():%b %Y}–{f['Order Date'].max():%b %Y}", "Filtered period")

    st.markdown("### Data Quality")
    q1 = int(f.isna().sum().sum())
    q2 = int((f["Profit"] < 0).sum())
    q3 = int((f["Discount"] > .5).sum())
    st.info(f"Missing values: **{q1}**  •  Negative-profit rows: **{q2:,}**  •  Discount > 50%: **{q3:,}**")

    st.dataframe(f.sort_values("Order Date", ascending=False), use_container_width=True, hide_index=True, height=520)
    csv = f.to_csv(index=False).encode("utf-8")
    st.download_button("⬇ Download Filtered CSV", csv, "sapphire_iq_filtered_sales.csv", "text/csv")

st.markdown("<hr>", unsafe_allow_html=True)
st.caption(f"Internal Report • Showing {len(f):,} records • {f['Order Date'].min():%d %b %Y} to {f['Order Date'].max():%d %b %Y}")
