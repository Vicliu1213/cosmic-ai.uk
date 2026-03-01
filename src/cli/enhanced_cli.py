#!/usr/bin/env python3
"""
Enhanced CLI with Real-time Task Panel
增強型 CLI，集成實時任務面板

提供帶有實時更新任務面板的主 CLI 界面，支持左上/右上角顯示
"""

import os
import sys
import time
import threading
from pathlib import Path
from typing import Optional, Any
from datetime import datetime

# 添加項目根目錄
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, project_root)

from src.core.task_panel import RealTimeTaskPanel, TaskPanelConfig

class EnhancedCliWithPanel:
    """增強型 CLI，包含實時任務面板"""
    
    def __init__(self, panel_position: str = "top-left") -> Any:
        """初始化增強 CLI"""
        self.panel_config = TaskPanelConfig(
            position=panel_position,
            width=45,
            compact_mode=False,
            enable_auto_refresh=True,
            refresh_interval=3
        )
        self.panel = RealTimeTaskPanel(self.panel_config)
        self.running = False
        self.last_panel_output = ""
    
    def clear_screen(self) -> Any:
        """清屏"""
        os.system('clear' if os.name == 'posix' else 'cls')
    
    def print_header(self) -> Any:
        """打印標題"""
        print("\n" + "="*80)
        print("🚀 Comic AI 任務管理系統 - 實時面板版本".center(80))
        print("="*80 + "\n")
    
    def display_main_menu(self) -> Any:
        """顯示主菜單"""
        print("\n📌 主菜單:")
        print("  1. 刷新任務面板")
        print("  2. 查看完整任務列表")
        print("  3. 更新任務狀態")
        print("  4. 查看會話摘要")
        print("  5. 退出")
        print("\n選擇操作 (1-5): ", end="")
    
    def refresh_panel_display(self) -> Any:
        """刷新面板顯示"""
        self.clear_screen()
        self.print_header()
        
        # 顯示任務面板
        panel_text = self.panel.update()
        print(panel_text)
        
        print("\n" + "-"*80)
        print("面板信息:")
        print(f"  位置: {self.panel.config.position}")
        print(f"  最後更新: {self.panel.last_update.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"  刷新間隔: {self.panel.config.refresh_interval}秒")
        print("-"*80)
    
    def show_full_task_list(self) -> Any:
        """顯示完整任務列表"""
        self.clear_screen()
        self.print_header()
        
        summary = self.panel.recap.generate_recap()
        todos = summary.todos
        
        print("📋 完整任務列表")
        print("="*80)
        print(f"總任務數: {len(todos)}")
        print(f"分支: {summary.git_branch}")
        print(f"時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80 + "\n")
        
        # 按狀態分組顯示
        states = {
            'in_progress': ('進行中 🔵', []),
            'pending': ('待辦 ⬜', []),
            'completed': ('已完成 ✅', []),
            'cancelled': ('已取消 ❌', [])
        }
        
        for todo in todos:
            status = todo.get('status', 'unknown')
            if status in states:
                states[status][1].append(todo)
        
        for status, (label, tasks) in states.items():
            if tasks:
                print(f"\n{label}:")
                print("-" * 80)
                for i, task in enumerate(tasks, 1):
                    priority = task.get('priority', 'medium')
                    priority_emoji = {
                        'high': '🔴',
                        'medium': '🟡',
                        'low': '🟢'
                    }.get(priority, '⚪')
                    
                    content = task.get('content', 'Unknown')
                    print(f"  {i}. {priority_emoji} {content}")
    
    def show_session_summary(self) -> Any:
        """顯示會話摘要"""
        self.clear_screen()
        self.print_header()
        
        self.panel.recap.print_recap(self.panel.recap.generate_recap())
    
    def run_interactive(self) -> Any:
        """運行交互式 CLI"""
        self.running = True
        
        try:
            while self.running:
                self.refresh_panel_display()
                self.display_main_menu()
                
                try:
                    choice = input().strip()
                    
                    if choice == '1':
                        # 刷新面板 - 已在主循環中做了
                        pass
                    elif choice == '2':
                        self.show_full_task_list()
                        input("\n按 Enter 返回主菜單...")
                    elif choice == '3':
                        print("\n此功能將在後續版本中添加")
                        input("按 Enter 返回主菜單...")
                    elif choice == '4':
                        self.show_session_summary()
                        input("\n按 Enter 返回主菜單...")
                    elif choice == '5':
                        print("\n👋 謝謝使用，再見！")
                        self.running = False
                        break
                    else:
                        print("❌ 無效選項，請重新選擇")
                        time.sleep(1)
                
                except KeyboardInterrupt:
                    print("\n\n👋 程序已中止")
                    self.running = False
                    break
                except Exception as e:
                    print(f"❌ 錯誤: {e}")
                    time.sleep(1)
        
        except KeyboardInterrupt:
            print("\n\n👋 程序已中止")
        finally:
            self.running = False
    
    def run_auto_update_mode(self, update_interval: int = 3) -> Any:
        """運行自動更新模式"""
        print("🔄 進入自動更新模式（按 Ctrl+C 退出）")
        time.sleep(1)
        
        try:
            while True:
                self.refresh_panel_display()
                time.sleep(update_interval)
        except KeyboardInterrupt:
            print("\n\n👋 自動更新模式已退出")

def main() -> Any:
    """主函數"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Comic AI 增強 CLI - 帶實時任務面板",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python enhanced_cli.py              # 交互模式（默認）
  python enhanced_cli.py --auto       # 自動更新模式
  python enhanced_cli.py --position top-right  # 指定面板位置
        """
    )
    
    parser.add_argument(
        '--auto',
        action='store_true',
        help='自動更新模式'
    )
    
    parser.add_argument(
        '--position',
        choices=['top-left', 'top-right', 'bottom-left', 'bottom-right'],
        default='top-left',
        help='任務面板位置（默認: top-left）'
    )
    
    parser.add_argument(
        '--interval',
        type=int,
        default=3,
        help='更新間隔（秒，默認: 3）'
    )
    
    parser.add_argument(
        '--compact',
        action='store_true',
        help='使用緊湊模式'
    )
    
    args = parser.parse_args()
    
    try:
        cli = EnhancedCliWithPanel(panel_position=args.position)
        cli.panel.config.compact_mode = args.compact
        cli.panel.config.refresh_interval = args.interval
        
        if args.auto:
            cli.run_auto_update_mode(update_interval=args.interval)
        else:
            cli.run_interactive()
    
    except Exception as e:
        print(f"❌ 錯誤: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
