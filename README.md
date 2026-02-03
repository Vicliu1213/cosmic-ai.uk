# Opencode 插件自動化管理系統

## 支持的插件列表
- opencode
- oh-my-opencode  
- claude-vcode
- worktree
- pty
- supermemory
- type-inject
- morph-fast-apply
- browser
- arise
- notificator
- plantator
- dcp
- skillful
- mem0s
- code-snippet

## 快速開始

### 1. 自動下載和安裝所有插件
```bash
curl -sSL https://raw.githubusercontent.com/your-repo/opencode-plugins/main/install.sh | bash
```

### 2. 個別插件安裝
```bash
# 安裝特定插件
./scripts/install-plugin.sh <plugin-name>

# 例如：
./scripts/install-plugin.sh worktree
./scripts/install-plugin.sh supermemory
```

### 3. 創建獨立虛擬空間
```bash
# 為每個插件創建隔離環境
./scripts/create-env.sh <plugin-name>

# 例如：
./scripts/create-env.sh pty
./scripts/create-env.sh browser
```

## 快捷命令

| 命令 | 功能 |
|------|------|
| `op install-all` | 安裝所有插件 |
| `op install <plugin>` | 安裝特定插件 |
| `op env <plugin>` | 創建插件環境 |
| `op list` | 列出所有插件 |
| `op update` | 更新所有插件 |
| `op clean` | 清理所有環境 |

## 插件介紹

### 🛠️ 開發工具
- **opencode**: 核心開發環境
- **claude-vcode**: AI 輔助編碼
- **worktree**: Git 工作樹管理
- **code-snippet**: 代碼片段管理

### 💾 記憶管理
- **supermemory**: 智能記憶系統
- **mem0s**: 零記憶管理

### 🎨 用戶界面
- **browser**: 網頁瀏覽器
- **arise**: 界面增強
- **notificator**: 通知系統

### ⚡ 性能工具
- **morph-fast-apply**: 快速應用工具
- **type-inject**: 類型注入
- **pty**: 終端模擬器

### 🌱 自動化
- **plantator**: 自動化種植
- **dcp**: 數據處理管道
- **skillful**: 技能管理

## 環境隔離

每個插件都在獨立的虛擬空間中運行，避免互相影響：

```bash
# 查看所有環境
op env list

# 切換到特定環境
op env activate <plugin>

# 停用環境
op env deactivate
```

## 自動壓縮備份

```bash
# 自動壓縮所有插件環境
./scripts/backup.sh

# 恢復備份
./scripts/restore.sh <backup-file>
```

## 故障排除

如果遇到問題：
1. 檢查網絡連接
2. 確認 Python 版本 ≥ 3.8
3. 清理緩存：`op clean --cache`
4. 重新安裝：`op reinstall <plugin>`

## 貢獻

歡迎提交 Issue 和 Pull Request！

## 許可證

MIT License