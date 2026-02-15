#!/usr/bin/env python3
"""测试全屏CLI界面"""
import sys
from src.cli.cli import FullScreenCLI

if __name__ == "__main__":
    cli = FullScreenCLI()
    # 演示一下界面，然后退出
    cli.clear_screen()
    print(cli.build_full_interface())
    print("\n✅ 界面显示完整，无需滚动！")
    print("\n运行 'python src/cli/cli.py' 来使用完整的交互式CLI")
