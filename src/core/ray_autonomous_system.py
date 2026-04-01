#!/usr/bin/env python3
"""
Ray 自動執行系統 - Ray Autonomous Execution System
集成所有系統(量子優化、守護程序、監控)到 Ray 分佈式框架

核心功能:
1. 自動啟動 Ray 集群
2. 分布式執行量子優化
3. 自動執行守護程序
4. 實時監控和儀表板
5. 無縫自動運行
"""

import ray
import logging
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
import json
import os
import asyncio
from dataclasses import dataclass, asdict
import numpy as np

# 配置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(name)s] - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class RayClusterConfig:
    """Ray 集群配置"""
    num_cpus: Optional[int] = None
    num_gpus: int = 0
    memory_gb: int = 4
    object_store_gb: int = 2
    dashboard: bool = False  # 關閉儀表板以避免依賴問題
    dashboard_port: int = 8265


class RayQuantumExecutor:
    """Ray 量子執行器 - 分布式執行量子優化"""
    
    def __init__(self, config: Optional[RayClusterConfig] = None):
        self.config = config or RayClusterConfig()
        self.is_initialized = False
        self.tasks = []
        logger.info("🚀 初始化 Ray 量子執行器")
    
    def initialize_cluster(self) -> bool:
        """初始化 Ray 集群"""
        try:
            if not ray.is_initialized():
                logger.info("📡 啟動 Ray 集群...")
                
                init_kwargs = {
                    "include_dashboard": self.config.dashboard,
                }
                
                if self.config.num_cpus:
                    init_kwargs["num_cpus"] = self.config.num_cpus
                if self.config.num_gpus:
                    init_kwargs["num_gpus"] = self.config.num_gpus
                
                ray.init(**init_kwargs)
                
                self.is_initialized = True
                logger.info("✅ Ray 集群已啟動")
                self._print_cluster_info()
                return True
            else:
                logger.info("✅ Ray 集群已存在")
                self.is_initialized = True
                return True
                
        except Exception as e:
            logger.error(f"❌ Ray 集群初始化失敗: {e}")
            return False
    
    def _print_cluster_info(self):
        """打印集群信息"""
        try:
            info = ray.cluster_resources()
            logger.info(f"📊 Ray 集群資源:")
            logger.info(f"   CPU: {info.get('CPU', 0)}")
            logger.info(f"   GPU: {info.get('GPU', 0)}")
            logger.info(f"   對象存儲: {info.get('object_store_memory', 0) / (1024**3):.2f} GB")
            
            dashboard_url = f"http://127.0.0.1:{self.config.dashboard_port}"
            logger.info(f"   📈 儀表板: {dashboard_url}")
        except Exception as e:
            logger.warning(f"⚠️  無法獲取集群信息: {e}")
    
    @ray.remote
    def execute_quantum_optimization(self, token_costs: List[float]) -> Dict[str, Any]:
        """Ray 遠程函數: 執行量子優化
        
        此函數在 Ray worker 上並行執行
        """
        from quantum_cost_optimization import QuantumCostOptimizationSystem
        
        logger.info(f"🧬 [Worker] 執行量子優化 {len(token_costs)} 個 token")
        
        system = QuantumCostOptimizationSystem()
        states = system.optimize_token_stream(token_costs)
        report = system.generate_optimization_report()
        
        return {
            "success": True,
            "token_count": len(token_costs),
            "original_cost": system.total_original_cost,
            "optimized_cost": system.total_optimized_cost,
            "savings": system.total_original_cost - system.total_optimized_cost,
            "report": report
        }
    
    @ray.remote
    def execute_daemon_monitoring(self, duration_seconds: int = 30) -> Dict[str, Any]:
        """Ray 遠程函數: 執行守護程序監控
        
        此函數在 Ray worker 上執行監控
        """
        import time
        import psutil
        from datetime import datetime
        
        logger.info(f"🔍 [Worker] 開始監控 {duration_seconds} 秒")
        
        monitoring_data = {
            "start_time": datetime.now().isoformat(),
            "cpu_samples": [],
            "memory_samples": [],
            "errors": []
        }
        
        start_time = time.time()
        while time.time() - start_time < duration_seconds:
            try:
                # 收集系統數據
                cpu_percent = psutil.cpu_percent(interval=1)
                memory_info = psutil.virtual_memory()
                
                monitoring_data["cpu_samples"].append(cpu_percent)
                monitoring_data["memory_samples"].append(memory_info.percent)
                
                # 檢測故障
                if cpu_percent > 85:
                    monitoring_data["errors"].append({
                        "type": "HIGH_CPU",
                        "value": cpu_percent,
                        "timestamp": datetime.now().isoformat()
                    })
                
                if memory_info.percent > 85:
                    monitoring_data["errors"].append({
                        "type": "HIGH_MEMORY",
                        "value": memory_info.percent,
                        "timestamp": datetime.now().isoformat()
                    })
                
                time.sleep(5)
                
            except Exception as e:
                logger.error(f"❌ [Worker] 監控錯誤: {e}")
                monitoring_data["errors"].append({"error": str(e)})
        
        monitoring_data["end_time"] = datetime.now().isoformat()
        monitoring_data["error_count"] = len(monitoring_data["errors"])
        
        return monitoring_data
    
    @ray.remote
    def execute_dashboard_update(self) -> Dict[str, Any]:
        """Ray 遠程函數: 更新儀表板
        
        此函數在 Ray worker 上更新儀表板數據
        """
        from quantum_dashboard import QuantumDashboard
        
        logger.info(f"📊 [Worker] 更新儀表板")
        
        dashboard = QuantumDashboard()
        if dashboard.report:
            return {
                "success": True,
                "timestamp": datetime.now().isoformat(),
                "report": dashboard.report,
                "optimization_complete": True
            }
        else:
            return {
                "success": False,
                "error": "No report available"
            }
    
    def submit_quantum_task(self, token_costs: List[float]) -> str:
        """提交量子優化任務到 Ray"""
        logger.info(f"📤 提交量子優化任務 ({len(token_costs)} tokens)")
        
        future = self.execute_quantum_optimization.remote(token_costs)
        self.tasks.append({
            "id": str(future),
            "type": "quantum_optimization",
            "submitted_at": datetime.now().isoformat(),
            "future": future
        })
        
        logger.info(f"✅ 任務已提交: {future}")
        return str(future)
    
    def submit_monitoring_task(self, duration: int = 30) -> str:
        """提交監控任務到 Ray"""
        logger.info(f"📤 提交監控任務 ({duration}秒)")
        
        future = self.execute_daemon_monitoring.remote(duration)
        self.tasks.append({
            "id": str(future),
            "type": "monitoring",
            "submitted_at": datetime.now().isoformat(),
            "future": future
        })
        
        logger.info(f"✅ 監控任務已提交: {future}")
        return str(future)
    
    def submit_dashboard_task(self) -> str:
        """提交儀表板更新任務到 Ray"""
        logger.info(f"📤 提交儀表板更新任務")
        
        future = self.execute_dashboard_update.remote()
        self.tasks.append({
            "id": str(future),
            "type": "dashboard",
            "submitted_at": datetime.now().isoformat(),
            "future": future
        })
        
        logger.info(f"✅ 儀表板任務已提交: {future}")
        return str(future)
    
    def wait_for_task(self, future_id: str, timeout: Optional[float] = None) -> Any:
        """等待任務完成"""
        for task in self.tasks:
            if str(task["future"]) == future_id:
                logger.info(f"⏳ 等待任務完成: {future_id}")
                try:
                    result = ray.get(task["future"], timeout=timeout)
                    logger.info(f"✅ 任務完成")
                    return result
                except Exception as e:
                    logger.error(f"❌ 任務失敗: {e}")
                    return None
        
        logger.warning(f"⚠️  未找到任務: {future_id}")
        return None
    
    def get_all_results(self, timeout: Optional[float] = None) -> List[Dict]:
        """獲取所有已完成任務的結果"""
        logger.info(f"📊 收集所有任務結果...")
        
        results = []
        for task in self.tasks:
            try:
                result = ray.get(task["future"], timeout=timeout or 10)
                results.append({
                    "id": task["id"],
                    "type": task["type"],
                    "result": result
                })
            except Exception as e:
                logger.warning(f"⚠️  無法獲取任務結果: {e}")
        
        return results
    
    def shutdown(self):
        """關閉 Ray 集群"""
        if self.is_initialized:
            logger.info("🛑 關閉 Ray 集群...")
            ray.shutdown()
            self.is_initialized = False
            logger.info("✅ Ray 集群已關閉")


class RayAutonomousSystem:
    """Ray 自動執行系統 - 主控制類"""
    
    def __init__(self):
        self.executor = RayQuantumExecutor()
        self.execution_log = []
        logger.info("=" * 100)
        logger.info("🚀 初始化 Ray 自動執行系統")
        logger.info("=" * 100)
    
    def start(self) -> bool:
        """啟動系統"""
        if not self.executor.initialize_cluster():
            return False
        
        logger.info("\n✅ 系統已就緒")
        logger.info("\n【自動執行計畫】")
        logger.info("  1. 執行量子成本優化 (並行)")
        logger.info("  2. 執行系統監控 (並行)")
        logger.info("  3. 更新儀表板 (並行)")
        logger.info("  4. 收集結果")
        
        return True
    
    def run_all_tasks_parallel(self) -> Dict[str, Any]:
        """並行執行所有任務"""
        logger.info("\n【階段 1】提交所有任務到 Ray")
        logger.info("-" * 100)
        
        # 準備 token 成本
        token_costs = np.random.uniform(0.001, 0.01, 20).tolist()
        
        # 並行提交所有任務
        quantum_task_id = self.executor.submit_quantum_task(token_costs)
        monitoring_task_id = self.executor.submit_monitoring_task(duration=15)
        dashboard_task_id = self.executor.submit_dashboard_task()
        
        logger.info(f"\n✅ 所有任務已並行提交到 Ray")
        
        # 階段 2: 等待所有任務完成
        logger.info("\n【階段 2】等待並行任務完成")
        logger.info("-" * 100)
        
        quantum_result = self.executor.wait_for_task(quantum_task_id, timeout=60)
        monitoring_result = self.executor.wait_for_task(monitoring_task_id, timeout=30)
        dashboard_result = self.executor.wait_for_task(dashboard_task_id, timeout=30)
        
        # 階段 3: 彙總結果
        logger.info("\n【階段 3】彙總結果")
        logger.info("-" * 100)
        
        final_report = {
            "timestamp": datetime.now().isoformat(),
            "system_status": "success",
            "quantum_optimization": quantum_result,
            "system_monitoring": monitoring_result,
            "dashboard_update": dashboard_result
        }
        
        self._print_final_report(final_report)
        
        return final_report
    
    def _print_final_report(self, report: Dict[str, Any]):
        """打印最終報告"""
        logger.info("\n" + "=" * 100)
        logger.info("📊 Ray 自動執行最終報告")
        logger.info("=" * 100)
        
        # 量子優化結果
        if report.get("quantum_optimization"):
            qo = report["quantum_optimization"]
            if qo.get("success"):
                logger.info(f"\n✅ 量子優化:")
                logger.info(f"   Token 數: {qo.get('token_count')}")
                logger.info(f"   原始成本: {qo.get('original_cost'):.8f}")
                logger.info(f"   優化後: {qo.get('optimized_cost'):.8f}")
                logger.info(f"   節省: {qo.get('savings'):.8f}")
        
        # 監控結果
        if report.get("system_monitoring"):
            sm = report["system_monitoring"]
            logger.info(f"\n✅ 系統監控:")
            logger.info(f"   CPU 樣本數: {len(sm.get('cpu_samples', []))}")
            logger.info(f"   平均 CPU: {np.mean(sm.get('cpu_samples', [0])):.2f}%")
            logger.info(f"   平均內存: {np.mean(sm.get('memory_samples', [0])):.2f}%")
            logger.info(f"   檢測到的錯誤: {sm.get('error_count', 0)}")
        
        # 儀表板更新
        if report.get("dashboard_update"):
            du = report["dashboard_update"]
            logger.info(f"\n✅ 儀表板更新: {'成功' if du.get('success') else '失敗'}")
        
        logger.info("\n" + "=" * 100)
    
    def shutdown(self):
        """關閉系統"""
        logger.info("\n【系統關閉】")
        self.executor.shutdown()


def main():
    """主程序 - Ray 自動執行演示"""
    
    system = RayAutonomousSystem()
    
    try:
        # 啟動系統
        if not system.start():
            logger.error("❌ 系統啟動失敗")
            return
        
        # 執行所有任務 (自動並行)
        report = system.run_all_tasks_parallel()
        
        # 保存報告
        report_file = "/workspaces/cosmic-ai.uk/logs/ray_execution_report.json"
        os.makedirs(os.path.dirname(report_file), exist_ok=True)
        
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        logger.info(f"\n💾 報告已保存: {report_file}")
        
        logger.info("\n" + "=" * 100)
        logger.info("✅ Ray 自動執行系統完成!")
        logger.info("=" * 100)
        
    except Exception as e:
        logger.error(f"❌ 系統錯誤: {e}", exc_info=True)
    
    finally:
        system.shutdown()


if __name__ == "__main__":
    main()
