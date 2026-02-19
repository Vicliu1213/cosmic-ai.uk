#!/bin/bash

# Comic AI HTTPS 伺服器背景執行版本
# HTTPS Server Background Execution Version

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
LOG_FILE="$SCRIPT_DIR/logs/https_server.log"

# 建立日誌目錄
mkdir -p "$(dirname "$LOG_FILE")"

echo "🚀 Comic AI HTTPS 服務器啟動" | tee -a "$LOG_FILE"
echo "================================" | tee -a "$LOG_FILE"
echo "[$(date '+%Y-%m-%d %H:%M:%S')] 啟動 HTTPS 伺服器..." | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# 檢查 SSL 憑證
if [ ! -f "ssl_certs/cert.pem" ] || [ ! -f "ssl_certs/key.pem" ]; then
    echo "⚠️  SSL 憑證不存在，正在生成..." | tee -a "$LOG_FILE"
    python scripts/setup_ssl.py generate --domain localhost --days 365 2>&1 | tee -a "$LOG_FILE"
    echo "" | tee -a "$LOG_FILE"
fi

# 驗證 SSL 憑證
echo "🔍 驗證 SSL 憑證..." | tee -a "$LOG_FILE"
python scripts/setup_ssl.py verify 2>&1 | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# 顯示配置信息
echo "📋 配置信息:" | tee -a "$LOG_FILE"
echo "   協議: HTTPS" | tee -a "$LOG_FILE"
echo "   主機: 0.0.0.0" | tee -a "$LOG_FILE"
echo "   端口: 8443" | tee -a "$LOG_FILE"
echo "   證書: ssl_certs/cert.pem" | tee -a "$LOG_FILE"
echo "   私鑰: ssl_certs/key.pem" | tee -a "$LOG_FILE"
echo "   日誌: $LOG_FILE" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# 提示用戶
echo "⏳ 啟動服務器..." | tee -a "$LOG_FILE"
echo "📍 訪問地址: https://localhost:8443" | tee -a "$LOG_FILE"
echo "🧪 測試端點: https://localhost:8443/health" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# 啟動 Dashboard HTTPS 服務器（背景執行，日誌記錄）
cd "$SCRIPT_DIR"
python dashboard/app_ssl.py >> "$LOG_FILE" 2>&1 &

# 記錄進程 ID
echo "[$(date '+%Y-%m-%d %H:%M:%S')] HTTPS 伺服器啟動，進程 ID: $!" >> "$LOG_FILE"
echo "[$(date '+%Y-%m-%d %H:%M:%S')] 伺服器運行中..." >> "$LOG_FILE"

# 等待進程（防止 tmux 視窗立即關閉）
wait
