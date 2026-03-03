# 🌌 宇宙交易 AI - 面板系統快速開始指南

**最後更新**: 2026-03-03  
**版本**: 1.0 - 生產就緒

---

## 📚 5 分鐘快速開始

### Step 1: 安裝依賴

```bash
cd /workspaces/cosmic-ai.uk

# 安裝必要的包
pip install rich ray asyncio
```

### Step 2: 運行面板演示

```bash
# 方式 1: 運行完整集成演示（推薦）
python -m src.dashboard.integration_examples

# 方式 2: 運行基礎面板演示
python -c "import asyncio; from src.dashboard.unified_panel import run_panel_demo; asyncio.run(run_panel_demo())"
```

### Step 3: 查看實時儀表板

你應該看到一個類似這樣的界面：

```
╔════════════════════════════════════════════════════════════════════════╗
║           🌌 宇宙交易 AI - 統一面板系統                               ║
╚════════════════════════════════════════════════════════════════════════╝

┌─────────────────────────────────────────────────────────────────────┐
│ 📊 系統概覽                                                         │
│                                                                     │
│ 面板狀態: 🚀 運行中                                                  │
│ 運行時間: 120 秒                                                    │
│ 已連接模塊: 15/15                                                  │
│ 活躍告警: 3                                                        │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│ 🧠 Cosmic Engine - 15 個理論模塊                                    │
│                                                                     │
│ 模塊名稱            │ 狀態   │ Actor ID │ 調用 │ 錯誤 │ 耗時    │
│ quantum_singularity │ 🚀... │ actor... │ 120  │ 0    │ 45.2   │
│ temporal_dominance  │ 🚀... │ actor... │ 118  │ 0    │ 43.8   │
│ cosmic_intelligence │ 🚀... │ actor... │ 115  │ 1    │ 50.1   │
│ ...                 │ ...    │ ...      │ ...  │ ...  │ ...    │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│ 💰 交易指標                                                        │
│                                                                     │
│ 總交易次數: 256                                                     │
│ 勝率: 65.2%                                                         │
│ 總 PnL: $12,450.50                                                 │
│ Sharpe 比率: 2.15                                                  │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│ 🔔 系統告警                                                        │
│                                                                     │
│ [12:34:56] ✅ Ray 集群已初始化                                     │
│ [12:35:02] 💰 執行套利: BTC 買賣, 預計利潤 $245.50               │
│ [12:35:08] ⚡ HFT 訂單: 45 筆/秒, 延遲 25.3ms                    │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 🎯 核心概念

### 1. 統一面板 (UnifiedPanel)

**主要功能**：
- 監控所有 15 個 Cosmic Engine 理論模塊
- 顯示實時交易指標
- 管理系統告警

**使用方式**：
```python
from src.dashboard.unified_panel import UnifiedPanel

# 創建面板
panel = UnifiedPanel(refresh_interval=1)

# 更新交易指標
from src.dashboard.unified_panel import TradeMetrics
metrics = TradeMetrics(
    total_trades=100,
    winning_trades=65,
    sharpe_ratio=2.15,
    total_pnl=12450.50
)
panel.update_trade_metrics(metrics)

# 添加告警
panel.add_alert("✅ 高頻交易執行完成")
```

### 2. 面板擴展管理器 (PanelExtensionManager)

**主要功能**：
- 添加自定義監控模塊
- 管理自定義指標
- 設置告警規則

**使用方式**：
```python
from src.dashboard.panel_extensions import PanelExtensionManager, MetricType, AlertLevel

manager = PanelExtensionManager(panel)

# 添加自定義模塊
manager.add_custom_module(
    "my_strategy",
    "我的策略",
    "自定義交易策略監控",
    icon="🎯"
)

# 添加指標
manager.add_custom_metric(
    "my_strategy",
    "win_rate",
    MetricType.GAUGE,
    0.65,
    "%",
    "勝率"
)

# 更新指標
manager.update_metric("my_strategy", "win_rate", 0.72)

# 添加告警規則
manager.add_alert_rule(
    "high_win_rate",
    lambda: manager.get_metric("my_strategy", "win_rate").value > 0.70,
    AlertLevel.INFO,
    "勝率高於 70%"
)
```

### 3. 集成橋接器

**Cosmic Engine 集成**：
```python
from src.dashboard.unified_panel import CosmicEngineIntegration

cosmic_integration = CosmicEngineIntegration(panel)

# 從 Ray Actor 更新模塊狀態
cosmic_integration.update_module_from_ray_actor(
    "quantum_singularity",
    {
        "actor_id": "actor_001",
        "processing_time_ms": 45.2,
        "result": "Optimization complete"
    }
)
```

**EthanAlgoX 集成**：
```python
from src.dashboard.unified_panel import EthanAlgoXIntegration

ethanalgo_integration = EthanAlgoXIntegration(panel)

# 從 MarketBot/LLM-TradeBot 更新交易指標
ethanalgo_integration.update_trade_metrics_from_bot({
    "total_trades": 256,
    "winning_trades": 167,
    "win_rate": 0.652,
    "total_pnl": 12450.50,
    "sharpe_ratio": 2.15
})
```

---

## 🚀 實際使用場景

### 場景 1: 套利策略監控

```python
from src.dashboard.integration_examples import ArbitrageStrategyMonitor

# 初始化套利監控
arbitrage = ArbitrageStrategyMonitor(panel, manager)

# 更新價差數據
manager.update_metric("arbitrage_strategy", "btc_usd_spread", 0.75)
manager.update_metric("arbitrage_strategy", "eth_usd_spread", 0.45)

# 記錄執行結果
manager.increment_metric("arbitrage_strategy", "daily_arbitrage_profit", 245.50)
manager.increment_metric("arbitrage_strategy", "executed_trades")
```

**監控指標**：
- `btc_usd_spread`: BTC-USD 價差 (%)
- `eth_usd_spread`: ETH-USD 價差 (%)
- `daily_arbitrage_profit`: 今日套利收益 ($)
- `executed_trades`: 已執行套利筆數

**自動告警**：
- `high_btc_spread`: BTC 價差 > 0.5% 時觸發
- `high_profit_opportunity`: BTC 價差 > 1.0% 時觸發

### 場景 2: 高頻交易監控

```python
from src.dashboard.integration_examples import HighFrequencyTradingMonitor

# 初始化 HFT 監控
hft = HighFrequencyTradingMonitor(panel, manager)

# 更新 HFT 指標
manager.update_metric("hft", "orders_per_second", 45)
manager.update_metric("hft", "avg_latency_ms", 25.3)
manager.update_metric("hft", "fill_rate", 95.2)
```

**監控指標**：
- `orders_per_second`: 每秒訂單數 (筆/秒)
- `avg_latency_ms`: 平均訂單延遲 (ms)
- `fill_rate`: 訂單成交率 (%)
- `daily_hft_pnl`: 今日 HFT 收益 ($)

### 場景 3: 風險管理面板

```python
from src.dashboard.integration_examples import RiskManagementMonitor

# 初始化風險管理監控
risk = RiskManagementMonitor(panel, manager)

# 更新風險指標
manager.update_metric("risk_management", "position_limit_usage", 75.5)
manager.update_metric("risk_management", "var_95", 45000)
manager.update_metric("risk_management", "portfolio_beta", 1.1)
```

**監控指標**：
- `position_limit_usage`: 倉位限制使用率 (%)
- `var_95`: 95% 風險在值 ($)
- `portfolio_beta`: 投資組合 Beta
- `correlation_with_market`: 與市場相關性

### 場景 4: 機器學習模型追蹤

```python
from src.dashboard.integration_examples import MachineLearningMonitor

# 初始化 ML 監控
ml = MachineLearningMonitor(panel, manager)

# 更新 ML 指標
manager.update_metric("ml_models", "model_accuracy", 72.5)
manager.update_metric("ml_models", "training_loss", 0.245)
manager.update_metric("ml_models", "model_drift_score", 0.15)
```

**監控指標**：
- `model_accuracy`: 模型預測精度 (%)
- `training_loss`: 訓練損失
- `model_drift_score`: 模型漂移指數
- `predictions_per_minute`: 每分鐘預測數

---

## 📊 如何添加新功能

### 添加新監控模塊（3 步）

#### Step 1: 創建模塊

```python
# 在 src/dashboard/integration_examples.py 中添加

class MyCustomMonitor:
    def __init__(self, panel, manager):
        self.panel = panel
        self.manager = manager
        
        # 添加模塊
        self.manager.add_custom_module(
            "my_module",           # 內部名稱
            "我的模塊",            # 顯示名稱
            "模塊描述",            # 描述
            icon="🎯"              # 圖標
        )
        
        # 添加指標
        self.manager.add_custom_metric(
            "my_module",
            "my_metric",
            MetricType.GAUGE,
            0.0,
            "%",
            "我的指標描述"
        )
```

#### Step 2: 添加告警規則

```python
    def __init__(self, panel, manager):
        # ... 前面的代碼 ...
        
        # 添加告警規則
        self.manager.add_alert_rule(
            "my_alert_rule",
            lambda: self._get_metric_value() > threshold,
            AlertLevel.WARNING,
            "告警描述"
        )
    
    def _get_metric_value(self):
        metric = self.manager.get_metric("my_module", "my_metric")
        return metric.value if metric else 0.0
```

#### Step 3: 更新指標

```python
    async def update_metrics(self):
        while self.panel.is_running:
            await asyncio.sleep(1)
            
            # 更新指標
            new_value = calculate_value()
            self.manager.update_metric("my_module", "my_metric", new_value)
            
            # 或者增加計數
            self.manager.increment_metric("my_module", "my_counter", 1)
```

### 快速模板

創建新文件 `src/dashboard/custom_monitors.py`：

```python
#!/usr/bin/env python3
"""
自定義監控模塊
"""

import asyncio
import logging
from src.dashboard.unified_panel import UnifiedPanel
from src.dashboard.panel_extensions import (
    PanelExtensionManager,
    MetricType,
    AlertLevel,
)


class MyCustomMonitor:
    """我的自定義監控"""
    
    def __init__(self, panel: UnifiedPanel, manager: PanelExtensionManager):
        self.panel = panel
        self.manager = manager
        self.logger = logging.getLogger(__name__)
        
        # 添加模塊
        self.manager.add_custom_module(
            "my_module",
            "我的模塊",
            "模塊描述",
            icon="🎯"
        )
        
        # 添加指標
        self.manager.add_custom_metric(
            "my_module",
            "metric_1",
            MetricType.GAUGE,
            0.0,
            "",
            "指標 1"
        )
        
        # 添加告警
        self.manager.add_alert_rule(
            "my_alert",
            lambda: self._check_condition(),
            AlertLevel.WARNING,
            "告警條件"
        )
    
    def _check_condition(self) -> bool:
        metric = self.manager.get_metric("my_module", "metric_1")
        return metric.value > 0.7 if metric else False
    
    async def run(self):
        """運行監控循環"""
        while self.panel.is_running:
            await asyncio.sleep(1)
            
            # 計算新值
            new_value = 0.5  # 替換為實際計算
            
            # 更新指標
            self.manager.update_metric("my_module", "metric_1", new_value)


# 使用示例
async def main():
    from src.dashboard.unified_panel import run_panel_demo
    
    panel = UnifiedPanel()
    manager = PanelExtensionManager(panel)
    
    # 創建自定義監控
    my_monitor = MyCustomMonitor(panel, manager)
    
    # 運行面板和監控
    panel_task = asyncio.create_task(panel.start_live_display())
    monitor_task = asyncio.create_task(my_monitor.run())
    
    await asyncio.gather(panel_task, monitor_task)


if __name__ == "__main__":
    asyncio.run(main())
```

---

## 🔧 高級用法

### 1. 自定義渲染

```python
# 在面板擴展中添加自定義渲染
def render_my_custom_panel(manager):
    from rich.panel import Panel
    
    content = "自定義內容"
    return Panel(content, title="我的面板", border_style="cyan")

# 集成到主面板
panel.custom_panels.append(render_my_custom_panel)
```

### 2. 數據持久化

```python
import json

# 保存指標歷史
def save_metrics_history(manager, filename):
    history = {}
    for module_name, metrics in manager.custom_metrics.items():
        history[module_name] = {
            metric_name: {
                "value": metric.value,
                "history": metric.history[-10:]  # 保存最近 10 個值
            }
            for metric_name, metric in metrics.items()
        }
    
    with open(filename, 'w') as f:
        json.dump(history, f, indent=2)

# 定期保存
async def periodic_save(manager):
    while True:
        await asyncio.sleep(60)
        save_metrics_history(manager, "metrics_history.json")
```

### 3. 與外部系統集成

```python
# 集成 Webhook 告警
async def send_webhook_alert(alert_message):
    import aiohttp
    
    async with aiohttp.ClientSession() as session:
        await session.post(
            "https://your-webhook.url",
            json={"message": alert_message}
        )

# 在告警規則中使用
async def alert_with_webhook(manager):
    while True:
        await asyncio.sleep(1)
        alerts = manager.check_alert_rules()
        for rule_name, level in alerts:
            await send_webhook_alert(f"{level.value}: {rule_name}")
```

---

## 📝 常見問題

### Q1: 如何連接真實的 Cosmic Engine 數據？

```python
# 使用 Ray 遠程調用
import ray

actor_ref = ray.get_actor("quantum_singularity_actor")
result = ray.get(actor_ref.run_cycle.remote(market_data))

cosmic_integration.update_module_from_ray_actor(
    "quantum_singularity",
    result
)
```

### Q2: 如何連接真實的 EthanAlgoX MarketBot 數據？

```python
# 從 MarketBot GraphQL API 獲取數據
import aiohttp

async def fetch_marketbot_data():
    async with aiohttp.ClientSession() as session:
        async with session.get(
            "http://marketbot-api:3000/metrics"
        ) as resp:
            return await resp.json()

# 定期更新
async def sync_marketbot_metrics():
    while panel.is_running:
        await asyncio.sleep(2)
        data = await fetch_marketbot_data()
        ethanalgo_integration.update_trade_metrics_from_bot(data)
```

### Q3: 如何導出指標報告？

```python
# 生成 CSV 報告
import csv
from datetime import datetime

def export_metrics_to_csv(manager, filename):
    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['時間', '模塊', '指標', '值', '單位'])
        
        for module_name, metrics in manager.custom_metrics.items():
            for metric_name, metric in metrics.items():
                for value in metric.history:
                    writer.writerow([
                        datetime.now().isoformat(),
                        module_name,
                        metric_name,
                        value,
                        metric.unit
                    ])
```

---

## 📚 相關文檔

- [統一面板 API 文檔](./unified_panel.py)
- [擴展管理器 API 文檔](./panel_extensions.py)
- [集成示例](./integration_examples.py)
- [Cosmic Engine 文檔](../../../cosmic_engine/STRUCTURE_SUMMARY.md)
- [EthanAlgoX 文檔](../../../external/MarketBot/)

---

## 🎓 學習路徑

1. **初級**: 運行面板演示
   - `python -m src.dashboard.integration_examples`

2. **中級**: 添加自定義指標
   - 修改 `ArbitrageStrategyMonitor` 示例
   - 添加新的指標和告警

3. **高級**: 創建完整的監控系統
   - 集成真實的交易數據
   - 實現數據持久化
   - 構建自定義告警系統

---

**最後更新**: 2026-03-03  
**版本**: 1.0 Release  
**狀態**: ✅ 生產就緒
