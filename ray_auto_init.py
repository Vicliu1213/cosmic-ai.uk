#!/usr/bin/env python3
"""
Ray Auto-Initialization Module
Ray 自動初始化模組 - 系統啟動時自動開啟並行處理
"""

import ray
import logging
from typing import Dict, Any, Optional
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RayAutoInit:
    """Ray 自動初始化管理器"""
    
    _initialized = False
    
    @classmethod
    def init(cls, auto_start: bool = True, **kwargs) -> bool:
        """
        初始化 Ray 並行處理
        
        Args:
            auto_start: 是否自動啟動
            **kwargs: 傳遞給 ray.init() 的參數
            
        Returns:
            是否成功初始化
        """
        if cls._initialized:
            logger.info("✅ Ray 已初始化，跳過重複初始化")
            return True
        
        try:
            if not auto_start:
                logger.warning("⚠️  Ray 自動啟動已禁用")
                return False
            
            # 默認配置
            default_config = {
                'num_cpus': os.cpu_count() or 4,
                'object_store_memory': int(1e9),  # 1GB
                'log_to_driver': True,
                'include_dashboard': False,
                '_temp_dir': '/tmp/ray',
            }
            
            # 合併用戶配置
            config = {**default_config, **kwargs}
            
            logger.info("🚀 正在啟動 Ray...")
            logger.info(f"   CPU 核心: {config['num_cpus']}")
            logger.info(f"   對象存儲: {config['object_store_memory'] / 1e9:.1f} GB")
            
            ray.init(**config)
            
            cls._initialized = True
            logger.info("✅ Ray 啟動成功")
            
            # 顯示集群信息
            info = ray.cluster_resources()
            logger.info(f"\n📊 Ray 集群資源:")
            for key, value in info.items():
                logger.info(f"   {key}: {value}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Ray 初始化失敗: {e}")
            return False
    
    @classmethod
    def shutdown(cls) -> None:
        """關閉 Ray"""
        if ray.is_initialized():
            logger.info("🛑 正在關閉 Ray...")
            ray.shutdown()
            cls._initialized = False
            logger.info("✅ Ray 已關閉")
    
    @classmethod
    def is_ready(cls) -> bool:
        """檢查 Ray 是否就緒"""
        return ray.is_initialized()
    
    @classmethod
    def get_status(cls) -> Dict[str, Any]:
        """獲取 Ray 狀態"""
        if not ray.is_initialized():
            return {'status': 'not_initialized', 'initialized': False}
        
        return {
            'status': 'initialized',
            'initialized': True,
            'resources': ray.cluster_resources(),
            'nodes': len(ray.nodes()),
            'version': ray.__version__,
        }


# 自動初始化標誌
_AUTO_INIT_ENABLED = True


def auto_init_ray():
    """在模組導入時自動初始化 Ray"""
    if _AUTO_INIT_ENABLED and not ray.is_initialized():
        RayAutoInit.init(auto_start=True)


# 當此模組被導入時自動運行
auto_init_ray()


if __name__ == '__main__':
    # 測試
    logger.info("\n" + "="*60)
    logger.info("🧪 Ray 自動初始化測試")
    logger.info("="*60 + "\n")
    
    # 初始化
    success = RayAutoInit.init(auto_start=True)
    logger.info(f"\n初始化結果: {'✅ 成功' if success else '❌ 失敗'}")
    
    # 獲取狀態
    status = RayAutoInit.get_status()
    logger.info(f"\n狀態信息:")
    for key, value in status.items():
        logger.info(f"  {key}: {value}")
    
    # 關閉
    RayAutoInit.shutdown()
    logger.info("\n✅ 測試完成")

