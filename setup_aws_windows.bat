@echo off
REM Windows AWS Setup Helper for AI Audio Pipeline
REM This script helps set up AWS credentials on Windows

echo 🌤️  AI Audio Pipeline - Windows AWS Setup
echo ============================================
echo.

echo 📋 You have several options to configure AWS credentials:
echo.

echo Option 1: Edit .env file (RECOMMENDED)
echo ----------------------------------------
echo 1. Open .env file in any text editor
echo 2. Replace the placeholder values with your real AWS credentials
echo 3. Save the file
echo.
echo Example:
echo AWS_ACCESS_KEY_ID=AKIA1234567890EXAMPLE
echo AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
echo AWS_REGION=us-east-1
echo.

echo Option 2: Use Windows Environment Variables
echo --------------------------------------------
echo Open PowerShell and run:
echo $env:AWS_ACCESS_KEY_ID="your_access_key_here"
echo $env:AWS_SECRET_ACCESS_KEY="your_secret_access_key_here"
echo $env:AWS_REGION="us-east-1"
echo.

echo Option 3: Install AWS CLI
echo --------------------------
echo 1. Download from: https://aws.amazon.com/cli/
echo 2. Install the MSI package
echo 3. Run: aws configure
echo 4. Enter your credentials when prompted
echo.

echo 🔐 Getting AWS Credentials:
echo ============================
echo 1. Log into AWS Console
echo 2. Go to IAM ^> Users ^> Your User ^> Security Credentials
echo 3. Create Access Key (if you don't have one)
echo 4. Copy the Access Key ID and Secret Access Key
echo.

echo ⚠️  Important: Keep your credentials secure!
echo - Never share them publicly
echo - Never commit them to version control
echo - Rotate them regularly
echo.

echo 📝 Next Steps:
echo ==============
echo 1. Configure your credentials using one of the options above
echo 2. Test with: python test_aws.py
echo 3. Start the server: python app.py
echo.

echo 📚 For detailed instructions, see: AWS_SETUP.md
echo.

pause
