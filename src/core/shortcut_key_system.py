#!/usr/bin/env python3
"""
超短快捷鍵系統 (Shortcut Key System)
用於快速觸發記憶恢復和常見操作

快捷鍵設計:
- `m` - 顯示記憶摘要
- `r` - 快速恢復上次會話
- `c` - 清空當前會話
- `s` - 保存當前狀態快照
- `h` - 顯示幫助
- `!` - 執行命令行
"""

import json
import sys
from typing import Callable, Dict, Any, Optional
from datetime import datetime
from pathlib import Path

from enhanced_memory_manager import (
    get_memory_manager,
    MemoryTier,
    EnhancedMemoryManager
)


class ShortcutKeySystem:
    """超短快捷鍵系統"""

    def __init__(self):
        self.memory_manager = get_memory_manager()
        self.shortcuts: Dict[str, Callable] = {
            'm': self.show_memory_summary,      # 記憶摘要
            'r': self.recover_session,          # 恢復會話
            'c': self.clear_session,            # 清空會話
            's': self.save_snapshot,            # 保存快照
            'h': self.show_help,                # 幫助
            '!': self.execute_command,          # 執行命令
            'stat': self.show_stats,            # 統計信息
            'trade': self.show_trading_state,   # 交易狀態
        }

    def execute(self, shortcut: str, *args) -> Optional[str]:
        """
        執行快捷鍵

        Args:
            shortcut: 快捷鍵代碼
            *args: 額外參數

        Returns:
            執行結果或 None
        """
        if shortcut in self.shortcuts:
            try:
                return self.shortcuts[shortcut](*args)
            except Exception as e:
                return f"❌ 快捷鍵執行失敗: {shortcut}, 錯誤: {e}"
        else:
            return f"❌ 未知快捷鍵: {shortcut}"

    def show_memory_summary(self) -> str:
        """顯示記憶摘要"""
        snapshot = self.memory_manager.get_context_snapshot()

        if not snapshot:
            return "❌ 無會話數據"

        # 格式化輸出
        output = []
        output.append("\n" + "="*60)
        output.append("🧠 記憶摘要")
        output.append("="*60)
        output.append(f"會話 ID: {snapshot.get('session_id', 'N/A')}")
        output.append(f"活躍任務: {len(snapshot.get('active_tasks', []))} 個")
        
        if snapshot.get('active_tasks'):
            for task in snapshot['active_tasks'][:5]:
                output.append(f"  • {task}")

        output.append(f"最近對話: {len(snapshot.get('recent_exchanges', []))} 條")
        output.append(f"記憶大小: {self.memory_manager.get_stats()['total_size_mb']:.2f} MB")
        output.append("="*60 + "\n")

        return "\n".join(output)

    def recover_session(self) -> str:
        """快速恢復會話"""
        snapshot = self.memory_manager.get_context_snapshot()

        if not snapshot:
            return "❌ 無會話可恢復"

        output = []
        output.append("\n" + "="*60)
        output.append("🔄 會話恢復中...")
        output.append("="*60)
        output.append(f"會話 ID: {snapshot['session_id']}")
        output.append(f"恢復時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        output.append(f"活躍任務: {len(snapshot['active_tasks'])} 個")
        
        if snapshot['active_tasks']:
            output.append("\n📋 待恢復任務:")
            for task in snapshot['active_tasks'][:10]:
                output.append(f"  ✓ {task}")

        if snapshot['recent_exchanges']:
            output.append("\n💬 最近對話:")
            for exchange in snapshot['recent_exchanges'][-3:]:
                output.append(f"  Q: {exchange.get('q', 'N/A')[:50]}...")

        output.append("="*60 + "\n")

        return "\n".join(output)

    def clear_session(self) -> str:
        """清空當前會話"""
        self.memory_manager.current_session = None
        session_file = self.memory_manager.session_file
        if session_file.exists():
            session_file.unlink()
        return "✅ 會話已清空"

    def save_snapshot(self) -> str:
        """保存當前狀態快照"""
        snapshot = self.memory_manager.get_context_snapshot()
        
        if not snapshot:
            return "❌ 無會話可保存"

        # 保存快照到文件
        snapshot_file = self.memory_manager.data_dir / \
            f"snapshots/snapshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        snapshot_file.parent.mkdir(parents=True, exist_ok=True)

        with open(snapshot_file, 'w') as f:
            json.dump(snapshot, f, indent=2)

        return f"✅ 快照已保存: {snapshot_file.name}"

    def show_stats(self) -> str:
        """顯示統計信息"""
        stats = self.memory_manager.get_stats()

        output = []
        output.append("\n" + "="*60)
        output.append("📊 統計信息")
        output.append("="*60)
        output.append(f"總記憶數: {stats.get('total_memories', 0)}")
        output.append(f"總大小: {stats.get('total_size_mb', 0):.2f} MB")
        output.append(f"訪問次數: {stats.get('access_count', 0)}")
        output.append(f"清理次數: {stats.get('cleanup_count', 0)}")
        
        output.append("\n層級大小:")
        for tier_name, tier_size in stats.get('tier_sizes', {}).items():
            output.append(f"  {tier_name}: {tier_size:.2f} MB")

        output.append("="*60 + "\n")

        return "\n".join(output)

    def show_trading_state(self) -> str:
        """顯示交易狀態"""
        snapshot = self.memory_manager.get_context_snapshot()

        if not snapshot:
            return "❌ 無交易狀態"

        trading_state = snapshot.get('trading_state', {})

        output = []
        output.append("\n" + "="*60)
        output.append("💰 交易狀態")
        output.append("="*60)

        if not trading_state:
            output.append("  (無交易信息)")
        else:
            for key, value in trading_state.items():
                output.append(f"  {key}: {value}")

        output.append("="*60 + "\n")

        return "\n".join(output)

    def show_help(self) -> str:
        """顯示幫助"""
        output = []
        output.append("\n" + "="*60)
        output.append("📖 快捷鍵幫助")
        output.append("="*60)
        output.append("\n超短快捷鍵:")
        output.append("  m    - 記憶摘要")
        output.append("  r    - 恢復會話")
        output.append("  c    - 清空會話")
        output.append("  s    - 保存快照")
        output.append("  stat - 統計信息")
        output.append("  trade- 交易狀態")
        output.append("  h    - 顯示幫助")
        output.append("  !    - 執行命令")
        output.append("="*60 + "\n")

        return "\n".join(output)

    def execute_command(self, *args) -> str:
        """執行外部命令"""
        if not args:
            return "❌ 請提供命令"

        command = " ".join(args)
        return f"執行命令: {command}"


# CLI 介面
def main():
    """主程序"""
    system = ShortcutKeySystem()

    # 啟動會話
    manager = get_memory_manager()
    import time
    session = manager.start_session(f"cli_session_{int(time.time())}")

    print("\n✅ 交易系統快捷鍵系統已啟動")
    print("輸入 'h' 查看幫助, 'q' 退出\n")

    # 交互循環
    while True:
        try:
            user_input = input("快捷鍵> ").strip()

            if user_input.lower() == 'q':
                print("👋 再見！")
                break

            if not user_input:
                continue

            # 解析輸入
            parts = user_input.split()
            shortcut = parts[0]
            args = parts[1:] if len(parts) > 1 else []

            # 執行快捷鍵
            result = system.execute(shortcut, *args)
            if result:
                print(result)

        except KeyboardInterrupt:
            print("\n👋 程序已中斷")
            break
        except Exception as e:
            print(f"❌ 錯誤: {e}")


if __name__ == "__main__":
    main()
