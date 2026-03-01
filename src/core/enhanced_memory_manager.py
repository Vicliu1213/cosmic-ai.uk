#!/usr/bin/env python3
"""
增強記憶力管理系統 (Enhanced Memory Manager)
設計用於交易系統的分層記憶策略，支持快速恢復和自動清理

核心特性:
- 分層記憶 (Tiered Memory): 熱(Hot) / 溫(Warm) / 冷(Cold)
- 自動清理機制: 防止內存溢出
- 快速上下文恢復: <50ms 恢復
- 會話追蹤: 自動記錄對話歷史
"""

import json
import os
import time
import hashlib
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum

# 設置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MemoryTier(Enum):
    """記憶層級 (分層策略)"""
    HOT = "hot"  # 熱記憶: 最近 24 小時，頻繁訪問
    WARM = "warm"  # 溫記憶: 1-7 天，中等訪問
    COLD = "cold"  # 冷記憶: 7+ 天，歸檔

@dataclass
class MemoryEntry:
    """單個記憶項目"""
    key: str  # 唯一標識
    content: Dict[str, Any]  # 實際內容
    tier: MemoryTier  # 所屬層級
    created_at: float  # 創建時間戳
    accessed_at: float  # 最後訪問時間戳
    access_count: int = 0  # 訪問次數
    size_bytes: int = 0  # 內容大小

@dataclass
class SessionContext:
    """會話上下文 (快速恢復用)"""
    session_id: str  # 會話 ID
    started_at: float  # 開始時間
    last_activity: float  # 最後活動時間
    active_tasks: List[str] = field(default_factory=list)  # 進行中任務
    recent_exchanges: List[Dict[str, str]] = field(default_factory=list)  # 最近對話
    trading_state: Dict[str, Any] = field(default_factory=dict)  # 交易狀態
    memory_summary: str = ""  # 會話記憶摘要

class EnhancedMemoryManager:
    """增強記憶管理器 (核心類)"""

    def __init__(
        self,
        data_dir: str = "/root/comic_ai/data/enhanced_memory",
        max_hot_size_mb: int = 50,
        max_warm_size_mb: int = 200,
        max_total_size_mb: int = 500
    ):
        """
        初始化記憶管理器

        Args:
            data_dir: 數據存儲目錄
            max_hot_size_mb: 熱記憶最大大小 (MB)
            max_warm_size_mb: 溫記憶最大大小 (MB)
            max_total_size_mb: 總記憶最大大小 (MB)
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # 記憶層級大小限制
        self.max_sizes: Dict[MemoryTier, float] = {
            MemoryTier.HOT: float(max_hot_size_mb * 1024 * 1024),
            MemoryTier.WARM: float(max_warm_size_mb * 1024 * 1024),
            MemoryTier.COLD: float('inf')
        }
        self.max_total_size: float = float(max_total_size_mb * 1024 * 1024)

        # 記憶層級文件路徑
        self.tier_dirs = {
            tier: self.data_dir / tier.value
            for tier in MemoryTier
        }
        for tier_dir in self.tier_dirs.values():
            tier_dir.mkdir(parents=True, exist_ok=True)

        # 會話上下文
        self.current_session: Optional[SessionContext] = None
        self.session_file = self.data_dir / "current_session.json"

        # 指標
        self.stats = {
            'total_memories': 0,
            'total_size_mb': 0,
            'access_count': 0,
            'cleanup_count': 0
        }

        logger.info(f"記憶管理器初始化完成: {self.data_dir}")

    def start_session(self, session_id: str) -> SessionContext:
        """啟動新會話或恢復現有會話"""
        now = time.time()

        # 嘗試恢復現有會話
        if self.session_file.exists():
            try:
                with open(self.session_file, 'r') as f:
                    session_data = json.load(f)
                    self.current_session = SessionContext(**session_data)
                    self.current_session.last_activity = now
                    logger.info(f"恢復會話: {self.current_session.session_id}")
                    return self.current_session
            except Exception as e:
                logger.warning(f"恢復會話失敗: {e}")

        # 創建新會話
        self.current_session = SessionContext(
            session_id=session_id,
            started_at=now,
            last_activity=now
        )
        self._save_session()
        logger.info(f"創建新會話: {session_id}")
        return self.current_session

    def add_memory(
        self,
        key: str,
        content: Dict[str, Any],
        tier: MemoryTier = MemoryTier.HOT
    ) -> bool:
        """
        添加記憶項目

        Args:
            key: 唯一標識
            content: 記憶內容
            tier: 記憶層級

        Returns:
            是否成功添加
        """
        now = time.time()

        # 計算大小
        content_str = json.dumps(content)
        size_bytes = len(content_str.encode('utf-8'))

        # 檢查大小限制
        if size_bytes > self.max_sizes[tier]:
            logger.warning(f"記憶項目過大: {key} ({size_bytes/1024/1024:.2f}MB)")
            return False

        # 創建記憶項目
        entry = MemoryEntry(
            key=key,
            content=content,
            tier=tier,
            created_at=now,
            accessed_at=now,
            access_count=1,
            size_bytes=size_bytes
        )

        # 保存到文件
        tier_dir = self.tier_dirs[tier]
        file_path = tier_dir / f"{key}.json"

        try:
            with open(file_path, 'w') as f:
                json.dump({
                    'key': entry.key,
                    'content': entry.content,
                    'tier': entry.tier.value,
                    'created_at': entry.created_at,
                    'accessed_at': entry.accessed_at,
                    'access_count': entry.access_count,
                    'size_bytes': entry.size_bytes
                }, f, indent=2)

            self.stats['total_memories'] += 1
            self.stats['total_size_mb'] = self._get_total_size_mb()

            # 檢查是否需要清理
            if self.stats['total_size_mb'] * 1024 * 1024 > self.max_total_size * 0.8:
                self._cleanup_memories()

            logger.debug(f"記憶已添加: {key} (tier={tier.value}, size={size_bytes})")
            return True

        except Exception as e:
            logger.error(f"保存記憶失敗: {key}, 錯誤: {e}")
            return False

    def get_memory(self, key: str) -> Optional[Dict[str, Any]]:
        """
        獲取記憶項目

        Args:
            key: 記憶標識

        Returns:
            記憶內容或 None
        """
        # 在所有層級中搜索
        for tier in MemoryTier:
            file_path = self.tier_dirs[tier] / f"{key}.json"
            if file_path.exists():
                try:
                    with open(file_path, 'r') as f:
                        entry_data = json.load(f)
                        entry = MemoryEntry(**entry_data)

                        # 更新訪問信息
                        entry.accessed_at = time.time()
                        entry.access_count += 1

                        # 保存更新
                        self._save_entry(entry)

                        self.stats['access_count'] += 1
                        logger.debug(f"記憶已訪問: {key} (訪問次數: {entry.access_count})")
                        return entry.content

                except Exception as e:
                    logger.error(f"讀取記憶失敗: {key}, 錯誤: {e}")
                    return None

        logger.warning(f"記憶未找到: {key}")
        return None

    def update_session_context(self, **kwargs) -> None:
        """更新會話上下文"""
        if not self.current_session:
            return

        now = time.time()
        self.current_session.last_activity = now

        for key, value in kwargs.items():
            if hasattr(self.current_session, key):
                setattr(self.current_session, key, value)

        self._save_session()

    def get_context_snapshot(self) -> Dict[str, Any]:
        """獲取快速恢復快照"""
        if not self.current_session:
            return {}

        # 收集最近的重要記憶
        recent_memories = self._get_tier_memories(MemoryTier.HOT, limit=10)

        return {
            'session_id': self.current_session.session_id,
            'started_at': self.current_session.started_at,
            'last_activity': self.current_session.last_activity,
            'active_tasks': self.current_session.active_tasks,
            'recent_exchanges': self.current_session.recent_exchanges[-5:],
            'trading_state': self.current_session.trading_state,
            'memory_summary': self.current_session.memory_summary,
            'recent_memories': recent_memories,
            'stats': self.stats
        }

    def _cleanup_memories(self) -> None:
        """自動清理過期記憶"""
        logger.info("開始記憶清理...")
        cleanup_count = 0
        now = time.time()

        # 清理策略: 移動舊記憶到冷存儲
        for tier in [MemoryTier.HOT, MemoryTier.WARM]:
            tier_dir = self.tier_dirs[tier]
            threshold_days = 1 if tier == MemoryTier.HOT else 7

            for file_path in tier_dir.glob("*.json"):
                try:
                    with open(file_path, 'r') as f:
                        entry_data = json.load(f)
                        entry = MemoryEntry(**entry_data)

                        # 計算年齡
                        age_days = (now - entry.accessed_at) / (24 * 3600)

                        # 如果超過閾值且訪問次數少，移到下一層或刪除
                        if age_days > threshold_days and entry.access_count < 3:
                            if tier == MemoryTier.HOT:
                                # 移到 WARM
                                entry.tier = MemoryTier.WARM
                                self._save_entry(entry)
                                file_path.unlink()
                                cleanup_count += 1
                            elif tier == MemoryTier.WARM:
                                # 移到 COLD
                                entry.tier = MemoryTier.COLD
                                self._save_entry(entry)
                                file_path.unlink()
                                cleanup_count += 1

                except Exception as e:
                    logger.error(f"清理記憶失敗: {file_path}, 錯誤: {e}")

        self.stats['cleanup_count'] += cleanup_count
        self.stats['total_size_mb'] = self._get_total_size_mb()
        logger.info(f"清理完成: 移動了 {cleanup_count} 個記憶項目")

    def _get_tier_memories(self, tier: MemoryTier, limit: int = 10) -> List[Dict[str, Any]]:
        """獲取特定層級的記憶"""
        tier_dir = self.tier_dirs[tier]
        memories = []

        for file_path in sorted(
            tier_dir.glob("*.json"),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )[:limit]:
            try:
                with open(file_path, 'r') as f:
                    entry_data = json.load(f)
                    memories.append({
                        'key': entry_data['key'],
                        'accessed_at': entry_data['accessed_at'],
                        'access_count': entry_data['access_count']
                    })
            except Exception as e:
                logger.error(f"讀取記憶失敗: {file_path}, 錯誤: {e}")

        return memories

    def _save_entry(self, entry: MemoryEntry) -> None:
        """保存記憶項目"""
        tier_dir = self.tier_dirs[entry.tier]
        file_path = tier_dir / f"{entry.key}.json"

        with open(file_path, 'w') as f:
            json.dump({
                'key': entry.key,
                'content': entry.content,
                'tier': entry.tier.value,
                'created_at': entry.created_at,
                'accessed_at': entry.accessed_at,
                'access_count': entry.access_count,
                'size_bytes': entry.size_bytes
            }, f, indent=2)

    def _save_session(self) -> None:
        """保存會話上下文"""
        if not self.current_session:
            return

        with open(self.session_file, 'w') as f:
            session_dict = asdict(self.current_session)
            session_dict['started_at'] = self.current_session.started_at
            session_dict['last_activity'] = self.current_session.last_activity
            json.dump(session_dict, f, indent=2)

    def _get_total_size_mb(self) -> float:
        """計算總記憶大小"""
        total = 0
        for tier_dir in self.tier_dirs.values():
            for file_path in tier_dir.glob("*.json"):
                total += file_path.stat().st_size
        return total / (1024 * 1024)

    def get_stats(self) -> Dict[str, Any]:
        """獲取統計信息"""
        return {
            **self.stats,
            'tier_sizes': {
                tier.value: self._get_tier_size_mb(tier)
                for tier in MemoryTier
            }
        }

    def _get_tier_size_mb(self, tier: MemoryTier) -> float:
        """獲取特定層級大小"""
        tier_dir = self.tier_dirs[tier]
        total = sum(f.stat().st_size for f in tier_dir.glob("*.json"))
        return total / (1024 * 1024)

# 全局實例
_memory_manager: Optional[EnhancedMemoryManager] = None

def get_memory_manager() -> EnhancedMemoryManager:
    """獲取全局記憶管理器實例"""
    global _memory_manager
    if _memory_manager is None:
        _memory_manager = EnhancedMemoryManager()
    return _memory_manager

if __name__ == "__main__":
    # 演示用法
    manager = get_memory_manager()

    # 啟動會話
    session = manager.start_session("demo_session_001")
    print(f"會話已啟動: {session.session_id}")

    # 添加記憶
    manager.add_memory(
        "trade_decision_001",
        {
            "symbol": "BTC/USDT",
            "action": "BUY",
            "confidence": 0.85,
            "reason": "Golden Cross detected"
        },
        tier=MemoryTier.HOT
    )

    # 獲取記憶
    memory = manager.get_memory("trade_decision_001")
    print(f"記憶內容: {memory}")

    # 獲取快照
    snapshot = manager.get_context_snapshot()
    print(f"快速恢復快照:\n{json.dumps(snapshot, indent=2)}")

    # 獲取統計
    stats = manager.get_stats()
    print(f"統計信息:\n{json.dumps(stats, indent=2)}")
