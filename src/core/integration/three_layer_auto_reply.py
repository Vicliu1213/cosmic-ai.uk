#!/usr/bin/env python3
"""
三層自動回復系統 (Three-Layer Auto Reply System)
Three-Layer Auto Reply System for Comic AI

包含三個回復層級:
1. 快速回復 (Quick Reply) - <100ms，缓存响应
2. 标准回復 (Standard Reply) - <500ms，内存处理
3. 深度回復 (Deep Reply) - <2s，完整分析

用途:
- 自动处理用户请求
- 多智能体协调响应
- 自适应回复深度
"""

import json
import time
import logging
from typing import Dict, List, Optional, Any, Callable, Tuple
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, asdict, field
import threading
from queue import Queue, PriorityQueue

logger = logging.getLogger(__name__)

class ReplyLevel(Enum):
    """回復層級枚舉"""
    QUICK = 1      # 快速回復 (<100ms)
    STANDARD = 2   # 標準回復 (<500ms)
    DEEP = 3       # 深度回復 (<2s)

@dataclass
class UserQuery:
    """用户查询數據結構"""
    query_id: str
    content: str
    user_id: str
    timestamp: datetime = field(default_factory=datetime.now)
    priority: int = 5  # 1-10，10為最高優先級
    context: Dict[str, Any] = field(default_factory=dict)
    
    def get_age_ms(self) -> float:
        """获取查询年龄（毫秒）"""
        return (datetime.now() - self.timestamp).total_seconds() * 1000

@dataclass
class AutoReply:
    """自動回復數據結構"""
    reply_id: str
    query_id: str
    level: ReplyLevel
    content: str
    confidence: float  # 0.0-1.0
    processing_time_ms: float
    source: str  # 'quick_cache', 'standard_process', 'deep_analysis'
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

class QuickReplyCache:
    """快速回復緩存層 (<100ms)"""
    
    def __init__(self, max_size: int = 1000, ttl_seconds: int = 3600) -> Any:
        """初始化快速回復緩存
        
        Args:
            max_size: 最大緩存項數
            ttl_seconds: 缓存有效期（秒）
        """
        self.cache: Dict[str, Tuple[str, float]] = {}  # {query_hash: (response, timestamp)}
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self.lock = threading.RLock()
        self.hit_count = 0
        self.miss_count = 0
    
    def get(self, query_hash: str) -> Optional[str]:
        """從緩存獲取回復"""
        with self.lock:
            if query_hash not in self.cache:
                self.miss_count += 1
                return None
            
            response, timestamp = self.cache[query_hash]
            
            # 检查过期
            if time.time() - timestamp > self.ttl_seconds:
                del self.cache[query_hash]
                self.miss_count += 1
                return None
            
            self.hit_count += 1
            return response
    
    def put(self, query_hash: str, response: str) -> None:
        """將回復存入緩存"""
        with self.lock:
            if len(self.cache) >= self.max_size:
                # LRU: 删除最旧的项
                oldest_key = min(self.cache.keys(), 
                                key=lambda k: self.cache[k][1])
                del self.cache[oldest_key]
            
            self.cache[query_hash] = (response, time.time())
    
    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计"""
        total = self.hit_count + self.miss_count
        hit_rate = self.hit_count / total if total > 0 else 0
        
        return {
            'cache_size': len(self.cache),
            'max_size': self.max_size,
            'total_requests': total,
            'hit_count': self.hit_count,
            'miss_count': self.miss_count,
            'hit_rate': hit_rate
        }

class StandardReplyProcessor:
    """标准回復處理層 (<500ms)"""
    
    def __init__(self, max_workers: int = 4) -> Any:
        """初始化标准回復處理器
        
        Args:
            max_workers: 最大工作線程數
        """
        self.max_workers = max_workers
        self.processors: Dict[str, Callable] = {}
        self.response_queue: Queue = Queue()
        self.stats = {
            'processed': 0,
            'avg_time_ms': 0,
            'total_time_ms': 0
        }
        self.lock = threading.RLock()
    
    def register_processor(self, key: str, processor: Callable) -> None:
        """註冊處理器"""
        self.processors[key] = processor
    
    def process(self, query: UserQuery) -> Optional[AutoReply]:
        """處理標準查詢"""
        start_time = time.time()
        
        try:
            # 根據查詢內容分類
            processor_key = self._classify_query(query)
            
            if processor_key not in self.processors:
                processor_key = 'default'
            
            processor = self.processors.get(processor_key)
            if not processor:
                return None
            
            # 执行处理器
            response = processor(query)
            processing_time = (time.time() - start_time) * 1000
            
            # 更新统计
            with self.lock:
                self.stats['processed'] += 1
                self.stats['total_time_ms'] += processing_time
                self.stats['avg_time_ms'] = (
                    self.stats['total_time_ms'] / self.stats['processed']
                )
            
            if processing_time > 500:
                logger.warning(f"⚠️ 標準回復超時: {processing_time:.2f}ms")
            
            return AutoReply(
                reply_id=f"reply_{query.query_id}",
                query_id=query.query_id,
                level=ReplyLevel.STANDARD,
                content=response,
                confidence=0.7,
                processing_time_ms=processing_time,
                source='standard_process'
            )
        
        except Exception as e:
            logger.error(f"❌ 標準回復失敗: {e}")
            return None
    
    def _classify_query(self, query: UserQuery) -> str:
        """分類查詢"""
        content = query.content.lower()
        
        if 'status' in content or '狀態' in content:
            return 'status'
        elif 'list' in content or '列表' in content:
            return 'list'
        elif 'help' in content or '幫助' in content:
            return 'help'
        else:
            return 'default'
    
    def get_stats(self) -> Dict[str, Any]:
        """获取統計信息"""
        with self.lock:
            return self.stats.copy()

class DeepReplyAnalyzer:
    """深度回復分析層 (<2s)"""
    
    def __init__(self) -> Any:
        """初始化深度分析器"""
        self.analyzers: Dict[str, Callable] = {}
        self.stats = {
            'analyzed': 0,
            'avg_time_ms': 0,
            'total_time_ms': 0
        }
        self.lock = threading.RLock()
    
    def register_analyzer(self, key: str, analyzer: Callable) -> None:
        """註冊分析器"""
        self.analyzers[key] = analyzer
    
    def analyze(self, query: UserQuery, context: Optional[Dict] = None) -> Optional[AutoReply]:
        """深度分析查詢"""
        start_time = time.time()
        
        try:
            # 執行多個分析器
            analysis_results = []
            
            for key, analyzer in self.analyzers.items():
                try:
                    result = analyzer(query, context)
                    if result:
                        analysis_results.append(result)
                except Exception as e:
                    logger.warning(f"分析器 {key} 失敗: {e}")
            
            # 綜合分析結果
            if not analysis_results:
                return None
            
            combined_response = self._combine_analysis(analysis_results)
            processing_time = (time.time() - start_time) * 1000
            
            # 更新統計
            with self.lock:
                self.stats['analyzed'] += 1
                self.stats['total_time_ms'] += processing_time
                self.stats['avg_time_ms'] = (
                    self.stats['total_time_ms'] / self.stats['analyzed']
                )
            
            if processing_time > 2000:
                logger.warning(f"⚠️ 深度分析超時: {processing_time:.2f}ms")
            
            return AutoReply(
                reply_id=f"reply_{query.query_id}",
                query_id=query.query_id,
                level=ReplyLevel.DEEP,
                content=combined_response,
                confidence=0.95,
                processing_time_ms=processing_time,
                source='deep_analysis',
                metadata={'analysis_count': len(analysis_results)}
            )
        
        except Exception as e:
            logger.error(f"❌ 深度分析失敗: {e}")
            return None
    
    def _combine_analysis(self, results: List[str]) -> str:
        """綜合分析結果"""
        combined = "\n".join([
            f"【分析 {i+1}】\n{result}"
            for i, result in enumerate(results)
        ])
        return combined
    
    def get_stats(self) -> Dict[str, Any]:
        """获取統計信息"""
        with self.lock:
            return self.stats.copy()

class ThreeLayerAutoReplySystem:
    """三層自動回復系統主類"""
    
    def __init__(self, cache_size: int = 1000) -> Any:
        """初始化三層系統
        
        Args:
            cache_size: 快速回復緩存大小
        """
        self.quick_cache = QuickReplyCache(max_size=cache_size)
        self.standard_processor = StandardReplyProcessor()
        self.deep_analyzer = DeepReplyAnalyzer()
        
        self.query_queue: PriorityQueue = PriorityQueue()
        self.running = False
        self.worker_threads: List[threading.Thread] = []
        
        self.logger = logging.getLogger(__name__)
        self._setup_default_processors()
    
    def _setup_default_processors(self) -> None:
        """設置默認處理器"""
        def default_processor(query: UserQuery) -> str:
            return f"已收到您的查詢: {query.content}"
        
        def status_processor(query: UserQuery) -> str:
            return "系統狀態: 正常運行 ✅"
        
        def help_processor(query: UserQuery) -> str:
            return "這是幫助信息。請提供更多詳細信息。"
        
        self.standard_processor.register_processor('default', default_processor)
        self.standard_processor.register_processor('status', status_processor)
        self.standard_processor.register_processor('help', help_processor)
    
    def register_analyzer(self, key: str, analyzer: Callable) -> None:
        """註冊深度分析器"""
        self.deep_analyzer.register_analyzer(key, analyzer)
    
    def process_query(self, query: UserQuery) -> Optional[AutoReply]:
        """處理查詢 - 自動選擇合適的層級
        
        返回流程:
        1. 快速回復 (缓存检查)
        2. 標準回復 (內存處理)
        3. 深度回復 (完整分析)
        """
        start_time = time.time()
        
        # 生成查詢哈希
        query_hash = hash(query.content) % (10 ** 8)
        query_hash_str = f"q_{query_hash}"
        
        # 第1層: 快速回復
        cached_reply = self.quick_cache.get(query_hash_str)
        if cached_reply:
            return AutoReply(
                reply_id=f"reply_{query.query_id}",
                query_id=query.query_id,
                level=ReplyLevel.QUICK,
                content=cached_reply,
                confidence=0.9,
                processing_time_ms=(time.time() - start_time) * 1000,
                source='quick_cache'
            )
        
        # 第2層: 標準回復
        standard_reply = self.standard_processor.process(query)
        if standard_reply:
            self.quick_cache.put(query_hash_str, standard_reply.content)
            return standard_reply
        
        # 第3層: 深度回復
        deep_reply = self.deep_analyzer.analyze(query, query.context)
        if deep_reply:
            self.quick_cache.put(query_hash_str, deep_reply.content)
            return deep_reply
        
        return None
    
    def get_system_stats(self) -> Dict[str, Any]:
        """获取系統統計"""
        return {
            'quick_cache': self.quick_cache.get_stats(),
            'standard_processor': self.standard_processor.get_stats(),
            'deep_analyzer': self.deep_analyzer.get_stats(),
            'timestamp': datetime.now().isoformat()
        }
    
    def print_status_report(self) -> None:
        """打印狀態報告"""
        stats = self.get_system_stats()
        
        print("\n" + "=" * 70)
        print("📊 三層自動回復系統 - 狀態報告")
        print("=" * 70)
        
        # 快速回復緩存
        quick_stats = stats['quick_cache']
        print(f"\n🚀 第1層 - 快速回復 (Quick Cache)")
        print(f"   緩存大小: {quick_stats['cache_size']}/{quick_stats['max_size']}")
        print(f"   命中率: {quick_stats['hit_rate']:.1%}")
        print(f"   總請求: {quick_stats['total_requests']}")
        
        # 標準回復
        standard_stats = stats['standard_processor']
        print(f"\n⚙️  第2層 - 標準回復 (Standard)")
        print(f"   已處理: {standard_stats['processed']} 個查詢")
        print(f"   平均時間: {standard_stats['avg_time_ms']:.2f}ms")
        
        # 深度回復
        deep_stats = stats['deep_analyzer']
        print(f"\n🧠 第3層 - 深度分析 (Deep)")
        print(f"   已分析: {deep_stats['analyzed']} 個查詢")
        print(f"   平均時間: {deep_stats['avg_time_ms']:.2f}ms")
        
        print("\n" + "=" * 70)

def demo() -> Any:
    """演示三層自動回復系統"""
    print("\n" + "=" * 70)
    print("🎯 三層自動回復系統演示")
    print("=" * 70)
    
    # 初始化系統
    system = ThreeLayerAutoReplySystem(cache_size=100)
    
    # 註冊深度分析器
    def sentiment_analyzer(query: UserQuery, context: Optional[Dict]) -> str:
        return "情感分析: 中性"
    
    def intent_analyzer(query: UserQuery, context: Optional[Dict]) -> str:
        return "意圖識別: 信息查詢"
    
    system.register_analyzer('sentiment', sentiment_analyzer)
    system.register_analyzer('intent', intent_analyzer)
    
    # 測試查詢
    test_queries = [
        UserQuery("q1", "系統狀態如何?", "user1"),
        UserQuery("q2", "幫助我", "user1"),
        UserQuery("q3", "系統狀態如何?", "user1"),  # 緩存命中
        UserQuery("q4", "顯示列表", "user1"),
    ]
    
    print("\n📝 處理查詢:\n")
    
    for query in test_queries:
        reply = system.process_query(query)
        
        if reply:
            print(f"查詢: {query.content}")
            print(f"層級: {reply.level.name}")
            print(f"回復: {reply.content}")
            print(f"時間: {reply.processing_time_ms:.2f}ms")
            print(f"來源: {reply.source}")
            print()
    
    # 顯示統計
    system.print_status_report()

if __name__ == "__main__":
    demo()
