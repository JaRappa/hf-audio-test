#!/usr/bin/env python3
"""
AWS Bedrock test script for AI Audio Pipeline
Quick test to verify AWS Bedrock integration
"""

import sys
import os
import json
import boto3
from botocore.exceptions import ClientError, NoCredentialsError

def test_bedrock_with_bearer_token(bearer_token, body):
    """Test Bedrock using bearer token authentication"""
    import requests
    
    region = os.getenv('AWS_REGION', 'us-east-1')
    model_id = 'anthropic.claude-3-haiku-20240307-v1:0'
    url = f"https://bedrock-runtime.{region}.amazonaws.com/model/{model_id}/invoke"
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {bearer_token}',
        'Accept': 'application/json'
    }
    
    response = requests.post(url, headers=headers, data=body, timeout=30)
    response.raise_for_status()
    
    response_data = response.json()
    return response_data['content'][0]['text']

def test_aws_bedrock():
    """Test AWS Bedrock integration"""
    print("🌤️ Testing AWS Bedrock Integration")
    print("=" * 40)
    
    try:
        # Test boto3 import
        print("📦 Testing boto3 installation...")
        import boto3
        print("✅ boto3 installed")
        
        # Test credentials
        print("\n🔐 Testing AWS credentials...")
        
        # Check for bearer token first
        bearer_token = os.getenv('AWS_BEARER_TOKEN_BEDROCK')
        if bearer_token:
            print("✅ AWS Bearer Token found")
            print("🔑 Using bearer token authentication")
            # We'll test this in the Bedrock section
        else:
            try:
                client = boto3.client('bedrock-runtime', region_name='us-east-1')
                print("✅ AWS credentials found")
            except NoCredentialsError:
                print("❌ No AWS credentials found")
                print("   Please configure AWS credentials using one of:")
                print("   1. aws configure")
                print("   2. Environment variables (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)")
                print("   3. AWS credentials file")
                print("   4. IAM roles (if on EC2)")
                return False
            except Exception as e:
                print(f"❌ AWS client error: {e}")
                return False
        
        # Test Bedrock access
        print("\n🤖 Testing Bedrock model access...")
        
        # Check if we should use bearer token
        bearer_token = os.getenv('AWS_BEARER_TOKEN_BEDROCK')
        
        try:
            # Prepare a simple test message
            body = json.dumps({
                "anthropic_version": "bedrock-2023-05-15",
                "max_tokens": 20,
                "messages": [
                    {
                        "role": "user",
                        "content": "Say 'Hello from AWS Bedrock!' in exactly 5 words."
                    }
                ]
            })
            
            if bearer_token:
                # Test with bearer token using direct HTTP request
                ai_response = test_bedrock_with_bearer_token(bearer_token, body)
            else:
                # Call Bedrock with standard boto3
                if 'client' not in locals():
                    client = boto3.client('bedrock-runtime', region_name='us-east-1')
                    
                response = client.invoke_model(
                    modelId='anthropic.claude-3-haiku-20240307-v1:0',
                    body=body
                )
                
                # Parse response
                response_body = json.loads(response['body'].read())
                ai_response = response_body['content'][0]['text']
            
            print("✅ Bedrock model access successful!")
            print(f"🗣️  Test response: '{ai_response.strip()}'")
            
            # Estimate cost
            input_tokens = len(body.split())
            output_tokens = len(ai_response.split())
            estimated_cost = (input_tokens * 0.00025 + output_tokens * 0.00125) / 1000
            print(f"💰 Estimated cost for this test: ${estimated_cost:.6f}")
            
            return True
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'AccessDeniedException':
                print("❌ Access denied to Bedrock models")
                print("   Please:")
                print("   1. Go to AWS Bedrock console")
                print("   2. Navigate to 'Model Access'")
                print("   3. Request access to Anthropic Claude models")
                print("   4. Wait for approval (usually immediate)")
            elif error_code == 'ValidationException':
                print("⚠️  Model validation error (but credentials work)")
                print("   This might indicate model access is pending")
            else:
                print(f"❌ Bedrock error ({error_code}): {e}")
            return False
            
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            return False
            
    except ImportError:
        print("❌ boto3 not installed")
        print("   Install with: pip install boto3")
        return False
    except Exception as e:
        print(f"❌ Setup error: {e}")
        return False

def show_setup_help():
    """Show setup instructions"""
    print("\n📋 AWS Setup Instructions")
    print("=" * 40)
    print("1. 🔧 Install AWS CLI (optional):")
    print("   https://aws.amazon.com/cli/")
    print("")
    print("2. 🔑 Configure credentials:")
    print("   aws configure")
    print("   (Enter your Access Key ID, Secret Access Key, and region)")
    print("")
    print("3. 🚀 Enable Bedrock models:")
    print("   - Go to AWS Bedrock console")
    print("   - Click 'Model Access' in left sidebar")
    print("   - Request access to Anthropic Claude models")
    print("")
    print("4. 💰 Set up billing alerts (recommended):")
    print("   - Go to AWS Billing console")
    print("   - Set up cost alerts for Bedrock usage")
    print("")
    print("📚 Full guide: See AWS_SETUP.md")

def main():
    """Run AWS test"""
    success = test_aws_bedrock()
    
    if not success:
        show_setup_help()
        return 1
    else:
        print("\n✅ AWS Bedrock is ready!")
        print("🎤 Your AI Audio Pipeline will use AWS for intelligent responses")
        print("🔒 Audio processing remains local for privacy")
        return 0

if __name__ == "__main__":
    sys.exit(main())
