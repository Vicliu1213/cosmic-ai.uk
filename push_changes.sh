#!/bin/bash
# 推送 Import 修正到 GitHub
# 執行此指令稿將自動推送所有 import 修正

cd /workspaces/cosmic-ai.uk

# 檢查 git 狀態
git status

# 添加修正的檔案
git add \
  src/main.py \
  src/engine/quantum_engine.py \
  src/config_manager.py \
  src/schema_validator.py \
  src/core/engine.py \
  src/utils/logger.py \
  src/api/binance_client.py

# 確認已暫存的變更
git diff --cached --stat

# 創建提交
git commit -m "refactor: 清理和標準化 Python imports

- 移除所有未使用的 imports
- 修正相對導入為更規範的形式
- 檢查並驗證所有 7 個關鍵模組的 import 語句

修正的檔案:
- src/main.py: 移除 logging
- src/engine/quantum_engine.py: 修正相對導入
- src/config_manager.py: 移除 sys, re, datetime, json
- src/schema_validator.py: 移除 sys, dataclasses
- src/core/engine.py: 移除 time
- src/utils/logger.py: 移除 json
- src/api/binance_client.py: 移除 asyncio"

# 推送到 GitHub
git push origin $(git rev-parse --abbrev-ref HEAD)

echo "✨ 完成！所有修正已推送到 GitHub"
