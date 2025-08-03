#!/bin/bash
"""
Terraform deployment script for Weather Chat AI infrastructure.
"""

set -e

echo "Deploying Weather Chat AI infrastructure with Terraform..."

# Check if Terraform is installed
if ! command -v terraform &> /dev/null; then
    echo "Terraform is not installed. Please install it first."
    exit 1
fi

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo "AWS CLI is not installed. Please install it first."
    exit 1
fi

# Change to terraform directory
cd terraform

# Initialize Terraform
echo "Initializing Terraform..."
terraform init

# Plan the deployment
echo "Planning deployment..."
terraform plan

# Deploy the infrastructure
echo "Deploying infrastructure..."
terraform apply -auto-approve

# Get outputs
echo "Deployment complete! Here are the outputs:"
terraform output

echo "Terraform deployment complete!"
echo "API Gateway URL: $(terraform output -raw api_gateway_url)"
echo "Check CloudWatch for logs and monitoring." 