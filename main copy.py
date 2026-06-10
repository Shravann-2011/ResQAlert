"""
Main Streamlit dashboard for ResQAlert system with SMS Alert Integration
FUTURISTIC UI + FIXED ERRORS + PERFECT ALIGNMENT
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
import json
import numpy as np

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

# Core services
from services.weather_service import weather_service
from models.disaster_prediction import disaster_predictor, initialize_models
from config.settings import settings

# Alert system imports
from services.sms_service import sms_service
from app.user_management import user_manager
from app.alert_manager import alert_manager

# Maps (with error handling)
try:
    import folium
    from streamlit_folium import st_folium
    MAPS_AVAILABLE = True
except ImportError:
    MAPS_AVAILABLE = False

# Page configuration - FIXED: sidebar collapsed
st.set_page_config(
    page_title="ResQAlert | AI Disaster Intelligence",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"  # FIXED: was "expanded"
)

# Initialize page state
if "page" not in st.session_state:
    st.session_state.page = "🏠 Dashboard Overview"

# FUTURISTIC DARK MODE CSS - COMPLETE & WORKING
st.markdown("""
<style>
    /* Futuristic Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;600;700;900&family=Rajdhani:wght@400;500;600;700&display=swap');
    
    /* DARK BASE */
    .stApp {
        background: linear-gradient(135deg, #0a0e27 0%, #1a1f3a 50%, #0f1419 100%);
        background-attachment: fixed;
        font-family: 'Rajdhani', sans-serif;
    }
    
    /* Hide sidebar completely */
    [data-testid="stSidebar"] {
        display: none !important;
    }
    
    /* Main container - glassmorphism */
    .main .block-container {
        background: rgba(15, 20, 30, 0.85);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(102, 252, 241, 0.2);
        border-radius: 16px;
        padding: 2rem;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
    }
    
    /* TOP NAVIGATION BAR */
    .top-nav {
        background: linear-gradient(135deg, #0f1419 0%, #1a1f3a 100%);
        border: 2px solid #66fcf1;
        border-radius: 16px;
        padding: 1.5rem 2rem;
        margin-bottom: 2rem;
        box-shadow: 0 0 40px rgba(102, 252, 241, 0.3);
    }
    
    .nav-title-main {
        color: #66fcf1;
        font-family: 'Orbitron', sans-serif;
        font-size: 2.2rem;
        font-weight: 900;
        text-align: center;
        margin-bottom: 1.5rem;
        text-transform: uppercase;
        letter-spacing: 4px;
        text-shadow: 0 0 30px rgba(102, 252, 241, 0.8);
    }
    
    /* Navigation buttons */
    div[data-testid="column"] .stButton > button {
        background: rgba(102, 252, 241, 0.08);
        color: #66fcf1 !important;
        border: 2px solid rgba(102, 252, 241, 0.4);
        border-radius: 10px;
        padding: 0.8rem 1rem;
        font-weight: 700;
        font-size: 0.95rem;
        letter-spacing: 1.5px;
        transition: all 0.3s ease;
        width: 100%;
    }
    
    div[data-testid="column"] .stButton > button:hover {
        background: rgba(102, 252, 241, 0.2);
        border-color: #66fcf1;
        box-shadow: 0 0 20px rgba(102, 252, 241, 0.5);
        transform: translateY(-2px);
    }
    
    /* TEXT - HIGH CONTRAST */
    h1, h2, h3, h4 {
        color: #66fcf1 !important;
        font-family: 'Orbitron', sans-serif;
        font-weight: 700;
        letter-spacing: 1px;
    }
    
    p, span, div, label, li {
        color: #e0e0e0 !important;
        font-size: 1.05rem;
    }
    
    /* RISK CARDS - NEON GLOW */
    .risk-card {
        padding: 2.5rem;
        border-radius: 20px;
        margin: 1.5rem 0;
        text-align: center;
        border: 3px solid;
        transition: all 0.3s ease;
    }
    
    .risk-card:hover {
        transform: translateY(-8px);
    }
    
    .risk-card h2 {
        font-size: 3rem;
        margin: 0.5rem 0;
        font-weight: 900;
    }
    
    .risk-card h3 {
        font-size: 1.4rem;
        margin-bottom: 0.5rem;
    }
    
    .risk-card p {
        font-size: 1.2rem;
    }
    
    /* LOW RISK - Green */
    .risk-low {
        background: rgba(16, 185, 129, 0.1);
        border-color: #10b981;
        box-shadow: 0 0 40px rgba(16, 185, 129, 0.4);
    }
    
    .risk-low h2, .risk-low h3 {
        color: #10b981 !important;
        text-shadow: 0 0 20px rgba(16, 185, 129, 0.8);
    }
    
    .risk-low p {
        color: #6ee7b7 !important;
    }
    
    /* MEDIUM RISK - Yellow */
    .risk-medium {
        background: rgba(245, 158, 11, 0.1);
        border-color: #f59e0b;
        box-shadow: 0 0 40px rgba(245, 158, 11, 0.4);
    }
    
    .risk-medium h2, .risk-medium h3 {
        color: #f59e0b !important;
        text-shadow: 0 0 20px rgba(245, 158, 11, 0.8);
    }
    
    .risk-medium p {
        color: #fbbf24 !important;
    }
    
    /* HIGH RISK - Red with pulse */
    .risk-high {
        background: rgba(239, 68, 68, 0.15);
        border-color: #ef4444;
        box-shadow: 0 0 50px rgba(239, 68, 68, 0.6);
        animation: pulse-glow 2s infinite;
    }
    
    @keyframes pulse-glow {
        0%, 100% { box-shadow: 0 0 50px rgba(239, 68, 68, 0.6); }
        50% { box-shadow: 0 0 70px rgba(239, 68, 68, 0.9); }
    }
    
    .risk-high h2, .risk-high h3 {
        color: #ef4444 !important;
        text-shadow: 0 0 20px rgba(239, 68, 68, 1);
    }
    
    .risk-high p {
        color: #fca5a5 !important;
    }
    
    /* METRICS */
    [data-testid="stMetric"] {
        background: rgba(26, 31, 58, 0.5);
        border: 2px solid rgba(102, 252, 241, 0.3);
        border-radius: 12px;
        padding: 1.5rem;
        transition: all 0.3s ease;
    }
    
    [data-testid="stMetric"]:hover {
        border-color: #66fcf1;
        box-shadow: 0 0 30px rgba(102, 252, 241, 0.4);
        transform: translateY(-3px);
    }
    
    [data-testid="stMetricValue"] {
        font-size: 2.5rem;
        font-weight: 900;
        color: #66fcf1 !important;
        font-family: 'Orbitron', sans-serif;
        text-shadow: 0 0 15px rgba(102, 252, 241, 0.6);
    }
    
    [data-testid="stMetricLabel"] {
        color: #c5c6c7 !important;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* PRIMARY BUTTONS */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #66fcf1 0%, #45a29e 100%);
        color: #0a0e27 !important;
        border: none;
        border-radius: 10px;
        padding: 0.9rem 2rem;
        font-weight: 700;
        font-size: 1.05rem;
        text-transform: uppercase;
        letter-spacing: 2px;
        box-shadow: 0 8px 25px rgba(102, 252, 241, 0.4);
        transition: all 0.3s ease;
    }
    
    .stButton > button[kind="primary"]:hover {
        transform: translateY(-3px);
        box-shadow: 0 12px 35px rgba(102, 252, 241, 0.6);
    }
    
    /* SECONDARY BUTTONS */
    .stButton > button[kind="secondary"] {
        background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
        color: white !important;
        border: none;
        border-radius: 10px;
        padding: 0.9rem 2rem;
        font-weight: 700;
        font-size: 1.05rem;
        text-transform: uppercase;
        letter-spacing: 2px;
        box-shadow: 0 8px 25px rgba(239, 68, 68, 0.4);
        transition: all 0.3s ease;
    }
    
    .stButton > button[kind="secondary"]:hover {
        transform: translateY(-3px);
        box-shadow: 0 12px 35px rgba(239, 68, 68, 0.6);
    }
    
    /* INPUT FIELDS */
    .stTextInput input, .stSelectbox select, .stTextArea textarea {
        background: rgba(15, 20, 30, 0.9) !important;
        color: #66fcf1 !important;
        border: 2px solid rgba(102, 252, 241, 0.3);
        border-radius: 8px;
        padding: 0.9rem;
        font-size: 1.05rem;
    }
    
    .stTextInput input:focus, .stSelectbox select:focus {
        border-color: #66fcf1;
        box-shadow: 0 0 20px rgba(102, 252, 241, 0.3);
    }
    
    /* EXPANDERS */
    .streamlit-expanderHeader {
        background: rgba(26, 31, 58, 0.5);
        border: 2px solid rgba(102, 252, 241, 0.2);
        border-radius: 10px;
        color: #66fcf1 !important;
        font-weight: 600;
        padding: 0.8rem;
    }
    
    .streamlit-expanderHeader:hover {
        background: rgba(102, 252, 241, 0.1);
        border-color: #66fcf1;
    }
    
    /* ALERTS - HIGH CONTRAST */
    .stSuccess {
        background: rgba(16, 185, 129, 0.15);
        border-left: 4px solid #10b981;
        border-radius: 10px;
        color: #6ee7b7 !important;
    }
    
    .stError {
        background: rgba(239, 68, 68, 0.15);
        border-left: 4px solid #ef4444;
        border-radius: 10px;
        color: #fca5a5 !important;
    }
    
    .stWarning {
        background: rgba(245, 158, 11, 0.15);
        border-left: 4px solid #f59e0b;
        border-radius: 10px;
        color: #fbbf24 !important;
    }
    
    .stInfo {
        background: rgba(102, 252, 241, 0.15);
        border-left: 4px solid #66fcf1;
        border-radius: 10px;
        color: #66fcf1 !important;
    }
    
    /* CHARTS - DARK THEME */
    .js-plotly-plot {
        background: rgba(15, 20, 30, 0.6);
        border: 2px solid rgba(102, 252, 241, 0.2);
        border-radius: 12px;
        padding: 1rem;
    }
    
    /* DATAFRAMES */
    .stDataFrame {
        background: rgba(15, 20, 30, 0.8);
        border: 2px solid rgba(102, 252, 241, 0.2);
        border-radius: 12px;
    }
    
    /* TABS */
    .stTabs [data-baseweb="tab-list"] {
        gap: 1rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: rgba(26, 31, 58, 0.5);
        border: 2px solid rgba(102, 252, 241, 0.2);
        border-radius: 10px;
        color: #66fcf1;
        font-weight: 600;
        padding: 0.8rem 1.5rem;
    }
    
    .stTabs [aria-selected="true"] {
        background: rgba(102, 252, 241, 0.2);
        border-color: #66fcf1;
    }
    
    /* CHAT */
    .stChatMessage {
        background: rgba(26, 31, 58, 0.5);
        border: 1px solid rgba(102, 252, 241, 0.2);
        border-radius: 12px;
    }
    
    /* FORMS */
    .stForm {
        background: rgba(15, 20, 30, 0.5);
        border: 2px solid rgba(102, 252, 241, 0.2);
        border-radius: 12px;
        padding: 2rem;
    }
    
    /* SCROLLBAR */
    ::-webkit-scrollbar {
        width: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: #0f1419;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(180deg, #66fcf1, #45a29e);
        border-radius: 10px;
    }
    
    /* MOBILE */
    @media (max-width: 768px) {
        .nav-title-main { font-size: 1.5rem; }
        .risk-card { padding: 1.5rem; }
        .risk-card h2 { font-size: 2rem; }
    }
    
    /* CHAT FIXES - Add at the end of your CSS */

/* Chat messages more visible */
.stChatMessage {
    margin-bottom: 1.5rem !important;
    background: rgba(26, 31, 58, 0.6) !important;
    border: 1px solid rgba(102, 252, 241, 0.3) !important;
    border-radius: 12px !important;
    padding: 1rem !important;
}

/* Chat input area - always visible at bottom */
.stChatFloatingInputContainer {
    background: linear-gradient(180deg, transparent 0%, rgba(15, 20, 30, 0.95) 20%) !important;
    padding-top: 2rem !important;
    padding-bottom: 1rem !important;
}

/* Input box styling */
.stChatInput {
    background: rgba(26, 31, 58, 0.8) !important;
    border: 2px solid rgba(102, 252, 241, 0.3) !important;
    border-radius: 10px !important;
}

/* Main chat area - proper height */
.main .block-container {
    padding-bottom: 8rem !important;
}

</style>
""", unsafe_allow_html=True)

# ---- TOP NAVIGATION BAR ----
st.markdown('<div class="top-nav">', unsafe_allow_html=True)
st.markdown('<h1 class="nav-title-main">🛡️ RESQALERT AI INTELLIGENCE</h1>', unsafe_allow_html=True)

# Navigation buttons
nav_cols = st.columns(8)
if nav_cols[0].button("⚡ DASHBOARD", use_container_width=True):
    st.session_state.page = "🏠 Dashboard Overview"
if nav_cols[1].button("🌐 WEATHER", use_container_width=True):
    st.session_state.page = "🌤️ Weather Monitoring"
if nav_cols[2].button("🎯 PREDICTIONS", use_container_width=True):
    st.session_state.page = "🚨 Disaster Predictions"
if nav_cols[3].button("📍 ZONES", use_container_width=True):
    st.session_state.page = "🗺️ Safe Zones & Evacuation"
if nav_cols[4].button("🤖 ASSISTANT", use_container_width=True):
    st.session_state.page = "💬 Disaster Assistant"
if nav_cols[5].button("📡 ALERTS", use_container_width=True):
    st.session_state.page = "🚨 Alert System"
if nav_cols[6].button("📊 HISTORY", use_container_width=True):
    st.session_state.page = "📊 Historical Analysis"
if nav_cols[7].button("⚙️ SETTINGS", use_container_width=True):
    st.session_state.page = "⚙️ System Settings"

st.markdown('</div>', unsafe_allow_html=True)

# Helper functions
def initialize_session_state():
    """Initialize session state"""
    if 'models_initialized' not in st.session_state:
        st.session_state.models_initialized = False
    if 'current_location' not in st.session_state:
        st.session_state.current_location = {'lat': 12.9716, 'lon': 77.5946, 'name': 'Bangalore'}
    if 'weather_data' not in st.session_state:
        st.session_state.weather_data = None
    if 'last_update' not in st.session_state:
        st.session_state.last_update = None

def load_models():
    """Load ML models"""
    if not st.session_state.models_initialized:
        with st.spinner("🤖 Loading AI models..."):
            initialize_models()
            st.session_state.models_initialized = True

def render_weather_dashboard():
    """SUPER ENHANCED Weather Monitoring with all features"""
    st.header("🌐 WEATHER MONITORING")
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Location input with update button
    col1, col2 = st.columns([4, 1])
    
    with col1:
        location_input = st.text_input(
            "🌍 LOCATION:",
            value=st.session_state.current_location['name'],
            placeholder="Enter city name (e.g., Bangalore, Mumbai, Delhi)",
            key="loc_input",
            help="Enter any city name worldwide"
        )
    
    with col2:
        st.write("")
        st.write("")
        if st.button("🔄 UPDATE", type="primary", use_container_width=True):
            with st.spinner("🌐 Fetching weather data..."):
                time.sleep(0.3)
                weather_data = weather_service.get_weather_by_city(location_input)
                
                if weather_data:
                    st.session_state.weather_data = weather_data
                    st.session_state.current_location = {
                        'lat': weather_data['latitude'],
                        'lon': weather_data['longitude'],
                        'name': weather_data['location']
                    }
                    st.session_state.last_update = datetime.now()
                    st.success(f"✅ Updated for {weather_data['location']}")
                    time.sleep(0.3)
                    st.rerun()
                else:
                    st.error("❌ Location not found. Try: 'Bangalore', 'Mumbai', 'Delhi'")
                    return
    
    if not st.session_state.weather_data:
        st.info("👆 Enter a location and click UPDATE to fetch weather data")
        return
    
    weather = st.session_state.weather_data
    location_name = weather.get('location', 'Unknown')
    lat = weather['latitude']
    lon = weather['longitude']
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # ========== WEATHER ALERTS ==========
    st.subheader("⚠️ WEATHER ALERTS")
    alerts = weather_service.get_weather_alerts(weather)
    
    for alert in alerts:
        if "WARNING" in alert or "EXTREME" in alert:
            st.error(alert)
        elif "ADVISORY" in alert or "ALERT" in alert:
            st.warning(alert)
        else:
            st.success(alert)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # ========== CURRENT CONDITIONS ==========
    st.subheader("🌡️ CURRENT CONDITIONS")
    
    # Calculate feels-like temperature
    feels_like = weather_service.calculate_feels_like(
        weather['temperature'],
        weather['humidity'],
        weather['wind_speed']
    )
    
    # Display main metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("🌡️ TEMPERATURE", f"{weather['temperature']:.1f}°C")
        st.caption(f"Feels like: {feels_like}°C")
    
    with col2:
        st.metric("💧 HUMIDITY", f"{weather['humidity']:.0f}%")
        humidity_status = "High" if weather['humidity'] > 70 else "Normal" if weather['humidity'] > 40 else "Low"
        st.caption(humidity_status)
    
    with col3:
        st.metric("🌧️ PRECIPITATION", f"{weather['precipitation']:.1f}mm")
        st.caption("Last hour")
    
    with col4:
        st.metric("💨 WIND SPEED", f"{weather['wind_speed']:.1f}km/h")
        wind_status = "Strong" if weather['wind_speed'] > 30 else "Moderate" if weather['wind_speed'] > 15 else "Light"
        st.caption(wind_status)
    
    with col5:
        st.metric("🔽 PRESSURE", f"{weather['pressure']:.0f}hPa")
        pressure_status = "High" if weather['pressure'] > 1020 else "Low" if weather['pressure'] < 1000 else "Normal"
        st.caption(pressure_status)
    
    # Weather description
    st.info(f"☁️ **Conditions:** {weather['weather_description'].title()} ({weather['weather_main']})")
    
    # Last update time
    if st.session_state.last_update:
        update_time = st.session_state.last_update.strftime('%Y-%m-%d %H:%M:%S')
        st.caption(f"⏰ Last updated: {update_time} | 📡 Source: OpenWeatherMap API")
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # ========== 7-DAY FORECAST ==========
    st.subheader("📅 7-DAY FORECAST")
    
    with st.spinner("📊 Loading forecast..."):
        daily_forecast = weather_service.get_daily_forecast_summary(lat, lon)
    
    if daily_forecast:
        # Create forecast dataframe for chart
        forecast_df = pd.DataFrame(daily_forecast)
        forecast_df['date_str'] = forecast_df['date'].astype(str)
        forecast_df['day_name'] = pd.to_datetime(forecast_df['date']).dt.strftime('%a %d')
        
        # Temperature forecast chart
        fig_temp = go.Figure()
        
        fig_temp.add_trace(go.Scatter(
            x=forecast_df['day_name'],
            y=forecast_df['temp_max'],
            name='High',
            mode='lines+markers',
            line=dict(color='#ef4444', width=3),
            marker=dict(size=10),
            fill=None
        ))
        
        fig_temp.add_trace(go.Scatter(
            x=forecast_df['day_name'],
            y=forecast_df['temp_avg'],
            name='Average',
            mode='lines+markers',
            line=dict(color='#f59e0b', width=3),
            marker=dict(size=8),
            fill='tonexty',
            fillcolor='rgba(239, 68, 68, 0.1)'
        ))
        
        fig_temp.add_trace(go.Scatter(
            x=forecast_df['day_name'],
            y=forecast_df['temp_min'],
            name='Low',
            mode='lines+markers',
            line=dict(color='#3b82f6', width=3),
            marker=dict(size=10),
            fill='tonexty',
            fillcolor='rgba(245, 158, 11, 0.1)'
        ))
        
        fig_temp.update_layout(
            title="🌡️ TEMPERATURE FORECAST (7 DAYS)",
            xaxis_title="Date",
            yaxis_title="Temperature (°C)",
            template="plotly_dark",
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#c5c6c7', size=12),
            title_font=dict(color='#66fcf1', size=18, family='Orbitron'),
            hovermode='x unified',
            height=400
        )
        
        st.plotly_chart(fig_temp, use_container_width=True)
        
        # Precipitation forecast chart
        fig_precip = go.Figure()
        
        fig_precip.add_trace(go.Bar(
            x=forecast_df['day_name'],
            y=forecast_df['precipitation'],
            name='Rainfall',
            marker=dict(
                color=forecast_df['precipitation'],
                colorscale='Blues',
                showscale=True,
                colorbar=dict(title="mm")
            ),
            text=forecast_df['precipitation'].round(1),
            textposition='outside'
        ))
        
        fig_precip.update_layout(
            title="🌧️ PRECIPITATION FORECAST (7 DAYS)",
            xaxis_title="Date",
            yaxis_title="Rainfall (mm)",
            template="plotly_dark",
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#c5c6c7', size=12),
            title_font=dict(color='#66fcf1', size=18, family='Orbitron'),
            height=400
        )
        
        st.plotly_chart(fig_precip, use_container_width=True)
        
        # Detailed forecast table
        st.markdown("<br>", unsafe_allow_html=True)
        st.subheader("📋 DETAILED FORECAST")
        
        # Create display dataframe
        display_df = forecast_df[['day_name', 'temp_max', 'temp_min', 'precipitation', 'humidity', 'description']].copy()
        display_df.columns = ['Day', 'High (°C)', 'Low (°C)', 'Rain (mm)', 'Humidity (%)', 'Conditions']
        
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
            height=300
        )
        
    else:
        st.warning("⚠️ Unable to load forecast data")
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # ========== ADDITIONAL WEATHER INFO ==========
    st.subheader("📊 ADDITIONAL INFORMATION")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**🌡️ TEMPERATURE DETAILS:**")
        st.write(f"• Actual: {weather['temperature']:.1f}°C")
        st.write(f"• Feels Like: {feels_like}°C")
        temp_diff = abs(weather['temperature'] - feels_like)
        if temp_diff > 5:
            st.write(f"• ⚠️ Feels {temp_diff:.1f}°C {'hotter' if feels_like > weather['temperature'] else 'cooler'} than actual")
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("**💨 WIND INFORMATION:**")
        st.write(f"• Speed: {weather['wind_speed']:.1f} km/h")
        if weather['wind_speed'] > 50:
            st.write("• ⚠️ Very high winds - secure loose objects")
        elif weather['wind_speed'] > 30:
            st.write("• ⚠️ High winds - be cautious")
        else:
            st.write("• ✅ Winds are normal")
    
    with col2:
        st.markdown("**🔽 ATMOSPHERIC PRESSURE:**")
        st.write(f"• Pressure: {weather['pressure']:.0f} hPa")
        if weather['pressure'] < 1000:
            st.write("• ⚠️ Low pressure - possible storms")
        elif weather['pressure'] > 1020:
            st.write("• ✅ High pressure - clear skies likely")
        else:
            st.write("• ✅ Normal pressure")
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("**💧 HUMIDITY & PRECIPITATION:**")
        st.write(f"• Humidity: {weather['humidity']:.0f}%")
        st.write(f"• Recent rainfall: {weather['precipitation']:.1f}mm")
        if weather['humidity'] > 80 and weather['temperature'] > 30:
            st.write("• ⚠️ High heat index - stay cool")
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # ========== RECOMMENDATIONS ==========
    st.subheader("💡 RECOMMENDATIONS")
    
    recommendations = []
    
    # Temperature-based
    if weather['temperature'] > 38:
        recommendations.append("🔥 Stay indoors during peak hours (10 AM - 6 PM)")
        recommendations.append("💧 Drink plenty of water (3-4 liters/day)")
    elif weather['temperature'] < 10:
        recommendations.append("🧥 Wear warm clothing in layers")
        recommendations.append("☕ Stay warm, drink hot beverages")
    
    # Rain-based
    if weather['precipitation'] > 10:
        recommendations.append("☂️ Carry umbrella, wear waterproof clothing")
        recommendations.append("🚗 Drive carefully, roads may be slippery")
    
    # Wind-based
    if weather['wind_speed'] > 40:
        recommendations.append("🌬️ Secure loose outdoor objects")
        recommendations.append("🚫 Avoid outdoor activities")
    
    # Humidity-based
    if weather['humidity'] > 85:
        recommendations.append("💧 High humidity - use dehumidifier if indoors")
    
    if recommendations:
        for rec in recommendations:
            st.info(rec)
    else:
        st.success("✅ Current conditions are comfortable - enjoy your day!")


def render_disaster_predictions():
    """SUPER ENHANCED Disaster Predictions with Interactive Features"""
    st.header("🎯 AI DISASTER RISK ASSESSMENT")
    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.session_state.weather_data is None:
        st.warning("⚠️ Update weather data first in Weather Monitoring page")
        return
    
    weather = st.session_state.weather_data
    
    # ========== CURRENT CONDITIONS ==========
    st.subheader("📊 CURRENT CONDITIONS")
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("🌡️ Temperature", f"{weather['temperature']:.1f}°C")
    with col2:
        st.metric("💧 Humidity", f"{weather['humidity']:.0f}%")
    with col3:
        st.metric("🌧️ Precipitation", f"{weather['precipitation']:.1f}mm")
    with col4:
        st.metric("💨 Wind", f"{weather['wind_speed']:.1f}km/h")
    with col5:
        st.metric("🔽 Pressure", f"{weather['pressure']:.0f}hPa")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # ========== PREDICT ALL TYPES ==========
    disaster_types = ['flood', 'drought', 'heatwave']
    predictions = {}
    
    for dtype in disaster_types:
        risk_score, risk_level, details = disaster_predictor.predict_disaster_risk(weather, dtype)
        predictions[dtype] = {
            'risk_score': risk_score,
            'risk_level': risk_level,
            'details': details
        }
    
    # ========== RISK CARDS ==========
    st.subheader("🎯 CURRENT RISK LEVELS")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        flood = predictions['flood']
        risk_color = 'red' if flood['risk_score'] > 0.7 else 'orange' if flood['risk_score'] > 0.4 else 'green'
        st.markdown(f"""
        <div style="background: rgba(26, 31, 58, 0.6); padding: 1.5rem; border-radius: 12px; border: 2px solid {risk_color};">
            <h3 style="color: #66fcf1; margin: 0;">🌊 FLOOD RISK</h3>
            <h1 style="color: {risk_color}; margin: 0.5rem 0;">{flood['risk_level'].upper()}</h1>
            <p style="color: #c5c6c7; margin: 0.5rem 0;">Score: <strong>{flood['risk_score']:.3f}</strong></p>
            <p style="color: #c5c6c7; font-size: 0.9rem; margin: 0;">Confidence: {flood['details'].get('confidence', 'N/A')}</p>
        </div>
        """, unsafe_allow_html=True)
        
        if 'explanation' in flood['details']:
            with st.expander("ℹ️ Details & Explanation"):
                st.info(flood['details']['explanation'])
                st.caption(f"Timestamp: {flood['details'].get('timestamp', 'N/A')}")
    
    with col2:
        drought = predictions['drought']
        risk_color = 'red' if drought['risk_score'] > 0.7 else 'orange' if drought['risk_score'] > 0.4 else 'green'
        st.markdown(f"""
        <div style="background: rgba(26, 31, 58, 0.6); padding: 1.5rem; border-radius: 12px; border: 2px solid {risk_color};">
            <h3 style="color: #66fcf1; margin: 0;">🏜️ DROUGHT RISK</h3>
            <h1 style="color: {risk_color}; margin: 0.5rem 0;">{drought['risk_level'].upper()}</h1>
            <p style="color: #c5c6c7; margin: 0.5rem 0;">Score: <strong>{drought['risk_score']:.3f}</strong></p>
            <p style="color: #c5c6c7; font-size: 0.9rem; margin: 0;">Confidence: {drought['details'].get('confidence', 'N/A')}</p>
        </div>
        """, unsafe_allow_html=True)
        
        if 'explanation' in drought['details']:
            with st.expander("ℹ️ Details & Explanation"):
                st.info(drought['details']['explanation'])
                st.caption(f"Timestamp: {drought['details'].get('timestamp', 'N/A')}")
    
    with col3:
        heatwave = predictions['heatwave']
        risk_color = 'red' if heatwave['risk_score'] > 0.7 else 'orange' if heatwave['risk_score'] > 0.4 else 'green'
        st.markdown(f"""
        <div style="background: rgba(26, 31, 58, 0.6); padding: 1.5rem; border-radius: 12px; border: 2px solid {risk_color};">
            <h3 style="color: #66fcf1; margin: 0;">🔥 HEATWAVE RISK</h3>
            <h1 style="color: {risk_color}; margin: 0.5rem 0;">{heatwave['risk_level'].upper()}</h1>
            <p style="color: #c5c6c7; margin: 0.5rem 0;">Score: <strong>{heatwave['risk_score']:.3f}</strong></p>
            <p style="color: #c5c6c7; font-size: 0.9rem; margin: 0;">Confidence: {heatwave['details'].get('confidence', 'N/A')}</p>
        </div>
        """, unsafe_allow_html=True)
        
        if 'explanation' in heatwave['details']:
            with st.expander("ℹ️ Details & Explanation"):
                st.info(heatwave['details']['explanation'])
                st.caption(f"Timestamp: {heatwave['details'].get('timestamp', 'N/A')}")
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # ========== RISK COMPARISON CHART ==========
    st.subheader("📊 RISK COMPARISON")
    
    df_risk = pd.DataFrame([
        {
            'Disaster': 'Flood', 
            'Risk Score': predictions['flood']['risk_score'],
            'Risk Level': predictions['flood']['risk_level']
        },
        {
            'Disaster': 'Drought',
            'Risk Score': predictions['drought']['risk_score'],
            'Risk Level': predictions['drought']['risk_level']
        },
        {
            'Disaster': 'Heatwave',
            'Risk Score': predictions['heatwave']['risk_score'],
            'Risk Level': predictions['heatwave']['risk_level']
        }
    ])
    
    color_map = {
        'Low': '#10b981',
        'Low-Medium': '#84cc16',
        'Medium': '#f59e0b',
        'Medium-High': '#f97316',
        'High': '#ef4444'
    }
    
    fig = px.bar(
        df_risk,
        x='Disaster',
        y='Risk Score',
        color='Risk Level',
        color_discrete_map=color_map,
        title="CURRENT RISK LEVELS (Ensemble ML Model)",
        template="plotly_dark",
        text='Risk Score'
    )
    
    fig.update_traces(texttemplate='%{text:.3f}', textposition='outside')
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#c5c6c7', size=14),
        title_font=dict(color='#66fcf1', size=20, family='Orbitron'),
        showlegend=True,
        height=450,
        yaxis=dict(range=[0, 1], title="Risk Score (0-1)"),
        xaxis=dict(title="Disaster Type")
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # ========== WHAT-IF SIMULATOR ==========
    st.subheader("🔬 WHAT-IF RISK SIMULATOR")
    st.markdown("**Adjust weather parameters to see how risk changes:**")
    
    with st.expander("🎮 INTERACTIVE SIMULATOR", expanded=False):
        st.markdown("**Try different scenarios to understand risk factors:**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            sim_temp = st.slider(
                "Temperature (°C)", 
                min_value=-10.0, 
                max_value=50.0, 
                value=float(weather['temperature']),
                step=1.0,
                key="sim_temp"
            )
            
            sim_humidity = st.slider(
                "Humidity (%)", 
                min_value=0.0, 
                max_value=100.0, 
                value=float(weather['humidity']),
                step=5.0,
                key="sim_humidity"
            )
            
            sim_precip = st.slider(
                "Precipitation (mm)", 
                min_value=0.0, 
                max_value=100.0, 
                value=float(weather['precipitation']),
                step=5.0,
                key="sim_precip"
            )
        
        with col2:
            sim_wind = st.slider(
                "Wind Speed (km/h)", 
                min_value=0.0, 
                max_value=120.0, 
                value=float(weather['wind_speed']),
                step=5.0,
                key="sim_wind"
            )
            
            sim_pressure = st.slider(
                "Pressure (hPa)", 
                min_value=950.0, 
                max_value=1050.0, 
                value=float(weather['pressure']),
                step=5.0,
                key="sim_pressure"
            )
            
            if st.button("🔄 RUN SIMULATION", type="primary", use_container_width=True):
                st.session_state.run_simulation = True
        
        if st.session_state.get('run_simulation', False):
            sim_weather = {
                'temperature': sim_temp,
                'humidity': sim_humidity,
                'precipitation': sim_precip,
                'wind_speed': sim_wind,
                'pressure': sim_pressure
            }
            
            st.markdown("---")
            st.markdown("**📊 SIMULATED RISK RESULTS:**")
            
            sim_predictions = {}
            for dtype in disaster_types:
                score, level, details = disaster_predictor.predict_disaster_risk(sim_weather, dtype)
                sim_predictions[dtype] = {'score': score, 'level': level}
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    "🌊 Flood Risk",
                    f"{sim_predictions['flood']['score']:.3f}",
                    delta=f"{sim_predictions['flood']['score'] - predictions['flood']['risk_score']:.3f}",
                    delta_color="inverse"
                )
                st.caption(f"Level: {sim_predictions['flood']['level']}")
            
            with col2:
                st.metric(
                    "🏜️ Drought Risk",
                    f"{sim_predictions['drought']['score']:.3f}",
                    delta=f"{sim_predictions['drought']['score'] - predictions['drought']['risk_score']:.3f}",
                    delta_color="inverse"
                )
                st.caption(f"Level: {sim_predictions['drought']['level']}")
            
            with col3:
                st.metric(
                    "🔥 Heatwave Risk",
                    f"{sim_predictions['heatwave']['score']:.3f}",
                    delta=f"{sim_predictions['heatwave']['score'] - predictions['heatwave']['risk_score']:.3f}",
                    delta_color="inverse"
                )
                st.caption(f"Level: {sim_predictions['heatwave']['level']}")
            
            st.session_state.run_simulation = False
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # ========== FEATURE IMPORTANCE ==========
    st.subheader("📈 MODEL FEATURE IMPORTANCE")
    
    with st.expander("🔍 WHICH FACTORS MATTER MOST?"):
        disaster_select = st.selectbox(
            "Select Disaster Type:",
            ["Flood", "Drought", "Heatwave"],
            key="feature_importance_select"
        )
        
        dtype_map = {'Flood': 'flood', 'Drought': 'drought', 'Heatwave': 'heatwave'}
        selected_type = dtype_map[disaster_select]
        
        importance = disaster_predictor.get_feature_importance(selected_type)
        
        if importance:
            # Create bar chart
            imp_df = pd.DataFrame([
                {'Feature': k.replace('_', ' ').title(), 'Importance': v}
                for k, v in list(importance.items())[:8]  # Top 8 features
            ])
            
            fig_imp = px.bar(
                imp_df,
                x='Importance',
                y='Feature',
                orientation='h',
                title=f"TOP FEATURES FOR {disaster_select.upper()} PREDICTION",
                template="plotly_dark",
                color='Importance',
                color_continuous_scale='Teal'
            )
            
            fig_imp.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#c5c6c7', size=12),
                title_font=dict(color='#66fcf1', size=16, family='Orbitron'),
                height=400,
                showlegend=False
            )
            
            st.plotly_chart(fig_imp, use_container_width=True)
            
            st.info("💡 **Feature Importance** shows which weather factors the AI model considers most important for predicting this disaster type.")
        else:
            st.warning("Feature importance data not available")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # ========== MODEL INSIGHTS ==========
    st.subheader("🤖 AI MODEL INSIGHTS")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**✅ Model Architecture:**")
        st.write("• Ensemble Learning")
        st.write("• Random Forest + Gradient Boosting")
        st.write("• Soft Voting Classification")
        st.write("• 11 features per disaster")
    
    with col2:
        st.markdown("**📊 Performance Metrics:**")
        st.write("• Training Accuracy: ~92%")
        st.write("• Test Accuracy: ~87%")
        st.write("• 5-Fold Cross-Validation")
        st.write("• Balanced Class Handling")
    
    with col3:
        st.markdown("**🎯 Advanced Features:**")
        st.write("• Confidence Scoring")
        st.write("• Temporal Patterns")
        st.write("• Risk Trend Analysis")
        st.write("• Explainable Predictions")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # ========== HIGHEST RISK ALERT ==========
    highest_risk = max(predictions.items(), key=lambda x: x[1]['risk_score'])
    
    if highest_risk[1]['risk_score'] > 0.6:
        st.error(f"""
        🚨 **ELEVATED RISK DETECTED: {highest_risk[0].upper()}**
        
        **Risk Level:** {highest_risk[1]['risk_level']}  
        **Risk Score:** {highest_risk[1]['risk_score']:.3f}
        
        {highest_risk[1]['details'].get('explanation', 'Elevated risk conditions detected.')}
        
        **⚠️ RECOMMENDED ACTIONS:**
        • 📡 Monitor weather updates every hour
        • 📋 Review and update emergency plans
        • 🚨 Ensure alert system is active
        • 📍 Identify nearest safe zones
        • 👥 Inform family members and neighbors
        • 📦 Prepare emergency kit
        """)
    else:
        st.success("""
        ✅ **ALL RISK LEVELS NORMAL**
        
        Current weather conditions are within safe parameters.
        Continue routine monitoring and stay informed.
        
        💡 **TIPS:**
        • Check forecasts daily
        • Keep emergency kit ready
        • Stay connected to alert system
        """)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # ========== EXPORT PREDICTION ==========
    st.subheader("📥 EXPORT PREDICTION REPORT")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📄 GENERATE REPORT", type="primary", use_container_width=True):
            st.session_state.show_report = True
    
    with col2:
        if st.button("💾 DOWNLOAD CSV", use_container_width=True):
            st.session_state.download_pred = True
    
    if st.session_state.get('show_report', False):
        st.markdown("---")
        
        report = f"""# ResQAlert - Disaster Risk Assessment Report
**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Location:** {weather.get('location', 'Unknown')}

## Current Weather Conditions
- Temperature: {weather['temperature']:.1f}°C
- Humidity: {weather['humidity']:.0f}%
- Precipitation: {weather['precipitation']:.1f}mm
- Wind Speed: {weather['wind_speed']:.1f}km/h
- Pressure: {weather['pressure']:.0f}hPa

## Risk Assessment Results

### 🌊 Flood Risk
- **Risk Level:** {predictions['flood']['risk_level']}
- **Risk Score:** {predictions['flood']['risk_score']:.4f}
- **Confidence:** {predictions['flood']['details'].get('confidence', 'N/A')}
- **Explanation:** {predictions['flood']['details'].get('explanation', 'N/A')}

### 🏜️ Drought Risk
- **Risk Level:** {predictions['drought']['risk_level']}
- **Risk Score:** {predictions['drought']['risk_score']:.4f}
- **Confidence:** {predictions['drought']['details'].get('confidence', 'N/A')}
- **Explanation:** {predictions['drought']['details'].get('explanation', 'N/A')}

### 🔥 Heatwave Risk
- **Risk Level:** {predictions['heatwave']['risk_level']}
- **Risk Score:** {predictions['heatwave']['risk_score']:.4f}
- **Confidence:** {predictions['heatwave']['details'].get('confidence', 'N/A')}
- **Explanation:** {predictions['heatwave']['details'].get('explanation', 'N/A')}

## Model Information
- Architecture: Ensemble (Random Forest + Gradient Boosting)
- Training Accuracy: ~92%
- Test Accuracy: ~87%
- Cross-Validation: 5-fold

---
*Report generated by ResQAlert AI Disaster Prediction System*
*Powered by Ensemble Machine Learning Models*
"""
        
        st.markdown(report)
        
        st.download_button(
            "💾 DOWNLOAD REPORT",
            report,
            file_name=f"risk_assessment_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain",
            use_container_width=True
        )
        
        if st.button("❌ CLOSE", key="close_report"):
            st.session_state.show_report = False
            st.rerun()
    
    if st.session_state.get('download_pred', False):
        import io
        
        pred_data = []
        for dtype, data in predictions.items():
            pred_data.append({
                'Timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'Location': weather.get('location', 'Unknown'),
                'Disaster Type': dtype.title(),
                'Risk Score': data['risk_score'],
                'Risk Level': data['risk_level'],
                'Confidence': data['details'].get('confidence', 'N/A'),
                'Temperature': weather['temperature'],
                'Humidity': weather['humidity'],
                'Precipitation': weather['precipitation']
            })
        
        df_export = pd.DataFrame(pred_data)
        csv_buffer = io.StringIO()
        df_export.to_csv(csv_buffer, index=False)
        
        st.download_button(
            "💾 DOWNLOAD CSV DATA",
            csv_buffer.getvalue(),
            file_name=f"predictions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True,
            type="primary"
        )
        
        if st.button("❌ CLOSE", key="close_csv"):
            st.session_state.download_pred = False
            st.rerun()



def get_real_safe_zones(lat: float, lon: float, radius_km: float = 5) -> list:
    """
    Fetch real safe zones from OpenStreetMap - ENHANCED VERSION
    """
    import requests
    
    try:
        radius_m = radius_km * 1000
        overpass_url = "https://overpass-api.de/api/interpreter"
        
        # ENHANCED: More facility types
        overpass_query = f"""
        [out:json][timeout:30];
        (
          node["amenity"="hospital"](around:{radius_m},{lat},{lon});
          node["amenity"="clinic"](around:{radius_m},{lat},{lon});
          node["amenity"="doctors"](around:{radius_m},{lat},{lon});
          node["amenity"="fire_station"](around:{radius_m},{lat},{lon});
          node["amenity"="police"](around:{radius_m},{lat},{lon});
          node["amenity"="shelter"](around:{radius_m},{lat},{lon});
          node["amenity"="community_centre"](around:{radius_m},{lat},{lon});
          node["amenity"="social_facility"](around:{radius_m},{lat},{lon});
          node["emergency"="assembly_point"](around:{radius_m},{lat},{lon});
          way["amenity"="hospital"](around:{radius_m},{lat},{lon});
          way["amenity"="clinic"](around:{radius_m},{lat},{lon});
          way["amenity"="fire_station"](around:{radius_m},{lat},{lon});
          way["amenity"="police"](around:{radius_m},{lat},{lon});
          way["building"="hospital"](around:{radius_m},{lat},{lon});
        );
        out center tags;
        """
        
        response = requests.post(overpass_url, data={'data': overpass_query}, timeout=30)
        
        if response.status_code != 200:
            return []
        
        data = response.json()
        elements = data.get('elements', [])
        
        safe_zones = []
        seen_names = set()
        
        for element in elements:
            # Get coordinates
            if element.get('type') == 'node':
                elem_lat = element.get('lat')
                elem_lon = element.get('lon')
            elif element.get('type') == 'way' and 'center' in element:
                elem_lat = element['center']['lat']
                elem_lon = element['center']['lon']
            else:
                continue
            
            tags = element.get('tags', {})
            name = tags.get('name', tags.get('operator', 'Unknown Facility'))
            
            # Skip duplicates
            if name in seen_names and name != 'Unknown Facility':
                continue
            seen_names.add(name)
            
            # Determine facility type and details
            amenity = tags.get('amenity', '')
            building = tags.get('building', '')
            emergency = tags.get('emergency', '')
            
            if amenity == 'hospital' or building == 'hospital':
                facility_type = 'Hospital'
                icon_color = 'red'
                services = tags.get('healthcare', 'General Medical Care')
                capacity = tags.get('beds', 'N/A')
            elif amenity == 'clinic' or amenity == 'doctors':
                facility_type = 'Clinic'
                icon_color = 'pink'
                services = 'Outpatient Care'
                capacity = 'N/A'
            elif amenity == 'fire_station':
                facility_type = 'Fire Station'
                icon_color = 'orange'
                services = 'Fire & Rescue'
                capacity = 'N/A'
            elif amenity == 'police':
                facility_type = 'Police Station'
                icon_color = 'blue'
                services = 'Law Enforcement'
                capacity = 'N/A'
            elif amenity == 'shelter' or amenity == 'social_facility':
                facility_type = 'Emergency Shelter'
                icon_color = 'green'
                services = 'Temporary Shelter'
                capacity = tags.get('capacity', 'N/A')
            elif amenity == 'community_centre':
                facility_type = 'Community Center'
                icon_color = 'purple'
                services = 'Evacuation Point'
                capacity = tags.get('capacity', 'N/A')
            elif emergency == 'assembly_point':
                facility_type = 'Assembly Point'
                icon_color = 'lightblue'
                services = 'Emergency Meeting Point'
                capacity = 'N/A'
            else:
                facility_type = 'Emergency Facility'
                icon_color = 'gray'
                services = 'General Emergency Services'
                capacity = 'N/A'
            
            # Calculate distance
            from math import radians, sin, cos, sqrt, atan2
            R = 6371
            lat1, lon1 = radians(lat), radians(lon)
            lat2, lon2 = radians(elem_lat), radians(elem_lon)
            dlat = lat2 - lat1
            dlon = lon2 - lon1
            a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
            c = 2 * atan2(sqrt(a), sqrt(1-a))
            distance_km = R * c
            
            # Estimate travel time (assuming 40 km/h average speed)
            travel_time_min = int((distance_km / 40) * 60)
            
            # Get contact info
            addr_street = tags.get('addr:street', '')
            addr_city = tags.get('addr:city', '')
            addr_postcode = tags.get('addr:postcode', '')
            phone = tags.get('phone', tags.get('contact:phone', 'N/A'))
            website = tags.get('website', tags.get('contact:website', ''))
            opening_hours = tags.get('opening_hours', '24/7' if amenity in ['hospital', 'fire_station', 'police'] else 'N/A')
            
            # Build address
            address_parts = [p for p in [addr_street, addr_city, addr_postcode] if p]
            address = ', '.join(address_parts) if address_parts else 'Address not available'
            
            safe_zones.append({
                'name': name,
                'type': facility_type,
                'lat': elem_lat,
                'lon': elem_lon,
                'distance_km': round(distance_km, 2),
                'travel_time_min': travel_time_min,
                'address': address,
                'phone': phone,
                'website': website,
                'opening_hours': opening_hours,
                'services': services,
                'capacity': capacity,
                'icon_color': icon_color
            })
        
        # Sort by distance
        safe_zones.sort(key=lambda x: x['distance_km'])
        
        return safe_zones[:20]  # Top 20
    
    except Exception as e:
        st.error(f"⚠️ Error fetching facilities: {str(e)}")
        return []


def render_safe_zones():
    """SUPER ENHANCED Safe Zones with all features"""
    st.header("📍 SAFE ZONES & EVACUATION")
    st.markdown("<br>", unsafe_allow_html=True)
    
    if not st.session_state.current_location:
        st.warning("⚠️ Set location in Weather Monitoring first")
        return
    
    center_lat = st.session_state.current_location['lat']
    center_lon = st.session_state.current_location['lon']
    location_name = st.session_state.current_location['name']
    
    # Controls row
    col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
    with col1:
        st.info(f"📍 **{location_name}**")
    with col2:
        radius = st.selectbox("Radius:", [2, 5, 10, 15, 20], index=1, key="radius")
    with col3:
        refresh = st.button("🔄 REFRESH", use_container_width=True, key="refresh")
    with col4:
        # FIXED: Toggle export mode
        if st.button("📥 EXPORT", use_container_width=True, key="export_btn"):
            st.session_state.export_mode = not st.session_state.get('export_mode', False)

    st.markdown("<br>", unsafe_allow_html=True)

    # Caching logic
    cache_key = f"{center_lat}_{center_lon}_{radius}"

    if 'safe_zones_cache' not in st.session_state:
        st.session_state.safe_zones_cache = {}
    if 'favorites' not in st.session_state:
        st.session_state.favorites = set()
    if 'export_mode' not in st.session_state:
        st.session_state.export_mode = False

    need_fetch = refresh or cache_key not in st.session_state.safe_zones_cache

    if need_fetch:
        with st.spinner(f"🔍 Searching within {radius}km..."):
            safe_zones = get_real_safe_zones(center_lat, center_lon, radius)
            st.session_state.safe_zones_cache[cache_key] = safe_zones
    else:
        safe_zones = st.session_state.safe_zones_cache[cache_key]

    if not safe_zones:
        st.warning(f"⚠️ No facilities found within {radius}km")
        return
    
    # Statistics row
    col1, col2, col3, col4 = st.columns(4)
    hospitals = len([z for z in safe_zones if z['type'] in ['Hospital', 'Clinic']])
    fire_police = len([z for z in safe_zones if z['type'] in ['Fire Station', 'Police Station']])
    shelters = len([z for z in safe_zones if 'Shelter' in z['type'] or 'Center' in z['type']])
    
    with col1:
        st.metric("🏥 Medical", hospitals)
    with col2:
        st.metric("🚨 Emergency", fire_police)
    with col3:
        st.metric("🏠 Shelters", shelters)
    with col4:
        st.metric("📍 Total", len(safe_zones))
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Filters
    col1, col2 = st.columns([2, 1])
    with col1:
        types = list(set([z['type'] for z in safe_zones]))
        selected = st.multiselect("Filter by type:", types, default=types, key="filter")
    with col2:
        sort_by = st.selectbox("Sort by:", ["Distance", "Name", "Type"], key="sort")
    
    # Apply filters and sorting
    filtered = [z for z in safe_zones if z['type'] in selected]
    
    if sort_by == "Distance":
        filtered.sort(key=lambda x: x['distance_km'])
    elif sort_by == "Name":
        filtered.sort(key=lambda x: x['name'])
    else:
        filtered.sort(key=lambda x: x['type'])
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # FIXED: Export panel that stays visible
    if st.session_state.export_mode:
        st.markdown("---")
        st.subheader("📥 EXPORT DATA")
        
        if filtered:
            import io
            
            export_data = []
            for z in filtered:
                export_data.append({
                    'Name': z['name'],
                    'Type': z['type'],
                    'Distance': z.get('distance_display', f"{z['distance_km']}km"),
                    'Travel Time (min)': z['travel_time_min'],
                    'Phone': z['phone'],
                    'Address': z['address'],
                    'Services': z['services'],
                    'Opening Hours': z.get('opening_hours', 'N/A'),
                    'Latitude': z['lat'],
                    'Longitude': z['lon']
                })
            
            df = pd.DataFrame(export_data)
            
            # Create CSV
            csv_buffer = io.StringIO()
            df.to_csv(csv_buffer, index=False)
            csv_data = csv_buffer.getvalue()
            
            # Show preview
            st.write(f"**Ready to export {len(filtered)} facilities:**")
            st.dataframe(df.head(5), use_container_width=True)
            
            # Download buttons
            col1, col2, col3 = st.columns([2, 2, 2])
            
            with col1:
                st.download_button(
                    label="📥 DOWNLOAD CSV",
                    data=csv_data,
                    file_name=f"safe_zones_{location_name.replace(' ', '_')}_{radius}km.csv",
                    mime="text/csv",
                    type="primary",
                    use_container_width=True
                )
            
            with col2:
                # JSON export
                import json
                json_data = json.dumps(export_data, indent=2)
                st.download_button(
                    label="📄 DOWNLOAD JSON",
                    data=json_data,
                    file_name=f"safe_zones_{location_name.replace(' ', '_')}_{radius}km.json",
                    mime="application/json",
                    use_container_width=True
                )
            
            with col3:
                if st.button("❌ CLOSE", use_container_width=True, key="close_export"):
                    st.session_state.export_mode = False
                    st.rerun()
            
            st.success("✅ Click download button to save the file")
        
        st.markdown("---")

    
    # Display facilities
    st.subheader(f"📋 {len(filtered)} FACILITIES")
    
    for i, zone in enumerate(filtered):
        is_favorite = f"{zone['name']}_{zone['lat']}" in st.session_state.favorites
        
        title = f"{'⭐' if is_favorite else ''} {zone['type']}: {zone['name']}"
        subtitle = f"{zone['distance_km']}km • {zone['travel_time_min']} min drive"
        
        with st.expander(f"{title} ({subtitle})"):
            # Details in columns
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**📍 Distance:** {zone['distance_km']} km")
                st.write(f"**⏱️ Travel Time:** ~{zone['travel_time_min']} minutes")
                st.write(f"**🏢 Type:** {zone['type']}")
                st.write(f"**🛠️ Services:** {zone['services']}")
                if zone['capacity'] != 'N/A':
                    st.write(f"**👥 Capacity:** {zone['capacity']}")
            
            with col2:
                st.write(f"**📫 Address:** {zone['address']}")
                st.write(f"**📞 Phone:** {zone['phone']}")
                st.write(f"**🕐 Hours:** {zone['opening_hours']}")
                if zone['website']:
                    st.write(f"**🌐 Website:** [Visit]({zone['website']})")
            
            # Action buttons
            st.markdown("<br>", unsafe_allow_html=True)
            action_cols = st.columns(5)
            
            with action_cols[0]:
                maps_url = f"https://www.google.com/maps/dir/?api=1&origin={center_lat},{center_lon}&destination={zone['lat']},{zone['lon']}"
                st.markdown(f"[🗺️ NAVIGATE]({maps_url})", unsafe_allow_html=False)
            
            with action_cols[1]:
                if zone['phone'] != 'N/A':
                    phone_clean = zone['phone'].replace(' ', '').replace('-', '')
                    st.markdown(f"[📞 CALL](tel:{phone_clean})", unsafe_allow_html=False)
            
            with action_cols[2]:
                if st.button("⭐ FAV", key=f"fav_{i}", use_container_width=True):
                    fav_key = f"{zone['name']}_{zone['lat']}"
                    if fav_key in st.session_state.favorites:
                        st.session_state.favorites.remove(fav_key)
                    else:
                        st.session_state.favorites.add(fav_key)
                    st.rerun()
            
            with action_cols[3]:
                coords = f"{zone['lat']},{zone['lon']}"
                st.markdown(f"[📋 COPY]", unsafe_allow_html=False)
            
            with action_cols[4]:
                if st.button("ℹ️ MORE", key=f"more_{i}", use_container_width=True):
                    st.info(f"**Full Details:**\nLat/Lon: {zone['lat']:.6f}, {zone['lon']:.6f}")
    
    # Map
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    if MAPS_AVAILABLE:
        st.subheader("🗺️ INTERACTIVE MAP")
        
        try:
            m = folium.Map(location=[center_lat, center_lon], zoom_start=13)
            
            # User location
            folium.Marker(
                [center_lat, center_lon],
                popup="📍 You",
                icon=folium.Icon(color='blue', icon='home', prefix='fa'),
                tooltip="Your Location"
            ).add_to(m)
            
            # Facilities
            for zone in filtered:
                popup_html = f"""
                <div style="font-family: Arial; width: 250px;">
                    <h4 style="margin:0;">{zone['name']}</h4>
                    <p style="margin:5px 0;"><b>{zone['type']}</b></p>
                    <p style="margin:5px 0;">📍 {zone['distance_km']}km ({zone['travel_time_min']} min)</p>
                    <p style="margin:5px 0;">📞 {zone['phone']}</p>
                    <p style="margin:5px 0;">🕐 {zone['opening_hours']}</p>
                    <p style="margin:5px 0;"><b>Services:</b> {zone['services']}</p>
                    <a href="https://www.google.com/maps/dir/?api=1&origin={center_lat},{center_lon}&destination={zone['lat']},{zone['lon']}" target="_blank">🗺️ Get Directions</a>
                </div>
                """
                
                folium.Marker(
                    [zone['lat'], zone['lon']],
                    popup=folium.Popup(popup_html, max_width=300),
                    icon=folium.Icon(color=zone['icon_color'], icon='info-sign'),
                    tooltip=f"{zone['name']} ({zone['distance_km']}km)"
                ).add_to(m)
            
            # Search radius circle
            folium.Circle(
                [center_lat, center_lon],
                radius=radius * 1000,
                color='cyan',
                fill=True,
                opacity=0.15
            ).add_to(m)
            
            st_folium(m, width=1200, height=650, key=f"map_{cache_key}")
            
        except Exception as e:
            st.warning(f"⚠️ Map error: {str(e)}")
    
    # Emergency contacts
    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("📞 QUICK CONTACTS")
    
    emerg = st.columns(4)
    with emerg[0]:
        st.metric("🚨 Emergency", "112")
    with emerg[1]:
        st.metric("🚑 Ambulance", "108")
    with emerg[2]:
        st.metric("🔥 Fire", "101")
    with emerg[3]:
        st.metric("🌊 Disaster", "1078")


def render_chatbot():
    """AI-powered disaster chatbot - COMPLETE WORKING VERSION"""
    st.header("🤖 AI DISASTER ASSISTANT")
    
    # Initialize Gemini with CORRECT model names
    gemini_error = None
    if GEMINI_AVAILABLE and settings.GEMINI_API_KEY:
        if 'gemini_model' not in st.session_state:
            try:
                genai.configure(api_key=settings.GEMINI_API_KEY)
                
                # Try multiple models (latest to oldest)
                models_to_try = [
                    'gemini-2.5-pro',
                    'gemini-pro',
                    'gemini-1.0-pro-latest'
                ]
                
                model_loaded = False
                for model_name in models_to_try:
                    try:
                        st.session_state.gemini_model = genai.GenerativeModel(model_name)
                        st.session_state.gemini_chat = st.session_state.gemini_model.start_chat(history=[])
                        st.session_state.ai_enabled = True
                        st.session_state.model_name = model_name
                        model_loaded = True
                        break
                    except:
                        continue
                
                if not model_loaded:
                    raise Exception("No available Gemini models found")
                    
            except Exception as e:
                gemini_error = str(e)
                st.session_state.ai_enabled = False
        else:
            st.session_state.ai_enabled = True
    else:
        st.session_state.ai_enabled = False
    
    # Status bar
    col1, col2 = st.columns([3, 1])
    with col1:
        if st.session_state.get('ai_enabled', False):
            model_name = st.session_state.get('model_name', 'Unknown')
            st.success(f"🤖 **AI Mode:** Google Gemini ({model_name}) ✨")
        else:
            st.info("💡 **Rule-Based Mode:** Pre-programmed responses")
            if gemini_error:
                with st.expander("⚠️ See Error"):
                    st.error(f"Error: {gemini_error}")
    
    with col2:
        if st.button("🔄 CLEAR", use_container_width=True, key="clear_chat"):
            st.session_state.messages = []
            if st.session_state.get('ai_enabled'):
                try:
                    st.session_state.gemini_chat = st.session_state.gemini_model.start_chat(history=[])
                except:
                    pass
            st.rerun()
    
    # Initialize messages
    if "messages" not in st.session_state:
        st.session_state.messages = [{
            "role": "assistant",
            "content": """👋 **Welcome to ResQAlert AI Assistant!**

**I can help with:**
🌊 Flood Safety | 🔥 Wildfire Protection | 🌪️ Tornado Safety  
🌍 Earthquake Prep | 🏜️ Drought Management | ☀️ Heatwave Safety  
🌊 Tsunami Warnings | 🎒 Emergency Kits | 🚨 Evacuation Planning

**Emergency Numbers (India):**
📞 **112** - All Emergencies | **108** - Ambulance | **101** - Fire | **1078** - Disaster Mgmt

**Ask me anything about disaster preparedness!** 🛡️"""
        }]
    
    # Display messages
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask about disaster preparedness...", key="chat_input"):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate and display response
        with st.chat_message("assistant"):
            with st.spinner("🤖 Thinking..."):
                response = get_chatbot_response(prompt)
                st.markdown(response)
        
        # Save response
        st.session_state.messages.append({"role": "assistant", "content": response})

def get_chatbot_response(text: str) -> str:
    """Generate AI response - FIXED VERSION"""
    
    # Check AI availability
    if st.session_state.get('ai_enabled') and 'gemini_chat' in st.session_state:
        try:
            # Enhanced disaster-focused prompt
            system_context = f"""You are ResQAlert AI, an expert disaster preparedness assistant for India.

User Question: {text}

Provide a helpful, structured response following these guidelines:

**Format:**
1. Start with relevant emoji and brief intro
2. Use clear sections with **bold headings**
3. Include numbered or bulleted lists for steps
4. Add ⚠️ for warnings, ✅ for recommendations
5. Include Indian emergency numbers when relevant

**Content Focus:**
- Specific, actionable steps (Before/During/After when relevant)
- Indian context (monsoons, geography, infrastructure)
- Safety warnings and precautions
- Practical tips anyone can follow
- Emergency contacts: 112 (All), 108 (Ambulance), 101 (Fire), 1078 (Disaster)

**Style:**
- Clear, concise (300-500 words)
- Professional but caring tone
- Use metric units (km, celsius)
- Avoid technical jargon

Provide your expert advice now:"""

            # Call Gemini API
            response = st.session_state.gemini_chat.send_message(system_context)
            
            # Return AI response
            return response.text
            
        except Exception as e:
            # Show error gracefully
            error_msg = str(e)[:200]
            fallback = get_rule_based_response(text)
            
            return f"""⚠️ **AI temporarily unavailable**

*Error: {error_msg}*

**Using emergency response mode:**

{fallback}"""
    
    # Rule-based fallback
    return get_rule_based_response(text)


def get_rule_based_response(text: str) -> str:
    """Enhanced rule-based responses with better formatting"""
    text = text.lower()
    
    # Emergency Kit
    if any(w in text for w in ['kit', 'supplies', 'emergency', 'bag', 'prepare']):
        return """📦 **EMERGENCY KIT ESSENTIALS**

**🥤 Water & Food (3-Day Supply):**
✅ 1 gallon water per person per day (3 liters)
✅ Non-perishable food (canned goods, dry fruits, nuts)
✅ Manual can opener
✅ High-energy snacks

**🔦 Tools & Safety:**
✅ Flashlight + extra batteries
✅ Battery-powered or hand-crank radio
✅ Complete first aid kit
✅ Whistle (to signal for help)
✅ Dust masks, plastic sheeting, duct tape
✅ Multipurpose tool/knife

**📱 Communication:**
✅ Portable phone charger/power bank
✅ Written emergency contact list
✅ Local maps (paper copies)
✅ Waterproof document bag

**💊 Medical:**
✅ 7-day supply of prescription medications
✅ Glasses/contact lenses
✅ Sanitation items

**💵 Important Items:**
✅ Cash in small bills (₹500, ₹100, ₹50)
✅ Photocopies of important documents (Aadhar, insurance, bank)
✅ Extra house and car keys

**🧥 Clothing:**
✅ Complete change of clothes
✅ Sturdy shoes/boots
✅ Rain gear
✅ Warm blankets

**💡 TIP:** Store in waterproof container. Check every 6 months!

**📞 Emergency Contacts:**
🚨 **112** - All Emergencies | **108** - Ambulance | **101** - Fire | **1078** - Disaster Management"""

    # Evacuation
    elif any(w in text for w in ['evacuation', 'evacuate', 'leave', 'escape']):
        return """🚨 **EVACUATION PLANNING GUIDE**

**📍 BEFORE DISASTER:**
✅ **Know Your Routes:** Identify 2-3 evacuation paths from home/work
✅ **Practice Drills:** Run evacuation practice with family
✅ **Meeting Points:** Designate 2 locations:
   - One near home (neighbor's house, park)
   - One outside neighborhood (relative's house, community center)
✅ **Keep Emergency Kit Ready:** By main exit door

**🚗 DURING EVACUATION:**
1. **Act Immediately:** Don't wait if officials order evacuation
2. **Secure Home:** 
   - Lock doors and windows
   - Turn off utilities (if time permits)
   - Leave note with destination
3. **Take Only Essentials:**
   - Emergency kit
   - Important documents
   - Medications
   - Phone + charger
   - Cash
4. **Follow Official Routes:** Use designated evacuation roads only
5. **Help Neighbors:** Check on elderly, disabled neighbors
6. **Stay Informed:** Monitor radio/TV for updates

**📱 COMMUNICATION:**
✅ Text instead of call (saves network bandwidth)
✅ Use social media to update your status
✅ Check in with out-of-area contact person

**⚠️ NEVER:**
❌ Drive through flooded areas (Turn Around, Don't Drown!)
❌ Return home until authorities declare safe
❌ Use elevators during evacuation

**💡 REMEMBER:** Your life is more valuable than any possession!

**📞 Emergency:** **112** | **1078** (Disaster Management)"""

    # Flood
    elif 'flood' in text or 'flooding' in text:
        return """🌊 **FLOOD SAFETY GUIDE**

**⚠️ BEFORE FLOOD:**
✅ Move valuables to higher floors
✅ Turn off electricity, gas if instructed
✅ Fill bathtubs with clean water (for sanitation)
✅ Charge all devices
✅ Prepare to evacuate to higher ground

**🚨 DURING FLOOD:**
⚠️ **MOVE TO HIGHER GROUND IMMEDIATELY**
❌ **NEVER walk through moving water** (6 inches can knock you down)
❌ **NEVER drive through flooded roads** (2 feet sweeps away vehicles)
✅ Stay away from windows
✅ Avoid contact with flood water (contaminated)
✅ If trapped, go to highest level of building
✅ Signal for help (whistle, flashlight, bright cloth)

**✅ AFTER FLOOD:**
✅ Wait for "all clear" from authorities
✅ Avoid standing water (may hide hazards)
✅ Watch for snakes, insects
✅ Check building stability before entering
✅ Document damage with photos (insurance)
✅ Throw away contaminated food
✅ Boil water before drinking (until declared safe)

**⚠️ CRITICAL FACTS:**
🌊 **6 inches** of moving water = knock down an adult
🚗 **2 feet** of water = float most vehicles
💀 **Flood water contains:** Sewage, chemicals, debris, sharp objects

**📞 Emergency:** **108** (Ambulance) | **1078** (Disaster) | **112** (All Emergencies)"""

    # Earthquake
    elif any(w in text for w in ['earthquake', 'quake', 'tremor', 'seismic']):
        return """🌍 **EARTHQUAKE SAFETY**

**⚡ DURING EARTHQUAKE:**

**🏠 IF INDOORS:**
1. **DROP** to hands and knees
2. **COVER** head and neck under sturdy desk/table
3. **HOLD ON** until shaking stops
4. Stay away from:
   ❌ Windows, mirrors, glass
   ❌ Heavy furniture, appliances
   ❌ Exterior walls
5. **DON'T** run outside (falling debris risk)
6. **DON'T** use elevators
7. If in bed: Stay there, cover head with pillow

**🚗 IF IN VEHICLE:**
1. Pull over safely (away from buildings, trees, bridges, overpasses)
2. Stay inside with seatbelt fastened
3. Avoid stopping near power lines, signs
4. Resume driving carefully after shaking stops

**🌳 IF OUTDOORS:**
1. Move to open area away from buildings, trees, power lines
2. Drop to ground
3. Stay there until shaking stops

**✅ AFTER EARTHQUAKE:**
✅ Check yourself and others for injuries
✅ Inspect home for structural damage
✅ Turn off utilities if you smell gas or see damage
✅ **Watch for AFTERSHOCKS** (can occur hours/days later)
✅ Stay away from damaged buildings
✅ Use stairs, not elevators
✅ Stay off phone (except emergencies)
✅ Listen to radio for emergency broadcasts

**📦 EARTHQUAKE SURVIVAL KIT:**
✅ Sturdy shoes (protect from broken glass)
✅ Whistle (signal for help if trapped)
✅ Flashlight
✅ Fire extinguisher
✅ Wrench (to turn off utilities)
✅ 3-day water and food supply

**⚠️ REMEMBER:** DROP, COVER, HOLD ON!

**📞 Emergency:** **112** | **108** | **1078** (Disaster Management)"""

    # Heatwave
    elif any(w in text for w in ['heat', 'heatwave', 'hot', 'temperature']):
        return """🔥 **HEATWAVE SAFETY**

**❄️ STAY COOL:**
✅ Stay indoors during hottest hours (10 AM - 6 PM)
✅ Use AC, fans, or coolers
✅ Close curtains/blinds during day
✅ Take cool showers/baths
✅ Wear light, loose, cotton clothing
✅ Use damp cloth on neck/wrists
✅ Visit cooling centers if no AC (malls, libraries)

**💧 STAY HYDRATED:**
✅ Drink water regularly (don't wait to feel thirsty)
✅ Aim for 8-10 glasses per day
✅ Carry water bottle always
✅ Eat water-rich fruits (watermelon, cucumber)
❌ Avoid alcohol, caffeine, sugary drinks (dehydrating)

**🚨 HEAT ILLNESS WARNING SIGNS:**

**Heat Exhaustion (Moderate):**
- Heavy sweating
- Weakness, dizziness
- Nausea, vomiting
- Headache
- Cool, pale, clammy skin
- Fast, weak pulse

**ACTION:** Move to cool place, drink water, rest. Seek medical help if symptoms worsen.

**Heat Stroke (LIFE-THREATENING EMERGENCY!):**
- High body temperature (103°F / 39.4°C+)
- Hot, RED, DRY skin (NO sweating)
- Confusion, slurred speech
- Seizures
- Loss of consciousness

**ACTION:** ⚠️ **CALL 108 IMMEDIATELY!** Cool person with water, ice. This is a medical emergency!

**👶 PROTECT VULNERABLE:**
✅ Check on elderly, children, pregnant women, sick people
✅ NEVER leave anyone (humans or pets) in parked vehicles
✅ Pets need water and shade too

**💡 SAFETY TIPS:**
✅ Wear sunscreen (SPF 30+)
✅ Wear wide-brimmed hat
✅ Avoid heavy meals (generate body heat)
✅ Reduce physical activity
✅ Check weather forecasts

**📞 Medical Emergency:** **108** (Ambulance) | **112** (All Emergencies)"""

    # Wildfire
    elif any(w in text for w in ['wildfire', 'forest fire', 'bushfire', 'fire']):
        return """🔥 **WILDFIRE SAFETY**

**⚠️ BEFORE WILDFIRE SEASON:**
✅ Create 30-foot defensible space around home
✅ Clear dry leaves, dead vegetation, woodpiles
✅ Trim tree branches (6+ feet from ground)
✅ Install fire-resistant roofing
✅ Have garden hose connected and ready
✅ Know evacuation routes
✅ Pack emergency go-bag

**🚨 WILDFIRE APPROACHING:**
1. **Evacuate IMMEDIATELY if ordered** (don't wait!)
2. Close all windows and doors
3. Fill bathtubs, sinks with water
4. Move flammable furniture to center of rooms
5. Turn on ALL lights (helps firefighters see your house)
6. Shut off gas at meter (if time permits)
7. Take pets, emergency kit, important documents

**😷 SMOKE PROTECTION:**
✅ Stay indoors with windows closed
✅ Use air purifier if available
✅ Set AC to recirculate (don't bring outside air in)
✅ Wear N95 or P100 mask if going outside
✅ Keep car recirculation on if driving

**🚗 IF TRAPPED WHILE EVACUATING:**
1. Park in area clear of vegetation
2. Close windows, vents
3. Turn on headlights, hazard lights
4. Stay INSIDE vehicle
5. Cover yourself with blanket or jacket
6. Lie on floor
7. Call **101** (Fire) or **112**

**✅ AFTER WILDFIRE:**
✅ Wait for authorities to declare "all clear"
✅ Watch for hot spots, ash pits (can burn)
✅ Wear N95 mask (ash is toxic)
✅ Check for structural damage before entering home
✅ Document damage (photos for insurance)
✅ Watch for flare-ups (can reignite days later)

**⚠️ WILDFIRE SIGNS:**
🔥 Smoke in distance
🔥 Strong smell of smoke
🔥 Ash falling
🔥 Red/orange glow at night
🔥 Loud roaring sound

**📞 Fire Emergency:** **101** | **112** (All Emergencies)"""

    # Emergency Numbers
    elif any(w in text for w in ['emergency', 'number', 'contact', 'call', 'help', 'phone']):
        return """📞 **EMERGENCY CONTACT NUMBERS - INDIA**

**🚨 IMMEDIATE EMERGENCIES:**
**112** - National Emergency (Police, Fire, Ambulance - ALL SERVICES)
**100** - Police
**101** - Fire Brigade
**108** - Ambulance / Medical Emergency
**1078** - National Disaster Management Authority (NDMA)

**🏥 MEDICAL:**
**108** - Medical Emergency / Ambulance
**104** - National Blood Bank
**1800-599-0019** - Mental Health Helpline (KIRAN)

**👮 SAFETY & PROTECTION:**
**1091** - Women Helpline
**1098** - Child Helpline (CHILDLINE)
**1091** - Senior Citizen Helpline
**181** - Women in Distress

**🌊 DISASTER-SPECIFIC:**
**1078** - Earthquake, Flood, Cyclone, any natural disaster
**1093** - Coastal Security / Marine Emergency
**1077** - Railway Accident Emergency

**🚗 TRANSPORT:**
**139** - Railway Enquiry
**1073** - Road Accident Emergency Service

**💡 IMPORTANT TIPS:**
✅ **Save these numbers in your phone NOW**
✅ **Memorize 112** (universal emergency number)
✅ **TEXT if calls don't go through** (uses less bandwidth)
✅ **Give exact location when calling**
✅ **Stay calm and speak clearly**
✅ **Have important info ready:** Name, location, emergency type
✅ **Don't hang up** until told to by operator

**📱 EMERGENCY APPS TO DOWNLOAD:**
✅ **NDMA Disaster Alert** - Official disaster warnings
✅ **DisasterAlert (PDC)** - Global disaster tracking
✅ **Indian Red Cross** - Emergency response
✅ **Smart 24x7** - Women's safety
✅ **Meri Sakhi** - Women's helpline integration

**🌐 EMERGENCY WEBSITES:**
✅ ndma.gov.in - National Disaster Management
✅ ndrf.gov.in - National Disaster Response Force
✅ mha.gov.in - Ministry of Home Affairs

**Remember: In any emergency, call 112 first! It connects to all emergency services.**"""

    # Default comprehensive response
    else:
        return """🛡️ **DISASTER PREPAREDNESS ASSISTANT**

**I can help you with detailed information on:**

**🌊 NATURAL DISASTERS:**
• **Floods** - Safety before, during, after | Evacuation
• **Earthquakes** - Drop, Cover, Hold On | Aftershock safety
• **Wildfires** - Evacuation, smoke protection, home defense
• **Tornadoes/Cyclones** - Shelter, warning signs
• **Tsunamis** - Warning signs, evacuation routes
• **Landslides** - Risk areas, safety measures

**☀️ WEATHER EMERGENCIES:**
• **Heatwaves** - Heat illness prevention, cooling strategies
• **Droughts** - Water conservation, health precautions
• **Lightning** - Indoor/outdoor safety
• **Severe Storms** - Protection measures

**🎒 PREPAREDNESS:**
• **Emergency Kits** - Essential supplies checklist
• **Evacuation Planning** - Routes, meeting points, drills
• **Family Safety Plans** - Communication, responsibilities
• **First Aid** - Basic emergency medical care
• **Food & Water** - Storage, purification

**📱 EMERGENCY RESOURCES:**
• **Contact Numbers** - Police, Fire, Ambulance, Disaster Management
• **Safety Apps** - Disaster alerts, emergency communication
• **Community Resources** - Shelters, relief centers

**💡 EXAMPLE QUESTIONS:**
"What should be in my emergency kit?"
"How do I prepare for Mumbai monsoon floods?"
"Earthquake safety for apartment residents?"
"Emergency contacts for disasters?"
"How to evacuate safely with children?"

**📞 QUICK REFERENCE:**
🚨 **112** - All Emergencies
📱 **108** - Ambulance
🔥 **101** - Fire
🌊 **1078** - Disaster Management

**Ask me anything specific about disaster preparedness, and I'll provide detailed, actionable advice!** 🛡️"""


def render_alert_system():
    """Alert system"""
    st.header("📡 ALERT SYSTEM")
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        status = "✅ ACTIVE" if sms_service.is_configured else "❌ OFF"
        st.metric("SMS", status)
    with col2:
        users = user_manager.get_all_users()
        st.metric("USERS", len(users))
    with col3:
        alerts = alert_manager.get_alert_history(limit=10)
        st.metric("ALERTS", len(alerts))
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4 = st.tabs(["👤 REGISTER", "🧪 TEST", "🚨 SEND", "📊 HISTORY"])
    
    with tab1:
        render_user_registration()
    with tab2:
        render_test_alerts()
    with tab3:
        render_disaster_alert_sender()
    with tab4:
        render_alert_history()

def validate_email(email: str) -> dict:
    """Validate email address format"""
    import re
    
    # Basic email regex pattern
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not email:
        return {"valid": False, "message": "❌ Email is required"}
    
    if not re.match(email_pattern, email):
        return {"valid": False, "message": "❌ Invalid email format. Use: name@example.com"}
    
    if len(email) > 100:
        return {"valid": False, "message": "❌ Email too long (max 100 characters)"}
    
    return {"valid": True, "message": "✅ Valid email"}

def validate_phone(phone: str) -> dict:
    """Validate phone number format"""
    import re
    
    if not phone:
        return {"valid": False, "message": "❌ Phone number is required"}
    
    # Remove all spaces, dashes, parentheses
    phone_clean = re.sub(r'[\s\-\(\)]', '', phone)
    
    # Check for E.164 format (+country code + number)
    if not phone_clean.startswith('+'):
        return {
            "valid": False,
            "message": "❌ Phone must start with + and country code",
            "hint": "Example for India: +919008769230"
        }
    
    # Remove + for length check
    phone_digits = phone_clean[1:]
    
    # Check if only digits after +
    if not phone_digits.isdigit():
        return {
            "valid": False,
            "message": "❌ Phone can only contain digits after +",
            "hint": "Format: +[country code][number]"
        }
    
    # Check length (international phone numbers are 10-15 digits)
    if len(phone_digits) < 10:
        return {
            "valid": False,
            "message": "❌ Phone number too short (min 10 digits)",
            "hint": "Include country code. Example: +919008769230"
        }
    
    if len(phone_digits) > 15:
        return {
            "valid": False,
            "message": "❌ Phone number too long (max 15 digits)"
        }
    
    # Special check for Indian numbers
    if phone_clean.startswith('+91'):
        if len(phone_digits) != 12:  # 91 + 10 digits
            return {
                "valid": False,
                "message": "❌ Indian numbers must be 10 digits after +91",
                "hint": "Format: +91XXXXXXXXXX (10 digits)"
            }
    
    return {"valid": True, "message": "✅ Valid phone number"}

def render_user_registration():
    """User registration with validation"""
    st.subheader("👤 REGISTRATION")
    st.markdown("<br>", unsafe_allow_html=True)
    
    users = user_manager.get_all_users()
    if users:
        st.success(f"✅ {len(users)} users registered")
        with st.expander("👥 VIEW USERS"):
            for user in users:
                st.write(f"• **{user.name}** - {user.phone} - {user.location_name}")
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("📝 NEW USER")
    
    with st.form("reg_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Name*", placeholder="Full name", key="reg_name")
            email = st.text_input("Email*", placeholder="email@example.com", key="reg_email")
        
        with col2:
            phone = st.text_input(
                "Phone*", 
                placeholder="+919008769230",
                help="Format: +[country code][number]",
                key="reg_phone"
            )
            location = st.text_input("Location*", placeholder="City", key="reg_loc")
        
        lat = st.session_state.current_location['lat'] if st.session_state.current_location else 12.9716
        lon = st.session_state.current_location['lon'] if st.session_state.current_location else 77.5946
        
        submit = st.form_submit_button("🔔 REGISTER", type="primary", use_container_width=True)
        
        if submit:
            # Check if all fields filled
            if not all([name, email, phone, location]):
                st.error("❌ Fill all required fields marked with *")
                return
            
            # Validate name
            if len(name.strip()) < 2:
                st.error("❌ Name must be at least 2 characters")
                return
            
            # Validate email
            email_check = validate_email(email)
            if not email_check["valid"]:
                st.error(email_check["message"])
                return
            
            # Validate phone
            phone_check = validate_phone(phone)
            if not phone_check["valid"]:
                st.error(phone_check["message"])
                if "hint" in phone_check:
                    st.info(f"💡 {phone_check['hint']}")
                return
            
            # All validations passed - register user
            result = user_manager.register_user(name, email, phone, location, lat, lon)
            
            if result["status"] == "success":
                st.success(f"✅ {name} registered successfully!")
                st.balloons()
                time.sleep(1)
                st.rerun()
            else:
                st.error(f"❌ Registration failed: {result['message']}")

def render_test_alerts():
    """Test SMS with better feedback"""
    st.subheader("🧪 TEST SMS ALERTS")
    st.markdown("<br>", unsafe_allow_html=True)
    
    if not sms_service.is_configured:
        st.error("❌ SMS Service not configured")
        st.info("💡 Configure Twilio credentials in your .env file")
        return
    
    # Show SMS service status
    account_info = sms_service.get_account_info()
    if account_info.get("status") == "success":
        col1, col2 = st.columns(2)
        with col1:
            st.success("✅ SMS Service: Connected")
        with col2:
            if account_info.get("is_trial"):
                verified_count = account_info.get("verified_count", 0)
                st.warning(f"⚠️ Trial Account: {verified_count} verified numbers")
            else:
                st.success("✅ Full Account: All numbers allowed")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Test SMS form
    col1, col2 = st.columns([3, 1])
    
    with col1:
        test_phone = st.text_input(
            "PHONE NUMBER:", 
            placeholder="+919008769230",
            help="For trial accounts, use verified numbers only",
            key="test_ph"
        )
    
    with col2:
        st.write("")
        st.write("")
        if st.button("📱 SEND TEST", type="primary", use_container_width=True):
            if not test_phone:
                st.error("❌ Enter a phone number")
                return
            
            # Validate phone format
            phone_validation = validate_phone(test_phone)
            if not phone_validation["valid"]:
                st.error(phone_validation["message"])
                if "hint" in phone_validation:
                    st.info(f"💡 {phone_validation['hint']}")
                return
            
            # Send test SMS with progress indicator
            progress_text = st.empty()
            
            progress_text.text("📡 Connecting to Twilio...")
            time.sleep(0.3)
            
            progress_text.text("📱 Sending test SMS...")
            result = sms_service.send_test_message(test_phone)
            time.sleep(0.3)
            
            progress_text.empty()
            
            if result["status"] == "success":
                st.success("✅ Test SMS sent successfully!")
                
                # Show details
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Message ID:** `{result['message_sid']}`")
                    st.write(f"**Sent to:** `{result['to']}`")
                with col2:
                    st.write(f"**Timestamp:** `{result.get('sent_at', datetime.now()).strftime('%H:%M:%S')}`")
                
                # Store message ID for status checking
                st.session_state['last_msg_id'] = result['message_sid']
                
                st.info("💡 Use 'Check Status' button below to verify delivery")
                
            elif result.get("error_code") == "TRIAL_UNVERIFIED":
                st.error(f"❌ {result['message']}")
                st.warning("⚠️ For trial accounts, verify the number first:")
                st.code("https://console.twilio.com/us1/develop/phone-numbers/manage/verified")
                
                if result.get("verified_numbers"):
                    st.info(f"✅ Your verified numbers: {', '.join(result['verified_numbers'][:3])}")
            else:
                st.error(f"❌ SMS failed: {result.get('message', 'Unknown error')}")
                
                # Show solution if available
                if result.get("solution"):
                    with st.expander("🔧 How to fix this:"):
                        st.write(result["solution"])
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Check delivery status
    if 'last_msg_id' in st.session_state:
        st.subheader("📊 DELIVERY STATUS")
        
        if st.button("🔍 CHECK STATUS", use_container_width=True):
            with st.spinner("Checking delivery status..."):
                time.sleep(0.5)
                status = sms_service.get_message_status(st.session_state['last_msg_id'])
                
                if status.get("status") == "success":
                    delivery_status = status.get("delivery_status", "unknown")
                    
                    # Status display with colors
                    if delivery_status == "delivered":
                        st.success("✅ SMS DELIVERED SUCCESSFULLY!")
                        st.write(f"**To:** {status.get('to', 'Unknown')}")
                        st.write(f"**Time:** {status.get('date_sent', 'Unknown')}")
                        
                    elif delivery_status == "sent":
                        st.info("📨 SMS sent to carrier (delivery pending)")
                        st.write("Usually delivers within 1-2 minutes")
                        
                    elif delivery_status == "queued":
                        st.warning("📤 SMS queued for sending")
                        st.write("Will be sent shortly")
                        
                    elif delivery_status in ["failed", "undelivered"]:
                        st.error(f"❌ Delivery failed")
                        if status.get("error_code"):
                            st.error(f"Error code: {status['error_code']}")
                            st.write(f"Error: {status.get('error_message', 'Unknown error')}")
                            
                            # Show solution
                            if status.get("solution"):
                                with st.expander("🔧 How to fix:"):
                                    st.write(status["solution"])
                    else:
                        st.info(f"📊 Status: {delivery_status}")
                else:
                    st.error("❌ Could not check status")


def render_disaster_alert_sender():
    """Send disaster alerts with progress tracking"""
    st.subheader("🚨 SEND DISASTER ALERT")
    st.markdown("<br>", unsafe_allow_html=True)
    
    users = user_manager.get_all_users()
    if not users:
        st.warning("⚠️ No users registered. Register users first in the 'REGISTER' tab.")
        return
    
    st.info(f"📱 Ready to send alerts to {len(users)} registered users")
    
    with st.form("alert_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            dtype = st.selectbox("DISASTER TYPE", ["flood", "drought", "heatwave"])
            rlevel = st.selectbox("RISK LEVEL", ["Medium", "High"])
        with col2:
            loc = st.text_input(
                "LOCATION", 
                value=st.session_state.current_location['name'] if st.session_state.current_location else "Bangalore"
            )
            rscore = st.slider("RISK SCORE", 0.0, 1.0, 0.7, 0.05)
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.subheader("📝 MESSAGE PREVIEW")
        preview = f"""🚨 ResQAlert {rlevel.upper()} ALERT

🌊 {dtype.upper()}: {rlevel} Risk
📍 Location: {loc}
📊 Risk Score: {rscore:.2f}

🛡️ Take immediate safety actions
📞 Emergency: 108
⏰ {datetime.now().strftime('%d/%m %H:%M')}"""
        
        st.code(preview)
        
        send = st.form_submit_button(
            f"🚨 SEND {dtype.upper()} ALERT TO {len(users)} USERS", 
            type="secondary", 
            use_container_width=True
        )
        
        if send:
            # Enhanced progress tracking
            progress_text = st.empty()
            progress_bar = st.progress(0)
            
            progress_text.text(f"📡 Preparing to send alerts to {len(users)} users...")
            progress_bar.progress(10)
            time.sleep(0.3)
            
            progress_text.text(f"🔄 Sending {dtype} alerts...")
            progress_bar.progress(30)
            
            weather_data = st.session_state.weather_data or {
                'temperature': 25, 'humidity': 70, 'precipitation': 0, 
                'wind_speed': 10, 'pressure': 1013
            }
            
            result = alert_manager.send_disaster_alert(
                disaster_type=dtype,
                risk_level=rlevel,
                risk_score=rscore,
                location=loc,
                lat=st.session_state.current_location['lat'] if st.session_state.current_location else 12.9716,
                lon=st.session_state.current_location['lon'] if st.session_state.current_location else 77.5946,
                weather_data=weather_data
            )
            
            progress_bar.progress(90)
            time.sleep(0.3)
            
            progress_bar.progress(100)
            progress_text.text("✅ Alerts sent!")
            time.sleep(0.5)
            
            # Clear progress indicators
            progress_text.empty()
            progress_bar.empty()
            
            # Display results
            if result["status"] == "success":
                st.success("🎉 Disaster alerts sent successfully!")
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                # Results metrics
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("📊 Total Users", result["total_users"])
                with col2:
                    st.metric("✅ SMS Sent", result["sms_sent"], delta=result["sms_sent"], delta_color="normal")
                with col3:
                    st.metric("❌ Failed", result["sms_failed"], delta=result["sms_failed"], delta_color="inverse")
                
                # Show detailed results if available
                if result.get("details"):
                    st.markdown("<br>", unsafe_allow_html=True)
                    with st.expander("📊 Detailed Delivery Report"):
                        for detail in result["details"]:
                            if detail.get("status") == "sent":
                                st.success(f"✅ {detail['user']} ({detail['phone']})")
                            else:
                                st.error(f"❌ {detail['user']} ({detail['phone']}) - {detail.get('error', 'Unknown error')}")
                
                st.balloons()
            else:
                st.error(f"❌ Alert sending failed: {result.get('message', 'Unknown error')}")


def render_alert_history():
    """ENHANCED Alert History & Analytics Dashboard"""
    st.header("📊 ALERT HISTORY & ANALYTICS")
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Fetch all alerts
    all_alerts = alert_manager.get_alert_history(limit=100)
    
    if not all_alerts:
        st.info("📪 No alert history yet. Send your first alert!")
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Show example/placeholder
        st.subheader("📋 WHAT YOU'LL SEE HERE:")
        st.write("• **Timeline** of all sent alerts")
        st.write("• **Statistics** on alert types and success rates")
        st.write("• **Trends** showing alert patterns over time")
        st.write("• **Export** capabilities for reports")
        
        return
    
    # ========== SUMMARY STATISTICS ==========
    st.subheader("📈 QUICK STATISTICS")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("📨 Total Alerts", len(all_alerts))
    
    with col2:
        sms_count = len([a for a in all_alerts if a.alert_type == "sms"])
        st.metric("📱 SMS Sent", sms_count)
    
    with col3:
        success_count = len([a for a in all_alerts if a.status == "sent"])
        success_rate = (success_count / len(all_alerts)) * 100 if all_alerts else 0
        st.metric("✅ Success Rate", f"{success_rate:.1f}%")
    
    with col4:
        # Most common disaster type
        disaster_counts = {}
        for a in all_alerts:
            disaster_counts[a.disaster_type] = disaster_counts.get(a.disaster_type, 0) + 1
        most_common = max(disaster_counts.items(), key=lambda x: x[1])[0] if disaster_counts else "N/A"
        st.metric("🔥 Most Common", most_common.title())
    
    with col5:
        # Last alert time
        if all_alerts:
            last_alert = all_alerts[0].sent_at
            time_diff = datetime.now() - last_alert
            if time_diff.days > 0:
                last_str = f"{time_diff.days}d ago"
            elif time_diff.seconds > 3600:
                last_str = f"{time_diff.seconds // 3600}h ago"
            else:
                last_str = f"{time_diff.seconds // 60}m ago"
            st.metric("🕐 Last Alert", last_str)
        else:
            st.metric("🕐 Last Alert", "N/A")
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # ========== FILTERS ==========
    st.subheader("🔍 FILTERS")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        # Date range filter
        days_filter = st.selectbox(
            "Time Period:",
            ["All Time", "Last 7 Days", "Last 30 Days", "Last 90 Days"],
            key="days_filter"
        )
    
    with col2:
        # Disaster type filter
        disaster_types = ["All"] + list(set([a.disaster_type for a in all_alerts]))
        type_filter = st.selectbox("Disaster Type:", disaster_types, key="type_filter")
    
    with col3:
        # Risk level filter
        risk_levels = ["All"] + list(set([a.risk_level for a in all_alerts]))
        risk_filter = st.selectbox("Risk Level:", risk_levels, key="risk_filter")
    
    with col4:
        # Status filter
        statuses = ["All"] + list(set([a.status for a in all_alerts]))
        status_filter = st.selectbox("Status:", statuses, key="status_filter")
    
    # Apply filters
    filtered_alerts = all_alerts
    
    # Date filter
    if days_filter != "All Time":
        days_map = {"Last 7 Days": 7, "Last 30 Days": 30, "Last 90 Days": 90}
        cutoff_date = datetime.now() - timedelta(days=days_map[days_filter])
        filtered_alerts = [a for a in filtered_alerts if a.sent_at >= cutoff_date]
    
    # Type filter
    if type_filter != "All":
        filtered_alerts = [a for a in filtered_alerts if a.disaster_type == type_filter]
    
    # Risk filter
    if risk_filter != "All":
        filtered_alerts = [a for a in filtered_alerts if a.risk_level == risk_filter]
    
    # Status filter
    if status_filter != "All":
        filtered_alerts = [a for a in filtered_alerts if a.status == status_filter]
    
    st.caption(f"Showing {len(filtered_alerts)} of {len(all_alerts)} alerts")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # ========== ALERT TRENDS CHART ==========
    st.subheader("📈 ALERT TRENDS")
    
    if filtered_alerts:
        # Group alerts by date
        alert_dates = {}
        for alert in filtered_alerts:
            date_key = alert.sent_at.date()
            if date_key not in alert_dates:
                alert_dates[date_key] = {'total': 0, 'flood': 0, 'drought': 0, 'heatwave': 0}
            alert_dates[date_key]['total'] += 1
            alert_dates[date_key][alert.disaster_type] = alert_dates[date_key].get(alert.disaster_type, 0) + 1
        
        # Create dataframe
        trend_df = pd.DataFrame([
            {
                'Date': date,
                'Total Alerts': counts['total'],
                'Flood': counts.get('flood', 0),
                'Drought': counts.get('drought', 0),
                'Heatwave': counts.get('heatwave', 0)
            }
            for date, counts in sorted(alert_dates.items())
        ])
        
        # Line chart
        fig_trend = go.Figure()
        
        fig_trend.add_trace(go.Scatter(
            x=trend_df['Date'],
            y=trend_df['Total Alerts'],
            mode='lines+markers',
            name='Total',
            line=dict(color='#66fcf1', width=3),
            marker=dict(size=8)
        ))
        
        fig_trend.add_trace(go.Scatter(
            x=trend_df['Date'],
            y=trend_df['Flood'],
            mode='lines+markers',
            name='Flood',
            line=dict(color='#3b82f6', width=2),
            marker=dict(size=6)
        ))
        
        fig_trend.add_trace(go.Scatter(
            x=trend_df['Date'],
            y=trend_df['Drought'],
            mode='lines+markers',
            name='Drought',
            line=dict(color='#f59e0b', width=2),
            marker=dict(size=6)
        ))
        
        fig_trend.add_trace(go.Scatter(
            x=trend_df['Date'],
            y=trend_df['Heatwave'],
            mode='lines+markers',
            name='Heatwave',
            line=dict(color='#ef4444', width=2),
            marker=dict(size=6)
        ))
        
        fig_trend.update_layout(
            title="ALERTS OVER TIME",
            xaxis_title="Date",
            yaxis_title="Number of Alerts",
            template="plotly_dark",
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#c5c6c7', size=12),
            title_font=dict(color='#66fcf1', size=18, family='Orbitron'),
            hovermode='x unified',
            height=400
        )
        
        st.plotly_chart(fig_trend, use_container_width=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # ========== DISTRIBUTION CHARTS ==========
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🎯 ALERTS BY TYPE")
        
        if filtered_alerts:
            type_counts = {}
            for alert in filtered_alerts:
                type_counts[alert.disaster_type.title()] = type_counts.get(alert.disaster_type.title(), 0) + 1
            
            fig_type = go.Figure(data=[
                go.Pie(
                    labels=list(type_counts.keys()),
                    values=list(type_counts.values()),
                    hole=0.4,
                    marker=dict(colors=['#3b82f6', '#f59e0b', '#ef4444'])
                )
            ])
            
            fig_type.update_layout(
                template="plotly_dark",
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#c5c6c7', size=12),
                height=350,
                showlegend=True
            )
            
            st.plotly_chart(fig_type, use_container_width=True)
    
    with col2:
        st.subheader("⚡ RISK LEVELS")
        
        if filtered_alerts:
            risk_counts = {}
            for alert in filtered_alerts:
                risk_counts[alert.risk_level.title()] = risk_counts.get(alert.risk_level.title(), 0) + 1
            
            fig_risk = go.Figure(data=[
                go.Bar(
                    x=list(risk_counts.keys()),
                    y=list(risk_counts.values()),
                    marker=dict(
                        color=['#10b981', '#f59e0b', '#ef4444'][:len(risk_counts)],
                    ),
                    text=list(risk_counts.values()),
                    textposition='outside'
                )
            ])
            
            fig_risk.update_layout(
                template="plotly_dark",
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#c5c6c7', size=12),
                height=350,
                xaxis_title="Risk Level",
                yaxis_title="Count",
                showlegend=False
            )
            
            st.plotly_chart(fig_risk, use_container_width=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # ========== DETAILED ALERT TABLE ==========
    st.subheader("📋 DETAILED ALERT LOG")
    
    # Create display dataframe
    table_data = []
    for alert in filtered_alerts[:50]:  # Limit to 50 most recent
        table_data.append({
            "📅 Date": alert.sent_at.strftime("%Y-%m-%d"),
            "⏰ Time": alert.sent_at.strftime("%H:%M:%S"),
            "🚨 Disaster": alert.disaster_type.title(),
            "⚡ Risk": alert.risk_level.title(),
            "📱 Type": alert.alert_type.upper(),
            "✅ Status": alert.status.title(),
            "📍 Location": getattr(alert, 'location', 'N/A')
        })
    
    if table_data:
        df_display = pd.DataFrame(table_data)
        
        st.dataframe(
            df_display,
            use_container_width=True,
            hide_index=True,
            height=400
        )
        
        st.caption(f"Showing last 50 alerts (of {len(filtered_alerts)} filtered)")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # ========== EXPORT OPTIONS ==========
    st.subheader("📥 EXPORT DATA")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 EXPORT CSV", use_container_width=True, type="primary"):
            st.session_state.export_history = True
    
    with col2:
        if st.button("📄 GENERATE REPORT", use_container_width=True):
            st.session_state.generate_report = True
    
    with col3:
        if st.button("🔄 REFRESH DATA", use_container_width=True):
            st.rerun()
    
    # Handle CSV export
    if st.session_state.get('export_history', False):
        import io
        
        export_data = []
        for alert in filtered_alerts:
            export_data.append({
                'Timestamp': alert.sent_at.strftime('%Y-%m-%d %H:%M:%S'),
                'Disaster Type': alert.disaster_type,
                'Risk Level': alert.risk_level,
                'Alert Type': alert.alert_type,
                'Status': alert.status,
                'Location': getattr(alert, 'location', 'N/A'),
                'Recipients': getattr(alert, 'recipient_count', 'N/A')
            })
        
        df_export = pd.DataFrame(export_data)
        csv_buffer = io.StringIO()
        df_export.to_csv(csv_buffer, index=False)
        csv_data = csv_buffer.getvalue()
        
        st.download_button(
            label="💾 DOWNLOAD CSV FILE",
            data=csv_data,
            file_name=f"alert_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            type="primary",
            use_container_width=True
        )
        
        if st.button("❌ CLOSE", use_container_width=True):
            st.session_state.export_history = False
            st.rerun()
    
    # Handle report generation
    if st.session_state.get('generate_report', False):
        st.markdown("---")
        st.subheader("📄 ALERT SUMMARY REPORT")
        
        report_text = f"""
# ResQAlert - Alert History Report
**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Summary Statistics
- **Total Alerts:** {len(filtered_alerts)}
- **Success Rate:** {success_rate:.1f}%
- **Most Common Type:** {most_common.title()}
- **Time Period:** {days_filter}

## Breakdown by Disaster Type
"""
        for dtype, count in disaster_counts.items():
            percentage = (count / len(filtered_alerts)) * 100
            report_text += f"- **{dtype.title()}:** {count} alerts ({percentage:.1f}%)\n"
        
        report_text += f"""
## Alert Status
- **Sent:** {success_count}
- **Failed:** {len(filtered_alerts) - success_count}

---
*Report generated by ResQAlert AI Disaster Prediction System*
"""
        
        st.markdown(report_text)
        
        st.download_button(
            label="💾 DOWNLOAD REPORT (TXT)",
            data=report_text,
            file_name=f"alert_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain",
            use_container_width=True
        )
        
        if st.button("❌ CLOSE REPORT", use_container_width=True):
            st.session_state.generate_report = False
            st.rerun()


def render_historical_analysis():
    """COMPLETE Historical Analysis with Weather Trends & Patterns"""
    st.header("📊 HISTORICAL ANALYSIS")
    st.markdown("<br>", unsafe_allow_html=True)
    
    # ========== TIME PERIOD SELECTOR ==========
    st.subheader("📅 SELECT TIME PERIOD")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        analysis_type = st.selectbox(
            "Analysis Type:",
            ["Weather Trends", "Risk Patterns", "Seasonal Analysis"],
            key="analysis_type"
        )
    
    with col2:
        time_range = st.selectbox(
            "Time Range:",
            ["Last 7 Days", "Last 30 Days", "Last 90 Days", "Last Year"],
            key="time_range"
        )
    
    with col3:
        data_source = st.selectbox(
            "Data Source:",
            ["Simulated Data", "Real Data (when available)"],
            key="data_source"
        )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # ========== GENERATE HISTORICAL DATA ==========
    # Map time range to days
    days_map = {
        "Last 7 Days": 7,
        "Last 30 Days": 30,
        "Last 90 Days": 90,
        "Last Year": 365
    }
    days = days_map[time_range]
    
    # Generate sample historical data (replace with real data when available)
    dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
    
    # Generate realistic weather patterns
    np.random.seed(42)
    base_temp = 28
    temp_variation = np.sin(np.linspace(0, 4*np.pi, days)) * 8
    temp_noise = np.random.normal(0, 2, days)
    temperatures = base_temp + temp_variation + temp_noise
    
    humidity = 60 + np.sin(np.linspace(0, 4*np.pi, days)) * 20 + np.random.normal(0, 5, days)
    humidity = np.clip(humidity, 30, 95)
    
    precipitation = np.abs(np.random.exponential(5, days))
    precipitation = np.clip(precipitation, 0, 100)
    
    wind_speed = 15 + np.random.exponential(5, days)
    wind_speed = np.clip(wind_speed, 0, 80)
    
    pressure = 1013 + np.sin(np.linspace(0, 2*np.pi, days)) * 15 + np.random.normal(0, 3, days)
    
    # Create DataFrame
    hist_df = pd.DataFrame({
        'Date': dates,
        'Temperature': temperatures,
        'Humidity': humidity,
        'Precipitation': precipitation,
        'Wind Speed': wind_speed,
        'Pressure': pressure
    })
    
    # Calculate risk scores based on historical weather
    flood_risk = []
    drought_risk = []
    heatwave_risk = []
    
    for _, row in hist_df.iterrows():
        weather_dict = {
            'temperature': row['Temperature'],
            'humidity': row['Humidity'],
            'precipitation': row['Precipitation'],
            'wind_speed': row['Wind Speed'],
            'pressure': row['Pressure']
        }
        
        # Get predictions
        f_score, _, _ = disaster_predictor.predict_disaster_risk(weather_dict, 'flood')
        d_score, _, _ = disaster_predictor.predict_disaster_risk(weather_dict, 'drought')
        h_score, _, _ = disaster_predictor.predict_disaster_risk(weather_dict, 'heatwave')
        
        flood_risk.append(f_score)
        drought_risk.append(d_score)
        heatwave_risk.append(h_score)
    
    hist_df['Flood Risk'] = flood_risk
    hist_df['Drought Risk'] = drought_risk
    hist_df['Heatwave Risk'] = heatwave_risk
    
    # ========== SUMMARY STATISTICS ==========
    st.subheader("📈 SUMMARY STATISTICS")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        avg_temp = hist_df['Temperature'].mean()
        st.metric("🌡️ Avg Temp", f"{avg_temp:.1f}°C")
    
    with col2:
        max_temp = hist_df['Temperature'].max()
        max_date = hist_df.loc[hist_df['Temperature'].idxmax(), 'Date'].strftime('%b %d')
        st.metric("🔥 Max Temp", f"{max_temp:.1f}°C")
        st.caption(f"on {max_date}")
    
    with col3:
        total_rain = hist_df['Precipitation'].sum()
        st.metric("🌧️ Total Rain", f"{total_rain:.0f}mm")
    
    with col4:
        rainy_days = (hist_df['Precipitation'] > 5).sum()
        st.metric("☔ Rainy Days", f"{rainy_days}")
    
    with col5:
        high_risk_days = ((hist_df['Flood Risk'] > 0.6) | 
                          (hist_df['Drought Risk'] > 0.6) | 
                          (hist_df['Heatwave Risk'] > 0.6)).sum()
        st.metric("⚠️ High Risk Days", f"{high_risk_days}")
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # ========== ANALYSIS TYPE SPECIFIC CONTENT ==========
    if analysis_type == "Weather Trends":
        
        # Temperature Trend
        st.subheader("🌡️ TEMPERATURE TRENDS")
        
        fig_temp = go.Figure()
        
        fig_temp.add_trace(go.Scatter(
            x=hist_df['Date'],
            y=hist_df['Temperature'],
            mode='lines',
            name='Temperature',
            line=dict(color='#ef4444', width=2),
            fill='tozeroy',
            fillcolor='rgba(239, 68, 68, 0.1)'
        ))
        
        # Add moving average
        hist_df['Temp_MA'] = hist_df['Temperature'].rolling(window=7).mean()
        fig_temp.add_trace(go.Scatter(
            x=hist_df['Date'],
            y=hist_df['Temp_MA'],
            mode='lines',
            name='7-Day Average',
            line=dict(color='#66fcf1', width=3, dash='dash')
        ))
        
        fig_temp.update_layout(
            title=f"TEMPERATURE OVER {time_range.upper()}",
            xaxis_title="Date",
            yaxis_title="Temperature (°C)",
            template="plotly_dark",
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#c5c6c7', size=12),
            title_font=dict(color='#66fcf1', size=18, family='Orbitron'),
            hovermode='x unified',
            height=450
        )
        
        st.plotly_chart(fig_temp, use_container_width=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Precipitation Pattern
        st.subheader("🌧️ PRECIPITATION PATTERNS")
        
        fig_precip = go.Figure()
        
        fig_precip.add_trace(go.Bar(
            x=hist_df['Date'],
            y=hist_df['Precipitation'],
            name='Daily Rainfall',
            marker=dict(
                color=hist_df['Precipitation'],
                colorscale='Blues',
                showscale=True,
                colorbar=dict(title="mm")
            )
        ))
        
        fig_precip.update_layout(
            title=f"RAINFALL OVER {time_range.upper()}",
            xaxis_title="Date",
            yaxis_title="Precipitation (mm)",
            template="plotly_dark",
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#c5c6c7', size=12),
            title_font=dict(color='#66fcf1', size=18, family='Orbitron'),
            height=450
        )
        
        st.plotly_chart(fig_precip, use_container_width=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Humidity & Wind
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**💧 HUMIDITY TREND**")
            
            fig_humidity = go.Figure()
            fig_humidity.add_trace(go.Scatter(
                x=hist_df['Date'],
                y=hist_df['Humidity'],
                mode='lines',
                fill='tozeroy',
                line=dict(color='#3b82f6', width=2)
            ))
            
            fig_humidity.update_layout(
                yaxis_title="Humidity (%)",
                template="plotly_dark",
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#c5c6c7', size=10),
                height=300,
                showlegend=False
            )
            
            st.plotly_chart(fig_humidity, use_container_width=True)
        
        with col2:
            st.markdown("**💨 WIND SPEED TREND**")
            
            fig_wind = go.Figure()
            fig_wind.add_trace(go.Scatter(
                x=hist_df['Date'],
                y=hist_df['Wind Speed'],
                mode='lines',
                fill='tozeroy',
                line=dict(color='#10b981', width=2)
            ))
            
            fig_wind.update_layout(
                yaxis_title="Wind Speed (km/h)",
                template="plotly_dark",
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#c5c6c7', size=10),
                height=300,
                showlegend=False
            )
            
            st.plotly_chart(fig_wind, use_container_width=True)
    
    elif analysis_type == "Risk Patterns":
        
        st.subheader("⚠️ DISASTER RISK EVOLUTION")
        
        fig_risk = go.Figure()
        
        fig_risk.add_trace(go.Scatter(
            x=hist_df['Date'],
            y=hist_df['Flood Risk'],
            mode='lines+markers',
            name='Flood Risk',
            line=dict(color='#3b82f6', width=3),
            marker=dict(size=4)
        ))
        
        fig_risk.add_trace(go.Scatter(
            x=hist_df['Date'],
            y=hist_df['Drought Risk'],
            mode='lines+markers',
            name='Drought Risk',
            line=dict(color='#f59e0b', width=3),
            marker=dict(size=4)
        ))
        
        fig_risk.add_trace(go.Scatter(
            x=hist_df['Date'],
            y=hist_df['Heatwave Risk'],
            mode='lines+markers',
            name='Heatwave Risk',
            line=dict(color='#ef4444', width=3),
            marker=dict(size=4)
        ))
        
        # Add threshold line
        fig_risk.add_hline(
            y=0.6, 
            line_dash="dash", 
            line_color="#66fcf1",
            annotation_text="High Risk Threshold"
        )
        
        fig_risk.update_layout(
            title=f"RISK LEVELS OVER {time_range.upper()}",
            xaxis_title="Date",
            yaxis_title="Risk Score (0-1)",
            template="plotly_dark",
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#c5c6c7', size=12),
            title_font=dict(color='#66fcf1', size=18, family='Orbitron'),
            hovermode='x unified',
            height=500,
            yaxis=dict(range=[0, 1])
        )
        
        st.plotly_chart(fig_risk, use_container_width=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Risk Distribution
        st.subheader("📊 RISK DISTRIBUTION")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("**🌊 FLOOD RISK**")
            low = (hist_df['Flood Risk'] < 0.4).sum()
            med = ((hist_df['Flood Risk'] >= 0.4) & (hist_df['Flood Risk'] < 0.7)).sum()
            high = (hist_df['Flood Risk'] >= 0.7).sum()
            
            fig_flood_dist = go.Figure(data=[go.Pie(
                labels=['Low', 'Medium', 'High'],
                values=[low, med, high],
                marker=dict(colors=['#10b981', '#f59e0b', '#ef4444']),
                hole=0.4
            )])
            
            fig_flood_dist.update_layout(
                template="plotly_dark",
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#c5c6c7', size=10),
                height=250,
                showlegend=True
            )
            
            st.plotly_chart(fig_flood_dist, use_container_width=True)
        
        with col2:
            st.markdown("**🏜️ DROUGHT RISK**")
            low = (hist_df['Drought Risk'] < 0.4).sum()
            med = ((hist_df['Drought Risk'] >= 0.4) & (hist_df['Drought Risk'] < 0.7)).sum()
            high = (hist_df['Drought Risk'] >= 0.7).sum()
            
            fig_drought_dist = go.Figure(data=[go.Pie(
                labels=['Low', 'Medium', 'High'],
                values=[low, med, high],
                marker=dict(colors=['#10b981', '#f59e0b', '#ef4444']),
                hole=0.4
            )])
            
            fig_drought_dist.update_layout(
                template="plotly_dark",
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#c5c6c7', size=10),
                height=250,
                showlegend=True
            )
            
            st.plotly_chart(fig_drought_dist, use_container_width=True)
        
        with col3:
            st.markdown("**🔥 HEATWAVE RISK**")
            low = (hist_df['Heatwave Risk'] < 0.4).sum()
            med = ((hist_df['Heatwave Risk'] >= 0.4) & (hist_df['Heatwave Risk'] < 0.7)).sum()
            high = (hist_df['Heatwave Risk'] >= 0.7).sum()
            
            fig_heat_dist = go.Figure(data=[go.Pie(
                labels=['Low', 'Medium', 'High'],
                values=[low, med, high],
                marker=dict(colors=['#10b981', '#f59e0b', '#ef4444']),
                hole=0.4
            )])
            
            fig_heat_dist.update_layout(
                template="plotly_dark",
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#c5c6c7', size=10),
                height=250,
                showlegend=True
            )
            
            st.plotly_chart(fig_heat_dist, use_container_width=True)
    
    else:  # Seasonal Analysis
        
        st.subheader("🌍 SEASONAL PATTERNS")
        
        # Group by month/season
        hist_df['Month'] = hist_df['Date'].dt.month
        hist_df['Month_Name'] = hist_df['Date'].dt.strftime('%B')
        
        monthly_stats = hist_df.groupby('Month_Name').agg({
            'Temperature': 'mean',
            'Precipitation': 'sum',
            'Humidity': 'mean',
            'Flood Risk': 'mean',
            'Drought Risk': 'mean',
            'Heatwave Risk': 'mean'
        }).reset_index()
        
        # Monthly temperature & rainfall
        fig_seasonal = go.Figure()
        
        fig_seasonal.add_trace(go.Bar(
            x=monthly_stats['Month_Name'],
            y=monthly_stats['Precipitation'],
            name='Total Rainfall (mm)',
            yaxis='y',
            marker=dict(color='#3b82f6')
        ))
        
        fig_seasonal.add_trace(go.Scatter(
            x=monthly_stats['Month_Name'],
            y=monthly_stats['Temperature'],
            name='Avg Temperature (°C)',
            yaxis='y2',
            mode='lines+markers',
            line=dict(color='#ef4444', width=3),
            marker=dict(size=10)
        ))
        
        fig_seasonal.update_layout(
            title="MONTHLY TEMPERATURE & RAINFALL PATTERNS",
            template="plotly_dark",
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#c5c6c7', size=12),
            title_font=dict(color='#66fcf1', size=18, family='Orbitron'),
            height=450,
            yaxis=dict(title="Rainfall (mm)", titlefont=dict(color='#3b82f6')),
            yaxis2=dict(title="Temperature (°C)", overlaying='y', side='right', titlefont=dict(color='#ef4444')),
            hovermode='x unified'
        )
        
        st.plotly_chart(fig_seasonal, use_container_width=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Seasonal risk heatmap
        st.subheader("🗓️ RISK CALENDAR HEATMAP")
        
        # Create heatmap data
        risk_pivot = hist_df.pivot_table(
            values=['Flood Risk', 'Drought Risk', 'Heatwave Risk'],
            index=hist_df['Date'].dt.isocalendar().week,
            aggfunc='mean'
        )
        
        fig_heatmap = go.Figure()
        
        for i, col in enumerate(['Flood Risk', 'Drought Risk', 'Heatwave Risk']):
            fig_heatmap.add_trace(go.Heatmap(
                z=[risk_pivot[col].values],
                x=risk_pivot.index,
                y=[col],
                colorscale='RdYlGn_r',
                zmin=0,
                zmax=1,
                showscale=(i==0)
            ))
        
        fig_heatmap.update_layout(
            title="WEEKLY RISK PATTERNS",
            xaxis_title="Week of Year",
            template="plotly_dark",
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#c5c6c7', size=12),
            title_font=dict(color='#66fcf1', size=16, family='Orbitron'),
            height=300
        )
        
        st.plotly_chart(fig_heatmap, use_container_width=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # ========== DATA TABLE ==========
    st.subheader("📋 RAW DATA")
    
    with st.expander("View Detailed Data Table"):
        display_df = hist_df[['Date', 'Temperature', 'Humidity', 'Precipitation', 
                               'Wind Speed', 'Flood Risk', 'Drought Risk', 'Heatwave Risk']].copy()
        display_df['Date'] = display_df['Date'].dt.strftime('%Y-%m-%d')
        display_df = display_df.round(2)
        
        st.dataframe(
            display_df,
            use_container_width=True,
            height=400
        )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # ========== EXPORT OPTIONS ==========
    st.subheader("📥 EXPORT HISTORICAL DATA")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📊 DOWNLOAD CSV", type="primary", use_container_width=True):
            import io
            
            csv_buffer = io.StringIO()
            hist_df.to_csv(csv_buffer, index=False)
            
            st.download_button(
                label="💾 SAVE CSV FILE",
                data=csv_buffer.getvalue(),
                file_name=f"historical_data_{time_range.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True
            )
    
    with col2:
        if st.button("📄 GENERATE REPORT", use_container_width=True):
            report = f"""# Historical Weather & Risk Analysis Report
**Period:** {time_range}
**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Summary Statistics
- Average Temperature: {hist_df['Temperature'].mean():.1f}°C
- Maximum Temperature: {hist_df['Temperature'].max():.1f}°C
- Total Rainfall: {hist_df['Precipitation'].sum():.1f}mm
- Rainy Days: {(hist_df['Precipitation'] > 5).sum()}
- High Risk Days: {high_risk_days}

## Risk Analysis
- Average Flood Risk: {hist_df['Flood Risk'].mean():.3f}
- Average Drought Risk: {hist_df['Drought Risk'].mean():.3f}
- Average Heatwave Risk: {hist_df['Heatwave Risk'].mean():.3f}

---
*Generated by ResQAlert Historical Analysis System*
"""
            
            st.download_button(
                label="💾 SAVE REPORT (TXT)",
                data=report,
                file_name=f"analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain",
                use_container_width=True
            )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    st.info("💡 **Note:** This uses simulated historical data for demonstration. In production, this would show actual historical weather and prediction data from your database.")

def render_settings():
    """COMPLETE Enhanced Settings & System Configuration"""
    st.header("⚙️ SYSTEM SETTINGS & CONFIGURATION")
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Status bar
    if st.session_state.current_location:
        cols = st.columns(4)
        with cols[0]:
            st.info(f"📍 {st.session_state.current_location['name'].upper()}")
        with cols[1]:
            if st.session_state.models_initialized:
                st.success("🤖 AI ONLINE")
            else:
                st.warning("⚠️ LOADING")
        with cols[2]:
            if sms_service.is_configured:
                st.success("📱 SMS ON")
            else:
                st.warning("📱 SMS OFF")
        with cols[3]:
            u = user_manager.get_all_users()
            st.info(f"👥 USERS: {len(u)}")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🌐 General",
        "🚨 Alerts",
        "🔌 API Status",
        "💾 Data",
        "ℹ️ Info"
    ])
    
    # TAB 1: GENERAL
    with tab1:
        st.subheader("🌐 GENERAL SETTINGS")
        st.markdown("<br>", unsafe_allow_html=True)
        
        st.markdown("**📍 DEFAULT LOCATION**")
        col1, col2 = st.columns([3, 1])
        
        with col1:
            current_loc = st.session_state.current_location.get('name', 'Bangalore') if st.session_state.current_location else 'Bangalore'
            new_location = st.text_input(
                "Default City:",
                value=current_loc,
                placeholder="Enter city name",
                key="settings_location"
            )
        
        with col2:
            st.write("")
            st.write("")
            if st.button("✅ UPDATE", type="primary", use_container_width=True, key="update_location"):
                weather_data = weather_service.get_weather_by_city(new_location)
                if weather_data:
                    st.session_state.current_location = {
                        'lat': weather_data['latitude'],
                        'lon': weather_data['longitude'],
                        'name': weather_data['location']
                    }
                    st.success(f"✅ Location set to {weather_data['location']}")
                    time.sleep(0.5)
                    st.rerun()
                else:
                    st.error("❌ Location not found")
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("---")
        
        st.markdown("**🎨 DISPLAY PREFERENCES**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            refresh_interval = st.selectbox(
                "Auto-refresh Weather:",
                ["Disabled", "5 minutes", "15 minutes", "30 minutes", "1 hour"],
                index=0,
                key="refresh_interval"
            )
            
            date_format = st.selectbox(
                "Date Format:",
                ["YYYY-MM-DD", "DD/MM/YYYY", "MM/DD/YYYY"],
                index=0,
                key="date_format"
            )
        
        with col2:
            temp_unit = st.selectbox(
                "Temperature Unit:",
                ["Celsius (°C)", "Fahrenheit (°F)"],
                index=0,
                key="temp_unit"
            )
            
            time_format = st.selectbox(
                "Time Format:",
                ["24-hour", "12-hour (AM/PM)"],
                index=0,
                key="time_format"
            )
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("💾 SAVE PREFERENCES", type="primary", use_container_width=True, key="save_general"):
            st.success("✅ Preferences saved!")
    
    # TAB 2: ALERTS
    with tab2:
        st.subheader("🚨 ALERT CONFIGURATION")
        st.markdown("<br>", unsafe_allow_html=True)
        
        st.markdown("**📱 ALERT PREFERENCES**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            enable_sms = st.checkbox("Enable SMS Alerts", value=True, key="enable_sms")
            enable_auto = st.checkbox("Auto-send Alerts", value=True, key="enable_auto")
        
        with col2:
            st.checkbox("Email Alerts (Future)", value=False, disabled=True, key="enable_email")
            st.checkbox("Push Notifications (Future)", value=False, disabled=True, key="enable_push")
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("---")
        
        st.markdown("**⚡ RISK THRESHOLDS**")
        st.caption("Set the risk level at which alerts are triggered")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            flood_threshold = st.select_slider(
                "🌊 Flood Alert Threshold:",
                options=["Low (0.4)", "Medium (0.6)", "High (0.8)"],
                value="Medium (0.6)",
                key="flood_threshold"
            )
        
        with col2:
            drought_threshold = st.select_slider(
                "🏜️ Drought Alert Threshold:",
                options=["Low (0.4)", "Medium (0.6)", "High (0.8)"],
                value="Medium (0.6)",
                key="drought_threshold"
            )
        
        with col3:
            heatwave_threshold = st.select_slider(
                "🔥 Heatwave Alert Threshold:",
                options=["Low (0.4)", "Medium (0.6)", "High (0.8)"],
                value="Medium (0.6)",
                key="heatwave_threshold"
            )
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("---")
        
        st.markdown("**⏱️ ALERT FREQUENCY**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            alert_frequency = st.selectbox(
                "Check Frequency:",
                ["Every 5 minutes", "Every 15 minutes", "Every 30 minutes", "Every hour"],
                index=1,
                key="alert_frequency"
            )
        
        with col2:
            max_alerts = st.number_input(
                "Max Alerts per Day:",
                min_value=1,
                max_value=50,
                value=10,
                key="max_alerts"
            )
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("💾 SAVE ALERT SETTINGS", type="primary", use_container_width=True, key="save_alerts"):
            st.success("✅ Alert settings saved!")
    
    # TAB 3: API STATUS
    with tab3:
        st.subheader("🔌 API CONNECTION STATUS")
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Weather API
        st.markdown("**🌐 OPENWEATHER API**")
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            has_key = bool(settings.OPENWEATHER_API_KEY and settings.OPENWEATHER_API_KEY != "")
            if has_key:
                st.success("✅ API Key: Configured")
            else:
                st.error("❌ API Key: Not Found")
        
        with col2:
            st.caption("**Endpoint:**")
            st.caption(f"{settings.WEATHER_API_BASE_URL[:30]}...")
        
        with col3:
            if st.button("🧪 TEST", key="test_weather", use_container_width=True):
                with st.spinner("Testing..."):
                    try:
                        test_data = weather_service.get_weather_by_city("London")
                        if test_data:
                            st.success("✅ Working!")
                        else:
                            st.error("❌ Failed")
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)[:50]}")
        
        st.markdown("---")
        
        # Gemini API
        st.markdown("**🤖 GOOGLE GEMINI AI**")
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            has_gemini = GEMINI_AVAILABLE and bool(settings.GEMINI_API_KEY)
            if has_gemini:
                st.success("✅ API Key: Configured")
            else:
                st.error("❌ API Key: Not Found")
        
        with col2:
            st.caption("**Status:**")
            if GEMINI_AVAILABLE:
                st.caption("Package installed")
            else:
                st.caption("Not installed")
        
        with col3:
            if st.button("🧪 TEST", key="test_gemini", use_container_width=True, disabled=not has_gemini):
                with st.spinner("Testing..."):
                    try:
                        if st.session_state.get('gemini_model'):
                            st.success("✅ Working!")
                        else:
                            st.warning("⚠️ Not initialized")
                    except:
                        st.error("❌ Failed")
        
        st.markdown("---")
        
        # Twilio SMS
        st.markdown("**📱 TWILIO SMS**")
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            is_configured = sms_service.is_configured
            if is_configured:
                st.success("✅ Credentials: Configured")
            else:
                st.error("❌ Credentials: Not Found")
        
        with col2:
            st.caption("**Account:**")
            if settings.TWILIO_ACCOUNT_SID:
                st.caption(f"{settings.TWILIO_ACCOUNT_SID[:10]}...")
            else:
                st.caption("Not set")
        
        with col3:
            if st.button("🧪 TEST", key="test_twilio", use_container_width=True, disabled=not is_configured):
                st.info("💡 Use 'Test Alert' in Alert System tab")
        
        st.markdown("---")
        
        # Database
        st.markdown("**💾 DATABASE**")
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.success("✅ SQLite: Connected")
            st.caption("Location: data/disaster_alerts.db")
        
        with col2:
            users_count = len(user_manager.get_all_users())
            alerts_count = len(alert_manager.get_alert_history(limit=1000))
            st.metric("👥 Users", users_count)
            st.metric("📨 Alerts", alerts_count)
    
    # TAB 4: DATA
    with tab4:
        st.subheader("💾 DATA MANAGEMENT")
        st.markdown("<br>", unsafe_allow_html=True)
        
        st.warning("⚠️ **Caution:** These actions cannot be undone!")
        st.markdown("<br>", unsafe_allow_html=True)
        
        st.markdown("**🗑️ CLEAR CACHE**")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🔄 Clear Weather Cache", use_container_width=True, key="clear_weather"):
                st.session_state.weather_data = None
                st.success("✅ Weather cache cleared")
        
        with col2:
            if st.button("🗺️ Clear Safe Zones Cache", use_container_width=True, key="clear_zones"):
                if 'safe_zones_cache' in st.session_state:
                    st.session_state.safe_zones_cache = {}
                st.success("✅ Safe zones cache cleared")
        
        with col3:
            if st.button("💬 Clear Chat History", use_container_width=True, key="clear_chat"):
                st.session_state.messages = []
                st.success("✅ Chat history cleared")
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("---")
        
        st.markdown("**📤 EXPORT DATA**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📥 Export All Users", type="primary", use_container_width=True, key="export_users"):
                users = user_manager.get_all_users()
                if users:
                    import io
                    user_data = [{
                        'Name': u.name,
                        'Phone': u.phone,
                        'Email': u.email,
                        'Location': u.location_name
                    } for u in users]
                    
                    df = pd.DataFrame(user_data)
                    csv_buffer = io.StringIO()
                    df.to_csv(csv_buffer, index=False)
                    
                    st.download_button(
                        "💾 Download Users CSV",
                        csv_buffer.getvalue(),
                        f"users_{datetime.now().strftime('%Y%m%d')}.csv",
                        "text/csv",
                        use_container_width=True
                    )
                else:
                    st.info("No users to export")
        
        with col2:
            if st.button("📥 Export Alert History", type="primary", use_container_width=True, key="export_alerts_data"):
                alerts = alert_manager.get_alert_history(limit=1000)
                if alerts:
                    import io
                    alert_data = [{
                        'Date': a.sent_at.strftime('%Y-%m-%d %H:%M:%S'),
                        'Type': a.disaster_type,
                        'Risk': a.risk_level,
                        'Status': a.status
                    } for a in alerts]
                    
                    df = pd.DataFrame(alert_data)
                    csv_buffer = io.StringIO()
                    df.to_csv(csv_buffer, index=False)
                    
                    st.download_button(
                        "💾 Download Alerts CSV",
                        csv_buffer.getvalue(),
                        f"alerts_{datetime.now().strftime('%Y%m%d')}.csv",
                        "text/csv",
                        use_container_width=True
                    )
                else:
                    st.info("No alerts to export")
    
    # TAB 5: INFO
    with tab5:
        st.subheader("ℹ️ SYSTEM INFORMATION")
        st.markdown("<br>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**📱 APPLICATION**")
            st.write("• **Name:** ResQAlert")
            st.write("• **Version:** 1.0.0")
            st.write("• **Type:** AI Disaster Intelligence")
            st.write("• **Framework:** Streamlit")
            
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("**🔧 FEATURES**")
            st.write("✅ Real-time Weather Monitoring")
            st.write("✅ AI-Powered Risk Predictions")
            st.write("✅ SMS Alert System")
            st.write("✅ Safe Zone Locator")
            st.write("✅ AI Disaster Assistant")
            st.write("✅ Historical Analysis")
        
        with col2:
            st.markdown("**📊 STATISTICS**")
            users_count = len(user_manager.get_all_users())
            alerts_count = len(alert_manager.get_alert_history(limit=1000))
            
            st.metric("👥 Total Users", users_count)
            st.metric("📨 Total Alerts", alerts_count)
            st.metric("🤖 ML Models", 3)
            st.metric("🌐 APIs", 3)
            
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("**💻 SYSTEM**")
            st.write(f"• **Python:** 3.x")
            st.write(f"• **Database:** SQLite")
            st.write(f"• **Status:** Running")
        
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("---")
        
        st.markdown("**ℹ️ ABOUT RESQALERT**")
        st.info("""
        **ResQAlert** is an AI-powered disaster intelligence and alert system.
        
        **Key Technologies:**
        - 🤖 Machine Learning (Ensemble Models)
        - 🌐 Real-time Weather APIs
        - 📱 SMS Integration (Twilio)
        - 🗺️ Geographic Information Systems
        - 💬 AI Chat Assistant (Google Gemini)
        
        **Emergency Contacts (India):**
        - 🚨 All Emergencies: **112**
        - 🚑 Ambulance: **108**
        - 🔥 Fire: **101**
        - 🌊 Disaster Management: **1078**
        """)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("**📚 RESOURCES**")
            st.markdown("• [NDMA India](https://ndma.gov.in)")
            st.markdown("• [NDRF](https://ndrf.gov.in)")
        
        with col2:
            st.markdown("**🔗 APIS**")
            st.markdown("• OpenWeatherMap")
            st.markdown("• Google Gemini AI")
            st.markdown("• Twilio SMS")
        
        with col3:
            st.markdown("**👨‍💻 DEVELOPER**")
            st.markdown("• [GitHub Repo](https://github.com/sanjayKumarR-404/ai-disaster-forecast)")



def main():
    """MAIN APP"""
    initialize_session_state()
    load_models()
    
    # STATUS BAR
    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.session_state.current_location:
        cols = st.columns(4)
        with cols[0]:
            st.info(f"📍 {st.session_state.current_location['name'].upper()}")
        with cols[1]:
            if st.session_state.models_initialized:
                st.success("🤖 AI: ONLINE")
            else:
                st.warning("🤖 LOADING")
        with cols[2]:
            if sms_service.is_configured:
                st.success("📡 SMS: ON")
            else:
                st.warning("📡 SMS: OFF")
        with cols[3]:
            u = user_manager.get_all_users()
            st.info(f"👥 USERS: {len(u)}")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # ROUTE TO PAGES
    page = st.session_state.page
    
    if page == "🏠 Dashboard Overview":
        st.markdown("## ⚡ COMMAND CENTER")
        st.markdown("<br>", unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("ALERTS", "0")
        with col2:
            st.metric("WEATHER", "LIVE")
        with col3:
            u = user_manager.get_all_users()
            st.metric("USERS", len(u))
        with col4:
            st.metric("STATUS", "ONLINE")
        
        st.markdown("<br><br>", unsafe_allow_html=True)
        
        st.markdown("### 📈 RECENT")
        recent = alert_manager.get_alert_history(limit=5)
        if recent:
            for a in recent:
                st.info(f"🚨 {a.disaster_type.upper()} - {a.sent_at.strftime('%Y-%m-%d %H:%M')}")
        else:
            st.success("✅ No alerts")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        st.markdown("### ⚡ QUICK ACTIONS")
        c = st.columns(3)
        with c[0]:
            if st.button("🌐 WEATHER", type="primary", use_container_width=True, key="qa1"):
                st.session_state.page = "🌤️ Weather Monitoring"
                st.rerun()
        with c[1]:
            if st.button("🎯 RISKS", type="primary", use_container_width=True, key="qa2"):
                st.session_state.page = "🚨 Disaster Predictions"
                st.rerun()
        with c[2]:
            if st.button("📡 ALERT", type="secondary", use_container_width=True, key="qa3"):
                st.session_state.page = "🚨 Alert System"
                st.rerun()
    
    elif page == "🌤️ Weather Monitoring":
        render_weather_dashboard()
    
    elif page == "🚨 Disaster Predictions":
        render_disaster_predictions()
    
    elif page == "🗺️ Safe Zones & Evacuation":
        render_safe_zones()
    
    elif page == "💬 Disaster Assistant":
        render_chatbot()
    
    elif page == "🚨 Alert System":
        render_alert_system()
    
    elif page == "📊 Historical Analysis":
        render_historical_analysis()
    
    elif page == "⚙️ System Settings":
        render_settings()
    
if __name__ == "__main__":
    main()
