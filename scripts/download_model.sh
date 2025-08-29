#!/bin/bash
# MBBuddy 模型下載腳本
# 此腳本會自動下載所需的 AI 模型檔案

set -e  # 遇到錯誤時停止執行

# 獲取腳本所在目錄的父目錄（專案根目錄）
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
MODEL_DIR="$PROJECT_ROOT/ai_models"
MODEL_FILE="mistral-7b-instruct-v0.2.Q5_K_M.gguf"
MODEL_URL="https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF/resolve/main/mistral-7b-instruct-v0.2.Q5_K_M.gguf"
EXPECTED_SIZE="5131409696"  # 約 5.1GB

echo "🤖 MBBuddy 模型下載工具"
echo "================================"

# 檢查目錄是否存在
if [ ! -d "$MODEL_DIR" ]; then
    echo "❌ 錯誤：找不到 $MODEL_DIR 目錄"
    echo "請確保您在 MBBuddy 專案根目錄或 scripts 目錄下執行此腳本"
    exit 1
fi

cd "$MODEL_DIR"

# 檢查檔案是否已存在
if [ -f "$MODEL_FILE" ]; then
    echo "📁 檢查現有模型檔案..."
    
    # 檢查檔案大小
    if command -v stat >/dev/null 2>&1; then
        # macOS/BSD stat
        if stat -f%z "$MODEL_FILE" 2>/dev/null | grep -q "$EXPECTED_SIZE"; then
            echo "✅ 模型檔案已存在且大小正確"
            echo "🎉 無需重新下載！"
            exit 0
        fi
    elif command -v stat >/dev/null 2>&1; then
        # Linux stat
        if stat -c%s "$MODEL_FILE" 2>/dev/null | grep -q "$EXPECTED_SIZE"; then
            echo "✅ 模型檔案已存在且大小正確"
            echo "🎉 無需重新下載！"
            exit 0
        fi
    fi
    
    echo "⚠️  模型檔案存在但大小不正確，將重新下載..."
    rm -f "$MODEL_FILE"
fi

echo "📥 開始下載模型檔案..."
echo "模型：$MODEL_FILE"
echo "大小：約 5.1GB"
echo "這可能需要一些時間，請耐心等待..."
echo ""

# 嘗試使用 wget
if command -v wget >/dev/null 2>&1; then
    echo "使用 wget 下載..."
    wget --progress=bar:force:noscroll -O "$MODEL_FILE" "$MODEL_URL"
# 嘗試使用 curl
elif command -v curl >/dev/null 2>&1; then
    echo "使用 curl 下載..."
    curl -L --progress-bar -o "$MODEL_FILE" "$MODEL_URL"
else
    echo "❌ 錯誤：找不到 wget 或 curl"
    echo "請手動下載模型檔案："
    echo "1. 前往：https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF"
    echo "2. 下載：$MODEL_FILE"
    echo "3. 放置於：$(pwd)/$MODEL_FILE"
    exit 1
fi

# 驗證下載
if [ -f "$MODEL_FILE" ]; then
    echo ""
    echo "✅ 下載完成！"
    echo "📊 檔案資訊："
    ls -lh "$MODEL_FILE"
    echo ""
    echo "🚀 現在您可以啟動 MBBuddy："
    echo "   docker-compose -f docker/docker-compose.yml up -d"
else
    echo "❌ 下載失敗，請檢查網路連線或手動下載"
    exit 1
fi
