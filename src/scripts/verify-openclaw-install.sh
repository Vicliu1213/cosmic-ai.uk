#!/bin/bash
# OpenClaw 安装验证脚本
# 验证 OpenClaw 是否已正确安装并可用

set -euo pipefail

# 颜色定义
SUCCESS='\033[0;32m'
ERROR='\033[0;31m'
WARN='\033[0;33m'
INFO='\033[0;36m'
NC='\033[0m' # No Color

# 计数器
CHECKS_PASSED=0
CHECKS_FAILED=0

check() {
    local name="$1"
    local command="$2"
    
    if eval "$command" > /dev/null 2>&1; then
        echo -e "${SUCCESS}✓${NC} $name"
        ((CHECKS_PASSED++))
        return 0
    else
        echo -e "${ERROR}✗${NC} $name"
        ((CHECKS_FAILED++))
        return 1
    fi
}

info() {
    echo -e "${INFO}ℹ${NC} $*"
}

warn() {
    echo -e "${WARN}!${NC} $*"
}

error() {
    echo -e "${ERROR}✗${NC} $*"
}

success() {
    echo -e "${SUCCESS}✓${NC} $*"
}

main() {
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "   OpenClaw 安装验证"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""

    # 检查系统信息
    echo "系统信息："
    echo "  操作系统: $(uname -s)"
    echo "  架构: $(uname -m)"
    echo ""

    # 检查依赖
    echo "检查依赖..."
    check "Node.js 已安装" "command -v node"
    check "npm 已安装" "command -v npm"
    check "Git 已安装" "command -v git"
    echo ""

    # 检查版本
    echo "检查版本..."
    if command -v node &> /dev/null; then
        local node_version
        node_version=$(node -v)
        info "Node.js 版本: $node_version"
    fi

    if command -v npm &> /dev/null; then
        local npm_version
        npm_version=$(npm -v)
        info "npm 版本: $npm_version"
    fi
    echo ""

    # 检查 OpenClaw 安装
    echo "检查 OpenClaw..."
    if check "OpenClaw 已安装" "command -v openclaw"; then
        local openclaw_version
        openclaw_version=$(openclaw --version 2>/dev/null || echo "未知")
        info "OpenClaw 版本: $openclaw_version"
    else
        warn "OpenClaw 未找到。运行以下命令进行安装:"
        echo "  bash src/scripts/install-openclaw.sh"
    fi
    echo ""

    # npm 全局包
    echo "npm 全局包:"
    if command -v npm &> /dev/null; then
        local npm_global
        npm_global=$(npm list -g --depth=0 2>/dev/null | grep openclaw || true)
        if [[ -n "$npm_global" ]]; then
            info "$npm_global"
        else
            warn "openclaw 未在全局 npm 包中找到"
        fi
    fi
    echo ""

    # 总结
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    if [[ $CHECKS_FAILED -eq 0 ]]; then
        success "所有检查通过！OpenClaw 已正确安装。"
        echo ""
        info "下一步："
        echo "  1. 运行: openclaw"
        echo "  2. 配置您的设置"
        echo "  3. 开始使用！"
    else
        error "有 $CHECKS_FAILED 个检查失败"
        echo ""
        warn "请解决上述问题，然后重试。"
    fi
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""

    if [[ $CHECKS_FAILED -eq 0 ]]; then
        return 0
    else
        return 1
    fi
}

main "$@"
