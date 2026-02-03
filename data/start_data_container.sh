#!/bin/bash
# 數據容器化管理腳本

echo "🚀 啟動 Comic AI 數據容器化服務..."

# 檢查 Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker 未安裝，正在安裝..."
    curl -fsSL https://get.docker.com | sh
    systemctl start docker
    systemctl enable docker
fi

# 檢查 Docker Compose
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose 未安裝，正在安裝..."
    apt install docker-compose-plugin -y
fi

# 啟動服務
if command -v docker-compose &> /dev/null; then
    docker-compose up -d
else
    docker compose up -d
fi

echo "✅ 容器化服務已啟動"
echo "📊 Redis 緩存: localhost:6379"
echo "📁 數據掛載: ./data, ./config, ./logs, ./uploads"