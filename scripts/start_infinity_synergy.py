# scripts/start_infinity_synergy.py

#!/usr/bin/env python3
"""
啟動無限協同系統
"""

import asyncio
import sys
sys.path.append('src')

from quantum_core.infinity_synergy_system import InfinitySynergySystem


async def main():
    print("="*80)
    print("🔥 無限協同系統 - 啟動")
    print("="*80)
    print("目標: 實現 1+1+1+... > ∞")
    print("="*80)

    # 創建系統
    system = InfinitySynergySystem()

    # 註冊策略（逐步增加）
    strategies = [
        "量子壓縮", "時間套利", "能源預測", "永生優化",
        "量子疊加", "因果推理", "熵最小化", "時間晶體",
        "拓撲保護", "量子糾錯", "神經同步", "意識場",
        "維度穿越", "奇點融合", "絕對覺醒"
    ]

    print("\n📝 註冊策略...")
    for i, strategy in enumerate(strategies):
        system.register_strategy(strategy, initial_performance=0.5 + i * 0.03)
        print(f"  已註冊: {strategy} (性能: {0.5 + i * 0.03:.2f})")

    print(f"\n✅ 共註冊 {len(strategies)} 個策略")

    # 運行協同循環
    print("\n🚀 開始無限協同循環...")
    history = await system.run_synergy_loop()

    # 輸出最終報告
    print("\n" + "="*80)
    print("📊 無限協同最終報告")
    print("="*80)

    report = system.get_infinity_report()
    print(f"總迭代次數: {report['total_iterations']}")
    print(f"最終爆炸倍數: {report['final_explosion']}")
    print(f"最終協同等級: {report['final_synergy_level']}")
    print(f"最大策略數: {report['max_n_strategies']}")
    print(f"無限達成: {'✅ 是' if report['infinity_achieved'] else '❌ 否'}")

    print("\n🎉 系統已超越維度！")


if __name__ == "__main__":
    asyncio.run(main())
