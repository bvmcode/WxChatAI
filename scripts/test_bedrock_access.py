#!/usr/bin/env python3
"""
Test Bedrock model access and diagnose access issues.
"""

import boto3
import json
import os
from botocore.exceptions import ClientError, NoCredentialsError

def test_bedrock_access():
    """Test Bedrock model access."""
    print("🔍 Testing AWS Bedrock Access")
    print("=" * 50)
    
    # Check AWS credentials
    try:
        sts = boto3.client('sts')
        identity = sts.get_caller_identity()
        print(f"✅ AWS credentials configured")
        print(f"   Account: {identity['Account']}")
        print(f"   User: {identity['Arn']}")
    except NoCredentialsError:
        print("❌ AWS credentials not found")
        print("   Run: aws configure")
        return False
    except Exception as e:
        print(f"❌ AWS credentials error: {e}")
        return False
    
    # Test Bedrock client
    try:
        bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')
        print(f"✅ Bedrock client initialized")
    except Exception as e:
        print(f"❌ Bedrock client error: {e}")
        return False
    
    # List available models
    try:
        bedrock_list = boto3.client('bedrock', region_name='us-east-1')
        models = bedrock_list.list_foundation_models()
        print(f"✅ Found {len(models['modelSummaries'])} foundation models")
        
        # Show Claude models
        claude_models = [m for m in models['modelSummaries'] if 'claude' in m['modelId'].lower()]
        print(f"   Claude models available: {len(claude_models)}")
        for model in claude_models:
            print(f"   - {model['modelId']}")
            
    except Exception as e:
        print(f"❌ Error listing models: {e}")
    
    # Test specific model access
    test_models = [
        "anthropic.claude-v2",
        "anthropic.claude-v2:1",
        "anthropic.claude-instant-v1",
        "anthropic.claude-3-sonnet-20240229-v1:0"
    ]
    
    print(f"\n🧪 Testing Model Access")
    print("-" * 30)
    
    for model_id in test_models:
        try:
            # Try to invoke the model with a simple test
            response = bedrock.invoke_model(
                modelId=model_id,
                body=json.dumps({
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": 10,
                    "messages": [{"role": "user", "content": "Hello"}]
                })
            )
            print(f"✅ {model_id} - ACCESS GRANTED")
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            
            if error_code == 'AccessDeniedException':
                print(f"❌ {model_id} - ACCESS DENIED")
                print(f"   Error: {error_message}")
                print(f"   Solution: Request access in AWS Bedrock console")
            else:
                print(f"⚠️  {model_id} - OTHER ERROR")
                print(f"   Error: {error_message}")
                
        except Exception as e:
            print(f"❌ {model_id} - UNEXPECTED ERROR")
            print(f"   Error: {e}")
    
    print(f"\n📋 Next Steps:")
    print("1. Go to AWS Bedrock Console: https://console.aws.amazon.com/bedrock/")
    print("2. Click 'Model access' in the sidebar")
    print("3. Request access for the models you need")
    print("4. Wait for approval (usually instant)")
    print("5. Run this script again to verify access")

if __name__ == "__main__":
    test_bedrock_access() 