#!/usr/bin/env python3
"""Test different anthropic_version values for Claude 3.5 Sonnet v2"""

import boto3
import json

def test_anthropic_versions():
    client = boto3.client('bedrock-runtime', region_name='us-east-1')
    
    # Test different anthropic_version values
    versions = [
        'bedrock-2023-05-15', 
        'bedrock-2023-10-18', 
        'bedrock-2024-02-15', 
        'bedrock-2024-06-01',
        'bedrock-2024-10-15'
    ]
    
    for version in versions:
        try:
            response = client.invoke_model(
                modelId='us.anthropic.claude-3-5-sonnet-20241022-v2:0',
                body=json.dumps({
                    'anthropic_version': version,
                    'messages': [{'role': 'user', 'content': 'test'}],
                    'max_tokens': 5
                })
            )
            print(f'✅ SUCCESS with version: {version}')
            return version
        except Exception as e:
            print(f'❌ FAILED with version {version}: {str(e)[:100]}...')
    
    print("❌ No working version found")
    return None

if __name__ == "__main__":
    test_anthropic_versions()
