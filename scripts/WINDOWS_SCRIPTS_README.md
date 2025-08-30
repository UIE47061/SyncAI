# SyncAI Windows 安裝與控制腳本

本目錄包含 SyncAI 在 Windows 環境下的安裝、啟動和控制腳本，讓您快速部署和管理 SyncAI 服務。

## 🚀 快速開始

### 1. 一鍵安裝（推薦）

```batch
# 中文版一鍵安裝
0_one_click_install_TW.bat

# 英文版一鍵安裝  
0_one_click_install_US.bat
```

**功能**：自動完成 Docker 安裝、AnythingLLM 設置、環境配置和服務部署

## 📥 安裝腳本

### 基礎安裝
```batch
# 安裝 Docker Desktop
install_docker.bat

# 完整 SyncAI 安裝
install_syncai.bat
```

### 開發環境設置
```batch
# 設置開發環境
setup_dev.bat

# 下載 AI 模型
download_model.bat
```

## ▶️ 啟動與控制

### 開發服務
```batch
# 啟動開發服務
start_dev.bat

# 停止開發服務
stop_dev.bat
```

### 生產環境
```batch
# 快速部署
quick_deploy.bat

# 重新部署
redeploy.bat
```

## 🎛️ 控制與監控

### 服務管理
```batch
# 控制面板（推薦）
control_panel.bat

# 檢查服務狀態
service_status.bat

# 開啟網頁介面
open_web.bat
```

## 📋 使用步驟

1. **初次安裝**：
   ```batch
   # 執行一鍵安裝
   0_one_click_install_TW.bat
   ```

2. **日常啟動**：
   ```batch
   # 使用控制面板
   control_panel.bat
   ```

3. **檢查狀態**：
   ```batch
   # 查看服務狀態
   service_status.bat
   ```

4. **訪問服務**：
   ```batch
   # 自動開啟瀏覽器
   open_web.bat
   ```

## ⚠️ 注意事項

- 所有腳本需要以**管理員身份**執行
- 首次安裝可能需要重新啟動電腦
- 確保 Windows 11 或 Windows 10 (1903 以上版本)
- 建議至少 8GB RAM 用於 AI 模型運行

## 🆘 常見問題

**Q: 一鍵安裝失敗怎麼辦？**
A: 檢查網路連線，以管理員身份重新執行

**Q: 服務無法啟動？**
A: 執行 `service_status.bat` 檢查狀態，確認 Docker 是否正常運行

**Q: 如何停止所有服務？**
A: 執行 `stop_dev.bat` 停止開發服務，或使用 `control_panel.bat` 進行管理
