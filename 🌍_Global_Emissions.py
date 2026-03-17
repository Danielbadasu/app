import streamlit as st
import pandas as pd
import plotly.express as px
from chatbot_widget import render_ai_banner

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
</style>
""", unsafe_allow_html=True)

# ---- TITLE ----
st.title("🌍 Global Climate Intelligence Dashboard")
st.markdown("Exploring CO₂ emissions and climate trends using public data.")

# ---- LOAD DATA ----
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/owid/co2-data/master/owid-co2-data.csv"
    df = pd.read_csv(url)
    return df

df = load_data()

# ---- EXCLUDE AGGREGATES ----
exclude = [
    'World', 'Asia', 'Europe', 'Africa', 'Oceania',
    'North America', 'South America', 'Antarctic',
    'European Union (27)', 'High-income countries',
    'Low-income countries', 'Upper-middle-income countries',
    'Lower-middle-income countries', 'International transport'
]
countries_df = df[~df['country'].isin(exclude)]

# ---- SIDEBAR FILTERS ----
st.sidebar.header("Filters")

countries = sorted(countries_df['country'].dropna().unique().tolist())
selected_countries = st.sidebar.multiselect(
    "Select Countries",
    options=countries,
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