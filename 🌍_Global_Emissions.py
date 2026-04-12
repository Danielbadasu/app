import streamlit as st
import pandas as pd
import plotly.express as px
from chatbot_widget import render_ai_banner, render_sidebar_chat, render_disclaimer

# ---- PAGE CONFIG ----
st.set_page_config(page_title="Global Climate Dashboard", layout="wide")

# ---- CUSTOM CSS ----
st.markdown("""
<style>
.kpi-container {
    display: flex;
    gap: 20px;
    margin-bottom: 30px;
}
.kpi-card {
    flex: 1;
    padding: 24px 28px;
    border-radius: 16px;
    position: relative;
    overflow: hidden;
    box-shadow: 0 8px 32px rgba(0,0,0,0.4);
}
.kpi-card.green {
    background: linear-gradient(135deg, #11998e, #38ef7d);
}
.kpi-card.purple {
    background: linear-gradient(135deg, #6a11cb, #a855f7);
}
.kpi-card.cyan {
    background: linear-gradient(135deg, #0ea5e9, #06b6d4);
}
.kpi-label {
    font-size: 12px;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: rgba(255,255,255,0.75);
    margin-bottom: 10px;
    font-weight: 600;
}
.kpi-value {
    font-size: 38px;
    font-weight: 800;
    letter-spacing: -1px;
    margin-bottom: 6px;
    color: #ffffff;
    text-shadow: 0 2px 10px rgba(0,0,0,0.2);
}
.kpi-sub {
    font-size: 12px;
    color: rgba(255,255,255,0.65);
}
.kpi-icon {
    position: absolute;
    top: 18px; right: 20px;
    font-size: 42px;
    opacity: 0.25;
}
.overview-container {
    background: linear-gradient(135deg, rgba(168,85,247,0.08), rgba(14,165,233,0.08));
    border: 1px solid rgba(168,85,247,0.25);
    border-radius: 16px;
    padding: 28px 32px;
    margin-bottom: 32px;
}
.overview-title {
    font-size: 13px;
    font-weight: 700;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: #a855f7;
    margin-bottom: 12px;
}
.overview-text {
    font-size: 17px;
    color: rgba(255,255,255,0.8);
    line-height: 1.8;
    margin-bottom: 20px;
}
.overview-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 16px;
    margin-top: 8px;
}
.overview-item {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 10px;
    padding: 14px 16px;
}
.overview-item-icon {
    font-size: 20px;
    margin-bottom: 6px;
}
.overview-item-title {
    font-size: 15px;
    font-weight: 700;
    color: #ffffff;
    margin-bottom: 4px;
}
.overview-item-desc {
    font-size: 14px;
    color: rgba(255,255,255,0.55);
    line-height: 1.5;
}
</style>
""", unsafe_allow_html=True)

# ---- TITLE ----
st.title("🌍 Global Climate Intelligence Dashboard")
st.markdown("Exploring CO₂ emissions and climate trends using public data.")

# ---- PROJECT OVERVIEW ----
st.markdown("""
<div class="overview-container">
    <div class="overview-title">📌 Project Overview</div>
    <div class="overview-text">
        The Global Climate Intelligence Dashboard is an open-access data platform designed to make 
        climate science accessible, interactive, and actionable. Built for policymakers, researchers, 
        institutions, and informed citizens, it transforms complex global datasets into clear visual 
        insights, enabling evidence-based understanding of the climate crisis without requiring 
        technical expertise.
    </div>
    <div class="overview-grid">
        <div class="overview-item">
            <div class="overview-item-icon">🌍</div>
            <div class="overview-item-title">CO₂ Emissions</div>
            <div class="overview-item-desc">Track emissions by country and per capita across time to understand who contributes most to global warming.</div>
        </div>
        <div class="overview-item">
            <div class="overview-item-icon">🌡️</div>
            <div class="overview-item-title">Temperature Trends</div>
            <div class="overview-item-desc">Explore how land surface temperatures have shifted country by country since the 18th century.</div>
        </div>
        <div class="overview-item">
            <div class="overview-item-icon">⚡</div>
            <div class="overview-item-title">Renewable Energy</div>
            <div class="overview-item-desc">Monitor the global transition from fossil fuels to clean energy sources across nations.</div>
        </div>
        <div class="overview-item">
            <div class="overview-item-icon">🌎</div>
            <div class="overview-item-title">Climate Vulnerability</div>
            <div class="overview-item-desc">Identify which countries face the greatest climate risk — and who bears the least responsibility for it.</div>
        </div>
        <div class="overview-item">
            <div class="overview-item-icon">🔮</div>
            <div class="overview-item-title">Scenario Simulator</div>
            <div class="overview-item-desc">Project future CO₂ and temperature trends to 2100 under optimistic, moderate, and pessimistic scenarios.</div>
        </div>
        <div class="overview-item">
            <div class="overview-item-icon">🤖</div>
            <div class="overview-item-title">AI Assistant</div>
            <div class="overview-item-desc">Ask climate questions in plain language and get instant, data-driven answers powered by AI.</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ---- LOAD DATA ----
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/owid/co2-data/master/owid-co2-data.csv"
    df = pd.read_csv(url)
    return df

df = load_data()

# ---- SMART COUNTRY FILTER ----
@st.cache_data
def get_real_countries(df):
    filtered = df[df['iso_code'].notna()]
    filtered = filtered[filtered['iso_code'].str.len() == 3]
    filtered = filtered[filtered['iso_code'].str.startswith('OWID') == False]
    return sorted(filtered['country'].dropna().unique().tolist())

real_countries = get_real_countries(df)
countries_df = df[df['country'].isin(real_countries)]

# ---- SIDEBAR FILTERS ----
st.sidebar.header("Filters")

selected_countries = st.sidebar.multiselect(
    "Select Countries",
    options=real_countries,
    default=["United States", "China", "India", "United Kingdom", "Germany"]
)

year_range = st.sidebar.slider(
    "Select Year Range",
    min_value=int(df['year'].min()),
    max_value=int(df['year'].max()),
    value=(1990, 2022)
)

# ---- FILTER DATA ----
filtered_df = countries_df[
    (countries_df['country'].isin(selected_countries)) &
    (countries_df['year'].between(year_range[0], year_range[1]))
]

# ---- SAFETY CHECK ----
if filtered_df.empty:
    st.warning("⚠️ No data found for the selected filters. Please adjust your selection.")
    st.stop()

# ---- KPI VALUES ----
total_co2 = filtered_df['co2'].sum()
max_co2_country = filtered_df.groupby('country')['co2'].sum().idxmax()
latest_year = int(filtered_df['year'].max())

# ---- KPI CARDS ----
st.markdown(f"""
<div class="kpi-container">
    <div class="kpi-card green">
        <div class="kpi-icon">🌿</div>
        <div class="kpi-label">Total CO₂ Emissions</div>
        <div class="kpi-value">{total_co2:,.0f} Mt</div>
        <div class="kpi-sub">Selected countries & period</div>
    </div>
    <div class="kpi-card purple">
        <div class="kpi-icon">🏭</div>
        <div class="kpi-label">Highest Emitter</div>
        <div class="kpi-value">{max_co2_country}</div>
        <div class="kpi-sub">In selected time range</div>
    </div>
    <div class="kpi-card cyan">
        <div class="kpi-icon">📅</div>
        <div class="kpi-label">Latest Data Year</div>
        <div class="kpi-value">{latest_year}</div>
        <div class="kpi-sub">Most recent available data</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ---- AI BANNER ----
render_ai_banner("CO₂ Emissions")

st.markdown("---")

# ---- CO2 LINE CHART ----
st.subheader("CO₂ Emissions Over Time (per country)")
fig1 = px.line(
    filtered_df,
    x="year",
    y="co2",
    color="country",
    labels={"co2": "CO₂ Emissions (million tonnes)", "year": "Year"},
    template="plotly_dark"
)
st.plotly_chart(fig1, use_container_width=True)

# ---- CO2 PER CAPITA ----
st.subheader("CO₂ Emissions Per Capita")
fig2 = px.line(
    filtered_df,
    x="year",
    y="co2_per_capita",
    color="country",
    labels={"co2_per_capita": "CO₂ Per Capita (tonnes)", "year": "Year"},
    template="plotly_dark"
)
st.plotly_chart(fig2, use_container_width=True)

# ---- DOWNLOAD DATA ----
st.markdown("---")
csv = filtered_df[['country', 'year', 'co2', 'co2_per_capita']].to_csv(index=False).encode('utf-8')
st.download_button(
    label="📥 Download Filtered Data as CSV",
    data=csv,
    file_name="co2_emissions_data.csv",
    mime="text/csv"
)

# ---- RAW DATA TOGGLE ----
if st.checkbox("Show raw data"):
    st.dataframe(filtered_df[['country', 'year', 'co2', 'co2_per_capita']].reset_index(drop=True))

# ---- DISCLAIMER ----
render_disclaimer("CO₂ Emissions")

# ---- SIDEBAR CHAT ----
render_sidebar_chat("CO₂ Emissions")