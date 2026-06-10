import streamlit as st
import requests
from math import radians, sin, cos, sqrt, atan2

def get_real_safe_zones(lat: float, lon: float, radius_km: float = 5):
    """
    Fetch real safe zones from OpenStreetMap - ENHANCED VERSION
    """
    import requests
    
    try:
        radius_m = radius_km * 1000
        overpass_url = "https://overpass-api.de/api/interpreter"
        
        # ENHANCED: More facility types
        overpass_query = f"""
        [out:json][timeout:30];
        (
          node["amenity"="hospital"](around:{radius_m},{lat},{lon});
          node["amenity"="clinic"](around:{radius_m},{lat},{lon});
          node["amenity"="doctors"](around:{radius_m},{lat},{lon});
          node["amenity"="fire_station"](around:{radius_m},{lat},{lon});
          node["amenity"="police"](around:{radius_m},{lat},{lon});
          node["amenity"="shelter"](around:{radius_m},{lat},{lon});
          node["amenity"="community_centre"](around:{radius_m},{lat},{lon});
          node["amenity"="social_facility"](around:{radius_m},{lat},{lon});
          node["emergency"="assembly_point"](around:{radius_m},{lat},{lon});
          way["amenity"="hospital"](around:{radius_m},{lat},{lon});
          way["amenity"="clinic"](around:{radius_m},{lat},{lon});
          way["amenity"="fire_station"](around:{radius_m},{lat},{lon});
          way["amenity"="police"](around:{radius_m},{lat},{lon});
          way["building"="hospital"](around:{radius_m},{lat},{lon});
        );
        out center tags;
        """
        
        response = requests.post(overpass_url, data={'data': overpass_query}, timeout=30)
        
        if response.status_code != 200:
            return []
        
        data = response.json()
        elements = data.get('elements', [])
        
        safe_zones = []
        seen_names = set()
        
        for element in elements:
            # Get coordinates
            if element.get('type') == 'node':
                elem_lat = element.get('lat')
                elem_lon = element.get('lon')
            elif element.get('type') == 'way' and 'center' in element:
                elem_lat = element['center']['lat']
                elem_lon = element['center']['lon']
            else:
                continue
            
            tags = element.get('tags', {})
            name = tags.get('name', tags.get('operator', 'Unknown Facility'))
            
            # Skip duplicates
            if name in seen_names and name != 'Unknown Facility':
                continue
            seen_names.add(name)
            
            # Determine facility type and details
            amenity = tags.get('amenity', '')
            building = tags.get('building', '')
            emergency = tags.get('emergency', '')
            
            if amenity == 'hospital' or building == 'hospital':
                facility_type = 'Hospital'
                icon_color = 'red'
                services = tags.get('healthcare', 'General Medical Care')
                capacity = tags.get('beds', 'N/A')
            elif amenity == 'clinic' or amenity == 'doctors':
                facility_type = 'Clinic'
                icon_color = 'pink'
                services = 'Outpatient Care'
                capacity = 'N/A'
            elif amenity == 'fire_station':
                facility_type = 'Fire Station'
                icon_color = 'orange'
                services = 'Fire & Rescue'
                capacity = 'N/A'
            elif amenity == 'police':
                facility_type = 'Police Station'
                icon_color = 'blue'
                services = 'Law Enforcement'
                capacity = 'N/A'
            elif amenity == 'shelter' or amenity == 'social_facility':
                facility_type = 'Emergency Shelter'
                icon_color = 'green'
                services = 'Temporary Shelter'
                capacity = tags.get('capacity', 'N/A')
            elif amenity == 'community_centre':
                facility_type = 'Community Center'
                icon_color = 'purple'
                services = 'Evacuation Point'
                capacity = tags.get('capacity', 'N/A')
            elif emergency == 'assembly_point':
                facility_type = 'Assembly Point'
                icon_color = 'lightblue'
                services = 'Emergency Meeting Point'
                capacity = 'N/A'
            else:
                facility_type = 'Emergency Facility'
                icon_color = 'gray'
                services = 'General Emergency Services'
                capacity = 'N/A'
            
            # Calculate distance
            from math import radians, sin, cos, sqrt, atan2
            R = 6371
            lat1, lon1 = radians(lat), radians(lon)
            lat2, lon2 = radians(elem_lat), radians(elem_lon)
            dlat = lat2 - lat1
            dlon = lon2 - lon1
            a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
            c = 2 * atan2(sqrt(a), sqrt(1-a))
            distance_km = R * c
            
            # Estimate travel time (assuming 40 km/h average speed)
            travel_time_min = int((distance_km / 40) * 60)
            
            # Get contact info
            addr_street = tags.get('addr:street', '')
            addr_city = tags.get('addr:city', '')
            addr_postcode = tags.get('addr:postcode', '')
            phone = tags.get('phone', tags.get('contact:phone', 'N/A'))
            website = tags.get('website', tags.get('contact:website', ''))
            opening_hours = tags.get('opening_hours', '24/7' if amenity in ['hospital', 'fire_station', 'police'] else 'N/A')
            
            # Build address
            address_parts = [p for p in [addr_street, addr_city, addr_postcode] if p]
            address = ', '.join(address_parts) if address_parts else 'Address not available'
            
            safe_zones.append({
                'name': name,
                'type': facility_type,
                'lat': elem_lat,
                'lon': elem_lon,
                'distance_km': round(distance_km, 2),
                'travel_time_min': travel_time_min,
                'address': address,
                'phone': phone,
                'website': website,
                'opening_hours': opening_hours,
                'services': services,
                'capacity': capacity,
                'icon_color': icon_color
            })
        
        # Sort by distance
        safe_zones.sort(key=lambda x: x['distance_km'])
        
        return safe_zones[:20]  # Top 20
    
    except Exception as e:
        st.error(f"⚠️ Error fetching facilities: {str(e)}")
        return []