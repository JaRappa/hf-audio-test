#!/usr/bin/env python3
"""
Quick test script for the AI Audio Pipeline
Creates a test audio file and sends it to the server
"""

import sys
import requests
import tempfile
from gtts import gTTS
import time

def test_pipeline():
    """Test the complete audio pipeline"""
    print("🧪 Testing AI Audio Pipeline...")
    
    # Check if server is running
    try:
        response = requests.get("http://localhost:5000/health", timeout=5)
        if response.status_code == 200:
            print("✅ Server is running")
            print(f"   Device: {response.json().get('device', 'unknown')}")
        else:
            print("❌ Server health check failed")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to server: {e}")
        print("   Make sure the server is running: python3 app.py")
        return False
    
    # Create test audio
    print("🎤 Creating test audio...")
    test_text = "Hello, this is a test of the AI audio pipeline."
    
    try:
        tts = gTTS(text=test_text, lang='en')
        
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as tmp_file:
            temp_path = tmp_file.name
            tts.save(temp_path)
        
        print(f"✅ Test audio created: {temp_path}")
        
        # Send to server
        print("📤 Sending audio to server...")
        
        with open(temp_path, 'rb') as f:
            files = {'audio': ('test.mp3', f, 'audio/mpeg')}
            response = requests.post("http://localhost:5000/process_audio", files=files, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Server processed audio successfully!")
            print(f"   Transcription: '{result.get('transcription', 'N/A')}'")
            print(f"   AI Response: '{result.get('response_text', 'N/A')}'")
            print(f"   Audio Generated: {result.get('audio_available', False)}")
            return True
        else:
            print(f"❌ Server returned error: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False
    
    finally:
        # Clean up
        try:
            import os
            if 'temp_path' in locals():
                os.unlink(temp_path)
        except:
            pass

def main():
    print("🎤 AI Audio Pipeline - Quick Test")
    print("=" * 40)
    
    success = test_pipeline()
    
    print("\n" + "=" * 40)
    if success:
        print("✅ All tests passed! The AI Audio Pipeline is working correctly.")
        print(f"🌐 Web interface: http://192.168.1.17:5000")
    else:
        print("❌ Tests failed. Check the troubleshooting section in README.md")
        
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
