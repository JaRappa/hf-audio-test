#!/usr/bin/env python3
"""
Quick troubleshooting script for AI Audio Pipeline Docker deployment
"""

import subprocess
import sys
import time
import requests

def check_docker_status():
    """Check Docker container status"""
    print("🔍 Checking Docker container status...")
    
    try:
        # Check if container is running
        result = subprocess.run(['docker', 'ps'], capture_output=True, text=True, timeout=10)
        if 'ai-audio-pipeline' in result.stdout:
            print("✅ Container is running")
            return True
        else:
            print("❌ Container is not running")
            
            # Check if container exists but stopped
            result = subprocess.run(['docker', 'ps', '-a'], capture_output=True, text=True, timeout=10)
            if 'ai-audio-pipeline' in result.stdout:
                print("⚠️  Container exists but is stopped")
                return False
            else:
                print("❌ Container doesn't exist")
                return False
                
    except Exception as e:
        print(f"❌ Error checking Docker: {e}")
        return False

def check_container_logs():
    """Check container logs for errors"""
    print("\n📋 Checking container logs...")
    
    try:
        result = subprocess.run(['docker', 'logs', 'ai-audio-pipeline', '--tail', '20'], 
                              capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("Recent logs:")
            print("-" * 40)
            print(result.stdout)
            if result.stderr:
                print("Errors:")
                print(result.stderr)
            print("-" * 40)
        else:
            print("❌ Could not retrieve logs")
            
    except Exception as e:
        print(f"❌ Error checking logs: {e}")

def test_health_endpoint():
    """Test the health endpoint"""
    print("\n🏥 Testing health endpoint...")
    
    max_attempts = 5
    for attempt in range(1, max_attempts + 1):
        try:
            response = requests.get('http://localhost:5000/health', timeout=5)
            if response.status_code == 200:
                print(f"✅ Health check passed: {response.json()}")
                return True
            else:
                print(f"⚠️  Health check returned status {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            print(f"❌ Attempt {attempt}/{max_attempts}: Connection refused")
        except requests.exceptions.Timeout:
            print(f"⚠️  Attempt {attempt}/{max_attempts}: Request timed out")
        except Exception as e:
            print(f"❌ Attempt {attempt}/{max_attempts}: {e}")
        
        if attempt < max_attempts:
            print("   Waiting 10 seconds before retry...")
            time.sleep(10)
    
    print("❌ Health check failed after all attempts")
    return False

def suggest_fixes():
    """Suggest common fixes"""
    print("\n🔧 Common Fixes:")
    print("=" * 40)
    print("1. If container is not running:")
    print("   docker-compose up -d")
    print("")
    print("2. If container name conflict:")
    print("   docker rm ai-audio-pipeline")
    print("   docker-compose up -d")
    print("")
    print("3. If models are still loading (first run):")
    print("   docker logs ai-audio-pipeline -f")
    print("   (Wait 5-10 minutes for model download)")
    print("")
    print("4. If persistent issues:")
    print("   docker-compose down")
    print("   docker-compose up --build")
    print("")
    print("5. Reset everything:")
    print("   docker-compose down -v --rmi all")
    print("   docker-compose up --build")

def main():
    """Run troubleshooting checks"""
    print("🐳 AI Audio Pipeline - Docker Troubleshooting")
    print("=" * 50)
    
    # Check Docker status
    container_running = check_docker_status()
    
    # Check logs regardless of status
    check_container_logs()
    
    if container_running:
        # Test health endpoint
        health_ok = test_health_endpoint()
        
        if health_ok:
            print("\n✅ All checks passed! Service is healthy.")
            print("🌐 Access the web interface at: http://localhost:5000")
            return 0
        else:
            print("\n⚠️  Container is running but service is not responding")
    else:
        print("\n❌ Container is not running")
    
    suggest_fixes()
    return 1

if __name__ == "__main__":
    sys.exit(main())
