@echo off
REM Windows FFmpeg installer for AI Audio Pipeline
REM This script helps install FFmpeg on Windows

echo 🎵 AI Audio Pipeline - FFmpeg Setup for Windows
echo =================================================
echo.

echo FFmpeg is required for audio processing in the AI Audio Pipeline.
echo.

echo 📋 Installation Options:
echo.

echo Option 1: Download FFmpeg manually (RECOMMENDED)
echo -------------------------------------------------
echo 1. Go to: https://ffmpeg.org/download.html#build-windows
echo 2. Download "Windows builds by BtbN" (essentials build)
echo 3. Extract the zip file to C:\ffmpeg
echo 4. Add C:\ffmpeg\bin to your PATH environment variable
echo.

echo Option 2: Using Chocolatey (if installed)
echo -------------------------------------------
echo If you have Chocolatey installed, run:
echo choco install ffmpeg
echo.

echo Option 3: Using winget (Windows 10/11)
echo ---------------------------------------
echo If you have winget available, run:
echo winget install Gyan.FFmpeg
echo.

echo 🔧 Adding to PATH:
echo ==================
echo 1. Open System Properties (Windows key + Pause)
echo 2. Click "Advanced system settings"
echo 3. Click "Environment Variables"
echo 4. Under "System Variables", find and select "Path"
echo 5. Click "Edit" then "New"
echo 6. Add: C:\ffmpeg\bin
echo 7. Click OK to save
echo.

echo 🧪 Testing Installation:
echo ========================
echo After installation, test with:
echo ffmpeg -version
echo.

echo 💡 Alternative: Use Docker
echo ===========================
echo If FFmpeg installation is problematic, consider using Docker:
echo .\docker.ps1 start
echo.
echo Docker includes all dependencies pre-installed.
echo.

echo ⚠️  Note: You may need to restart your command prompt
echo or VS Code after adding FFmpeg to PATH.
echo.

pause
