#!/usr/bin/env python3
"""
Task Panel Controller - CLI Tool
任務面板控制器 - 用於激活和管理任務面板
"""

import os
import sys
import json
import argparse
import logging
from pathlib import Path
from typing import Optional, List, Any

# 添加項目根目錄
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, project_root)

from src.core.task_panel_persistence import get_task_panel_manager

# 配置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)
logger = logging.getLogger(__name__)

def activate_panel(username: str, tasks_json: Optional[str] = None) -> Any:
    """激活任務面板"""
    manager = get_task_panel_manager()
    
    initial_tasks = []
    if tasks_json:
        try:
            initial_tasks = json.loads(tasks_json)
        except json.JSONDecodeError:
            logger.error('❌ Invalid JSON for tasks')
            return False
    
    success = manager.activate(username, initial_tasks)
    if success:
        logger.info(f'✅ Task panel activated for {username}')
        summary = manager.get_summary()
        logger.info(f'📊 Current tasks: {summary["total"]}')
        logger.info(f'   - Completed: {summary["completed"]}')
        logger.info(f'   - In Progress: {summary["in_progress"]}')
        logger.info(f'   - Pending: {summary["pending"]}')
    else:
        logger.error('❌ Failed to activate task panel')
    
    return success

def deactivate_panel() -> Any:
    """停用任務面板"""
    manager = get_task_panel_manager()
    success = manager.deactivate()
    if success:
        logger.info('✅ Task panel deactivated')
    else:
        logger.error('❌ Failed to deactivate task panel')
    return success

def add_task(content: str, priority: str = 'medium', status: str = 'pending') -> Any:
    """添加任務"""
    manager = get_task_panel_manager()
    try:
        task = manager.add_task(content, status, priority)
        logger.info(f'✅ Task added: {task.id}')
        logger.info(f'   Content: {task.content}')
        logger.info(f'   Status: {task.status}')
        logger.info(f'   Priority: {task.priority}')
        return True
    except Exception as e:
        logger.error(f'❌ Failed to add task: {e}')
        return False

def update_status(task_id: str, status: str) -> Any:
    """更新任務狀態"""
    manager = get_task_panel_manager()
    task = manager.update_task_status(task_id, status)
    if task:
        logger.info(f'✅ Task {task_id} updated to {status}')
        return True
    else:
        logger.error(f'❌ Task {task_id} not found')
        return False

def list_tasks(status: Optional[str] = None) -> Any:
    """列出任務"""
    manager = get_task_panel_manager()
    
    if status:
        tasks = manager.get_tasks_by_status(status)
        logger.info(f'📋 Tasks with status "{status}":')
    else:
        summary = manager.get_summary()
        tasks = summary['tasks']
        logger.info(f'📋 All tasks ({len(tasks)} total):')
    
    if tasks:
        for i, task in enumerate(tasks, 1):
            task_dict = task if isinstance(task, dict) else vars(task)
            status_icon = {
                'completed': '✅',
                'in_progress': '🔵',
                'pending': '⬜',
                'cancelled': '❌'
            }.get(task_dict.get('status'), '❓')
            
            priority_icon = {
                'high': '🔴',
                'medium': '🟡',
                'low': '🟢'
            }.get(task_dict.get('priority'), '⚪')
            
            logger.info(f'  {i}. {status_icon} {priority_icon} {task_dict.get("content", "Untitled")}')
            logger.info(f'     ID: {task_dict.get("id")}')
    else:
        logger.info('  No tasks found')

def show_summary() -> Any:
    """顯示摘要"""
    manager = get_task_panel_manager()
    summary = manager.get_summary()
    
    logger.info('📊 Task Panel Summary:')
    logger.info(f'  Activated: {"✅ Yes" if summary["activated"] else "❌ No"}')
    logger.info(f'  Total Tasks: {summary["total"]}')
    logger.info(f'    - ✅ Completed: {summary["completed"]}')
    logger.info(f'    - 🔵 In Progress: {summary["in_progress"]}')
    logger.info(f'    - ⬜ Pending: {summary["pending"]}')
    logger.info(f'    - ❌ Cancelled: {summary["cancelled"]}')
    
    if summary['session_info']:
        logger.info(f'  Session: {summary["session_info"].get("username")} ({summary["session_info"].get("role")})')

def export_state() -> Any:
    """導出狀態"""
    manager = get_task_panel_manager()
    export_data = manager.export_state()
    
    logger.info('💾 Task Panel State:')
    print(json.dumps(export_data, ensure_ascii=False, indent=2))

def clear_all() -> Any:
    """清除所有"""
    manager = get_task_panel_manager()
    success = manager.clear_all()
    if success:
        logger.info('✅ All tasks and state cleared')
    else:
        logger.error('❌ Failed to clear state')
    return success

def main() -> Any:
    """主函數"""
    parser = argparse.ArgumentParser(
        description='Task Panel Controller - Manage persisted task states',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Activate task panel
  python task_panel_controller.py activate --user alice
  
  # Activate with initial tasks
  python task_panel_controller.py activate --user alice --tasks '[{"content": "Task 1", "priority": "high"}]'
  
  # Add a task
  python task_panel_controller.py add --content "New task" --priority high
  
  # List all tasks
  python task_panel_controller.py list
  
  # List pending tasks
  python task_panel_controller.py list --status pending
  
  # Update task status
  python task_panel_controller.py update --id task_0_1234567890 --status completed
  
  # Show summary
  python task_panel_controller.py summary
  
  # Export state
  python task_panel_controller.py export
  
  # Deactivate
  python task_panel_controller.py deactivate
  
  # Clear all
  python task_panel_controller.py clear
        '''
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Activate command
    activate_parser = subparsers.add_parser('activate', help='Activate task panel')
    activate_parser.add_argument('--user', '-u', required=True, help='Username')
    activate_parser.add_argument('--tasks', '-t', help='Initial tasks as JSON')
    
    # Deactivate command
    subparsers.add_parser('deactivate', help='Deactivate task panel')
    
    # Add command
    add_parser = subparsers.add_parser('add', help='Add a task')
    add_parser.add_argument('--content', '-c', required=True, help='Task content')
    add_parser.add_argument('--priority', '-p', choices=['low', 'medium', 'high'], default='medium')
    add_parser.add_argument('--status', '-s', choices=['pending', 'in_progress', 'completed', 'cancelled'], 
                           default='pending')
    
    # Update command
    update_parser = subparsers.add_parser('update', help='Update task status')
    update_parser.add_argument('--id', '-i', required=True, help='Task ID')
    update_parser.add_argument('--status', '-s', required=True, 
                              choices=['pending', 'in_progress', 'completed', 'cancelled'])
    
    # List command
    list_parser = subparsers.add_parser('list', help='List tasks')
    list_parser.add_argument('--status', '-s', choices=['pending', 'in_progress', 'completed', 'cancelled'],
                            help='Filter by status')
    
    # Summary command
    subparsers.add_parser('summary', help='Show task summary')
    
    # Export command
    subparsers.add_parser('export', help='Export task panel state')
    
    # Clear command
    subparsers.add_parser('clear', help='Clear all tasks and state')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Execute command
    if args.command == 'activate':
        activate_panel(args.user, args.tasks)
    elif args.command == 'deactivate':
        deactivate_panel()
    elif args.command == 'add':
        add_task(args.content, args.priority, args.status)
    elif args.command == 'update':
        update_status(args.id, args.status)
    elif args.command == 'list':
        list_tasks(args.status)
    elif args.command == 'summary':
        show_summary()
    elif args.command == 'export':
        export_state()
    elif args.command == 'clear':
        clear_all()

if __name__ == '__main__':
    main()
