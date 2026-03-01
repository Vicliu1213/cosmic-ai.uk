#!/usr/bin/env python3
"""
快速上下文恢復流程 (Context Recovery Pipeline)
<50ms 內恢復完整會話狀態，支持快捷鍵觸發

流程步驟:
1. 讀取會話文件 (~5ms)
2. 恢復記憶層級 (~10ms)
3. 重建活躍任務列表 (~15ms)
4. 恢復交易狀態 (~10ms)
5. 返回可用快照 (<50ms)
"""

import json
import time
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from pathlib import Path

from enhanced_memory_manager import (
    get_memory_manager,
    MemoryTier,
    SessionContext
)

logger = logging.getLogger(__name__)

class ContextRecoveryPipeline:
    """快速上下文恢復管道"""

    def __init__(self):
        self.memory_manager = get_memory_manager()
        self.performance_metrics = {
            'last_recovery_time_ms': 0,
            'total_recoveries': 0,
            'avg_recovery_time_ms': 0
        }

    def recover_fast(self) -> Tuple[Optional[Dict[str, Any]], float]:
        """
        快速恢復會話 (<50ms)

        Returns:
            (恢復的上下文, 恢復耗時 ms)
        """
        start_time = time.time()

        try:
            # 步驟 1: 讀取會話文件 (~5ms)
            session_data = self._load_session_file()
            if not session_data:
                return None, 0

            # 步驟 2: 恢復記憶層級 (~10ms)
            hot_memories = self._recover_hot_memories()

            # 步驟 3: 重建活躍任務 (~15ms)
            active_tasks = self._rebuild_active_tasks()

            # 步驟 4: 恢復交易狀態 (~10ms)
            trading_state = self._restore_trading_state()

            # 組合恢復的上下文
            context = {
                'session': session_data,
                'hot_memories': hot_memories,
                'active_tasks': active_tasks,
                'trading_state': trading_state,
                'recovered_at': datetime.now().isoformat()
            }

            # 計算耗時
            elapsed_ms = (time.time() - start_time) * 1000

            # 更新性能指標
            self._update_performance_metrics(elapsed_ms)

            logger.info(f"✅ 快速恢復完成 ({elapsed_ms:.2f}ms)")
            return context, elapsed_ms

        except Exception as e:
            logger.error(f"❌ 恢復失敗: {e}")
            return None, (time.time() - start_time) * 1000

    def _load_session_file(self) -> Optional[Dict[str, Any]]:
        """讀取會話文件 (~5ms)"""
        session_file = self.memory_manager.session_file

        if not session_file.exists():
            logger.debug("會話文件不存在")
            return None

        try:
            with open(session_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"讀取會話文件失敗: {e}")
            return None

    def _recover_hot_memories(self) -> List[Dict[str, Any]]:
        """恢復熱記憶 (~10ms)"""
        tier_dir = self.memory_manager.tier_dirs[MemoryTier.HOT]
        memories = []

        try:
            # 只讀取最新的 N 個文件以加快速度
            files = sorted(
                tier_dir.glob("*.json"),
                key=lambda p: p.stat().st_mtime,
                reverse=True
            )[:20]  # 限制為 20 個

            for file_path in files:
                try:
                    with open(file_path, 'r') as f:
                        entry = json.load(f)
                        memories.append({
                            'key': entry['key'],
                            'accessed_at': entry['accessed_at'],
                            'access_count': entry['access_count']
                        })
                except Exception:
                    pass

        except Exception as e:
            logger.error(f"恢復熱記憶失敗: {e}")

        return memories

    def _rebuild_active_tasks(self) -> List[str]:
        """重建活躍任務列表 (~15ms)"""
        tasks = []

        try:
            # 從會話上下文中獲取活躍任務
            session_data = self._load_session_file()
            if session_data:
                tasks = session_data.get('active_tasks', [])

        except Exception as e:
            logger.error(f"重建任務列表失敗: {e}")

        return tasks

    def _restore_trading_state(self) -> Dict[str, Any]:
        """恢復交易狀態 (~10ms)"""
        state = {}

        try:
            session_data = self._load_session_file()
            if session_data:
                state = session_data.get('trading_state', {})

        except Exception as e:
            logger.error(f"恢復交易狀態失敗: {e}")

        return state

    def _update_performance_metrics(self, elapsed_ms: float) -> None:
        """更新性能指標"""
        self.performance_metrics['last_recovery_time_ms'] = elapsed_ms
        self.performance_metrics['total_recoveries'] += 1

        total = self.performance_metrics['total_recoveries']
        avg = self.performance_metrics['avg_recovery_time_ms']
        self.performance_metrics['avg_recovery_time_ms'] = (
            (avg * (total - 1) + elapsed_ms) / total
        )

    def get_performance(self) -> Dict[str, float]:
        """獲取性能指標"""
        return self.performance_metrics.copy()

    def trigger_recovery(self, shortcut: str = 'r') -> str:
        """
        通過快捷鍵觸發快速恢復

        Args:
            shortcut: 快捷鍵 (默認 'r')

        Returns:
            恢復摘要
        """
        context, elapsed_ms = self.recover_fast()

        if not context:
            return "❌ 恢復失敗：無會話數據"

        # 格式化輸出
        output = []
        output.append("\n" + "="*60)
        output.append(f"⚡ 快速恢復完成 ({elapsed_ms:.2f}ms)")
        output.append("="*60)
        output.append(f"會話 ID: {context['session']['session_id']}")
        output.append(f"活躍任務: {len(context['active_tasks'])} 個")
        output.append(f"熱記憶: {len(context['hot_memories'])} 個")
        
        if context['active_tasks']:
            output.append("\n待恢復任務:")
            for task in context['active_tasks'][:5]:
                output.append(f"  • {task}")

        if context['trading_state']:
            output.append("\n交易狀態:")
            for key, value in list(context['trading_state'].items())[:5]:
                output.append(f"  • {key}: {value}")

        output.append("="*60 + "\n")

        return "\n".join(output)

# 快捷鍵觸發器
class RecoveryShortcutTrigger:
    """快捷鍵觸發恢復"""

    def __init__(self):
        self.pipeline = ContextRecoveryPipeline()
        self.shortcuts = {
            'r': self.recover_now,      # r - 立即恢復
            'rp': self.recover_and_peek, # rp - 恢復並預覽
            'rs': self.recover_stats,   # rs - 恢復統計
        }

    def execute(self, shortcut: str) -> str:
        """執行快捷鍵恢復"""
        if shortcut in self.shortcuts:
            return self.shortcuts[shortcut]()
        return f"❌ 未知快捷鍵: {shortcut}"

    def recover_now(self) -> str:
        """立即恢復 (r)"""
        return self.pipeline.trigger_recovery()

    def recover_and_peek(self) -> str:
        """恢復並預覽 (rp)"""
        context, elapsed_ms = self.pipeline.recover_fast()

        if not context:
            return "❌ 無會話可恢復"

        output = []
        output.append(self.pipeline.trigger_recovery())
        output.append("\n💾 完整上下文快照:")
        output.append(json.dumps(context, indent=2, default=str)[:500])
        output.append("...\n")

        return "\n".join(output)

    def recover_stats(self) -> str:
        """恢復統計 (rs)"""
        stats = self.pipeline.get_performance()

        output = []
        output.append("\n" + "="*60)
        output.append("📈 恢復性能統計")
        output.append("="*60)
        output.append(f"最後恢復耗時: {stats['last_recovery_time_ms']:.2f} ms")
        output.append(f"總恢復次數: {stats['total_recoveries']}")
        output.append(f"平均恢復耗時: {stats['avg_recovery_time_ms']:.2f} ms")
        output.append("="*60 + "\n")

        return "\n".join(output)

if __name__ == "__main__":
    # 演示
    trigger = RecoveryShortcutTrigger()

    print("=== 快速上下文恢復演示 ===\n")

    # 執行多次恢復測試
    for i in range(3):
        print(f"\n--- 測試 {i+1} ---")
        print(trigger.recover_now())
        time.sleep(0.1)

    # 顯示性能統計
    print(trigger.recover_stats())
