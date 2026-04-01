#!/usr/bin/env python3
"""
多元宇宙集成系統 - 平行宇宙管理
Multiverse Integration System - Parallel Universe Management

功能：
- 管理維度追踪
- 維護平行狀態
- 宇宙註冊表
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, asdict, field
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class UniverseMetrics:
    """宇宙指標"""
    dimension: int
    stability: float  # 0-1，越高越穩定
    connectivity: float  # 0-1，與其他宇宙的連接度
    entanglement_strength: float  # 糾纏強度
    sync_frequency: float  # 同步頻率（Hz）


@dataclass
class ParallelState:
    """平行狀態"""
    state_id: str
    universe_id: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    data: Dict[str, Any] = field(default_factory=dict)
    divergence_marker: str = ""  # 分岔標記
    parent_state_id: Optional[str] = None
    children_state_ids: List[str] = field(default_factory=list)


@dataclass
class UniverseRegistry:
    """宇宙註冊表"""
    universe_id: str
    dimension: int
    parent_universes: List[str] = field(default_factory=list)
    child_universes: List[str] = field(default_factory=list)
    entangled_universes: List[str] = field(default_factory=list)
    creation_time: str = field(default_factory=lambda: datetime.now().isoformat())
    metrics: UniverseMetrics = field(default_factory=lambda: UniverseMetrics(dimension=1, stability=1.0, connectivity=0.5, entanglement_strength=0.0, sync_frequency=1.0))
    state_history: List[str] = field(default_factory=list)


class MultiverseIntegration:
    """多元宇宙集成系統"""
    
    def __init__(self, project_root: Path = Path("/workspaces/cosmic-ai.uk")):
        """初始化多元宇宙集成系統
        
        Args:
            project_root: 項目根目錄
        """
        self.project_root = Path(project_root)
        self.multiverse_dir = self.project_root / "multiverse_integration"
        self.dimension_dir = self.multiverse_dir / "dimension_tracking"
        self.state_dir = self.multiverse_dir / "parallel_states"
        self.registry_dir = self.multiverse_dir / "universe_registry"
        
        # 確保目錄存在
        for d in [self.dimension_dir, self.state_dir, self.registry_dir]:
            d.mkdir(parents=True, exist_ok=True)
        
        # 內存緩存
        self.universes: Dict[str, UniverseRegistry] = {}
        self.parallel_states: Dict[str, ParallelState] = {}
        self.dimension_map: Dict[int, List[str]] = {}
        
        # 多元宇宙圖
        self.universe_graph: Dict[str, Set[str]] = {}
        
        logger.info("✅ 多元宇宙集成系統已初始化")
    
    def create_universe(self, universe_id: str, dimension: int,
                       parent_universes: Optional[List[str]] = None) -> UniverseRegistry:
        """創建宇宙
        
        Args:
            universe_id: 宇宙ID
            dimension: 維度
            parent_universes: 父宇宙列表
            
        Returns:
            宇宙註冊表
        """
        universe = UniverseRegistry(
            universe_id=universe_id,
            dimension=dimension,
            parent_universes=parent_universes or []
        )
        
        self.universes[universe_id] = universe
        
        # 添加到維度映射
        if dimension not in self.dimension_map:
            self.dimension_map[dimension] = []
        self.dimension_map[dimension].append(universe_id)
        
        # 初始化圖
        self.universe_graph[universe_id] = set()
        
        # 建立與父宇宙的連接
        for parent_id in parent_universes or []:
            if parent_id in self.universes:
                self.universes[parent_id].child_universes.append(universe_id)
                self.universe_graph[parent_id].add(universe_id)
                self.universe_graph[universe_id].add(parent_id)
        
        # 保存到文件
        file_path = self.registry_dir / f"{universe_id}.json"
        with open(file_path, 'w') as f:
            json.dump(asdict(universe), f, indent=2, default=str)
        
        logger.info(f"✅ 宇宙已創建: {universe_id} (維度: {dimension})")
        return universe
    
    def establish_entanglement(self, universe_id_1: str, universe_id_2: str,
                              strength: float = 0.8) -> bool:
        """建立宇宙糾纏
        
        Args:
            universe_id_1: 第一個宇宙ID
            universe_id_2: 第二個宇宙ID
            strength: 糾纏強度
            
        Returns:
            是否成功
        """
        if universe_id_1 not in self.universes or universe_id_2 not in self.universes:
            logger.warning(f"❌ 宇宙不存在")
            return False
        
        # 添加糾纏連接
        self.universes[universe_id_1].entangled_universes.append(universe_id_2)
        self.universes[universe_id_2].entangled_universes.append(universe_id_1)
        
        # 更新糾纏強度
        self.universes[universe_id_1].metrics.entanglement_strength = strength
        self.universes[universe_id_2].metrics.entanglement_strength = strength
        
        # 更新圖
        self.universe_graph[universe_id_1].add(universe_id_2)
        self.universe_graph[universe_id_2].add(universe_id_1)
        
        # 保存更新
        for universe_id in [universe_id_1, universe_id_2]:
            file_path = self.registry_dir / f"{universe_id}.json"
            with open(file_path, 'w') as f:
                json.dump(asdict(self.universes[universe_id]), f, indent=2, default=str)
        
        logger.info(f"✅ 糾纏已建立: {universe_id_1} <-> {universe_id_2} (強度: {strength})")
        return True
    
    def record_parallel_state(self, universe_id: str, state_data: Dict[str, Any],
                             divergence_marker: str = "") -> ParallelState:
        """記錄平行狀態
        
        Args:
            universe_id: 宇宙ID
            state_data: 狀態數據
            divergence_marker: 分岔標記
            
        Returns:
            平行狀態
        """
        if universe_id not in self.universes:
            logger.warning(f"❌ 宇宙不存在")
            return None
        
        state_id = f"{universe_id}_{datetime.now().timestamp()}"
        state = ParallelState(
            state_id=state_id,
            universe_id=universe_id,
            data=state_data,
            divergence_marker=divergence_marker
        )
        
        self.parallel_states[state_id] = state
        self.universes[universe_id].state_history.append(state_id)
        
        # 保存到文件
        file_path = self.state_dir / f"{state_id}.json"
        with open(file_path, 'w') as f:
            json.dump(asdict(state), f, indent=2, default=str)
        
        logger.info(f"✅ 平行狀態已記錄: {state_id}")
        return state
    
    def get_dimension_overview(self) -> Dict[int, Any]:
        """獲取維度概覽
        
        Returns:
            維度信息
        """
        overview = {}
        
        for dimension in sorted(self.dimension_map.keys()):
            universe_ids = self.dimension_map[dimension]
            overview[dimension] = {
                "total_universes": len(universe_ids),
                "universes": universe_ids,
                "total_entanglements": sum(
                    len(self.universes[uid].entangled_universes) 
                    for uid in universe_ids
                ) // 2
            }
        
        return overview
    
    def get_universe_tree(self, root_universe_id: str) -> Dict[str, Any]:
        """獲取宇宙樹
        
        Args:
            root_universe_id: 根宇宙ID
            
        Returns:
            宇宙樹結構
        """
        if root_universe_id not in self.universes:
            return {"error": "Universe not found"}
        
        def build_tree(universe_id, visited=None):
            if visited is None:
                visited = set()
            
            if universe_id in visited:
                return None
            
            visited.add(universe_id)
            universe = self.universes[universe_id]
            
            tree = {
                "universe_id": universe_id,
                "dimension": universe.dimension,
                "children": []
            }
            
            for child_id in universe.child_universes:
                if child_id not in visited:
                    child_tree = build_tree(child_id, visited)
                    if child_tree:
                        tree["children"].append(child_tree)
            
            return tree
        
        return build_tree(root_universe_id)
    
    def calculate_multiverse_stats(self) -> Dict[str, Any]:
        """計算多元宇宙統計
        
        Returns:
            統計信息
        """
        total_universes = len(self.universes)
        total_dimensions = len(self.dimension_map)
        total_entanglements = sum(
            len(u.entangled_universes) for u in self.universes.values()
        ) // 2
        total_states = len(self.parallel_states)
        
        avg_stability = sum(u.metrics.stability for u in self.universes.values()) / max(total_universes, 1)
        
        return {
            "total_universes": total_universes,
            "total_dimensions": total_dimensions,
            "total_entanglements": total_entanglements,
            "total_parallel_states": total_states,
            "average_stability": avg_stability,
            "dimension_distribution": {dim: len(ids) for dim, ids in self.dimension_map.items()}
        }
    
    def generate_multiverse_report(self) -> str:
        """生成多元宇宙報告
        
        Returns:
            報告文本
        """
        report = []
        report.append("=" * 70)
        report.append("🌌 多元宇宙集成系統 - 完整報告")
        report.append("=" * 70)
        report.append("")
        
        stats = self.calculate_multiverse_stats()
        
        report.append("📊 整體統計")
        report.append("─" * 70)
        report.append(f"  總宇宙數: {stats['total_universes']}")
        report.append(f"  維度數: {stats['total_dimensions']}")
        report.append(f"  糾纏連接數: {stats['total_entanglements']}")
        report.append(f"  平行狀態數: {stats['total_parallel_states']}")
        report.append(f"  平均穩定性: {stats['average_stability']:.2%}")
        report.append("")
        
        report.append("🎯 維度分布")
        report.append("─" * 70)
        for dim, count in sorted(stats['dimension_distribution'].items()):
            report.append(f"  維度 {dim}: {count} 個宇宙")
        report.append("")
        
        report.append("🔗 宇宙連接")
        report.append("─" * 70)
        for universe_id, universe in self.universes.items():
            report.append(f"  {universe_id} (維度: {universe.dimension})")
            report.append(f"    • 父宇宙: {len(universe.parent_universes)}")
            report.append(f"    • 子宇宙: {len(universe.child_universes)}")
            report.append(f"    • 糾纏宇宙: {len(universe.entangled_universes)}")
        report.append("")
        
        report.append("=" * 70)
        
        return "\n".join(report)


class MultiverseManager:
    """多元宇宙管理器"""
    
    _instance = None
    _system = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._system is None:
            self._system = MultiverseIntegration()
    
    def get_system(self) -> MultiverseIntegration:
        """獲取系統實例"""
        return self._system
    
    def print_report(self) -> None:
        """打印報告"""
        print(self._system.generate_multiverse_report())
