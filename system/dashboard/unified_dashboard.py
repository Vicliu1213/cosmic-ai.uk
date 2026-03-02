#!/usr/bin/env python3
"""
統一整合儀表版系統 - Unified Integrated Dashboard System
密交互式版本，整合進度追蹤、系統記憶、導覽索引、恢復系統等
"""

import os
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import time
from enum import Enum

class SystemComponent(Enum):
    """系統組件"""
    PROGRESS = "progress"      # A 層 - 進度追蹤
    MEMORY = "memory"          # B 層 - 系統記憶
    INDEX = "index"            # C 層 - 導覽索引
    RECOVERY = "recovery"      # 恢復系統
    QUANTUM = "quantum"        # 量子系統
    STATUS = "status"          # 系統狀態

class UnifiedDashboard:
    """統一整合儀表版"""
    
    def __init__(self):
        self.base_path = Path("/workspaces/cosmic-ai.uk")
        self.system_path = self.base_path / "system"
        self.data_path = self.base_path / "data"
        self.running = True
        
        # 組件路徑
        self.components = {
            SystemComponent.PROGRESS: self.system_path / "tracking" / "PROGRESS_TRACKER.md",
            SystemComponent.MEMORY: self.base_path / "memory.md",
            SystemComponent.INDEX: self.system_path / "navigation" / "INDEX.md",
            SystemComponent.RECOVERY: self.data_path / "state" / ".recovery_state.json",
            SystemComponent.QUANTUM: self.data_path / "state" / ".quantum_state.json",
        }
    
    def load_component(self, component: SystemComponent) -> Dict[str, Any]:
        """加載組件數據"""
        path = self.components.get(component)
        
        if not path:
            return {"status": "not_found"}
        
        if not path.exists():
            return {"status": "not_found"}
        
        try:
            if path.suffix == ".json":
                with open(path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.split('\n')
                    return {
                        "status": "loaded",
                        "size": len(content),
                        "lines": len(lines),
                        "content": content,
                    }
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def clear_screen(self):
        """清屏"""
        os.system('clear' if os.name == 'posix' else 'cls')
    
    def print_header(self, title: str, width: int = 80):
        """打印頭部"""
        print("\n" + "="*width)
        print(f"  {title}".center(width))
        print("="*width + "\n")
    
    def print_section(self, title: str, icon: str = ""):
        """打印章節"""
        separator = "─" * 60
        if icon:
            print(f"\n{icon} {title}")
        else:
            print(f"\n[{title}]")
        print(separator)
    
    def format_size(self, size: int) -> str:
        """格式化文件大小"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f}{unit}"
            size /= 1024
        return f"{size:.1f}TB"
    
    # ==================== 主儀表版視圖 ====================
    
    def display_unified_dashboard(self):
        """顯示統一儀表版"""
        self.clear_screen()
        self.print_header("🎯 Cosmic AI 統一整合儀表版", 80)
        
        # 加載所有組件
        progress_data = self.load_component(SystemComponent.PROGRESS)
        memory_data = self.load_component(SystemComponent.MEMORY)
        index_data = self.load_component(SystemComponent.INDEX)
        recovery_data = self.load_component(SystemComponent.RECOVERY)
        quantum_data = self.load_component(SystemComponent.QUANTUM)
        
        # ═══════════════ A 層 - 進度追蹤 ═══════════════
        self.print_section("A 層 - 進度追蹤", "📈")
        if progress_data.get("status") == "loaded":
            print(f"✅ 已加載 | 大小: {self.format_size(progress_data['size'])} | 行數: {progress_data['lines']}")
            # 顯示前 10 行
            lines = progress_data['content'].split('\n')[:10]
            for line in lines:
                if line.strip():
                    print(f"   {line[:76]}")
            print("   ...")
        else:
            print(f"❌ 未找到")
        
        # ═══════════════ B 層 - 系統記憶 ═══════════════
        self.print_section("B 層 - 系統記憶", "💾")
        if memory_data.get("status") == "loaded":
            print(f"✅ 已加載 | 大小: {self.format_size(memory_data['size'])} | 行數: {memory_data['lines']}")
            # 顯示前 10 行
            lines = memory_data['content'].split('\n')[:10]
            for line in lines:
                if line.strip():
                    print(f"   {line[:76]}")
            print("   ...")
        else:
            print(f"❌ 未找到")
        
        # ═══════════════ C 層 - 導覽索引 ═══════════════
        self.print_section("C 層 - 導覽索引", "🗂️")
        if index_data.get("status") == "loaded":
            print(f"✅ 已加載 | 大小: {self.format_size(index_data['size'])} | 行數: {index_data['lines']}")
            # 顯示前 10 行
            lines = index_data['content'].split('\n')[:10]
            for line in lines:
                if line.strip():
                    print(f"   {line[:76]}")
            print("   ...")
        else:
            print(f"❌ 未找到")
        
        # ═══════════════ 系統狀態 ═══════════════
        self.print_section("系統狀態", "⚙️")
        
        # 恢復系統
        if recovery_data.get("status") in ["active", "loaded"]:
            print(f"✅ 恢復系統: 活躍")
            print(f"   最後恢復: {recovery_data.get('last_recovery', 'N/A')}")
            print(f"   恢復次數: {recovery_data.get('recovery_count', 0)}")
        else:
            print(f"⚠️  恢復系統: {recovery_data.get('status', '未知')}")
        
        # 量子系統
        if quantum_data.get("status") in ["active", "loaded"]:
            print(f"✅ 量子系統: 活躍")
            print(f"   活躍系統: {quantum_data.get('active_systems', 0)}")
        else:
            print(f"⚠️  量子系統: {quantum_data.get('status', '未知')}")
        
        # 時間戳
        self.print_section("信息", "ℹ️")
        print(f"更新時間: {datetime.now().isoformat()}")
        print(f"工作目錄: {self.base_path}")
    
    def display_progress_full(self):
        """顯示進度追蹤完整內容"""
        self.clear_screen()
        self.print_header("📊 A 層 - 進度追蹤詳細", 80)
        
        data = self.load_component(SystemComponent.PROGRESS)
        if data.get("status") == "loaded":
            lines = data['content'].split('\n')
            # 顯示前 60 行
            for i, line in enumerate(lines[:60], 1):
                print(line)
            
            if len(lines) > 60:
                remaining = len(lines) - 60
                print(f"\n... 還有 {remaining} 行，請查看完整文件")
        else:
            print("❌ 無法加載進度追蹤文件")
    
    def display_memory_full(self):
        """顯示系統記憶完整內容"""
        self.clear_screen()
        self.print_header("💾 B 層 - 系統記憶詳細", 80)
        
        data = self.load_component(SystemComponent.MEMORY)
        if data.get("status") == "loaded":
            lines = data['content'].split('\n')
            # 顯示前 60 行
            for i, line in enumerate(lines[:60], 1):
                print(line)
            
            if len(lines) > 60:
                remaining = len(lines) - 60
                print(f"\n... 還有 {remaining} 行，請查看完整文件")
        else:
            print("❌ 無法加載系統記憶文件")
    
    def display_index_full(self):
        """顯示導覽索引完整內容"""
        self.clear_screen()
        self.print_header("🗂️ C 層 - 導覽索引詳細", 80)
        
        data = self.load_component(SystemComponent.INDEX)
        if data.get("status") == "loaded":
            lines = data['content'].split('\n')
            # 顯示所有內容（INDEX 通常較小）
            for line in lines:
                print(line)
        else:
            print("❌ 無法加載導覽索引文件")
    
    def display_component_status(self):
        """顯示所有組件狀態"""
        self.clear_screen()
        self.print_header("🔍 系統組件狀態", 80)
        
        components_info = [
            ("A 層 - 進度追蹤", SystemComponent.PROGRESS, "📍"),
            ("B 層 - 系統記憶", SystemComponent.MEMORY, "💾"),
            ("C 層 - 導覽索引", SystemComponent.INDEX, "🗂️"),
            ("恢復系統", SystemComponent.RECOVERY, "🔄"),
            ("量子系統", SystemComponent.QUANTUM, "⚛️"),
        ]
        
        for name, component, icon in components_info:
            data = self.load_component(component)
            self.print_section(f"{icon} {name}", "")
            
            if data.get("status") == "loaded":
                size = data.get("size", 0)
                lines = data.get("lines", 0)
                print(f"✅ 已加載")
                print(f"   大小: {self.format_size(size)}")
                print(f"   行數/項目: {lines}")
            elif data.get("status") == "error":
                print(f"❌ 錯誤: {data.get('error', '未知錯誤')}")
            else:
                print(f"⚠️  狀態: {data.get('status', '未知')}")
            
            path = self.components.get(component)
            if path:
                print(f"   路徑: {path}")
    
    def display_system_health(self):
        """顯示系統健康檢查"""
        self.clear_screen()
        self.print_header("🏥 系統健康檢查", 80)
        
        checks = [
            ("系統文件夾", self.system_path),
            ("數據文件夾", self.data_path),
            ("進度追蹤文件", self.components[SystemComponent.PROGRESS]),
            ("系統記憶文件", self.components[SystemComponent.MEMORY]),
            ("導覽索引文件", self.components[SystemComponent.INDEX]),
            ("恢復狀態文件", self.components[SystemComponent.RECOVERY]),
            ("量子狀態文件", self.components[SystemComponent.QUANTUM]),
        ]
        
        health_score = 0
        total_checks = len(checks)
        
        for name, path in checks:
            if path.exists():
                if path.is_file():
                    size = path.stat().st_size
                    print(f"✅ {name}: {self.format_size(size)}")
                else:
                    items = len(list(path.rglob("*")))
                    print(f"✅ {name}: {items} 項")
                health_score += 1
            else:
                print(f"❌ {name}: 未找到")
        
        self.print_section("健康評分", "📈")
        percentage = int((health_score / total_checks) * 100)
        bar_length = 40
        filled = int(bar_length * health_score / total_checks)
        bar = "█" * filled + "░" * (bar_length - filled)
        print(f"狀態: [{bar}] {percentage}%")
        print(f"檢查: {health_score}/{total_checks} 通過")
        
        if health_score == total_checks:
            print("✅ 系統健康狀況良好！")
        elif health_score >= total_checks * 0.8:
            print("⚠️  系統基本正常，但有些組件缺失")
        else:
            print("❌ 系統需要維護")
    
    # ==================== 菜單系統 ====================
    
    def display_main_menu(self):
        """顯示主菜單"""
        self.clear_screen()
        self.print_header("🎯 Cosmic AI 統一整合儀表版 - 主菜單", 80)
        
        menu = """
┌─ 【核心視圖】
├─ [1] 📍 統一儀表版      - 所有層級信息概覽
├─ [2] 📈 A 層進度追蹤    - 進度詳細信息
├─ [3] 💾 B 層系統記憶    - 系統記憶詳細
├─ [4] 🗂️  C 層導覽索引   - 導覽索引詳細
│
├─ 【系統管理】
├─ [5] 🔍 組件狀態        - 查看所有組件狀態
├─ [6] 🏥 健康檢查        - 系統健康評分
│
├─ 【操作】
├─ [7] 🔄 刷新            - 重新加載所有數據
├─ [0] 👋 退出            - 退出儀表版
└─

請輸入選擇 (Enter choice): """
        
        print(menu, end="")
    
    def run(self):
        """運行儀表版"""
        while self.running:
            try:
                self.display_main_menu()
                choice = input().strip()
                
                if choice == "1":
                    self.display_unified_dashboard()
                    input("\n按 Enter 繼續...")
                elif choice == "2":
                    self.display_progress_full()
                    input("\n按 Enter 繼續...")
                elif choice == "3":
                    self.display_memory_full()
                    input("\n按 Enter 繼續...")
                elif choice == "4":
                    self.display_index_full()
                    input("\n按 Enter 繼續...")
                elif choice == "5":
                    self.display_component_status()
                    input("\n按 Enter 繼續...")
                elif choice == "6":
                    self.display_system_health()
                    input("\n按 Enter 繼續...")
                elif choice == "7":
                    print("\n🔄 刷新中...")
                    time.sleep(0.5)
                    continue
                elif choice == "0":
                    self.clear_screen()
                    print("\n👋 感謝使用 Cosmic AI 統一整合儀表版")
                    print("再見！\n")
                    self.running = False
                else:
                    print("\n❌ 無效選擇，請重試")
                    time.sleep(1)
            
            except KeyboardInterrupt:
                self.clear_screen()
                print("\n\n👋 由用戶中斷")
                print("再見！\n")
                self.running = False
            except EOFError:
                # 用於測試模式
                self.running = False
            except Exception as e:
                print(f"\n❌ 錯誤: {e}")
                import traceback
                traceback.print_exc()
                input("\n按 Enter 繼續...")

def main():
    """主函數"""
    print("\n🚀 啟動 Cosmic AI 統一整合儀表版...")
    time.sleep(1)
    
    dashboard = UnifiedDashboard()
    dashboard.run()

if __name__ == "__main__":
    main()
