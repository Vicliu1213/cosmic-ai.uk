import ray

@ray.remote
class ConsensusManager:
    def __init__(self, consensus_config, agents):
        self.config = consensus_config
        self.agents = agents
        print(f"共識管理器啟動，演算法: {self.config['algorithm']}")

    def propose_and_vote(self, proposal):
        if self.config["algorithm"] != "weighted_voting":
            return {"error": "不支援的演算法"}
        vote_refs = [agent.vote.remote(proposal) for agent in self.agents]
        results = ray.get(vote_refs)
        total_weight = 0.0
        approve_weight = 0.0
        for r in results:
            weight = r["weight"] * self.config.get("default_vote_weight", 1.0)
            total_weight += weight
            if r["decision"] == "approve":
                approve_weight += weight
        approval_rate = approve_weight / total_weight if total_weight else 0
        passed = approval_rate >= self.config["voting_threshold"]
        return {"proposal": proposal, "passed": passed, "approval_rate": approval_rate}
