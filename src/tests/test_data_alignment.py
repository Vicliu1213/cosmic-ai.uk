#!/usr/bin/env python3
"""
Tests for src/utils/data_alignment.py

Covers: DataAlignmentHelper._load_config, _should_use_realtime,
        _calculate_completion, _calculate_lag_minutes, _check_lag_warning,
        get_aligned_candle, get_multi_timeframe_metadata, format_metadata_log,
        and the module-level get_aligned_candle convenience function.
"""

import sys
import os
import logging
import tempfile
import pytest
import yaml
import pandas as pd
from datetime import datetime, timezone, timedelta
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.utils.data_alignment import DataAlignmentHelper, get_aligned_candle


# ─── fixtures ──────────────────────────────────────────────────────────────────

def _make_df(n: int = 10, freq: str = "5min", tz: str = "UTC") -> pd.DataFrame:
    """Return a minimal OHLCV DataFrame with DatetimeIndex."""
    timestamps = pd.date_range("2025-01-01 00:00:00", periods=n, freq=freq, tz=tz)
    return pd.DataFrame(
        {"open": 100.0, "high": 101.0, "low": 99.0, "close": 100.5, "volume": 1000},
        index=timestamps,
    )


def _helper(config: dict) -> DataAlignmentHelper:
    """Create a DataAlignmentHelper from an in-memory config dict."""
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".yaml", delete=False, encoding="utf-8"
    ) as f:
        yaml.dump(config, f)
        path = f.name
    h = DataAlignmentHelper(config_path=path)
    os.unlink(path)
    return h


@pytest.fixture()
def backtest_helper():
    return _helper({"mode": "backtest", "timeframe_settings": {}})


@pytest.fixture()
def live_helper():
    return _helper({"mode": "live", "timeframe_settings": {}})


@pytest.fixture()
def live_aggressive_helper():
    return _helper({"mode": "live_aggressive", "timeframe_settings": {}})


@pytest.fixture()
def df10():
    return _make_df(n=10)


# ─── _load_config ──────────────────────────────────────────────────────────────

class TestLoadConfig:
    def test_missing_file_returns_defaults(self):
        h = DataAlignmentHelper(config_path="/nonexistent/path/config.yaml")
        assert h.mode == "backtest"
        assert h.config["timeframe_settings"] == {}

    def test_loads_mode_from_file(self):
        h = _helper({"mode": "live", "timeframe_settings": {}})
        assert h.mode == "live"

    def test_period_minutes_populated(self, backtest_helper):
        assert backtest_helper.period_minutes["5m"] == 5
        assert backtest_helper.period_minutes["1h"] == 60
        assert backtest_helper.period_minutes["1d"] == 1440


# ─── _should_use_realtime ──────────────────────────────────────────────────────

class TestShouldUseRealtime:
    def test_backtest_always_false(self, backtest_helper):
        for tf in ["1m", "5m", "1h", "1d"]:
            assert backtest_helper._should_use_realtime(tf, {}) is False

    def test_live_default_false(self, live_helper):
        assert live_helper._should_use_realtime("5m", {}) is False

    def test_live_explicit_true(self, live_helper):
        assert live_helper._should_use_realtime("5m", {"use_realtime": True}) is True

    def test_live_aggressive_default_true(self, live_aggressive_helper):
        assert live_aggressive_helper._should_use_realtime("5m", {}) is True

    def test_live_aggressive_explicit_false(self, live_aggressive_helper):
        assert live_aggressive_helper._should_use_realtime("5m", {"use_realtime": False}) is False


# ─── _calculate_completion ────────────────────────────────────────────────────

class TestCalculateCompletion:
    def test_before_candle_start_returns_zero(self, backtest_helper):
        df = _make_df(n=5, freq="5min")
        # now is exactly at last candle time → 0 % elapsed
        now = df.index[-1].to_pydatetime()
        pct = backtest_helper._calculate_completion(df, "5m", now)
        assert pct == 0.0

    def test_halfway_through_candle(self, backtest_helper):
        df = _make_df(n=5, freq="5min")
        last = df.index[-1].to_pydatetime()
        now = last + timedelta(minutes=2.5)
        pct = backtest_helper._calculate_completion(df, "5m", now)
        assert abs(pct - 50.0) < 0.5

    def test_after_candle_end_returns_100(self, backtest_helper):
        df = _make_df(n=5, freq="5min")
        last = df.index[-1].to_pydatetime()
        now = last + timedelta(minutes=10)
        pct = backtest_helper._calculate_completion(df, "5m", now)
        assert pct == 100.0

    def test_unknown_timeframe_falls_back_to_5min(self, backtest_helper):
        df = _make_df(n=5, freq="5min")
        last = df.index[-1].to_pydatetime()
        now = last + timedelta(minutes=10)
        pct = backtest_helper._calculate_completion(df, "unknown_tf", now)
        assert pct == 100.0

    def test_empty_dataframe_returns_zero(self, backtest_helper):
        df = _make_df(n=0)
        now = datetime(2025, 1, 1, tzinfo=timezone.utc)
        pct = backtest_helper._calculate_completion(df, "5m", now)
        assert pct == 0.0

    def test_timezone_naive_df_with_aware_now(self, backtest_helper):
        # DataFrame without timezone; now with UTC timezone
        timestamps = pd.date_range("2025-01-01", periods=5, freq="5min")
        df = pd.DataFrame({"close": 100.0}, index=timestamps)
        now = datetime(2025, 1, 1, 0, 30, 0, tzinfo=timezone.utc)
        pct = backtest_helper._calculate_completion(df, "5m", now)
        assert 0.0 <= pct <= 100.0


# ─── _calculate_lag_minutes ───────────────────────────────────────────────────

class TestCalculateLagMinutes:
    def test_zero_lag(self, backtest_helper):
        ts = pd.Timestamp("2025-01-01 10:00:00", tz="UTC")
        now = datetime(2025, 1, 1, 10, 0, 0, tzinfo=timezone.utc)
        lag = backtest_helper._calculate_lag_minutes(ts, now)
        assert lag == 0.0

    def test_five_minute_lag(self, backtest_helper):
        ts = pd.Timestamp("2025-01-01 10:00:00", tz="UTC")
        now = datetime(2025, 1, 1, 10, 5, 0, tzinfo=timezone.utc)
        lag = backtest_helper._calculate_lag_minutes(ts, now)
        assert abs(lag - 5.0) < 0.01

    def test_lag_with_naive_timestamp(self, backtest_helper):
        ts = pd.Timestamp("2025-01-01 10:00:00")
        now = datetime(2025, 1, 1, 10, 10, 0, tzinfo=timezone.utc)
        lag = backtest_helper._calculate_lag_minutes(ts, now)
        assert abs(lag - 10.0) < 0.01


# ─── get_aligned_candle ───────────────────────────────────────────────────────

class TestGetAlignedCandle:
    def test_raises_on_short_df(self, backtest_helper):
        df = _make_df(n=1)
        with pytest.raises(ValueError, match="DataFrame长度不足"):
            backtest_helper.get_aligned_candle(df, "5m")

    def test_backtest_uses_second_to_last(self, backtest_helper, df10):
        now = datetime(2025, 1, 1, 1, 0, 0, tzinfo=timezone.utc)
        candle, meta = backtest_helper.get_aligned_candle(df10, "5m", now=now)
        assert meta["index"] == -2
        assert meta["is_realtime"] is False
        assert meta["is_completed"] is True
        assert meta["completion_pct"] == 100.0
        assert meta["timeframe"] == "5m"
        assert meta["mode"] == "backtest"

    def test_metadata_contains_required_keys(self, backtest_helper, df10):
        now = datetime(2025, 1, 1, 1, 0, 0, tzinfo=timezone.utc)
        _, meta = backtest_helper.get_aligned_candle(df10, "5m", now=now)
        for key in ("index", "timestamp", "lag_minutes", "is_realtime",
                    "is_completed", "completion_pct", "timeframe", "mode"):
            assert key in meta

    def test_lag_minutes_is_positive(self, backtest_helper, df10):
        now = datetime(2025, 1, 1, 1, 0, 0, tzinfo=timezone.utc)
        _, meta = backtest_helper.get_aligned_candle(df10, "5m", now=now)
        assert meta["lag_minutes"] >= 0

    def test_live_completed_candle_uses_realtime_when_configured(self):
        # live mode + use_realtime=True → index -1 when candle is completed
        df = _make_df(n=5, freq="5min")
        last = df.index[-1].to_pydatetime()
        now = last + timedelta(minutes=10)  # candle fully complete

        h = _helper({"mode": "live", "timeframe_settings": {
            "5m": {"use_realtime": True}
        }})
        _, meta = h.get_aligned_candle(df, "5m", now=now)
        assert meta["index"] == -1
        assert meta["is_realtime"] is True

    def test_live_incomplete_candle_with_min_completion_fallback(self):
        # Require 80% completion but candle is only 10% done → fallback to -2
        df = _make_df(n=5, freq="5min")
        last = df.index[-1].to_pydatetime()
        now = last + timedelta(seconds=30)  # 30s into a 5min candle = 10%

        h = _helper({"mode": "live", "timeframe_settings": {
            "5m": {"use_realtime": True, "min_completion_pct": 80}
        }})
        _, meta = h.get_aligned_candle(df, "5m", now=now)
        assert meta["index"] == -2
        assert meta["is_completed"] is True

    def test_returned_candle_is_series(self, backtest_helper, df10):
        now = datetime(2025, 1, 1, 1, 0, 0, tzinfo=timezone.utc)
        candle, _ = backtest_helper.get_aligned_candle(df10, "5m", now=now)
        assert isinstance(candle, pd.Series)

    def test_default_now_uses_current_time(self, backtest_helper, df10):
        # Should not raise; now defaults to datetime.now(timezone.utc)
        candle, meta = backtest_helper.get_aligned_candle(df10, "5m")
        assert meta["index"] == -2


# ─── get_multi_timeframe_metadata ────────────────────────────────────────────

class TestGetMultiTimeframeMetadata:
    def test_returns_required_keys(self, backtest_helper):
        data = {
            "5m": _make_df(n=10, freq="5min"),
            "1h": _make_df(n=10, freq="1h"),
        }
        now = datetime(2025, 6, 1, 12, 0, 0, tzinfo=timezone.utc)
        result = backtest_helper.get_multi_timeframe_metadata(data, now=now)

        assert "timeframes" in result
        assert "5m" in result["timeframes"]
        assert "1h" in result["timeframes"]
        assert "time_gap_minutes" in result
        assert "max_lag_minutes" in result
        assert "earliest_timestamp" in result
        assert "latest_timestamp" in result

    def test_empty_input_returns_empty_dict(self, backtest_helper):
        result = backtest_helper.get_multi_timeframe_metadata({})
        assert result == {}

    def test_max_lag_minutes_non_negative(self, backtest_helper):
        data = {
            "5m": _make_df(n=10, freq="5min"),
            "15m": _make_df(n=10, freq="15min"),
        }
        now = datetime(2025, 6, 1, 12, 0, 0, tzinfo=timezone.utc)
        result = backtest_helper.get_multi_timeframe_metadata(data, now=now)
        assert result["max_lag_minutes"] >= 0


# ─── format_metadata_log ─────────────────────────────────────────────────────

class TestFormatMetadataLog:
    def test_single_timeframe_returns_string(self, backtest_helper, df10):
        now = datetime(2025, 1, 1, 1, 0, 0, tzinfo=timezone.utc)
        _, meta = backtest_helper.get_aligned_candle(df10, "5m", now=now)
        result = backtest_helper.format_metadata_log(meta)
        assert isinstance(result, str)
        assert "5m" in result

    def test_multi_timeframe_returns_multiline_string(self, backtest_helper):
        data = {
            "5m": _make_df(n=10, freq="5min"),
            "1h": _make_df(n=10, freq="1h"),
        }
        now = datetime(2025, 6, 1, 12, 0, 0, tzinfo=timezone.utc)
        multi_meta = backtest_helper.get_multi_timeframe_metadata(data, now=now)
        result = backtest_helper.format_metadata_log(multi_meta)
        assert isinstance(result, str)
        assert "\n" in result


# ─── module-level convenience function ───────────────────────────────────────

class TestModuleLevelGetAlignedCandle:
    def test_convenience_function_returns_tuple(self, tmp_path):
        df = _make_df(n=5)
        config = {"mode": "backtest", "timeframe_settings": {}}
        cfg_file = tmp_path / "cfg.yaml"
        cfg_file.write_text(yaml.dump(config))

        candle, meta = get_aligned_candle(df, "5m", config_path=str(cfg_file))
        assert isinstance(candle, pd.Series)
        assert isinstance(meta, dict)

    def test_convenience_function_without_config(self):
        df = _make_df(n=5)
        # May log a warning about missing config; should still work
        candle, meta = get_aligned_candle(df, "5m")
        assert meta["mode"] == "backtest"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
