#!/usr/bin/env python3
"""
永生系統直接啟動器 - 同步啟動所有組件
"""

import subprocess
import time
import logging
import sys
import os
from pathlib import Path
import asyncio
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(name)s] - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """主函數 - 直接啟動超腦控制器"""
    
    workspace = Path("/workspaces/cosmic-ai.uk")
    log_dir = workspace / "logs" / "eternal_system"
    log_dir.mkdir(parents=True, exist_ok=True)
    
    logger.info("=" * 120)
    logger.info("🧠 超腦系統永生 - 直接啟動".center(120))
    logger.info("=" * 120)
    
    logger.info("\n【檢查系統依賴】")
    logger.info("-" * 120)
    
    try:
        import ray
        logger.info(f"✅ Ray 已安裝: {ray.__version__}")
    except ImportError:
        logger.error("❌ Ray 未安裝")
        return
    
    try:
        import psutil
        logger.info(f"✅ psutil 已安裝")
    except ImportError:
        logger.error("❌ psutil 未安裝")
        return
    
    try:
        from quantum_cost_optimization import QuantumCostOptimization
        logger.info("✅ 量子優化引擎可用")
    except ImportError:
        logger.error("❌ 量子優化引擎未找到")
        return
    
    logger.info("\n【步驟 1】確保 Ray 集群運行")
    logger.info("-" * 120)
    
    try:
        if not ray.is_initialized():
            logger.info("🚀 初始化 Ray 集群...")
            ray.init(
                num_cpus=4,
                object_store_memory=int(2e9),
                log_to_driver=False,
                ignore_reinit_error=True
            )
        else:
            logger.info("✅ Ray 集群已運行")
        
        logger.info(f"✅ Ray 資源: {ray.available_resources()}")
    
    except Exception as e:
        logger.error(f"❌ Ray 初始化失敗: {e}")
        return
    
    logger.info("\n【步驟 2】啟動超腦控制器】")
    logger.info("-" * 120)
    
    try:
        # 動態導入控制器
        sys.path.insert(0, str(workspace))
        from ultrabrain_controller import UltraBrainController
        
        logger.info("✅ 超腦控制器已導入")
        
        # 啟動控制器
        logger.info("🔄 創建控制器實例...")
        controller = UltraBrainController()
        
        logger.info("🔄 啟動永生循環...")
        
        # 使用事件循環運行永生循環
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            loop.run_until_complete(controller.eternal_life_cycle())
        except KeyboardInterrupt:
            logger.info("\n⚠️  接收到中斷信號")
        finally:
            loop.close()
    
    except Exception as e:
        logger.error(f"❌ 啟動失敗: {e}", exc_info=True)
        return


if __name__ == "__main__":
    main()
