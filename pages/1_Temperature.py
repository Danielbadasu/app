import streamlit as st
import pandas as pd
import plotly.express as px

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
.kpi-card.red::before   { background: linear-gradient(90deg, #ff416c, #ff4b2b); box-shadow: 0 0 20px #ff416c; }
.kpi-card.orange::before { background: linear-gradient(90deg, #f7971e, #ffd200); box-shadow: 0 0 20px #f7971e; }
.kpi-card.blue::before  { background: linear-gradient(90deg, #4facfe, #00f2fe); box-shadow: 0 0 20px #4facfe; }
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
.kpi-card.red   .kpi-value { color: #ff6b8a; }
.kpi-card.orange .kpi-value { color: #ffd200; }
.kpi-card.blue  .kpi-value { color: #4facfe; }
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

# ---- SIDEBAR ----
st.sidebar.header("Filters")
entities = df['entity'].unique().tolist()
selected_entity = st.sidebar.selectbox("Select Region", options=entities)

# ---- FILTER ----
filtered_df = df[df['entity'] == selected_entity]

# ---- KPI VALUES ----
latest = filtered_df[filtered_df['year'] == filtered_df['year'].max()].iloc[0]
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
        <div class="kpi-sub">Across all recorded years</div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# ---- LINE CHART ----
st.subheader("Temperature Anomaly Over Time")
fig1 = px.line(
    filtered_df,
    x="year",
    y="anomaly",
    labels={"anomaly": "Temperature Anomaly (°C)", "year": "Year"},
    template="plotly_dark",
    color_discrete_sequence=["#EF553B"]
)
fig1.add_hline(y=0, line_dash="dash", line_color="white", opacity=0.4, annotation_text="Baseline")
st.plotly_chart(fig1, use_container_width=True)

# ---- DECADE BAR CHART ----
st.subheader("Average Anomaly by Decade")
filtered_df = filtered_df.copy()
filtered_df['decade'] = (filtered_df['year'] // 10) * 10
decade_df = filtered_df.groupby('decade')['anomaly'].mean().reset_index()

fig2 = px.bar(
    decade_df,
    x="decade",
    y="anomaly",
    labels={"anomaly": "Avg Anomaly (°C)", "decade": "Decade"},
    template="plotly_dark",
    color="anomaly",
    color_continuous_scale="RdYlBu_r"
)
st.plotly_chart(fig2, use_container_width=True)

# ---- RAW DATA ----
if st.checkbox("Show raw data"):
    st.dataframe(filtered_df[['entity', 'year', 'anomaly']].reset_index(drop=True))