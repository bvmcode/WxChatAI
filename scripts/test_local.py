#!/usr/bin/env python3
"""
Local testing script for Weather Chat AI.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from weather_service import WeatherService
import json

def test_query_parsing():
    """Test the query parsing functionality."""
    print("Testing query parsing...")
    
    weather_service = WeatherService()
    
    test_queries = [
        "Will it rain in Denver on Sunday?",
        "What's the temperature in New York today?",
        "Is it going to snow in Seattle this weekend?"
    ]
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        parsed = weather_service.parse_weather_query(query)
        print(f"Parsed: {json.dumps(parsed, indent=2)}")
        print("-" * 30)

def test_weather_responses():
    """Test the weather response generation."""
    print("\nTesting Weather Chat AI locally...")
    
    weather_service = WeatherService()
    
    test_queries = [
        "Will it rain in Denver on Sunday?",
        "What's the temperature in New York today?",
        "Is it going to snow in Seattle this weekend?",
        "How's the weather in Miami?",
        "Will it be sunny in Los Angeles tomorrow?"
    ]
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        try:
            response = weather_service.get_weather_response(query)
            print(f"Response: {response}")
        except Exception as e:
            print(f"Error: {e}")
        print("-" * 50)

if __name__ == "__main__":
    print("Weather Chat AI Local Testing")
    print("=" * 50)
    
    test_query_parsing()
    test_weather_responses()
    
    print("\nTesting complete!") 