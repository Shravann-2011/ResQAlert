import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta

from services.weather_service import weather_service
from models.disaster_prediction import disaster_predictor
from app.user_management import user_manager
from app.alert_manager import alert_manager
from services.sms_service import sms_service

def render_overview_dashboard():
    """Professional Dashboard Overview - Main Entry Point"""
    
    st.markdown("## 🏠 DASHBOARD OVERVIEW")
    st.markdown("**Real-time Disaster Intelligence & Monitoring System**")
    st.markdown("---")
    
    # ============================================
    # SECTION 1: SYSTEM STATUS BAR
    # ============================================
    st.markdown("### 📊 System Status")
    status_cols = st.columns(5)
    
    with status_cols[0]:
        if st.session_state.get('current_location'):
            location = st.session_state.current_location.get('name', 'Unknown')
            st.metric("📍 Location", location)
        else:
            st.metric("📍 Location", "Not Set")
    
    with status_cols[1]:
        if st.session_state.get('models_loaded', False):
            st.metric("🤖 AI Models", "Online", delta="Ready")
        else:
            st.metric("🤖 AI Models", "Loading", delta="Please wait")
    
    with status_cols[2]:
        users = user_manager.get_all_users()
        st.metric("👥 Registered Users", len(users))
    
    with status_cols[3]:
        if sms_service.is_configured:
            st.metric("📱 SMS Alerts", "Active", delta="Enabled")
        else:
            st.metric("📱 SMS Alerts", "Inactive", delta="Disabled", delta_color="inverse")
    
    with status_cols[4]:
        # Use the correct AlertManager method
        try:
            alert_history = alert_manager.get_alert_history()
            recent_alerts = [a for a in alert_history if (datetime.now() - datetime.fromisoformat(a['timestamp'])).days <= 7]
            st.metric("🚨 Alerts (7d)", len(recent_alerts))
        except:
            st.metric("🚨 Alerts (7d)", "N/A")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # ============================================
    # SECTION 2: REAL-TIME WEATHER & RISK OVERVIEW
    # ============================================
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 🌦️ Current Weather Conditions")
        
        if st.session_state.get('weather_data'):
            weather = st.session_state.weather_data
            
            # Weather metrics in a nice grid
            w_cols = st.columns(4)
            
            with w_cols[0]:
                temp = weather.get('temperature', 0)
                st.metric("🌡️ Temperature", f"{temp:.1f}°C")
            
            with w_cols[1]:
                humidity = weather.get('humidity', 0)
                st.metric("💧 Humidity", f"{humidity:.0f}%")
            
            with w_cols[2]:
                wind = weather.get('wind_speed', 0)
                st.metric("💨 Wind Speed", f"{wind:.1f} km/h")
            
            with w_cols[3]:
                precip = weather.get('precipitation', 0)
                st.metric("🌧️ Precipitation", f"{precip:.1f} mm")
            
            # Quick weather status
            st.markdown("<br>", unsafe_allow_html=True)
            alerts = weather_service.get_weather_alerts(weather)
            if alerts:
                for alert in alerts[:3]:  # Show top 3 alerts
                    if "WARNING" in alert or "EXTREME" in alert:
                        st.error(alert)
                    elif "ADVISORY" in alert:
                        st.warning(alert)
                    else:
                        st.info(alert)
            else:
                st.success("✅ No weather warnings - Conditions are normal")
        else:
            st.info("👆 Please set your location in Weather Monitoring to view current conditions")
            if st.button("🔄 Go to Weather Monitoring", use_container_width=True):
                st.session_state.page = "☁️ Weather Monitoring"
                st.rerun()
    
    with col2:
        st.markdown("### ⚡ Quick Actions")
        
        if st.button("🔮 Check Disaster Risk", use_container_width=True, type="primary"):
            st.session_state.page = "🔮 Disaster Predictions"
            st.rerun()
        
        if st.button("🗺️ Find Safe Zones", use_container_width=True):
            st.session_state.page = "🗺️ Safe Zones"
            st.rerun()
        
        if st.button("🚨 Send Alert", use_container_width=True):
            st.session_state.page = "🚨 Alert System"
            st.rerun()
        
        if st.button("💬 Ask AI Assistant", use_container_width=True):
            st.session_state.page = "💬 AI Assistant"
            st.rerun()
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Last update time
        if st.session_state.get('last_update'):
            last_update = st.session_state.last_update.strftime("%I:%M %p")
            st.caption(f"🕐 Last updated: {last_update}")
    
    st.markdown("---")
    
    # ============================================
    # SECTION 3: DISASTER RISK SUMMARY
    # ============================================
    st.markdown("### 🎯 Disaster Risk Assessment")
    
    if st.session_state.get('weather_data'):
        weather = st.session_state.weather_data
        
        # Get predictions for all disaster types
        predictions = {}
        disaster_types = ['flood', 'drought', 'heatwave']
        
        for dtype in disaster_types:
            score, level, details = disaster_predictor.predict_disaster_risk(weather, dtype)
            predictions[dtype] = {
                'score': score,
                'level': level,
                'details': details
            }
        
        # Display risk cards
        risk_cols = st.columns(3)
        
        with risk_cols[0]:
            flood = predictions['flood']
            risk_class = "risk-high" if flood['score'] > 0.7 else "risk-medium" if flood['score'] > 0.4 else "risk-low"
            
            st.markdown(f"""
            <div class="{risk_class}" style="padding: 1.5rem; border-radius: 12px; text-align: center;">
                <h3 style="margin: 0;">🌊 Flood Risk</h3>
                <h2 style="margin: 0.5rem 0; font-size: 2.5rem;">{flood['score']:.1%}</h2>
                <p style="margin: 0; font-size: 1.1rem;">{flood['level']}</p>
            </div>
            """, unsafe_allow_html=True)
            st.caption(f"Confidence: {flood['details'].get('confidence', 'N/A')}")
        
        with risk_cols[1]:
            drought = predictions['drought']
            risk_class = "risk-high" if drought['score'] > 0.7 else "risk-medium" if drought['score'] > 0.4 else "risk-low"
            
            st.markdown(f"""
            <div class="{risk_class}" style="padding: 1.5rem; border-radius: 12px; text-align: center;">
                <h3 style="margin: 0;">🏜️ Drought Risk</h3>
                <h2 style="margin: 0.5rem 0; font-size: 2.5rem;">{drought['score']:.1%}</h2>
                <p style="margin: 0; font-size: 1.1rem;">{drought['level']}</p>
            </div>
            """, unsafe_allow_html=True)
            st.caption(f"Confidence: {drought['details'].get('confidence', 'N/A')}")
        
        with risk_cols[2]:
            heatwave = predictions['heatwave']
            risk_class = "risk-high" if heatwave['score'] > 0.7 else "risk-medium" if heatwave['score'] > 0.4 else "risk-low"
            
            st.markdown(f"""
            <div class="{risk_class}" style="padding: 1.5rem; border-radius: 12px; text-align: center;">
                <h3 style="margin: 0;">🔥 Heatwave Risk</h3>
                <h2 style="margin: 0.5rem 0; font-size: 2.5rem;">{heatwave['score']:.1%}</h2>
                <p style="margin: 0; font-size: 1.1rem;">{heatwave['level']}</p>
            </div>
            """, unsafe_allow_html=True)
            st.caption(f"Confidence: {heatwave['details'].get('confidence', 'N/A')}")
        
        # Overall risk status
        st.markdown("<br>", unsafe_allow_html=True)
        max_risk = max(predictions.items(), key=lambda x: x[1]['score'])
        
        if max_risk[1]['score'] > 0.7:
            st.error(f"⚠️ **HIGH RISK DETECTED**: {max_risk[0].title()} risk is at {max_risk[1]['score']:.1%}. Immediate action recommended.")
            st.markdown("**Recommended Actions:**")
            st.markdown("- Monitor weather updates frequently")
            st.markdown("- Review emergency plans")
            st.markdown("- Alert registered users")
            st.markdown("- Identify evacuation routes")
        elif max_risk[1]['score'] > 0.4:
            st.warning(f"⚡ **MODERATE RISK**: {max_risk[0].title()} conditions detected. Stay vigilant.")
        else:
            st.success("✅ **ALL CLEAR**: Risk levels are currently normal. Continue routine monitoring.")
    
    else:
        st.info("Set your location in Weather Monitoring to see disaster risk assessment")
    
    st.markdown("---")
    
    # ============================================
    # SECTION 4: RECENT ALERTS ACTIVITY
    # ============================================
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📢 Recent Alert Activity")
        
        try:
            alerts = alert_manager.get_alert_history()
            if alerts:
                # Show last 5 alerts
                recent = sorted(alerts, key=lambda x: x['timestamp'], reverse=True)[:5]
                
                for alert in recent:
                    timestamp = datetime.fromisoformat(alert['timestamp'])
                    time_ago = datetime.now() - timestamp
                    
                    if time_ago.days > 0:
                        time_str = f"{time_ago.days}d ago"
                    elif time_ago.seconds // 3600 > 0:
                        time_str = f"{time_ago.seconds // 3600}h ago"
                    else:
                        time_str = f"{time_ago.seconds // 60}m ago"
                    
                    disaster_type = alert.get('disaster_type', 'Unknown')
                    severity = alert.get('severity', 'Unknown')
                    recipients = alert.get('recipients_count', 0)
                    
                    st.markdown(f"""
                    <div style="padding: 0.8rem; background: rgba(26, 31, 58, 0.5); border-left: 3px solid #66fcf1; border-radius: 8px; margin-bottom: 0.5rem;">
                        <strong>{disaster_type.title()}</strong> - {severity}<br>
                        <small>📤 {recipients} recipients • {time_str}</small>
                    </div>
                    """, unsafe_allow_html=True)
                
                if st.button("📜 View Full Alert History", use_container_width=True):
                    st.session_state.page = "🚨 Alert System"
                    st.rerun()
            else:
                st.info("No alerts sent yet. Send your first alert from the Alert System.")
        except Exception as e:
            st.info("No alerts sent yet. Send your first alert from the Alert System.")
    
    with col2:
        st.markdown("### 📊 Alert Statistics (Last 7 Days)")
        
        try:
            alerts = alert_manager.get_alert_history()
            recent_alerts = [a for a in alerts if (datetime.now() - datetime.fromisoformat(a['timestamp'])).days <= 7]
            
            if recent_alerts:
                # Count by disaster type
                type_counts = {}
                for alert in recent_alerts:
                    dtype = alert.get('disaster_type', 'Unknown')
                    type_counts[dtype] = type_counts.get(dtype, 0) + 1
                
                # Create pie chart
                fig = go.Figure(data=[go.Pie(
                    labels=list(type_counts.keys()),
                    values=list(type_counts.values()),
                    hole=0.4,
                    marker=dict(colors=['#66fcf1', '#ef4444', '#f59e0b'])
                )])
                
                fig.update_layout(
                    template="plotly_dark",
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#c5c6c7', size=12),
                    height=300,
                    showlegend=True,
                    margin=dict(t=20, b=20, l=20, r=20)
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Summary stats
                st.metric("Total Alerts", len(recent_alerts))
                total_recipients = sum(a.get('recipients_count', 0) for a in recent_alerts)
                st.metric("Total Recipients Reached", total_recipients)
            else:
                st.info("No alerts in the last 7 days")
        except Exception as e:
            st.info("No alerts in the last 7 days")
    
    st.markdown("---")
    
    # ============================================
    # SECTION 5: REGISTERED USERS OVERVIEW
    # ============================================
    st.markdown("### 👥 Alert System Coverage")
    
    users = user_manager.get_all_users()
    
    if users:
        user_cols = st.columns(4)
        
        with user_cols[0]:
            st.metric("Total Users", len(users))
        
        with user_cols[1]:
            sms_users = sum(1 for u in users if hasattr(u, 'phone') and u.phone)
            st.metric("SMS Enabled", sms_users)

        with user_cols[2]:
            email_users = sum(1 for u in users if hasattr(u, 'email') and u.email)
            st.metric("Email Enabled", email_users)

        with user_cols[3]:
        # Count users by location if available
            locations = set(getattr(u, 'location', 'Unknown') for u in users)
            st.metric("Locations", len(locations))

        
        if st.button("➕ Register New User", use_container_width=True):
            st.session_state.page = "🚨 Alert System"
            st.rerun()
    else:
        st.info("No users registered yet. Start by registering users in the Alert System.")
        if st.button("➕ Register First User", use_container_width=True, type="primary"):
            st.session_state.page = "🚨 Alert System"
            st.rerun()
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # ============================================
    # FOOTER
    # ============================================
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #66fcf1; opacity: 0.8;">
        <p>ResQAlert AI Disaster Intelligence System</p>
        <small>Powered by Ensemble Machine Learning • Real-time Weather Integration • SMS Alert System</small>
    </div>
    """, unsafe_allow_html=True)
