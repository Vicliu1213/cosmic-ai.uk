#!/bin/bash
# OpenClaw 安装 - 完整工作版本
# 这个脚本已验证可在 Ubuntu 上工作

set -euo pipefail

# 使用完整路径确保兼容性
CURL="/usr/bin/curl"
BASH="/bin/bash"

# 颜色定义
SUCCESS='\033[0;32m'
ERROR='\033[0;31m'
WARN='\033[0;33m'
INFO='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

print_header() {
    echo -e "${BOLD}${INFO}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "   🦞 OpenClaw 安装器 - 完整版本"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo -e "${NC}"
}

info() {
    echo -e "${INFO}ℹ${NC} $*"
}

success() {
    echo -e "${SUCCESS}✓${NC} $*"
}

warn() {
    echo -e "${WARN}!${NC} $*"
}

error() {
    echo -e "${ERROR}✗${NC} $*"
}

verify_dependencies() {
    echo "验证依赖..."
    
    # 检查 curl
    if [[ -x "$CURL" ]]; then
        success "curl 已找到"
    else
        error "curl 未找到"
        return 1
    fi
    
    # 检查 bash
    if [[ -x "$BASH" ]]; then
        success "bash 已找到"
    else
        error "bash 未找到"
        return 1
    fi
    
    echo ""
    return 0
}

install_openclaw() {
    echo "安装 OpenClaw..."
    echo ""
    
    # 使用 curl 和 bash 运行官方安装器
    $CURL -fsSL https://openclaw.ai/install.sh | $BASH -s -- "$@"
    
    if [[ $? -eq 0 ]]; then
        success "OpenClaw 安装成功"
        return 0
    else
        warn "OpenClaw 安装过程出现问题"
        return 1
    fi
}

show_next_steps() {
    echo ""
    echo -e "${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    success "安装完成！"
    echo -e "${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    info "下一步："
    echo "  1. 运行 OpenClaw:"
    echo "     openclaw"
    echo ""
    echo "  2. 查看帮助:"
    echo "     openclaw --help"
    echo ""
    echo "  3. 访问官方网站:"
    echo "     https://openclaw.ai"
    echo ""
}

main() {
    print_header
    
    # 验证依赖
    if ! verify_dependencies; then
        error "依赖验证失败"
        return 1
    fi
    
    # 安装 OpenClaw
    if install_openclaw "$@"; then
        show_next_steps
        success "所有步骤完成！"
        return 0
    else
        error "安装失败"
        return 1
    fi
}

# 运行主程序
main "$@"
