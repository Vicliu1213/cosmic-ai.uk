# 🎯 雙框任務面板 - 即時任務 vs 完成任務

## 概述

**雙框任務面板**是一個強大的任務可視化工具，支持左右分欄顯示：
- **左側框** 🔵 - 即時任務（進行中 + 待辦）
- **右側框** ✅ - 完成任務（已完成）
- **統計條** 📊 - 實時進度和統計信息

## 快速開始

### 最簡單的方式（推薦）

```bash
python dual_panel_launcher.py
```

然後選擇：
- **1** - 交互模式（帶菜單）⭐ 推薦
- **2** - 自動更新模式
- **3** - 緊湊模式

### 命令行啟動

```bash
# 交互模式（默認）
python src/core/dual_task_panel.py

# 自動更新（2秒刷新）
python src/core/dual_task_panel.py --auto --interval 2

# 緊湊模式
python src/core/dual_task_panel.py --compact

# 緊湊 + 自動更新
python src/core/dual_task_panel.py --auto --compact --interval 3
```

---

## 📊 面板布局

### 完整模式

```
==================================================================================
                          📋 實時任務面板 - 即時任務 vs 完成任務
==================================================================================

┌───────────────────────────────────────────┐  ┌─────────────────────────────────┐
│ 🔵 即時任務（進行中+待辦）                      │  │ ✅ 已完成任務                     │
├───────────────────────────────────────────┤  ├─────────────────────────────────┤
│ 🕐 23:11:04                                │  │ ✅ 3/6 已完成                     │
├───────────────────────────────────────────┤  ├─────────────────────────────────┤
│ 🔄 進行中的任務:                              │  │ █████████████░░░░░░░░░░░░░░ 50% │
│ 🔵🟡 測試自動化回顧系統                          │  ├─────────────────────────────────┤
├───────────────────────────────────────────┤  │ ✅🔴 創建自動化回顧配置文件 (YAML) │
│ ⏳ 待辦的任務:                                │  │ ✅🔴 創建自動化回顧核心模塊       │
│ ⬜🟡 優化回顧輸出格式                           │  │ ✅🔴 集成回顧功能到 CLI         │
│ ⬜🟢 添加自動回顧到啟動流程                      │  └─────────────────────────────────┘
└───────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────┐
│ 📊 統計: ✅3 🔵1 ⏳2 ❌0 | 進度: 50%                                               │
└─────────────────────────────────────────────────────────────────────────────────┘

🌿 分支: main | 🕐 更新時間: 23:11:04
==================================================================================
```

### 緊湊模式

```
┌─────────────────────────────────────────────────────┐
│ 📊 任務統計 | ✅3 🔵1 ⏳2 | 進度: 50%
├─────────────────────────────────────────────────────┤
│ 🔄 進行中:
│   • 測試自動化回顧系統
│ ⏳ 待辦:
│   • 優化回顧輸出格式
│   • 添加自動回顧到啟動流程
└─────────────────────────────────────────────────────┘
```

---

## 🎮 交互模式菜單

在交互模式下，可以使用以下功能：

```
1. 刷新面板      - 更新當前顯示
2. 切換模式      - 在完整/緊湊模式之間切換
3. 自動更新      - 啟動自動更新（5秒刷新）
4. 完整列表      - 查看所有任務的詳細列表
5. 查看建議      - 顯示系統建議
6. 退出          - 退出程序
```

---

## 🎨 面板特性

### 左側框：即時任務
- 🔄 **進行中的任務** - 標記為 🔵
- ⏳ **待辦的任務** - 標記為 ⬜
- 📍 **時間戳** - 實時顯示當前時間
- 🎯 **優先級標記** - 🔴高 🟡中 🟢低

### 右側框：完成任務
- ✅ **已完成任務** - 標記為 ✅
- 📊 **完成統計** - 顯示 X/Y 已完成
- 📈 **進度條** - 可視化完成百分比
- 📝 **任務內容** - 已完成任務的詳細信息

### 統計條
- 📊 **狀態計數** - ✅已完成 🔵進行中 ⏳待辦 ❌已取消
- 📈 **進度百分比** - 完成率百分比
- 🌿 **Git 分支** - 當前工作分支
- 🕐 **更新時間** - 最後更新時間

---

## 📋 配置選項

### 面板寬度
```python
left_width: int = 45      # 左框寬度
right_width: int = 35     # 右框寬度
```

### 顯示任務數
```python
max_left_tasks: int = 10   # 左側最多顯示10個任務
max_right_tasks: int = 8   # 右側最多顯示8個任務
```

### 更新間隔
```python
refresh_interval: int = 3  # 刷新間隔3秒
```

### 顯示選項
```python
compact_mode: bool = False       # 緊湊模式
show_progress_bar: bool = True   # 顯示進度條
show_stats: bool = True          # 顯示統計信息
```

---

## 🔄 自動更新模式

在自動更新模式下，面板會每隔指定的秒數自動刷新一次，無需手動操作。

```bash
# 3秒刷新一次
python src/core/dual_task_panel.py --auto --interval 3

# 2秒刷新一次（更快）
python src/core/dual_task_panel.py --auto --interval 2

# 緊湊模式，2秒刷新
python src/core/dual_task_panel.py --auto --compact --interval 2
```

按 **Ctrl+C** 退出自動更新模式。

---

## 📊 符號說明

### 狀態符號
| 符號 | 狀態 | 含義 |
|------|------|------|
| 🔵 | in_progress | 進行中 |
| ⬜ | pending | 待辦 |
| ✅ | completed | 已完成 |
| ❌ | cancelled | 已取消 |

### 優先級符號
| 符號 | 優先級 | 含義 |
|------|--------|------|
| 🔴 | high | 高優先級 |
| 🟡 | medium | 中優先級 |
| 🟢 | low | 低優先級 |

### 其他符號
| 符號 | 含義 |
|------|------|
| 🔄 | 進行中的任務 |
| ⏳ | 待辦的任務 |
| 📊 | 統計信息 |
| 🌿 | Git 分支 |
| 🕐 | 時間信息 |
| 📈 | 進度 |

---

## 💡 使用建議

### 開發中監控進度
```bash
python dual_panel_launcher.py  # 選擇交互模式
```

### 後台實時監控
```bash
python src/core/dual_task_panel.py --auto --interval 2 &
```

### 會議演示
```bash
python src/core/dual_task_panel.py --auto --interval 5
```

### 快速查看
```bash
python src/core/dual_task_panel.py
```

---

## 🔧 高級用法

### 在 Python 代碼中使用

```python
from src.core.dual_task_panel import DualTaskPanel, DualPanelConfig

# 創建配置
config = DualPanelConfig(
    left_width=50,
    right_width=40,
    max_left_tasks=12,
    max_right_tasks=10,
    refresh_interval=2,
    compact_mode=False,
    show_progress_bar=True
)

# 創建面板
panel = DualTaskPanel(config)

# 生成並顯示
panel.display()

# 獲取面板文本
panel_text = panel.update()
print(panel_text)
```

### 集成到其他工具

```python
from src.core.dual_task_panel import InteractiveDualPanel

panel = InteractiveDualPanel()
panel.run()
```

---

## 📁 文件結構

```
/root/comic_ai/
├── src/core/
│   ├── dual_task_panel.py     # 雙框面板核心
│   ├── task_panel.py          # 單框面板
│   └── session_recap.py       # 會話回顧
├── dual_panel_launcher.py     # 快速啟動
├── task_panel_launcher.py     # 單框啟動
└── recap_cli.py               # 回顧命令
```

---

## ❓ 常見問題

### Q: 面板不更新？
**A:** 確認 `.session_todos.json` 文件存在且格式正確

### Q: 如何修改任務？
**A:** 編輯 `.session_todos.json`，面板會自動檢測變更

### Q: 可以改變面板寬度嗎？
**A:** 可以，在 Python 代碼中修改 `DualPanelConfig` 的 `left_width` 和 `right_width`

### Q: 支持自定義主題嗎？
**A:** 目前不支持，但可以修改源代碼中的符號和顏色

### Q: 如何在終端固定位置顯示？
**A:** 暫不支持，可使用分屏終端軟件

---

## 🚀 快速命令參考

```bash
# 一鍵啟動（推薦）
python dual_panel_launcher.py

# 查看即時面板
python src/core/dual_task_panel.py

# 自動更新（右上角推薦）
python src/core/dual_task_panel.py --auto --interval 2

# 緊湊自動更新
python src/core/dual_task_panel.py --auto --compact

# 完整任務列表
python recap_cli.py

# 只看待辦任務
python recap_cli.py --todos
```

---

## 📝 後續改進

- [ ] 支持任務狀態更新
- [ ] 支持任務排序和過濾
- [ ] 添加搜索功能
- [ ] 支持自定義主題
- [ ] 集成到 Web 儀表板
- [ ] 支持遠程任務同步

---

立即開始：

```bash
python dual_panel_launcher.py
```

祝您使用愉快！🎉
