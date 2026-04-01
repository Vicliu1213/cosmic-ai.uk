---
name: OpenCode 量子遺傳算法進化系統完整指南
description: 如何使用自進化系統優化 OpenCode 配置
---

# 🧬 OpenCode 量子遺傳算法進化系統

完整的自進化編碼助手系統，融合量子計算邏輯與經典遺傳算法。

## 📚 概述

### 核心理念

此系統基於三個量子計算概念：

1. **量子疊加態** - 配置的多種可能性同時存在並探索
2. **量子糾纏** - 代理、模型和工具之間的相互依賴關係
3. **測量坍縮** - 通過性能評估選擇最優配置

### 遺傳算法循環

```
初始種群 → 評估適應度 → 選擇 → 交叉與突變 → 新種群
   ↑                                        ↓
   └─────────────── 重複直到收斂 ──────────┘
```

---

## 🚀 快速開始

### 1. 初始化系統

```bash
python opencode_evolution_system.py --init
```

這將創建：
- `~/.config/opencode/opencode.json` - 主配置文件
- `~/.config/opencode/backups/` - 備份目錄
- `~/.config/opencode/skills/` - 技能配置目錄

### 2. 記錄性能數據

在使用 OpenCode 進行各類任務後，記錄性能指標：

```bash
python opencode_evolution_system.py --record <task_type> <agent> <quality> <duration> <success> <tokens>
```

**參數說明：**
- `task_type`: 任務類型 (code_generation, analysis, debug, refactor)
- `agent`: 使用的代理 (build, plan, general, explore)
- `quality`: 品質得分 (0-100)
- `duration`: 執行時間 (秒)
- `success`: 是否成功 (true/false)
- `tokens`: 使用的 Token 數量

**示例：**

```bash
# 代碼生成任務，使用 build 代理
python opencode_evolution_system.py --record code_generation build 95.0 12.5 true 1500

# 代碼分析任務，使用 plan 代理
python opencode_evolution_system.py --record analysis plan 88.0 8.2 true 950

# 調試任務，使用 explore 代理
python opencode_evolution_system.py --record debug explore 91.0 10.5 true 1200
```

### 3. 查看性能報告

```bash
python opencode_evolution_system.py --report
```

輸出示例：
```
📊 總體統計:
  • 任務總數: 4
  • 成功率: 100.0%
  • 平均品質: 91.5/100
  • 平均耗時: 11.62秒

🤖 代理性能詳情:
  BUILD:
    • 使用次數: 2
    • 成功率: 100.0%
    • 平均品質: 93.5
```

### 4. 執行進化優化

```bash
python quantum_genetic_algorithm.py
```

這將：
- 初始化 20 個配置變體的種群
- 運行 30 代進化
- 生成優化報告
- 導出最優配置到 `~/.config/opencode/evolved_config.json`

### 5. 應用最優配置

```bash
python opencode_evolution_system.py --apply
```

**結果：**
- 當前配置備份到 `~/.config/opencode/backups/`
- 最優配置應用到 `~/.config/opencode/opencode.json`

---

## 🧠 工作原理

### 配置基因

每個配置由以下基因組成：

| 基因名 | 範圍 | 說明 |
|-------|------|------|
| `temperature` | 0.0 - 1.0 | 模型創意度（低=確定，高=創意） |
| `max_steps` | 5 - 20 | 最大執行步數 |
| `agent_type` | 離散 | 使用的代理類型 |
| `model_size` | 離散 | 模型大小（快速/平衡/強力） |
| `scroll_acceleration` | 布爾 | 是否啟用滾動加速 |
| `auto_save_interval` | 30 - 300 | 自動保存間隔（秒） |

### 適應度評估

適應度得分基於：

```
適應度 = 代理匹配權重(40%) + 溫度匹配(30%) + 效率(30%)
```

- **代理匹配**：配置的代理類型是否適合任務
- **溫度匹配**：配置的溫度是否接近任務的最優溫度
- **效率**：步數是否不超過最優步數

### 進化操作

1. **選擇** - 基於量子振幅的概率選擇
   ```
   選擇概率 ∝ √(適應度 / 最大適應度)
   ```

2. **交叉** - 單點交叉產生後代

3. **突變** - 高斯突變調整參數值

---

## 📊 數據文件

### 性能指標日誌

**文件：** `~/.config/opencode/evolution_metrics.jsonl`

每行一個指標記錄：

```json
{
  "timestamp": "2026-02-15T16:12:32.123456",
  "task_type": "code_generation",
  "agent": "build",
  "quality_score": 95.0,
  "duration_seconds": 12.5,
  "success": true,
  "tokens_used": 1500
}
```

### 進化配置

**文件：** `~/.config/opencode/evolved_config.json`

```json
{
  "model": "anthropic/claude-haiku-4-20250514",
  "optimization": {
    "temperature": 0.28,
    "max_steps": 5,
    "agent_type": "build",
    "model_size": "fast"
  },
  "genetic_algorithm": {
    "fitness": 77.0,
    "generation": 30,
    "evolved_at": "2026-02-15T16:12:18.664839"
  }
}
```

---

## 💡 使用最佳實踐

### 1. 持續記錄

在每個主要任務後記錄性能：

```bash
#!/bin/bash
# 在 OpenCode 使用後執行

python opencode_evolution_system.py \
  --record code_generation build 94.0 15.2 true 1600
```

### 2. 定期進化

每週或積累足夠數據後執行進化：

```bash
# 每週執行
python quantum_genetic_algorithm.py
```

### 3. 監控進化進度

查看適應度圖表，確保有改進：

```bash
python opencode_evolution_system.py --report
```

### 4. 驗證新配置

應用新配置後，驗證性能是否提升：

```bash
python opencode_evolution_system.py --apply

# 使用新配置工作
opencode

# 記錄新配置下的性能
python opencode_evolution_system.py \
  --record code_generation build 96.0 14.8 true 1550
```

---

## 🔧 進階配置

### 自定義進化參數

編輯 `quantum_genetic_algorithm.py`：

```python
# 調整種群大小和代數
ga = QuantumGeneticAlgorithm(
    population_size=30,    # 增加種群多樣性
    generations=50         # 更多代數 = 更好結果（但更慢）
)
```

### 自定義評估函數

修改 `evaluate_fitness` 方法以適應你的需求：

```python
def evaluate_fitness(self, chromosome, task_history):
    # 自定義適應度計算邏輯
    ...
```

---

## 📈 解釋報告

### 進化統計

```
📊 進化統計:
  • 總代數: 30             # 已進化的世代數
  • 種群大小: 20           # 每代配置數量
  • 最終適應度: 77.0/100   # 最優配置的得分
  • 適應度改善: +0.00      # 首尾適應度差
  • 平均進步: 0.0000/代    # 每代平均改善
```

### 適應度演變圖

```
📈 適應度演變:
  [21] ███████░░░ 77.0    # 第 21 代，適應度 77.0
  [22] ███████░░░ 77.0
  ...
  [30] ███████░░░ 77.0
```

- 滿滿的 █ 表示高適應度
- 如果圖表停滯，表示已收斂

---

## 🐛 故障排除

### 問題：適應度沒有改善

**原因：** 任務數據不足或評估函數不准確

**解決：**
1. 記錄更多性能數據
2. 調整 `evaluate_fitness` 中的權重
3. 增加種群大小和代數

### 問題：配置應用後性能下降

**原因：** 新配置可能過度優化了特定任務

**解決：**
1. 恢復備份：`cp ~/.config/opencode/backups/opencode_backup_*.json ~/.config/opencode/opencode.json`
2. 記錄不同任務的性能
3. 重新運行進化

### 問題：進化太慢

**原因：** 種群太大或代數過多

**解決：**
```python
ga = QuantumGeneticAlgorithm(
    population_size=15,    # 減小種群
    generations=20         # 減少代數
)
```

---

## 📚 相關文件

- **主配置：** `~/.config/opencode/opencode.json`
- **進化引擎：** `quantum_genetic_algorithm.py`
- **系統管理：** `opencode_evolution_system.py`
- **性能監測：** `opencode_evolution_engine.py`

---

## 🎯 下一步

1. ✅ 初始化系統
2. ✅ 記錄日常性能數據
3. ✅ 運行進化優化
4. ✅ 應用最優配置
5. ✅ 驗證改進效果
6. 🔄 重複 2-5 步以持續優化

---

祝你使用愉快！🚀
