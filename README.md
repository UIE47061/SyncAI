# SyncAI Meeting

**SyncAI** 是一款專為「內部會議協作」打造的**本地私有化 AI 互動平台**，  
讓組織能**完全離線、即時互動**，輕鬆擁有 AI 智能助理、匿名意見收集、即時討論、AI 統整等新一代會議體驗。  
設計重點：「隱私安全」「本地運行」「高互動」「跨裝置易用」「彈性擴展」。

---

## 🌟 主要特色

- 🏠 **本地部署，數據零外洩**：所有服務與 AI 問答/摘要模型均在用戶端設備運行，不依賴雲端，適合企業/校園/封閉場域。
- 💡 **即時生成 QR Code 入會**：主持人開啟會議主題即產生專屬房間與參與連結，手機掃描秒進會議。
- 📲 **RWD 響應式設計**：電腦、平板、手機端皆美觀實用。
- 💬 **匿名留言、投票、互動**：參與者無壓力發表意見，主持人可掌控匿名/署名、投票、訊息管理。
- 🧠 **本地 AI 協作**：支援離線 LLM（如 llama.cpp/Mistral/TinyLlama）即時協助討論、會議摘要、智慧回覆，會議結論自動整理。
- ⚡ **彈性擴充架構**：API/模組化設計，便於客製新功能（如語音輸入、NPU 最佳化、外部系統串接）。
- 🔒 **高度隱私，開源部署**：適合有資安、個資、內部創新需求的所有單位。

---

## 🗂️ 目錄結構

```
SyncAI/
├── ai_models/           # 本地 LLM 模型（.gguf 等格式）
├── backend/             # FastAPI 後端，串接本地 LLM，管理會議/訊息流
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

## 🚀 快速啟動指南

### 前端（Vue 3 + Vite）

```bash
cd frontend/syncai-frontend
npm install
npm run dev
```
開啟 [http://localhost:5173](http://localhost:5173) 即可預覽。

---

### 後端（FastAPI + llama.cpp）

```bash
# 進入 SyncAI 資料夾，啟動虛擬環境
python -m venv .venv
source .venv/bin/activate      # macOS/Linux
.venv\Scripts\activate         # Windows

# 安裝依賴
pip install fastapi uvicorn llama-cpp-python

# 啟動後端（建議用區網 IP 公開服務）
uvicorn backend.main:app --reload --host 0.0.0.0
```

- LLM 模型建議放於 `ai_models/`，支援各種 gguf 格式模型  
- 主要 API 包含 `/ai/ask`（AI 問答）、`/ai/summary`（AI 統整）、`/api/hostip`（主機 IP 取得）等

---

## 📝 典型使用流程

1. 主持人首頁輸入會議主題，點擊「開啟會議」
2. 系統自動產生房間 ID、參與者連結（含 QRCode）
3. 現場手機掃描/點擊即可匿名或署名加入互動頁
4. 即時留言、投票、AI 問答、AI 自動統整重點
5. 會議結束，一鍵取得 AI 會議摘要、行動建議

---

## 💡 進階特色 & 延伸應用

- 支援 BYOM (Bring Your Own Model)／未來可串接 Qualcomm AI Hub、NPU 部署等
- 架構可外接語音轉文字、議程規劃、工作坊互動、智慧報表等模組
- 高彈性 API，便於整合現有系統

---

## 🛡️ 隱私與本地運行保證

本系統全程本地推理、無雲端資料傳輸，任何會議訊息、AI 討論、決策過程**均不會外洩**。  
特別適合需要高隱私、高安全、高自主的創新團隊或組織！