#!/usr/bin/env python3
"""
AI Audio Pipeline Server with AWS Bedrock Integration
Handles audio transcription, text generation via AWS, and text-to-speech
Uses AWS Bedrock for text generation, local models for audio processing
"""

import os
import io
import json
import base64
import tempfile
import logging
from pathlib import Path
from flask import Flask, request, jsonify, render_template, send_file
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import torch
from transformers import (
    WhisperProcessor, WhisperForConditionalGeneration
)
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
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
        
        # Initialize AWS Bedrock client for text generation
        self.setup_aws_client()
        
    def setup_aws_client(self):
        """Initialize AWS Bedrock client for text generation"""
        try:
            # Initialize Bedrock client
            self.bedrock_client = boto3.client(
                'bedrock-runtime',
                region_name=os.getenv('AWS_REGION', 'us-east-1')
            )
            
            # Test connection
            self.test_aws_connection()
            self.aws_available = True
            logger.info("✅ AWS Bedrock client initialized successfully!")
            
        except NoCredentialsError:
            logger.warning("❌ AWS credentials not found. Please configure AWS credentials.")
            logger.warning("   You can set up credentials using:")
            logger.warning("   1. AWS CLI: aws configure")
            logger.warning("   2. Environment variables: AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY")
            logger.warning("   3. IAM roles (if running on EC2)")
            self.aws_available = False
            
        except Exception as e:
            logger.warning(f"❌ AWS Bedrock initialization failed: {e}")
            logger.warning("   Falling back to simple response generation")
            self.aws_available = False
    
    def test_aws_connection(self):
        """Test AWS Bedrock connection"""
        try:
            # Try a minimal test with Claude
            response = self.bedrock_client.invoke_model(
                modelId='anthropic.claude-3-haiku-20240307-v1:0',
                body=json.dumps({
                    "anthropic_version": "bedrock-2023-05-15",
                    "max_tokens": 10,
                    "messages": [{"role": "user", "content": "test"}]
                })
            )
            logger.info("AWS Bedrock connection test successful")
        except Exception as e:
            logger.warning(f"AWS Bedrock connection test failed: {e}")
            raise e
        
    def load_models(self):
        """Load local AI models (Whisper for STT, keep TTS local)"""
        logger.info("Loading local AI models...")
        
        # Load Whisper for speech-to-text (keeping local for better privacy/speed)
        logger.info("Loading Whisper model...")
        self.whisper_processor = WhisperProcessor.from_pretrained("openai/whisper-base")
        self.whisper_model = WhisperForConditionalGeneration.from_pretrained("openai/whisper-base")
        self.whisper_model.to(self.device)
        
        # Remove local language model loading since we're using AWS
        logger.info("Text generation will use AWS Bedrock")
        
        # Initialize TTS (keeping local)
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
        
        logger.info("Local models loaded successfully!")
    
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
        """Generate AI response using AWS Bedrock or fallback to simple response"""
        try:
            if self.aws_available:
                return self.generate_aws_response(text)
            else:
                return self.generate_fallback_response(text)
        
        except Exception as e:
            logger.error(f"Response generation error: {e}")
            return "I'm sorry, I couldn't process that request at the moment."
    
    def generate_aws_response(self, text):
        """Generate response using AWS Bedrock Claude model"""
        try:
            # Prepare the prompt for Claude
            prompt = f"""You are a helpful AI assistant. Please respond to the following message in a conversational and helpful manner. Keep your response concise but informative.

User: {text}
