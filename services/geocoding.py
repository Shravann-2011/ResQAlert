import requests

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"

def geocode_location(query: str):
    """
    Geocode a free-text location name to (lat, lon, display_name).
    Uses OpenStreetMap Nominatim (no key required, but rate-limited).
    Returns (lat, lon, display_name) or (None, None, None) on failure.
    """
    if not query or not query.strip():
        return None, None, None

    params = {
        "q": query,
        "format": "json",
        "limit": 1,
    }

    try:
        resp = requests.get(
            NOMINATIM_URL,
            params=params,
            headers={"User-Agent": "resqalert-safezones/1.0"},
            timeout=10,
        )
        if resp.status_code != 200:
            return None, None, None

        data = resp.json()
        if not data:
            return None, None, None

        first = data[0]
        lat = float(first.get("lat"))
        lon = float(first.get("lon"))
        display_name = first.get("display_name", query)

        return lat, lon, display_name
    except Exception:
        return None, None, None
