#!/usr/bin/env python3
"""
Dual Panel Quick Launcher
雙框面板快速啟動器
"""

import os
import sys

project_root = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, project_root)

from src.core.dual_task_panel import InteractiveDualPanel


def main():
    """主函數"""
    print("\n" + "="*60)
    print("🎯 實時任務面板 - 即時任務 vs 完成任務".center(60))
    print("="*60)
    print("\n選擇啟動模式:")
    print("  1️⃣  交互模式 (推薦) - 帶菜單的面板")
    print("  2️⃣  自動更新模式 - 自動刷新")
    print("  3️⃣  緊湊模式 - 簡潔顯示")
    print("\n選擇 (1-3) 或按 Enter 使用默認 (1): ", end="")
    
    try:
        choice = input().strip() or "1"
        
        if choice in ["1", "2", "3"]:
            panel = InteractiveDualPanel()
            
            if choice == "1":
                # 交互模式
                panel.run()
            elif choice == "2":
                # 自動更新模式
                panel.panel.display()
                panel.auto_update_mode(interval=3)
            elif choice == "3":
                # 緊湊模式
                panel.panel.config.compact_mode = True
                panel.panel.display()
                panel.auto_update_mode(interval=2)
        else:
            print("❌ 無效選項")
            sys.exit(1)
    
    except KeyboardInterrupt:
        print("\n\n👋 程序已退出")
    except Exception as e:
        print(f"❌ 錯誤: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
