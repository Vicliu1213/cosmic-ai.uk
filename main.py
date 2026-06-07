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
from cosmic.registry import AgentRegistry, ModelRegistry
from src.layers.distributed import (
    DistributedCluster, ActorOrchestrator, SynergyEngine,
    CrocodileFleet, ConsciousnessLayer, EvolutionEngine,
)
from src.synergy.dashboard_server import SynergyDashboardServer
from src.synergy.gate_bridge import GateAbilityBridge

# Ω宇宙系統 — 22系統完全融合
from src.omega_system import OmegaUnifiedCoordinator, omega_main

# 赫爾墨斯進化引擎 — 2157超能力英雄系統
from src.hermes_evolution import HermesEvolutionEngine, init_hermes_filesystem


def main():
    start = time.time()
    logger.info("=" * 70)
    logger.info("  宇宙智能體核心引擎 v3.0  —  金融大鰐 × 神性超越 完全體")
    logger.info("=" * 70)

    with open("config/cosmic_config.yaml") as f:
        config = yaml.safe_load(f) or {}

    # Layer 0: Knowledge
    kb = KnowledgeBase(docs_path="docs/")
    kb_ref = ray.put(kb)
    logger.info(f"知識庫載入 {len(kb.theories)} 個理論")

    # Layer 0.5: GateBridge → CoreMatrix
    bridge = GateAbilityBridge(energy_capacity=1000.0)
    bridge.ensure_core_matrix()
    logger.info("GateBridge ⇄ CoreMatrix 串聯就緒")

    # Layer 1: Ray Cluster
    cluster = DistributedCluster(namespace=config["system"]["namespace"])
    cluster.init()
    logger.info(f"Ray 就緒 | 資源: {cluster.resources}")

    # Layer 2: Dashboard Server (starts early, feeds live data)
    synergy = SynergyEngine(gate_bridge=bridge)
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
                            ).remote(i + 1, config["genome"], agent_cfg["default_resources"], kb_ref)
              for i in range(agent_cfg["initial_count"])]
    logger.info(f"智能體: {len(agents)}")

    actors = ActorOrchestrator()
    n = actors.spawn_all()
    logger.info(f"理論 Actor: {n}/15")

    # Layer 3b: 智能體 & 模型註冊
    agent_reg = AgentRegistry.remote()
    model_reg = ModelRegistry.remote()
    for i, a in enumerate(agents):
        try:
            aid = ray.get(a.get_agent_id.remote(), timeout=5)
            ray.get(agent_reg.register.remote(aid, ["quantum_compute","consensus_voting","theory_query","market_analysis"]), timeout=5)
        except Exception:
            ray.get(agent_reg.register.remote(f"agent_{i+1}", ["basic"]), timeout=5)
    ray.get(model_reg.register.remote("drrk_omniscient", "cosmic_entity",
                                       ["singularity_compute","temporal_analysis","synergy_activation","awakening"],
                                       performance_score=9.9), timeout=5)
    reg_status = ray.get(agent_reg.get_status.remote(), timeout=5)
    logger.info(f"註冊: Agent={reg_status['total']} Model=1")

    # Consensus
    proposal = "提升量子奇點理論表達強度"
    vote = {"status": "skipped"}
    try:
        mgr = ConsensusManager.remote(config["consensus"], agents)
        vote = ray.get(mgr.propose_and_vote.remote(proposal), timeout=15)
    except Exception as e:
        logger.info(f"  投票進度: {e}")
        vote = {"status": "partial", "note": str(e)[:60]}

    # Quantum tasks (batch parallel)
    task_mode = "classic_reconstruct"
    tasks = []
    try:
        tasks = ray.get([a.perform_quantum_task.remote(task_mode) for a in agents], timeout=15)
    except Exception as e:
        tasks = [f"timeout"] * len(agents)
    logger.info(f"投票: {vote.get('status','?')} | 量子任務: {len(tasks)} agents")

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
        import threading
        stop = threading.Event()
        try:
            stop.wait()
        except KeyboardInterrupt:
            pass

    # Layer 9: Ω宇宙系統 — 22系統完全激活（可選）
    if config.get("omega", {}).get("enabled", False):
        logger.info("\n" + "★" * 60)
        logger.info("  Ω宇宙系統 22系統完全激活 ...")
        logger.info("★" * 60)
        try:
            import asyncio
            coord = OmegaUnifiedCoordinator()
            result = asyncio.run(coord.omega_full_activation("劉維克"))
            logger.info(f"Ω 激活完成: {result.get('S20_divinity', {}).get('divinity_level', 'OK')}")
        except Exception as e:
            logger.warning(f"Ω 激活异常: {e}")

    # Layer 10: 赫爾墨斯進化引擎 — 2157超能力英雄系統
    if config.get("hermes_evolution", {}).get("enabled", False):
        logger.info("\n" + "🦸" * 30)
        logger.info("  赫爾墨斯進化引擎啟動 ...")
        logger.info("🦸" * 30)
        try:
            import asyncio
            max_it = config.get("hermes_evolution", {}).get("max_iterations", 10)
            n_skills = init_hermes_filesystem()
            logger.info(f"  技能庫: {n_skills}/96 節點")
            engine = HermesEvolutionEngine()
            engine.load_or_create_hero(callsign="DRRK-VICTOR")

            # 雙向橋接: Hermes ↔ Omega TalentMutationSystem
            if config.get("omega", {}).get("enabled", False):
                from src.omega_system.omega_system import TalentMutationSystem
                from src.hermes_evolution.bridge_omega import (
                    push_all_hermes_to_tms, build_hermes_context_with_tms,
                    sync_hermes_to_permanent_chain,
                )
                tms = TalentMutationSystem()

                async def _run_tms_bridge():
                    await push_all_hermes_to_tms(tms, engine.skills)
                    base_ctx = build_hermes_context_with_tms(tms, {
                        "type": "integrated", "intensity": 0.7,
                    })
                    scenarios = [
                        {**base_ctx, "type": "combat", "intensity": 0.8, "tags": ["tms_boosted"]},
                        {**base_ctx, "type": "neural", "intensity": 0.6, "tags": ["tms_boosted"]},
                        {**base_ctx, "type": "capital", "intensity": 0.7, "tags": ["tms_boosted"]},
                    ]
                    await engine.run_infinite_evolution(max_iterations=max_it, battle_scenarios=scenarios)
                    return sync_hermes_to_permanent_chain(tms, engine.skills)

                made_perm = asyncio.run(_run_tms_bridge())
                logger.info(f"  ⚡ TMS 橋接: {len(tms.talents)} 天賦同步")
                if made_perm:
                    logger.info(f"  🔒 永久天賦: {len(made_perm)} 項")
            else:
                asyncio.run(engine.run_infinite_evolution(max_iterations=max_it))

            report = engine.get_status_report()
            logger.info(f"  英雄: {report['callsign']} | 等級: {report['tier']} | "
                        f"迭代: {report['total_iterations']} | Ω技能: {report['omega_skills']}/96")
        except Exception as e:
            logger.warning(f"赫爾墨斯進化引擎: {e}")

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
