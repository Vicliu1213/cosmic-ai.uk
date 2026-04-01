#!/usr/bin/env python3
"""
Comic AI 激活介面主菜單
統一入口 - 顯示所有激活功能和狀態
"""

import os
import sys
import subprocess
import time
from pathlib import Path


class ActivationMainMenu:
    """激活主菜單"""
    
    def __init__(self):
        self.project_root = Path("/root/comic_ai")
    
    def clear_screen(self):
        """清屏"""
        os.system('clear' if os.name == 'posix' else 'cls')
    
    def display_menu(self):
        """顯示主菜單"""
        self.clear_screen()
        width = 100
        
        print("╔" + "═" * (width - 2) + "╗")
        print("║" + "🚀 Comic AI 激活介面主菜單".center(width - 2) + "║")
        print("║" + "所有激活功能統一入口".center(width - 2) + "║")
        print("╚" + "═" * (width - 2) + "╝")
        print()
        
        print("┌" + "─" * (width - 2) + "┐")
        print("│ " + "📊 激活狀態選項".ljust(width - 4) + " │")
        print("└" + "─" * (width - 2) + "┘")
        print()
        
        options = [
            {
                "key": "1",
                "title": "🎯 激活完成展示",
                "desc": "顯示所有激活步驟和完成狀態",
                "cmd": "activation_display.py"
            },
            {
                "key": "2",
                "title": "📋 激活狀態儀表板",
                "desc": "實時查看狀態、運行測試、啟動應用",
                "cmd": "activation_status_cli.py"
            },
            {
                "key": "3",
                "title": "🎬 運行完整演示",
                "desc": "展示所有 7 個系統功能的集成演示",
                "cmd": "demo_complete_system.py"
            },
            {
                "key": "4",
                "title": "🖥️  啟動所有應用",
                "desc": "使用 TMUX 同時啟動 7 個應用",
                "cmd": "setup_tmux_apps.sh"
            },
            {
                "key": "5",
                "title": "📖 查看文檔",
                "desc": "顯示各種使用和參考文檔",
                "cmd": "docs"
            },
            {
                "key": "6",
                "title": "🧪 運行測試",
                "desc": "執行完整測試套件 (218 項)",
                "cmd": "pytest"
            },
            {
                "key": "q",
                "title": "❌ 退出",
                "desc": "退出激活介面",
                "cmd": "quit"
            },
        ]
        
        for opt in options:
            print(f"  [{opt['key']}] {opt['title']:<40} - {opt['desc']}")
        
        print()
        print("═" * width)
        print()
        
        return input("🎯 請選擇 (1-6/q): ").strip().lower()
    
    def run_activation_display(self):
        """運行激活展示"""
        print("\n🎯 啟動激活完成展示...\n")
        result = subprocess.run(
            [sys.executable, str(self.project_root / "activation_display.py")],
            cwd=self.project_root
        )
    
    def run_activation_cli(self):
        """運行激活狀態 CLI"""
        print("\n📋 啟動激活狀態儀表板...\n")
        result = subprocess.run(
            [sys.executable, str(self.project_root / "activation_status_cli.py")],
            cwd=self.project_root
        )
    
    def run_demo(self):
        """運行演示系統"""
        print("\n🎬 啟動完整演示系統...\n")
        result = subprocess.run(
            [sys.executable, str(self.project_root / "demo_complete_system.py")],
            cwd=self.project_root
        )
    
    def launch_apps(self):
        """啟動應用"""
        print("\n🖥️  啟動應用環境...\n")
        result = subprocess.run(
            ["bash", str(self.project_root / "setup_tmux_apps.sh")],
            cwd=self.project_root
        )
        print("\n✅ 應用已在 TMUX 中啟動")
        print("   使用命令加入會話: tmux attach-session -t comic-ai-apps")
        input("\n按 Enter 返回菜單...")
    
    def show_documents(self):
        """顯示文檔菜單"""
        self.clear_screen()
        
        docs = [
            ("1", "QUICK_START.md", "3 步快速開始"),
            ("2", "APPS_USAGE_GUIDE.md", "詳細應用指南"),
            ("3", "ACTIVATION_STATUS_GUIDE.md", "激活狀態詳情"),
            ("4", "ACTIVATION_COMPLETE_REPORT.md", "完整激活報告"),
            ("5", "DOCUMENTATION_INDEX.md", "文檔導航索引"),
            ("q", "返回菜單", ""),
        ]
        
        print("📖 文檔選擇")
        print("═" * 60)
        for key, name, desc in docs:
            if desc:
                print(f"  [{key}] {name:<40} - {desc}")
            else:
                print(f"  [{key}] {name}")
        print()
        
        choice = input("🎯 選擇文檔 (1-5/q): ").strip().lower()
        
        if choice == "q":
            return
        
        doc_map = {
            "1": "QUICK_START.md",
            "2": "APPS_USAGE_GUIDE.md",
            "3": "ACTIVATION_STATUS_GUIDE.md",
            "4": "ACTIVATION_COMPLETE_REPORT.md",
            "5": "DOCUMENTATION_INDEX.md",
        }
        
        if choice in doc_map:
            doc_file = self.project_root / doc_map[choice]
            if doc_file.exists():
                with open(doc_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.split('\n')
                    
                    # 顯示前 80 行
                    self.clear_screen()
                    for line in lines[:80]:
                        print(line)
                    
                    print("\n... (更多內容請查看完整文件)")
                    input("\n按 Enter 返回...")
    
    def run_tests(self):
        """運行測試"""
        print("\n🧪 運行測試套件...\n")
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "src/tests/", "-v"],
            cwd=self.project_root
        )
    
    def run(self):
        """主循環"""
        try:
            while True:
                choice = self.display_menu()
                
                if choice == "1":
                    self.run_activation_display()
                elif choice == "2":
                    self.run_activation_cli()
                elif choice == "3":
                    self.run_demo()
                elif choice == "4":
                    self.launch_apps()
                elif choice == "5":
                    self.show_documents()
                elif choice == "6":
                    self.run_tests()
                elif choice == "q":
                    self.clear_screen()
                    print("👋 感謝使用 Comic AI 激活介面，再見！")
                    time.sleep(1)
                    break
                else:
                    print(f"⚠️  無效選擇 '{choice}'")
                    time.sleep(1)
        
        except KeyboardInterrupt:
            self.clear_screen()
            print("👋 程序已中止")
            time.sleep(1)


def main():
    """主函數"""
    menu = ActivationMainMenu()
    menu.run()


if __name__ == "__main__":
    main()
