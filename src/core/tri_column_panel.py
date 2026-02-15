#!/usr/bin/env python3
"""
三栏式任务面板 - 即时任务 | 未完成任务 | 已完成任务
显示实时任务追踪面板
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass, field

@dataclass
class Task:
    """任务数据类"""
    id: str
    title: str
    status: str  # 'running', 'pending', 'completed'
    priority: str = 'medium'  # 'high', 'medium', 'low'
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    
    def get_duration(self) -> str:
        """获取任务耗时"""
        if self.status == 'completed' and self.completed_at:
            duration = self.completed_at - self.created_at
            seconds = int(duration.total_seconds())
            minutes = seconds // 60
            seconds = seconds % 60
            if minutes > 0:
                return f"{minutes}m{seconds}s"
            return f"{seconds}s"
        elif self.status == 'running':
            duration = datetime.now() - self.created_at
            seconds = int(duration.total_seconds())
            minutes = seconds // 60
            seconds = seconds % 60
            if minutes > 0:
                return f"{minutes}m{seconds}s"
            return f"{seconds}s"
        return "-"


class TriColumnTaskPanel:
    """三栏式任务面板"""
    
    def __init__(self, column_width: int = 30):
        """初始化面板
        
        Args:
            column_width: 每列的宽度（字符数，不含边框）
        """
        self.column_width = column_width
        self.running_tasks: List[Task] = []
        self.pending_tasks: List[Task] = []
        self.completed_tasks: List[Task] = []
        self.max_rows = 8
    
    def add_task(self, task_id: str, title: str, status: str = 'pending', priority: str = 'medium'):
        """添加任务"""
        task = Task(id=task_id, title=title, status=status, priority=priority)
        
        if status == 'running':
            self.running_tasks.append(task)
        elif status == 'pending':
            self.pending_tasks.append(task)
        elif status == 'completed':
            task.completed_at = datetime.now()
            self.completed_tasks.append(task)
    
    def update_task_status(self, task_id: str, new_status: str):
        """更新任务状态"""
        # 从原列表移除
        for tasks_list in [self.running_tasks, self.pending_tasks, self.completed_tasks]:
            for task in tasks_list[:]:
                if task.id == task_id:
                    tasks_list.remove(task)
                    
                    # 添加到新列表
                    if new_status == 'running':
                        self.running_tasks.append(task)
                    elif new_status == 'pending':
                        self.pending_tasks.append(task)
                    elif new_status == 'completed':
                        task.completed_at = datetime.now()
                        self.completed_tasks.append(task)
                    
                    task.status = new_status
                    return
    
    def get_priority_emoji(self, priority: str) -> str:
        """获取优先级图标"""
        emoji_map = {
            'high': '🔴',
            'medium': '🟡',
            'low': '🟢'
        }
        return emoji_map.get(priority, '⚪')
    
    def format_task_line(self, task: Task) -> str:
        """格式化任务行"""
        priority_emoji = self.get_priority_emoji(task.priority)
        duration = task.get_duration()
        
        # 计算可用宽度
        available_width = self.column_width - 10
        
        # 截断标题
        title = task.title
        if len(title) > available_width:
            title = title[:available_width-3] + "..."
        
        # 组合显示
        line = f"{priority_emoji} {title:<{available_width}} {duration:>5}"
        return line[:self.column_width].ljust(self.column_width)
    
    def format_header(self, emoji: str, title: str, count: int) -> str:
        """格式化列标题"""
        header = f"{emoji} {title} ({count})"
        return header.ljust(self.column_width)
    
    def build_full_panel(self) -> str:
        """构建完整三栏面板"""
        lines = []
        
        # 顶部边框
        lines.append("┌" + "─" * self.column_width + "┬" + "─" * self.column_width + "┬" + "─" * self.column_width + "┐")
        
        # 列标题行
        header_left = self.format_header("🔄", "即时任务", len(self.running_tasks))
        header_middle = self.format_header("⏳", "未完成", len(self.pending_tasks))
        header_right = self.format_header("✅", "已完成", len(self.completed_tasks))
        
        lines.append(f"│{header_left}│{header_middle}│{header_right}│")
        
        # 分隔线
        lines.append("├" + "─" * self.column_width + "┼" + "─" * self.column_width + "┼" + "─" * self.column_width + "┤")
        
        # 任务行
        for row in range(self.max_rows):
            # 左列 (即时任务)
            if row < len(self.running_tasks):
                left = self.format_task_line(self.running_tasks[row])
            else:
                left = " " * self.column_width
            
            # 中列 (未完成任务)
            if row < len(self.pending_tasks):
                middle = self.format_task_line(self.pending_tasks[row])
            else:
                middle = " " * self.column_width
            
            # 右列 (已完成任务)
            if row < len(self.completed_tasks):
                right = self.format_task_line(self.completed_tasks[row])
            else:
                right = " " * self.column_width
            
            lines.append(f"│{left}│{middle}│{right}│")
        
        # 底部边框
        lines.append("└" + "─" * self.column_width + "┴" + "─" * self.column_width + "┴" + "─" * self.column_width + "┘")
        
        return "\n".join(lines)
    
    def print_panel(self):
        """打印面板"""
        print(self.build_full_panel())


# 测试代码
if __name__ == "__main__":
    import time
    
    panel = TriColumnTaskPanel(column_width=30)
    
    # 添加测试任务
    panel.add_task("task1", "初始化系统", status="completed")
    panel.add_task("task2", "加载配置", status="completed")
    panel.add_task("task3", "分析数据", status="running")
    panel.add_task("task4", "优化参数", status="running")
    panel.add_task("task5", "编译代码", status="pending")
    panel.add_task("task6", "运行测试", status="pending")
    panel.add_task("task7", "生成报告", status="pending")
    
    print("\n初始状态:")
    panel.print_panel()
    
    # 模拟任务完成
    print("\n\n等待2秒...")
    time.sleep(2)
    
    print("更新任务状态...")
    panel.update_task_status("task3", "completed")
    panel.update_task_status("task5", "running")
    
    print("\n更新后状态:")
    panel.print_panel()
