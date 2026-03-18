import streamlit as st
import pandas as pd
import plotly.express as px
from chatbot_widget import render_ai_banner

st.set_page_config(page_title="Temperature Anomalies", layout="wide")

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
.kpi-card.red {
    background: linear-gradient(135deg, #ff416c, #ff4b2b);
}
.kpi-card.orange {
    background: linear-gradient(135deg, #f7971e, #ffd200);
}
.kpi-card.blue {
    background: linear-gradient(135deg, #1a6dff, #4facfe);
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

st.title("🌡️ Global Temperature Anomalies")
st.markdown("How much warmer is the Earth compared to the 20th century baseline?")

# ---- LOAD DATA ----
@st.cache_data
def load_temp_data():
    url = "https://raw.githubusercontent.com/owid/owid-datasets/master/datasets/Global%20average%20temperature%20anomaly%20-%20Hadley%20Centre/Global%20average%20temperature%20anomaly%20-%20Hadley%20Centre.csv"
    df = pd.read_csv(url)
    df.columns = ["entity", "year", "anomaly"]
    return df

df = load_temp_data()

# ---- CONTINENT TO ENTITY MAPPING ----
continent_map = {
    "Global": ["World"],
    "Northern Hemisphere": ["Northern Hemisphere"],
    "Southern Hemisphere": ["Southern Hemisphere"],
    "Africa": ["Africa"],
    "Asia": ["Asia"],
    "Europe": ["Europe"],
    "North America": ["North America"],
    "South America": ["South America"],
    "Oceania": ["Oceania"]
}

available_entities = df['entity'].unique().tolist()

# ---- SIDEBAR FILTERS ----
st.sidebar.header("Filters")

# Continent filter
available_continents = ["All"] + [c for c in continent_map.keys()
                                   if any(e in available_entities
                                   for e in continent_map[c])]
selected_continent = st.sidebar.selectbox(
    "Filter by Continent / Region",
    options=available_continents
)

# Country/entity filter based on continent
if selected_continent == "All":
    entity_options = sorted(available_entities)
else:
    entity_options = [e for e in continent_map.get(selected_continent, [])
                      if e in available_entities]
    if not entity_options:
        entity_options = sorted(available_entities)

selected_entities = st.sidebar.multiselect(
    "Select Region(s)",
    options=entity_options,
    default=entity_options[:1]
)

# Fallback if nothing selected
if not selected_entities:
    selected_entities = entity_options[:1]

year_range = st.sidebar.slider(
    "Select Year Range",
    min_value=int(df['year'].min()),
    max_value=int(df['year'].max()),
    value=(int(df['year'].min()), int(df['year'].max()))
)

st.sidebar.markdown("---")
st.sidebar.markdown(f"**📊 Showing:** {year_range[0]} – {year_range[1]}")
st.sidebar.markdown(f"**🌍 Region(s):** {', '.join(selected_entities)}")

# ---- FILTER ----
filtered_df = df[
    (df['entity'].isin(selected_entities)) &
    (df['year'].between(year_range[0], year_range[1]))
]

if filtered_df.empty:
    st.warning("⚠️ No data found for the selected filters. Please adjust your selection.")
    st.stop()

# ---- KPI VALUES ----
latest_year = filtered_df['year'].max()
latest = filtered_df[filtered_df['year'] == latest_year].iloc[0]
max_anomaly = filtered_df['anomaly'].max()
avg_anomaly = filtered_df['anomaly'].mean()

# ---- KPI CARDS ----
st.markdown(f"""
<div class="kpi-container">
    <div class="kpi-card red">
        <div class="kpi-icon">🌡️</div>
        <div class="kpi-label">Latest Anomaly</div>
        <div class="kpi-value">{latest['anomaly']:.3f}°C</div>
        <div class="kpi-sub">Recorded in {int(latest['year'])}</div>
    </div>
    <div class="kpi-card orange">
        <div class="kpi-icon">🔥</div>
        <div class="kpi-label">Highest Ever Recorded</div>
        <div class="kpi-value">{max_anomaly:.3f}°C</div>
        <div class="kpi-sub">All time peak anomaly</div>
    </div>
    <div class="kpi-card blue">
        <div class="kpi-icon">📊</div>
        <div class="kpi-label">Average Anomaly</div>
        <div class="kpi-value">{avg_anomaly:.3f}°C</div>
        <div class="kpi-sub">Across selected year range</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ---- AI BANNER ----
render_ai_banner("Temperature Anomalies")

st.markdown("---")

# ---- LINE CHART ----
st.subheader("Temperature Anomaly Over Time")
fig1 = px.line(
    filtered_df,
    x="year",
    y="anomaly",
    color="entity",
    labels={"anomaly": "Temperature Anomaly (°C)", "year": "Year", "entity": "Region"},
    template="plotly_dark",
    color_discrete_sequence=["#EF553B", "#636EFA", "#00CC96", "#AB63FA", "#FFA15A"]
)
fig1.add_hline(
    y=0,
    line_dash="dash",
    line_color="white",
    opacity=0.4,
    annotation_text="Baseline"
)
st.plotly_chart(fig1, use_container_width=True)

# ---- DECADE BAR CHART ----
st.subheader("Average Anomaly by Decade")
decade_df = filtered_df.copy()
decade_df['decade'] = (decade_df['year'] // 10) * 10
decade_grouped = decade_df.groupby('decade')['anomaly'].mean().reset_index()

fig2 = px.bar(
    decade_grouped,
    x="decade",
    y="anomaly",
    labels={"anomaly": "Avg Anomaly (°C)", "decade": "Decade"},
    template="plotly_dark",
    color="anomaly",
    color_continuous_scale="RdYlBu_r"
)
st.plotly_chart(fig2, use_container_width=True)

# ---- DOWNLOAD DATA ----
st.markdown("---")
csv = filtered_df.to_csv(index=False).encode('utf-8')
st.download_button(
    label="📥 Download Filtered Data as CSV",
    data=csv,
    file_name="temperature_anomaly_data.csv",
    mime="text/csv"
)

# ---- RAW DATA ----
if st.checkbox("Show raw data"):
    st.dataframe(filtered_df[['entity', 'year', 'anomaly']].reset_index(drop=True))

from chatbot_widget import render_ai_banner, render_sidebar_chat

# at the very bottom of each page:
render_sidebar_chat("Temperature Anomalies")  # change context per page