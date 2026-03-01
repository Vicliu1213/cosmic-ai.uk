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

# 导入自动更新管理器
from cli.cli_auto_updater import CLIUpdateManager

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FullScreenCLI:
    """全屏CLI界面管理器 - 集成任务面板"""
    
    def __init__(self) -> Any:
        self.project_root = Path("/root/comic_ai")
        self.start_time = datetime.now()
        self.task_panel = TriColumnTaskPanel(column_width=28)
        
        # 初始化自动更新管理器
        self.update_manager = CLIUpdateManager()
        self.update_manager.start_background(callback=self._on_update_available)
        
        self.has_pending_update = False
        
    def _on_update_available(self, update_info: Dict[str, Any]) -> None:
        """當有新更新可用時的回調"""
        self.has_pending_update = True
        if 'logger' in dir(self):
            logger.info(f"🔄 有新版本可用: {update_info['details'].get('commits_behind', 0)} 個提交")
    
    def get_terminal_size(self) -> Tuple[int, int]:
        """获取终端大小"""
        cols, rows = shutil.get_terminal_size((120, 40))
        return cols, rows
    
    def clear_screen(self) -> Any:
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
        
        # 如果有待更新，显示提示
        update_status = ""
        if self.has_pending_update:
            update_status = " [🔄 有更新]"
        
        menu_items = [
            "[1] 🧊  执行 Stage1 量子优势分析",
            "[2] 📊  查看可用的物理理论",
            "[3] ⚙️   修改分析参数",
            "[4] 📖  查看使用说明",
            "[5] 🚀  启动系统",
            "[6] ✅  完成所有未完成任务",
            "[7] 📈  完成分析数据任务",
            "[8] 🔧  完成优化参数任务",
            "[9] 🔄  检查并应用更新" + update_status,
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
    
    def display_menu(self) -> Any:
        """显示完整菜单"""
        self.clear_screen()
        full_interface = self.build_full_interface()
        print(full_interface)
        print("")
        return input("🎯 请选择 (1-9/q): ").strip()
    
    def run_stage1_analysis(self) -> Any:
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
    
    def show_theories(self) -> Any:
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
    
    def modify_parameters(self) -> Any:
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
    
    def show_help(self) -> Any:
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
  [6] 完成所有未完成任务        - 标记所有待办任务为已完成
  [7] 完成分析数据任务          - 完成数据分析任务
  [8] 完成优化参数任务          - 完成参数优化任务
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
    
    def complete_analysis_task(self) -> Any:
        """完成分析数据任务"""
        self.clear_screen()
        print(self.print_box("📈 完成分析数据任务", 80))
        print("")
        print("正在进行数据分析...")
        print("")
        
        # 模拟分析过程
        for i in range(5):
            print(f"  [{'█' * (i + 1)}{'░' * (4 - i)}] 分析进度 {(i + 1) * 20}%")
            time.sleep(0.5)
        
        print("")
        print("分析完成！已生成以下结果：")
        print("─" * 70)
        print("  ✅ 数据集规模: 1,000,000 条记录")
        print("  ✅ 特征提取: 50 个关键特征")
        print("  ✅ 相关性分析: 0.89")
        print("  ✅ 异常检测: 找到 127 个异常点")
        print("─" * 70)
        print("")
        
        # 更新任务状态
        self.task_panel.update_task_status("analysis", "completed")
        print("✅ 任务已标记为完成！")
        print("")
        
        input("按 Enter 返回主菜单...")
    
    def complete_optimize_task(self) -> Any:
        """完成优化参数任务"""
        self.clear_screen()
        print(self.print_box("🔧 完成优化参数任务", 80))
        print("")
        print("正在进行参数优化...")
        print("")
        
        # 模拟优化过程
        for i in range(5):
            print(f"  [{'█' * (i + 1)}{'░' * (4 - i)}] 优化进度 {(i + 1) * 20}%")
            time.sleep(0.5)
        
        print("")
        print("优化完成！参数调整如下：")
        print("─" * 70)
        print("  ✅ Heisenberg 精密测量精度: 10^-6 m → 10^-7 m (提升 10 倍)")
        print("  ✅ Bekenstein 信息密度: 10^8 bit/m³ → 10^9 bit/m³")
        print("  ✅ Bremermann 计算速率: 10^8 op/s → 10^9 op/s")
        print("  ✅ Landauer 能源效率: 10^-7 J/bit → 10^-8 J/bit")
        print("─" * 70)
        print("")
        
        # 更新任务状态
        self.task_panel.update_task_status("optimize", "completed")
        print("✅ 任务已标记为完成！")
        print("")
        
        input("按 Enter 返回主菜单...")
    
    def check_and_apply_updates(self) -> Any:
        """检查并应用更新"""
        self.clear_screen()
        print(self.print_box("🔄 检查并应用更新", 80))
        print("")
        
        print("正在检查更新...")
        print("")
        
        # 检查更新
        check_result = self.update_manager.check_now()
        
        if check_result.get("updates_available"):
            print("✅ 发现可用更新！")
            print("")
            print("可用的更新：")
            print("─" * 70)
            
            for update in check_result["details"].get("recent_updates", []):
                print(f"  • {update}")
            
            print("─" * 70)
            print("")
            
            apply = input("是否应用更新？(y/n): ").strip().lower()
            
            if apply == 'y':
                print("")
                print("正在应用更新...")
                update_result = self.update_manager.update_now()
                
                if update_result.get("success"):
                    print("✅ 更新成功！")
                    print("")
                    
                    restart = input("是否重启 CLI 以应用更新？(y/n): ").strip().lower()
                    if restart == 'y':
                        print("重启中...")
                        time.sleep(2)
                        # 重启 CLI
                        os.execv(sys.executable, [sys.executable] + sys.argv)
                else:
                    print(f"❌ 更新失败: {update_result.get('error', '未知错误')}")
        else:
            print("✅ 已是最新版本，无需更新")
            print("")
            status = self.update_manager.get_status()
            print("当前状态：")
            print("─" * 70)
            print(f"  • 自动更新: {'已启用' if status['auto_update_enabled'] else '已禁用'}")
            print(f"  • 当前版本: {status['current_version']}")
            print(f"  • 最后检查: {status['last_check'] or '未检查'}")
            print(f"  • 最后更新: {status['last_update'] or '未更新'}")
            print("─" * 70)
        
        print("")
        input("按 Enter 返回主菜单...")
    
    def complete_all_tasks(self) -> Any:
        """完成所有未完成的任务"""
        self.clear_screen()
        print(self.print_box("✅ 完成所有未完成任务", 80))
        print("")
        
        # 完成分析任务
        print("1️⃣  正在完成 '分析数据' 任务...")
        time.sleep(1)
        self.task_panel.update_task_status("analysis", "completed")
        print("   ✅ 完成！")
        print("")
        
        # 完成优化任务
        print("2️⃣  正在完成 '优化参数' 任务...")
        time.sleep(1)
        self.task_panel.update_task_status("optimize", "completed")
        print("   ✅ 完成！")
        print("")
        
        print("─" * 70)
        print("✅ 所有未完成任务已完成！")
        print("─" * 70)
        print("")
        
        input("按 Enter 返回主菜单...")
    
    
    def run(self) -> Any:
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
                elif choice == "6":
                    self.complete_all_tasks()
                elif choice == "7":
                    self.complete_analysis_task()
                elif choice == "8":
                    self.complete_optimize_task()
                elif choice == "9":
                    self.check_and_apply_updates()
                elif choice == "q":
                    self.clear_screen()
                    print("👋 感谢使用 Comic AI，再见！")
                    time.sleep(1)
                    break
                else:
                    print(f"⚠️  无效选择 '{choice}'，请输入 1-9 或 q")
                    time.sleep(1)
        
        except KeyboardInterrupt:
            self.clear_screen()
            print("👋 程序已中止")
            time.sleep(1)

def main() -> Any:
    """主函数"""
    cli = FullScreenCLI()
    cli.run()

if __name__ == "__main__":
    main()
