import streamlit as st
import time

try:
    import folium
    from streamlit_folium import st_folium
    MAPS_AVAILABLE = True
except ImportError:
    MAPS_AVAILABLE = False

from services.safe_zones import get_real_safe_zones
from services.geocoding import geocode_location


def render_safe_zones():
    """Render safe zones locator page with real-time updates and geolocation"""

    # Custom CSS for app-like UI
    st.markdown(
        """
        <style>
            /* Main container styling */
            .sz-header {
                background: linear-gradient(135deg, rgba(56, 189, 248, 0.1) 0%, rgba(14, 165, 233, 0.05) 100%);
                padding: 1.5rem;
                border-radius: 16px;
                border: 1px solid rgba(56, 189, 248, 0.2);
                margin-bottom: 1.5rem;
            }
            .sz-header h2 {
                margin: 0;
                color: #38bdf8;
                font-size: 1.8rem;
                font-weight: 700;
            }
            .sz-header p {
                margin: 0.3rem 0 0 0;
                color: #9ca3af;
                font-size: 0.95rem;
            }
            
            /* Control panel styling */
            .sz-control-panel {
                background: rgba(17, 24, 39, 0.6);
                padding: 1.2rem;
                border-radius: 12px;
                border: 1px solid rgba(75, 85, 99, 0.4);
                margin-bottom: 1rem;
                backdrop-filter: blur(10px);
            }
            
            /* Facility card styling */
            .sz-facility-card {
                background: linear-gradient(135deg, rgba(17, 24, 39, 0.95) 0%, rgba(31, 41, 55, 0.9) 100%);
                border-radius: 12px;
                padding: 1rem 1.2rem;
                border-left: 4px solid #38bdf8;
                margin-bottom: 0.8rem;
                transition: transform 0.2s, box-shadow 0.2s;
                cursor: pointer;
            }
            .sz-facility-card:hover {
                transform: translateX(4px);
                box-shadow: 0 4px 12px rgba(56, 189, 248, 0.2);
            }
            
            /* Type badges */
            .sz-badge {
                display: inline-block;
                padding: 0.25rem 0.7rem;
                border-radius: 20px;
                font-size: 0.75rem;
                font-weight: 600;
                margin-right: 0.4rem;
                margin-bottom: 0.3rem;
            }
            .sz-badge-hospital {
                background: rgba(239, 68, 68, 0.15);
                color: #fca5a5;
                border: 1px solid rgba(239, 68, 68, 0.3);
            }
            .sz-badge-shelter {
                background: rgba(34, 197, 94, 0.15);
                color: #86efac;
                border: 1px solid rgba(34, 197, 94, 0.3);
            }
            .sz-badge-emergency {
                background: rgba(249, 115, 22, 0.15);
                color: #fdba74;
                border: 1px solid rgba(249, 115, 22, 0.3);
            }
            .sz-badge-other {
                background: rgba(147, 197, 253, 0.15);
                color: #93c5fd;
                border: 1px solid rgba(147, 197, 253, 0.3);
            }
            .sz-badge-distance {
                background: rgba(168, 85, 247, 0.15);
                color: #c4b5fd;
                border: 1px solid rgba(168, 85, 247, 0.3);
            }
            
            /* Status indicator */
            .sz-status {
                display: inline-flex;
                align-items: center;
                padding: 0.4rem 0.8rem;
                border-radius: 8px;
                font-size: 0.85rem;
                font-weight: 600;
                margin-bottom: 0.5rem;
            }
            .sz-status-loading {
                background: rgba(234, 179, 8, 0.15);
                color: #fde047;
                border: 1px solid rgba(234, 179, 8, 0.3);
            }
            .sz-status-ready {
                background: rgba(34, 197, 94, 0.15);
                color: #86efac;
                border: 1px solid rgba(34, 197, 94, 0.3);
            }
            
            /* Metric cards */
            .sz-metric {
                background: rgba(17, 24, 39, 0.8);
                padding: 1rem;
                border-radius: 10px;
                border: 1px solid rgba(75, 85, 99, 0.4);
                text-align: center;
            }
            .sz-metric-value {
                font-size: 1.8rem;
                font-weight: 700;
                color: #38bdf8;
                margin-bottom: 0.2rem;
            }
            .sz-metric-label {
                font-size: 0.8rem;
                color: #9ca3af;
                text-transform: uppercase;
                letter-spacing: 0.05em;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Header
    st.markdown(
        """
        <div class="sz-header">
            <h2>🗺️ Safe Zones & Emergency Facilities</h2>
            <p>Real-time location tracking • Find nearby hospitals, shelters & emergency services</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not MAPS_AVAILABLE:
        st.error(
            "📍 **Map visualization unavailable**\n\n"
            "Install required dependencies: `pip install folium streamlit-folium`"
        )
        return

    # Initialize session state for location and flags
    if "sz_center_lat" not in st.session_state:
        st.session_state.sz_center_lat = 12.9716
    if "sz_center_lon" not in st.session_state:
        st.session_state.sz_center_lon = 77.5946
    if "sz_radius" not in st.session_state:
        st.session_state.sz_radius = 5
    if "sz_auto_refresh" not in st.session_state:
        st.session_state.sz_auto_refresh = False
    if "sz_has_searched" not in st.session_state:
        st.session_state.sz_has_searched = False

    # ==========================
    # CONTROL PANEL
    # ==========================
    st.markdown('<div class="sz-control-panel">', unsafe_allow_html=True)

    control_col1, control_col2, control_col3 = st.columns([2, 2, 1])

    with control_col1:
        st.markdown("**📍 Location Settings**")

        # Quick location presets
        location_preset = st.selectbox(
            "Quick select",
            ["Custom Location", "Bangalore", "Mumbai", "Delhi", "Chennai", "Hyderabad"],
            label_visibility="collapsed",
            key="location_preset",
        )

        # Free-text place search (any country/city/area)
        search_place = st.text_input(
            "Search any location (city, country, address)",
            value="",
            placeholder="e.g., Tokyo, Japan or Shibuya City",
            key="sz_search_place",
        )

        if st.button("🔍 Locate on map", key="sz_geocode_button"):
            lat_g, lon_g, display_name = geocode_location(search_place)
            if lat_g is not None and lon_g is not None:
                st.session_state.sz_center_lat = lat_g
                st.session_state.sz_center_lon = lon_g
                st.success(f"📍 Location set to: {display_name}")
                st.rerun()
            else:
                st.warning("Could not find that location. Try a more specific name.")

        # Update coordinates based on preset
        if location_preset == "Bangalore":
            st.session_state.sz_center_lat = 12.9716
            st.session_state.sz_center_lon = 77.5946
        elif location_preset == "Mumbai":
            st.session_state.sz_center_lat = 19.0760
            st.session_state.sz_center_lon = 72.8777
        elif location_preset == "Delhi":
            st.session_state.sz_center_lat = 28.7041
            st.session_state.sz_center_lon = 77.1025
        elif location_preset == "Chennai":
            st.session_state.sz_center_lat = 13.0827
            st.session_state.sz_center_lon = 80.2707
        elif location_preset == "Hyderabad":
            st.session_state.sz_center_lat = 17.3850
            st.session_state.sz_center_lon = 78.4867

        coord_col1, coord_col2 = st.columns(2)
        with coord_col1:
            lat = st.number_input(
                "Latitude",
                min_value=-90.0,
                max_value=90.0,
                value=st.session_state.sz_center_lat,
                step=0.0001,
                format="%.4f",
                key="input_lat",
            )
            st.session_state.sz_center_lat = lat

        with coord_col2:
            lon = st.number_input(
                "Longitude",
                min_value=-180.0,
                max_value=180.0,
                value=st.session_state.sz_center_lon,
                step=0.0001,
                format="%.4f",
                key="input_lon",
            )
            st.session_state.sz_center_lon = lon

    with control_col2:
        st.markdown("**🎯 Search Settings**")

        radius = st.slider(
            "Search radius (km)",
            min_value=1,
            max_value=30,
            value=st.session_state.sz_radius,
            step=1,
            key="input_radius",
            help="Facilities within this radius will be displayed",
        )
        st.session_state.sz_radius = radius

        facility_filter = st.multiselect(
            "Filter facility types",
            ["Hospital/Clinic", "Shelter", "Fire/Police", "Other"],
            default=["Hospital/Clinic", "Shelter", "Fire/Police", "Other"],
            key="facility_filter",
            label_visibility="collapsed",
        )

    with control_col3:
        st.markdown("**⚡ Actions**")

        if st.button("🔄 Refresh", use_container_width=True, type="primary"):
            st.rerun()

        auto_refresh = st.checkbox(
            "Auto-refresh",
            value=st.session_state.sz_auto_refresh,
            key="auto_refresh_check",
        )
        st.session_state.sz_auto_refresh = auto_refresh

        if st.button("📍 Use Weather Location", use_container_width=True):
            if st.session_state.get("current_location") and \
               st.session_state.current_location.get("lat") is not None and \
               st.session_state.current_location.get("lon") is not None:
                st.session_state.sz_center_lat = st.session_state.current_location.get("lat", 12.9716)
                st.session_state.sz_center_lon = st.session_state.current_location.get("lon", 77.5946)
                st.success(
                    f"✅ Location synced: {st.session_state.current_location.get('name', 'Selected location')}"
                )
                st.rerun()
            else:
                st.warning("No location found from Weather. Please set your location in the Weather Monitoring page first.")

    st.markdown("</div>", unsafe_allow_html=True)

    # ==========================
    # FETCH SAFE ZONES (REAL-TIME)
    # ==========================
    st.markdown(
        '<div class="sz-status sz-status-loading">⏳ Fetching real-time data from OpenStreetMap...</div>',
        unsafe_allow_html=True,
    )

    with st.spinner(""):
        safe_zones = get_real_safe_zones(
            st.session_state.sz_center_lat,
            st.session_state.sz_center_lon,
            st.session_state.sz_radius,
        )
        st.session_state.sz_has_searched = True

    if not safe_zones:
        st.info(
            "🔍 No facilities found in the selected radius. Try increasing the radius or adjusting coordinates."
        )
        return

    # Filter based on selection
    filtered_zones = []
    for zone in safe_zones:
        z_type = zone.get("type", "").lower()
        include = False

        if "Hospital/Clinic" in facility_filter and (
            "hospital" in z_type or "clinic" in z_type
        ):
            include = True
        if "Shelter" in facility_filter and "shelter" in z_type:
            include = True
        if "Fire/Police" in facility_filter and (
            "fire" in z_type or "police" in z_type
        ):
            include = True
        if "Other" in facility_filter and not any(
            kw in z_type for kw in ["hospital", "clinic", "shelter", "fire", "police"]
        ):
            include = True

        if include:
            filtered_zones.append(zone)

    st.markdown(
        f'<div class="sz-status sz-status-ready">✅ Found {len(filtered_zones)} facilities • Last updated: {time.strftime("%I:%M %p")}</div>',
        unsafe_allow_html=True,
    )

    # Current search area summary
    st.markdown(
        f"""
        <div style="font-size:0.85rem; color:#9ca3af; margin-bottom:0.8rem;">
            <b>Current center:</b> {st.session_state.sz_center_lat:.4f}, {st.session_state.sz_center_lon:.4f} • 
            <b>Radius:</b> {st.session_state.sz_radius} km
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ==========================
    # METRICS ROW
    # ==========================
    metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)

    hospital_count = sum(
        1
        for z in filtered_zones
        if "hospital" in z.get("type", "").lower()
        or "clinic" in z.get("type", "").lower()
    )
    shelter_count = sum(
        1 for z in filtered_zones if "shelter" in z.get("type", "").lower()
    )
    emergency_count = sum(
        1
        for z in filtered_zones
        if "fire" in z.get("type", "").lower()
        or "police" in z.get("type", "").lower()
    )

    with metric_col1:
        st.markdown(
            f"""
            <div class="sz-metric">
                <div class="sz-metric-value">{len(filtered_zones)}</div>
                <div class="sz-metric-label">Total Facilities</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with metric_col2:
        st.markdown(
            f"""
            <div class="sz-metric">
                <div class="sz-metric-value">{hospital_count}</div>
                <div class="sz-metric-label">Hospitals</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with metric_col3:
        st.markdown(
            f"""
            <div class="sz-metric">
                <div class="sz-metric-value">{shelter_count}</div>
                <div class="sz-metric-label">Shelters</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with metric_col4:
        st.markdown(
            f"""
            <div class="sz-metric">
                <div class="sz-metric-value">{emergency_count}</div>
                <div class="sz-metric-label">Emergency</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # ==========================
    # MAP + LIST LAYOUT
    # ==========================
    map_col, list_col = st.columns([1.8, 1.2])

    with map_col:
        st.markdown("### 🗺️ Interactive Map")

        # Legend
        st.markdown(
            """
            <div style="font-size:0.8rem; color:#9ca3af; margin-bottom:0.3rem;">
                Legend: 
                <span class="sz-badge sz-badge-hospital">Hospitals</span>
                <span class="sz-badge sz-badge-shelter">Shelters</span>
                <span class="sz-badge sz-badge-emergency">Fire / Police</span>
                <span class="sz-badge sz-badge-other">Others</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Create map
        base_map = folium.Map(
            location=[st.session_state.sz_center_lat, st.session_state.sz_center_lon],
            zoom_start=14,
            tiles="OpenStreetMap",
        )

        # Center marker with pulsing effect
        folium.CircleMarker(
            location=[st.session_state.sz_center_lat, st.session_state.sz_center_lon],
            radius=10,
            color="#38bdf8",
            fill=True,
            fill_color="#0ea5e9",
            fill_opacity=0.8,
            popup="<b>Your Location</b>",
            tooltip="Search Center",
        ).add_to(base_map)

        # Add radius circle
        folium.Circle(
            location=[st.session_state.sz_center_lat, st.session_state.sz_center_lon],
            radius=st.session_state.sz_radius * 1000,  # Convert to meters
            color="#38bdf8",
            fill=True,
            fill_opacity=0.1,
            weight=2,
            popup=f"Search Radius: {st.session_state.sz_radius} km",
        ).add_to(base_map)

        # Add facility markers
        for zone in filtered_zones:
            z_lat = zone.get("lat")
            z_lon = zone.get("lon")
            if z_lat is None or z_lon is None:
                continue

            z_type = zone.get("type", "").lower()
            name = zone.get("name", "Unnamed facility")
            dist = zone.get("distance_km", None)
            address = zone.get("address", "")

            # Determine marker color
            if "hospital" in z_type or "clinic" in z_type:
                color = "#ef4444"
                icon = "plus"
            elif "shelter" in z_type:
                color = "#22c55e"
                icon = "home"
            elif "police" in z_type or "fire" in z_type:
                color = "#f97316"
                icon = "warning-sign"
            else:
                color = "#3b82f6"
                icon = "info-sign"

            popup_html = f"""
            <div style="font-family: sans-serif; min-width: 200px;">
                <h4 style="margin: 0 0 8px 0; color: {color};">{name}</h4>
                <p style="margin: 4px 0;"><b>Type:</b> {zone.get('type', 'N/A')}</p>
                {f'<p style="margin: 4px 0;"><b>Distance:</b> {dist:.2f} km</p>' if dist else ''}
                {f'<p style="margin: 4px 0;"><b>Address:</b> {address}</p>' if address else ''}
            </div>
            """

            folium.Marker(
                location=[z_lat, z_lon],
                popup=folium.Popup(popup_html, max_width=300),
                tooltip=name,
                icon=folium.Icon(
                    color="red"
                    if "hospital" in z_type
                    else "green"
                    if "shelter" in z_type
                    else "orange"
                    if "fire" in z_type or "police" in z_type
                    else "blue",
                    icon=icon,
                ),
            ).add_to(base_map)

        st_folium(base_map, width=None, height=600, key="safezones_map")

    with list_col:
        st.markdown("### 📋 Facilities List")
        st.caption(f"Showing {len(filtered_zones)} facilities sorted by distance")

        # Scrollable container under the map
        st.markdown(
            '<div style="max-height: 600px; overflow-y: auto; padding-right: 4px;">',
            unsafe_allow_html=True,
        )

        for zone in sorted(filtered_zones, key=lambda x: x.get("distance_km", 999)):
            name = zone.get("name", "Unnamed facility")
            z_type = zone.get("type", "Facility")
            distance = zone.get("distance_km", None)
            address = zone.get("address", "Address not available")
            lat = zone.get("lat")
            lon = zone.get("lon")

            # Optional extra fields if present in data
            phone = zone.get("phone", "")
            beds = zone.get("beds", "")
            capacity = zone.get("capacity", "")
            extra = zone.get("details", "")

            # Determine badge style
            z_type_lower = z_type.lower()
            if "hospital" in z_type_lower or "clinic" in z_type_lower:
                badge_class = "sz-badge-hospital"
                badge_text = "🏥 Hospital / Clinic"
            elif "shelter" in z_type_lower:
                badge_class = "sz-badge-shelter"
                badge_text = "🏠 Shelter"
            elif "police" in z_type_lower or "fire" in z_type_lower:
                badge_class = "sz-badge-emergency"
                badge_text = "🚨 Emergency"
            else:
                badge_class = "sz-badge-other"
                badge_text = f"📍 {z_type}"

            distance_badge = (
                f'<span class="sz-badge sz-badge-distance">📏 {distance:.2f} km</span>'
                if distance is not None
                else ""
            )

            coord_line = ""
            if lat is not None and lon is not None:
                coord_line = f"Lat: {lat:.4f}, Lon: {lon:.4f}"

            # One card per facility, full width, clear sections
            st.markdown(
                f"""
                <div class="sz-facility-card" style="margin-bottom: 0.9rem;">
                    <div style="display:flex; justify-content:space-between; gap:0.75rem;">
                        <div style="flex: 1;">
                            <div style="font-weight:700; font-size:1rem; color:#e5e7eb; margin-bottom:0.25rem;">
                                {name}
                            </div>
                            <div style="margin-bottom:0.45rem;">
                                <span class="sz-badge {badge_class}">{badge_text}</span>
                                {distance_badge}
                            </div>
                            <div style="font-size:0.82rem; color:#9ca3af; line-height:1.4; margin-bottom:0.35rem;">
                                {address}
                            </div>
                            <div style="font-size:0.78rem; color:#9ca3af; line-height:1.4;">
                                <span style="display:block;"><b>📞 Phone:</b> {phone if phone else "Not available"}</span>
                                <span style="display:block;"><b>🛏️ Capacity:</b> {beds if beds else (capacity if capacity else "Not specified")}</span>
                                <span style="display:block;"><b>ℹ️ Additional info:</b> {extra if extra else "—"}</span>
                            </div>
                        </div>
                        <div style="min-width: 110px; text-align:right; font-size:0.78rem; color:#6b7280;">
                            {f"<div><b>Distance</b><br>{distance:.2f} km</div>" if distance is not None else ""}
                            {f"<div style='margin-top:0.4rem;'>{coord_line}</div>" if coord_line else ""}
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown("</div>", unsafe_allow_html=True)

    # Auto-refresh logic (only after at least one search)
    if st.session_state.sz_auto_refresh and st.session_state.sz_has_searched:
        time.sleep(30)  # Refresh every 30 seconds
        st.rerun()
