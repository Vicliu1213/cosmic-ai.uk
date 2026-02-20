#!/bin/bash
# Comic AI 激活介面主入口
# 所有激活功能的統一入口

cd /root/comic_ai

# 檢查虛擬環境
if [ ! -d "venv" ]; then
    echo "❌ 虛擬環境未找到"
    echo "📝 請先運行: python3 -m venv venv && pip install -r requirements.txt"
    exit 1
fi

# 激活虛擬環境
source venv/bin/activate

# 運行主菜單
python activation_main_menu.py

# 停用虛擬環境
deactivate
