# OpenCode CLI 快速指南

## 🚀 啟動 OpenCode

### 1. **基本啟動 (TUI 終端模式)**

進入項目目錄，執行：

```bash
cd /root/comic_ai
opencode
```

這會啟動交互式終端界面 (TUI)，可以直接對話和編輯代碼。

### 2. **直接運行命令 (CLI 模式)**

不需要進入交互式界面，直接執行命令：

```bash
# 簡單提問
opencode run "解釋多智能體交易系統的架構"

# 指定模型
opencode run -m anthropic/claude-3-5-sonnet-20241022 "幫我檢查 src/plugins/multi_agent_trading.py 的代碼質量"

# 附加文件
opencode run -f src/plugins/multi_agent_trading.py "這個文件有什麼問題嗎？"

# 附加多個文件
opencode run -f src/core/logging_integration.py -f src/plugins/multi_agent_trading.py "比較這兩個文件的設計模式"
```

### 3. **繼續上次的對話**

```bash
# 繼續最後一次會話
opencode --continue

# 或指定會話 ID
opencode --session <SESSION_ID>

# fork 一個會話（保留原會話，創建新的分支）
opencode --continue --fork
```

### 4. **Web 界面**

```bash
# 啟動 Web 服務器並打開瀏覽器
opencode web

# 指定端口
opencode web --port 3000

# 允許遠程訪問
opencode web --hostname 0.0.0.0
```

---

## 📊 實用命令

### **查看可用模型**

```bash
# 列出所有可用模型
opencode models

# 只看特定提供商的模型
opencode models anthropic
opencode models openai

# 顯示詳細信息（包括價格）
opencode models --verbose

# 刷新模型列表
opencode models --refresh
```

### **管理會話**

```bash
# 列出所有會話
opencode session list

# 列出最近的 10 個會話
opencode session list -n 10

# JSON 格式輸出
opencode session list --format json

# 導出會話
opencode export <SESSION_ID>

# 導入會話
opencode import session.json
opencode import https://opncd.ai/s/abc123
```

### **查看使用統計**

```bash
# 顯示代幣使用和成本
opencode stats

# 最近 7 天
opencode stats --days 7

# 按模型分類
opencode stats --models 5

# 按工具分類
opencode stats --tools 10
```

### **管理認證**

```bash
# 添加或更新 API 密鑰
opencode auth login

# 列出已認證的提供商
opencode auth list

# 登出
opencode auth logout
```

---

## 🎯 Comic AI 項目實用示例

### **1. 檢查多智能體交易日誌集成**

```bash
opencode run -f src/plugins/multi_agent_trading.py -f src/core/logging_integration.py \
  "檢查多智能體交易系統和 LogManager 的集成是否完整，列出所有日誌事件類型"
```

### **2. 生成集成測試**

```bash
opencode run \
  "為 MULTI_AGENT_TRADING_INTEGRATION_EXAMPLES.py 中的每個例子生成單元測試"
```

### **3. 改進 README 文檔**

```bash
opencode run -f MULTI_AGENT_TRADING_LOGGING_README.md \
  "根據最佳實踐改進這個 README 文檔，特別是快速開始部分"
```

### **4. 代碼審查**

```bash
opencode run -f src/plugins/multi_agent_trading.py \
  "進行代碼審查。檢查：\
  1. 代碼風格是否符合 AGENTS.md 中的指南\
  2. 錯誤處理是否完整\
  3. 是否有性能問題\
  4. 類型提示是否完整"
```

### **5. 生成 API 文檔**

```bash
opencode run -f src/plugins/multi_agent_trading.py \
  "為 MultiAgentCoordinator 類生成完整的 API 文檔，包括所有方法、參數和返回值"
```

### **6. 創建使用示例**

```bash
opencode run \
  "創建一個完整的示例代碼，展示如何在實際項目中使用多智能體交易系統和 LogManager。\
  包括：初始化、創建代理、執行交易、查看日誌"
```

### **7. 性能分析**

```bash
opencode run -f src/plugins/multi_agent_trading.py \
  "分析這個模塊的時間複雜度和空間複雜度，提出優化建議"
```

### **8. 添加新功能**

```bash
opencode run \
  "我想在多智能體交易系統中添加一個性能指標跟蹤功能。\
  它應該記錄每個代理的決策準確度、執行時間等。\
  請提供實現方案"
```

---

## 🔧 高級用法

### **使用不同的代理**

```bash
# 列出可用代理
opencode agent list

# 使用特定代理
opencode run --agent plan "創建一個實現 feature X 的計劃"
opencode run --agent build "根據計劃實現代碼"

# 創建自定義代理
opencode agent create
```

### **連接到遠程服務器**

```bash
# 終端 1：啟動遠程服務器
opencode serve --hostname 0.0.0.0 --port 4096

# 終端 2：連接到遠程服務器
opencode attach http://remote-ip:4096
```

### **配置 API 密鑰**

```bash
# 通過環境變量
export ANTHROPIC_API_KEY="sk-..."
opencode run "解釋閉包"

# 通過 .env 文件
echo "ANTHROPIC_API_KEY=sk-..." > .env
opencode run "解釋閉包"
```

---

## 📱 Skills 系統集成

我已經為你創建了 skills 文件：

```bash
ls -la /root/comic_ai/.opencode/skills/
```

**可用的 Skills：**

1. **git-release** - 創建發佈和變更日誌
2. **multi-agent-trading** - 多智能體交易系統集成

**在 OpenCode 中使用 Skills：**

在 TUI 或 CLI 對話中，OpenCode 會自動顯示可用的 skills，你可以要求它加載：

```bash
opencode run "加載 multi-agent-trading skill 並告訴我如何集成"
```

---

## 🎨 配置文件

### **查看/編輯配置**

```bash
# OpenCode 配置文件位置
cat ~/.config/opencode/opencode.json

# 或指定自定義配置
export OPENCODE_CONFIG=/root/comic_ai/.opencode/config.json
opencode
```

### **創建項目特定配置**

在 `/root/comic_ai/.opencode/config.json` 中：

```json
{
  "permission": {
    "skill": {
      "*": "allow",
      "multi-agent-trading": "allow",
      "git-release": "allow"
    }
  },
  "models": {
    "default": "anthropic/claude-3-5-sonnet-20241022"
  }
}
```

---

## 💾 實用技巧

### **快速查詢幫助**

```bash
# 查看所有命令
opencode --help

# 查看特定命令幫助
opencode run --help
opencode session --help
opencode auth --help
```

### **導出會話進行分享**

```bash
# 導出當前會話
opencode export <SESSION_ID> > session.json

# 分享 (在 TUI 中按 Ctrl+S)
# 或使用：
opencode run --share "我的提問"
```

### **日誌輸出**

```bash
# 打印詳細日誌
opencode run --print-logs "命令" 2>&1

# 指定日誌級別
opencode run --log-level DEBUG "命令"
```

---

## 📋 完整工作流示例

### **場景：改進多智能體交易系統**

```bash
# Step 1: 進入項目目錄
cd /root/comic_ai

# Step 2: 啟動 CLI，進行代碼審查
opencode run -f src/plugins/multi_agent_trading.py \
  "進行代碼審查並提出改進建議"

# Step 3: 根據反饋改進代碼
# (手動編輯或讓 OpenCode 生成)

# Step 4: 生成文檔
opencode run -f src/plugins/multi_agent_trading.py \
  "為這個模塊生成 API 文檔"

# Step 5: 查看統計
opencode stats

# Step 6: 導出會話
opencode export <SESSION_ID> > improvements.json
```

---

## 🌐 Web 界面

```bash
# 啟動 Web 界面
opencode web --port 3000

# 打開瀏覽器訪問：
# http://localhost:3000
```

Web 界面的功能與 TUI 相同，但提供了更友好的圖形界面。

---

## 總結

**快速記住的命令：**

```bash
# 啟動 TUI
opencode

# 快速運行命令
opencode run "你的提問"

# 使用特定模型
opencode run -m provider/model "你的提問"

# 查看統計
opencode stats

# 列出會話
opencode session list

# Web 界面
opencode web
```

**現在你可以充分利用 OpenCode 的 CLI 功能來加速開發！** 🚀
