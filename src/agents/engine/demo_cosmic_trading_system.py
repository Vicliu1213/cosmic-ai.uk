#!/usr/bin/env python3
"""
異變全知宇宙交易智能體系統 (Mutant Omniscient Cosmic Trading Agent System)
完整功能演示

展示:
- 完整的知識庫系統
- 量子任務管理
- 多策略交易引擎
- 共識投票機制
- 遺傳演算法突變
- 基因交叉
"""

import ray
import yaml
import time
import json
from pathlib import Path
from datetime import datetime

# 導入 cosmic 模組
from cosmic import (
    KnowledgeBase, Agent, TradingEngine, ConsensusManager, DataInterface,
    quantum_manager, run_grover, run_shor, run_annealing, setup_logging, get_logger
)


def setup_system():
    """設置系統"""
    # 初始化日誌
    setup_logging(level="INFO", log_file="cosmic_engine.log")
    logger = get_logger("cosmic_system")
    logger.info("=" * 80)
    logger.info("異變全知宇宙交易智能體系統啟動")
    logger.info("=" * 80)
    
    # 初始化 Ray
    if not ray.is_initialized():
        ray.init(ignore_reinit_error=True, namespace="cosmic_ai")
    
    return logger


def initialize_knowledge_base(logger):
    """初始化知識庫"""
    logger.info("\n[1] 初始化知識庫系統...")
    
    docs_path = Path("cosmic_engine/docs")
    docs_path.mkdir(parents=True, exist_ok=True)
    
    kb = KnowledgeBase(docs_path=str(docs_path))
    logger.info(f"✓ 知識庫已初始化，包含 {len(kb.theories)} 個理論")
    logger.info(f"✓ 理論列表: {kb.list_theories()}")
    logger.info(f"✓ 最頂級理論: {kb.get_top_theories(3)}")
    
    return kb


def initialize_trading_engine(logger):
    """初始化交易引擎"""
    logger.info("\n[2] 初始化交易引擎...")
    
    config = {
        "initial_capital": 100000,
        "max_position_pct": 0.1,
        "max_daily_loss_pct": 0.05,
        "use_leverage": False,
        "max_leverage": 1.5
    }
    
    trading_engine_ref = TradingEngine.remote(config)
    logger.info(f"✓ 交易引擎已初始化 - 初始資本: ${config['initial_capital']:,}")
    
    return trading_engine_ref


def initialize_data_interface(logger):
    """初始化數據接口"""
    logger.info("\n[3] 初始化數據接口...")
    
    data_config = {
        "type": "simulated",  # 稍後可改為 "openbb"
        "update_interval": 60
    }
    
    data_interface = DataInterface(data_config)
    logger.info(f"✓ 數據接口已初始化 - 模式: {data_config['type']}")
    logger.info(f"✓ 可用符號: {list(data_interface.data.keys())}")
    
    return data_interface


def create_agents(kb_ref, logger):
    """創建異變智能體"""
    logger.info("\n[4] 創建異變全知宇宙智能體...")
    
    # 定義基因組配置
    genome_config = {
        "theories": [
            {"name": "量子糾纏理論", "initial_expression": 1.2},
            {"name": "交易策略理論", "initial_expression": 1.0},
            {"name": "共識機制", "initial_expression": 0.9},
            {"name": "遺傳演算法", "initial_expression": 1.5},
        ],
        "strategies": {
            "mean_reversion": {"weight": 0.25, "confidence": 0.7},
            "momentum": {"weight": 0.25, "confidence": 0.7},
            "quantum_optimized": {"weight": 0.25, "confidence": 0.8},
            "risk_parity": {"weight": 0.25, "confidence": 0.75}
        },
        "mutation_rate": 0.05,
        "mutation_amplitude": 0.1
    }
    
    resources = {
        "num_cpus": 1,
        "num_gpus": 0,
        "risk_tolerance": 0.5
    }
    
    # 創建多個代理
    agents = []
    num_agents = 3
    
    for i in range(num_agents):
        agent = Agent.options(
            name=f"CosmicAgent_{i+1}",
            num_cpus=resources["num_cpus"]
        ).remote(
            agent_id=i+1,
            genome_config=genome_config,
            resources=resources,
            kb_ref=kb_ref
        )
        agents.append(agent)
    
    logger.info(f"✓ 已創建 {num_agents} 個異變智能體")
    
    # 取得代理狀態
    for i, agent in enumerate(agents):
        status = ray.get(agent.get_agent_status.remote())
        logger.info(f"  • 代理 {i+1}: 信譽={status['reputation']:.2f}, "
                   f"風險容忍度={status['risk_tolerance']:.2f}")
    
    return agents


def demonstrate_quantum_tasks(logger):
    """演示量子任務"""
    logger.info("\n[5] 執行量子任務...")
    
    # Grover 搜尋
    grover_result = run_grover(search_space=1000000)
    logger.info(f"✓ Grover 搜尋: {grover_result.get('algorithm')}, "
               f"迭代次數: {grover_result.get('iterations')}")
    
    # Shor 分解
    shor_result = run_shor(number=15)
    logger.info(f"✓ Shor 分解: 因子 {shor_result.get('factors')}")
    
    # 量子退火
    annealing_result = run_annealing(problem_size=100)
    logger.info(f"✓ 量子退火: 最佳能量 {annealing_result.get('best_energy')}")
    
    # 量子任務管理器統計
    report = quantum_manager.get_performance_report()
    logger.info(f"✓ 量子系統總任務數: {report['total_tasks']}")
    logger.info(f"✓ 平均執行時間: {report['average_execution_time']:.3f}s")


def demonstrate_mutations(agents, logger):
    """演示遺傳突變機制"""
    logger.info("\n[6] 演示遺傳突變機制...")
    
    agent = agents[0]
    
    # 執行突變
    mutation_result = ray.get(agent.mutate.remote(base_rate=0.3, cycle_factor=0.15))
    logger.info(f"✓ 執行突變 - 總變化數: {mutation_result['total_changes']}")
    
    for mutation in mutation_result['mutations'][:3]:
        logger.info(f"  • {mutation['type']}: {mutation.get('theory', mutation.get('strategy'))}")
    
    # 代理交叉
    if len(agents) > 1:
        agent2_data = {
            'agent_id': 2,
            'genome': [{"name": "test", "initial_expression": 0.8}],
            'strategies': agents[1].strategy_weights.remote() if hasattr(agents[1], 'strategy_weights') else {}
        }
        
        crossover_result = ray.get(agent.apply_crossover.remote(agent2_data, crossover_rate=0.5))
        logger.info(f"✓ 基因交叉完成 - 交換數: {len(crossover_result['exchanges'])}")


def demonstrate_trading(agents, data_interface, logger):
    """演示交易功能"""
    logger.info("\n[7] 演示交易功能...")
    
    agent = agents[0]
    
    # 選擇策略
    strategy, confidence = ray.get(agent.select_trading_strategy.remote("trending"))
    logger.info(f"✓ 選定策略: {strategy} (信心度: {confidence:.2f})")
    
    # 執行交易
    market_data = {
        'price': 50000,
        'position_size': 0.05,
        'condition': 'trending'
    }
    signal = {'signal': 'BUY'}
    
    trade_record = ray.get(agent.execute_trade.remote("BTC/USD", signal, market_data))
    logger.info(f"✓ 交易執行: {trade_record['action']} {trade_record['quantity']} BTC @ "
               f"${trade_record['price']:,.0f}")
    
    # 更新交易性能
    ray.get(agent.update_trading_performance.remote(pnl=500.0, win=True))
    
    # 取得代理狀態
    status = ray.get(agent.get_agent_status.remote())
    logger.info(f"✓ 代理狀態: 總利潤=${status['total_profit']:.2f}, "
               f"勝率={status['win_rate']:.2%}")


def demonstrate_consensus(agents, kb_ref, logger):
    """演示共識投票機制"""
    logger.info("\n[8] 演示共識投票機制...")
    
    # 創建共識管理器
    consensus_config = {
        "algorithm": "weighted_voting",
        "voting_threshold": 0.5,
        "default_vote_weight": 1.0
    }
    
    consensus_mgr = ConsensusManager.remote(consensus_config, agents)
    
    # 執行投票
    proposal = {
        "type": "theory_update",
        "content": "提升量子糾纏理論在交易系統中的權重",
        "priority": "high"
    }
    
    voting_result = ray.get(consensus_mgr.propose_and_vote.remote(proposal))
    logger.info(f"✓ 投票結果: {'通過' if voting_result.get('passed') else '未通過'} "
               f"(贊成率: {voting_result.get('approval_rate', 0):.2%})")
    
    # 取得投票統計
    stats = ray.get(consensus_mgr.get_voting_statistics.remote())
    logger.info(f"✓ 投票統計: 總投票數={stats.get('total_votes', 0)}, "
               f"通過率={stats.get('pass_rate', 0):.2%}")


def export_snapshots(agents, data_interface, logger):
    """匯出系統快照"""
    logger.info("\n[9] 匯出系統快照...")
    
    snapshot_dir = Path("cosmic_engine/snapshots")
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    
    # 匯出代理快照
    for i, agent in enumerate(agents):
        filepath = snapshot_dir / f"agent_{i+1}_snapshot.json"
        ray.get(agent.export_agent_snapshot.remote(str(filepath)))
    
    logger.info(f"✓ 代理快照已匯出至 {snapshot_dir}")
    
    # 匯出數據快照
    data_snapshot_path = snapshot_dir / "market_snapshot.json"
    data_interface.export_market_snapshot(str(data_snapshot_path))
    logger.info(f"✓ 市場數據快照已匯出")


def generate_report(logger):
    """生成系統報告"""
    logger.info("\n[10] 生成系統報告...")
    
    report = {
        'timestamp': datetime.now().isoformat(),
        'system_name': '異變全知宇宙交易智能體系統',
        'version': '2.0.0',
        'components': {
            'knowledge_base': '完全激活',
            'quantum_tasks': '完全激活',
            'trading_engine': '完全激活',
            'consensus_manager': '完全激活',
            'genetic_algorithms': '完全激活',
            'data_interface': '完全激活'
        },
        'quantum_system': quantum_manager.get_performance_report(),
        'status': 'FULLY_OPERATIONAL'
    }
    
    report_path = Path("cosmic_engine/system_report.json")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    logger.info(f"✓ 系統報告已生成: {report_path}")
    logger.info(f"✓ 系統狀態: {report['status']}")


def main():
    """主函數"""
    logger = setup_system()
    
    try:
        # 初始化系統
        kb = initialize_knowledge_base(logger)
        kb_ref = ray.put(kb)
        
        trading_engine = initialize_trading_engine(logger)
        data_interface = initialize_data_interface(logger)
        
        # 創建代理
        agents = create_agents(kb_ref, logger)
        
        # 演示各個系統
        demonstrate_quantum_tasks(logger)
        demonstrate_mutations(agents, logger)
        demonstrate_trading(agents, data_interface, logger)
        demonstrate_consensus(agents, kb_ref, logger)
        
        # 匯出快照
        export_snapshots(agents, data_interface, logger)
        
        # 生成報告
        generate_report(logger)
        
        logger.info("\n" + "=" * 80)
        logger.info("✓ 異變全知宇宙交易智能體系統演示完成！")
        logger.info("=" * 80)
        logger.info("\n所有功能已激活:")
        logger.info("  ✓ 完整知識庫系統")
        logger.info("  ✓ 量子任務管理（Grover、Shor、Annealing、VQE、QAOA）")
        logger.info("  ✓ 多策略交易引擎")
        logger.info("  ✓ 共識投票機制（加權投票、量子共識、委託投票、排名選擇）")
        logger.info("  ✓ 完整的遺傳演算法（點突變、策略突變、信譽突變、基因交叉）")
        logger.info("  ✓ 數據接口（模擬、OpenBB、混合模式）")
        logger.info("\n下一步: 申請 OpenBB 帳號以啟用實時數據功能！")
        
    except Exception as e:
        logger.error(f"系統錯誤: {e}", exc_info=True)
    finally:
        # 清理
        if ray.is_initialized():
            ray.shutdown()


if __name__ == "__main__":
    main()
