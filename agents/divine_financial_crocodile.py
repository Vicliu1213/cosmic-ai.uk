#!/usr/bin/env python3
"""Dry-run first trading runner for the Divine Financial Crocodile surface.

This module replaces the previous mythology-only demo with a coherent operator flow:
signal -> risk -> execution -> portfolio -> verification.

Default mode is always dry-run. No live broker side effects are enabled here.
"""

from __future__ import annotations

import asyncio
import hashlib
import random
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Mapping, Optional


class RiskLimits:
    def __init__(
        self,
        max_position_fraction: float = 0.10,
        risk_per_trade: float = 0.01,
        max_daily_drawdown: float = 0.03,
        min_confidence: float = 0.55,
    ) -> None:
        self.max_position_fraction = float(max_position_fraction)
        self.risk_per_trade = float(risk_per_trade)
        self.max_daily_drawdown = float(max_daily_drawdown)
        self.min_confidence = float(min_confidence)

    def to_dict(self) -> Dict[str, float]:
        return {
            "max_position_fraction": self.max_position_fraction,
            "risk_per_trade": self.risk_per_trade,
            "max_daily_drawdown": self.max_daily_drawdown,
            "min_confidence": self.min_confidence,
        }


class TradeSignal:
    def __init__(
        self,
        symbol: str,
        side: str,
        confidence: float,
        entry_price: float,
        stop_loss: float,
        take_profit: float,
        reason: str,
        short_ma: Optional[float] = None,
        long_ma: Optional[float] = None,
    ) -> None:
        self.symbol = symbol
        self.side = side.upper()
        self.confidence = float(confidence)
        self.entry_price = float(entry_price)
        self.stop_loss = float(stop_loss)
        self.take_profit = float(take_profit)
        self.reason = reason
        self.short_ma = short_ma
        self.long_ma = long_ma

    @property
    def stop_distance(self) -> float:
        return abs(self.entry_price - self.stop_loss)

    @property
    def reward_distance(self) -> float:
        return abs(self.take_profit - self.entry_price)

    @property
    def reward_risk_ratio(self) -> float:
        if self.stop_distance <= 0:
            return 0.0
        return self.reward_distance / self.stop_distance

    def to_dict(self) -> Dict[str, Any]:
        return {
            "symbol": self.symbol,
            "side": self.side,
            "confidence": self.confidence,
            "entry_price": self.entry_price,
            "stop_loss": self.stop_loss,
            "take_profit": self.take_profit,
            "reason": self.reason,
            "short_ma": self.short_ma,
            "long_ma": self.long_ma,
            "reward_risk_ratio": self.reward_risk_ratio,
        }


class DryRunBroker:
    def __init__(self, initial_cash: float = 100_000.0) -> None:
        self.initial_cash = float(initial_cash)
        self.cash = float(initial_cash)
        self.positions: Dict[str, Dict[str, float]] = {}
        self.orders: List[Dict[str, Any]] = []
        self.realized_pnl = 0.0

    def buy(self, symbol: str, quantity: float, price: float) -> Dict[str, Any]:
        notional = quantity * price
        if quantity <= 0:
            return {
                "status": "rejected",
                "side": "BUY",
                "symbol": symbol,
                "price": price,
                "quantity": quantity,
                "filled_quantity": 0.0,
                "reason": "non_positive_quantity",
            }
        if notional > self.cash + 1e-9:
            return {
                "status": "rejected",
                "side": "BUY",
                "symbol": symbol,
                "price": price,
                "quantity": quantity,
                "filled_quantity": 0.0,
                "reason": "insufficient_cash",
            }

        self.cash -= notional
        position = self.positions.get(symbol, {"quantity": 0.0, "avg_price": 0.0})
        new_quantity = position["quantity"] + quantity
        if new_quantity > 0:
            position["avg_price"] = (
                position["quantity"] * position["avg_price"] + notional
            ) / new_quantity
        position["quantity"] = new_quantity
        self.positions[symbol] = position

        order = {
            "status": "filled",
            "side": "BUY",
            "symbol": symbol,
            "price": price,
            "quantity": quantity,
            "filled_quantity": quantity,
            "notional": notional,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        self.orders.append(order)
        return order

    def sell(self, symbol: str, quantity: float, price: float) -> Dict[str, Any]:
        position = self.positions.get(symbol, {"quantity": 0.0, "avg_price": 0.0})
        if quantity <= 0:
            return {
                "status": "rejected",
                "side": "SELL",
                "symbol": symbol,
                "price": price,
                "quantity": quantity,
                "filled_quantity": 0.0,
                "reason": "non_positive_quantity",
            }
        if position["quantity"] + 1e-9 < quantity:
            return {
                "status": "rejected",
                "side": "SELL",
                "symbol": symbol,
                "price": price,
                "quantity": quantity,
                "filled_quantity": 0.0,
                "reason": "insufficient_position",
            }

        notional = quantity * price
        self.cash += notional
        position["quantity"] -= quantity
        self.realized_pnl += (price - position["avg_price"]) * quantity
        if position["quantity"] <= 1e-9:
            self.positions.pop(symbol, None)
        else:
            self.positions[symbol] = position

        order = {
            "status": "filled",
            "side": "SELL",
            "symbol": symbol,
            "price": price,
            "quantity": quantity,
            "filled_quantity": quantity,
            "notional": notional,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        self.orders.append(order)
        return order

    def portfolio_snapshot(self, marks: Optional[Mapping[str, float]] = None) -> Dict[str, Any]:
        marks = marks or {}
        positions_value = 0.0
        rendered_positions: Dict[str, Dict[str, float]] = {}
        for symbol, position in self.positions.items():
            mark = float(marks.get(symbol, position["avg_price"]))
            market_value = position["quantity"] * mark
            unrealized = (mark - position["avg_price"]) * position["quantity"]
            positions_value += market_value
            rendered_positions[symbol] = {
                "quantity": position["quantity"],
                "avg_price": position["avg_price"],
                "mark_price": mark,
                "market_value": market_value,
                "unrealized_pnl": unrealized,
            }
        equity = self.cash + positions_value
        return {
            "cash": self.cash,
            "positions": rendered_positions,
            "positions_value": positions_value,
            "equity": equity,
            "realized_pnl": self.realized_pnl,
        }


class CoherentTradingRunner:
    def __init__(
        self,
        broker: Optional[DryRunBroker] = None,
        risk_limits: Optional[RiskLimits] = None,
        live_trading_enabled: bool = False,
    ) -> None:
        self.broker = broker or DryRunBroker()
        self.risk_limits = risk_limits or RiskLimits()
        self.live_trading_enabled = bool(live_trading_enabled)
        self.created_at = datetime.now(timezone.utc)
        self.runner_id = self._generate_runner_id()
        self.daily_realized_pnl = 0.0
        self.high_water_mark = self.broker.initial_cash
        self.last_signal: Optional[TradeSignal] = None
        self.last_risk: Optional[Dict[str, Any]] = None
        self.last_execution: Optional[Dict[str, Any]] = None

    def _generate_runner_id(self) -> str:
        seed = f"{datetime.now(timezone.utc).isoformat()}::{random.random()}"
        return "CROC-DRY-" + hashlib.sha256(seed.encode()).hexdigest()[:10]

    def _extract_series(self, market_data: Any, field: str) -> List[float]:
        if isinstance(market_data, Mapping):
            values = market_data.get(field, [])
        else:
            values = getattr(market_data, field, [])
        if values is None:
            return []
        return [float(v) for v in list(values)]

    def _moving_average(self, values: List[float], window: int) -> float:
        if not values:
            return 0.0
        sample = values[-window:] if len(values) >= window else values
        return sum(sample) / len(sample)

    def generate_signal(self, market_data: Any, symbol: str) -> TradeSignal:
        closes = self._extract_series(market_data, "close")
        if len(closes) < 5:
            price = closes[-1] if closes else 0.0
            return TradeSignal(
                symbol=symbol,
                side="HOLD",
                confidence=0.0,
                entry_price=price,
                stop_loss=price,
                take_profit=price,
                reason="insufficient_history",
            )

        current_price = closes[-1]
        short_ma = self._moving_average(closes, 5)
        long_ma = self._moving_average(closes, 20)
        trend_gap = 0.0 if long_ma == 0 else abs(short_ma - long_ma) / long_ma
        confidence = min(0.95, 0.55 + trend_gap * 10)

        if short_ma > long_ma:
            side = "BUY"
            stop_loss = current_price * 0.98
            take_profit = current_price * 1.04
            reason = "short_ma_above_long_ma"
        elif short_ma < long_ma:
            side = "SELL"
            stop_loss = current_price * 1.02
            take_profit = current_price * 0.96
            reason = "short_ma_below_long_ma"
        else:
            side = "HOLD"
            stop_loss = current_price
            take_profit = current_price
            confidence = 0.50
            reason = "moving_averages_flat"

        return TradeSignal(
            symbol=symbol,
            side=side,
            confidence=confidence,
            entry_price=current_price,
            stop_loss=stop_loss,
            take_profit=take_profit,
            reason=reason,
            short_ma=short_ma,
            long_ma=long_ma,
        )

    def assess_risk(self, signal: TradeSignal) -> Dict[str, Any]:
        reasons: List[str] = []
        approved = True

        if signal.side == "HOLD":
            approved = False
            reasons.append("signal_is_hold")

        if signal.confidence < self.risk_limits.min_confidence:
            approved = False
            reasons.append(
                f"confidence_below_min:{signal.confidence:.3f}<{self.risk_limits.min_confidence:.3f}"
            )

        portfolio = self.broker.portfolio_snapshot({signal.symbol: signal.entry_price})
        equity = max(portfolio["equity"], 0.0)
        drawdown = 0.0
        if self.high_water_mark > 0:
            drawdown = max(0.0, (self.high_water_mark - equity) / self.high_water_mark)
        if drawdown > self.risk_limits.max_daily_drawdown:
            approved = False
            reasons.append(
                f"daily_drawdown_exceeded:{drawdown:.3f}>{self.risk_limits.max_daily_drawdown:.3f}"
            )

        stop_distance = signal.stop_distance
        if stop_distance <= 0:
            approved = False
            reasons.append("invalid_stop_distance")

        if signal.reward_risk_ratio < 1.5 and signal.side != "HOLD":
            approved = False
            reasons.append(
                f"reward_risk_too_low:{signal.reward_risk_ratio:.2f}<1.50"
            )

        return {
            "approved": approved,
            "reasons": reasons,
            "estimated_drawdown": drawdown,
            "reward_risk_ratio": signal.reward_risk_ratio,
            "limits": self.risk_limits.to_dict(),
        }

    def build_order_plan(self, signal: TradeSignal) -> Dict[str, Any]:
        portfolio = self.broker.portfolio_snapshot({signal.symbol: signal.entry_price})
        equity = portfolio["equity"]
        risk_budget = equity * self.risk_limits.risk_per_trade
        max_notional = equity * self.risk_limits.max_position_fraction
        stop_distance = max(signal.stop_distance, 1e-9)
        quantity_from_risk = risk_budget / stop_distance
        quantity_from_notional = max_notional / max(signal.entry_price, 1e-9)
        quantity = min(quantity_from_risk, quantity_from_notional)
        return {
            "quantity": round(max(quantity, 0.0), 8),
            "risk_budget": risk_budget,
            "max_notional": max_notional,
            "stop_distance": stop_distance,
        }

    def execute_signal(self, signal: TradeSignal, risk: Dict[str, Any]) -> Dict[str, Any]:
        if not risk["approved"]:
            execution = {
                "status": "blocked",
                "side": signal.side,
                "symbol": signal.symbol,
                "price": signal.entry_price,
                "quantity": 0.0,
                "filled_quantity": 0.0,
                "reason": ";".join(risk["reasons"]) or "risk_blocked",
            }
            self.last_execution = execution
            return execution

        plan = self.build_order_plan(signal)
        quantity = plan["quantity"]
        if quantity <= 0:
            execution = {
                "status": "blocked",
                "side": signal.side,
                "symbol": signal.symbol,
                "price": signal.entry_price,
                "quantity": 0.0,
                "filled_quantity": 0.0,
                "reason": "quantity_is_zero",
            }
            self.last_execution = execution
            return execution

        if signal.side == "BUY":
            execution = self.broker.buy(signal.symbol, quantity, signal.entry_price)
        elif signal.side == "SELL":
            execution = self.broker.sell(signal.symbol, quantity, signal.entry_price)
        else:
            execution = {
                "status": "blocked",
                "side": signal.side,
                "symbol": signal.symbol,
                "price": signal.entry_price,
                "quantity": 0.0,
                "filled_quantity": 0.0,
                "reason": "hold_signal",
            }

        execution = {**execution, **plan}
        if execution["status"] == "filled":
            self.daily_realized_pnl = self.broker.realized_pnl
        self.last_execution = execution
        return execution

    async def trading_cycle(self, market_data: Any, symbol: str = "BTCUSDT") -> Dict[str, Any]:
        signal = self.generate_signal(market_data, symbol=symbol)
        risk = self.assess_risk(signal)
        execution = self.execute_signal(signal, risk)
        portfolio = self.broker.portfolio_snapshot({symbol: signal.entry_price})
        self.high_water_mark = max(self.high_water_mark, portfolio["equity"])
        verification = {
            "mode": "dry-run",
            "live_trading_enabled": self.live_trading_enabled,
            "safe_to_promote": execution["status"] in {"filled", "blocked"} and not self.live_trading_enabled,
            "checks": {
                "has_signal": signal.side in {"BUY", "SELL", "HOLD"},
                "risk_evaluated": isinstance(risk["approved"], bool),
                "portfolio_non_negative_cash": portfolio["cash"] >= 0.0,
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        self.last_signal = signal
        self.last_risk = risk
        return {
            "signal": signal.to_dict(),
            "risk": risk,
            "execution": execution,
            "portfolio": portfolio,
            "verification": verification,
        }

    async def absolute_trading_cycle(self, market_data: Any) -> Dict[str, Any]:
        return await self.trading_cycle(market_data, symbol="BTCUSDT")

    def get_absolute_status(self) -> Dict[str, Any]:
        portfolio = self.broker.portfolio_snapshot()
        return {
            "runner_id": self.runner_id,
            "created_at": self.created_at.isoformat(),
            "mode": "dry-run",
            "live_trading_enabled": self.live_trading_enabled,
            "cash": portfolio["cash"],
            "equity": portfolio["equity"],
            "positions": portfolio["positions"],
            "orders": len(self.broker.orders),
            "risk_limits": self.risk_limits.to_dict(),
            "last_signal": None if self.last_signal is None else self.last_signal.to_dict(),
            "last_risk": self.last_risk,
            "last_execution": self.last_execution,
        }


class DivineFinancialCrocodile(CoherentTradingRunner):
    """Backwards-compatible surface that now runs the coherent dry-run engine."""


def generate_synthetic_market(days: int = 1, freq: str = "1min") -> Dict[str, List[float]]:
    del freq
    total_points = max(days * 24 * 60, 30)
    start = datetime(2024, 1, 1)
    closes: List[float] = []
    volumes: List[float] = []
    price = 10_000.0
    for i in range(total_points):
        drift = 0.0003
        seasonal = ((i % 20) - 10) / 10_000
        price = max(100.0, price * (1 + drift + seasonal))
        closes.append(round(price, 2))
        volumes.append(float(1_000 + (i % 50) * 25))
    timestamps = [
        (start + timedelta(minutes=i)).isoformat() + "Z" for i in range(total_points)
    ]
    return {"timestamp": timestamps, "close": closes, "volume": volumes}


async def main() -> None:
    runner = DivineFinancialCrocodile()
    market = generate_synthetic_market(days=1)
    result = await runner.trading_cycle(market, symbol="BTCUSDT")
    status = runner.get_absolute_status()

    print("=" * 88)
    print("Divine Financial Crocodile -> coherent dry-run runner")
    print("=" * 88)
    print("signal:", result["signal"])
    print("risk:", result["risk"])
    print("execution:", result["execution"])
    print("portfolio:", result["portfolio"])
    print("verification:", result["verification"])
    print("status:", status)


if __name__ == "__main__":
    asyncio.run(main())
