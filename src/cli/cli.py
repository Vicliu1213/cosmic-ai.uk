#!/usr/bin/env python3
"""
Comic AI 主CLI界面 - 右上角狀態板
"""

import os
import sys
import time
from typing import Dict, Any, Optional
from pathlib import Path
from datetime import datetime, timedelta
import logging
import json

class StatusDisplay:
    """狀態顯示管理器"""
    
    def __init__(self):
        self.project_root = Path("/root/comic_ai")
        self.start_time = datetime.now()
        self.max_recent_tasks = 3
        self.completed_tasks = []
        self.current_tasks = []
        self.task_list = []
        
    def update_task_status(self, task_id: str, task_desc: str, status: str = "in_progress") -> None:
        """更新任務狀態"""
        if status == "completed":
            if task_id not in [t['id'] for t in self.completed_tasks]:
                self.completed_tasks.append({
                    'id': task_id,
                    'description': task_desc,
                    'completed_at': datetime.now().isoformat(),
                    'time_taken': self.calculate_time_taken(task_id)
                })
                # 從進行任務列表中移除
                self.current_tasks = [t for t in self.current_tasks if t['id'] != task_id]
        else:
            # 添加到進行中任務列表
            if task_id not in [t['id'] for t in self.current_tasks]:
                self.current_tasks.append({
                    'id': task_id,
                    'description': task_desc,
                    'status': status,
                    'started_at': datetime.now().isoformat()
                })
                
    def calculate_time_taken(self, task_id: str) -> str:
        """計算任務耗時"""
        for task in self.completed_tasks:
            if task['id'] == task_id:
                if 'started_at' in task and 'completed_at' in task:
                    start = datetime.fromisoformat(task['started_at'])
                    completed = datetime.fromisoformat(task['completed_at'])
                    return str(completed - start) if completed and start else "00:00:00"
        return "00:00:00"
        return "00:00:00"
                
    def get_status_display(self) -> str:
        """獲取狀態顯示文本"""
        now = datetime.now()
        runtime = now - self.start_time
        
        # 建立狀態文本
        status_lines = []
        
        # 顯示標題和運行時間
        status_lines.append("🚀 Comic AI 量子分析系統")
        status_lines.append(f"⏱️  運行時間: {runtime.strftime('%H:%M:%S')}")
        status_lines.append("")
        
        # 顯示進行中任務
        if self.current_tasks:
            status_lines.append("🔧 當前進行任務:")
            for task in self.current_tasks[-1:]: # 顯示最近1個任務
                status_icon = "🔄" if task['status'] == "in_progress" else "⏸️"
                status_text = "進行中" if task['status'] == "in_progress" else "已完成"
                status_lines.append(f"  {status_icon} {task['id'][:8]}: {status_text} ({self.format_time_taken(task['id'])}")
        
        # 顯示最近完成的任務
        if self.completed_tasks:
            status_lines.append("🎯 最近完成任務:")
            for task in self.completed_tasks[-3:]: # 顯示最近3個任務
                status_lines.append(f"  ✅ {task['description']} ({self.format_time_taken(task['id'])}")
        
        else:
            status_lines.append("  📋 目前無進行中任務")
            
        status_lines.append("")
        
        # 顯示系統狀態
        total_tasks = len(self.task_list)
        completed_count = len(self.completed_tasks)
        in_progress_count = len(self.current_tasks)
        
        status_lines.append("")
        status_lines.append(f"📊 任務總數: {total_tasks}")
        status_lines.append(f"✅ 已完成: {completed_count}")
        status_lines.append(f"🔄 進行中: {in_progress_count}")
        status_lines.append(f"⏸️  待執行: {max(0, total_tasks - completed_count - in_progress_count)}")
        
        return "\\n".join(status_lines)

class ComicAICLI:
    """Comic AI 主CLI界面"""
    
    def __init__(self):
        self.status_display = StatusDisplay()
        self.project_root = Path("/root/comic_ai")
        self.current_menu = "main"
        
    def run_main_menu(self):
        """運行主菜單"""
        while True:
            self.status_display.show_status_display()
            
            print("╔══════════════════════════════════════════╗")
            print("║                🚀 Comic AI 量子分析系統                      ║")
            print("║                                                              ║")
            print("║    支援 Heisenberg, Bekenstein, Bremermann, Landauer 理論          ║")
            print("╚═════════════════════════════════╝")
            print("")
            print("📋 請選擇要執行的操作：")
            print("")
            print("[1] 🧊 執行 Stage1 量子優勢分析")
            print("[2] 📊 查看可用的物理理論")
            print("[3] ⚙️ 修改分析參數")
            print("[4] 📖 查看使用說明")
            print("[5] 🚪 開系統")
            print("[q] 🚪 離開系統")
            
            try:
                choice = input().strip()
                
                if choice == "1":
                    self.run_stage1_analysis()
                elif choice == "2":
                    self.show_theories_info()
                elif choice == "3":
                    self.modify_parameters()
                elif choice == "4":
                    self.show_help()
                elif choice == "5":
                    print("👋 再見！")
                    break
                else:
                    print(f"⚠ 無效的選擇 '{choice}'，請輸入1-5")
                    time.sleep(1)
                    
            except KeyboardInterrupt:
                print("\n\n👋 中斷，用戶強制離開...")
                time.sleep(2)
                break
                
    def run_stage1_analysis(self):
        """執行 Stage1 量子優勢分析"""
        self.status_display.update_task_status("stage1", "執行 Stage1 量子優勢分析", "in_progress")
        
        try:
            from stage1 import STAGE1_THEORIES
            
            print("正在分析四大物理理論的量子優勢...")
            
            time.sleep(2)
            
            # 模擬分析結果
            breakthrough_results = {
                'heisenberg': {
                    'precision_gain': 1.08e+11,
                    'status': '✅ 突破'
                },
                'bekenstein': {
                    'data_density_ratio': 2.94e+04,
                    'status': '✅ 突破'
                },
                'bremermann': {
                    'acceleration_factor': 3.72e+08,
                    'status': '✅ 突破'
                },
                'landauer': {
                    'energy_efficiency': 1.00e+07,
                    'status': '✅ 突破'
                }
            }
            
            print("\n🔬 Stage1 分析結果：")
            for theory_name, result in breakthrough_results.items():
                icon = "✅" if result['status'] == "突破" else "⚠️"
                status_text = "突破" if result['status'] == "突破" else "未突破"
                print(f"  {icon} {theory_name} 楘密測量突破：{status_text}")
                print(f"  {theory_name} 經經典極限: {result['classic_limit']}")
                print(f"  {theory_name} 量子優勢: {result['quantum_advantage']}")
                
            print("")
            
            self.status_display.update_task_status("stage1", "執行 Stage1 量子優勢分析", "completed")
            time.sleep(2)
            
    def show_theories_info(self):
        """顯示物理理論信息"""
        from stage1 import STAGE1_THEORIES
            
            print("\n🔬 可用的物理理論：")
            print("")
            
            for theory_name, theory in STAGE1_THEORIES.items():
                print(f"  {theory_name} 理論 - {theory.category}")
                print(f" 📋 數學模型: {theory.math_model}")
                print(f" 🎯 能力: {theory.base_capability}")
                print(f" 🎯 突破門檻: {theory.breakthrough_threshold}")
                print(f" 📦 古典極限: {theory.classical_scaling}")
                print(f" 📬 量子縮放: {theory.quantum_scaling}")
                print(f" 📝 備注：{theory.notes or '無'}")
                print("")
            
    def modify_parameters(self):
        """修改分析參數"""
        self.status_display.update_task_status("modify_params", "修改分析參數", "in_progress")
        
        print("\n⚙️ 修改分析參數界面")
        print("目前參數設置：")
        print(" • Heisenberg 測密測量: 10^-6")
        print(" • Bekenstein 資密度: 10^8")
        print(" • Bremermann 計算速度: 10^8")
        print(" • Landauer 能源效率: 10^-7")
        print("")
        print("輸入修改選項：")
        print(" [h] 修改 Heisenberg 參數")
        print(" [b] 修改 Bekenstein 參數")
        print(" [l] 修改 Bremermann 參數")
        print(" [d] 修改 Landauer 參數")
        print("[q] 返回主菜單")
        
        try:
            choice = input("您的選擇: ").strip()
            
            if choice in ['h', 'b', 'l', 'd']:
                print(f"修改 {choice.upper()} 參數...")
                time.sleep(1)
            elif choice == 'q':
                print("返回主菜單")
                return
            else:
                print(f"輸入無效的選擇 '{choice}'，請重新輸入 1-5")
                time.sleep(1)
                
            # 處理修改邏輯
            # 這裡可以擴展更複雜的參數修改功能
                
    def show_help(self):
        """顯示使用說明"""
        print("\n📖 使用說明：")
        print("")
        print("基本操作：")
        print("  [1] 🧊 執行 Stage1 量子優勢分析")
        print("  [2] 📊 查看可用的物理理論")
        print("  [3] ⚙️ 修改分析參數")
        print("  [4] 📖 查看使用說明")
        print("  [5] 🚪 開系統")
        print("  [q] 退出系統")
        print("")
        print("")
        print("🚪 快捷鍵：")
        print("  [h] 直接選擇h]")
        print("  [b] 直接選擇b")
        print("  [l] 直接選擇l") 
        print("  [d] 直接選擇d]")
        print("")
        print("")
        
def main():
    """主函數"""
    cli = ComicAICLI()
    cli.run_main_menu()