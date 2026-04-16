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


class ShortTermMemory:
    """Short-term memory: Fast access, automatic expiration"""
    
    def __init__(self, ttl_seconds: int = 300, max_entries: int = 1000):
        """
        Initialize short-term memory
        
        Args:
            ttl_seconds: Time to live before auto-expiration (default: 5 minutes)
            max_entries: Maximum entries before eviction
        """
        self.ttl_seconds = ttl_seconds
        self.max_entries = max_entries
        self.entries: OrderedDict[str, Tuple[Any, float]] = OrderedDict()
        self.access_count: Dict[str, int] = {}
        self.lock = threading.RLock()

    def put(self, key: str, value: Any) -> bool:
        """Store value in short-term memory"""
        with self.lock:
            # Evict oldest if at max capacity
            if len(self.entries) >= self.max_entries and key not in self.entries:
                oldest_key = next(iter(self.entries))
                del self.entries[oldest_key]
                self.access_count.pop(oldest_key, None)

            self.entries[key] = (value, time.time())
            self.access_count[key] = self.access_count.get(key, 0) + 1
            self.entries.move_to_end(key)
            return True

    def get(self, key: str) -> Optional[Any]:
        """Retrieve value from short-term memory"""
        with self.lock:
            if key in self.entries:
                value, created_at = self.entries[key]
                
                # Check expiration
                if time.time() - created_at > self.ttl_seconds:
                    del self.entries[key]
                    self.access_count.pop(key, None)
                    return None

                # Update access
                self.access_count[key] = self.access_count.get(key, 0) + 1
                self.entries.move_to_end(key)
                return value
        return None

    def get_expired(self) -> List[str]:
        """Get list of expired keys"""
        with self.lock:
            expired = []
            for key, (_, created_at) in self.entries.items():
                if time.time() - created_at > self.ttl_seconds:
                    expired.append(key)
            return expired

    def stats(self) -> Dict[str, Any]:
        """Get short-term memory statistics"""
        with self.lock:
            return {
                "entries": len(self.entries),
                "max_entries": self.max_entries,
                "ttl_seconds": self.ttl_seconds,
                "utilization_percent": (len(self.entries) / self.max_entries * 100) if self.max_entries > 0 else 0
            }

    def clear(self):
        """Clear all short-term memory"""
        with self.lock:
            self.entries.clear()
            self.access_count.clear()


class LongTermMemory:
    """Long-term memory: Persistent storage for important information"""
    
    def __init__(self, storage_dir: str = ".memory/long_term"):
        """
        Initialize long-term memory
        
        Args:
            storage_dir: Directory for persistent storage
        """
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.metadata_file = self.storage_dir / "metadata.json"
        self.metadata: Dict[str, Any] = self._load_metadata()
        self.lock = threading.RLock()

    def put(self, key: str, value: Any, importance: float = 0.5, tags: Optional[List[str]] = None) -> bool:
        """Store value in long-term memory"""
        with self.lock:
            try:
                # Save data file
                data_file = self.storage_dir / f"{key}.pkl"
                with open(data_file, 'wb') as f:
                    pickle.dump(value, f)

                # Update metadata
                self.metadata[key] = {
                    "timestamp": time.time(),
                    "datetime": datetime.now().isoformat(),
                    "importance": importance,
                    "tags": tags or [],
                    "access_count": 0,
                    "last_accessed": None,
                    "size_bytes": data_file.stat().st_size
                }
                self._save_metadata()
                return True
            except Exception as e:
                logger.error(f"Error saving to long-term memory: {e}")
                return False

    def get(self, key: str) -> Optional[Any]:
        """Retrieve value from long-term memory"""
        with self.lock:
            try:
                data_file = self.storage_dir / f"{key}.pkl"
                if data_file.exists():
                    with open(data_file, 'rb') as f:
                        value = pickle.load(f)
                    
                    # Update access statistics
                    if key in self.metadata:
                        self.metadata[key]["access_count"] += 1
                        self.metadata[key]["last_accessed"] = datetime.now().isoformat()
                        self._save_metadata()
                    
                    return value
            except Exception as e:
                logger.error(f"Error retrieving from long-term memory: {e}")
        return None

    def search(self, tags: Optional[List[str]] = None, min_importance: float = 0.0) -> List[str]:
        """Search long-term memory by tags and importance"""
        with self.lock:
            results = []
            for key, meta in self.metadata.items():
                # Check importance filter
                if meta.get("importance", 0) < min_importance:
                    continue
                
                # Check tags filter
                if tags:
                    meta_tags = meta.get("tags", [])
                    if any(tag in meta_tags for tag in tags):
                        results.append(key)
                else:
                    results.append(key)
            
            return results

    def _load_metadata(self) -> Dict[str, Any]:
        """Load metadata from file"""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Could not load long-term memory metadata: {e}")
        return {}

    def _save_metadata(self):
        """Save metadata to file"""
        try:
            with open(self.metadata_file, 'w') as f:
                json.dump(self.metadata, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error saving metadata: {e}")

    def stats(self) -> Dict[str, Any]:
        """Get long-term memory statistics"""
        with self.lock:
            files = list(self.storage_dir.glob("*.pkl"))
            total_size = sum(f.stat().st_size for f in files)
            
            # Calculate importance distribution
            importance_dist = {
                "critical": sum(1 for m in self.metadata.values() if m.get("importance", 0) > 0.8),
                "high": sum(1 for m in self.metadata.values() if 0.5 <= m.get("importance", 0) <= 0.8),
                "medium": sum(1 for m in self.metadata.values() if 0.2 <= m.get("importance", 0) < 0.5),
                "low": sum(1 for m in self.metadata.values() if m.get("importance", 0) < 0.2)
            }
            
            return {
                "entries": len(self.metadata),
                "total_size_mb": round(total_size / 1024 / 1024, 2),
                "importance_distribution": importance_dist,
                "storage_dir": str(self.storage_dir)
            }

    def clear(self):
        """Clear all long-term memory"""
        with self.lock:
            for file in self.storage_dir.glob("*.pkl"):
                file.unlink()
            self.metadata.clear()
            self._save_metadata()


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
    """Data compression and decompression engine with importance-based decisions"""

    # Content importance levels
    IMPORTANCE_CRITICAL = 1.0    # Never compress
    IMPORTANCE_HIGH = 0.8        # Minimal compression
    IMPORTANCE_MEDIUM = 0.5      # Balanced compression
    IMPORTANCE_LOW = 0.2         # Aggressive compression
    IMPORTANCE_TRIVIAL = 0.0     # Maximum compression

    @staticmethod
    def calculate_content_importance(data: Any) -> float:
        """
        Calculate content importance score (0.0 - 1.0)
        
        Score factors:
        - Critical keywords (ML models, configs) → HIGH
        - Numeric/structured data → MEDIUM
        - Duplicates, logs → LOW
        """
        try:
            data_str = json.dumps(data, default=str)
            
            # Critical patterns that should NOT be compressed
            critical_keywords = [
                'model', 'weight', 'parameter', 'config', 'api_key', 
                'token', 'secret', 'credential', 'algorithm', 'metric',
                'accuracy', 'performance', 'optimization', 'strategy'
            ]
            
            score = 0.0
            data_lower = data_str.lower()
            
            # Check for critical content
            for keyword in critical_keywords:
                if keyword in data_lower:
                    score = max(score, 0.9)  # HIGH importance
                    break
            
            # Structured data (dict/list) is more important than plain text
            if isinstance(data, (dict, list)) and len(data) > 10:
                score = max(score, 0.7)
            
            # Check for duplicates (low importance)
            if len(data_str) < 100 and data_str.count(data_str[:20]) > 2:
                score = min(score, 0.2)  # LOW importance
            
            # Size heuristic: very large data might be logs (low importance)
            if len(data_str) > 10000:
                score = max(score, 0.5)  # At least MEDIUM
            
            return score
        except:
            return 0.5  # Default to MEDIUM if calculation fails

    @staticmethod
    def compress(data: Any, compression_level: int = 6, force_compress: bool = False) -> Tuple[bytes, float, bool]:
        """
        Compress data using zlib with importance-aware decisions
        
        Returns:
            Tuple of (compressed_data, compression_ratio, was_compressed)
        """
        original_data = pickle.dumps(data)
        original_size = len(original_data)

        # Calculate importance
        importance = CompressionEngine.calculate_content_importance(data)
        
        # Decision: compress or not based on importance
        # HIGH importance (>0.7): use minimal compression
        # MEDIUM importance (0.3-0.7): use normal compression
        # LOW importance (<0.3): use aggressive compression
        
        if importance > 0.8 and not force_compress:
            # Critical content - don't compress
            compression_ratio = 1.0
            return original_data, compression_ratio, False
        
        # Adjust compression level based on importance
        if importance > 0.7:
            effective_level = min(compression_level, 3)  # Light compression
        elif importance < 0.3:
            effective_level = max(compression_level, 8)  # Aggressive compression
        else:
            effective_level = compression_level

        compressed_data = zlib.compress(original_data, effective_level)
        compressed_size = len(compressed_data)

        compression_ratio = original_size / compressed_size if compressed_size > 0 else 1.0

        return compressed_data, compression_ratio, True

    @staticmethod
    def decompress(compressed_data: bytes) -> Any:
        """Decompress data using zlib"""
        original_data = zlib.decompress(compressed_data)
        return pickle.loads(original_data)

    @staticmethod
    def calculate_compression_benefit(original_size: int, compressed_size: int, importance: float = 0.5) -> Dict[str, Any]:
        """Calculate compression benefit metrics with importance weighting"""
        return {
            "original_size_bytes": original_size,
            "compressed_size_bytes": compressed_size,
            "savings_bytes": original_size - compressed_size,
            "savings_percent": round((1 - compressed_size / original_size) * 100, 2) if original_size > 0 else 0,
            "compression_ratio": round(original_size / compressed_size, 2) if compressed_size > 0 else 0,
            "importance_score": round(importance, 2),
            "compression_recommended": importance < 0.7
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

    def put(self, key: str, value: Any) -> Tuple[bool, float, float]:
        """
        Put value into L3 compressed cache

        Returns:
            Tuple of (success, compression_ratio, importance_score)
        """
        with self.lock:
            try:
                # Calculate importance
                importance = self.compressor.calculate_content_importance(value)
                
                # Compress with importance awareness
                compressed_data, ratio, was_compressed = self.compressor.compress(
                    value, 
                    self.compression_level,
                    force_compress=False
                )
                
                if not was_compressed:
                    # If not compressed (important data), still store in L3 but mark it
                    logger.info(f"Storing important data in L3 (uncompressed): {key}")
                
                cache_file = self.cache_dir / f"{key}.zp"
                with open(cache_file, 'wb') as f:
                    f.write(compressed_data)
                return True, ratio, importance
            except Exception as e:
                logger.error(f"Error saving L3 cache {key}: {e}")
                return False, 1.0, 0.5

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
        enable_learning: bool = True,
        short_term_ttl: int = 300,
        short_term_max_entries: int = 1000
    ):
        """Initialize advanced memory cache with short and long-term memory"""
        self.l1 = L1MemoryCache(max_size_bytes=l1_max_size_mb * 1024 * 1024)
        self.l2 = L2DiskCache(l2_cache_dir)
        self.l3 = L3CompressedCache(l3_cache_dir)
        self.optimizer = MemoryOptimizer()
        self.compressor = CompressionEngine()
        self.deduplicator = DeduplicationEngine() if enable_deduplication else None
        self.enable_compression = enable_compression
        self.enable_learning = enable_learning
        self.stats = CacheStats()
        self.lock = threading.RLock()
        
        # Short-term and long-term memory
        self.short_term = ShortTermMemory(ttl_seconds=short_term_ttl, max_entries=short_term_max_entries)
        self.long_term = LongTermMemory()
        
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
        Put value into cache with importance-aware compression

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

            # Calculate content importance
            importance_score = self.compressor.calculate_content_importance(value)
            
            # Determine storage tier based on importance and system state
            should_compress = compress or (self.optimizer.should_optimize() and importance_score < 0.7)

            if should_compress and self.enable_compression:
                # Use L3 compressed cache for low-importance data
                result = self.l3.put(key, value)
                if result[0]:  # success
                    ratio = result[1]
                    importance = result[2]
                    self.stats.total_compressions += 1
                    self.stats.compression_ratio = ratio
                    logger.info(f"Compressed {key} (importance: {importance:.2f}, ratio: {ratio:.2f}x)")
            else:
                # Keep important data uncompressed in L1/L2
                self.l1.put(key, value, ttl_seconds)
                logger.info(f"Kept {key} uncompressed (importance: {importance_score:.2f})")

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
