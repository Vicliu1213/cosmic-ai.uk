#!/bin/bash
# 互動式儀表版啟動腳本
# Interactive Dashboard Launcher

echo "🚀 啟動 Cosmic AI 互動式儀表版..."
echo ""

# 檢查 Python 3
if ! command -v python3 &> /dev/null; then
    echo "❌ 錯誤: 未找到 Python 3"
    exit 1
fi

# 啟動儀表版
cd "$(dirname "$0")"/../..
python3 system/dashboard/interactive_dashboard.py
