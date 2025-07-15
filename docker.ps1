# Docker PowerShell management script for AI Audio Pipeline
# Windows-compatible version of docker.sh

param(
    [Parameter(Position=0)]
    [string]$Command = "help"
)

function Show-Help {
    Write-Host "🐳 AI Audio Pipeline - Docker Management (Windows)" -ForegroundColor Cyan
    Write-Host "Usage: .\docker.ps1 [COMMAND]" -ForegroundColor White
    Write-Host ""
    Write-Host "Commands:" -ForegroundColor Yellow
    Write-Host "  build     - Build the Docker image"
    Write-Host "  start     - Start the containers"
    Write-Host "  stop      - Stop the containers"
    Write-Host "  restart   - Restart the containers"
    Write-Host "  logs      - Show container logs"
    Write-Host "  status    - Show container status"
    Write-Host "  shell     - Open shell in running container"
    Write-Host "  clean     - Remove containers and images"
    Write-Host "  reset     - Clean everything and rebuild"
    Write-Host "  ip        - Show access URLs"
    Write-Host "  help      - Show this help message"
    Write-Host ""
    Write-Host "Examples:" -ForegroundColor Green
    Write-Host "  .\docker.ps1 start          # Start the AI pipeline"
    Write-Host "  .\docker.ps1 logs           # View logs"
    Write-Host "  .\docker.ps1 shell          # Debug inside container"
}

function Build-Image {
    Write-Host "🔨 Building AI Audio Pipeline Docker image..." -ForegroundColor Blue
    docker-compose build
}

function Start-Containers {
    Write-Host "🚀 Starting AI Audio Pipeline containers..." -ForegroundColor Green
    docker-compose up -d
    Write-Host "✅ Containers started!" -ForegroundColor Green
    Write-Host "🌐 Access the web interface at:" -ForegroundColor Cyan
    Show-URLs
}

function Stop-Containers {
    Write-Host "🛑 Stopping AI Audio Pipeline containers..." -ForegroundColor Red
    docker-compose down
    Write-Host "✅ Containers stopped!" -ForegroundColor Green
}

function Restart-Containers {
    Write-Host "🔄 Restarting AI Audio Pipeline containers..." -ForegroundColor Yellow
    docker-compose restart
    Write-Host "✅ Containers restarted!" -ForegroundColor Green
}

function Show-Logs {
    Write-Host "📋 AI Audio Pipeline logs:" -ForegroundColor Cyan
    Write-Host "==========================" -ForegroundColor Cyan
    docker-compose logs -f
}

function Show-Status {
    Write-Host "📊 Container status:" -ForegroundColor Cyan
    Write-Host "===================" -ForegroundColor Cyan
    docker-compose ps
    Write-Host ""
    Write-Host "💾 Volume usage:" -ForegroundColor Yellow
    docker volume ls | Select-String "ai-audio-pipeline"
    Write-Host ""
    Write-Host "🔧 Resource usage:" -ForegroundColor Yellow
    try {
        docker stats --no-stream ai-audio-pipeline
    }
    catch {
        Write-Host "Container not running" -ForegroundColor Red
    }
}

function Open-Shell {
    Write-Host "🐚 Opening shell in AI Audio Pipeline container..." -ForegroundColor Blue
    docker-compose exec ai-audio-pipeline /bin/bash
}

function Clean-Containers {
    Write-Host "🧹 Cleaning up containers and images..." -ForegroundColor Yellow
    $response = Read-Host "This will remove containers and images. Continue? (y/N)"
    if ($response -eq "y" -or $response -eq "Y") {
        docker-compose down --rmi all
        Write-Host "✅ Cleanup complete!" -ForegroundColor Green
    }
    else {
        Write-Host "❌ Cleanup cancelled" -ForegroundColor Red
    }
}

function Reset-Everything {
    Write-Host "🔥 Resetting everything (containers, images, volumes)..." -ForegroundColor Red
    $response = Read-Host "This will remove EVERYTHING including cached models. Continue? (y/N)"
    if ($response -eq "y" -or $response -eq "Y") {
        docker-compose down -v --rmi all
        Write-Host "🔨 Rebuilding..." -ForegroundColor Blue
        docker-compose up --build -d
        Write-Host "✅ Reset complete!" -ForegroundColor Green
        Show-URLs
    }
    else {
        Write-Host "❌ Reset cancelled" -ForegroundColor Red
    }
}

function Show-URLs {
    Write-Host "🌐 Access URLs:" -ForegroundColor Cyan
    Write-Host "   Local:   http://localhost:5000" -ForegroundColor White
    
    # Try to get host IP
    try {
        $hostIP = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.InterfaceAlias -notlike "*Loopback*" -and $_.InterfaceAlias -notlike "*Teredo*" } | Select-Object -First 1).IPAddress
        if ($hostIP) {
            Write-Host "   Network: http://$hostIP:5000" -ForegroundColor White
        }
    }
    catch {
        # Fallback method
        $hostIP = (ipconfig | Select-String "IPv4.*: (\d+\.\d+\.\d+\.\d+)" | ForEach-Object { $_.Matches[0].Groups[1].Value } | Select-Object -First 1)
        if ($hostIP) {
            Write-Host "   Network: http://$hostIP:5000" -ForegroundColor White
        }
    }
}

function Test-Health {
    Write-Host "🏥 Checking container health..." -ForegroundColor Blue
    
    # Check if container is running
    $containerStatus = docker-compose ps | Select-String "Up"
    if (-not $containerStatus) {
        Write-Host "❌ Container is not running" -ForegroundColor Red
        return $false
    }
    
    # Check health endpoint
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:5000/health" -UseBasicParsing -TimeoutSec 5
        if ($response.StatusCode -eq 200) {
            Write-Host "✅ Health check passed" -ForegroundColor Green
            return $true
        }
    }
    catch {
        Write-Host "⚠️  Health check failed - service may still be starting" -ForegroundColor Yellow
        return $false
    }
}

function Wait-ForService {
    Write-Host "⏳ Waiting for service to be ready..." -ForegroundColor Yellow
    $maxAttempts = 30
    $attempt = 1
    
    while ($attempt -le $maxAttempts) {
        if (Test-Health) {
            Write-Host "✅ Service is ready!" -ForegroundColor Green
            return $true
        }
        
        Write-Host "   Attempt $attempt/$maxAttempts - waiting..." -ForegroundColor Gray
        Start-Sleep -Seconds 2
        $attempt++
    }
    
    Write-Host "❌ Service failed to start within timeout" -ForegroundColor Red
    Write-Host "📋 Check logs with: .\docker.ps1 logs" -ForegroundColor Yellow
    return $false
}

# Main command handling
switch ($Command.ToLower()) {
    "build" {
        Build-Image
    }
    "start" {
        Start-Containers
        Wait-ForService
    }
    "stop" {
        Stop-Containers
    }
    "restart" {
        Restart-Containers
        Wait-ForService
    }
    "logs" {
        Show-Logs
    }
    "status" {
        Show-Status
    }
    "shell" {
        Open-Shell
    }
    "clean" {
        Clean-Containers
    }
    "reset" {
        Reset-Everything
    }
    { $_ -in "ip", "urls" } {
        Show-URLs
    }
    "health" {
        Test-Health
    }
    { $_ -in "help", "--help", "-h" } {
        Show-Help
    }
    default {
        Write-Host "❌ Unknown command: $Command" -ForegroundColor Red
        Write-Host ""
        Show-Help
        exit 1
    }
}
