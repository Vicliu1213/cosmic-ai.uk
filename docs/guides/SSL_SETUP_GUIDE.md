# Comic AI HTTPS/SSL 設置指南
# Comic AI HTTPS/SSL Setup Guide

## 快速開始 (Quick Start)

### 1️⃣ 生成 SSL 憑證

```bash
# 進入專案目錄
cd /root/comic_ai

# 安裝依賴（如需要）
pip install flask pyopenssl

# 生成自簽名憑證
python scripts/setup_ssl.py generate --domain localhost --days 365

# 或指定域名
python scripts/setup_ssl.py generate --domain your-domain.com --days 365
```

### 2️⃣ 驗證憑證

```bash
# 驗證憑證有效性
python scripts/setup_ssl.py verify

# 查看憑證詳細資訊
python scripts/setup_ssl.py info
```

### 3️⃣ 啟用 Dashboard HTTPS

編輯 `dashboard/dashboard_config.yaml`:

```yaml
# Server Settings
server:
  host: "0.0.0.0"
  port: 8443  # 改為 8443 (HTTPS 標準端口)
  debug: false
  
  # SSL/TLS Configuration
  ssl:
    enabled: true
    cert: "ssl_certs/cert.pem"
    key: "ssl_certs/key.pem"
```

### 4️⃣ 啟動 HTTPS 服務器

```bash
# 使用新的 app_ssl.py
python dashboard/app_ssl.py

# 或使用原始 app.py（已更新）
python dashboard/app.py
```

### 5️⃣ 測試連接

```bash
# 使用 curl（接受自簽名證書）
curl -k https://localhost:8443/health

# 或使用 Python requests
python -c "
import requests
requests.packages.urllib3.disable_warnings()
r = requests.get('https://localhost:8443/health', verify=False)
print(r.json())
"
```

## 配置詳解 (Configuration Details)

### SSL 憑證位置
- 證書: `ssl_certs/cert.pem`
- 私鑰: `ssl_certs/key.pem`

### 支持的協議
- ✅ TLSv1.2
- ✅ TLSv1.3
- ✅ SSLv3（已棄用但向後相容）

### 端口映射
- HTTP: 8080 (不安全)
- HTTPS: 8443 (安全)

## 生產環境推薦 (Production Recommendations)

### 使用 Let's Encrypt 免費憑證

```bash
# 安裝 Certbot
sudo apt-get install certbot python3-certbot-dns-digitalocean

# 獲取免費憑證
sudo certbot certonly --dns-digitalocean -d your-domain.com

# 證書位置
# /etc/letsencrypt/live/your-domain.com/fullchain.pem
# /etc/letsencrypt/live/your-domain.com/privkey.pem
```

### 使用 Gunicorn + Nginx

```bash
# 安裝
pip install gunicorn
sudo apt-get install nginx

# 啟動 Gunicorn
gunicorn --certfile=ssl_certs/cert.pem --keyfile=ssl_certs/key.pem \
  --bind 0.0.0.0:8443 dashboard.app_ssl:app

# Nginx 反向代理配置 (見下面)
```

### Nginx 配置範例

```nginx
server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    
    # SSL 安全設定
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    
    # 安全頭
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "DENY" always;
    
    # 代理到 Gunicorn
    location / {
        proxy_pass https://127.0.0.1:8443;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## 故障排除 (Troubleshooting)

### 問題 1: OpenSSL 未安裝

```bash
# Ubuntu/Debian
sudo apt-get install openssl

# macOS
brew install openssl

# CentOS/RHEL
sudo yum install openssl
```

### 問題 2: 憑證過期

```bash
# 重新生成憑證
python scripts/setup_ssl.py generate --force --days 365
```

### 問題 3: 端口被佔用

```bash
# 查找佔用端口的進程
sudo lsof -i :8443

# 更改 dashboard_config.yaml 中的端口
port: 9443  # 改為其他端口
```

### 問題 4: SSL 握手失敗

```bash
# 驗證憑證
python scripts/setup_ssl.py verify

# 檢查文件權限
chmod 644 ssl_certs/cert.pem
chmod 600 ssl_certs/key.pem
```

## 安全檢查清單 (Security Checklist)

- [ ] SSL 憑證已生成
- [ ] 私鑰檔案已保護 (chmod 600)
- [ ] 使用 HTTPS 而非 HTTP
- [ ] 啟用 HSTS (Strict-Transport-Security)
- [ ] 禁用弱加密算法
- [ ] 啟用 HTTP 安全頭
- [ ] 定期更新憑證
- [ ] 監控 SSL 憑證有效期

## 監控憑證有效期

```bash
# 檢查憑證過期日期
openssl x509 -in ssl_certs/cert.pem -noout -dates

# 自動檢查腳本
python -c "
import ssl
import datetime
from pathlib import Path

cert_file = 'ssl_certs/cert.pem'
context = ssl.create_default_context()
with open(cert_file, 'rb') as f:
    cert = ssl.DER_cert_to_PEM_cert(f.read())
    # 解析並顯示過期日期
"
```

## API 端點安全

所有 API 端點現在支持 HTTPS:

- ✅ `https://localhost:8443/` - 主頁面
- ✅ `https://localhost:8443/health` - 健康檢查
- ✅ `https://localhost:8443/api/status` - API 狀態
- ✅ `https://localhost:8443/test-clipboard` - 剪貼板測試

## 進階配置

### 自定義 SSL 選項

編輯 `dashboard/dashboard_config.yaml`:

```yaml
server:
  ssl:
    enabled: true
    cert: "ssl_certs/cert.pem"
    key: "ssl_certs/key.pem"
    # 進階選項
    protocol: "TLSv1.3"
    ciphers: "HIGH:!aNULL:!MD5"
    verify_mode: "CERT_NONE"  # 開發環境
    # verify_mode: "CERT_REQUIRED"  # 生產環境
```

### 雙協議支持 (HTTP + HTTPS)

```python
# 在 app.py 中
if __name__ == '__main__':
    # HTTP 端口
    Thread(target=lambda: app.run(port=8080, ssl_context=None)).start()
    
    # HTTPS 端口
    ssl_context = dashboard.get_ssl_config()
    app.run(port=8443, ssl_context=ssl_context)
```

## 進一步幫助

- 🔗 OpenSSL 文檔: https://www.openssl.org/docs/
- 🔗 Let's Encrypt: https://letsencrypt.org/
- 🔗 Flask SSL: https://flask.palletsprojects.com/
- 🔗 Nginx SSL: https://nginx.org/en/docs/http/ngx_http_ssl_module.html

---

**建議**: 在生產環境中使用 Let's Encrypt 免費憑證，而非自簽名憑證。
