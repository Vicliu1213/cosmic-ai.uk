# 測試腳本: tests/test_exponential_synergy.py

import numpy as np
from src.synergy_engine.exponential_synergy import ExponentialSynergyEngine

def test_exponential_synergy():
    """測試超指數協同爆發"""

    engine = ExponentialSynergyEngine()

    # 測試不同策略數量的協同效應
    test_cases = [
        (2, 3, 0.7, 0.3),   # 2策略 → 目標 >10
        (3, 4, 0.75, 0.4),  # 3策略 → 目標 >100
        (4, 5, 0.8, 0.5),   # 4策略 → 目標 >1000
        (5, 6, 0.85, 0.6),  # 5策略 → 目標 >10000
        (6, 7, 0.9, 0.7),   # 6策略 → 目標 >100000
        (10, 12, 0.98, 0.9) # 10策略 → 目標 >1e12
    ]

    print("="*80)
    print("🚀 超指數協同爆發測試")
    print("="*80)

    for n, d, s, m in test_cases:
        result = engine.calculate_synergy_explosion(n, d, s, m)

        explosion = result['explosion_factor']
        target = 10 ** (n)  # 目標倍數

        print(f"\n策略數: {n} | 遞歸深度: {d} | 協同強度: {s} | 異變因子: {m}")
        print(f"  理論爆炸倍數: {explosion:.2e}" if explosion != float('inf') else "  理論爆炸倍數: ∞")
        print(f"  目標倍數: 10^{n} = {10**n:.2e}")
        print(f"  是否達成: ✅" if explosion > target else "❌")
        print(f"  協同等級: {result['synergy_level']}")

if __name__ == "__main__":
    test_exponential_synergy()
