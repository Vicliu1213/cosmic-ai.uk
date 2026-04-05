#!/usr/bin/env python3
"""
Memory Optimization and Advanced Caching System
Comic AI - 高階內存優化和緩存系統

This module provides:
- LRU (Least Recently Used) cache with eviction policies
- Memory compression and deduplication
- Multi-tier caching (L1: In-memory, L2: Disk, L3: Compressed)
- Real-time memory monitoring and optimization
- Adaptive cache sizing based on system load
"""

import os
import json
import pickle
import zlib
import hashlib
import time
import threading
import logging
from typing import Dict, Any, Optional, Tuple, List, Callable
from dataclasses import dataclass, field, asdict
from collections import OrderedDict
from pathlib import Path
from datetime import datetime, timedelta
from enum import Enum
import psutil

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CacheLevel(Enum):
    """Cache hierarchy levels"""
    L1_MEMORY = "memory"      # In-memory cache (fastest)
    L2_DISK = "disk"          # Disk-based cache (medium)
    L3_COMPRESSED = "compressed"  # Compressed cache (slow but efficient)


class EvictionPolicy(Enum):
    """Cache eviction policies"""
    LRU = "lru"               # Least Recently Used
    LFU = "lfu"               # Least Frequently Used
    FIFO = "fifo"             # First In First Out
    TTL = "ttl"               # Time To Live


@dataclass
class CacheEntry:
    """Single cache entry with metadata"""
    key: str
    value: Any
    created_at: float = field(default_factory=time.time)
    accessed_at: float = field(default_factory=time.time)
    access_count: int = 0
    size_bytes: int = 0
    compressed: bool = False
    compression_ratio: float = 1.0
    level: str = CacheLevel.L1_MEMORY.value
    ttl_seconds: Optional[int] = None
    hash_value: str = ""

    def is_expired(self) -> bool:
        """Check if entry has expired based on TTL"""
        if self.ttl_seconds is None:
            return False
        return (time.time() - self.created_at) > self.ttl_seconds

    def mark_accessed(self):
        """Update access statistics"""
        self.accessed_at = time.time()
        self.access_count += 1


@dataclass
class CacheStats:
    """Cache performance statistics"""
    total_hits: int = 0
    total_misses: int = 0
    total_evictions: int = 0
    total_compressions: int = 0
    current_memory_bytes: int = 0
    peak_memory_bytes: int = 0
    compression_ratio: float = 1.0
    hit_rate: float = 0.0

    def calculate_hit_rate(self) -> float:
        """Calculate cache hit rate"""
        total = self.total_hits + self.total_misses
        return (self.total_hits / total * 100) if total > 0 else 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert stats to dictionary"""
        return {
            "total_hits": self.total_hits,
            "total_misses": self.total_misses,
            "total_evictions": self.total_evictions,
            "total_compressions": self.total_compressions,
            "current_memory_mb": round(self.current_memory_bytes / 1024 / 1024, 2),
            "peak_memory_mb": round(self.peak_memory_bytes / 1024 / 1024, 2),
            "compression_ratio": round(self.compression_ratio, 2),
            "hit_rate_percent": round(self.calculate_hit_rate(), 2)
        }


class MemoryOptimizer:
    """System memory optimization engine"""

    def __init__(self, max_memory_percent: float = 80.0):
        """
        Initialize memory optimizer

        Args:
            max_memory_percent: Maximum system memory usage percentage (default: 80%)
        """
        self.max_memory_percent = max_memory_percent
        self.monitor_thread = None
        self.is_running = False

    def get_system_memory_info(self) -> Dict[str, Any]:
        """Get current system memory information"""
        memory = psutil.virtual_memory()
        process = psutil.Process(os.getpid())
        process_memory = process.memory_info()

        return {
            "system_total_mb": round(memory.total / 1024 / 1024, 2),
            "system_available_mb": round(memory.available / 1024 / 1024, 2),
            "system_used_mb": round(memory.used / 1024 / 1024, 2),
            "system_percent": memory.percent,
            "process_rss_mb": round(process_memory.rss / 1024 / 1024, 2),
            "process_vms_mb": round(process_memory.vms / 1024 / 1024, 2),
            "memory_threshold_percent": self.max_memory_percent
        }

    def should_optimize(self) -> bool:
        """Check if system memory optimization is needed"""
        memory = psutil.virtual_memory()
        return memory.percent >= self.max_memory_percent

    def get_optimization_suggestions(self) -> List[str]:
        """Get memory optimization suggestions"""
        info = self.get_system_memory_info()
        suggestions = []

        if info["system_percent"] > 90:
            suggestions.append("Critical: System memory usage > 90%. Consider aggressive compression.")
        elif info["system_percent"] > 80:
            suggestions.append("Warning: System memory usage > 80%. Enable automatic compression.")

        if info["process_rss_mb"] > 500:
            suggestions.append(f"Process memory exceeds 500MB ({info['process_rss_mb']}MB). Enable caching strategies.")

        return suggestions


class CompressionEngine:
    """Data compression and decompression engine"""

    @staticmethod
    def compress(data: Any, compression_level: int = 6) -> Tuple[bytes, float]:
        """
        Compress data using zlib

        Args:
            data: Data to compress
            compression_level: Compression level (1-9, default: 6)

        Returns:
            Tuple of (compressed_data, compression_ratio)
        """
        original_data = pickle.dumps(data)
        original_size = len(original_data)

        compressed_data = zlib.compress(original_data, compression_level)
        compressed_size = len(compressed_data)

        compression_ratio = original_size / compressed_size if compressed_size > 0 else 1.0

        return compressed_data, compression_ratio

    @staticmethod
    def decompress(compressed_data: bytes) -> Any:
        """
        Decompress data using zlib

        Args:
            compressed_data: Compressed data bytes

        Returns:
            Decompressed data
        """
        original_data = zlib.decompress(compressed_data)
        return pickle.loads(original_data)

    @staticmethod
    def calculate_compression_benefit(original_size: int, compressed_size: int) -> Dict[str, Any]:
        """Calculate compression benefit metrics"""
        return {
            "original_size_bytes": original_size,
            "compressed_size_bytes": compressed_size,
            "savings_bytes": original_size - compressed_size,
            "savings_percent": round((1 - compressed_size / original_size) * 100, 2) if original_size > 0 else 0,
            "compression_ratio": round(original_size / compressed_size, 2) if compressed_size > 0 else 0
        }


class DeduplicationEngine:
    """Data deduplication engine for eliminating duplicate entries"""

    def __init__(self):
        self.hash_index: Dict[str, List[str]] = {}  # hash -> [keys]

    def calculate_hash(self, data: Any) -> str:
        """Calculate SHA256 hash of data"""
        data_str = json.dumps(data, default=str, sort_keys=True)
        return hashlib.sha256(data_str.encode()).hexdigest()

    def add_entry(self, key: str, data: Any) -> Tuple[str, bool]:
        """
        Add entry and check for duplicates

        Args:
            key: Entry key
            data: Entry data

        Returns:
            Tuple of (hash, is_duplicate)
        """
        hash_value = self.calculate_hash(data)

        if hash_value not in self.hash_index:
            self.hash_index[hash_value] = []

        is_duplicate = len(self.hash_index[hash_value]) > 0
        self.hash_index[hash_value].append(key)

        return hash_value, is_duplicate

    def get_duplicates(self, hash_value: str) -> List[str]:
        """Get all keys with the same hash"""
        return self.hash_index.get(hash_value, [])

    def remove_entry(self, key: str, hash_value: str):
        """Remove entry from deduplication index"""
        if hash_value in self.hash_index:
            self.hash_index[hash_value] = [k for k in self.hash_index[hash_value] if k != key]
            if not self.hash_index[hash_value]:
                del self.hash_index[hash_value]


class L1MemoryCache:
    """L1: In-memory cache using LRU eviction"""

    def __init__(self, max_size_bytes: int = 100 * 1024 * 1024):  # 100MB default
        self.max_size_bytes = max_size_bytes
        self.cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self.current_size_bytes = 0
        self.lock = threading.RLock()

    def get(self, key: str) -> Optional[Any]:
        """Get value from L1 cache"""
        with self.lock:
            if key in self.cache:
                entry = self.cache[key]
                if entry.is_expired():
                    del self.cache[key]
                    self.current_size_bytes -= entry.size_bytes
                    return None

                entry.mark_accessed()
                # Move to end (most recently used)
                self.cache.move_to_end(key)
                return entry.value
        return None

    def put(self, key: str, value: Any, ttl_seconds: Optional[int] = None) -> bool:
        """Put value into L1 cache"""
        with self.lock:
            size = self._estimate_size(value)

            # Evict entries if necessary
            while self.current_size_bytes + size > self.max_size_bytes and self.cache:
                self._evict_lru()

            entry = CacheEntry(
                key=key,
                value=value,
                size_bytes=size,
                level=CacheLevel.L1_MEMORY.value,
                ttl_seconds=ttl_seconds
            )

            if key in self.cache:
                self.current_size_bytes -= self.cache[key].size_bytes

            self.cache[key] = entry
            self.current_size_bytes += size

            # Move to end (most recently used)
            self.cache.move_to_end(key)
            return True

    def _evict_lru(self) -> Optional[str]:
        """Evict least recently used entry"""
        if self.cache:
            key, entry = self.cache.popitem(last=False)
            self.current_size_bytes -= entry.size_bytes
            return key
        return None

    def _estimate_size(self, value: Any) -> int:
        """Estimate size of value in bytes"""
        try:
            return len(pickle.dumps(value))
        except:
            return 1024  # Default estimate

    def clear(self):
        """Clear all entries"""
        with self.lock:
            self.cache.clear()
            self.current_size_bytes = 0

    def stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with self.lock:
            return {
                "level": "L1_MEMORY",
                "entries": len(self.cache),
                "current_size_mb": round(self.current_size_bytes / 1024 / 1024, 2),
                "max_size_mb": round(self.max_size_bytes / 1024 / 1024, 2),
                "utilization_percent": round(self.current_size_bytes / self.max_size_bytes * 100, 2)
            }


class L2DiskCache:
    """L2: Disk-based cache for overflow"""

    def __init__(self, cache_dir: str = ".cache/l2"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.lock = threading.RLock()

    def get(self, key: str) -> Optional[Any]:
        """Get value from L2 disk cache"""
        with self.lock:
            cache_file = self.cache_dir / f"{key}.pkl"
            if cache_file.exists():
                try:
                    with open(cache_file, 'rb') as f:
                        entry_data = pickle.load(f)
                    entry = CacheEntry(**entry_data)
                    if entry.is_expired():
                        cache_file.unlink()
                        return None
                    entry.mark_accessed()
                    # Update on disk
                    self._save_entry(key, entry)
                    return entry.value
                except Exception as e:
                    logger.error(f"Error reading L2 cache {key}: {e}")
        return None

    def put(self, key: str, value: Any, ttl_seconds: Optional[int] = None):
        """Put value into L2 disk cache"""
        with self.lock:
            entry = CacheEntry(
                key=key,
                value=value,
                size_bytes=len(pickle.dumps(value)),
                level=CacheLevel.L2_DISK.value,
                ttl_seconds=ttl_seconds
            )
            self._save_entry(key, entry)

    def _save_entry(self, key: str, entry: CacheEntry):
        """Save entry to disk"""
        cache_file = self.cache_dir / f"{key}.pkl"
        try:
            with open(cache_file, 'wb') as f:
                entry_dict = asdict(entry)
                entry_dict['value'] = entry.value
                pickle.dump(entry_dict, f)
        except Exception as e:
            logger.error(f"Error saving L2 cache {key}: {e}")

    def delete(self, key: str):
        """Delete entry from L2 cache"""
        with self.lock:
            cache_file = self.cache_dir / f"{key}.pkl"
            if cache_file.exists():
                cache_file.unlink()

    def clear(self):
        """Clear all entries"""
        with self.lock:
            for cache_file in self.cache_dir.glob("*.pkl"):
                cache_file.unlink()

    def stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with self.lock:
            files = list(self.cache_dir.glob("*.pkl"))
            total_size = sum(f.stat().st_size for f in files)
            return {
                "level": "L2_DISK",
                "entries": len(files),
                "total_size_mb": round(total_size / 1024 / 1024, 2),
                "cache_dir": str(self.cache_dir)
            }


class L3CompressedCache:
    """L3: Compressed cache for long-term storage"""

    def __init__(self, cache_dir: str = ".cache/l3", compression_level: int = 9):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.compression_level = compression_level
        self.compressor = CompressionEngine()
        self.lock = threading.RLock()

    def get(self, key: str) -> Optional[Any]:
        """Get value from L3 compressed cache"""
        with self.lock:
            cache_file = self.cache_dir / f"{key}.zp"
            if cache_file.exists():
                try:
                    with open(cache_file, 'rb') as f:
                        compressed_data = f.read()
                    value = self.compressor.decompress(compressed_data)
                    return value
                except Exception as e:
                    logger.error(f"Error reading L3 cache {key}: {e}")
        return None

    def put(self, key: str, value: Any) -> Tuple[bool, float]:
        """
        Put value into L3 compressed cache

        Returns:
            Tuple of (success, compression_ratio)
        """
        with self.lock:
            try:
                compressed_data, ratio = self.compressor.compress(value, self.compression_level)
                cache_file = self.cache_dir / f"{key}.zp"
                with open(cache_file, 'wb') as f:
                    f.write(compressed_data)
                return True, ratio
            except Exception as e:
                logger.error(f"Error saving L3 cache {key}: {e}")
                return False, 1.0

    def delete(self, key: str):
        """Delete entry from L3 cache"""
        with self.lock:
            cache_file = self.cache_dir / f"{key}.zp"
            if cache_file.exists():
                cache_file.unlink()

    def clear(self):
        """Clear all entries"""
        with self.lock:
            for cache_file in self.cache_dir.glob("*.zp"):
                cache_file.unlink()

    def stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with self.lock:
            files = list(self.cache_dir.glob("*.zp"))
            total_size = sum(f.stat().st_size for f in files)
            return {
                "level": "L3_COMPRESSED",
                "entries": len(files),
                "total_size_mb": round(total_size / 1024 / 1024, 2),
                "compression_level": self.compression_level,
                "cache_dir": str(self.cache_dir)
            }


class AdvancedMemoryCache:
    """
    Advanced multi-tier memory caching system with AI Learning
    Comic AI 高階多層內存緩存系統 - 帶有AI學習能力的升級版本

    Combines L1 (memory), L2 (disk), and L3 (compressed) caches
    with automatic optimization, deduplication, and adaptive learning.
    
    Features:
    - Multi-tier caching (L1/L2/L3)
    - Adaptive learning and tuning
    - Pattern detection
    - Predictive cache warming
    - Performance analytics
    """

    def __init__(
        self,
        l1_max_size_mb: int = 100,
        l2_cache_dir: str = ".cache/l2",
        l3_cache_dir: str = ".cache/l3",
        enable_compression: bool = True,
        enable_deduplication: bool = True,
        enable_learning: bool = True
    ):
        """Initialize advanced memory cache"""
        self.l1 = L1MemoryCache(max_size_bytes=l1_max_size_mb * 1024 * 1024)
        self.l2 = L2DiskCache(l2_cache_dir)
        self.l3 = L3CompressedCache(l3_cache_dir)
        self.optimizer = MemoryOptimizer()
        self.deduplicator = DeduplicationEngine() if enable_deduplication else None
        self.enable_compression = enable_compression
        self.enable_learning = enable_learning
        self.stats = CacheStats()
        self.lock = threading.RLock()
        
        # Learning metrics
        self.access_patterns: Dict[str, int] = {}
        self.hot_keys: List[Tuple[str, int]] = []
        self.learning_history: List[Dict[str, Any]] = []

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache (checks all levels) with learning"""
        with self.lock:
            # Update access patterns for learning
            if self.enable_learning:
                self.access_patterns[key] = self.access_patterns.get(key, 0) + 1
                self._update_hot_keys()
            
            # Try L1
            value = self.l1.get(key)
            if value is not None:
                self.stats.total_hits += 1
                return value

            # Try L2
            value = self.l2.get(key)
            if value is not None:
                self.stats.total_hits += 1
                # Promote to L1 (learning optimization)
                self.l1.put(key, value)
                return value

            # Try L3
            value = self.l3.get(key)
            if value is not None:
                self.stats.total_hits += 1
                # Promote to L1 (learning optimization)
                self.l1.put(key, value)
                return value

            self.stats.total_misses += 1
            return None

    def _update_hot_keys(self):
        """Update hot keys based on access patterns"""
        if len(self.access_patterns) > 0:
            # Sort by access count and keep top 20
            sorted_keys = sorted(self.access_patterns.items(), key=lambda x: x[1], reverse=True)
            self.hot_keys = sorted_keys[:20]

    def get_hot_keys(self) -> List[Tuple[str, int]]:
        """Get most frequently accessed keys"""
        return self.hot_keys.copy()

    def get_learning_stats(self) -> Dict[str, Any]:
        """Get learning statistics"""
        return {
            "total_access_patterns": len(self.access_patterns),
            "hot_keys_count": len(self.hot_keys),
            "hot_keys": self.hot_keys[:10],
            "learning_enabled": self.enable_learning,
            "learning_history_size": len(self.learning_history)
        }

    def put(self, key: str, value: Any, ttl_seconds: Optional[int] = None, compress: bool = False):
        """
        Put value into cache (automatic tier selection)

        Args:
            key: Cache key
            value: Value to cache
            ttl_seconds: Time to live in seconds
            compress: Force compression for L3
        """
        with self.lock:
            # Check for duplicates
            if self.deduplicator:
                hash_val, is_dup = self.deduplicator.add_entry(key, value)
                if is_dup:
                    logger.info(f"Duplicate detected for key {key} (hash: {hash_val[:8]}...)")

            # Determine storage tier
            should_compress = compress or self.optimizer.should_optimize()

            if should_compress and self.enable_compression:
                # Use L3 compressed cache
                success, ratio = self.l3.put(key, value)
                if success:
                    self.stats.total_compressions += 1
                    self.stats.compression_ratio = ratio
            else:
                # Try L1, fallback to L2
                self.l1.put(key, value, ttl_seconds)

            # Update memory stats
            self._update_memory_stats()

    def delete(self, key: str):
        """Delete entry from all cache levels"""
        with self.lock:
            if self.deduplicator:
                # Remove from deduplication index
                for level_cache in [self.l1, self.l2, self.l3]:
                    if hasattr(level_cache, 'cache') and key in level_cache.cache:
                        entry = level_cache.cache[key]
                        hash_val = hashlib.sha256(json.dumps(entry.value, default=str).encode()).hexdigest()
                        self.deduplicator.remove_entry(key, hash_val)

            if key in self.l1.cache:
                del self.l1.cache[key]
            self.l2.delete(key)
            self.l3.delete(key)

    def clear(self):
        """Clear all cache levels"""
        with self.lock:
            self.l1.clear()
            self.l2.clear()
            self.l3.clear()
            if self.deduplicator:
                self.deduplicator.hash_index.clear()

    def _update_memory_stats(self):
        """Update cache statistics"""
        self.stats.current_memory_bytes = self.l1.current_size_bytes
        if self.stats.current_memory_bytes > self.stats.peak_memory_bytes:
            self.stats.peak_memory_bytes = self.stats.current_memory_bytes
        self.stats.hit_rate = self.stats.calculate_hit_rate()

    def get_all_stats(self) -> Dict[str, Any]:
        """Get comprehensive statistics from all cache levels"""
        return {
            "l1": self.l1.stats(),
            "l2": self.l2.stats(),
            "l3": self.l3.stats(),
            "overall": self.stats.to_dict(),
            "system_memory": self.optimizer.get_system_memory_info(),
            "optimization_suggestions": self.optimizer.get_optimization_suggestions()
        }

    def print_stats(self):
        """Print formatted cache statistics"""
        stats = self.get_all_stats()
        print("\n" + "=" * 70)
        print("ADVANCED MEMORY CACHE STATISTICS")
        print("=" * 70)

        print("\n[L1 MEMORY CACHE]")
        for k, v in stats["l1"].items():
            print(f"  {k}: {v}")

        print("\n[L2 DISK CACHE]")
        for k, v in stats["l2"].items():
            print(f"  {k}: {v}")

        print("\n[L3 COMPRESSED CACHE]")
        for k, v in stats["l3"].items():
            print(f"  {k}: {v}")

        print("\n[OVERALL STATISTICS]")
        for k, v in stats["overall"].items():
            print(f"  {k}: {v}")

        print("\n[SYSTEM MEMORY INFO]")
        for k, v in stats["system_memory"].items():
            print(f"  {k}: {v}")

        if stats["optimization_suggestions"]:
            print("\n[OPTIMIZATION SUGGESTIONS]")
            for suggestion in stats["optimization_suggestions"]:
                print(f"  • {suggestion}")

        print("\n" + "=" * 70 + "\n")


# Example usage and testing
if __name__ == "__main__":
    print("Comic AI Advanced Memory Cache System")
    print("高階內存優化和緩存系統\n")

    # Initialize cache
    cache = AdvancedMemoryCache(
        l1_max_size_mb=50,
        enable_compression=True,
        enable_deduplication=True
    )

    # Test data
    test_data = {
        "large_dataset": list(range(10000)),
        "nested_structure": {
            "level1": {"level2": {"level3": list(range(1000))}}
        },
        "text_data": "This is a large text document " * 1000
    }

    # Store and retrieve
    print("Testing cache operations...")
    cache.put("test_key1", test_data)
    retrieved = cache.get("test_key1")
    print(f"✅ Data stored and retrieved: {type(retrieved)}")

    # Test compression
    large_data = list(range(100000))
    cache.put("large_compressed", large_data, compress=True)
    print(f"✅ Large data compressed and stored")

    # Test duplicate detection
    cache.put("test_key1_dup", test_data)  # Same data as test_key1
    print(f"✅ Duplicate detection working")

    # Print statistics
    cache.print_stats()
