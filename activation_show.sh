#!/bin/bash
# Comic AI 激活展示啟動器 - 自動展示所有激活情況

cd /root/comic_ai

# 檢查虛擬環境
if [ ! -d "venv" ]; then
    echo "❌ 虛擬環境未找到"
    echo "📝 請先運行: python3 -m venv venv"
    exit 1
fi

# 激活虛擬環境
source venv/bin/activate

# 運行激活展示
python activation_display.py

# 停用虛擬環境
deactivate
