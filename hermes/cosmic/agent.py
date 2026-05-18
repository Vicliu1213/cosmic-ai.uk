import ray
import random
from cosmic import quantum_tasks

@ray.remote
class Agent:
    def __init__(self, agent_id, genome_config, resources, kb_ref):
        self.id = agent_id
        self.genome = genome_config["theories"]
        self.resources = resources
        self.reputation = 1.0
        self.kb = ray.get(kb_ref) if isinstance(kb_ref, ray.ObjectRef) else kb_ref
        self.known_theories = {}
        for theory in self.genome:
            name = theory['name']
            details = self.kb.get_theory(name)
            if details:
                self.known_theories[name] = details['summary']
        print(f"Agent {self.id} 已載入 {len(self.known_theories)} 個理論知識")

    def vote(self, proposal):
        decision = random.choice(["approve", "reject"])
        weight = self.reputation
        return {"agent_id": self.id, "decision": decision, "weight": weight}

    def update_reputation(self, delta):
        self.reputation += delta

    def query_theory(self, theory_name):
        return self.kb.get_theory(theory_name)

    def perform_quantum_task(self, task_type, **kwargs):
        if task_type == "grover":
            return quantum_tasks.run_grover(**kwargs)
        elif task_type == "shor":
            return quantum_tasks.run_shor(**kwargs)
        elif task_type == "annealing":
            return quantum_tasks.run_annealing(**kwargs)
        elif task_type == "classic_reconstruct":
            return quantum_tasks.run_classic_reconstruction(**kwargs)
        else:
            return f"未知任務: {task_type}"
