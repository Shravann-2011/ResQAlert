import streamlit as st

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
