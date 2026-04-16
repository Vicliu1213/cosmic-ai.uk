#!/usr/bin/env python3
"""
Dynamic Risk Management Engine - Phase 3
動態風險管理引擎 - 第3階段

Provides adaptive risk management through:
- Real-time drawdown monitoring
- Dynamic position sizing based on risk
- Leverage adjustment for changing volatility
- Stop-loss and take-profit optimization
"""

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
from enum import Enum
import numpy as np
from collections import deque

logger = logging.getLogger(__name__)


class RiskLevel(Enum):
    """風險等級分類"""
    LOW = "low"  # < 5% 回撤
    MODERATE = "moderate"  # 5-10% 回撤
    ELEVATED = "elevated"  # 10-15% 回撤
    HIGH = "high"  # 15-25% 回撤
    CRITICAL = "critical"  # > 25% 回撤


class LeverageAdjustmentMode(Enum):
    """槓桿調整模式"""
    CONSERVATIVE = "conservative"  # 1/3 目標槓桿
    NORMAL = "normal"  # 標準槓桿
    AGGRESSIVE = "aggressive"  # 1.5x 目標槓桿
    SINGULARITY = "singularity"  # 2x+ 目標槓桿


@dataclass
class RiskMetrics:
    """風險相關指標集合"""
    current_drawdown: float  # 當前回撤
    max_drawdown: float  # 最大歷史回撤
    drawdown_recovery_rate: float  # 回撤恢復速度
    volatility: float  # 當前波動率
    var_95: float  # Value at Risk (95%)
    cvar_95: float  # Conditional VaR (95%)
    risk_level: RiskLevel = field(default=RiskLevel.MODERATE)
    timestamp: datetime = field(default_factory=datetime.now)

    def get_risk_score(self) -> float:
        """計算綜合風險評分 (0-1)"""
        dd_factor = min(abs(self.current_drawdown), 0.3) / 0.3  # 0-1
        vol_factor = min(self.volatility, 0.5) / 0.5  # 0-1
        var_factor = min(self.var_95, 0.1) / 0.1  # 0-1

        score = (dd_factor * 0.5 + vol_factor * 0.3 + var_factor * 0.2)
        return min(score, 1.0)


@dataclass
class PositionRiskLimit:
    """位置風險限制"""
    symbol: str
    max_position_size: float
    max_leverage: float
    stop_loss_pct: float
    take_profit_pct: float
    max_loss_per_trade: float
    max_portfolio_loss_pct: float


class DrawdownMonitor:
    """回撤監控引擎"""

    def __init__(self, window_size: int = 100):
        """
        初始化回撤監控器

        Args:
            window_size: 歷史價值記錄窗口
        """
        self.window_size = window_size
        self.portfolio_values: deque = deque(maxlen=window_size)
        self.peak_value = 0.0
        self.current_drawdown = 0.0
        self.max_drawdown = 0.0
        self.recovery_start = None
        self.recovery_duration = timedelta()

    def update(self, portfolio_value: float) -> Dict[str, float]:
        """
        更新投資組合價值並計算回撤

        Args:
            portfolio_value: 當前投資組合價值

        Returns:
            回撤指標字典
        """
        self.portfolio_values.append(portfolio_value)

        # 更新峰值
        if portfolio_value > self.peak_value:
            self.peak_value = portfolio_value
            self.recovery_start = None

        # 計算當前回撤
        self.current_drawdown = (portfolio_value - self.peak_value) / self.peak_value if self.peak_value > 0 else 0.0

        # 更新最大回撤
        if self.current_drawdown < self.max_drawdown:
            self.max_drawdown = self.current_drawdown

        # 檢查恢復
        if abs(self.current_drawdown) < 0.01:  # 接近 0%
            if self.recovery_start is None:
                self.recovery_start = datetime.now()
            self.recovery_duration = datetime.now() - self.recovery_start

        return {
            "current_drawdown": self.current_drawdown,
            "max_drawdown": self.max_drawdown,
            "peak_value": self.peak_value,
            "recovery_duration_hours": self.recovery_duration.total_seconds() / 3600
        }

    def get_drawdown_level(self) -> RiskLevel:
        """根據回撤判斷風險等級"""
        dd = abs(self.current_drawdown)

        if dd < 0.05:
            return RiskLevel.LOW
        elif dd < 0.10:
            return RiskLevel.MODERATE
        elif dd < 0.15:
            return RiskLevel.ELEVATED
        elif dd < 0.25:
            return RiskLevel.HIGH
        else:
            return RiskLevel.CRITICAL

    def reset(self) -> None:
        """重設監控器"""
        self.portfolio_values.clear()
        self.peak_value = 0.0
        self.current_drawdown = 0.0
        self.max_drawdown = 0.0
        self.recovery_start = None


class VolatilityAdjuster:
    """波動率調整引擎"""

    def __init__(self, lookback_periods: int = 20):
        """
        初始化波動率調整器

        Args:
            lookback_periods: 波動率計算周期
        """
        self.lookback_periods = lookback_periods
        self.returns_history: deque = deque(maxlen=lookback_periods)
        self.volatility = 0.0
        self.volatility_regime = "normal"

    def update(self, return_value: float) -> float:
        """
        更新收益並計算波動率

        Args:
            return_value: 週期收益率

        Returns:
            當前波動率
        """
        self.returns_history.append(return_value)

        if len(self.returns_history) >= 2:
            self.volatility = float(np.std(self.returns_history))

        # 判斷波動率制度
        if self.volatility < 0.01:
            self.volatility_regime = "low"
        elif self.volatility < 0.03:
            self.volatility_regime = "normal"
        elif self.volatility < 0.06:
            self.volatility_regime = "elevated"
        else:
            self.volatility_regime = "high"

        return self.volatility

    def get_volatility_adjustment(self) -> float:
        """
        根據波動率制度取得槓桿調整因子

        Returns:
            調整因子 (< 1.0 表示降低槓桿)
        """
        adjustment_map = {
            "low": 1.1,  # 低波動 -> 增加槓桿
            "normal": 1.0,  # 正常波動 -> 標準槓桿
            "elevated": 0.8,  # 高波動 -> 降低槓桿
            "high": 0.5  # 非常高波動 -> 大幅降低槓桿
        }
        return adjustment_map.get(self.volatility_regime, 1.0)

    def reset(self) -> None:
        """重設調整器"""
        self.returns_history.clear()
        self.volatility = 0.0


class VaRCalculator:
    """風險值 (VaR) 計算引擎"""

    def __init__(self, confidence_level: float = 0.95, lookback_periods: int = 100):
        """
        初始化 VaR 計算器

        Args:
            confidence_level: 信心度 (預設 95%)
            lookback_periods: 歷史回望期
        """
        self.confidence_level = confidence_level
        self.lookback_periods = lookback_periods
        self.returns_history: deque = deque(maxlen=lookback_periods)

    def update(self, return_value: float) -> None:
        """更新收益歷史"""
        self.returns_history.append(return_value)

    def calculate_var(self) -> float:
        """
        計算 VaR (參數法)

        Returns:
            VaR 值
        """
        if len(self.returns_history) < 2:
            return 0.0

        returns_array = np.array(self.returns_history)
        mean_return = np.mean(returns_array)
        std_return = np.std(returns_array)

        # 正態分佈下的 VaR
        z_score = np.percentile(returns_array, (1 - self.confidence_level) * 100)
        var = mean_return - z_score * std_return

        return float(max(var, 0.0))

    def calculate_cvar(self) -> float:
        """
        計算條件 VaR (CVaR/Expected Shortfall)

        Returns:
            CVaR 值
        """
        if len(self.returns_history) < 2:
            return 0.0

        returns_array = np.array(self.returns_history)
        var = self.calculate_var()

        # 低於 VaR 的平均損失
        losses = returns_array[returns_array < -var]

        if len(losses) == 0:
            return var

        cvar = np.mean(losses)
        return float(abs(cvar))

    def reset(self) -> None:
        """重設計算器"""
        self.returns_history.clear()


class LeverageController:
    """槓桿控制引擎"""

    def __init__(self, max_leverage: float = 3.0, min_leverage: float = 0.1):
        """
        初始化槓桿控制器

        Args:
            max_leverage: 最大槓桿
            min_leverage: 最小槓桿
        """
        self.max_leverage = max_leverage
        self.min_leverage = min_leverage
        self.current_leverage = 1.0
        self.leverage_history: deque = deque(maxlen=50)

    def adjust_leverage(
        self,
        target_leverage: float,
        risk_level: RiskLevel,
        volatility_adjustment: float,
        sharpe_ratio: Optional[float] = None
    ) -> Tuple[float, str]:
        """
        根據風險等級調整槓桿

        Args:
            target_leverage: 目標槓桿
            risk_level: 當前風險等級
            volatility_adjustment: 波動率調整因子
            sharpe_ratio: 可選的 Sharpe 比率

        Returns:
            (調整後槓桿, 調整理由)
        """
        # 基於風險等級的調整
        risk_adjustment_map = {
            RiskLevel.LOW: 1.2,
            RiskLevel.MODERATE: 1.0,
            RiskLevel.ELEVATED: 0.8,
            RiskLevel.HIGH: 0.5,
            RiskLevel.CRITICAL: 0.2
        }
        risk_adjustment = risk_adjustment_map.get(risk_level, 1.0)

        # 計算調整後的槓桿
        adjusted_leverage = target_leverage * risk_adjustment * volatility_adjustment

        # 應用 Sharpe 比率調整 (如果提供)
        if sharpe_ratio is not None:
            if sharpe_ratio > 2.5:
                sharpe_adjustment = 1.2  # 高 Sharpe -> 增加槓桿
            elif sharpe_ratio > 2.0:
                sharpe_adjustment = 1.1
            elif sharpe_ratio > 1.5:
                sharpe_adjustment = 1.0
            elif sharpe_ratio > 1.0:
                sharpe_adjustment = 0.9
            else:
                sharpe_adjustment = 0.7

            adjusted_leverage *= sharpe_adjustment

        # 應用限制
        adjusted_leverage = max(adjusted_leverage, self.min_leverage)
        adjusted_leverage = min(adjusted_leverage, self.max_leverage)

        # 記錄歷史
        self.leverage_history.append(adjusted_leverage)
        self.current_leverage = adjusted_leverage

        reason = f"risk={risk_level.value}, vol_adj={volatility_adjustment:.2f}"
        if sharpe_ratio is not None:
            reason += f", sharpe={sharpe_ratio:.2f}"

        return adjusted_leverage, reason

    def get_leverage_trend(self) -> Tuple[float, str]:
        """
        分析槓桿趨勢

        Returns:
            (平均槓桿變化, 趨勢描述)
        """
        if len(self.leverage_history) < 2:
            return 0.0, "insufficient_data"

        recent = list(self.leverage_history)[-10:]
        avg_recent = np.mean(recent)
        avg_previous = np.mean(list(self.leverage_history)[:-10]) if len(self.leverage_history) > 10 else recent[0]

        change = (avg_recent - avg_previous) / avg_previous if avg_previous > 0 else 0.0

        if change > 0.1:
            trend = "increasing"
        elif change < -0.1:
            trend = "decreasing"
        else:
            trend = "stable"

        return float(change), trend

    def reset(self) -> None:
        """重設控制器"""
        self.leverage_history.clear()
        self.current_leverage = 1.0


class DynamicRiskManagementEngine:
    """Phase 3 動態風險管理引擎 - 核心系統"""

    def __init__(
        self,
        max_leverage: float = 3.0,
        max_portfolio_loss_pct: float = 0.15,
        drawdown_recovery_target: float = 0.05
    ):
        """
        初始化動態風險管理引擎

        Args:
            max_leverage: 最大槓桿
            max_portfolio_loss_pct: 最大投資組合損失 (%)
            drawdown_recovery_target: 回撤恢復目標
        """
        self.drawdown_monitor = DrawdownMonitor(window_size=100)
        self.volatility_adjuster = VolatilityAdjuster(lookback_periods=20)
        self.var_calculator = VaRCalculator(confidence_level=0.95, lookback_periods=100)
        self.leverage_controller = LeverageController(max_leverage=max_leverage)

        self.max_portfolio_loss_pct = max_portfolio_loss_pct
        self.drawdown_recovery_target = drawdown_recovery_target
        self.position_limits: Dict[str, PositionRiskLimit] = {}
        self.active_stops: Dict[str, Dict[str, float]] = {}  # symbol -> {stop_loss, take_profit}

        self.logger = logging.getLogger(self.__class__.__name__)

    def process_portfolio_update(
        self,
        portfolio_value: float,
        return_value: float
    ) -> RiskMetrics:
        """
        處理投資組合更新並計算風險指標

        Args:
            portfolio_value: 當前投資組合價值
            return_value: 本期收益率

        Returns:
            RiskMetrics 物件
        """
        # 更新各個監控器
        drawdown_info = self.drawdown_monitor.update(portfolio_value)
        volatility = self.volatility_adjuster.update(return_value)
        self.var_calculator.update(return_value)

        # 計算 VaR 和 CVaR
        var_95 = self.var_calculator.calculate_var()
        cvar_95 = self.var_calculator.calculate_cvar()

        # 計算回撤恢復速度
        recovery_rate = 1.0 - abs(drawdown_info["current_drawdown"]) if drawdown_info["current_drawdown"] < 0 else 1.0

        # 判斷風險等級
        risk_level = self.drawdown_monitor.get_drawdown_level()

        metrics = RiskMetrics(
            current_drawdown=drawdown_info["current_drawdown"],
            max_drawdown=drawdown_info["max_drawdown"],
            drawdown_recovery_rate=recovery_rate,
            volatility=volatility,
            var_95=var_95,
            cvar_95=cvar_95,
            risk_level=risk_level
        )

        self.logger.debug(
            f"Risk metrics: drawdown={metrics.current_drawdown:.2%}, "
            f"level={risk_level.value}, volatility={volatility:.4f}"
        )

        return metrics

    def calculate_adjusted_leverage(
        self,
        target_leverage: float,
        risk_metrics: RiskMetrics,
        sharpe_ratio: Optional[float] = None
    ) -> Tuple[float, str]:
        """
        計算調整後的槓桿

        Args:
            target_leverage: 目標槓桿
            risk_metrics: 風險指標
            sharpe_ratio: 可選的 Sharpe 比率

        Returns:
            (調整後槓桿, 調整理由)
        """
        volatility_adj = self.volatility_adjuster.get_volatility_adjustment()

        adjusted_leverage, reason = self.leverage_controller.adjust_leverage(
            target_leverage=target_leverage,
            risk_level=risk_metrics.risk_level,
            volatility_adjustment=volatility_adj,
            sharpe_ratio=sharpe_ratio
        )

        return adjusted_leverage, reason

    def set_position_limits(
        self,
        symbol: str,
        max_position_size: float,
        max_leverage: float,
        stop_loss_pct: float = 0.05,
        take_profit_pct: float = 0.10
    ) -> None:
        """
        設定位置風險限制

        Args:
            symbol: 交易對代碼
            max_position_size: 最大位置大小
            max_leverage: 最大槓桿
            stop_loss_pct: 止損百分比
            take_profit_pct: 獲利目標百分比
        """
        max_loss = max_position_size * stop_loss_pct
        max_portfolio_loss = max_position_size * self.max_portfolio_loss_pct

        limit = PositionRiskLimit(
            symbol=symbol,
            max_position_size=max_position_size,
            max_leverage=max_leverage,
            stop_loss_pct=stop_loss_pct,
            take_profit_pct=take_profit_pct,
            max_loss_per_trade=max_loss,
            max_portfolio_loss_pct=self.max_portfolio_loss_pct
        )

        self.position_limits[symbol] = limit
        self.logger.info(f"Set position limits for {symbol}: max_pos={max_position_size}, max_lev={max_leverage}")

    def set_stop_levels(
        self,
        symbol: str,
        entry_price: float,
        stop_loss_pct: float,
        take_profit_pct: float
    ) -> Dict[str, float]:
        """
        設定止損和獲利目標

        Args:
            symbol: 交易對代碼
            entry_price: 進場價格
            stop_loss_pct: 止損百分比
            take_profit_pct: 獲利目標百分比

        Returns:
            停損水平字典
        """
        stop_loss = entry_price * (1 - stop_loss_pct)
        take_profit = entry_price * (1 + take_profit_pct)

        self.active_stops[symbol] = {
            "entry_price": entry_price,
            "stop_loss": stop_loss,
            "take_profit": take_profit,
            "stop_loss_pct": stop_loss_pct,
            "take_profit_pct": take_profit_pct
        }

        self.logger.info(
            f"Set stops for {symbol}: SL={stop_loss:.2f}, TP={take_profit:.2f}"
        )

        return self.active_stops[symbol]

    def check_stop_levels(self, symbol: str, current_price: float) -> Optional[str]:
        """
        檢查是否觸發止損或獲利目標

        Args:
            symbol: 交易對代碼
            current_price: 當前價格

        Returns:
            觸發事件 ("stop_loss", "take_profit", None)
        """
        if symbol not in self.active_stops:
            return None

        stops = self.active_stops[symbol]
        stop_loss = stops["stop_loss"]
        take_profit = stops["take_profit"]

        if current_price <= stop_loss:
            self.logger.warning(f"🔴 Stop loss triggered for {symbol} at {current_price:.2f}")
            return "stop_loss"

        if current_price >= take_profit:
            self.logger.info(f"🟢 Take profit triggered for {symbol} at {current_price:.2f}")
            return "take_profit"

        return None

    def recommend_position_size(
        self,
        symbol: str,
        account_size: float,
        current_risk_level: RiskLevel
    ) -> float:
        """
        建議位置大小

        Args:
            symbol: 交易對代碼
            account_size: 賬戶大小
            current_risk_level: 當前風險等級

        Returns:
            建議位置大小
        """
        if symbol in self.position_limits:
            max_pos = self.position_limits[symbol].max_position_size
        else:
            max_pos = account_size * 0.1  # 預設 10%

        # 根據風險等級調整
        risk_factor_map = {
            RiskLevel.LOW: 1.0,
            RiskLevel.MODERATE: 0.8,
            RiskLevel.ELEVATED: 0.6,
            RiskLevel.HIGH: 0.4,
            RiskLevel.CRITICAL: 0.1
        }
        risk_factor = risk_factor_map.get(current_risk_level, 0.5)

        recommended_position = max_pos * risk_factor

        self.logger.debug(
            f"Recommended position for {symbol}: {recommended_position:.2f} "
            f"(risk_level={current_risk_level.value})"
        )

        return recommended_position

    def get_current_status(self) -> Dict[str, Any]:
        """
        取得引擎目前狀態

        Returns:
            狀態字典
        """
        return {
            "current_drawdown": self.drawdown_monitor.current_drawdown,
            "max_drawdown": self.drawdown_monitor.max_drawdown,
            "volatility": self.volatility_adjuster.volatility,
            "volatility_regime": self.volatility_adjuster.volatility_regime,
            "current_leverage": self.leverage_controller.current_leverage,
            "risk_level": self.drawdown_monitor.get_drawdown_level().value,
            "var_95": self.var_calculator.calculate_var(),
            "cvar_95": self.var_calculator.calculate_cvar(),
            "active_position_limits": len(self.position_limits),
            "active_stops": len(self.active_stops),
            "timestamp": datetime.now().isoformat()
        }

    def reset(self) -> None:
        """重設引擎"""
        self.drawdown_monitor.reset()
        self.volatility_adjuster.reset()
        self.var_calculator.reset()
        self.leverage_controller.reset()
        self.position_limits.clear()
        self.active_stops.clear()
        self.logger.info("✅ Dynamic Risk Management Engine reset")
