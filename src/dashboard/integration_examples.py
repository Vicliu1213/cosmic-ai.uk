#!/usr/bin/env python3
"""
面板集成示例 (Panel Integration Examples)
宇宙交易 AI - 實際使用案例

展示如何：
1. 集成 Cosmic Engine 理論模塊到面板
2. 集成 EthanAlgoX MarketBot 數據
3. 添加自定義交易策略監控
4. 設置即時告警和通知

實際使用場景：
- 套利策略監控
- 高頻交易儀表板
- 風險管理面板
- 機器學習模型跟蹤
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import random

from src.dashboard.unified_panel import (
    UnifiedPanel,
    PanelStatus,
    TradeMetrics,
    ComponentType,
)
from src.dashboard.panel_extensions import (
    PanelExtensionManager,
    MetricType,
    AlertLevel,
    create_standard_extension_set,
)


# ==================== 場景 1: 套利策略監控 ====================

class ArbitrageStrategyMonitor:
    """
    套利策略監控系統
    
    使用場景：
    - 監控跨交易所價差
    - 追蹤套利執行
    - 計算實際收益
    """
    
    def __init__(self, panel: UnifiedPanel, manager: PanelExtensionManager):
        self.panel = panel
        self.manager = manager
        self.logger = logging.getLogger(__name__)
        
        # 添加套利模塊
        self.manager.add_custom_module(
            "arbitrage_strategy",
            "套利策略監控",
            "實時監控 Binance-Kraken-Coinbase 價差",
            icon="💰"
        )
        
        # 添加關鍵指標
        self.manager.add_custom_metric(
            "arbitrage_strategy",
            "btc_usd_spread",
            MetricType.GAUGE,
            0.0,
            "%",
            "BTC-USD 價差"
        )
        
        self.manager.add_custom_metric(
            "arbitrage_strategy",
            "eth_usd_spread",
            MetricType.GAUGE,
            0.0,
            "%",
            "ETH-USD 價差"
        )
        
        self.manager.add_custom_metric(
            "arbitrage_strategy",
            "daily_arbitrage_profit",
            MetricType.COUNTER,
            0,
            "$",
            "今日套利收益"
        )
        
        self.manager.add_custom_metric(
            "arbitrage_strategy",
            "executed_trades",
            MetricType.COUNTER,
            0,
            "筆",
            "已執行套利筆數"
        )
        
        # 添加告警規則
        self.manager.add_alert_rule(
            "high_btc_spread",
            lambda: self._get_btc_spread() > 0.5,
            AlertLevel.INFO,
            "BTC 價差超過 0.5%"
        )
        
        self.manager.add_alert_rule(
            "high_profit_opportunity",
            lambda: self._get_btc_spread() > 1.0,
            AlertLevel.WARNING,
            "BTC 出現高利潤機會（> 1%）"
        )
        
        self.logger.info("✅ 套利策略監控已初始化")
    
    def _get_btc_spread(self) -> float:
        """獲取 BTC 價差"""
        metric = self.manager.get_metric("arbitrage_strategy", "btc_usd_spread")
        return metric.value if metric else 0.0
    
    async def simulate_price_updates(self):
        """模擬價格更新"""
        while self.panel.is_running:
            await asyncio.sleep(1)
            
            # 模擬 BTC 價差波動
            btc_spread = random.uniform(0.1, 1.5)
            self.manager.update_metric("arbitrage_strategy", "btc_usd_spread", btc_spread)
            
            # 模擬 ETH 價差波動
            eth_spread = random.uniform(0.05, 0.8)
            self.manager.update_metric("arbitrage_strategy", "eth_usd_spread", eth_spread)
            
            # 如果價差大於 0.5%，執行套利交易
            if btc_spread > 0.5 and random.random() > 0.3:
                profit = btc_spread * 100000  # 假設交易 1 BTC @ $100k
                self.manager.increment_metric("arbitrage_strategy", "daily_arbitrage_profit", profit)
                self.manager.increment_metric("arbitrage_strategy", "executed_trades")
                self.panel.add_alert(f"✅ 執行套利: BTC 買賣, 預計利潤 ${profit:.2f}")


# ==================== 場景 2: 高頻交易監控 ====================

class HighFrequencyTradingMonitor:
    """
    高頻交易監控系統
    
    使用場景：
    - 追蹤毫秒級訂單
    - 監控延遲和成交率
    - 計算 VWAP 和 TWAP
    """
    
    def __init__(self, panel: UnifiedPanel, manager: PanelExtensionManager):
        self.panel = panel
        self.manager = manager
        self.logger = logging.getLogger(__name__)
        
        # 添加 HFT 模塊
        self.manager.add_custom_module(
            "hft",
            "高頻交易系統",
            "毫秒級交易執行和市場微結構分析",
            icon="⚡"
        )
        
        # 添加關鍵指標
        self.manager.add_custom_metric(
            "hft",
            "orders_per_second",
            MetricType.GAUGE,
            0,
            "筆/秒",
            "每秒訂單數"
        )
        
        self.manager.add_custom_metric(
            "hft",
            "avg_latency_ms",
            MetricType.TIMER,
            0.0,
            "ms",
            "平均訂單延遲"
        )
        
        self.manager.add_custom_metric(
            "hft",
            "fill_rate",
            MetricType.GAUGE,
            0.0,
            "%",
            "訂單成交率"
        )
        
        self.manager.add_custom_metric(
            "hft",
            "daily_hft_pnl",
            MetricType.COUNTER,
            0,
            "$",
            "今日 HFT 收益"
        )
        
        # 添加告警規則
        self.manager.add_alert_rule(
            "high_latency",
            lambda: self._get_latency() > 50,
            AlertLevel.WARNING,
            "訂單延遲超過 50ms"
        )
        
        self.manager.add_alert_rule(
            "low_fill_rate",
            lambda: self._get_fill_rate() < 80,
            AlertLevel.WARNING,
            "訂單成交率低於 80%"
        )
        
        self.logger.info("✅ 高頻交易監控已初始化")
    
    def _get_latency(self) -> float:
        """獲取延遲"""
        metric = self.manager.get_metric("hft", "avg_latency_ms")
        return metric.value if metric else 0.0
    
    def _get_fill_rate(self) -> float:
        """獲取成交率"""
        metric = self.manager.get_metric("hft", "fill_rate")
        return metric.value if metric else 0.0
    
    async def simulate_hft_activity(self):
        """模擬 HFT 活動"""
        while self.panel.is_running:
            await asyncio.sleep(0.5)  # 更頻繁的更新
            
            # 模擬每秒訂單數
            orders = random.randint(10, 50)
            self.manager.update_metric("hft", "orders_per_second", orders)
            
            # 模擬延遲
            latency = random.uniform(5, 100)
            self.manager.update_metric("hft", "avg_latency_ms", latency)
            
            # 模擬成交率
            fill_rate = random.uniform(75, 99)
            self.manager.update_metric("hft", "fill_rate", fill_rate)
            
            # 模擬 PnL
            if random.random() > 0.8:
                pnl_increment = random.uniform(50, 500)
                self.manager.increment_metric("hft", "daily_hft_pnl", pnl_increment)


# ==================== 場景 3: 風險管理面板 ====================

class RiskManagementMonitor:
    """
    風險管理監控系統
    
    使用場景：
    - 監控倉位限制
    - 追蹤 VaR 和 CVaR
    - 管理風險敞口
    """
    
    def __init__(self, panel: UnifiedPanel, manager: PanelExtensionManager):
        self.panel = panel
        self.manager = manager
        self.logger = logging.getLogger(__name__)
        
        # 添加風險管理模塊
        self.manager.add_custom_module(
            "risk_management",
            "風險管理系統",
            "多層風險控制和動態倉位調整",
            icon="🛡️"
        )
        
        # 添加關鍵指標
        self.manager.add_custom_metric(
            "risk_management",
            "position_limit_usage",
            MetricType.GAUGE,
            0.0,
            "%",
            "倉位限制使用率"
        )
        
        self.manager.add_custom_metric(
            "risk_management",
            "var_95",
            MetricType.GAUGE,
            0.0,
            "$",
            "95% VaR（最大潛在損失）"
        )
        
        self.manager.add_custom_metric(
            "risk_management",
            "portfolio_beta",
            MetricType.GAUGE,
            0.0,
            "",
            "投資組合 Beta"
        )
        
        self.manager.add_custom_metric(
            "risk_management",
            "correlation_with_market",
            MetricType.GAUGE,
            0.0,
            "",
            "與市場相關性"
        )
        
        # 添加告警規則
        self.manager.add_alert_rule(
            "high_position_usage",
            lambda: self._get_position_usage() > 80,
            AlertLevel.WARNING,
            "倉位使用率超過 80%"
        )
        
        self.manager.add_alert_rule(
            "var_limit_exceeded",
            lambda: self._get_var() > 50000,
            AlertLevel.CRITICAL,
            "VaR 超過 $50,000"
        )
        
        self.logger.info("✅ 風險管理監控已初始化")
    
    def _get_position_usage(self) -> float:
        """獲取倉位使用率"""
        metric = self.manager.get_metric("risk_management", "position_limit_usage")
        return metric.value if metric else 0.0
    
    def _get_var(self) -> float:
        """獲取 VaR"""
        metric = self.manager.get_metric("risk_management", "var_95")
        return metric.value if metric else 0.0
    
    async def simulate_risk_metrics(self):
        """模擬風險指標"""
        while self.panel.is_running:
            await asyncio.sleep(2)
            
            # 模擬倉位使用率
            position_usage = random.uniform(20, 95)
            self.manager.update_metric("risk_management", "position_limit_usage", position_usage)
            
            # 模擬 VaR
            var = random.uniform(10000, 80000)
            self.manager.update_metric("risk_management", "var_95", var)
            
            # 模擬 Beta
            beta = random.uniform(0.5, 1.5)
            self.manager.update_metric("risk_management", "portfolio_beta", beta)
            
            # 模擬與市場相關性
            correlation = random.uniform(-0.2, 0.9)
            self.manager.update_metric("risk_management", "correlation_with_market", correlation)


# ==================== 場景 4: 機器學習模型追蹤 ====================

class MachineLearningMonitor:
    """
    機器學習模型監控系統
    
    使用場景：
    - 追蹤模型精度
    - 監控訓練進度
    - 檢測模型漂移
    """
    
    def __init__(self, panel: UnifiedPanel, manager: PanelExtensionManager):
        self.panel = panel
        self.manager = manager
        self.logger = logging.getLogger(__name__)
        
        # 添加 ML 模塊
        self.manager.add_custom_module(
            "ml_models",
            "機器學習系統",
            "深度學習策略和強化學習優化",
            icon="🤖"
        )
        
        # 添加關鍵指標
        self.manager.add_custom_metric(
            "ml_models",
            "model_accuracy",
            MetricType.GAUGE,
            0.5,
            "%",
            "模型預測精度"
        )
        
        self.manager.add_custom_metric(
            "ml_models",
            "training_loss",
            MetricType.GAUGE,
            1.0,
            "",
            "訓練損失"
        )
        
        self.manager.add_custom_metric(
            "ml_models",
            "model_drift_score",
            MetricType.GAUGE,
            0.0,
            "",
            "模型漂移指數"
        )
        
        self.manager.add_custom_metric(
            "ml_models",
            "predictions_per_minute",
            MetricType.COUNTER,
            0,
            "個/分",
            "每分鐘預測數"
        )
        
        # 添加告警規則
        self.manager.add_alert_rule(
            "accuracy_degraded",
            lambda: self._get_accuracy() < 55,
            AlertLevel.WARNING,
            "模型精度下降到 55% 以下"
        )
        
        self.manager.add_alert_rule(
            "high_model_drift",
            lambda: self._get_drift() > 0.3,
            AlertLevel.CRITICAL,
            "檢測到模型漂移（> 0.3）"
        )
        
        self.logger.info("✅ 機器學習監控已初始化")
    
    def _get_accuracy(self) -> float:
        """獲取模型精度"""
        metric = self.manager.get_metric("ml_models", "model_accuracy")
        return metric.value if metric else 0.0
    
    def _get_drift(self) -> float:
        """獲取模型漂移"""
        metric = self.manager.get_metric("ml_models", "model_drift_score")
        return metric.value if metric else 0.0
    
    async def simulate_ml_training(self):
        """模擬 ML 訓練過程"""
        while self.panel.is_running:
            await asyncio.sleep(2)
            
            # 模擬精度改進（訓練過程中逐漸提升）
            current_acc = self._get_accuracy()
            new_acc = min(current_acc + random.uniform(-2, 3), 95)
            self.manager.update_metric("ml_models", "model_accuracy", new_acc)
            
            # 模擬損失下降
            current_loss = self.manager.get_metric("ml_models", "training_loss").value
            new_loss = max(current_loss - random.uniform(0.01, 0.2), 0.1)
            self.manager.update_metric("ml_models", "training_loss", new_loss)
            
            # 模擬模型漂移
            drift = random.uniform(0.0, 0.4)
            self.manager.update_metric("ml_models", "model_drift_score", drift)
            
            # 模擬預測數
            predictions = random.randint(100, 1000)
            self.manager.increment_metric("ml_models", "predictions_per_minute", predictions / 60)


# ==================== 主演示函數 ====================

async def run_full_integration_demo():
    """
    運行完整集成演示
    
    展示所有監控系統同時運行
    """
    
    # 1. 初始化面板
    panel = UnifiedPanel(refresh_interval=1)
    
    # 2. 初始化擴展管理器
    manager = PanelExtensionManager(panel)
    
    # 3. 添加標準擴展集合
    create_standard_extension_set(manager)
    
    print("=" * 70)
    print("🌌 宇宙交易 AI - 統一面板系統")
    print("=" * 70)
    print("\n正在初始化監控系統...\n")
    
    # 4. 初始化各個監控系統
    arbitrage_monitor = ArbitrageStrategyMonitor(panel, manager)
    hft_monitor = HighFrequencyTradingMonitor(panel, manager)
    risk_monitor = RiskManagementMonitor(panel, manager)
    ml_monitor = MachineLearningMonitor(panel, manager)
    
    print("✅ 所有監控系統已初始化\n")
    print("已添加以下模塊:")
    print(f"  💰 套利策略 (arbitrage_strategy)")
    print(f"  ⚡ 高頻交易 (hft)")
    print(f"  🛡️  風險管理 (risk_management)")
    print(f"  🤖 機器學習 (ml_models)")
    print("\n" + "=" * 70)
    print("啟動實時儀表板... (按 Ctrl+C 退出)")
    print("=" * 70 + "\n")
    
    # 5. 創建非同步任務
    tasks = [
        asyncio.create_task(panel.start_live_display()),
        asyncio.create_task(arbitrage_monitor.simulate_price_updates()),
        asyncio.create_task(hft_monitor.simulate_hft_activity()),
        asyncio.create_task(risk_monitor.simulate_risk_metrics()),
        asyncio.create_task(ml_monitor.simulate_ml_training()),
    ]
    
    # 6. 定期檢查告警
    async def monitor_alerts():
        while panel.is_running:
            await asyncio.sleep(3)
            triggered = manager.check_alert_rules()
            for rule_name, level in triggered:
                panel.add_alert(f"{level.value} {rule_name}")
    
    tasks.append(asyncio.create_task(monitor_alerts()))
    
    # 7. 等待所有任務完成
    try:
        await asyncio.gather(*tasks)
    except KeyboardInterrupt:
        panel.stop_display()
        for task in tasks:
            task.cancel()


if __name__ == "__main__":
    asyncio.run(run_full_integration_demo())
