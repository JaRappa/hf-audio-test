# 🎤 AI Audio Pipeline

A complete AI-powered audio processing pipeline that:
1. **Transcribes** speech to text using Whisper
2. **Generates** AI responses using DialoGPT
3. **Synthesizes** speech from text using TTS
4. **Serves** a beautiful web interface for interaction

## 🚀 Quick Start

### 🐳 Docker (Recommended)

The easiest way to run the AI Audio Pipeline is using Docker:

```bash
# Clone the repository
git clone <your-repo-url>
cd hf-audio-test

# Start with Docker Compose
docker-compose up --build

# Or use the management script (Windows)
.\docker.ps1 start

# Or use the management script (Linux/Mac)
./docker.sh start
```

**Access**: http://localhost:5000

### 🐧 Native Installation

#### Prerequisites
- Linux/Windows/macOS
- Python 3.8+ (tested with Python 3.13)
- Virtual environment activated
- Internet connection for downloading models

#### Installation

1. **Activate your virtual environment:**
   ```bash
   source .venv/bin/activate
   ```

2. **Install packages:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Start the server:**
   ```bash
   ./start_server.sh
   ```
   Or directly:
   ```bash
   source .venv/bin/activate && python3 app.py
   ```

4. **Access the web interface:**
   - Open browser to `http://localhost:5000` (Docker) or `http://192.168.1.17:5000` (native)
   - The interface will work from any device on your LAN

## 🐳 Docker Usage

### Quick Commands

```bash
# Windows
.\docker.ps1 start     # Start containers
.\docker.ps1 logs      # View logs
.\docker.ps1 status    # Check status
.\docker.ps1 stop      # Stop containers

# Linux/Mac
./docker.sh start      # Start containers
./docker.sh logs       # View logs
./docker.sh status     # Check status
./docker.sh stop       # Stop containers
```

For complete Docker documentation, see [DOCKER.md](DOCKER.md).

## 🔧 Manual Installation

If you prefer manual setup:

```bash
# Install system dependencies
sudo pacman -S python python-pip ffmpeg portaudio espeak-ng alsa-utils pulseaudio

# Install Python packages
pip install -r requirements.txt

# Run the application
python3 app.py
```

## 🌐 Network Configuration

### Finding Your Server IP
```bash
ip addr show | grep "inet " | grep -v 127.0.0.1
```

### Firewall Configuration
```bash
# For ufw
sudo ufw allow 5000

# For iptables
sudo iptables -A INPUT -p tcp --dport 5000 -j ACCEPT
```

## 🎯 Usage

### Web Interface
1. **Record Audio**: Click "Start Recording" and speak
2. **Upload File**: Choose an audio file and click "Upload & Process"
3. **Get Response**: View transcription, AI response, and hear audio output

### API Endpoints

#### Health Check
```bash
curl http://localhost:5000/health
```

#### Process Audio
```bash
curl -X POST -F "audio=@your_audio.wav" http://localhost:5000/process_audio
```

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Web Client    │───▶│   Flask Server   │───▶│  AI Pipeline    │
│  (Browser UI)   │    │  (API + WebUI)   │    │ (Whisper+GPT+   │
└─────────────────┘    └──────────────────┘    │      TTS)       │
                                                └─────────────────┘
```

### Components

- **Frontend**: HTML5 + JavaScript with WebRTC for audio recording
- **Backend**: Flask + SocketIO for real-time communication
- **AI Models**:
  - **Whisper** (openai/whisper-base) for speech-to-text
  - **DialoGPT** (microsoft/DialoGPT-medium) for conversation
  - **gTTS** (Google Text-to-Speech) for voice synthesis (Python 3.13 compatible)

## ⚙️ Configuration

### Model Configuration
Edit `app.py` to change models:

```python
# Change Whisper model size
self.whisper_processor = WhisperProcessor.from_pretrained("openai/whisper-large")

# Change language model
self.tokenizer = AutoTokenizer.from_pretrained("microsoft/DialoGPT-large")

# Change TTS to gTTS
self.tts_available = True  # gTTS doesn't need model loading
```

### Server Configuration
```python
# Change host/port in app.py
socketio.run(app, host='0.0.0.0', port=8080, debug=False)
```

## 🐛 Troubleshooting

### Common Issues

#### Audio Processing HTTP 500 Error
If you get "HTTP error! status: 500" when processing audio:
1. **Check the server logs** in your terminal
2. **Restart the server** with the virtual environment:
   ```bash
   source .venv/bin/activate && python3 app.py
   ```
3. **Verify all packages are installed**:
   ```bash
   source .venv/bin/activate && python3 test_setup.py
   ```

#### Setup Script Errors
If you see "No module named 'TTS'" during setup:
- This is expected with Python 3.13 - the setup script has been updated to use gTTS instead
- Just run: `pip install -r requirements.txt`

#### Audio Recording Not Working
```bash
# Check PulseAudio
pulseaudio --check

# Restart PulseAudio
pulseaudio -k && pulseaudio --start
```

#### CUDA Not Detected
```bash
# Install CUDA (optional for GPU acceleration)
sudo pacman -S cuda cudnn

# Verify CUDA
python3 -c "import torch; print(torch.cuda.is_available())"
```

#### Models Not Loading
```bash
# Check disk space
df -h

# Clear Hugging Face cache if needed
rm -rf ~/.cache/huggingface/
```

#### Port Already in Use
```bash
# Find what's using port 5000
sudo netstat -tulpn | grep :5000

# Kill the process
sudo kill -9 <PID>
```

#### Server Connection Issues
- Use `http://` not `https://` when accessing the server
- Make sure you're using the correct IP: `http://192.168.1.17:5000`
- Check firewall: `sudo ufw allow 5000` (if using ufw)

### Performance Optimization

#### For CPU-only systems:
- Use smaller models (whisper-tiny, DialoGPT-small)
- Reduce max_length in text generation
- Use basic TTS instead of neural TTS

#### For GPU systems:
- Install CUDA support
- Use larger models for better quality
- Enable mixed precision training

## 📊 System Requirements

### Minimum
- **RAM**: 4GB
- **Storage**: 5GB free space
- **CPU**: 2+ cores
- **Network**: 100 Mbps for model downloads

### Recommended
- **RAM**: 8GB+
- **Storage**: 10GB+ SSD
- **CPU**: 4+ cores
- **GPU**: NVIDIA GPU with 4GB+ VRAM (optional)

## 🔒 Security Notes

- The server binds to `0.0.0.0` for LAN access
- No authentication is implemented by default
- Consider adding HTTPS and authentication for production use
- Firewall rules should restrict access to trusted networks

## 📝 Development

### Project Structure
```
hf-test/
├── app.py              # Main Flask application
├── requirements.txt    # Python dependencies
├── setup.sh           # Installation script
├── templates/
│   └── index.html     # Web interface
└── README.md          # This file
```

### Adding Features
- Modify `app.py` for backend changes
- Update `templates/index.html` for UI changes
- Add dependencies to `requirements.txt`

