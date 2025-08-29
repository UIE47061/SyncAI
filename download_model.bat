@echo off
chcp 65001 >nul
REM SyncAI Model Download Script (Windows)
REM This script will automatically download the required AI model files

setlocal enabledelayedexpansion

set MODEL_DIR=ai_models
set MODEL_FILE=mistral-7b-instruct-v0.2.Q5_K_M.gguf
set MODEL_URL=https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF/resolve/main/mistral-7b-instruct-v0.2.Q5_K_M.gguf

echo.
echo =====================================
echo    SyncAI Model Download Tool
echo =====================================
echo.

REM Check if directory exists
if not exist "%MODEL_DIR%" (
    echo [ERROR] Cannot find %MODEL_DIR% directory
    echo Please make sure you are running this script from the SyncAI project root directory
    echo.
    pause
    exit /b 1
)

cd "%MODEL_DIR%"

REM Check if file already exists
if exist "%MODEL_FILE%" (
    echo [INFO] Checking existing model file...
    for %%F in ("%MODEL_FILE%") do (
        if %%~zF GTR 5000000000 (
            echo [SUCCESS] Model file already exists and size is correct
            echo [INFO] No need to download again!
            echo.
            pause
            exit /b 0
        )
    )
    echo [WARNING] Model file exists but size is incorrect, will re-download...
    del /f "%MODEL_FILE%"
)

echo [INFO] Starting model file download...
echo Model: %MODEL_FILE%
echo Size: Approximately 5.1GB
echo This may take some time, please be patient...
echo.

REM Download using PowerShell
echo [INFO] Using PowerShell to download...
powershell -Command "& {Import-Module BitsTransfer; Start-BitsTransfer -Source '%MODEL_URL%' -Destination '%MODEL_FILE%'}"

REM If BITS fails, try Invoke-WebRequest
if not exist "%MODEL_FILE%" (
REM If BITS fails, try Invoke-WebRequest
if not exist "%MODEL_FILE%" (
    echo [INFO] Trying alternative download method...
    powershell -Command "Invoke-WebRequest -Uri '%MODEL_URL%' -OutFile '%MODEL_FILE%'"
)

REM Verify download
if exist "%MODEL_FILE%" (
    echo.
    echo [SUCCESS] Download completed!
    echo [INFO] File information:
    dir "%MODEL_FILE%"
    echo.
    echo [INFO] Now you can start SyncAI:
    echo    docker-compose -f docker/docker-compose.yml up -d
    echo.
) else (
    echo [ERROR] Download failed, please check network connection or download manually
    echo Manual download URL:
    echo https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF
    echo.
    pause
    exit /b 1
)

echo Press any key to exit...
pause >nul
