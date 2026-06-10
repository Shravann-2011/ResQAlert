import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

from app.alert_manager import alert_manager

def render_alert_history():
    """ENHANCED Alert History & Analytics Dashboard"""
    st.header("📊 ALERT HISTORY & ANALYTICS")
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Fetch all alerts
    all_alerts = alert_manager.get_alert_history(limit=100)
    
    if not all_alerts:
        st.info("📪 No alert history yet. Send your first alert!")
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Show example/placeholder
        st.subheader("📋 WHAT YOU'LL SEE HERE:")
        st.write("• **Timeline** of all sent alerts")
        st.write("• **Statistics** on alert types and success rates")
        st.write("• **Trends** showing alert patterns over time")
        st.write("• **Export** capabilities for reports")
        
        return
    
    # ========== SUMMARY STATISTICS ==========
    st.subheader("📈 QUICK STATISTICS")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("📨 Total Alerts", len(all_alerts))
    
    with col2:
        sms_count = len([a for a in all_alerts if a.alert_type == "sms"])
        st.metric("📱 SMS Sent", sms_count)
    
    with col3:
        success_count = len([a for a in all_alerts if a.status == "sent"])
        success_rate = (success_count / len(all_alerts)) * 100 if all_alerts else 0
        st.metric("✅ Success Rate", f"{success_rate:.1f}%")
    
    with col4:
        # Most common disaster type
        disaster_counts = {}
        for a in all_alerts:
            disaster_counts[a.disaster_type] = disaster_counts.get(a.disaster_type, 0) + 1
        most_common = max(disaster_counts.items(), key=lambda x: x[1])[0] if disaster_counts else "N/A"
        st.metric("🔥 Most Common", most_common.title())
    
    with col5:
        # Last alert time
        if all_alerts:
            last_alert = all_alerts[0].sent_at
            time_diff = datetime.now() - last_alert
            if time_diff.days > 0:
                last_str = f"{time_diff.days}d ago"
            elif time_diff.seconds > 3600:
                last_str = f"{time_diff.seconds // 3600}h ago"
            else:
                last_str = f"{time_diff.seconds // 60}m ago"
            st.metric("🕐 Last Alert", last_str)
        else:
            st.metric("🕐 Last Alert", "N/A")
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # ========== FILTERS ==========
    st.subheader("🔍 FILTERS")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        # Date range filter
        days_filter = st.selectbox(
            "Time Period:",
            ["All Time", "Last 7 Days", "Last 30 Days", "Last 90 Days"],
            key="days_filter"
        )
    
    with col2:
        # Disaster type filter
        disaster_types = ["All"] + list(set([a.disaster_type for a in all_alerts]))
        type_filter = st.selectbox("Disaster Type:", disaster_types, key="type_filter")
    
    with col3:
        # Risk level filter
        risk_levels = ["All"] + list(set([a.risk_level for a in all_alerts]))
        risk_filter = st.selectbox("Risk Level:", risk_levels, key="risk_filter")
    
    with col4:
        # Status filter
        statuses = ["All"] + list(set([a.status for a in all_alerts]))
        status_filter = st.selectbox("Status:", statuses, key="status_filter")
    
    # Apply filters
    filtered_alerts = all_alerts
    
    # Date filter
    if days_filter != "All Time":
        days_map = {"Last 7 Days": 7, "Last 30 Days": 30, "Last 90 Days": 90}
        cutoff_date = datetime.now() - timedelta(days=days_map[days_filter])
        filtered_alerts = [a for a in filtered_alerts if a.sent_at >= cutoff_date]
    
    # Type filter
    if type_filter != "All":
        filtered_alerts = [a for a in filtered_alerts if a.disaster_type == type_filter]
    
    # Risk filter
    if risk_filter != "All":
        filtered_alerts = [a for a in filtered_alerts if a.risk_level == risk_filter]
    
    # Status filter
    if status_filter != "All":
        filtered_alerts = [a for a in filtered_alerts if a.status == status_filter]
    
    st.caption(f"Showing {len(filtered_alerts)} of {len(all_alerts)} alerts")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # ========== ALERT TRENDS CHART ==========
    st.subheader("📈 ALERT TRENDS")
    
    if filtered_alerts:
        # Group alerts by date
        alert_dates = {}
        for alert in filtered_alerts:
            date_key = alert.sent_at.date()
            if date_key not in alert_dates:
                alert_dates[date_key] = {'total': 0, 'flood': 0, 'drought': 0, 'heatwave': 0}
            alert_dates[date_key]['total'] += 1
            alert_dates[date_key][alert.disaster_type] = alert_dates[date_key].get(alert.disaster_type, 0) + 1
        
        # Create dataframe
        trend_df = pd.DataFrame([
            {
                'Date': date,
                'Total Alerts': counts['total'],
                'Flood': counts.get('flood', 0),
                'Drought': counts.get('drought', 0),
                'Heatwave': counts.get('heatwave', 0)
            }
            for date, counts in sorted(alert_dates.items())
        ])
        
        # Line chart
        fig_trend = go.Figure()
        
        fig_trend.add_trace(go.Scatter(
            x=trend_df['Date'],
            y=trend_df['Total Alerts'],
            mode='lines+markers',
            name='Total',
            line=dict(color='#66fcf1', width=3),
            marker=dict(size=8)
        ))
        
        fig_trend.add_trace(go.Scatter(
            x=trend_df['Date'],
            y=trend_df['Flood'],
            mode='lines+markers',
            name='Flood',
            line=dict(color='#3b82f6', width=2),
            marker=dict(size=6)
        ))
        
        fig_trend.add_trace(go.Scatter(
            x=trend_df['Date'],
            y=trend_df['Drought'],
            mode='lines+markers',
            name='Drought',
            line=dict(color='#f59e0b', width=2),
            marker=dict(size=6)
        ))
        
        fig_trend.add_trace(go.Scatter(
            x=trend_df['Date'],
            y=trend_df['Heatwave'],
            mode='lines+markers',
            name='Heatwave',
            line=dict(color='#ef4444', width=2),
            marker=dict(size=6)
        ))
        
        fig_trend.update_layout(
            title="ALERTS OVER TIME",
            xaxis_title="Date",
            yaxis_title="Number of Alerts",
            template="plotly_dark",
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#c5c6c7', size=12),
            title_font=dict(color='#66fcf1', size=18, family='Orbitron'),
            hovermode='x unified',
            height=400
        )
        
        st.plotly_chart(fig_trend, use_container_width=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # ========== DISTRIBUTION CHARTS ==========
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🎯 ALERTS BY TYPE")
        
        if filtered_alerts:
            type_counts = {}
            for alert in filtered_alerts:
                type_counts[alert.disaster_type.title()] = type_counts.get(alert.disaster_type.title(), 0) + 1
            
            fig_type = go.Figure(data=[
                go.Pie(
                    labels=list(type_counts.keys()),
                    values=list(type_counts.values()),
                    hole=0.4,
                    marker=dict(colors=['#3b82f6', '#f59e0b', '#ef4444'])
                )
            ])
            
            fig_type.update_layout(
                template="plotly_dark",
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#c5c6c7', size=12),
                height=350,
                showlegend=True
            )
            
            st.plotly_chart(fig_type, use_container_width=True)
    
    with col2:
        st.subheader("⚡ RISK LEVELS")
        
        if filtered_alerts:
            risk_counts = {}
            for alert in filtered_alerts:
                risk_counts[alert.risk_level.title()] = risk_counts.get(alert.risk_level.title(), 0) + 1
            
            fig_risk = go.Figure(data=[
                go.Bar(
                    x=list(risk_counts.keys()),
                    y=list(risk_counts.values()),
                    marker=dict(
                        color=['#10b981', '#f59e0b', '#ef4444'][:len(risk_counts)],
                    ),
                    text=list(risk_counts.values()),
                    textposition='outside'
                )
            ])
            
            fig_risk.update_layout(
                template="plotly_dark",
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#c5c6c7', size=12),
                height=350,
                xaxis_title="Risk Level",
                yaxis_title="Count",
                showlegend=False
            )
            
            st.plotly_chart(fig_risk, use_container_width=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # ========== DETAILED ALERT TABLE ==========
    st.subheader("📋 DETAILED ALERT LOG")
    
    # Create display dataframe
    table_data = []
    for alert in filtered_alerts[:50]:  # Limit to 50 most recent
        table_data.append({
            "📅 Date": alert.sent_at.strftime("%Y-%m-%d"),
            "⏰ Time": alert.sent_at.strftime("%H:%M:%S"),
            "🚨 Disaster": alert.disaster_type.title(),
            "⚡ Risk": alert.risk_level.title(),
            "📱 Type": alert.alert_type.upper(),
            "✅ Status": alert.status.title(),
            "📍 Location": getattr(alert, 'location', 'N/A')
        })
    
    if table_data:
        df_display = pd.DataFrame(table_data)
        
        st.dataframe(
            df_display,
            use_container_width=True,
            hide_index=True,
            height=400
        )
        
        st.caption(f"Showing last 50 alerts (of {len(filtered_alerts)} filtered)")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # ========== EXPORT OPTIONS ==========
    st.subheader("📥 EXPORT DATA")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 EXPORT CSV", use_container_width=True, type="primary"):
            st.session_state.export_history = True
    
    with col2:
        if st.button("📄 GENERATE REPORT", use_container_width=True):
            st.session_state.generate_report = True
    
    with col3:
        if st.button("🔄 REFRESH DATA", use_container_width=True):
            st.rerun()
    
    # Handle CSV export
    if st.session_state.get('export_history', False):
        import io
        
        export_data = []
        for alert in filtered_alerts:
            export_data.append({
                'Timestamp': alert.sent_at.strftime('%Y-%m-%d %H:%M:%S'),
                'Disaster Type': alert.disaster_type,
                'Risk Level': alert.risk_level,
                'Alert Type': alert.alert_type,
                'Status': alert.status,
                'Location': getattr(alert, 'location', 'N/A'),
                'Recipients': getattr(alert, 'recipient_count', 'N/A')
            })
        
        df_export = pd.DataFrame(export_data)
        csv_buffer = io.StringIO()
        df_export.to_csv(csv_buffer, index=False)
        csv_data = csv_buffer.getvalue()
        
        st.download_button(
            label="💾 DOWNLOAD CSV FILE",
            data=csv_data,
            file_name=f"alert_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            type="primary",
            use_container_width=True
        )
        
        if st.button("❌ CLOSE", use_container_width=True):
            st.session_state.export_history = False
            st.rerun()
    
    # Handle report generation
    if st.session_state.get('generate_report', False):
        st.markdown("---")
        st.subheader("📄 ALERT SUMMARY REPORT")
        
        report_text = f"""
# ResQAlert - Alert History Report
**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Summary Statistics
- **Total Alerts:** {len(filtered_alerts)}
- **Success Rate:** {success_rate:.1f}%
- **Most Common Type:** {most_common.title()}
- **Time Period:** {days_filter}

## Breakdown by Disaster Type
"""
        for dtype, count in disaster_counts.items():
            percentage = (count / len(filtered_alerts)) * 100
            report_text += f"- **{dtype.title()}:** {count} alerts ({percentage:.1f}%)\n"
        
        report_text += f"""
## Alert Status
- **Sent:** {success_count}
- **Failed:** {len(filtered_alerts) - success_count}

---
*Report generated by ResQAlert AI Disaster Prediction System*
"""
        
        st.markdown(report_text)
        
        st.download_button(
            label="💾 DOWNLOAD REPORT (TXT)",
            data=report_text,
            file_name=f"alert_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain",
            use_container_width=True
        )
        
        if st.button("❌ CLOSE REPORT", use_container_width=True):
            st.session_state.generate_report = False
            st.rerun()
