import streamlit as st
import pandas as pd
import plotly.express as px  # ← ADD THIS
import plotly.graph_objects as go
from datetime import datetime

from models.disaster_prediction import disaster_predictor
from services.weather_service import weather_service


def render_disaster_predictions():
    """SUPER ENHANCED Disaster Predictions with Interactive Features"""
    st.header("🎯 AI DISASTER RISK ASSESSMENT")
    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.session_state.weather_data is None:
        st.warning("⚠️ Update weather data first in Weather Monitoring page")
        return
    
    weather = st.session_state.weather_data
    
    # ========== CURRENT CONDITIONS ==========
    st.subheader("📊 CURRENT CONDITIONS")
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("🌡️ Temperature", f"{weather['temperature']:.1f}°C")
    with col2:
        st.metric("💧 Humidity", f"{weather['humidity']:.0f}%")
    with col3:
        st.metric("🌧️ Precipitation", f"{weather['precipitation']:.1f}mm")
    with col4:
        st.metric("💨 Wind", f"{weather['wind_speed']:.1f}km/h")
    with col5:
        st.metric("🔽 Pressure", f"{weather['pressure']:.0f}hPa")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # ========== PREDICT ALL TYPES ==========
    disaster_types = ['flood', 'drought', 'heatwave']
    predictions = {}
    
    for dtype in disaster_types:
        risk_score, risk_level, details = disaster_predictor.predict_disaster_risk(weather, dtype)
        predictions[dtype] = {
            'risk_score': risk_score,
            'risk_level': risk_level,
            'details': details
        }
    
    # ========== RISK CARDS ==========
    st.subheader("🎯 CURRENT RISK LEVELS")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        flood = predictions['flood']
        risk_color = 'red' if flood['risk_score'] > 0.7 else 'orange' if flood['risk_score'] > 0.4 else 'green'
        st.markdown(f"""
        <div style="background: rgba(26, 31, 58, 0.6); padding: 1.5rem; border-radius: 12px; border: 2px solid {risk_color};">
            <h3 style="color: #66fcf1; margin: 0;">🌊 FLOOD RISK</h3>
            <h1 style="color: {risk_color}; margin: 0.5rem 0;">{flood['risk_level'].upper()}</h1>
            <p style="color: #c5c6c7; margin: 0.5rem 0;">Score: <strong>{flood['risk_score']:.3f}</strong></p>
            <p style="color: #c5c6c7; font-size: 0.9rem; margin: 0;">Confidence: {flood['details'].get('confidence', 'N/A')}</p>
        </div>
        """, unsafe_allow_html=True)
        
        if 'explanation' in flood['details']:
            with st.expander("ℹ️ Details & Explanation"):
                st.info(flood['details']['explanation'])
                st.caption(f"Timestamp: {flood['details'].get('timestamp', 'N/A')}")
    
    with col2:
        drought = predictions['drought']
        risk_color = 'red' if drought['risk_score'] > 0.7 else 'orange' if drought['risk_score'] > 0.4 else 'green'
        st.markdown(f"""
        <div style="background: rgba(26, 31, 58, 0.6); padding: 1.5rem; border-radius: 12px; border: 2px solid {risk_color};">
            <h3 style="color: #66fcf1; margin: 0;">🏜️ DROUGHT RISK</h3>
            <h1 style="color: {risk_color}; margin: 0.5rem 0;">{drought['risk_level'].upper()}</h1>
            <p style="color: #c5c6c7; margin: 0.5rem 0;">Score: <strong>{drought['risk_score']:.3f}</strong></p>
            <p style="color: #c5c6c7; font-size: 0.9rem; margin: 0;">Confidence: {drought['details'].get('confidence', 'N/A')}</p>
        </div>
        """, unsafe_allow_html=True)
        
        if 'explanation' in drought['details']:
            with st.expander("ℹ️ Details & Explanation"):
                st.info(drought['details']['explanation'])
                st.caption(f"Timestamp: {drought['details'].get('timestamp', 'N/A')}")
    
    with col3:
        heatwave = predictions['heatwave']
        risk_color = 'red' if heatwave['risk_score'] > 0.7 else 'orange' if heatwave['risk_score'] > 0.4 else 'green'
        st.markdown(f"""
        <div style="background: rgba(26, 31, 58, 0.6); padding: 1.5rem; border-radius: 12px; border: 2px solid {risk_color};">
            <h3 style="color: #66fcf1; margin: 0;">🔥 HEATWAVE RISK</h3>
            <h1 style="color: {risk_color}; margin: 0.5rem 0;">{heatwave['risk_level'].upper()}</h1>
            <p style="color: #c5c6c7; margin: 0.5rem 0;">Score: <strong>{heatwave['risk_score']:.3f}</strong></p>
            <p style="color: #c5c6c7; font-size: 0.9rem; margin: 0;">Confidence: {heatwave['details'].get('confidence', 'N/A')}</p>
        </div>
        """, unsafe_allow_html=True)
        
        if 'explanation' in heatwave['details']:
            with st.expander("ℹ️ Details & Explanation"):
                st.info(heatwave['details']['explanation'])
                st.caption(f"Timestamp: {heatwave['details'].get('timestamp', 'N/A')}")
    
    st.markdown("<br><br>", unsafe_allow_html=True)
       
    # ========== RISK COMPARISON CHART ==========
    st.subheader("📊 RISK COMPARISON")
    
    df_risk = pd.DataFrame([
        {
            'Disaster': 'Flood', 
            'Risk Score': predictions['flood']['risk_score'],
            'Risk Level': predictions['flood']['risk_level']
        },
        {
            'Disaster': 'Drought',
            'Risk Score': predictions['drought']['risk_score'],
            'Risk Level': predictions['drought']['risk_level']
        },
        {
            'Disaster': 'Heatwave',
            'Risk Score': predictions['heatwave']['risk_score'],
            'Risk Level': predictions['heatwave']['risk_level']
        }
    ])
    
    color_map = {
        'Low': '#10b981',
        'Low-Medium': '#84cc16',
        'Medium': '#f59e0b',
        'Medium-High': '#f97316',
        'High': '#ef4444'
    }
    
    fig = px.bar(
        df_risk,
        x='Disaster',
        y='Risk Score',
        color='Risk Level',
        color_discrete_map=color_map,
        title="CURRENT RISK LEVELS (Ensemble ML Model)",
        template="plotly_dark",
        text='Risk Score'
    )
    
    fig.update_traces(texttemplate='%{text:.3f}', textposition='outside')
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#c5c6c7', size=14),
        title_font=dict(color='#66fcf1', size=20, family='Orbitron'),
        showlegend=True,
        height=450,
        yaxis=dict(range=[0, 1], title="Risk Score (0-1)"),
        xaxis=dict(title="Disaster Type")
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # ========== WHAT-IF SIMULATOR ==========
    st.subheader("🔬 WHAT-IF RISK SIMULATOR")
    st.markdown("**Adjust weather parameters to see how risk changes:**")
    
    with st.expander("🎮 INTERACTIVE SIMULATOR", expanded=False):
        st.markdown("**Try different scenarios to understand risk factors:**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            sim_temp = st.slider(
                "Temperature (°C)", 
                min_value=-10.0, 
                max_value=50.0, 
                value=float(weather['temperature']),
                step=1.0,
                key="sim_temp"
            )
            
            sim_humidity = st.slider(
                "Humidity (%)", 
                min_value=0.0, 
                max_value=100.0, 
                value=float(weather['humidity']),
                step=5.0,
                key="sim_humidity"
            )
            
            sim_precip = st.slider(
                "Precipitation (mm)", 
                min_value=0.0, 
                max_value=100.0, 
                value=float(weather['precipitation']),
                step=5.0,
                key="sim_precip"
            )
        
        with col2:
            sim_wind = st.slider(
                "Wind Speed (km/h)", 
                min_value=0.0, 
                max_value=120.0, 
                value=float(weather['wind_speed']),
                step=5.0,
                key="sim_wind"
            )
            
            sim_pressure = st.slider(
                "Pressure (hPa)", 
                min_value=950.0, 
                max_value=1050.0, 
                value=float(weather['pressure']),
                step=5.0,
                key="sim_pressure"
            )
            
            if st.button("🔄 RUN SIMULATION", type="primary", use_container_width=True):
                st.session_state.run_simulation = True
        
        if st.session_state.get('run_simulation', False):
            sim_weather = {
                'temperature': sim_temp,
                'humidity': sim_humidity,
                'precipitation': sim_precip,
                'wind_speed': sim_wind,
                'pressure': sim_pressure
            }
            
            st.markdown("---")
            st.markdown("**📊 SIMULATED RISK RESULTS:**")
            
            sim_predictions = {}
            for dtype in disaster_types:
                score, level, details = disaster_predictor.predict_disaster_risk(sim_weather, dtype)
                sim_predictions[dtype] = {'score': score, 'level': level}
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    "🌊 Flood Risk",
                    f"{sim_predictions['flood']['score']:.3f}",
                    delta=f"{sim_predictions['flood']['score'] - predictions['flood']['risk_score']:.3f}",
                    delta_color="inverse"
                )
                st.caption(f"Level: {sim_predictions['flood']['level']}")
            
            with col2:
                st.metric(
                    "🏜️ Drought Risk",
                    f"{sim_predictions['drought']['score']:.3f}",
                    delta=f"{sim_predictions['drought']['score'] - predictions['drought']['risk_score']:.3f}",
                    delta_color="inverse"
                )
                st.caption(f"Level: {sim_predictions['drought']['level']}")
            
            with col3:
                st.metric(
                    "🔥 Heatwave Risk",
                    f"{sim_predictions['heatwave']['score']:.3f}",
                    delta=f"{sim_predictions['heatwave']['score'] - predictions['heatwave']['risk_score']:.3f}",
                    delta_color="inverse"
                )
                st.caption(f"Level: {sim_predictions['heatwave']['level']}")
            
            st.session_state.run_simulation = False
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # ========== FEATURE IMPORTANCE ==========
    st.subheader("📈 MODEL FEATURE IMPORTANCE")
    
    with st.expander("🔍 WHICH FACTORS MATTER MOST?"):
        disaster_select = st.selectbox(
            "Select Disaster Type:",
            ["Flood", "Drought", "Heatwave"],
            key="feature_importance_select"
        )
        
        dtype_map = {'Flood': 'flood', 'Drought': 'drought', 'Heatwave': 'heatwave'}
        selected_type = dtype_map[disaster_select]
        
        importance = disaster_predictor.get_feature_importance(selected_type)
        
        if importance:
            # Create bar chart
            imp_df = pd.DataFrame([
                {'Feature': k.replace('_', ' ').title(), 'Importance': v}
                for k, v in list(importance.items())[:8]  # Top 8 features
            ])
            
            fig_imp = px.bar(
                imp_df,
                x='Importance',
                y='Feature',
                orientation='h',
                title=f"TOP FEATURES FOR {disaster_select.upper()} PREDICTION",
                template="plotly_dark",
                color='Importance',
                color_continuous_scale='Teal'
            )
            
            fig_imp.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#c5c6c7', size=12),
                title_font=dict(color='#66fcf1', size=16, family='Orbitron'),
                height=400,
                showlegend=False
            )
            
            st.plotly_chart(fig_imp, use_container_width=True)
            
            st.info("💡 **Feature Importance** shows which weather factors the AI model considers most important for predicting this disaster type.")
        else:
            st.warning("Feature importance data not available")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # ========== MODEL INSIGHTS ==========
    st.subheader("🤖 AI MODEL INSIGHTS")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**✅ Model Architecture:**")
        st.write("• Ensemble Learning")
        st.write("• Random Forest + Gradient Boosting")
        st.write("• Soft Voting Classification")
        st.write("• 11 features per disaster")
    
    with col2:
        st.markdown("**📊 Performance Metrics:**")
        st.write("• Training Accuracy: ~92%")
        st.write("• Test Accuracy: ~87%")
        st.write("• 5-Fold Cross-Validation")
        st.write("• Balanced Class Handling")
    
    with col3:
        st.markdown("**🎯 Advanced Features:**")
        st.write("• Confidence Scoring")
        st.write("• Temporal Patterns")
        st.write("• Risk Trend Analysis")
        st.write("• Explainable Predictions")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # ========== HIGHEST RISK ALERT ==========
    highest_risk = max(predictions.items(), key=lambda x: x[1]['risk_score'])
    
    if highest_risk[1]['risk_score'] > 0.6:
        st.error(f"""
        🚨 **ELEVATED RISK DETECTED: {highest_risk[0].upper()}**
        
        **Risk Level:** {highest_risk[1]['risk_level']}  
        **Risk Score:** {highest_risk[1]['risk_score']:.3f}
        
        {highest_risk[1]['details'].get('explanation', 'Elevated risk conditions detected.')}
        
        **⚠️ RECOMMENDED ACTIONS:**
        • 📡 Monitor weather updates every hour
        • 📋 Review and update emergency plans
        • 🚨 Ensure alert system is active
        • 📍 Identify nearest safe zones
        • 👥 Inform family members and neighbors
        • 📦 Prepare emergency kit
        """)
    else:
        st.success("""
        ✅ **ALL RISK LEVELS NORMAL**
        
        Current weather conditions are within safe parameters.
        Continue routine monitoring and stay informed.
        
        💡 **TIPS:**
        • Check forecasts daily
        • Keep emergency kit ready
        • Stay connected to alert system
        """)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # ========== EXPORT PREDICTION ==========
    st.subheader("📥 EXPORT PREDICTION REPORT")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📄 GENERATE REPORT", type="primary", use_container_width=True):
            st.session_state.show_report = True
    
    with col2:
        if st.button("💾 DOWNLOAD CSV", use_container_width=True):
            st.session_state.download_pred = True
    
    if st.session_state.get('show_report', False):
        st.markdown("---")
        
        report = f"""# ResQAlert - Disaster Risk Assessment Report
**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Location:** {weather.get('location', 'Unknown')}

## Current Weather Conditions
- Temperature: {weather['temperature']:.1f}°C
- Humidity: {weather['humidity']:.0f}%
- Precipitation: {weather['precipitation']:.1f}mm
- Wind Speed: {weather['wind_speed']:.1f}km/h
- Pressure: {weather['pressure']:.0f}hPa

## Risk Assessment Results

### 🌊 Flood Risk
- **Risk Level:** {predictions['flood']['risk_level']}
- **Risk Score:** {predictions['flood']['risk_score']:.4f}
- **Confidence:** {predictions['flood']['details'].get('confidence', 'N/A')}
- **Explanation:** {predictions['flood']['details'].get('explanation', 'N/A')}

### 🏜️ Drought Risk
- **Risk Level:** {predictions['drought']['risk_level']}
- **Risk Score:** {predictions['drought']['risk_score']:.4f}
- **Confidence:** {predictions['drought']['details'].get('confidence', 'N/A')}
- **Explanation:** {predictions['drought']['details'].get('explanation', 'N/A')}

### 🔥 Heatwave Risk
- **Risk Level:** {predictions['heatwave']['risk_level']}
- **Risk Score:** {predictions['heatwave']['risk_score']:.4f}
- **Confidence:** {predictions['heatwave']['details'].get('confidence', 'N/A')}
- **Explanation:** {predictions['heatwave']['details'].get('explanation', 'N/A')}

## Model Information
- Architecture: Ensemble (Random Forest + Gradient Boosting)
- Training Accuracy: ~92%
- Test Accuracy: ~87%
- Cross-Validation: 5-fold

---
*Report generated by ResQAlert AI Disaster Prediction System*
*Powered by Ensemble Machine Learning Models*
"""
        
        st.markdown(report)
        
        st.download_button(
            "💾 DOWNLOAD REPORT",
            report,
            file_name=f"risk_assessment_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain",
            use_container_width=True
        )
        
        if st.button("❌ CLOSE", key="close_report"):
            st.session_state.show_report = False
            st.rerun()
    
    if st.session_state.get('download_pred', False):
        import io
        
        pred_data = []
        for dtype, data in predictions.items():
            pred_data.append({
                'Timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'Location': weather.get('location', 'Unknown'),
                'Disaster Type': dtype.title(),
                'Risk Score': data['risk_score'],
                'Risk Level': data['risk_level'],
                'Confidence': data['details'].get('confidence', 'N/A'),
                'Temperature': weather['temperature'],
                'Humidity': weather['humidity'],
                'Precipitation': weather['precipitation']
            })
        
        df_export = pd.DataFrame(pred_data)
        csv_buffer = io.StringIO()
        df_export.to_csv(csv_buffer, index=False)
        
        st.download_button(
            "💾 DOWNLOAD CSV DATA",
            csv_buffer.getvalue(),
            file_name=f"predictions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True,
            type="primary"
        )
        
        if st.button("❌ CLOSE", key="close_csv"):
            st.session_state.download_pred = False
            st.rerun()
