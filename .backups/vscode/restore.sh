#!/bin/bash
echo "🔄 恢復 VSCode 配置..."

# 恢復 settings.json
cp /workspaces/cosmic-ai.uk/.backups/vscode/settings.json /home/codespace/.vscode-remote/data/Machine/settings.json
echo "✅ 已恢復 settings.json"

echo "🎉 恢復完成！"
echo "請重新啟動 VSCode 以應用更改"
