#!/usr/bin/env python3
"""
Test suite for core/dynamic_risk_management.py

Tests cover:
- DrawdownMonitor: portfolio value tracking, drawdown calculation, risk level classification
- VolatilityAdjuster: return history, regime detection, leverage adjustment factors
- VaRCalculator: Value at Risk and Conditional VaR computations
- LeverageController: leverage clamping, risk-adjusted leverage, Sharpe ratio effects
- RiskMetrics: risk score aggregation
- DynamicRiskManagementEngine: end-to-end risk processing, position limits, stop levels
"""

import sys
import pytest
import numpy as np
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.dynamic_risk_management import (
    DrawdownMonitor,
    VolatilityAdjuster,
    VaRCalculator,
    LeverageController,
    DynamicRiskManagementEngine,
    RiskLevel,
    RiskMetrics,
    PositionRiskLimit,
    LeverageAdjustmentMode,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _feed_drawdown(monitor: DrawdownMonitor, values: list) -> dict:
    result = {}
    for v in values:
        result = monitor.update(v)
    return result


def _feed_volatility(adjuster: VolatilityAdjuster, returns: list) -> float:
    vol = 0.0
    for r in returns:
        vol = adjuster.update(r)
    return vol


def _feed_var(calc: VaRCalculator, returns: list) -> None:
    for r in returns:
        calc.update(r)


# ---------------------------------------------------------------------------
# DrawdownMonitor
# ---------------------------------------------------------------------------

class TestDrawdownMonitor:

    def test_initial_state(self):
        m = DrawdownMonitor()
        assert m.peak_value == 0.0
        assert m.current_drawdown == 0.0
        assert m.max_drawdown == 0.0

    def test_peak_grows_monotonically(self):
        m = DrawdownMonitor()
        m.update(100)
        assert m.peak_value == 100
        m.update(200)
        assert m.peak_value == 200
        m.update(150)
        assert m.peak_value == 200  # Peak stays at 200

    def test_no_drawdown_on_growth(self):
        m = DrawdownMonitor()
        result = _feed_drawdown(m, [100, 110, 120])
        assert result["current_drawdown"] == pytest.approx(0.0, abs=1e-9)
        assert result["max_drawdown"] == pytest.approx(0.0, abs=1e-9)

    def test_drawdown_calculation(self):
        m = DrawdownMonitor()
        m.update(100)
        result = m.update(90)
        expected = (90 - 100) / 100  # -0.10
        assert result["current_drawdown"] == pytest.approx(expected)

    def test_max_drawdown_tracks_worst(self):
        m = DrawdownMonitor()
        m.update(100)
        m.update(80)   # -20%
        m.update(90)   # -10%
        assert m.max_drawdown == pytest.approx(-0.20)

    def test_peak_value_reported(self):
        m = DrawdownMonitor()
        m.update(100)
        m.update(200)
        result = m.update(150)
        assert result["peak_value"] == 200

    def test_reset_clears_state(self):
        m = DrawdownMonitor()
        _feed_drawdown(m, [100, 50])
        m.reset()
        assert m.peak_value == 0.0
        assert m.current_drawdown == 0.0
        assert m.max_drawdown == 0.0
        assert len(m.portfolio_values) == 0

    def test_window_size_respected(self):
        m = DrawdownMonitor(window_size=5)
        for i in range(10):
            m.update(float(i + 1))
        assert len(m.portfolio_values) == 5

    @pytest.mark.parametrize("drawdown_pct,expected_level", [
        (0.03, RiskLevel.LOW),
        (0.07, RiskLevel.MODERATE),
        (0.12, RiskLevel.ELEVATED),
        (0.20, RiskLevel.HIGH),
        (0.30, RiskLevel.CRITICAL),
    ])
    def test_get_drawdown_level(self, drawdown_pct, expected_level):
        m = DrawdownMonitor()
        m.update(100.0)
        m.update(100.0 * (1 - drawdown_pct))
        assert m.get_drawdown_level() == expected_level

    def test_zero_portfolio_value_no_crash(self):
        m = DrawdownMonitor()
        result = m.update(0.0)
        assert result["current_drawdown"] == 0.0


# ---------------------------------------------------------------------------
# VolatilityAdjuster
# ---------------------------------------------------------------------------

class TestVolatilityAdjuster:

    def test_initial_state(self):
        a = VolatilityAdjuster()
        assert a.volatility == 0.0
        assert a.volatility_regime == "normal"

    def test_single_return_no_std(self):
        a = VolatilityAdjuster()
        vol = a.update(0.01)
        assert vol == 0.0  # Need at least 2 points

    def test_volatility_increases_with_spread(self):
        a = VolatilityAdjuster()
        _feed_volatility(a, [0.0] * 20)
        zero_vol = a.volatility
        a.reset()
        _feed_volatility(a, [0.05, -0.05] * 10)
        assert a.volatility > zero_vol

    @pytest.mark.parametrize("returns,expected_regime", [
        ([0.005, -0.005] * 15, "low"),       # std ≈ 0.005 → low
        ([0.02, -0.02] * 15, "normal"),      # std ≈ 0.02 → normal
        ([0.04, -0.04] * 15, "elevated"),    # std ≈ 0.04 → elevated
        ([0.07, -0.07] * 15, "high"),        # std ≈ 0.07 → high
    ])
    def test_volatility_regime_classification(self, returns, expected_regime):
        a = VolatilityAdjuster()
        _feed_volatility(a, returns)
        assert a.volatility_regime == expected_regime

    @pytest.mark.parametrize("regime,expected_factor", [
        ("low", 1.1),
        ("normal", 1.0),
        ("elevated", 0.8),
        ("high", 0.5),
    ])
    def test_get_volatility_adjustment(self, regime, expected_factor):
        a = VolatilityAdjuster()
        a.volatility_regime = regime
        assert a.get_volatility_adjustment() == expected_factor

    def test_unknown_regime_returns_1(self):
        a = VolatilityAdjuster()
        a.volatility_regime = "unknown_regime"
        assert a.get_volatility_adjustment() == 1.0

    def test_reset_clears_history(self):
        a = VolatilityAdjuster()
        _feed_volatility(a, [0.05] * 20)
        a.reset()
        assert a.volatility == 0.0
        assert len(a.returns_history) == 0


# ---------------------------------------------------------------------------
# VaRCalculator
# ---------------------------------------------------------------------------

class TestVaRCalculator:

    def test_var_zero_with_insufficient_data(self):
        c = VaRCalculator()
        assert c.calculate_var() == 0.0
        c.update(0.01)
        assert c.calculate_var() == 0.0  # Only 1 point

    def test_cvar_zero_with_insufficient_data(self):
        c = VaRCalculator()
        assert c.calculate_cvar() == 0.0

    def test_var_non_negative(self):
        c = VaRCalculator()
        returns = list(np.random.normal(0, 0.02, 50))
        _feed_var(c, returns)
        assert c.calculate_var() >= 0.0

    def test_cvar_non_negative(self):
        c = VaRCalculator()
        returns = list(np.random.normal(0, 0.02, 50))
        _feed_var(c, returns)
        assert c.calculate_cvar() >= 0.0

    def test_higher_volatility_higher_var(self):
        rng = np.random.default_rng(42)
        c_low = VaRCalculator()
        c_high = VaRCalculator()
        _feed_var(c_low, list(rng.normal(0.001, 0.001, 100)))
        _feed_var(c_high, list(rng.normal(0.001, 0.05, 100)))
        assert c_high.calculate_var() >= c_low.calculate_var()

    def test_reset_clears_history(self):
        c = VaRCalculator()
        _feed_var(c, [0.01, 0.02, -0.03] * 20)
        c.reset()
        assert c.calculate_var() == 0.0
        assert len(c.returns_history) == 0

    def test_confidence_level_stored(self):
        c = VaRCalculator(confidence_level=0.99)
        assert c.confidence_level == 0.99


# ---------------------------------------------------------------------------
# LeverageController
# ---------------------------------------------------------------------------

class TestLeverageController:

    def test_initial_state(self):
        lc = LeverageController()
        assert lc.current_leverage == 1.0
        assert lc.max_leverage == 3.0
        assert lc.min_leverage == 0.1

    def test_leverage_clamped_to_max(self):
        lc = LeverageController(max_leverage=3.0)
        adjusted, _ = lc.adjust_leverage(
            target_leverage=10.0,
            risk_level=RiskLevel.LOW,
            volatility_adjustment=1.1,
        )
        assert adjusted <= 3.0

    def test_leverage_clamped_to_min(self):
        lc = LeverageController(min_leverage=0.1)
        adjusted, _ = lc.adjust_leverage(
            target_leverage=0.0001,
            risk_level=RiskLevel.CRITICAL,
            volatility_adjustment=0.5,
        )
        assert adjusted >= 0.1

    @pytest.mark.parametrize("risk_level,should_be_lower", [
        (RiskLevel.LOW, False),
        (RiskLevel.MODERATE, False),
        (RiskLevel.ELEVATED, True),
        (RiskLevel.HIGH, True),
        (RiskLevel.CRITICAL, True),
    ])
    def test_risk_level_reduces_leverage(self, risk_level, should_be_lower):
        lc = LeverageController(max_leverage=10.0)
        baseline, _ = lc.adjust_leverage(
            target_leverage=2.0,
            risk_level=RiskLevel.MODERATE,
            volatility_adjustment=1.0,
        )
        lc2 = LeverageController(max_leverage=10.0)
        adjusted, _ = lc2.adjust_leverage(
            target_leverage=2.0,
            risk_level=risk_level,
            volatility_adjustment=1.0,
        )
        if should_be_lower:
            assert adjusted < baseline
        else:
            assert adjusted >= baseline

    def test_high_sharpe_increases_leverage(self):
        lc_no_sharpe = LeverageController(max_leverage=10.0)
        adj_no, _ = lc_no_sharpe.adjust_leverage(
            target_leverage=2.0,
            risk_level=RiskLevel.MODERATE,
            volatility_adjustment=1.0,
            sharpe_ratio=None,
        )
        lc_high_sharpe = LeverageController(max_leverage=10.0)
        adj_high, _ = lc_high_sharpe.adjust_leverage(
            target_leverage=2.0,
            risk_level=RiskLevel.MODERATE,
            volatility_adjustment=1.0,
            sharpe_ratio=3.0,
        )
        assert adj_high > adj_no

    def test_low_sharpe_decreases_leverage(self):
        lc_high = LeverageController(max_leverage=10.0)
        adj_high, _ = lc_high.adjust_leverage(
            target_leverage=2.0, risk_level=RiskLevel.MODERATE,
            volatility_adjustment=1.0, sharpe_ratio=2.0,
        )
        lc_low = LeverageController(max_leverage=10.0)
        adj_low, _ = lc_low.adjust_leverage(
            target_leverage=2.0, risk_level=RiskLevel.MODERATE,
            volatility_adjustment=1.0, sharpe_ratio=0.5,
        )
        assert adj_low < adj_high

    def test_current_leverage_updated(self):
        lc = LeverageController()
        lc.adjust_leverage(
            target_leverage=2.0,
            risk_level=RiskLevel.MODERATE,
            volatility_adjustment=1.0,
        )
        assert lc.current_leverage != 1.0  # Updated from initial 1.0

    def test_reason_string_returned(self):
        lc = LeverageController()
        _, reason = lc.adjust_leverage(
            target_leverage=2.0, risk_level=RiskLevel.LOW, volatility_adjustment=1.0,
        )
        assert isinstance(reason, str)
        assert len(reason) > 0

    def test_get_leverage_trend_insufficient_data(self):
        lc = LeverageController()
        change, trend = lc.get_leverage_trend()
        assert change == 0.0
        assert trend == "insufficient_data"

    def test_get_leverage_trend_decreasing(self):
        lc = LeverageController(max_leverage=20.0, min_leverage=0.01)
        # Feed decreasing leverage values
        for target in [5.0, 4.0, 3.0, 2.0, 1.5, 1.0, 0.8, 0.6, 0.5, 0.4,
                       0.3, 0.2, 0.1]:
            lc.adjust_leverage(target, RiskLevel.CRITICAL, 0.5)
        _, trend = lc.get_leverage_trend()
        assert trend == "decreasing"

    def test_reset_clears_history(self):
        lc = LeverageController()
        lc.adjust_leverage(2.0, RiskLevel.MODERATE, 1.0)
        lc.reset()
        assert lc.current_leverage == 1.0
        assert len(lc.leverage_history) == 0


# ---------------------------------------------------------------------------
# RiskMetrics
# ---------------------------------------------------------------------------

class TestRiskMetrics:

    def _make_metrics(self, drawdown=0.0, volatility=0.02, var_95=0.01):
        return RiskMetrics(
            current_drawdown=drawdown,
            max_drawdown=drawdown,
            drawdown_recovery_rate=1.0,
            volatility=volatility,
            var_95=var_95,
            cvar_95=var_95 * 1.2,
        )

    def test_risk_score_zero_for_safe_conditions(self):
        m = self._make_metrics(drawdown=0.0, volatility=0.0, var_95=0.0)
        score = m.get_risk_score()
        assert score == pytest.approx(0.0)

    def test_risk_score_one_for_extreme_conditions(self):
        m = self._make_metrics(drawdown=-0.30, volatility=0.50, var_95=0.10)
        score = m.get_risk_score()
        assert score == pytest.approx(1.0)

    def test_risk_score_between_zero_and_one(self):
        m = self._make_metrics(drawdown=-0.10, volatility=0.05, var_95=0.02)
        score = m.get_risk_score()
        assert 0.0 <= score <= 1.0

    def test_higher_drawdown_higher_score(self):
        low = self._make_metrics(drawdown=-0.02)
        high = self._make_metrics(drawdown=-0.25)
        assert high.get_risk_score() > low.get_risk_score()

    def test_default_risk_level_is_moderate(self):
        m = self._make_metrics()
        assert m.risk_level == RiskLevel.MODERATE


# ---------------------------------------------------------------------------
# DynamicRiskManagementEngine
# ---------------------------------------------------------------------------

class TestDynamicRiskManagementEngine:

    def _make_engine(self, max_leverage=3.0, max_portfolio_loss_pct=0.15):
        return DynamicRiskManagementEngine(
            max_leverage=max_leverage,
            max_portfolio_loss_pct=max_portfolio_loss_pct,
        )

    def test_process_portfolio_update_returns_metrics(self):
        engine = self._make_engine()
        metrics = engine.process_portfolio_update(10000.0, 0.01)
        assert isinstance(metrics, RiskMetrics)

    def test_process_portfolio_update_tracks_drawdown(self):
        engine = self._make_engine()
        engine.process_portfolio_update(10000.0, 0.0)
        metrics = engine.process_portfolio_update(8000.0, -0.20)
        assert metrics.current_drawdown == pytest.approx(-0.20, abs=1e-9)

    def test_risk_level_reflects_drawdown(self):
        engine = self._make_engine()
        engine.process_portfolio_update(10000.0, 0.0)
        metrics = engine.process_portfolio_update(6000.0, -0.40)
        assert metrics.risk_level == RiskLevel.CRITICAL

    def test_calculate_adjusted_leverage_returns_tuple(self):
        engine = self._make_engine()
        metrics = engine.process_portfolio_update(10000.0, 0.0)
        lev, reason = engine.calculate_adjusted_leverage(2.0, metrics)
        assert isinstance(lev, float)
        assert isinstance(reason, str)

    def test_adjusted_leverage_bounded_by_max(self):
        engine = self._make_engine(max_leverage=3.0)
        metrics = engine.process_portfolio_update(10000.0, 0.0)
        lev, _ = engine.calculate_adjusted_leverage(100.0, metrics)
        assert lev <= 3.0

    def test_set_position_limits_stored(self):
        engine = self._make_engine()
        engine.set_position_limits("BTCUSDT", max_position_size=1000.0, max_leverage=5.0)
        assert "BTCUSDT" in engine.position_limits
        limit = engine.position_limits["BTCUSDT"]
        assert isinstance(limit, PositionRiskLimit)
        assert limit.max_position_size == 1000.0
        assert limit.max_leverage == 5.0

    def test_set_stop_levels_calculates_prices(self):
        engine = self._make_engine()
        stops = engine.set_stop_levels(
            symbol="BTCUSDT",
            entry_price=50000.0,
            stop_loss_pct=0.05,
            take_profit_pct=0.10,
        )
        assert stops["stop_loss"] == pytest.approx(47500.0)
        assert stops["take_profit"] == pytest.approx(55000.0)
        assert stops["entry_price"] == 50000.0

    def test_check_stop_levels_none_when_symbol_unknown(self):
        engine = self._make_engine()
        result = engine.check_stop_levels("UNKNOWN", 50000.0)
        assert result is None

    def test_check_stop_levels_triggers_stop_loss(self):
        engine = self._make_engine()
        engine.set_stop_levels("BTCUSDT", 50000.0, stop_loss_pct=0.05, take_profit_pct=0.10)
        # Price drops below stop loss (50000 * 0.95 = 47500)
        result = engine.check_stop_levels("BTCUSDT", 47000.0)
        assert result == "stop_loss"

    def test_check_stop_levels_triggers_take_profit(self):
        engine = self._make_engine()
        engine.set_stop_levels("BTCUSDT", 50000.0, stop_loss_pct=0.05, take_profit_pct=0.10)
        # Price rises above take profit (50000 * 1.10 = 55000)
        result = engine.check_stop_levels("BTCUSDT", 56000.0)
        assert result == "take_profit"

    def test_check_stop_levels_no_trigger_in_range(self):
        engine = self._make_engine()
        engine.set_stop_levels("BTCUSDT", 50000.0, stop_loss_pct=0.05, take_profit_pct=0.10)
        # Price within [47500, 55000]
        result = engine.check_stop_levels("BTCUSDT", 51000.0)
        assert result is None

    @pytest.mark.parametrize("risk_level,max_factor", [
        (RiskLevel.LOW, 1.0),
        (RiskLevel.MODERATE, 0.8),
        (RiskLevel.ELEVATED, 0.6),
        (RiskLevel.HIGH, 0.4),
        (RiskLevel.CRITICAL, 0.1),
    ])
    def test_recommend_position_size_scales_with_risk(self, risk_level, max_factor):
        engine = self._make_engine()
        account_size = 10000.0
        engine.set_position_limits("ETHUSDT", max_position_size=account_size, max_leverage=3.0)
        recommended = engine.recommend_position_size("ETHUSDT", account_size, risk_level)
        assert recommended == pytest.approx(account_size * max_factor, rel=1e-6)

    def test_recommend_position_size_default_ten_pct_unknown_symbol(self):
        engine = self._make_engine()
        account_size = 10000.0
        recommended = engine.recommend_position_size("UNKNOWN", account_size, RiskLevel.LOW)
        # Default is 10% of account, adjusted by LOW risk factor (1.0)
        assert recommended == pytest.approx(account_size * 0.1 * 1.0)

    def test_get_current_status_returns_dict(self):
        engine = self._make_engine()
        engine.process_portfolio_update(10000.0, 0.01)
        status = engine.get_current_status()
        assert isinstance(status, dict)
        expected_keys = [
            "current_drawdown", "max_drawdown", "volatility",
            "volatility_regime", "current_leverage", "risk_level",
            "var_95", "cvar_95", "active_position_limits", "active_stops", "timestamp",
        ]
        for key in expected_keys:
            assert key in status

    def test_reset_clears_all_state(self):
        engine = self._make_engine()
        engine.process_portfolio_update(10000.0, 0.05)
        engine.set_position_limits("BTC", 1000.0, 3.0)
        engine.set_stop_levels("BTC", 50000.0, 0.05, 0.10)
        engine.reset()

        assert engine.drawdown_monitor.current_drawdown == 0.0
        assert len(engine.position_limits) == 0
        assert len(engine.active_stops) == 0

    def test_multiple_symbols_tracked_independently(self):
        engine = self._make_engine()
        engine.set_stop_levels("BTC", 50000.0, 0.05, 0.10)
        engine.set_stop_levels("ETH", 3000.0, 0.05, 0.10)

        assert engine.check_stop_levels("BTC", 47000.0) == "stop_loss"
        assert engine.check_stop_levels("ETH", 2800.0) == "stop_loss"
        assert engine.check_stop_levels("BTC", 52000.0) is None
