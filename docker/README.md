# Docker 配置檔案

這個資料夾包含所有 SyncAI 專案的 Docker 相關配置檔案。

## 📁 檔案說明

- `docker-compose.yml` - 生產環境 Docker Compose 配置
- `docker-compose.dev.yml` - 開發環境 Docker Compose 配置
- `Dockerfile.backend` - 後端 Python FastAPI 應用的 Dockerfile
- `Dockerfile.frontend` - 前端 Vue.js 生產環境的 Dockerfile
- `Dockerfile.frontend.dev` - 前端 Vue.js 開發環境的 Dockerfile
- `nginx.conf` - Nginx 伺服器配置檔案
- `.dockerignore` - Docker 構建時忽略的檔案清單

## 🚀 使用方法

### 生產環境

```bash
# 從專案根目錄執行
docker-compose -f docker/docker-compose.yml up -d

# 查看狀態
docker-compose -f docker/docker-compose.yml ps

# 查看日誌
docker-compose -f docker/docker-compose.yml logs -f

# 停止服務
docker-compose -f docker/docker-compose.yml down
```

### 開發環境

```bash
# 從專案根目錄執行
docker-compose -f docker/docker-compose.dev.yml up -d

# 查看狀態
docker-compose -f docker/docker-compose.dev.yml ps

# 停止服務
docker-compose -f docker/docker-compose.dev.yml down
```

## 📝 注意事項

- 所有命令都需要從專案根目錄執行
- 確保 `ai_models/` 資料夾存在且包含必要的模型檔案
- 後端映像較大（約 11GB），主要因為包含 AI 模型檔案

## 🔄 更新

當修改代碼後，需要重新構建映像：

```bash
# 生產環境更新
docker-compose -f docker/docker-compose.yml down
docker-compose -f docker/docker-compose.yml build --no-cache
docker-compose -f docker/docker-compose.yml up -d

# 開發環境更新
docker-compose -f docker/docker-compose.dev.yml down
docker-compose -f docker/docker-compose.dev.yml build --no-cache
docker-compose -f docker/docker-compose.dev.yml up -d
```
