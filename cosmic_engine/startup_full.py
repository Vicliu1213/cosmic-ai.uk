#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
宇宙智能體核心引擎 v3.0 - 完整啟動程序
Cosmic Intelligence Cluster v3.0 - Full Startup
"""

import sys
import os
import yaml
import logging
import time
from datetime import datetime
from pathlib import Path

# 添加當前目錄到 Python 路徑
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 配置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('cosmic_engine.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

def load_config(config_path):
    """載入 YAML 配置"""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        logger.info(f"✅ 配置加載成功：{config_path}")
        return config
    except Exception as e:
        logger.error(f"❌ 配置加載失敗：{e}")
        return None

def init_knowledge_base(docs_path):
    """初始化知識庫"""
    try:
        from cosmic.knowledge_base import KnowledgeBase
        kb = KnowledgeBase(docs_path)
        logger.info(f"✅ 知識庫初始化成功，已載入 {len(kb.theories)} 個理論")
        return kb
    except Exception as e:
        logger.error(f"❌ 知識庫初始化失敗：{e}")
        return None

def init_ray_cluster(config):
    """初始化 Ray 集群"""
    try:
        import ray
        
        if ray.is_initialized():
            ray.shutdown()
        
        namespace = config.get('system', {}).get('namespace', 'cosmic')
        ray.init(
            namespace=namespace,
            ignore_reinit_error=True,
            logging_level='ERROR'
        )
        logger.info(f"✅ Ray 集群初始化成功（命名空間：{namespace}）")
        return ray
    except Exception as e:
        logger.error(f"❌ Ray 集群初始化失敗：{e}")
        return None

def create_agents(ray, config, kb):
    """創建智能體"""
    try:
        from cosmic.agent import Agent
        
        agents = []
        agent_count = config.get('agents', {}).get('initial_count', 3)
        
        for i in range(agent_count):
            agent = Agent.options(
                name=f"Agent_{i+1}",
                num_cpus=config['agents']['default_resources']['num_cpus'],
            ).remote(i+1, config.get('genome', {}), config['agents']['default_resources'], ray.put(kb))
            agents.append(agent)
        
        logger.info(f"✅ 已創建 {len(agents)} 個智能體")
        return agents
    except Exception as e:
        logger.error(f"❌ 智能體創建失敗：{e}")
        return []

def test_quantum_tasks(config):
    """測試量子任務"""
    try:
        from cosmic.quantum_tasks import run_grover, run_shor, run_annealing
        
        logger.info("\n🔬 量子任務測試")
        logger.info("─" * 50)
        
        # Grover 搜尋
        result = run_grover(search_space=100000)
        logger.info(f"✅ Grover 搜尋：{result}")
        
        # Shor 分解
        result = run_shor(number=15)
        logger.info(f"✅ Shor 分解：{result}")
        
        # 量子退火
        result = run_annealing(problem_size=50)
        logger.info(f"✅ 量子退火：{result}")
        
        return True
    except Exception as e:
        logger.error(f"❌ 量子任務測試失敗：{e}")
        return False

def test_trading_engine(config):
    """測試交易引擎"""
    try:
        import ray
        from cosmic.trading import TradingEngine
        
        logger.info("\n💰 交易引擎測試")
        logger.info("─" * 50)
        
        engine = TradingEngine.remote(config.get('trading', {}))
        result = ray.get(engine.place_order.remote("BTC/USD", 100, "BUY", 50000))
        logger.info(f"✅ 訂單執行：{result}")
        
        return True
    except Exception as e:
        logger.error(f"❌ 交易引擎測試失敗：{e}")
        return False

def generate_system_report(config, kb):
    """生成系統報告"""
    try:
        logger.info("\n📊 系統狀態報告")
        logger.info("=" * 70)
        
        # 系統信息
        system = config.get('system', {})
        logger.info(f"系統名稱：{system.get('name', 'N/A')}")
        logger.info(f"系統版本：{system.get('version', 'N/A')}")
        logger.info(f"命名空間：{system.get('namespace', 'N/A')}")
        
        # 理論基因組
        genome = config.get('genome', {})
        theories = genome.get('theories', [])
        logger.info(f"\n📚 理論基因組：{len(theories)} 個理論")
        for i, theory in enumerate(theories[:5], 1):
            logger.info(f"   {i}. {theory.get('name', 'N/A')}")
        if len(theories) > 5:
            logger.info(f"   ... 還有 {len(theories) - 5} 個理論")
        
        # 知識庫
        logger.info(f"\n🧠 知識庫：{len(kb.theories) if kb else 0} 個理論文檔")
        if kb and kb.theories:
            for i, theory_name in enumerate(list(kb.theories.keys())[:5], 1):
                logger.info(f"   {i}. {theory_name}")
        
        # 交易配置
        trading = config.get('trading', {})
        logger.info(f"\n💼 交易配置")
        logger.info(f"   初始資本：${trading.get('initial_capital', 0):,.0f}")
        logger.info(f"   最大頭寸：{trading.get('max_position_pct', 0):.1%}")
        logger.info(f"   止損：{trading.get('stop_loss_pct', 0):.2%}")
        logger.info(f"   獲利目標：{trading.get('take_profit_pct', 0):.2%}")
        
        # 監控
        monitoring = config.get('monitoring', {})
        logger.info(f"\n📈 監控配置")
        logger.info(f"   Prometheus：{'啟用' if monitoring.get('prometheus', {}).get('enabled') else '禁用'}")
        logger.info(f"   Ray 儀表板：{'啟用' if monitoring.get('ray_dashboard', {}).get('enabled') else '禁用'}")
        
        logger.info("\n" + "=" * 70)
        return True
    except Exception as e:
        logger.error(f"❌ 系統報告生成失敗：{e}")
        return False

def main():
    """主程序"""
    logger.info("\n" + "=" * 70)
    logger.info("🚀 宇宙智能體核心引擎 v3.0 - 完整啟動")
    logger.info("🚀 Cosmic Intelligence Cluster v3.0 - Full Startup")
    logger.info("=" * 70)
    
    start_time = time.time()
    
    # 1. 載入配置
    logger.info("\n📋 步驟 1：載入配置")
    config = load_config('config/cosmic_config.yaml')
    if not config:
        logger.error("❌ 程序終止：無法載入配置")
        return False
    
    # 2. 初始化知識庫
    logger.info("\n📚 步驟 2：初始化知識庫")
    kb = init_knowledge_base('docs/')
    if not kb:
        logger.warning("⚠️  知識庫初始化失敗，繼續運行")
    
    # 3. 初始化 Ray 集群
    logger.info("\n⚡ 步驟 3：初始化 Ray 集群")
    ray = init_ray_cluster(config)
    if not ray:
        logger.error("❌ 程序終止：無法初始化 Ray")
        return False
    
    # 4. 創建智能體
    logger.info("\n🤖 步驟 4：創建智能體")
    agents = create_agents(ray, config, kb)
    if not agents:
        logger.warning("⚠️  未能創建智能體")
    
    # 5. 測試量子任務
    logger.info("\n🔬 步驟 5：測試量子任務")
    test_quantum_tasks(config)
    
    # 6. 測試交易引擎
    logger.info("\n💰 步驟 6：測試交易引擎")
    test_trading_engine(config)
    
    # 7. 生成系統報告
    logger.info("\n📊 步驟 7：生成系統報告")
    generate_system_report(config, kb)
    
    # 執行時間統計
    elapsed_time = time.time() - start_time
    logger.info(f"\n⏱️  總執行時間：{elapsed_time:.2f} 秒")
    
    # 最終狀態
    logger.info("\n" + "=" * 70)
    logger.info("✨ 宇宙智能體核心引擎啟動完成！")
    logger.info("✨ Cosmic Intelligence Cluster Ready!")
    logger.info("=" * 70)
    
    # Ray 信息
    logger.info(f"\n📡 Ray 集群信息")
    logger.info(f"   状態：{'運行中' if ray.is_initialized() else '未初始化'}")
    if ray.is_initialized():
        import ray as ray_module
        resources = ray_module.available_resources()
        logger.info(f"   CPU：{resources.get('CPU', 0):.1f}")
        logger.info(f"   GPU：{resources.get('GPU', 0):.1f}")
    
    logger.info("\n💡 下一步提示：")
    logger.info("   1. 查看日誌文件：tail -f cosmic_engine.log")
    logger.info("   2. 啟動 Ray 儀表板：ray dashboard")
    logger.info("   3. 運行主程序：python main.py")
    
    return True

if __name__ == '__main__':
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("\n⏹️  程序被用戶中止")
        sys.exit(0)
    except Exception as e:
        logger.exception(f"❌ 未預期的錯誤：{e}")
        sys.exit(1)
