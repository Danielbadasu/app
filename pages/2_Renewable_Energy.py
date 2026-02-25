import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Renewable Energy Transition", layout="wide")

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
.kpi-card.yellow {
    background: linear-gradient(135deg, #f7971e, #ffd200);
}
.kpi-card.green {
    background: linear-gradient(135deg, #11998e, #38ef7d);
}
.kpi-card.pink {
    background: linear-gradient(135deg, #ee0979, #ff6a00);
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
st.title("⚡ Renewable Energy Transition")
st.markdown("Tracking the global shift from fossil fuels to clean energy sources.")

# ---- LOAD DATA ----
@st.cache_data
def load_energy_data():
    url = "https://raw.githubusercontent.com/owid/energy-data/master/owid-energy-data.csv"
    df = pd.read_csv(url)
    return df

df = load_energy_data()

# ---- SIDEBAR FILTERS ----
st.sidebar.header("Filters")

countries = df['country'].dropna().unique().tolist()
selected_countries = st.sidebar.multiselect(
    "Select Countries",
    options=countries,
    default=["United States", "China", "Germany", "India", "United Kingdom"]
)

year_range = st.sidebar.slider(
    "Select Year Range",
    min_value=int(df['year'].min()),
    max_value=int(df['year'].max()),
    value=(2000, 2022)
)

# ---- FILTER DATA ----
filtered_df = df[
    (df['country'].isin(selected_countries)) &
    (df['year'].between(year_range[0], year_range[1]))
]

# ---- KPI VALUES ----
latest_year_df = filtered_df[filtered_df['year'] == filtered_df['year'].max()]

total_solar = filtered_df['solar_electricity'].sum()
top_renewable_country = (
    latest_year_df.groupby('country')['renewables_share_energy']
    .mean()
    .idxmax()
)
avg_renewable_share = latest_year_df['renewables_share_energy'].mean()

# ---- KPI CARDS ----
st.markdown(f"""
<div class="kpi-container">
    <div class="kpi-card yellow">
        <div class="kpi-icon">☀️</div>
        <div class="kpi-label">Total Solar Generated</div>
        <div class="kpi-value">{total_solar:,.0f} TWh</div>
        <div class="kpi-sub">Selected countries & period</div>
    </div>
    <div class="kpi-card green">
        <div class="kpi-icon">🌱</div>
        <div class="kpi-label">Leading Renewable Country</div>
        <div class="kpi-value">{top_renewable_country}</div>
        <div class="kpi-sub">Highest renewables share latest year</div>
    </div>
    <div class="kpi-card pink">
        <div class="kpi-icon">⚡</div>
        <div class="kpi-label">Avg Renewables Share</div>
        <div class="kpi-value">{avg_renewable_share:.1f}%</div>
        <div class="kpi-sub">Across selected countries</div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# ---- RENEWABLE SHARE OVER TIME ----
st.subheader("Renewables Share of Energy Over Time")
fig1 = px.line(
    filtered_df,
    x="year",
    y="renewables_share_energy",
    color="country",
    labels={
        "renewables_share_energy": "Renewables Share (%)",
        "year": "Year"
    },
    template="plotly_dark"
)
st.plotly_chart(fig1, use_container_width=True)

# ---- SOLAR VS WIND VS FOSSIL ----
st.subheader("Solar vs Wind vs Fossil Fuel Electricity")

energy_cols = ['year', 'country', 'solar_electricity', 'wind_electricity', 'fossil_electricity']
energy_df = filtered_df[energy_cols].dropna()
energy_melted = energy_df.melt(
    id_vars=['year', 'country'],
    value_vars=['solar_electricity', 'wind_electricity', 'fossil_electricity'],
    var_name='Source',
    value_name='TWh'
)
energy_melted['Source'] = energy_melted['Source'].replace({
    'solar_electricity': 'Solar',
    'wind_electricity': 'Wind',
    'fossil_electricity': 'Fossil Fuels'
})

# sum across selected countries per year
grouped = energy_melted.groupby(['year', 'Source'])['TWh'].sum().reset_index()

fig2 = px.area(
    grouped,
    x="year",
    y="TWh",
    color="Source",
    labels={"TWh": "Electricity (TWh)", "year": "Year"},
    template="plotly_dark",
    color_discrete_map={
        "Solar": "#ffd200",
        "Wind": "#38ef7d",
        "Fossil Fuels": "#ff416c"
    }
)
st.plotly_chart(fig2, use_container_width=True)

# ---- RENEWABLES BY COUNTRY BAR ----
st.subheader("Renewables Share by Country (Latest Year)")
bar_df = latest_year_df[['country', 'renewables_share_energy']].dropna().sort_values(
    'renewables_share_energy', ascending=True
)

fig3 = px.bar(
    bar_df,
    x="renewables_share_energy",
    y="country",
    orientation='h',
    labels={"renewables_share_energy": "Renewables Share (%)", "country": "Country"},
    template="plotly_dark",
    color="renewables_share_energy",
    color_continuous_scale="Viridis"
)
st.plotly_chart(fig3, use_container_width=True)

# ---- RAW DATA ----
if st.checkbox("Show raw data"):
    st.dataframe(
        filtered_df[['country', 'year', 'solar_electricity', 'wind_electricity',
                     'fossil_electricity', 'renewables_share_energy']].reset_index(drop=True)
    )