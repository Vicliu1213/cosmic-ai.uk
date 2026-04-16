"""
Engine Registry - Central registry for all engine metadata and indexing
Provides unified access to engine information and discovery
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class EngineCategory(Enum):
    """Engine categories for organization"""
    QUANTUM = "quantum"
    SYNERGY = "synergy"
    TRADING = "trading"
    EVOLUTION = "evolution"
    INTEGRATION = "integration"
    ANALYSIS = "analysis"
    CORE = "core"
    UTILITY = "utility"


@dataclass
class EngineMetadata:
    """Metadata for engine discovery and management"""
    name: str
    version: str
    category: EngineCategory
    description: str
    author: str = "Cosmic AI"
    enabled: bool = True
    dependencies: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    config_schema: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metadata to dictionary"""
        return {
            'name': self.name,
            'version': self.version,
            'category': self.category.value,
            'description': self.description,
            'author': self.author,
            'enabled': self.enabled,
            'dependencies': self.dependencies,
            'tags': self.tags,
            'config_schema': self.config_schema
        }


class EngineRegistry:
    """
    Central registry for all engines in the system
    Provides indexing, discovery, and metadata management
    """
    
    def __init__(self):
        """Initialize the engine registry"""
        self._engines: Dict[str, EngineMetadata] = {}
        self._categories: Dict[EngineCategory, List[str]] = {
            category: [] for category in EngineCategory
        }
        self._tags_index: Dict[str, List[str]] = {}
        self._dependency_graph: Dict[str, List[str]] = {}
    
    def register(self, metadata: EngineMetadata) -> None:
        """
        Register an engine in the registry
        
        Args:
            metadata: Engine metadata
        """
        if metadata.name in self._engines:
            logger.warning(f"Engine '{metadata.name}' already registered, overwriting")
        
        self._engines[metadata.name] = metadata
        
        # Index by category
        if metadata.category not in self._categories:
            self._categories[metadata.category] = []
        self._categories[metadata.category].append(metadata.name)
        
        # Index by tags
        for tag in metadata.tags:
            if tag not in self._tags_index:
                self._tags_index[tag] = []
            self._tags_index[tag].append(metadata.name)
        
        # Index dependencies
        self._dependency_graph[metadata.name] = metadata.dependencies
        
        logger.info(f"Registered engine: {metadata.name} (v{metadata.version})")
    
    def unregister(self, engine_name: str) -> bool:
        """
        Unregister an engine from the registry
        
        Args:
            engine_name: Engine name
        
        Returns:
            bool: True if unregistered successfully
        """
        if engine_name not in self._engines:
            logger.warning(f"Engine '{engine_name}' not found in registry")
            return False
        
        metadata = self._engines[engine_name]
        
        # Remove from category index
        if metadata.category in self._categories:
            self._categories[metadata.category].remove(engine_name)
        
        # Remove from tags index
        for tag in metadata.tags:
            if tag in self._tags_index:
                self._tags_index[tag].remove(engine_name)
        
        # Remove from dependency graph
        if engine_name in self._dependency_graph:
            del self._dependency_graph[engine_name]
        
        del self._engines[engine_name]
        logger.info(f"Unregistered engine: {engine_name}")
        
        return True
    
    def get(self, engine_name: str) -> Optional[EngineMetadata]:
        """
        Get engine metadata by name
        
        Args:
            engine_name: Engine name
        
        Returns:
            Optional[EngineMetadata]: Engine metadata or None
        """
        return self._engines.get(engine_name)
    
    def get_by_category(self, category: EngineCategory) -> List[str]:
        """
        Get all engines in a category
        
        Args:
            category: Engine category
        
        Returns:
            List: Engine names in the category
        """
        return self._categories.get(category, []).copy()
    
    def get_by_tag(self, tag: str) -> List[str]:
        """
        Get all engines with a specific tag
        
        Args:
            tag: Tag name
        
        Returns:
            List: Engine names with the tag
        """
        return self._tags_index.get(tag, []).copy()
    
    def search(self, keyword: str) -> List[str]:
        """
        Search engines by keyword in name or description
        
        Args:
            keyword: Search keyword
        
        Returns:
            List: Matching engine names
        """
        results = []
        keyword_lower = keyword.lower()
        
        for name, metadata in self._engines.items():
            if (keyword_lower in name.lower() or 
                keyword_lower in metadata.description.lower()):
                results.append(name)
        
        return results
    
    def get_dependencies(self, engine_name: str) -> List[str]:
        """
        Get direct dependencies of an engine
        
        Args:
            engine_name: Engine name
        
        Returns:
            List: Dependent engine names
        """
        return self._dependency_graph.get(engine_name, []).copy()
    
    def get_all_dependencies(self, engine_name: str) -> List[str]:
        """
        Get all recursive dependencies of an engine
        
        Args:
            engine_name: Engine name
        
        Returns:
            List: All dependent engine names
        """
        all_deps = set()
        to_process = [engine_name]
        
        while to_process:
            current = to_process.pop()
            deps = self.get_dependencies(current)
            
            for dep in deps:
                if dep not in all_deps:
                    all_deps.add(dep)
                    to_process.append(dep)
        
        return list(all_deps)
    
    def get_all(self) -> Dict[str, EngineMetadata]:
        """
        Get all registered engines
        
        Returns:
            Dict: All engine metadata indexed by name
        """
        return self._engines.copy()
    
    def list_all(self) -> List[str]:
        """
        List all registered engine names
        
        Returns:
            List: All engine names
        """
        return list(self._engines.keys())
    
    def get_status_report(self) -> Dict[str, Any]:
        """
        Get a comprehensive status report of the registry
        
        Returns:
            Dict: Status information
        """
        return {
            'total_engines': len(self._engines),
            'by_category': {
                cat.value: len(engines)
                for cat, engines in self._categories.items()
            },
            'total_tags': len(self._tags_index),
            'engines': [
                metadata.to_dict()
                for metadata in self._engines.values()
            ]
        }


# Global registry instance
_global_registry: Optional[EngineRegistry] = None


def get_engine_registry() -> EngineRegistry:
    """
    Get or create the global engine registry
    
    Returns:
        EngineRegistry: Global registry instance
    """
    global _global_registry
    if _global_registry is None:
        _global_registry = EngineRegistry()
    return _global_registry


def register_engine(metadata: EngineMetadata) -> None:
    """
    Register an engine globally
    
    Args:
        metadata: Engine metadata
    """
    registry = get_engine_registry()
    registry.register(metadata)
