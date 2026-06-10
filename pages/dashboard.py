import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time

from services.weather_service import weather_service

def render_weather_dashboard():
    """SUPER ENHANCED Weather Monitoring with all features"""
    st.header("🌐 WEATHER MONITORING")
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Location input with update button
    col1, col2 = st.columns([4, 1])
    
    with col1:
        location_input = st.text_input(
            "🌍 LOCATION:",
            value=st.session_state.current_location['name'],
            placeholder="Enter city name (e.g., Bangalore, Mumbai, Delhi)",
            key="loc_input",
            help="Enter any city name worldwide"
        )
    
    with col2:
        st.write("")
        st.write("")
        if st.button("🔄 UPDATE", type="primary", use_container_width=True):
            with st.spinner("🌐 Fetching weather data..."):
                time.sleep(0.3)
                weather_data = weather_service.get_weather_by_city(location_input)
                
                if weather_data:
                    st.session_state.weather_data = weather_data
                    st.session_state.current_location = {
                        'lat': weather_data['latitude'],
                        'lon': weather_data['longitude'],
                        'name': weather_data['location']
                    }
                    st.session_state.last_update = datetime.now()
                    st.success(f"✅ Updated for {weather_data['location']}")
                    time.sleep(0.3)
                    st.rerun()
                else:
                    st.error("❌ Location not found. Try: 'Bangalore', 'Mumbai', 'Delhi'")
                    return
    
    if not st.session_state.weather_data:
        st.info("👆 Enter a location and click UPDATE to fetch weather data")
        return
    
    weather = st.session_state.weather_data
    location_name = weather.get('location', 'Unknown')
    lat = weather['latitude']
    lon = weather['longitude']
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # ========== WEATHER ALERTS ==========
    st.subheader("⚠️ WEATHER ALERTS")
    alerts = weather_service.get_weather_alerts(weather)
    
    for alert in alerts:
        if "WARNING" in alert or "EXTREME" in alert:
            st.error(alert)
        elif "ADVISORY" in alert or "ALERT" in alert:
            st.warning(alert)
        else:
            st.success(alert)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # ========== CURRENT CONDITIONS ==========
    st.subheader("🌡️ CURRENT CONDITIONS")
    
    # Calculate feels-like temperature
    feels_like = weather_service.calculate_feels_like(
        weather['temperature'],
        weather['humidity'],
        weather['wind_speed']
    )
    
    # Display main metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("🌡️ TEMPERATURE", f"{weather['temperature']:.1f}°C")
        st.caption(f"Feels like: {feels_like}°C")
    
    with col2:
        st.metric("💧 HUMIDITY", f"{weather['humidity']:.0f}%")
        humidity_status = "High" if weather['humidity'] > 70 else "Normal" if weather['humidity'] > 40 else "Low"
        st.caption(humidity_status)
    
    with col3:
        st.metric("🌧️ PRECIPITATION", f"{weather['precipitation']:.1f}mm")
        st.caption("Last hour")
    
    with col4:
        st.metric("💨 WIND SPEED", f"{weather['wind_speed']:.1f}km/h")
        wind_status = "Strong" if weather['wind_speed'] > 30 else "Moderate" if weather['wind_speed'] > 15 else "Light"
        st.caption(wind_status)
    
    with col5:
        st.metric("🔽 PRESSURE", f"{weather['pressure']:.0f}hPa")
        pressure_status = "High" if weather['pressure'] > 1020 else "Low" if weather['pressure'] < 1000 else "Normal"
        st.caption(pressure_status)
    
    # Weather description
    st.info(f"☁️ **Conditions:** {weather['weather_description'].title()} ({weather['weather_main']})")
    
    # Last update time
    if st.session_state.last_update:
        update_time = st.session_state.last_update.strftime('%Y-%m-%d %H:%M:%S')
        st.caption(f"⏰ Last updated: {update_time} | 📡 Source: OpenWeatherMap API")
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # ========== 7-DAY FORECAST ==========
    st.subheader("📅 7-DAY FORECAST")
    
    with st.spinner("📊 Loading forecast..."):
        daily_forecast = weather_service.get_daily_forecast_summary(lat, lon)
    
    if daily_forecast:
        # Create forecast dataframe for chart
        forecast_df = pd.DataFrame(daily_forecast)
        forecast_df['date_str'] = forecast_df['date'].astype(str)
        forecast_df['day_name'] = pd.to_datetime(forecast_df['date']).dt.strftime('%a %d')
        
        # Temperature forecast chart
        fig_temp = go.Figure()
        
        fig_temp.add_trace(go.Scatter(
            x=forecast_df['day_name'],
            y=forecast_df['temp_max'],
            name='High',
            mode='lines+markers',
            line=dict(color='#ef4444', width=3),
            marker=dict(size=10),
            fill=None
        ))
        
        fig_temp.add_trace(go.Scatter(
            x=forecast_df['day_name'],
            y=forecast_df['temp_avg'],
            name='Average',
            mode='lines+markers',
            line=dict(color='#f59e0b', width=3),
            marker=dict(size=8),
            fill='tonexty',
            fillcolor='rgba(239, 68, 68, 0.1)'
        ))
        
        fig_temp.add_trace(go.Scatter(
            x=forecast_df['day_name'],
            y=forecast_df['temp_min'],
            name='Low',
            mode='lines+markers',
            line=dict(color='#3b82f6', width=3),
            marker=dict(size=10),
            fill='tonexty',
            fillcolor='rgba(245, 158, 11, 0.1)'
        ))
        
        fig_temp.update_layout(
            title="🌡️ TEMPERATURE FORECAST (7 DAYS)",
            xaxis_title="Date",
            yaxis_title="Temperature (°C)",
            template="plotly_dark",
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#c5c6c7', size=12),
            title_font=dict(color='#66fcf1', size=18, family='Orbitron'),
            hovermode='x unified',
            height=400
        )
        
        st.plotly_chart(fig_temp, use_container_width=True)
        
        # Precipitation forecast chart
        fig_precip = go.Figure()
        
        fig_precip.add_trace(go.Bar(
            x=forecast_df['day_name'],
            y=forecast_df['precipitation'],
            name='Rainfall',
            marker=dict(
                color=forecast_df['precipitation'],
                colorscale='Blues',
                showscale=True,
                colorbar=dict(title="mm")
            ),
            text=forecast_df['precipitation'].round(1),
            textposition='outside'
        ))
        
        fig_precip.update_layout(
            title="🌧️ PRECIPITATION FORECAST (7 DAYS)",
            xaxis_title="Date",
            yaxis_title="Rainfall (mm)",
            template="plotly_dark",
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#c5c6c7', size=12),
            title_font=dict(color='#66fcf1', size=18, family='Orbitron'),
            height=400
        )
        
        st.plotly_chart(fig_precip, use_container_width=True)
        
        # Detailed forecast table
        st.markdown("<br>", unsafe_allow_html=True)
        st.subheader("📋 DETAILED FORECAST")
        
        # Create display dataframe
        display_df = forecast_df[['day_name', 'temp_max', 'temp_min', 'precipitation', 'humidity', 'description']].copy()
        display_df.columns = ['Day', 'High (°C)', 'Low (°C)', 'Rain (mm)', 'Humidity (%)', 'Conditions']
        
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
            height=300
        )
        
    else:
        st.warning("⚠️ Unable to load forecast data")
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # ========== ADDITIONAL WEATHER INFO ==========
    st.subheader("📊 ADDITIONAL INFORMATION")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**🌡️ TEMPERATURE DETAILS:**")
        st.write(f"• Actual: {weather['temperature']:.1f}°C")
        st.write(f"• Feels Like: {feels_like}°C")
        temp_diff = abs(weather['temperature'] - feels_like)
        if temp_diff > 5:
            st.write(f"• ⚠️ Feels {temp_diff:.1f}°C {'hotter' if feels_like > weather['temperature'] else 'cooler'} than actual")
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("**💨 WIND INFORMATION:**")
        st.write(f"• Speed: {weather['wind_speed']:.1f} km/h")
        if weather['wind_speed'] > 50:
            st.write("• ⚠️ Very high winds - secure loose objects")
        elif weather['wind_speed'] > 30:
            st.write("• ⚠️ High winds - be cautious")
        else:
            st.write("• ✅ Winds are normal")
    
    with col2:
        st.markdown("**🔽 ATMOSPHERIC PRESSURE:**")
        st.write(f"• Pressure: {weather['pressure']:.0f} hPa")
        if weather['pressure'] < 1000:
            st.write("• ⚠️ Low pressure - possible storms")
        elif weather['pressure'] > 1020:
            st.write("• ✅ High pressure - clear skies likely")
        else:
            st.write("• ✅ Normal pressure")
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("**💧 HUMIDITY & PRECIPITATION:**")
        st.write(f"• Humidity: {weather['humidity']:.0f}%")
        st.write(f"• Recent rainfall: {weather['precipitation']:.1f}mm")
        if weather['humidity'] > 80 and weather['temperature'] > 30:
            st.write("• ⚠️ High heat index - stay cool")
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # ========== RECOMMENDATIONS ==========
    st.subheader("💡 RECOMMENDATIONS")
    
    recommendations = []
    
    # Temperature-based
    if weather['temperature'] > 38:
        recommendations.append("🔥 Stay indoors during peak hours (10 AM - 6 PM)")
        recommendations.append("💧 Drink plenty of water (3-4 liters/day)")
    elif weather['temperature'] < 10:
        recommendations.append("🧥 Wear warm clothing in layers")
        recommendations.append("☕ Stay warm, drink hot beverages")
    
    # Rain-based
    if weather['precipitation'] > 10:
        recommendations.append("☂️ Carry umbrella, wear waterproof clothing")
        recommendations.append("🚗 Drive carefully, roads may be slippery")
    
    # Wind-based
    if weather['wind_speed'] > 40:
        recommendations.append("🌬️ Secure loose outdoor objects")
        recommendations.append("🚫 Avoid outdoor activities")
    
    # Humidity-based
    if weather['humidity'] > 85:
        recommendations.append("💧 High humidity - use dehumidifier if indoors")
    
    if recommendations:
        for rec in recommendations:
            st.info(rec)
    else:
        st.success("✅ Current conditions are comfortable - enjoy your day!")
