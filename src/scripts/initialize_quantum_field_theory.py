#!/usr/bin/env python3
"""
量子場論系統初始化腳本
Initialize the Quantum Field Theory Full System
"""

import sys
import json
import logging
from pathlib import Path

# Add project root to path
sys.path.insert(0, '/workspaces/cosmic-ai.uk')

from quantum_field_theory_system.qft_engine import (
    QuantumFieldTheoryEngine,
    QuantumOperator,
    QuantumFieldMode
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    """初始化量子場論系統"""
    logger.info("=" * 60)
    logger.info("🚀 量子場論全系統初始化")
    logger.info("=" * 60)
    
    # 創建引擎
    qft_engine = QuantumFieldTheoryEngine(lattice_size=8, hilbert_dim=256)
    
    # 第1步: 創建量子場晶格
    logger.info("\n[第1步] 創建量子場晶格...")
    qft_engine.create_quantum_field_lattice()
    
    # 第2步: 建立場點糾纏網絡
    logger.info("\n[第2步] 建立量子場點糾纏連接...")
    qft_engine.establish_field_entanglement()
    
    # 第3步: 創建量子態
    logger.info("\n[第3步] 創建量子態...")
    qft_engine.create_quantum_states(num_states=64)
    
    # 第4步: 應用量子算子
    logger.info("\n[第4步] 應用量子算子...")
    
    # 獲取一些場點用於操作
    field_point_ids = list(qft_engine.field_points.keys())[:32]
    
    # 應用產生算子
    qft_engine.apply_quantum_operator(
        QuantumOperator.CREATION,
        field_point_ids[:8],
        "op_creation_001"
    )
    
    # 應用湮滅算子
    qft_engine.apply_quantum_operator(
        QuantumOperator.ANNIHILATION,
        field_point_ids[8:16],
        "op_annihilation_001"
    )
    
    # 應用數算子
    qft_engine.apply_quantum_operator(
        QuantumOperator.NUMBER,
        field_point_ids[16:24],
        "op_number_001"
    )
    
    # 應用哈密頓量
    qft_engine.apply_quantum_operator(
        QuantumOperator.HAMILTONIAN,
        field_point_ids[24:32],
        "op_hamiltonian_001"
    )
    
    # 第5步: 實現混合量子算法
    logger.info("\n[第5步] 實現增強的混合量子算法...")
    
    algorithms = [
        "variational_quantum_eigensolver",
        "qaoa",
        "quantum_phase_estimation",
        "amplitude_amplification",
        "quantum_fourier_transform"
    ]
    
    for algo in algorithms:
        qft_engine.implement_hybrid_quantum_algorithm(algo)
    
    # 第6步: 更新量子相干網絡
    logger.info("\n[第6步] 更新量子相干網絡...")
    qft_engine.update_coherence_network()
    
    # 第7步: 計算並匯出系統狀態
    logger.info("\n[第7步] 計算系統狀態...")
    system_state = qft_engine.calculate_system_state()
    logger.info(f"✅ 系統狀態:")
    logger.info(f"   - 量子場點: {system_state['field_points']}")
    logger.info(f"   - 量子態: {system_state['quantum_states']}")
    logger.info(f"   - 場操作: {system_state['field_operations']}")
    logger.info(f"   - 量子糾纏: {system_state['total_entanglement']}")
    logger.info(f"   - 平均相干性: {system_state['avg_coherence']:.4f}")
    logger.info(f"   - 平均能量密度: {system_state['avg_energy_density']:.4f}")
    
    # 匯出完整狀態
    logger.info("\n[第8步] 匯出系統狀態...")
    full_state = qft_engine.export_system_state()
    
    # 保存到JSON
    export_file = Path("/workspaces/cosmic-ai.uk/quantum_field_theory_system/system_state_export.json")
    with open(export_file, 'w') as f:
        json.dump(full_state, f, indent=2, default=str)
    
    logger.info(f"✅ 系統狀態已保存: {export_file}")
    
    # 生成報告
    logger.info("\n" + "=" * 60)
    logger.info("📊 量子場論系統初始化報告")
    logger.info("=" * 60)
    logger.info(f"✅ 量子場晶格大小: {qft_engine.lattice_size}³ = {len(qft_engine.field_points)} 個量子場點")
    logger.info(f"✅ Hilbert空間維度: {qft_engine.hilbert_dim}")
    logger.info(f"✅ 量子態: {len(qft_engine.quantum_states)} 個")
    logger.info(f"✅ 場操作: {len(qft_engine.field_operations)} 個")
    logger.info(f"✅ 量子糾纏連接: {sum(len(partners) for partners in qft_engine.entanglement_graph.values()) // 2} 個")
    logger.info(f"✅ 實現混合算法: {len(algorithms)} 個")
    logger.info(f"✅ 系統相干性: {system_state['avg_coherence']:.4%}")
    logger.info("\n🎉 量子場論系統初始化完成!")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
