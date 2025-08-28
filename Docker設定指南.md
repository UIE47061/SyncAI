# SyncAI Docker 設定指南

## 🐳 架構概述

### 生產環境
- **後端**：Python FastAPI + uvicorn，運行在端口 8000
- **前端**：Vue.js + Vite，生產環境使用 nginx，運行在端口 80
- **AI 模型**：本地 Mistral 7B 模型，通過 llama-cpp-python 加載

### 開發環境
- **後端**：Python FastAPI + uvicorn，運行在端口 8001（避免與生產環境衝突）
- **前端**：Vue.js + Vite 開發服務器，運行在端口 5173
- **AI 模型**：與生產環境共享相同模型

## 🚀 快速開始

### 生產環境部署

```bash
# 構建並啟動服務
docker-compose -f docker/docker-compose.yml up -d

# 查看服務狀態
docker-compose -f docker/docker-compose.yml ps

# 查看日誌
docker-compose -f docker/docker-compose.yml logs -f
```

### 生產環境更新

當您修改了代碼檔案後，需要更新生產環境：

#### 🔄 完整更新流程

```bash
# 1. 停止服務
docker-compose -f docker/docker-compose.yml down

# 2. 重新構建映像（包含最新的代碼變更）
docker-compose -f docker/docker-compose.yml build --no-cache

# 3. 啟動更新後的服務
docker-compose -f docker/docker-compose.yml up -d

# 4. 確認服務狀態
docker-compose -f docker/docker-compose.yml ps

# 5. 查看啟動日誌
docker-compose -f docker/docker-compose.yml logs -f
```

#### ⚡ 快速更新（推薦）

```bash
# 一次性命令：重新構建並啟動
docker-compose -f docker/docker-compose.yml up -d --build

# 如果需要清除快取（確保使用最新代碼）
docker-compose -f docker/docker-compose.yml build --no-cache && docker-compose -f docker/docker-compose.yml up -d
```

#### 🎯 更新特定服務

如果只修改了前端或後端的檔案：

```bash
# 只更新前端
docker-compose -f docker/docker-compose.yml build --no-cache frontend
docker-compose -f docker/docker-compose.yml up -d frontend

# 只更新後端
docker-compose -f docker/docker-compose.yml build --no-cache backend
docker-compose -f docker/docker-compose.yml up -d backend
```

#### 🔍 驗證更新

```bash
# 檢查容器創建時間（確認是否為新容器）
docker-compose -f docker/docker-compose.yml ps

# 查看服務啟動日誌
docker-compose -f docker/docker-compose.yml logs backend
docker-compose -f docker/docker-compose.yml logs frontend

# 測試應用是否正常運行
curl http://192.168.0.114:8000/docs  # 測試後端
curl http://192.168.0.114            # 測試前端
```

### 開發環境部署

開發環境使用不同的端口配置以避免與生產環境衝突：

```bash
# 使用開發環境配置
docker-compose -f docker/docker-compose.dev.yml up -d

# 查看開發環境日誌
docker-compose -f docker/docker-compose.dev.yml logs -f
```

**開發環境訪問地址：**
- **前端應用**：http://localhost:5173
- **後端 API**：http://localhost:8001
- **API 文件**：http://localhost:8001/docs

## 🌐 查詢您的網路連結

### 步驟 1：查詢本機 IP 地址

在終端中執行以下命令來查詢您的區域網路 IP：

```bash
# macOS/Linux
ifconfig | grep "inet " | grep -v 127.0.0.1

# 或者使用
ip route get 1 | awk '{print $7}' | head -1

# Windows (PowerShell)
ipconfig | findstr "IPv4"
```

例如輸出可能是：
```
inet 192.168.0.114 netmask 0xffffff00 broadcast 192.168.0.255
```

這表示您的 IP 地址是 `192.168.0.114`

### 步驟 2：本地訪問應用

使用查詢到的 IP 地址替換以下範例中的 `192.168.0.114`：

#### 在區域網路中的設備訪問：
- **前端應用**：http://192.168.0.114
- **後端 API**：http://192.168.0.114:8000
- **API 文件**：http://192.168.0.114:8000/docs

### 步驟 3：在手機或平板上訪問

1. 確保設備連接到相同的 WiFi 網路
2. 在瀏覽器中輸入您的 IP 地址：`http://192.168.0.114`
3. 應用應該可以正常載入和使用

## 🔧 區域網路配置說明

系統已進行以下配置修改以支援區域網路訪問：

### 1. Docker 端口綁定
- 綁定到 `0.0.0.0` 而非 `localhost`
- 前端：`0.0.0.0:80:80`
- 後端：`0.0.0.0:8000:8000`

### 2. Nginx 配置
- 接受任何主機名 (`server_name localhost _;`)
- 添加 CORS 標頭支援跨域訪問
- API 代理正確配置

### 3. Vite 開發服務器
- 配置為 `host: '0.0.0.0'`
- 支援從任何 IP 訪問

### 4. FastAPI CORS
- 允許所有來源 (`allow_origins=["*"]`)
- 支援跨域請求

## 🛠️ 常用命令

### 基本操作
```bash
# 停止服務
docker-compose -f docker/docker-compose.yml down

# 重新構建映像
docker-compose -f docker/docker-compose.yml build

# 強制重新構建並啟動
docker-compose -f docker/docker-compose.yml up -d --build

# 進入容器
docker exec -it syncai-backend bash
docker exec -it syncai-frontend sh

# 查看特定服務日誌
docker-compose -f docker/docker-compose.yml logs -f backend
docker-compose -f docker/docker-compose.yml logs -f frontend

# 重啟特定服務
docker-compose -f docker/docker-compose.yml restart backend
docker-compose -f docker/docker-compose.yml restart frontend
```

### 更新與維護
```bash
# 清理未使用的映像和容器
docker system prune -f

# 查看映像大小
docker images | grep syncai

# 清理舊的映像
docker rmi $(docker images -f "dangling=true" -q)

# 備份重要數據（AI 模型等）
docker run --rm -v syncai_ai_models:/data -v $(pwd):/backup alpine tar czf /backup/ai_models_backup.tar.gz /data

# 查看容器資源使用情況
docker stats syncai-backend syncai-frontend
```

### 故障恢復
```bash
# 強制重建所有容器
docker-compose -f docker/docker-compose.yml down
docker-compose -f docker/docker-compose.yml build --no-cache
docker-compose -f docker/docker-compose.yml up -d

# 查看詳細錯誤信息
docker-compose -f docker/docker-compose.yml logs --tail=50 backend
docker-compose -f docker/docker-compose.yml logs --tail=50 frontend

# 重置到初始狀態
docker-compose -f docker/docker-compose.yml down -v  # 注意：這會刪除所有數據
docker system prune -af
docker-compose -f docker/docker-compose.yml up -d --build
```

## 🔥 防火牆設定

如果無法從其他設備訪問，請檢查防火牆設定：

### macOS 防火牆
```bash
# 檢查防火牆狀態
sudo pfctl -s all | grep -E "block|pass"

# 如果需要，可以暫時關閉防火牆進行測試
sudo pfctl -d
```

### 需要開放的端口
- 端口 80 (前端)
- 端口 8000 (後端 API)

## 🚀 測試連接

### 方法 1：瀏覽器測試
在其他設備的瀏覽器中輸入：
- 前端：`http://[您的IP地址]`
- API 文件：`http://[您的IP地址]:8000/docs`

### 方法 2：命令行測試
```bash
# 測試前端是否可訪問
curl http://[您的IP地址]

# 測試 API 文件
curl http://[您的IP地址]:8000/docs
```

## ⚙️ 環境變數配置

可以創建 `.env` 檔案來配置環境變數：

```env
# API 配置
API_HOST=0.0.0.0
API_PORT=8000

# 前端配置
VITE_API_URL=http://[您的IP地址]:8000
```

## 🔄 如果 IP 地址改變

路由器重新分配 IP 地址後：

1. **重新查詢 IP**：
   ```bash
   ifconfig | grep "inet " | grep -v 127.0.0.1
   ```

2. **更新訪問地址**：
   使用新的 IP 地址更新您的書籤和連結

3. **無需重啟 Docker**：
   Docker 配置不需要修改，直接使用新 IP 訪問即可

## 🛠️ 故障排除

### 1. 無法從其他設備連接
- ✅ 檢查所有設備是否在同一 WiFi 網路
- ✅ 確認防火牆設定
- ✅ 重啟 Docker 服務：`docker-compose -f docker/docker-compose.yml restart`

### 2. 端口衝突
- ✅ 確保端口 80 和 8000 未被其他程式占用
- ✅ 檢查：`lsof -i :80` 和 `lsof -i :8000`

### 3. 模型載入失敗
- ✅ 檢查 `ai_models/` 資料夾中是否有模型檔案
- ✅ 確認 Docker 有足夠記憶體載入 AI 模型

### 4. API 請求失敗
- ✅ 檢查瀏覽器開發者工具的網路標籤
- ✅ 確認 CORS 設定正確
- ✅ 查看後端日誌：`docker-compose -f docker/docker-compose.yml logs backend`

### 5. 前端顯示異常
- ✅ 清除瀏覽器快取
- ✅ 檢查前端日誌：`docker-compose -f docker/docker-compose.yml logs frontend`
- ✅ 重新構建前端：`docker-compose -f docker/docker-compose.yml build frontend`

## 📝 注意事項

### 更新相關
1. **生產環境更新**：與開發環境不同，生產環境需要重新構建映像才能看到代碼變更
2. **更新前備份**：重要更新前建議備份 AI 模型和配置檔案
3. **分階段更新**：可以先更新單一服務測試，確認無誤後再更新另一個服務
4. **停機時間**：生產環境更新會有短暫停機時間（通常 1-2 分鐘）

### 系統需求
1. **首次構建時間**：AI 模型檔案較大，首次構建可能需要較長時間
2. **記憶體需求**：確保 Docker 有足夠記憶體來載入 AI 模型
3. **開發環境**：開發環境會掛載本地代碼，可以即時重載
4. **安全性**：生產環境建議配置更嚴格的 CORS 和防火牆規則

### 最佳實踐
1. **版本控制**：使用 Git 標籤標記每個發布版本
2. **測試流程**：先在開發環境測試，再部署到生產環境
3. **監控日誌**：定期檢查應用日誌，及時發現問題
4. **定期清理**：定期清理未使用的 Docker 映像和容器

## 🎉 完成！

現在您的 SyncAI 應用已經完全容器化並支援區域網路訪問。您可以：

- 在任何連接相同 WiFi 的設備上使用應用
- 輕鬆部署到其他支援 Docker 的環境
- 通過 Docker 命令管理整個應用生命週期

如有任何問題，請檢查日誌或參考故障排除部分！
