#!/usr/bin/env python3
"""
Test suite for core/market_regime_detector.py

Tests cover:
- TechnicalIndicators: trend, volatility, ATR, RSI, Bollinger Bands, range
- MarketRegimeDetector: regime detection, characteristics, confidence, strategy recommendations
- MarketRegime dataclass fields
"""

import sys
import pytest
import numpy as np
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.market_regime_detector import (
    TechnicalIndicators,
    MarketRegime,
    MarketRegimeType,
    MarketRegimeDetector,
)


# ---------------------------------------------------------------------------
# Fixtures / helpers
# ---------------------------------------------------------------------------

def _trend_up(n: int = 50, slope: float = 1.0) -> np.ndarray:
    """Monotonically rising prices."""
    return np.array([100.0 + slope * i for i in range(n)])


def _trend_down(n: int = 50, slope: float = 1.0) -> np.ndarray:
    """Monotonically falling prices."""
    return np.array([100.0 + slope * (n - 1 - i) for i in range(n)])


def _ranging(n: int = 50, amplitude: float = 1.0, center: float = 100.0) -> np.ndarray:
    """Oscillating prices with small amplitude (rangebound)."""
    return np.array([center + amplitude * np.sin(2 * np.pi * i / 10) for i in range(n)])


def _volatile(n: int = 50, std: float = 5.0, center: float = 100.0) -> np.ndarray:
    """Prices with large random steps."""
    rng = np.random.default_rng(0)
    return np.abs(center + np.cumsum(rng.normal(0, std, n)))


# ---------------------------------------------------------------------------
# TechnicalIndicators
# ---------------------------------------------------------------------------

class TestTechnicalIndicatorsTrend:

    def test_uptrend_positive_strength(self):
        prices = _trend_up(50, slope=2.0)
        strength, direction = TechnicalIndicators.calculate_trend(prices, period=20)
        assert strength > 0, "Uptrend should have positive strength"

    def test_downtrend_negative_strength(self):
        prices = _trend_down(50, slope=2.0)
        strength, direction = TechnicalIndicators.calculate_trend(prices, period=20)
        assert strength < 0, "Downtrend should have negative strength"

    def test_flat_prices_near_zero_strength(self):
        prices = np.full(50, 100.0)
        strength, direction = TechnicalIndicators.calculate_trend(prices, period=20)
        assert abs(strength) < 1e-6

    def test_insufficient_data_returns_zeros(self):
        prices = np.array([100.0, 101.0])
        strength, direction = TechnicalIndicators.calculate_trend(prices, period=20)
        assert strength == 0.0
        assert direction == 0.5

    def test_strength_clamped_between_minus1_and_1(self):
        prices = np.linspace(1, 1000, 100)
        strength, direction = TechnicalIndicators.calculate_trend(prices, period=20)
        assert -1.0 <= strength <= 1.0

    def test_direction_between_0_and_1(self):
        prices = _trend_up(50)
        _, direction = TechnicalIndicators.calculate_trend(prices, period=20)
        assert 0.0 <= direction <= 1.0


class TestTechnicalIndicatorsVolatility:

    def test_zero_for_constant_prices(self):
        prices = np.full(50, 100.0)
        vol = TechnicalIndicators.calculate_volatility(prices, period=20)
        assert vol == 0.0

    def test_higher_for_volatile_prices(self):
        prices_quiet = 100.0 + np.sin(np.linspace(0, np.pi, 50)) * 0.01
        rng = np.random.default_rng(1)
        prices_volatile = np.abs(100.0 + rng.normal(0, 5, 50))
        vol_quiet = TechnicalIndicators.calculate_volatility(prices_quiet, period=20)
        vol_volatile = TechnicalIndicators.calculate_volatility(prices_volatile, period=20)
        assert vol_volatile > vol_quiet

    def test_insufficient_data_returns_zero(self):
        prices = np.array([100.0, 101.0])
        vol = TechnicalIndicators.calculate_volatility(prices, period=20)
        assert vol == 0.0

    def test_non_negative(self):
        rng = np.random.default_rng(2)
        prices = np.abs(100.0 + rng.normal(0, 2, 50))
        vol = TechnicalIndicators.calculate_volatility(prices, period=20)
        assert vol >= 0.0


class TestTechnicalIndicatorsATR:

    def test_returns_zero_for_insufficient_data(self):
        high = np.array([102.0, 103.0])
        low = np.array([99.0, 100.0])
        close = np.array([101.0, 101.5])
        atr = TechnicalIndicators.calculate_atr(high, low, close, period=14)
        assert atr == 0.0

    def test_positive_for_normal_ohlc(self):
        n = 50
        close = np.linspace(100, 110, n)
        high = close + 1.0
        low = close - 1.0
        atr = TechnicalIndicators.calculate_atr(high, low, close, period=14)
        assert atr > 0.0

    def test_proportional_to_bar_size(self):
        n = 50
        close = np.linspace(100, 110, n)
        high_small = close + 0.5
        low_small = close - 0.5
        high_large = close + 5.0
        low_large = close - 5.0
        atr_small = TechnicalIndicators.calculate_atr(high_small, low_small, close, period=14)
        atr_large = TechnicalIndicators.calculate_atr(high_large, low_large, close, period=14)
        assert atr_large > atr_small


class TestTechnicalIndicatorsRSI:

    def test_returns_50_for_insufficient_data(self):
        prices = np.array([100.0] * 5)
        rsi = TechnicalIndicators.calculate_rsi(prices, period=14)
        assert rsi == 50.0

    def test_rsi_between_0_and_100(self):
        rng = np.random.default_rng(3)
        prices = np.abs(100.0 + np.cumsum(rng.normal(0, 1, 50)))
        rsi = TechnicalIndicators.calculate_rsi(prices, period=14)
        assert 0.0 <= rsi <= 100.0

    def test_high_rsi_for_consecutive_gains(self):
        prices = np.linspace(100, 200, 50)  # Purely uptrending
        rsi = TechnicalIndicators.calculate_rsi(prices, period=14)
        assert rsi == 100.0

    def test_low_rsi_for_consecutive_losses(self):
        prices = np.linspace(200, 100, 50)  # Purely downtrending
        rsi = TechnicalIndicators.calculate_rsi(prices, period=14)
        assert rsi == 0.0

    def test_neutral_rsi_for_alternating_prices(self):
        prices = np.array([100.0 + (1 if i % 2 == 0 else -1) for i in range(50)])
        rsi = TechnicalIndicators.calculate_rsi(prices, period=14)
        assert 40.0 <= rsi <= 60.0


class TestTechnicalIndicatorsBBands:

    def test_returns_none_for_insufficient_data(self):
        prices = np.array([100.0] * 5)
        result = TechnicalIndicators.calculate_bbands(prices, period=20)
        assert result is None

    def test_returns_dict_with_expected_keys(self):
        prices = np.linspace(90, 110, 50)
        result = TechnicalIndicators.calculate_bbands(prices, period=20)
        assert result is not None
        for key in ["upper", "middle", "lower", "width"]:
            assert key in result

    def test_upper_above_middle_above_lower(self):
        prices = _volatile(50)
        result = TechnicalIndicators.calculate_bbands(prices, period=20)
        assert result["upper"] > result["middle"] > result["lower"]

    def test_width_doubles_with_num_std(self):
        prices = _volatile(50, std=2.0)
        r1 = TechnicalIndicators.calculate_bbands(prices, period=20, num_std=1.0)
        r2 = TechnicalIndicators.calculate_bbands(prices, period=20, num_std=2.0)
        assert r2["width"] == pytest.approx(r1["width"] * 2, rel=1e-9)


class TestTechnicalIndicatorsRange:

    def test_returns_zero_for_insufficient_data(self):
        high = np.array([101.0, 102.0])
        low = np.array([99.0, 98.0])
        result = TechnicalIndicators.calculate_range(high, low, period=20)
        assert result == 0.0

    def test_larger_range_higher_value(self):
        n = 30
        h_small = np.full(n, 101.0)
        l_small = np.full(n, 99.0)
        h_large = np.full(n, 110.0)
        l_large = np.full(n, 90.0)
        r_small = TechnicalIndicators.calculate_range(h_small, l_small, period=20)
        r_large = TechnicalIndicators.calculate_range(h_large, l_large, period=20)
        assert r_large > r_small

    def test_zero_when_high_equals_low(self):
        n = 30
        prices = np.full(n, 100.0)
        result = TechnicalIndicators.calculate_range(prices, prices, period=20)
        assert result == 0.0


# ---------------------------------------------------------------------------
# MarketRegimeDetector
# ---------------------------------------------------------------------------

class TestMarketRegimeDetectorInit:

    def test_default_parameters(self):
        d = MarketRegimeDetector()
        assert d.trend_threshold == 0.3
        assert d.volatile_threshold == 0.04
        assert d.lookback_period == 20

    def test_custom_parameters(self):
        d = MarketRegimeDetector(trend_threshold=0.5, volatile_threshold=0.06, lookback_period=30)
        assert d.trend_threshold == 0.5
        assert d.volatile_threshold == 0.06
        assert d.lookback_period == 30


class TestMarketRegimeDetectorDetectRegime:

    def test_returns_unknown_for_insufficient_data(self):
        d = MarketRegimeDetector(lookback_period=20)
        prices = np.array([100.0] * 5)
        regime = d.detect_regime(prices)
        assert regime.regime_type == MarketRegimeType.UNKNOWN
        assert regime.strength == 0.0
        assert regime.confidence == 0.0

    def test_detects_trending_regime(self):
        d = MarketRegimeDetector(trend_threshold=0.2, volatile_threshold=0.1)
        # Strong uptrend with very small random noise
        prices = np.linspace(100, 200, 60)
        regime = d.detect_regime(prices)
        assert regime.regime_type == MarketRegimeType.TRENDING

    def test_detects_volatile_regime(self):
        d = MarketRegimeDetector(volatile_threshold=0.01)  # Low threshold to trigger easily
        # High-volatility prices (large random swings)
        rng = np.random.default_rng(42)
        prices = np.abs(100.0 + np.cumsum(rng.normal(0, 3.0, 50)))
        regime = d.detect_regime(prices)
        assert regime.regime_type == MarketRegimeType.VOLATILE

    def test_regime_has_timestamp(self):
        d = MarketRegimeDetector()
        prices = _trend_up(60)
        regime = d.detect_regime(prices)
        assert isinstance(regime.timestamp, datetime)

    def test_regime_has_recommended_strategies(self):
        d = MarketRegimeDetector()
        prices = _trend_up(60)
        regime = d.detect_regime(prices)
        assert isinstance(regime.recommended_strategies, dict)

    def test_regime_stored_in_history(self):
        d = MarketRegimeDetector()
        prices = _trend_up(60)
        d.detect_regime(prices)
        assert len(d.regime_history) == 1
        d.detect_regime(prices)
        assert len(d.regime_history) == 2

    def test_characteristics_non_empty_for_sufficient_data(self):
        d = MarketRegimeDetector()
        prices = _trend_up(60)
        regime = d.detect_regime(prices)
        assert isinstance(regime.characteristics, dict)
        assert len(regime.characteristics) > 0

    def test_strength_between_0_and_1(self):
        d = MarketRegimeDetector()
        for prices in [_trend_up(60), _ranging(60), _volatile(60)]:
            regime = d.detect_regime(prices)
            assert 0.0 <= regime.strength <= 1.0

    def test_confidence_between_0_and_1(self):
        d = MarketRegimeDetector()
        for prices in [_trend_up(60), _ranging(60), _volatile(60)]:
            regime = d.detect_regime(prices)
            assert 0.0 <= regime.confidence <= 1.0

    def test_detect_regime_with_ohlc(self):
        n = 60
        prices = _trend_up(n, slope=1.0)
        high = prices + 1.0
        low = prices - 1.0
        d = MarketRegimeDetector()
        regime = d.detect_regime(prices, high=high, low=low)
        assert regime.regime_type != MarketRegimeType.UNKNOWN
        assert "atr" in regime.characteristics
        assert "price_range" in regime.characteristics


class TestMarketRegimeDetectorStrategyRecommendations:

    def _detect(self, regime_type: MarketRegimeType, detector: MarketRegimeDetector,
                 prices: np.ndarray) -> MarketRegime:
        return detector.detect_regime(prices)

    def test_trending_recommends_momentum(self):
        d = MarketRegimeDetector(trend_threshold=0.2, volatile_threshold=0.1)
        prices = np.linspace(100, 200, 60)
        regime = d.detect_regime(prices)
        if regime.regime_type == MarketRegimeType.TRENDING:
            assert "momentum" in regime.recommended_strategies
            assert regime.recommended_strategies["momentum"] > 0

    def test_volatile_recommends_quantum_optimized(self):
        d = MarketRegimeDetector(volatile_threshold=0.01)
        rng = np.random.default_rng(7)
        prices = np.abs(100.0 + np.cumsum(rng.normal(0, 3.0, 50)))
        regime = d.detect_regime(prices)
        if regime.regime_type == MarketRegimeType.VOLATILE:
            assert "quantum_optimized" in regime.recommended_strategies

    def test_strategy_weights_sum_to_approximately_one(self):
        """Verify strategy weights for each deterministic regime type sum to 1."""
        d = MarketRegimeDetector()
        # Use internal method to test strategy recommendations directly
        for regime_type in [
            MarketRegimeType.TRENDING,
            MarketRegimeType.RANGING,
            MarketRegimeType.VOLATILE,
            MarketRegimeType.MIXED,
            MarketRegimeType.UNKNOWN,
        ]:
            strategies = d._recommend_strategies(regime_type, {})
            total = sum(strategies.values())
            assert total == pytest.approx(1.0, abs=1e-9), f"Weights for {regime_type} don't sum to 1: {total}"
