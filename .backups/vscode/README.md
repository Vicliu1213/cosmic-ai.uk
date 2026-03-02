# VSCode 配置備份

## 備份內容
- ✅ settings.json - VSCode 主要設定
- ✅ extensions_backup.txt - 已安裝擴展列表

## 恢復方法

### 快速恢復
```bash
bash /workspaces/cosmic-ai.uk/.backups/vscode/restore.sh
```

### 手動恢復
1. 複製 `settings.json` 到 `/home/codespace/.vscode-remote/data/Machine/settings.json`
2. 重新啟動 VSCode

## 配置詳情
- **主題**: GitHub Dark
- **活動欄**: 可見（左側）
- **字體**: Monaco, 14pt
- **語言**: 繁體中文

## 已清理的擴展
已刪除 30+ 個不必要的 Claude 和開發工具擴展
