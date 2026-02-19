# 🎯 Comic AI 持久化系統 - 快速參考卡
# Comic AI Persistent System - Quick Reference Card

## 🚀 啟動系統

```bash
cd /root/comic_ai
./start_persistent_system.sh
```

---

## 🪟 窗口快速導航

| 窗口 | 名稱 | 快捷鍵 | 功能 |
|------|------|--------|------|
| 0 | 控制中心 | `Ctrl+b 0` | 幫助和快速參考 |
| 1 | 任務面板 | `Ctrl+b 1` | 📌 任務追蹤 |
| 2 | 圖像上傳 | `Ctrl+b 2` | 🖼️ 文件處理 |
| 3 | OpenCode | `Ctrl+b 3` | 💬 AI 對話 |
| 4 | 日誌監視 | `Ctrl+b 4` | 📊 日誌查看 |
| 5 | 儀表板 | `Ctrl+b 5` | 📈 Web 儀表板 |
| 6 | CLI | `Ctrl+b 6` | ⚙️ 命令行 |

---

## 🎮 Tmux 快捷鍵

### 窗口操作
```
Ctrl+b c          新建窗口
Ctrl+b n          下一個窗口
Ctrl+b p          上一個窗口
Ctrl+b &          殺死當前窗口
Ctrl+b [0-9]      跳到指定窗口
```

### 會話操作
```
Ctrl+b d          分離會話 (後台運行)
Ctrl+b s          列出所有會話
Ctrl+b $          重命名會話
Ctrl+b :          進入命令模式
```

### 窗格操作
```
Ctrl+b %          垂直分屏
Ctrl+b "          水平分屏
Ctrl+b o          切換窗格
Ctrl+b z          縮放/取消縮放窗格
```

---

## 💻 常用命令

### 會話管理
```bash
# 列出所有會話
tmux list-sessions

# 附加會話
tmux attach -t comic_ai_persistent

# 分離會話
tmux detach-client -t comic_ai_persistent

# 殺死會話
tmux kill-session -t comic_ai_persistent

# 重新啟動系統
./start_persistent_system.sh
```

### 窗口管理
```bash
# 列出窗口
tmux list-windows -t comic_ai_persistent

# 發送命令到窗口
tmux send-keys -t comic_ai_persistent:task-panel 'command' Enter

# 在窗口中執行命令
tmux send-keys -t comic_ai_persistent:opencode-chat 'help' Enter

# 清空窗口
tmux send-keys -t comic_ai_persistent:logs 'clear' Enter
```

### 日誌查看
```bash
# 查看所有日誌
tail -f /root/comic_ai/logs/*.log

# 查看特定日誌
tail -f /root/comic_ai/logs/trading_agents.log

# 搜索錯誤
grep ERROR /root/comic_ai/logs/*.log

# 查看最後 50 行
tail -n 50 /root/comic_ai/logs/trading_agents.log
```

---

## 📝 常見任務

### 上傳圖像
```bash
# 方式 1: 复制到上傳文件夾
cp image.jpg /root/comic_ai/uploads/

# 方式 2: 在圖像上傳窗口中上傳
# Ctrl+b 2  → 選擇上傳選項

# 方式 3: 命令行上傳
tmux send-keys -t comic_ai_persistent:image-upload 'upload myimage.jpg' Enter
```

### 查詢 AI (OpenCode)
```bash
# 基本查詢
describe the project

# 分析代碼
analyze src/core/multi_agent_trading.py

# 生成代碼
create a function for image validation

# 執行命令
run pytest tests/

# 多輪對話
# 第一個查詢 → Enter
# 後續查詢 (上下文保留) → Enter
```

### 管理任務
```bash
# 創建任務
# 在 OpenCode 中: create task: description

# 查看任務
# Ctrl+b 1 → 選擇選項 2

# 標記完成
# Ctrl+b 1 → 選擇選項 3 → 輸入任務 ID

# 自動更新
# Ctrl+b 1 → 選擇選項 4
```

### 監視系統
```bash
# 查看日誌
Ctrl+b 4

# 打開儀表板
Ctrl+b 5
# 瀏覽器: http://localhost:5000

# 查看系統資源
tmux send-keys -t comic_ai_persistent:cli 'top' Enter
```

---

## 🔗 重要位置

```
項目根目錄:        /root/comic_ai/
上傳文件夾:        /root/comic_ai/uploads/
日誌文件夾:        /root/comic_ai/logs/
任務文件:          /root/comic_ai/.session_todos.json
配置文件夾:        /root/comic_ai/config/
源代碼:            /root/comic_ai/src/
核心模塊:          /root/comic_ai/src/core/
插件:              /root/comic_ai/src/plugins/
```

---

## 🌐 訪問地址

```
儀表板:            http://localhost:5000
API 服務器:        http://localhost:8000
OpenCode:          本地 CLI (Ctrl+b 3)
文件上傳:          /root/comic_ai/uploads/
```

---

## 🆘 快速故障排除

| 問題 | 解決方案 |
|------|---------|
| 窗口不響應 | `Ctrl+c` 停止 → 重新啟動 |
| 找不到命令 | `cd /root/comic_ai` 確保在正確目錄 |
| 權限拒絕 | `chmod +x start_persistent_system.sh` |
| 端口被佔用 | `lsof -i :5000` 檢查 → 殺死進程 |
| Tmux 崩潰 | `tmux kill-session -t comic_ai_persistent` → 重啟 |
| 文件上傳失敗 | `mkdir -p /root/comic_ai/uploads` → 檢查權限 |

---

## 📱 移動操作

### 使用鼠標
```
右鍵單擊 + 拖動  選擇文本
Shift + 右鍵    粘貼
滾輪            上下滾動
```

### 複製和粘貼
```
# 進入複製模式
Ctrl+b [

# 選擇文本 (使用方向鍵或鼠標)
# 按 Enter 複製

# 粘貼
Ctrl+b ]
```

---

## 🎯 工作流速查表

### 開發新功能
```
1. ./start_persistent_system.sh
2. Ctrl+b 3 (OpenCode) → describe requirements
3. Ctrl+b 2 (Image) → upload test files
4. Ctrl+b 1 (Tasks) → create and track tasks
5. Ctrl+b 4 (Logs) → monitor progress
```

### 調試問題
```
1. Ctrl+b 4 (Logs) → view error messages
2. Ctrl+b 3 (OpenCode) → query about issue
3. Ctrl+b 6 (CLI) → run diagnostics
4. Ctrl+b 2 (Image) → test with sample files
```

### 批量處理
```
1. cp files /root/comic_ai/uploads/
2. Ctrl+b 2 (Image) → select batch mode
3. Ctrl+b 5 (Dashboard) → monitor progress
4. Ctrl+b 1 (Tasks) → track completion
```

---

## 📚 更詳細的說明

查看完整指南: [`PERSISTENT_SYSTEM_GUIDE.md`](PERSISTENT_SYSTEM_GUIDE.md)

---

**快速啟動**:
```bash
cd /root/comic_ai && ./start_persistent_system.sh
```

**立即附加**:
```bash
tmux attach -t comic_ai_persistent
```

**快速停止**:
```bash
tmux kill-session -t comic_ai_persistent
```

---

*最後更新: 2026-02-19 | 版本: 1.0*
