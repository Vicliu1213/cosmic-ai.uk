#!/bin/bash
# 統一整合儀表版啟動腳本
# Unified Integrated Dashboard Launcher

echo "🚀 啟動 Cosmic AI 統一整合儀表版..."
echo ""

# 檢查 Python 3
if ! command -v python3 &> /dev/null; then
    echo "❌ 錯誤: 未找到 Python 3"
    exit 1
fi

# 切換到工作目錄
cd "$(dirname "$0")"/../.. || exit 1

# 啟動統一儀表版
python3 system/dashboard/unified_dashboard.py

exit 0
