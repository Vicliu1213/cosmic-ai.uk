#!/usr/bin/env python3
"""
DataAlignmentHelper Tests
数据对齐辅助模块测试

Unit tests for DataAlignmentHelper and the get_aligned_candle convenience function.
"""

import sys
import logging
from datetime import datetime, timezone, timedelta
from pathlib import Path

import pandas as pd
import pytest

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.data_alignment import DataAlignmentHelper, get_aligned_candle


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_df(periods: int = 10, freq: str = '5min', tz: str = 'UTC') -> pd.DataFrame:
    """Create a simple OHLCV DataFrame with a DatetimeIndex."""
    timestamps = pd.date_range('2025-01-01 00:00:00', periods=periods, freq=freq, tz=tz)
    return pd.DataFrame(
        {
            'open': 100.0,
            'high': 101.0,
            'low': 99.0,
            'close': 100.5,
            'volume': 1000.0,
        },
        index=timestamps,
    )


def _backtest_config() -> dict:
    """Minimal config dict that forces backtest (lag) mode."""
    return {'mode': 'backtest', 'timeframe_settings': {}, 'lag_detection': {}}


def _live_config(use_realtime: bool = False) -> dict:
    """Minimal config dict for live mode."""
    return {
        'mode': 'live',
        'timeframe_settings': {
            '5m': {'use_realtime': use_realtime, 'min_completion_pct': 0, 'lag_warning_threshold': 30},
        },
        'lag_detection': {'warning_threshold_minutes': 30, 'time_gap_threshold_minutes': 60},
    }


def _make_helper(config: dict) -> DataAlignmentHelper:
    """Instantiate a DataAlignmentHelper with an in-memory config (no file I/O)."""
    helper = DataAlignmentHelper.__new__(DataAlignmentHelper)
    helper.logger = logging.getLogger('test')
    helper.config = config
    helper.mode = config.get('mode', 'backtest')
    helper.period_minutes = {
        '1m': 1, '3m': 3, '5m': 5, '15m': 15, '30m': 30,
        '1h': 60, '2h': 120, '4h': 240, '6h': 360, '12h': 720,
        '1d': 1440, '1w': 10080,
    }
    return helper


# ---------------------------------------------------------------------------
# DataAlignmentHelper – initialisation
# ---------------------------------------------------------------------------

class TestDataAlignmentHelperInit:
    """Tests for DataAlignmentHelper initialisation via a real (temp) config."""

    def test_init_with_nonexistent_config(self):
        """Missing config file should produce a default backtest config."""
        helper = DataAlignmentHelper(config_path='/nonexistent/path/config.yaml')
        assert helper.mode == 'backtest'
        assert isinstance(helper.config, dict)

    def test_period_minutes_map(self):
        helper = DataAlignmentHelper(config_path='/nonexistent/path/config.yaml')
        assert helper.period_minutes['1m'] == 1
        assert helper.period_minutes['1h'] == 60
        assert helper.period_minutes['1d'] == 1440
        assert helper.period_minutes['1w'] == 10080


# ---------------------------------------------------------------------------
# DataAlignmentHelper – _should_use_realtime
# ---------------------------------------------------------------------------

class TestShouldUseRealtime:
    """Tests for the _should_use_realtime decision logic."""

    def test_backtest_always_lag(self):
        helper = _make_helper(_backtest_config())
        assert helper._should_use_realtime('5m', {}) is False

    def test_live_default_lag(self):
        helper = _make_helper(_live_config(use_realtime=False))
        assert helper._should_use_realtime('5m', {'use_realtime': False}) is False

    def test_live_realtime_enabled(self):
        helper = _make_helper(_live_config(use_realtime=True))
        assert helper._should_use_realtime('5m', {'use_realtime': True}) is True

    def test_live_aggressive_default_realtime(self):
        config = {'mode': 'live_aggressive', 'timeframe_settings': {}}
        helper = _make_helper(config)
        # No explicit 'use_realtime' key → should default to True in live_aggressive
        assert helper._should_use_realtime('5m', {}) is True

    def test_live_aggressive_explicit_false(self):
        config = {'mode': 'live_aggressive', 'timeframe_settings': {}}
        helper = _make_helper(config)
        assert helper._should_use_realtime('5m', {'use_realtime': False}) is False


# ---------------------------------------------------------------------------
# DataAlignmentHelper – _calculate_completion
# ---------------------------------------------------------------------------

class TestCalculateCompletion:
    """Tests for _calculate_completion."""

    def test_fully_completed_candle(self):
        helper = _make_helper(_backtest_config())
        df = _make_df(periods=5, freq='5min')
        # Set 'now' well past the last candle's expected end
        now = df.index[-1].to_pydatetime() + timedelta(minutes=10)
        now = now.replace(tzinfo=timezone.utc)
        pct = helper._calculate_completion(df, '5m', now)
        assert pct == 100.0

    def test_half_completed_candle(self):
        helper = _make_helper(_backtest_config())
        df = _make_df(periods=3, freq='5min')
        last_time = df.index[-1].to_pydatetime().replace(tzinfo=timezone.utc)
        # Exactly 2.5 minutes after the last candle opened → 50 %
        now = last_time + timedelta(minutes=2, seconds=30)
        pct = helper._calculate_completion(df, '5m', now)
        assert abs(pct - 50.0) < 1.0

    def test_not_started_candle(self):
        helper = _make_helper(_backtest_config())
        df = _make_df(periods=3, freq='5min')
        last_time = df.index[-1].to_pydatetime().replace(tzinfo=timezone.utc)
        # 'now' is exactly at candle open
        pct = helper._calculate_completion(df, '5m', last_time)
        assert pct == 0.0

    def test_completion_clamped_to_zero(self):
        helper = _make_helper(_backtest_config())
        df = _make_df(periods=3, freq='5min')
        last_time = df.index[-1].to_pydatetime().replace(tzinfo=timezone.utc)
        # 'now' before candle open → should clamp to 0
        pct = helper._calculate_completion(df, '5m', last_time - timedelta(seconds=1))
        assert pct == 0.0

    def test_unknown_timeframe_defaults_to_5min(self):
        helper = _make_helper(_backtest_config())
        df = _make_df(periods=3, freq='5min')
        now = df.index[-1].to_pydatetime().replace(tzinfo=timezone.utc) + timedelta(minutes=10)
        pct = helper._calculate_completion(df, 'unknown', now)
        assert pct == 100.0  # past the default 5-minute window


# ---------------------------------------------------------------------------
# DataAlignmentHelper – _calculate_lag_minutes
# ---------------------------------------------------------------------------

class TestCalculateLagMinutes:
    """Tests for _calculate_lag_minutes."""

    def test_zero_lag(self):
        helper = _make_helper(_backtest_config())
        ts = pd.Timestamp('2025-01-01 12:00:00', tz='UTC')
        now = datetime(2025, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        lag = helper._calculate_lag_minutes(ts, now)
        assert lag == 0.0

    def test_30_minute_lag(self):
        helper = _make_helper(_backtest_config())
        ts = pd.Timestamp('2025-01-01 12:00:00', tz='UTC')
        now = datetime(2025, 1, 1, 12, 30, 0, tzinfo=timezone.utc)
        lag = helper._calculate_lag_minutes(ts, now)
        assert abs(lag - 30.0) < 0.01

    def test_naive_timestamps(self):
        """Should handle naive timestamps by assuming UTC."""
        helper = _make_helper(_backtest_config())
        ts = pd.Timestamp('2025-01-01 12:00:00')  # naive
        now = datetime(2025, 1, 1, 12, 15, 0, tzinfo=timezone.utc)
        lag = helper._calculate_lag_minutes(ts, now)
        assert abs(lag - 15.0) < 0.01


# ---------------------------------------------------------------------------
# DataAlignmentHelper – get_aligned_candle (backtest mode)
# ---------------------------------------------------------------------------

class TestGetAlignedCandleBacktest:
    """Tests for get_aligned_candle in backtest mode (always uses penultimate candle)."""

    def test_returns_tuple(self):
        helper = _make_helper(_backtest_config())
        df = _make_df(periods=5)
        candle, meta = helper.get_aligned_candle(df, '5m')
        assert isinstance(candle, pd.Series)
        assert isinstance(meta, dict)

    def test_uses_penultimate_candle(self):
        helper = _make_helper(_backtest_config())
        df = _make_df(periods=5)
        candle, meta = helper.get_aligned_candle(df, '5m')
        assert meta['index'] == -2
        assert not meta['is_realtime']

    def test_completion_is_100_in_backtest(self):
        helper = _make_helper(_backtest_config())
        df = _make_df(periods=5)
        _, meta = helper.get_aligned_candle(df, '5m')
        assert meta['completion_pct'] == 100.0
        assert meta['is_completed'] is True

    def test_metadata_keys_present(self):
        helper = _make_helper(_backtest_config())
        df = _make_df(periods=5)
        _, meta = helper.get_aligned_candle(df, '5m')
        expected_keys = {'index', 'timestamp', 'lag_minutes', 'is_realtime',
                         'is_completed', 'completion_pct', 'timeframe', 'mode'}
        assert expected_keys.issubset(set(meta.keys()))

    def test_timeframe_recorded_in_metadata(self):
        helper = _make_helper(_backtest_config())
        df = _make_df(periods=5)
        _, meta = helper.get_aligned_candle(df, '15m')
        assert meta['timeframe'] == '15m'

    def test_raises_on_short_df(self):
        helper = _make_helper(_backtest_config())
        df = _make_df(periods=1)
        with pytest.raises(ValueError):
            helper.get_aligned_candle(df, '5m')

    def test_candle_values_match_penultimate_row(self):
        helper = _make_helper(_backtest_config())
        df = _make_df(periods=5)
        candle, _ = helper.get_aligned_candle(df, '5m')
        pd.testing.assert_series_equal(candle, df.iloc[-2])


# ---------------------------------------------------------------------------
# DataAlignmentHelper – get_aligned_candle (live mode)
# ---------------------------------------------------------------------------

class TestGetAlignedCandleLive:
    """Tests for get_aligned_candle in live mode."""

    def test_live_lag_uses_penultimate(self):
        helper = _make_helper(_live_config(use_realtime=False))
        df = _make_df(periods=5)
        _, meta = helper.get_aligned_candle(df, '5m')
        assert meta['index'] == -2
        assert not meta['is_realtime']

    def test_live_realtime_uses_last(self):
        helper = _make_helper(_live_config(use_realtime=True))
        df = _make_df(periods=5)
        # Provide 'now' right in the middle of the latest candle so it's ≥ min_completion
        last_time = df.index[-1].to_pydatetime().replace(tzinfo=timezone.utc)
        now = last_time + timedelta(seconds=30)  # 10% complete for a 5-min candle
        _, meta = helper.get_aligned_candle(df, '5m', now=now)
        assert meta['index'] == -1
        assert meta['is_realtime']

    def test_live_realtime_degrades_when_below_min_completion(self):
        config = {
            'mode': 'live',
            'timeframe_settings': {
                '5m': {'use_realtime': True, 'min_completion_pct': 80,
                       'lag_warning_threshold': 30},
            },
            'lag_detection': {},
        }
        helper = _make_helper(config)
        df = _make_df(periods=5)
        last_time = df.index[-1].to_pydatetime().replace(tzinfo=timezone.utc)
        # Only 10% complete – below the 80% threshold
        now = last_time + timedelta(seconds=30)
        _, meta = helper.get_aligned_candle(df, '5m', now=now)
        # Should have fallen back to the penultimate (completed) candle
        assert meta['index'] == -2
        assert meta['completion_pct'] == 100.0


# ---------------------------------------------------------------------------
# DataAlignmentHelper – get_multi_timeframe_metadata
# ---------------------------------------------------------------------------

class TestGetMultiTimeframeMetadata:
    """Tests for get_multi_timeframe_metadata."""

    def test_returns_dict(self):
        helper = _make_helper(_backtest_config())
        data = {
            '5m': _make_df(periods=5, freq='5min'),
            '15m': _make_df(periods=5, freq='15min'),
        }
        result = helper.get_multi_timeframe_metadata(data)
        assert isinstance(result, dict)

    def test_contains_expected_keys(self):
        helper = _make_helper(_backtest_config())
        data = {'5m': _make_df(periods=5, freq='5min')}
        result = helper.get_multi_timeframe_metadata(data)
        assert 'timeframes' in result
        assert 'time_gap_minutes' in result
        assert 'earliest_timestamp' in result
        assert 'latest_timestamp' in result
        assert 'max_lag_minutes' in result

    def test_timeframes_key_contains_all_inputs(self):
        helper = _make_helper(_backtest_config())
        data = {
            '5m': _make_df(periods=5, freq='5min'),
            '1h': _make_df(periods=5, freq='1h'),
        }
        result = helper.get_multi_timeframe_metadata(data)
        assert '5m' in result['timeframes']
        assert '1h' in result['timeframes']

    def test_empty_input_returns_empty(self):
        helper = _make_helper(_backtest_config())
        result = helper.get_multi_timeframe_metadata({})
        assert result == {}


# ---------------------------------------------------------------------------
# DataAlignmentHelper – format_metadata_log
# ---------------------------------------------------------------------------

class TestFormatMetadataLog:
    """Tests for format_metadata_log."""

    def test_single_timeframe_format(self):
        helper = _make_helper(_backtest_config())
        df = _make_df(periods=5)
        _, meta = helper.get_aligned_candle(df, '5m')
        log_str = helper.format_metadata_log(meta)
        assert isinstance(log_str, str)
        assert '5m' in log_str

    def test_multi_timeframe_format(self):
        helper = _make_helper(_backtest_config())
        data = {
            '5m': _make_df(periods=5, freq='5min'),
            '15m': _make_df(periods=5, freq='15min'),
        }
        multi_meta = helper.get_multi_timeframe_metadata(data)
        log_str = helper.format_metadata_log(multi_meta)
        assert isinstance(log_str, str)
        assert '5m' in log_str
        assert '15m' in log_str


# ---------------------------------------------------------------------------
# Convenience function get_aligned_candle
# ---------------------------------------------------------------------------

class TestGetAlignedCandleFunction:
    """Tests for the module-level get_aligned_candle convenience function."""

    def test_returns_tuple(self):
        df = _make_df(periods=5)
        # Pass a non-existent config path so it falls back to defaults (backtest mode)
        candle, meta = get_aligned_candle(df, '5m', config_path='/nonexistent/config.yaml')
        assert isinstance(candle, pd.Series)
        assert isinstance(meta, dict)

    def test_uses_backtest_defaults(self):
        df = _make_df(periods=5)
        _, meta = get_aligned_candle(df, '5m', config_path='/nonexistent/config.yaml')
        # Default mode is backtest → should use the penultimate candle
        assert meta['index'] == -2


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
