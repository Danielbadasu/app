import streamlit as st
import pandas as pd
import plotly.express as px
from chatbot_widget import render_ai_banner, render_sidebar_chat, render_disclaimer

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
st.markdown("Tracking how surface temperatures have changed country by country since 1961.")

# ---- LOAD DATA ----
@st.cache_data
def load_temp_data():
    url = "https://raw.githubusercontent.com/owid/owid-datasets/master/datasets/Annual%20average%20surface%20temperatures%20by%20country/Annual%20average%20surface%20temperatures%20by%20country.csv"
    df = pd.read_csv(url)
    df.columns = [c.strip() for c in df.columns]
    df = df.rename(columns={
        df.columns[0]: "country",
        df.columns[1]: "year",
        df.columns[2]: "temperature"
    })
    return df

df = load_temp_data()

# ---- CONTINENT MAPPING ----
continent_map = {
    'Africa': ['Nigeria', 'Ethiopia', 'Kenya', 'Ghana', 'Tanzania', 'Uganda',
               'Mozambique', 'Madagascar', 'Cameroon', 'Angola', 'Niger',
               'Burkina Faso', 'Mali', 'Malawi', 'Zambia', 'Chad', 'Somalia',
               'Zimbabwe', 'Guinea', 'Rwanda', 'Benin', 'Burundi', 'Tunisia',
               'South Africa', 'Egypt', 'Algeria', 'Morocco', 'Sudan',
               'Democratic Republic of Congo', 'Ivory Coast', 'Senegal'],
    'Asia': ['China', 'India', 'Indonesia', 'Pakistan', 'Bangladesh',
             'Japan', 'Philippines', 'Vietnam', 'Iran', 'Thailand',
             'Myanmar', 'South Korea', 'Iraq', 'Afghanistan', 'Saudi Arabia',
             'Uzbekistan', 'Malaysia', 'Yemen', 'Nepal', 'Sri Lanka',
             'Cambodia', 'Jordan', 'Azerbaijan', 'Tajikistan', 'Israel',
             'Laos', 'Singapore', 'Kuwait', 'Qatar', 'United Arab Emirates'],
    'Europe': ['Russia', 'Germany', 'United Kingdom', 'France', 'Italy',
               'Spain', 'Ukraine', 'Poland', 'Romania', 'Netherlands',
               'Belgium', 'Sweden', 'Czech Republic', 'Greece', 'Portugal',
               'Hungary', 'Belarus', 'Austria', 'Switzerland', 'Bulgaria',
               'Denmark', 'Finland', 'Norway', 'Slovakia', 'Ireland',
               'Croatia', 'Bosnia and Herzegovina', 'Albania', 'Lithuania'],
    'Americas': ['United States', 'Brazil', 'Mexico', 'Colombia', 'Argentina',
                 'Canada', 'Peru', 'Venezuela', 'Chile', 'Ecuador',
                 'Bolivia', 'Paraguay', 'Uruguay', 'Cuba', 'Haiti',
                 'Dominican Republic', 'Honduras', 'Guatemala', 'El Salvador',
                 'Nicaragua', 'Costa Rica', 'Panama', 'Jamaica', 'Trinidad and Tobago'],
    'Oceania': ['Australia', 'Papua New Guinea', 'New Zealand', 'Fiji',
                'Solomon Islands', 'Vanuatu', 'Samoa', 'Kiribati', 'Tonga']
}

def get_continent(country):
    for continent, countries in continent_map.items():
        if country in countries:
            return continent
    return 'Other'

df['continent'] = df['country'].apply(get_continent)

available_countries = sorted(df['country'].dropna().unique().tolist())
available_continents = ['All'] + sorted(df['continent'].unique().tolist())

# ---- SIDEBAR FILTERS ----
st.sidebar.header("Filters")

selected_continent = st.sidebar.selectbox(
    "Filter by Continent",
    options=available_continents
)

if selected_continent == 'All':
    country_options = available_countries
else:
    country_options = sorted(
        df[df['continent'] == selected_continent]['country'].unique().tolist()
    )

selected_countries = st.sidebar.multiselect(
    "Select Countries",
    options=country_options,
    default=country_options[:3] if len(country_options) >= 3 else country_options
)

if not selected_countries:
    selected_countries = country_options[:3]

year_range = st.sidebar.slider(
    "Select Year Range",
    min_value=int(df['year'].min()),
    max_value=int(df['year'].max()),
    value=(int(df['year'].min()), int(df['year'].max()))
)

st.sidebar.markdown("---")
st.sidebar.markdown(f"**📊 Showing:** {year_range[0]} – {year_range[1]}")
st.sidebar.markdown(f"**🌍 Continent:** {selected_continent}")

# ---- FILTER ----
filtered_df = df[
    (df['country'].isin(selected_countries)) &
    (df['year'].between(year_range[0], year_range[1]))
]

if filtered_df.empty:
    st.warning("⚠️ No data found for the selected filters. Please adjust your selection.")
    st.stop()

# ---- KPI VALUES ----
latest_year = filtered_df['year'].max()
latest_df = filtered_df[filtered_df['year'] == latest_year]
avg_latest = latest_df['temperature'].mean()
max_temp = filtered_df['temperature'].max()
max_temp_country = filtered_df.loc[filtered_df['temperature'].idxmax(), 'country']
avg_temp = filtered_df['temperature'].mean()

# ---- KPI CARDS ----
st.markdown(f"""
<div class="kpi-container">
    <div class="kpi-card red">
        <div class="kpi-icon">🌡️</div>
        <div class="kpi-label">Latest Avg Temperature</div>
        <div class="kpi-value">{avg_latest:.2f}°C</div>
        <div class="kpi-sub">Across selected countries in {int(latest_year)}</div>
    </div>
    <div class="kpi-card orange">
        <div class="kpi-icon">🔥</div>
        <div class="kpi-label">Highest Recorded</div>
        <div class="kpi-value">{max_temp:.2f}°C</div>
        <div class="kpi-sub">{max_temp_country} — all time peak</div>
    </div>
    <div class="kpi-card blue">
        <div class="kpi-icon">📊</div>
        <div class="kpi-label">Average Temperature</div>
        <div class="kpi-value">{avg_temp:.2f}°C</div>
        <div class="kpi-sub">Across selected countries & period</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ---- AI BANNER ----
render_ai_banner("Temperature Anomalies")

st.markdown("---")

# ---- LINE CHART ----
st.subheader("Average Surface Temperature Over Time")
fig1 = px.line(
    filtered_df,
    x="year",
    y="temperature",
    color="country",
    labels={"temperature": "Avg Surface Temp (°C)", "year": "Year", "country": "Country"},
    template="plotly_dark"
)
st.plotly_chart(fig1, use_container_width=True)

# ---- DECADE BAR CHART ----
st.subheader("Average Temperature by Decade")
decade_df = filtered_df.copy()
decade_df['decade'] = (decade_df['year'] // 10) * 10
decade_grouped = decade_df.groupby('decade')['temperature'].mean().reset_index()

fig2 = px.bar(
    decade_grouped,
    x="decade",
    y="temperature",
    labels={"temperature": "Avg Temp (°C)", "decade": "Decade"},
    template="plotly_dark",
    color="temperature",
    color_continuous_scale="RdYlBu_r"
)
st.plotly_chart(fig2, use_container_width=True)

# ---- DOWNLOAD DATA ----
st.markdown("---")
csv = filtered_df.to_csv(index=False).encode('utf-8')
st.download_button(
    label="📥 Download Filtered Data as CSV",
    data=csv,
    file_name="temperature_data.csv",
    mime="text/csv"
)

# ---- RAW DATA ----
if st.checkbox("Show raw data"):
    st.dataframe(filtered_df[['country', 'year', 'temperature']].reset_index(drop=True))

# ---- DISCLAIMER ----
render_disclaimer("Temperature Anomalies")

# ---- SIDEBAR CHAT ----
render_sidebar_chat("Temperature Anomalies")
