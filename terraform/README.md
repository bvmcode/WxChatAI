# Weather Chat AI - Terraform Infrastructure

This directory contains the Terraform configuration for deploying the Weather Chat AI infrastructure to AWS.

## Prerequisites

1. **Terraform** (>= 1.0)
2. **AWS CLI** configured with appropriate credentials
3. **Python** with required dependencies installed

## Infrastructure Components

- **Lambda Functions**: Weather processing and health checks
- **API Gateway**: RESTful API endpoints
- **DynamoDB**: Conversation history storage
- **S3 Bucket**: Weather data cache
- **CloudWatch**: Logging and monitoring
- **IAM**: Roles and policies for Lambda execution

## Deployment

### Quick Deploy

```bash
# From the project root
./terraform/deploy.sh
```

### Manual Deployment

```bash
# Change to terraform directory
cd terraform

# Initialize Terraform
terraform init

# Plan the deployment
terraform plan

# Deploy the infrastructure
terraform apply -auto-approve

# View outputs
terraform output
```

## Configuration

### Variables

You can customize the deployment by creating a `terraform.tfvars` file:

```hcl
aws_region = "us-west-2"
project_name = "my-weather-app"
tags = {
  Project     = "weather-chat-ai"
  Environment = "production"
  ManagedBy   = "terraform"
}
```

### Available Variables

- `aws_region`: AWS region for resources (default: "us-east-1")
- `project_name`: Name of the project (default: "weather-chat-ai")
- `tags`: Tags to apply to all resources

## Outputs

After deployment, Terraform will output:

- `api_gateway_url`: URL of the deployed API Gateway
- `weather_lambda_arn`: ARN of the weather processing Lambda
- `health_lambda_arn`: ARN of the health check Lambda
- `dynamodb_table_name`: Name of the DynamoDB table
- `s3_bucket_name`: Name of the S3 bucket
- `lambda_role_arn`: ARN of the Lambda execution role

## Testing the Deployment

Once deployed, you can test the API:

```bash
# Test weather endpoint
curl -X POST "$(terraform output -raw api_gateway_url)/weather" \
  -H "Content-Type: application/json" \
  -d '{"query": "Will it rain in Denver on Sunday?"}'

# Test health endpoint
curl "$(terraform output -raw api_gateway_url)/health"
```

## Cleanup

To destroy the infrastructure:

```bash
cd terraform
terraform destroy -auto-approve
```

## Security Notes

- All resources are tagged for cost tracking
- S3 bucket has public access blocked
- IAM roles follow least privilege principle
- API Gateway has CORS enabled for web access 