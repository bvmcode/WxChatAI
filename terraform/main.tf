provider "aws" {
  region = var.aws_region
}

# Data source for current region
data "aws_region" "current" {}

# S3 bucket for weather data cache
resource "aws_s3_bucket" "weather_data" {
  bucket = "${var.project_name}-weather-data-${random_string.bucket_suffix.result}"
}

resource "aws_s3_bucket_versioning" "weather_data" {
  bucket = aws_s3_bucket.weather_data.id
  versioning_configuration {
    status = "Disabled"
  }
}

resource "aws_s3_bucket_public_access_block" "weather_data" {
  bucket = aws_s3_bucket.weather_data.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# DynamoDB table for conversation history
resource "aws_dynamodb_table" "conversations" {
  name           = "${var.project_name}-conversations"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "user_id"
  range_key      = "timestamp"

  attribute {
    name = "user_id"
    type = "S"
  }

  attribute {
    name = "timestamp"
    type = "S"
  }

  ttl {
    attribute_name = "ttl"
    enabled        = true
  }

  tags = var.tags
}

# IAM role for Lambda functions
resource "aws_iam_role" "lambda_role" {
  name = "${var.project_name}-lambda-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

# Attach basic execution policy
resource "aws_iam_role_policy_attachment" "lambda_basic" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# IAM policy for Lambda to access DynamoDB, S3, and Bedrock
resource "aws_iam_policy" "lambda_permissions" {
  name = "${var.project_name}-lambda-permissions"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "dynamodb:GetItem",
          "dynamodb:PutItem",
          "dynamodb:UpdateItem",
          "dynamodb:DeleteItem",
          "dynamodb:Query",
          "dynamodb:Scan"
        ]
        Resource = aws_dynamodb_table.conversations.arn
      },
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject",
          "s3:ListBucket"
        ]
        Resource = [
          aws_s3_bucket.weather_data.arn,
          "${aws_s3_bucket.weather_data.arn}/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "bedrock:InvokeModel"
        ]
        Resource = [
          "arn:aws:bedrock:${data.aws_region.current.name}::foundation-model/anthropic.claude-3-sonnet-20240229-v1:0",
          "arn:aws:bedrock:${data.aws_region.current.name}::foundation-model/anthropic.claude-3-haiku-20240307-v1:0",
          "arn:aws:bedrock:${data.aws_region.current.name}::foundation-model/anthropic.claude-3-opus-20240229-v1:0",
          "arn:aws:bedrock:${data.aws_region.current.name}::foundation-model/meta.llama-2-70b-chat-v1",
          "arn:aws:bedrock:${data.aws_region.current.name}::foundation-model/amazon.titan-text-express-v1"
        ]
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_permissions" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = aws_iam_policy.lambda_permissions.arn
}

# Lambda function for weather processing
resource "aws_lambda_function" "weather_lambda" {
  filename         = data.archive_file.lambda_zip.output_path
  function_name    = "${var.project_name}-weather-lambda"
  role            = aws_iam_role.lambda_role.arn
  handler         = "aws_lambda_handler.lambda_handler"
  runtime         = "python3.11"
  timeout         = 30
  memory_size     = 512

  environment {
    variables = {
      CONVERSATIONS_TABLE = aws_dynamodb_table.conversations.name
      WEATHER_BUCKET      = aws_s3_bucket.weather_data.bucket
      LOG_LEVEL          = "INFO"
    }
  }

  tags = var.tags
}

# Lambda function for health checks
resource "aws_lambda_function" "health_lambda" {
  filename         = data.archive_file.lambda_zip.output_path
  function_name    = "${var.project_name}-health-lambda"
  role            = aws_iam_role.lambda_role.arn
  handler         = "aws_lambda_handler.health_check"
  runtime         = "python3.11"
  timeout         = 10
  memory_size     = 128

  environment {
    variables = {
      LOG_LEVEL = "INFO"
    }
  }

  tags = var.tags
}

# API Gateway
resource "aws_api_gateway_rest_api" "weather_api" {
  name        = "${var.project_name}-weather-api"
  description = "Weather Chat AI API"
}

# API Gateway resources
resource "aws_api_gateway_resource" "weather" {
  rest_api_id = aws_api_gateway_rest_api.weather_api.id
  parent_id   = aws_api_gateway_rest_api.weather_api.root_resource_id
  path_part   = "weather"
}

resource "aws_api_gateway_resource" "health" {
  rest_api_id = aws_api_gateway_rest_api.weather_api.id
  parent_id   = aws_api_gateway_rest_api.weather_api.root_resource_id
  path_part   = "health"
}

resource "aws_api_gateway_resource" "capabilities" {
  rest_api_id = aws_api_gateway_rest_api.weather_api.id
  parent_id   = aws_api_gateway_rest_api.weather_api.root_resource_id
  path_part   = "capabilities"
}

# API Gateway methods
resource "aws_api_gateway_method" "weather_post" {
  rest_api_id   = aws_api_gateway_rest_api.weather_api.id
  resource_id   = aws_api_gateway_resource.weather.id
  http_method   = "POST"
  authorization = "NONE"
}

resource "aws_api_gateway_method" "health_get" {
  rest_api_id   = aws_api_gateway_rest_api.weather_api.id
  resource_id   = aws_api_gateway_resource.health.id
  http_method   = "GET"
  authorization = "NONE"
}

resource "aws_api_gateway_method" "capabilities_get" {
  rest_api_id   = aws_api_gateway_rest_api.weather_api.id
  resource_id   = aws_api_gateway_resource.capabilities.id
  http_method   = "GET"
  authorization = "NONE"
}

# API Gateway integrations
resource "aws_api_gateway_integration" "weather_lambda" {
  rest_api_id = aws_api_gateway_rest_api.weather_api.id
  resource_id = aws_api_gateway_resource.weather.id
  http_method = aws_api_gateway_method.weather_post.http_method

  integration_http_method = "POST"
  type                   = "AWS_PROXY"
  uri                    = aws_lambda_function.weather_lambda.invoke_arn
}

resource "aws_api_gateway_integration" "health_lambda" {
  rest_api_id = aws_api_gateway_rest_api.weather_api.id
  resource_id = aws_api_gateway_resource.health.id
  http_method = aws_api_gateway_method.health_get.http_method

  integration_http_method = "POST"
  type                   = "AWS_PROXY"
  uri                    = aws_lambda_function.health_lambda.invoke_arn
}

# Mock integration for capabilities
resource "aws_api_gateway_integration" "capabilities_mock" {
  rest_api_id = aws_api_gateway_rest_api.weather_api.id
  resource_id = aws_api_gateway_resource.capabilities.id
  http_method = aws_api_gateway_method.capabilities_get.http_method

  type = "MOCK"

  request_templates = {
    "application/json" = jsonencode({
      statusCode = 200
    })
  }
}

resource "aws_api_gateway_method_response" "capabilities_200" {
  rest_api_id = aws_api_gateway_rest_api.weather_api.id
  resource_id = aws_api_gateway_resource.capabilities.id
  http_method = aws_api_gateway_method.capabilities_get.http_method
  status_code = "200"

  response_parameters = {
    "method.response.header.Access-Control-Allow-Origin"  = true
    "method.response.header.Access-Control-Allow-Headers" = true
  }
}

resource "aws_api_gateway_integration_response" "capabilities_200" {
  rest_api_id = aws_api_gateway_rest_api.weather_api.id
  resource_id = aws_api_gateway_resource.capabilities.id
  http_method = aws_api_gateway_method.capabilities_get.http_method
  status_code = aws_api_gateway_method_response.capabilities_200.status_code

  response_parameters = {
    "method.response.header.Access-Control-Allow-Origin"  = "'*'"
    "method.response.header.Access-Control-Allow-Headers" = "'Content-Type'"
  }
}

# Lambda permissions for API Gateway
resource "aws_lambda_permission" "weather_api_gw" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.weather_lambda.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.weather_api.execution_arn}/*/*"
}

resource "aws_lambda_permission" "health_api_gw" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.health_lambda.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.weather_api.execution_arn}/*/*"
}

# API Gateway deployment
resource "aws_api_gateway_deployment" "weather_api" {
  depends_on = [
    aws_api_gateway_integration.weather_lambda,
    aws_api_gateway_integration.health_lambda,
    aws_api_gateway_integration.capabilities_mock,
  ]

  rest_api_id = aws_api_gateway_rest_api.weather_api.id
}

resource "aws_api_gateway_stage" "prod" {
  deployment_id = aws_api_gateway_deployment.weather_api.id
  rest_api_id   = aws_api_gateway_rest_api.weather_api.id
  stage_name    = "prod"
}

# CloudWatch log groups
resource "aws_cloudwatch_log_group" "weather_lambda" {
  name              = "/aws/lambda/${aws_lambda_function.weather_lambda.function_name}"
  retention_in_days = 7
}

resource "aws_cloudwatch_log_group" "health_lambda" {
  name              = "/aws/lambda/${aws_lambda_function.health_lambda.function_name}"
  retention_in_days = 7
}

# Random string for bucket name
resource "random_string" "bucket_suffix" {
  length  = 8
  special = false
  upper   = false
}

# Data source for Lambda zip
data "archive_file" "lambda_zip" {
  type        = "zip"
  source_dir  = "${path.module}/../src"
  output_path = "${path.module}/lambda.zip"
} 