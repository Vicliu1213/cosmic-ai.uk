#!/usr/bin/env python3
"""
Tests for src/risk/manager.py

Covers: RiskManager.validate_format, calculate_position_size,
        calculate_stop_loss_price, calculate_take_profit_price,
        record_trade, update_drawdown, get_risk_status.
"""

import sys
import os
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.risk.manager import RiskManager


# ─── helpers ──────────────────────────────────────────────────────────────────

def _valid_open_long_decision(**overrides) -> dict:
    """Return a minimally valid open_long decision (R:R >= 2.0 required).

    entry=48000, SL=45000 (risk=3000), TP=54000 (reward=6000) → R:R=2.0
    """
    base = {
        "symbol": "BTCUSDT",
        "action": "open_long",
        "reasoning": "Test signal",
        "leverage": 2,
        "position_size_usd": 100,
        "stop_loss": 45000.0,
        "take_profit": 54000.0,
        "current_price": 48000.0,
    }
    base.update(overrides)
    return base


def _valid_open_short_decision(**overrides) -> dict:
    """Return a minimally valid open_short decision (R:R >= 2.0 required).

    entry=48000, SL=51000 (risk=3000), TP=42000 (reward=6000) → R:R=2.0
    """
    base = {
        "symbol": "BTCUSDT",
        "action": "open_short",
        "reasoning": "Test signal",
        "leverage": 2,
        "position_size_usd": 100,
        "stop_loss": 51000.0,
        "take_profit": 42000.0,
        "current_price": 48000.0,
    }
    base.update(overrides)
    return base


def _rm() -> RiskManager:
    return RiskManager()


# ─── validate_format ─────────────────────────────────────────────────────────

class TestValidateFormatMissingFields:
    """Missing required fields must fail validation."""

    def test_missing_symbol(self):
        d = _valid_open_long_decision()
        del d["symbol"]
        ok, msg = _rm().validate_format(d)
        assert not ok
        assert "symbol" in msg

    def test_missing_action(self):
        # A missing action is normalised to "wait" (passive), so the
        # decision is considered valid (no open-action fields required).
        d = _valid_open_long_decision()
        del d["action"]
        ok, msg = _rm().validate_format(d)
        # validate_format normalises the missing action to "wait",
        # which only needs symbol + action + reasoning → should pass.
        assert ok, f"Expected wait (passive) to be valid, got: {msg}"

    def test_missing_reasoning(self):
        d = _valid_open_long_decision()
        del d["reasoning"]
        ok, msg = _rm().validate_format(d)
        assert not ok
        assert "reasoning" in msg

    def test_empty_symbol(self):
        d = _valid_open_long_decision(symbol="")
        ok, msg = _rm().validate_format(d)
        assert not ok


class TestValidateFormatPassiveActions:
    """Passive (wait/hold) actions only need symbol + action + reasoning."""

    def test_wait_is_valid(self):
        d = {"symbol": "BTCUSDT", "action": "wait", "reasoning": "No signal"}
        ok, msg = _rm().validate_format(d)
        assert ok, msg

    def test_hold_is_valid(self):
        d = {"symbol": "BTCUSDT", "action": "hold", "reasoning": "Holding"}
        ok, msg = _rm().validate_format(d)
        assert ok, msg

    def test_close_long_is_valid(self):
        d = {"symbol": "BTCUSDT", "action": "close_long", "reasoning": "TP hit"}
        ok, msg = _rm().validate_format(d)
        assert ok, msg


class TestValidateFormatOpenLong:
    def test_valid_open_long_passes(self):
        ok, msg = _rm().validate_format(_valid_open_long_decision())
        assert ok, msg

    def test_missing_leverage(self):
        d = _valid_open_long_decision()
        del d["leverage"]
        ok, msg = _rm().validate_format(d)
        assert not ok
        assert "leverage" in msg

    def test_missing_position_size_usd(self):
        d = _valid_open_long_decision()
        del d["position_size_usd"]
        ok, msg = _rm().validate_format(d)
        assert not ok

    def test_missing_stop_loss(self):
        d = _valid_open_long_decision()
        del d["stop_loss"]
        ok, msg = _rm().validate_format(d)
        assert not ok

    def test_missing_take_profit(self):
        d = _valid_open_long_decision()
        del d["take_profit"]
        ok, msg = _rm().validate_format(d)
        assert not ok

    def test_leverage_too_high(self):
        d = _valid_open_long_decision(leverage=10)
        ok, msg = _rm().validate_format(d)
        assert not ok
        assert "leverage" in msg.lower() or "1-5" in msg

    def test_leverage_zero(self):
        d = _valid_open_long_decision(leverage=0)
        ok, msg = _rm().validate_format(d)
        assert not ok

    def test_string_leverage(self):
        d = _valid_open_long_decision(leverage="2x")
        ok, msg = _rm().validate_format(d)
        assert not ok

    def test_long_stop_loss_above_entry_fails(self):
        # For open_long, SL must be < entry price
        d = _valid_open_long_decision(
            current_price=48000.0, stop_loss=49000.0, take_profit=55000.0
        )
        ok, msg = _rm().validate_format(d)
        assert not ok
        assert "止损" in msg or "stop" in msg.lower()

    def test_long_take_profit_below_entry_fails(self):
        d = _valid_open_long_decision(
            current_price=48000.0, stop_loss=45000.0, take_profit=47000.0
        )
        ok, msg = _rm().validate_format(d)
        assert not ok

    def test_low_rr_ratio_fails(self):
        # risk 1000, reward 500 → RR = 0.5 < 2.0
        d = _valid_open_long_decision(
            current_price=50000.0, stop_loss=49000.0, take_profit=50500.0
        )
        ok, msg = _rm().validate_format(d)
        assert not ok
        assert "R:R" in msg or "2.0" in msg

    def test_reasoning_too_long_fails(self):
        d = _valid_open_long_decision(reasoning=" ".join(["word"] * 60))
        ok, msg = _rm().validate_format(d)
        assert not ok
        assert "reasoning" in msg.lower() or "过长" in msg


class TestValidateFormatOpenShort:
    def test_valid_open_short_passes(self):
        ok, msg = _rm().validate_format(_valid_open_short_decision())
        assert ok, msg

    def test_short_stop_loss_below_entry_fails(self):
        d = _valid_open_short_decision(
            current_price=48000.0, stop_loss=47000.0, take_profit=44000.0
        )
        ok, msg = _rm().validate_format(d)
        assert not ok

    def test_short_take_profit_above_entry_fails(self):
        d = _valid_open_short_decision(
            current_price=48000.0, stop_loss=52000.0, take_profit=50000.0
        )
        ok, msg = _rm().validate_format(d)
        assert not ok


class TestValidateFormatRawResponse:
    """When raw_response is provided it must contain the expected XML/JSON tags."""

    def _wrap(self, decision_json: str) -> str:
        return (
            f"<reasoning>test reasoning</reasoning>"
            f"<decision>```json\n[{decision_json}]\n```</decision>"
        )

    def test_valid_raw_response_passes(self):
        d = _valid_open_long_decision()
        import json
        raw = self._wrap(json.dumps(d))
        ok, msg = _rm().validate_format(d, raw_response=raw)
        assert ok, msg

    def test_missing_reasoning_tags_fails(self):
        d = _valid_open_long_decision()
        raw = "<decision>```json\n[{}]\n```</decision>"
        ok, msg = _rm().validate_format(d, raw_response=raw)
        assert not ok
        assert "reasoning" in msg

    def test_missing_decision_tags_fails(self):
        d = _valid_open_long_decision()
        raw = "<reasoning>ok</reasoning>```json\n[{}]\n```"
        ok, msg = _rm().validate_format(d, raw_response=raw)
        assert not ok
        assert "decision" in msg

    def test_missing_json_block_fails(self):
        d = _valid_open_long_decision()
        raw = "<reasoning>ok</reasoning><decision>{}</decision>"
        ok, msg = _rm().validate_format(d, raw_response=raw)
        assert not ok

    def test_non_array_json_fails(self):
        # The check only activates when JSON is in [...] form but doesn't start with [{
        d = _valid_open_long_decision()
        raw = (
            "<reasoning>ok</reasoning>"
            "<decision>```json\n[\"open_long\"]\n```</decision>"
        )
        ok, msg = _rm().validate_format(d, raw_response=raw)
        assert not ok


# ─── calculate_position_size ─────────────────────────────────────────────────

class TestCalculatePositionSize:
    def test_basic_calculation(self):
        rm = _rm()
        qty = rm.calculate_position_size(
            account_balance=10000,
            position_pct=10,
            leverage=5,
            current_price=50000,
        )
        # 10000 * 0.10 * 5 / 50000 = 0.1
        assert abs(qty - 0.1) < 1e-3

    def test_minimum_quantity_enforced(self):
        # Very small balance should produce at least 0.001
        rm = _rm()
        qty = rm.calculate_position_size(1.0, 0.1, 1, 1_000_000)
        assert qty >= 0.001

    def test_result_rounded_to_3_decimals(self):
        rm = _rm()
        qty = rm.calculate_position_size(10000, 5, 3, 47123.456)
        decimals = len(str(qty).split(".")[1]) if "." in str(qty) else 0
        assert decimals <= 3

    def test_high_leverage_increases_quantity(self):
        rm = _rm()
        qty_low = rm.calculate_position_size(10000, 10, 1, 50000)
        qty_high = rm.calculate_position_size(10000, 10, 5, 50000)
        assert qty_high > qty_low


# ─── calculate_stop_loss_price ───────────────────────────────────────────────

class TestCalculateStopLossPrice:
    def test_long_stop_loss_below_entry(self):
        rm = _rm()
        sl = rm.calculate_stop_loss_price(50000.0, 2.0, "LONG")
        assert sl == 49000.0
        assert sl < 50000.0

    def test_short_stop_loss_above_entry(self):
        rm = _rm()
        sl = rm.calculate_stop_loss_price(50000.0, 2.0, "SHORT")
        assert sl == 51000.0
        assert sl > 50000.0

    def test_result_rounded_to_2_decimals(self):
        rm = _rm()
        sl = rm.calculate_stop_loss_price(49999.999, 1.5, "LONG")
        assert round(sl, 2) == sl

    def test_zero_percent_sl(self):
        rm = _rm()
        sl = rm.calculate_stop_loss_price(50000.0, 0.0, "LONG")
        assert sl == 50000.0


# ─── calculate_take_profit_price ─────────────────────────────────────────────

class TestCalculateTakeProfitPrice:
    def test_long_take_profit_above_entry(self):
        rm = _rm()
        tp = rm.calculate_take_profit_price(50000.0, 5.0, "LONG")
        assert tp == 52500.0
        assert tp > 50000.0

    def test_short_take_profit_below_entry(self):
        rm = _rm()
        tp = rm.calculate_take_profit_price(50000.0, 5.0, "SHORT")
        assert tp == 47500.0
        assert tp < 50000.0

    def test_result_rounded_to_2_decimals(self):
        rm = _rm()
        tp = rm.calculate_take_profit_price(49999.999, 3.0, "LONG")
        assert round(tp, 2) == tp


# ─── record_trade ────────────────────────────────────────────────────────────

class TestRecordTrade:
    def test_trade_appended_to_history(self):
        rm = _rm()
        rm.record_trade({"pnl": 100.0, "symbol": "BTC"})
        assert len(rm.trade_history) == 1

    def test_winning_trade_resets_consecutive_losses(self):
        rm = _rm()
        rm.consecutive_losses = 2
        rm.record_trade({"pnl": 50.0})
        assert rm.consecutive_losses == 0

    def test_losing_trade_increments_consecutive_losses(self):
        rm = _rm()
        rm.record_trade({"pnl": -10.0})
        assert rm.consecutive_losses == 1

    def test_consecutive_losses_accumulate(self):
        rm = _rm()
        for _ in range(3):
            rm.record_trade({"pnl": -5.0})
        assert rm.consecutive_losses == 3

    def test_win_after_losses_resets_count(self):
        rm = _rm()
        rm.record_trade({"pnl": -5.0})
        rm.record_trade({"pnl": -5.0})
        rm.record_trade({"pnl": 20.0})
        assert rm.consecutive_losses == 0

    def test_multiple_trades_stored(self):
        rm = _rm()
        for i in range(5):
            rm.record_trade({"pnl": float(i)})
        assert len(rm.trade_history) == 5


# ─── update_drawdown ─────────────────────────────────────────────────────────

class TestUpdateDrawdown:
    def test_no_drawdown(self):
        rm = _rm()
        rm.update_drawdown(10000, 10000)
        assert rm.total_drawdown_pct == 0.0

    def test_drawdown_calculated_correctly(self):
        rm = _rm()
        rm.update_drawdown(9000, 10000)
        assert abs(rm.total_drawdown_pct - 10.0) < 0.01

    def test_fifty_percent_drawdown(self):
        rm = _rm()
        rm.update_drawdown(5000, 10000)
        assert abs(rm.total_drawdown_pct - 50.0) < 0.01

    def test_zero_peak_balance_does_not_raise(self):
        rm = _rm()
        rm.update_drawdown(1000, 0)  # should not raise
        # drawdown stays at its previous value (0 from init)
        assert rm.total_drawdown_pct == 0.0


# ─── get_risk_status ─────────────────────────────────────────────────────────

class TestGetRiskStatus:
    def test_fresh_manager_can_trade(self):
        rm = _rm()
        status = rm.get_risk_status()
        assert status["can_trade"] is True

    def test_status_keys_present(self):
        rm = _rm()
        status = rm.get_risk_status()
        for key in ("consecutive_losses", "total_drawdown_pct", "can_trade", "total_trades"):
            assert key in status

    def test_total_trades_reflects_history(self):
        rm = _rm()
        rm.record_trade({"pnl": 10})
        rm.record_trade({"pnl": -5})
        assert rm.get_risk_status()["total_trades"] == 2

    def test_too_many_consecutive_losses_disables_trading(self):
        rm = _rm()
        for _ in range(rm.max_consecutive_losses):
            rm.record_trade({"pnl": -1.0})
        status = rm.get_risk_status()
        assert status["can_trade"] is False

    def test_high_drawdown_disables_trading(self):
        rm = _rm()
        rm.update_drawdown(0, 10000)  # 100% drawdown
        assert rm.get_risk_status()["can_trade"] is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
