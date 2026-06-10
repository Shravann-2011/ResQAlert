import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

from services.weather_service import weather_service
from models.disaster_prediction import disaster_predictor  # ← ADD THIS LINE

def render_historical_analysis():
    """COMPLETE Historical Analysis with Weather Trends & Patterns"""
    st.header("📊 HISTORICAL ANALYSIS")
    st.markdown("<br>", unsafe_allow_html=True)
    
    # ========== TIME PERIOD SELECTOR ==========
    st.subheader("📅 SELECT TIME PERIOD")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        analysis_type = st.selectbox(
            "Analysis Type:",
            ["Weather Trends", "Risk Patterns", "Seasonal Analysis"],
            key="analysis_type"
        )
    
    with col2:
        time_range = st.selectbox(
            "Time Range:",
            ["Last 7 Days", "Last 30 Days", "Last 90 Days", "Last Year"],
            key="time_range"
        )
    
    with col3:
        data_source = st.selectbox(
            "Data Source:",
            ["Simulated Data", "Real Data (when available)"],
            key="data_source"
        )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # ========== GENERATE HISTORICAL DATA ==========
    # Map time range to days
    days_map = {
        "Last 7 Days": 7,
        "Last 30 Days": 30,
        "Last 90 Days": 90,
        "Last Year": 365
    }
    days = days_map[time_range]
    
    # Generate sample historical data (replace with real data when available)
    dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
    
    # Generate realistic weather patterns
    np.random.seed(42)
    base_temp = 28
    temp_variation = np.sin(np.linspace(0, 4*np.pi, days)) * 8
    temp_noise = np.random.normal(0, 2, days)
    temperatures = base_temp + temp_variation + temp_noise
    
    humidity = 60 + np.sin(np.linspace(0, 4*np.pi, days)) * 20 + np.random.normal(0, 5, days)
    humidity = np.clip(humidity, 30, 95)
    
    precipitation = np.abs(np.random.exponential(5, days))
    precipitation = np.clip(precipitation, 0, 100)
    
    wind_speed = 15 + np.random.exponential(5, days)
    wind_speed = np.clip(wind_speed, 0, 80)
    
    pressure = 1013 + np.sin(np.linspace(0, 2*np.pi, days)) * 15 + np.random.normal(0, 3, days)
    
    # Create DataFrame
    hist_df = pd.DataFrame({
        'Date': dates,
        'Temperature': temperatures,
        'Humidity': humidity,
        'Precipitation': precipitation,
        'Wind Speed': wind_speed,
        'Pressure': pressure
    })
    
    # Calculate risk scores based on historical weather
    flood_risk = []
    drought_risk = []
    heatwave_risk = []
    
    for _, row in hist_df.iterrows():
        weather_dict = {
            'temperature': row['Temperature'],
            'humidity': row['Humidity'],
            'precipitation': row['Precipitation'],
            'wind_speed': row['Wind Speed'],
            'pressure': row['Pressure']
        }
        
        # Get predictions
        f_score, _, _ = disaster_predictor.predict_disaster_risk(weather_dict, 'flood')
        d_score, _, _ = disaster_predictor.predict_disaster_risk(weather_dict, 'drought')
        h_score, _, _ = disaster_predictor.predict_disaster_risk(weather_dict, 'heatwave')
        
        flood_risk.append(f_score)
        drought_risk.append(d_score)
        heatwave_risk.append(h_score)
    
    hist_df['Flood Risk'] = flood_risk
    hist_df['Drought Risk'] = drought_risk
    hist_df['Heatwave Risk'] = heatwave_risk
    
    # ========== SUMMARY STATISTICS ==========
    st.subheader("📈 SUMMARY STATISTICS")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        avg_temp = hist_df['Temperature'].mean()
        st.metric("🌡️ Avg Temp", f"{avg_temp:.1f}°C")
    
    with col2:
        max_temp = hist_df['Temperature'].max()
        max_date = hist_df.loc[hist_df['Temperature'].idxmax(), 'Date'].strftime('%b %d')
        st.metric("🔥 Max Temp", f"{max_temp:.1f}°C")
        st.caption(f"on {max_date}")
    
    with col3:
        total_rain = hist_df['Precipitation'].sum()
        st.metric("🌧️ Total Rain", f"{total_rain:.0f}mm")
    
    with col4:
        rainy_days = (hist_df['Precipitation'] > 5).sum()
        st.metric("☔ Rainy Days", f"{rainy_days}")
    
    with col5:
        high_risk_days = ((hist_df['Flood Risk'] > 0.6) | 
                          (hist_df['Drought Risk'] > 0.6) | 
                          (hist_df['Heatwave Risk'] > 0.6)).sum()
        st.metric("⚠️ High Risk Days", f"{high_risk_days}")
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # ========== ANALYSIS TYPE SPECIFIC CONTENT ==========
    if analysis_type == "Weather Trends":
        
        # Temperature Trend
        st.subheader("🌡️ TEMPERATURE TRENDS")
        
        fig_temp = go.Figure()
        
        fig_temp.add_trace(go.Scatter(
            x=hist_df['Date'],
            y=hist_df['Temperature'],
            mode='lines',
            name='Temperature',
            line=dict(color='#ef4444', width=2),
            fill='tozeroy',
            fillcolor='rgba(239, 68, 68, 0.1)'
        ))
        
        # Add moving average
        hist_df['Temp_MA'] = hist_df['Temperature'].rolling(window=7).mean()
        fig_temp.add_trace(go.Scatter(
            x=hist_df['Date'],
            y=hist_df['Temp_MA'],
            mode='lines',
            name='7-Day Average',
            line=dict(color='#66fcf1', width=3, dash='dash')
        ))
        
        fig_temp.update_layout(
            title=f"TEMPERATURE OVER {time_range.upper()}",
            xaxis_title="Date",
            yaxis_title="Temperature (°C)",
            template="plotly_dark",
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#c5c6c7', size=12),
            title_font=dict(color='#66fcf1', size=18, family='Orbitron'),
            hovermode='x unified',
            height=450
        )
        
        st.plotly_chart(fig_temp, use_container_width=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Precipitation Pattern
        st.subheader("🌧️ PRECIPITATION PATTERNS")
        
        fig_precip = go.Figure()
        
        fig_precip.add_trace(go.Bar(
            x=hist_df['Date'],
            y=hist_df['Precipitation'],
            name='Daily Rainfall',
            marker=dict(
                color=hist_df['Precipitation'],
                colorscale='Blues',
                showscale=True,
                colorbar=dict(title="mm")
            )
        ))
        
        fig_precip.update_layout(
            title=f"RAINFALL OVER {time_range.upper()}",
            xaxis_title="Date",
            yaxis_title="Precipitation (mm)",
            template="plotly_dark",
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#c5c6c7', size=12),
            title_font=dict(color='#66fcf1', size=18, family='Orbitron'),
            height=450
        )
        
        st.plotly_chart(fig_precip, use_container_width=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Humidity & Wind
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**💧 HUMIDITY TREND**")
            
            fig_humidity = go.Figure()
            fig_humidity.add_trace(go.Scatter(
                x=hist_df['Date'],
                y=hist_df['Humidity'],
                mode='lines',
                fill='tozeroy',
                line=dict(color='#3b82f6', width=2)
            ))
            
            fig_humidity.update_layout(
                yaxis_title="Humidity (%)",
                template="plotly_dark",
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#c5c6c7', size=10),
                height=300,
                showlegend=False
            )
            
            st.plotly_chart(fig_humidity, use_container_width=True)
        
        with col2:
            st.markdown("**💨 WIND SPEED TREND**")
            
            fig_wind = go.Figure()
            fig_wind.add_trace(go.Scatter(
                x=hist_df['Date'],
                y=hist_df['Wind Speed'],
                mode='lines',
                fill='tozeroy',
                line=dict(color='#10b981', width=2)
            ))
            
            fig_wind.update_layout(
                yaxis_title="Wind Speed (km/h)",
                template="plotly_dark",
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#c5c6c7', size=10),
                height=300,
                showlegend=False
            )
            
            st.plotly_chart(fig_wind, use_container_width=True)
    
    elif analysis_type == "Risk Patterns":
        
        st.subheader("⚠️ DISASTER RISK EVOLUTION")
        
        fig_risk = go.Figure()
        
        fig_risk.add_trace(go.Scatter(
            x=hist_df['Date'],
            y=hist_df['Flood Risk'],
            mode='lines+markers',
            name='Flood Risk',
            line=dict(color='#3b82f6', width=3),
            marker=dict(size=4)
        ))
        
        fig_risk.add_trace(go.Scatter(
            x=hist_df['Date'],
            y=hist_df['Drought Risk'],
            mode='lines+markers',
            name='Drought Risk',
            line=dict(color='#f59e0b', width=3),
            marker=dict(size=4)
        ))
        
        fig_risk.add_trace(go.Scatter(
            x=hist_df['Date'],
            y=hist_df['Heatwave Risk'],
            mode='lines+markers',
            name='Heatwave Risk',
            line=dict(color='#ef4444', width=3),
            marker=dict(size=4)
        ))
        
        # Add threshold line
        fig_risk.add_hline(
            y=0.6, 
            line_dash="dash", 
            line_color="#66fcf1",
            annotation_text="High Risk Threshold"
        )
        
        fig_risk.update_layout(
            title=f"RISK LEVELS OVER {time_range.upper()}",
            xaxis_title="Date",
            yaxis_title="Risk Score (0-1)",
            template="plotly_dark",
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#c5c6c7', size=12),
            title_font=dict(color='#66fcf1', size=18, family='Orbitron'),
            hovermode='x unified',
            height=500,
            yaxis=dict(range=[0, 1])
        )
        
        st.plotly_chart(fig_risk, use_container_width=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Risk Distribution
        st.subheader("📊 RISK DISTRIBUTION")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("**🌊 FLOOD RISK**")
            low = (hist_df['Flood Risk'] < 0.4).sum()
            med = ((hist_df['Flood Risk'] >= 0.4) & (hist_df['Flood Risk'] < 0.7)).sum()
            high = (hist_df['Flood Risk'] >= 0.7).sum()
            
            fig_flood_dist = go.Figure(data=[go.Pie(
                labels=['Low', 'Medium', 'High'],
                values=[low, med, high],
                marker=dict(colors=['#10b981', '#f59e0b', '#ef4444']),
                hole=0.4
            )])
            
            fig_flood_dist.update_layout(
                template="plotly_dark",
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#c5c6c7', size=10),
                height=250,
                showlegend=True
            )
            
            st.plotly_chart(fig_flood_dist, use_container_width=True)
        
        with col2:
            st.markdown("**🏜️ DROUGHT RISK**")
            low = (hist_df['Drought Risk'] < 0.4).sum()
            med = ((hist_df['Drought Risk'] >= 0.4) & (hist_df['Drought Risk'] < 0.7)).sum()
            high = (hist_df['Drought Risk'] >= 0.7).sum()
            
            fig_drought_dist = go.Figure(data=[go.Pie(
                labels=['Low', 'Medium', 'High'],
                values=[low, med, high],
                marker=dict(colors=['#10b981', '#f59e0b', '#ef4444']),
                hole=0.4
            )])
            
            fig_drought_dist.update_layout(
                template="plotly_dark",
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#c5c6c7', size=10),
                height=250,
                showlegend=True
            )
            
            st.plotly_chart(fig_drought_dist, use_container_width=True)
        
        with col3:
            st.markdown("**🔥 HEATWAVE RISK**")
            low = (hist_df['Heatwave Risk'] < 0.4).sum()
            med = ((hist_df['Heatwave Risk'] >= 0.4) & (hist_df['Heatwave Risk'] < 0.7)).sum()
            high = (hist_df['Heatwave Risk'] >= 0.7).sum()
            
            fig_heat_dist = go.Figure(data=[go.Pie(
                labels=['Low', 'Medium', 'High'],
                values=[low, med, high],
                marker=dict(colors=['#10b981', '#f59e0b', '#ef4444']),
                hole=0.4
            )])
            
            fig_heat_dist.update_layout(
                template="plotly_dark",
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#c5c6c7', size=10),
                height=250,
                showlegend=True
            )
            
            st.plotly_chart(fig_heat_dist, use_container_width=True)
    
    else:  # Seasonal Analysis
        
        st.subheader("🌍 SEASONAL PATTERNS")
        
        # Group by month/season
        hist_df['Month'] = hist_df['Date'].dt.month
        hist_df['Month_Name'] = hist_df['Date'].dt.strftime('%B')
        
        monthly_stats = hist_df.groupby('Month_Name').agg({
            'Temperature': 'mean',
            'Precipitation': 'sum',
            'Humidity': 'mean',
            'Flood Risk': 'mean',
            'Drought Risk': 'mean',
            'Heatwave Risk': 'mean'
        }).reset_index()
        
        # Monthly temperature & rainfall
        fig_seasonal = go.Figure()
        
        fig_seasonal.add_trace(go.Bar(
            x=monthly_stats['Month_Name'],
            y=monthly_stats['Precipitation'],
            name='Total Rainfall (mm)',
            yaxis='y',
            marker=dict(color='#3b82f6')
        ))
        
        fig_seasonal.add_trace(go.Scatter(
            x=monthly_stats['Month_Name'],
            y=monthly_stats['Temperature'],
            name='Avg Temperature (°C)',
            yaxis='y2',
            mode='lines+markers',
            line=dict(color='#ef4444', width=3),
            marker=dict(size=10)
        ))
        
        fig_seasonal.update_layout(
            title="MONTHLY TEMPERATURE & RAINFALL PATTERNS",
            template="plotly_dark",
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#c5c6c7', size=12),
            title_font=dict(color='#66fcf1', size=18, family='Orbitron'),
            height=450,
            yaxis=dict(title="Rainfall (mm)", titlefont=dict(color='#3b82f6')),
            yaxis2=dict(title="Temperature (°C)", overlaying='y', side='right', titlefont=dict(color='#ef4444')),
            hovermode='x unified'
        )
        
        st.plotly_chart(fig_seasonal, use_container_width=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Seasonal risk heatmap
        st.subheader("🗓️ RISK CALENDAR HEATMAP")
        
        # Create heatmap data
        risk_pivot = hist_df.pivot_table(
            values=['Flood Risk', 'Drought Risk', 'Heatwave Risk'],
            index=hist_df['Date'].dt.isocalendar().week,
            aggfunc='mean'
        )
        
        fig_heatmap = go.Figure()
        
        for i, col in enumerate(['Flood Risk', 'Drought Risk', 'Heatwave Risk']):
            fig_heatmap.add_trace(go.Heatmap(
                z=[risk_pivot[col].values],
                x=risk_pivot.index,
                y=[col],
                colorscale='RdYlGn_r',
                zmin=0,
                zmax=1,
                showscale=(i==0)
            ))
        
        fig_heatmap.update_layout(
            title="WEEKLY RISK PATTERNS",
            xaxis_title="Week of Year",
            template="plotly_dark",
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#c5c6c7', size=12),
            title_font=dict(color='#66fcf1', size=16, family='Orbitron'),
            height=300
        )
        
        st.plotly_chart(fig_heatmap, use_container_width=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # ========== DATA TABLE ==========
    st.subheader("📋 RAW DATA")
    
    with st.expander("View Detailed Data Table"):
        display_df = hist_df[['Date', 'Temperature', 'Humidity', 'Precipitation', 
                               'Wind Speed', 'Flood Risk', 'Drought Risk', 'Heatwave Risk']].copy()
        display_df['Date'] = display_df['Date'].dt.strftime('%Y-%m-%d')
        display_df = display_df.round(2)
        
        st.dataframe(
            display_df,
            use_container_width=True,
            height=400
        )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # ========== EXPORT OPTIONS ==========
    st.subheader("📥 EXPORT HISTORICAL DATA")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📊 DOWNLOAD CSV", type="primary", use_container_width=True):
            import io
            
            csv_buffer = io.StringIO()
            hist_df.to_csv(csv_buffer, index=False)
            
            st.download_button(
                label="💾 SAVE CSV FILE",
                data=csv_buffer.getvalue(),
                file_name=f"historical_data_{time_range.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True
            )
    
    with col2:
        if st.button("📄 GENERATE REPORT", use_container_width=True):
            report = f"""# Historical Weather & Risk Analysis Report
**Period:** {time_range}
**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Summary Statistics
- Average Temperature: {hist_df['Temperature'].mean():.1f}°C
- Maximum Temperature: {hist_df['Temperature'].max():.1f}°C
- Total Rainfall: {hist_df['Precipitation'].sum():.1f}mm
- Rainy Days: {(hist_df['Precipitation'] > 5).sum()}
- High Risk Days: {high_risk_days}

## Risk Analysis
- Average Flood Risk: {hist_df['Flood Risk'].mean():.3f}
- Average Drought Risk: {hist_df['Drought Risk'].mean():.3f}
- Average Heatwave Risk: {hist_df['Heatwave Risk'].mean():.3f}

---
*Generated by ResQAlert Historical Analysis System*
"""
            
            st.download_button(
                label="💾 SAVE REPORT (TXT)",
                data=report,
                file_name=f"analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain",
                use_container_width=True
            )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    st.info("💡 **Note:** This uses simulated historical data for demonstration. In production, this would show actual historical weather and prediction data from your database.")
