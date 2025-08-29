# SyncAI Windows 安裝與控制腳本

本目錄包含了 SyncAI 專案在 Windows 系統上的一鍵安裝和控制腳本。

## 📁 腳本檔案說明

### 一鍵安裝腳本
- **`install_syncai.bat`** - 完整的一鍵安裝腳本（包含 git clone）
- **`quick_deploy.bat`** - 快速部署腳本（適用於已有專案目錄）

### 控制腳本
- **`control_panel.bat`** - 圖形化控制面板（推薦使用）
- **`start_dev.bat`** - 啟動開發環境
- **`stop_dev.bat`** - 停止開發環境

### 輔助腳本
- **`download_model.bat`** - 下載 AI 模型
- **`setup_dev.bat`** - 設置開發環境

## 🚀 快速開始

### 方案一：全新安裝（推薦新用戶）

1. 創建一個新目錄（例如：`C:\SyncAI-Install`）
2. 下載 `install_syncai.bat` 到該目錄
3. 雙擊運行 `install_syncai.bat`
4. 按照提示完成安裝

### 方案二：已有專案目錄

1. 確保您在 SyncAI 專案根目錄中
2. 雙擊運行 `quick_deploy.bat`
3. 等待部署完成

### 方案三：使用控制面板（推薦）

1. 雙擊運行 `control_panel.bat`
2. 選擇對應的操作選項
3. 按照螢幕提示操作

## 📋 系統需求

### 必需軟體
- **Windows 10/11** (64位元)
- **Docker Desktop** - [下載連結](https://docs.docker.com/desktop/install/windows-install/)
- **Git** - [下載連結](https://git-scm.com/download/win) （僅全新安裝需要）

### 硬體需求
- **RAM**: 至少 8GB (推薦 16GB)
- **硬碟空間**: 至少 10GB 可用空間
- **網路**: 穩定的網際網路連線（用於下載模型和映像）

## 🔧 安裝步驟詳解

### 1. Git Clone
- 自動從 GitHub 克隆最新版本
- 如果目錄已存在則跳過

### 2. AI 模型準備
- 下載 Mistral-7B 模型（約 5.1GB）
- 自動驗證檔案完整性
- 支援斷點續傳

### 3. Docker 檢查
- 驗證 Docker Desktop 安裝
- 檢查 Docker 服務運行狀態
- 提供安裝指引（如需要）

### 4. Docker 部署
- 自動建構前端和後端映像
- 啟動容器服務
- 配置網路和埠映射

### 5. IP 地址查詢
- 自動檢測本機 IP 地址
- 提供區域網路存取地址
- 顯示服務狀態

### 6. 控制指令
- 創建便捷的控制腳本
- 提供啟動、停止、重啟功能
- 包含狀態查詢和日誌查看

## 🌐 存取地址

安裝完成後，您可以通過以下地址存取 SyncAI：

### 本機存取
- **前端**: http://localhost
- **後端 API**: http://localhost:8000

### 區域網路存取
- **前端**: http://[您的IP地址]
- **後端 API**: http://[您的IP地址]:8000

> 💡 **提示**: 使用 `control_panel.bat` 中的選項 6 來查看當前可用的存取地址

## 🎮 控制指令

### 使用控制面板（推薦）
```batch
# 啟動控制面板
control_panel.bat
```

### 手動控制
```batch
# 啟動服務
start_meeting.bat

# 停止服務
stop_meeting.bat

# 重啟服務
restart_meeting.bat

# 查看狀態
status_meeting.bat
```

### Docker 原生指令
```batch
# 啟動
docker-compose -f docker/docker-compose.yml up -d

# 停止
docker-compose -f docker/docker-compose.yml down

# 重啟
docker-compose -f docker/docker-compose.yml restart

# 查看狀態
docker-compose -f docker/docker-compose.yml ps

# 查看日誌
docker-compose -f docker/docker-compose.yml logs -f
```

## 🐛 故障排除

### 常見問題

#### 1. Docker 相關問題
**問題**: Docker 未安裝或服務未運行
**解決**: 
- 安裝 Docker Desktop
- 確保 Docker Desktop 正在運行
- 重新啟動 Docker Desktop

#### 2. 模型下載失敗
**問題**: AI 模型下載緩慢或失敗
**解決**: 
- 檢查網路連線
- 重新運行 `download_model.bat`
- 考慮使用 VPN 或代理

#### 3. 埠被佔用
**問題**: 80 或 8000 埠被其他程式佔用
**解決**: 
- 停止佔用埠的程式
- 或修改 `docker-compose.yml` 中的埠映射

#### 4. 容器啟動失敗
**問題**: 容器無法正常啟動
**解決**: 
- 檢查 Docker 日誌：`docker-compose -f docker/docker-compose.yml logs`
- 確保模型檔案存在且完整
- 重新建構映像：`docker-compose -f docker/docker-compose.yml up -d --build`

### 獲取幫助

如果遇到問題，請：

1. 查看控制面板中的服務狀態和日誌
2. 檢查 Docker Desktop 是否正常運行
3. 確認防火牆設置允許相關埠
4. 提交 Issue 到 GitHub 專案

## 📝 注意事項

- **首次啟動**: 可能需要較長時間來下載映像和模型
- **防火牆**: 確保 Windows 防火牆允許 Docker 存取
- **資源使用**: AI 模型需要較多記憶體，建議關閉不必要的程式
- **網路分享**: 要讓其他裝置存取，請確保網路設置允許

## 🔄 更新說明

要更新到最新版本：

1. 停止目前服務
2. 執行 `git pull` 更新程式碼
3. 重新運行部署腳本
4. 或使用控制面板中的相關功能

---

**版本**: 1.0.0  
**最後更新**: 2025年8月29日  
**相容性**: Windows 10/11, Docker Desktop
