# Comic AI 配置快速參考卡
# Quick Configuration Reference Card

## 🎯 核心配置位置

```
/root/comic_ai/
├── .env                           ← 環境變量 (實際使用)
├── .env.template                  ← 環境變量模板 (版本控制)
├── .env.example                   ← 環境變量示例
├── config/
│   ├── main_system_config.yaml    ← 主系統配置
│   ├── api_config.yaml            ← API 集成
│   ├── logging_config.yaml        ← 日誌系統
│   ├── database_config.yaml       ← 數據庫
│   ├── security_config.yaml       ← 安全設置
│   ├── deployment_config.yaml     ← 部署配置
│   ├── trading_config.yaml        ← 交易系統
│   └── ...
├── engine/
│   └── engine_config.yaml         ← 量子引擎
└── dashboard/
    └── dashboard_config.yaml      ← 儀表板
```

## ⚡ 快速開始

### 1. 初始化配置
```bash
# 複製環境模板
cp /root/comic_ai/.env.template /root/comic_ai/.env

# 編輯實際值
nano /root/comic_ai/.env
```

### 2. 必填項目
```bash
# 生成 JWT 密鑰
python3 -c "import secrets; print('SECURITY_JWT_SECRET=' + secrets.token_urlsafe(32))"

# 複製輸出結果到 .env
```

### 3. 驗證配置
```bash
cd /root/comic_ai
python3 -c "
from dotenv import load_dotenv
import os
load_dotenv()
print('✅ Configuration loaded successfully')
"
```

## 🔑 關鍵環境變量

### 系統
```bash
COMIC_AI_ENV=production           # 環境: production/staging/development
COMIC_AI_VERSION=2.0.0           # 版本
LOG_LEVEL=INFO                   # 日誌級別
TIMEZONE=Asia/Hong_Kong          # 時區
```

### 服務器端口
```bash
DASHBOARD_PORT=8080              # Dashboard
CLI_PORT=8081                    # CLI
HTTP_SERVER_PORT=8083            # HTTP Server
```

### 數據庫
```bash
DATABASE_TYPE=sqlite
DATABASE_PATH=data/comic_ai.db
REDIS_HOST=localhost
REDIS_PORT=6379
```

### AI/ML
```bash
VERTEX_AI_MODEL=Claude-3-5-sonnet@20241022
OPENAI_MODEL=gpt-4-turbo
VERTEX_AI_TEMPERATURE=0.7
VERTEX_AI_MAX_TOKENS=2048
```

### 安全
```bash
SECURITY_JWT_SECRET=[生成的密鑰]
SECURITY_SSL_CERT_PATH=/etc/letsencrypt/live/cosmic-ai.uk/fullchain.pem
SECURITY_SSL_KEY_PATH=/etc/letsencrypt/live/cosmic-ai.uk/privkey.pem
```

### 通知
```bash
TELEGRAM_BOT_TOKEN=[your-token]
TELEGRAM_CHAT_ID=[your-chat-id]
SLACK_WEBHOOK_URL=[optional]
```

## 🔍 配置驗證清單

- [ ] .env 文件已創建且包含所有必填項
- [ ] JWT 密鑰已生成 (最少 32 字符)
- [ ] SSL 證書路徑正確
- [ ] 數據庫連接已驗證
- [ ] API 密鑰已配置
- [ ] Redis 連接已測試
- [ ] 日誌目錄可寫入
- [ ] 備份目錄已創建

## 📋 常見配置任務

### 更改日誌級別
```bash
# 編輯 .env
LOG_LEVEL=DEBUG

# 或編輯 config/logging_config.yaml
logging:
  level: DEBUG
```

### 修改數據庫路徑
```bash
# 編輯 .env
DATABASE_PATH=/path/to/new/database.db

# 重啟應用
```

### 配置新的 API
```bash
# 1. 編輯 .env
OPENAI_API_KEY=your-key

# 2. 編輯 config/api_config.yaml
api:
  openai:
    enabled: true
    api_key: ${OPENAI_API_KEY}

# 3. 在代碼中使用
os.getenv('OPENAI_API_KEY')
```

### 啟用/禁用功能
```bash
# 編輯 config/main_system_config.yaml
features:
  quantum_analysis: true          # 啟用量子分析
  immune_system: true             # 啟用免疫系統
  intelligent_agents: true        # 啟用智能代理
```

## ⚠️ 安全最佳實踐

1. **從不提交 .env 到 Git**
   ```bash
   echo ".env" >> .gitignore
   ```

2. **定期輪換 API 密鑰**
   - 每 90 天執行一次
   - 文檔化輪換日期

3. **備份敏感配置**
   ```bash
   # 加密備份
   gpg --encrypt /root/comic_ai/.env
   ```

4. **監控配置更改**
   ```bash
   # 檢查日誌
   tail -f /root/comic_ai/logs/audit.log
   ```

5. **驗證配置權限**
   ```bash
   # 只有所有者可讀取
   chmod 600 /root/comic_ai/.env
   ```

## 🚨 故障排除

### 配置未加載
```bash
# 檢查 .env 格式
python3 -m py_compile .env

# 驗證環境變量
env | grep COMIC_AI
```

### 路徑問題
```bash
# 驗證路徑存在
ls -la /root/comic_ai/data/
ls -la /root/comic_ai/logs/

# 檢查權限
stat /root/comic_ai/logs/
```

### 連接問題
```bash
# 測試 Redis
redis-cli ping

# 測試數據庫
sqlite3 /root/comic_ai/data/comic_ai.db "SELECT 1"

# 測試 API
curl -I https://cosmic-ai.uk/api/health
```

## 📞 支持資源

- 完整報告: `/root/comic_ai/CONFIG_SETUP_REPORT.md`
- API 配置: `/root/comic_ai/config/api_config.yaml`
- 日誌配置: `/root/comic_ai/config/logging_config.yaml`
- 安全配置: `/root/comic_ai/config/security_config.yaml`

## 📈 性能調優

### 優化內存使用
```yaml
COMIC_AI_CACHE_SIZE=2GB           # 增加或減少
QUANTUM_RAM_SIZE=2GB              # 量子內存
```

### 優化 I/O
```yaml
DATABASE_CACHE_SIZE=10000          # SQLite 緩存
LOGGING_MAX_SIZE=500MB             # 日誌大小限制
```

### 優化 CPU
```yaml
COMIC_AI_MAX_WORKERS=8             # 工作線程數
ML_BATCH_SIZE=32                   # 批處理大小
```

---

**最後更新**: 2026-02-13
**版本**: 1.0
**狀態**: ✅ 生效中
