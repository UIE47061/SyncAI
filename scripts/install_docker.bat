@echo off
chcp 65001 >nul
REM Docker Auto-Installer for Windows
REM This script attempts to automatically install Docker Desktop

setlocal enabledelayedexpansion

echo.
echo =====================================
echo      Docker Auto-Installer
echo =====================================
echo.

REM Check if Docker is already installed
docker --version >nul 2>&1
if %errorlevel% equ 0 (
    echo [SUCCESS] Docker is already installed
    docker --version
    
    REM Check if Docker service is running
    docker info >nul 2>&1
    if %errorlevel% equ 0 (
        echo [SUCCESS] Docker service is running
        exit /b 0
    ) else (
        echo [WARNING] Docker service is not running
        echo Please start Docker Desktop and try again
        pause
        exit /b 1
    )
)

echo [INFO] Docker not found, attempting automatic installation...
echo.

REM Check Windows version
ver | findstr /i "10\|11" >nul
if %errorlevel% neq 0 (
    echo [ERROR] Docker Desktop requires Windows 10 or Windows 11
    echo Please upgrade your Windows version
    pause
    exit /b 1
)

REM Check if running as administrator
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARNING] Administrator privileges recommended for installation
    echo Would you like to continue anyway? (Y/N)
    set /p admin_choice="Enter your choice: "
    if /i not "!admin_choice!"=="Y" (
        echo [INFO] Please run this script as administrator for best results
        pause
        exit /b 1
    )
)

echo [INFO] Trying multiple installation methods...
echo.

REM Method 1: Try Chocolatey
echo [Method 1] Checking for Chocolatey...
choco --version >nul 2>&1
if %errorlevel% equ 0 (
    echo [INFO] Chocolatey found, installing Docker Desktop...
    choco install docker-desktop -y --ignore-checksums
    if %errorlevel% equ 0 (
        echo [SUCCESS] Docker Desktop installed successfully via Chocolatey!
        goto :installation_complete
    ) else (
        echo [WARNING] Chocolatey installation failed, trying next method...
    )
) else (
    echo [INFO] Chocolatey not found, trying next method...
)

REM Method 2: Try winget
echo.
echo [Method 2] Checking for winget...
winget --version >nul 2>&1
if %errorlevel% equ 0 (
    echo [INFO] Winget found, installing Docker Desktop...
    winget install Docker.DockerDesktop --accept-package-agreements --accept-source-agreements
    if %errorlevel% equ 0 (
        echo [SUCCESS] Docker Desktop installed successfully via winget!
        goto :installation_complete
    ) else (
        echo [WARNING] Winget installation failed, trying next method...
    )
) else (
    echo [INFO] Winget not found, trying next method...
)

REM Method 3: Direct download and install
echo.
echo [Method 3] Direct download installation...
echo [INFO] Downloading Docker Desktop installer...

set "DOCKER_INSTALLER=%TEMP%\DockerDesktopInstaller.exe"
set "DOCKER_URL=https://desktop.docker.com/win/main/amd64/Docker Desktop Installer.exe"

REM Try curl first
curl --version >nul 2>&1
if %errorlevel% equ 0 (
    echo [INFO] Using curl to download...
    curl -L --progress-bar -o "%DOCKER_INSTALLER%" "%DOCKER_URL%"
    set download_result=%errorlevel%
) else (
    echo [INFO] Using PowerShell to download...
    powershell -Command "& {$ProgressPreference = 'SilentlyContinue'; Invoke-WebRequest -Uri '%DOCKER_URL%' -OutFile '%DOCKER_INSTALLER%'; exit $LASTEXITCODE}"
    set download_result=%errorlevel%
)

if !download_result! neq 0 (
    echo [ERROR] Failed to download Docker Desktop installer
    goto :manual_installation
)

if not exist "%DOCKER_INSTALLER%" (
    echo [ERROR] Installer file not found after download
    goto :manual_installation
)

echo [INFO] Download completed successfully
echo [INFO] Running Docker Desktop installer...
echo.
echo NOTE: Please follow the installation wizard:
echo 1. Accept the license agreement
echo 2. Choose installation options (default recommended)
echo 3. Allow restart when prompted
echo 4. Run this script again after restart
echo.

start /wait "%DOCKER_INSTALLER%" install --quiet --accept-license
set install_result=%errorlevel%

REM Clean up installer
if exist "%DOCKER_INSTALLER%" del /f "%DOCKER_INSTALLER%"

if !install_result! equ 0 (
    echo [SUCCESS] Docker Desktop installation completed!
    goto :installation_complete
) else (
    echo [WARNING] Installation may have issues, checking status...
    
    REM Wait a moment and check if Docker was installed
    timeout /t 5 /nobreak >nul
    docker --version >nul 2>&1
    if %errorlevel% equ 0 (
        echo [SUCCESS] Docker appears to be installed despite warnings
        goto :installation_complete
    ) else (
        echo [ERROR] Docker installation failed
        goto :manual_installation
    )
)

:installation_complete
echo.
echo =====================================
echo    Docker Installation Complete!
echo =====================================
echo.
echo [INFO] Docker Desktop has been installed successfully
echo [INFO] You may need to:
echo   1. Restart your computer
echo   2. Start Docker Desktop manually
echo   3. Accept any license agreements
echo   4. Complete the initial setup
echo.
echo [INFO] After restart, Docker will be available for use
echo.
pause
exit /b 0

:manual_installation
echo.
echo =====================================
echo      Manual Installation Required
echo =====================================
echo.
echo [ERROR] Automatic installation failed
echo.
echo Please manually install Docker Desktop:
echo 1. Visit: https://docs.docker.com/desktop/install/windows-install/
echo 2. Download Docker Desktop for Windows
echo 3. Run the installer as administrator
echo 4. Restart your computer when prompted
echo 5. Run this installation script again
echo.
echo System Requirements:
echo - Windows 10 64-bit or Windows 11
echo - WSL 2 feature enabled
echo - Virtualization enabled in BIOS
echo - At least 4GB RAM (8GB recommended)
echo.
pause
exit /b 1
