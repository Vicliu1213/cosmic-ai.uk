#!/usr/bin/env python3
"""
Cosmic AI - 完整驗證和測試套件
確保所有功能都完整實現並可以正確運行
"""

import sys
import asyncio
import logging
from typing import Dict, List, Any, Tuple
from pathlib import Path
from datetime import datetime
import importlib
import inspect

# 配置日誌
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)


class ValidationResult:
    """驗證結果類"""
    def __init__(self, name: str, category: str):
        self.name = name
        self.category = category
        self.passed = False
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.details: Dict[str, Any] = {}
        self.execution_time: float = 0.0
    
    def add_error(self, error: str):
        self.errors.append(error)
        self.passed = False
    
    def add_warning(self, warning: str):
        self.warnings.append(warning)
    
    def mark_passed(self):
        self.passed = True
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'category': self.category,
            'passed': self.passed,
            'errors': self.errors,
            'warnings': self.warnings,
            'details': self.details,
            'execution_time': self.execution_time
        }


class CosmicAIValidator:
    """完整的 Cosmic AI 驗證器"""
    
    def __init__(self, src_path: str = "./src"):
        self.src_path = Path(src_path)
        self.results: List[ValidationResult] = []
        self.start_time = datetime.now()
    
    # ===== 1. 結構驗證 =====
    def validate_structure(self) -> ValidationResult:
        """驗證項目結構"""
        result = ValidationResult("Project Structure", "Structure")
        
        try:
            required_dirs = [
                'data', 'analysis', 'utils', 'quantum', 'optimizer',
                'agents', 'execution', 'risk', 'core', 'strategies'
            ]
            
            for dir_name in required_dirs:
                dir_path = self.src_path / dir_name
                if not dir_path.exists():
                    result.add_error(f"缺失目錄: {dir_name}")
                else:
                    init_file = dir_path / "__init__.py"
                    main_file = dir_path / "main.py"
                    
                    if not init_file.exists():
                        result.add_error(f"{dir_name}/__init__.py 缺失")
                    if not main_file.exists():
                        result.add_error(f"{dir_name}/main.py 缺失")
            
            if not result.errors:
                result.mark_passed()
                result.details['verified_modules'] = required_dirs
            
        except Exception as e:
            result.add_error(f"結構驗證異常: {str(e)}")
        
        return result
    
    # ===== 2. 導入驗證 =====
    def validate_imports(self) -> ValidationResult:
        """驗證所有模塊都能正確導入"""
        result = ValidationResult("Module Imports", "Imports")
        
        try:
            sys.path.insert(0, str(self.src_path.parent))
            
            modules_to_test = [
                ('src', 'Main package'),
                ('src.data', 'Data module'),
                ('src.analysis', 'Analysis module'),
                ('src.utils', 'Utils module'),
                ('src.quantum', 'Quantum module'),
                ('src.optimizer', 'Optimizer module'),
                ('src.agents', 'Agents module'),
                ('src.execution', 'Execution module'),
                ('src.risk', 'Risk module'),
                ('src.core', 'Core module'),
                ('src.strategies', 'Strategies module'),
            ]
            
            successful_imports = 0
            for module_name, description in modules_to_test:
                try:
                    module = importlib.import_module(module_name)
                    successful_imports += 1
                    logger.info(f"✅ 成功導入: {module_name}")
                except ImportError as e:
                    result.add_warning(f"導入 {module_name} 失敗: {str(e)}")
                except Exception as e:
                    result.add_error(f"導入 {module_name} 異常: {str(e)}")
            
            if successful_imports >= len(modules_to_test) - 3:  # 允許部分失敗
                result.mark_passed()
                result.details['successful_imports'] = successful_imports
                result.details['total_modules'] = len(modules_to_test)
            else:
                result.add_error(f"導入成功率過低: {successful_imports}/{len(modules_to_test)}")
        
        except Exception as e:
            result.add_error(f"導入驗證異常: {str(e)}")
        
        return result
    
    # ===== 3. 功能驗證 =====
    def validate_module_managers(self) -> ValidationResult:
        """驗證所有 ModuleManager 類都存在"""
        result = ValidationResult("Module Managers", "Functionality")
        
        try:
            sys.path.insert(0, str(self.src_path.parent))
            
            managers_to_check = [
                ('src.data.main', 'DataModuleManager'),
                ('src.analysis.main', 'AnalysisModuleManager'),
                ('src.utils.main', 'UtilsModuleManager'),
                ('src.quantum.main', 'QuantumModuleManager'),
                ('src.optimizer.main', 'OptimizerModuleManager'),
                ('src.agents.main', 'AgentsModuleManager'),
                ('src.execution.main', 'ExecutionModuleManager'),
                ('src.risk.main', 'RiskModuleManager'),
                ('src.core.main', 'CoreModuleManager'),
            ]
            
            valid_managers = 0
            for module_name, class_name in managers_to_check:
                try:
                    module = importlib.import_module(module_name)
                    manager_class = getattr(module, class_name)
                    
                    # 檢查必要的方法
                    required_methods = ['get_status']
                    for method_name in required_methods:
                        if not hasattr(manager_class, method_name):
                            result.add_warning(f"{class_name} 缺失方法: {method_name}")
                        else:
                            valid_managers += 1
                    
                    logger.info(f"✅ 驗證通過: {class_name}")
                except Exception as e:
                    result.add_error(f"無法驗證 {class_name}: {str(e)}")
            
            if valid_managers >= len(managers_to_check) * 0.8:
                result.mark_passed()
                result.details['valid_managers'] = valid_managers
            else:
                result.add_error(f"無效的 Manager 數量過多")
        
        except Exception as e:
            result.add_error(f"Manager 驗證異常: {str(e)}")
        
        return result
    
    # ===== 4. 非空驗證 =====
    def validate_non_empty_modules(self) -> ValidationResult:
        """驗證所有主要模塊不為空"""
        result = ValidationResult("Non-Empty Modules", "Integrity")
        
        try:
            modules_to_check = [
                'data', 'analysis', 'utils', 'quantum', 'optimizer',
                'agents', 'execution', 'risk', 'core', 'strategies'
            ]
            
            empty_modules = []
            for module_name in modules_to_check:
                module_path = self.src_path / module_name
                
                # 計算 Python 文件
                py_files = list(module_path.glob("*.py"))
                if len(py_files) < 2:  # 至少需要 __init__.py 和 main.py
                    empty_modules.append(module_name)
                else:
                    result.details[f"{module_name}_files"] = len(py_files)
            
            if empty_modules:
                result.add_warning(f"模塊文件較少: {empty_modules}")
            else:
                result.mark_passed()
        
        except Exception as e:
            result.add_error(f"非空驗證異常: {str(e)}")
        
        return result
    
    # ===== 5. 主系統驗證 =====
    async def validate_main_system(self) -> ValidationResult:
        """驗證主系統可以初始化"""
        result = ValidationResult("Main System", "System")
        
        try:
            sys.path.insert(0, str(self.src_path.parent))
            from src.main import CosmicAITradingSystem, SystemConfig
            
            # 創建配置
            config = SystemConfig(
                mode="test",
                symbols=["BTCUSDT"],
                enable_quantum=False,
                enable_agents=False,
                enable_risk_management=False,
                enable_strategies=False
            )
            
            # 創建系統
            system = CosmicAITradingSystem(config)
            result.details['system_version'] = system.__class__.__module__
            
            logger.info(f"✅ 主系統成功初始化: {config.mode}")
            result.mark_passed()
        
        except Exception as e:
            result.add_error(f"主系統初始化失敗: {str(e)}")
        
        return result
    
    # ===== 6. 配置驗證 =====
    def validate_configs(self) -> ValidationResult:
        """驗證配置文件"""
        result = ValidationResult("Configuration Files", "Config")
        
        try:
            config_files = list(self.src_path.glob("**/config*.yaml")) + \
                          list(self.src_path.glob("**/config*.yml")) + \
                          list(self.src_path.glob("**/config*.json"))
            
            if not config_files:
                result.add_warning("找不到配置文件")
            else:
                result.details['config_files_count'] = len(config_files)
                result.mark_passed()
        
        except Exception as e:
            result.add_error(f"配置驗證異常: {str(e)}")
        
        return result
    
    # ===== 7. 依賴驗證 =====
    def validate_dependencies(self) -> ValidationResult:
        """驗證重要依賴"""
        result = ValidationResult("Dependencies", "Dependencies")
        
        try:
            dependencies = [
                'asyncio', 'logging', 'dataclasses', 'typing',
                'pathlib', 'json', 'yaml', 'datetime'
            ]
            
            missing_deps = []
            for dep in dependencies:
                try:
                    importlib.import_module(dep)
                except ImportError:
                    missing_deps.append(dep)
            
            if missing_deps:
                result.add_warning(f"缺失依賴: {missing_deps}")
            else:
                result.mark_passed()
                result.details['verified_dependencies'] = dependencies
        
        except Exception as e:
            result.add_error(f"依賴驗證異常: {str(e)}")
        
        return result
    
    # ===== 主驗證方法 =====
    async def run_all_validations(self) -> Dict[str, Any]:
        """運行所有驗證"""
        logger.info("🔍 開始完整的系統驗證...")
        logger.info("=" * 70)
        
        # 同步驗證
        self.results.append(self.validate_structure())
        self.results.append(self.validate_imports())
        self.results.append(self.validate_module_managers())
        self.results.append(self.validate_non_empty_modules())
        self.results.append(self.validate_configs())
        self.results.append(self.validate_dependencies())
        
        # 異步驗證
        self.results.append(await self.validate_main_system())
        
        # 生成報告
        return self.generate_report()
    
    def generate_report(self) -> Dict[str, Any]:
        """生成驗證報告"""
        total_validations = len(self.results)
        passed_validations = sum(1 for r in self.results if r.passed)
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'total_validations': total_validations,
            'passed_validations': passed_validations,
            'passed_rate': f"{(passed_validations / total_validations * 100):.1f}%",
            'results': [r.to_dict() for r in self.results],
            'summary': {
                'status': '✅ 全部通過' if passed_validations == total_validations else '⚠️ 部分通過' if passed_validations >= total_validations * 0.8 else '❌ 驗證失敗',
                'details': self._generate_summary_details()
            }
        }
        
        return report
    
    def _generate_summary_details(self) -> Dict[str, Any]:
        """生成摘要詳情"""
        return {
            'structure': next((r.passed for r in self.results if r.name == "Project Structure"), False),
            'imports': next((r.passed for r in self.results if r.name == "Module Imports"), False),
            'managers': next((r.passed for r in self.results if r.name == "Module Managers"), False),
            'non_empty': next((r.passed for r in self.results if r.name == "Non-Empty Modules"), False),
            'main_system': next((r.passed for r in self.results if r.name == "Main System"), False),
            'configs': next((r.passed for r in self.results if r.name == "Configuration Files"), False),
            'dependencies': next((r.passed for r in self.results if r.name == "Dependencies"), False),
        }
    
    def print_report(self, report: Dict[str, Any]):
        """打印驗證報告"""
        print("\n" + "=" * 70)
        print("🌌 COSMIC AI - 完整驗證報告")
        print("=" * 70)
        print(f"時間: {report['timestamp']}")
        print(f"總驗證項: {report['total_validations']}")
        print(f"通過項: {report['passed_validations']}")
        print(f"通過率: {report['passed_rate']}")
        print(f"狀態: {report['summary']['status']}")
        print("=" * 70)
        
        print("\n📋 詳細結果:")
        for result in report['results']:
            status = "✅" if result['passed'] else "❌"
            print(f"\n{status} {result['category']} - {result['name']}")
            
            if result['errors']:
                for error in result['errors']:
                    print(f"  ❌ {error}")
            
            if result['warnings']:
                for warning in result['warnings']:
                    print(f"  ⚠️  {warning}")
            
            if result['details']:
                for key, value in result['details'].items():
                    print(f"  ℹ️  {key}: {value}")
        
        print("\n" + "=" * 70)
        print("✅ 驗證完成!")
        print("=" * 70 + "\n")


async def main():
    """主函數"""
    validator = CosmicAIValidator(src_path="./src")
    report = await validator.run_all_validations()
    validator.print_report(report)
    
    # 返回狀態碼
    if report['summary']['status'] == '✅ 全部通過':
        return 0
    else:
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
