# -------------------- Imports --------------------
import streamlit as st
import pandas as pd
import numpy as np
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from PIL import Image
import streamlit.components.v1 as components

# -------------------- Page Config --------------------
st.set_page_config(page_title='🚴 Citi Bike Strategy Dashboard', layout='wide')
st.title("🚴‍♀️ New York Citi Bike Strategy Dashboard")
st.markdown("""
Welcome to the interactive strategy dashboard designed to guide improvements for the Citi Bike system in New York City 🚲.  
This tool reveals usage patterns, seasonal effects, and popular locations to help address key supply challenges.
""")

# -------------------- Sidebar Page Selector --------------------
page = st.sidebar.selectbox('🔎 Explore Analysis Sections:',
    ["🏠 Introduction",  
     "📈 Bike Usage vs Weather",
     "📊 Top Stations Analysis",
     "🗺️ Interactive Trip Map",
     "✅ Final Recommendations"])

# -------------------- Load Data --------------------
df = pd.read_csv('reduced_data_to_plot_7.csv', encoding='utf-8')

# -------------------- Page 1: Introduction --------------------
if page == "🏠 Introduction":
    st.header("📋 Project Overview & Objectives")
    st.markdown("""
    Citi Bike is facing a recurring issue: 🚴‍♂️ **bike shortages during peak demand periods**.  
    This dashboard presents findings from our 2022 analysis of NYC trip data and weather conditions.
    
    #### 🔍 What you’ll find inside:
    - 📊 **Most Popular Stations** – discover where demand is highest
    - 📈 **Weather vs Usage** – see seasonal patterns
    - 🗺️ **Interactive Map** – explore top trips visually
    - ✅ **Final Strategy** – targeted improvements for station supply

    Use the dropdown in the sidebar ⬅️ to navigate through insights.
    """)

    try:
        image = Image.open("intro_bike.jpg")
        st.image(image, caption="Image: Bike NYC | Unsplash", use_column_width=True)
    except:
        st.info("📸 Optional image not found — skipping display.")

# -------------------- Page 2: Line Chart --------------------
elif page == "📈 Bike Usage vs Weather":
    st.header("📈 Daily Bike Rides vs Temperature")
    fig_line = make_subplots(specs=[[{"secondary_y": True}]])

    fig_line.add_trace(
        go.Scatter(x=df['date'], y=df['value'], name='🚲 Daily Bike Rides', line=dict(color='blue')),
        secondary_y=False
    )

    fig_line.add_trace(
        go.Scatter(x=df['date'], y=df['avg_temp'], name='🌡️ Avg Temperature (°F)', line=dict(color='red')),
        secondary_y=True
    )

    fig_line.update_layout(
        title='📆 Bike Usage and Temperature Trends – 2022',
        xaxis_title='Date',
        yaxis_title='Bike Rides',
        yaxis2_title='Avg Temp (°F)',
        height=600
    )

    st.plotly_chart(fig_line, use_container_width=True)
    st.markdown("""
    ❄️ As temperatures drop, bike usage falls.  
    ☀️ Usage peaks in warmer months — particularly **May to October** — suggesting that resource allocation should vary **seasonally**.
    """)

# -------------------- Page 3: Bar Chart with Season Filter --------------------
elif page == "📊 Top Stations Analysis":
    st.header("📊 Most Popular Start Stations (Filtered by Season)")

    with st.sidebar:
        season_filter = st.multiselect('🗓️ Filter by Season:', options=df['season'].unique(), default=df['season'].unique())

    df1 = df.query('season == @season_filter')
    total_rides = int(df1['value'].sum())
    st.metric(label='🚴 Total Filtered Rides', value=f"{total_rides:,}")

    df_group = df1.groupby('start_station_name', as_index=False)['value'].sum()
    top20 = df_group.nlargest(20, 'value')

    fig_bar = go.Figure(go.Bar(
        x=top20['start_station_name'],
        y=top20['value'],
        marker={'color': top20['value'], 'colorscale': 'Blues'}
    ))

    fig_bar.update_layout(
        title='🔝 Top 20 Start Stations in NYC',
        xaxis_title='Start Station',
        yaxis_title='Number of Trips',
        height=600
    )

    st.plotly_chart(fig_bar, use_container_width=True)
    st.markdown("""
    📌 Stations like **Streeter Dr / Grand Ave** and **Canal St / Adams St** consistently top the charts.  
    This indicates **central hubs** that may require **more frequent rebalancing** or **larger docks** during peak seasons.
    """)

# -------------------- Page 4: Map --------------------
elif page == "🗺️ Interactive Trip Map":
    st.header("🗺️ Aggregated Bike Trip Map – Explore Routes Visually")

    try:
        with open("NYC_Bike_Trips_Map.html", "r", encoding="utf-8") as f:
            html_data = f.read()
        components.html(html_data, height=1000)
    except FileNotFoundError:
        st.error("🚫 Map file not found. Ensure 'NYC_Bike_Trips_Map.html' exists.")

    st.markdown("""
    📍 **Map Insights**:  
    - Most frequent routes connect high-footfall zones, especially near the **waterfront** and **tourist areas**.
    - Common start stations often do **not** correspond to the most frequent **trip combinations**.
    
    ✅ **Recommendation**:  
    Adjust **trip-level rebalancing** — not just per-station — especially during **summer weekends**.
    """)

# -------------------- Page 5: Recommendations --------------------
else:
    st.header("✅ Final Strategy Recommendations")
    try:
        bikes = Image.open("recs_page.jpg")
        st.image(bikes, use_column_width=True)
    except:
        st.info("📸 Recommendation image not found — skipping display.")

    st.markdown("""
    ### 🎯 Strategic Actions Moving Forward:
    - 🧭 **Install more docks** near:
      - 🎭 Theater on the Lake  
      - 🌊 Streeter Dr / Grand Ave  
      - 🏞️ Millennium Park  
      - 🐟 Shedd Aquarium  
      - 🛍️ Michigan Ave / Oak St  
    - 📦 **Reallocate inventory** seasonally:
      - Boost supply from **May–October**  
      - Reduce logistics in colder months
    - 📊 **Track usage trends** with:
      - Real-time dashboards  
      - Route-specific heatmaps
    - ⚖️ **Balance trip flow**, not just station popularity
    - 🚴‍♀️ **Improve user experience** with predictive demand models
    """)