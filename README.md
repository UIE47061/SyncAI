# SyncAI Meeting

## 📱 應用程式說明

**SyncAI** 是一款專為「內部會議協作」打造的本地私有化 AI 互動平台，整合了匿名意見收集、即時投票、AI 智能助理及自動統整等功能，提供全新的會議互動體驗。

### 核心特色：

- **匿名意見表達**：參與者可匿名提交意見，降低發言心理門檻
- **即時投票機制**：對提出的意見快速進行正負面投票，突顯共識與分歧
- **本地 AI 助理**：提供即時會議資訊統整與摘要，無需雲端連接
- **跨裝置支援**：主持人可在電腦管理會議，參與者用手機掃碼即可加入
- **PDF 報告匯出**：一鍵產生包含圖表分析的完整會議記錄

### 技術亮點：

- **隱私安全**：全程本地推理，無雲端資料傳輸，保障會議資訊安全
- **NPU 加速**：支援高通 Snapdragon X 系列裝置 NPU 加速，提升 AI 處理效能
- **輕量部署**：前後端分離架構，可輕鬆部署於各種環境
- **互動體驗**：即時更新的投票機制與討論計時器，增強會議參與感

## 👥 參賽團隊成員

| 姓名 | 電子郵件 |
| --- | --- |
| 趙祖威 | t110ab0012@ntut.org.tw |
| 賴聖元 | 11046015@ntub.edu.tw |
| 吳承諺 | t111ab0011@ntut.org.tw |
| 陳以珊 | t112ab0025@ntut.org.tw |
| 林佑亦 | t112ab0004@ntut.org.tw |

## 📦 安裝與使用指引

### 1. 下載專案

```bash
git clone https://github.com/UIE47061/SyncAI.git
cd SyncAI
```

### 2. 準備 AI 模型

⚠️ **重要**：由於模型檔案過大（5.1GB），已加入 `.gitignore`，需要手動下載

#### 方法一：使用自動下載腳本（推薦）
```bash
# macOS/Linux
./download_model.sh

# Windows
download_model.bat
```

#### 方法二：手動下載
```bash
# 使用 wget（推薦）
cd ai_models
wget https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF/resolve/main/mistral-7b-instruct-v0.2.Q5_K_M.gguf

# 使用 curl
cd ai_models
curl -L -o mistral-7b-instruct-v0.2.Q5_K_M.gguf https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF/resolve/main/mistral-7b-instruct-v0.2.Q5_K_M.gguf

# 手動下載
# 前往 https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF
# 下載 mistral-7b-instruct-v0.2.Q5_K_M.gguf 檔案
```

#### 驗證下載
```bash
# 檢查檔案是否存在且大小正確（約 5.1GB）
ls -lh ai_models/mistral-7b-instruct-v0.2.Q5_K_M.gguf
```

應該看到類似輸出：
```
-rw-r--r-- 1 user staff 4.8G Aug 28 22:50 ai_models/mistral-7b-instruct-v0.2.Q5_K_M.gguf
```

### 3. 選擇部署方式

## 🚀 方法一：Docker 部署（推薦）

### 先決條件
1. 確保已安裝 Docker 和 Docker Compose
2. **重要**：確保已完成上述「準備 AI 模型」步驟
3. 驗證模型檔案存在：
   ```bash
   ls -la ai_models/mistral-7b-instruct-v0.2.Q5_K_M.gguf
   ```
   如果檔案不存在，請返回「準備 AI 模型」章節完成下載

### 開發環境（支援熱重載）
```bash
# 啟動開發環境
docker-compose -f docker/docker-compose.dev.yml up -d

# 查看日誌
docker-compose -f docker/docker-compose.dev.yml logs -f

# 停止服務
docker-compose -f docker/docker-compose.dev.yml down
```
**訪問地址**：
- 前端：`http://[您的IP地址]`
- 後端：`http://[您的IP地址]:8000`

### 生產環境
```bash
# 啟動生產環境
docker-compose -f docker/docker-compose.yml up -d

# 查看日誌
docker-compose -f docker/docker-compose.yml logs -f

# 停止服務
docker-compose -f docker/docker-compose.yml down
```
**訪問地址**：
- 前端：`http://[您的IP地址]:5173`
- 後端：`http://[您的IP地址]:8001`

### 查詢您的 IP 地址
   ```bash
   # macOS/Linux
   ifconfig | grep "inet " | grep -v 127.0.0.1

   # Windows (命令提示字元)
   ipconfig | findstr "IPv4"

   # 會顯示類似：	
   #      inet 192.168.0.114 netmask 0xffffff00 broadcast 192.168.100.255  (macOS/Linux)
   #      IPv4 地址 . . . . . . . . . . . . : 192.168.0.114                (Windows)
   # 則 192.168.0.114 就會是您的IP位址！
   ```

## 🔧 方法二：本地開發模式

### 安裝相依套件

#### 後端相依套件
```bash
# 建立虛擬環境
python -m venv .venv

# 啟動虛擬環境
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# 安裝相依套件
pip install -r requirements.txt
```

**後端相依套件列表**：fastapi, uvicorn, pydantic, llama-cpp-python, reportlab

#### 前端相依套件
```bash
# 進入前端目錄
cd frontend/syncai-frontend

# 安裝相依套件
npm install
```

**前端相依套件列表**：vue, vue-router, uuid, qrcode.vue

### 啟動服務

1. **啟動後端服務**：
   ```bash
   # 在專案根目錄下執行
   uvicorn backend.main:app --reload --host 0.0.0.0 --port 8001
   ```

2. **啟動前端開發伺服器**：
   ```bash
   # 在 frontend/syncai-frontend 目錄下執行
   npm run dev
   ```

3. **查詢您的 IP 地址**（區域網路訪問）：
   ```bash
   # macOS/Linux
   ifconfig | grep "inet " | grep -v 127.0.0.1

   # Windows (命令提示字元)
   ipconfig | findstr "IPv4"

   # 會顯示類似：	
   #      inet 192.168.0.114 netmask 0xffffff00 broadcast 192.168.100.255  (macOS/Linux)
   #      IPv4 地址 . . . . . . . . . . . . : 192.168.0.114                (Windows)
   # 則 192.168.0.114 就會是您的IP位址！
   ```

**訪問地址**：
- 前端：`http://[您的IP地址]:5173`
- 後端：`http://[您的IP地址]:8001`

## 📱 使用流程

1. **建立會議室**：
   - 在首頁輸入會議主題
   - 點擊「建立會議室」按鈕
   - 填寫會議設定（名稱、議題、時間等）

2. **邀請參與者**：
   - 使用生成的 QR Code 或連結邀請參與者
   - 參與者掃描 QR Code 即可加入

3. **開始會議**：
   - 主持人可發起、暫停或結束討論
   - 設定倒數計時器
   - 隨時切換討論主題

4. **互動參與**：
   - 參與者提交意見/問題
   - 為他人意見投票（贊成/反對）
   - 查看即時排序的意見列表

5. **AI 輔助**：
   - 點擊「AI 統整」獲取當前討論摘要
   - AI 可自動產生議程主題建議

6. **匯出結果**：
   - 會議結束後點擊「匯出 PDF」
   - 獲取完整會議記錄，含意見、投票統計與圖表分析

## ⚡ Snapdragon X 系列裝置 NPU 加速

若使用 Snapdragon X 系列筆電，可啟用 NPU 加速：

1. 確認已安裝最新 Windows 11 與 NPU 驅動程式
2. 修改 `ai_api.py` 中的模型載入參數：
   ```python
   llm = Llama(
       model_path=MODEL_PATH, 
       n_ctx=2048,
       n_gpu_layers=0,  # 不使用 GPU
       n_threads=8,     # CPU 線程數
       n_npu_layers=20  # 啟用 NPU 加速
   )
   ```

## 📂 目錄結構
```
SyncAI/
├── 📁 ai_models/                    # AI 模型檔案目錄
│   ├── mistral-7b-instruct-v0.2.Q5_K_M.gguf  # Mistral 7B 模型（需下載）
│   └── test_llama_python.py         # 模型測試腳本
│
├── 🚀 backend/                      # FastAPI 後端服務
│   ├── main.py                      # 後端主入口點
│   └── api/                         # API 模組
│       ├── __init__.py              # 套件初始化
│       ├── ai_api.py                # AI 相關 API（模型推理、摘要）
│       ├── participants_api.py      # 會議參與 API（用戶管理、投票）
│       └── utility.py               # 工具函數（PDF 生成等）
│
├── 🎨 frontend/                     # 前端應用
│   └── syncai-frontend/             # Vue3 + Vite 前端專案
│       ├── index.html               # 主 HTML 模板
│       ├── package.json             # 前端依賴配置
│       ├── vite.config.js           # Vite 建置配置
│       ├── public/                  # 靜態資源
│       └── src/                     # 源碼目錄
│           ├── App.vue              # 根組件
│           ├── main.js              # 應用入口點
│           ├── assets/              # 樣式資源
│           ├── components/          # Vue 組件
│           │   ├── CreateRoomModal.vue    # 建立會議室彈窗
│           │   ├── Home.vue               # 首頁組件
│           │   ├── HostPanel.vue          # 主持人面板
│           │   ├── JoinRoomModal.vue      # 加入會議室彈窗
│           │   ├── NicknameModals.vue     # 暱稱設定彈窗
│           │   ├── ParticipantPanel.vue   # 參與者面板
│           │   └── icons/                 # 圖標組件
│           ├── composables/         # Vue Composition API
│           │   └── useRoom.js       # 會議室邏輯
│           ├── router/              # 路由配置
│           │   └── index.js         # 路由定義
│           └── utils/               # 工具函數
│               └── api.js           # API 請求封裝
│
├── 🐳 docker/                       # Docker 部署配置
│   ├── README.md                    # Docker 使用說明
│   ├── docker-compose.yml          # 生產環境配置
│   ├── docker-compose.dev.yml      # 開發環境配置
│   ├── Dockerfile.backend          # 後端容器配置
│   ├── Dockerfile.frontend         # 前端生產容器配置
│   ├── Dockerfile.frontend.dev     # 前端開發容器配置
│   ├── nginx.conf                  # Nginx 配置
│   └── .dockerignore               # Docker 忽略檔案
│
├── 🛠️ 配置檔案
│   ├── .gitignore                  # Git 忽略檔案
│   ├── package.json                # 專案元數據
│   ├── requirement.txt             # Python 依賴清單
│   └── test.py                     # 測試腳本
│
├── 📥 模型下載工具
│   ├── download_model.sh           # macOS/Linux 模型下載腳本
│   └── download_model.bat          # Windows 模型下載腳本
│
└── 📄 文檔
    ├── README.md                   # 專案說明文檔
    ├── LICENSE                     # MIT 授權條款
    └── THIRD_PARTY_NOTICES.md      # 第三方授權聲明
```

### 📋 關鍵檔案說明

| 檔案/目錄 | 功能說明 |
|-----------|----------|
| `ai_models/` | 存放 AI 模型檔案，模型檔案需手動下載 |
| `backend/api/ai_api.py` | 核心 AI 功能，包括文本生成和會議摘要 |
| `backend/api/participants_api.py` | 會議參與邏輯，用戶管理和投票系統 |
| `frontend/src/components/` | Vue 組件，實現各種 UI 功能 |
| `frontend/src/composables/useRoom.js` | 會議室狀態管理和 WebSocket 通訊 |
| `docker/` | 容器化部署配置，支援開發和生產環境 |
| `download_model.*` | 自動下載 AI 模型的便利腳本 |

## 🛡️ 隱私保障

本系統全程本地推理、無雲端資料傳輸，任何會議訊息、AI 討論、決策過程**均不會外洩**。特別適合需要高隱私、高安全的組織與團隊使用。

## ⚠️ Docker 部署注意事項

### AI 模型檔案處理
- 本專案使用 **Volume 掛載** 方式處理 AI 模型檔案
- 模型檔案 `mistral-7b-instruct-v0.2.Q5_K_M.gguf` (約 5.1GB) **不會**被複製到 Docker 映像中
- 而是透過掛載本地 `ai_models/` 目錄到容器中的方式使用

### 優點：
- ✅ Docker 映像大小大幅縮小（僅約 1-2GB）
- ✅ 建置速度快速
- ✅ 容易更新和分發
- ✅ 節省儲存空間

### 部署前檢查清單：
1. ✅ 確保 `ai_models/mistral-7b-instruct-v0.2.Q5_K_M.gguf` 檔案存在
2. ✅ 檔案大小約為 5.1GB（使用 `ls -lh ai_models/*.gguf` 檢查）
3. ✅ 如果在其他機器部署，需要先傳輸模型檔案到目標機器的相同路徑

### 常見問題排除：

#### 錯誤：找不到模型檔案
```bash
# 如果 Docker 啟動時出現找不到模型檔案的錯誤
# 請檢查以下項目：

# 1. 檢查檔案是否存在
ls -la ai_models/
ls -la ai_models/mistral-7b-instruct-v0.2.Q5_K_M.gguf

# 2. 如果檔案不存在，重新下載
cd ai_models
wget https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF/resolve/main/mistral-7b-instruct-v0.2.Q5_K_M.gguf

# 3. 確認檔案權限
chmod 644 ai_models/mistral-7b-instruct-v0.2.Q5_K_M.gguf
```

#### 首次設定完整流程：
```bash
# 1. Clone 專案
git clone https://github.com/UIE47061/SyncAI.git
cd SyncAI

# 2. 下載模型（必須步驟）
./download_model.sh        # macOS/Linux
# 或 download_model.bat     # Windows

# 3. 啟動 Docker
docker-compose -f docker/docker-compose.yml up -d
```

### 檔案結構確認：
```
SyncAI/
├── ai_models/
│   └── mistral-7b-instruct-v0.2.Q5_K_M.gguf  # 必須存在
├── docker/
│   ├── docker-compose.yml
│   └── docker-compose.dev.yml
└── ...
```

## 📄 授權資訊

本專案採用 [MIT License](https://choosealicense.com/licenses/mit/) 授權，可自由使用、修改、散布本程式碼，但請保留原始授權聲明。