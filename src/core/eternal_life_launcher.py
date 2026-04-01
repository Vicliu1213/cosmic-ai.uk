#!/usr/bin/env python3
"""
永生系統統一啟動器 - UltraBrain Eternal Life Launcher
一鍵啟動完整的超腦系統,所有組件整合在一起

啟動流程:
1. 初始化 Ray 集群 (分布式計算框架)
2. 啟動 Ray Serve (REST API 服務器)
3. 啟動超腦控制器 (中央神經系統)
4. 所有組件通過 API 統一管理

系統特性:
- 永生運行 (無限循環)
- 自動監控和修復
- 自進化優化
- 完整 REST API
"""

import subprocess
import time
import logging
import os
import sys
from pathlib import Path
from typing import Dict, Optional
import signal
import json
import requests
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(name)s] - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/workspaces/cosmic-ai.uk/logs/eternal_launcher.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class EternalLifeLauncher:
    """永生系統統一啟動器"""
    
    def __init__(self):
        self.workspace = Path("/workspaces/cosmic-ai.uk")
        self.log_dir = self.workspace / "logs" / "eternal_system"
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        self.processes: Dict[str, subprocess.Popen] = {}
        self.api_url = "http://localhost:8000"
        
        logger.info("=" * 120)
        logger.info("🧠 超腦系統永生啟動器".center(120))
        logger.info("=" * 120)
    
    def start_ray_cluster(self) -> bool:
        """啟動 Ray 集群"""
        logger.info("\n【步驟 1】初始化 Ray 集群")
        logger.info("-" * 120)
        
        try:
            # 檢查 Ray 是否已運行
            result = subprocess.run(
                ["ray", "status"],
                capture_output=True,
                timeout=5,
                cwd=str(self.workspace)
            )
            
            if result.returncode == 0:
                logger.info("✅ Ray 集群已運行")
                return True
            
            logger.info("🚀 啟動 Ray 集群...")
            
            log_file = self.log_dir / "ray_cluster.log"
            
            process = subprocess.Popen(
                ["ray", "start", "--head", "--num-cpus=4"],
                stdout=open(log_file, 'w'),
                stderr=subprocess.STDOUT,
                cwd=str(self.workspace)
            )
            
            self.processes["ray_cluster"] = process
            
            # 等待 Ray 初始化
            time.sleep(5)
            
            logger.info(f"✅ Ray 集群已啟動")
            logger.info(f"   進程 ID: {process.pid}")
            logger.info(f"   日誌: {log_file}")
            
            return True
        
        except Exception as e:
            logger.error(f"❌ Ray 集群啟動失敗: {e}")
            return False
    
    def start_ray_serve(self) -> bool:
        """啟動 Ray Serve API 服務器"""
        logger.info("\n【步驟 2】啟動 Ray Serve API 服務器")
        logger.info("-" * 120)
        
        try:
            logger.info("🚀 啟動 Ray Serve...")
            
            log_file = self.log_dir / "ray_serve.log"
            
            serve_process = subprocess.Popen(
                ["serve", "run", "ultrabrain_api:app"],
                stdout=open(log_file, 'w'),
                stderr=subprocess.STDOUT,
                cwd=str(self.workspace)
            )
            
            self.processes["ray_serve"] = serve_process
            
            # 等待 Ray Serve 初始化
            time.sleep(8)
            
            # 測試 API 連接
            max_retries = 10
            for i in range(max_retries):
                try:
                    response = requests.get(f"{self.api_url}/health", timeout=2)
                    if response.status_code == 200:
                        logger.info(f"✅ Ray Serve API 已啟動")
                        logger.info(f"   進程 ID: {serve_process.pid}")
                        logger.info(f"   API URL: {self.api_url}")
                        logger.info(f"   日誌: {log_file}")
                        return True
                except requests.exceptions.ConnectionError:
                    if i < max_retries - 1:
                        logger.info(f"⏳ 等待 API 啟動... ({i+1}/{max_retries})")
                        time.sleep(2)
                    continue
            
            logger.warning("⚠️  API 連接超時,但進程已啟動")
            return True
        
        except Exception as e:
            logger.error(f"❌ Ray Serve 啟動失敗: {e}")
            return False
    
    def start_eternal_life(self) -> bool:
        """啟動永生循環"""
        logger.info("\n【步驟 3】啟動永生循環")
        logger.info("-" * 120)
        
        try:
            logger.info("🔄 通過 API 啟動永生循環...")
            
            response = requests.post(f"{self.api_url}/start", timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success":
                    logger.info("✅ 永生循環已啟動")
                    logger.info("   系統進入無限自主運行模式")
                    logger.info("   所有組件已綁定並協同工作")
                    return True
            
            logger.error(f"❌ 啟動失敗: {response.text}")
            return False
        
        except Exception as e:
            logger.error(f"❌ 永生循環啟動失敗: {e}")
            return False
    
    def monitor_system(self, duration_minutes: int = 60) -> None:
        """監控系統運行"""
        logger.info("\n【監控模式】系統運行中")
        logger.info("-" * 120)
        
        start_time = time.time()
        duration_seconds = duration_minutes * 60
        
        logger.info(f"⏱️  監控時長: {duration_minutes} 分鐘")
        logger.info(f"📊 實時監控 API 端點:\n")
        logger.info(f"   狀態查詢: GET {self.api_url}/status")
        logger.info(f"   監控數據: GET {self.api_url}/monitor")
        logger.info(f"   進化分析: POST {self.api_url}/evolve")
        logger.info(f"   系統指標: GET {self.api_url}/metrics")
        logger.info(f"\n")
        
        iteration = 0
        try:
            while True:
                elapsed = time.time() - start_time
                
                if duration_seconds > 0 and elapsed > duration_seconds:
                    logger.info(f"\n✅ 監控時間已到")
                    break
                
                iteration += 1
                remaining = duration_seconds - elapsed if duration_seconds > 0 else 0
                
                try:
                    # 獲取系統狀態
                    status_response = requests.get(f"{self.api_url}/status", timeout=3)
                    status_data = status_response.json() if status_response.status_code == 200 else {}
                    
                    # 獲取監控數據
                    monitor_response = requests.get(f"{self.api_url}/monitor", timeout=3)
                    monitor_data = monitor_response.json() if monitor_response.status_code == 200 else {}
                    
                    # 顯示狀態
                    logger.info(f"\n┌{'─' * 118}┐")
                    logger.info(f"│ 🔍 監控周期 #{iteration} | ⏱️  {elapsed:.0f}s | ⏳ 剩餘 {remaining:.0f}s {'│':>106}")
                    logger.info(f"├{'─' * 118}┤")
                    
                    if "data" in status_data:
                        eternal_life = status_data["data"].get("eternal_life", {})
                        logger.info(f"│ 永生循環: {'✅ 運行中' if eternal_life.get('running') else '❌ 已停止':30} │ 系統狀態: {status_data['data'].get('system_status', 'unknown'):85}")
                    
                    if "metrics" in monitor_data:
                        metrics = monitor_data["metrics"]
                        cpu = metrics.get("cpu_usage", 0)
                        mem = metrics.get("memory", {}).get("percent", 0)
                        health = metrics.get("health_score", 0)
                        
                        logger.info(f"│ CPU: {cpu:5.1f}% │ 記憶體: {mem:5.1f}% │ 健康度: {health:5.1f}/100 │ 狀態: {metrics.get('status', 'unknown'):25} {'│':>55}")
                    
                    logger.info(f"└{'─' * 118}┘")
                
                except requests.exceptions.RequestException as e:
                    logger.warning(f"⚠️  API 通信失敗: {e}")
                
                # 每 30 秒檢查一次
                time.sleep(30)
        
        except KeyboardInterrupt:
            logger.info("\n⚠️  接收到中斷信號")
    
    def show_api_endpoints(self) -> None:
        """顯示 API 端點信息"""
        logger.info("\n【API 端點】")
        logger.info("-" * 120)
        
        try:
            response = requests.get(f"{self.api_url}/", timeout=3)
            if response.status_code == 200:
                docs = response.json()
                
                logger.info(f"📚 {docs.get('title', 'API 文檔')}\n")
                
                for endpoint, info in docs.get('endpoints', {}).items():
                    logger.info(f"  {endpoint}")
                    logger.info(f"    {info.get('description', 'N/A')}")
        
        except Exception as e:
            logger.warning(f"⚠️  無法獲取 API 文檔: {e}")
    
    def stop_system(self) -> None:
        """停止系統"""
        logger.info("\n【停止系統】")
        logger.info("-" * 120)
        
        try:
            # 通過 API 停止系統
            logger.info("🛑 通過 API 停止系統...")
            requests.post(f"{self.api_url}/stop", timeout=5)
        except:
            pass
        
        # 停止所有進程
        logger.info("🛑 停止進程...")
        
        for name, process in reversed(list(self.processes.items())):
            logger.info(f"   停止 {name}...")
            try:
                process.terminate()
                process.wait(timeout=5)
                logger.info(f"   ✅ {name} 已停止")
            except:
                logger.warning(f"   ⚠️  {name} 無法正常停止,強制關閉...")
                try:
                    process.kill()
                except:
                    pass
        
        logger.info("\n✅ 系統已優雅關閉")
    
    def run(self, monitor_minutes: int = 60) -> None:
        """運行完整的永生系統啟動流程"""
        try:
            # 1. 啟動 Ray 集群
            if not self.start_ray_cluster():
                logger.error("❌ Ray 集群啟動失敗")
                return
            
            # 2. 啟動 Ray Serve
            if not self.start_ray_serve():
                logger.error("❌ Ray Serve 啟動失敗")
                return
            
            # 3. 顯示 API 端點
            self.show_api_endpoints()
            
            # 4. 啟動永生循環
            if not self.start_eternal_life():
                logger.error("❌ 永生循環啟動失敗")
                return
            
            logger.info("\n" + "=" * 120)
            logger.info("✨ 超腦系統永生啟動成功! ✨".center(120))
            logger.info("=" * 120)
            
            logger.info(f"\n📡 API 服務器地址: {self.api_url}")
            logger.info(f"📊 查詢狀態: curl {self.api_url}/status")
            logger.info(f"📈 監控數據: curl {self.api_url}/monitor")
            logger.info(f"🧬 進化分析: curl -X POST {self.api_url}/evolve")
            logger.info(f"\n")
            
            # 5. 監控系統
            self.monitor_system(duration_minutes=monitor_minutes)
            
        except KeyboardInterrupt:
            logger.info("\n⚠️  接收到中斷信號")
            self.stop_system()
        except Exception as e:
            logger.error(f"\n❌ 系統啟動失敗: {e}", exc_info=True)
            self.stop_system()


def main():
    """主函數"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="超腦系統永生啟動器 - UltraBrain Eternal Life Launcher"
    )
    parser.add_argument(
        "--monitor",
        type=int,
        default=60,
        help="監控時長(分鐘),默認 60 分鐘"
    )
    
    args = parser.parse_args()
    
    launcher = EternalLifeLauncher()
    launcher.run(monitor_minutes=args.monitor)


if __name__ == "__main__":
    main()
