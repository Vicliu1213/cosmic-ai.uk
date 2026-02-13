# 🎯 實時任務面板集成指南

## 概述

實時任務面板是一個動態的、可自定義的任務追蹤組件，支持以下功能：

- ✅ **實時更新** - 自動刷新任務狀態
- 📍 **位置選擇** - 支持左上、右上、左下、右下四個位置
- 🎨 **多種模式** - 完整模式和緊湊模式
- 🔄 **自動和交互模式** - 根據需要切換
- 📊 **任務統計** - 顯示進度和優先級信息

## 快速開始

### 1. 啟動實時面板（推薦方式）

```bash
python task_panel_launcher.py
```

選擇啟動模式：
- **1. 交互模式** - 帶有菜單的實時面板
- **2. 自動更新模式** - 自動刷新面板
- **3. 緊湊模式** - 簡潔顯示
- **4. 自定義配置** - 設置位置和間隔

### 2. 直接使用增強 CLI

```bash
# 交互模式（默認）
python src/cli/enhanced_cli.py

# 自動更新模式
python src/cli/enhanced_cli.py --auto

# 指定位置
python src/cli/enhanced_cli.py --position top-right

# 緊湊模式
python src/cli/enhanced_cli.py --compact

# 自定義刷新間隔（秒）
python src/cli/enhanced_cli.py --interval 2
```

### 3. 在代碼中使用

```python
from src.core.task_panel import RealTimeTaskPanel, TaskPanelConfig

# 創建配置
config = TaskPanelConfig(
    position="top-left",
    width=40,
    refresh_interval=3,
    compact_mode=False
)

# 創建面板
panel = RealTimeTaskPanel(config)

# 生成面板內容
panel_text = panel.update()
print(panel_text)

# 自動更新
panel.start_auto_refresh(callback=lambda text: print(text))
```

## 面板組件

### TaskPanelConfig

配置類，包含以下選項：

```python
@dataclass
class TaskPanelConfig:
    position: str = "top-left"        # 面板位置
    width: int = 40                   # 面板寬度
    refresh_interval: int = 5         # 刷新間隔（秒）
    max_tasks_display: int = 8        # 最多顯示任務數
    enable_auto_refresh: bool = True  # 是否自動刷新
    compact_mode: bool = False        # 是否緊湊模式
```

### RealTimeTaskPanel

主要的面板類，提供以下方法：

- `update()` - 更新面板並返回內容
- `build_panel()` - 構建面板內容
- `start_auto_refresh(callback)` - 開始自動刷新
- `stop_auto_refresh()` - 停止自動刷新

## 面板顯示

### 完整模式

```
┌──────────────────────────────────────┐
│ 📋 任務追蹤面板                             │
├──────────────────────────────────────┤
│ 🕐 22:54:36 | 🌿 main                  │
├──────────────────────────────────────┤
│ 進度: 3/6 已完成 (50%)                    │
├──────────────────────────────────────┤
│ 🔵🟡 測試自動化回顧系統                         │
│ ⬜🟡 優化回顧輸出格式                          │
│ ⬜🟢 添加自動回顧到啟動流程                       │
│ ✅🔴 創建自動化回顧配置文件 (YAML)                │
│ ✅🔴 創建自動化回顧核心模塊                       │
│ ✅🔴 集成回顧功能到 CLI                       │
└──────────────────────────────────────┘
```

### 緊湊模式

```
┌───────────────────────────────────────────┐
│ 📋 任務面板 22:54:36                           │
├───────────────────────────────────────────┤
│ ✅ 3 │ 🔵 1 │ ⬜ 2                           │
├───────────────────────────────────────────┤
│ 🔵🟡 測試自動化回顧系統                          │
│ ⬜🟡 優化回顧輸出格式                           │
│ ⬜🟢 添加自動回顧到啟動流程                       │
└───────────────────────────────────────────┘
```

## 符號說明

### 狀態符號
- 🔵 進行中
- ⬜ 待辦
- ✅ 已完成
- ❌ 已取消

### 優先級符號
- 🔴 高優先級
- 🟡 中優先級
- 🟢 低優先級
- ⚪ 未定義

## 文件結構

```
/root/comic_ai/
├── src/
│   ├── core/
│   │   ├── session_recap.py      # 會話回顧核心
│   │   └── task_panel.py         # 實時面板組件
│   ├── cli/
│   │   ├── enhanced_cli.py       # 增強 CLI
│   │   └── recap_command.py      # 回顧命令
│   └── ...
├── recap_cli.py                   # 快速回顧命令
├── task_panel_launcher.py         # 面板啟動器
├── config/
│   └── session_recap_config.yaml # 回顧配置
└── ...
```

## 主要特性

### 1. 實時更新
面板會自動檢測任務文件變更，按設定的間隔刷新顯示

### 2. 智能任務排序
- 優先顯示進行中的任務
- 然後顯示待辦任務
- 最後顯示已完成的任務

### 3. 進度跟踪
實時顯示：
- 已完成 / 總數
- 完成百分比
- 各狀態任務計數

### 4. 靈活配置
支持自定義：
- 面板位置
- 面板寬度
- 刷新間隔
- 顯示模式

## 使用場景

1. **開發過程中監控任務進度**
   ```bash
   python task_panel_launcher.py  # 選擇 1. 交互模式
   ```

2. **後台自動監控任務**
   ```bash
   python src/cli/enhanced_cli.py --auto --interval 3 &
   ```

3. **查看完整任務列表**
   ```bash
   python task_panel_launcher.py  # 選擇 1，然後選擇 2
   ```

4. **集成到其他工具**
   ```python
   from src.core.task_panel import RealTimeTaskPanel
   panel = RealTimeTaskPanel()
   print(panel.update())
   ```

## 故障排除

### 面板不更新
- 檢查 `.session_todos.json` 文件是否存在
- 確認文件格式正確（有效的 JSON）
- 檢查文件權限

### 顯示不正常
- 嘗試調整面板寬度：`--width 50`
- 使用緊湊模式：`--compact`
- 檢查終端寬度（至少 80 列）

### 導入錯誤
- 確保在項目根目錄運行
- 檢查 Python 版本 >= 3.8
- 驗證所有依賴已安裝

## 後續改進計劃

- [ ] 支持 ANSI 位置控制（固定面板位置）
- [ ] 添加面板主題定制
- [ ] 支持任務排序和過濾
- [ ] 集成到 Web 儀表板
- [ ] 支持遠程任務同步

## 相關文件

- `src/core/task_panel.py` - 面板核心實現
- `src/cli/enhanced_cli.py` - 增強 CLI 實現
- `task_panel_launcher.py` - 快速啟動器
- `config/session_recap_config.yaml` - 配置文件
