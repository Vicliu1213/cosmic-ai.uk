#!/usr/bin/env python3
"""
互動式儀表版系統 - Interactive Dashboard System
密交互式版本，提供即時監控和交互功能
"""

import os
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import curses
import time
from enum import Enum

class DashboardMode(Enum):
    """儀表版模式"""
    OVERVIEW = "overview"
    PROGRESS = "progress"
    SYSTEM = "system"
    RECOVERY = "recovery"
    QUANTUM = "quantum"

class InteractiveDashboard:
    """互動式儀表版"""
    
    def __init__(self):
        self.base_path = Path("/workspaces/cosmic-ai.uk")
        self.system_path = self.base_path / "system"
        self.data_path = self.base_path / "data"
        self.current_mode = DashboardMode.OVERVIEW
        self.running = True
        self.refresh_rate = 1  # 秒
        
    def load_progress_data(self) -> Dict[str, Any]:
        """加載進度數據"""
        progress_file = self.system_path / "tracking" / "PROGRESS_TRACKER.md"
        if progress_file.exists():
            with open(progress_file, 'r', encoding='utf-8') as f:
                content = f.read()
                return {"status": "loaded", "size": len(content)}
        return {"status": "not_found"}
    
    def load_memory_data(self) -> Dict[str, Any]:
        """加載記憶數據"""
        memory_file = self.base_path / "memory.md"
        if memory_file.exists():
            size = memory_file.stat().st_size
            with open(memory_file, 'r', encoding='utf-8') as f:
                lines = len(f.readlines())
            return {"status": "loaded", "size": size, "lines": lines}
        return {"status": "not_found"}
    
    def load_recovery_state(self) -> Dict[str, Any]:
        """加載恢復狀態"""
        state_file = self.data_path / "state" / ".recovery_state.json"
        if state_file.exists():
            try:
                with open(state_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {"status": "error"}
        return {"status": "not_found"}
    
    def load_quantum_state(self) -> Dict[str, Any]:
        """加載量子狀態"""
        state_file = self.data_path / "state" / ".quantum_state.json"
        if state_file.exists():
            try:
                with open(state_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {"status": "error"}
        return {"status": "not_found"}
    
    def get_overview_data(self) -> Dict[str, Any]:
        """獲取概覽數據"""
        return {
            "timestamp": datetime.now().isoformat(),
            "progress": self.load_progress_data(),
            "memory": self.load_memory_data(),
            "recovery": self.load_recovery_state(),
            "quantum": self.load_quantum_state(),
        }
    
    def format_size(self, size: int) -> str:
        """格式化文件大小"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f}{unit}"
            size /= 1024
        return f"{size:.1f}TB"
    
    def print_header(self, title: str):
        """打印頭部"""
        width = 80
        print("\n" + "="*width)
        print(f"  {title}".center(width))
        print("="*width + "\n")
    
    def print_section(self, title: str):
        """打印章節"""
        print(f"\n[{title}]")
        print("-" * 60)
    
    def display_overview(self):
        """顯示概覽"""
        self.print_header("🎯 Cosmic AI 互動式儀表版 - 系統概覽")
        
        data = self.get_overview_data()
        
        # 進度信息
        self.print_section("進度追蹤 (A 層)")
        progress = data["progress"]
        if progress["status"] == "loaded":
            print(f"✅ 進度追蹤已加載")
            print(f"   大小: {self.format_size(progress['size'])}")
        else:
            print(f"❌ 進度追蹤未找到")
        
        # 記憶信息
        self.print_section("系統記憶 (B 層)")
        memory = data["memory"]
        if memory["status"] == "loaded":
            print(f"✅ 系統記憶已加載")
            print(f"   大小: {self.format_size(memory['size'])}")
            print(f"   行數: {memory['lines']}")
        else:
            print(f"❌ 系統記憶未找到")
        
        # 恢復狀態
        self.print_section("恢復系統狀態")
        recovery = data["recovery"]
        if recovery.get("status") == "active":
            print(f"✅ 恢復系統活躍")
            print(f"   最後恢復時間: {recovery.get('last_recovery', 'N/A')}")
            print(f"   恢復次數: {recovery.get('recovery_count', 0)}")
        else:
            print(f"⚠️  恢復系統: {recovery.get('status', '未知')}")
        
        # 量子狀態
        self.print_section("量子系統狀態")
        quantum = data["quantum"]
        if quantum.get("status") == "active":
            print(f"✅ 量子系統活躍")
            print(f"   活躍系統: {quantum.get('active_systems', 0)}")
            print(f"   量子噪聲: {quantum.get('quantum_noise', 'N/A')}")
        else:
            print(f"⚠️  量子系統: {quantum.get('status', '未知')}")
        
        # 時間戳
        self.print_section("系統信息")
        print(f"更新時間: {data['timestamp']}")
        print(f"工作目錄: {self.base_path}")
    
    def display_progress_detail(self):
        """顯示進度詳細信息"""
        self.print_header("📊 進度追蹤詳細信息")
        
        progress_file = self.system_path / "tracking" / "PROGRESS_TRACKER.md"
        if progress_file.exists():
            with open(progress_file, 'r', encoding='utf-8') as f:
                content = f.read()
                # 只顯示前 50 行
                lines = content.split('\n')[:50]
                for line in lines:
                    print(line)
                if len(content.split('\n')) > 50:
                    print("\n... (更多內容，請查看完整文件)")
        else:
            print("❌ 進度追蹤文件未找到")
    
    def display_memory_detail(self):
        """顯示記憶詳細信息"""
        self.print_header("💾 系統記憶詳細信息")
        
        memory_file = self.base_path / "memory.md"
        if memory_file.exists():
            with open(memory_file, 'r', encoding='utf-8') as f:
                content = f.read()
                # 只顯示前 50 行
                lines = content.split('\n')[:50]
                for line in lines:
                    print(line)
                if len(content.split('\n')) > 50:
                    print("\n... (更多內容，請查看完整文件)")
        else:
            print("❌ 系統記憶文件未找到")
    
    def display_system_status(self):
        """顯示系統狀態"""
        self.print_header("🔧 系統狀態信息")
        
        self.print_section("文件夾結構")
        folders = [
            ("系統文件夾", self.system_path),
            ("數據文件夾", self.data_path),
            ("文檔文件夾", self.base_path / "docs"),
            ("集成文件夾", self.base_path / "integration"),
        ]
        
        for name, path in folders:
            if path.exists():
                file_count = len(list(path.rglob("*")))
                print(f"✅ {name}: {path.name} ({file_count} 項)")
            else:
                print(f"❌ {name}: {path.name} (不存在)")
        
        self.print_section("關鍵文件")
        key_files = [
            ("進度追蹤", self.system_path / "tracking" / "PROGRESS_TRACKER.md"),
            ("系統記憶", self.base_path / "memory.md"),
            ("導覽索引", self.system_path / "navigation" / "INDEX.md"),
            ("恢復系統", self.system_path / "recovery" / "cosmic_auto_recovery.py"),
        ]
        
        for name, file_path in key_files:
            if file_path.exists():
                size = file_path.stat().st_size
                print(f"✅ {name}: {self.format_size(size)}")
            else:
                print(f"❌ {name}: 不存在")
    
    def display_menu(self):
        """顯示菜單"""
        print("\n" + "="*60)
        print("  選擇視圖 (Select View)".center(60))
        print("="*60)
        print("""
[1] 📊 概覽 (Overview)
[2] 📈 進度詳細 (Progress Detail)
[3] 💾 記憶詳細 (Memory Detail)
[4] 🔧 系統狀態 (System Status)
[5] 🔄 重新整理 (Refresh)
[0] 退出 (Exit)

請輸入選擇 (Enter choice): """, end="")
    
    def run_interactive(self):
        """運行互動模式"""
        while self.running:
            try:
                # 清屏
                os.system('clear' if os.name == 'posix' else 'cls')
                
                # 顯示菜單
                self.display_menu()
                choice = input().strip()
                
                # 處理選擇
                if choice == "1":
                    os.system('clear' if os.name == 'posix' else 'cls')
                    self.display_overview()
                    input("\n按 Enter 繼續...")
                elif choice == "2":
                    os.system('clear' if os.name == 'posix' else 'cls')
                    self.display_progress_detail()
                    input("\n按 Enter 繼續...")
                elif choice == "3":
                    os.system('clear' if os.name == 'posix' else 'cls')
                    self.display_memory_detail()
                    input("\n按 Enter 繼續...")
                elif choice == "4":
                    os.system('clear' if os.name == 'posix' else 'cls')
                    self.display_system_status()
                    input("\n按 Enter 繼續...")
                elif choice == "5":
                    continue
                elif choice == "0":
                    print("\n👋 退出儀表版，再見！")
                    self.running = False
                else:
                    print("❌ 無效選擇，請重試")
                    time.sleep(1)
            
            except KeyboardInterrupt:
                print("\n\n👋 由用戶中斷，退出儀表版")
                self.running = False
            except Exception as e:
                print(f"❌ 錯誤: {e}")
                input("\n按 Enter 繼續...")

def main():
    """主函數"""
    dashboard = InteractiveDashboard()
    
    # 顯示歡迎信息
    print("\n🚀 啟動互動式儀表版...")
    time.sleep(1)
    
    # 運行互動模式
    dashboard.run_interactive()

if __name__ == "__main__":
    main()
