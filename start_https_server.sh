#!/bin/bash

# Comic AI HTTPS 快速啟動腳本
# Quick start HTTPS server for Comic AI

set -e

echo "🚀 Comic AI HTTPS 服務器啟動"
echo "================================"
echo ""

# 檢查 SSL 憑證
if [ ! -f "ssl_certs/cert.pem" ] || [ ! -f "ssl_certs/key.pem" ]; then
    echo "⚠️  SSL 憑證不存在，正在生成..."
    python scripts/setup_ssl.py generate --domain localhost --days 365
    echo ""
fi

# 驗證 SSL 憑證
echo "🔍 驗證 SSL 憑證..."
python scripts/setup_ssl.py verify
echo ""

# 顯示配置信息
echo "📋 配置信息:"
echo "   協議: HTTPS"
echo "   主機: 0.0.0.0"
echo "   端口: 8443"
echo "   證書: ssl_certs/cert.pem"
echo "   私鑰: ssl_certs/key.pem"
echo ""

# 提示用戶
echo "⏳ 啟動服務器..."
echo "📍 訪問地址: https://localhost:8443"
echo "🧪 測試端點: https://localhost:8443/health"
echo "🛑 按 Ctrl+C 停止服務器"
echo ""

# 啟動 Dashboard HTTPS 服務器
cd "$(dirname "$0")"
python dashboard/app_ssl.py
