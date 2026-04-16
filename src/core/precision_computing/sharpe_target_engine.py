#!/usr/bin/env python3
"""
Sharpe Target Engine - Phase 3
夏普目標引擎 - 第3階段

Captures and optimizes high Sharpe ratio periods through:
- Real-time Sharpe ratio calculation
- Target Sharpe threshold detection
- Dynamic position sizing based on Sharpe
- Confidence-based leverage adjustment
"""

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
from enum import Enum
import numpy as np
from collections import deque

logger = logging.getLogger(__name__)


class SharpeLevel(Enum):
    """分類 Sharpe 比率水平"""
    CRITICAL = "critical"  # Sharpe < 0 (虧損)
    POOR = "poor"  # 0 <= Sharpe < 0.5
    FAIR = "fair"  # 0.5 <= Sharpe < 1.0
    GOOD = "good"  # 1.0 <= Sharpe < 2.0
    EXCELLENT = "excellent"  # 2.0 <= Sharpe < 2.5
    EXCEPTIONAL = "exceptional"  # Sharpe >= 2.5 (奇點候選)


class TargetStrategy(Enum):
    """目標策略類型"""
    CONSERVATIVE = "conservative"  # 保守: 0.7x 槓桿, Sharpe > 1.0
    BALANCED = "balanced"  # 平衡: 1.0x 槓桿, Sharpe > 1.5
    AGGRESSIVE = "aggressive"  # 激進: 1.5x 槓桿, Sharpe > 2.0
    SINGULARITY = "singularity"  # 奇點: 2.0x+ 槓桿, Sharpe > 2.5


@dataclass
class SharpeMetrics:
    """Sharpe 相關指標集合"""
    sharpe_ratio: float
    annual_return: float
    volatility: float
    max_drawdown: float
    win_rate: float
    profit_factor: float
    return_std: float
    return_mean: float
    timestamp: datetime = field(default_factory=datetime.now)

    def get_level(self) -> SharpeLevel:
        """判斷 Sharpe 水平"""
        if self.sharpe_ratio < 0:
            return SharpeLevel.CRITICAL
        elif self.sharpe_ratio < 0.5:
            return SharpeLevel.POOR
        elif self.sharpe_ratio < 1.0:
            return SharpeLevel.FAIR
        elif self.sharpe_ratio < 2.0:
            return SharpeLevel.GOOD
        elif self.sharpe_ratio < 2.5:
            return SharpeLevel.EXCELLENT
        else:
            return SharpeLevel.EXCEPTIONAL

    def is_target_worthy(self, threshold: float = 2.0) -> bool:
        """檢查是否值得提升目標"""
        return self.sharpe_ratio >= threshold


@dataclass
class PositionTarget:
    """位置目標定義"""
    symbol: str
    target_quantity: float
    target_leverage: float
    confidence: float
    sharpe_based: bool
    timestamp: datetime = field(default_factory=datetime.now)


class SharpeCalculator:
    """Sharpe 比率計算引擎"""

    def __init__(self, risk_free_rate: float = 0.02, lookback_periods: int = 252):
        """
        初始化 Sharpe 計算器

        Args:
            risk_free_rate: 無風險利率 (年度)
            lookback_periods: 回望期 (預設 252 個交易日)
        """
        self.risk_free_rate = risk_free_rate
        self.lookback_periods = lookback_periods
        self.daily_rf_rate = risk_free_rate / 252

    def calculate_sharpe(
        self,
        returns: List[float],
        risk_free_rate: Optional[float] = None
    ) -> float:
        """
        計算 Sharpe 比率

        Args:
            returns: 收益率列表
            risk_free_rate: 可選的無風險利率覆蓋

        Returns:
            Sharpe 比率
        """
        if len(returns) < 2:
            return 0.0

        returns_array = np.array(returns)
        rf = risk_free_rate if risk_free_rate is not None else self.daily_rf_rate

        mean_return = np.mean(returns_array)
        std_return = np.std(returns_array)

        if std_return == 0:
            return 0.0

        sharpe = (mean_return - rf) / std_return
        return float(sharpe)

    def calculate_annual_return(
        self,
        returns: List[float],
        periods_per_year: int = 252
    ) -> float:
        """計算年化收益率"""
        if len(returns) == 0:
            return 0.0
        cum_return = np.prod([1 + r for r in returns]) - 1
        years = len(returns) / periods_per_year
        if years == 0:
            return 0.0
        annual = (1 + cum_return) ** (1 / years) - 1
        return float(annual)

    def calculate_volatility(self, returns: List[float]) -> float:
        """計算年化波動率"""
        if len(returns) == 0:
            return 0.0
        return float(np.std(returns) * np.sqrt(252))

    def calculate_max_drawdown(self, returns: List[float]) -> float:
        """計算最大回撤"""
        if len(returns) == 0:
            return 0.0

        cum_returns = np.cumprod([1 + r for r in returns])
        running_max = np.maximum.accumulate(cum_returns)
        drawdown = (cum_returns - running_max) / running_max
        return float(np.min(drawdown))

    def calculate_metrics(
        self,
        returns: List[float],
        wins: List[bool]
    ) -> SharpeMetrics:
        """
        計算完整 Sharpe 相關指標

        Args:
            returns: 收益率列表
            wins: 勝負列表

        Returns:
            SharpeMetrics 物件
        """
        sharpe = self.calculate_sharpe(returns)
        annual_return = self.calculate_annual_return(returns)
        volatility = self.calculate_volatility(returns)
        max_drawdown = self.calculate_max_drawdown(returns)

        win_rate = np.mean(wins) if len(wins) > 0 else 0.0
        profit_factor = self._calculate_profit_factor(returns, wins)

        return SharpeMetrics(
            sharpe_ratio=sharpe,
            annual_return=annual_return,
            volatility=volatility,
            max_drawdown=max_drawdown,
            win_rate=float(win_rate),
            profit_factor=profit_factor,
            return_std=float(np.std(returns)) if len(returns) > 0 else 0.0,
            return_mean=float(np.mean(returns)) if len(returns) > 0 else 0.0
        )

    def _calculate_profit_factor(
        self,
        returns: List[float],
        wins: List[bool]
    ) -> float:
        """計算利潤因子"""
        if len(returns) == 0 or len(wins) == 0:
            return 0.0

        returns_array = np.array(returns)
        wins_array = np.array(wins)

        profits = returns_array[wins_array]
        losses = returns_array[~wins_array]

        total_profit = np.sum(profits) if len(profits) > 0 else 0.0
        total_loss = -np.sum(losses) if len(losses) > 0 else 0.0

        if total_loss == 0:
            return float('inf') if total_profit > 0 else 0.0

        return float(total_profit / total_loss)


class SharpeTargetDetector:
    """Sharpe 目標偵測引擎"""

    def __init__(self, window_size: int = 20):
        """
        初始化偵測器

        Args:
            window_size: 滑動視窗大小 (交易數)
        """
        self.window_size = window_size
        self.metrics_history: deque = deque(maxlen=window_size)
        self.peak_sharpe = 0.0
        self.peak_timestamp = datetime.now()
        self.above_threshold_count = 0
        self.threshold = 2.0  # 奇點閾值

    def add_metrics(self, metrics: SharpeMetrics) -> None:
        """記錄新指標"""
        self.metrics_history.append(metrics)

        # 追蹤峰值 Sharpe
        if metrics.sharpe_ratio > self.peak_sharpe:
            self.peak_sharpe = metrics.sharpe_ratio
            self.peak_timestamp = metrics.timestamp

        # 計算高於閾值的次數
        if metrics.sharpe_ratio >= self.threshold:
            self.above_threshold_count += 1

    def detect_singularity_period(self) -> bool:
        """
        檢測是否在奇點期間

        奇點期間定義: Sharpe >= 2.5 且持續性高 (70% 以上)

        Returns:
            是否檢測到奇點期間
        """
        if len(self.metrics_history) < self.window_size:
            return False

        recent_sharpe = [m.sharpe_ratio for m in self.metrics_history]
        above_threshold = sum(1 for s in recent_sharpe if s >= self.threshold)
        persistence = above_threshold / len(recent_sharpe)

        return persistence >= 0.7

    def detect_regime_change(self) -> bool:
        """
        偵測 Sharpe 制度變化

        Returns:
            是否檢測到重大變化
        """
        if len(self.metrics_history) < 2:
            return False

        recent = self.metrics_history[-1].sharpe_ratio
        previous = self.metrics_history[-2].sharpe_ratio

        change_magnitude = abs(recent - previous) / (abs(previous) + 1e-6)
        return change_magnitude > 0.5  # 50% 以上變化

    def get_target_strategy(self) -> TargetStrategy:
        """
        根據目前 Sharpe 推薦策略

        Returns:
            建議的目標策略
        """
        if len(self.metrics_history) == 0:
            return TargetStrategy.CONSERVATIVE

        current_sharpe = self.metrics_history[-1].sharpe_ratio

        if current_sharpe >= 2.5:
            return TargetStrategy.SINGULARITY
        elif current_sharpe >= 2.0:
            return TargetStrategy.AGGRESSIVE
        elif current_sharpe >= 1.5:
            return TargetStrategy.BALANCED
        else:
            return TargetStrategy.CONSERVATIVE

    def get_target_leverage(self, strategy: TargetStrategy) -> float:
        """根據策略取得目標槓桿"""
        leverage_map = {
            TargetStrategy.CONSERVATIVE: 0.7,
            TargetStrategy.BALANCED: 1.0,
            TargetStrategy.AGGRESSIVE: 1.5,
            TargetStrategy.SINGULARITY: 2.0
        }
        return leverage_map.get(strategy, 1.0)

    def get_confidence(self) -> float:
        """
        計算目前 Sharpe 目標的信心度 (0-1)

        Returns:
            信心度分數
        """
        if len(self.metrics_history) == 0:
            return 0.0

        current_sharpe = self.metrics_history[-1].sharpe_ratio
        peak_distance = current_sharpe / (self.peak_sharpe + 1e-6)

        # 信心度基於: 1) 相對於峰值的位置, 2) 持續時間
        persistence_factor = min(len(self.metrics_history) / self.window_size, 1.0)
        sharpe_factor = peak_distance * 0.8 + 0.2

        confidence = min(sharpe_factor * persistence_factor, 1.0)
        return float(max(confidence, 0.0))


class PositionSizer:
    """位置大小計算引擎 (基於 Sharpe)"""

    def __init__(self, base_position_size: float = 1000.0):
        """
        初始化位置計算器

        Args:
            base_position_size: 基礎位置大小 (美元)
        """
        self.base_position_size = base_position_size

    def calculate_position(
        self,
        sharpe_metrics: SharpeMetrics,
        target_leverage: float,
        confidence: float,
        max_leverage: float = 3.0
    ) -> Tuple[float, float]:
        """
        計算目標位置大小和槓桿

        Args:
            sharpe_metrics: Sharpe 指標
            target_leverage: 目標槓桿
            confidence: 信心度
            max_leverage: 最大槓桿限制

        Returns:
            (位置大小, 實際槓桿)
        """
        # 基於 Sharpe 調整位置
        sharpe_factor = min(sharpe_metrics.sharpe_ratio / 3.0, 1.0)
        sharpe_factor = max(sharpe_factor, 0.1)

        # 基於波動率調整
        volatility_factor = 1.0 / (sharpe_metrics.volatility + 1e-6)
        volatility_factor = min(volatility_factor, 5.0)  # 最多 5x

        # 信心度調整
        adjusted_leverage = target_leverage * confidence

        # 應用限制
        adjusted_leverage = min(adjusted_leverage, max_leverage)
        adjusted_leverage = max(adjusted_leverage, 0.1)

        # 計算位置
        position_size = self.base_position_size * sharpe_factor * volatility_factor * adjusted_leverage

        return position_size, adjusted_leverage

    def calculate_dynamic_position(
        self,
        current_sharpe: float,
        volatility: float,
        previous_sharpe: float,
        trend: int = 1
    ) -> Tuple[float, str]:
        """
        計算動態位置 (考慮 Sharpe 趨勢)

        Args:
            current_sharpe: 當前 Sharpe
            volatility: 波動率
            previous_sharpe: 前期 Sharpe
            trend: 趨勢方向 (1: 上升, -1: 下降)

        Returns:
            (調整位置, 調整理由)
        """
        base_position = self.base_position_size

        # 趨勢因子
        if trend > 0 and current_sharpe > previous_sharpe:
            # 上升趨勢且 Sharpe 改善 -> 增加位置
            trend_factor = 1.2
            reason = "uptrend_sharpe_improvement"
        elif trend < 0 or current_sharpe < previous_sharpe:
            # 下降趨勢或 Sharpe 惡化 -> 減少位置
            trend_factor = 0.8
            reason = "downtrend_or_sharpe_deterioration"
        else:
            trend_factor = 1.0
            reason = "neutral_trend"

        # 波動率因子
        volatility_factor = 1.0 / (volatility + 0.1)
        volatility_factor = min(volatility_factor, 3.0)

        adjusted_position = base_position * trend_factor * volatility_factor

        return adjusted_position, reason


class SharpeTargetEngine:
    """Phase 3 Sharpe 目標引擎 - 核心系統"""

    def __init__(
        self,
        base_position_size: float = 1000.0,
        risk_free_rate: float = 0.02,
        sharpe_threshold: float = 2.0
    ):
        """
        初始化 Sharpe 目標引擎

        Args:
            base_position_size: 基礎位置大小
            risk_free_rate: 無風險利率
            sharpe_threshold: Sharpe 奇點閾值
        """
        self.calculator = SharpeCalculator(risk_free_rate=risk_free_rate)
        self.detector = SharpeTargetDetector(window_size=20)
        self.position_sizer = PositionSizer(base_position_size)

        self.sharpe_threshold = sharpe_threshold
        self.current_targets: Dict[str, PositionTarget] = {}
        self.metrics_history: List[SharpeMetrics] = []
        self.singularity_periods: List[Tuple[datetime, datetime]] = []
        self.logger = logging.getLogger(self.__class__.__name__)

    def process_returns(
        self,
        returns: List[float],
        wins: List[bool],
        symbol: str = "PORTFOLIO"
    ) -> SharpeMetrics:
        """
        處理收益數據並計算指標

        Args:
            returns: 收益列表
            wins: 勝負列表
            symbol: 交易對代碼

        Returns:
            SharpeMetrics 物件
        """
        metrics = self.calculator.calculate_metrics(returns, wins)
        self.detector.add_metrics(metrics)
        self.metrics_history.append(metrics)

        level = metrics.get_level()
        self.logger.info(
            f"Sharpe metrics for {symbol}: ratio={metrics.sharpe_ratio:.2f}, "
            f"level={level.value}, annual_return={metrics.annual_return:.2%}"
        )

        return metrics

    def update_position_targets(
        self,
        current_metrics: SharpeMetrics,
        symbols: List[str]
    ) -> Dict[str, PositionTarget]:
        """
        根據當前 Sharpe 更新位置目標

        Args:
            current_metrics: 當前 Sharpe 指標
            symbols: 交易對列表

        Returns:
            更新的位置目標字典
        """
        strategy = self.detector.get_target_strategy()
        target_leverage = self.detector.get_target_leverage(strategy)
        confidence = self.detector.get_confidence()

        position_size, actual_leverage = self.position_sizer.calculate_position(
            current_metrics,
            target_leverage,
            confidence
        )

        self.current_targets.clear()

        for symbol in symbols:
            # 根據每個交易對分配位置
            symbol_portion = position_size / len(symbols) if symbols else 0
            target_quantity = symbol_portion / current_metrics.volatility if current_metrics.volatility > 0 else symbol_portion

            target = PositionTarget(
                symbol=symbol,
                target_quantity=target_quantity,
                target_leverage=actual_leverage,
                confidence=confidence,
                sharpe_based=True
            )
            self.current_targets[symbol] = target

        self.logger.info(
            f"Updated position targets: strategy={strategy.value}, "
            f"leverage={actual_leverage:.2f}, confidence={confidence:.2%}"
        )

        return self.current_targets

    def check_singularity_entry(self) -> bool:
        """
        檢查是否進入奇點期間

        Returns:
            是否偵測到奇點期間
        """
        is_singularity = self.detector.detect_singularity_period()

        if is_singularity:
            now = datetime.now()
            self.singularity_periods.append((now, None))
            self.logger.warning("⭐ SINGULARITY PERIOD DETECTED! Sharpe >= 2.5")

        return is_singularity

    def check_regime_change(self) -> Tuple[bool, Optional[str]]:
        """
        檢查 Sharpe 制度變化

        Returns:
            (是否檢測到變化, 變化類型描述)
        """
        if not self.detector.detect_regime_change():
            return False, None

        current_strategy = self.detector.get_target_strategy()
        change_desc = f"Sharpe regime changed to {current_strategy.value}"
        self.logger.info(f"🔄 {change_desc}")

        return True, change_desc

    def get_current_status(self) -> Dict[str, Any]:
        """
        取得引擎目前狀態

        Returns:
            狀態字典
        """
        if len(self.metrics_history) == 0:
            return {
                "status": "no_data",
                "sharpe_ratio": 0.0,
                "strategy": "unknown",
                "targets_count": 0
            }

        latest = self.metrics_history[-1]
        strategy = self.detector.get_target_strategy()
        is_singularity = self.detector.detect_singularity_period()

        return {
            "status": "active",
            "sharpe_ratio": latest.sharpe_ratio,
            "level": latest.get_level().value,
            "strategy": strategy.value,
            "confidence": self.detector.get_confidence(),
            "is_singularity": is_singularity,
            "targets_count": len(self.current_targets),
            "peak_sharpe": self.detector.peak_sharpe,
            "annual_return": latest.annual_return,
            "volatility": latest.volatility,
            "max_drawdown": latest.max_drawdown,
            "win_rate": latest.win_rate,
            "timestamp": latest.timestamp.isoformat()
        }

    def reset(self) -> None:
        """重設引擎狀態"""
        self.detector = SharpeTargetDetector(window_size=20)
        self.current_targets.clear()
        self.metrics_history.clear()
        self.singularity_periods.clear()
        self.logger.info("✅ Sharpe Target Engine reset")
