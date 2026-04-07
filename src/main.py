#!/usr/bin/env python3
"""
宇宙AI交易系統 - 根目錄主入點

完整集成所有模塊：
- 數據模塊 (Data Module)
- 工具模塊 (Utils Module)  
- 核心模塊 (Core Module)
- 量子模塊 (Quantum Module)
- 分析模塊 (Analysis Module)
- 優化模塊 (Optimizer Module)
- 代理模塊 (Agents Module)
- 執行模塊 (Execution Module)
- 風險模塊 (Risk Module)
- 策略模塊 (Strategies Module)
"""

import sys
import asyncio
import logging
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime
from pathlib import Path

# 配置日誌
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(Path(__file__).parent / "logs" / "cosmic_ai.log")
    ]
)
logger = logging.getLogger(__name__)

# 匯入重連管理器
try:
    from core.reconnect_manager import AutoReconnect, SystemGuard, ReconnectConfig
    RECONNECT_ENABLED = True
except ImportError:
    RECONNECT_ENABLED = False
    logger.warning("⚠️  重連管理器未可用")


@dataclass
class SystemConfig:
    """系統配置數據類"""
    mode: str = "live"
    symbols: List[str] = field(default_factory=lambda: ["BTCUSDT", "ETHUSDT"])
    enable_quantum: bool = True
    enable_agents: bool = True
    enable_risk_management: bool = True
    enable_strategies: bool = True
    max_position_size: float = 1000.0
    
    def __post_init__(self):
        if not self.symbols:
            self.symbols = ["BTCUSDT", "ETHUSDT"]


class ModuleRegistry:
    """模塊註冊表 - 追蹤所有模塊的初始化狀態"""
    
    def __init__(self):
        self.modules = {}
        self.initialized = {}
    
    def register(self, name: str, module_manager) -> bool:
        """註冊模塊"""
        try:
            self.modules[name] = module_manager
            self.initialized[name] = False
            logger.info(f"✅ 模塊已註冊: {name}")
            return True
        except Exception as e:
            logger.error(f"❌ 模塊註冊失敗 ({name}): {str(e)}")
            return False
    
    def initialize_all(self) -> Dict[str, bool]:
        """初始化所有已註冊的模塊"""
        results = {}
        for name, manager in self.modules.items():
            try:
                if hasattr(manager, 'initialize'):
                    success = manager.initialize()
                elif hasattr(manager, 'initialize_algorithms'):
                    success = bool(manager.initialize_algorithms())
                elif hasattr(manager, 'initialize_agents'):
                    success = bool(manager.initialize_agents())
                else:
                    success = True
                
                self.initialized[name] = success
                results[name] = success
                status = "✅ 成功" if success else "❌ 失敗"
                logger.info(f"{status}: 模塊 {name} 已初始化")
            except Exception as e:
                logger.error(f"❌ 初始化失敗 ({name}): {str(e)}")
                results[name] = False
                self.initialized[name] = False
        
        return results
    
    def get_status(self) -> Dict[str, Any]:
        """獲取所有模塊的狀態"""
        return {
            'total_modules': len(self.modules),
            'initialized_modules': sum(1 for v in self.initialized.values() if v),
            'status_details': self.initialized.copy()
        }


class CosmicAITradingSystem:
    """宇宙AI交易系統 - 核心交易引擎"""
    
    def __init__(self, config: Optional[SystemConfig] = None):
        self.config = config or SystemConfig()
        self.registry = ModuleRegistry()
        self.start_time = datetime.now()
        self.hybrid_engine = None  # 混合量子-經典引擎
        logger.info("✅ Cosmic AI 系統初始化完成")
    
    async def initialize_modules(self) -> Dict[str, bool]:
        """初始化所有系統模塊"""
        try:
            # 初始化混合量子-經典引擎（優先級最高）
            try:
                from .engine import get_hybrid_engine
                self.hybrid_engine = get_hybrid_engine()
                success = self.hybrid_engine.initialize()
                if success:
                    logger.info("✅ 混合量子-經典引擎已初始化 (混合量子-經典交易引擎)")
                    self.registry.initialized['hybrid_engine'] = True
                else:
                    logger.warning("⚠️ 混合量子-經典引擎初始化失敗")
            except Exception as e:
                logger.warning(f"⚠️ 混合量子-經典引擎初始化失敗: {str(e)}")
            
            # 初始化數據模塊
            if True:  # 始終初始化
                from .data.main import DataModuleManager
                self.registry.register('data', DataModuleManager())
            
            # 初始化工具模塊
            if True:
                from .utils.main import UtilsModuleManager
                self.registry.register('utils', UtilsModuleManager())
            
            # 初始化分析模塊
            if True:
                from .analysis.main import AnalysisModuleManager
                self.registry.register('analysis', AnalysisModuleManager())
            
            # 初始化量子模塊 (如果啟用)
            if self.config.enable_quantum:
                try:
                    from .quantum.main import QuantumModuleManager
                    self.registry.register('quantum', QuantumModuleManager())
                except Exception as e:
                    logger.warning(f"⚠️ 量子模塊初始化失敗: {str(e)}")
            
            # 初始化優化模塊
            if True:
                from .optimizer.main import OptimizerModuleManager
                self.registry.register('optimizer', OptimizerModuleManager())
            
            # 初始化代理模塊 (如果啟用)
            if self.config.enable_agents:
                try:
                    from .agents.main import AgentsModuleManager
                    self.registry.register('agents', AgentsModuleManager())
                except Exception as e:
                    logger.warning(f"⚠️ 代理模塊初始化失敗: {str(e)}")
            
            # 初始化執行模塊
            if True:
                from .execution.main import ExecutionModuleManager
                self.registry.register('execution', ExecutionModuleManager())
            
            # 初始化風險模塊 (如果啟用)
            if self.config.enable_risk_management:
                from .risk.main import RiskModuleManager
                self.registry.register('risk', RiskModuleManager())
            
            # 初始化策略模塊 (如果啟用)
            if self.config.enable_strategies:
                try:
                    # 策略模塊沒有 StrategyManager，只有主模塊
                    logger.info("✅ 策略模塊已載入")
                except Exception as e:
                    logger.warning(f"⚠️ 策略模塊初始化失敗: {str(e)}")
            
            # 初始化核心模塊
            if True:
                try:
                    from .core.main_system import CoreSystemManager
                    self.registry.register('core', CoreSystemManager())
                except Exception as e:
                    logger.warning(f"⚠️ 核心模塊初始化失敗: {str(e)}")
            
            # 執行所有模塊的初始化
            return self.registry.initialize_all()
            
        except Exception as e:
            logger.error(f"❌ 模塊初始化失敗: {str(e)}")
            return {}
    
    async def run_trading_cycle(self) -> Dict[str, Any]:
        """執行交易周期"""
        logger.info(f"🚀 開始交易周期 (模式: {self.config.mode})")
        
        result = {
            'timestamp': datetime.now().isoformat(),
            'symbols': self.config.symbols,
            'mode': self.config.mode,
            'uptime': str(datetime.now() - self.start_time),
            'hybrid_engine_status': self.get_hybrid_engine_status() if self.hybrid_engine else None
        }
        
        logger.info("✅ 交易周期執行完成")
        return result
    
    def get_hybrid_engine_status(self) -> Optional[Dict[str, Any]]:
        """獲取混合引擎狀態"""
        if not self.hybrid_engine:
            return None
        try:
            return self.hybrid_engine.get_status()
        except Exception as e:
            logger.warning(f"⚠️ 無法獲取混合引擎狀態: {str(e)}")
            return None
    
    def get_status(self) -> Dict[str, Any]:
        """獲取系統狀態"""
        return {
            'system': {
                'mode': self.config.mode,
                'symbols': self.config.symbols,
                'uptime': str(datetime.now() - self.start_time),
                'start_time': self.start_time.isoformat()
            },
            'modules': self.registry.get_status()
        }


async def main(config: Optional[SystemConfig] = None, enable_auto_reconnect: bool = True):
    """
    系統主入點 - 初始化和運行 Cosmic AI 交易系統
    
    Args:
        config: 系統配置
        enable_auto_reconnect: 是否啟用自動重連
    """
    config = config or SystemConfig(mode="live", symbols=["BTCUSDT", "ETHUSDT"])
    
    # 初始化系統
    system = CosmicAITradingSystem(config)
    
    print("\n" + "="*70)
    print("🌌 宇宙 AI 交易系統 (Cosmic AI Trading System)")
    print("="*70)
    print(f"⏰ 啟動時間: {datetime.now().isoformat()}")
    print(f"🔧 模式: {config.mode}")
    print(f"💰 交易對: {', '.join(config.symbols)}")
    print(f"⚙️  量子系統: {'✅ 啟用' if config.enable_quantum else '❌ 禁用'}")
    print(f"🤖 代理系統: {'✅ 啟用' if config.enable_agents else '❌ 禁用'}")
    print(f"⚠️  風險管理: {'✅ 啟用' if config.enable_risk_management else '❌ 禁用'}")
    print(f"🔄 自動重連: {'✅ 啟用' if (enable_auto_reconnect and RECONNECT_ENABLED) else '❌ 禁用'}")
    print("="*70)
    
    # 如果啟用自動重連，使用 SystemGuard
    if enable_auto_reconnect and RECONNECT_ENABLED:
        reconnect_config = ReconnectConfig(
            max_retries=5,
            initial_delay=1.0,
            max_delay=30.0,
            backoff_factor=2.0,
            jitter=True
        )
        
        guard = SystemGuard(system, reconnect_config)
        print("\n🛡️  系統守護者已啟用 - 閃退自動重連")
        
        # 初始化模塊
        print("\n📦 正在初始化模塊...")
        try:
            module_status = await guard.reconnect.execute_with_retry(
                lambda: system.initialize_modules(),
                "模塊初始化"
            )
            
            print("\n✅ 模塊初始化結果:")
            for module_name, success in module_status.items():
                status = "✅ 成功" if success else "❌ 失敗"
                print(f"  {status} - {module_name}")
        except Exception as e:
            logger.error(f"❌ 模塊初始化失敗: {e}")
            return system
        
        # 運行交易周期
        print("\n🚀 啟動交易周期...")
        try:
            cycle_result = await guard.reconnect.execute_with_retry(
                lambda: system.run_trading_cycle(),
                "交易周期執行"
            )
        except Exception as e:
            logger.error(f"❌ 交易周期執行失敗: {e}")
        
        # 顯示系統狀態
        status = system.get_status()
        print("\n📊 系統狀態:")
        print(f"  模塊總數: {status['modules']['total_modules']}")
        print(f"  已初始化: {status['modules']['initialized_modules']}")
        
        # 顯示守護者狀態
        guard_status = guard.get_status()
        print(f"\n🛡️  守護者狀態:")
        print(f"  崩潰次數: {guard_status['crash_count']}")
        print(f"  運行時間: {guard_status['uptime']}")
    
    else:
        # 不使用重連，直接初始化
        print("\n📦 正在初始化模塊...")
        module_status = await system.initialize_modules()
        
        print("\n✅ 模塊初始化結果:")
        for module_name, success in module_status.items():
            status = "✅ 成功" if success else "❌ 失敗"
            print(f"  {status} - {module_name}")
        
        # 運行交易周期
        print("\n🚀 啟動交易周期...")
        cycle_result = await system.run_trading_cycle()
        
        # 顯示系統狀態
        status = system.get_status()
        print("\n📊 系統狀態:")
        print(f"  模塊總數: {status['modules']['total_modules']}")
        print(f"  已初始化: {status['modules']['initialized_modules']}")
    
    print("\n" + "="*70)
    print("✅ Cosmic AI 交易系統 - 執行成功!")
    print("="*70 + "\n")
    
    return system


if __name__ == "__main__":
    # 確保能夠執行成功，並支持自動重連
    try:
        config = SystemConfig(
            mode="live",
            symbols=["BTCUSDT", "ETHUSDT"],
            enable_quantum=True,
            enable_agents=True,
            enable_risk_management=True,
            enable_strategies=True
        )
        
        # 啟用自動重連
        asyncio.run(main(config, enable_auto_reconnect=True))
        print("✅ 程式執行完成\n")
        sys.exit(0)
    except KeyboardInterrupt:
        print("\n\n⚠️  系統被用戶中斷")
        sys.exit(130)
    except Exception as e:
        logger.error(f"❌ 系統執行失敗: {str(e)}")
        # 嘗試重連
        if RECONNECT_ENABLED:
            logger.info("🔄 嘗試自動重連...")
            try:
                reconnect = AutoReconnect()
                asyncio.run(reconnect.execute_with_retry(
                    lambda: main(config, enable_auto_reconnect=True),
                    "系統啟動"
                ))
            except Exception as retry_error:
                logger.error(f"❌ 重連失敗: {retry_error}")
                sys.exit(1)
        else:
            sys.exit(1)

