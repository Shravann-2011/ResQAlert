import streamlit as st
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

from config.settings import settings
from chatbot.rule_based import get_rule_based_response

def get_chatbot_response(text):
    """Generate AI response - FIXED VERSION"""
    
    # Check AI availability
    if st.session_state.get('ai_enabled') and 'gemini_chat' in st.session_state:
        try:
            # Enhanced disaster-focused prompt
            system_context = f"""You are ResQAlert AI, an expert disaster preparedness assistant for India.

User Question: {text}

Provide a helpful, structured response following these guidelines:

**Format:**
1. Start with relevant emoji and brief intro
2. Use clear sections with **bold headings**
3. Include numbered or bulleted lists for steps
4. Add ⚠️ for warnings, ✅ for recommendations
5. Include Indian emergency numbers when relevant

**Content Focus:**
- Specific, actionable steps (Before/During/After when relevant)
- Indian context (monsoons, geography, infrastructure)
- Safety warnings and precautions
- Practical tips anyone can follow
- Emergency contacts: 112 (All), 108 (Ambulance), 101 (Fire), 1078 (Disaster)

**Style:**
- Clear, concise (300-500 words)
- Professional but caring tone
- Use metric units (km, celsius)
- Avoid technical jargon

Provide your expert advice now:"""

            # Call Gemini API
            response = st.session_state.gemini_chat.send_message(system_context)
            
            # Return AI response
            return response.text
            
        except Exception as e:
            # Show error gracefully
            error_msg = str(e)[:200]
            fallback = get_rule_based_response(user_input)
            
            return f"""⚠️ **AI temporarily unavailable**

*Error: {error_msg}*

**Using emergency response mode:**

{fallback}"""
    
    # Rule-based fallback
    return get_rule_based_response(user_input)
