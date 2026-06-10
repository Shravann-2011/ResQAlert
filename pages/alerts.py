import streamlit as st
import time

from services.sms_service import sms_service
from app.user_management import user_manager
from app.alert_manager import alert_manager

# Import the sub-page renderers
from pages.user_registration import render_user_registration
from pages.test_alerts import render_test_alerts
from pages.disaster_alert_sender import render_disaster_alert_sender
from pages.alert_history import render_alert_history

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
