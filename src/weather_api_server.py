"""
Weather Chat AI - FastAPI REST Server

A FastAPI-based REST server that provides weather information through natural language queries.
This server integrates with AWS Bedrock for AI-powered query understanding and response generation.
"""

import json
import logging
import os
from typing import Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from weather_service import WeatherService
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="Weather Chat AI API Server", version="1.0.0")

# Initialize weather service with AI model support
use_ai_model = os.getenv("USE_AI_MODEL", "true").lower() == "true"
bedrock_model_id = os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-3-sonnet-20240229-v1:0")
weather_service = WeatherService(use_ai_model=use_ai_model, bedrock_model_id=bedrock_model_id)

logger.info(f"Weather service initialized with AI model: {use_ai_model}")
if use_ai_model:
    logger.info(f"Using Bedrock model: {bedrock_model_id}")


class WeatherQuery(BaseModel):
    """Pydantic model for weather query requests."""
    query: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None


class WeatherResponse(BaseModel):
    """Pydantic model for weather responses."""
    response: str
    query: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    timestamp: str
    ai_enhanced: bool = False


class HealthResponse(BaseModel):
    """Pydantic model for health check responses."""
    status: str
    service: str
    version: str
    ai_model_enabled: bool


@app.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint for health check."""
    return HealthResponse(
        status="healthy",
        service="Weather Chat AI API Server",
        version="1.0.0",
        ai_model_enabled=use_ai_model
    )


@app.post("/weather", response_model=WeatherResponse)
async def get_weather(query: WeatherQuery):
    """
    Main endpoint for weather queries.
    
    Args:
        query: WeatherQuery object containing user's weather question
        
    Returns:
        WeatherResponse with friendly weather information
    """
    try:
        logger.info(f"Received weather query: {query.query}")
        
        # Get weather response from service
        response_text = weather_service.get_weather_response(query.query)
        
        # Check if AI model was used
        ai_enhanced = weather_service.use_ai_model and weather_service.ai_service is not None
        
        # Create response object
        response = WeatherResponse(
            response=response_text,
            query=query.query,
            user_id=query.user_id,
            session_id=query.session_id,
            timestamp=json.dumps({"timestamp": "2024-01-01T00:00:00Z"}),  # In production, use actual timestamp
            ai_enhanced=ai_enhanced
        )
        
        logger.info(f"Generated response (AI enhanced: {ai_enhanced}): {response_text}")
        return response
        
    except Exception as e:
        logger.error(f"Error processing weather query: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing weather query: {str(e)}")


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        service="Weather Chat AI API Server",
        version="1.0.0",
        ai_model_enabled=use_ai_model
    )


@app.get("/capabilities")
async def get_capabilities():
    """Return API server capabilities."""
    return {
        "name": "Weather Chat AI",
        "version": "1.0.0",
        "description": "A friendly weather assistant that provides weather information through natural language queries",
        "ai_model_enabled": use_ai_model,
        "capabilities": {
            "weather_queries": {
                "description": "Process natural language weather queries",
                "examples": [
                    "Will it rain in Denver on Sunday?",
                    "What's the temperature in New York today?",
                    "Is it going to snow in Seattle this weekend?"
                ]
            },
            "ai_enhancement": {
                "description": "AI-powered query understanding and response generation",
                "enabled": use_ai_model,
                "features": [
                    "Natural language location extraction",
                    "Contextual response generation",
                    "Intent recognition",
                    "Conversational responses"
                ]
            }
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 