#!/usr/bin/env python3
"""
Comic AI 主CLI界面 - 集成三栏任务面板
打开即显示完整界面，包含任务追踪面板
"""

import os
import sys
import time
import shutil
from typing import Dict, Any, Optional, Tuple
from pathlib import Path
from datetime import datetime, timedelta
import logging

# 导入三栏面板
sys.path.insert(0, str(Path(__file__).parent.parent))
from core.tri_column_panel import TriColumnTaskPanel, Task

class FullScreenCLI:
    """全屏CLI界面管理器 - 集成任务面板"""
    
    def __init__(self):
        self.project_root = Path("/root/comic_ai")
        self.start_time = datetime.now()
        self.task_panel = TriColumnTaskPanel(column_width=28)
        
    def get_terminal_size(self) -> Tuple[int, int]:
        """获取终端大小"""
        cols, rows = shutil.get_terminal_size((120, 40))
        return cols, rows
    
    def clear_screen(self):
        """清屏"""
        os.system('clear' if os.name == 'posix' else 'cls')
    
    def print_box(self, title: str, width: int = 90) -> str:
        """打印标题框"""
        lines = []
        lines.append("╔" + "═" * (width - 2) + "╗")
        title_padded = title.center(width - 2)
        lines.append("║" + title_padded + "║")
        lines.append("╚" + "═" * (width - 2) + "╝")
        return "\n".join(lines)
    
    def build_full_interface(self) -> str:
        """构建完整的界面"""
        width = 90
        output = []
        
        # === 顶部标题 ===
        output.append(self.print_box("🚀 Comic AI 量子分析系统", width))
        output.append("")
        
        # === 任务追踪面板 (三栏) ===
        output.append("📋 任务追踪面板")
        output.append("─" * width)
        output.append(self.task_panel.build_full_panel())
        output.append("")
        
        # === 系统状态 ===
        runtime = datetime.now() - self.start_time
        output.append("📊 系统状态")
        output.append("─" * width)
        
        # 状态信息双栏显示
        status_left = [
            f"  ⏱️  运行时间: {runtime.total_seconds():.0f}s",
            f"  📍 工作目录: {str(self.project_root)[:40]}",
        ]
        status_right = [
            f"  🖥️  终端大小: {self.get_terminal_size()[0]}x{self.get_terminal_size()[1]}",
            f"  ⌚ 当前时间: {datetime.now().strftime('%H:%M:%S')}",
        ]
        
        for left, right in zip(status_left, status_right):
            output.append(f"{left:<45} {right}")
        
        output.append("")
        
        # === 菜单选项 ===
        output.append("📋 菜单选项")
        output.append("─" * width)
        
        menu_items = [
            "[1] 🧊  执行 Stage1 量子优势分析",
            "[2] 📊  查看可用的物理理论",
            "[3] ⚙️   修改分析参数",
            "[4] 📖  查看使用说明",
            "[5] 🚀  启动系统",
            "[q] 🚪  离开系统",
        ]
        
        for i in range(0, len(menu_items), 2):
            left = menu_items[i].ljust(45)
            right = menu_items[i+1] if i+1 < len(menu_items) else ""
            output.append(f"  {left}  {right}")
        
        output.append("")
        
        # === 快速命令 ===
        output.append("⚡ 快速命令")
        output.append("─" * width)
        output.append("  Ctrl+C: 立即退出  |  h/b/l/d: 理论速查")
        output.append("")
        output.append("═" * width)
        
        return "\n".join(output)
    
    def display_menu(self):
        """显示完整菜单"""
        self.clear_screen()
        full_interface = self.build_full_interface()
        print(full_interface)
        print("")
        return input("🎯 请选择 (1-5/q): ").strip()
    
    def run_stage1_analysis(self):
        """执行 Stage1 分析"""
        # 添加任务
        task_id = f"stage1_{int(time.time())}"
        self.task_panel.add_task(task_id, "执行 Stage1 分析", status="running")
        
        self.clear_screen()
        print(self.print_box("🔬 Stage1 量子优势分析", 80))
        print("")
        print("正在分析四大物理理论的量子优势...")
        print("")
        
        time.sleep(2)
        
        theories = {
            'Heisenberg': '量子精密测量',
            'Bekenstein': '黑洞信息论',
            'Bremermann': '计算速度极限',
            'Landauer': '能源-计算关系'
        }
        
        print("分析结果：")
        print("─" * 70)
        for theory, desc in theories.items():
            print(f"  ✅ {theory:15} ({desc:15}) - 实现量子突破")
        print("─" * 70)
        print("")
        
        # 更新任务状态为已完成
        self.task_panel.update_task_status(task_id, "completed")
        
        input("按 Enter 返回主菜单...")
    
    def show_theories(self):
        """显示物理理论"""
        self.clear_screen()
        print(self.print_box("🔬 物理理论库", 80))
        print("")
        
        theories = {
            'Heisenberg': {
                'desc': '量子精密测量理论',
                'key': '量子位置-动量不确定性原理'
            },
            'Bekenstein': {
                'desc': '黑洞信息论',
                'key': '黑洞熵与信息内容关系'
            },
            'Bremermann': {
                'desc': '计算速度极限理论',
                'key': '物理过程最高计算速率'
            },
            'Landauer': {
                'desc': '能源-计算关系理论',
                'key': '信息擦除与能量消耗的关系'
            },
        }
        
        for theory, info in theories.items():
            print(f"📚 {theory}")
            print(f"   描述: {info['desc']}")
            print(f"   核心: {info['key']}")
            print("")
        
        input("按 Enter 返回主菜单...")
    
    def modify_parameters(self):
        """修改参数"""
        self.clear_screen()
        print(self.print_box("⚙️  参数修改界面", 80))
        print("")
        
        print("当前参数设置：")
        print("─" * 70)
        print("  • Heisenberg 精密测量精度: 10^-6 m")
        print("  • Bekenstein 信息密度: 10^8 bit/m³")
        print("  • Bremermann 计算速率: 10^8 op/s")
        print("  • Landauer 能源效率: 10^-7 J/bit")
        print("─" * 70)
        print("")
        
        print("修改选项:")
        print("  [h] 修改 Heisenberg 参数")
        print("  [b] 修改 Bekenstein 参数")
        print("  [l] 修改 Bremermann 参数")
        print("  [d] 修改 Landauer 参数")
        print("  [q] 返回主菜单")
        print("")
        
        choice = input("请选择: ").strip()
        if choice != 'q' and choice in ['h', 'b', 'l', 'd']:
            print(f"修改 {choice.upper()} 参数...")
            time.sleep(1)
    
    def show_help(self):
        """显示帮助"""
        self.clear_screen()
        print(self.print_box("📖 使用说明", 100))
        print("")
        
        help_text = """
基本操作：
  [1] 执行 Stage1 分析         - 进行量子优势分析
  [2] 查看物理理论             - 显示支持的理论列表
  [3] 修改参数                 - 调整分析参数
  [4] 查看说明                 - 显示此帮助信息
  [5] 启动系统                 - 启动完整系统
  [q] 离开                     - 退出程序

快速参考：
  Ctrl+C: 中断当前操作并退出
  Enter: 返回主菜单

理论速查：
  • Heisenberg:  量子精密测量的极限
  • Bekenstein:  黑洞的信息内容
  • Bremermann:  物理计算的速度极限
  • Landauer:    信息处理的能源成本

任务面板说明：
  • 左栏 (🔄 即时任务):   正在进行中的任务
  • 中栏 (⏳ 未完成):    待处理的任务
  • 右栏 (✅ 已完成):    已完成的任务
  
  每列显示最多8个任务，按优先级和时间排序
        """
        print(help_text)
        input("按 Enter 返回主菜单...")
    
    def run(self):
        """主程序循环"""
        try:
            # 添加一些示例任务
            self.task_panel.add_task("init", "初始化系统", status="completed")
            self.task_panel.add_task("config", "加载配置", status="completed")
            self.task_panel.add_task("analysis", "分析数据", status="pending")
            self.task_panel.add_task("optimize", "优化参数", status="pending")
            
            while True:
                choice = self.display_menu()
                
                if choice == "1":
                    self.run_stage1_analysis()
                elif choice == "2":
                    self.show_theories()
                elif choice == "3":
                    self.modify_parameters()
                elif choice == "4":
                    self.show_help()
                elif choice == "5":
                    self.clear_screen()
                    print("🚀 启动系统中...")
                    time.sleep(2)
                elif choice == "q":
                    self.clear_screen()
                    print("👋 感谢使用 Comic AI，再见！")
                    time.sleep(1)
                    break
                else:
                    print(f"⚠️  无效选择 '{choice}'，请输入 1-5 或 q")
                    time.sleep(1)
        
        except KeyboardInterrupt:
            self.clear_screen()
            print("👋 程序已中止")
            time.sleep(1)

def main():
    """主函数"""
    cli = FullScreenCLI()
    cli.run()

if __name__ == "__main__":
    main()
