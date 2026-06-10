import streamlit as st
import time

# Add these imports at the top
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

from config.settings import settings  # Add this too
from chatbot.chatbot_core import get_chatbot_response


def render_sos_panel():
    """
    Render SOS help signal panel.
    Allows users to send emergency SMS to configured contacts.
    """
    from app.user_management import user_manager
    from app.alert_manager import alert_manager
    from config.settings import settings
    from twilio.rest import Client
    
    st.markdown("### 📱 Send Help Signal (SOS)")
    st.warning("🚨 Use this only in genuine emergency situations.")
    
    # Get current location
    current_location = st.session_state.get('current_location', {})
    lat = current_location.get('lat', st.session_state.get('sz_center_lat', 'Unknown'))
    lon = current_location.get('lon', st.session_state.get('sz_center_lon', 'Unknown'))
    location_name = current_location.get('name', 'Your Location')
    
    # Get highest risk
    weather_data = st.session_state.get('weather_data', {})
    
    # Try to get predictions
    highest_risk = "Unknown"
    try:
        from models.disaster_prediction import disaster_predictor
        if weather_data:
            f_score, f_level, _ = disaster_predictor.predict_disaster_risk(weather_data, 'flood')
            d_score, d_level, _ = disaster_predictor.predict_disaster_risk(weather_data, 'drought')
            h_score, h_level, _ = disaster_predictor.predict_disaster_risk(weather_data, 'heatwave')
            
            risks = {'Flood': f_score, 'Drought': d_score, 'Heatwave': h_score}
            highest_risk = max(risks.items(), key=lambda x: x[1])[0]
    except:
        pass
    
    # Form
    sos_form = st.form("sos_form")
    
    with sos_form:
        st.markdown("**Your Location:**")
        st.markdown(f"📍 {location_name} (Lat: {lat}, Lon: {lon})")
        
        st.markdown("**Current Highest Risk:**")
        st.markdown(f"⚠️ {highest_risk}")
        
        st.markdown("**Your Situation (max 100 chars):**")
        situation = st.text_area(
            "Describe your situation",
            placeholder="e.g., Trapped on second floor, water rising",
            max_chars=100,
            label_visibility="collapsed"
        )
        
        st.markdown("**Emergency Contacts:**")
        all_users = user_manager.get_all_users()
        responder_options = []
        responder_phones = {}
        
        for user in all_users:
            try:
                name = getattr(user, 'name', 'Unknown')
                phone = getattr(user, 'phone', None)
                is_responder = getattr(user, 'is_responder', False)
                
                if phone:
                    label = f"{name} {'(Responder)' if is_responder else ''}"
                    responder_options.append(label)
                    responder_phones[label] = phone
            except:
                pass
        
        if not responder_options:
            st.warning("No emergency contacts registered. Register users in Alert System first.")
            responder_options = ["No contacts available"]
        
        selected_contacts = st.multiselect(
            "Select who to notify:",
            responder_options,
            label_visibility="collapsed"
        )
        
        submitted = st.form_submit_button("🚨 Send SOS", use_container_width=True, type="primary")
    
    if submitted:
        if not selected_contacts or selected_contacts == ["No contacts available"]:
            st.error("Please select at least one contact.")
            return
        
        # Build SOS message
        sos_message = f"""🚨 SOS ALERT 🚨
Location: {location_name}
Coordinates: {lat}, {lon}
Risk Level: {highest_risk}
Situation: {situation}
Time: {st.session_state.get('last_update', 'Now')}

PLEASE RESPOND IMMEDIATELY"""
        
        # Send SMS directly using Twilio
        sent_count = 0
        
        if not settings.TWILIO_ACCOUNT_SID or not settings.TWILIO_AUTH_TOKEN or not settings.TWILIO_PHONE_NUMBER:
            st.error("❌ SMS service not configured. Please check settings.")
            return
        
        try:
            client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            
            for contact_label in selected_contacts:
                if contact_label in responder_phones:
                    phone = responder_phones[contact_label]
                    try:
                        message = client.messages.create(
                            body=sos_message,
                            from_=settings.TWILIO_PHONE_NUMBER,
                            to=phone
                        )
                        sent_count += 1
                    except Exception as e:
                        st.warning(f"Could not send to {contact_label}: {str(e)}")
        except Exception as e:
            st.error(f"SMS Service Error: {str(e)}")
            return
        
        if sent_count > 0:
            st.success(f"✅ SOS sent to {sent_count} contact(s)!")
            
            # Log to alert history
            try:
                alert_manager.add_alert(
                    disaster_type="SOS",
                    severity="CRITICAL",
                    message=sos_message,
                    recipients_count=sent_count,
                    location=location_name
                )
            except:
                pass
        else:
            st.error("Failed to send SOS to any contact.")


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
    
    # ============================================
    # NEW: Safety Guide and SOS buttons
    # ============================================
    st.markdown("---")
    safety_col1, safety_col2, safety_col3 = st.columns([1, 1, 1])

    with safety_col1:
        if st.button("🛡️ Show Safety Guide", use_container_width=True):
            st.session_state.show_safety_guide = True

    with safety_col2:
        if st.button("📱 SOS Help Signal", use_container_width=True):
            st.session_state.show_sos_panel = True

    with safety_col3:
        pass

    st.markdown("---")

    # Show safety guide if requested
    if st.session_state.get('show_safety_guide', False):
        from services.safety_guides import get_safety_guide
        
        disaster_type = st.selectbox(
            "Choose disaster type for safety guide:",
            ['flood', 'heatwave', 'drought'],
            key='guide_selector'
        )
        guide = get_safety_guide(disaster_type)
        
        tab1, tab2 = st.tabs(["🚨 During", "✅ After"])
        
        with tab1:
            for step in guide['during']:
                st.markdown(f"- {step}")
        
        with tab2:
            for step in guide['after']:
                st.markdown(f"- {step}")
        
        if st.button("Close Guide", key='close_guide', use_container_width=True):
            st.session_state.show_safety_guide = False
        
        st.markdown("---")

    # Show SOS panel if requested
    if st.session_state.get('show_sos_panel', False):
        render_sos_panel()
        if st.button("Close SOS Panel", key='close_sos', use_container_width=True):
            st.session_state.show_sos_panel = False
        
        st.markdown("---")
    
    # ============================================
    # ORIGINAL CHATBOT (UNCHANGED)
    # ============================================
    
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
