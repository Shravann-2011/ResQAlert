"""
Main Streamlit dashboard for ResQAlert system with SMS Alert Integration
FUTURISTIC UI + FIXED ERRORS + PERFECT ALIGNMENT
"""

import streamlit as st

# Page configuration - MUST BE FIRST STREAMLIT COMMAND
st.set_page_config(
    page_title="ResQAlert | AI Disaster Intelligence",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Now import everything else
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

# Import UI configuration
from config.ui_config import apply_custom_css, render_navigation

# Import utilities
from utils.session import initialize_session_state
from utils.models import load_models

# Import all page renderers
from pages.overview_dashboard import render_overview_dashboard
from pages.dashboard import render_weather_dashboard
from pages.predictions import render_disaster_predictions
from pages.safe_zones import render_safe_zones
from pages.chatbot import render_chatbot
from pages.alerts import render_alert_system
from pages.user_registration import render_user_registration
from pages.test_alerts import render_test_alerts
from pages.disaster_alert_sender import render_disaster_alert_sender
from pages.alert_history import render_alert_history
from pages.historical_analysis import render_historical_analysis
from pages.settings import render_settings

# Initialize page state
if "page" not in st.session_state:
    st.session_state.page = "🏠 Dashboard Overview"

# Apply custom CSS and navigation
apply_custom_css()
render_navigation()

# ============ LOGOUT BUTTON AS TOP MENU ICON ============
# ============ LOGOUT BUTTON AS TOP MENU ICON ============
col1, col2, col3 = st.columns([6, 1, 1])
with col3:
    if st.button("🚪 Logout", key="logout_btn", use_container_width=True):
        # Clear all session state
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        
        # Redirect using Streamlit's native method
        st.markdown("""
            <meta http-equiv="refresh" content="0; url=http://localhost:5000" />
            <style>
                .logout-overlay {
                    position: fixed;
                    top: 0;
                    left: 0;
                    width: 100vw;
                    height: 100vh;
                    background: rgba(10, 14, 39, 0.98);
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    z-index: 999999;
                    animation: fadeIn 0.3s ease;
                }
                .logout-box {
                    text-align: center;
                    padding: 50px;
                    border: 3px solid #00f0ff;
                    border-radius: 25px;
                    background: rgba(10, 14, 39, 0.95);
                    box-shadow: 0 0 50px rgba(0, 240, 255, 0.5);
                    animation: scaleIn 0.5s ease;
                }
                .logout-icon {
                    font-size: 5rem;
                    margin-bottom: 20px;
                    animation: wave 1s ease infinite;
                }
                .logout-title {
                    font-size: 2.5rem;
                    background: linear-gradient(90deg, #00f0ff, #ff00e6);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                    font-weight: 900;
                    margin: 20px 0;
                }
                .logout-text {
                    color: rgba(0, 240, 255, 0.8);
                    font-size: 1.2rem;
                }
                @keyframes fadeIn {
                    from { opacity: 0; }
                    to { opacity: 1; }
                }
                @keyframes scaleIn {
                    from { transform: scale(0.8); opacity: 0; }
                    to { transform: scale(1); opacity: 1; }
                }
                @keyframes wave {
                    0%, 100% { transform: rotate(0deg); }
                    25% { transform: rotate(-10deg); }
                    75% { transform: rotate(10deg); }
                }
            </style>
            <div class="logout-overlay">
                <div class="logout-box">
                    <div class="logout-icon">👋</div>
                    <div class="logout-title">Logged Out Successfully</div>
                    <div class="logout-text">Redirecting to homepage...</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        st.stop()
# ============ END OF LOGOUT BUTTON ============

# ============ END OF LOGOUT BUTTON ============

def main():
    """Main application entry point"""
    # Initialize session state
    initialize_session_state()
    
    # Load models
    load_models()
    
    # Page routing
    page = st.session_state.page
    
    if page == "🏠 Dashboard Overview":
        render_overview_dashboard()
    elif page == "☁️ Weather Monitoring":
        render_weather_dashboard()
    elif page == "🔮 Disaster Predictions":
        render_disaster_predictions()
    elif page == "🗺️ Safe Zones":
        render_safe_zones()
    elif page == "💬 AI Assistant":
        render_chatbot()
    elif page == "🚨 Alert System":
        render_alert_system()
    elif page == "📊 Historical Analysis":
        render_historical_analysis()
    elif page == "⚙️ Settings":
        render_settings()
    else:
        render_overview_dashboard()


if __name__ == "__main__":
    main()
