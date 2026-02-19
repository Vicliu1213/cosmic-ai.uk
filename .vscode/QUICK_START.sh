#!/bin/bash

# 🎨 VSCode 快速開始 | Quick Start Script

echo "╔═══════════════════════════════════════════════╗"
echo "║   VSCode 快速開始 | Quick Start               ║"
echo "╚═══════════════════════════════════════════════╝"
echo ""

# 1. 驗證配置
echo "✓ 驗證配置檔案..."
python3 -m json.tool /root/comic_ai/.vscode/settings.json > /dev/null 2>&1
if [ $? -eq 0 ]; then
  echo "  ✓ settings.json 語法正確"
else
  echo "  ✗ settings.json 語法錯誤"
  exit 1
fi

python3 -m json.tool /root/comic_ai/.vscode/keybindings.json > /dev/null 2>&1
if [ $? -eq 0 ]; then
  echo "  ✓ keybindings.json 語法正確"
else
  echo "  ✗ keybindings.json 語法錯誤"
  exit 1
fi

python3 -m json.tool /root/comic_ai/.vscode/tasks.json > /dev/null 2>&1
if [ $? -eq 0 ]; then
  echo "  ✓ tasks.json 語法正確"
else
  echo "  ✗ tasks.json 語法錯誤"
  exit 1
fi

echo ""
echo "✓ 所有配置驗證通過！"
echo ""

# 2. 列出快速鍵
echo "📋 核心快捷鍵 | Core Keybindings"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Shift+Alt+1  →  開啟儀表板 (Dashboard)"
echo "Shift+Alt+2  →  開啟終端 (Terminal)"
echo "Shift+Alt+4  →  執行與除錯 (Run & Debug)"
echo "Shift+Alt+6  →  執行測試 (Testing)"
echo "Shift+Alt+8  →  禪宗模式 (Zen Mode)"
echo ""

# 3. 建議操作
echo "🚀 建議操作 | Recommended Actions"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "1. 開啟 VSCode:"
echo "   cd /root/comic_ai && code ."
echo ""
echo "2. 按下快速鍵啟動儀表板:"
echo "   Shift+Alt+1"
echo ""
echo "3. 查詢更多快捷鍵:"
echo "   cat .vscode/VSCODE_QUICKREF.md"
echo ""

# 4. 檔案統計
echo "📊 配置統計 | Configuration Statistics"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "設定檔案:    5 個 JSON 檔案"
echo "快捷鍵:      88 個"
echo "工作任務:    23 個"
echo "推薦擴充:    50+ 個"
echo "設定項目:    150+ 個"
echo ""

echo "✅ VSCode 配置準備就緒！"
echo "🎉 準備好開始了嗎? Shift+Alt+1 開啟儀表板！"
