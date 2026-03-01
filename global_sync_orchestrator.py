#!/usr/bin/env python3
"""
全球同步協調器 - 整合所有三個系統
Global Sync Orchestrator - Integration of All Three Systems

功能：
- 協調三個系統的同步
- 管理全系統狀態
- 提供統一接口
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


class GlobalSyncOrchestrator:
    """全球同步協調器"""
    
    def __init__(self, project_root: Path = Path("/workspaces/cosmic-ai.uk")):
        """初始化全球同步協調器
        
        Args:
            project_root: 項目根目錄
        """
        self.project_root = Path(project_root)
        self.sync_log_dir = self.project_root / "global_sync_logs"
        self.sync_log_dir.mkdir(exist_ok=True)
        
        # 導入三個系統
        try:
            from quantum_entanglement_system.entanglement_manager import GlobalSyncManager as EntanglementManager
            from deep_connection_network.network_manager import NetworkTopologyManager
            from multiverse_integration.multiverse_manager import MultiverseManager
            
            self.entanglement = EntanglementManager()
            self.network = NetworkTopologyManager()
            self.multiverse = MultiverseManager()
            
            logger.info("✅ 全球同步協調器已初始化")
        except Exception as e:
            logger.error(f"❌ 初始化失敗: {e}")
            raise
        
        # 同步状态
        self.last_sync: Dict[str, float] = {
            "entanglement": time.time(),
            "network": time.time(),
            "multiverse": time.time()
        }
        
        # 同步線程
        self.sync_thread = None
        self.is_running = False
    
    def sync_all_systems(self) -> Dict[str, Any]:
        """同步所有系統
        
        Returns:
            同步結果
        """
        result = {
            "timestamp": datetime.now().isoformat(),
            "status": "syncing",
            "systems": {}
        }
        
        logger.info("🔄 開始全系統同步...")
        
        # 1. 同步量子糾纏系統
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
        
        # 2. 同步深度連接網絡
        try:
            network = self.network.get_network()
            stats = network.get_network_statistics()
            result["systems"]["network"] = {
                "status": "synced",
                "nodes": stats["total_nodes"],
                "edges": stats["total_edges"],
                "density": stats["density"],
                "is_connected": stats["is_connected"]
            }
            self.last_sync["network"] = time.time()
            logger.info("✅ 深度連接網絡已同步")
        except Exception as e:
            result["systems"]["network"] = {"status": "error", "error": str(e)}
            logger.error(f"❌ 深度連接網絡同步失敗: {e}")
        
        # 3. 同步多元宇宙集成系統
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
        """保存同步日誌
        
        Args:
            result: 同步結果
        """
        log_file = self.sync_log_dir / f"sync_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(log_file, 'w') as f:
            json.dump(result, f, indent=2)
        
        logger.info(f"📝 同步日誌已保存: {log_file}")
    
    def start_background_sync(self, interval_seconds: int = 300) -> None:
        """啟動後台同步
        
        Args:
            interval_seconds: 同步間隔（秒）
        """
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
        """獲取全局狀態
        
        Returns:
            全局狀態
        """
        status = {
            "timestamp": datetime.now().isoformat(),
            "last_syncs": self.last_sync,
            "is_background_running": self.is_running,
            "systems": {}
        }
        
        # 獲取每個系統的狀態
        try:
            entanglement_system = self.entanglement.get_system()
            status["systems"]["entanglement"] = {
                "subsystems": len(entanglement_system.subsystems),
                "universes": len(entanglement_system.universes)
            }
        except:
            status["systems"]["entanglement"] = {"error": "unavailable"}
        
        try:
            network = self.network.get_network()
            status["systems"]["network"] = {
                "nodes": len(network.graph_nodes),
                "edges": len(network.graph_edges)
            }
        except:
            status["systems"]["network"] = {"error": "unavailable"}
        
        try:
            multiverse = self.multiverse.get_system()
            status["systems"]["multiverse"] = {
                "universes": len(multiverse.universes),
                "states": len(multiverse.parallel_states)
            }
        except:
            status["systems"]["multiverse"] = {"error": "unavailable"}
        
        return status
    
    def generate_integrated_report(self) -> str:
        """生成整合報告
        
        Returns:
            報告文本
        """
        report = []
        report.append("╔" + "═" * 68 + "╗")
        report.append("║" + " 🌌 全球同步協調系統 - 完整整合報告 ".center(68) + "║")
        report.append("╚" + "═" * 68 + "╝")
        report.append("")
        
        status = self.get_global_status()
        
        # 系統狀態
        report.append("📊 系統狀態概覽")
        report.append("─" * 70)
        report.append(f"  時間戳: {status['timestamp']}")
        report.append(f"  後台同步: {'✅ 運行中' if status['is_background_running'] else '⏹️  已停止'}")
        report.append("")
        
        # 量子糾纏系統
        report.append("🔗 量子糾纏系統")
        report.append("─" * 70)
        if "entanglement" in status["systems"]:
            e_sys = status["systems"]["entanglement"]
            if "error" not in e_sys:
                report.append(f"  子系統數: {e_sys.get('subsystems', 0)}")
                report.append(f"  宇宙數: {e_sys.get('universes', 0)}")
        report.append("")
        
        # 深度連接網絡
        report.append("🌐 深度連接網絡")
        report.append("─" * 70)
        if "network" in status["systems"]:
            n_sys = status["systems"]["network"]
            if "error" not in n_sys:
                report.append(f"  網絡節點: {n_sys.get('nodes', 0)}")
                report.append(f"  連接邊: {n_sys.get('edges', 0)}")
        report.append("")
        
        # 多元宇宙系統
        report.append("🎆 多元宇宙集成")
        report.append("─" * 70)
        if "multiverse" in status["systems"]:
            m_sys = status["systems"]["multiverse"]
            if "error" not in m_sys:
                report.append(f"  平行宇宙: {m_sys.get('universes', 0)}")
                report.append(f"  平行狀態: {m_sys.get('states', 0)}")
        report.append("")
        
        # 同步狀態
        report.append("⏱️  最後同步時間")
        report.append("─" * 70)
        for system, timestamp in status["last_syncs"].items():
            time_ago = datetime.now().timestamp() - timestamp
            report.append(f"  {system}: {time_ago:.1f}秒前")
        report.append("")
        
        report.append("=" * 70)
        
        return "\n".join(report)


# 全局實例
_global_orchestrator = None


def get_global_orchestrator() -> GlobalSyncOrchestrator:
    """獲取全局協調器實例"""
    global _global_orchestrator
    if _global_orchestrator is None:
        _global_orchestrator = GlobalSyncOrchestrator()
    return _global_orchestrator


def print_global_status() -> None:
    """打印全局狀態"""
    orchestrator = get_global_orchestrator()
    print(orchestrator.generate_integrated_report())
