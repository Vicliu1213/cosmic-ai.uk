#!/usr/bin/env python3
"""
EthanAlgoX 策略对标系统初始化脚本
"""

import os
import sys
from pathlib import Path

def setup_directories():
    """创建必要的目录"""
    dirs = [
        "src/integrations/strategy_adapters",
        "src/backtesting",
        "reports/benchmarking",
        "data/backtest_results",
    ]
    
    for d in dirs:
        Path(d).mkdir(parents=True, exist_ok=True)
        print(f"✅ 创建目录: {d}")

def create_init_files():
    """创建 __init__.py 文件"""
    dirs = [
        "src/integrations/strategy_adapters",
        "src/backtesting",
    ]
    
    for d in dirs:
        init_file = Path(d) / "__init__.py"
        init_file.touch(exist_ok=True)
        print(f"✅ 创建: {init_file}")

def print_next_steps():
    """打印下一步说明"""
    print("\n" + "="*60)
    print("🎉 策略对标系统初始化完成！")
    print("="*60)
    print("\n📋 下一步:")
    print("1. 审查对标计划: cat ETHANALGOX_STRATEGY_BENCHMARKING_PLAN.md")
    print("2. 创建统一策略接口: python src/integrations/strategy_interface.py")
    print("3. 开发策略适配层")
    print("4. 运行对标测试")
    print("\n📚 相关文档:")
    print("- ETHANALGOX_STRATEGY_BENCHMARKING_PLAN.md (完整方案)")
    print("- memory.md (进度记录)")
    print("- task/task.md (任务追踪)")

if __name__ == "__main__":
    print("\n🚀 初始化 EthanAlgoX 策略对标系统...")
    setup_directories()
    create_init_files()
    print_next_steps()
