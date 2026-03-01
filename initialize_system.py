#!/usr/bin/env python3
"""
全系統初始化腳本
Complete System Initialization Script

初始化所有三個系統並建立連接
"""

import sys
from pathlib import Path

# 添加項目路徑
sys.path.insert(0, str(Path(__file__).parent))

from quantum_entanglement_system.entanglement_manager import (
    GlobalSyncManager, SubsystemType, UniverseState
)
from deep_connection_network.network_manager import (
    NetworkTopologyManager, NetworkNode
)
from multiverse_integration.multiverse_manager import MultiverseManager
from global_sync_orchestrator import get_global_orchestrator

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def initialize_complete_system():
    """初始化完整系統"""
    
    print("\n" + "╔" + "═" * 68 + "╗")
    print("║" + " 🚀 全系統初始化 ".center(68) + "║")
    print("╚" + "═" * 68 + "╝" + "\n")
    
    # ========== 階段 1: 初始化量子糾纏系統 ==========
    print("📍 第一階段: 初始化量子糾纏系統...")
    print("─" * 70)
    
    entanglement_mgr = GlobalSyncManager()
    entanglement_sys = entanglement_mgr.get_system()
    
    # 註冊主要子系統
    subsystems = [
        ("quantum_engine", "量子計算引擎", SubsystemType.QUANTUM_ENGINE),
        ("trading_system", "交易系統", SubsystemType.TRADING_SYSTEM),
        ("data_manager", "數據管理器", SubsystemType.DATA_MANAGER),
        ("memory_mgr", "內存管理器", SubsystemType.MEMORY_MANAGER),
        ("task_panel", "任務面板", SubsystemType.TASK_PANEL),
        ("ray_dist", "Ray分布式引擎", SubsystemType.RAY_DISTRIBUTED),
        ("mcp_service", "MCP服務", SubsystemType.MCP_SERVICE),
        ("cli_interface", "CLI界面", SubsystemType.CLI_INTERFACE),
    ]
    
    for subsys_id, name, subsys_type in subsystems:
        entanglement_mgr.register_subsystem(subsys_id, name, subsys_type)
    
    # 建立糾纏連接
    print("\n建立糾纏連接...")
    connections = [
        ("quantum_engine", "trading_system"),
        ("trading_system", "data_manager"),
        ("data_manager", "memory_mgr"),
        ("memory_mgr", "task_panel"),
        ("task_panel", "cli_interface"),
        ("ray_dist", "quantum_engine"),
        ("mcp_service", "data_manager"),
    ]
    
    for subsys1, subsys2 in connections:
        entanglement_sys.establish_entanglement(subsys1, subsys2)
    
    # 創建主宇宙
    print("\n創建主宇宙...")
    main_universe = entanglement_sys.create_universe(
        "universe_0",
        subsystems=[s[0] for s in subsystems]
    )
    
    # 同步宇宙狀態
    entanglement_sys.sync_universe_state("universe_0")
    
    print("✅ 量子糾纏系統初始化完成\n")
    
    # ========== 階段 2: 初始化深度連接網絡 ==========
    print("📍 第二階段: 初始化深度連接網絡...")
    print("─" * 70)
    
    network_mgr = NetworkTopologyManager()
    network = network_mgr.get_network()
    
    # 添加網絡節點
    node_configs = [
        ("node_quantum", "量子引擎節點", "quantum"),
        ("node_trading", "交易節點", "trading"),
        ("node_data", "數據節點", "data"),
        ("node_memory", "內存節點", "memory"),
        ("node_task", "任務節點", "task"),
        ("node_ray", "Ray分布式節點", "distributed"),
        ("node_mcp", "MCP服務節點", "service"),
        ("node_cli", "CLI節點", "interface"),
    ]
    
    for node_id, name, node_type in node_configs:
        node = NetworkNode(
            node_id=node_id,
            node_type=node_type,
            name=name,
            region="local"
        )
        network.add_node(node)
    
    # 連接網絡節點
    print("\n建立網絡連接...")
    network_connections = [
        ("node_quantum", "node_trading", 1.0, 5.0),
        ("node_trading", "node_data", 1.0, 10.0),
        ("node_data", "node_memory", 0.8, 2.0),
        ("node_memory", "node_task", 1.0, 1.0),
        ("node_task", "node_cli", 1.0, 1.0),
        ("node_ray", "node_quantum", 0.9, 3.0),
        ("node_mcp", "node_data", 1.0, 8.0),
    ]
    
    for source, target, weight, latency in network_connections:
        network.connect_nodes(source, target, weight, latency)
    
    # 生成路由表
    routing_table = network.generate_routing_table()
    
    print("✅ 深度連接網絡初始化完成\n")
    
    # ========== 階段 3: 初始化多元宇宙系統 ==========
    print("📍 第三階段: 初始化多元宇宙集成系統...")
    print("─" * 70)
    
    multiverse_mgr = MultiverseManager()
    multiverse = multiverse_mgr.get_system()
    
    # 創建多個維度的宇宙
    print("\n創建平行宇宙...")
    universes_config = [
        ("universe_1d_0", 1),
        ("universe_1d_1", 1),
        ("universe_2d_0", 2),
        ("universe_3d_0", 3),
    ]
    
    for universe_id, dimension in universes_config:
        parent = ["universe_0"] if dimension > 1 else []
        multiverse.create_universe(universe_id, dimension, parent)
    
    # 建立宇宙糾纏
    print("\n建立宇宙糾纏...")
    entanglements = [
        ("universe_1d_0", "universe_1d_1", 0.9),
        ("universe_1d_0", "universe_2d_0", 0.7),
        ("universe_2d_0", "universe_3d_0", 0.8),
    ]
    
    for u1, u2, strength in entanglements:
        multiverse.establish_entanglement(u1, u2, strength)
    
    # 記錄平行狀態
    print("\n記錄初始狀態...")
    for universe_id in [u[0] for u in universes_config]:
        state_data = {
            "initialization": True,
            "timestamp": __import__("datetime").datetime.now().isoformat(),
            "subsystem_count": len(subsystems)
        }
        multiverse.record_parallel_state(universe_id, state_data, "initialization")
    
    print("✅ 多元宇宙集成系統初始化完成\n")
    
    # ========== 階段 4: 激活全局同步協調器 ==========
    print("📍 第四階段: 激活全局同步協調器...")
    print("─" * 70)
    
    orchestrator = get_global_orchestrator()
    
    # 執行首次同步
    print("\n執行首次全系統同步...")
    sync_result = orchestrator.sync_all_systems()
    
    # 啟動後台同步
    print("\n啟動後台同步 (300秒間隔)...")
    orchestrator.start_background_sync(interval_seconds=300)
    
    print("✅ 全局同步協調器已激活\n")
    
    # ========== 最終報告 ==========
    print("=" * 70)
    print("✅ 全系統初始化完成！")
    print("=" * 70)
    print("\n")
    
    # 生成並顯示完整報告
    print(orchestrator.generate_integrated_report())
    
    # 保存初始化報告
    import json
    report = {
        "initialization_time": __import__("datetime").datetime.now().isoformat(),
        "systems": {
            "entanglement": {
                "subsystems": len(entanglement_sys.subsystems),
                "universes": len(entanglement_sys.universes),
                "connections": sum(len(v) for v in entanglement_sys.entanglement_graph.values()) // 2
            },
            "network": {
                "nodes": len(network.nodes),
                "edges": len(network.graph_edges)
            },
            "multiverse": {
                "universes": len(multiverse.universes),
                "parallel_states": len(multiverse.parallel_states)
            }
        }
    }
    
    report_file = Path(__file__).parent / "global_sync_logs" / "initialization_report.json"
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"📝 初始化報告已保存: {report_file}\n")


if __name__ == "__main__":
    try:
        initialize_complete_system()
    except Exception as e:
        logger.error(f"❌ 初始化失敗: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
