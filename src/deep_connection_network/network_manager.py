#!/usr/bin/env python3
"""
深度連接網絡 - 全系統拓撲管理
Deep Connection Network - System Topology Management

功能：
- 管理節點映射
- 維護拓撲索引
- 路由表管理
"""

import json
from pathlib import Path
from typing import Dict, List, Set, Any, Optional, Tuple
from dataclasses import dataclass, asdict, field
from datetime import datetime
import logging
from collections import defaultdict, deque

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class NetworkNode:
    """網絡節點"""
    node_id: str
    node_type: str
    name: str
    ip_address: Optional[str] = None
    port: Optional[int] = None
    region: str = "local"
    neighbors: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class DeepConnectionNetwork:
    """深度連接網絡"""
    
    def __init__(self, project_root: Path = Path("/workspaces/cosmic-ai.uk")):
        """初始化深度連接網絡
        
        Args:
            project_root: 項目根目錄
        """
        self.project_root = Path(project_root)
        self.network_dir = self.project_root / "deep_connection_network"
        self.node_dir = self.network_dir / "node_mapping"
        self.topo_dir = self.network_dir / "topology_index"
        self.route_dir = self.network_dir / "routing_table"
        
        # 確保目錄存在
        for d in [self.node_dir, self.topo_dir, self.route_dir]:
            d.mkdir(parents=True, exist_ok=True)
        
        # 構建網絡圖（簡化實現，不使用 networkx）
        self.graph_nodes: Dict[str, Any] = {}
        self.graph_edges: Dict[Tuple[str, str], Dict[str, Any]] = {}
        self.nodes: Dict[str, NetworkNode] = {}
        
        logger.info("✅ 深度連接網絡已初始化")
    
    def add_node(self, node: NetworkNode) -> None:
        """添加網絡節點
        
        Args:
            node: 網絡節點
        """
        self.nodes[node.node_id] = node
        self.graph_nodes[node.node_id] = asdict(node)
        
        # 保存到文件
        file_path = self.node_dir / f"{node.node_id}.json"
        with open(file_path, 'w') as f:
            json.dump(asdict(node), f, indent=2)
        
        logger.info(f"✅ 節點已添加: {node.name} ({node.node_id})")
    
    def connect_nodes(self, source_id: str, target_id: str, 
                     weight: float = 1.0, latency: float = 0.0) -> None:
        """連接兩個節點
        
        Args:
            source_id: 源節點ID
            target_id: 目標節點ID
            weight: 連接權重
            latency: 延遲（毫秒）
        """
        if source_id not in self.nodes or target_id not in self.nodes:
            logger.warning(f"❌ 節點不存在")
            return
        
        edge_key = (source_id, target_id)
        self.graph_edges[edge_key] = {
            "weight": weight,
            "latency": latency
        }
        
        # 更新鄰居列表
        if target_id not in self.nodes[source_id].neighbors:
            self.nodes[source_id].neighbors.append(target_id)
        
        logger.info(f"✅ 連接已建立: {source_id} -> {target_id}")
    
    def find_shortest_path(self, source_id: str, target_id: str) -> Optional[List[str]]:
        """找到最短路徑 (BFS)
        
        Args:
            source_id: 源節點ID
            target_id: 目標節點ID
            
        Returns:
            路徑列表
        """
        if source_id not in self.nodes or target_id not in self.nodes:
            return None
        
        # BFS 算法
        queue = deque([(source_id, [source_id])])
        visited = {source_id}
        
        while queue:
            current, path = queue.popleft()
            
            if current == target_id:
                return path
            
            for neighbor in self.nodes[current].neighbors:
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))
        
        return None
    
    def calculate_all_shortest_paths(self) -> Dict[str, Dict[str, float]]:
        """計算所有最短路徑
        
        Returns:
            路徑信息字典
        """
        paths = {}
        
        for source in self.nodes:
            paths[source] = {}
            for target in self.nodes:
                if source != target:
                    path = self.find_shortest_path(source, target)
                    if path:
                        paths[source][target] = len(path) - 1
                    else:
                        paths[source][target] = float('inf')
        
        return paths
    
    def get_network_statistics(self) -> Dict[str, Any]:
        """獲取網絡統計信息
        
        Returns:
            統計信息
        """
        total_nodes = len(self.nodes)
        total_edges = len(self.graph_edges)
        
        # 計算密度
        if total_nodes > 1:
            max_edges = total_nodes * (total_nodes - 1)
            density = total_edges / max_edges if max_edges > 0 else 0
        else:
            density = 0
        
        # 檢查連通性（簡化版）
        is_connected = True
        if total_nodes > 1:
            for node in self.nodes:
                for other_node in self.nodes:
                    if node != other_node:
                        if not self.find_shortest_path(node, other_node):
                            is_connected = False
                            break
        
        stats = {
            "total_nodes": total_nodes,
            "total_edges": total_edges,
            "density": density,
            "is_connected": is_connected,
            "avg_degree": total_edges / total_nodes if total_nodes > 0 else 0
        }
        
        return stats
    
    def export_topology(self, output_file: Path) -> None:
        """導出拓撲信息
        
        Args:
            output_file: 輸出文件
        """
        topology = {
            "timestamp": datetime.now().isoformat(),
            "nodes": {node_id: asdict(node) for node_id, node in self.nodes.items()},
            "edges": [
                {
                    "source": u,
                    "target": v,
                    **self.graph_edges[(u, v)]
                }
                for (u, v) in self.graph_edges.keys()
            ],
            "statistics": self.get_network_statistics()
        }
        
        with open(output_file, 'w') as f:
            json.dump(topology, f, indent=2, default=str)
        
        logger.info(f"✅ 拓撲已導出: {output_file}")
    
    def generate_routing_table(self) -> Dict[str, Dict[str, Any]]:
        """生成路由表
        
        Returns:
            路由表
        """
        routing_table = {}
        
        for node_id in self.nodes:
            routing_table[node_id] = {}
            
            for target_id in self.nodes:
                if node_id != target_id:
                    path = self.find_shortest_path(node_id, target_id)
                    if path:
                        routing_table[node_id][target_id] = {
                            "next_hop": path[1] if len(path) > 1 else target_id,
                            "distance": len(path) - 1,
                            "path": path
                        }
        
        # 保存路由表
        file_path = self.route_dir / "routing_table.json"
        with open(file_path, 'w') as f:
            json.dump(routing_table, f, indent=2)
        
        return routing_table

class NetworkTopologyManager:
    """網絡拓撲管理器"""
    
    _instance = None
    _network = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._network is None:
            self._network = DeepConnectionNetwork()
    
    def get_network(self) -> DeepConnectionNetwork:
        """獲取網絡實例"""
        return self._network
