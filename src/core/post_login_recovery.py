#!/usr/bin/env python3
"""
Post-Login Auto-Recovery System
登入後自動恢復系統 - 自動回顧任務進度和歷史對話
"""

import os
import sys
import json
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

# 添加項目根目錄
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

logger = logging.getLogger(__name__)


class PostLoginAutoRecovery:
    """登入後自動恢復管理器"""
    
    def __init__(self, user_id: str = None):
        """初始化恢復管理器"""
        self.user_id = user_id or 'default'
        self.memory_dir = Path('/root/comic_ai/data/user_memory')
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        
        self.user_memory_file = self.memory_dir / f'{self.user_id}_memory.md'
        self.task_history_file = self.memory_dir / f'{self.user_id}_task_history.json'
        self.dialogue_history_file = self.memory_dir / f'{self.user_id}_dialogue_history.json'
        self.recovery_log_file = self.memory_dir / f'{self.user_id}_recovery_log.json'
        
        logger.info('✅ Post-Login Auto-Recovery Manager initialized')
    
    def get_last_session_info(self) -> Dict[str, Any]:
        """獲取上次會話信息"""
        try:
            if self.recovery_log_file.exists():
                with open(self.recovery_log_file, 'r', encoding='utf-8') as f:
                    logs = json.load(f)
                    if logs:
                        return logs[-1]  # 返回最後一次記錄
            return {}
        except Exception as e:
            logger.error(f'❌ Failed to get last session info: {e}')
            return {}
    
    def get_task_progress(self) -> Dict[str, Any]:
        """獲取任務進度"""
        try:
            task_history = {}
            if self.task_history_file.exists():
                with open(self.task_history_file, 'r', encoding='utf-8') as f:
                    task_history = json.load(f)
            
            # 計算任務統計
            tasks = task_history.get('tasks', [])
            completed = len([t for t in tasks if t.get('status') == 'completed'])
            in_progress = len([t for t in tasks if t.get('status') == 'in_progress'])
            pending = len([t for t in tasks if t.get('status') == 'pending'])
            total = len(tasks)
            
            # 找出最近修改的任務
            recent_tasks = sorted(
                tasks, 
                key=lambda x: x.get('last_updated', ''), 
                reverse=True
            )[:3]
            
            return {
                'total': total,
                'completed': completed,
                'in_progress': in_progress,
                'pending': pending,
                'completion_rate': f'{int(100 * completed / total) if total > 0 else 0}%',
                'recent_tasks': recent_tasks,
                'last_update': task_history.get('last_updated', 'Unknown')
            }
        except Exception as e:
            logger.error(f'❌ Failed to get task progress: {e}')
            return {}
    
    def get_dialogue_history(self, limit: int = 5) -> List[Dict[str, Any]]:
        """獲取對話歷史"""
        try:
            if self.dialogue_history_file.exists():
                with open(self.dialogue_history_file, 'r', encoding='utf-8') as f:
                    dialogues = json.load(f)
                    return dialogues[-limit:] if len(dialogues) > limit else dialogues
            return []
        except Exception as e:
            logger.error(f'❌ Failed to get dialogue history: {e}')
            return []
    
    def generate_memory_md(self) -> str:
        """生成 memory.md 文件內容"""
        try:
            content = []
            content.append(f"# 用戶記憶 - {self.user_id}")
            content.append(f"\n**更新時間**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            
            # 1. 上次會話信息
            content.append("## 📅 上次會話信息\n")
            last_session = self.get_last_session_info()
            if last_session:
                last_login = last_session.get('login_time', '未知')
                last_logout = last_session.get('logout_time', '未知')
                session_duration = last_session.get('duration', '未知')
                content.append(f"- **上次登入**: {last_login}")
                content.append(f"- **上次登出**: {last_logout}")
                content.append(f"- **會話時長**: {session_duration}\n")
            else:
                content.append("- 無上次會話記錄\n")
            
            # 2. 任務進度回顧
            content.append("## 📋 任務進度回顧\n")
            task_progress = self.get_task_progress()
            if task_progress:
                content.append(f"### 任務統計")
                content.append(f"- **總任務數**: {task_progress.get('total', 0)}")
                content.append(f"- **已完成**: {task_progress.get('completed', 0)} ✅")
                content.append(f"- **進行中**: {task_progress.get('in_progress', 0)} 🔵")
                content.append(f"- **待辦**: {task_progress.get('pending', 0)} ⬜")
                content.append(f"- **完成率**: {task_progress.get('completion_rate', '0%')}\n")
                
                # 最近的任務
                recent = task_progress.get('recent_tasks', [])
                if recent:
                    content.append("### 最近修改的任務")
                    for i, task in enumerate(recent, 1):
                        status_emoji = {
                            'completed': '✅',
                            'in_progress': '🔵',
                            'pending': '⬜',
                            'cancelled': '❌'
                        }.get(task.get('status'), '❓')
                        
                        content.append(f"{i}. {status_emoji} {task.get('content', 'Untitled')}")
                        content.append(f"   - 優先級: {task.get('priority', 'medium')}")
                        content.append(f"   - 狀態: {task.get('status', 'unknown')}")
                        content.append(f"   - 最後更新: {task.get('last_updated', '未知')}\n")
            else:
                content.append("- 無任務記錄\n")
            
            # 3. 對話歷史
            content.append("## 💬 最近的對話歷史\n")
            dialogues = self.get_dialogue_history()
            if dialogues:
                for i, dialogue in enumerate(dialogues, 1):
                    content.append(f"### 對話 {i}")
                    content.append(f"**時間**: {dialogue.get('timestamp', '未知')}")
                    content.append(f"**主題**: {dialogue.get('topic', '未分類')}")
                    content.append(f"**用戶**: {dialogue.get('user_message', '...')[:100]}")
                    content.append(f"**回應**: {dialogue.get('assistant_message', '...')[:100]}\n")
            else:
                content.append("- 無對話記錄\n")
            
            # 4. 建議和提醒
            content.append("## 💡 建議和提醒\n")
            
            pending_count = task_progress.get('pending', 0)
            if pending_count > 0:
                content.append(f"- 🔔 您有 {pending_count} 個待辦任務需要開始")
            
            in_progress_count = task_progress.get('in_progress', 0)
            if in_progress_count > 0:
                content.append(f"- ⏳ 您有 {in_progress_count} 個進行中的任務")
            
            completion_rate = task_progress.get('completion_rate', '0%')
            if completion_rate != '0%':
                content.append(f"- 🎯 當前完成率: {completion_rate}")
            
            if last_session:
                last_update = task_progress.get('last_update', '')
                if last_update:
                    content.append(f"- ⏱️ 上次任務更新: {last_update}\n")
            
            # 5. 快速導航
            content.append("## 🚀 快速導航\n")
            content.append("- [查看所有任務](#任務進度回顧)")
            content.append("- [查看對話歷史](#最近的對話歷史)")
            content.append("- [管理任務](../../src/cli/task_panel_controller.py)\n")
            
            # 6. 元數據
            content.append("---\n")
            content.append(f"**生成時間**: {datetime.now().isoformat()}")
            content.append(f"**用戶**: {self.user_id}\n")
            
            return '\n'.join(content)
        except Exception as e:
            logger.error(f'❌ Failed to generate memory.md: {e}')
            return ""
    
    def save_memory_md(self) -> bool:
        """保存 memory.md"""
        try:
            content = self.generate_memory_md()
            with open(self.user_memory_file, 'w', encoding='utf-8') as f:
                f.write(content)
            logger.info(f'✅ Memory.md saved: {self.user_memory_file}')
            return True
        except Exception as e:
            logger.error(f'❌ Failed to save memory.md: {e}')
            return False
    
    def log_recovery_event(self, event_type: str, details: Dict[str, Any]) -> bool:
        """記錄恢復事件"""
        try:
            logs = []
            if self.recovery_log_file.exists():
                with open(self.recovery_log_file, 'r', encoding='utf-8') as f:
                    logs = json.load(f)
            
            event = {
                'timestamp': datetime.now().isoformat(),
                'type': event_type,
                'details': details
            }
            logs.append(event)
            
            # 只保留最近 100 條記錄
            if len(logs) > 100:
                logs = logs[-100:]
            
            with open(self.recovery_log_file, 'w', encoding='utf-8') as f:
                json.dump(logs, f, ensure_ascii=False, indent=2)
            
            logger.info(f'✅ Recovery event logged: {event_type}')
            return True
        except Exception as e:
            logger.error(f'❌ Failed to log recovery event: {e}')
            return False
    
    def update_task_history(self, tasks: List[Dict[str, Any]]) -> bool:
        """更新任務歷史"""
        try:
            history = {
                'user_id': self.user_id,
                'last_updated': datetime.now().isoformat(),
                'tasks': tasks
            }
            
            with open(self.task_history_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, ensure_ascii=False, indent=2)
            
            logger.info('✅ Task history updated')
            return True
        except Exception as e:
            logger.error(f'❌ Failed to update task history: {e}')
            return False
    
    def add_dialogue(self, user_message: str, assistant_message: str, topic: str = '通用') -> bool:
        """添加對話記錄"""
        try:
            dialogues = []
            if self.dialogue_history_file.exists():
                with open(self.dialogue_history_file, 'r', encoding='utf-8') as f:
                    dialogues = json.load(f)
            
            dialogue = {
                'timestamp': datetime.now().isoformat(),
                'topic': topic,
                'user_message': user_message,
                'assistant_message': assistant_message
            }
            dialogues.append(dialogue)
            
            # 只保留最近 100 條對話
            if len(dialogues) > 100:
                dialogues = dialogues[-100:]
            
            with open(self.dialogue_history_file, 'w', encoding='utf-8') as f:
                json.dump(dialogues, f, ensure_ascii=False, indent=2)
            
            logger.info('✅ Dialogue added')
            return True
        except Exception as e:
            logger.error(f'❌ Failed to add dialogue: {e}')
            return False
    
    def execute_auto_recovery(self) -> Dict[str, Any]:
        """執行自動恢復流程"""
        try:
            logger.info('🚀 Starting post-login auto-recovery...')
            
            # 1. 記錄登入事件
            self.log_recovery_event('login', {
                'user_id': self.user_id,
                'login_time': datetime.now().isoformat()
            })
            
            # 2. 生成並保存 memory.md
            self.save_memory_md()
            
            # 3. 獲取任務進度
            task_progress = self.get_task_progress()
            
            # 4. 獲取最近的對話
            recent_dialogues = self.get_dialogue_history(limit=3)
            
            # 5. 記錄恢復完成
            self.log_recovery_event('recovery_completed', {
                'task_progress': task_progress,
                'dialogue_count': len(recent_dialogues),
                'memory_file': str(self.user_memory_file)
            })
            
            result = {
                'success': True,
                'user_id': self.user_id,
                'task_progress': task_progress,
                'recent_dialogues': recent_dialogues,
                'memory_file': str(self.user_memory_file),
                'timestamp': datetime.now().isoformat()
            }
            
            logger.info('✅ Post-login auto-recovery completed successfully')
            return result
        except Exception as e:
            logger.error(f'❌ Auto-recovery failed: {e}')
            return {'success': False, 'error': str(e)}
    
    def get_summary(self) -> str:
        """獲取摘要"""
        task_progress = self.get_task_progress()
        summary = f"""
📊 用戶 {self.user_id} 恢復摘要:
  - 任務總數: {task_progress.get('total', 0)}
  - 已完成: {task_progress.get('completed', 0)}
  - 進行中: {task_progress.get('in_progress', 0)}
  - 待辦: {task_progress.get('pending', 0)}
  - 完成率: {task_progress.get('completion_rate', '0%')}
"""
        return summary.strip()


def main():
    """測試主函數"""
    logging.basicConfig(level=logging.INFO, format='%(message)s')
    
    # 創建恢復管理器
    recovery = PostLoginAutoRecovery('alice')
    
    # 模擬任務數據
    sample_tasks = [
        {
            'id': 'task_1',
            'content': '完成功能 A',
            'status': 'completed',
            'priority': 'high',
            'last_updated': (datetime.now() - timedelta(days=1)).isoformat()
        },
        {
            'id': 'task_2',
            'content': '測試功能 B',
            'status': 'in_progress',
            'priority': 'high',
            'last_updated': datetime.now().isoformat()
        },
        {
            'id': 'task_3',
            'content': '文檔編寫',
            'status': 'pending',
            'priority': 'medium',
            'last_updated': (datetime.now() - timedelta(hours=2)).isoformat()
        }
    ]
    
    # 模擬對話數據
    recovery.add_dialogue(
        '如何改進系統性能？',
        '可以考慮優化數據庫查詢、增加緩存層、使用 CDN 等方式。',
        '技術討論'
    )
    recovery.add_dialogue(
        '下一步計劃是什麼？',
        '計劃是完成功能 B 的測試，然後進行系統集成。',
        '項目進度'
    )
    
    # 更新任務歷史
    recovery.update_task_history(sample_tasks)
    
    # 執行自動恢復
    print("\n🚀 執行自動恢復流程...\n")
    result = recovery.execute_auto_recovery()
    
    # 顯示摘要
    print(recovery.get_summary())
    
    # 顯示生成的 memory.md 內容
    print("\n" + "="*60)
    print("📄 生成的 memory.md 內容:")
    print("="*60 + "\n")
    
    with open(recovery.user_memory_file, 'r', encoding='utf-8') as f:
        print(f.read())


if __name__ == '__main__':
    main()
