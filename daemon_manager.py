#!/usr/bin/env python3
"""
自動化守護程序管理器
Auto Daemon Manager - 管理自動化守護程序的生命周期
"""

import sys
import os
import subprocess
import signal
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any
import argparse
import logging

# 設置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 全局配置
DAEMON_SCRIPT = Path(__file__).parent / 'auto_evolution_daemon.py'
PID_FILE = Path(__file__).parent / '.daemon.pid'
STATUS_FILE = Path(__file__).parent / 'logs' / 'daemon_status.json'


def read_daemon_status() -> Dict[str, Any]:
    """讀取守護程序狀態"""
    try:
        if STATUS_FILE.exists():
            with open(STATUS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        logger.error(f"讀取狀態文件失敗: {e}")
    return {}


def is_daemon_running() -> bool:
    """檢查守護程序是否正在運行"""
    try:
        if PID_FILE.exists():
            with open(PID_FILE, 'r') as f:
                pid = int(f.read().strip())
            
            # 檢查進程是否存在
            os.kill(pid, 0)  # 不發送信號，只檢查進程是否存在
            return True
    except (FileNotFoundError, ValueError, ProcessLookupError):
        pass
    return False


def start_daemon() -> bool:
    """啟動守護程序"""
    try:
        if is_daemon_running():
            logger.warning("⚠️  守護程序已在運行中")
            return False
        
        if not DAEMON_SCRIPT.exists():
            logger.error(f"❌ 守護程序腳本不存在: {DAEMON_SCRIPT}")
            return False
        
        # 確保日誌目錄存在
        DAEMON_SCRIPT.parent.joinpath('logs').mkdir(exist_ok=True)
        
        # 啟動新進程
        process = subprocess.Popen(
            [sys.executable, str(DAEMON_SCRIPT)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True
        )
        
        # 保存 PID
        with open(PID_FILE, 'w') as f:
            f.write(str(process.pid))
        
        time.sleep(1)
        
        if is_daemon_running():
            logger.info(f"✅ 守護程序已啟動 (PID: {process.pid})")
            return True
        else:
            logger.error("❌ 守護程序啟動失敗")
            return False
            
    except Exception as e:
        logger.error(f"❌ 啟動守護程序時出錯: {e}")
        return False


def stop_daemon() -> bool:
    """停止守護程序"""
    try:
        if not is_daemon_running():
            logger.warning("⚠️  守護程序未在運行")
            return False
        
        with open(PID_FILE, 'r') as f:
            pid = int(f.read().strip())
        
        # 嘗試優雅關閉
        try:
            os.killpg(os.getpgid(pid), signal.SIGTERM)
            
            # 等待進程終止
            for _ in range(10):
                if not is_daemon_running():
                    break
                time.sleep(0.5)
            
            # 如果還在運行，發送 SIGKILL
            if is_daemon_running():
                os.killpg(os.getpgid(pid), signal.SIGKILL)
                time.sleep(0.5)
            
            # 清理 PID 文件
            PID_FILE.unlink(missing_ok=True)
            
            logger.info("✅ 守護程序已停止")
            return True
            
        except ProcessLookupError:
            PID_FILE.unlink(missing_ok=True)
            logger.info("✅ 守護程序已停止")
            return True
            
    except Exception as e:
        logger.error(f"❌ 停止守護程序時出錯: {e}")
        return False


def get_daemon_status() -> Dict[str, Any]:
    """獲取守護程序狀態"""
    status = {
        "is_running": is_daemon_running(),
        "timestamp": datetime.now().isoformat(),
    }
    
    if PID_FILE.exists():
        try:
            with open(PID_FILE, 'r') as f:
                status["pid"] = int(f.read().strip())
        except:
            pass
    
    # 讀取詳細狀態
    detailed_status = read_daemon_status()
    if detailed_status:
        status.update(detailed_status)
    
    return status


def print_status(status: Dict[str, Any]):
    """打印守護程序狀態"""
    print("\n" + "=" * 70)
    print("🔍 守護程序狀態")
    print("=" * 70)
    
    is_running = status.get("is_running", False)
    status_text = "✅ 運行中" if is_running else "❌ 已停止"
    print(f"狀態: {status_text}")
    
    if "pid" in status:
        print(f"PID: {status['pid']}")
    
    if "timestamp" in status:
        print(f"檢查時間: {status['timestamp']}")
    
    if "threads" in status:
        print(f"運行線程數: {status['threads']}")
    
    # 容錯監控狀態
    if "fault_tolerance" in status:
        ft = status["fault_tolerance"]
        print("\n📊 容錯監控狀態:")
        if isinstance(ft, dict) and "fault_tolerance" in ft:
            ft_data = ft["fault_tolerance"]
            print(f"  • 健康節點: {ft_data.get('healthy_nodes', 'N/A')}")
            print(f"  • 故障節點: {ft_data.get('faulty_nodes', [])}")
            print(f"  • 整體健康度: {ft_data.get('overall_health', 'N/A')}%")
    
    # 進化引擎狀態
    if "evolution" in status:
        ev = status["evolution"]
        print("\n🧬 進化引擎狀態:")
        print(f"  • 當前代數: {ev.get('current_generation', 'N/A')}")
        print(f"  • 最佳適應度: {ev.get('best_fitness', 'N/A'):.4f}" if isinstance(ev.get('best_fitness'), (int, float)) else f"  • 最佳適應度: {ev.get('best_fitness', 'N/A')}")
        print(f"  • 總進化次數: {ev.get('total_evolutions', 'N/A')}")
    
    print("=" * 70 + "\n")


def restart_daemon() -> bool:
    """重啟守護程序"""
    logger.info("🔄 重啟守護程序...")
    stop_daemon()
    time.sleep(1)
    return start_daemon()


def main():
    """主函數"""
    parser = argparse.ArgumentParser(
        description="自動化守護程序管理器 (Auto Daemon Manager)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python daemon_manager.py --start     # 啟動守護程序
  python daemon_manager.py --stop      # 停止守護程序
  python daemon_manager.py --status    # 檢查狀態
  python daemon_manager.py --restart   # 重啟守護程序
        """
    )
    
    parser.add_argument('--start', action='store_true', help='啟動守護程序')
    parser.add_argument('--stop', action='store_true', help='停止守護程序')
    parser.add_argument('--status', action='store_true', help='檢查狀態')
    parser.add_argument('--restart', action='store_true', help='重啟守護程序')
    
    args = parser.parse_args()
    
    # 如果沒有指定任何操作，顯示狀態
    if not any([args.start, args.stop, args.status, args.restart]):
        args.status = True
    
    try:
        if args.start:
            start_daemon()
        
        if args.stop:
            stop_daemon()
        
        if args.restart:
            restart_daemon()
        
        if args.status:
            status = get_daemon_status()
            print_status(status)
    
    except KeyboardInterrupt:
        print("\n✅ 已取消操作")
    except Exception as e:
        logger.error(f"❌ 發生錯誤: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
