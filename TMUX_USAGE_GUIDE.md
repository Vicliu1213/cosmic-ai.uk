# 🚀 Comic AI Tmux 多會話管理系統

## 概述

Comic AI 現已升級為 **完整的 Tmux 多會話管理系統**。你可以同時運行多個服務，每個服務在獨立的視窗中，輕鬆管理和監控。

### 什麼是 Tmux？

**Tmux** (Terminal Multiplexer) 是一個終端複用器，允許你：
- 在一個終端中運行多個視窗（像瀏覽器的標籤頁）
- 在視窗之間快速切換
- 保持後台進程運行（即使斷開連接）
- 輕鬆分割和組織工作區

## 📋 系統架構

Comic AI Tmux 系統包含 **6 個獨立視窗**：

| 編號 | 視窗名稱 | 功能 | 狀態 |
|------|---------|------|------|
| 0️⃣ | `https-server` | HTTPS 加密伺服器 | 背景執行 + 日誌 |
| 1️⃣ | `dashboard` | Web 儀表板界面 | 前台執行 + 日誌 |
| 2️⃣ | `task-panel` | AI 任務面板 | 前台執行 + 日誌 |
| 3️⃣ | `main-cli` | 主命令行介面 | 前台執行 |
| 4️⃣ | `monitor` | 即時監控和日誌 | 實時更新 |
| 5️⃣ | `shell` | 控制台 Shell | 待命 |

## 🎯 快速開始

### 方法 1️⃣：自動啟動（推薦）

最簡單的方式 - 執行設置腳本：

```bash
# 從項目根目錄運行
./setup_tmux_sessions.sh
```

這會自動：
- 建立新的 Tmux 會話 `comic-ai`
- 啟動所有 6 個服務視窗
- 自動附加到會話（你會看到視窗 0）

### 方法 2️⃣：交互式管理

使用管理腳本進行完整控制：

```bash
./manage_tmux_sessions.sh
```

這提供一個友好的菜單來：- 附加/分離會話
- 查看會話狀態
- 切換視窗
- 查看日誌
- 管理進程

### 方法 3️⃣：手動 Tmux 命令

如果你熟悉 Tmux，使用原生命令：

```bash
# 附加到會話
tmux attach-session -t comic-ai

# 切換視窗 (前綴: Ctrl+B)
Ctrl+B 0  # 切換到視窗 0
Ctrl+B 1  # 切換到視窗 1
# ... 以此類推

# 新建視窗
Ctrl+B c

# 列出視窗
Ctrl+B w

# 分割窗格
Ctrl+B %  # 水平分割
Ctrl+B "  # 垂直分割

# 分離會話
Ctrl+B d
```

## 📂 日誌和輸出

所有服務日誌存儲在 `/root/comic_ai/logs/tmux/`：

```
logs/tmux/
├── https_server.log    # HTTPS 伺服器日誌
├── dashboard.log       # Dashboard 日誌
├── task_panel.log      # 任務面板日誌
└── [其他日誌]
```

查看特定服務的日誌：

```bash
# 查看 HTTPS 伺服器日誌（實時跟蹤）
tail -f logs/tmux/https_server.log

# 查看 Dashboard 日誌
tail -f logs/tmux/dashboard.log

# 查看所有日誌
tail -f logs/tmux/*.log
```

## 🎮 常見操作

### 1️⃣ 查看所有運行的服務

在 `monitor` 視窗（編號 4）中，自動實時顯示：
- 所有視窗狀態
- 運行中的 Python 進程數量
- 最新的服務日誌片段

或手動：

```bash
# 列出會話的所有視窗
tmux list-windows -t comic-ai

# 查看進程
ps aux | grep python | grep -v grep
```

### 2️⃣ 切換視窗

**快速切換**（使用 Tmux 快捷鍵）：

進入會話後按 `Ctrl+B` 然後：
- `0` - 切換到 HTTPS 伺服器視窗
- `1` - 切換到 Dashboard
- `2` - 切換到任務面板
- `3` - 切換到主 CLI
- `4` - 切換到監控
- `5` - 切換到 Shell

**使用管理腳本**：

```bash
./manage_tmux_sessions.sh
# 選擇 "3) 切換視窗"
```

### 3️⃣ 監控服務狀態

```bash
# 在 Shell 視窗 (5) 中執行
./check_deployment_status.sh

# 或查看特定服務
curl -k https://localhost:8443/health
```

### 4️⃣ 重啟特定服務

**重啟 HTTPS 伺服器**：

```bash
# 進入管理菜單
./manage_tmux_sessions.sh

# 選擇 "6) 殺死進程/重啟服務"
# 選擇 "2) 殺死特定進程"
# 殺死 HTTPS 進程
pkill -f "app_ssl.py"

# 在視窗 0 中手動重新啟動
./start_https_server_bg.sh
```

**重啟整個會話**：

```bash
./manage_tmux_sessions.sh

# 選擇 "6) 殺死進程/重啟服務"
# 選擇 "3) 重啟會話"
```

### 5️⃣ 查看實時日誌

在 `monitor` 視窗中（編號 4）自動顯示。

或者手動：

```bash
# 在管理菜單中
./manage_tmux_sessions.sh

# 選擇 "5) 查看服務日誌"
# 選擇日誌文件並 tail -f
```

## 🔧 背後發生什麼

當你運行 `setup_tmux_sessions.sh` 時：

1. **檢查會話** - 查看 `comic-ai` 會話是否已存在
2. **建立會話** - 創建新的 Tmux 會話（如需要）
3. **創建視窗** - 按順序創建 6 個視窗
4. **啟動服務** - 在各視窗中啟動相應的 Python/Bash 程序
5. **日誌記錄** - 所有輸出重定向到 `logs/tmux/` 目錄
6. **附加會話** - 自動連接到會話（你會看到活動界面）

### 各個視窗的啟動命令

| 視窗 | 命令 |
|------|------|
| 0️⃣ https-server | `bash start_https_server_bg.sh` |
| 1️⃣ dashboard | `python dashboard/app_ssl.py` |
| 2️⃣ task-panel | `python task_panel_optimized.py` |
| 3️⃣ main-cli | `python src/cli/cli.py` |
| 4️⃣ monitor | 實時監控腳本（watch 命令） |
| 5️⃣ shell | 標準 Bash shell |

## 🛑 停止會話

### 方法 1：使用管理腳本

```bash
./manage_tmux_sessions.sh

# 選擇 "7) 停止會話"
# 確認刪除
```

### 方法 2：使用 Tmux 命令

```bash
# 停止整個會話
tmux kill-session -t comic-ai

# 停止特定視窗
tmux kill-window -t comic-ai:0
```

### 方法 3：按下 Ctrl+C

在任何視窗中按 `Ctrl+C` 可以停止該視窗的進程。

## 📊 分離和重新附加

Tmux 的一個強大功能是你可以 **分離會話並稍後重新附加**：

```bash
# 分離會話（保留所有進程運行）
# 在會話中按 Ctrl+B 然後按 d

# 列出所有會話
tmux list-sessions

# 重新附加
tmux attach-session -t comic-ai

# 或從管理菜單
./manage_tmux_sessions.sh
# 選擇 "1) 附加到會話"
```

這對於 SSH 連接特別有用 - 即使斷開連接，所有服務也會繼續運行！

## 🔐 安全注意事項

- **日誌文件** - 包含敏感信息，確保權限正確
- **SSL 憑證** - 私鑰權限設置為 `600`（僅所有者可讀）
- **進程隔離** - 各個視窗運行各自的進程，互不影響

## 🐛 故障排除

### 問題：會話已存在

```bash
# 選項 1：重新啟動會話
tmux kill-session -t comic-ai
./setup_tmux_sessions.sh

# 選項 2：附加到現有會話
tmux attach-session -t comic-ai
```

### 問題：找不到命令

確保你在項目根目錄 `/root/comic_ai/`：

```bash
cd /root/comic_ai
./setup_tmux_sessions.sh
```

### 問題：某個視窗無法啟動

檢查相應的日誌文件：

```bash
tail -f logs/tmux/[service_name].log
```

### 問題：進程佔用端口

```bash
# 查找佔用 8443 端口的進程
lsof -i :8443

# 殺死該進程
kill -9 [PID]
```

## 📚 更多 Tmux 資源

- [Tmux 官方文檔](https://github.com/tmux/tmux)
- [Tmux 快速參考](https://tmuxcheatsheet.com/)
- [Tmux 中文教程](https://zhuanlan.zhihu.com/p/98384704)

## ✅ 檢查清單

啟動前確認：

- ✅ Tmux 已安裝 (`which tmux`)
- ✅ SSL 憑證存在 (`ls ssl_certs/`)
- ✅ Python 依賴已安裝 (`pip install -r requirements.txt`)
- ✅ 在項目根目錄 (`pwd` 顯示 `/root/comic_ai`)
- ✅ 腳本有執行權限 (`ls -l setup_tmux_sessions.sh`)

## 🎉 就這樣！

現在你有一個完整的多服務管理系統，所有服務在獨立的視窗中運行，輕鬆管理和監控。

```bash
./setup_tmux_sessions.sh
```

祝你使用愉快！🚀
