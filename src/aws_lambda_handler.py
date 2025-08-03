"""
AWS Lambda handler for weather processing.
"""

import json
import logging
from typing import Dict, Any
from weather_service import WeatherService

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize weather service
weather_service = WeatherService()


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    AWS Lambda handler for processing weather queries.
    
    Args:
        event: Lambda event containing weather query
        context: Lambda context
        
    Returns:
        Dictionary containing weather response
    """
    try:
        logger.info(f"Received event: {json.dumps(event)}")
        
        # Extract query from event
        if 'body' in event:
            # API Gateway event
            body = json.loads(event['body'])
            query = body.get('query', '')
            user_id = body.get('user_id')
            session_id = body.get('session_id')
        else:
            # Direct Lambda invocation
            query = event.get('query', '')
            user_id = event.get('user_id')
            session_id = event.get('session_id')
            
        if not query:
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': 'Missing query parameter',
                    'message': 'Please provide a weather query'
                })
            }
            
        # Get weather response
        response_text = weather_service.get_weather_response(query)
        
        # Prepare response
        response_body = {
            'response': response_text,
            'query': query,
            'user_id': user_id,
            'session_id': session_id,
            'timestamp': '2024-01-01T00:00:00Z'  # In production, use actual timestamp
        }
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'POST, OPTIONS'
            },
            'body': json.dumps(response_body)
        }
        
    except Exception as e:
        logger.error(f"Error processing weather query: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': 'Internal server error',
                'message': f'Error processing weather query: {str(e)}'
            })
        }


def health_check(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Health check Lambda handler.
    
    Args:
        event: Lambda event
        context: Lambda context
        
    Returns:
        Health status response
    """
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps({
            'status': 'healthy',
            'service': 'Weather Chat AI Lambda',
            'version': '1.0.0'
        })
    } 