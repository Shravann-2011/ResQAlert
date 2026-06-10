"""
Weather API service for fetching real-time weather data
"""
import requests
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from config.settings import settings
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WeatherService:
    def __init__(self):
        self.api_key = settings.OPENWEATHER_API_KEY
        self.base_url = settings.WEATHER_API_BASE_URL
        self.session = requests.Session()
    
    def get_current_weather(self, lat: float, lon: float) -> Optional[Dict]:
        """
        Get current weather data for given coordinates
        
        Args:
            lat: Latitude
            lon: Longitude
            
        Returns:
            Dictionary with weather data or None if failed
        """
        try:
            url = f"{self.base_url}/weather"
            params = {
                'lat': lat,
                'lon': lon,
                'appid': self.api_key,
                'units': 'metric'  # Celsius, km/h, etc.
            }
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Extract relevant weather information
            weather_data = {
                'location': data.get('name', 'Unknown'),
                'latitude': lat,
                'longitude': lon,
                'temperature': data['main']['temp'],
                'humidity': data['main']['humidity'],
                'pressure': data['main']['pressure'],
                'wind_speed': data.get('wind', {}).get('speed', 0),
                'precipitation': data.get('rain', {}).get('1h', 0) + data.get('snow', {}).get('1h', 0),
                'weather_main': data['weather'][0]['main'],
                'weather_description': data['weather'][0]['description'],
                'timestamp': datetime.utcnow()
            }
            
            logger.info(f"Successfully fetched weather data for {lat}, {lon}")
            return weather_data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching weather data: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in get_current_weather: {e}")
            return None
    
    def get_forecast(self, lat: float, lon: float, days: int = 5) -> Optional[List[Dict]]:
        """
        Get weather forecast for given coordinates
        
        Args:
            lat: Latitude
            lon: Longitude
            days: Number of days to forecast
            
        Returns:
            List of forecast data or None if failed
        """
        try:
            url = f"{self.base_url}/forecast"
            params = {
                'lat': lat,
                'lon': lon,
                'appid': self.api_key,
                'units': 'metric'
            }
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            forecast_data = []
            for item in data['list'][:days * 8]:  # 8 forecasts per day (3-hour intervals)
                forecast_item = {
                    'datetime': datetime.fromtimestamp(item['dt']),
                    'temperature': item['main']['temp'],
                    'humidity': item['main']['humidity'],
                    'pressure': item['main']['pressure'],
                    'wind_speed': item.get('wind', {}).get('speed', 0),
                    'precipitation': item.get('rain', {}).get('3h', 0) + item.get('snow', {}).get('3h', 0),
                    'weather_main': item['weather'][0]['main'],
                    'weather_description': item['weather'][0]['description']
                }
                forecast_data.append(forecast_item)
            
            logger.info(f"Successfully fetched forecast data for {lat}, {lon}")
            return forecast_data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching forecast data: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in get_forecast: {e}")
            return None
    
    def get_historical_data(self, lat: float, lon: float, start_date: datetime, end_date: datetime) -> Optional[List[Dict]]:
        """
        Get historical weather data (Note: Requires OpenWeather One Call API subscription)
        For free tier, this will return mock data based on current weather patterns
        """
        try:
            # For demonstration, we'll create mock historical data
            # In production, you would use the One Call API historical endpoint
            historical_data = []
            current_date = start_date
            
            while current_date <= end_date:
                # Get current weather as base for historical estimation
                current_weather = self.get_current_weather(lat, lon)
                if current_weather:
                    historical_item = {
                        'date': current_date,
                        'temperature': current_weather['temperature'] + (hash(str(current_date)) % 20 - 10),  # Mock variation
                        'humidity': max(0, min(100, current_weather['humidity'] + (hash(str(current_date)) % 40 - 20))),
                        'precipitation': max(0, current_weather['precipitation'] + (hash(str(current_date)) % 10 - 5)),
                        'pressure': current_weather['pressure'] + (hash(str(current_date)) % 20 - 10)
                    }
                    historical_data.append(historical_item)
                
                current_date += timedelta(days=1)
            
            return historical_data
            
        except Exception as e:
            logger.error(f"Error generating historical data: {e}")
            return None
    
    def get_weather_by_city(self, city_name: str) -> Optional[Dict]:
        """
        Get weather data by city name
        
        Args:
            city_name: Name of the city
            
        Returns:
            Weather data dictionary or None if failed
        """
        try:
            url = f"{self.base_url}/weather"
            params = {
                'q': city_name,
                'appid': self.api_key,
                'units': 'metric'
            }
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Extract coordinates and get detailed weather
            lat = data['coord']['lat']
            lon = data['coord']['lon']
            
            return self.get_current_weather(lat, lon)
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching weather data for city {city_name}: {e}")
            return None
        
    def calculate_feels_like(self, temp: float, humidity: float, wind_speed: float) -> float:
        """Calculate feels-like temperature (heat index or wind chill)"""
        if temp >= 27:  # Hot - use heat index
            heat_index = temp + (0.5555 * (6.11 * pow(2.718281828, (17.27 * temp) / (237.7 + temp)) * (humidity / 100) - 10))
            return round(heat_index, 1)
        elif temp <= 10:  # Cold - use wind chill
            wind_chill = 13.12 + 0.6215 * temp - 11.37 * pow(wind_speed, 0.16) + 0.3965 * temp * pow(wind_speed, 0.16)
            return round(wind_chill, 1)
        else:
            return round(temp, 1)
    
    def get_daily_forecast_summary(self, lat: float, lon: float) -> Optional[List[Dict]]:
        """Get simplified daily forecast (1 per day for 7 days)"""
        try:
            forecast = self.get_forecast(lat, lon, days=7)
            if not forecast:
                return None
            
            # Group by day and average
            daily_data = {}
            for item in forecast:
                date_key = item['datetime'].date()
                if date_key not in daily_data:
                    daily_data[date_key] = []
                daily_data[date_key].append(item)
            
            # Calculate daily averages
            daily_forecast = []
            for date, items in sorted(daily_data.items())[:7]:
                avg_temp = sum(i['temperature'] for i in items) / len(items)
                max_temp = max(i['temperature'] for i in items)
                min_temp = min(i['temperature'] for i in items)
                total_precip = sum(i['precipitation'] for i in items)
                avg_humidity = sum(i['humidity'] for i in items) / len(items)
                
                daily_forecast.append({
                    'date': date,
                    'temp_avg': round(avg_temp, 1),
                    'temp_max': round(max_temp, 1),
                    'temp_min': round(min_temp, 1),
                    'precipitation': round(total_precip, 1),
                    'humidity': round(avg_humidity, 1),
                    'description': items[len(items)//2]['weather_description']  # Midday description
                })
            
            return daily_forecast
        except Exception as e:
            logger.error(f"Error getting daily forecast: {e}")
            return None
    
    def get_weather_alerts(self, weather_data: Dict) -> List[str]:
        """Generate weather alerts based on current conditions"""
        alerts = []
        
        temp = weather_data.get('temperature', 0)
        humidity = weather_data.get('humidity', 0)
        wind = weather_data.get('wind_speed', 0)
        precip = weather_data.get('precipitation', 0)
        
        # Temperature alerts
        if temp > 42:
            alerts.append("🔥 EXTREME HEAT WARNING - Stay indoors, avoid sun exposure")
        elif temp > 38:
            alerts.append("☀️ HEAT ADVISORY - Stay hydrated, limit outdoor activities")
        elif temp < 5:
            alerts.append("❄️ COLD WEATHER ALERT - Wear warm clothing, check heating")
        
        # Precipitation alerts
        if precip > 50:
            alerts.append("🌊 HEAVY RAIN WARNING - Flooding possible, avoid travel")
        elif precip > 20:
            alerts.append("🌧️ RAIN ALERT - Carry umbrella, roads may be slippery")
        
        # Wind alerts
        if wind > 60:
            alerts.append("💨 HIGH WIND WARNING - Secure loose objects, avoid trees")
        elif wind > 40:
            alerts.append("🌬️ WIND ADVISORY - Exercise caution outdoors")
        
        # Humidity alerts
        if humidity > 90 and temp > 30:
            alerts.append("💧 HIGH HUMIDITY - Heat index elevated, stay cool")
        
        if not alerts:
            alerts.append("✅ NO WEATHER WARNINGS - Conditions are normal")
        
        return alerts

# Create global weather service instance
weather_service = WeatherService()

# Test function to verify API connectivity
def test_weather_service():
    """Test function to verify weather service is working"""
    # Test with Bangalore coordinates
    bangalore_lat, bangalore_lon = 12.9716, 77.5946
    
    print("Testing Weather Service...")
    
    # Test current weather
    current = weather_service.get_current_weather(bangalore_lat, bangalore_lon)
    if current:
        print(f"✅ Current weather: {current['temperature']}°C, {current['weather_description']}")
    else:
        print("❌ Failed to fetch current weather")
    
    # Test forecast
    forecast = weather_service.get_forecast(bangalore_lat, bangalore_lon, days=2)
    if forecast:
        print(f"✅ Forecast: {len(forecast)} data points retrieved")
    else:
        print("❌ Failed to fetch forecast")
    
    # Test city search
    city_weather = weather_service.get_weather_by_city("Mumbai")
    if city_weather:
        print(f"✅ City weather: Mumbai - {city_weather['temperature']}°C")
    else:
        print("❌ Failed to fetch city weather")

if __name__ == "__main__":
    test_weather_service()
