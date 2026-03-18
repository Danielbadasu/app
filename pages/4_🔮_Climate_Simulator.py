import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from chatbot_widget import render_ai_banner, render_sidebar_chat, render_disclaimer

st.set_page_config(page_title="Climate Scenario Simulator", layout="wide")

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
.kpi-card.orange {
    background: linear-gradient(135deg, #f7971e, #ffd200);
}
.kpi-card.red {
    background: linear-gradient(135deg, #ff416c, #ff4b2b);
}
.kpi-card.purple {
    background: linear-gradient(135deg, #6a11cb, #a855f7);
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
    font-size: 34px;
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
st.title("🔮 Climate Scenario Simulator")
st.markdown("Project future CO₂ emissions and temperature rise based on different global action scenarios.")

# ---- LOAD DATA ----
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/owid/co2-data/master/owid-co2-data.csv"
    df = pd.read_csv(url)
    return df

df = load_data()

# ---- SIDEBAR FILTERS ----
st.sidebar.header("Simulation Settings")

scenario = st.sidebar.radio(
    "Select Scenario",
    options=["🟢 Optimistic", "🟡 Moderate", "🔴 Pessimistic"],
    index=1
)

target_year = st.sidebar.slider(
    "Project to Year",
    min_value=2025,
    max_value=2100,
    value=2050,
    step=5
)

countries = df['country'].dropna().unique().tolist()
selected_countries = st.sidebar.multiselect(
    "Select Countries",
    options=countries,
    default=["United States", "China", "India", "United Kingdom", "Germany"]
)

st.sidebar.markdown("---")
st.sidebar.markdown(f"**🔮 Scenario:** {scenario}")
st.sidebar.markdown(f"**📅 Target Year:** {target_year}")

# ---- SCENARIO RATES ----
scenario_config = {
    "🟢 Optimistic": {
        "co2_rate": -0.03,
        "temp_rate": 0.010,
        "color": "#38ef7d",
        "label": "Aggressive climate action — 3% annual emissions reduction",
    },
    "🟡 Moderate": {
        "co2_rate": -0.01,
        "temp_rate": 0.018,
        "color": "#ffd200",
        "label": "Current pace — 1% annual emissions reduction",
    },
    "🔴 Pessimistic": {
        "co2_rate": 0.02,
        "temp_rate": 0.030,
        "color": "#ff416c",
        "label": "Fossil fuel dependency grows — 2% annual emissions increase",
    }
}

config = scenario_config[scenario]
years_ahead = target_year - 2022

# ---- FILTER HISTORICAL DATA ----
hist_df = df[
    (df['country'].isin(selected_countries)) &
    (df['year'] >= 1990) &
    (df['year'] <= 2022)
]

# ---- BUILD PROJECTIONS ----
base_co2 = hist_df[hist_df['year'] == 2022].groupby('country')['co2'].sum()
projection_years = list(range(2023, target_year + 1))

projection_rows = []
for country in selected_countries:
    if country not in base_co2.index:
        continue
    base = base_co2[country]
    for i, year in enumerate(projection_years):
        projected_co2 = base * ((1 + config["co2_rate"]) ** (i + 1))
        projection_rows.append({
            "country": country,
            "year": year,
            "co2": projected_co2,
            "type": "Projected"
        })

proj_df = pd.DataFrame(projection_rows)

# ---- HISTORICAL FOR CHART ----
hist_chart_df = hist_df[['country', 'year', 'co2']].copy()
hist_chart_df['type'] = 'Historical'

# ---- COMBINE ----
combined_df = pd.concat([hist_chart_df, proj_df], ignore_index=True)

# ---- TEMPERATURE PROJECTION ----
base_temp = 1.1
temp_years = list(range(1990, target_year + 1))
temp_values_hist = [base_temp * ((1 + 0.018) ** max(0, y - 2022)) if y <= 2022
                    else None for y in temp_years]
temp_values_proj = [None if y <= 2022
                    else base_temp * ((1 + config["temp_rate"]) ** (y - 2022))
                    for y in temp_years]

# ---- KPI VALUES ----
total_hist_co2 = hist_df[hist_df['year'] == 2022]['co2'].sum()
total_proj_co2 = proj_df[proj_df['year'] == target_year]['co2'].sum() if not proj_df.empty else 0
co2_change_pct = ((total_proj_co2 - total_hist_co2) / total_hist_co2) * 100 if total_hist_co2 > 0 else 0
proj_temp_rise = base_temp * ((1 + config["temp_rate"]) ** years_ahead)
co2_card = "green" if co2_change_pct < 0 else "red"
temp_card = "green" if proj_temp_rise < 1.5 else "orange" if proj_temp_rise < 2.5 else "red"

# ---- KPI CARDS ----
st.markdown(f"""
<div class="kpi-container">
    <div class="kpi-card purple">
        <div class="kpi-icon">📅</div>
        <div class="kpi-label">Projection Target</div>
        <div class="kpi-value">{target_year}</div>
        <div class="kpi-sub">{years_ahead} years from 2022 baseline</div>
    </div>
    <div class="kpi-card {co2_card}">
        <div class="kpi-icon">💨</div>
        <div class="kpi-label">Projected CO₂ Change</div>
        <div class="kpi-value">{co2_change_pct:+.1f}%</div>
        <div class="kpi-sub">vs 2022 baseline across selected countries</div>
    </div>
    <div class="kpi-card {temp_card}">
        <div class="kpi-icon">🌡️</div>
        <div class="kpi-label">Est. Temperature Rise</div>
        <div class="kpi-value">{proj_temp_rise:.2f}°C</div>
        <div class="kpi-sub">Above pre-industrial baseline by {target_year}</div>
    </div>
    <div class="kpi-card orange">
        <div class="kpi-icon">⚠️</div>
        <div class="kpi-label">Paris Agreement Target</div>
        <div class="kpi-value">{"✅ Met" if proj_temp_rise <= 1.5 else "❌ Missed"}</div>
        <div class="kpi-sub">1.5°C limit {"achieved" if proj_temp_rise <= 1.5 else f"exceeded by {proj_temp_rise - 1.5:.2f}°C"}</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ---- SCENARIO DESCRIPTION ----
st.info(f"**{scenario} Scenario:** {config['label']}")

# ---- AI BANNER ----
render_ai_banner("Climate Projections & Scenarios")

st.markdown("---")

# ---- CO2 PROJECTION CHART ----
st.subheader("📈 CO₂ Emissions — Historical + Projected")
st.markdown("Solid lines = historical data. Dashed lines = projected trajectory.")

fig1 = go.Figure()

for country in selected_countries:
    country_hist = combined_df[
        (combined_df['country'] == country) &
        (combined_df['type'] == 'Historical')
    ]
    country_proj = combined_df[
        (combined_df['country'] == country) &
        (combined_df['type'] == 'Projected')
    ]

    fig1.add_trace(go.Scatter(
        x=country_hist['year'],
        y=country_hist['co2'],
        mode='lines',
        name=f"{country} (Historical)",
        line=dict(width=2)
    ))

    fig1.add_trace(go.Scatter(
        x=country_proj['year'],
        y=country_proj['co2'],
        mode='lines',
        name=f"{country} (Projected)",
        line=dict(width=2, dash='dash'),
    ))

fig1.add_vline(
    x=2022,
    line_dash="dot",
    line_color="white",
    opacity=0.5,
    annotation_text="2022 Baseline",
    annotation_position="top right"
)

fig1.update_layout(
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0.2)",
    xaxis_title="Year",
    yaxis_title="CO₂ Emissions (million tonnes)",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
)
st.plotly_chart(fig1, use_container_width=True)

st.markdown("---")

# ---- TEMPERATURE CHART ----
st.subheader("🌡️ Global Temperature Rise Projection")
st.markdown("Based on current anomaly trend extended through selected scenario.")

fig2 = go.Figure()

fig2.add_trace(go.Scatter(
    x=temp_years,
    y=temp_values_hist,
    mode='lines',
    name='Historical Trend',
    line=dict(color='#EF553B', width=2)
))

fig2.add_trace(go.Scatter(
    x=temp_years,
    y=temp_values_proj,
    mode='lines',
    name=f'{scenario} Projection',
    line=dict(color=config['color'], width=2, dash='dash')
))

fig2.add_hline(
    y=1.5,
    line_dash="dash",
    line_color="#38ef7d",
    opacity=0.7,
    annotation_text="🎯 Paris 1.5°C Target",
    annotation_position="top left"
)

fig2.add_hline(
    y=2.0,
    line_dash="dash",
    line_color="#ffd200",
    opacity=0.7,
    annotation_text="⚠️ 2°C Danger Threshold",
    annotation_position="top left"
)

fig2.add_vline(
    x=2022,
    line_dash="dot",
    line_color="white",
    opacity=0.5,
    annotation_text="2022 Baseline",
    annotation_position="top right"
)

fig2.update_layout(
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0.2)",
    xaxis_title="Year",
    yaxis_title="Temperature Rise (°C above pre-industrial)",
)
st.plotly_chart(fig2, use_container_width=True)

st.markdown("---")

# ---- CO2 BAR: NOW VS PROJECTED ----
st.subheader(f"⚖️ CO₂ Now vs Projected ({target_year})")

now_df = hist_df[hist_df['year'] == 2022][['country', 'co2']].copy()
now_df['period'] = '2022 (Baseline)'

proj_target_df = proj_df[proj_df['year'] == target_year][['country', 'co2']].copy()
proj_target_df['period'] = f'{target_year} ({scenario})'

compare_df = pd.concat([now_df, proj_target_df], ignore_index=True)

fig3 = px.bar(
    compare_df,
    x='country',
    y='co2',
    color='period',
    barmode='group',
    labels={'co2': 'CO₂ Emissions (million tonnes)', 'country': 'Country'},
    template='plotly_dark',
    color_discrete_map={
        '2022 (Baseline)': '#a855f7',
        f'{target_year} ({scenario})': config['color']
    }
)
fig3.update_layout(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0.2)"
)
st.plotly_chart(fig3, use_container_width=True)

st.markdown("---")

# ---- DOWNLOAD ----
csv = combined_df.to_csv(index=False).encode('utf-8')
st.download_button(
    label="📥 Download Simulation Data as CSV",
    data=csv,
    file_name=f"climate_simulation_{scenario}_{target_year}.csv",
    mime="text/csv"
)

from chatbot_widget import render_ai_banner, render_sidebar_chat

# ---- DISCLAIMER ----
render_disclaimer("Climate Projections Simulator")  # change context per page

# at the very bottom of each page:
render_sidebar_chat("Climate Projections")  # change context per page
