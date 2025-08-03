#!/usr/bin/env python3
"""
Test script for AI-enhanced weather service.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from weather_service import WeatherService
import json


def test_ai_weather_queries():
    """Test various weather queries with AI enhancement."""
    
    # Test with AI model enabled
    print("🤖 Testing AI-Enhanced Weather Service")
    print("=" * 50)
    
    weather_service_ai = WeatherService(use_ai_model=True)
    
    test_queries = [
        "Will it rain in Denver on Sunday?",
        "What's the temperature in New York today?",
        "Is it going to snow in Seattle this weekend?",
        "How's the weather in Miami?",
        "Will it be sunny in Los Angeles tomorrow?",
        "Should I bring an umbrella to Chicago today?",
        "What's the forecast for Boston this week?",
        "Is it going to be cold in Phoenix tomorrow?"
    ]
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        try:
            response = weather_service_ai.get_weather_response(query)
            print(f"🤖 AI Response: {response}")
        except Exception as e:
            print(f"Error: {e}")
        print("-" * 50)
    
    # Test with AI model disabled (fallback)
    print("\n\n🔧 Testing Rule-Based Weather Service (Fallback)")
    print("=" * 50)
    
    weather_service_rule = WeatherService(use_ai_model=False)
    
    for query in test_queries[:3]:  # Test first 3 queries
        print(f"\nQuery: {query}")
        try:
            response = weather_service_rule.get_weather_response(query)
            print(f"🔧 Rule Response: {response}")
        except Exception as e:
            print(f"Error: {e}")
        print("-" * 50)


def test_ai_extraction():
    """Test AI model's query extraction capabilities."""
    print("\n\nTesting AI Query Extraction")
    print("=" * 50)
    
    weather_service = WeatherService(use_ai_model=True)
    
    test_queries = [
        "Will it rain in Denver on Sunday?",
        "What's the temperature in New York today?",
        "Is it going to snow in Seattle this weekend?",
        "Should I bring an umbrella to Chicago today?",
        "What's the forecast for Boston this week?"
    ]
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        try:
            parsed = weather_service.parse_weather_query(query)
            print(f"🔍 Parsed Info: {json.dumps(parsed, indent=2)}")
        except Exception as e:
            print(f"Error: {e}")
        print("-" * 30)


if __name__ == "__main__":
    print("AI-Enhanced Weather Chat AI Testing")
    print("=" * 60)
    
    # Check if AWS credentials are configured
    try:
        import boto3
        boto3.client('sts').get_caller_identity()
        print("AWS credentials configured")
    except Exception:
        print("   Warning: AWS credentials not configured. AI features will fall back to rule-based parsing.")
        print("   Configure AWS credentials to enable Bedrock AI features.")
        print()
    
    # Test AI-enhanced queries
    test_ai_weather_queries()
    
    # Test AI extraction
    test_ai_extraction()
    
    print("\nTesting complete!") 