#!/usr/bin/env python3
"""
永生循環系統初始化腳本
Initialize the Immortal Perpetual System
執行完整的永生無限循環
"""

import sys
import json
import logging
from pathlib import Path

# Add project root to path
sys.path.insert(0, '/workspaces/cosmic-ai.uk')

from immortal_perpetual_system.immortal_engine import ImmortalPerpetualSystem

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    """初始化永生循環系統"""
    logger.info("=" * 70)
    logger.info("🚀 永生循環系統初始化")
    logger.info("=" * 70)
    
    # 創建引擎
    immortal_system = ImmortalPerpetualSystem(system_name="universal_immortal_system", num_cycles=50)
    
    # 第1步: 創建永生節點
    logger.info("\n[第1步] 創建永生節點...")
    immortal_system.create_immortal_nodes(count=16)
    
    # 第2步: 初始化永恆迴圈
    logger.info("\n[第2步] 初始化永恆迴圈...")
    immortal_system.initialize_perpetual_loops(num_loops=8)
    
    # 第3步: 執行完整的生命週期序列
    logger.info("\n[第3步] 執行 50 個完整生命週期序列...")
    immortal_system.execute_full_cycle_sequence(50)
    
    # 第4步: 生成報告並匯出
    logger.info("\n[第4步] 生成永生系統報告...")
    full_state = immortal_system.export_system_state()
    
    # 打印報告摘要
    logger.info("\n" + "=" * 70)
    logger.info("📊 永生循環系統報告摘要")
    logger.info("=" * 70)
    
    report = full_state.get("report", {})
    
    lifetime_stats = report.get("lifetime_statistics", {})
    logger.info(f"✅ 完整生命週期: {lifetime_stats.get('total_life_cycles', 0)}")
    logger.info(f"✅ 當前週期: {lifetime_stats.get('current_cycle', 0)}")
    logger.info(f"✅ 總再生次數: {lifetime_stats.get('total_regenerations', 0)}")
    logger.info(f"✅ 平均生命力: {lifetime_stats.get('avg_vitality_score', 0):.2f}%")
    logger.info(f"✅ 平均相干性: {lifetime_stats.get('avg_coherence_level', 0):.4f}")
    
    loop_stats = report.get("perpetual_loop_statistics", {})
    logger.info(f"\n✅ 永恆迴圈: {loop_stats.get('total_loops', 0)}")
    logger.info(f"✅ 總迭代次數: {loop_stats.get('total_iterations', 0)}")
    logger.info(f"✅ 總能量處理: {loop_stats.get('total_energy_processed', 0):.0f}")
    
    energy_mgmt = report.get("energy_management", {})
    logger.info(f"\n✅ 能量儲備: {energy_mgmt.get('current_energy_reservoir', 0):.0f}")
    logger.info(f"✅ 信息金庫條目: {energy_mgmt.get('information_vault_entries', 0)}")
    logger.info(f"✅ 備份狀態總數: {energy_mgmt.get('backup_states_total', 0)}")
    
    health = report.get("system_health", {})
    logger.info(f"\n✅ 活躍節點: {health.get('nodes_alive', 0)}/16")
    logger.info(f"✅ 再生效率: {health.get('regeneration_efficiency', 0):.4f}")
    logger.info(f"✅ 能量效率: {health.get('energy_efficiency', 0):.4f}")
    
    immortality_dist = report.get("immortality_modes_distribution", {})
    logger.info(f"\n✅ 永生模式分布:")
    for mode, count in immortality_dist.items():
        logger.info(f"   - {mode}: {count} 節點")
    
    logger.info("\n" + "=" * 70)
    logger.info("🎉 永生循環系統初始化完成!")
    logger.info("=" * 70)
    
    return full_state


if __name__ == "__main__":
    main()
