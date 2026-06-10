import streamlit as st
from datetime import datetime
import time

from services.sms_service import sms_service
from app.user_management import user_manager
from app.alert_manager import alert_manager

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
