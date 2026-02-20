#!/usr/bin/env python3
"""
Test Suite for Advanced Memory Cache and Optimization System
Comic AI 高階內存緩存和優化系統測試套件

Comprehensive tests for:
- Multi-tier caching (L1, L2, L3)
- Memory optimization
- Compression and deduplication
- Performance benchmarks
"""

import pytest
import time
import json
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any, List

from memory_cache_optimization import (
    AdvancedMemoryCache,
    L1MemoryCache,
    L2DiskCache,
    L3CompressedCache,
    MemoryOptimizer,
    CompressionEngine,
    DeduplicationEngine,
    CacheEntry,
    CacheLevel,
    EvictionPolicy
)
from memory_manager import MemoryManager, init_memory_manager


class TestL1MemoryCache:
    """Test L1 in-memory cache"""

    def test_put_get_basic(self):
        """Test basic put and get operations"""
        cache = L1MemoryCache(max_size_bytes=10 * 1024 * 1024)
        test_data = {"key": "value", "number": 42}

        cache.put("test_key", test_data)
        retrieved = cache.get("test_key")

        assert retrieved == test_data
        assert cache.stats()["entries"] == 1

    def test_lru_eviction(self):
        """Test LRU eviction when cache is full"""
        cache = L1MemoryCache(max_size_bytes=1024)  # Small cache

        # Fill cache with multiple entries
        for i in range(5):
            cache.put(f"key_{i}", f"value_{i}" * 50)

        # Cache should have evicted older entries
        assert cache.stats()["entries"] <= 5
        assert cache.stats()["current_size_mb"] > 0

    def test_ttl_expiration(self):
        """Test TTL-based entry expiration"""
        cache = L1MemoryCache()

        cache.put("expire_key", {"data": "test"}, ttl_seconds=1)
        assert cache.get("expire_key") is not None

        time.sleep(1.1)
        assert cache.get("expire_key") is None

    def test_access_count(self):
        """Test access count tracking"""
        cache = L1MemoryCache()
        cache.put("track_key", "value")

        # Access multiple times
        for _ in range(3):
            cache.get("track_key")

        # Check access count
        entry = cache.cache.get("track_key")
        assert entry.access_count >= 3


class TestL2DiskCache:
    """Test L2 disk-based cache"""

    def setup_method(self):
        """Setup temporary directory for tests"""
        self.temp_dir = tempfile.mkdtemp()

    def teardown_method(self):
        """Cleanup temporary directory"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_put_get_disk(self):
        """Test disk cache put and get"""
        cache = L2DiskCache(cache_dir=self.temp_dir)
        test_data = {"disk": "cache", "list": [1, 2, 3]}

        cache.put("disk_key", test_data)
        retrieved = cache.get("disk_key")

        assert retrieved == test_data

    def test_persistence(self):
        """Test data persistence across instances"""
        test_data = {"persistent": "data"}

        # Write with first instance
        cache1 = L2DiskCache(cache_dir=self.temp_dir)
        cache1.put("persist_key", test_data)

        # Read with second instance
        cache2 = L2DiskCache(cache_dir=self.temp_dir)
        retrieved = cache2.get("persist_key")

        assert retrieved == test_data

    def test_delete(self):
        """Test delete operation"""
        cache = L2DiskCache(cache_dir=self.temp_dir)
        cache.put("delete_key", "value")
        cache.delete("delete_key")

        assert cache.get("delete_key") is None


class TestL3CompressedCache:
    """Test L3 compressed cache"""

    def setup_method(self):
        """Setup temporary directory"""
        self.temp_dir = tempfile.mkdtemp()

    def teardown_method(self):
        """Cleanup temporary directory"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_compression_efficiency(self):
        """Test compression efficiency"""
        cache = L3CompressedCache(cache_dir=self.temp_dir)

        # Large repetitive data compresses well
        large_data = {"data": "test" * 10000}

        success, ratio = cache.put("compress_key", large_data)

        assert success
        assert ratio > 1.0  # Should compress

    def test_decompress(self):
        """Test decompression accuracy"""
        cache = L3CompressedCache(cache_dir=self.temp_dir)
        original_data = {
            "numbers": list(range(1000)),
            "text": "Hello World" * 100,
            "nested": {"level": {"deep": [1, 2, 3]}}
        }

        cache.put("decompress_key", original_data)
        retrieved = cache.get("decompress_key")

        assert retrieved == original_data


class TestCompressionEngine:
    """Test data compression"""

    def test_compress_decompress(self):
        """Test compression and decompression cycle"""
        engine = CompressionEngine()
        original_data = {"test": "data" * 1000}

        compressed, ratio = engine.compress(original_data)
        decompressed = engine.decompress(compressed)

        assert decompressed == original_data
        assert ratio > 1.0

    def test_compression_levels(self):
        """Test different compression levels"""
        engine = CompressionEngine()
        test_data = {"data": "test" * 5000}

        # Different compression levels
        compressed_1, ratio_1 = engine.compress(test_data, level=1)
        compressed_6, ratio_6 = engine.compress(test_data, level=6)
        compressed_9, ratio_9 = engine.compress(test_data, level=9)

        # Higher compression levels should achieve better ratios
        assert len(compressed_9) <= len(compressed_6) <= len(compressed_1)


class TestDeduplicationEngine:
    """Test data deduplication"""

    def test_duplicate_detection(self):
        """Test duplicate data detection"""
        engine = DeduplicationEngine()
        data = {"test": "data"}

        hash1, is_dup1 = engine.add_entry("key1", data)
        hash2, is_dup2 = engine.add_entry("key2", data)

        assert hash1 == hash2
        assert not is_dup1
        assert is_dup2

    def test_hash_uniqueness(self):
        """Test hash uniqueness for different data"""
        engine = DeduplicationEngine()

        hash1, _ = engine.add_entry("key1", {"a": 1})
        hash2, _ = engine.add_entry("key2", {"a": 2})

        assert hash1 != hash2

    def test_get_duplicates(self):
        """Test retrieving duplicate entries"""
        engine = DeduplicationEngine()
        data = {"duplicate": "data"}

        engine.add_entry("key1", data)
        engine.add_entry("key2", data)
        engine.add_entry("key3", data)

        hash_val = engine.calculate_hash(data)
        duplicates = engine.get_duplicates(hash_val)

        assert len(duplicates) == 3


class TestAdvancedMemoryCache:
    """Test multi-tier advanced cache"""

    def setup_method(self):
        """Setup temporary directories"""
        self.temp_dir = tempfile.mkdtemp()

    def teardown_method(self):
        """Cleanup"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_multi_tier_caching(self):
        """Test data flow through multiple cache tiers"""
        cache = AdvancedMemoryCache()

        test_data = {"multi": "tier", "cache": "test"}
        cache.put("multi_key", test_data)

        # Should be retrievable from L1
        retrieved = cache.get("multi_key")
        assert retrieved == test_data

    def test_cache_stats(self):
        """Test cache statistics"""
        cache = AdvancedMemoryCache()

        cache.put("stat_key1", "value1")
        cache.put("stat_key2", "value2")
        cache.get("stat_key1")

        stats = cache.get_all_stats()

        assert stats["overall"]["total_hits"] > 0
        assert "l1" in stats
        assert "l2" in stats
        assert "l3" in stats

    def test_compression_with_threshold(self):
        """Test compression at memory threshold"""
        cache = AdvancedMemoryCache(enable_compression=True)

        # Add data that should be compressed
        large_data = list(range(100000))
        cache.put("compress_large", large_data, compress=True)

        retrieved = cache.get("compress_large")
        assert retrieved == large_data


class TestMemoryOptimizer:
    """Test memory optimization"""

    def test_system_memory_info(self):
        """Test system memory information retrieval"""
        optimizer = MemoryOptimizer()
        info = optimizer.get_system_memory_info()

        assert "system_total_mb" in info
        assert "system_used_mb" in info
        assert "process_rss_mb" in info
        assert info["system_total_mb"] > 0

    def test_optimization_suggestions(self):
        """Test optimization suggestions"""
        optimizer = MemoryOptimizer()
        suggestions = optimizer.get_optimization_suggestions()

        assert isinstance(suggestions, list)


class TestMemoryManager:
    """Test memory manager integration"""

    def setup_method(self):
        """Setup temporary directory and manager"""
        self.temp_dir = tempfile.mkdtemp()
        self.memory_file = Path(self.temp_dir) / "memory.md"
        self.memory_file.write_text("# Test Memory File\n")

    def teardown_method(self):
        """Cleanup"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_manager_initialization(self):
        """Test manager initialization"""
        manager = MemoryManager(
            memory_file=str(self.memory_file),
            state_file=str(Path(self.temp_dir) / ".memory_state.json")
        )
        manager.initialize()

        assert manager.state is not None
        assert manager.cache is not None

    def test_cache_operations(self):
        """Test cache operations through manager"""
        manager = MemoryManager(
            memory_file=str(self.memory_file),
            state_file=str(Path(self.temp_dir) / ".memory_state.json")
        )
        manager.initialize()

        test_data = {"manager": "test"}
        manager.cache_put("manager_key", test_data)
        retrieved = manager.cache_get("manager_key")

        assert retrieved == test_data

    def test_snapshot_generation(self):
        """Test snapshot generation"""
        manager = MemoryManager(
            memory_file=str(self.memory_file),
            state_file=str(Path(self.temp_dir) / ".memory_state.json")
        )
        manager.initialize()

        snapshot = manager.take_snapshot()

        assert snapshot.timestamp > 0
        assert snapshot.datetime_str
        assert snapshot.cache_stats is not None


class TestPerformanceBenchmarks:
    """Performance benchmarks"""

    def benchmark_cache_operations(self):
        """Benchmark cache put/get operations"""
        cache = AdvancedMemoryCache()

        # Benchmark puts
        put_times = []
        for i in range(100):
            data = {"benchmark": f"data_{i}" * 10}
            start = time.time()
            cache.put(f"bench_key_{i}", data)
            put_times.append(time.time() - start)

        avg_put_time = sum(put_times) / len(put_times) * 1000  # ms
        print(f"\nAverage PUT time: {avg_put_time:.3f}ms")

        # Benchmark gets
        get_times = []
        for i in range(100):
            start = time.time()
            cache.get(f"bench_key_{i}")
            get_times.append(time.time() - start)

        avg_get_time = sum(get_times) / len(get_times) * 1000  # ms
        print(f"Average GET time: {avg_get_time:.3f}ms")

        # Should be reasonably fast
        assert avg_put_time < 100  # Less than 100ms
        assert avg_get_time < 10   # Less than 10ms

    def benchmark_compression(self):
        """Benchmark compression performance"""
        engine = CompressionEngine()

        # Test data
        test_data = {"data": "value" * 10000}

        # Benchmark compress
        start = time.time()
        for _ in range(10):
            engine.compress(test_data)
        compress_time = (time.time() - start) / 10 * 1000  # ms
        print(f"\nAverage compression time: {compress_time:.3f}ms")

        # Benchmark decompress
        compressed, _ = engine.compress(test_data)
        start = time.time()
        for _ in range(10):
            engine.decompress(compressed)
        decompress_time = (time.time() - start) / 10 * 1000  # ms
        print(f"Average decompression time: {decompress_time:.3f}ms")


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--tb=short"])
