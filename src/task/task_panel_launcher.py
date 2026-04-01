#!/usr/bin/env python3
"""
Quick Launch Script for Task Panel
快速啟動腳本 - 用於實時任務面板
"""

import os
import sys

# 添加項目根目錄
project_root = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, project_root)

from src.cli.enhanced_cli import EnhancedCliWithPanel


def print_intro():
    """打印介紹信息"""
    print("\n" + "="*60)
    print("🚀 Comic AI 實時任務面板".center(60))
    print("="*60)
    print("\n選擇啟動模式:")
    print("  1️⃣  交互模式 (推薦) - 實時面板 + 互動菜單")
    print("  2️⃣  自動更新模式 - 自動刷新面板")
    print("  3️⃣  緊湊模式 - 簡潔的面板顯示")
    print("  4️⃣  自定義配置 - 設置位置和間隔")
    print("\n選擇 (1-4) 或按 Enter 使用默認 (1): ", end="")


def main():
    """主函數"""
    print_intro()
    
    try:
        choice = input().strip() or "1"
        
        if choice == "1":
            cli = EnhancedCliWithPanel(panel_position="top-left")
            cli.run_interactive()
        
        elif choice == "2":
            cli = EnhancedCliWithPanel(panel_position="top-right")
            cli.run_auto_update_mode(update_interval=3)
        
        elif choice == "3":
            cli = EnhancedCliWithPanel(panel_position="top-left")
            cli.panel.config.compact_mode = True
            cli.run_auto_update_mode(update_interval=2)
        
        elif choice == "4":
            print("\n配置設置:")
            
            print("選擇面板位置 (1=左上, 2=右上, 3=左下, 4=右下): ", end="")
            pos_choice = input().strip() or "1"
            positions = {
                "1": "top-left",
                "2": "top-right",
                "3": "bottom-left",
                "4": "bottom-right"
            }
            position = positions.get(pos_choice, "top-left")
            
            print("設置更新間隔（秒，默認 3）: ", end="")
            try:
                interval = int(input().strip() or "3")
            except ValueError:
                interval = 3
            
            print("使用緊湊模式？(y/n，默認 n): ", end="")
            compact = input().strip().lower() == 'y'
            
            cli = EnhancedCliWithPanel(panel_position=position)
            cli.panel.config.compact_mode = compact
            cli.run_auto_update_mode(update_interval=interval)
        
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
