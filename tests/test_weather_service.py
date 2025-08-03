"""
Unit tests for weather service module.
"""

import sys
import os
from unittest.mock import Mock, patch

# Add the src directory to the Python path more reliably
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, '..', 'src')
sys.path.insert(0, src_dir)

from weather_service import WeatherService


class TestWeatherService:
    """Test cases for WeatherService class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        # Disable AI model for testing to use rule-based parsing
        self.weather_service = WeatherService(use_ai_model=False)
        
    def test_parse_weather_query_location(self):
        """Test location extraction from weather queries."""
        query = "Will it rain in Denver on Sunday?"
        result = self.weather_service.parse_weather_query(query)
        assert result['location'] == 'denver'
        assert result['weather_type'] == 'rain'
        
    def test_parse_weather_query_time(self):
        """Test time extraction from weather queries."""
        query = "What's the temperature in New York today?"
        result = self.weather_service.parse_weather_query(query)
        # Rule-based parsing extracts "new york" correctly
        assert result['location'] == 'new york'
        assert result['target_day'] == 0  # today
        
    def test_parse_weather_query_no_location(self):
        """Test query without location."""
        query = "What's the weather like?"
        result = self.weather_service.parse_weather_query(query)
        # Should handle queries without location gracefully
        assert result is not None
        assert 'location' in result
        
    @patch('weather_service.requests.get')
    def test_get_forecast_success(self, mock_get):
        """Test successful forecast retrieval."""
        # Mock the points API response
        mock_points_response = Mock()
        mock_points_response.json.return_value = {
            'properties': {
                'forecast': 'https://api.weather.gov/gridpoints/BOU/80,80/forecast'
            }
        }
        mock_points_response.raise_for_status.return_value = None
        
        # Mock the forecast API response
        mock_forecast_response = Mock()
        mock_forecast_response.json.return_value = {
            'properties': {
                'periods': [
                    {
                        'name': 'Today',
                        'temperature': 75,
                        'temperatureUnit': 'F',
                        'shortForecast': 'Sunny',
                        'detailedForecast': 'Sunny with clear skies'
                    }
                ]
            }
        }
        mock_forecast_response.raise_for_status.return_value = None
        
        # Set up mock to return different responses for different URLs
        def mock_get_side_effect(url, **kwargs):
            if 'points' in url:
                return mock_points_response
            else:
                return mock_forecast_response
        
        mock_get.side_effect = mock_get_side_effect
        
        result = self.weather_service.get_forecast(39.7392, -104.9903)
        assert result is not None
        assert 'properties' in result
        
    @patch('weather_service.requests.get')
    def test_get_forecast_failure(self, mock_get):
        """Test forecast retrieval failure."""
        import requests
        mock_get.side_effect = requests.RequestException("API Error")
        
        # The function should return None when an exception occurs
        result = self.weather_service.get_forecast(39.7392, -104.9903)
        assert result is None
        
    def test_generate_friendly_response_rain(self):
        """Test friendly response generation for rain query."""
        query_info = {
            'location': 'Denver',
            'weather_type': 'rain',
            'target_day': 6  # Sunday
        }
        
        weather_data = {
            'properties': {
                'periods': [
                    {
                        'name': 'Sunday',
                        'temperature': 45,
                        'temperatureUnit': 'F',
                        'shortForecast': 'Rain showers likely',
                        'detailedForecast': 'Rain showers with cloudy conditions'
                    }
                ]
            }
        }
        
        response = self.weather_service.generate_friendly_response(query_info, weather_data)
        # Check for rain-related content in the response
        assert "rain" in response.lower() or "shower" in response.lower()
        assert "Denver" in response or "45" in response
        
    def test_generate_friendly_response_no_rain(self):
        """Test friendly response generation for no rain."""
        query_info = {
            'location': 'Denver',
            'weather_type': 'rain',
            'target_day': 6
        }
        
        weather_data = {
            'properties': {
                'periods': [
                    {
                        'name': 'Sunday',
                        'temperature': 75,
                        'temperatureUnit': 'F',
                        'shortForecast': 'Sunny',
                        'detailedForecast': 'Clear and sunny'
                    }
                ]
            }
        }
        
        response = self.weather_service.generate_friendly_response(query_info, weather_data)
        # Check for sunny content in the response
        assert "sunny" in response.lower() or "clear" in response.lower()
        assert "75" in response or "Denver" in response 