#!/usr/bin/env python3
"""
Comic AI 完整啟動流程 - 包含自動回顧 + 自動化守護程序
Full Startup Flow with Automatic Session Recap + Auto Daemon
"""

import sys
import os
import logging
import subprocess
import time
import signal
from pathlib import Path
from datetime import datetime
from typing import Optional

# 添加項目路徑
sys.path.insert(0, '/root/comic_ai')
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from main_system import ComicAISystem

# 全局守護程序進程
daemon_process = None


def setup_startup_logger() -> logging.Logger:
    """設置啟動日誌"""
    logger = logging.getLogger("ComicAI_Startup")
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger


def start_daemon(logger: logging.Logger) -> Optional[subprocess.Popen]:
    """啟動自動化守護程序"""
    try:
        logger.info("🚀 啟動自動化守護程序...")
        daemon_path = Path(__file__).parent / 'auto_evolution_daemon.py'
        
        if not daemon_path.exists():
            logger.warning(f"⚠️  守護程序文件不存在: {daemon_path}")
            return None
        
        # 啟動守護程序進程
        process = subprocess.Popen(
            [sys.executable, str(daemon_path)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True  # 建立新進程組，不與主程序共享終端
        )
        
        time.sleep(1)  # 等待守護程序啟動
        
        if process.poll() is None:  # 檢查進程是否仍在運行
            logger.info(f"✅ 守護程序已啟動 (PID: {process.pid})")
            return process
        else:
            logger.error("❌ 守護程序啟動失敗")
            return None
            
    except Exception as e:
        logger.error(f"❌ 無法啟動守護程序: {e}")
        return None


def stop_daemon(logger: logging.Logger):
    """停止守護程序"""
    global daemon_process
    try:
        if daemon_process and daemon_process.poll() is None:
            logger.info("🛑 停止守護程序...")
            os.killpg(os.getpgid(daemon_process.pid), signal.SIGTERM)
            daemon_process.wait(timeout=5)
            logger.info("✅ 守護程序已停止")
    except Exception as e:
        logger.warning(f"⚠️  停止守護程序時出錯: {e}")
        try:
            if daemon_process:
                os.killpg(os.getpgid(daemon_process.pid), signal.SIGKILL)
        except:
            pass


def print_startup_banner():
    """顯示啟動橫幅"""
    banner = """
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║           🚀 Comic AI - 完整系統啟動流程啟動                         ║
║           Comic AI - Full System Startup Flow                        ║
║                                                                      ║
║           ✨ 包含功能：                                              ║
║           • 自動會話回顧 (Auto Session Recap)                        ║
║           • 防閃退系統 (Crash Prevention)                            ║
║           • 自動斷線重連 (Auto Reconnection)                         ║
║           • 實時監控 (Real-time Monitoring)                          ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
"""
    print(banner)


def main():
    """主函數"""
    print_startup_banner()
    
    logger = setup_startup_logger()
    logger.info("=" * 70)
    logger.info("啟動時間: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    logger.info("=" * 70)
    
    global daemon_process
    
    try:
        # 啟動守護程序
        daemon_process = start_daemon(logger)
        
        # 創建並運行系統
        system = ComicAISystem()
        system.run()
    
    except KeyboardInterrupt:
        logger.info("\n✅ 系統已優雅關閉")
    
    except Exception as e:
        logger.error(f"❌ 啟動失敗: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    finally:
        # 確保守護程序被停止
        stop_daemon(logger)


if __name__ == "__main__":
    main()
