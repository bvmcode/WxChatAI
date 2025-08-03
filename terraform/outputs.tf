output "api_gateway_url" {
  description = "URL of the API Gateway"
  value       = "${aws_api_gateway_stage.prod.invoke_url}"
}

output "weather_lambda_arn" {
  description = "ARN of the weather Lambda function"
  value       = aws_lambda_function.weather_lambda.arn
}

output "health_lambda_arn" {
  description = "ARN of the health Lambda function"
  value       = aws_lambda_function.health_lambda.arn
}

output "dynamodb_table_name" {
  description = "Name of the DynamoDB conversations table"
  value       = aws_dynamodb_table.conversations.name
}

output "s3_bucket_name" {
  description = "Name of the S3 bucket for weather data"
  value       = aws_s3_bucket.weather_data.bucket
}

output "lambda_role_arn" {
  description = "ARN of the Lambda execution role"
  value       = aws_iam_role.lambda_role.arn
} 