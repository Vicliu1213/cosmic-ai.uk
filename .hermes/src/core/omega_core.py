from __future__ import annotations

import argparse
import importlib.util
import json
import sys
import types
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional


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
SelfEvolve = _load_symbol("hermes_self_evolve", "self_evolve/evolution_egnine.py", "SelfEvolve")


@dataclass
class ScreenSnapshot:
    mode: str
    objective: str
    active_skills: list[str]
    passive_skills: list[str]
    risk_state: Dict[str, Any]
    memory_state: Dict[str, Any]
    next_action: str


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
        self.trade_history: List[Dict[str, Any]] = []
        self.active_tasks = []
        self.passive_monitors = [self.risk_shield, self.memory]
        self.last_opp: Optional[Dict[str, Any]] = None
        self.high_win_rate_mode = False
        self.execution_log: List[Dict[str, Any]] = []
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

    def enable_high_win_rate_mode(self) -> None:
        self.high_win_rate_mode = True
        self.mode = "passive"

    def get_atr(self, symbol: str) -> float:
        if self.trade_history:
            recent_ranges = [abs(float(item.get("tp", 0)) - float(item.get("sl", 0))) for item in self.trade_history[-14:] if item.get("tp") is not None and item.get("sl") is not None]
            if recent_ranges:
                return max(sum(recent_ranges) / len(recent_ranges), 10.0)
        return 80.0 if symbol.startswith("BTC") else 5.0

    def get_adx(self, symbol: str) -> float:
        recent_confidence = [float(item.get("confidence", 0.5)) for item in self.trade_history[-14:]]
        if recent_confidence:
            return 20.0 + min(25.0, sum(recent_confidence) / len(recent_confidence) * 20.0)
        return 24.0

    def calculate_trade_setup(self, entry_price, atr, adx=None):
        dynamic_mult = 2.1 if (atr / entry_price) < 0.02 else 2.5
        sl = entry_price - atr * dynamic_mult
        rr = 2.2 if adx and adx > 30 else 1.5
        tp = entry_price + (entry_price - sl) * rr
        sl_pct = (entry_price - sl) / entry_price
        lev = 0.02 / sl_pct if sl_pct > 0 else 10
        return {"entry": entry_price, "sl": sl, "tp": tp, "leverage": min(lev, 20), "risk_reward": rr}

    def _observe_passive(self, tick_data: Dict[str, Any]) -> Dict[str, Any]:
        memory_status = self.memory.status()
        return {
            "can_open": self.risk_shield.can_open(),
            "daily_loss": self.risk_shield.daily_loss,
            "active_positions": self.risk_shield.active_positions,
            "memory_items": memory_status["long_term_items"],
            "pending_patterns": memory_status["pending_patterns"],
            "last_seen_symbol": tick_data.get("symbol"),
            "high_win_rate_mode": self.high_win_rate_mode,
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

    def record_trade_result(self, opportunity: Dict[str, Any], order_packet: Dict[str, Any], symbol: str) -> Dict[str, Any]:
        confidence = float(opportunity.get("confidence", 0.5))
        pnl = round((confidence - 0.45) * 120.0, 4)
        win = pnl >= 0
        trade_result = {
            "symbol": symbol,
            "entry": opportunity.get("entry"),
            "sl": opportunity.get("sl"),
            "tp": opportunity.get("tp"),
            "confidence": confidence,
            "pnl": pnl,
            "win": win,
            "orders": len(order_packet.get("orders", [])),
        }
        self.trade_history.append(trade_result)
        self.execution_log.append(trade_result)
        self.evolve.ingest_trade(trade_result)
        memory_update = self.memory.commit(opportunity, outcome=trade_result, win=win)
        if not win:
            self.risk_shield.daily_loss -= abs(pnl) / 10000.0
        return {"trade": trade_result, "memory_update": memory_update}

    def build_dashboard_state(self, result: Dict[str, Any]) -> Dict[str, Any]:
        passive_state = result["passive"]
        return {
            "identity": {
                "mode": result["mode"],
                "objective": result["objective"],
                "next_action": result["next_action"],
            },
            "skill_mesh": {
                "active": ["orderflow_hunt", "arbitrage_capture", "liquidity_stealth"] if result["mode"] != "passive" else [],
                "passive": ["risk_shield", "memory_matrix", "self_evolve"],
            },
            "risk_shell": {
                "can_open": passive_state["can_open"],
                "daily_loss": passive_state["daily_loss"],
                "active_positions": passive_state["active_positions"],
                "high_win_rate_mode": passive_state["high_win_rate_mode"],
            },
            "memory_learn": {
                "pending_patterns": passive_state["pending_patterns"],
                "long_term_items": passive_state["memory_items"],
                "latest_evolution_action": result["evolution"]["action"],
            },
            "execution": result.get("order_packet"),
            "mcp": result["mcp"],
        }

    def process_tick(self, tick_data: Dict[str, Any]) -> Dict[str, Any]:
        symbol = tick_data["symbol"]
        passive_state = self._observe_passive(tick_data)
        opp = None
        order_packet = None
        trade_result = None
        memory_write = False
        memory_update = None

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
                pending_commit = self.memory.commit(opp, outcome={"mode": self.mode}, win=None)
                memory_write = True
                memory_update = pending_commit
                execution_update = self.record_trade_result(opp, order_packet, symbol)
                trade_result = execution_update["trade"]
                memory_update = execution_update["memory_update"]
                passive_state = self._observe_passive(tick_data)

        if self.mode == "passive":
            next_action = "observe"
        elif order_packet:
            next_action = "prepare_execution"
        else:
            next_action = "hold"

        evolve_review = self.evolve.review()
        dashboard_state = self.build_dashboard_state({
            "mode": self.mode,
            "objective": self.objective,
            "next_action": next_action,
            "passive": passive_state,
            "evolution": evolve_review,
            "order_packet": order_packet,
            "mcp": self.mcp_state,
        })
        return {
            "mode": self.mode,
            "symbol": symbol,
            "objective": self.objective,
            "passive": passive_state,
            "mcp": self.mcp_state,
            "opportunity": opp,
            "order_packet": order_packet,
            "memory_write": memory_write,
            "memory_update": memory_update,
            "trade_result": trade_result,
            "evolution": evolve_review,
            "dashboard": dashboard_state,
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


def write_runtime_state(dashboard_state: Optional[Dict[str, Any]]) -> Optional[Path]:
    if dashboard_state is None:
        return None
    path = (BASE_DIR.parents[2] / "hermes" / "dashboard" / "runtime_state.json").resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(dashboard_state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


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
    runtime_state_path = write_runtime_state(latest.get("dashboard") if latest else None)
    print({
        "screen": snapshot.__dict__,
        "dashboard": latest.get("dashboard") if latest else None,
        "runtime_state_path": str(runtime_state_path) if runtime_state_path else None,
        "last_result": latest,
    })


if __name__ == "__main__":
    main()
