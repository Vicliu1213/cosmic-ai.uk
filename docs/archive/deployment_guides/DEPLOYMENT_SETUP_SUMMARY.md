# 🚀 Comic AI 部署配置總結

## 項目情況

| 項目 | 值 |
|-----|-----|
| 項目目錄 | `/root/comic_ai/` |
| 生產域名 | `cosmic-ai.uk` |
| 開發環境 | localhost (本地) |
| 狀態 | ✅ 完全就緒 |

---

## 環境配置

### 📌 開發環境 (Development)

**用途**: 本地開發、測試、演示

```yaml
DEPLOYMENT_ENV: development
DOMAIN_NAME: localhost
SSL_CERT: /root/comic_ai/ssl_certs/cert.pem (自簽名)
SSL_KEY: /root/comic_ai/ssl_certs/key.pem
VALID: 2026-02-17 ~ 2027-02-17
```

**啟動方式**:
```bash
cd /root/comic_ai
./start_https_server.sh
# 或
python dashboard/app_ssl.py
```

**訪問地址**:
```
https://localhost:8443
https://127.0.0.1:8443
```

⚠️ **注意**: 瀏覽器會顯示自簽名憑證警告，這是正常的（選擇繼續瀏覽）

---

### 📌 生產環境 (Production)

**用途**: cosmic-ai.uk 實際部署

```yaml
DEPLOYMENT_ENV: production
DOMAIN_NAME: cosmic-ai.uk
SSL_CERT: /etc/letsencrypt/live/cosmic-ai.uk/fullchain.pem (Let's Encrypt)
SSL_KEY: /etc/letsencrypt/live/cosmic-ai.uk/privkey.pem
VALID: 2026-02-13 ~ 2026-05-14
```

**切換方式**:

編輯 `.env` 文件：
```bash
# 將此行改為:
DEPLOYMENT_ENV=production

# 並更新憑證路徑:
SECURITY_SSL_CERT_PATH=/etc/letsencrypt/live/cosmic-ai.uk/fullchain.pem
SECURITY_SSL_KEY_PATH=/etc/letsencrypt/live/cosmic-ai.uk/privkey.pem
```

**訪問地址**:
```
https://cosmic-ai.uk
```

✅ **優勢**: 浏览器完全信任，显示安全徽章

---

## 🔐 SSL/TLS 憑證清單

### 開發環境憑證
```
📁 /root/comic_ai/ssl_certs/
├── cert.pem (1200 bytes) ✅
├── key.pem (1704 bytes) ✅
└── 有效期: 1 年
```

### 生產環境憑證 (cosmic-ai.uk)
```
📁 /etc/letsencrypt/live/cosmic-ai.uk/
├── cert.pem (證書) ✅
├── chain.pem (中間憑證) ✅
├── fullchain.pem (完整鏈) ✅ [使用此項]
├── privkey.pem (私鑰) ✅
└── 有效期: ~3 個月 (自動續期)
```

---

## 📋 完整部署檢查清單

### ✅ 已完成

- [x] .env 配置文件已生成 (96 個配置項)
- [x] 所有 YAML 配置文件已驗證 (18 個文件)
- [x] 配置子目錄完整 (core, deployment, optimization, security, services, templates)
- [x] 必要的系統目錄已初始化
- [x] 開發環境 SSL 自簽名憑證已生成
- [x] 生產環境 Let's Encrypt 憑證已驗證
- [x] 部署狀態檢查腳本已創建

### ⚠️ 待辦

- [ ] 填入 .env 中的敏感信息 (API 密鑰等)
- [ ] 根據部署場景修改 DEPLOYMENT_ENV
- [ ] 如需部署到 cosmic-ai.uk，確保 DNS 解析正確
- [ ] 配置 nginx/Apache 反向代理（如適用）

---

## 🔧 快速命令

### 檢查部署狀態
```bash
cd /root/comic_ai
bash check_deployment_status.sh
```

### 切換到開發環境
```bash
sed -i 's/DEPLOYMENT_ENV=.*/DEPLOYMENT_ENV=development/' .env
```

### 切換到生產環境
```bash
sed -i 's/DEPLOYMENT_ENV=.*/DEPLOYMENT_ENV=production/' .env
```

### 驗證 SSL 憑證
```bash
# 開發環境
openssl x509 -in /root/comic_ai/ssl_certs/cert.pem -noout -dates

# 生產環境
openssl x509 -in /etc/letsencrypt/live/cosmic-ai.uk/fullchain.pem -noout -dates
```

### 查看完整部署指南
```bash
cat .env.deployment
```

---

## 📚 配置文件位置

| 文件 | 位置 | 說明 |
|-----|------|------|
| 環境配置 | `.env` | 主要配置文件（96 項配置） |
| 部署指南 | `.env.deployment` | 部署場景說明和快速參考 |
| YAML 配置 | `config/*.yaml` | 18 個配置文件 |
| 初始化日誌 | `logs/initialization.log` | 系統初始化記錄 |

---

## 🌐 訪問地址參考

### 開發環境 (localhost)

| 服務 | 地址 | 狀態 |
|-----|------|------|
| Dashboard | https://localhost:8443 | 🟡 自簽名 |
| API | https://localhost:8443/api | 🟡 自簽名 |
| Health Check | https://localhost:8443/health | 🟡 自簽名 |

### 生產環境 (cosmic-ai.uk)

| 服務 | 地址 | 狀態 |
|-----|------|------|
| Dashboard | https://cosmic-ai.uk | 🟢 Let's Encrypt |
| API | https://cosmic-ai.uk/api | 🟢 Let's Encrypt |
| Health Check | https://cosmic-ai.uk/health | 🟢 Let's Encrypt |

---

## ✨ 系統狀態

```
🎯 Comic AI 系統完全就緒
├── ✅ 環境配置已生成
├── ✅ 所有配置文件已驗證
├── ✅ 系統目錄已初始化
├── ✅ 開發憑證已生成
├── ✅ 生產憑證已驗證
└── ✅ 部署工具已完善
```

---

## 🔍 快速故障排除 (Quick Troubleshooting)

### 常見問題速查表

| 問題 | 症狀 | 解決方案 |
|------|------|---------|
| SSL 證書過期 | 瀏覽器警告 | `sudo certbot renew --force-renewal` |
| 連接被拒絕 | `Connection refused` | 檢查服務是否運行: `systemctl status comic-ai` |
| 配置讀取失敗 | `.env` 錯誤 | 驗證 `.env` 文件格式: `python -m dotenv list` |
| 數據庫鎖定 | 操作超時 | 重啟應用: `systemctl restart comic-ai` |
| 內存泄漏 | 緩慢變慢 | 檢查進程: `ps aux \| grep python` |

### 自動化故障排除腳本

```bash
#!/bin/bash
# scripts/quick_fix.sh
# 快速故障排除腳本

echo "🔧 Running Quick Troubleshoot..."

# 檢查配置
echo "Validating configuration..."
python3 scripts/config_validator.py

# 檢查服務
echo "Checking services..."
python3 scripts/deployment_monitor.py

# 清理緩存
echo "Cleaning cache..."
rm -rf /tmp/comic_ai_cache/*

# 重啟服務
echo "Restarting service..."
systemctl restart comic-ai

echo "✅ Troubleshoot complete!"
```

---

## 🛠️ 自動化部署工具

### 一鍵部署腳本

```bash
#!/bin/bash
# scripts/auto_deploy.sh
# 完整自動化部署腳本

set -e

echo "🚀 Starting automated deployment..."

# Step 1: 驗證環境
echo "1️⃣ Validating environment..."
python3 scripts/config_validator.py || exit 1

# Step 2: 備份
echo "2️⃣ Creating backup..."
mkdir -p data/backups
tar -czf data/backups/pre_deploy_$(date +%Y%m%d_%H%M%S).tar.gz data/ config/

# Step 3: 安裝依賴
echo "3️⃣ Installing dependencies..."
pip install -r requirements.txt --quiet

# Step 4: 初始化數據庫
echo "4️⃣ Initializing database..."
python3 -c "from src.core import init_db; init_db()"

# Step 5: 啟動服務
echo "5️⃣ Starting services..."
systemctl restart redis-server
systemctl restart comic-ai

# Step 6: 驗證部署
echo "6️⃣ Verifying deployment..."
sleep 5
curl -s https://localhost:8443/health > /dev/null && echo "✅ Deployment successful!" || echo "❌ Deployment failed!"

echo "🎉 Automated deployment complete!"
```

### 健康檢查 Cron 任務

```bash
# /etc/cron.d/comic-ai-health
# 每 5 分鐘運行一次健康檢查

*/5 * * * * root python3 /root/comic_ai/scripts/deployment_monitor.py >> /var/log/comic-ai-health.log 2>&1
0 * * * * root python3 /root/comic_ai/scripts/backup.sh >> /var/log/comic-ai-backup.log 2>&1
0 0 * * 0 root python3 /root/comic_ai/scripts/maintenance.sh >> /var/log/comic-ai-maintenance.log 2>&1
```

---

## 📊 部署性能基準線

| 指標 | 目標值 | 當前狀態 |
|-----|-------|--------|
| 應用啟動時間 | < 10s | 待測試 |
| API 響應時間 | < 500ms | 待測試 |
| 內存使用量 | < 500MB | 待測試 |
| CPU 利用率 | < 50% | 待測試 |
| 磁盤 I/O | < 100MB/s | 待測試 |
| 數據庫查詢 | < 100ms (95%) | 待測試 |

### 性能測試命令

```bash
# 負載測試
ab -n 1000 -c 10 https://localhost:8443/health

# 內存分析
python -m memory_profiler scripts/deployment_monitor.py

# 性能分析
python -m cProfile -s cumulative src/cli/cli.py

# 磁盤使用
du -sh data/ config/ logs/
```

---

## 📞 需要幫助？

查看相關文檔：
- `FIRST_TIME_DEPLOYMENT_GUIDE.md` - 首次部署指南
- `QUICK_CONFIG_REFERENCE.md` - 快速配置參考
- `LIVE_TRADING_GUIDE.md` - 交易系統指南
- `README.md` - 項目概述

