# Weather Chat AI - Infrastructure & Deployment Summary

## **AWS Infrastructure Architecture**

### **Core Components**

| Component | Purpose | Technology |
|-----------|---------|------------|
| **API Gateway** | REST API endpoint | AWS API Gateway |
| **Lambda Functions** | Serverless compute | AWS Lambda (Python 3.11) |
| **DynamoDB** | Conversation history | AWS DynamoDB |
| **S3** | Weather data cache | AWS S3 |
| **Bedrock** | AI model service | AWS Bedrock (Claude) |
| **CloudWatch** | Monitoring & logging | AWS CloudWatch |
| **IAM** | Security & permissions | AWS IAM |

### **Infrastructure Diagram**

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

## **Deployment Process**

### **Prerequisites**

1. **AWS CLI installed and configured:**
   ```bash
   aws configure
   ```

2. **Terraform installed:**
   ```bash
   # macOS
   brew install terraform
   
   # Linux
   curl -fsSL https://apt.releases.hashicorp.com/gpg | sudo apt-key add -
   sudo apt-add-repository "deb [arch=amd64] https://apt.releases.hashicorp.com $(lsb_release -cs) main"
   sudo apt-get update && sudo apt-get install terraform
   ```

3. **Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

### **Quick Deployment**

```bash
# 1. Navigate to terraform directory
cd terraform

# 2. Initialize Terraform
terraform init

# 3. Plan deployment
terraform plan

# 4. Deploy infrastructure
terraform apply -auto-approve

# 5. Get deployment outputs
terraform output
```

### **Automated Deployment Script**

```bash
# Run the automated deployment script
./terraform/deploy.sh
```

This script will:
- ✅ Check for required tools (Terraform, AWS CLI)
- ✅ Initialize Terraform
- ✅ Plan the deployment
- ✅ Apply the infrastructure
- ✅ Display outputs

## 📋 **Infrastructure Details**

### **1. API Gateway**
- **Purpose**: REST API endpoint for weather queries
- **Endpoints**:
  - `POST /weather` - Process weather queries
  - `GET /health` - Health check
  - `GET /capabilities` - Service capabilities
- **CORS**: Enabled for cross-origin requests
- **Integration**: Lambda proxy integration

### **2. Lambda Functions**

#### **Weather Lambda**
- **Runtime**: Python 3.11
- **Memory**: 512 MB
- **Timeout**: 30 seconds
- **Handler**: `aws_lambda_handler.lambda_handler`
- **Environment Variables**:
  - `CONVERSATIONS_TABLE` - DynamoDB table name
  - `WEATHER_BUCKET` - S3 bucket name
  - `LOG_LEVEL` - Logging level

#### **Health Lambda**
- **Runtime**: Python 3.11
- **Memory**: 128 MB
- **Timeout**: 10 seconds
- **Handler**: `aws_lambda_handler.health_check`

### **3. DynamoDB Table**
- **Name**: `{project_name}-conversations`
- **Billing**: Pay-per-request
- **Primary Key**: `user_id` (hash)
- **Sort Key**: `timestamp` (range)
- **TTL**: Enabled for automatic cleanup
- **Purpose**: Store conversation history and user sessions

### **4. S3 Bucket**
- **Name**: `{project_name}-weather-data-{random_suffix}`
- **Versioning**: Disabled
- **Public Access**: Blocked (secure)
- **Purpose**: Cache weather data and static assets

### **5. IAM Roles & Policies**

#### **Lambda Execution Role**
- **Basic Execution**: CloudWatch Logs
- **DynamoDB Access**: Read/Write conversations
- **S3 Access**: Read/Write weather data
- **Bedrock Access**: Invoke AI models

#### **Bedrock Model Permissions**
```json
{
  "Effect": "Allow",
  "Action": ["bedrock:InvokeModel"],
  "Resource": [
    "arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-3-sonnet-20240229-v1:0",
    "arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-3-haiku-20240307-v1:0",
    "arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-3-opus-20240229-v1:0",
    "arn:aws:bedrock:us-east-1::foundation-model/meta.llama-2-70b-chat-v1",
    "arn:aws:bedrock:us-east-1::foundation-model/amazon.titan-text-express-v1"
  ]
}
```

### **6. CloudWatch Log Groups**
- **Weather Lambda**: `/aws/lambda/{project_name}-weather-lambda`
- **Health Lambda**: `/aws/lambda/{project_name}-health-lambda`
- **Retention**: 7 days
- **Purpose**: Centralized logging and monitoring

## **How It Works**

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
   - **AI Model Service**: Extracts location, time, intent
   - **Weather Service**: Fetches data from NWS API
   - **Response Generation**: Creates friendly response
   - **Storage**: Saves to DynamoDB

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

3. **Model Options**:
   - **Claude 3 Sonnet** (recommended)
   - **Claude 3 Haiku** (fast, cheap)
   - **Claude 3 Opus** (most capable)
   - **Llama 2** (alternative)
   - **Titan** (AWS native)

## **Deployment Outputs**

After successful deployment, Terraform outputs:

```bash
api_gateway_url = "https://{api-id}.execute-api.us-east-1.amazonaws.com/prod"
weather_lambda_arn = "arn:aws:lambda:us-east-1:{account}:function:weather-chat-ai-weather-lambda"
health_lambda_arn = "arn:aws:lambda:us-east-1:{account}:function:weather-chat-ai-health-lambda"
dynamodb_table_name = "weather-chat-ai-conversations"
s3_bucket_name = "weather-chat-ai-weather-data-{suffix}"
lambda_role_arn = "arn:aws:iam::{account}:role/weather-chat-ai-lambda-role"
```

## **Testing the Deployment**

### **1. Health Check**
```bash
curl -X GET "https://{api-id}.execute-api.us-east-1.amazonaws.com/prod/health"
```

### **2. Weather Query**
```bash
curl -X POST "https://{api-id}.execute-api.us-east-1.amazonaws.com/prod/weather" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Will it rain in Denver on Sunday?",
    "user_id": "test-user",
    "session_id": "test-session"
  }'
```

### **3. Capabilities Check**
```bash
curl -X GET "https://{api-id}.execute-api.us-east-1.amazonaws.com/prod/capabilities"
```

## **Configuration Options**

### **Environment Variables**

| Variable | Default | Purpose |
|----------|---------|---------|
| `AWS_DEFAULT_REGION` | `us-east-1` | AWS region |
| `BEDROCK_MODEL_ID` | `anthropic.claude-3-sonnet-20240229-v1:0` | AI model |
| `USE_AI_MODEL` | `true` | Enable/disable AI |
| `LOG_LEVEL` | `INFO` | Logging level |

### **Terraform Variables**

| Variable | Default | Purpose |
|----------|---------|---------|
| `aws_region` | `us-east-1` | AWS region |
| `project_name` | `weather-chat-ai` | Project name |
| `tags` | `{}` | Resource tags |

## **Maintenance & Monitoring**

### **CloudWatch Monitoring**
- **Logs**: Centralized logging for all Lambda functions
- **Metrics**: Lambda invocation, duration, errors
- **Alarms**: Set up alerts for errors or high latency

### **Cost Optimization**
- **DynamoDB**: Pay-per-request billing
- **Lambda**: Pay only for invocations
- **S3**: Lifecycle policies for old data
- **Bedrock**: Choose appropriate model tier

### **Security**
- **IAM**: Least privilege access
- **S3**: Private bucket with encryption
- **API Gateway**: HTTPS only
- **Lambda**: VPC isolation (optional)

## **Cleanup**

To destroy the infrastructure:

```bash
cd terraform
terraform destroy -auto-approve
```

** Warning**: This will delete all resources including data!

## **Scaling Considerations**

### **Auto-scaling**
- **Lambda**: Automatically scales with demand
- **DynamoDB**: Handles traffic spikes
- **API Gateway**: Scales automatically

### **Performance**
- **Cold Start**: ~1-2 seconds for Lambda
- **Response Time**: ~2-5 seconds total
- **Concurrent**: Limited by Lambda limits (1000 default)

### **Limits**
- **Lambda**: 15-minute timeout, 10GB memory
- **API Gateway**: 10,000 requests/second
- **DynamoDB**: 40,000 read/write units per second
- **Bedrock**: Rate limits per model

This infrastructure provides a **scalable, secure, and cost-effective** weather chat AI service with AI-powered natural language processing!