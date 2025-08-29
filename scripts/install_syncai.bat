@echo off
chcp 65001 >nul
REM SyncAI One-Click Installation Script for Windows
REM This script will automatically:
REM 1. Clone the repository (if needed)
REM 2. Download AI model
REM 3. Install Docker (if needed)
REM 4. Deploy with Docker
REM 5. Show IP addresses
REM 6. Provide control commands

setlocal enabledelayedexpansion

echo.
echo =====================================
echo    SyncAI One-Click Installation
echo =====================================
echo.
echo This script will:
echo 1. Clone project repository (if needed)
echo 2. Prepare AI model
echo 3. Install Docker (if needed)
echo 4. Docker deployment
echo 5. Query and display IP addresses
echo 6. Provide meeting room control commands
echo.
pause

REM =====================================
REM 1. Git Clone Repository
REM =====================================
echo.
echo [Step 1/6] Checking project repository...

set "REPO_URL=https://github.com/UIE47061/SyncAI.git"
set "PROJECT_NAME=SyncAI"

REM Check if we're already in SyncAI directory
if exist "package.json" if exist "backend" if exist "frontend" (
    echo [SUCCESS] Already in SyncAI project directory
    set "PROJECT_ROOT=%CD%"
    goto :check_git
)

REM Check if SyncAI directory exists in current location
if exist "%PROJECT_NAME%" (
    echo [INFO] Found existing SyncAI directory
    cd /d "%PROJECT_NAME%"
    set "PROJECT_ROOT=%CD%"
    goto :check_git
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

:check_git
echo [SUCCESS] Project repository ready

REM =====================================
REM 2. Prepare AI Model
REM =====================================
echo.
echo [Step 2/6] Preparing AI model...

set "MODEL_DIR=%PROJECT_ROOT%\ai_models"
set "MODEL_FILE=mistral-7b-instruct-v0.2.Q5_K_M.gguf"
set "MODEL_PATH=%MODEL_DIR%\%MODEL_FILE%"

if not exist "%MODEL_DIR%" (
    echo [INFO] Creating ai_models directory...
    mkdir "%MODEL_DIR%"
)

REM Check if model file exists and is complete
if exist "%MODEL_PATH%" (
    echo [INFO] Checking existing model file...
    for %%F in ("%MODEL_PATH%") do (
        if %%~zF GTR 5000000000 (
            echo [SUCCESS] AI model already exists and is complete
            goto :check_docker
        )
    )
    echo [WARNING] Model file incomplete, will re-download...
    del /f "%MODEL_PATH%"
)

echo [INFO] Downloading AI model file...
echo File size: Approximately 5.1GB, please wait...

REM Try to download using curl first, then fallback to PowerShell
curl --version >nul 2>&1
if %errorlevel% equ 0 (
    echo [INFO] Using curl to download model...
    curl -L -o "%MODEL_PATH%" "https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF/resolve/main/mistral-7b-instruct-v0.2.Q5_K_M.gguf"
) else (
    echo [INFO] Using PowerShell to download model...
    powershell -Command "& {Invoke-WebRequest -Uri 'https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF/resolve/main/mistral-7b-instruct-v0.2.Q5_K_M.gguf' -OutFile '%MODEL_PATH%'}"
)

if not exist "%MODEL_PATH%" (
    echo [ERROR] Model download failed
    pause
    exit /b 1
)

echo [SUCCESS] AI model ready

REM =====================================
REM 3. Check/Install Docker
REM =====================================
echo.
echo [Step 3/6] Checking Docker installation...

docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARNING] Docker not installed
    echo.
    echo Please manually install Docker Desktop for Windows:
    echo https://docs.docker.com/desktop/install/windows-install/
    echo.
    echo Please restart this script after installation
    pause
    exit /b 1
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
REM 4. Docker Deployment
REM =====================================
echo.
echo [Step 4/6] Docker deployment...

REM Stop existing containers
echo [INFO] Stopping existing containers...
docker-compose -f docker/docker-compose.yml down 2>nul

REM Build and start services
echo [INFO] Building and starting services...
echo This may take several minutes to download images and build containers...
docker-compose -f docker/docker-compose.yml up -d --build

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
docker-compose -f docker/docker-compose.yml ps
echo [SUCCESS] Docker deployment completed

REM =====================================
REM 5. Show IP Addresses
REM =====================================
echo.
echo [Step 5/6] Querying IP addresses...

echo.
echo =====================================
echo        Available Access URLs
echo =====================================

REM Get local IP addresses
echo [Local IP Addresses]
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

echo [Container Status]
docker-compose -f docker/docker-compose.yml ps

echo.
echo =====================================
echo         Installation Complete!
echo =====================================

REM =====================================
REM 6. Control Commands
REM =====================================
echo.
echo [Step 6/6] Setting up control commands...

echo.
echo =====================================
echo       Meeting Room Controls
echo =====================================
echo.

REM Create control scripts
echo [INFO] Creating control scripts...

REM Create start script
(
echo @echo off
echo chcp 65001 ^>nul
echo echo Starting SyncAI meeting room services...
echo cd /d "%PROJECT_ROOT%"
echo docker-compose -f docker/docker-compose.yml up -d
echo echo Services started!
echo echo Frontend: http://localhost
echo echo Backend:  http://localhost:8000
echo pause
) > "%PROJECT_ROOT%\start_meeting.bat"

REM Create stop script
(
echo @echo off
echo chcp 65001 ^>nul
echo echo Stopping SyncAI meeting room services...
echo cd /d "%PROJECT_ROOT%"
echo docker-compose -f docker/docker-compose.yml down
echo echo Services stopped!
echo pause
) > "%PROJECT_ROOT%\stop_meeting.bat"

REM Create status script
(
echo @echo off
echo chcp 65001 ^>nul
echo echo SyncAI meeting room service status:
echo cd /d "%PROJECT_ROOT%"
echo docker-compose -f docker/docker-compose.yml ps
echo echo.
echo echo Service logs:
echo docker-compose -f docker/docker-compose.yml logs --tail=20
echo pause
) > "%PROJECT_ROOT%\status_meeting.bat"

REM Create restart script
(
echo @echo off
echo chcp 65001 ^>nul
echo echo Restarting SyncAI meeting room services...
echo cd /d "%PROJECT_ROOT%"
echo docker-compose -f docker/docker-compose.yml restart
echo echo Services restarted!
echo echo Frontend: http://localhost
echo echo Backend:  http://localhost:8000
echo pause
) > "%PROJECT_ROOT%\restart_meeting.bat"

echo Created the following control scripts:
echo.
echo   📂 start_meeting.bat    - Start meeting room services
echo   📂 stop_meeting.bat     - Stop meeting room services
echo   📂 status_meeting.bat   - View service status
echo   📂 restart_meeting.bat  - Restart meeting room services
echo.

echo =====================================
echo          Usage Instructions
echo =====================================
echo.
echo 🚀 Quick Start:
echo   Double-click start_meeting.bat to start services
echo   Open browser to http://localhost
echo.
echo 🛑 Stop Services:
echo   Double-click stop_meeting.bat
echo.
echo 📊 Check Status:
echo   Double-click status_meeting.bat
echo.
echo 🔄 Restart Services:
echo   Double-click restart_meeting.bat
echo.
echo 💡 Tips:
echo   - First startup may take longer time
echo   - Keep Docker Desktop running
echo   - Share IP addresses for device access
echo.

echo =====================================
echo      Installation Successful! 🎉
echo =====================================
echo.
echo Press any key to exit installation...
pause >nul

exit /b 0

REM Error handling
:error_dir
echo [ERROR] Cannot find project directory structure
echo Please ensure you are running this script in the correct directory
pause
exit /b 1
