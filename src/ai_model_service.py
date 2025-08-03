"""
AI Model Service for enhanced weather query processing and response generation using AWS Bedrock.
"""

import os
import json
import logging
from typing import Dict, Optional, Any
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


class AIModelService:
    """AI model service for weather query processing and response generation using AWS Bedrock."""
    
    def __init__(self, model_id: str = "anthropic.claude-3-sonnet-20240229-v1:0"):
        self.model_id = model_id
        self.bedrock_client = None
        self._initialize_bedrock_client()
        
    def _initialize_bedrock_client(self):
        """Initialize the Bedrock client."""
        try:
            # Try to get AWS credentials from environment or IAM role
            self.bedrock_client = boto3.client(
                service_name='bedrock-runtime',
                region_name=os.getenv('AWS_DEFAULT_REGION', 'us-east-1')
            )
            logger.info(f"Bedrock client initialized with model: {self.model_id}")
        except NoCredentialsError:
            logger.error("AWS credentials not found. Please configure AWS credentials.")
            self.bedrock_client = None
        except Exception as e:
            logger.error(f"Failed to initialize Bedrock client: {e}")
            self.bedrock_client = None
    
    def _invoke_bedrock_model(self, prompt: str, system_prompt: str = None) -> Optional[str]:
        """
        Invoke Bedrock model with the given prompt.
        
        Args:
            prompt: User prompt
            system_prompt: System prompt (if supported by model)
            
        Returns:
            Model response or None if failed
        """
        if not self.bedrock_client:
            logger.error("Bedrock client not initialized")
            return None
            
        try:
            # Prepare the request based on model type
            if "claude" in self.model_id.lower():
                # Claude models
                messages = []
                if system_prompt:
                    messages.append({"role": "user", "content": f"<system>{system_prompt}</system>"})
                messages.append({"role": "user", "content": prompt})
                
                request_body = {
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": 1000,
                    "messages": messages
                }
                
            elif "llama" in self.model_id.lower():
                # Llama models
                full_prompt = prompt
                if system_prompt:
                    full_prompt = f"{system_prompt}\n\n{prompt}"
                
                request_body = {
                    "prompt": full_prompt,
                    "max_tokens": 1000,
                    "temperature": 0.1
                }
                
            elif "titan" in self.model_id.lower():
                # Titan models
                full_prompt = prompt
                if system_prompt:
                    full_prompt = f"{system_prompt}\n\n{prompt}"
                
                request_body = {
                    "inputText": full_prompt,
                    "textGenerationConfig": {
                        "maxTokenCount": 1000,
                        "temperature": 0.1
                    }
                }
                
            else:
                # Default to Claude format
                messages = []
                if system_prompt:
                    messages.append({"role": "user", "content": f"<system>{system_prompt}</system>"})
                messages.append({"role": "user", "content": prompt})
                
                request_body = {
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": 1000,
                    "messages": messages
                }
            
            response = self.bedrock_client.invoke_model(
                modelId=self.model_id,
                body=json.dumps(request_body)
            )
            
            response_body = json.loads(response['body'].read())
            
            # Extract response based on model type
            if "claude" in self.model_id.lower():
                return response_body['content'][0]['text']
            elif "llama" in self.model_id.lower():
                return response_body['generation']
            elif "titan" in self.model_id.lower():
                return response_body['results'][0]['outputText']
            else:
                # Default to Claude format
                return response_body['content'][0]['text']
                
        except ClientError as e:
            logger.error(f"Bedrock API error: {e}")
            return None
        except Exception as e:
            logger.error(f"Error invoking Bedrock model: {e}")
            return None
    
    def extract_weather_info(self, query: str) -> Dict[str, Any]:
        """
        Extract location, time, and weather intent from natural language query.
        
        Args:
            query: User's weather query
            
        Returns:
            Dictionary with extracted information
        """
        try:
            system_prompt = """
            You are a weather query parser. Extract the following information from weather queries:
            - location: The city, state, or area mentioned
            - time_reference: When the user is asking about (today, tomorrow, Sunday, etc.)
            - weather_intent: What weather condition they're asking about (rain, snow, temperature, etc.)
            - is_question: Whether they're asking a yes/no question or requesting general info
            
            Return the information as a JSON object with these exact keys.
            """
            
            user_prompt = f"Parse this weather query: {query}"
            
            response = self._invoke_bedrock_model(user_prompt, system_prompt)
            
            if response:
                try:
                    # Try to extract JSON from the response
                    if "{" in response and "}" in response:
                        start = response.find("{")
                        end = response.rfind("}") + 1
                        json_str = response[start:end]
                        result = json.loads(json_str)
                    else:
                        # Fallback parsing
                        result = self._fallback_parsing(query)
                        
                    logger.info(f"AI extracted info: {result}")
                    return result
                    
                except json.JSONDecodeError:
                    logger.warning(f"Failed to parse AI response: {response}")
                    return self._fallback_parsing(query)
            else:
                return self._fallback_parsing(query)
                
        except Exception as e:
            logger.error(f"Error in AI extraction: {e}")
            return self._fallback_parsing(query)
    
    def _fallback_parsing(self, query: str) -> Dict[str, Any]:
        """Fallback to rule-based parsing if AI fails."""
        query_lower = query.lower()
        
        # Simple location extraction
        location = None
        if " in " in query_lower:
            parts = query_lower.split(" in ")
            if len(parts) > 1:
                location_part = parts[1].split()[0]
                location = location_part.strip()
        
        # Time reference
        time_ref = None
        time_keywords = ["today", "tomorrow", "sunday", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday"]
        for keyword in time_keywords:
            if keyword in query_lower:
                time_ref = keyword
                break
        
        # Weather intent
        weather_intent = None
        weather_keywords = {
            "rain": ["rain", "raining", "rainy"],
            "snow": ["snow", "snowing", "snowy"],
            "temperature": ["temperature", "temp", "hot", "cold", "warm"],
            "sunny": ["sunny", "sun", "clear"],
            "cloudy": ["cloudy", "clouds", "overcast"]
        }
        
        for intent, keywords in weather_keywords.items():
            if any(keyword in query_lower for keyword in keywords):
                weather_intent = intent
                break
        
        return {
            "location": location,
            "time_reference": time_ref,
            "weather_intent": weather_intent,
            "is_question": "?" in query or any(word in query_lower for word in ["will", "is", "going", "be"])
        }
    
    def generate_friendly_response(self, query: str, weather_data: Dict[str, Any], 
                                 extracted_info: Dict[str, Any]) -> str:
        """
        Generate a friendly, contextual weather response using AI.
        
        Args:
            query: Original user query
            weather_data: Weather data from NWS API
            extracted_info: Information extracted from the query
            
        Returns:
            Friendly weather response
        """
        try:
            # Prepare weather data for the model
            weather_summary = self._prepare_weather_summary(weather_data)
            
            system_prompt = """
            You are a friendly weather assistant. Generate a natural, conversational response to weather queries.
            
            Guidelines:
            - Be conversational and friendly
            - Answer the specific question asked
            - Include relevant weather details (temperature, conditions)
            - If asked about specific weather (rain, snow), give a clear yes/no answer
            - Keep responses concise but informative
            - Use the weather data provided to give accurate information
            """
            
            user_prompt = f"""
            User Query: "{query}"
            
            Extracted Information:
            - Location: {extracted_info.get('location', 'unknown')}
            - Time: {extracted_info.get('time_reference', 'current')}
            - Weather Intent: {extracted_info.get('weather_intent', 'general')}
            - Is Question: {extracted_info.get('is_question', False)}
            
            Weather Data: {weather_summary}
            
            Generate a friendly, conversational response that directly answers the user's question.
            """
            
            response = self._invoke_bedrock_model(user_prompt, system_prompt)
            
            if response:
                return response.strip()
            else:
                return self._generate_fallback_response(query, weather_data, extracted_info)
            
        except Exception as e:
            logger.error(f"Error generating AI response: {e}")
            return self._generate_fallback_response(query, weather_data, extracted_info)
    
    def _prepare_weather_summary(self, weather_data: Dict[str, Any]) -> str:
        """Prepare weather data summary for the AI model."""
        if not weather_data or 'properties' not in weather_data:
            return "No weather data available"
        
        periods = weather_data.get('properties', {}).get('periods', [])
        if not periods:
            return "No weather forecast available"
        
        # Get the most relevant period (first one for now)
        period = periods[0]
        
        summary = f"""
        Location: {weather_data.get('properties', {}).get('location', 'Unknown')}
        Period: {period.get('name', 'Unknown')}
        Temperature: {period.get('temperature', 'Unknown')}°{period.get('temperatureUnit', 'F')}
        Short Forecast: {period.get('shortForecast', 'Unknown')}
        Detailed Forecast: {period.get('detailedForecast', 'Unknown')}
        """
        
        return summary
    
    def _generate_fallback_response(self, query: str, weather_data: Dict[str, Any], 
                                  extracted_info: Dict[str, Any]) -> str:
        """Generate a fallback response if AI fails."""
        location = extracted_info.get('location', 'the area')
        weather_intent = extracted_info.get('weather_intent')
        
        if not weather_data or 'properties' not in weather_data:
            return f"I'm sorry, I couldn't get weather information for {location} right now. Please try again later!"
        
        periods = weather_data.get('properties', {}).get('periods', [])
        if not periods:
            return f"I couldn't find detailed weather information for {location}."
        
        period = periods[0]
        temperature = period.get('temperature')
        temp_unit = period.get('temperatureUnit', 'F')
        short_forecast = period.get('shortForecast', '')
        
        # Generate response based on intent
        if weather_intent == 'rain':
            if any(word in short_forecast.lower() for word in ['rain', 'shower', 'precipitation']):
                return f"Yes, there's a chance of rain in {location}! Temperature will be around {temperature}°{temp_unit}. {short_forecast}"
            else:
                return f"No, it doesn't look like it will rain in {location}. Temperature will be around {temperature}°{temp_unit}. {short_forecast}"
        elif weather_intent == 'snow':
            if any(word in short_forecast.lower() for word in ['snow', 'winter']):
                return f"Yes, there's a chance of snow in {location}! Temperature will be around {temperature}°{temp_unit}. {short_forecast}"
            else:
                return f"No, it doesn't look like it will snow in {location}. Temperature will be around {temperature}°{temp_unit}. {short_forecast}"
        else:
            return f"Here's the weather for {location}: Temperature will be around {temperature}°{temp_unit}. {short_forecast}" 