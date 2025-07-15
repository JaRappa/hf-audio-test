#!/usr/bin/env python3
"""
Docker setup verification script for AI Audio Pipeline
"""

import subprocess
import sys
import os

def check_docker():
    """Check if Docker is installed and running"""
    print("🐳 Checking Docker installation...")
    
    try:
        # Check Docker command
        result = subprocess.run(['docker', '--version'], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"✅ Docker found: {result.stdout.strip()}")
        else:
            print("❌ Docker command failed")
            return False
            
        # Check Docker Compose
        result = subprocess.run(['docker-compose', '--version'], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"✅ Docker Compose found: {result.stdout.strip()}")
        else:
            # Try docker compose (newer syntax)
            result = subprocess.run(['docker', 'compose', 'version'], capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                print(f"✅ Docker Compose found: {result.stdout.strip()}")
            else:
                print("❌ Docker Compose not found")
                return False
                
        # Check if Docker daemon is running
        result = subprocess.run(['docker', 'info'], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ Docker daemon is running")
            return True
        else:
            print("❌ Docker daemon is not running")
            print("   Please start Docker Desktop or Docker service")
            return False
            
    except FileNotFoundError:
        print("❌ Docker not found in PATH")
        print("   Please install Docker: https://docs.docker.com/get-docker/")
        return False
    except subprocess.TimeoutExpired:
        print("❌ Docker command timed out")
        return False
    except Exception as e:
        print(f"❌ Error checking Docker: {e}")
        return False

def check_files():
    """Check if required Docker files exist"""
    print("\n📁 Checking Docker configuration files...")
    
    required_files = [
        'Dockerfile',
        'docker-compose.yml',
        '.dockerignore',
        'requirements.txt',
        'app.py'
    ]
    
    missing_files = []
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file}")
        else:
            print(f"❌ {file} - missing")
            missing_files.append(file)
    
    return len(missing_files) == 0

def estimate_requirements():
    """Estimate system requirements"""
    print("\n💾 System Requirements Estimate:")
    print("   RAM: 4GB minimum, 8GB+ recommended")
    print("   Disk: 10GB+ free space (for models and images)")
    print("   Network: Internet connection for model downloads")
    print("   Time: First build ~10-20 minutes (downloading models)")

def show_quick_start():
    """Show quick start commands"""
    print("\n🚀 Quick Start Commands:")
    print("=" * 40)
    
    if os.name == 'nt':  # Windows
        print("Windows PowerShell:")
        print("   .\\docker.ps1 start     # Start the service")
        print("   .\\docker.ps1 logs      # View logs")
        print("   .\\docker.ps1 status    # Check status")
        print("   .\\docker.ps1 stop      # Stop the service")
        print("")
        print("Or using Docker Compose directly:")
        print("   docker-compose up --build")
    else:  # Linux/Mac
        print("Linux/Mac:")
        print("   ./docker.sh start       # Start the service")
        print("   ./docker.sh logs        # View logs")
        print("   ./docker.sh status      # Check status")
        print("   ./docker.sh stop        # Stop the service")
        print("")
        print("Or using Docker Compose directly:")
        print("   docker-compose up --build")
    
    print("\n🌐 Access URL: http://localhost:5000")

def main():
    """Run all checks"""
    print("🔍 AI Audio Pipeline - Docker Setup Verification")
    print("=" * 55)
    
    # Check Docker
    docker_ok = check_docker()
    
    # Check files
    files_ok = check_files()
    
    # Show requirements
    estimate_requirements()
    
    # Summary
    print("\n" + "=" * 55)
    if docker_ok and files_ok:
        print("✅ Docker setup verification passed!")
        print("🎯 Ready to build and run the AI Audio Pipeline")
        show_quick_start()
        return 0
    else:
        print("❌ Docker setup verification failed!")
        if not docker_ok:
            print("   - Install and start Docker")
        if not files_ok:
            print("   - Ensure you're in the correct directory")
            print("   - Check if all Docker files were created")
        return 1

if __name__ == "__main__":
    sys.exit(main())
