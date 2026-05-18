"""
异能矩阵演示入口
"""
import asyncio
import logging
from hermes.src.异能矩阵 import AbilityConfig, AbilityType
from hermes.src.异能矩阵.核心矩阵 import CoreMatrix

logging.basicConfig(level=logging.INFO, format='%(message)s')

async def demo():
    matrix = CoreMatrix()

    fireball = AbilityConfig(
        ability_id="fire_001", name="火球术",
        ability_type=AbilityType.OFFENSIVE,
        base_energy_cost=50.0, base_cooldown=5.0,
        synergy_tags=['fire', 'projectile', 'aoe']
    )
    shield = AbilityConfig(
        ability_id="def_001", name="能量护盾",
        ability_type=AbilityType.DEFENSIVE,
        base_energy_cost=30.0, base_cooldown=10.0,
        synergy_tags=['defense', 'barrier']
    )
    heal = AbilityConfig(
        ability_id="sup_001", name="治疗术",
        ability_type=AbilityType.SUPPORT,
        base_energy_cost=40.0, base_cooldown=8.0,
        synergy_tags=['heal', 'support']
    )

    print("\n" + "="*60)
    print("🎮 异能矩阵系统演示")
    print("="*60 + "\n")

    await matrix.activate_ability(fireball, intensity=0.8)
    await matrix.activate_ability(shield)

    print("\n" + "="*60)
    print("📊 系统状态")
    print("="*60)
    status = matrix.get_system_status()
    e = status['energy_status']
    print(f"能量状态: {e['current']:.1f}/{e['capacity']:.1f} ({e['percentage']:.1f}%)")
    print(f"激活中的异能: {status['active_abilities']}")
    print(f"冷却中的异能: {status['cooling_abilities']}")
    print(f"系统健康度: {status['system_health']}")

    print("\n" + "="*60)
    print("🎨 组合生成演示")
    print("="*60)
    combos = matrix.combo_generator.generate_combinations([fireball, shield, heal], combo_size=2)
    for combo in combos[:3]:
        print(f"  {combo['combo_name']} → {combo['recommendation']} (评分: {combo['total_score']:.1f})")

    print("\n" + "="*60)
    print("🔗 协同分析演示")
    print("="*60)
    analysis = matrix.synergy_analyzer.analyze_group([fireball, shield, heal])
    print(f"整体协同分: {analysis['total_synergy']:.1f}")
    multiplier = matrix.synergy_calculator.calculate_multiplier([fireball, shield, heal])
    print(f"协同倍率: {multiplier:.2f}x")

if __name__ == "__main__":
    asyncio.run(demo())
