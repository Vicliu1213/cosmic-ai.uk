#!/usr/bin/env python3
"""
Cosmic AI - 綜合測試套件
測試所有主要功能模塊
"""

import sys
import asyncio
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

# 添加 src 到路徑
sys.path.insert(0, str(Path(__file__).parent / "src"))


class IntegrationTester:
    """集成測試類"""
    
    def __init__(self):
        self.test_results: Dict[str, Dict[str, Any]] = {}
        self.start_time = datetime.now()
    
    async def test_data_module(self) -> bool:
        """測試數據模塊"""
        print("\n📊 測試數據模塊...")
        try:
            from src.data.main import DataModuleManager
            
            manager = DataModuleManager()
            status = manager.get_status()
            
            assert status is not None
            assert 'data_dir' in status
            assert 'modules' in status
            
            # 測試方法
            kline_result = manager.validate_klines("BTCUSDT", 100)
            assert kline_result['symbol'] == "BTCUSDT"
            
            process_result = manager.process_market_data("BTCUSDT")
            assert process_result['status'] == "success"
            
            print("  ✅ 數據模塊測試通過")
            self.test_results['data_module'] = {'passed': True}
            return True
        except Exception as e:
            print(f"  ❌ 數據模塊測試失敗: {str(e)}")
            self.test_results['data_module'] = {'passed': False, 'error': str(e)}
            return False
    
    async def test_analysis_module(self) -> bool:
        """測試分析模塊"""
        print("\n📈 測試分析模塊...")
        try:
            from src.analysis.main import AnalysisModuleManager
            
            manager = AnalysisModuleManager()
            status = manager.get_status()
            
            assert status is not None
            assert 'modules' in status
            
            # 測試方法
            indicators = manager.calculate_indicators({'test': True}, "BTCUSDT")
            assert indicators['symbol'] == "BTCUSDT"
            assert 'indicators' in indicators
            
            signals = manager.generate_signals("BTCUSDT", indicators)
            assert signals['symbol'] == "BTCUSDT"
            assert 'signal' in signals
            
            print("  ✅ 分析模塊測試通過")
            self.test_results['analysis_module'] = {'passed': True}
            return True
        except Exception as e:
            print(f"  ❌ 分析模塊測試失敗: {str(e)}")
            self.test_results['analysis_module'] = {'passed': False, 'error': str(e)}
            return False
    
    async def test_utils_module(self) -> bool:
        """測試工具模塊"""
        print("\n🔧 測試工具模塊...")
        try:
            from src.utils.main import UtilsModuleManager
            
            manager = UtilsModuleManager()
            status = manager.get_status()
            
            assert status is not None
            assert 'components' in status
            
            # 測試方法
            save_result = manager.save_data({'test': 'data'}, 'test_category', 'BTCUSDT')
            assert save_result['status'] == "success"
            assert save_result['category'] == 'test_category'
            
            cache_result = manager.load_kline_cache('BTCUSDT')
            assert cache_result['symbol'] == 'BTCUSDT'
            
            print("  ✅ 工具模塊測試通過")
            self.test_results['utils_module'] = {'passed': True}
            return True
        except Exception as e:
            print(f"  ❌ 工具模塊測試失敗: {str(e)}")
            self.test_results['utils_module'] = {'passed': False, 'error': str(e)}
            return False
    
    async def test_quantum_module(self) -> bool:
        """測試量子模塊"""
        print("\n⚛️  測試量子模塊...")
        try:
            from src.quantum.main import QuantumModuleManager
            
            manager = QuantumModuleManager()
            status = manager.get_status()
            
            assert status is not None
            assert 'quantum_available' in status
            
            # 測試方法
            analysis = manager.run_quantum_analysis({'test': 'data'})
            assert analysis['status'] == "success"
            assert 'coherence' in analysis
            
            optimization = manager.hybrid_quantum_optimization({'test': 'problem'})
            assert optimization['status'] == "success"
            
            print("  ✅ 量子模塊測試通過")
            self.test_results['quantum_module'] = {'passed': True}
            return True
        except Exception as e:
            print(f"  ❌ 量子模塊測試失敗: {str(e)}")
            self.test_results['quantum_module'] = {'passed': False, 'error': str(e)}
            return False
    
    async def test_optimizer_module(self) -> bool:
        """測試優化模塊"""
        print("\n⚡ 測試優化模塊...")
        try:
            from src.optimizer.main import OptimizerModuleManager
            
            manager = OptimizerModuleManager()
            status = manager.get_status()
            
            assert status is not None
            assert 'optimizer_available' in status
            
            print("  ✅ 優化模塊測試通過")
            self.test_results['optimizer_module'] = {'passed': True}
            return True
        except Exception as e:
            print(f"  ⚠️  優化模塊測試: {str(e)}")
            self.test_results['optimizer_module'] = {'passed': False, 'error': str(e)}
            return False
    
    async def test_agents_module(self) -> bool:
        """測試代理模塊"""
        print("\n🤖 測試代理模塊...")
        try:
            from src.agents.main import AgentsModuleManager
            
            manager = AgentsModuleManager()
            status = manager.get_status()
            
            assert status is not None
            assert 'total_agents' in status or 'agents_available' in status
            
            print("  ✅ 代理模塊測試通過")
            self.test_results['agents_module'] = {'passed': True}
            return True
        except Exception as e:
            print(f"  ⚠️  代理模塊測試: {str(e)}")
            self.test_results['agents_module'] = {'passed': False, 'error': str(e)}
            return False
    
    async def test_execution_module(self) -> bool:
        """測試執行模塊"""
        print("\n🚀 測試執行模塊...")
        try:
            from src.execution.main import ExecutionModuleManager
            
            manager = ExecutionModuleManager()
            status = manager.get_status()
            
            assert status is not None
            assert 'execution_ready' in status or 'engine_initialized' in status
            
            print("  ✅ 執行模塊測試通過")
            self.test_results['execution_module'] = {'passed': True}
            return True
        except Exception as e:
            print(f"  ⚠️  執行模塊測試: {str(e)}")
            self.test_results['execution_module'] = {'passed': False, 'error': str(e)}
            return False
    
    async def test_risk_module(self) -> bool:
        """測試風險模塊"""
        print("\n⚠️  測試風險模塊...")
        try:
            from src.risk.main import RiskModuleManager
            
            manager = RiskModuleManager()
            status = manager.get_status()
            
            assert status is not None
            assert 'risk_manager_available' in status or 'status' in status
            
            print("  ✅ 風險模塊測試通過")
            self.test_results['risk_module'] = {'passed': True}
            return True
        except Exception as e:
            print(f"  ⚠️  風險模塊測試: {str(e)}")
            self.test_results['risk_module'] = {'passed': False, 'error': str(e)}
            return False
    
    async def test_core_module(self) -> bool:
        """測試核心模塊"""
        print("\n⚙️  測試核心模塊...")
        try:
            from src.core.main import CoreModuleManager
            
            manager = CoreModuleManager()
            assert manager is not None
            assert manager.initialized == False  # 未初始化前為 False
            
            # 嘗試初始化
            await manager.initialize()
            assert manager.initialized == True
            
            status = manager.get_status()
            assert status is not None
            
            print("  ✅ 核心模塊測試通過")
            self.test_results['core_module'] = {'passed': True}
            return True
        except Exception as e:
            print(f"  ⚠️  核心模塊測試: {str(e)}")
            self.test_results['core_module'] = {'passed': False, 'error': str(e)}
            return False
    
    async def test_strategies_module(self) -> bool:
        """測試策略模塊"""
        print("\n📊 測試策略模塊...")
        try:
            from src.strategies import main as strategies_main
            
            assert strategies_main is not None
            
            print("  ✅ 策略模塊測試通過")
            self.test_results['strategies_module'] = {'passed': True}
            return True
        except Exception as e:
            print(f"  ⚠️  策略模塊測試: {str(e)}")
            self.test_results['strategies_module'] = {'passed': False, 'error': str(e)}
            return False
    
    async def test_main_system(self) -> bool:
        """測試主系統"""
        print("\n🌌 測試主系統...")
        try:
            from src.main import CosmicAITradingSystem, SystemConfig
            
            # 創建配置
            config = SystemConfig(
                mode="test",
                symbols=["BTCUSDT", "ETHUSDT"],
                enable_quantum=True,
                enable_agents=True,
                enable_risk_management=True,
                enable_strategies=True
            )
            
            # 創建系統
            system = CosmicAITradingSystem(config)
            assert system is not None
            assert system.config.mode == "test"
            
            # 獲取狀態
            status = system.get_status()
            assert status is not None
            assert 'system' in status
            assert 'modules' in status
            
            print("  ✅ 主系統測試通過")
            self.test_results['main_system'] = {'passed': True}
            return True
        except Exception as e:
            print(f"  ❌ 主系統測試失敗: {str(e)}")
            self.test_results['main_system'] = {'passed': False, 'error': str(e)}
            return False
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """運行所有測試"""
        print("\n" + "=" * 70)
        print("🧪 COSMIC AI - 綜合測試套件")
        print("=" * 70)
        
        results = []
        results.append(await self.test_data_module())
        results.append(await self.test_analysis_module())
        results.append(await self.test_utils_module())
        results.append(await self.test_quantum_module())
        results.append(await self.test_optimizer_module())
        results.append(await self.test_agents_module())
        results.append(await self.test_execution_module())
        results.append(await self.test_risk_module())
        results.append(await self.test_core_module())
        results.append(await self.test_strategies_module())
        results.append(await self.test_main_system())
        
        # 生成報告
        passed = sum(results)
        total = len(results)
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'total_tests': total,
            'passed_tests': passed,
            'passed_rate': f"{(passed / total * 100):.1f}%",
            'status': '✅ 全部通過' if passed == total else f"⚠️  部分通過 ({passed}/{total})",
            'details': self.test_results
        }
        
        self._print_summary(report)
        return report
    
    def _print_summary(self, report: Dict[str, Any]):
        """打印測試摘要"""
        print("\n" + "=" * 70)
        print("📋 測試結果摘要")
        print("=" * 70)
        print(f"時間: {report['timestamp']}")
        print(f"總測試數: {report['total_tests']}")
        print(f"通過數: {report['passed_tests']}")
        print(f"通過率: {report['passed_rate']}")
        print(f"狀態: {report['status']}")
        print("=" * 70 + "\n")


async def main():
    """主函數"""
    tester = IntegrationTester()
    report = await tester.run_all_tests()
    
    # 返回狀態碼
    if report['passed_tests'] == report['total_tests']:
        return 0
    else:
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
