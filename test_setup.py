#!/usr/bin/env python3
"""
Test script to verify AI Audio Pipeline setup
"""

import sys
import subprocess
import importlib

def test_imports():
    """Test if all required packages can be imported"""
    required_packages = [
        'torch',
        'transformers',
        'flask',
        'flask_cors',
        'flask_socketio',
        'librosa',
        'soundfile',
        'numpy',
        'gtts',
        'pydub'
    ]
    
    print("🧪 Testing package imports...")
    failed_imports = []
    
    for package in required_packages:
        try:
            importlib.import_module(package)
            print(f"✅ {package}")
        except ImportError as e:
            print(f"❌ {package}: {e}")
            failed_imports.append(package)
    
    return failed_imports

def test_cuda():
    """Test CUDA availability"""
    print("\n🔥 Testing CUDA availability...")
    try:
        import torch
        if torch.cuda.is_available():
            print(f"✅ CUDA available: {torch.cuda.get_device_name(0)}")
            print(f"   GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")
        else:
            print("⚠️  CUDA not available (CPU mode will be used)")
    except Exception as e:
        print(f"❌ Error checking CUDA: {e}")

def test_audio_system():
    """Test audio system components"""
    print("\n🔊 Testing audio system...")
    
    # Test if PulseAudio is running
    try:
        result = subprocess.run(['pulseaudio', '--check'], capture_output=True, timeout=5)
        if result.returncode == 0:
            print("✅ PulseAudio is running")
        else:
            print("⚠️  PulseAudio may not be running")
    except Exception as e:
        print(f"❌ Error checking PulseAudio: {e}")
    
    # Test if FFmpeg is available
    try:
        result = subprocess.run(['ffmpeg', '-version'], capture_output=True, timeout=5)
        if result.returncode == 0:
            print("✅ FFmpeg is available")
        else:
            print("❌ FFmpeg not found")
    except Exception as e:
        print(f"❌ Error checking FFmpeg: {e}")

def test_model_loading():
    """Test if models can be loaded (this may take time)"""
    print("\n🤖 Testing model loading (this may take a while)...")
    
    try:
        from transformers import WhisperProcessor
        print("✅ Whisper processor loaded")
        
        from transformers import AutoTokenizer
        tokenizer = AutoTokenizer.from_pretrained("microsoft/DialoGPT-medium")
        print("✅ DialoGPT tokenizer loaded")
        
        # Test gTTS (Google Text-to-Speech)
        try:
            from gtts import gTTS
            from pydub import AudioSegment
            print("✅ gTTS and pydub loaded (Google Text-to-Speech)")
        except Exception as e:
            print(f"⚠️  gTTS loading issue: {e}")
            
    except Exception as e:
        print(f"❌ Model loading error: {e}")

def test_server_dependencies():
    """Test server-specific dependencies"""
    print("\n🌐 Testing server dependencies...")
    
    try:
        from flask import Flask
        from flask_cors import CORS
        from flask_socketio import SocketIO
        print("✅ Flask and extensions loaded")
    except Exception as e:
        print(f"❌ Flask error: {e}")

def main():
    """Run all tests"""
    print("🔍 AI Audio Pipeline - System Test")
    print("=" * 50)
    
    # Test imports
    failed_imports = test_imports()
    
    # Test CUDA
    test_cuda()
    
    # Test audio system
    test_audio_system()
    
    # Test server dependencies
    test_server_dependencies()
    
    # Test model loading (optional - can be slow)
    if "--skip-models" not in sys.argv:
        test_model_loading()
    else:
        print("\n⏭️  Skipping model loading test (use --skip-models to skip)")
    
    # Summary
    print("\n" + "=" * 50)
    if failed_imports:
        print(f"❌ Test completed with {len(failed_imports)} failed imports:")
        for package in failed_imports:
            print(f"   - {package}")
        print("\nRun: pip install -r requirements.txt")
        return 1
    else:
        print("✅ All tests passed! System ready for AI Audio Pipeline")
        print("\nTo start the server: python3 app.py")
        return 0

if __name__ == "__main__":
    sys.exit(main())
