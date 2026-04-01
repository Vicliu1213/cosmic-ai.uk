# core/algorithm_registry.py
import asyncio
import logging
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class AlgorithmMetadata:
    name: str
    category: str
    description: str
    min_qubits: int
    required_platforms: List[str]
    preferred_platform: Optional[str] = None
    alternative_platforms: List[str] = None
    synergy_capable: bool = False
    compatible_algorithms: List[str] = None


class PlatformManager:
    """管理所有平台实例"""
    def __init__(self, platforms: Dict[str, Any]):
        self.platforms = platforms
        # 标记活跃平台（已连接）
        self.active_platforms = {
            name: p for name, p in platforms.items() if getattr(p, 'status', None) == "connected"
        }

    async def get_platform(self, name: str) -> Any:
        return self.platforms.get(name)

    def get_executor(self, platform_name: str) -> Optional[Callable]:
        """获取平台的执行方法"""
        platform = self.platforms.get(platform_name)
        if platform and hasattr(platform, 'execute_circuit'):
            return platform.execute_circuit
        return None

    def get_hybrid_executor(self, platform_name: str) -> Optional[Callable]:
        """混合执行器（简化，与普通执行器相同）"""
        return self.get_executor(platform_name)


class PlatformAwareRegistry:
    """算法注册中心，感知平台能力"""
    def __init__(self, platform_manager: PlatformManager):
        self.platform_manager = platform_manager
        self.algorithms: Dict[str, Callable] = {}
        self.metadata: Dict[str, AlgorithmMetadata] = {}
        self.platform_to_algorithms: Dict[str, List[str]] = {}

    def register(self, func: Callable, metadata: AlgorithmMetadata):
        name = metadata.name
        self.algorithms[name] = func
        self.metadata[name] = metadata
        for platform in metadata.required_platforms:
            self.platform_to_algorithms.setdefault(platform, []).append(name)
        logger.info(f"算法注册: {name}")

    async def select_platform_for_algorithm(self, algorithm_name: str, context: Dict) -> Optional[str]:
        meta = self.metadata.get(algorithm_name)
        if not meta:
            return None
        # 优先首选平台
        if meta.preferred_platform and meta.preferred_platform in self.platform_manager.active_platforms:
            return meta.preferred_platform
        for platform in meta.required_platforms:
            if platform in self.platform_manager.active_platforms:
                return platform
        for platform in meta.alternative_platforms or []:
            if platform in self.platform_manager.active_platforms:
                return platform
        return None

    def find_compatible_algorithms(self, algorithm_name: str, task_type: str) -> List[str]:
        meta = self.metadata.get(algorithm_name)
        if not meta or not meta.synergy_capable:
            return []
        return meta.compatible_algorithms or []

    def get_algorithm_info(self, algorithm_name: str) -> Optional[Dict]:
        meta = self.metadata.get(algorithm_name)
        if not meta:
            return None
        return {
            "name": meta.name,
            "category": meta.category,
            "description": meta.description,
            "min_qubits": meta.min_qubits,
            "required_platforms": meta.required_platforms,
            "preferred_platform": meta.preferred_platform,
            "synergy_capable": meta.synergy_capable,
            "compatible_algorithms": meta.compatible_algorithms
        }

    def get_platform(self, name: str) -> Any:
        return self.platform_manager.get_platform(name)

    def get_executor(self, platform_name: str) -> Optional[Callable]:
        return self.platform_manager.get_executor(platform_name)

    def get_hybrid_executor(self, platform_name: str) -> Optional[Callable]:
        return self.platform_manager.get_hybrid_executor(platform_name)
