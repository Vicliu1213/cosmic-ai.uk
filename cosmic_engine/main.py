import ray
import yaml
import logging
import time
from cosmic.agent import Agent
from cosmic.consensus import ConsensusManager
from cosmic.knowledge_base import KnowledgeBase
from cosmic.fault_tolerance import FaultToleranceOrchestrator
from cosmic.error_correction import QuantumErrorCorrectionEngine
from cosmic.self_evolution import SelfEvolutionEngine

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 載入設定
with open("config/cosmic_config.yaml", "r") as f:
    config = yaml.safe_load(f)

# 初始化 Ray
ray.init(namespace=config["system"]["namespace"])
system_name = config['system']['name']
system_version = config['system']['version']
msg = f"Ray initialized: {system_name} v{system_version}"
logger.info(msg)

# 初始化知識庫
kb = KnowledgeBase(docs_path="docs/")
kb_ref = ray.put(kb)
logger.info("Knowledge Base initialized")

# 建立 Agents
agents = []
for i in range(config["agents"]["initial_count"]):
    agent = Agent.options(
        name=f"{config['agents']['naming_prefix']}_{i+1}",
        num_cpus=config["agents"]["default_resources"]["num_cpus"],
        num_gpus=config["agents"]["default_resources"]["num_gpus"],
        resources=config["agents"]["default_resources"]["resources"]
    ).remote(i+1, config["genome"],
             config["agents"]["default_resources"], kb_ref)
    agents.append(agent)
logger.info(f"{len(agents)} agents initialized")

# 建立共識管理器
consensus_mgr = ConsensusManager.remote(config["consensus"], agents)
logger.info("Consensus Manager initialized")

# Initialize Fault Tolerance System
if config.get("fault_tolerance", {}).get("enabled", False):
    ft_config = config["fault_tolerance"]
    fault_tolerance = FaultToleranceOrchestrator.remote(ft_config, agents)
    msg = "🔧 Fault Tolerance System initialized - AUTO REPAIR MODE: ALWAYS ON"
    logger.info(msg)
    if config["fault_tolerance"].get("auto_repair_enabled"):
        logger.info("   ✅ Auto-repair functionality ENABLED as default mode")
else:
    fault_tolerance = None

# Initialize Quantum Error Correction System
if config.get("error_correction", {}).get("enabled", False):
    ec_config = config["error_correction"]
    error_correction = QuantumErrorCorrectionEngine.remote(ec_config)
    msg = ("🛡️ Quantum Error Correction System initialized - "
           "AUTO CORRECTION MODE: CONTINUOUS")
    logger.info(msg)
    if config["error_correction"].get("auto_correction_enabled"):
        msg = "   ✅ Auto-correction functionality ENABLED as default mode"
        logger.info(msg)
else:
    error_correction = None

# Initialize Self-Evolution Learning System
if config.get("self_evolution", {}).get("enabled", False):
    se_config = config["self_evolution"]
    self_evolution = SelfEvolutionEngine.remote(se_config, agents)
    msg = ("🧠 Self-Evolution Learning System initialized - "
           "AUTO LEARNING MODE: CONTINUOUS")
    logger.info(msg)
    if config["self_evolution"].get("auto_optimization_enabled"):
        msg = "   ✅ Auto-optimization functionality ENABLED as default mode"
        logger.info(msg)
else:
    self_evolution = None

# 測試提案
proposal = "提升量子奇點理論表達強度"
result = ray.get(consensus_mgr.propose_and_vote.remote(proposal))
print("投票結果:", result)

# 執行一個量子任務
task_result = ray.get(agents[0].perform_quantum_task.remote("grover"))
print("Agent 1 任務結果:", task_result)

# 保持運行
try:
    logger.info("="*60)
    logger.info("✨ 宇宙智能體系統運行中 - 自動修復常態已啟動 ✨")
    logger.info("="*60)

    cycle_count = 0
    while True:
        cycle_count += 1

        # Auto-repair health check with Fault Tolerance System
        ft_config = config.get("fault_tolerance", {})
        if (fault_tolerance is not None and
                ft_config.get("auto_repair_enabled")):
            health_status = ray.get(
                fault_tolerance.perform_health_check.remote())
            if cycle_count % 5 == 0:
                msg = (f"🔧 [Cycle {cycle_count}] 容错系统健康检查 - "
                       f"自动修复状态: 活跃")
                logger.info(msg)

        # Auto-correction error synchronization (continuous mode)
        ec_config = config.get("error_correction", {})
        if (error_correction is not None and
                ec_config.get("auto_correction_enabled")):
            if cycle_count % 3 == 0:
                msg = (f"🛡️ [Cycle {cycle_count}] "
                       f"量子纠错系统连续运行中...")
                logger.debug(msg)

        # Auto-learning updates (continuous mode)
        se_config = config.get("self_evolution", {})
        if (self_evolution is not None and
                se_config.get("auto_optimization_enabled")):
            if cycle_count % 2 == 0:
                msg = (f"🧠 [Cycle {cycle_count}] "
                       f"自进化系统持续学习中...")
                logger.debug(msg)

        # ==================== 三 Agent 信號接收流程 ====================
        # 1. 獲取市場數據 (A)
        try:
            # 從前三個 Agent 獲取計算信號
            if len(agents) >= 3:
                # 2. 分發給三個 Agent (B -> C, D, E)
                #    每個 agent 都有 compute_signal 方法返回原始信號
                signal_futures = [
                    agents[0].compute_signal.remote({"cycle": cycle_count}),
                    agents[1].compute_signal.remote({"cycle": cycle_count}),
                    agents[2].compute_signal.remote({"cycle": cycle_count})
                ]
                raw_signals = ray.get(signal_futures)

                # 3. 將原始信號傳給信號聚合器 (C, D, E -> F)
                # 簡單的聚合邏輯 - 可根據需求增強
                strengths = [s.get("strength", 0) for s in raw_signals]
                consensus_val = (sum(strengths) / len(raw_signals)
                                 if raw_signals else 0)
                aggregated_signal = {
                    "signal_count": len(raw_signals),
                    "signals": raw_signals,
                    "consensus": consensus_val
                }

                # 4. 將最終指令發送給執行層 (F -> G)
                if cycle_count % 10 == 0:
                    msg = (f"📊 [Cycle {cycle_count}] 信號聚合完成 - "
                           f"共識度: {aggregated_signal['consensus']:.2f}")
                    logger.info(msg)

                # 5. 接收成交回報 (J -> B) 並進行學習更新
                for i, agent in enumerate(agents[:3]):
                    agent.update_with_execution.remote({
                        "cycle": cycle_count,
                        "signal_index": i,
                        "aggregated_result": aggregated_signal
                    })
        except Exception as e:
            logger.error(f"❌ [Cycle {cycle_count}] 信號處理異常: {e}")

        time.sleep(2)
except KeyboardInterrupt:
    logger.info("="*60)
    logger.info("🛑 正在关闭Ray集群...")
    logger.info("="*60)
    ray.shutdown()
    logger.info("✅ Ray集群关闭完成")
