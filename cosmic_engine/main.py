import ray
import yaml
import logging
import asyncio
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
logger.info(f"Ray initialized: {config['system']['name']} v{config['system']['version']}")

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
    ).remote(i+1, config["genome"], config["agents"]["default_resources"], kb_ref)
    agents.append(agent)
logger.info(f"{len(agents)} agents initialized")

# 建立共識管理器
consensus_mgr = ConsensusManager.remote(config["consensus"], agents)
logger.info("Consensus Manager initialized")

# Initialize Fault Tolerance System
if config.get("fault_tolerance", {}).get("enabled", False):
    fault_tolerance = FaultToleranceOrchestrator.remote(config["fault_tolerance"], agents)
    logger.info("🔧 Fault Tolerance System initialized - AUTO REPAIR MODE: ALWAYS ON")
    if config["fault_tolerance"].get("auto_repair_enabled"):
        logger.info("   ✅ Auto-repair functionality ENABLED as default mode")
else:
    fault_tolerance = None

# Initialize Quantum Error Correction System
if config.get("error_correction", {}).get("enabled", False):
    error_correction = QuantumErrorCorrectionEngine.remote(config["error_correction"])
    logger.info("🛡️ Quantum Error Correction System initialized - AUTO CORRECTION MODE: CONTINUOUS")
    if config["error_correction"].get("auto_correction_enabled"):
        logger.info("   ✅ Auto-correction functionality ENABLED as default mode")
else:
    error_correction = None

# Initialize Self-Evolution Learning System
if config.get("self_evolution", {}).get("enabled", False):
    self_evolution = SelfEvolutionEngine.remote(config["self_evolution"], agents)
    logger.info("🧠 Self-Evolution Learning System initialized - AUTO LEARNING MODE: CONTINUOUS")
    if config["self_evolution"].get("auto_optimization_enabled"):
        logger.info("   ✅ Auto-optimization functionality ENABLED as default mode")
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
import time
try:
    logger.info("="*60)
    logger.info("✨ 宇宙智能體系統運行中 - 自動修復常態已啟動 ✨")
    logger.info("="*60)
    
    cycle_count = 0
    while True:
        cycle_count += 1
        
        # Auto-repair health check with Fault Tolerance System
        if fault_tolerance is not None and config["fault_tolerance"].get("auto_repair_enabled"):
            health_status = ray.get(fault_tolerance.perform_health_check.remote())
            if cycle_count % 5 == 0:
                logger.info(f"🔧 [Cycle {cycle_count}] 容错系统健康检查 - 自动修复状态: 活跃")
        
        # Auto-correction error synchronization (continuous mode)
        if error_correction is not None and config["error_correction"].get("auto_correction_enabled"):
            if cycle_count % 3 == 0:
                logger.debug(f"🛡️ [Cycle {cycle_count}] 量子纠错系统连续运行中...")
        
        # Auto-learning updates (continuous mode)
        if self_evolution is not None and config["self_evolution"].get("auto_optimization_enabled"):
            if cycle_count % 2 == 0:
                logger.debug(f"🧠 [Cycle {cycle_count}] 自进化系统持续学习中...")
        
        time.sleep(2)
except KeyboardInterrupt:
    logger.info("="*60)
    logger.info("🛑 正在关闭Ray集群...")
    logger.info("="*60)
    ray.shutdown()
    logger.info("✅ Ray集群关闭完成")
