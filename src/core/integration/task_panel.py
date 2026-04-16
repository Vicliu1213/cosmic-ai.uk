#!/usr/bin/env python3
"""
Real-time Task Panel Component
實時任務面板組件 - 顯示在左側邊欄或右上角

提供實時更新的任務追蹤面板，支持動態刷新和狀態更新
"""

import os
import sys
import json
import threading
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
class TaskPanelConfig:
    """任務面板配置"""
    position: str = "top-left"  # top-left, top-right, bottom-left, bottom-right
    width: int = 40
    refresh_interval: int = 5  # 秒
    max_tasks_display: int = 8
    enable_auto_refresh: bool = True
    compact_mode: bool = False

class RealTimeTaskPanel:
    """實時任務面板"""
    
    def __init__(self, config: Optional[TaskPanelConfig] = None) -> None:
        """初始化任務面板"""
        self.config = config or TaskPanelConfig()
        self.recap = SessionRecap()
        self.last_update = datetime.now()
        self.is_running = False
        self.refresh_thread = None
        
        # 性能優化: 緩存
        self._cache = {
            'summary': None,
            'panel_text': None,
            'timestamp': None,
            'cache_duration': 2  # 秒
        }
        self._stats = {
            'total_updates': 0,
            'cache_hits': 0,
            'cache_misses': 0
        }
        
    def get_terminal_size(self) -> Tuple[int, int]:
        """獲取終端大小"""
        import shutil
        cols, rows = shutil.get_terminal_size((80, 24))
        return cols, rows
    
    def _is_cache_valid(self) -> bool:
        """檢查緩存是否有效"""
        if not self._cache['summary'] or not self._cache['timestamp']:
            return False
        elapsed = (datetime.now() - self._cache['timestamp']).total_seconds()
        return elapsed < self._cache['cache_duration']
    
    def _get_summary_cached(self) -> Any:
        """獲取緩存的會話摘要"""
        if self._is_cache_valid():
            self._stats['cache_hits'] += 1
            return self._cache['summary']
        
        self._stats['cache_misses'] += 1
        summary = self.recap.generate_recap()
        self._cache['summary'] = summary
        self._cache['timestamp'] = datetime.now()
        return summary
    
    def get_stats(self) -> Dict[str, Any]:
        """獲取性能統計"""
        total = self._stats['cache_hits'] + self._stats['cache_misses']
        hit_rate = (self._stats['cache_hits'] / total * 100) if total > 0 else 0
        return {
            'total_updates': self._stats['total_updates'],
            'cache_hits': self._stats['cache_hits'],
            'cache_misses': self._stats['cache_misses'],
            'hit_rate': f"{hit_rate:.1f}%"
        }
    
    def format_task_line(self, task: Dict[str, Any], max_width: int) -> str:
        """格式化單個任務行"""
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
        
        # 縮短內容
        available_width = max_width - 8
        if len(content) > available_width:
            content = content[:available_width-3] + "..."
        
        return f"{status_emoji}{priority_emoji} {content}"
    
    def build_panel_compact(self) -> str:
        """構建緊湊模式面板"""
        summary = self._get_summary_cached()
        todos = summary.todos
        
        lines = []
        lines.append("┌" + "─" * (self.config.width - 2) + "┐")
        lines.append(f"│ 📋 任務面板 {datetime.now().strftime('%H:%M:%S')}".ljust(self.config.width - 1) + "│")
        lines.append("├" + "─" * (self.config.width - 2) + "┤")
        
        # 統計信息
        completed = len([t for t in todos if t.get('status') == 'completed'])
        in_progress = len([t for t in todos if t.get('status') == 'in_progress'])
        pending = len([t for t in todos if t.get('status') == 'pending'])
        
        lines.append(f"│ ✅ {completed} │ 🔵 {in_progress} │ ⬜ {pending}".ljust(self.config.width - 1) + "│")
        lines.append("├" + "─" * (self.config.width - 2) + "┤")
        
        # 顯示進行中的任務（優先）
        in_progress_tasks = [t for t in todos if t.get('status') == 'in_progress']
        for task in in_progress_tasks[:3]:
            line = self.format_task_line(task, self.config.width - 2)
            lines.append("│ " + line.ljust(self.config.width - 3) + "│")
        
        # 顯示待辦任務
        pending_tasks = [t for t in todos if t.get('status') == 'pending']
        for task in pending_tasks[:2]:
            line = self.format_task_line(task, self.config.width - 2)
            lines.append("│ " + line.ljust(self.config.width - 3) + "│")
        
        lines.append("└" + "─" * (self.config.width - 2) + "┘")
        
        return "\n".join(lines)
    
    def build_panel_full(self) -> str:
        """構建完整模式面板"""
        summary = self._get_summary_cached()
        todos = summary.todos
        
        lines = []
        width = self.config.width
        
        # 標題
        lines.append("┌" + "─" * (width - 2) + "┐")
        title = "📋 任務追蹤面板"
        lines.append(f"│ {title}".ljust(width - 1) + "│")
        lines.append("├" + "─" * (width - 2) + "┤")
        
        # 時間戳和分支信息
        timestamp = datetime.now().strftime("%H:%M:%S")
        branch = summary.git_branch[:15]
        lines.append(f"│ 🕐 {timestamp} | 🌿 {branch}".ljust(width - 1) + "│")
        lines.append("├" + "─" * (width - 2) + "┤")
        
        # 統計信息
        completed = len([t for t in todos if t.get('status') == 'completed'])
        in_progress = len([t for t in todos if t.get('status') == 'in_progress'])
        pending = len([t for t in todos if t.get('status') == 'pending'])
        total = len(todos)
        
        lines.append(f"│ 進度: {completed}/{total} 已完成 ({100*completed//total if total > 0 else 0}%)".ljust(width - 1) + "│")
        lines.append("├" + "─" * (width - 2) + "┤")
        
        # 任務列表
        displayed_count = 0
        max_display = self.config.max_tasks_display
        
        # 優先顯示進行中的任務
        for task in todos:
            if displayed_count >= max_display:
                break
            if task.get('status') == 'in_progress':
                line = self.format_task_line(task, width - 2)
                lines.append("│ " + line.ljust(width - 3) + "│")
                displayed_count += 1
        
        # 然後顯示待辦任務
        for task in todos:
            if displayed_count >= max_display:
                break
            if task.get('status') == 'pending':
                line = self.format_task_line(task, width - 2)
                lines.append("│ " + line.ljust(width - 3) + "│")
                displayed_count += 1
        
        # 然後顯示已完成的任務
        for task in todos:
            if displayed_count >= max_display:
                break
            if task.get('status') == 'completed':
                line = self.format_task_line(task, width - 2)
                lines.append("│ " + line.ljust(width - 3) + "│")
                displayed_count += 1
        
        if displayed_count < max_display and todos:
            remaining = len(todos) - displayed_count
            if remaining > 0:
                lines.append(f"│ ... 還有 {remaining} 個任務".ljust(width - 1) + "│")
        
        lines.append("└" + "─" * (width - 2) + "┘")
        
        return "\n".join(lines)
    
    def build_panel(self) -> str:
        """構建面板"""
        if self.config.compact_mode:
            return self.build_panel_compact()
        else:
            return self.build_panel_full()
    
    def display_at_position(self, panel_text: str) -> str:
        """根據位置調整面板顯示"""
        lines = panel_text.split("\n")
        
        # 這裡只返回面板文本，實際位置由調用者決定
        # 在實際集成時，可以使用 ANSI 控制碼進行位置控制
        
        return panel_text
    
    def update(self) -> str:
        """更新面板並返回內容"""
        self.last_update = datetime.now()
        self._stats['total_updates'] += 1
        panel = self.build_panel()
        return self.display_at_position(panel)
    
    def start_auto_refresh(self, callback: Optional[Any] = None) -> None:
        """開始自動刷新"""
        self.is_running = True
        
        def refresh_loop() -> None:
            while self.is_running:
                try:
                    updated_panel = self.update()
                    if callback:
                        callback(updated_panel)
                    time.sleep(self.config.refresh_interval)
                except Exception as e:
                    print(f"面板更新錯誤: {e}")
                    time.sleep(1)
        
        self.refresh_thread = threading.Thread(target=refresh_loop, daemon=True)
        self.refresh_thread.start()
    
    def stop_auto_refresh(self) -> None:
        """停止自動刷新"""
        self.is_running = False
        if self.refresh_thread:
            self.refresh_thread.join(timeout=2)

class TaskPanelDisplay:
    """任務面板顯示管理器"""
    
    def __init__(self, position: str = "top-left") -> None:
        """初始化顯示器"""
        config = TaskPanelConfig(position=position)
        self.panel = RealTimeTaskPanel(config)
        self.last_panel_lines = 0
    
    def get_ansi_position_code(self, row: int, col: int) -> str:
        """獲取 ANSI 位置碼"""
        return f"\033[{row};{col}H"
    
    def get_ansi_clear_code(self) -> str:
        """獲取 ANSI 清除碼"""
        return "\033[2J\033[H"
    
    def display_panel(self) -> None:
        """在終端顯示面板"""
        panel_text = self.panel.update()
        print(panel_text)
    
    def get_panel_text(self) -> str:
        """獲取面板文本"""
        return self.panel.update()

def main() -> None:
    """主函數 - 測試面板"""
    panel = TaskPanelDisplay(position="top-right")
    
    # 顯示面板
    panel.display_panel()
    
    print("\n" + "="*50)
    print("面板配置:")
    print(f"  位置: {panel.panel.config.position}")
    print(f"  寬度: {panel.panel.config.width}")
    print(f"  刷新間隔: {panel.panel.config.refresh_interval}s")
    
    # 顯示性能統計
    stats = panel.panel.get_stats()
    print("\n性能統計:")
    print(f"  總更新次數: {stats['total_updates']}")
    print(f"  緩存命中率: {stats['hit_rate']}")
    print("="*50)

if __name__ == "__main__":
    main()
