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
| 吳承彥 | t112ab0025@ntut.org.tw |
| 陳以珊 | t111ab0011@ntut.org.tw |
| 林佑亦 | t112ab0004@ntut.org.tw |

## 📦 從零開始的安裝指引

### 1. 下載專案

```bash
git clone https://github.com/your-username/SyncAI.git
cd SyncAI
```

### 2. 準備 AI 模型

1. 下載 Mistral 模型：
   - 下載 `mistral-7b-instruct-v0.2.Q5_K_M.gguf` 模型檔案
   - 下載連結：https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF
2. 將下載的模型檔案放置於 `ai_models` 資料夾中

### 3. 安裝後端相依套件

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

#### 後端相依套件列表：
- fastapi
- uvicorn
- pydantic
- llama-cpp-python
- reportlab

### 4. 安裝前端相依套件

```bash
# 進入前端目錄
cd frontend/syncai-frontend

# 安裝相依套件
npm install
```

#### 前端相依套件列表：
- vue
- vue-router
- uuid
- qrcode.vue

## 🚀 執行與使用說明

### 啟動服務

1. **啟動後端服務**：
   ```bash
   # 在專案根目錄下執行
   uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **啟動前端開發伺服器**：
   ```bash
   # 在 frontend/syncai-frontend 目錄下執行
   npm run dev
   ```

3. **存取應用程式**：
   - 開啟瀏覽器，前往 `http://localhost:5173`

### 使用流程

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

### Snapdragon X 系列裝置使用說明

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
├── ai_models/           # 本地 LLM 模型（.gguf 格式）
├── backend/             # FastAPI 後端
│   ├── main.py          # 後端主入口
│   ├── api/             # API 實作
│   │   ├── ai_api.py    # AI 相關 API
│   │   ├── participants_api.py  # 會議參與 API
│   │   └── utility.py   # 工具函數
├── frontend/
│   └── syncai-frontend/ # Vue3 + Vite 前端
│       ├── public/
│       ├── src/
│       │   ├── App.vue
│       │   ├── assets/
│       │   ├── components/
│       │   └── router/
└── README.md
```

## 🛡️ 隱私保障

本系統全程本地推理、無雲端資料傳輸，任何會議訊息、AI 討論、決策過程**均不會外洩**。特別適合需要高隱私、高安全的組織與團隊使用。

## 📄 授權資訊

本專案採用 [MIT License](https://choosealicense.com/licenses/mit/) 授權，可自由使用、修改、散布本程式碼，但請保留原始授權聲明。