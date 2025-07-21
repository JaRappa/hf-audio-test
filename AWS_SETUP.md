# 🌤️ AWS Setup Guide for AI Audio Pipeline

This guide explains how to configure AWS Bedrock for cloud-based text generation while keeping audio processing local.

## 🏗️ Architecture Overview

**What's Local:**
- 🎤 Speech-to-Text (Whisper model)
- 🔊 Text-to-Speech (Google TTS)
- 🌐 Web interface and audio processing

**What's in AWS:**
- 🧠 Language Model (Claude 3 Haiku via Bedrock)
- 📝 Text generation and conversation

## 🔧 AWS Setup

### 1. Prerequisites

- AWS Account with Bedrock access
- AWS CLI installed (optional but recommended)
- Proper IAM permissions for Bedrock

### 2. Enable Bedrock Model Access

1. **Log into AWS Console**
2. **Navigate to Amazon Bedrock**
3. **Go to "Model Access" in the left sidebar**
4. **Request access to Anthropic Claude models:**
   - Claude 3 Haiku
   - Claude 3 Sonnet (optional, for more advanced responses)

⚠️ **Note:** Model access requests may take a few minutes to be approved.

### 3. Configure AWS Credentials

Choose one of these methods:

#### Method 1: AWS CLI (Recommended)
```bash
# Install AWS CLI if not already installed
# Then configure your credentials
aws configure

# You'll be prompted for:
# AWS Access Key ID: [Your Access Key]
# AWS Secret Access Key: [Your Secret Key]  
# Default region name: us-east-1
# Default output format: json
```

#### Method 2: Environment Variables
```bash
# Windows (Command Prompt)
set AWS_ACCESS_KEY_ID=your_access_key_here
set AWS_SECRET_ACCESS_KEY=your_secret_access_key_here
set AWS_REGION=us-east-1

# Windows (PowerShell)
$env:AWS_ACCESS_KEY_ID="your_access_key_here"
$env:AWS_SECRET_ACCESS_KEY="your_secret_access_key_here" 
$env:AWS_REGION="us-east-1"

# Linux/Mac
export AWS_ACCESS_KEY_ID=your_access_key_here
export AWS_SECRET_ACCESS_KEY=your_secret_access_key_here
export AWS_REGION=us-east-1
```

#### Method 3: AWS Credentials File
Create `~/.aws/credentials` (Linux/Mac) or `C:\Users\{username}\.aws\credentials` (Windows):
```ini
[default]
aws_access_key_id = your_access_key_here
aws_secret_access_key = your_secret_access_key_here
region = us-east-1
```

### 4. Required IAM Permissions

Your AWS user/role needs these permissions:
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "bedrock:InvokeModel"
            ],
            "Resource": [
                "arn:aws:bedrock:*::foundation-model/anthropic.claude-3-haiku-20240307-v1:0"
            ]
        }
    ]
}
```

## 🚀 Testing the Setup

### 1. Test AWS Credentials
```bash
# Test if credentials are working
aws bedrock list-foundation-models --region us-east-1
```

### 2. Start the Application
```bash
# With Docker
docker-compose up --build

# Or natively
python app.py
```

### 3. Check the Health Endpoint
```bash
curl http://localhost:5000/health
```

Expected response with AWS working:
```json
{
  "status": "healthy",
  "device": "cpu",
  "aws_available": true,
  "tts_available": true
}
```

## 🔄 Fallback Behavior

If AWS credentials are not configured or Bedrock is unavailable:
- ✅ The application will still work
- 🤖 Text generation falls back to simple rule-based responses
- 🎤 Speech-to-text continues working (local Whisper)
- 🔊 Text-to-speech continues working (local gTTS)

## 💰 Cost Considerations

**AWS Bedrock Claude 3 Haiku Pricing (approximate):**
- Input tokens: ~$0.25 per 1M tokens
- Output tokens: ~$1.25 per 1M tokens

**Typical usage:**
- Short conversation (50 words): ~$0.0001
- 1000 conversations: ~$0.10

Much more cost-effective than running large language models locally!

## 🌍 Supported AWS Regions

Bedrock is available in these regions:
- `us-east-1` (N. Virginia) - Recommended
- `us-west-2` (Oregon)
- `ap-southeast-1` (Singapore)
- `eu-central-1` (Frankfurt)

## 🐛 Troubleshooting

### "AWS credentials not found"
- Verify AWS CLI configuration: `aws configure list`
- Check environment variables are set
- Ensure credentials file exists and is readable

### "Model access denied"
- Request model access in Bedrock console
- Wait for approval (usually immediate)
- Verify IAM permissions

### "Region not supported"
- Use `us-east-1` (most reliable)
- Check Bedrock availability in your region

### High latency
- Use a region closer to your location
- Consider switching to Claude 3 Haiku (fastest model)

## 📊 Monitoring Usage

Track your AWS usage:
1. **AWS Console → Billing → Cost Explorer**
2. **Filter by service: "Amazon Bedrock"**
3. **Set up billing alerts for cost control**

## 🔒 Security Best Practices

1. **Use IAM roles instead of access keys when possible**
2. **Rotate access keys regularly**
3. **Limit permissions to only Bedrock InvokeModel**
4. **Use AWS CloudTrail to monitor API calls**
5. **Never commit AWS credentials to version control**
