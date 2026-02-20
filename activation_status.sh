#!/bin/bash
# Comic AI 激活狀態展示 - 便捷啟動腳本
# 直接運行此腳本即可打開激活狀態儀表板

cd /root/comic_ai

# 檢查虛擬環境
if [ ! -d "venv" ]; then
    echo "❌ 虛擬環境未找到"
    echo "📝 請先運行: python3 -m venv venv"
    exit 1
fi

# 激活虛擬環境
source venv/bin/activate

# 運行激活狀態 CLI
echo "🚀 啟動 Comic AI 激活狀態儀表板..."
python activation_status_cli.py

# 停用虛擬環境
deactivate
