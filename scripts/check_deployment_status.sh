#!/bin/bash

echo "=================================================="
echo "🔍 Comic AI 部署狀態檢查"
echo "=================================================="
echo ""

# 檢查環境設置
DEPLOYMENT_ENV=$(grep "^DEPLOYMENT_ENV=" .env | cut -d= -f2)
echo "📌 當前部署環境: $DEPLOYMENT_ENV"
echo ""

# 檢查憑證
echo "🔐 SSL 憑證狀態:"
echo "---------"

if [ "$DEPLOYMENT_ENV" = "development" ]; then
    CERT_PATH="/root/comic_ai/ssl_certs/cert.pem"
    KEY_PATH="/root/comic_ai/ssl_certs/key.pem"
    echo "開發環境 (localhost)"
else
    CERT_PATH="/etc/letsencrypt/live/cosmic-ai.uk/fullchain.pem"
    KEY_PATH="/etc/letsencrypt/live/cosmic-ai.uk/privkey.pem"
    echo "生產環境 (cosmic-ai.uk)"
fi

if [ -f "$CERT_PATH" ] && [ -f "$KEY_PATH" ]; then
    echo "✅ 證書: $CERT_PATH"
    echo "✅ 私鑰: $KEY_PATH"
    echo ""
    echo "📋 證書信息:"
    openssl x509 -in "$CERT_PATH" -noout -text | grep -E "Subject:|Issuer:|Not Before|Not After|Public-Key"
else
    echo "❌ 證書或私鑰不存在！"
    echo "   證書: $CERT_PATH"
    echo "   私鑰: $KEY_PATH"
fi

echo ""
echo "=================================================="
echo "✅ 檢查完成"
echo "=================================================="
