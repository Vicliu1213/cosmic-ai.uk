import ray
import yaml
import os
from cosmic.agent import Agent
from cosmic.consensus import ConsensusManager
from cosmic.knowledge_base import KnowledgeBase
# main.py（核心改動：模擬 → 真實）

import agents.tools.market_data as md          # ← 取代原來的模擬 tools
from agents.tools.perp_subscribe import perp_subscribe_tool  # ← 真實 WebSocket

from core.orchestrator import SeripAgent

# 直接使用 md.xxx 取代原來的 get_xxx 工具
# 例如：md.get_all_symbols() / md.get_market_stats() / md.get_current_price()

def resolve_agent_resources(default_resources):
    cluster_resources = ray.cluster_resources()

    num_cpus = min(default_resources.get("num_cpus", 1), max(1, int(cluster_resources.get("CPU", 1))))
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


def resolve_agent_count(default_count, num_cpus):
    available_cpus = max(1, int(ray.cluster_resources().get("CPU", 1)))
    max_by_cpu = max(1, available_cpus // max(1, num_cpus))
    return max(1, min(default_count, max_by_cpu))


def pick_task_mode():
    cluster_resources = ray.cluster_resources()
    return "grover" if cluster_resources.get("GPU", 0) >= 0.5 else "classic_reconstruct"


# 載入設定
with open("config/cosmic_config.yaml", "r") as f:
    config = yaml.safe_load(f)

# 初始化 Ray
ray.init(namespace=config["system"]["namespace"], ignore_reinit_error=True)

num_cpus, num_gpus, resources = resolve_agent_resources(config["agents"]["default_resources"])
agent_count = resolve_agent_count(config["agents"]["initial_count"], num_cpus)

# 初始化知識庫
kb = KnowledgeBase(docs_path="docs/")
kb_ref = ray.put(kb)

# 建立 Agents
agents = []
for i in range(agent_count):
    agent = Agent.options(
        name=f"{config['agents']['naming_prefix']}_{i+1}",
        num_cpus=num_cpus,
        num_gpus=num_gpus,
        resources=resources
    ).remote(i+1, config["genome"], config["agents"]["default_resources"], kb_ref)
    agents.append(agent)

proposal = "提升量子奇點理論表達強度"
if len(agents) > 1:
    consensus_mgr = ConsensusManager.remote(config["consensus"], agents)
    result = ray.get(consensus_mgr.propose_and_vote.remote(proposal))
    print("投票結果:", result)
else:
    print("投票結果:", {"proposal": proposal, "passed": True, "mode": "single_agent"})

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
