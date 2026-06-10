import streamlit as st

from app.user_management import user_manager
from utils.validators import validate_email, validate_phone

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
