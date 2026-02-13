# 🎯 實時任務面板 - 使用指南

## 快速開始

### 方式 1️⃣：一鍵啟動（推薦）

```bash
python task_panel_launcher.py
```

然後選擇：
- **1** - 交互模式（帶菜單）✨ 推薦
- **2** - 自動更新模式
- **3** - 緊湊模式
- **4** - 自定義配置

### 方式 2️⃣：命令行啟動

```bash
# 交互模式
python src/cli/enhanced_cli.py

# 自動更新（右上角）
python src/cli/enhanced_cli.py --auto --position top-right

# 緊湊模式，2秒刷新
python src/cli/enhanced_cli.py --auto --compact --interval 2
```

### 方式 3️⃣：快速回顧

```bash
# 查看任務面板
python src/core/task_panel.py

# 查看完整回顧報告
python recap_cli.py --save-report

# 只看待辦事項
python recap_cli.py --todos
```

## 📊 面板功能概覽

### 🎨 完整模式

```
┌──────────────────────────────────────┐
│ 📋 任務追蹤面板                             │
├──────────────────────────────────────┤
│ 🕐 22:55:46 | 🌿 main                  │
├──────────────────────────────────────┤
│ 進度: 3/6 已完成 (50%)                    │
├──────────────────────────────────────┤
│ 🔵🟡 測試自動化回顧系統                         │
│ ⬜🟡 優化回顧輸出格式                          │
│ ⬜🟢 添加自動回顧到啟動流程                       │
└──────────────────────────────────────┘
```

### 🎯 緊湊模式

```
┌───────────────────────────────────────────┐
│ 📋 任務面板 22:54:36                           │
├───────────────────────────────────────────┤
│ ✅ 3 │ 🔵 1 │ ⬜ 2                           │
├───────────────────────────────────────────┤
│ 🔵🟡 測試自動化回顧系統                          │
└───────────────────────────────────────────┘
```

## 📝 任務狀態說明

| 符號 | 狀態 | 含義 |
|------|------|------|
| 🔵 | in_progress | 正在進行 |
| ⬜ | pending | 待辦中 |
| ✅ | completed | 已完成 |
| ❌ | cancelled | 已取消 |

## ⭐ 優先級說明

| 符號 | 優先級 | 含義 |
|------|--------|------|
| 🔴 | high | 高優先 |
| 🟡 | medium | 中優先 |
| 🟢 | low | 低優先 |

## 🎮 交互模式菜單

當選擇交互模式時，你可以：

```
1. 刷新任務面板    - 實時更新顯示
2. 查看完整列表    - 按狀態分組顯示所有任務
3. 更新任務狀態    - 手動修改任務狀態（開發中）
4. 查看會話摘要    - 顯示 Git 提交和建議
5. 退出           - 退出程序
```

## 🔧 配置選項

### 面板位置

- `top-left` - 左上角（默認）
- `top-right` - 右上角 ⭐ 推薦
- `bottom-left` - 左下角
- `bottom-right` - 右下角

### 刷新間隔

- 默認: 3 秒
- 最小: 1 秒
- 最大: 30 秒

### 面板寬度

- 默認: 40 字符
- 最小: 30 字符
- 最大: 80 字符

## 📋 常用命令

### 查看任務

```bash
# 完整面板
python src/core/task_panel.py

# 緊湊面板
python src/cli/enhanced_cli.py --compact

# 只看待辦
python recap_cli.py --todos
```

### 監控任務（自動更新）

```bash
# 右上角，2秒刷新
python src/cli/enhanced_cli.py --auto --position top-right --interval 2

# 後台運行
python src/cli/enhanced_cli.py --auto --compact &
```

### 生成報告

```bash
# 保存完整回顧報告
python recap_cli.py --full

# 生成到指定文件
python recap_cli.py --save-report
```

## 🚀 高級用法

### 在 Python 代碼中使用

```python
from src.core.task_panel import RealTimeTaskPanel, TaskPanelConfig

# 創建配置
config = TaskPanelConfig(
    position="top-right",
    width=45,
    refresh_interval=2,
    compact_mode=False
)

# 創建面板
panel = RealTimeTaskPanel(config)

# 生成面板文本
panel_text = panel.update()
print(panel_text)

# 自動更新（需要線程）
panel.start_auto_refresh(callback=lambda text: print(text))

# 停止更新
panel.stop_auto_refresh()
```

### 集成到現有 CLI

```python
from src.cli.enhanced_cli import EnhancedCliWithPanel

cli = EnhancedCliWithPanel(panel_position="top-left")
cli.run_interactive()
```

## 💡 最佳實踐

1. **開發時**：使用交互模式，方便查看詳細信息
2. **監控時**：使用自動更新模式，實時跟踪進度
3. **關鍵時刻**：使用右上角位置，不遮擋主要工作區
4. **長時運行**：使用緊湊模式，節省空間
5. **複雜任務**：定期查看完整列表，了解全局

## ❓ 常見問題

### Q: 面板顯示不更新？
**A:** 檢查 `.session_todos.json` 文件是否存在且格式正確

### Q: 如何修改任務？
**A:** 直接編輯 `.session_todos.json`，面板會自動刷新

### Q: 可以同時運行多個面板嗎？
**A:** 可以，但建議使用不同的位置和模式

### Q: 如何快速進入自動更新？
**A:** 使用命令：`python src/cli/enhanced_cli.py --auto`

### Q: 支持遠程同步嗎？
**A:** 目前不支持，可編輯任務文件手動同步

## 📚 相關文件

| 文件 | 用途 |
|------|------|
| `task_panel_launcher.py` | 快速啟動器 ⭐ |
| `src/cli/enhanced_cli.py` | 增強 CLI |
| `src/core/task_panel.py` | 面板核心 |
| `.session_todos.json` | 任務存儲 |
| `TASK_PANEL_GUIDE.md` | 詳細指南 |

## 🎉 開始使用吧！

```bash
# 最簡單的方式
python task_panel_launcher.py

# 或直接自動更新
python src/cli/enhanced_cli.py --auto --position top-right
```

祝你工作順利！ 🚀
