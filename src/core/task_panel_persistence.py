#!/usr/bin/env python3
"""
Task Panel Persistence Manager
任務面板持久化管理器 - 在登入後激活並保存任務追蹤狀態
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass, asdict

# 添加項目根目錄
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, project_root)

logger = logging.getLogger(__name__)

@dataclass
class Task:
    """任務數據類"""
    id: str
    content: str
    status: str = "pending"  # pending, in_progress, completed, cancelled
    priority: str = "medium"  # low, medium, high
    timestamp: Optional[str] = None
    description: Optional[str] = None
    
    def __post_init__(self) -> Any:
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()

class TaskPanelPersistenceManager:
    """任務面板持久化管理器"""
    
    def __init__(self, storage_dir: Optional[str] = None) -> Any:
        """初始化任務面板持久化管理器"""
        if storage_dir is None:
            storage_dir = os.path.join(project_root, 'data', 'task_state')
        
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        self.tasks_file = self.storage_dir / 'tasks.json'
        self.state_file = self.storage_dir / 'panel_state.json'
        self.session_file = self.storage_dir / 'user_session.json'
        
        self.tasks: List[Task] = []
        self.activated = False
        self.session_info: Dict[str, Any] = {}
        
        self._load_state()
        logger.info('✅ Task Panel Persistence Manager initialized')
    
    def _load_state(self) -> None:
        """從文件加載狀態"""
        try:
            if self.tasks_file.exists():
                with open(self.tasks_file, 'r', encoding='utf-8') as f:
                    tasks_data = json.load(f)
                    self.tasks = [Task(**t) for t in tasks_data]
                logger.info(f'✅ Loaded {len(self.tasks)} tasks')
            
            if self.state_file.exists():
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    state_data = json.load(f)
                    self.activated = state_data.get('activated', False)
                logger.info(f'✅ Loaded panel state: activated={self.activated}')
            
            if self.session_file.exists():
                with open(self.session_file, 'r', encoding='utf-8') as f:
                    self.session_info = json.load(f)
                logger.info('✅ Loaded user session')
        except Exception as e:
            logger.error(f'❌ Failed to load state: {e}')
    
    def _save_state(self) -> None:
        """保存狀態到文件"""
        try:
            # 保存任務
            tasks_data = [asdict(t) for t in self.tasks]
            with open(self.tasks_file, 'w', encoding='utf-8') as f:
                json.dump(tasks_data, f, ensure_ascii=False, indent=2)
            
            # 保存面板狀態
            state_data = {
                'activated': self.activated,
                'timestamp': datetime.now().isoformat(),
                'task_count': len(self.tasks)
            }
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(state_data, f, ensure_ascii=False, indent=2)
            
            # 保存會話信息
            if self.session_info:
                with open(self.session_file, 'w', encoding='utf-8') as f:
                    json.dump(self.session_info, f, ensure_ascii=False, indent=2)
            
            logger.info('✅ State saved')
        except Exception as e:
            logger.error(f'❌ Failed to save state: {e}')
    
    def activate(self, username: str = 'user', initial_tasks: List[Dict] = None) -> bool:
        """激活任務面板"""
        try:
            self.activated = True
            self.session_info = {
                'username': username,
                'activated_at': datetime.now().isoformat(),
                'role': 'user'
            }
            
            # 如果提供了初始任務，就添加它們
            if initial_tasks:
                for task_data in initial_tasks:
                    task = Task(
                        id=f"task_{len(self.tasks)}_{int(datetime.now().timestamp())}",
                        content=task_data.get('content', 'Untitled'),
                        status=task_data.get('status', 'pending'),
                        priority=task_data.get('priority', 'medium'),
                        description=task_data.get('description')
                    )
                    self.tasks.append(task)
            
            self._save_state()
            logger.info(f'✅ Task Panel activated for {username}')
            return True
        except Exception as e:
            logger.error(f'❌ Failed to activate task panel: {e}')
            return False
    
    def deactivate(self) -> bool:
        """停用任務面板"""
        try:
            self.activated = False
            self._save_state()
            logger.info('✅ Task Panel deactivated')
            return True
        except Exception as e:
            logger.error(f'❌ Failed to deactivate task panel: {e}')
            return False
    
    def add_task(self, content: str, status: str = 'pending', priority: str = 'medium', 
                 description: Optional[str] = None) -> Task:
        """添加任務"""
        try:
            task = Task(
                id=f"task_{len(self.tasks)}_{int(datetime.now().timestamp() * 1000)}",
                content=content,
                status=status,
                priority=priority,
                description=description
            )
            self.tasks.append(task)
            self._save_state()
            logger.info(f'✅ Task added: {task.id}')
            return task
        except Exception as e:
            logger.error(f'❌ Failed to add task: {e}')
            raise
    
    def update_task_status(self, task_id: str, status: str) -> Optional[Task]:
        """更新任務狀態"""
        try:
            for task in self.tasks:
                if task.id == task_id:
                    task.status = status
                    self._save_state()
                    logger.info(f'✅ Task {task_id} status updated to {status}')
                    return task
            logger.warning(f'⚠️ Task {task_id} not found')
            return None
        except Exception as e:
            logger.error(f'❌ Failed to update task: {e}')
            return None
    
    def delete_task(self, task_id: str) -> bool:
        """刪除任務"""
        try:
            original_count = len(self.tasks)
            self.tasks = [t for t in self.tasks if t.id != task_id]
            if len(self.tasks) < original_count:
                self._save_state()
                logger.info(f'✅ Task {task_id} deleted')
                return True
            else:
                logger.warning(f'⚠️ Task {task_id} not found')
                return False
        except Exception as e:
            logger.error(f'❌ Failed to delete task: {e}')
            return False
    
    def get_tasks_by_status(self, status: str) -> List[Task]:
        """按狀態獲取任務"""
        return [t for t in self.tasks if t.status == status]
    
    def get_summary(self) -> Dict[str, Any]:
        """獲取任務摘要"""
        return {
            'total': len(self.tasks),
            'completed': len(self.get_tasks_by_status('completed')),
            'in_progress': len(self.get_tasks_by_status('in_progress')),
            'pending': len(self.get_tasks_by_status('pending')),
            'cancelled': len(self.get_tasks_by_status('cancelled')),
            'activated': self.activated,
            'session_info': self.session_info,
            'tasks': [asdict(t) for t in self.tasks]
        }
    
    def export_state(self) -> Dict[str, Any]:
        """導出完整狀態"""
        return {
            'version': '1.0.0',
            'export_date': datetime.now().isoformat(),
            'summary': self.get_summary(),
            'tasks': [asdict(t) for t in self.tasks],
            'session_info': self.session_info
        }
    
    def clear_all(self) -> bool:
        """清除所有任務和狀態"""
        try:
            self.tasks = []
            self.activated = False
            self.session_info = {}
            self._save_state()
            logger.info('✅ All tasks and state cleared')
            return True
        except Exception as e:
            logger.error(f'❌ Failed to clear state: {e}')
            return False
    
    def is_activated(self) -> bool:
        """檢查是否已激活"""
        return self.activated
    
    def restore_from_session(self) -> bool:
        """從保存的會話恢復"""
        try:
            if self.activated and self.session_info:
                logger.info(f'✅ Restored session: {self.session_info.get("username")}')
                return True
            return False
        except Exception as e:
            logger.error(f'❌ Failed to restore session: {e}')
            return False

# 全局實例
_task_panel_manager = None

def get_task_panel_manager(storage_dir: Optional[str] = None) -> TaskPanelPersistenceManager:
    """獲取全局任務面板管理器實例"""
    global _task_panel_manager
    if _task_panel_manager is None:
        _task_panel_manager = TaskPanelPersistenceManager(storage_dir)
    return _task_panel_manager

def main() -> Any:
    """測試主函數"""
    logging.basicConfig(level=logging.INFO, format='%(message)s')
    
    # 創建管理器
    manager = get_task_panel_manager()
    
    # 激活面板
    print("\n🚀 Activating Task Panel...")
    manager.activate('test_user', [
        {'content': '設置系統組件', 'priority': 'high'},
        {'content': '運行量子分析', 'priority': 'high'},
        {'content': '檢查結果', 'priority': 'medium'}
    ])
    
    # 添加更多任務
    print("\n📋 Adding tasks...")
    manager.add_task('完成數據導入', 'in_progress', 'high')
    manager.add_task('驗證分析結果', 'pending', 'medium')
    
    # 更新任務狀態
    print("\n✏️ Updating task status...")
    tasks = manager.get_tasks_by_status('in_progress')
    if tasks:
        manager.update_task_status(tasks[0].id, 'completed')
    
    # 顯示摘要
    print("\n📊 Task Summary:")
    summary = manager.get_summary()
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    
    # 顯示導出
    print("\n💾 Exporting state...")
    export_data = manager.export_state()
    print(json.dumps(export_data, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
