#!/bin/bash

# Docker management script for AI Audio Pipeline
# Provides easy commands to manage the Docker containers

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

show_help() {
    echo "🐳 AI Audio Pipeline - Docker Management"
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  build     - Build the Docker image"
    echo "  start     - Start the containers"
    echo "  stop      - Stop the containers"
    echo "  restart   - Restart the containers"
    echo "  logs      - Show container logs"
    echo "  status    - Show container status"
    echo "  shell     - Open shell in running container"
    echo "  clean     - Remove containers and images"
    echo "  reset     - Clean everything and rebuild"
    echo "  ip        - Show access URLs"
    echo "  help      - Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 start          # Start the AI pipeline"
    echo "  $0 logs           # View logs"
    echo "  $0 shell          # Debug inside container"
}

build_image() {
    echo "🔨 Building AI Audio Pipeline Docker image..."
    docker-compose build
}

start_containers() {
    echo "🚀 Starting AI Audio Pipeline containers..."
    docker-compose up -d
    echo "✅ Containers started!"
    echo "🌐 Access the web interface at:"
    show_urls
}

stop_containers() {
    echo "🛑 Stopping AI Audio Pipeline containers..."
    docker-compose down
    echo "✅ Containers stopped!"
}

restart_containers() {
    echo "🔄 Restarting AI Audio Pipeline containers..."
    docker-compose restart
    echo "✅ Containers restarted!"
}

show_logs() {
    echo "📋 AI Audio Pipeline logs:"
    echo "=========================="
    docker-compose logs -f
}

show_status() {
    echo "📊 Container status:"
    echo "==================="
    docker-compose ps
    echo ""
    echo "💾 Volume usage:"
    docker volume ls | grep ai-audio-pipeline
    echo ""
    echo "🔧 Resource usage:"
    docker stats --no-stream ai-audio-pipeline 2>/dev/null || echo "Container not running"
}

open_shell() {
    echo "🐚 Opening shell in AI Audio Pipeline container..."
    docker-compose exec ai-audio-pipeline /bin/bash
}

clean_containers() {
    echo "🧹 Cleaning up containers and images..."
    read -p "This will remove containers and images. Continue? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        docker-compose down --rmi all
        echo "✅ Cleanup complete!"
    else
        echo "❌ Cleanup cancelled"
    fi
}

reset_everything() {
    echo "🔥 Resetting everything (containers, images, volumes)..."
    read -p "This will remove EVERYTHING including cached models. Continue? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        docker-compose down -v --rmi all
        echo "🔨 Rebuilding..."
        docker-compose up --build -d
        echo "✅ Reset complete!"
        show_urls
    else
        echo "❌ Reset cancelled"
    fi
}

show_urls() {
    echo "🌐 Access URLs:"
    echo "   Local:   http://localhost:5000"
    
    # Try to get host IP
    if command -v hostname &> /dev/null; then
        host_ip=$(hostname -I | awk '{print $1}' 2>/dev/null)
        if [ ! -z "$host_ip" ]; then
            echo "   Network: http://$host_ip:5000"
        fi
    fi
    
    # For Windows/WSL
    if command -v ipconfig.exe &> /dev/null; then
        win_ip=$(ipconfig.exe | grep -A 4 "WSL" | grep "IPv4" | awk '{print $NF}' | tr -d '\r' 2>/dev/null)
        if [ ! -z "$win_ip" ]; then
            echo "   WSL:     http://$win_ip:5000"
        fi
    fi
}

# Health check function
check_health() {
    echo "🏥 Checking container health..."
    
    # Check if container is running
    if ! docker-compose ps | grep -q "Up"; then
        echo "❌ Container is not running"
        return 1
    fi
    
    # Check health endpoint
    if curl -f http://localhost:5000/health >/dev/null 2>&1; then
        echo "✅ Health check passed"
        return 0
    else
        echo "⚠️  Health check failed - service may still be starting"
        return 1
    fi
}

# Wait for service to be ready
wait_for_service() {
    echo "⏳ Waiting for service to be ready..."
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if check_health >/dev/null 2>&1; then
            echo "✅ Service is ready!"
            return 0
        fi
        
        echo "   Attempt $attempt/$max_attempts - waiting..."
        sleep 2
        ((attempt++))
    done
    
    echo "❌ Service failed to start within timeout"
    echo "📋 Check logs with: $0 logs"
    return 1
}

# Main command handling
case "${1:-help}" in
    build)
        build_image
        ;;
    start)
        start_containers
        wait_for_service
        ;;
    stop)
        stop_containers
        ;;
    restart)
        restart_containers
        wait_for_service
        ;;
    logs)
        show_logs
        ;;
    status)
        show_status
        ;;
    shell)
        open_shell
        ;;
    clean)
        clean_containers
        ;;
    reset)
        reset_everything
        ;;
    ip|urls)
        show_urls
        ;;
    health)
        check_health
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
