# ✅ Comic AI 持久化系統 - 完整設置

## 🎉 系統已就緒!

所有組件已成功配置並準備運行。以下是您需要了解的所有信息:

---

## 🚀 三步啟動

### 步驟 1: 打開終端

```bash
# 任何終端中執行
cd /root/comic_ai
```

### 步驟 2: 啟動系統

```bash
./start_persistent_system.sh
```

### 步驟 3: 享受!

系統會自動:
- ✅ 創建 tmux 會話
- ✅ 啟動所有 6 個窗口
- ✅ 保持應用一直運行

---

## 🪟 您將獲得什麼

### 持久運行的三個核心組件

1. **📌 任務面板** (Window 1)
   - 實時任務追蹤和管理
   - 標記任務完成
   - 自動更新模式

2. **🖼️ 圖像上傳處理** (Window 2)
   - 上傳和處理圖像文件
   - 支持多種格式
   - 批量處理選項

3. **💬 OpenCode 對話界面** (Window 3)
   - AI 驅動的代碼助手
   - 交互式開發環境
   - 多輪對話上下文

### 額外的幫助窗口

4. **🎛️ 控制中心** (Window 0) - 快速參考
5. **📊 日誌監視** (Window 4) - 實時日誌查看
6. **📈 儀表板** (Window 5) - Web 可視化
7. **⚙️ CLI 界面** (Window 6) - 命令行工具

---

## 🎮 快速導航

### 切換窗口

```
Ctrl+b 0  →  控制中心 (幫助和快速參考)
Ctrl+b 1  →  任務面板 (📌 任務追蹤)
Ctrl+b 2  →  圖像上傳 (🖼️ 文件處理)
Ctrl+b 3  →  OpenCode (💬 AI 對話)
Ctrl+b 4  →  日誌監視 (📊 日誌查看)
Ctrl+b 5  →  儀表板 (📈 Web 界面)
Ctrl+b 6  →  CLI (⚙️ 命令行)
```

### 基本操作

```
Ctrl+b n  →  下一個窗口
Ctrl+b p  →  上一個窗口
Ctrl+b d  →  分離 (後台運行)
Ctrl+b &  →  關閉窗口
```

---

## 📁 文件位置

```
啟動腳本:        /root/comic_ai/start_persistent_system.sh
完整指南:        /root/comic_ai/PERSISTENT_SYSTEM_GUIDE.md
快速參考:        /root/comic_ai/PERSISTENT_SYSTEM_QUICKREF.md
上傳文件夾:      /root/comic_ai/uploads/
日誌文件夾:      /root/comic_ai/logs/
任務文件:        /root/comic_ai/.session_todos.json
```

---

## 💡 使用示例

### 上傳圖像

```bash
# 方式 1: 復制文件
cp myimage.jpg /root/comic_ai/uploads/

# 方式 2: 在窗口 2 中上傳
Ctrl+b 2  →  按照提示上傳

# 方式 3: 批量上傳
cp *.jpg /root/comic_ai/uploads/
```

### 查詢 AI

```bash
# 在窗口 3 中:
Ctrl+b 3

# 然後輸入查詢:
describe the project structure
analyze src/core/multi_agent_trading.py
create a function for image processing
```

### 管理任務

```bash
# 在窗口 1 中:
Ctrl+b 1

# 操作:
1 - 刷新面板
2 - 查看任務詳情
3 - 標記任務完成
4 - 自動更新模式
5 - 退出
```

### 監視進度

```bash
# 查看日誌
Ctrl+b 4

# 打開儀表板 (在瀏覽器中)
Ctrl+b 5
# → http://localhost:5000
```

---

## 🔄 常用命令

### 會話管理

```bash
# 查看所有會話
tmux list-sessions

# 附加已運行的會話
tmux attach -t comic_ai_persistent

# 分離會話
Ctrl+b d

# 重新啟動系統
cd /root/comic_ai && ./start_persistent_system.sh

# 停止系統
tmux kill-session -t comic_ai_persistent
```

### 窗口控制

```bash
# 發送命令到窗口
tmux send-keys -t comic_ai_persistent:task-panel 'command' Enter

# 在特定窗口執行
tmux send-keys -t comic_ai_persistent:opencode-chat 'help' Enter

# 列出所有窗口
tmux list-windows -t comic_ai_persistent
```

---

## 🛠️ 故障排除

### 問題: 系統不啟動

```bash
# 解決方案
chmod +x /root/comic_ai/start_persistent_system.sh
./start_persistent_system.sh
```

### 問題: 窗口不響應

```bash
# 解決方案
Ctrl+c  # 停止當前進程
# 然後重新啟動系統
```

### 問題: 無法上傳文件

```bash
# 解決方案
mkdir -p /root/comic_ai/uploads/
chmod 755 /root/comic_ai/uploads/
```

### 問題: 日誌文件夾不存在

```bash
# 解決方案
mkdir -p /root/comic_ai/logs/
```

---

## 📚 相關文檔

| 文檔 | 說明 |
|------|------|
| `PERSISTENT_SYSTEM_GUIDE.md` | 📖 完整詳細指南 |
| `PERSISTENT_SYSTEM_QUICKREF.md` | 📋 快速參考卡 |
| `OPENCODE_CLI_GUIDE.md` | 🧠 OpenCode 使用指南 |
| `MULTI_AGENT_TRADING_LOGGING_README.md` | 📊 交易系統日誌 |
| `TMUX_USAGE_GUIDE.md` | 🎮 Tmux 使用指南 |

---

## 🎯 工作流示例

### 開發新功能

```
1. 啟動系統
   cd /root/comic_ai && ./start_persistent_system.sh

2. 在 OpenCode 中描述需求
   Ctrl+b 3 → "create function for..."

3. 上傳測試文件
   Ctrl+b 2 → 上傳測試圖像

4. 追蹤進度
   Ctrl+b 1 → 查看和更新任務

5. 監視日誌
   Ctrl+b 4 → 查看實時日誌

6. 查看儀表板
   Ctrl+b 5 → 訪問 http://localhost:5000
```

### 批量處理

```
1. 準備文件
   cp *.jpg /root/comic_ai/uploads/

2. 啟動處理
   Ctrl+b 2 → 選擇批量模式

3. 監視進度
   Ctrl+b 5 → 查看實時統計

4. 檢查結果
   Ctrl+b 1 → 查看已完成任務
```

---

## ✨ 關鍵特性

✅ **持久運行** - 一旦啟動,應用保持在後台運行  
✅ **多窗口** - 同時運行多個工具  
✅ **易於切換** - 使用快捷鍵快速導航  
✅ **後台操作** - 可以分離會話並在後台工作  
✅ **日誌記錄** - 完整的日誌追蹤和監視  
✅ **Web 儀表板** - 可視化實時數據  
✅ **文件上傳** - 輕鬆處理和分析文件  
✅ **AI 對話** - 強大的代碼助手  

---

## 🎪 首次使用清單

- [ ] 閱讀本指南
- [ ] 運行 `./start_persistent_system.sh`
- [ ] 測試切換窗口 (Ctrl+b 0-6)
- [ ] 上傳一個測試圖像
- [ ] 在 OpenCode 中詢問一個問題
- [ ] 在任務面板中創建任務
- [ ] 查看日誌
- [ ] 訪問儀表板 (http://localhost:5000)

---

## 🚀 立即開始

### 最快的方式

```bash
cd /root/comic_ai
./start_persistent_system.sh
```

### 已在後台運行?

```bash
# 附加到已運行的會話
tmux attach -t comic_ai_persistent
```

### 需要停止?

```bash
# 優雅停止
Ctrl+b d  # 在會話中按此組合鍵

# 或者完全停止
tmux kill-session -t comic_ai_persistent
```

---

## 📞 需要幫助?

### 在 OpenCode 中獲取幫助

```bash
Ctrl+b 3  # 進入 OpenCode 窗口
help      # 查看可用命令
```

### 查看快速參考

```bash
Ctrl+b 0  # 控制中心窗口會顯示所有快捷鍵
```

### 查看完整文檔

```bash
less PERSISTENT_SYSTEM_GUIDE.md
```

---

## 🎊 完成!

您現在已準備好使用 Comic AI 持久化系統。

**三個核心組件**已配置:
1. ✅ 任務面板 - 一直開著
2. ✅ 圖像上傳 - 一直開著
3. ✅ 對話界面 - 一直開著

**加上額外幫助窗口**:
- 控制中心、日誌監視、儀表板、CLI

所有內容都將保持運行,您可以隨時切換和交互!

### 現在就開始:

```bash
cd /root/comic_ai
./start_persistent_system.sh
```

祝您使用愉快! 🎉

---

**版本**: 1.0  
**更新時間**: 2026-02-19  
**狀態**: ✅ 生產就緒
