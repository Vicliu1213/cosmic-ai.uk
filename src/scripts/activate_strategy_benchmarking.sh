#!/bin/bash
# 🚀 EthanAlgoX 策略对标激活脚本
# 用于克隆和集成所有对标策略

set -e

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎯 EthanAlgoX 策略对标激活系统"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

REPO_ROOT="/workspaces/cosmic-ai.uk"
EXTERNAL_DIR="$REPO_ROOT/external"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Step 1: 创建目录结构
echo ""
echo "📁 Step 1: 创建项目目录结构..."
mkdir -p "$EXTERNAL_DIR"
mkdir -p "$REPO_ROOT/src/integrations/strategy_adapters"
mkdir -p "$REPO_ROOT/src/backtesting"
mkdir -p "$REPO_ROOT/reports/benchmarking"
mkdir -p "$REPO_ROOT/data/backtest_results"
echo "✅ 目录结构创建完成"

# Step 2: 克隆 Hummingbot
echo ""
echo "🤖 Step 2: 克隆 Hummingbot..."
if [ ! -d "$EXTERNAL_DIR/hummingbot" ]; then
    echo "📥 克隆 Hummingbot..."
    cd "$EXTERNAL_DIR"
    git clone --depth 1 https://github.com/hummingbot/hummingbot.git 2>/dev/null || {
        echo "⚠️ Hummingbot 克隆失败（可能是网络问题），继续..."
    }
    cd "$REPO_ROOT"
else
    echo "✅ Hummingbot 已存在"
fi

# Step 3: 克隆 LLM-TradeBot
echo ""
echo "🤖 Step 3: 克隆 LLM-TradeBot..."
if [ ! -d "$EXTERNAL_DIR/llm_tradebot" ]; then
    echo "📥 克隆 LLM-TradeBot..."
    cd "$EXTERNAL_DIR"
    git clone --depth 1 https://github.com/EthanAlgoX/LLM-TradeBot.git llm_tradebot 2>/dev/null || {
        echo "⚠️ LLM-TradeBot 克隆失败（可能是网络问题），继续..."
    }
    cd "$REPO_ROOT"
else
    echo "✅ LLM-TradeBot 已存在"
fi

# Step 4: 克隆 MarketBot (作为数据源)
echo ""
echo "📊 Step 4: 克隆 MarketBot..."
if [ ! -d "$EXTERNAL_DIR/marketbot" ]; then
    echo "📥 克隆 MarketBot..."
    cd "$EXTERNAL_DIR"
    git clone --depth 1 https://github.com/EthanAlgoX/MarketBot.git 2>/dev/null || {
        echo "⚠️ MarketBot 克隆失败（可能是网络问题），继续..."
    }
    cd "$REPO_ROOT"
else
    echo "✅ MarketBot 已存在"
fi

# Step 5: 显示项目结构
echo ""
echo "📋 Step 5: 检查项目结构..."
echo ""
echo "已克隆的仓库:"
ls -la "$EXTERNAL_DIR" | grep "^d" | awk '{print "  ├─ " $NF}'
echo ""

# Step 6: 创建初始化脚本
echo ""
echo "⚙️ Step 6: 生成初始化脚本..."

cat > "$REPO_ROOT/setup_strategy_benchmarking.py" << 'PYTHON_SCRIPT'
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
PYTHON_SCRIPT

chmod +x "$REPO_ROOT/setup_strategy_benchmarking.py"
echo "✅ 生成初始化脚本"

# Step 7: 运行初始化
echo ""
echo "🔧 Step 7: 运行初始化..."
cd "$REPO_ROOT"
python3 setup_strategy_benchmarking.py

# Step 8: 最后信息
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ 全部完成！"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📊 系统状态:"
echo "  • Cosmic 系统: ✅ 就绪 (src/core/)"
echo "  • Hummingbot: $([ -d "$EXTERNAL_DIR/hummingbot" ] && echo '✅ 已克隆' || echo '⏳ 待克隆')"
echo "  • LLM-TradeBot: $([ -d "$EXTERNAL_DIR/llm_tradebot" ] && echo '✅ 已克隆' || echo '⏳ 待克隆')"
echo "  • MarketBot: $([ -d "$EXTERNAL_DIR/marketbot" ] && echo '✅ 已克隆' || echo '⏳ 待克隆')"
echo ""
echo "🎯 立即开始:"
echo "  1. 查看完整方案:"
echo "     cat ETHANALGOX_STRATEGY_BENCHMARKING_PLAN.md | less"
echo ""
echo "  2. 开始开发统一策略接口:"
echo "     touch src/integrations/strategy_adapters/strategy_interface.py"
echo ""
echo "  3. 跟踪进度:"
echo "     更新 memory.md 和 task/task.md"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
