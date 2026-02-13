#!/usr/bin/env python3
"""
Session Recap & Auto Review Module
會話回顧與自動審查模組

This module provides automatic session recap functionality to review previous work
and resume tasks automatically.
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timezone
import subprocess
import yaml

from dataclasses import dataclass, asdict


@dataclass
class GitCommit:
    """Git 提交記錄"""
    hash: str
    author: str
    date: str
    message: str
    files_changed: int


@dataclass
class SessionSummary:
    """會話摘要"""
    timestamp: str
    git_branch: str
    recent_commits: List[GitCommit]
    uncommitted_changes: List[str]
    git_status: str
    todos: List[Dict[str, Any]]
    recommendations: List[str]


class SessionRecap:
    """會話回顧系統"""
    
    def __init__(self, config_path: str = "config/session_recap_config.yaml"):
        """初始化會話回顧系統"""
        self.config = self._load_config(config_path)
        self.logger = self._setup_logging()
        
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """載入配置文件"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            self.logger = logging.getLogger(__name__)
            self.logger.warning(f"Config file not found: {config_path}")
            return {}
    
    def _setup_logging(self) -> logging.Logger:
        """設置日誌"""
        logger = logging.getLogger(__name__)
        
        if not logger.handlers:
            logging_config: Dict[str, Any] = self.config.get('logging', {}) or {}
            log_level: str = str(logging_config.get('level', 'INFO') or 'INFO')
            log_file: str = str(logging_config.get('file', 'logs/recap.log') or 'logs/recap.log')
            log_format: str = str(logging_config.get(
                'format', "[%(asctime)s] %(levelname)s: %(message)s"
            ) or "[%(asctime)s] %(levelname)s: %(message)s")
            
            # 創建日誌目錄
            os.makedirs(os.path.dirname(log_file), exist_ok=True)
            
            handler = logging.FileHandler(log_file)
            handler.setFormatter(logging.Formatter(log_format))
            logger.addHandler(handler)
            logger.setLevel(getattr(logging, log_level))
        
        return logger
    
    def get_git_branch(self) -> str:
        """獲取當前 Git 分支"""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                capture_output=True,
                text=True,
                cwd=os.getcwd()
            )
            return result.stdout.strip()
        except Exception as e:
            self.logger.error(f"Failed to get git branch: {e}")
            return "unknown"
    
    def get_recent_commits(self, max_commits: int = 10) -> List[GitCommit]:
        """獲取最近的 Git 提交"""
        try:
            result = subprocess.run(
                ["git", "log", f"--max-count={max_commits}", 
                 "--format=%H|%an|%ad|%s|%numstat"],
                capture_output=True,
                text=True,
                cwd=os.getcwd()
            )
            
            commits = []
            for line in result.stdout.strip().split('\n'):
                if line and '|' in line:
                    parts = line.split('|')
                    if len(parts) >= 4:
                        # 計算修改的文件數
                        files_changed = len([p for p in parts[4:] if p.strip()])
                        commits.append(GitCommit(
                            hash=parts[0][:7],
                            author=parts[1],
                            date=parts[2],
                            message=parts[3],
                            files_changed=files_changed
                        ))
            return commits
        except Exception as e:
            self.logger.error(f"Failed to get git commits: {e}")
            return []
    
    def get_git_status(self) -> Tuple[str, List[str]]:
        """獲取 Git 狀態"""
        try:
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True,
                text=True,
                cwd=os.getcwd()
            )
            
            status_lines = result.stdout.strip().split('\n') if result.stdout.strip() else []
            status_summary = subprocess.run(
                ["git", "status", "--short"],
                capture_output=True,
                text=True,
                cwd=os.getcwd()
            ).stdout.strip()
            
            return status_summary, status_lines
        except Exception as e:
            self.logger.error(f"Failed to get git status: {e}")
            return "unknown", []
    
    def get_todos(self) -> List[Dict[str, Any]]:
        """獲取待辦事項"""
        todo_file = self.config.get('task_tracking', {}).get('todo_file', '.session_todos.json')
        
        if os.path.exists(todo_file):
            try:
                with open(todo_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.error(f"Failed to load todos: {e}")
        
        return []
    
    def generate_recommendations(self, summary: SessionSummary) -> List[str]:
        """根據會話信息生成建議"""
        recommendations = []
        
        # 檢查是否有未提交的更改
        if summary.uncommitted_changes:
            recommendations.append(f"📌 有 {len(summary.uncommitted_changes)} 個未提交的文件變更")
        
        # 檢查待辦事項
        pending_todos = [t for t in summary.todos if t.get('status') == 'pending']
        if pending_todos:
            recommendations.append(f"📋 有 {len(pending_todos)} 個待辦任務需要完成")
        
        in_progress_todos = [t for t in summary.todos if t.get('status') == 'in_progress']
        if in_progress_todos:
            recommendations.append(f"⏳ 正在進行中的任務: {len(in_progress_todos)} 個")
        
        # 檢查最近的提交
        if summary.recent_commits:
            latest_commit = summary.recent_commits[0]
            recommendations.append(f"✅ 最後提交: {latest_commit.message[:50]}...")
        
        return recommendations
    
    def generate_recap(self) -> SessionSummary:
        """生成會話回顧"""
        branch = self.get_git_branch()
        commits = self.get_recent_commits(
            self.config.get('recap_strategy', {}).get('max_commits', 10)
        )
        status, changes = self.get_git_status()
        todos = self.get_todos()
        
        summary = SessionSummary(
            timestamp=datetime.now(timezone.utc).isoformat(),
            git_branch=branch,
            recent_commits=commits,
            uncommitted_changes=changes,
            git_status=status,
            todos=todos,
            recommendations=[]
        )
        
        summary.recommendations = self.generate_recommendations(summary)
        
        return summary
    
    def print_recap(self, summary: SessionSummary) -> None:
        """打印會話回顧"""
        print("\n" + "="*60)
        print("📋 會話回顧摘要 (Session Recap)")
        print("="*60)
        
        print(f"\n🕐 時間: {summary.timestamp}")
        print(f"🌿 分支: {summary.git_branch}")
        
        # 最近的提交
        if self.config.get('recap_strategy', {}).get('include_recent_commits'):
            print("\n📝 最近的提交:")
            for i, commit in enumerate(summary.recent_commits[:5], 1):
                print(f"  {i}. [{commit.hash}] {commit.message[:50]}")
        
        # 未提交的更改
        if self.config.get('recap_strategy', {}).get('include_git_status'):
            print(f"\n📂 未提交的更改:")
            if summary.uncommitted_changes:
                for change in summary.uncommitted_changes[:10]:
                    print(f"  {change}")
            else:
                print("  ✅ 工作目錄乾淨")
        
        # 待辦事項
        if self.config.get('output_format', {}).get('show_todos'):
            print(f"\n✓ 待辦事項:")
            for todo in summary.todos:
                todo_status: str = str(todo.get('status', 'unknown') or 'unknown')
                status_emoji = {
                    'pending': '⬜',
                    'in_progress': '🔵',
                    'completed': '✅',
                    'cancelled': '❌'
                }.get(todo_status, '❓')
                
                print(f"  {status_emoji} {todo.get('content', 'Unknown')}")
        
        # 建議
        if self.config.get('output_format', {}).get('show_recommendations'):
            print(f"\n💡 建議:")
            for rec in summary.recommendations:
                print(f"  {rec}")
        
        print("\n" + "="*60 + "\n")
    
    def save_recap_report(self, summary: SessionSummary) -> None:
        """保存回顧報告"""
        report_file = self.config.get('output_format', {}).get('report_file', 'logs/session_recap.md')
        
        os.makedirs(os.path.dirname(report_file), exist_ok=True)
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(f"# 會話回顧報告\n\n")
            f.write(f"**時間**: {summary.timestamp}\n")
            f.write(f"**分支**: {summary.git_branch}\n\n")
            
            f.write(f"## 最近提交\n\n")
            for commit in summary.recent_commits[:5]:
                f.write(f"- `{commit.hash}` - {commit.message}\n")
            
            f.write(f"\n## 待辦事項\n\n")
            for todo in summary.todos:
                status = todo.get('status', 'unknown')
                f.write(f"- [{status}] {todo.get('content', 'Unknown')}\n")
            
            f.write(f"\n## 建議\n\n")
            for rec in summary.recommendations:
                f.write(f"- {rec}\n")
        
        self.logger.info(f"Recap report saved to {report_file}")


def main():
    """主函數"""
    recap = SessionRecap()
    summary = recap.generate_recap()
    recap.print_recap(summary)
    
    if recap.config.get('output_format', {}).get('create_recap_report'):
        recap.save_recap_report(summary)


if __name__ == "__main__":
    main()
