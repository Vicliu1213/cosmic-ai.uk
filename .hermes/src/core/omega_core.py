from __future__ import annotations

import argparse
import importlib.util
import sys
import types
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional


BASE_DIR = Path(__file__).resolve().parent

SRC_DIR = BASE_DIR.parent
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

core_pkg = sys.modules.get("core")
if core_pkg is None:
    core_pkg = types.ModuleType("core")
    core_pkg.__path__ = [str(SRC_DIR / "core")]
    sys.modules["core"] = core_pkg

sys.modules["core.omega_core"] = sys.modules[__name__]


class OmegaSkill:
    """Lightweight compatibility base for local skill objects."""


def _load_symbol(module_name: str, relative_path: str, symbol: str):
    path = (BASE_DIR / relative_path).resolve()
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load {module_name} from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return getattr(module, symbol)


OrderFlowHunt = _load_symbol("hermes_orderflow_hunt", "orderflow_hunt/hunt_engine.py", "OrderFlowHunt")
ArbitrageCapture = _load_symbol("hermes_arbitrage_capture", "arbitrage_capture/arbitrage_engine.py", "ArbitrageCapture")
LiquidityStealth = _load_symbol("hermes_liquidity_stealth", "liquidity_stealth/stealth_order.py", "LiquidityStealth")
RiskShield = _load_symbol("hermes_risk_shield", "risk_shield/risk_monitor.py", "RiskShield")
MemoryMatrix = _load_symbol("hermes_memory_matrix", "memory_matrix/memory_core.py", "MemoryMatrix")


@dataclass
class ScreenSnapshot:
    mode: str
    objective: str
    active_skills: list[str]
    passive_skills: list[str]
    risk_state: Dict[str, Any]
    memory_state: Dict[str, Any]
    next_action: str


class SelfEvolve(OmegaSkill):
    def __init__(self, trade_history=None):
        self.trade_history = trade_history or []
        self.last_review = None

    def review(self) -> Dict[str, Any]:
        win_rate = 0.0
        if self.trade_history:
            wins = sum(1 for item in self.trade_history if item.get("win"))
            win_rate = wins / len(self.trade_history)
        self.last_review = {
            "trade_count": len(self.trade_history),
            "win_rate": win_rate,
            "action": "retain" if win_rate >= 0.5 else "tighten",
        }
        return self.last_review


class OmegaCore:
    _instance: Optional["OmegaCore"] = None

    @staticmethod
    def get_instance() -> "OmegaCore":
        if OmegaCore._instance is None:
            OmegaCore._instance = OmegaCore()
        return OmegaCore._instance

    def __init__(self):
        self.mode = "hybrid"
        self.objective = "hermes"
        self.memory = MemoryMatrix()
        self.risk_shield = RiskShield()
        self.hunt_engine = OrderFlowHunt(self.memory)
        self.arbitrage = ArbitrageCapture()
        self.stealth = LiquidityStealth()
        self.evolve = SelfEvolve(trade_history=[])
        self.trade_history: list[Dict[str, Any]] = []
        self.active_tasks = []
        self.passive_monitors = [self.risk_shield, self.memory]
        self.last_opp: Optional[Dict[str, Any]] = None
        self.mcp_state = {
            "endpoint": "http://127.0.0.1:8787/mcp",
            "registered_tools": [
                "terminal",
                "file",
                "web",
                "browser",
                "memory",
                "todo",
                "skills",
                "session_search",
                "mcp_hermes_webui",
            ],
        }

    def interpret_command(self, text: str) -> Dict[str, Any]:
        normalized = text.strip().lower()
        actions = []

        if any(word in normalized for word in ["passive", "被動", "觀察", "watch"]):
            actions.append({"type": "mode", "value": "passive"})
        if any(word in normalized for word in ["active", "主動", "執行", "trade"]):
            actions.append({"type": "mode", "value": "active"})
        if any(word in normalized for word in ["hybrid", "混合"]):
            actions.append({"type": "mode", "value": "hybrid"})
        if any(word in normalized for word in ["high win", "高勝率", "勝率"]):
            actions.append({"type": "mode", "value": "passive"})
            actions.append({"type": "toggle", "value": "high_win_rate_mode"})
        if any(word in normalized for word in ["dashboard", "儀表板", "webui", "面板"]):
            actions.append({"type": "surface", "value": "dashboard"})
        if any(word in normalized for word in ["mcp", "tools", "server", "服務"]):
            actions.append({"type": "surface", "value": "mcp"})
        if any(word in normalized for word in ["memory", "記憶"]):
            actions.append({"type": "surface", "value": "memory"})
        if any(word in normalized for word in ["risk", "風控", "風險"]):
            actions.append({"type": "surface", "value": "risk"})

        symbol_match = re.search(r"(?:for|in|對|針對)\s*([A-Z0-9/_:-]+)", text, re.IGNORECASE)
        symbol = symbol_match.group(1) if symbol_match else None
        if symbol:
            actions.append({"type": "symbol", "value": symbol})

        if not actions:
            actions.append({"type": "noop", "value": normalized})

        return {"text": text, "normalized": normalized, "actions": actions}

    def set_mode(self, mode: str) -> None:
        mode = mode.lower().strip()
        if mode not in {"passive", "active", "hybrid"}:
            raise ValueError("mode must be passive, active, or hybrid")
        self.mode = mode

    def calculate_trade_setup(self, entry_price, atr, adx=None):
        dynamic_mult = 2.1 if (atr / entry_price) < 0.02 else 2.5
        sl = entry_price - atr * dynamic_mult
        rr = 2.2 if adx and adx > 30 else 1.5
        tp = entry_price + (entry_price - sl) * rr
        sl_pct = (entry_price - sl) / entry_price
        lev = 0.02 / sl_pct if sl_pct > 0 else 10
        return {"entry": entry_price, "sl": sl, "tp": tp, "leverage": min(lev, 20), "risk_reward": rr}

    def _observe_passive(self, tick_data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "can_open": self.risk_shield.can_open(),
            "daily_loss": self.risk_shield.daily_loss,
            "active_positions": self.risk_shield.active_positions,
            "memory_items": len(self.memory.l3),
            "last_seen_symbol": tick_data.get("symbol"),
        }

    def _observe_active(self, symbol: str, tick_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        opp = self.hunt_engine.evaluate(
            symbol,
            tick_data["buy_vol"],
            tick_data["sell_vol"],
            tick_data["price_ticks"],
            tick_data["spread"],
        )
        if not opp:
            return None
        if not self.risk_shield.check_order(opp["entry"], tick_data["price_ticks"][-1]):
            return None
        self.last_opp = opp
        return opp

    def process_tick(self, tick_data: Dict[str, Any]) -> Dict[str, Any]:
        symbol = tick_data["symbol"]
        passive_state = self._observe_passive(tick_data)
        opp = None
        order_packet = None

        if self.mode in {"active", "hybrid"}:
            opp = self._observe_active(symbol, tick_data)
            if opp:
                order_packet = {
                    "symbol": symbol,
                    "entry": opp["entry"],
                    "sl": opp["sl"],
                    "tp": opp["tp"],
                    "confidence": opp["confidence"],
                    "orders": self.stealth.split_order(0.01, opp["entry"], opp["confidence"]),
                }

        if self.mode == "passive":
            next_action = "observe"
        elif order_packet:
            next_action = "prepare_execution"
        else:
            next_action = "hold"

        memory_write = False
        if opp:
            self.memory.commit(opp, outcome={"mode": self.mode}, win=None)
            memory_write = True

        evolve_review = self.evolve.review()
        return {
            "mode": self.mode,
            "symbol": symbol,
            "objective": self.objective,
            "passive": passive_state,
            "mcp": self.mcp_state,
            "opportunity": opp,
            "order_packet": order_packet,
            "memory_write": memory_write,
            "evolution": evolve_review,
            "next_action": next_action,
        }

    def snapshot(self, tick_data: Optional[Dict[str, Any]] = None) -> ScreenSnapshot:
        tick_data = tick_data or {"symbol": "BTC/USDT"}
        passive_state = self._observe_passive(tick_data)
        return ScreenSnapshot(
            mode=self.mode,
            objective=self.objective,
            active_skills=["orderflow_hunt", "arbitrage_capture", "liquidity_stealth"] if self.mode != "passive" else [],
            passive_skills=["risk_shield", "memory_matrix", "self_evolve"],
            risk_state={
                "can_open": passive_state["can_open"],
                "daily_loss": passive_state["daily_loss"],
                "active_positions": passive_state["active_positions"],
            },
            memory_state={"long_term_items": passive_state["memory_items"]},
            next_action="observe" if self.mode == "passive" else "evaluate_active_flow",
        )

    def run_once(self, tick_data: Dict[str, Any]) -> Dict[str, Any]:
        return self.process_tick(tick_data)

    def run(self, feeder=None, limit: Optional[int] = None):
        if feeder is None:
            from core.data_feeder import DataFeeder

            feeder = DataFeeder()
        for i, tick in enumerate(feeder.stream()):
            yield self.process_tick(tick)
            if limit is not None and i + 1 >= limit:
                break


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Hermes orchestration entrypoint")
    parser.add_argument("command", nargs="?", default="hermes")
    parser.add_argument("--mode", choices=["passive", "active", "hybrid"], default="hybrid")
    parser.add_argument("--limit", type=int, default=1)
    parser.add_argument("--say", type=str, default=None)
    return parser


def main():
    parser = build_arg_parser()
    args = parser.parse_args()
    if args.command != "hermes":
        raise SystemExit("usage: python .hermes/hermes.py hermes [--mode passive|active|hybrid]")

    core = OmegaCore.get_instance()
    core.set_mode(args.mode)

    if args.say:
        interpretation = core.interpret_command(args.say)
        for action in interpretation["actions"]:
            if action["type"] == "mode":
                core.set_mode(action["value"])
            elif action["type"] == "toggle" and action["value"] == "high_win_rate_mode":
                core.enable_high_win_rate_mode()

    if args.say and args.limit == 1:
        snapshot = core.snapshot({"symbol": "BTC/USDT"})
        print({
            "intent": core.interpret_command(args.say),
            "screen": snapshot.__dict__,
            "last_result": None,
        })
        return

    from core.data_feeder import DataFeeder

    feeder = DataFeeder()
    latest = None
    for result in core.run(feeder=feeder, limit=args.limit):
        latest = result

    snapshot = core.snapshot(latest or {"symbol": "BTC/USDT"})
    print({
        "screen": snapshot.__dict__,
        "last_result": latest,
    })


if __name__ == "__main__":
    main()
