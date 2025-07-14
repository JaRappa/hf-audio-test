#!/usr/bin/env python3
"""
AI Audio Pipeline Server
Handles audio transcription, text generation, and text-to-speech
"""

import os
import io
import base64
import tempfile
import logging
from pathlib import Path
from flask import Flask, request, jsonify, render_template, send_file
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import torch
from transformers import (
    AutoTokenizer, AutoModelForCausalLM,
    WhisperProcessor, WhisperForConditionalGeneration,
    pipeline
)
from gtts import gTTS
import librosa
import soundfile as sf
import numpy as np
from pydub import AudioSegment

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

class AudioPipeline:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Using device: {self.device}")
        
        # Initialize models
        self.load_models()
        
    def load_models(self):
        """Load all AI models"""
        logger.info("Loading AI models...")
        
        # Load Whisper for speech-to-text
        logger.info("Loading Whisper model...")
        self.whisper_processor = WhisperProcessor.from_pretrained("openai/whisper-base")
        self.whisper_model = WhisperForConditionalGeneration.from_pretrained("openai/whisper-base")
        self.whisper_model.to(self.device)
        
        # Load language model for text generation
        logger.info("Loading language model...")
        self.tokenizer = AutoTokenizer.from_pretrained("microsoft/DialoGPT-medium")
        self.language_model = AutoModelForCausalLM.from_pretrained("microsoft/DialoGPT-medium")
        self.language_model.to(self.device)
        
        # Add padding token if it doesn't exist
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        
        # Initialize TTS
        logger.info("Loading TTS model...")
        try:
            # Using gTTS (Google Text-to-Speech) as it's Python 3.13 compatible
            # Test gTTS availability
            test_tts = gTTS(text="test", lang='en')
            self.tts_available = True
            logger.info("gTTS (Google Text-to-Speech) initialized successfully!")
        except Exception as e:
            logger.warning(f"Could not initialize gTTS: {e}. TTS will be disabled.")
            self.tts_available = False
        
        logger.info("All models loaded successfully!")
    
    def transcribe_audio(self, audio_data, sample_rate=16000):
        """Convert audio to text using Whisper"""
        try:
            # Ensure audio is the right format
            if len(audio_data.shape) > 1:
                audio_data = librosa.to_mono(audio_data.T)
            
            # Resample if necessary
            if sample_rate != 16000:
                audio_data = librosa.resample(audio_data, orig_sr=sample_rate, target_sr=16000)
            
            # Process with Whisper
            input_features = self.whisper_processor(
                audio_data, 
                sampling_rate=16000, 
                return_tensors="pt"
            ).input_features.to(self.device)
            
            # Generate transcription
            with torch.no_grad():
                predicted_ids = self.whisper_model.generate(input_features)
                transcription = self.whisper_processor.batch_decode(
                    predicted_ids, skip_special_tokens=True
                )[0]
            
            return transcription.strip()
        
        except Exception as e:
            logger.error(f"Transcription error: {e}")
            return ""
    
    def generate_response(self, text):
        """Generate AI response using language model"""
        try:
            # Encode the input text
            inputs = self.tokenizer.encode(text + self.tokenizer.eos_token, return_tensors="pt")
            inputs = inputs.to(self.device)
            
            # Generate response
            with torch.no_grad():
                outputs = self.language_model.generate(
                    inputs,
                    max_length=inputs.shape[1] + 100,
                    num_beams=5,
                    early_stopping=True,
                    temperature=0.7,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id
                )
            
            # Decode the response
            response = self.tokenizer.decode(outputs[0][inputs.shape[1]:], skip_special_tokens=True)
            return response.strip()
        
        except Exception as e:
            logger.error(f"Response generation error: {e}")
            return "I'm sorry, I couldn't process that request."
    
    def text_to_speech(self, text):
        """Convert text to speech using gTTS"""
        try:
            if not self.tts_available:
                logger.warning("TTS not available")
                return None
            
            # Create gTTS object
            tts = gTTS(text=text, lang='en', slow=False)
            
            # Create temporary file for audio output
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp_file:
                temp_path = tmp_file.name
            
            # Save to temporary file
            tts.save(temp_path)
            
            # Convert MP3 to WAV for better compatibility
            audio = AudioSegment.from_mp3(temp_path)
            wav_path = temp_path.replace('.mp3', '.wav')
            audio.export(wav_path, format="wav")
            
            # Read the WAV file
            with open(wav_path, "rb") as f:
                audio_data = f.read()
            
            # Clean up
            os.unlink(temp_path)
            os.unlink(wav_path)
            
            return audio_data
        
        except Exception as e:
            logger.error(f"TTS error: {e}")
            return None

# Initialize the pipeline
pipeline = AudioPipeline()

@app.route('/')
def index():
    """Serve the main web interface"""
    return render_template('index.html')

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "device": pipeline.device})

@app.route('/process_audio', methods=['POST'])
def process_audio():
    """Process audio through the complete pipeline"""
    try:
        # Get audio file from request
        if 'audio' not in request.files:
            return jsonify({"error": "No audio file provided"}), 400
        
        audio_file = request.files['audio']
        
        # Read the file data
        file_data = audio_file.read()
        
        # Convert audio to a standard format using pydub
        # This handles many different audio formats (mp3, wav, m4a, etc.)
        try:
            # Try to load with pydub first (handles more formats)
            audio_segment = AudioSegment.from_file(io.BytesIO(file_data))
            
            # Convert to WAV format for librosa
            wav_data = io.BytesIO()
            audio_segment.export(wav_data, format="wav")
            wav_data.seek(0)
            
            # Now load with librosa
            audio_data, sample_rate = librosa.load(wav_data, sr=None)
            
        except Exception as e:
            logger.error(f"Error converting audio format: {e}")
            # Fallback: try librosa directly
            try:
                audio_data, sample_rate = librosa.load(io.BytesIO(file_data), sr=None)
            except Exception as e2:
                logger.error(f"Fallback also failed: {e2}")
                return jsonify({"error": f"Could not process audio format: {str(e)}"}), 400
        
        # Step 1: Transcribe audio to text
        logger.info("Transcribing audio...")
        transcription = pipeline.transcribe_audio(audio_data, sample_rate)
        logger.info(f"Transcription: {transcription}")
        
        if not transcription:
            return jsonify({"error": "Could not transcribe audio"}), 400
        
        # Step 2: Generate AI response
        logger.info("Generating response...")
        response_text = pipeline.generate_response(transcription)
        logger.info(f"Response: {response_text}")
        
        # Step 3: Convert response to speech
        logger.info("Converting to speech...")
        audio_response = pipeline.text_to_speech(response_text)
        
        result = {
            "transcription": transcription,
            "response_text": response_text,
            "audio_available": audio_response is not None
        }
        
        if audio_response:
            # Encode audio as base64 for JSON response
            audio_b64 = base64.b64encode(audio_response).decode('utf-8')
            result["audio_data"] = audio_b64
        
        return jsonify(result)
    
    except Exception as e:
        logger.error(f"Processing error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/test_response.html')
def test_response():
    """Serve the test response page"""
    return send_file('test_response.html')

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    logger.info("Client connected")
    emit('status', {'message': 'Connected to AI pipeline server'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    logger.info("Client disconnected")

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    
    # Start the server
    logger.info("Starting AI Pipeline Server...")
    socketio.run(app, host='0.0.0.0', port=5000, debug=False)
