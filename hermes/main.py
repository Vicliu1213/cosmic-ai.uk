import ray
import yaml
from cosmic.agent import Agent
from cosmic.consensus import ConsensusManager
from cosmic.knowledge_base import KnowledgeBase
from src.core import build_default_registry

# 載入設定
with open("config/cosmic_config.yaml", "r") as f:
    config = yaml.safe_load(f)

# 初始化 Ray
ray.init(namespace=config["system"]["namespace"])

# 初始化知識庫
kb = KnowledgeBase(docs_path="docs/")
kb_ref = ray.put(kb)

# 建立全局技能註冊表
skill_registry = build_default_registry()
print("全局技能模塊:", list(skill_registry.entries.keys()))

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

# 建立共識管理器
consensus_mgr = ConsensusManager.remote(config["consensus"], agents)

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
    while True:
        time.sleep(10)
except KeyboardInterrupt:
    ray.shutdown()
