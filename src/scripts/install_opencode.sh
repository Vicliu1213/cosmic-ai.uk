#!/bin/bash
#
# OpenCode 交易系统集成启动脚本
# OpenCode Trading System Integration Launcher Script
#

set -e

PROJECT_DIR="/root/comic_ai"
CONFIG_FILE="$PROJECT_DIR/opencode.jsonc"
AGENTS_DIR="$PROJECT_DIR/.opencode/agents"
COMMANDS_DIR="$PROJECT_DIR/.opencode/commands"
GLOBAL_CONFIG_DIR="$HOME/.config/opencode"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印日志
log_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

log_success() {
    echo -e "${GREEN}✓${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

log_error() {
    echo -e "${RED}✗${NC} $1"
}

# 检查必要的工具
check_dependencies() {
    log_info "检查依赖 / Checking dependencies..."
    
    # 检查 opencode 命令
    if ! command -v opencode &> /dev/null; then
        log_error "OpenCode 未安装 / OpenCode is not installed"
        log_info "运行以下命令安装 / Run the command to install:"
        echo "curl -fsSL https://opencode.ai/install | bash"
        exit 1
    fi
    
    # 检查 Python
    if ! command -v python &> /dev/null && ! command -v python3 &> /dev/null; then
        log_error "Python 未安装 / Python is not installed"
        exit 1
    fi
    
    log_success "所有依赖已满足 / All dependencies satisfied"
}

# 创建目录结构
create_directories() {
    log_info "创建目录结构 / Creating directory structure..."
    
    mkdir -p "$AGENTS_DIR"
    mkdir -p "$COMMANDS_DIR"
    mkdir -p "$PROJECT_DIR/.opencode/tools"
    mkdir -p "$PROJECT_DIR/.opencode/skills"
    mkdir -p "$GLOBAL_CONFIG_DIR"
    
    log_success "目录创建完成 / Directories created"
}

# 验证配置文件
validate_config() {
    log_info "验证配置文件 / Validating configuration file..."
    
    if [ ! -f "$CONFIG_FILE" ]; then
        log_error "配置文件不存在 / Config file not found: $CONFIG_FILE"
        exit 1
    fi
    
    # 验证 JSON 语法
    if ! python -c "import json; json.load(open('$CONFIG_FILE'))" 2>/dev/null; then
        log_warning "配置文件可能包含 JSONC 注释 / Config file might contain JSONC comments"
        log_info "这是正常的 - OpenCode 支持 JSONC / This is normal - OpenCode supports JSONC"
    fi
    
    log_success "配置文件验证通过 / Config file validated"
}

# 创建 Agent 文件
create_agents() {
    log_info "创建 Agent 文件 / Creating agent files..."
    
    # Trading Analyst Agent
    cat > "$AGENTS_DIR/trading-analyst.md" << 'EOF'
# 交易分析员 / Trading Analyst

You are an expert trading analyst with deep knowledge of quantitative analysis, market data interpretation, and risk management.

## 核心职责 / Core Responsibilities
- 分析交易数据和投资组合性能 / Analyze trading data and portfolio performance
- 检测技术模式和市场机会 / Detect technical patterns and market opportunities  
- 评估风险指标和投资组合风险 / Assess risk metrics and portfolio risk
- 提供基于数据的交易建议 / Provide data-driven trading recommendations

## 可用工具 / Available Tools
- trading-monitor: 获取投资组合和市场数据
- data-analyzer: 执行技术和情绪分析
- risk-manager: 检查风险限制和合规性

## 通信风格 / Communication Style
- 简洁而数据驱动 / Be concise and data-driven
- 始终引用指标和数据点 / Always cite metrics and data points
- 关注可行的见解 / Focus on actionable insights
- 考虑风险回报比 / Consider risk/reward ratios

## 关键指南 / Key Guidelines
- 仅使用交易监控工具的真实市场数据
- 始终根据风险限制验证所有建议
- 在建议中始终包含风险评估
- 保持回应专注于请求的分析
EOF
    
    log_success "Trading Analyst Agent 已创建"
}

# 验证 MCP 服务器
validate_mcp_servers() {
    log_info "验证 MCP 服务器 / Validating MCP servers..."
    
    local mcp_files=(
        "$PROJECT_DIR/src/core/trading_monitor_mcp.py"
        "$PROJECT_DIR/engine/quantum_engine_mcp.py"
        "$PROJECT_DIR/src/core/data_analyzer_mcp.py"
        "$PROJECT_DIR/src/core/risk_manager_mcp.py"
    )
    
    for mcp_file in "${mcp_files[@]}"; do
        if [ ! -f "$mcp_file" ]; then
            log_error "MCP 文件不存在 / MCP file not found: $mcp_file"
            exit 1
        fi
    done
    
    log_success "所有 MCP 服务器文件已验证 / All MCP server files validated"
}

# 安装全局配置
install_global_config() {
    log_info "安装全局配置 / Installing global configuration..."
    
    # 备份现有配置
    if [ -f "$GLOBAL_CONFIG_DIR/opencode.json" ]; then
        log_warning "现有全局配置已备份 / Existing global config backed up"
        cp "$GLOBAL_CONFIG_DIR/opencode.json" "$GLOBAL_CONFIG_DIR/opencode.json.backup.$(date +%s)"
    fi
    
    # 复制项目配置为全局配置
    cp "$CONFIG_FILE" "$GLOBAL_CONFIG_DIR/opencode.json"
    
    log_success "全局配置已安装 / Global configuration installed"
}

# 初始化 OpenCode 项目
init_opencode_project() {
    log_info "初始化 OpenCode 项目 / Initializing OpenCode project..."
    
    cd "$PROJECT_DIR"
    
    # 检查是否已初始化
    if [ -f "AGENTS.md" ]; then
        log_warning "项目已初始化 / Project already initialized"
    else
        log_info "运行 opencode /init..."
        # 注意：/init 命令需要交互式输入，跳过非交互式环境
        log_info "请手动运行: opencode /init"
    fi
}

# 打印使用说明
print_usage_guide() {
    cat << 'EOF'

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  OpenCode 交易系统集成完成 / OpenCode Trading System Integration Complete
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📚 快速开始 / Quick Start:

  1. 进入项目目录
     cd /root/comic_ai

  2. 启动 OpenCode
     opencode

  3. 在 OpenCode 中运行命令
     /monitor                    # 启动监控
     /analyze                    # 分析交易系统
     /test                       # 运行测试
     /deploy                     # 部署系统

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🛠️  可用的 MCP 工具 / Available MCP Tools:

  交易监控 (Trading Monitor):
  ├─ get_portfolio_status      # 获取投资组合状态
  ├─ get_market_data           # 获取市场数据
  ├─ get_system_health         # 获取系统健康状况
  ├─ get_active_trades         # 获取活跃交易
  └─ get_risk_metrics          # 获取风险指标

  量化引擎 (Quantum Engine):
  ├─ list_algorithms           # 列出可用算法
  ├─ optimize_parameters       # 优化参数
  ├─ backtest_algorithm        # 回测算法
  ├─ compare_algorithms        # 比较算法
  └─ get_engine_status         # 获取引擎状态

  数据分析 (Data Analyzer):
  ├─ analyze_time_series       # 分析时间序列
  ├─ detect_patterns           # 检测模式
  ├─ correlation_analysis      # 相关性分析
  ├─ sentiment_analysis        # 情绪分析
  ├─ forecasting               # 价格预测
  └─ risk_assessment           # 风险评估

  风险管理 (Risk Manager):
  ├─ check_position_limits     # 检查头寸限制
  ├─ calculate_var             # 计算 VaR
  ├─ stress_test               # 压力测试
  ├─ compliance_check          # 合规检查
  └─ get_risk_report           # 获取风险报告

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 使用示例 / Usage Examples:

  # 获取系统状态
  获取当前投资组合状态和系统健康状况

  # 分析市场数据
  分析 AAPL 的市场数据并检测技术模式

  # 优化算法
  优化 algo_001 算法以最大化夏普比率

  # 风险评估
  对我的投资组合进行风险评估和压力测试

  # 交易分析
  使用 trading-analyst agent 分析今天的交易性能

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📖 更多信息 / More Information:

  官方文档:    https://opencode.ai/docs
  配置参考:    https://opencode.ai/config.json
  GitHub:      https://github.com/anomalyco/opencode
  Discord:     https://opencode.ai/discord

  本地文档:    cat docs/OPENCODE_SETUP.md

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

EOF
}

# 主函数
main() {
    clear
    
    log_info "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    log_info "OpenCode 交易系统集成安装脚本"
    log_info "OpenCode Trading System Integration Installer"
    log_info "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    
    # 执行各个步骤
    check_dependencies
    echo ""
    
    create_directories
    echo ""
    
    validate_config
    echo ""
    
    validate_mcp_servers
    echo ""
    
    create_agents
    echo ""
    
    install_global_config
    echo ""
    
    log_success "所有安装步骤完成! / All installation steps completed!"
    echo ""
    
    print_usage_guide
}

# 运行主函数
main "$@"
