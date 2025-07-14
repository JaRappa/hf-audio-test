#!/bin/bash
# Simple server starter for AI Audio Pipeline
# This ensures the virtual environment is activated

cd "$(dirname "$0")"

echo "🎤 AI Audio Pipeline - Quick Start"
echo "=================================="

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "Please create one with: python3 -m venv .venv"
    echo "Then install packages: pip install -r requirements.txt"
    exit 1
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source .venv/bin/activate

# Verify packages are installed
echo "🔍 Checking if packages are installed..."
python3 -c "import torch, flask, transformers, gtts" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ Some packages are missing!"
    echo "Installing packages..."
    pip install -r requirements.txt
fi

# Show network info
echo "🌐 Server will be accessible at:"
ip addr show | grep "inet " | grep -v 127.0.0.1 | while read line; do
    ip=$(echo $line | awk '{print $2}' | cut -d'/' -f1)
    interface=$(echo $line | awk '{print $NF}')
    echo "   http://$ip:5000 ($interface)"
done

echo ""
echo "🚀 Starting AI Audio Pipeline Server..."
echo "💡 The first start may take a while as models are downloaded"
echo "💡 Press Ctrl+C to stop the server"
echo ""

# Start the server
python3 app.py
