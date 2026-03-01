#!/usr/bin/env python3
"""
Recap Command Module
回顧命令模組 - 提供自動化會話回顧功能
"""

import sys
import os

# 添加項目根目錄到 Python 路徑
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.core.session_recap import SessionRecap
from typing import Optional, Any

class RecapCommand:
    """回顧命令處理器"""
    
    def __init__(self) -> Any:
        """初始化回顧命令"""
        self.recap = SessionRecap()
    
    def execute_recap(self, full_report: bool = False) -> None:
        """執行回顧"""
        print("\n🔄 正在生成會話回顧...")
        summary = self.recap.generate_recap()
        self.recap.print_recap(summary)
        
        if full_report:
            self.recap.save_recap_report(summary)
            print("✅ 完整報告已保存")
    
    def execute_todos_only(self) -> None:
        """只顯示待辦事項"""
        summary = self.recap.generate_recap()
        todos = summary.todos
        
        print("\n✓ 待辦事項列表:")
        print("="*40)
        
        if not todos:
            print("  ✅ 沒有待辦事項")
            return
        
        for i, todo in enumerate(todos, 1):
            status = todo.get('status', 'unknown')
            status_emoji = {
                'pending': '⬜',
                'in_progress': '🔵',
                'completed': '✅',
                'cancelled': '❌'
            }.get(status, '❓')
            
            print(f"{i}. {status_emoji} [{todo.get('priority', 'medium')}] {todo.get('content', 'Unknown')}")

def main() -> Any:
    """主函數 - CLI 入口點"""
    recap = RecapCommand()
    recap.execute_recap(full_report=True)

if __name__ == "__main__":
    main()
