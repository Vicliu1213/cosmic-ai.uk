#!/usr/bin/env python3
"""
優化版任務面板啟動器
Optimized Task Panel Launcher
"""

import os
import sys
import json
import time
from pathlib import Path
from datetime import datetime

project_root = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, project_root)

from src.core.task_panel import RealTimeTaskPanel, TaskPanelConfig


def load_todos() -> list:
    """加載任務"""
    todos_file = Path(project_root) / ".session_todos.json"
    if todos_file.exists():
        with open(todos_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []


def save_todos(todos: list):
    """保存任務"""
    todos_file = Path(project_root) / ".session_todos.json"
    with open(todos_file, 'w', encoding='utf-8') as f:
        json.dump(todos, f, ensure_ascii=False, indent=2)


def display_panel():
    """顯示優化面板"""
    config = TaskPanelConfig(
        position="top-left",
        width=50,
        refresh_interval=2,
        compact_mode=False
    )
    panel = RealTimeTaskPanel(config)
    print(panel.update())


def show_menu():
    """顯示菜單"""
    print("\n" + "="*50)
    print("📌 操作選項:")
    print("  1. 刷新面板")
    print("  2. 查看任務詳情")
    print("  3. 標記任務完成")
    print("  4. 自動更新模式")
    print("  5. 退出")
    print("="*50)


def auto_update_mode(interval: int = 3):
    """自動更新模式"""
    config = TaskPanelConfig(
        position="top-left",
        width=50,
        refresh_interval=interval,
        compact_mode=False
    )
    panel = RealTimeTaskPanel(config)
    
    print("\n🔄 自動更新模式 (按 Ctrl+C 退出)")
    try:
        while True:
            os.system('clear' if os.name == 'posix' else 'cls')
            print(panel.update())
            print(f"\n⏱ 每 {interval} 秒刷新 | 按 Ctrl+C 退出")
            time.sleep(interval)
    except KeyboardInterrupt:
        print("\n\n👋 已退出自動更新模式")


def main():
    """主函數"""
    os.system('clear' if os.name == 'posix' else 'cls')
    
    print("="*50)
    print("🚀 Comic AI 任務面板 (優化版)")
    print("="*50)
    print("\n選擇模式:")
    print("  1. 交互模式")
    print("  2. 自動更新模式")
    print("  3. 快速查看")
    print("\n選擇 (1-3): ", end="", flush=True)
    
    try:
        choice = input().strip() or "1"
        
        if choice == "1":
            while True:
                os.system('clear' if os.name == 'posix' else 'cls')
                display_panel()
                show_menu()
                print("\n選擇: ", end="", flush=True)
                action = input().strip()
                
                if action == "1":
                    continue
                elif action == "2":
                    todos = load_todos()
                    print("\n📋 任務詳情:")
                    for t in todos:
                        status = {"pending": "⬜", "in_progress": "🔵", "completed": "✅", "cancelled": "❌"}.get(t.get("status"), "❓")
                        priority = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(t.get("priority"), "⚪")
                        print(f"  {status}{priority} [{t.get('id')}] {t.get('content')}")
                    input("\n按 Enter 繼續...")
                elif action == "3":
                    todos = load_todos()
                    print("\n輸入任務 ID 標記完成: ", end="", flush=True)
                    task_id = input().strip()
                    for t in todos:
                        if t.get("id") == task_id:
                            t["status"] = "completed"
                            print(f"✅ 任務 {task_id} 已完成")
                            break
                    save_todos(todos)
                    input("按 Enter 繼續...")
                elif action == "4":
                    print("\n更新間隔 (秒，默認3): ", end="", flush=True)
                    try:
                        interval = int(input().strip() or "3")
                    except:
                        interval = 3
                    auto_update_mode(interval)
                elif action == "5":
                    print("\n👋 再見!")
                    break
        
        elif choice == "2":
            print("\n更新間隔 (秒，默認3): ", end="", flush=True)
            try:
                interval = int(input().strip() or "3")
            except:
                interval = 3
            auto_update_mode(interval)
        
        elif choice == "3":
            os.system('clear' if os.name == 'posix' else 'cls')
            display_panel()
    
    except KeyboardInterrupt:
        print("\n\n👋 程序已退出")
    except Exception as e:
        print(f"\n❌ 錯誤: {e}")


if __name__ == "__main__":
    main()
