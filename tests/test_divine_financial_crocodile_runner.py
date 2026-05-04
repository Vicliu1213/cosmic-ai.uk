from __future__ import annotations

import asyncio
import importlib.util
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "agents" / "divine_financial_crocodile.py"


def load_runner_module():
    spec = importlib.util.spec_from_file_location("divine_financial_crocodile", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def make_trending_market():
    return {
        "close": [100.0 + i * 1.2 for i in range(30)],
        "volume": [1_000 + i * 10 for i in range(30)],
    }


def test_runner_has_safe_dry_run_models():
    mod = load_runner_module()

    limits = mod.RiskLimits(
        max_position_fraction=0.10,
        risk_per_trade=0.01,
        max_daily_drawdown=0.03,
        min_confidence=0.60,
    )
    signal = mod.TradeSignal(
        symbol="BTCUSDT",
        side="BUY",
        confidence=0.72,
        entry_price=120.0,
        stop_loss=114.0,
        take_profit=132.0,
        reason="short_ma_above_long_ma",
    )

    assert limits.max_position_fraction == 0.10
    assert limits.risk_per_trade == 0.01
    assert signal.symbol == "BTCUSDT"
    assert signal.side == "BUY"
    assert signal.stop_loss < signal.entry_price < signal.take_profit


def test_risk_gate_blocks_low_confidence_signal():
    mod = load_runner_module()

    runner = mod.CoherentTradingRunner(
        broker=mod.DryRunBroker(initial_cash=10_000.0),
        risk_limits=mod.RiskLimits(min_confidence=0.70),
    )
    weak_signal = mod.TradeSignal(
        symbol="BTCUSDT",
        side="BUY",
        confidence=0.61,
        entry_price=100.0,
        stop_loss=97.0,
        take_profit=108.0,
        reason="edge_too_weak",
    )

    decision = runner.assess_risk(weak_signal)

    assert decision["approved"] is False
    assert any("confidence" in reason.lower() for reason in decision["reasons"])


def test_dry_run_cycle_executes_and_returns_status_packet():
    mod = load_runner_module()

    runner = mod.CoherentTradingRunner(
        broker=mod.DryRunBroker(initial_cash=25_000.0),
        risk_limits=mod.RiskLimits(
            max_position_fraction=0.10,
            risk_per_trade=0.01,
            max_daily_drawdown=0.05,
            min_confidence=0.55,
        ),
    )

    result = asyncio.run(runner.trading_cycle(make_trending_market(), symbol="BTCUSDT"))

    assert set(result) == {"signal", "risk", "execution", "portfolio", "verification"}
    assert result["verification"]["mode"] == "dry-run"
    assert result["verification"]["live_trading_enabled"] is False
    assert result["signal"]["symbol"] == "BTCUSDT"
    assert result["risk"]["approved"] is True
    assert result["execution"]["status"] == "filled"
    assert result["execution"]["side"] == "BUY"
    assert result["portfolio"]["cash"] >= 0.0
    assert result["portfolio"]["positions"]["BTCUSDT"]["quantity"] > 0.0
