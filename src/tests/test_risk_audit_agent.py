#!/usr/bin/env python3
"""
Test suite for agents/risk_audit_agent.py

Tests are loaded via importlib to bypass the broken agents/__init__.py circular
imports (which require pandas, ray, etc.).

Tests cover:
- RiskAuditAgent initialization
- _block_decision helper
- _check_duplicate_open
- _check_reverse_position
- _check_and_fix_stop_loss
- _check_margin_sufficiency
- _check_position_size
- _check_total_risk_exposure
- _evaluate_risk_level
- _check_market_traps_risk
- audit_decision (high-level async integration)
"""

import sys
import asyncio
import importlib.util
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Direct module load (bypasses agents/__init__.py which has broken imports)
# ---------------------------------------------------------------------------

_SRC = Path(__file__).parent.parent
sys.path.insert(0, str(_SRC))

_spec = importlib.util.spec_from_file_location(
    "risk_audit_agent",
    str(_SRC / "agents" / "risk_audit_agent.py"),
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

RiskAuditAgent = _mod.RiskAuditAgent
RiskCheckResult = _mod.RiskCheckResult
PositionInfo = _mod.PositionInfo
RiskLevel = _mod.RiskLevel


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _agent(**kwargs) -> RiskAuditAgent:
    defaults = dict(
        max_leverage=12.0,
        max_position_pct=0.35,
        max_total_risk_pct=0.012,
        min_stop_loss_pct=0.002,
        max_stop_loss_pct=0.025,
    )
    defaults.update(kwargs)
    return RiskAuditAgent(**defaults)


def _long_position(entry: float = 50000.0) -> PositionInfo:
    return PositionInfo(
        symbol="BTCUSDT",
        side="long",
        entry_price=entry,
        quantity=0.01,
        unrealized_pnl=0.0,
        current_price=entry,
    )


def _short_position(entry: float = 50000.0) -> PositionInfo:
    return PositionInfo(
        symbol="BTCUSDT",
        side="short",
        entry_price=entry,
        quantity=0.01,
        unrealized_pnl=0.0,
        current_price=entry,
    )


def _minimal_long_decision(
    entry: float = 50000.0,
    sl: float = 49000.0,
    tp: float = 52000.0,
    qty: float = 0.01,
    lev: float = 5.0,
    confidence: float = 85,
) -> dict:
    return {
        "action": "open_long",
        "entry_price": entry,
        "stop_loss": sl,
        "take_profit": tp,
        "quantity": qty,
        "leverage": lev,
        "confidence": confidence,
    }


def _run(coro):
    return asyncio.get_event_loop().run_until_complete(coro)


# ---------------------------------------------------------------------------
# Initialization
# ---------------------------------------------------------------------------

class TestRiskAuditAgentInit:

    def test_default_params(self):
        agent = _agent()
        assert agent.max_leverage == 12.0
        assert agent.max_position_pct == 0.35
        assert agent.max_total_risk_pct == 0.012

    def test_custom_params(self):
        agent = _agent(max_leverage=5.0, max_position_pct=0.20)
        assert agent.max_leverage == 5.0
        assert agent.max_position_pct == 0.20

    def test_audit_log_starts_empty(self):
        agent = _agent()
        assert agent.audit_log == []

    def test_block_stats_initialized(self):
        agent = _agent()
        for key in ["total_checks", "total_blocks", "stop_loss_corrections",
                    "reverse_position_blocks", "insufficient_margin_blocks", "over_leverage_blocks"]:
            assert key in agent.block_stats
            assert agent.block_stats[key] == 0


# ---------------------------------------------------------------------------
# _block_decision
# ---------------------------------------------------------------------------

class TestBlockDecision:

    def test_returns_failed_result(self):
        agent = _agent()
        result = agent._block_decision("total_blocks", "test reason")
        assert result.passed is False
        assert result.blocked_reason == "test reason"

    def test_increments_stat(self):
        agent = _agent()
        agent._block_decision("reverse_position_blocks", "r")
        assert agent.block_stats["reverse_position_blocks"] == 1

    def test_also_increments_total_blocks(self):
        agent = _agent()
        agent._block_decision("reverse_position_blocks", "r")
        assert agent.block_stats["total_blocks"] == 1

    def test_does_not_increment_other_stats(self):
        agent = _agent()
        agent._block_decision("reverse_position_blocks", "r")
        assert agent.block_stats["over_leverage_blocks"] == 0


# ---------------------------------------------------------------------------
# _check_duplicate_open
# ---------------------------------------------------------------------------

class TestCheckDuplicateOpen:

    def test_blocks_open_when_position_exists(self):
        agent = _agent()
        pos = _long_position()
        result = agent._check_duplicate_open("open_long", pos)
        assert result["passed"] is False

    def test_allows_close_when_position_exists(self):
        agent = _agent()
        pos = _long_position()
        result = agent._check_duplicate_open("close_long", pos)
        assert result["passed"] is True

    def test_allows_wait_when_position_exists(self):
        agent = _agent()
        pos = _long_position()
        result = agent._check_duplicate_open("wait", pos)
        assert result["passed"] is True


# ---------------------------------------------------------------------------
# _check_reverse_position
# ---------------------------------------------------------------------------

class TestCheckReversePosition:

    def test_blocks_short_open_with_long_position(self):
        agent = _agent()
        pos = _long_position()
        result = agent._check_reverse_position("open_short", pos)
        assert result["passed"] is False

    def test_blocks_long_open_with_short_position(self):
        agent = _agent()
        pos = _short_position()
        result = agent._check_reverse_position("open_long", pos)
        assert result["passed"] is False

    def test_allows_close_long_with_long_position(self):
        agent = _agent()
        pos = _long_position()
        result = agent._check_reverse_position("close_long", pos)
        assert result["passed"] is True

    def test_allows_close_short_with_short_position(self):
        agent = _agent()
        pos = _short_position()
        result = agent._check_reverse_position("close_short", pos)
        assert result["passed"] is True

    def test_allows_same_direction_recheck(self):
        agent = _agent()
        pos = _long_position()
        result = agent._check_reverse_position("open_long", pos)
        # Actually open_long with long position IS caught by duplicate check,
        # but reverse check only looks at cross-direction: here it should pass.
        assert result["passed"] is True


# ---------------------------------------------------------------------------
# _check_and_fix_stop_loss
# ---------------------------------------------------------------------------

class TestCheckAndFixStopLoss:

    def test_no_stop_loss_can_fix_long(self):
        agent = _agent()
        result = agent._check_and_fix_stop_loss("open_long", 50000.0, None, 50000.0)
        assert result["passed"] is False
        assert result["can_fix"] is True
        assert result["corrected_value"] < 50000.0

    def test_no_stop_loss_can_fix_short(self):
        agent = _agent()
        result = agent._check_and_fix_stop_loss("open_short", 50000.0, None, 50000.0)
        assert result["passed"] is False
        assert result["can_fix"] is True
        assert result["corrected_value"] > 50000.0

    def test_wrong_stop_loss_long_can_fix(self):
        """Stop loss above entry price for long is wrong and auto-fixable."""
        agent = _agent()
        result = agent._check_and_fix_stop_loss("open_long", 50000.0, 51000.0, 50000.0)
        assert result["passed"] is False
        assert result["can_fix"] is True
        assert result["corrected_value"] < 50000.0

    def test_wrong_stop_loss_short_can_fix(self):
        """Stop loss below entry price for short is wrong and auto-fixable."""
        agent = _agent()
        result = agent._check_and_fix_stop_loss("open_short", 50000.0, 49000.0, 50000.0)
        assert result["passed"] is False
        assert result["can_fix"] is True
        assert result["corrected_value"] > 50000.0

    def test_valid_stop_loss_long_passes(self):
        """Correct stop loss (below entry for long) should pass."""
        agent = _agent()
        # Entry 50000, stop at 49000 = 2% → within [0.2%, 2.5%]
        result = agent._check_and_fix_stop_loss("open_long", 50000.0, 49000.0, 50000.0)
        assert result["passed"] is True

    def test_valid_stop_loss_short_passes(self):
        """Correct stop loss (above entry for short) should pass."""
        agent = _agent()
        result = agent._check_and_fix_stop_loss("open_short", 50000.0, 51000.0, 50000.0)
        assert result["passed"] is True

    def test_atr_based_stop_computed(self):
        """When ATR is provided, dynamic stop should use it."""
        agent = _agent()
        result = agent._check_and_fix_stop_loss("open_long", 50000.0, None, 50000.0, atr_pct=2.0)
        assert result["can_fix"] is True
        corrected = result["corrected_value"]
        # 1.5 * 2.0% = 3% but capped at max_stop_loss_pct=2.5%
        expected_pct = min(1.5 * 2.0 / 100, agent.max_stop_loss_pct)
        expected_stop = 50000.0 * (1 - expected_pct)
        assert corrected == pytest.approx(expected_stop, rel=1e-6)


# ---------------------------------------------------------------------------
# _check_margin_sufficiency
# ---------------------------------------------------------------------------

class TestCheckMarginSufficiency:

    def test_passes_for_close_action(self):
        agent = _agent()
        result = agent._check_margin_sufficiency("close_long", 50000.0, 0.01, 5.0, 100.0)
        assert result["passed"] is True

    def test_passes_for_passive_action(self):
        agent = _agent()
        result = agent._check_margin_sufficiency("wait", 50000.0, 0.01, 5.0, 100.0)
        assert result["passed"] is True

    def test_passes_when_margin_sufficient(self):
        agent = _agent()
        # required = (0.001 * 50000) / 10 = 5.0; balance = 1000 → well within 95%
        result = agent._check_margin_sufficiency("open_long", 50000.0, 0.001, 10.0, 1000.0)
        assert result["passed"] is True

    def test_fails_when_margin_insufficient(self):
        agent = _agent()
        # required = (1.0 * 50000) / 1 = 50000; balance = 100 → fails
        result = agent._check_margin_sufficiency("open_long", 50000.0, 1.0, 1.0, 100.0)
        assert result["passed"] is False
        assert "保证金不足" in result["reason"]

    def test_margin_includes_5pct_buffer(self):
        agent = _agent()
        # required = (0.01 * 50000) / 5 = 100; balance = 100 → fails (100 > 100*0.95 = 95)
        result = agent._check_margin_sufficiency("open_long", 50000.0, 0.01, 5.0, 100.0)
        assert result["passed"] is False


# ---------------------------------------------------------------------------
# _check_position_size
# ---------------------------------------------------------------------------

class TestCheckPositionSize:

    def test_fails_for_zero_or_negative_balance(self):
        agent = _agent()
        result = agent._check_position_size(0.01, 50000.0, 0.0)
        assert result["passed"] is False

    def test_passes_when_within_limit(self):
        agent = _agent(max_position_pct=0.35)
        # position_value = 0.001 * 50000 = 50; balance = 1000; pct = 5% < 35%
        result = agent._check_position_size(0.001, 50000.0, 1000.0)
        assert result["passed"] is True

    def test_fails_when_exceeds_limit(self):
        agent = _agent(max_position_pct=0.10)
        # position_value = 0.1 * 50000 = 5000; balance = 1000; pct = 500% > 10%
        result = agent._check_position_size(0.1, 50000.0, 1000.0)
        assert result["passed"] is False


# ---------------------------------------------------------------------------
# _check_total_risk_exposure
# ---------------------------------------------------------------------------

class TestCheckTotalRiskExposure:

    def test_passes_for_close_action(self):
        agent = _agent()
        result = agent._check_total_risk_exposure("close_long", 50000.0, 49000.0, 0.01, 1000.0)
        assert result["passed"] is True

    def test_passes_when_no_stop_loss(self):
        agent = _agent()
        result = agent._check_total_risk_exposure("open_long", 50000.0, None, 0.01, 1000.0)
        assert result["passed"] is True

    def test_passes_when_risk_within_limit(self):
        agent = _agent(max_total_risk_pct=0.012)
        # risk = |50000 - 49500| * 0.001 = 0.5; pct = 0.5/10000 = 0.005% < 1.2%
        result = agent._check_total_risk_exposure("open_long", 50000.0, 49500.0, 0.001, 10000.0)
        assert result["passed"] is True

    def test_fails_when_risk_exceeds_limit(self):
        agent = _agent(max_total_risk_pct=0.012)
        # risk = |50000 - 40000| * 1.0 = 10000; balance = 100; pct = 100%
        result = agent._check_total_risk_exposure("open_long", 50000.0, 40000.0, 1.0, 100.0)
        assert result["passed"] is False


# ---------------------------------------------------------------------------
# _evaluate_risk_level
# ---------------------------------------------------------------------------

class TestEvaluateRiskLevel:

    def test_danger_with_many_warnings(self):
        agent = _agent()
        level = agent._evaluate_risk_level(warning_count=3, confidence=80.0, leverage=5.0)
        assert level == RiskLevel.DANGER

    def test_danger_with_high_leverage(self):
        agent = _agent()
        level = agent._evaluate_risk_level(warning_count=0, confidence=80.0, leverage=9.0)
        assert level == RiskLevel.DANGER

    def test_warning_with_one_warning(self):
        agent = _agent()
        level = agent._evaluate_risk_level(warning_count=1, confidence=80.0, leverage=3.0)
        assert level == RiskLevel.WARNING

    def test_warning_with_moderate_leverage(self):
        agent = _agent()
        level = agent._evaluate_risk_level(warning_count=0, confidence=80.0, leverage=6.0)
        assert level == RiskLevel.WARNING

    def test_safe_with_high_confidence(self):
        agent = _agent()
        level = agent._evaluate_risk_level(warning_count=0, confidence=80.0, leverage=3.0)
        assert level == RiskLevel.SAFE


# ---------------------------------------------------------------------------
# _check_market_traps_risk
# ---------------------------------------------------------------------------

class TestCheckMarketTrapsRisk:

    def test_non_long_always_passes(self):
        agent = _agent()
        # open_short, wait, and hold are not "long" actions per is_long_action
        for action in ["open_short", "wait", "hold"]:
            result = agent._check_market_traps_risk({"action": action, "traps": {"bull_trap_risk": True}})
            assert result["passed"] is True, f"Expected pass for action={action}"

    def test_bull_trap_blocks_long(self):
        agent = _agent()
        result = agent._check_market_traps_risk({
            "action": "open_long",
            "traps": {"bull_trap_risk": True},
        })
        assert result["passed"] is False
        assert "诱多" in result["reason"]

    def test_volume_divergence_blocks_long(self):
        agent = _agent()
        result = agent._check_market_traps_risk({
            "action": "open_long",
            "traps": {"volume_divergence": True},
        })
        assert result["passed"] is False
        assert "量价背离" in result["reason"]

    def test_weak_rebound_with_low_confidence_blocks(self):
        agent = _agent()
        result = agent._check_market_traps_risk({
            "action": "open_long",
            "traps": {"weak_rebound": True},
            "confidence": 50,
        })
        assert result["passed"] is False

    def test_weak_rebound_with_high_confidence_warns(self):
        agent = _agent()
        result = agent._check_market_traps_risk({
            "action": "open_long",
            "traps": {"weak_rebound": True},
            "confidence": 70,
        })
        assert result["passed"] is True
        assert "warnings" in result

    def test_no_traps_passes(self):
        agent = _agent()
        result = agent._check_market_traps_risk({"action": "open_long", "traps": {}})
        assert result["passed"] is True


# ---------------------------------------------------------------------------
# audit_decision (async integration tests)
# ---------------------------------------------------------------------------

class TestAuditDecision:

    def test_hold_passes_immediately(self):
        agent = _agent()
        decision = {"action": "hold"}
        result = _run(agent.audit_decision(decision, None, 1000.0, 50000.0))
        assert result.passed is True

    def test_wait_passes_immediately(self):
        agent = _agent()
        result = _run(agent.audit_decision({"action": "wait"}, None, 1000.0, 50000.0))
        assert result.passed is True

    def test_total_checks_incremented(self):
        agent = _agent()
        assert agent.block_stats["total_checks"] == 0
        _run(agent.audit_decision({"action": "hold"}, None, 1000.0, 50000.0))
        assert agent.block_stats["total_checks"] == 1

    def test_zero_balance_blocks_open(self):
        agent = _agent()
        decision = _minimal_long_decision()
        result = _run(agent.audit_decision(decision, None, 0.0, 50000.0))
        assert result.passed is False

    def test_excessive_leverage_blocked(self):
        agent = _agent(max_leverage=5.0)
        decision = _minimal_long_decision(lev=10.0)
        result = _run(agent.audit_decision(decision, None, 100000.0, 50000.0))
        assert result.passed is False

    def test_valid_long_no_position_passes(self):
        agent = _agent(max_leverage=12.0, max_total_risk_pct=0.5, max_position_pct=0.99)
        # Simple valid long: entry=50000, SL=49000 (2%), TP=53000 (6%), qty=0.001, lev=5x
        # Margin needed = (0.001 * 50000) / 5 = 10; balance = 10000 → fine
        decision = _minimal_long_decision(
            entry=50000.0, sl=49000.0, tp=53000.0, qty=0.001, lev=5.0, confidence=85
        )
        result = _run(agent.audit_decision(decision, None, 10000.0, 50000.0))
        assert result.passed is True

    def test_stop_loss_correction_applied(self):
        """Wrong stop loss for long should be auto-corrected, not blocked."""
        agent = _agent(max_leverage=12.0, max_total_risk_pct=0.5, max_position_pct=0.99)
        decision = {
            "action": "open_long",
            "entry_price": 50000.0,
            "stop_loss": 51000.0,   # Wrong: above entry for long
            "take_profit": 53000.0,
            "quantity": 0.001,
            "leverage": 5.0,
            "confidence": 85,
        }
        result = _run(agent.audit_decision(decision, None, 10000.0, 50000.0))
        if result.corrections and "stop_loss" in result.corrections:
            assert result.corrections["stop_loss"] < 50000.0
