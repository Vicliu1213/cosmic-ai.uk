#!/usr/bin/env python3
"""
Auto Recap Integration Script
自動化回顧集成腳本

提供簡單的命令行工具，用於啟動自動化會話回顧
"""

import sys
import os
import argparse
from pathlib import Path

# 添加項目根目錄到 Python 路徑
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.session_recap import SessionRecap


def main():
    """主函數"""
    parser = argparse.ArgumentParser(
        description="Comic AI 自動化會話回顧工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python recap_cli.py              # 顯示基本回顧
  python recap_cli.py --full       # 生成完整回顧報告
  python recap_cli.py --todos      # 只顯示待辦事項
        """
    )
    
    parser.add_argument(
        '--full',
        action='store_true',
        help='生成完整回顧報告並保存'
    )
    
    parser.add_argument(
        '--todos',
        action='store_true',
        help='只顯示待辦事項'
    )
    
    parser.add_argument(
        '--save-report',
        action='store_true',
        help='保存回顧報告'
    )
    
    args = parser.parse_args()
    
    try:
        recap = SessionRecap()
        summary = recap.generate_recap()
        
        if args.todos:
            # 只顯示待辦事項
            todos = summary.todos
            print("\n✓ 待辦事項列表:")
            print("="*50)
            
            if not todos:
                print("  ✅ 沒有待辦事項")
            else:
                for i, todo in enumerate(todos, 1):
                    status = todo.get('status', 'unknown')
                    status_emoji = {
                        'pending': '⬜',
                        'in_progress': '🔵',
                        'completed': '✅',
                        'cancelled': '❌'
                    }.get(status, '❓')
                    
                    priority = todo.get('priority', 'medium')
                    content = todo.get('content', 'Unknown')
                    print(f"{i}. {status_emoji} [{priority}] {content}")
        else:
            # 顯示基本回顧
            recap.print_recap(summary)
        
        # 保存報告
        if args.full or args.save_report:
            recap.save_recap_report(summary)
            print("✅ 回顧報告已保存")
        
    except Exception as e:
        print(f"❌ 錯誤: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
