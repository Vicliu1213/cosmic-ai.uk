import time
from src.algorithms.enhanced_classic import build_default_registry

def run_grover(search_space=1000000):
    time.sleep(0.1)
    return f"Grover 搜尋完成，空間 {search_space}"

def run_shor(number=15):
    time.sleep(0.2)
    return f"Shor 分解完成，數字 {number}"

def run_annealing(problem_size=100):
    time.sleep(0.15)
    return f"量子退火完成，問題規模 {problem_size}"


def run_classic_reconstruction(top_k=3):
    registry = build_default_registry()
    return {
        "mode": "classic_reconstruction",
        "recommendations": registry.recommend(top_k=top_k),
    }
