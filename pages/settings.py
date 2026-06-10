import streamlit as st
import json
import time

from config.settings import settings
from services.sms_service import sms_service  # ← ADD THIS LINE
from app.user_management import user_manager  # ← ADD THIS LINE
from services.weather_service import weather_service  # ← ADD THIS LINE
from app.alert_manager import alert_manager

# Gemini availability flag (same logic as in main.py)
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False


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
