#!/usr/bin/env python3
"""
Memory Manager for Comic AI
Comic AI 內存管理系統

Integrates memory.md persistence with advanced caching,
optimization, and automatic activation.
"""

import json
import time
import threading
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, asdict
import yaml
import sys

# Fix import path
sys.path.insert(0, str(Path(__file__).parent))

from memory_cache_optimization import (
    AdvancedMemoryCache,
    MemoryOptimizer,
    CompressionEngine,
    DeduplicationEngine,
    CacheStats
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class MemorySnapshot:
    """Single memory snapshot for history tracking"""
    timestamp: float
    datetime_str: str
    cache_stats: Dict[str, Any]
    system_memory: Dict[str, Any]
    entries_count: int
    compression_ratio: float


class MemoryManager:
    """
    Comprehensive Memory Management System with AI Intelligence
    整合記憶體持久化、緩存、優化和激活的系統 - AI智能增強版
    
    Features:
    - Multi-tier caching (L1/L2/L3)
    - AI-driven optimization
    - Adaptive learning and tuning
    - Predictive memory management
    - Performance tracking and analytics
    """

    def __init__(
        self,
        memory_file: str = "memory.md",
        state_file: str = ".memory_state.json",
        history_file: str = ".memory_history.json",
        l1_size_mb: int = 100,
        enable_auto_save: bool = True,
        auto_save_interval: int = 60,
        enable_ai_optimization: bool = True,
        enable_predictive_cache: bool = True
    ):
        """Initialize Memory Manager"""
        self.memory_file = Path(memory_file)
        self.state_file = Path(state_file)
        self.history_file = Path(history_file)
        self.enable_ai_optimization = enable_ai_optimization
        self.enable_predictive_cache = enable_predictive_cache

        self.cache = AdvancedMemoryCache(
            l1_max_size_mb=l1_size_mb,
            enable_compression=True,
            enable_deduplication=True
        )
        self.optimizer = MemoryOptimizer()
        self.compressor = CompressionEngine()
        self.deduplicator = DeduplicationEngine()

        self.state: Dict[str, Any] = self._load_state()
        self.history: List[MemorySnapshot] = self._load_history()
        self.enable_auto_save = enable_auto_save
        self.auto_save_interval = auto_save_interval
        self.auto_save_thread = None
        self.is_running = False
        self.lock = threading.RLock()
        
        # AI Optimization tracking
        self.ai_metrics: Dict[str, Any] = self._load_ai_metrics()
        self.prediction_history: List[Dict[str, Any]] = []

    def initialize(self):
        """Initialize the memory management system"""
        logger.info("Initializing Memory Manager...")

        if not self.state:
            self._initialize_state()

        if self.enable_auto_save:
            self._start_auto_save()

        logger.info("Memory Manager initialized successfully")

    def _initialize_state(self):
        """Initialize memory state file"""
        self.state = {
            "system_version": "1.0.0",
            "initialized_at": time.time(),
            "last_updated": time.time(),
            "total_operations": 0,
            "cache_configuration": {
                "l1_max_size_mb": 100,
                "enable_compression": True,
                "enable_deduplication": True
            },
            "optimization_config": {
                "max_memory_percent": 80.0,
                "auto_compression_threshold": 75.0
            },
            "statistics": {
                "total_hits": 0,
                "total_misses": 0,
                "total_compressions": 0,
                "total_evictions": 0
            }
        }
        self._save_state()

    def _load_state(self) -> Dict[str, Any]:
        """Load state from file"""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Could not load state file: {e}")
        return {}

    def _save_state(self):
        """Save state to file"""
        with self.lock:
            self.state["last_updated"] = time.time()
            try:
                with open(self.state_file, 'w') as f:
                    json.dump(self.state, f, indent=2)
                logger.debug(f"State saved to {self.state_file}")
            except Exception as e:
                logger.error(f"Error saving state: {e}")

    def _load_history(self) -> List[MemorySnapshot]:
        """Load memory history from file"""
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r') as f:
                    data = json.load(f)
                    return data.get("snapshots", [])
            except Exception as e:
                logger.warning(f"Could not load history file: {e}")
        return []

    def _load_ai_metrics(self) -> Dict[str, Any]:
        """Load AI optimization metrics"""
        ai_metrics_file = Path(".memory_ai_metrics.json")
        if ai_metrics_file.exists():
            try:
                with open(ai_metrics_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Could not load AI metrics: {e}")
        return self._initialize_ai_metrics()

    def _initialize_ai_metrics(self) -> Dict[str, Any]:
        """Initialize AI metrics"""
        return {
            "learning_enabled": self.enable_ai_optimization,
            "adaptive_l1_size": 100,
            "optimal_compression_threshold": 75.0,
            "cache_hit_target": 0.85,
            "eviction_predictions": [],
            "pattern_detected": False,
            "optimization_count": 0,
            "last_optimization": None
        }

    def _save_history(self):
        """Save memory history to file"""
        with self.lock:
            try:
                # Convert snapshots to dictionaries for JSON serialization
                snapshots_dict = []
                for snapshot in self.history[-100:]:
                    snap_dict = {
                        "timestamp": snapshot.timestamp,
                        "datetime_str": snapshot.datetime_str,
                        "entries_count": snapshot.entries_count,
                        "compression_ratio": snapshot.compression_ratio,
                        "cache_stats": snapshot.cache_stats,
                        "system_memory": snapshot.system_memory
                    }
                    snapshots_dict.append(snap_dict)

                history_data = {
                    "snapshots": snapshots_dict,
                    "total_snapshots": len(self.history),
                    "last_updated": time.time()
                }
                with open(self.history_file, 'w') as f:
                    json.dump(history_data, f, indent=2, default=str)
                logger.debug(f"History saved to {self.history_file}")
            except Exception as e:
                logger.error(f"Error saving history: {e}")

    def cache_put(self, key: str, value: Any, ttl_seconds: Optional[int] = None):
        """Put value into cache with memory optimization"""
        with self.lock:
            self.cache.put(key, value, ttl_seconds)
            self.state["total_operations"] += 1
            self._update_statistics()

    def cache_get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        with self.lock:
            value = self.cache.get(key)
            self.state["total_operations"] += 1
            self._update_statistics()
            return value

    def cache_delete(self, key: str):
        """Delete value from cache"""
        with self.lock:
            self.cache.delete(key)
            self.state["total_operations"] += 1

    def cache_clear(self):
        """Clear all cache levels"""
        with self.lock:
            self.cache.clear()
            logger.info("All cache levels cleared")

    def _update_statistics(self):
        """Update statistics from cache"""
        cache_stats = self.cache.stats
        self.state["statistics"] = {
            "total_hits": cache_stats.total_hits,
            "total_misses": cache_stats.total_misses,
            "total_compressions": cache_stats.total_compressions,
            "total_evictions": cache_stats.total_evictions,
            "hit_rate_percent": cache_stats.calculate_hit_rate()
        }

    def take_snapshot(self) -> MemorySnapshot:
        """Take a memory snapshot for history"""
        with self.lock:
            stats = self.cache.get_all_stats()
            snapshot = MemorySnapshot(
                timestamp=time.time(),
                datetime_str=datetime.now().isoformat(),
                cache_stats=stats,
                system_memory=stats["system_memory"],
                entries_count=stats["l1"]["entries"] + stats["l2"]["entries"] + stats["l3"]["entries"],
                compression_ratio=stats["overall"]["compression_ratio"]
            )
            self.history.append(snapshot)
            self._save_history()
            return snapshot

    def update_memory_md(self, section: str, content: str):
        """Update memory.md with new content"""
        with self.lock:
            if not self.memory_file.exists():
                logger.warning(f"Memory file {self.memory_file} does not exist")
                return

            try:
                with open(self.memory_file, 'r') as f:
                    md_content = f.read()

                # Find or create section
                section_marker = f"## {section}"
                if section_marker in md_content:
                    # Replace existing section
                    parts = md_content.split(section_marker)
                    before = parts[0]
                    # Find next section or end
                    rest = parts[1]
                    next_section_idx = rest.find("\n##")
                    if next_section_idx != -1:
                        after = rest[next_section_idx:]
                        md_content = before + section_marker + f"\n{content}" + after
                    else:
                        md_content = before + section_marker + f"\n{content}"
                else:
                    # Append new section
                    md_content += f"\n\n## {section}\n{content}"

                with open(self.memory_file, 'w') as f:
                    f.write(md_content)

                logger.info(f"Updated memory.md section: {section}")
            except Exception as e:
                logger.error(f"Error updating memory.md: {e}")

    def generate_memory_report(self) -> str:
        """Generate a detailed memory report"""
        with self.lock:
            stats = self.cache.get_all_stats()
            report = []

            report.append("# Memory System Report")
            report.append(f"\n**Generated**: {datetime.now().isoformat()}\n")

            # Cache Statistics
            report.append("## Cache Statistics\n")
            report.append(f"- **L1 Memory Entries**: {stats['l1']['entries']}")
            report.append(f"- **L1 Memory Usage**: {stats['l1']['current_size_mb']} MB / {stats['l1']['max_size_mb']} MB")
            report.append(f"- **L1 Utilization**: {stats['l1']['utilization_percent']}%")
            report.append(f"- **L2 Disk Entries**: {stats['l2']['entries']}")
            report.append(f"- **L2 Disk Usage**: {stats['l2']['total_size_mb']} MB")
            report.append(f"- **L3 Compressed Entries**: {stats['l3']['entries']}")
            report.append(f"- **L3 Compressed Usage**: {stats['l3']['total_size_mb']} MB")

            # Overall Performance
            report.append("\n## Overall Performance\n")
            report.append(f"- **Total Cache Hits**: {stats['overall']['total_hits']}")
            report.append(f"- **Total Cache Misses**: {stats['overall']['total_misses']}")
            report.append(f"- **Cache Hit Rate**: {stats['overall']['hit_rate_percent']}%")
            report.append(f"- **Total Compressions**: {stats['overall']['total_compressions']}")
            report.append(f"- **Average Compression Ratio**: {stats['overall']['compression_ratio']}x")

            # System Memory
            report.append("\n## System Memory\n")
            for key, value in stats['system_memory'].items():
                report.append(f"- **{key.replace('_', ' ').title()}**: {value}")

            # Optimization Suggestions
            if stats['optimization_suggestions']:
                report.append("\n## Optimization Suggestions\n")
                for suggestion in stats['optimization_suggestions']:
                    report.append(f"- {suggestion}")

            # State Information
            report.append("\n## State Information\n")
            report.append(f"- **System Version**: {self.state.get('system_version', 'unknown')}")
            report.append(f"- **Total Operations**: {self.state.get('total_operations', 0)}")
            report.append(f"- **Initialized At**: {datetime.fromtimestamp(self.state.get('initialized_at', 0)).isoformat()}")

            return "\n".join(report)

    def _auto_save_worker(self):
        """Background worker for automatic saves and memory cleanup"""
        cleanup_counter = 0
        
        while self.is_running:
            try:
                time.sleep(self.auto_save_interval)
                
                # Auto-save state
                self._save_state()
                self.take_snapshot()
                logger.debug("Auto-save completed")
                
                # Every 10 intervals (default: 600 seconds = 10 mins), cleanup short-term memory
                cleanup_counter += 1
                if cleanup_counter >= 10:
                    logger.info("Running scheduled short-term memory cleanup...")
                    cleanup_stats = self.cleanup_short_term_memory()
                    logger.info(f"Cleanup stats: {cleanup_stats}")
                    cleanup_counter = 0
                    
            except Exception as e:
                logger.error(f"Error in auto-save worker: {e}")

    def _start_auto_save(self):
        """Start automatic save thread"""
        if self.is_running:
            return

        self.is_running = True
        self.auto_save_thread = threading.Thread(target=self._auto_save_worker, daemon=True)
        self.auto_save_thread.start()
        logger.info("Auto-save thread started")

    def _stop_auto_save(self):
        """Stop automatic save thread"""
        self.is_running = False
        if self.auto_save_thread:
            self.auto_save_thread.join(timeout=5)
        logger.info("Auto-save thread stopped")

    def shutdown(self):
        """Shutdown memory manager gracefully"""
        logger.info("Shutting down Memory Manager...")
        self._stop_auto_save()
        self._save_state()
        self.take_snapshot()
        logger.info("Memory Manager shutdown complete")

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get current cache statistics"""
        return self.cache.get_all_stats()

    def ai_optimize(self) -> Dict[str, Any]:
        """Run AI-driven memory optimization"""
        if not self.enable_ai_optimization:
            return {"status": "disabled"}

        with self.lock:
            try:
                stats = self.cache.get_all_stats()
                current_hit_rate = stats['overall']['hit_rate_percent'] / 100.0
                
                optimization_result = {
                    "timestamp": datetime.now().isoformat(),
                    "before": {
                        "hit_rate": current_hit_rate,
                        "l1_size_mb": stats['l1']['current_size_mb'],
                        "compression_ratio": stats['overall']['compression_ratio']
                    },
                    "recommendations": []
                }

                # AI Decision 1: Adaptive L1 sizing
                if current_hit_rate < self.ai_metrics["cache_hit_target"]:
                    new_l1_size = int(stats['l1']['max_size_mb'] * 1.2)
                    optimization_result["recommendations"].append({
                        "type": "l1_resize",
                        "reason": f"Low hit rate ({current_hit_rate:.2%})",
                        "new_size_mb": min(new_l1_size, 500)
                    })
                
                # AI Decision 2: Compression threshold
                if stats['system_memory']['system_percent'] > 80:
                    optimization_result["recommendations"].append({
                        "type": "increase_compression",
                        "reason": "High system memory usage",
                        "threshold": 70.0
                    })
                
                # AI Decision 3: Predictive eviction
                if len(self.history) > 10:
                    avg_ops = sum(h.get('entries_count', 0) if isinstance(h, dict) else 0 
                                 for h in self.history[-10:]) / 10
                    if avg_ops > stats['l1']['entries'] * 1.5:
                        optimization_result["recommendations"].append({
                            "type": "predictive_preload",
                            "reason": "Predicted high load",
                            "expected_operations": int(avg_ops)
                        })

                self.ai_metrics["optimization_count"] += 1
                self.ai_metrics["last_optimization"] = datetime.now().isoformat()
                self._save_ai_metrics()

                return optimization_result

            except Exception as e:
                logger.error(f"Error in AI optimization: {e}")
                return {"status": "error", "message": str(e)}

    def _save_ai_metrics(self):
        """Save AI metrics to file"""
        try:
            with open(".memory_ai_metrics.json", 'w') as f:
                json.dump(self.ai_metrics, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving AI metrics: {e}")

    def print_report(self):
        """Print memory report to console"""
        report = self.generate_memory_report()
        print("\n" + "=" * 70)
        print(report)
        print("=" * 70 + "\n")

    def migrate_short_to_long_term(self, key: str) -> bool:
        """
        Migrate important data from short-term to long-term memory
        
        Args:
            key: Memory key to migrate
            
        Returns:
            True if migration successful
        """
        try:
            # Get value from short-term
            value = self.cache.short_term.get(key)
            if value is None:
                logger.warning(f"Key {key} not found in short-term memory")
                return False

            # Calculate importance
            importance = self.cache.compressor.calculate_content_importance(value)
            
            # Store in long-term with tags
            tags = ["migrated", "important"] if importance > 0.5 else ["auto_migrated"]
            success = self.cache.long_term.put(key, value, importance=importance, tags=tags)
            
            if success:
                logger.info(f"Migrated {key} to long-term memory (importance: {importance:.2f})")
            
            return success
        except Exception as e:
            logger.error(f"Error migrating to long-term: {e}")
            return False

    def cleanup_short_term_memory(self) -> Dict[str, Any]:
        """
        Clean up expired short-term memory entries
        Automatically migrates important items to long-term before deletion
        
        Returns:
            Cleanup statistics
        """
        with self.lock:
            try:
                # Get expired entries
                expired_keys = self.cache.short_term.get_expired()
                
                stats = {
                    "expired_count": len(expired_keys),
                    "migrated_count": 0,
                    "deleted_count": 0,
                    "timestamps": datetime.now().isoformat()
                }
                
                for key in expired_keys:
                    # Check importance before deleting
                    value = self.cache.short_term.entries.get(key)
                    if value:
                        data, _ = value
                        importance = self.cache.compressor.calculate_content_importance(data)
                        
                        # Migrate important data to long-term
                        if importance > 0.6:
                            if self.migrate_short_to_long_term(key):
                                stats["migrated_count"] += 1
                
                # Clear expired entries
                self.cache.short_term.entries.clear()
                for key in expired_keys:
                    self.cache.short_term.access_count.pop(key, None)
                
                stats["deleted_count"] = len(expired_keys) - stats["migrated_count"]
                logger.info(f"Short-term memory cleanup: {stats}")
                
                return stats
            except Exception as e:
                logger.error(f"Error cleaning up short-term memory: {e}")
                return {"error": str(e)}

    def memory_summary(self) -> Dict[str, Any]:
        """Get comprehensive memory system summary"""
        with self.lock:
            short_term_stats = self.cache.short_term.stats()
            long_term_stats = self.cache.long_term.stats()
            cache_stats = self.cache.get_all_stats()
            
            return {
                "short_term": {
                    **short_term_stats,
                    "expired_entries": len(self.cache.short_term.get_expired())
                },
                "long_term": long_term_stats,
                "cache": {
                    "l1": cache_stats["l1"],
                    "l2": cache_stats["l2"],
                    "l3": cache_stats["l3"],
                    "overall": cache_stats["overall"]
                },
                "ai_metrics": self.ai_metrics,
                "timestamp": datetime.now().isoformat()
            }
        """Print memory report to console"""
        report = self.generate_memory_report()
        print("\n" + "=" * 70)
        print(report)
        print("=" * 70 + "\n")


# Global instance
_memory_manager: Optional[MemoryManager] = None


def get_memory_manager() -> MemoryManager:
    """Get or create global memory manager instance"""
    global _memory_manager
    if _memory_manager is None:
        _memory_manager = MemoryManager()
        _memory_manager.initialize()
    return _memory_manager


def init_memory_manager(**kwargs) -> MemoryManager:
    """Initialize memory manager with custom parameters"""
    global _memory_manager
    _memory_manager = MemoryManager(**kwargs)
    _memory_manager.initialize()
    return _memory_manager


if __name__ == "__main__":
    print("Comic AI Memory Manager")
    print("內存管理系統\n")

    # Initialize
    manager = init_memory_manager(l1_size_mb=50)

    # Test operations
    print("Testing memory manager operations...")

    # Put test data
    test_data = {
        "model": "quantum_grover",
        "performance": {
            "accuracy": 0.95,
            "speed": "fast"
        },
        "timestamp": datetime.now().isoformat()
    }

    manager.cache_put("test_model_1", test_data)
    print("✅ Test data cached")

    # Retrieve
    retrieved = manager.cache_get("test_model_1")
    print(f"✅ Retrieved data: {type(retrieved)}")

    # Take snapshot
    snapshot = manager.take_snapshot()
    print(f"✅ Snapshot taken at {snapshot.datetime_str}")

    # Generate report
    manager.print_report()

    # Shutdown
    manager.shutdown()
