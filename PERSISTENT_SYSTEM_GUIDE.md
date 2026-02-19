# 🚀 Comic AI 持久化系統指南
# Comic AI Persistent System Guide

## 📋 概述 (Overview)

一個完整的持久化系統，將以下三個核心組件保持在後台一直運行:

- **📌 任務面板** - 實時任務追蹤和管理
- **🖼️ 圖像上傳處理** - 圖像文件處理和分析  
- **💬 OpenCode 對話界面** - AI 對話和代碼生成

所有組件通過 **tmux** 運行在獨立窗口中，可隨時切換和控制。

---

## 🎯 快速開始 (Quick Start)

### 步驟 1: 啟動系統

```bash
cd /root/comic_ai
./start_persistent_system.sh
```

這個命令會:
1. ✅ 自動檢測並安裝 tmux
2. ✅ 創建新的 tmux 會話
3. ✅ 啟動所有 6 個窗口
4. ✅ 附加到會話

### 步驟 2: 導航窗口

**使用快捷鍵:**
- `Ctrl+b` 然後 `n` - 下一個窗口
- `Ctrl+b` 然後 `p` - 上一個窗口
- `Ctrl+b` 然後 `0-6` - 跳到指定窗口

**或使用命令:**
```bash
# 切換到任務面板
tmux select-window -t comic_ai_persistent:1

# 切換到圖像上傳
tmux select-window -t comic_ai_persistent:2

# 切換到 OpenCode
tmux select-window -t comic_ai_persistent:3
```

### 步驟 3: 分離會話 (後台運行)

```bash
# 按 Ctrl+b 然後 d
# 或使用命令:
tmux detach-client -t comic_ai_persistent
```

---

## 🪟 窗口說明 (Window Details)

### 窗口 0: 控制中心 (Control Center)
- **作用**: 顯示快速參考和幫助信息
- **快捷命令**: 所有可用操作一覽表
- **建議**: 保持此窗口打開以查看幫助

### 窗口 1: 任務面板 (Task Panel)
- **文件**: `task_panel_optimized.py`
- **功能**:
  - 📌 實時任務追蹤
  - 🎨 交互式任務管理
  - 🔄 自動更新模式
  - 📊 任務統計

**操作**:
```
1 - 刷新面板
2 - 查看任務詳情
3 - 標記任務完成
4 - 自動更新模式
5 - 退出
```

### 窗口 2: 圖像上傳處理 (Image Upload Handler)
- **文件**: `intelligent_file_processor_cli.py`
- **功能**:
  - 🖼️ 圖像上傳和預處理
  - 🎨 圖像分析和轉換
  - 📦 批量文件處理
  - 🔍 文件內容識別

**支持格式**:
- 圖像: `jpg`, `png`, `gif`, `bmp`, `webp`
- 文檔: `pdf`, `docx`, `txt`
- 數據: `csv`, `json`, `yaml`

**上傳文件夾**: `/root/comic_ai/uploads/`

### 窗口 3: OpenCode 對話界面 (Chat Interface)
- **文件**: OpenCode CLI
- **功能**:
  - 💬 AI 對話和代碼生成
  - 🧠 跨多輪對話的上下文
  - 📝 代碼編輯和審查
  - 🚀 直接執行命令

**命令示例**:
```bash
# 列出可用操作
help

# 生成代碼
generate function to validate email addresses

# 分析文件
analyze src/core/logging_integration.py

# 執行命令
run pytest tests/

# 查看技能
skills list
```

### 窗口 4: 日誌監視器 (Log Monitor)
- **作用**: 實時查看應用日誌
- **日誌位置**: `/root/comic_ai/logs/`
- **主要日誌**:
  - `trading_agents.log` - 代理活動
  - `trading_decisions.log` - 決策記錄
  - `app.log` - 應用日誌

### 窗口 5: 儀表板 (Dashboard)
- **文件**: `logging_dashboard.py`
- **功能**:
  - 📊 Web 儀表板 (通常在 http://localhost:5000)
  - 📈 實時性能指標
  - 📉 歷史數據可視化
  - 🔔 警告和事件通知

### 窗口 6: 命令行界面 (CLI Interface)
- **文件**: `src/cli/cli.py`
- **功能**:
  - ⚙️ Comic AI 主命令行
  - 🎮 交互式菜單
  - 📝 配置管理
  - 🔧 系統工具

---

## 🎮 常用操作 (Common Operations)

### 發送命令到特定窗口

```bash
# 在任務面板發送命令
tmux send-keys -t comic_ai_persistent:task-panel 'python task.py' Enter

# 在圖像上傳窗口上傳文件
tmux send-keys -t comic_ai_persistent:image-upload 'upload myimage.jpg' Enter

# 在 OpenCode 發送查詢
tmux send-keys -t comic_ai_persistent:opencode-chat 'describe the project' Enter
```

### 查看窗口列表

```bash
# 列出所有窗口
tmux list-windows -t comic_ai_persistent

# 列出所有窗格
tmux list-panes -t comic_ai_persistent
```

### 會話管理

```bash
# 列出所有會話
tmux list-sessions

# 附加已分離的會話
tmux attach -t comic_ai_persistent

# 在會話中執行命令
tmux send-keys -t comic_ai_persistent 'command' Enter

# 終止會話
tmux kill-session -t comic_ai_persistent

# 終止特定窗口
tmux kill-window -t comic_ai_persistent:window_number
```

---

## 🖼️ 上傳圖像工作流 (Image Upload Workflow)

### 方法 1: 通過窗口上傳
```bash
# 1. 切換到圖像上傳窗口
tmux select-window -t comic_ai_persistent:image-upload

# 2. 按照提示上傳文件
# 選擇文件 → 上傳 → 處理 → 查看結果
```

### 方法 2: 直接復制到上傳文件夾
```bash
cp /path/to/image.jpg /root/comic_ai/uploads/
```

### 方法 3: 命令行上傳
```bash
tmux send-keys -t comic_ai_persistent:image-upload 'upload /path/to/image.jpg' Enter
```

### 查看上傳的文件
```bash
ls -la /root/comic_ai/uploads/
```

---

## 💬 使用 OpenCode 對話 (Using OpenCode Chat)

### 基本查詢

```bash
# 查看項目結構
describe the project structure

# 分析特定文件
analyze src/core/multi_agent_trading.py

# 生成代碼
create a function that calculates trading metrics

# 解釋代碼
explain how the logging system works
```

### 代碼審查

```bash
# 審查代碼
review src/plugins/multi_agent_trading.py

# 尋找問題
find potential bugs in src/core/

# 建議改進
suggest improvements for performance
```

### 執行命令

```bash
# 運行測試
run pytest tests/

# 構建項目
run python setup.py build

# 檢查語法
run flake8 src/
```

### 多輪對話

```bash
# 第一次查詢
describe the trading system

# 後續查詢 (保持上下文)
what are the main components?

# 再往前深入
how does the logging work?
```

---

## 📌 任務面板操作 (Task Panel Operations)

### 創建新任務

```bash
# 在 OpenCode 中
create task: implement new feature for image processing
create task: fix bug in logging system
create task: write documentation
```

### 標記任務完成

```bash
# 方式 1: 通過任務面板窗口
# 選擇選項 3 → 輸入任務 ID

# 方式 2: 直接命令
tmux send-keys -t comic_ai_persistent:task-panel '3' Enter
tmux send-keys -t comic_ai_persistent:task-panel 'task-123' Enter
```

### 實時監視

```bash
# 自動更新模式 (每 3 秒刷新)
# 在任務面板中選擇選項 4
```

---

## 🔧 配置和自定義 (Configuration)

### 修改更新間隔

在 `task_panel_optimized.py` 中:
```python
# 修改這行改變刷新間隔
refresh_interval=2  # 改為你想要的秒數
```

### 修改日誌位置

在 `start_persistent_system.sh` 中:
```bash
# 修改日誌查看命令
tail -f /your/custom/log/path/*.log
```

### 添加新窗口

在 `start_persistent_system.sh` 中:
```bash
# 添加新窗口
tmux new-window -t "$SESSION_NAME" -n "new-window"
tmux send-keys -t "$SESSION_NAME:new-window" "cd $PROJECT_ROOT && your_command" Enter
```

---

## 🐛 故障排除 (Troubleshooting)

### 問題 1: tmux 未安裝
```bash
# 解決方案
apt-get update && apt-get install -y tmux
```

### 問題 2: 窗口不響應
```bash
# 解決方案: 殺死窗口並重啟
tmux kill-window -t comic_ai_persistent:window_number
./start_persistent_system.sh  # 重啟系統
```

### 問題 3: 圖像上傳失敗
```bash
# 檢查上傳文件夾是否存在
mkdir -p /root/comic_ai/uploads/

# 檢查權限
chmod 755 /root/comic_ai/uploads/
```

### 問題 4: OpenCode 無法連接
```bash
# 確認已安裝 OpenCode
which opencode

# 或重新安裝
curl https://opencode.ai/install | bash
```

### 問題 5: 日誌文件夾不存在
```bash
# 創建日誌文件夾
mkdir -p /root/comic_ai/logs/
```

---

## 📚 高級用法 (Advanced Usage)

### 分屏顯示

```bash
# 在同一窗口中分屏
tmux split-window -h -t comic_ai_persistent:1

# 垂直分屏
tmux split-window -v -t comic_ai_persistent:1
```

### 運行背景任務

```bash
# 在後台運行長時間任務
tmux send-keys -t comic_ai_persistent:task-panel 'nohup python long_task.py &' Enter
```

### 導出會話日誌

```bash
# 捕獲窗口輸出
tmux capture-pane -t comic_ai_persistent:1 -p > window1_output.txt

# 捕獲整個會話
tmux capture-pane -t comic_ai_persistent -p -S -100 > session_output.txt
```

### 創建快捷別名

```bash
# 在 .bashrc 或 .zshrc 中添加
alias comic_start='cd /root/comic_ai && ./start_persistent_system.sh'
alias comic_attach='tmux attach -t comic_ai_persistent'
alias comic_kill='tmux kill-session -t comic_ai_persistent'
alias comic_logs='tmux send-keys -t comic_ai_persistent:logs'
```

---

## 🎯 工作流示例 (Workflow Examples)

### 示例 1: 開發新功能

```bash
# 1. 啟動系統
./start_persistent_system.sh

# 2. 在 OpenCode 中描述需求
# 窗口 3: "create function for image validation"

# 3. 上傳測試圖像
# 窗口 2: 上傳 test_image.jpg

# 4. 查看任務進度
# 窗口 1: 查看和更新任務狀態

# 5. 監視日誌
# 窗口 4: 查看實時日誌輸出

# 6. 查看儀表板
# 窗口 5: 訪問 http://localhost:5000
```

### 示例 2: 調試問題

```bash
# 1. 查看錯誤日誌
# 窗口 4: 監視日誌中的錯誤

# 2. 查詢問題
# 窗口 3: "debug the image upload issue"

# 3. 執行修復
# 窗口 6: 運行診斷命令

# 4. 驗證修復
# 窗口 2: 重新上傳文件進行測試
```

### 示例 3: 批量處理

```bash
# 1. 準備文件
cp *.jpg /root/comic_ai/uploads/

# 2. 在圖像處理窗口啟動批量處理
# 窗口 2: 選擇批量處理選項

# 3. 在儀表板中監視進度
# 窗口 5: 查看實時統計

# 4. 任務完成時查看結果
# 窗口 1: 檢查已完成任務
```

---

## 📊 系統資源

### 默認端口
- 儀表板: `http://localhost:5000`
- API 服務器: `http://localhost:8000` (如果配置)
- OpenCode: 本地 CLI

### 存儲位置
- 上傳: `/root/comic_ai/uploads/`
- 日誌: `/root/comic_ai/logs/`
- 任務: `/root/comic_ai/.session_todos.json`
- 配置: `/root/comic_ai/config/`

### 性能建議
- 4GB+ RAM 用於平穩運行所有窗口
- 快速硬盤以加快文件處理
- 穩定互聯網用於 OpenCode 功能

---

## 💡 提示和技巧 (Tips & Tricks)

1. **快速切換**: 使用 `Ctrl+b l` 切換回之前的窗口
2. **粘貼模式**: `Ctrl+b ]` 粘貼到 tmux 緩衝區
3. **命令模式**: `Ctrl+b :` 進入 tmux 命令模式
4. **縮放窗口**: `Ctrl+b z` 縮放/取消縮放當前窗格
5. **時間戳**: 查看日誌時使用 `tail -f logs/*.log | sed 's/^/[date +%T] /'`

---

## 🔗 相關文檔 (Related Documentation)

- [OpenCode CLI 指南](OPENCODE_CLI_GUIDE.md)
- [任務面板指南](QUICKSTART_TASK_PANEL.md)
- [多代理交易日誌](MULTI_AGENT_TRADING_LOGGING_README.md)
- [Tmux 使用指南](TMUX_USAGE_GUIDE.md)

---

## 📞 支持和反饋 (Support)

如有問題或建議:
1. 查看 `logs/` 文件夾中的日誌
2. 在 OpenCode 中使用 `help` 命令
3. 檢查本指南的故障排除部分
4. 提交反饋到 https://github.com/anomalyco/opencode

---

**最後更新**: 2026-02-19  
**版本**: 1.0  
**狀態**: ✅ 生產就緒
