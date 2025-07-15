@echo off
REM Quick Docker starter for Windows
REM AI Audio Pipeline

echo 🐳 AI Audio Pipeline - Docker Quick Start (Windows)
echo ================================================

REM Check if Docker is available
where docker >nul 2>nul
if errorlevel 1 (
    echo ❌ Docker not found!
    echo Please install Docker Desktop: https://docs.docker.com/desktop/windows/
    pause
    exit /b 1
)

REM Check if docker-compose.yml exists
if not exist "docker-compose.yml" (
    echo ❌ docker-compose.yml not found!
    echo Please run this script from the project directory.
    pause
    exit /b 1
)

echo ✅ Docker found, starting AI Audio Pipeline...
echo.
echo 📦 Building and starting containers...
echo This may take 10-20 minutes on first run (downloading models)
echo.

docker-compose up --build

echo.
echo 🛑 Containers stopped.
pause
