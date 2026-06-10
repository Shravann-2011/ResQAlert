import streamlit as st
from models.disaster_prediction import initialize_models

def load_models():
    """Load ML models"""
    if not st.session_state.models_initialized:
        with st.spinner("🤖 Loading AI models..."):
            initialize_models()
            st.session_state.models_initialized = True