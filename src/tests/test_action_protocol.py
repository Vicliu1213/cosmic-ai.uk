#!/usr/bin/env python3
"""
Test suite for utils/action_protocol.py
Tests normalize_action, is_open_action, is_close_action, is_long_action,
is_short_action, is_passive_action, and the Action enum.
"""

import sys
import pytest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.action_protocol import (
    Action,
    OPEN_ACTIONS,
    CLOSE_ACTIONS,
    PASSIVE_ACTIONS,
    VALID_ACTIONS,
    normalize_action,
    is_open_action,
    is_close_action,
    is_long_action,
    is_short_action,
    is_passive_action,
)


class TestActionEnum:
    """Test the Action enum values."""

    def test_action_values(self):
        assert Action.OPEN_LONG == "open_long"
        assert Action.OPEN_SHORT == "open_short"
        assert Action.CLOSE_LONG == "close_long"
        assert Action.CLOSE_SHORT == "close_short"
        assert Action.WAIT == "wait"
        assert Action.HOLD == "hold"

    def test_action_is_str_subclass(self):
        for action in Action:
            assert isinstance(action, str)

    def test_open_actions_set(self):
        assert "open_long" in OPEN_ACTIONS
        assert "open_short" in OPEN_ACTIONS
        assert "close_long" not in OPEN_ACTIONS
        assert "wait" not in OPEN_ACTIONS

    def test_close_actions_set(self):
        assert "close_long" in CLOSE_ACTIONS
        assert "close_short" in CLOSE_ACTIONS
        assert "close_position" in CLOSE_ACTIONS
        assert "open_long" not in CLOSE_ACTIONS

    def test_passive_actions_set(self):
        assert "wait" in PASSIVE_ACTIONS
        assert "hold" in PASSIVE_ACTIONS
        assert "open_long" not in PASSIVE_ACTIONS

    def test_valid_actions_union(self):
        for a in ["open_long", "open_short", "close_long", "close_short", "wait", "hold"]:
            assert a in VALID_ACTIONS


class TestNormalizeAction:
    """Test normalize_action with all supported aliases."""

    @pytest.mark.parametrize("alias,expected", [
        ("open_long", "open_long"),
        ("long", "open_long"),
        ("buy", "open_long"),
        ("go_long", "open_long"),
        ("open_short", "open_short"),
        ("short", "open_short"),
        ("sell", "open_short"),
        ("go_short", "open_short"),
        ("close_long", "close_long"),
        ("exit_long", "close_long"),
        ("close_short", "close_short"),
        ("exit_short", "close_short"),
        ("wait", "wait"),
        ("skip", "wait"),
        ("hold", "hold"),
    ])
    def test_known_aliases(self, alias, expected):
        assert normalize_action(alias) == expected

    def test_case_insensitive(self):
        assert normalize_action("LONG") == "open_long"
        assert normalize_action("BUY") == "open_long"
        assert normalize_action("Short") == "open_short"
        assert normalize_action("HOLD") == "hold"
        assert normalize_action("WAIT") == "wait"

    def test_whitespace_stripped(self):
        assert normalize_action("  long  ") == "open_long"
        assert normalize_action("\twait\n") == "wait"

    def test_unknown_action_returns_wait(self):
        assert normalize_action("unknown_xyz") == "wait"
        assert normalize_action("") == "wait"
        assert normalize_action("   ") == "wait"

    def test_none_returns_wait(self):
        assert normalize_action(None) == "wait"

    def test_close_with_long_position(self):
        assert normalize_action("close", position_side="long") == "close_long"
        assert normalize_action("exit", position_side="long") == "close_long"
        assert normalize_action("close_position", position_side="long") == "close_long"
        assert normalize_action("close", position_side="open_long") == "close_long"

    def test_close_with_short_position(self):
        assert normalize_action("close", position_side="short") == "close_short"
        assert normalize_action("exit", position_side="short") == "close_short"
        assert normalize_action("close_position", position_side="short") == "close_short"
        assert normalize_action("close", position_side="open_short") == "close_short"

    def test_close_with_no_position_side(self):
        assert normalize_action("close") == "close_position"
        assert normalize_action("close_position") == "close_position"
        assert normalize_action("exit") == "close_position"

    def test_position_side_ignored_for_direct_actions(self):
        """position_side should not override explicitly-named actions."""
        assert normalize_action("open_long", position_side="short") == "open_long"
        assert normalize_action("long", position_side="short") == "open_long"
        assert normalize_action("hold", position_side="long") == "hold"


class TestIsOpenAction:
    """Test is_open_action helper."""

    @pytest.mark.parametrize("action", ["open_long", "long", "buy", "go_long",
                                         "open_short", "short", "sell", "go_short"])
    def test_returns_true_for_open_actions(self, action):
        assert is_open_action(action) is True

    @pytest.mark.parametrize("action", ["close_long", "close_short", "wait", "hold",
                                         "exit_long", "exit_short", "skip", None, ""])
    def test_returns_false_for_non_open_actions(self, action):
        assert is_open_action(action) is False


class TestIsCloseAction:
    """Test is_close_action helper."""

    @pytest.mark.parametrize("action", ["close_long", "exit_long", "close_short", "exit_short"])
    def test_returns_true_for_close_actions(self, action):
        assert is_close_action(action) is True

    @pytest.mark.parametrize("action", ["open_long", "open_short", "buy", "sell", "wait", "hold", None])
    def test_returns_false_for_non_close_actions(self, action):
        assert is_close_action(action) is False


class TestIsLongAction:
    """Test is_long_action helper."""

    @pytest.mark.parametrize("action", ["open_long", "long", "buy", "go_long", "close_long", "exit_long"])
    def test_returns_true_for_long_actions(self, action):
        assert is_long_action(action) is True

    @pytest.mark.parametrize("action", ["open_short", "short", "sell", "close_short", "wait", "hold", None])
    def test_returns_false_for_non_long_actions(self, action):
        assert is_long_action(action) is False


class TestIsShortAction:
    """Test is_short_action helper."""

    @pytest.mark.parametrize("action", ["open_short", "short", "sell", "go_short", "close_short", "exit_short"])
    def test_returns_true_for_short_actions(self, action):
        assert is_short_action(action) is True

    @pytest.mark.parametrize("action", ["open_long", "long", "buy", "close_long", "wait", "hold", None])
    def test_returns_false_for_non_short_actions(self, action):
        assert is_short_action(action) is False


class TestIsPassiveAction:
    """Test is_passive_action helper."""

    @pytest.mark.parametrize("action", ["wait", "hold", "skip"])
    def test_returns_true_for_passive_actions(self, action):
        assert is_passive_action(action) is True

    @pytest.mark.parametrize("action", ["open_long", "open_short", "close_long", "close_short",
                                         "long", "short", "buy", "sell"])
    def test_returns_false_for_active_actions(self, action):
        assert is_passive_action(action) is False

    @pytest.mark.parametrize("action", [None, ""])
    def test_none_and_empty_normalize_to_wait(self, action):
        """None and empty string normalize to 'wait', which is passive."""
        assert is_passive_action(action) is True
