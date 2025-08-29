@echo off
chcp 65001 >nul
REM SyncAI Lightweight Installation Script (No AI Model)
REM This script installs SyncAI without AI model dependencies

setlocal enabledelayedexpansion

echo.
echo =====================================
echo   SyncAI Lightweight Installation
echo =====================================
echo.
echo This script will:
echo 1. Clone project repository (if needed)
echo 2. Install Docker (if needed)
echo 3. Deploy lightweight version
echo 4. Setup control scripts
echo.
echo NOTE: This version does not include AI model features
echo.
pause

REM Get script directory and project root
set SCRIPT_DIR=%~dp0
set PROJECT_ROOT=%SCRIPT_DIR%..

REM =====================================
REM 1. Git Clone Repository
REM =====================================
echo.
echo [Step 1/4] Checking project repository...

set "REPO_URL=https://github.com/UIE47061/SyncAI.git"
set "PROJECT_NAME=SyncAI"

REM Check if we're already in SyncAI directory
if exist "package.json" if exist "backend" if exist "frontend" (
    echo [SUCCESS] Already in SyncAI project directory
    set "PROJECT_ROOT=%CD%"
    goto :check_docker
)

REM Check if SyncAI directory exists in current location
if exist "%PROJECT_NAME%" (
    echo [INFO] Found existing SyncAI directory
    cd /d "%PROJECT_NAME%"
    set "PROJECT_ROOT=%CD%"
    goto :check_docker
)

REM Check if git is installed
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Git not found, please install Git first:
    echo https://git-scm.com/download/win
    echo.
    pause
    exit /b 1
)

echo [INFO] Cloning SyncAI repository...
git clone %REPO_URL%
if %errorlevel% neq 0 (
    echo [ERROR] Repository clone failed
    pause
    exit /b 1
)

cd /d "%PROJECT_NAME%"
set "PROJECT_ROOT=%CD%"

:check_docker
echo [SUCCESS] Project repository ready

REM =====================================
REM 2. Check/Install Docker
REM =====================================
echo.
echo [Step 2/4] Checking Docker installation...

docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARNING] Docker not installed
    echo [INFO] Attempting to install Docker automatically...
    echo.
    
    call "%SCRIPT_DIR%install_docker.bat"
    if %errorlevel% neq 0 (
        echo [ERROR] Docker installation failed
        echo Please install Docker manually and restart this script
        pause
        exit /b 1
    )
    
    echo [INFO] Docker installation completed
    echo [INFO] Please restart your computer and run this script again
    pause
    exit /b 0
)

docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARNING] Docker Compose not installed
    echo Docker Compose is usually installed with Docker Desktop
    echo Please ensure Docker Desktop is properly installed
    pause
    exit /b 1
)

echo [SUCCESS] Docker installed and available

REM Check if Docker daemon is running
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARNING] Docker service not running
    echo Please start Docker Desktop and restart this script
    pause
    exit /b 1
)

echo [SUCCESS] Docker service is running

REM =====================================
REM 3. Docker Deployment (Lightweight)
REM =====================================
echo.
echo [Step 3/4] Docker deployment (lightweight version)...

REM Create a lightweight docker-compose override
echo [INFO] Creating lightweight configuration...
(
echo version: '3.8'^

echo services:
echo   backend:
echo     environment:
echo       - AI_MODEL_ENABLED=false
echo       - LIGHTWEIGHT_MODE=true
echo   frontend:
echo     environment:
echo       - REACT_APP_AI_FEATURES=false
) > docker/docker-compose.lightweight.yml

REM Stop existing containers
echo [INFO] Stopping existing containers...
docker-compose -f docker/docker-compose.yml -f docker/docker-compose.lightweight.yml down 2>nul

REM Build and start services
echo [INFO] Building and starting lightweight services...
echo This may take several minutes to download images and build containers...
docker-compose -f docker/docker-compose.yml -f docker/docker-compose.lightweight.yml up -d --build

if %errorlevel% neq 0 (
    echo [ERROR] Docker deployment failed
    echo Please check error messages and retry
    pause
    exit /b 1
)

REM Wait for services to start
echo [INFO] Waiting for services to start...
timeout /t 10 /nobreak >nul

REM Check if containers are running
docker-compose -f docker/docker-compose.yml -f docker/docker-compose.lightweight.yml ps
echo [SUCCESS] Lightweight deployment completed

REM =====================================
REM 4. Setup Control Scripts
REM =====================================
echo.
echo [Step 4/4] Setting up control scripts...

REM Create lightweight control scripts
echo [INFO] Creating lightweight control scripts...

REM Create start script
(
echo @echo off
echo chcp 65001 ^>nul
echo echo Starting SyncAI lightweight services...
echo cd /d "%PROJECT_ROOT%"
echo docker-compose -f docker/docker-compose.yml -f docker/docker-compose.lightweight.yml up -d
echo echo Services started!
echo echo Frontend: http://localhost
echo echo Backend:  http://localhost:8000
echo pause
) > "%PROJECT_ROOT%\start_lightweight.bat"

REM Create stop script
(
echo @echo off
echo chcp 65001 ^>nul
echo echo Stopping SyncAI lightweight services...
echo cd /d "%PROJECT_ROOT%"
echo docker-compose -f docker/docker-compose.yml -f docker/docker-compose.lightweight.yml down
echo echo Services stopped!
echo pause
) > "%PROJECT_ROOT%\stop_lightweight.bat"

REM Create status script
(
echo @echo off
echo chcp 65001 ^>nul
echo echo SyncAI lightweight service status:
echo cd /d "%PROJECT_ROOT%"
echo docker-compose -f docker/docker-compose.yml -f docker/docker-compose.lightweight.yml ps
echo echo.
echo echo Service logs:
echo docker-compose -f docker/docker-compose.yml -f docker/docker-compose.lightweight.yml logs --tail=20
echo pause
) > "%PROJECT_ROOT%\status_lightweight.bat"

echo Created the following lightweight control scripts:
echo.
echo   📂 start_lightweight.bat    - Start lightweight services
echo   📂 stop_lightweight.bat     - Stop lightweight services
echo   📂 status_lightweight.bat   - View service status
echo.

REM Show access information
echo.
echo =====================================
echo        Access Information
echo =====================================

REM Get local IP addresses
echo [Available Access URLs]
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /i "IPv4"') do (
    for /f "tokens=1" %%b in ("%%a") do (
        set "ip=%%b"
        set "ip=!ip: =!"
        if not "!ip!"=="127.0.0.1" (
            echo   Frontend: http://!ip!
            echo   Backend:  http://!ip!:8000
            echo.
        )
    )
)

echo [Local Access]
echo   Frontend: http://localhost
echo   Backend:  http://localhost:8000
echo.

echo =====================================
echo      Usage Instructions
echo =====================================
echo.
echo 🚀 Quick Start:
echo   Double-click start_lightweight.bat to start services
echo   Open browser to http://localhost
echo.
echo 🛑 Stop Services:
echo   Double-click stop_lightweight.bat
echo.
echo 📊 Check Status:
echo   Double-click status_lightweight.bat
echo.
echo 💡 Features Available:
echo   - Meeting room management
echo   - Participant management
echo   - Real-time chat
echo   - Screen sharing (without AI)
echo.
echo ⚠️  Note: AI-powered features are disabled in lightweight mode
echo.

echo =====================================
echo   Lightweight Installation Complete! 🎉
echo =====================================
echo.
echo Press any key to exit installation...
pause >nul

exit /b 0
