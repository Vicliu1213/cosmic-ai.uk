#!/usr/bin/env python3
"""
Tests for src/utils/action_protocol.py

Covers: normalize_action, is_open_action, is_close_action,
        is_long_action, is_short_action, is_passive_action,
        Action enum, and the canonical action constant sets.
"""

import sys
import os
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.utils.action_protocol import (
    Action,
    normalize_action,
    is_open_action,
    is_close_action,
    is_long_action,
    is_short_action,
    is_passive_action,
    VALID_ACTIONS,
    OPEN_ACTIONS,
    CLOSE_ACTIONS,
    PASSIVE_ACTIONS,
)


class TestActionEnum:
    """Tests for the Action enum values."""

    def test_enum_values(self):
        assert Action.OPEN_LONG.value == "open_long"
        assert Action.OPEN_SHORT.value == "open_short"
        assert Action.CLOSE_LONG.value == "close_long"
        assert Action.CLOSE_SHORT.value == "close_short"
        assert Action.WAIT.value == "wait"
        assert Action.HOLD.value == "hold"

    def test_enum_is_str_subclass(self):
        assert isinstance(Action.OPEN_LONG, str)


class TestActionSets:
    """Tests for the constant action-set correctness."""

    def test_open_actions_membership(self):
        assert "open_long" in OPEN_ACTIONS
        assert "open_short" in OPEN_ACTIONS
        assert "close_long" not in OPEN_ACTIONS

    def test_close_actions_membership(self):
        assert "close_long" in CLOSE_ACTIONS
        assert "close_short" in CLOSE_ACTIONS
        assert "close_position" in CLOSE_ACTIONS
        assert "open_long" not in CLOSE_ACTIONS

    def test_passive_actions_membership(self):
        assert "wait" in PASSIVE_ACTIONS
        assert "hold" in PASSIVE_ACTIONS
        assert "open_long" not in PASSIVE_ACTIONS

    def test_valid_actions_is_union(self):
        assert VALID_ACTIONS == OPEN_ACTIONS | CLOSE_ACTIONS | PASSIVE_ACTIONS

    def test_action_sets_are_disjoint(self):
        assert not OPEN_ACTIONS & CLOSE_ACTIONS
        assert not OPEN_ACTIONS & PASSIVE_ACTIONS
        assert not CLOSE_ACTIONS & PASSIVE_ACTIONS


class TestNormalizeAction:
    """Tests for normalize_action()."""

    # ── Open-long aliases ──────────────────────────────────────────────
    @pytest.mark.parametrize("raw", ["open_long", "long", "buy", "go_long"])
    def test_open_long_aliases(self, raw: str):
        assert normalize_action(raw) == "open_long"

    # ── Open-short aliases ─────────────────────────────────────────────
    @pytest.mark.parametrize("raw", ["open_short", "short", "sell", "go_short"])
    def test_open_short_aliases(self, raw: str):
        assert normalize_action(raw) == "open_short"

    # ── Close-long aliases ─────────────────────────────────────────────
    @pytest.mark.parametrize("raw", ["close_long", "exit_long"])
    def test_close_long_aliases(self, raw: str):
        assert normalize_action(raw) == "close_long"

    # ── Close-short aliases ────────────────────────────────────────────
    @pytest.mark.parametrize("raw", ["close_short", "exit_short"])
    def test_close_short_aliases(self, raw: str):
        assert normalize_action(raw) == "close_short"

    # ── Passive aliases ────────────────────────────────────────────────
    def test_wait_alias_skip(self):
        assert normalize_action("skip") == "wait"

    def test_wait_canonical(self):
        assert normalize_action("wait") == "wait"

    def test_hold_canonical(self):
        assert normalize_action("hold") == "hold"

    # ── Generic close resolution via position_side ─────────────────────
    def test_close_with_long_side(self):
        assert normalize_action("close", position_side="long") == "close_long"

    def test_close_with_short_side(self):
        assert normalize_action("close", position_side="short") == "close_short"

    def test_close_with_open_long_side(self):
        assert normalize_action("close", position_side="open_long") == "close_long"

    def test_close_without_side_returns_generic(self):
        assert normalize_action("close") == "close_position"

    def test_exit_with_long_side(self):
        assert normalize_action("exit", position_side="long") == "close_long"

    def test_close_position_without_side(self):
        assert normalize_action("close_position") == "close_position"

    # ── Unknown input falls back to wait ──────────────────────────────
    def test_unknown_returns_wait(self):
        assert normalize_action("gibberish") == "wait"

    def test_empty_string_returns_wait(self):
        assert normalize_action("") == "wait"

    def test_none_returns_wait(self):
        assert normalize_action(None) == "wait"

    # ── Case insensitivity ─────────────────────────────────────────────
    def test_uppercase_buy(self):
        assert normalize_action("BUY") == "open_long"

    def test_mixed_case_sell(self):
        assert normalize_action("Sell") == "open_short"

    # ── Whitespace stripping ───────────────────────────────────────────
    def test_leading_trailing_whitespace(self):
        assert normalize_action("  buy  ") == "open_long"

    # ── Return value is always in VALID_ACTIONS or close_position ─────
    @pytest.mark.parametrize("raw", [
        "open_long", "open_short", "close_long", "close_short",
        "wait", "hold", "buy", "sell", "long", "short",
        "close", "exit", "skip", "HOLD", "close_position",
    ])
    def test_output_always_known(self, raw: str):
        result = normalize_action(raw)
        assert result in VALID_ACTIONS or result == "close_position"


class TestIsOpenAction:
    """Tests for is_open_action()."""

    def test_open_long_is_open(self):
        assert is_open_action("open_long") is True

    def test_open_short_is_open(self):
        assert is_open_action("open_short") is True

    def test_close_long_is_not_open(self):
        assert is_open_action("close_long") is False

    def test_wait_is_not_open(self):
        assert is_open_action("wait") is False

    def test_buy_alias_is_open(self):
        assert is_open_action("buy") is True

    def test_sell_alias_is_open(self):
        assert is_open_action("sell") is True

    def test_none_is_not_open(self):
        assert is_open_action(None) is False


class TestIsCloseAction:
    """Tests for is_close_action()."""

    def test_close_long_is_close(self):
        assert is_close_action("close_long") is True

    def test_close_short_is_close(self):
        assert is_close_action("close_short") is True

    def test_exit_long_is_close(self):
        assert is_close_action("exit_long") is True

    def test_open_long_is_not_close(self):
        assert is_close_action("open_long") is False

    def test_hold_is_not_close(self):
        assert is_close_action("hold") is False


class TestIsLongAction:
    """Tests for is_long_action()."""

    def test_open_long_is_long(self):
        assert is_long_action("open_long") is True

    def test_close_long_is_long(self):
        assert is_long_action("close_long") is True

    def test_open_short_is_not_long(self):
        assert is_long_action("open_short") is False

    def test_close_short_is_not_long(self):
        assert is_long_action("close_short") is False

    def test_buy_alias_is_long(self):
        assert is_long_action("buy") is True


class TestIsShortAction:
    """Tests for is_short_action()."""

    def test_open_short_is_short(self):
        assert is_short_action("open_short") is True

    def test_close_short_is_short(self):
        assert is_short_action("close_short") is True

    def test_open_long_is_not_short(self):
        assert is_short_action("open_long") is False

    def test_sell_alias_is_short(self):
        assert is_short_action("sell") is True


class TestIsPassiveAction:
    """Tests for is_passive_action()."""

    def test_wait_is_passive(self):
        assert is_passive_action("wait") is True

    def test_hold_is_passive(self):
        assert is_passive_action("hold") is True

    def test_skip_is_passive(self):
        assert is_passive_action("skip") is True

    def test_open_long_is_not_passive(self):
        assert is_passive_action("open_long") is False

    def test_close_long_is_not_passive(self):
        assert is_passive_action("close_long") is False

    def test_none_is_passive(self):
        # None normalises to wait → passive
        assert is_passive_action(None) is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
