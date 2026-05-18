import ray
import yaml
import os
from cosmic.agent import Agent
from cosmic.consensus import ConsensusManager
from cosmic.knowledge_base import KnowledgeBase
from src.core import build_default_registry


def resolve_agent_resources(default_resources):
    cluster_resources = ray.cluster_resources()

    num_cpus = default_resources.get("num_cpus", 1)
    if cluster_resources.get("CPU", 0) and num_cpus > cluster_resources.get("CPU", 0):
        num_cpus = max(1, int(cluster_resources.get("CPU", 0)))

    num_gpus = default_resources.get("num_gpus", 0)
    if num_gpus and cluster_resources.get("GPU", 0) < num_gpus:
        print("⚠️ 本地環境無足夠 GPU，已自動降級為 0")
        num_gpus = 0

    resources = {}
    for name, value in default_resources.get("resources", {}).items():
        if cluster_resources.get(name, 0) >= value:
            resources[name] = value
        else:
            print(f"⚠️ 跳過本地不可用自定義資源: {name}={value}")

    return num_cpus, num_gpus, resources


def pick_task_mode():
    cluster_resources = ray.cluster_resources()
    return "grover" if cluster_resources.get("GPU", 0) >= 0.5 else "classic_reconstruct"

# 載入設定
with open("config/cosmic_config.yaml", "r") as f:
    config = yaml.safe_load(f)

# 初始化 Ray
ray.init(namespace=config["system"]["namespace"], ignore_reinit_error=True)

num_cpus, num_gpus, resources = resolve_agent_resources(config["agents"]["default_resources"])

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
        num_cpus=num_cpus,
        num_gpus=num_gpus,
        resources=resources
    ).remote(i+1, config["genome"], config["agents"]["default_resources"], kb_ref)
    agents.append(agent)

# 建立共識管理器
consensus_mgr = ConsensusManager.remote(config["consensus"], agents)

# 測試提案
proposal = "提升量子奇點理論表達強度"
result = ray.get(consensus_mgr.propose_and_vote.remote(proposal))
print("投票結果:", result)

# 並行執行任務，沒 GPU 時自動降維為經典重構
task_mode = pick_task_mode()
task_refs = [agent.perform_quantum_task.remote(task_mode) for agent in agents]
task_results = ray.get(task_refs)
print(f"並行任務結果 ({task_mode}):", task_results)

if os.getenv("COSMIC_KEEP_RUNNING", "0") == "1":
    import time

    try:
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        ray.shutdown()
else:
    ray.shutdown()
