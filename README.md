# SyncAI Meeting

一個支援本地 AI 問答、即時互動、支援 QR Code 參與的**私有會議室**解決方案。  
前端採用 **Vue 3 + Vite**，後端採 **FastAPI** 串接本地 LLM（如 llama.cpp），重視隱私、速度與彈性。

---

## 🚀 特色功能

- 💬 主持人可自訂會議主題並一鍵開啟專屬房間
- 📱 自動產生 QR Code 參與連結，現場掃描即加入會議
- 🏠 會議畫面極簡易用，RWD 手機電腦皆美觀
- 🧠 本地 AI（可選）協助會議問答、摘要、票選等延伸功能
- 🔒 所有服務均可本地運行，不依賴雲端、不外洩數據

---

## 📁 目錄結構

```
SYNC-AI/
│
├── ai_models/           # 本地 LLM 模型
├── backend/             # FastAPI 後端
│   ├── main.py
│   ├── routers/
│   └── ...
├── frontend/
│   └── syncai-frontend/ # Vue3 前端
│       ├── public/
│       ├── src/
│       │   ├── App.vue
│       │   ├── assets/
│       │   │   └── style.css
│       └── ...
└── README.md
```

---

## 🖥️ 前端啟動說明（Vue 3）

```bash
# 1. 進入前端專案
cd frontend/syncai-frontend

# 2. 安裝依賴
npm install

# 3. 啟動開發伺服器
npm run dev
```
開啟 http://localhost:5173 即可預覽。

> **注意**  
> - 預設 QR Code 連結是本機網址，請依照區網實際需求調整（建議可換成內網 IP）  
> - `public/logo.png` 可放置自訂 Logo

---

## 🐍 後端啟動說明（FastAPI + LLM）

```bash
# 1. 在 SyncAI 資料夾下

# 2. 建立 python 虛擬環境（可選）
python -m venv .venv
# 啟動虛擬環境
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

# 3. 安裝依賴
pip install fastapi uvicorn llama-cpp-python

# 4. 啟動後端服務
uvicorn backend.main:app --reload --host 0.0.0.0
```

- LLM 模型建議放於 `ai_models/`，可自由替換
- 預設 API 路徑為 `/ai/ask`，可從前端呼叫

---

## 📝 典型開發流程

1. 主持人在首頁輸入會議主題，開啟會議
2. 產生房間 ID 與參與者連結（及 QRCode）
3. 參與者掃碼進入互動頁面
4. （未來功能）即時發問、投票、AI 摘要自動產生
