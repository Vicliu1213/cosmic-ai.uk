#!/usr/bin/env python3
"""
Dual Panel Task Display - Real-time + Completed
雙框任務面板 - 即時任務 + 完成任務實時顯示

提供左右分欄布局，左側顯示進行中/待辦任務，右側顯示已完成任務
"""

import os
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
from dataclasses import dataclass

# 添加項目根目錄
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, project_root)

from src.core.session_recap import SessionRecap

@dataclass
class DualPanelConfig:
    """雙框面板配置"""
    left_width: int = 45      # 左框寬度（進行中+待辦）
    right_width: int = 35     # 右框寬度（已完成）
    max_left_tasks: int = 10  # 左側最多顯示任務數
    max_right_tasks: int = 8  # 右側最多顯示任務數
    refresh_interval: int = 3 # 刷新間隔（秒）
    compact_mode: bool = False
    show_progress_bar: bool = True
    show_stats: bool = True

class DualTaskPanel:
    """雙框任務面板"""
    
    def __init__(self, config: Optional[DualPanelConfig] = None) -> Any:
        """初始化雙框面板"""
        self.config = config or DualPanelConfig()
        self.recap = SessionRecap()
        self.last_update = datetime.now()
        self.current_page_left = 0
        self.current_page_right = 0
    
    def format_task_item(self, task: Dict[str, Any], width: int) -> str:
        """格式化任務項"""
        status = task.get('status', 'unknown')
        priority = task.get('priority', 'medium')
        content = task.get('content', 'Unknown')
        
        # 狀態符號
        status_emoji = {
            'pending': '⬜',
            'in_progress': '🔵',
            'completed': '✅',
            'cancelled': '❌'
        }.get(status, '❓')
        
        # 優先級符號
        priority_emoji = {
            'high': '🔴',
            'medium': '🟡',
            'low': '🟢'
        }.get(priority, '⚪')
        
        # 縮短內容以適應寬度
        available_width = width - 6
        if len(content) > available_width:
            content = content[:available_width-3] + "..."
        
        return f"{status_emoji}{priority_emoji} {content}"
    
    def build_progress_bar(self, completed: int, total: int, width: int) -> str:
        """構建進度條"""
        if total == 0:
            return "█" * width + " 0%"
        
        percentage = (completed * 100) // total
        bar_width = width - 4
        filled = (bar_width * completed) // total
        
        bar = "█" * filled + "░" * (bar_width - filled)
        return f"{bar} {percentage}%"
    
    def build_left_panel(self, todos: List[Dict[str, Any]]) -> List[str]:
        """構建左側面板（進行中 + 待辦）"""
        lines = []
        width = self.config.left_width
        
        # 標題
        lines.append("┌" + "─" * (width - 2) + "┐")
        lines.append("│ 🔵 即時任務（進行中+待辦）".ljust(width - 1) + "│")
        lines.append("├" + "─" * (width - 2) + "┤")
        
        # 時間戳
        timestamp = datetime.now().strftime("%H:%M:%S")
        lines.append(f"│ 🕐 {timestamp}".ljust(width - 1) + "│")
        lines.append("├" + "─" * (width - 2) + "┤")
        
        # 進行中的任務
        in_progress = [t for t in todos if t.get('status') == 'in_progress']
        if in_progress:
            lines.append("│ 🔄 進行中的任務:".ljust(width - 1) + "│")
            for task in in_progress[:self.config.max_left_tasks]:
                line = self.format_task_item(task, width - 2)
                lines.append("│ " + line.ljust(width - 3) + "│")
        
        # 待辦任務
        pending = [t for t in todos if t.get('status') == 'pending']
        if pending:
            if in_progress:
                lines.append("├" + "─" * (width - 2) + "┤")
            lines.append("│ ⏳ 待辦的任務:".ljust(width - 1) + "│")
            remaining = self.config.max_left_tasks - len(in_progress)
            for task in pending[:remaining]:
                line = self.format_task_item(task, width - 2)
                lines.append("│ " + line.ljust(width - 3) + "│")
        
        if not in_progress and not pending:
            lines.append("│ ✨ 沒有進行中或待辦任務".ljust(width - 1) + "│")
        
        lines.append("└" + "─" * (width - 2) + "┘")
        
        return lines
    
    def build_right_panel(self, todos: List[Dict[str, Any]]) -> List[str]:
        """構建右側面板（已完成）"""
        lines = []
        width = self.config.right_width
        
        # 標題
        lines.append("┌" + "─" * (width - 2) + "┐")
        lines.append("│ ✅ 已完成任務".ljust(width - 1) + "│")
        lines.append("├" + "─" * (width - 2) + "┤")
        
        # 已完成任務計數
        completed = [t for t in todos if t.get('status') == 'completed']
        total = len(todos)
        count_text = f"✅ {len(completed)}/{total} 已完成"
        lines.append("│ " + count_text.ljust(width - 3) + "│")
        
        if self.config.show_progress_bar:
            lines.append("├" + "─" * (width - 2) + "┤")
            progress = self.build_progress_bar(len(completed), total, width - 4)
            lines.append("│ " + progress.ljust(width - 3) + "│")
        
        lines.append("├" + "─" * (width - 2) + "┤")
        
        # 已完成任務列表
        if completed:
            for task in completed[:self.config.max_right_tasks]:
                line = self.format_task_item(task, width - 2)
                lines.append("│ " + line.ljust(width - 3) + "│")
            
            if len(completed) > self.config.max_right_tasks:
                remaining = len(completed) - self.config.max_right_tasks
                lines.append(f"│ ... +{remaining} 更多".ljust(width - 1) + "│")
        else:
            lines.append("│ 還沒有完成的任務".ljust(width - 1) + "│")
        
        lines.append("└" + "─" * (width - 2) + "┘")
        
        return lines
    
    def build_stats_panel(self, todos: List[Dict[str, Any]]) -> List[str]:
        """構建統計面板"""
        lines = []
        
        completed = len([t for t in todos if t.get('status') == 'completed'])
        in_progress = len([t for t in todos if t.get('status') == 'in_progress'])
        pending = len([t for t in todos if t.get('status') == 'pending'])
        cancelled = len([t for t in todos if t.get('status') == 'cancelled'])
        total = len(todos)
        
        # 計算寬度
        total_width = self.config.left_width + self.config.right_width + 3
        
        lines.append("┌" + "─" * (total_width - 2) + "┐")
        
        # 統計信息
        if total > 0:
            percentage = (completed * 100) // total
        else:
            percentage = 0
        
        stats_text = f"📊 統計: ✅{completed} 🔵{in_progress} ⏳{pending} ❌{cancelled} | 進度: {percentage}%"
        lines.append("│ " + stats_text.ljust(total_width - 3) + "│")
        lines.append("└" + "─" * (total_width - 2) + "┘")
        
        return lines
    
    def build_full_panel(self) -> str:
        """構建完整面板"""
        summary = self.recap.generate_recap()
        todos = summary.todos
        
        lines = []
        
        # 標題
        lines.append("\n" + "="*82)
        lines.append("📋 實時任務面板 - 即時任務 vs 完成任務".center(82))
        lines.append("="*82 + "\n")
        
        # 獲取左右面板
        left_lines = self.build_left_panel(todos)
        right_lines = self.build_right_panel(todos)
        
        # 合併左右面板
        max_lines = max(len(left_lines), len(right_lines))
        for i in range(max_lines):
            left_line = left_lines[i] if i < len(left_lines) else " " * self.config.left_width
            right_line = right_lines[i] if i < len(right_lines) else " " * self.config.right_width
            
            # 確保寬度一致
            left_line = left_line.ljust(self.config.left_width)
            right_line = right_line.ljust(self.config.right_width)
            
            lines.append(left_line + "  " + right_line)
        
        lines.append("")
        
        # 添加統計面板
        stats_lines = self.build_stats_panel(todos)
        lines.extend(stats_lines)
        
        # Git 信息
        lines.append(f"\n🌿 分支: {summary.git_branch} | 🕐 更新時間: {datetime.now().strftime('%H:%M:%S')}")
        lines.append("="*82)
        
        return "\n".join(lines)
    
    def build_compact_panel(self) -> str:
        """構建緊湊面板"""
        summary = self.recap.generate_recap()
        todos = summary.todos
        
        lines = []
        
        completed = len([t for t in todos if t.get('status') == 'completed'])
        in_progress = len([t for t in todos if t.get('status') == 'in_progress'])
        pending = len([t for t in todos if t.get('status') == 'pending'])
        total = len(todos)
        
        lines.append("\n┌─────────────────────────────────────────────────────┐")
        lines.append(f"│ 📊 任務統計 | ✅{completed} 🔵{in_progress} ⏳{pending} | 進度: {(completed*100//total) if total > 0 else 0}%")
        lines.append("├─────────────────────────────────────────────────────┤")
        
        # 進行中和待辦
        in_prog_tasks = [t for t in todos if t.get('status') == 'in_progress']
        pending_tasks = [t for t in todos if t.get('status') == 'pending']
        
        lines.append("│ 🔄 進行中:")
        for task in in_prog_tasks[:3]:
            content = task.get('content', '')[:40]
            lines.append(f"│   • {content}")
        
        if pending_tasks:
            lines.append("│ ⏳ 待辦:")
            for task in pending_tasks[:2]:
                content = task.get('content', '')[:40]
                lines.append(f"│   • {content}")
        
        lines.append("└─────────────────────────────────────────────────────┘")
        
        return "\n".join(lines)
    
    def update(self) -> str:
        """更新面板"""
        self.last_update = datetime.now()
        
        if self.config.compact_mode:
            return self.build_compact_panel()
        else:
            return self.build_full_panel()
    
    def display(self) -> None:
        """顯示面板"""
        panel_text = self.update()
        print(panel_text)

class InteractiveDualPanel:
    """交互式雙框面板"""
    
    def __init__(self) -> Any:
        """初始化交互式面板"""
        self.panel = DualTaskPanel()
        self.running = False
    
    def clear_screen(self) -> Any:
        """清屏"""
        os.system('clear' if os.name == 'posix' else 'cls')
    
    def show_menu(self) -> Any:
        """顯示菜單"""
        print("\n" + "─"*60)
        print("📌 功能菜單:")
        print("  1. 刷新面板")
        print("  2. 切換緊湊/完整模式")
        print("  3. 自動更新（5秒）")
        print("  4. 查看完整任務列表")
        print("  5. 查看建議")
        print("  6. 退出")
        print("─"*60)
        print("選擇 (1-6): ", end="")
    
    def show_full_list(self) -> Any:
        """顯示完整列表"""
        self.clear_screen()
        summary = self.panel.recap.generate_recap()
        todos = summary.todos
        
        print("\n📋 完整任務列表")
        print("="*60)
        
        states = {
            'in_progress': ('🔵 進行中', []),
            'pending': ('⏳ 待辦', []),
            'completed': ('✅ 已完成', []),
            'cancelled': ('❌ 已取消', [])
        }
        
        for todo in todos:
            status = todo.get('status', 'unknown')
            if status in states:
                states[status][1].append(todo)
        
        for status, (label, tasks) in states.items():
            if tasks:
                print(f"\n{label}:")
                print("-" * 60)
                for i, task in enumerate(tasks, 1):
                    priority = task.get('priority', 'medium')
                    priority_emoji = {'high': '🔴', 'medium': '🟡', 'low': '🟢'}.get(priority, '⚪')
                    content = task.get('content', 'Unknown')
                    print(f"  {i}. {priority_emoji} {content}")
    
    def auto_update_mode(self, interval: int = 5) -> Any:
        """自動更新模式"""
        self.running = True
        try:
            while self.running:
                self.clear_screen()
                self.panel.display()
                print(f"\n⏱️  自動刷新中... (每 {interval} 秒更新一次，按 Ctrl+C 退出)")
                time.sleep(interval)
        except KeyboardInterrupt:
            print("\n✅ 自動更新已停止")
    
    def run(self) -> Any:
        """運行交互式面板"""
        while True:
            self.clear_screen()
            self.panel.display()
            self.show_menu()
            
            try:
                choice = input().strip()
                
                if choice == '1':
                    pass  # 刷新在主循環中
                elif choice == '2':
                    self.panel.config.compact_mode = not self.panel.config.compact_mode
                    mode = "緊湊" if self.panel.config.compact_mode else "完整"
                    print(f"✅ 已切換到{mode}模式")
                    time.sleep(1)
                elif choice == '3':
                    self.auto_update_mode(5)
                elif choice == '4':
                    self.show_full_list()
                    input("\n按 Enter 返回...")
                elif choice == '5':
                    summary = self.panel.recap.generate_recap()
                    print("\n💡 系統建議:")
                    for rec in summary.recommendations:
                        print(f"  {rec}")
                    input("\n按 Enter 返回...")
                elif choice == '6':
                    print("\n👋 謝謝使用，再見！")
                    break
                else:
                    print("❌ 無效選項")
                    time.sleep(1)
            
            except KeyboardInterrupt:
                print("\n\n👋 程序已中止")
                break
            except Exception as e:
                print(f"❌ 錯誤: {e}")
                time.sleep(1)

def main() -> Any:
    """主函數"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="雙框任務面板 - 即時任務 vs 完成任務",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python dual_task_panel.py         # 交互模式（默認）
  python dual_task_panel.py --auto  # 自動更新模式
  python dual_task_panel.py --compact  # 緊湊模式
        """
    )
    
    parser.add_argument(
        '--auto',
        action='store_true',
        help='自動更新模式'
    )
    
    parser.add_argument(
        '--compact',
        action='store_true',
        help='緊湊模式'
    )
    
    parser.add_argument(
        '--interval',
        type=int,
        default=3,
        help='更新間隔（秒）'
    )
    
    args = parser.parse_args()
    
    try:
        panel = InteractiveDualPanel()
        panel.panel.config.compact_mode = args.compact
        panel.panel.config.refresh_interval = args.interval
        
        if args.auto:
            panel.panel.display()
            panel.auto_update_mode(args.interval)
        else:
            panel.run()
    
    except Exception as e:
        print(f"❌ 錯誤: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
