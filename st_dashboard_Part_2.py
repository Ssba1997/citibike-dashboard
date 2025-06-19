# -------------------- Imports --------------------
import streamlit as st
import pandas as pd
import numpy as np
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from PIL import Image
import streamlit.components.v1 as components

# -------------------- Page Config --------------------
st.set_page_config(page_title='Citi Bike Dashboard NYC', layout='wide')

# -------------------- Sidebar Navigation --------------------
page = st.sidebar.selectbox('🚲 Select an aspect of the analysis',
   ["Intro page",
    "📈 Weather component and bike usage",
    "📊 Most popular stations",
    "🗺️ Interactive map with aggregated bike trips",
    "✅ Recommendations"])

# -------------------- Load Data --------------------
df = pd.read_csv("reduced_data_to_plot_7.csv")

# -------------------- Intro Page --------------------
if page == "Intro page":
    st.title("🚲 Citi Bike Strategy Dashboard - NYC")
    st.markdown("#### This dashboard provides insights on New York Citi Bike's supply challenges and usage trends.")
    st.markdown("""
    This analysis investigates customer complaints about bike unavailability. 
    It focuses on:
    - Most popular stations
    - Seasonality and temperature correlation
    - Aggregated bike trip routes (Kepler.gl)
    - Strategic recommendations for supply optimization
    
    Use the sidebar to explore the analysis sections.
    """)
    image = Image.open("recs_page.jpg")
    st.image(image, use_column_width=True)

# -------------------- Line Chart Page --------------------
elif page == "📈 Weather component and bike usage":
    st.subheader("📈 Daily Bike Trips vs Temperature")
    fig_line = make_subplots(specs=[[{"secondary_y": True}]])

    fig_line.add_trace(
        go.Scatter(x=df['date'], y=df['value'], name='Daily Bike Rides', line=dict(color='blue')),
        secondary_y=False
    )

    fig_line.add_trace(
        go.Scatter(x=df['date'], y=df['avg_temp'], name='Average Temperature', line=dict(color='red')),
        secondary_y=True
    )

    fig_line.update_layout(
        title='Daily Bike Trips and Temperatures in 2022',
        xaxis_title='Date',
        yaxis_title='Bike Rides',
        yaxis2_title='Avg Temperature (°F)',
        height=600
    )

    st.plotly_chart(fig_line, use_container_width=True)
    st.markdown("""
    🔍 **Insight:** There is a strong positive correlation between temperature and bike usage.
    Colder months show lower usage, while warmer months (May to October) experience peak activity.
    """)

# -------------------- Bar Chart Page --------------------
elif page == "📊 Most popular stations":
    with st.sidebar:
        season_filter = st.multiselect('🗓️ Select the season:', options=df['season'].unique(),
                                       default=df['season'].unique())

    df1 = df.query('season == @season_filter')
    df1['value'] = 1
    df_groupby_bar = df1.groupby('start_station_name', as_index=False).agg({'value': 'sum'})
    top20 = df_groupby_bar.nlargest(20, 'value')

    total_rides = int(df1['value'].sum())
    st.metric(label='📌 Total Bike Rides (Filtered)', value=f"{total_rides:,}")

    fig_bar = go.Figure(go.Bar(
        x=top20['start_station_name'],
        y=top20['value'],
        marker={'color': top20['value'], 'colorscale': 'Blues'}
    ))

    fig_bar.update_layout(
        title='Top 20 Most Popular Start Stations',
        xaxis_title='Start Station',
        yaxis_title='Number of Trips',
        width=1000, height=600
    )

    st.plotly_chart(fig_bar, use_container_width=True)
    st.markdown("""
    📌 **Insight:** Most rides originate from a few key stations such as Streeter Dr & Grand Ave, Clinton St & Madison St, and Canal St & Adams St. 
    Consider boosting supply at these hubs, especially during peak seasons.
    """)

# -------------------- Map Page --------------------
elif page == "🗺️ Interactive map with aggregated bike trips":
    st.subheader("🗺️ Aggregated Bike Trips - NYC")
    try:
        with open("NYC_Bike_Trips_Map.html", "r", encoding="utf-8") as f:
            html_data = f.read()
        components.html(html_data, height=1000)
        st.markdown("""
        📍 The map visualizes aggregated trips across the city. Major flows occur between lakeside stations and central tourist locations.
        These insights are crucial for optimizing route planning and seasonal supply allocation.
        """)
    except FileNotFoundError:
        st.error("Map file not found. Please make sure 'NYC_Bike_Trips_Map.html' is in the same folder.")

# -------------------- Recommendations Page --------------------
else:
    st.header("✅ Final Recommendations & Strategy Insights")
    try:
        image = Image.open("recs_page.jpg")
        st.image(image, caption="📷 Citi Bike NYC", use_column_width=True)
    except:
        st.warning("Image 'recs_page.jpg' not found. Skipping image display.")

    st.markdown("""
    ### 🚀 Strategic Recommendations

    ✅ **Focus Station Expansion:**
    - Add more docks at stations near waterfronts and tourist hubs:
      - 🎯 Streeter Dr & Grand Ave
      - 🎯 Millennium Park
      - 🎯 Canal St & Adams St

    ✅ **Seasonal Stocking Strategy:**
    - 🥶 Reduce supply during winter months (Nov–Mar)
    - ☀️ Increase stocking in summer and early fall

    ✅ **Route Planning & Redistribution:**
    - Use trip frequency data to plan optimized redistribution cycles
    - Consider heatmaps from Kepler.gl for predictive adjustments

    ✅ **Customer Experience:**
    - 🕒 Add real-time availability features at high-demand stations
    - 📲 Promote mobile app alerts for station status

    ---
    🔄 Analysis based on 2022 Citi Bike trip data and NOAA weather patterns.
    """)
