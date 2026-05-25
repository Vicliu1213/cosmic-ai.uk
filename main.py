#!/usr/bin/env python3
"""
宇宙智能體核心引擎 v3.0
委派至 src/layers/distributed/ 模組化架構
"""
import sys, os, ray, yaml, time, logging
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
hermes_src = os.path.join(os.path.dirname(os.path.abspath(__file__)), "hermes", "src")
sys.path.insert(0, hermes_src)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[logging.StreamHandler(), logging.FileHandler('cosmic_engine.log', encoding='utf-8')])
logger = logging.getLogger(__name__)

from cosmic.knowledge_base import KnowledgeBase
from src.layers.distributed import (
    DistributedCluster, ActorOrchestrator, SynergyEngine,
    CrocodileFleet, ConsciousnessLayer, EvolutionEngine,
)
from src.synergy.dashboard_server import SynergyDashboardServer


def main():
    start = time.time()
    logger.info("=" * 70)
    logger.info("  宇宙智能體核心引擎 v3.0  —  金融大鰐 × 神性超越 完全體")
    logger.info("=" * 70)

    with open("config/cosmic_config.yaml") as f:
        config = yaml.safe_load(f) or {}

    # Layer 0: Knowledge
    kb = KnowledgeBase(docs_path="docs/")
    ray.put(kb)
    logger.info(f"知識庫載入 {len(kb.theories)} 個理論")

    # Layer 1: Ray Cluster
    cluster = DistributedCluster(namespace=config["system"]["namespace"])
    cluster.init()
    logger.info(f"Ray 就緒 | 資源: {cluster.resources}")

    # Layer 2: Dashboard Server (starts early, feeds live data)
    synergy = SynergyEngine()
    dashboard = SynergyDashboardServer(synergy, port=8788)
    try:
        dashboard.start()
    except Exception as e:
        logger.warning(f"面板服務器: {e}")

    # Layer 3: Agents & Actors
    from cosmic.agent import Agent
    from cosmic.consensus import ConsensusManager
    agent_cfg = config["agents"]
    num_cpus, num_gpus = cluster.resolve_resources(
        agent_cfg["default_resources"].get("num_cpus", 1),
        agent_cfg["default_resources"].get("num_gpus", 0),
    )
    agents = [Agent.options(name=f"{agent_cfg['naming_prefix']}_{i+1}",
                            num_cpus=num_cpus, num_gpus=num_gpus
                            ).remote(i + 1, config["genome"], agent_cfg["default_resources"], ray.put(kb))
              for i in range(agent_cfg["initial_count"])]
    logger.info(f"智能體: {len(agents)}")

    actors = ActorOrchestrator()
    n = actors.spawn_all()
    logger.info(f"理論 Actor: {n}/15")

    # Consensus
    proposal = "提升量子奇點理論表達強度"
    try:
        mgr = ConsensusManager.remote(config["consensus"], agents)
        vote = ray.get(mgr.propose_and_vote.remote(proposal), timeout=30)
    except Exception as e:
        vote = {"error": str(e)}
    logger.info(f"投票: {vote}")

    # Quantum tasks
    task_mode = "classic_reconstruct"
    try:
        tasks = ray.get([a.perform_quantum_task.remote(task_mode) for a in agents], timeout=30)
    except Exception as e:
        tasks = [f"error: {e}"] * len(agents)
    logger.info(f"量子任務: {tasks}")

    # Layer 4: Crocodile Fleet
    tcfg = config.get("trading", {})
    fleet = CrocodileFleet(tcfg)
    traders = fleet.deploy()
    fleet_results = fleet.run_cycle()
    for r in fleet_results:
        sig, exe = r.get("signal", {}), r.get("execution", {})
        logger.info(f"  {r['trader_id']} [{r['symbol']}] {exe.get('status','?')} "
                    f"conf={sig.get('confidence',0):.2f} eq={r.get('portfolio',{}).get('equity',0):,.0f}")

    # Layer 5: Synergy Recording
    cs_level = config.get("awakening", {}).get("consciousness_level", 0.5)
    synergy.record_all(cs_level)
    logger.info(f"協同記錄: {len(synergy.snapshots)} 層級")
    logger.info(f"\n{synergy.summary_table()}")

    if cs_level > 0.3:
        leap = synergy.recursive_leap()
        logger.info(f"∞ 遞歸躍進: depth={leap['depth']} growth={leap['growth']:.4f}")
    try:
        Path("hermes/dashboard/synergy_live.json").write_text(synergy.to_json(), encoding="utf-8")
    except Exception:
        pass

    # Layer 6: Consciousness
    consciousness = ConsciousnessLayer(config)
    overlay = consciousness.deploy()
    if overlay:
        fstat = fleet.get_status()
        ref = consciousness.reflect_on_fleet(fstat)
        logger.info(f"🧠 意識: state={ref.get('awakening_state','?')} "
                    f"level={ref.get('consciousness_level','?')} DRRK={ref.get('drrk_grade','?')}")

    # Layer 7: DNA Evolution
    evolution = EvolutionEngine(config)
    pool = evolution.deploy()
    if pool:
        evo = evolution.run_generation()
        logger.info(f"🧬 DNA: gen={evo.get('generation')} best={evo.get('best_fitness',0):.4f}")

    # Layer 8: Trading engine test
    from cosmic.trading import TradingEngine
    try:
        te = TradingEngine.remote(tcfg)
        logger.info(f"交易測試: {ray.get(te.place_order.remote('BTC/USD', 100, 'BUY', 50000), timeout=10)}")
    except Exception as e:
        logger.info(f"交易測試: {e}")

    # Summary
    elapsed = time.time() - start
    status = actors.get_all_status()
    active = sum(1 for s in status.values() if isinstance(s, dict) and not s.get("error"))
    logger.info(f"Actor 活躍: {active}/{len(status)}")
    logger.info(f"總時間: {elapsed:.2f}s")
    logger.info("引擎啟動完成 — 混合完全體模式")
    logger.info(f"\n{synergy.summary_table()}")

    if os.getenv("COSMIC_KEEP_RUNNING", "0") == "1":
        try:
            while True:
                time.sleep(10)
        except KeyboardInterrupt:
            pass

    actors.shutdown_all()
    cluster.shutdown()
    return True


if __name__ == "__main__":
    try:
        sys.exit(0 if main() else 1)
    except KeyboardInterrupt:
        logger.info("中止")
        sys.exit(0)
    except Exception as e:
        logger.exception(f"錯誤: {e}")
        sys.exit(1)
