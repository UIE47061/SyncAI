@echo off
REM SyncAI 模型下載腳本 (Windows)
REM 此腳本會自動下載所需的 AI 模型檔案

setlocal enabledelayedexpansion

set MODEL_DIR=ai_models
set MODEL_FILE=mistral-7b-instruct-v0.2.Q5_K_M.gguf
set MODEL_URL=https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF/resolve/main/mistral-7b-instruct-v0.2.Q5_K_M.gguf

echo 🤖 SyncAI 模型下載工具
echo ================================

REM 檢查目錄是否存在
if not exist "%MODEL_DIR%" (
    echo ❌ 錯誤：找不到 %MODEL_DIR% 目錄
    echo 請確保您在 SyncAI 專案根目錄下執行此腳本
    pause
    exit /b 1
)

cd "%MODEL_DIR%"

REM 檢查檔案是否已存在
if exist "%MODEL_FILE%" (
    echo 📁 檢查現有模型檔案...
    for %%F in ("%MODEL_FILE%") do (
        if %%~zF GTR 5000000000 (
            echo ✅ 模型檔案已存在且大小正確
            echo 🎉 無需重新下載！
            pause
            exit /b 0
        )
    )
    echo ⚠️  模型檔案存在但大小不正確，將重新下載...
    del /f "%MODEL_FILE%"
)

echo 📥 開始下載模型檔案...
echo 模型：%MODEL_FILE%
echo 大小：約 5.1GB
echo 這可能需要一些時間，請耐心等待...
echo.

REM 使用 PowerShell 下載
echo 使用 PowerShell 下載...
powershell -Command "& {Import-Module BitsTransfer; Start-BitsTransfer -Source '%MODEL_URL%' -Destination '%MODEL_FILE%'}"

REM 如果 BITS 失敗，嘗試 Invoke-WebRequest
if not exist "%MODEL_FILE%" (
    echo 嘗試其他下載方法...
    powershell -Command "Invoke-WebRequest -Uri '%MODEL_URL%' -OutFile '%MODEL_FILE%'"
)

REM 驗證下載
if exist "%MODEL_FILE%" (
    echo.
    echo ✅ 下載完成！
    echo 📊 檔案資訊：
    dir "%MODEL_FILE%"
    echo.
    echo 🚀 現在您可以啟動 SyncAI：
    echo    docker-compose -f docker/docker-compose.yml up -d
) else (
    echo ❌ 下載失敗，請檢查網路連線或手動下載
    echo 手動下載地址：
    echo https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF
    pause
    exit /b 1
)

pause
