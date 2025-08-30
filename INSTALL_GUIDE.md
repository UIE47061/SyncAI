# SyncAI 一鍵安裝指南

本指南將協助您完成 SyncAI 的完整安裝和設置。

## 🚀 一鍵安裝

### 執行安裝腳本

在 SyncAI 專案根目錄中，執行以下命令：

```batch
scripts\one_click_install.bat
```

### 安裝步驟

腳本將自動完成以下步驟：

1. **檢查並安裝 Docker Desktop**
   - 自動檢查 Docker 是否已安裝
   - 如未安裝，將自動下載並安裝 Docker Desktop
   - 如果需要重新啟動電腦，請重新執行腳本

2. **AnythingLLM 設置指南**
   - 引導您下載 AnythingLLM Desktop 版本
   - 提供詳細的安裝和設置說明
   - 確認 AnythingLLM 在 localhost:3001 運行

3. **獲取 API 金鑰**
   - 自動打開 AnythingLLM 管理介面
   - 引導您創建和獲取 API 金鑰
   - 驗證金鑰格式

4. **配置環境變數**
   - 自動設置系統環境變數 `ANYTHINGLLM_API_KEY`
   - 創建 `.env` 檔案存儲配置
   - 更新 `docker-compose.yml` 配置

5. **部署正式環境**
   - 自動構建和啟動 SyncAI 服務
   - 檢查服務狀態
   - 等待服務完全啟動

6. **完成設置**
   - 顯示訪問地址和控制指令
   - 提供後續維護說明

## 📋 系統需求

### 必要條件

- **作業系統**: Windows 10 64-bit 或 Windows 11
- **記憶體**: 至少 8GB RAM (推薦 16GB)
- **硬碟空間**: 至少 10GB 可用空間
- **網路**: 穩定的網際網路連線

### 軟體需求

- **Docker Desktop**: 腳本將自動安裝
- **AnythingLLM Desktop**: 需要手動下載安裝

## 🔧 手動設置步驟

如果自動安裝失敗，您可以按照以下步驟手動設置：

### 1. 安裝 Docker Desktop

1. 前往 [Docker Desktop 下載頁面](https://docs.docker.com/desktop/install/windows-install/)
2. 下載適合您系統的版本
3. 以管理員身份執行安裝程式
4. 重新啟動電腦
5. 啟動 Docker Desktop

### 2. 安裝 AnythingLLM

1. 前往 [AnythingLLM 下載頁面](https://anythingllm.com/download)
2. 選擇 "Desktop" 版本
3. 下載並安裝
4. 啟動 AnythingLLM
5. 創建工作區，名稱設為 `syncai`
6. 確保服務運行在 `localhost:3001`

### 3. 獲取 API 金鑰

1. 在瀏覽器中打開 `http://localhost:3001`
2. 登入您的帳戶
3. 導航到設置 → API Keys
4. 創建新的 API 金鑰
5. 複製金鑰 (格式: XXX-XXXXXXX-XXXXXXX-XXXXXXX)

### 4. 配置環境變數

1. 複製 `.env.template` 為 `.env`
2. 編輯 `.env` 檔案，將 `YOUR_API_KEY_HERE` 替換為您的實際 API 金鑰
3. 設置系統環境變數:
   ```batch
   setx ANYTHINGLLM_API_KEY "您的API金鑰"
   ```

### 5. 部署服務

```batch
docker-compose -f docker/docker-compose.yml up -d --build
```

## 📱 使用說明

### 訪問 SyncAI

安裝完成後，您可以通過以下地址訪問：

- **前端**: http://localhost (或 http://您的IP地址)
- **後端 API**: http://localhost:8000
- **AnythingLLM**: http://localhost:3001

### 服務控制

#### 啟動服務
```batch
docker-compose -f docker/docker-compose.yml up -d
```

#### 停止服務
```batch
docker-compose -f docker/docker-compose.yml down
```

#### 重啟服務
```batch
docker-compose -f docker/docker-compose.yml restart
```

#### 查看服務狀態
```batch
docker-compose -f docker/docker-compose.yml ps
```

#### 查看服務日誌
```batch
docker-compose -f docker/docker-compose.yml logs -f
```

### 快速重新部署

如果需要重新部署（例如代碼更新後），可以使用：

```batch
scripts\redeploy.bat
```

## 🔧 常見問題

### Q: Docker 安裝失敗怎麼辦？

A: 請檢查：
- 是否以管理員身份執行
- 系統是否為 Windows 10/11 64-bit
- 是否開啟了虛擬化功能 (BIOS 設置)
- 是否有足夠的磁碟空間

### Q: 無法連接到 AnythingLLM？

A: 請確認：
- AnythingLLM 已正確安裝並啟動
- 服務運行在 localhost:3001
- 防火牆未阻止連線
- 工作區已正確創建

### Q: API 金鑰格式錯誤？

A: API 金鑰應為格式：`XXX-XXXXXXX-XXXXXXX-XXXXXXX`
如果格式不同，請確認您複製了正確的金鑰。

### Q: 服務無法啟動？

A: 請檢查：
- Docker Desktop 是否正在運行
- 埠號 80 和 8000 是否被其他程式佔用
- `.env` 檔案是否存在且配置正確
- 查看日誌了解具體錯誤

### Q: 如何更新 API 金鑰？

A: 有兩種方法：
1. 重新執行 `one_click_install.bat`
2. 手動編輯 `.env` 檔案，然後執行 `redeploy.bat`

## 🔧 維護和更新

### 定期維護

1. **保持 Docker Desktop 更新**
2. **定期更新 AnythingLLM**
3. **監控服務狀態**
4. **備份重要配置**

### 系統重啟後

重新啟動電腦後，需要：
1. 啟動 Docker Desktop
2. 啟動 AnythingLLM
3. 如果服務未自動啟動，執行：
   ```batch
   docker-compose -f docker/docker-compose.yml up -d
   ```

### 故障排除

如果遇到問題：
1. 查看 Docker 日誌
2. 檢查防火牆設置
3. 驗證網路連線
4. 重新執行安裝腳本

## 📞 技術支援

如果您需要進一步的協助：
1. 查看專案文檔
2. 檢查 GitHub Issues
3. 聯繫開發團隊

---

🎉 感謝使用 SyncAI！希望您有一個愉快的使用體驗。
