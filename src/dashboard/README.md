# 🌌 宇宙交易 AI - 統一面板系統

**版本**: 1.0  
**狀態**: ✅ 生產就緒  
**發布日期**: 2026-03-03

---

## 🎯 一句話介紹

將 Cosmic Engine、EthanAlgoX、交易引擎整合到**一個實時儀表板**中，監控 15 個理論模塊、實時交易指標、風險管理和自動告警。

---

## ⚡ 5 分鐘快速開始

### 1️⃣ 運行面板

```bash
cd /workspaces/cosmic-ai.uk
python -m src.dashboard.integration_examples
```

### 2️⃣ 看到儀表板

實時顯示：
- ✅ 15 個 Cosmic Engine 理論模塊狀態
- 📊 交易績效（Sharpe、勝率、PnL）
- 💰 套利、HFT、風險管理數據
- 🔔 實時告警

### 3️⃣ 添加自定義監控（2 行代碼）

```python
manager.add_custom_module("my_strategy", "我的策略", icon="🎯")
manager.add_custom_metric("my_strategy", "win_rate", MetricType.GAUGE, 0.65, "%")
```

---

## 📖 3 個核心概念

### 1️⃣ UnifiedPanel - 主儀表板

```python
from src.dashboard.unified_panel import UnifiedPanel

panel = UnifiedPanel()
panel.update_trade_metrics(metrics)
panel.add_alert("✅ 交易完成")
```

**功能**：監控 15 個 Cosmic Engine 模塊 + 交易指標 + 告警

### 2️⃣ PanelExtensionManager - 擴展工具

```python
from src.dashboard.panel_extensions import PanelExtensionManager, MetricType

manager = PanelExtensionManager(panel)
manager.add_custom_module("module_name", "顯示名稱", icon="📊")
manager.add_custom_metric("module_name", "metric", MetricType.GAUGE, 0.0, "%")
manager.update_metric("module_name", "metric", 0.75)
```

**功能**：添加無限個自定義模塊和指標

### 3️⃣ 集成橋接器 - 數據連接

```python
# Cosmic Engine 集成
cosmic_integration = CosmicEngineIntegration(panel)
cosmic_integration.update_module_from_ray_actor("quantum_singularity", result)

# EthanAlgoX 集成
ethanalgo_integration = EthanAlgoXIntegration(panel)
ethanalgo_integration.update_trade_metrics_from_bot(metrics_data)
```

**功能**：連接外部系統數據到面板

---

## 🎯 4 個監控場景

### 場景 1: 套利策略 💰

```python
from src.dashboard.integration_examples import ArbitrageStrategyMonitor

arbitrage = ArbitrageStrategyMonitor(panel, manager)
```

**監控**：BTC/ETH 價差、日套利收益、執行筆數  
**告警**：價差 > 0.5% (信息) / > 1.0% (警告)

### 場景 2: 高頻交易 ⚡

```python
from src.dashboard.integration_examples import HighFrequencyTradingMonitor

hft = HighFrequencyTradingMonitor(panel, manager)
```

**監控**：每秒訂單、延遲、成交率、日收益  
**告警**：延遲 > 50ms / 成交率 < 80%

### 場景 3: 風險管理 🛡️

```python
from src.dashboard.integration_examples import RiskManagementMonitor

risk = RiskManagementMonitor(panel, manager)
```

**監控**：倉位使用率、VaR、Beta、市場相關性  
**告警**：倉位 > 80% / VaR > $50k

### 場景 4: 機器學習 🤖

```python
from src.dashboard.integration_examples import MachineLearningMonitor

ml = MachineLearningMonitor(panel, manager)
```

**監控**：模型精度、訓練損失、模型漂移、預測數  
**告警**：精度 < 55% / 漂移 > 0.3

---

## 📁 文件結構

```
src/dashboard/
├── unified_panel.py           # 核心面板 (500+ 行)
├── panel_extensions.py        # 擴展系統 (600+ 行)
├── integration_examples.py    # 實際場景 (500+ 行)
├── QUICKSTART_GUIDE.md        # 詳細指南
└── README.md                  # 本文件
```

---

## 🚀 安裝與運行

### 安裝依賴

```bash
pip install rich ray asyncio
```

### 運行演示

```bash
# 完整集成演示（推薦）
python -m src.dashboard.integration_examples

# 基礎面板演示
python -c "import asyncio; from src.dashboard.unified_panel import run_panel_demo; asyncio.run(run_panel_demo())"
```

---

## 🔧 如何添加新功能

### 方法 A: 添加簡單指標（10 秒鐘）

```python
# 添加模塊
manager.add_custom_module("trading", "交易監控", icon="📈")

# 添加指標
manager.add_custom_metric(
    "trading",
    "daily_pnl",
    MetricType.COUNTER,
    0,
    "$",
    "今日收益"
)

# 更新指標
manager.update_metric("trading", "daily_pnl", 1000)
```

### 方法 B: 添加監控模塊（5 分鐘）

```python
class MyMonitor:
    def __init__(self, panel, manager):
        self.panel = panel
        self.manager = manager
        
        # 1. 添加模塊
        self.manager.add_custom_module("my_monitor", "我的監控", icon="🎯")
        
        # 2. 添加指標
        self.manager.add_custom_metric("my_monitor", "metric1", MetricType.GAUGE, 0.0, "%")
        
        # 3. 添加告警
        self.manager.add_alert_rule(
            "metric_alert",
            lambda: self._get_value() > 0.8,
            AlertLevel.WARNING,
            "指標超過 80%"
        )
    
    def _get_value(self):
        metric = self.manager.get_metric("my_monitor", "metric1")
        return metric.value if metric else 0.0
    
    async def run(self):
        while self.panel.is_running:
            await asyncio.sleep(1)
            new_value = calculate_value()  # 你的計算邏輯
            self.manager.update_metric("my_monitor", "metric1", new_value)
```

### 方法 C: 與外部系統集成

```python
# 從 API 獲取數據
async def sync_external_data():
    while panel.is_running:
        await asyncio.sleep(1)
        
        # 從 API 獲取數據
        data = await fetch_api_data()
        
        # 更新面板
        manager.update_metric("module", "metric", data['value'])
        
        # 檢查告警
        alerts = manager.check_alert_rules()
        for rule_name, level in alerts:
            panel.add_alert(f"{level.value} {rule_name}")
```

---

## 📊 儀表板示例

```
╔═══════════════════════════════════════════════════════╗
║     🌌 宇宙交易 AI - 統一面板系統                    ║
╚═══════════════════════════════════════════════════════╝

┌─────────────────────────────────────────────────────┐
│ 📊 系統概覽                                         │
│ 狀態: 🚀 運行中  |  運行時間: 120s  |  模塊: 15/15 │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│ 🧠 Cosmic Engine 理論模塊                          │
│                                                     │
│ 模塊名稱         | 狀態 | Actor ID | 耗時(ms)      │
│ quantum_...      | 🚀  | actor... | 45.2         │
│ temporal_...     | 🚀  | actor... | 43.8         │
│ cosmic_...       | 🚀  | actor... | 50.1         │
│ ...（12 個更多） |     |          |              │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│ 💰 交易指標                                        │
│ 總交易: 256  |  勝率: 65.2%  |  Sharpe: 2.15      │
│ 總 PnL: $12,450.50  |  今日 PnL: $3,250.00       │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│ 🔔 系統告警                                        │
│ [12:34:56] ✅ Ray 集群已初始化                    │
│ [12:35:02] 💰 執行套利: 預計利潤 $245.50         │
│ [12:35:08] ⚡ HFT 訂單: 45 筆/秒, 延遲 25.3ms   │
└─────────────────────────────────────────────────────┘
```

---

## 📚 詳細文檔

| 文檔 | 內容 | 時間 |
|-----|------|------|
| **本文件** | 快速概覽 | 5 分鐘 |
| **QUICKSTART_GUIDE.md** | 詳細教程 + 高級用法 | 30 分鐘 |
| **unified_panel.py** | UnifiedPanel API 文檔 | 代碼中 |
| **panel_extensions.py** | PanelExtensionManager API 文檔 | 代碼中 |
| **integration_examples.py** | 4 個實際場景代碼 | 代碼中 |

---

## 🎓 學習路徑

### 初級 (10 分鐘)
1. 閱讀本 README
2. 運行 `python -m src.dashboard.integration_examples`
3. 觀察儀表板輸出

### 中級 (1 小時)
1. 閱讀 QUICKSTART_GUIDE.md
2. 修改 integration_examples.py 中的參數
3. 添加 1-2 個自定義指標

### 高級 (2-3 小時)
1. 創建自己的 Monitor 類
2. 集成真實的交易數據
3. 實現自定義告警和通知

---

## ❓ 常見問題

**Q: 能監控多少個模塊？**  
A: Cosmic Engine 固定 15 個理論模塊，自定義模塊無限制

**Q: 如何實時看到更新？**  
A: 默認 1 秒刷新一次，可配置 `refresh_interval` 參數

**Q: 能導出數據嗎？**  
A: 是的，詳見 QUICKSTART_GUIDE.md 的高級用法

**Q: 如何集成我自己的數據源？**  
A: 使用 `manager.update_metric()` 更新數據

**Q: 支持遠程訪問嗎？**  
A: 可以配合 Web 框架實現，詳見高級用法

---

## 🔗 快速鏈接

- 📖 [詳細指南](./QUICKSTART_GUIDE.md)
- 💻 [完整代碼](./unified_panel.py)
- 🔧 [擴展系統](./panel_extensions.py)
- 📝 [集成示例](./integration_examples.py)

---

**準備開始了嗎？** 👉 `python -m src.dashboard.integration_examples`

**需要詳細説明？** 👉 閱讀 [QUICKSTART_GUIDE.md](./QUICKSTART_GUIDE.md)

---

**統一面板系統** - 宇宙交易 AI 的核心可視化層  
✅ 生產就緒 | 🚀 即插即用 | 🎯 易於擴展
