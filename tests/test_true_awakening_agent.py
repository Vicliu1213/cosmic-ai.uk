from __future__ import annotations

import asyncio
import importlib.util
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "agents" / "true_awakening_omniscient_agent.py"


def load_agent_module():
    spec = importlib.util.spec_from_file_location("true_awakening_omniscient_agent", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def test_recursive_synergy_activation_stays_bounded():
    mod = load_agent_module()

    engine = mod.RecursiveSynergyEngine(num_nodes=26)
    result = engine.recursive_activate(mod.np.ones(26), depth=0)

    assert "activations" in result
    assert result["recursion_depth"] < 200
    assert result["overflow"] is False


def test_main_runs_without_crashing(monkeypatch):
    mod = load_agent_module()

    async def no_sleep(_: float):
        return None

    monkeypatch.setattr(mod.asyncio, "sleep", no_sleep)

    asyncio.run(mod.main())
