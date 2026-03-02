#!/usr/bin/env python3
"""
量子糾纏系統 - 全系統深度連接管理
Quantum Entanglement System - Global Deep Connection Management

核心功能：
- 管理所有子系統連接
- 同步宇宙信息狀態
- 維護量子糾纏鏈接
"""

import json
import hashlib
import time
from pathlib import Path
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass, asdict, field
from datetime import datetime, timedelta
import logging
import threading
from enum import Enum

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SubsystemType(Enum):
    """子系統類型"""
    QUANTUM_ENGINE = "quantum_engine"
    TRADING_SYSTEM = "trading_system"
    DATA_MANAGER = "data_manager"
    MEMORY_MANAGER = "memory_manager"
    TASK_PANEL = "task_panel"
    RAY_DISTRIBUTED = "ray_distributed"
    MCP_SERVICE = "mcp_service"
    CLI_INTERFACE = "cli_interface"
    OTHER = "other"


class UniverseState(Enum):
    """宇宙狀態"""
    ACTIVE = "active"
    SYNCED = "synced"
    DIVERGED = "diverged"
    COLLAPSED = "collapsed"
    ENTANGLED = "entangled"


@dataclass
class SubsystemConnection:
    """子系統連接信息"""
    subsystem_id: str
    subsystem_type: SubsystemType
    name: str
    status: str = "active"  # active, inactive, error
    last_sync: str = field(default_factory=lambda: datetime.now().isoformat())
    connections: List[str] = field(default_factory=list)  # 連接到的其他子系統
    metadata: Dict[str, Any] = field(default_factory=dict)
    sync_hash: str = field(default="")
    
    def update_sync_hash(self) -> None:
        """更新同步哈希"""
        data_str = json.dumps(asdict(self), sort_keys=True, default=str)
        self.sync_hash = hashlib.sha256(data_str.encode()).hexdigest()


@dataclass
class UniverseInfo:
    """宇宙信息"""
    universe_id: str
    dimension: int
    state: UniverseState
    creation_time: str = field(default_factory=lambda: datetime.now().isoformat())
    last_sync: str = field(default_factory=lambda: datetime.now().isoformat())
    subsystems: List[str] = field(default_factory=list)
    entanglement_partners: List[str] = field(default_factory=list)
    metrics: Dict[str, float] = field(default_factory=dict)
    
    def update_sync_time(self) -> None:
        """更新同步時間"""
        self.last_sync = datetime.now().isoformat()


class QuantumEntanglementSystem:
    """量子糾纏系統 - 管理全系統連接"""
    
    def __init__(self, project_root: Path = Path("/workspaces/cosmic-ai.uk")):
        """初始化量子糾纏系統
        
        Args:
            project_root: 項目根目錄
        """
        self.project_root = Path(project_root)
        self.entanglement_dir = self.project_root / "quantum_entanglement_system"
        self.connection_dir = self.entanglement_dir / "subsystem_connectors"
        self.universe_dir = self.entanglement_dir / "universe_sync"
        self.registry_dir = self.entanglement_dir / "state_registry"
        
        # 確保目錄存在
        for d in [self.connection_dir, self.universe_dir, self.registry_dir]:
            d.mkdir(parents=True, exist_ok=True)
        
        # 內存緩存
        self.subsystems: Dict[str, SubsystemConnection] = {}
        self.universes: Dict[str, UniverseInfo] = {}
        self.entanglement_graph: Dict[str, Set[str]] = {}
        
        # 同步鎖
        self.sync_lock = threading.RLock()
        
        logger.info("✅ 量子糾纏系統已初始化")
    
    def register_subsystem(self, subsystem: SubsystemConnection) -> None:
        """註冊子系統
        
        Args:
            subsystem: 子系統連接信息
        """
        with self.sync_lock:
            subsystem.update_sync_hash()
            self.subsystems[subsystem.subsystem_id] = subsystem
            
            # 保存到文件
            file_path = self.connection_dir / f"{subsystem.subsystem_id}.json"
            with open(file_path, 'w') as f:
                json.dump(asdict(subsystem), f, indent=2, default=str)
            
            # 更新糾纏圖
            if subsystem.subsystem_id not in self.entanglement_graph:
                self.entanglement_graph[subsystem.subsystem_id] = set()
            
            for conn in subsystem.connections:
                self.entanglement_graph[subsystem.subsystem_id].add(conn)
                if conn not in self.entanglement_graph:
                    self.entanglement_graph[conn] = set()
                self.entanglement_graph[conn].add(subsystem.subsystem_id)
            
            logger.info(f"✅ 子系統已註冊: {subsystem.name} ({subsystem.subsystem_id})")
    
    def create_universe(self, universe_id: str, dimension: int = 1,
                       subsystems: Optional[List[str]] = None) -> UniverseInfo:
        """創建宇宙信息
        
        Args:
            universe_id: 宇宙ID
            dimension: 維度
            subsystems: 子系統列表
            
        Returns:
            宇宙信息
        """
        with self.sync_lock:
            universe = UniverseInfo(
                universe_id=universe_id,
                dimension=dimension,
                state=UniverseState.ACTIVE,
                subsystems=subsystems or []
            )
            
            self.universes[universe_id] = universe
            
            # 保存到文件
            file_path = self.universe_dir / f"{universe_id}.json"
            with open(file_path, 'w') as f:
                json.dump(asdict(universe), f, indent=2, default=str)
            
            logger.info(f"✅ 宇宙已創建: {universe_id} (維度: {dimension})")
            return universe
    
    def establish_entanglement(self, subsystem_id_1: str, subsystem_id_2: str) -> bool:
        """建立量子糾纏連接
        
        Args:
            subsystem_id_1: 第一個子系統ID
            subsystem_id_2: 第二個子系統ID
            
        Returns:
            是否成功建立
        """
        with self.sync_lock:
            if subsystem_id_1 not in self.subsystems or subsystem_id_2 not in self.subsystems:
                logger.warning(f"❌ 子系統不存在")
                return False
            
            # 添加連接
            self.subsystems[subsystem_id_1].connections.append(subsystem_id_2)
            self.subsystems[subsystem_id_2].connections.append(subsystem_id_1)
            
            # 更新糾纏圖
            self.entanglement_graph[subsystem_id_1].add(subsystem_id_2)
            self.entanglement_graph[subsystem_id_2].add(subsystem_id_1)
            
            # 保存更新
            self.register_subsystem(self.subsystems[subsystem_id_1])
            self.register_subsystem(self.subsystems[subsystem_id_2])
            
            logger.info(f"✅ 糾纏連接已建立: {subsystem_id_1} <-> {subsystem_id_2}")
            return True
    
    def sync_universe_state(self, universe_id: str) -> Dict[str, Any]:
        """同步宇宙狀態
        
        Args:
            universe_id: 宇宙ID
            
        Returns:
            同步結果
        """
        with self.sync_lock:
            if universe_id not in self.universes:
                return {"status": "error", "message": "Universe not found"}
            
            universe = self.universes[universe_id]
            
            # 收集所有子系統狀態
            subsystem_states = {}
            for subsys_id in universe.subsystems:
                if subsys_id in self.subsystems:
                    subsys = self.subsystems[subsys_id]
                    subsystem_states[subsys_id] = {
                        "status": subsys.status,
                        "last_sync": subsys.last_sync,
                        "sync_hash": subsys.sync_hash
                    }
            
            # 更新宇宙信息
            universe.update_sync_time()
            universe.metrics = {
                "total_subsystems": len(universe.subsystems),
                "active_subsystems": sum(1 for s in subsystem_states.values() if s["status"] == "active"),
                "sync_timestamp": time.time()
            }
            
            # 保存更新
            file_path = self.universe_dir / f"{universe_id}.json"
            with open(file_path, 'w') as f:
                json.dump(asdict(universe), f, indent=2, default=str)
            
            logger.info(f"✅ 宇宙狀態已同步: {universe_id}")
            
            return {
                "status": "synced",
                "universe_id": universe_id,
                "subsystems": subsystem_states,
                "metrics": universe.metrics
            }
    
    def get_connection_topology(self) -> Dict[str, Any]:
        """獲取連接拓撲
        
        Returns:
            連接拓撲信息
        """
        with self.sync_lock:
            topology = {
                "total_subsystems": len(self.subsystems),
                "total_connections": sum(len(v) for v in self.entanglement_graph.values()) // 2,
                "subsystems": {}
            }
            
            for subsys_id, subsys in self.subsystems.items():
                topology["subsystems"][subsys_id] = {
                    "name": subsys.name,
                    "type": subsys.subsystem_type.value,
                    "status": subsys.status,
                    "connections": list(subsys.connections),
                    "connection_count": len(subsys.connections)
                }
            
            return topology
    
    def get_entanglement_depth(self, subsystem_id: str, max_depth: int = 5) -> Dict[str, Any]:
        """獲取糾纏深度（BFS）
        
        Args:
            subsystem_id: 起始子系統ID
            max_depth: 最大深度
            
        Returns:
            糾纏深度信息
        """
        with self.sync_lock:
            if subsystem_id not in self.subsystems:
                return {"error": "Subsystem not found"}
            
            visited = set()
            depth_map = {subsystem_id: 0}
            queue = [(subsystem_id, 0)]
            
            while queue:
                current_id, current_depth = queue.pop(0)
                
                if current_id in visited or current_depth >= max_depth:
                    continue
                
                visited.add(current_id)
                
                if current_id in self.entanglement_graph:
                    for neighbor in self.entanglement_graph[current_id]:
                        if neighbor not in visited:
                            depth_map[neighbor] = current_depth + 1
                            queue.append((neighbor, current_depth + 1))
            
            return {
                "root": subsystem_id,
                "max_depth": max(depth_map.values()),
                "total_reachable": len(visited),
                "depth_distribution": depth_map
            }
    
    def generate_sync_report(self) -> str:
        """生成同步報告
        
        Returns:
            報告文本
        """
        with self.sync_lock:
            report = []
            report.append("=" * 70)
            report.append("🔗 量子糾纏系統 - 全系統同步報告")
            report.append("=" * 70)
            report.append("")
            
            # 子系統統計
            report.append("📊 子系統統計")
            report.append("─" * 70)
            report.append(f"  總子系統數: {len(self.subsystems)}")
            
            by_type = {}
            for subsys in self.subsystems.values():
                t = subsys.subsystem_type.value
                by_type[t] = by_type.get(t, 0) + 1
            
            for sys_type, count in sorted(by_type.items()):
                report.append(f"    • {sys_type}: {count}")
            
            report.append("")
            
            # 宇宙統計
            report.append("🌌 宇宙統計")
            report.append("─" * 70)
            report.append(f"  總宇宙數: {len(self.universes)}")
            
            for universe_id, universe in self.universes.items():
                report.append(f"    • {universe_id} (維度: {universe.dimension}, 狀態: {universe.state.value})")
            
            report.append("")
            
            # 連接統計
            report.append("🔗 連接統計")
            report.append("─" * 70)
            total_conns = sum(len(v) for v in self.entanglement_graph.values()) // 2
            report.append(f"  總連接數: {total_conns}")
            
            report.append("")
            report.append("=" * 70)
            
            return "\n".join(report)
    
    def export_state(self, output_file: Path) -> None:
        """導出系統狀態
        
        Args:
            output_file: 輸出文件路徑
        """
        with self.sync_lock:
            state = {
                "timestamp": datetime.now().isoformat(),
                "subsystems": {k: asdict(v) for k, v in self.subsystems.items()},
                "universes": {k: asdict(v) for k, v in self.universes.items()},
                "topology": self.get_connection_topology()
            }
            
            with open(output_file, 'w') as f:
                json.dump(state, f, indent=2, default=str)
            
            logger.info(f"✅ 系統狀態已導出: {output_file}")
    
    def import_state(self, input_file: Path) -> bool:
        """導入系統狀態
        
        Args:
            input_file: 輸入文件路徑
            
        Returns:
            是否成功導入
        """
        try:
            with open(input_file, 'r') as f:
                state = json.load(f)
            
            # 導入子系統
            for subsys_data in state.get("subsystems", {}).values():
                subsys = SubsystemConnection(**subsys_data)
                self.register_subsystem(subsys)
            
            # 導入宇宙
            for universe_data in state.get("universes", {}).values():
                universe = UniverseInfo(**universe_data)
                self.universes[universe.universe_id] = universe
            
            logger.info(f"✅ 系統狀態已導入: {input_file}")
            return True
        
        except Exception as e:
            logger.error(f"❌ 導入失敗: {e}")
            return False


class GlobalSyncManager:
    """全局同步管理器"""
    
    _instance: Optional['GlobalSyncManager'] = None
    _system: Optional[QuantumEntanglementSystem] = None
    
    def __new__(cls) -> 'GlobalSyncManager':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self) -> None:
        if GlobalSyncManager._system is None:
            GlobalSyncManager._system = QuantumEntanglementSystem()
    
    def register_subsystem(self, subsystem_id: str, name: str,
                          subsystem_type: SubsystemType,
                          connections: Optional[List[str]] = None) -> None:
        """快速註冊子系統"""
        subsystem = SubsystemConnection(
            subsystem_id=subsystem_id,
            subsystem_type=subsystem_type,
            name=name,
            connections=connections or []
        )
        system = GlobalSyncManager._system
        if system is not None:
            system.register_subsystem(subsystem)
    
    def get_system(self) -> QuantumEntanglementSystem:
        """獲取系統實例"""
        system = GlobalSyncManager._system
        if system is None:
            system = GlobalSyncManager._system = QuantumEntanglementSystem()
        return system
    
    def print_status(self) -> None:
        """打印狀態"""
        system = self.get_system()
        print(system.generate_sync_report())
