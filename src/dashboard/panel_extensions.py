#!/usr/bin/env python3
"""
面板擴展系統 (Panel Extension System)
宇宙交易 AI - 如何增加面板功能

提供簡單的 API 讓你快速添加：
1. 新的監控模塊
2. 自定義指標
3. 即時告警
4. 自定義渲染面板

使用範例：
    from src.dashboard.panel_extensions import PanelExtensionManager
    
    manager = PanelExtensionManager(panel)
    
    # 添加新模塊
    manager.add_custom_module("my_strategy", "策略引擎")
    
    # 添加自定義指標
    manager.add_custom_metric("win_streak", 5)
    
    # 添加告警規則
    manager.add_alert_rule("sharpe_below_1", lambda: panel.trade_metrics.sharpe_ratio < 1.0)
"""

import logging
from typing import Dict, List, Any, Callable, Optional
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
from rich.panel import Panel
from rich.table import Table
from rich.text import Text


# ==================== 擴展數據結構 ====================

class MetricType(Enum):
    """指標類型"""
    COUNTER = "計數器"           # 持續增加
    GAUGE = "儀表"               # 實時值
    HISTOGRAM = "直方圖"         # 分佈
    TIMER = "計時器"             # 耗時測量


class AlertLevel(Enum):
    """告警級別"""
    INFO = "ℹ️ 信息"
    WARNING = "⚠️ 警告"
    CRITICAL = "🔴 嚴重"
    RECOVERY = "✅ 恢復"


@dataclass
class CustomMetric:
    """自定義指標"""
    name: str                           # 指標名稱
    metric_type: MetricType            # 類型
    value: float = 0.0                 # 當前值
    description: str = ""              # 描述
    unit: str = ""                     # 單位
    history: List[float] = field(default_factory=list)  # 歷史值
    max_history: int = 100             # 最大歷史記錄數
    last_update: datetime = field(default_factory=datetime.now)
    
    def update(self, value: float) -> None:
        """更新指標"""
        self.value = value
        self.history.append(value)
        if len(self.history) > self.max_history:
            self.history = self.history[-self.max_history:]
        self.last_update = datetime.now()


@dataclass
class AlertRule:
    """告警規則"""
    name: str                          # 規則名稱
    condition: Callable[[], bool]      # 條件函數
    level: AlertLevel = AlertLevel.WARNING  # 級別
    enabled: bool = True               # 是否啟用
    triggered_count: int = 0           # 觸發次數
    last_triggered: Optional[datetime] = None  # 最後觸發時間


@dataclass
class CustomModule:
    """自定義監控模塊"""
    name: str                          # 模塊名稱
    display_name: str                  # 顯示名稱
    description: str = ""              # 描述
    status_text: str = "就緒"          # 狀態文本
    icon: str = "📦"                   # 圖標
    metrics: Dict[str, CustomMetric] = field(default_factory=dict)  # 模塊指標
    active: bool = True                # 是否活躍


# ==================== 擴展管理器 ====================

class PanelExtensionManager:
    """
    面板擴展管理器
    
    提供 API 添加自定義功能到統一面板
    
    使用範例:
        manager = PanelExtensionManager(panel)
        manager.add_custom_module("strategy", "交易策略")
        manager.add_custom_metric("strategy", "win_rate", MetricType.GAUGE, 0.65, "%")
    """
    
    def __init__(self, panel):
        """
        初始化擴展管理器
        
        Args:
            panel: UnifiedPanel 實例
        """
        self.panel = panel
        self.custom_modules: Dict[str, CustomModule] = {}
        self.custom_metrics: Dict[str, Dict[str, CustomMetric]] = {}
        self.alert_rules: Dict[str, AlertRule] = {}
        self.logger = logging.getLogger(__name__)
        
        self.logger.info("面板擴展管理器已初始化")
    
    # ==================== 模塊管理 ====================
    
    def add_custom_module(
        self,
        module_name: str,
        display_name: str,
        description: str = "",
        icon: str = "📦"
    ) -> CustomModule:
        """
        添加自定義監控模塊
        
        Args:
            module_name: 模塊內部名稱（英文）
            display_name: 顯示名稱（中文）
            description: 模塊描述
            icon: 圖標表情符號
            
        Returns:
            新建的 CustomModule
            
        Example:
            manager.add_custom_module(
                "arbitrage",
                "套利引擎",
                "實時跨交易所套利監控",
                icon="💰"
            )
        """
        if module_name in self.custom_modules:
            self.logger.warning(f"模塊 {module_name} 已存在，跳過添加")
            return self.custom_modules[module_name]
        
        module = CustomModule(
            name=module_name,
            display_name=display_name,
            description=description,
            icon=icon
        )
        
        self.custom_modules[module_name] = module
        self.custom_metrics[module_name] = {}
        
        self.logger.info(f"✅ 添加自定義模塊: {display_name} ({module_name})")
        self.panel.add_alert(f"✅ 模塊已添加: {icon} {display_name}")
        
        return module
    
    def get_custom_module(self, module_name: str) -> Optional[CustomModule]:
        """獲取自定義模塊"""
        return self.custom_modules.get(module_name)
    
    def update_module_status(self, module_name: str, status_text: str) -> None:
        """更新模塊狀態"""
        if module_name in self.custom_modules:
            self.custom_modules[module_name].status_text = status_text
    
    # ==================== 指標管理 ====================
    
    def add_custom_metric(
        self,
        module_name: str,
        metric_name: str,
        metric_type: MetricType = MetricType.GAUGE,
        initial_value: float = 0.0,
        unit: str = "",
        description: str = ""
    ) -> CustomMetric:
        """
        添加自定義指標到模塊
        
        Args:
            module_name: 所屬模塊名稱
            metric_name: 指標名稱
            metric_type: 指標類型
            initial_value: 初始值
            unit: 單位（如 "%", "ms", "$"）
            description: 描述
            
        Returns:
            新建的 CustomMetric
            
        Example:
            # 添加勝率指標
            manager.add_custom_metric(
                "arbitrage",
                "profit_per_trade",
                MetricType.GAUGE,
                100.5,
                "$",
                "每筆交易平均利潤"
            )
            
            # 添加執行次數計數器
            manager.add_custom_metric(
                "arbitrage",
                "execution_count",
                MetricType.COUNTER,
                0,
                "次"
            )
        """
        if module_name not in self.custom_modules:
            self.logger.error(f"模塊 {module_name} 不存在")
            return None
        
        metric = CustomMetric(
            name=metric_name,
            metric_type=metric_type,
            value=initial_value,
            unit=unit,
            description=description
        )
        
        self.custom_metrics[module_name][metric_name] = metric
        
        self.logger.info(
            f"✅ 添加指標: {metric_name} 到 {module_name} "
            f"(類型: {metric_type.value})"
        )
        
        return metric
    
    def update_metric(
        self,
        module_name: str,
        metric_name: str,
        value: float
    ) -> bool:
        """
        更新指標值
        
        Args:
            module_name: 模塊名稱
            metric_name: 指標名稱
            value: 新值
            
        Returns:
            是否更新成功
            
        Example:
            manager.update_metric("arbitrage", "profit_per_trade", 125.50)
        """
        if (module_name in self.custom_metrics and
            metric_name in self.custom_metrics[module_name]):
            
            metric = self.custom_metrics[module_name][metric_name]
            metric.update(value)
            return True
        
        self.logger.warning(
            f"指標不存在: {module_name}.{metric_name}"
        )
        return False
    
    def increment_metric(self, module_name: str, metric_name: str, amount: float = 1.0) -> bool:
        """增加指標值（適合計數器）"""
        if (module_name in self.custom_metrics and
            metric_name in self.custom_metrics[module_name]):
            
            metric = self.custom_metrics[module_name][metric_name]
            metric.update(metric.value + amount)
            return True
        
        return False
    
    def get_metric(self, module_name: str, metric_name: str) -> Optional[CustomMetric]:
        """獲取指標"""
        if module_name in self.custom_metrics:
            return self.custom_metrics[module_name].get(metric_name)
        return None
    
    # ==================== 告警規則管理 ====================
    
    def add_alert_rule(
        self,
        rule_name: str,
        condition: Callable[[], bool],
        level: AlertLevel = AlertLevel.WARNING,
        description: str = ""
    ) -> AlertRule:
        """
        添加告警規則
        
        Args:
            rule_name: 規則名稱
            condition: 條件函數（返回 True 時觸發告警）
            level: 告警級別
            description: 規則描述
            
        Returns:
            新建的 AlertRule
            
        Example:
            # Sharpe 比率低於 1.0 時告警
            manager.add_alert_rule(
                "low_sharpe",
                lambda: panel.trade_metrics.sharpe_ratio < 1.0,
                AlertLevel.WARNING,
                "Sharpe 比率低於目標值"
            )
            
            # 虧損超過 10% 時嚴重告警
            manager.add_alert_rule(
                "critical_loss",
                lambda: panel.trade_metrics.total_pnl < -10000,
                AlertLevel.CRITICAL,
                "單日虧損超過 $10,000"
            )
        """
        rule = AlertRule(
            name=rule_name,
            condition=condition,
            level=level
        )
        
        self.alert_rules[rule_name] = rule
        
        self.logger.info(
            f"✅ 添加告警規則: {rule_name} "
            f"(級別: {level.value})"
        )
        
        return rule
    
    def check_alert_rules(self) -> List[tuple]:
        """
        檢查所有告警規則
        
        Returns:
            觸發的告警列表 [(rule_name, level, message)]
        """
        triggered_alerts = []
        
        for rule_name, rule in self.alert_rules.items():
            if not rule.enabled:
                continue
            
            try:
                if rule.condition():
                    rule.triggered_count += 1
                    rule.last_triggered = datetime.now()
                    triggered_alerts.append((rule_name, rule.level))
                    
                    self.logger.warning(
                        f"{rule.level.value} 告警觸發: {rule_name}"
                    )
            except Exception as e:
                self.logger.error(
                    f"執行告警規則 {rule_name} 失敗: {e}"
                )
        
        return triggered_alerts
    
    # ==================== 渲染擴展面板 ====================
    
    def render_custom_modules_table(self) -> Table:
        """渲染自定義模塊表格"""
        table = Table(
            title="🧩 自定義模塊",
            show_header=True,
            header_style="bold cyan"
        )
        
        table.add_column("圖標", justify="center", width=3)
        table.add_column("模塊名稱", style="magenta")
        table.add_column("狀態", justify="center")
        table.add_column("指標數", justify="right")
        table.add_column("描述", style="dim")
        
        for module_name, module in sorted(self.custom_modules.items()):
            table.add_row(
                module.icon,
                module.display_name,
                module.status_text,
                str(len(self.custom_metrics.get(module_name, {}))),
                module.description[:30] + "..." if len(module.description) > 30 else module.description,
            )
        
        return table
    
    def render_custom_metrics_table(self) -> Table:
        """渲染自定義指標表格"""
        table = Table(
            title="📊 自定義指標",
            show_header=True,
            header_style="bold green"
        )
        
        table.add_column("模塊", style="magenta")
        table.add_column("指標名稱", style="cyan")
        table.add_column("值", justify="right")
        table.add_column("單位", justify="center")
        table.add_column("更新時間", style="dim")
        
        for module_name, metrics in sorted(self.custom_metrics.items()):
            for metric_name, metric in sorted(metrics.items()):
                time_ago = (datetime.now() - metric.last_update).total_seconds()
                time_str = f"{time_ago:.0f}s 前" if time_ago < 60 else "> 1分鐘"
                
                table.add_row(
                    module_name,
                    metric_name,
                    f"{metric.value:.2f}",
                    metric.unit,
                    time_str,
                )
        
        return table
    
    def render_alert_rules_table(self) -> Table:
        """渲染告警規則表格"""
        table = Table(
            title="🔔 告警規則",
            show_header=True,
            header_style="bold yellow"
        )
        
        table.add_column("規則名稱", style="cyan")
        table.add_column("級別", justify="center")
        table.add_column("狀態", justify="center")
        table.add_column("觸發次數", justify="right")
        table.add_column("最後觸發", style="dim")
        
        for rule_name, rule in sorted(self.alert_rules.items()):
            status = "✅ 啟用" if rule.enabled else "❌ 禁用"
            last_triggered = (
                rule.last_triggered.strftime("%H:%M:%S")
                if rule.last_triggered else "未觸發"
            )
            
            table.add_row(
                rule_name,
                rule.level.value,
                status,
                str(rule.triggered_count),
                last_triggered,
            )
        
        return table


# ==================== 便利函數 ====================

def create_standard_extension_set(manager: PanelExtensionManager) -> None:
    """
    創建標準擴展集合
    
    包含常用的模塊和指標
    """
    
    # 1. 套利引擎模塊
    manager.add_custom_module(
        "arbitrage",
        "套利引擎",
        "實時跨交易所價差監控和自動執行",
        icon="💰"
    )
    manager.add_custom_metric("arbitrage", "active_opportunities", MetricType.COUNTER, 0, "個", "活躍套利機會")
    manager.add_custom_metric("arbitrage", "avg_spread", MetricType.GAUGE, 0.0, "%", "平均價差")
    manager.add_custom_metric("arbitrage", "daily_profit", MetricType.COUNTER, 0, "$", "今日套利收益")
    
    # 2. 高頻交易模塊
    manager.add_custom_module(
        "hft",
        "高頻交易",
        "毫秒級訂單執行和市場微結構分析",
        icon="⚡"
    )
    manager.add_custom_metric("hft", "orders_per_second", MetricType.GAUGE, 0, "筆/秒", "每秒訂單數")
    manager.add_custom_metric("hft", "latency_ms", MetricType.TIMER, 0, "ms", "訂單延遲")
    manager.add_custom_metric("hft", "fill_rate", MetricType.GAUGE, 0.0, "%", "成交率")
    
    # 3. 風險管理模塊
    manager.add_custom_module(
        "risk",
        "風險管理",
        "多層風險控制和動態倉位調整",
        icon="🛡️"
    )
    manager.add_custom_metric("risk", "position_limit_used", MetricType.GAUGE, 0.0, "%", "倉位限制使用率")
    manager.add_custom_metric("risk", "var_95", MetricType.GAUGE, 0.0, "$", "95% VaR")
    manager.add_custom_metric("risk", "corr_matrix_updated", MetricType.COUNTER, 0, "次", "相關矩陣更新次數")
    
    # 4. 機器學習模塊
    manager.add_custom_module(
        "ml",
        "機器學習",
        "深度學習策略和強化學習優化",
        icon="🤖"
    )
    manager.add_custom_metric("ml", "model_accuracy", MetricType.GAUGE, 0.0, "%", "模型精度")
    manager.add_custom_metric("ml", "training_loss", MetricType.GAUGE, 0.0, "", "訓練損失")
    manager.add_custom_metric("ml", "predictions_per_minute", MetricType.COUNTER, 0, "個/分", "每分鐘預測數")
    
    # 5. 量子計算模塊
    manager.add_custom_module(
        "quantum",
        "量子計算",
        "量子優化算法和模擬",
        icon="⚛️"
    )
    manager.add_custom_metric("quantum", "circuit_depth", MetricType.GAUGE, 0, "層", "量子電路深度")
    manager.add_custom_metric("quantum", "coherence_time", MetricType.GAUGE, 0.0, "μs", "相幹時間")
    manager.add_custom_metric("quantum", "optimization_iterations", MetricType.COUNTER, 0, "次", "優化迭代次數")


# ==================== 演示範例 ====================

def demo_extension_manager():
    """
    演示如何使用面板擴展管理器
    """
    from src.dashboard.unified_panel import UnifiedPanel
    
    # 創建面板
    panel = UnifiedPanel()
    
    # 創建擴展管理器
    manager = PanelExtensionManager(panel)
    
    # 方式 1: 手動添加單個模塊
    print("=" * 50)
    print("方式 1: 手動添加單個模塊")
    print("=" * 50)
    
    manager.add_custom_module(
        "my_strategy",
        "我的策略",
        "自定義交易策略",
        icon="🎯"
    )
    
    manager.add_custom_metric(
        "my_strategy",
        "win_rate",
        MetricType.GAUGE,
        0.65,
        "%",
        "勝率"
    )
    
    manager.update_metric("my_strategy", "win_rate", 0.72)
    
    # 方式 2: 添加告警規則
    print("\n" + "=" * 50)
    print("方式 2: 添加告警規則")
    print("=" * 50)
    
    manager.add_alert_rule(
        "high_win_rate",
        lambda: manager.get_metric("my_strategy", "win_rate").value > 0.70,
        AlertLevel.INFO,
        "勝率高於 70%"
    )
    
    # 方式 3: 一次性添加標準擴展集合
    print("\n" + "=" * 50)
    print("方式 3: 添加標準擴展集合")
    print("=" * 50)
    
    create_standard_extension_set(manager)
    
    # 顯示結果
    print("\n✅ 已添加模塊:")
    for name, module in manager.custom_modules.items():
        print(f"  {module.icon} {module.display_name} ({name})")
    
    print("\n✅ 已添加指標:")
    for module_name, metrics in manager.custom_metrics.items():
        print(f"  {module_name}: {len(metrics)} 個指標")
    
    print("\n✅ 已添加告警規則:")
    for rule_name, rule in manager.alert_rules.items():
        print(f"  {rule_name} ({rule.level.value})")


if __name__ == "__main__":
    demo_extension_manager()
