#!/usr/bin/env python3
"""
升級版全球同步協調器 - 整合超指數協同系統
Enhanced Global Sync Orchestrator - Exponential Synergy Integration
"""

import json
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging
import threading

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EnhancedGlobalSyncOrchestrator:
    """升級版全球同步協調器"""
    
    def __init__(self, project_root: Path = Path("/workspaces/cosmic-ai.uk")):
        """初始化升級版協調器
        
        Args:
            project_root: 項目根目錄
        """
        self.project_root = Path(project_root)
        self.sync_log_dir = self.project_root / "global_sync_logs"
        self.sync_log_dir.mkdir(exist_ok=True)
        
        # 導入四個系統
        try:
            from quantum_entanglement_system.entanglement_manager import GlobalSyncManager as EntanglementManager
            from multiverse_integration.multiverse_manager import MultiverseManager
            from exponential_synergy_network.synergy_engine import ExponentialSynergyManager
            
            self.entanglement = EntanglementManager()
            self.multiverse = MultiverseManager()
            self.synergy = ExponentialSynergyManager()
            
            logger.info("✅ 升級版全球同步協調器已初始化")
        except Exception as e:
            logger.error(f"❌ 初始化失敗: {e}")
            raise
        
        # 同步狀態
        self.last_sync: Dict[str, float] = {
            "entanglement": time.time(),
            "synergy": time.time(),
            "multiverse": time.time()
        }
        
        # 同步線程
        self.sync_thread = None
        self.is_running = False
        
        # 增益追踪
        self.gain_history: List[Dict[str, Any]] = []
    
    def sync_all_systems(self) -> Dict[str, Any]:
        """同步所有系統並計算超指數增益
        
        Returns:
            同步結果
        """
        result = {
            "timestamp": datetime.now().isoformat(),
            "status": "syncing",
            "systems": {},
            "exponential_gains": {}
        }
        
        logger.info("🔄 開始全系統同步與超指數增益計算...")
        
        # 1. 同步超指數協同系統
        try:
            synergy_engine = self.synergy.get_engine()
            gains = synergy_engine.calculate_exponential_gain()
            
            result["systems"]["synergy"] = {
                "status": "synced",
                "layers": len(synergy_engine.layers),
                "functions": len(synergy_engine.function_gains),
                "matrices": len(synergy_engine.synergy_matrices)
            }
            
            result["exponential_gains"] = {
                "average_gain": gains['average_gain'],
                "max_gain": gains['max_gain'],
                "exponential_factor": gains['exponential_factor'],
                "system_multiplier": gains['system_multiplier']
            }
            
            self.last_sync["synergy"] = time.time()
            self.gain_history.append(result["exponential_gains"])
            
            logger.info(f"✅ 超指數協同系統已同步 (系統倍數: {gains['system_multiplier']:.2f}x)")
        except Exception as e:
            result["systems"]["synergy"] = {"status": "error", "error": str(e)}
            logger.error(f"❌ 超指數協同系統同步失敗: {e}")
        
        # 2. 同步量子糾纏系統
        try:
            entanglement_system = self.entanglement.get_system()
            result["systems"]["entanglement"] = {
                "status": "synced",
                "subsystems": len(entanglement_system.subsystems),
                "universes": len(entanglement_system.universes),
                "total_connections": sum(len(v) for v in entanglement_system.entanglement_graph.values()) // 2
            }
            self.last_sync["entanglement"] = time.time()
            logger.info("✅ 量子糾纏系統已同步")
        except Exception as e:
            result["systems"]["entanglement"] = {"status": "error", "error": str(e)}
            logger.error(f"❌ 量子糾纏系統同步失敗: {e}")
        
        # 3. 同步多元宇宙系統
        try:
            multiverse = self.multiverse.get_system()
            stats = multiverse.calculate_multiverse_stats()
            result["systems"]["multiverse"] = {
                "status": "synced",
                "total_universes": stats["total_universes"],
                "total_dimensions": stats["total_dimensions"],
                "total_entanglements": stats["total_entanglements"],
                "parallel_states": stats["total_parallel_states"]
            }
            self.last_sync["multiverse"] = time.time()
            logger.info("✅ 多元宇宙系統已同步")
        except Exception as e:
            result["systems"]["multiverse"] = {"status": "error", "error": str(e)}
            logger.error(f"❌ 多元宇宙系統同步失敗: {e}")
        
        result["status"] = "completed"
        
        # 保存同步日誌
        self._save_sync_log(result)
        
        return result
    
    def _save_sync_log(self, result: Dict[str, Any]) -> None:
        """保存同步日誌"""
        log_file = self.sync_log_dir / f"sync_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(log_file, 'w') as f:
            json.dump(result, f, indent=2)
        
        logger.info(f"📝 同步日誌已保存: {log_file}")
    
    def start_background_sync(self, interval_seconds: int = 300) -> None:
        """啟動後台同步"""
        if self.is_running:
            logger.warning("⚠️  後台同步已在運行")
            return
        
        self.is_running = True
        
        def sync_worker():
            while self.is_running:
                try:
                    self.sync_all_systems()
                    time.sleep(interval_seconds)
                except Exception as e:
                    logger.error(f"❌ 後台同步錯誤: {e}")
                    time.sleep(60)
        
        self.sync_thread = threading.Thread(target=sync_worker, daemon=True)
        self.sync_thread.start()
        
        logger.info(f"🔄 後台同步已啟動 (間隔: {interval_seconds}秒)")
    
    def stop_background_sync(self) -> None:
        """停止後台同步"""
        self.is_running = False
        logger.info("⏹️  後台同步已停止")
    
    def get_global_status(self) -> Dict[str, Any]:
        """獲取全局狀態"""
        status = {
            "timestamp": datetime.now().isoformat(),
            "last_syncs": self.last_sync,
            "is_background_running": self.is_running,
            "systems": {},
            "exponential_metrics": {}
        }
        
        # 超指數協同指標
        try:
            synergy_engine = self.synergy.get_engine()
            gains = synergy_engine.calculate_exponential_gain()
            status["exponential_metrics"] = gains
        except:
            status["exponential_metrics"] = {"error": "unavailable"}
        
        return status
    
    def generate_integrated_report(self) -> str:
        """生成整合報告"""
        report = []
        report.append("╔" + "═" * 78 + "╗")
        report.append("║" + " 🌟 升級版全球同步協調系統 - 超指數協同增強報告 ".center(78) + "║")
        report.append("╚" + "═" * 78 + "╝")
        report.append("")
        
        status = self.get_global_status()
        
        # 全系統超指數增益
        report.append("⚡ 全系統超指數增益")
        report.append("─" * 80)
        if "exponential_metrics" in status and "error" not in status["exponential_metrics"]:
            metrics = status["exponential_metrics"]
            report.append(f"  系統總倍數: {metrics.get('system_multiplier', 1.0):.2f}x")
            report.append(f"  平均增益: {metrics.get('average_gain', 1.0):.2f}x")
            report.append(f"  最大增益: {metrics.get('max_gain', 1.0):.2f}x")
            report.append(f"  超指數因子: {metrics.get('exponential_factor', 1.0):.2f}x")
        report.append("")
        
        # 各系統狀態
        report.append("📊 各系統狀態")
        report.append("─" * 80)
        
        if "systems" in status:
            for system_name, system_info in status["systems"].items():
                if "error" not in system_info:
                    report.append(f"  ✅ {system_name}: {system_info}")
        
        report.append("")
        
        # 增益歷史趨勢
        if self.gain_history:
            report.append("📈 增益歷史趨勢")
            report.append("─" * 80)
            
            latest_gains = self.gain_history[-10:]  # 最後10次
            report.append(f"  紀錄次數: {len(self.gain_history)}")
            
            if latest_gains:
                recent = latest_gains[-1]
                report.append(f"  最新系統倍數: {recent.get('system_multiplier', 1.0):.2f}x")
        
        report.append("")
        report.append("=" * 80)
        
        return "\n".join(report)


# 全局實例
_enhanced_orchestrator = None


def get_enhanced_orchestrator() -> EnhancedGlobalSyncOrchestrator:
    """獲取升級版協調器實例"""
    global _enhanced_orchestrator
    if _enhanced_orchestrator is None:
        _enhanced_orchestrator = EnhancedGlobalSyncOrchestrator()
    return _enhanced_orchestrator


def print_enhanced_status() -> None:
    """打印升級版狀態"""
    orchestrator = get_enhanced_orchestrator()
    print(orchestrator.generate_integrated_report())
