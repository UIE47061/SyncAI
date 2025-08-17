# SyncAI Meeting

**SyncAI** 是一款專為「內部會議協作」打造的本地私有化 AI 互動平台，  
支援 AI 智能助理、匿名意見收集、即時討論、AI 統整等新一代會議體驗。  
設計重點：「隱私安全」「本地運行」「高互動」「跨裝置易用」「彈性擴展」。

---

## 📦 安裝步驟與相依套件

### 前端（Vue 3 + Vite）

1. 進入前端目錄  
   `cd frontend/syncai-frontend`
2. 安裝依賴  
   `npm install`
3. 啟動開發伺服器  
   `npm run dev`
4. 開啟 [http://localhost:5173](http://localhost:5173)

**主要相依套件：**
- vue
- vue-router
- uuid

### 後端（FastAPI + llama.cpp）

1. 建立虛擬環境  
   `python -m venv .venv`
2. 啟動虛擬環境  
   - Windows: `.venv\Scripts\activate`
   - macOS/Linux: `source .venv/bin/activate`
3. 安裝依賴  
   `pip install -r requirement.txt`
4. 啟動後端服務  
   `uvicorn backend.main:app --reload --host 0.0.0.0`

### 模型
- mistral-7b-instruct-v0.2.Q5_K_M.gguf
下載後放到 `ai_models` 資料夾下

**主要相依套件：**
- fastapi
- uvicorn
- pydantic
- python-dotenv
- requests
- aiohttp
- sqlalchemy
- llama-cpp-python
- jinja2
- alembic
- httpx

---

## 💻 Snapdragon X 系列筆電操作指引（NPU 加速）

1. **安裝 Windows 11 並確認已啟用 NPU 驅動。**
2. **llama-cpp-python** 支援 Windows ARM64 與 NPU 加速，請參考 [llama-cpp-python 官方文件](https://github.com/abetlen/llama-cpp-python)。
3. 建議使用 Qualcomm AI Hub 或 Windows Dev Kit 2023 進行模型最佳化。
4. 若需啟用 NPU，請在啟動模型時加上 NPU 相關參數，例如：
   ```python
   from llama_cpp import Llama
   llm = Llama(model_path='ai_models/mistral-7b-instruct-v0.2.Q5_K_M.gguf', n_gpu_layers=0, n_ctx=4096, n_threads=8, n_npu_layers=20)
   ```
5. 若遇到 NPU 驅動或模型格式問題，請參考 Qualcomm 官方資源或 Windows AI 文件。

---

## 🧪 測試流程與驗證方式

1. 前端啟動後，瀏覽器開啟首頁，輸入會議主題並建立房間。
2. 參與者可用手機掃描 QR Code 或點擊連結加入。
3. 測試留言、投票、AI 問答、AI 統整等功能。
4. 可於多裝置（手機、平板、Snapdragon X 筆電）同時加入，驗證同步與互動。
5. 若需驗證 NPU 加速，請於後端 log 或 llama-cpp-python 啟動時確認 NPU 已啟用。

---

## 📝 典型使用流程

1. 主持人首頁輸入會議主題，點擊「開啟會議」
2. 系統自動產生房間 ID、參與者連結（含 QRCode）
3. 現場手機掃描/點擊即可匿名或署名加入互動頁
4. 即時留言、投票、AI 問答、AI 自動統整重點
5. 會議結束，一鍵取得 AI 會議摘要、行動建議

---

## 🛡️ 採用之開源授權

本專案採用 [MIT License](https://choosealicense.com/licenses/mit/) 授權，  
您可自由使用、修改、散布本程式碼，但請保留原始授權聲明。

---

## 📂 目錄結構

```
SyncAI/
├── ai_models/           # 本地 LLM 模型（.gguf 等格式）
├── backend/             # FastAPI 後端
│   ├── main.py
│   ├── api/
│   └── ...
├── frontend/
│   └── syncai-frontend/ # Vue3 + Vite 前端
│       ├── public/
│       ├── src/
│       │   ├── App.vue
│       │   ├── assets/
│       │   │   └── style.css
│       └── ...
└── README.md
```

---

## 💡 進階特色 & 延伸應用

- 支援 BYOM (Bring Your Own Model)／可串接 Qualcomm AI Hub、NPU 部署
- 架構可外接語音轉文字、議程規劃、智慧報表等模組
- 高彈性 API，便於整合現有系統

---

## 🛡️ 隱私與本地運行保證

本系統全程本地推理、無雲端資料傳輸，任何會議訊息、AI 討論、決策過程**均不會外洩**。  
特別適合需要高隱私、高安全、高自主的創新團隊或組織！