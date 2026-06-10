import streamlit as st

def apply_custom_css():
    # NEXT-GEN FUTURISTIC DARK MODE CSS - ENHANCED VERSION
    st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;600;700;900&family=Inter:wght@300;400;600;700&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
    
    <style>
        :root {
            --bg-primary: #0a0e27;
            --bg-secondary: #0f1419;
            --bg-card: #1a1f35;
            --accent-cyan: #00f5ff;
            --accent-purple: #b24bf3;
            --accent-orange: #ff6b35;
            --accent-green: #00ff88;
            --text-primary: #e8f1ff;
            --text-secondary: #8b9dc3;
            --glow-cyan: rgba(0, 245, 255, 0.4);
            --glow-purple: rgba(178, 75, 243, 0.4);
            --radius: 16px;
        }

        /* Animated holographic background */
        body {
            background: var(--bg-primary);
            overflow-x: hidden;
        }

        body::before {
            content: "";
            position: fixed;
            inset: 0;
            z-index: -1;
            background:
                radial-gradient(circle at 20% 30%, rgba(0, 245, 255, 0.08), transparent 50%),
                radial-gradient(circle at 80% 70%, rgba(178, 75, 243, 0.08), transparent 50%),
                radial-gradient(circle at 50% 50%, rgba(255, 107, 53, 0.05), transparent 60%);
            animation: holoDrift 20s ease-in-out infinite;
        }

        @keyframes holoDrift {
            0%, 100% { transform: translate(0, 0) scale(1); }
            33% { transform: translate(-20px, 30px) scale(1.05); }
            66% { transform: translate(20px, -30px) scale(0.98); }
        }

        /* Global font and text styling */
        .stApp {
            background: linear-gradient(135deg, #0a0e27 0%, #1a1f3a 50%, #0f1419 100%);
            background-attachment: fixed;
            font-family: 'Inter', sans-serif;
            color: var(--text-primary);
        }
        
        /* Hide sidebar completely */
        [data-testid="stSidebar"] {
            display: none !important;
        }
        
        /* Main container - glassmorphism */
        .main .block-container {
            background: linear-gradient(135deg, rgba(26, 31, 53, 0.85), rgba(15, 20, 25, 0.9));
            backdrop-filter: blur(20px) saturate(150%);
            border-radius: var(--radius);
            border: 1px solid rgba(0, 245, 255, 0.15);
            box-shadow: 
                0 8px 32px rgba(0, 0, 0, 0.4),
                inset 0 1px 0 rgba(255, 255, 255, 0.05),
                0 0 80px rgba(0, 245, 255, 0.05);
            padding: 2rem;
            animation: containerFadeIn 0.8s ease-out;
        }

        @keyframes containerFadeIn {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        /* TOP NAVIGATION BAR */
        .top-nav {
            position: sticky;
            top: 0;
            z-index: 9999;
            margin: -2rem -2rem 2rem -2rem;
            padding: 1.2rem 2rem;
            background: linear-gradient(135deg, rgba(10, 14, 39, 0.95), rgba(15, 20, 25, 0.98));
            backdrop-filter: blur(15px);
            border-bottom: 1px solid rgba(0, 245, 255, 0.2);
            box-shadow: 
                0 4px 24px rgba(0, 0, 0, 0.5),
                0 0 60px rgba(0, 245, 255, 0.1);
            animation: navSlideDown 0.6s ease-out;
        }

        @keyframes navSlideDown {
            from {
                transform: translateY(-100%);
                opacity: 0;
            }
            to {
                transform: translateY(0);
                opacity: 1;
            }
        }

        /* Logo and title area */
        .nav-header {
            display: flex;
            align-items: center;
            gap: 16px;
            margin-bottom: 16px;
        }

        .nav-logo {
            width: 56px;
            height: 56px;
            border-radius: 14px;
            background: linear-gradient(135deg, var(--accent-cyan), var(--accent-purple));
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 28px;
            box-shadow: 0 8px 24px var(--glow-cyan);
            animation: logoFloat 3s ease-in-out infinite;
        }

        @keyframes logoFloat {
            0%, 100% { transform: translateY(0) rotate(0deg); }
            50% { transform: translateY(-8px) rotate(5deg); }
        }
        
        .nav-title-main {
            font-size: 1.8rem;
            font-weight: 900;
            font-family: 'Orbitron', sans-serif;
            letter-spacing: 0.15em;
            background: linear-gradient(90deg, var(--accent-cyan), var(--accent-purple), var(--accent-orange));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            animation: titleGlow 3s ease-in-out infinite;
            text-shadow: 0 0 30px var(--glow-cyan);
        }

        @keyframes titleGlow {
            0%, 100% { filter: brightness(1); }
            50% { filter: brightness(1.3); }
        }

        .nav-subtitle {
            font-size: 0.75rem;
            color: var(--text-secondary);
            font-family: "JetBrains Mono", monospace;
            letter-spacing: 0.1em;
            margin-top: 4px;
        }

        /* Status indicator */
        .status-online {
            display: inline-block;
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: var(--accent-green);
            box-shadow: 0 0 12px var(--accent-green);
            animation: statusPulse 2s ease-in-out infinite;
            margin-right: 8px;
        }

        @keyframes statusPulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        
        /* Navigation buttons */
        div[data-testid="column"] .stButton > button {
            background: linear-gradient(135deg, rgba(0, 245, 255, 0.08), rgba(178, 75, 243, 0.08));
            color: var(--text-primary) !important;
            border: 1px solid rgba(0, 245, 255, 0.2);
            border-radius: 8px;
            padding: 0.7rem 0.5rem;
            font-weight: 600;
            font-size: 0.85rem;
            letter-spacing: 0.5px;
            font-family: 'Inter', sans-serif;
            transition: all 0.3s ease;
            width: 100%;
            height: 45px;
            position: relative;
            overflow: hidden;
            white-space: nowrap;
            display: flex;
            align-items: center;
            justify-content: center;
            line-height: 1.2;
        }

        div[data-testid="column"] .stButton > button::before {
            content: "";
            position: absolute;
            top: 50%;
            left: 50%;
            width: 0;
            height: 0;
            border-radius: 50%;
            background: rgba(0, 245, 255, 0.3);
            transform: translate(-50%, -50%);
            transition: width 0.6s, height 0.6s;
        }

        div[data-testid="column"] .stButton > button:hover::before {
            width: 300px;
            height: 300px;
        }
        
        div[data-testid="column"] .stButton > button:hover {
            background: rgba(0, 245, 255, 0.2);
            border-color: var(--accent-cyan);
            box-shadow: 0 4px 20px var(--glow-cyan);
            transform: translateY(-2px);
        }
        
        /* TEXT - HIGH CONTRAST */
        h1, h2, h3, h4 {
            color: var(--accent-cyan) !important;
            font-family: 'Orbitron', sans-serif;
            font-weight: 700;
            letter-spacing: 0.05em;
        }
        
        p, span, div, label, li {
            color: var(--text-primary) !important;
            font-size: 1.05rem;
        }
        
        /* Metric cards with enhanced styling */
        .metric-card {
            background: linear-gradient(135deg, rgba(26, 31, 53, 0.6), rgba(15, 20, 25, 0.8));
            border: 1px solid rgba(0, 245, 255, 0.15);
            border-radius: 12px;
            padding: 1.2rem;
            position: relative;
            overflow: hidden;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            cursor: pointer;
        }

        .metric-card::before {
            content: "";
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 2px;
            background: linear-gradient(90deg, transparent, var(--accent-cyan), transparent);
            opacity: 0;
            transition: opacity 0.3s;
        }

        .metric-card:hover {
            transform: translateY(-4px);
            border-color: var(--accent-cyan);
            box-shadow: 0 8px 32px var(--glow-cyan);
        }

        .metric-card:hover::before {
            opacity: 1;
            animation: scanLine 1.5s ease-in-out infinite;
        }

        @keyframes scanLine {
            0% { transform: translateX(-100%); }
            100% { transform: translateX(100%); }
        }
        
        /* RISK CARDS - NEON GLOW */
        .risk-card {
            padding: 2.5rem;
            border-radius: 20px;
            margin: 1.5rem 0;
            text-align: center;
            border: 3px solid;
            transition: all 0.3s ease;
            animation: cardPopIn 0.5s ease-out;
        }

        @keyframes cardPopIn {
            from {
                opacity: 0;
                transform: scale(0.9) translateY(20px);
            }
            to {
                opacity: 1;
                transform: scale(1) translateY(0);
            }
        }
        
        .risk-card:hover {
            transform: translateY(-8px) scale(1.02);
        }
        
        .risk-card h2 {
            font-size: 3rem;
            margin: 0.5rem 0;
            font-weight: 900;
        }
        
        .risk-card h3 {
            font-size: 1.4rem;
            margin-bottom: 0.5rem;
        }
        
        .risk-card p {
            font-size: 1.2rem;
        }
        
        /* LOW RISK - Green */
        .risk-low {
            background: linear-gradient(135deg, rgba(0, 255, 136, 0.1), rgba(0, 255, 136, 0.05));
            border-color: var(--accent-green);
            box-shadow: 0 8px 24px rgba(0, 255, 136, 0.1);
        }
        
        .risk-low h2, .risk-low h3 {
            color: var(--accent-green) !important;
            text-shadow: 0 0 20px rgba(0, 255, 136, 0.8);
        }
        
        .risk-low p {
            color: #6ee7b7 !important;
        }
        
        /* MEDIUM RISK - Yellow */
        .risk-medium {
            background: linear-gradient(135deg, rgba(255, 193, 7, 0.1), rgba(255, 193, 7, 0.05));
            border-color: #ffc107;
            box-shadow: 0 8px 24px rgba(255, 193, 7, 0.1);
        }
        
        .risk-medium h2, .risk-medium h3 {
            color: #ffc107 !important;
            text-shadow: 0 0 20px rgba(255, 193, 7, 0.8);
        }
        
        .risk-medium p {
            color: #fbbf24 !important;
        }
        
        /* HIGH RISK - Red with pulse */
        .risk-high {
            background: linear-gradient(135deg, rgba(239, 68, 68, 0.15), rgba(239, 68, 68, 0.08));
            border-color: #ef4444;
            box-shadow: 0 8px 24px rgba(239, 68, 68, 0.15);
            animation: pulseAlert 2s ease-in-out infinite;
        }
        
        @keyframes pulseAlert {
            0%, 100% { box-shadow: 0 8px 24px rgba(239, 68, 68, 0.15); }
            50% { box-shadow: 0 8px 32px rgba(239, 68, 68, 0.3); }
        }
        
        .risk-high h2, .risk-high h3 {
            color: #ef4444 !important;
            text-shadow: 0 0 20px rgba(239, 68, 68, 1);
        }
        
        .risk-high p {
            color: #fca5a5 !important;
        }
        
        /* METRICS */
        [data-testid="stMetric"] {
            background: linear-gradient(135deg, rgba(26, 31, 53, 0.6), rgba(15, 20, 25, 0.8));
            border: 1px solid rgba(0, 245, 255, 0.15);
            border-radius: 12px;
            padding: 1.5rem;
            transition: all 0.3s ease;
        }
        
        [data-testid="stMetric"]:hover {
            border-color: var(--accent-cyan);
            box-shadow: 0 8px 32px var(--glow-cyan);
            transform: translateY(-3px);
        }
        
        [data-testid="stMetricValue"] {
            font-size: 2.5rem;
            font-weight: 900;
            color: var(--accent-cyan) !important;
            font-family: 'Orbitron', sans-serif;
            text-shadow: 0 0 15px var(--glow-cyan);
        }
        
        [data-testid="stMetricLabel"] {
            color: var(--text-secondary) !important;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        /* PRIMARY BUTTONS */
        .stButton > button[kind="primary"] {
            background: linear-gradient(135deg, var(--accent-cyan) 0%, #45a29e 100%);
            color: #0a0e27 !important;
            border: none;
            border-radius: 10px;
            padding: 0.9rem 2rem;
            font-weight: 700;
            font-size: 1.05rem;
            text-transform: uppercase;
            letter-spacing: 2px;
            box-shadow: 0 8px 25px var(--glow-cyan);
            transition: all 0.3s ease;
        }
        
        .stButton > button[kind="primary"]:hover {
            transform: translateY(-3px);
            box-shadow: 0 12px 35px var(--glow-cyan);
        }
        
        /* SECONDARY BUTTONS */
        .stButton > button[kind="secondary"] {
            background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
            color: white !important;
            border: none;
            border-radius: 10px;
            padding: 0.9rem 2rem;
            font-weight: 700;
            font-size: 1.05rem;
            text-transform: uppercase;
            letter-spacing: 2px;
            box-shadow: 0 8px 25px rgba(239, 68, 68, 0.4);
            transition: all 0.3s ease;
        }
        
        .stButton > button[kind="secondary"]:hover {
            transform: translateY(-3px);
            box-shadow: 0 12px 35px rgba(239, 68, 68, 0.6);
        }
        
        /* INPUT FIELDS */
        .stTextInput input, .stSelectbox select, .stTextArea textarea {
            background: rgba(26, 31, 53, 0.6) !important;
            color: var(--text-primary) !important;
            border: 1px solid rgba(0, 245, 255, 0.2) !important;
            border-radius: 8px;
            padding: 0.9rem;
            font-size: 1.05rem;
            transition: all 0.3s ease;
        }
        
        .stTextInput input:focus, .stSelectbox select:focus {
            border-color: var(--accent-cyan) !important;
            box-shadow: 0 0 0 1px var(--accent-cyan), 0 0 20px var(--glow-cyan);
        }
        
        /* EXPANDERS */
        .streamlit-expanderHeader {
            background: linear-gradient(135deg, rgba(26, 31, 53, 0.6), rgba(15, 20, 25, 0.8));
            border: 1px solid rgba(0, 245, 255, 0.15);
            border-radius: 8px;
            color: var(--accent-cyan) !important;
            font-weight: 600;
            padding: 0.8rem;
            transition: all 0.3s ease;
        }
        
        .streamlit-expanderHeader:hover {
            background: rgba(0, 245, 255, 0.1);
            border-color: var(--accent-cyan);
            box-shadow: 0 4px 16px var(--glow-cyan);
        }
        
        /* ALERTS - HIGH CONTRAST */
        .stSuccess {
            background: rgba(0, 255, 136, 0.15);
            border-left: 4px solid var(--accent-green);
            border-radius: 10px;
            color: #6ee7b7 !important;
        }
        
        .stError {
            background: rgba(239, 68, 68, 0.15);
            border-left: 4px solid #ef4444;
            border-radius: 10px;
            color: #fca5a5 !important;
        }
        
        .stWarning {
            background: rgba(255, 193, 7, 0.15);
            border-left: 4px solid #ffc107;
            border-radius: 10px;
            color: #fbbf24 !important;
        }
        
        .stInfo {
            background: rgba(0, 245, 255, 0.15);
            border-left: 4px solid var(--accent-cyan);
            border-radius: 10px;
            color: var(--accent-cyan) !important;
        }
        
        /* CHARTS - DARK THEME */
        .js-plotly-plot {
            background: rgba(15, 20, 30, 0.6);
            border: 1px solid rgba(0, 245, 255, 0.1);
            border-radius: 12px;
            padding: 1rem;
            overflow: hidden;
        }
        
        /* DATAFRAMES */
        .stDataFrame {
            background: rgba(15, 20, 30, 0.8);
            border: 1px solid rgba(0, 245, 255, 0.15);
            border-radius: 12px;
            overflow: hidden;
        }
        
        /* TABS */
        .stTabs [data-baseweb="tab-list"] {
            gap: 1rem;
        }
        
        .stTabs [data-baseweb="tab"] {
            background: rgba(26, 31, 53, 0.5);
            border: 2px solid rgba(0, 245, 255, 0.2);
            border-radius: 10px;
            color: var(--accent-cyan);
            font-weight: 600;
            padding: 0.8rem 1.5rem;
        }
        
        .stTabs [aria-selected="true"] {
            background: rgba(0, 245, 255, 0.2);
            border-color: var(--accent-cyan);
        }
        
        /* CHAT */
        .stChatMessage {
            margin-bottom: 1.5rem !important;
            background: rgba(26, 31, 58, 0.6) !important;
            border: 1px solid rgba(0, 245, 255, 0.3) !important;
            border-radius: 12px !important;
            padding: 1rem !important;
        }

        /* Chat input area - always visible at bottom */
        .stChatFloatingInputContainer {
            background: linear-gradient(180deg, transparent 0%, rgba(15, 20, 30, 0.95) 20%) !important;
            padding-top: 2rem !important;
            padding-bottom: 1rem !important;
        }

        /* Input box styling */
        .stChatInput {
            background: rgba(26, 31, 58, 0.8) !important;
            border: 2px solid rgba(0, 245, 255, 0.3) !important;
            border-radius: 10px !important;
        }

        /* Main chat area - proper height */
        .main .block-container {
            padding-bottom: 8rem !important;
        }
        
        /* FORMS */
        .stForm {
            background: rgba(15, 20, 30, 0.5);
            border: 2px solid rgba(0, 245, 255, 0.2);
            border-radius: 12px;
            padding: 2rem;
        }
        
        /* SCROLLBAR */
        ::-webkit-scrollbar {
            width: 8px;
            height: 8px;
        }
        
        ::-webkit-scrollbar-track {
            background: var(--bg-secondary);
        }
        
        ::-webkit-scrollbar-thumb {
            background: linear-gradient(180deg, var(--accent-cyan), var(--accent-purple));
            border-radius: 4px;
        }

        ::-webkit-scrollbar-thumb:hover {
            background: linear-gradient(180deg, var(--accent-purple), var(--accent-orange));
        }

        /* Loading spinner */
        .stSpinner > div {
            border-color: var(--accent-cyan) transparent transparent transparent !important;
        }

        /* Alert animations */
        @keyframes alertBlink {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.6; }
        }

        .alert-critical {
            animation: alertBlink 1s ease-in-out infinite;
        }
        
        /* MOBILE */
        @media (max-width: 768px) {
            .top-nav {
                padding: 1rem;
            }
            
            .nav-title-main {
                font-size: 1rem;
            }
            
            .risk-card {
                padding: 1.5rem;
            }
            
            .risk-card h2 {
                font-size: 2rem;
            }

            .metric-card {
                padding: 1rem;
            }
        }
    </style>
    """, unsafe_allow_html=True)

def render_navigation():
    """Render top navigation bar with enhanced styling"""
    # Navigation container HTML
    st.markdown('<div class="top-nav">', unsafe_allow_html=True)
    
    # Header with logo and title
    st.markdown('''
    <div class="nav-header">
        <div class="nav-logo">🛡️</div>
        <div>
            <div class="nav-title-main">RESQALERT AI INTELLIGENCE</div>
            <div class="nav-subtitle"><span class="status-online"></span>REAL-TIME DISASTER MONITORING SYSTEM</div>
        </div>
    </div>
    ''', unsafe_allow_html=True)
    
    # Navigation buttons
    nav_cols = st.columns(8)
    
    if nav_cols[0].button("🏠 DASHBOARD", use_container_width=True):
        st.session_state.page = "🏠 Dashboard Overview"
    if nav_cols[1].button("☁️ WEATHER", use_container_width=True):
        st.session_state.page = "☁️ Weather Monitoring"
    if nav_cols[2].button("🔮 PREDICTIONS", use_container_width=True):
        st.session_state.page = "🔮 Disaster Predictions"
    if nav_cols[3].button("🗺️ ZONES", use_container_width=True):
        st.session_state.page = "🗺️ Safe Zones"
    if nav_cols[4].button("💬 ASSISTANT", use_container_width=True):
        st.session_state.page = "💬 AI Assistant"
    if nav_cols[5].button("🚨 ALERTS", use_container_width=True):
        st.session_state.page = "🚨 Alert System"
    if nav_cols[6].button("📊 HISTORY", use_container_width=True):
        st.session_state.page = "📊 Historical Analysis"
    if nav_cols[7].button("⚙️ SETTINGS", use_container_width=True):
        st.session_state.page = "⚙️ Settings"
    
    st.markdown('</div>', unsafe_allow_html=True)