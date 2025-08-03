"""
Weather service module for handling NWS API integration and weather data processing.
"""

import requests

from typing import Dict, Optional, Tuple
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable
import logging
import re
import os

logger = logging.getLogger(__name__)


class WeatherService:
    """Service for fetching and processing weather data from NWS API."""
    
    def __init__(self, use_ai_model: bool = True, bedrock_model_id: str = None):
        self.base_url = "https://api.weather.gov"
        self.geolocator = Nominatim(user_agent="weather_chat_ai")
        self.use_ai_model = use_ai_model
        
        # Initialize AI model service if enabled
        if self.use_ai_model:
            try:
                from ai_model_service import AIModelService
                model_id = bedrock_model_id or os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-3-sonnet-20240229-v1:0")
                self.ai_service = AIModelService(model_id=model_id)
                logger.info(f"AI model service initialized with Bedrock model: {model_id}")
            except Exception as e:
                logger.warning(f"Failed to initialize AI model service: {e}")
                self.use_ai_model = False
                self.ai_service = None
        else:
            self.ai_service = None
        
    def geocode_location(self, location: str) -> Optional[Tuple[float, float]]:
        """
        Convert location string to coordinates using geocoding.
        
        Args:
            location: Location string (e.g., "Denver, CO")
            
        Returns:
            Tuple of (latitude, longitude) or None if geocoding fails
        """
        try:
            # Ensure location is a string
            if not isinstance(location, str):
                logger.error(f"Location is not a string: {type(location)} - {location}")
                return None
                
            # Clean up location string
            location = location.strip()
            
            if location.startswith('in '):
                location = location[3:].strip()
                
            # Add common location suffixes if not present
            state_abbreviations = ['city', 'town', 'state', 'co', 'ca', 'ny', 'fl', 'wa', 'tx', 'il', 'pa', 'oh', 'ga', 'nc', 'mi', 'va', 'nj', 'tn', 'az', 'mo', 'md', 'in', 'or', 'sc', 'ky', 'la', 'al', 'ct', 'ut', 'ia', 'nv', 'ar', 'ms', 'ks', 'nm', 'ne', 'id', 'hi', 'nh', 'me', 'ri', 'mt', 'de', 'sd', 'nd', 'ak', 'vt', 'wy', 'wv']
            
            # Check if location contains any state abbreviations
            location_lower = location.lower()
            has_state = False
            for abbr in state_abbreviations:
                if abbr in location_lower:
                    has_state = True
                    break
                    
            if not has_state:
                location = f"{location}, USA"
                
            location_data = self.geolocator.geocode(location)
            if location_data:
                return (location_data.latitude, location_data.longitude)
            return None
        except (GeocoderTimedOut, GeocoderUnavailable) as e:
            logger.error(f"Geocoding error for {location}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in geocoding for {location}: {e}")
            return None
            
    def get_weather_station(self, lat: float, lon: float) -> Optional[str]:
        """
        Get the nearest weather station for given coordinates.
        
        Args:
            lat: Latitude
            lon: Longitude
            
        Returns:
            Weather station ID or None if not found
        """
        try:
            url = f"{self.base_url}/points/{lat},{lon}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            return data.get('properties', {}).get('forecast')
        except requests.RequestException as e:
            logger.error(f"Error getting weather station: {e}")
            return None
            
    def get_forecast(self, lat: float, lon: float) -> Optional[Dict]:
        """
        Get weather forecast for given coordinates.
        
        Args:
            lat: Latitude
            lon: Longitude
            
        Returns:
            Forecast data dictionary or None if error
        """
        try:
            # Get forecast URL
            points_url = f"{self.base_url}/points/{lat},{lon}"
            response = requests.get(points_url, timeout=10)
            response.raise_for_status()
            
            points_data = response.json()
            forecast_url = points_data['properties']['forecast']
            
            # Get forecast data
            forecast_response = requests.get(forecast_url, timeout=10)
            forecast_response.raise_for_status()
            
            return forecast_response.json()
        except requests.RequestException as e:
            logger.error(f"Error getting forecast: {e}")
            return None
            
    def get_current_conditions(self, lat: float, lon: float) -> Optional[Dict]:
        """
        Get current weather conditions for given coordinates.
        
        Args:
            lat: Latitude
            lon: Longitude
            
        Returns:
            Current conditions data or None if error
        """
        try:
            # Get stations
            stations_url = f"{self.base_url}/points/{lat},{lon}/stations"
            response = requests.get(stations_url, timeout=10)
            response.raise_for_status()
            
            stations_data = response.json()
            if not stations_data.get('features'):
                return None
                
            # Get observations from nearest station
            station_id = stations_data['features'][0]['properties']['stationIdentifier']
            observations_url = f"{self.base_url}/stations/{station_id}/observations/latest"
            
            obs_response = requests.get(observations_url, timeout=10)
            obs_response.raise_for_status()
            
            return obs_response.json()
        except requests.RequestException as e:
            logger.error(f"Error getting current conditions: {e}")
            return None
            
    def parse_weather_query(self, query: str) -> Dict:
        """
        Parse weather query to extract location, time, and weather type.
        Uses AI model if available, otherwise falls back to rule-based parsing.
        
        Args:
            query: User's weather query
            
        Returns:
            Dictionary with parsed information
        """
        if self.use_ai_model and self.ai_service:
            # Use AI model for parsing
            ai_result = self.ai_service.extract_weather_info(query)
            
            # Convert AI result to expected format
            return {
                'location': ai_result.get('location'),
                'target_day': self._convert_time_reference(ai_result.get('time_reference')),
                'weather_type': ai_result.get('weather_intent'),
                'original_query': query,
                'ai_extracted': ai_result
            }
        else:
            # Fallback to rule-based parsing
            return self._rule_based_parsing(query)
    
    def _convert_time_reference(self, time_ref: str) -> Optional[int]:
        """Convert time reference to day offset."""
        if not time_ref:
            return None
            
        time_mapping = {
            'today': 0,
            'tomorrow': 1,
            'sunday': 6,
            'monday': 0,
            'tuesday': 1,
            'wednesday': 2,
            'thursday': 3,
            'friday': 4,
            'saturday': 5
        }
        
        return time_mapping.get(time_ref.lower())
    
    def _rule_based_parsing(self, query: str) -> Dict:
        """Rule-based parsing as fallback."""
        query_lower = query.lower()
        location = None  # Initialize location variable
        
        # Look for "in [location]" pattern first
        if ' in ' in query_lower:
            parts = query_lower.split(' in ')
            if len(parts) > 1:
                location_part = parts[1]
                # Take words until we hit a time keyword or end
                time_keywords = ['on', 'today', 'tomorrow', 'this', 'next', 'will', 'is', 'going', 'be', 'the', 'area', 'tonight', '?']
                location_words = []
                for word in location_part.split():
                    if word in time_keywords:
                        break
                    location_words.append(word)
                if location_words:
                    location = ' '.join(location_words).strip()
                    # Clean up any remaining punctuation and time words
                    location = location.rstrip('?').strip()
                    # Remove common time words that might have been included
                    time_cleanup = ['today', 'tomorrow', 'tonight']
                    for time_word in time_cleanup:
                        location = location.replace(time_word, '').strip()
        
        # If no location found, try other patterns
        if not location:
            # Common location patterns
            location_patterns = [
                r'in ([a-zA-Z\s]+?)(?:\s+(?:on|today|tomorrow|this|next|will|is|going|be|the|area|tonight))',
                r'in ([a-zA-Z\s]+?)(?:\?|$)',
                r'([a-zA-Z\s]+?)(?:\s+(?:on|today|tomorrow|this|next))',
                r'([a-zA-Z\s]+?)(?:\?|$)',
            ]
            
            for pattern in location_patterns:
                match = re.search(pattern, query_lower)
                if match:
                    location = match.group(1).strip()
                    # Clean up location name
                    location = re.sub(r'\s+', ' ', location).strip()
                    # Remove common words that aren't part of location names
                    location = re.sub(r'\b(area|tonight|today|tomorrow|this|next|will|is|going|be|the)\b', '', location).strip()
                    if location and len(location) > 1:
                        break
                        
        # Extract time references
        time_keywords = {
            'today': 0,
            'tomorrow': 1,
            'sunday': 6,
            'monday': 0,
            'tuesday': 1,
            'wednesday': 2,
            'thursday': 3,
            'friday': 4,
            'saturday': 5
        }
        
        target_day = None
        for keyword, day_offset in time_keywords.items():
            if keyword in query_lower:
                target_day = day_offset
                break
                
        # Extract weather type
        weather_types = {
            'rain': ['rain', 'raining', 'rainy', 'precipitation'],
            'snow': ['snow', 'snowing', 'snowy'],
            'sunny': ['sunny', 'clear', 'sun'],
            'cloudy': ['cloudy', 'clouds', 'overcast'],
            'windy': ['windy', 'wind'],
            'hot': ['hot', 'warm', 'temperature'],
            'cold': ['cold', 'cool', 'freezing']
        }
        
        weather_type = None
        for weather, keywords in weather_types.items():
            if any(keyword in query_lower for keyword in keywords):
                weather_type = weather
                break
                
        return {
            'location': location,
            'target_day': target_day,
            'weather_type': weather_type,
            'original_query': query
        }
        
    def generate_friendly_response(self, query_info: Dict, weather_data: Dict) -> str:
        """
        Generate a friendly weather response based on parsed query and weather data.
        Uses AI model if available, otherwise falls back to rule-based response.
        
        Args:
            query_info: Parsed query information
            weather_data: Weather data from NWS API
            
        Returns:
            Friendly weather response string
        """
        if self.use_ai_model and self.ai_service:
            # Use AI model for response generation
            original_query = query_info.get('original_query', '')
            ai_extracted = query_info.get('ai_extracted', {})
            
            return self.ai_service.generate_friendly_response(
                original_query, 
                weather_data, 
                ai_extracted
            )
        else:
            # Fallback to rule-based response generation
            return self._rule_based_response(query_info, weather_data)
    
    def _rule_based_response(self, query_info: Dict, weather_data: Dict) -> str:
        """Rule-based response generation as fallback."""
        location = query_info.get('location', 'the area')
        weather_type = query_info.get('weather_type')
        target_day = query_info.get('target_day')
        
        if not weather_data:
            return f"I'm sorry, I couldn't get weather information for {location} right now. Please try again later!"
            
        # Extract relevant weather information
        periods = weather_data.get('properties', {}).get('periods', [])
        
        if not periods:
            return f"I couldn't find detailed weather information for {location}."
            
        # Find the relevant period based on target day
        relevant_period = None
        if target_day is not None:
            # Find period for the target day
            for period in periods:
                period_name = period.get('name', '').lower()
                # Convert target_day to day name for comparison
                day_names = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
                if target_day < len(day_names):
                    target_day_name = day_names[target_day]
                    if target_day_name in period_name:
                        relevant_period = period
                        break
        else:
            # Use first period (current/today)
            relevant_period = periods[0]
            
        if not relevant_period:
            return f"I couldn't find weather information for the specific time you mentioned in {location}."
            
        # Generate response
        temperature = relevant_period.get('temperature')
        temp_unit = relevant_period.get('temperatureUnit', 'F')
        short_forecast = relevant_period.get('shortForecast', '')
        detailed_forecast = relevant_period.get('detailedForecast', '')
        
        response_parts = []
        
        # Check if user asked about specific weather condition
        if weather_type:
            if weather_type == 'rain':
                if any(word in short_forecast.lower() for word in ['rain', 'shower', 'precipitation']):
                    response_parts.append(f"Yes, there's a chance of rain in {location}!")
                else:
                    response_parts.append(f"No, it doesn't look like it will rain in {location}.")
            elif weather_type == 'snow':
                if any(word in short_forecast.lower() for word in ['snow', 'winter']):
                    response_parts.append(f"Yes, there's a chance of snow in {location}!")
                else:
                    response_parts.append(f"No, it doesn't look like it will snow in {location}.")
            else:
                response_parts.append(f"Here's the weather for {location}:")
        else:
            response_parts.append(f"Here's the weather for {location}:")
            
        # Add temperature and forecast
        if temperature:
            response_parts.append(f"Temperature will be around {temperature}°{temp_unit}.")
            
        if short_forecast:
            response_parts.append(f"{short_forecast}")
            
        return " ".join(response_parts)
        
    def get_weather_response(self, query: str) -> str:
        """
        Main method to get weather response for a user query.
        
        Args:
            query: User's weather query
            
        Returns:
            Friendly weather response
        """
        # Parse the query
        query_info = self.parse_weather_query(query)
        location = query_info.get('location')
        
        if not location:
            return "I couldn't understand the location in your query. Please try asking about a specific city or area."
            
        # Geocode the location
        coords = self.geocode_location(location)
        if not coords:
            return f"I couldn't find weather information for {location}. Please check the location name and try again."
            
        # Get weather data
        weather_data = self.get_forecast(coords[0], coords[1])
        
        # Generate friendly response
        return self.generate_friendly_response(query_info, weather_data) 