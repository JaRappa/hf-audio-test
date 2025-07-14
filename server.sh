#!/bin/bash

# AI Audio Pipeline Launcher Script
# Provides easy commands to manage the server

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

show_help() {
    echo "🎤 AI Audio Pipeline - Server Management"
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  start     - Start the AI audio pipeline server"
    echo "  test      - Run system tests"
    echo "  setup     - Run the setup script"
    echo "  status    - Check if server is running"
    echo "  stop      - Stop the server"
    echo "  logs      - Show server logs"
    echo "  install   - Install system dependencies"
    echo "  ip        - Show server IP addresses"
    echo "  help      - Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 start          # Start the server"
    echo "  $0 test           # Test the setup"
    echo "  $0 ip             # Find server IP for client connections"
}

start_server() {
    echo "🚀 Starting AI Audio Pipeline server..."
    
    # Check if already running
    if pgrep -f "python3.*app.py" > /dev/null; then
        echo "⚠️  Server is already running!"
        echo "Use '$0 stop' to stop it first."
        exit 1
    fi
    
    # Activate virtual environment if it exists
    if [ -f ".venv/bin/activate" ]; then
        echo "🔧 Activating virtual environment..."
        source .venv/bin/activate
    fi
    
    # Start the server
    echo "🔍 Testing setup first..."
    python3 test_setup.py --skip-models
    
    if [ $? -eq 0 ]; then
        echo "✅ Setup test passed!"
        echo "🎯 Starting server on http://0.0.0.0:5000"
        echo "💡 Use Ctrl+C to stop the server"
        echo ""
        python3 app.py
    else
        echo "❌ Setup test failed! Please run '$0 setup' first."
        exit 1
    fi
}

test_system() {
    echo "🧪 Running system tests..."
    
    # Activate virtual environment if it exists
    if [ -f ".venv/bin/activate" ]; then
        echo "🔧 Activating virtual environment..."
        source .venv/bin/activate
    fi
    
    python3 test_setup.py "$@"
}

run_setup() {
    echo "⚙️ Running setup script..."
    ./setup.sh
}

check_status() {
    if pgrep -f "python3.*app.py" > /dev/null; then
        echo "✅ AI Audio Pipeline server is running"
        echo "🌐 Server should be accessible at:"
        show_ips
    else
        echo "❌ Server is not running"
        echo "Use '$0 start' to start the server"
    fi
}

stop_server() {
    echo "🛑 Stopping AI Audio Pipeline server..."
    
    if pgrep -f "python3.*app.py" > /dev/null; then
        pkill -f "python3.*app.py"
        sleep 2
        
        if pgrep -f "python3.*app.py" > /dev/null; then
            echo "⚠️  Server still running, force killing..."
            pkill -9 -f "python3.*app.py"
        fi
        
        echo "✅ Server stopped"
    else
        echo "ℹ️  Server was not running"
    fi
}

show_logs() {
    echo "📋 Server logs (last 50 lines):"
    echo "================================"
    
    # If running as systemd service
    if systemctl is-active --quiet ai-audio-pipeline; then
        journalctl -u ai-audio-pipeline -n 50 --no-pager
    else
        echo "Server is not running as a systemd service."
        echo "Start with '$0 start' to see live logs."
    fi
}

install_deps() {
    echo "📦 Installing system dependencies..."
    
    # Update package database
    sudo pacman -Syu
    
    # Install required packages
    sudo pacman -S --needed \
        python python-pip git ffmpeg portaudio \
        espeak-ng alsa-utils pulseaudio pulseaudio-alsa
    
    echo "✅ System dependencies installed!"
    echo "Now run '$0 setup' to install Python packages and download models."
}

show_ips() {
    echo "🌐 Server IP addresses:"
    ip addr show | grep "inet " | grep -v 127.0.0.1 | while read line; do
        ip=$(echo $line | awk '{print $2}' | cut -d'/' -f1)
        interface=$(echo $line | awk '{print $NF}')
        echo "   http://$ip:5000 ($interface)"
    done
    echo ""
    echo "💡 Use any of these URLs from devices on your LAN"
}

# Main command handling
case "${1:-help}" in
    start)
        start_server
        ;;
    test)
        shift
        test_system "$@"
        ;;
    setup)
        run_setup
        ;;
    status)
        check_status
        ;;
    stop)
        stop_server
        ;;
    logs)
        show_logs
        ;;
    install)
        install_deps
        ;;
    ip)
        show_ips
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo "❌ Unknown command: $1"
        echo ""
        show_help
        exit 1
        ;;
esac
