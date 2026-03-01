#!/usr/bin/env python3
"""
Auto Reply Systems Startup Manager
自動回覆系統啟動管理器
確保所有自動回覆系統都在上線時自動打開
"""

import sys
import logging
from pathlib import Path
from typing import Dict, List, Tuple
import importlib.util

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 自動回覆系統配置
AUTO_REPLY_SYSTEMS_CONFIG = {
    'three_layer_auto_reply': {
        'module_path': 'src/core/three_layer_auto_reply',
        'startup_func': 'start_three_layer_system',
        'description': '三層自動回覆系統',
        'priority': 1,
        'critical': True,
    },
    'autonomous_error_handler': {
        'module_path': 'autonomous_error_handler',
        'startup_func': 'start_error_handler',
        'description': '自主式錯誤處理',
        'priority': 2,
        'critical': True,
    },
    'eternal_autonomous_handler': {
        'module_path': 'eternal_autonomous_handler',
        'startup_func': 'initialize_eternal_system',
        'description': '永恆自主錯誤處理',
        'priority': 3,
        'critical': True,
    },
    'auto_evolution_daemon': {
        'module_path': 'auto_evolution_daemon',
        'startup_func': 'start_auto_evolution',
        'description': '自動進化系統',
        'priority': 4,
        'critical': False,
    },
    'context_recovery': {
        'module_path': 'src/core/context_recovery_pipeline',
        'startup_func': 'initialize_recovery',
        'description': '上下文恢復系統',
        'priority': 5,
        'critical': True,
    },
    'cli_auto_updater': {
        'module_path': 'src/cli/cli_auto_updater',
        'startup_func': 'start_auto_updater',
        'description': 'CLI 自動更新系統',
        'priority': 6,
        'critical': False,
    },
}


class AutoReplySystemManager:
    """自動回覆系統管理器"""
    
    def __init__(self, project_root: str = '/workspaces/cosmic-ai.uk'):
        self.project_root = Path(project_root)
        self.started_systems: Dict[str, bool] = {}
        sys.path.insert(0, str(self.project_root))
    
    def startup_all(self) -> Tuple[int, int]:
        """
        啟動所有自動回覆系統
        
        Returns:
            (成功數, 失敗數)
        """
        logger.info("\n" + "="*70)
        logger.info("🚀 啟動自動回覆系統")
        logger.info("="*70)
        
        # 按優先級排序
        sorted_systems = sorted(
            AUTO_REPLY_SYSTEMS_CONFIG.items(),
            key=lambda x: x[1]['priority']
        )
        
        success_count = 0
        fail_count = 0
        
        for system_name, config in sorted_systems:
            logger.info(f"\n[{config['priority']}] 啟動: {config['description']}")
            logger.info(f"     模組: {config['module_path']}")
            
            try:
                result = self._start_system(system_name, config)
                if result:
                    logger.info(f"     ✅ 啟動成功")
                    self.started_systems[system_name] = True
                    success_count += 1
                else:
                    logger.warning(f"     ⚠️  啟動失敗")
                    self.started_systems[system_name] = False
                    if config['critical']:
                        fail_count += 1
                    
            except Exception as e:
                logger.error(f"     ❌ 異常: {e}")
                self.started_systems[system_name] = False
                if config['critical']:
                    fail_count += 1
        
        logger.info("\n" + "="*70)
        logger.info("📊 啟動結果摘要")
        logger.info("="*70)
        logger.info(f"✅ 成功: {success_count}")
        logger.info(f"❌ 失敗: {fail_count}")
        logger.info(f"📈 成功率: {success_count/(success_count+fail_count)*100:.1f}%")
        
        return success_count, fail_count
    
    def _start_system(self, system_name: str, config: Dict) -> bool:
        """啟動單個系統"""
        try:
            # 導入模組
            module = self._import_module(config['module_path'])
            
            if module is None:
                logger.debug(f"模組 {config['module_path']} 不存在")
                return False
            
            # 查找啟動函數
            if hasattr(module, config['startup_func']):
                startup_func = getattr(module, config['startup_func'])
                result = startup_func()
                return result if isinstance(result, bool) else True
            else:
                logger.debug(f"模組中未找到 {config['startup_func']} 函數")
                return True  # 假設模組在導入時自動啟動
                
        except ImportError as e:
            logger.debug(f"導入錯誤: {e}")
            return False
        except Exception as e:
            logger.debug(f"執行錯誤: {e}")
            return False
    
    def _import_module(self, module_path: str):
        """動態導入模組"""
        try:
            # 嘗試直接導入
            parts = module_path.replace('/', '.').replace('.py', '').split('.')
            module = __import__(module_path.replace('/', '.'), fromlist=[parts[-1]])
            return module
        except ImportError:
            try:
                # 嘗試從文件路徑導入
                file_path = self.project_root / (module_path + '.py')
                if file_path.exists():
                    spec = importlib.util.spec_from_file_location(
                        module_path.replace('/', '.'),
                        file_path
                    )
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    return module
            except Exception:
                pass
            return None
    
    def get_status(self) -> Dict[str, bool]:
        """獲取所有系統的狀態"""
        return self.started_systems.copy()
    
    def get_summary(self) -> str:
        """獲取摘要信息"""
        total = len(self.started_systems)
        started = sum(1 for v in self.started_systems.values() if v)
        
        summary = f"""
╔═══════════════════════════════════════════════════════╗
║        🤖 自動回覆系統啟動摘要                        ║
╠═══════════════════════════════════════════════════════╣
║  總系統數:        {total:3d}                            ║
║  已啟動:          {started:3d}                            ║
║  未啟動:          {total-started:3d}                            ║
║  啟動率:          {started/total*100:5.1f}%                        ║
╠═══════════════════════════════════════════════════════╣
"""
        
        for system_name, status in self.started_systems.items():
            icon = "✅" if status else "❌"
            config = AUTO_REPLY_SYSTEMS_CONFIG[system_name]
            summary += f"║  {icon} {config['description']:35s}    ║\n"
        
        summary += "╚═══════════════════════════════════════════════════════╝"
        return summary


def main():
    """主函數"""
    manager = AutoReplySystemManager()
    success, fail = manager.startup_all()
    
    print(manager.get_summary())
    
    # 返回狀態碼
    return 0 if fail == 0 else 1


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
