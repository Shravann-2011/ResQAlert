import streamlit as st
import re
import time
from datetime import datetime

from services.sms_service import sms_service
from app.user_management import user_manager
from app.alert_manager import alert_manager

def validate_phone(phone):
    """Validate phone number format"""
    # Remove spaces, dashes, and parentheses
    phone = re.sub(r'[\s\-\(\)]', '', phone)
    
    # Check if it starts with + and has 10-15 digits
    if phone.startswith('+') and len(phone) >= 11 and len(phone) <= 16:
        if phone[1:].isdigit():
            return {'valid': True, 'message': '✅ Valid phone number', 'formatted': phone}
    
    # If not starting with +, check if it's 10 digits (add +91 for India)
    if phone.isdigit() and len(phone) == 10:
        formatted = '+91' + phone
        return {'valid': True, 'message': '✅ Valid (will add +91)', 'formatted': formatted}
    
    return {'valid': False, 'message': '❌ Invalid format. Use +CountryCode followed by number', 'formatted': phone}

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
