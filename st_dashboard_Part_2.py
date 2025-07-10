# -------------------- Imports --------------------
import streamlit as st
import pandas as pd
import numpy as np
import warnings
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from PIL import Image
import streamlit.components.v1 as components
import os

# -------------------- Suppress Python Warnings --------------------
warnings.filterwarnings("ignore")

# -------------------- Page Config (must be FIRST Streamlit command) --------------------
st.set_page_config(page_title='🚴 Citi Bike Strategy Dashboard', layout='wide')

# -------------------- CSS to reduce bottom margin after markdown --------------------
st.markdown("""
<style>
    .stApp div[data-testid="stMarkdownContainer"] {
        margin-bottom: 0rem;
    }
</style>
""", unsafe_allow_html=True)

# -------------------- Title & Intro --------------------
st.title("🚴‍♀️ New York Citi Bike Strategy Dashboard")
st.markdown("""
Welcome to this interactive dashboard analyzing Citi Bike usage patterns across New York City in 2022.  
Use the sidebar to explore sections and apply filters. All visualizations respond dynamically to your selections.
""")

# -------------------- Sidebar Navigation --------------------
page = st.sidebar.selectbox('🔎 Select a Section:',
    ["🏠 Introduction",  
     "📈 Bike Usage vs Weather",
     "📊 Top Stations Analysis",
     "🗺️ Interactive Trip Map",
     "✅ Final Recommendations"])

# -------------------- Define base path for files --------------------
BASE_PATH = "."

# -------------------- Load Dataset --------------------
try:
    df = pd.read_csv(os.path.join(BASE_PATH, 'reduced_data_to_plot_7.csv'), encoding='utf-8')
except FileNotFoundError:
    st.error("⚠️ Data file 'reduced_data_to_plot_7.csv' not found. Please ensure it exists in the folder.")
    st.stop()

# -------------------- Page 1: Introduction --------------------
if page == "🏠 Introduction":
    st.header("📋 Project Goals & Navigation Guide")
    st.markdown("""
### 🌟 Goal:
Help Citi Bike address **bike shortages during peak periods** and optimize **station coverage** based on real data.

### 🧭 How to Use:
- Use the **sidebar** to navigate sections.
- Apply **season filters** on charts for detailed views.
- Look for **numerical insights** and visual highlights.
- Scroll down for images and recommendations.
    """)
    try:
        image = Image.open(os.path.join(BASE_PATH, "intro_bike.jpg"))
        st.image(image, caption="📸 Image: Bike NYC", use_column_width=True)
    except FileNotFoundError:
        st.info("📷 Intro image not found. Skipping visual.")

# -------------------- Page 2: Bike Usage vs Weather --------------------
elif page == "📈 Bike Usage vs Weather":
    st.header("📈 Bike Rides vs. Temperature – 2022 Trends")
    st.markdown("""
🛠 **Instructions:**  
- This chart shows daily bike rides compared to average temperature.  
- Use it to understand how weather affects ridership patterns.

📌 **Why it matters:**  
- Shows peak usage during comfortable temperatures.  
- Helps plan seasonal bike availability and marketing campaigns.
    """)
    fig_line = make_subplots(specs=[[{"secondary_y": True}]])
    fig_line.add_trace(
        go.Scatter(x=df['date'], y=df['value'], name='🚲 Bike Rides', line=dict(color='blue')),
        secondary_y=False
    )
    fig_line.add_trace(
        go.Scatter(x=df['date'], y=df['avg_temp'], name='🌡️ Avg Temperature (°F)', line=dict(color='red')),
        secondary_y=True
    )
    fig_line.update_layout(
        title='📊 Daily Citi Bike Usage vs Avg Temperature (2022)',
        xaxis_title='Date',
        yaxis_title='Bike Rides',
        yaxis2_title='Average Temp (°F)',
        height=650
    )
    st.plotly_chart(fig_line, use_container_width=True)

    # Monthly summary table
    monthly_summary = df.groupby('month')[['value', 'avg_temp']].agg({'value':'sum', 'avg_temp':'mean'}).reset_index()
    monthly_summary.columns = ['Month', 'Total Rides', 'Avg Temperature (°F)']
    st.subheader("📅 Monthly Ride Summary")
    st.dataframe(monthly_summary.style.format({'Total Rides': '{:,}', 'Avg Temperature (°F)': '{:.1f}'}), use_container_width=True)

    st.markdown("""
### 🔍 Deeper Insights:
- 🧊 **Cold Weather (< 40°F):**  
  Nov–Feb had under **30,000 rides/month** on average.  
- 🌤️ **Comfort Zone (60–75°F):**  
  April–June and Sept–Oct saw strong demand.  
- 🔥 **Hot Days (> 85°F):**  
  July/August peaked at over **300,000 rides/month**.

### ✅ Actionable Strategy:
- Increase fleet size by **25–35%** during **May–October**.  
- Consider winter promotions to boost off-season usage.
    """)

# -------------------- Page 3: Top Stations Analysis --------------------
elif page == "📊 Top Stations Analysis":
    st.header("📊 Explore Most Popular Start Stations")
    st.markdown("""
🛠 **Instructions:**  
- Use the season filter to explore station popularity by season.  
- Results update dynamically to show the top 20 stations by ride count.

📌 **Why it matters:**  
- Highlights where bike shortages or dock overcrowding happen.
    """)

    # Extended season filter options
    available_seasons = list(df['season'].unique())
    extended_seasons = list(set(available_seasons + ['Spring', 'Summer', 'Rainy', 'Winter']))

    with st.sidebar:
        season_filter = st.multiselect(
            '🗓️ Filter by Season:',
            options=extended_seasons,
            default=extended_seasons
        )

    df_filtered = df[df['season'].isin(season_filter)]
    total_rides = int(df_filtered['value'].sum())
    st.metric(label='🚴 Total Rides (Filtered)', value=f"{total_rides:,}")

    df_grouped = df_filtered.groupby('start_station_name', as_index=False)['value'].sum()
    top20 = df_grouped.nlargest(20, 'value')

    fig_bar = go.Figure(go.Bar(
        x=top20['start_station_name'],
        y=top20['value'],
        marker={'color': top20['value'], 'colorscale': 'Blues'}
    ))
    fig_bar.update_layout(
        title='📍 Top 20 Start Stations',
        xaxis_title='Station Name',
        yaxis_title='Trip Count',
        height=600
    )
    st.plotly_chart(fig_bar, use_container_width=True)

    st.markdown(f"""
### 🔑 Key Insight:
- **{top20.iloc[0]['start_station_name']}** tops with **{int(top20.iloc[0]['value']):,} rides**.
- The top 5 stations combined have over **220,000 rides**.

### ✅ Recommendation:
- Install **larger or dual docks** at these high-demand stations.
- Implement **live rebalancing alerts** during peak seasons.
    """)

# -------------------- Page 4: Interactive Trip Map --------------------
elif page == "🗺️ Interactive Trip Map":
    st.header("🗺️ Visualize Citi Bike Routes in NYC")
    st.markdown("""
🛠 **Instructions:**  
- Scroll and zoom to explore popular bike routes on the map.  
- Lines show most frequent paths between stations.

📌 **Why it matters:**  
- Identifies key corridors and underserved areas.
    """)

    try:
        with open(os.path.join(BASE_PATH, "NYC_Bike_Trips_Map.html"), "r", encoding="utf-8") as f:
            html_data = f.read()
        components.html(html_data, height=1400)  # Bigger map height
    except FileNotFoundError:
        st.error("📍 Map file not found. Please place 'NYC_Bike_Trips_Map.html' in the folder.")

    with st.container():
        st.markdown("""
### 🔑 Map Insights:
- High traffic between Midtown, SoHo, and Battery Park.
- Frequent trips near Hudson River Greenway and tourist spots.

### ✅ Recommendation:
- Enhance rebalancing efforts around high-traffic corridors.
- Optimize route efficiency to reduce empty return trips.
        """)

# -------------------- Page 5: Final Recommendations --------------------
else:
    st.header("✅ Final Strategy Recommendations")
    st.markdown("""
🛠 **Instructions:**  
- Review these data-driven strategies designed to improve rider experience and operational efficiency.
    """)

    try:
        bikes_img = Image.open(os.path.join(BASE_PATH, "recs_page.jpg"))
        st.image(bikes_img, caption="📸 Strategy Highlights", use_column_width=True)
    except FileNotFoundError:
        st.info("📷 Recommendation image not found. Skipping visual.")

    st.markdown("""
### 📌 Action Plan Summary:

#### 🏗️ Infrastructure:
- Install **30–50% more docks** at key locations including Theater on the Lake, Shedd Aquarium, and Streeter Dr / Grand Ave.
- Expand dock size at the 5 busiest stations.

#### 🔄 Inventory & Logistics:
- Increase bike supply by **25% from May to October**.
- Reduce staffing and logistics by **40% in January and February**.

#### 📊 Data-Driven Operations:
- Launch **real-time dashboards** with weather overlays.
- Use **AI demand forecasting** to optimize bike distribution.

#### 🔄 Trip Flow Balancing:
- Focus on one-way trip volumes, not just station popularity.
- Implement dynamic bike rebalancing based on trip data.
    """)