# AnythingLLM API 集成設定說明

## 環境變數配置

在啟動應用程式之前，請設定以下環境變數：

```bash
export ANYTHINGLLM_BASE_URL=http://localhost:3001
export ANYTHINGLLM_API_KEY=your_api_key_here
export ANYTHINGLLM_WORKSPACE_SLUG=syncai
```

或者在 Docker 中：

```yaml
environment:
  - ANYTHINGLLM_BASE_URL=http://localhost:3001
  - ANYTHINGLLM_API_KEY=your_api_key_here
  - ANYTHINGLLM_WORKSPACE_SLUG=syncai
```

## 配置說明

- **ANYTHINGLLM_BASE_URL**: AnythingLLM 服務的基礎 URL (預設: http://localhost:3001)
- **ANYTHINGLLM_API_KEY**: 您的 AnythingLLM API 密鑰 (必填)
- **ANYTHINGLLM_WORKSPACE_SLUG**: 要使用的工作區名稱 (預設: syncai)

## 設定步驟

1. 確保 AnythingLLM 服務在 http://localhost:3001 上運行
2. 在 AnythingLLM 中創建或獲取 API Key
3. 創建名為 "syncai" 的工作區（或使用其他名稱並設定環境變數）
4. 設定上述環境變數
5. 啟動 SyncAI 後端服務

## API 端點對應

- `/ai/ask` → AnythingLLM `/api/v1/workspace/{slug}/chat`
- `/ai/summary` → AnythingLLM `/api/v1/workspace/{slug}/chat` (query 模式)
- `/ai/generate_topics` → AnythingLLM `/api/v1/workspace/{slug}/chat` (query 模式)
- `/ai/generate_single_topic` → AnythingLLM `/api/v1/workspace/{slug}/chat` (query 模式)

## 錯誤排除

如果遇到連接問題：
1. 檢查 AnythingLLM 服務是否運行
2. 確認 API Key 是否正確
3. 檢查工作區是否存在
4. 查看後端日誌獲取詳細錯誤信息
