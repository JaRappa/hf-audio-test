#!/bin/bash

# AI Audio Pipeline Setup Script for Arch Linux
# This script installs system dependencies and Python packages

set -e

echo "🚀 Setting up AI Audio Pipeline on Arch Linux..."

# Update system packages
echo "📦 Updating system packages..."
sudo pacman -Syu --noconfirm

# Install system dependencies
echo "🔧 Installing system dependencies..."
sudo pacman -S --needed --noconfirm \
    python \
    python-pip \
    git \
    ffmpeg \
    portaudio \
    espeak-ng \
    alsa-utils \
    pulseaudio \
    pulseaudio-alsa

# Install Python dependencies
echo "🐍 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Download required models (this will take some time)
echo "🤖 Pre-downloading AI models..."
python3 -c "
import torch
from transformers import WhisperProcessor, WhisperForConditionalGeneration, AutoTokenizer, AutoModelForCausalLM

print('Downloading Whisper model...')
WhisperProcessor.from_pretrained('openai/whisper-base')
WhisperForConditionalGeneration.from_pretrained('openai/whisper-base')

print('Downloading language model...')
AutoTokenizer.from_pretrained('microsoft/DialoGPT-medium')
AutoModelForCausalLM.from_pretrained('microsoft/DialoGPT-medium')

print('Testing TTS (Google Text-to-Speech)...')
try:
    from gtts import gTTS
    from pydub import AudioSegment
    # Test gTTS with a simple phrase
    test_tts = gTTS(text='Hello, this is a test.', lang='en')
    print('gTTS (Google Text-to-Speech) is working!')
except Exception as e:
    print(f'gTTS setup failed: {e}')
    print('TTS will be disabled.')

print('All models downloaded!')
"

# Create a systemd service file (optional)
echo "⚙️ Creating systemd service file..."
sudo tee /etc/systemd/system/ai-audio-pipeline.service > /dev/null << 'EOF'
[Unit]
Description=AI Audio Pipeline Server
After=network.target

[Service]
Type=simple
User=nobody
WorkingDirectory=/home/jake/hf-test
ExecStart=/usr/bin/python3 /home/jake/hf-test/app.py
Restart=always
RestartSec=3
Environment=PYTHONPATH=/home/jake/hf-test

[Install]
WantedBy=multi-user.target
EOF

# Set permissions
echo "🔐 Setting up permissions..."
sudo chown -R $USER:$USER /home/jake/hf-test
chmod +x /home/jake/hf-test/app.py

echo "✅ Setup complete!"
echo ""
echo "🎯 Next steps:"
echo "1. Run the server: python3 app.py"
echo "2. Open your browser to: http://[server-ip]:5000"
echo "3. Or enable as system service: sudo systemctl enable ai-audio-pipeline"
echo ""
echo "📝 Notes:"
echo "- The server runs on port 5000"
echo "- Make sure your firewall allows incoming connections on port 5000"
echo "- For Arch Linux: sudo ufw allow 5000 (if using ufw)"
echo "- The first run may take longer as models are loaded into memory"
echo ""
echo "🔧 Troubleshooting:"
echo "- If audio doesn't work, check PulseAudio: pulseaudio --check"
echo "- For CUDA support, install: sudo pacman -S cuda cudnn"
echo "- Check logs: journalctl -u ai-audio-pipeline -f"
