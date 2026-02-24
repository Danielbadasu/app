import streamlit as st
import pandas as pd
import plotly.express as px

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
    padding: 20px 25px;
    border-radius: 16px;
    background: linear-gradient(135deg, #1a1a2e, #16213e);
    border: 1px solid rgba(255,255,255,0.08);
    position: relative;
    overflow: hidden;
    box-shadow: 0 8px 32px rgba(0,0,0,0.4);
}
.kpi-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
}
.kpi-card.green::before  { background: linear-gradient(90deg, #11998e, #38ef7d); box-shadow: 0 0 20px #11998e; }
.kpi-card.purple::before { background: linear-gradient(90deg, #a855f7, #6366f1); box-shadow: 0 0 20px #a855f7; }
.kpi-card.cyan::before   { background: linear-gradient(90deg, #06b6d4, #0ea5e9); box-shadow: 0 0 20px #06b6d4; }
.kpi-label {
    font-size: 12px;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: rgba(255,255,255,0.45);
    margin-bottom: 10px;
}
.kpi-value {
    font-size: 38px;
    font-weight: 800;
    letter-spacing: -1px;
    margin-bottom: 6px;
}
.kpi-card.green  .kpi-value { color: #38ef7d; }
.kpi-card.purple .kpi-value { color: #a855f7; }
.kpi-card.cyan   .kpi-value { color: #06b6d4; }
.kpi-sub {
    font-size: 12px;
    color: rgba(255,255,255,0.35);
}
.kpi-icon {
    position: absolute;
    top: 18px; right: 20px;
    font-size: 28px;
    opacity: 0.15;
}
</style>
""", unsafe_allow_html=True)

# ---- TITLE ----
st.title("🌍 Global Climate Intelligence Dashboard")
st.markdown("Exploring temperature anomalies, CO₂ emissions, and climate trends using public data.")

# ---- LOAD DATA ----
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/owid/co2-data/master/owid-co2-data.csv"
    df = pd.read_csv(url)
    return df

df = load_data()

# ---- SIDEBAR FILTERS ----
st.sidebar.header("Filters")

countries = df['country'].dropna().unique().tolist()
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
filtered_df = df[
    (df['country'].isin(selected_countries)) & 
    (df['year'].between(year_range[0], year_range[1]))
]

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

# ---- RAW DATA TOGGLE ----
if st.checkbox("Show raw data"):
    st.dataframe(filtered_df[['country', 'year', 'co2', 'co2_per_capita']].reset_index(drop=True))