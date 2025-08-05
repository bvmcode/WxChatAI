# Weather Chat AI - Complete Guide

## 🏗️ **Infrastructure Overview**

### **Architecture Diagram**

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Client App    │───▶│  API Gateway    │───▶│  Lambda Function│
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                       │
                                ▼                       ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │   DynamoDB      │    │   AWS Bedrock   │
                       │ (Conversations) │    │   (Claude AI)   │
                       └─────────────────┘    └─────────────────┘
                                │                       │
                                ▼                       ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │   S3 Bucket     │    │   NWS API       │
                       │ (Weather Cache) │    │ (Weather Data)  │
                       └─────────────────┘    └─────────────────┘
```

### **AWS Components**

| Component | Purpose | Technology | Configuration |
|-----------|---------|------------|---------------|
| **API Gateway** | REST API endpoint | AWS API Gateway | Lambda proxy integration |
| **Lambda Functions** | Serverless compute | AWS Lambda (Python 3.11) | 512MB RAM, 30s timeout |
| **DynamoDB** | Conversation history | AWS DynamoDB | Pay-per-request, TTL enabled |
| **S3** | Weather data cache | AWS S3 | Private, versioning disabled |
| **Bedrock** | AI model service | AWS Bedrock (Claude) | Multiple model support |
| **CloudWatch** | Monitoring & logging | AWS CloudWatch | 7-day retention |
| **IAM** | Security & permissions | AWS IAM | Least privilege access |

## 🚀 **Deployment Options**

### **Option 1: AWS Deployment (Production)**

#### **Prerequisites**
```bash
# 1. Install AWS CLI
curl "https://awscli.amazonaws.com/AWSCLIV2.pkg" -o "AWSCLIV2.pkg"
sudo installer -pkg AWSCLIV2.pkg -target /

# 2. Install Terraform
brew install terraform  # macOS
# OR
curl -fsSL https://apt.releases.hashicorp.com/gpg | sudo apt-key add -
sudo apt-add-repository "deb [arch=amd64] https://apt.releases.hashicorp.com $(lsb_release -cs) main"
sudo apt-get update && sudo apt-get install terraform

# 3. Configure AWS credentials
aws configure
# Enter your AWS Access Key ID, Secret Access Key, Region, and Output format
```

#### **Quick Deployment**
```bash
# 1. Clone and setup
git clone <repository>
cd wxchatai
pip install -r requirements.txt

# 2. Deploy infrastructure
./terraform/deploy.sh

# 3. Get API URL
cd terraform
terraform output api_gateway_url
```

#### **Manual Deployment**
```bash
# 1. Navigate to terraform directory
cd terraform

# 2. Initialize Terraform
terraform init

# 3. Plan deployment
terraform plan

# 4. Deploy infrastructure
terraform apply -auto-approve

# 5. Get outputs
terraform output
```

### **Option 2: Local Development**

#### **Setup Local Environment**
```bash
# 1. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment (optional)
cp env.example .env
# Edit .env to customize settings
```

#### **Run Locally**
```bash
# Start the API server
python src/weather_api_server.py

# Test the API
curl -X POST "http://localhost:8001/weather" \
  -H "Content-Type: application/json" \
  -d '{"query": "Will it rain in Denver on Sunday?"}'
```

## 🔧 **Configuration**

### **Environment Variables**

| Variable | Default | Purpose | Required |
|----------|---------|---------|----------|
| `AWS_DEFAULT_REGION` | `us-east-1` | AWS region | Yes (for AWS) |
| `BEDROCK_MODEL_ID` | `anthropic.claude-3-sonnet-20240229-v1:0` | AI model | No |
| `USE_AI_MODEL` | `true` | Enable/disable AI | No |
| `LOG_LEVEL` | `INFO` | Logging level | No |

### **AWS Bedrock Models**

| Model | Speed | Cost | Capability | Use Case |
|-------|-------|------|------------|----------|
| `anthropic.claude-3-haiku-20240307-v1:0` | Fast | Low | Good | Quick responses |
| `anthropic.claude-3-sonnet-20240229-v1:0` | Medium | Medium | Excellent | **Recommended** |
| `anthropic.claude-3-opus-20240229-v1:0` | Slow | High | Best | Complex queries |
| `meta.llama-2-70b-chat-v1` | Medium | Low | Good | Alternative option |
| `amazon.titan-text-express-v1` | Fast | Low | Good | AWS native |

## 🧪 **Testing**

### **Local Testing**
```bash
# Test basic functionality
python scripts/test_local.py

# Test AI features
python scripts/test_ai_weather.py

# Run unit tests
python -m pytest tests/ -v

# Test API endpoints
curl -X GET "http://localhost:8001/health"
curl -X GET "http://localhost:8001/capabilities"
```

### **AWS Testing**
```bash
# Get API URL
cd terraform
API_URL=$(terraform output -raw api_gateway_url)

# Test health check
curl -X GET "$API_URL/health"

# Test weather query
curl -X POST "$API_URL/weather" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Will it rain in Denver on Sunday?",
    "user_id": "test-user",
    "session_id": "test-session"
  }'
```

## 📊 **API Reference**

### **Endpoints**

#### **POST /weather**
Process weather queries with AI enhancement.

**Request:**
```json
{
  "query": "Will it rain in Denver on Sunday?",
  "user_id": "user123",
  "session_id": "session456"
}
```

**Response:**
```json
{
  "response": "Yes, there's a chance of rain in Denver! Temperature will be around 89°F.",
  "query": "Will it rain in Denver on Sunday?",
  "user_id": "user123",
  "session_id": "session456",
  "timestamp": "2024-01-01T00:00:00Z",
  "ai_enhanced": true
}
```

#### **GET /health**
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "service": "Weather Chat AI API Server",
  "version": "1.0.0",
  "ai_model_enabled": true
}
```

#### **GET /capabilities**
Service capabilities and features.

**Response:**
```json
{
  "name": "Weather Chat AI",
  "version": "1.0.0",
  "description": "A friendly weather assistant that provides weather information through natural language queries",
  "ai_model_enabled": true,
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
      "enabled": true,
      "features": [
        "Natural language location extraction",
        "Contextual response generation",
        "Intent recognition",
        "Conversational responses"
      ]
    }
  }
}
```

## 🔄 **How It Works**

### **Request Flow**

1. **Client Request** → API Gateway
   ```
   POST /weather
   {
     "query": "Will it rain in Denver on Sunday?",
     "user_id": "user123",
     "session_id": "session456"
   }
   ```

2. **API Gateway** → Lambda Function
   - Routes request to weather Lambda
   - Handles CORS and authentication

3. **Lambda Processing**:
   - **AI Model Service**: Extracts location, time, intent using AWS Bedrock
   - **Weather Service**: Fetches data from NWS API
   - **Response Generation**: Creates friendly response using AI
   - **Storage**: Saves conversation to DynamoDB

4. **Response** → Client
   ```json
   {
     "response": "Yes, there's a chance of rain in Denver! Temperature will be around 89°F.",
     "query": "Will it rain in Denver on Sunday?",
     "user_id": "user123",
     "session_id": "session456",
     "timestamp": "2024-01-01T00:00:00Z",
     "ai_enhanced": true
   }
   ```

### **AI Model Integration**

1. **Query Processing**:
   - AWS Bedrock (Claude) extracts location, time, intent
   - Falls back to rule-based parsing if AI fails

2. **Response Generation**:
   - AI model creates contextual, friendly responses
   - Uses weather data from NWS API
   - Maintains conversation context

3. **Graceful Fallback**:
   - Automatic fallback to rule-based parsing
   - Works without AWS Bedrock access
   - Maintains functionality in all scenarios

## 💰 **Cost Optimization**

### **AWS Pricing (Estimated)**

| Service | Cost | Optimization |
|---------|------|--------------|
| **Lambda** | $0.20 per 1M requests | Pay only for invocations |
| **API Gateway** | $3.50 per 1M requests | Standard tier |
| **DynamoDB** | $1.25 per 1M requests | Pay-per-request |
| **S3** | $0.023 per GB/month | Lifecycle policies |
| **Bedrock** | $0.003-$0.015 per 1K tokens | Choose appropriate model |
| **CloudWatch** | $0.50 per GB ingested | 7-day retention |

### **Cost Optimization Tips**

1. **Choose appropriate Bedrock model**:
   - Haiku for testing (cheaper)
   - Sonnet for production (balanced)
   - Opus for complex queries (expensive)

2. **Optimize Lambda**:
   - Use appropriate memory (512MB is good)
   - Minimize cold starts
   - Cache weather data

3. **DynamoDB optimization**:
   - Use TTL for automatic cleanup
   - Pay-per-request billing
   - Monitor read/write units

## 🔒 **Security**

### **IAM Permissions**

The Lambda function has minimal required permissions:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "dynamodb:GetItem",
        "dynamodb:PutItem",
        "dynamodb:UpdateItem",
        "dynamodb:DeleteItem",
        "dynamodb:Query",
        "dynamodb:Scan"
      ],
      "Resource": "arn:aws:dynamodb:us-east-1:*:table/weather-chat-ai-conversations"
    },
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject",
        "s3:DeleteObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::weather-chat-ai-weather-data-*",
        "arn:aws:s3:::weather-chat-ai-weather-data-*/*"
      ]
    },
    {
      "Effect": "Allow",
      "Action": ["bedrock:InvokeModel"],
      "Resource": [
        "arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-3-sonnet-20240229-v1:0",
        "arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-3-haiku-20240307-v1:0"
      ]
    }
  ]
}
```

### **Security Features**

- ✅ **HTTPS only** (API Gateway)
- ✅ **Private S3 bucket** (no public access)
- ✅ **Least privilege IAM** (minimal permissions)
- ✅ **CORS enabled** (for web clients)
- ✅ **Input validation** (Pydantic models)
- ✅ **Error handling** (graceful failures)

## 📈 **Monitoring & Logging**

### **CloudWatch Logs**

- **Weather Lambda**: `/aws/lambda/weather-chat-ai-weather-lambda`
- **Health Lambda**: `/aws/lambda/weather-chat-ai-health-lambda`
- **Retention**: 7 days
- **Log levels**: INFO, ERROR, DEBUG

### **Key Metrics**

- **Lambda invocations** and duration
- **API Gateway requests** and latency
- **DynamoDB read/write** units
- **Bedrock model** invocations
- **Error rates** and types

### **Alarms (Recommended)**

1. **High error rate** (>5% for 5 minutes)
2. **High latency** (>10 seconds average)
3. **Lambda failures** (>10 failures in 5 minutes)
4. **API Gateway 5xx errors** (>10 in 5 minutes)

## 🗑️ **Cleanup**

### **Destroy Infrastructure**
```bash
cd terraform
terraform destroy -auto-approve
```

**⚠️ Warning**: This will delete all resources including data!

### **Cleanup Checklist**

- ✅ **Terraform state** deleted
- ✅ **Lambda functions** removed
- ✅ **API Gateway** deleted
- ✅ **DynamoDB table** deleted
- ✅ **S3 bucket** emptied and deleted
- ✅ **CloudWatch logs** deleted
- ✅ **IAM roles** deleted

## 🚀 **Production Deployment**

### **Pre-deployment Checklist**

1. ✅ **AWS credentials** configured
2. ✅ **Bedrock access** requested and approved
3. ✅ **Environment variables** set
4. ✅ **Terraform** installed and configured
5. ✅ **Python dependencies** installed
6. ✅ **Tests** passing locally

### **Deployment Steps**

```bash
# 1. Validate infrastructure
cd terraform
terraform validate

# 2. Plan deployment
terraform plan

# 3. Deploy infrastructure
terraform apply -auto-approve

# 4. Verify deployment
terraform output

# 5. Test endpoints
API_URL=$(terraform output -raw api_gateway_url)
curl -X GET "$API_URL/health"
```

### **Post-deployment Verification**

1. ✅ **Health check** returns 200
2. ✅ **Weather query** returns valid response
3. ✅ **AI model** is working (if enabled)
4. ✅ **Logs** are being generated
5. ✅ **Metrics** are being collected

## 🔧 **Troubleshooting**

### **Common Issues**

#### **1. Bedrock Access Denied**
```
ERROR: Bedrock API error: An error occurred (AccessDeniedException)
```
**Solution**: Request Bedrock access in AWS console

#### **2. Lambda Timeout**
```
ERROR: Lambda function timed out after 30 seconds
```
**Solution**: Increase timeout or optimize code

#### **3. DynamoDB Throttling**
```
ERROR: ProvisionedThroughputExceededException
```
**Solution**: Switch to on-demand billing

#### **4. API Gateway CORS**
```
ERROR: CORS policy blocked request
```
**Solution**: Check CORS configuration in API Gateway

### **Debug Commands**

```bash
# Check Lambda logs
aws logs tail /aws/lambda/weather-chat-ai-weather-lambda --follow

# Test Lambda directly
aws lambda invoke --function-name weather-chat-ai-weather-lambda \
  --payload '{"query": "test"}' response.json

# Check DynamoDB
aws dynamodb scan --table-name weather-chat-ai-conversations

# Check S3
aws s3 ls s3://weather-chat-ai-weather-data-*
```

## 📚 **Additional Resources**

- **AWS Documentation**: [Lambda](https://docs.aws.amazon.com/lambda/), [API Gateway](https://docs.aws.amazon.com/apigateway/), [Bedrock](https://docs.aws.amazon.com/bedrock/)
- **Terraform Documentation**: [AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- **FastAPI Documentation**: [FastAPI](https://fastapi.tiangolo.com/)
- **NWS API**: [Weather.gov API](https://www.weather.gov/documentation/services-web-api)

This comprehensive guide covers everything you need to deploy, run, and maintain the Weather Chat AI system! 🚀 