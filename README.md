# Weather Chat AI

A friendly weather assistant that uses **AI-powered natural language processing** to provide weather information through a **FastAPI REST API**.

## **AI Features**

- ** AWS Bedrock Integration**: Enhanced query understanding and response generation using Claude models
- ** Intelligent Location Extraction**: AI-powered location parsing from natural language
- ** Contextual Responses**: Conversational, friendly weather responses
- ** Graceful Fallback**: Falls back to rule-based parsing if AI is unavailable

## Architecture

- **FastAPI Server**: Python-based REST API for weather queries
- **NWS API**: National Weather Service API for real-time weather data
- **AWS Bedrock**: AI model service for enhanced query understanding and response generation
- **AWS Resources**: Lambda, API Gateway, DynamoDB, CloudWatch, S3
- **Infrastructure**: Terraform for infrastructure as code

## Features

- **AI-Enhanced Natural Language Processing**: Understands complex weather queries
- **Friendly, Conversational Responses**: Contextual weather information
- **Real-time Weather Data**: From NWS API (free, no API key required)
- **Scalable Serverless Architecture**: AWS Lambda and API Gateway
- **Conversation History Tracking**: DynamoDB storage
- **Graceful Fallback**: Works without AI model if needed

## Setup

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Set up AWS credentials** (required for Bedrock):
```bash
aws configure
# Or set environment variables:
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_DEFAULT_REGION=us-east-1
```

3. **Configure Bedrock model** (optional):
```bash
cp env.example .env
# Edit .env to customize Bedrock model
BEDROCK_MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0
```

4. **Deploy infrastructure with Terraform:**
```bash
./terraform/deploy.sh
```

5. **Run the API server locally:**
```bash
python src/weather_api_server.py
```

## Usage

### **AI-Enhanced Queries**
The app now understands complex, natural language queries:

- "Will it rain in Denver on Sunday?"
- "What's the temperature in New York today?"
- "Should I bring an umbrella to Chicago today?"
- "Is it going to be cold in Phoenix tomorrow?"
- "What's the forecast for Boston this week?"

### **Testing**

**Test AI-enhanced features:**
```bash
python scripts/test_ai_weather.py
```

**Test basic functionality:**
```bash
python scripts/test_local.py
```

**Test the API:**
```bash
curl -X POST "http://localhost:8000/weather" \
  -H "Content-Type: application/json" \
  -d '{"query": "Will it rain in Denver on Sunday?"}'
```

## Deployment Options

### **Terraform (Recommended)**
```bash
cd terraform
terraform init
terraform plan
terraform apply
```

### **Local Development**
```bash
# Test AI features
python scripts/test_ai_weather.py

# Run API server
python src/weather_api_server.py
```

## AI Model Configuration

### **Environment Variables**
```bash
# Enable/disable AI model (default: true)
USE_AI_MODEL=true

# Bedrock model ID (default: Claude 3 Sonnet)
BEDROCK_MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0
```

### **Available Bedrock Models**

| Model | Speed | Cost | Capability | Use Case |
|-------|-------|------|------------|----------|
| `anthropic.claude-3-haiku-20240307-v1:0` | Fast | Low | Good | Quick responses |
| `anthropic.claude-3-sonnet-20240229-v1:0` | Medium | Medium | Excellent | **Recommended** |
| `anthropic.claude-3-opus-20240229-v1:0` | Slow | High | Best | Complex queries |
| `meta.llama-2-70b-chat-v1` | Medium | Low | Good | Alternative option |
| `amazon.titan-text-express-v1` | Fast | Low | Good | AWS native |

### **AI vs Rule-Based Comparison**

| Feature | AI-Enhanced | Rule-Based |
|---------|-------------|------------|
| **Query Understanding** | Natural language processing | Pattern matching |
| **Location Extraction** | Context-aware parsing | Regex patterns |
| **Response Generation** | Conversational, contextual | Template-based |
| **Complex Queries** | Excellent | Good |
| **Cost** | AWS Bedrock pricing | Free |
| **Latency** | ~1-3 seconds | <100ms |
| **Fallback** | Automatic to rule-based | Always available |

## Example Responses

### **AI-Enhanced Response:**
```
Query: "Should I bring an umbrella to Chicago today?"
Response: "Based on the current forecast for Chicago, you should definitely bring an umbrella! 
         There's a 70% chance of rain with scattered showers throughout the day. 
         The temperature will be around 45°F, so you'll want to stay dry and warm."
```

### **Rule-Based Response:**
```
Query: "Will it rain in Denver on Sunday?"
Response: "No, it doesn't look like it will rain in denver. 
         Temperature will be around 88°F. Sunny"
```

## Architecture Flow

```
User Query → AWS Bedrock → Location Extraction → NWS API → AI Response Generation → Friendly Response
     ↓
Rule-Based Fallback → Pattern Matching → Weather Data → Template Response
```

The AI model enhances both the **input processing** (understanding what the user wants) and the **output generation** (providing friendly, contextual responses), while maintaining a robust fallback system for reliability. 