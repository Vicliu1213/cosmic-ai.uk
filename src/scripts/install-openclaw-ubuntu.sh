#!/bin/bash
# OpenClaw 安装脚本 - Ubuntu 移动版优化
# 针对 Ubuntu Touch/Ubuntu 移动设备优化

set -euo pipefail

# 颜色定义
SUCCESS='\033[0;32m'
ERROR='\033[0;31m'
WARN='\033[0;33m'
INFO='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# 系统信息
OS=$(uname -s)
ARCH=$(uname -m)

print_header() {
    echo -e "${BOLD}${INFO}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "   🦞 OpenClaw 安装器 - Ubuntu 移动版"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo -e "${NC}"
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

detect_system() {
    echo ""
    info "检测系统信息..."
    info "操作系统: $OS"
    info "架构: $ARCH"
    
    # 检查是否是 Ubuntu
    if [[ -f /etc/os-release ]]; then
        . /etc/os-release
        info "发行版: $PRETTY_NAME"
        info "版本 ID: $VERSION_ID"
    fi
    echo ""
}

check_dependencies() {
    echo "检查依赖..."
    local missing_deps=0
    
    # 检查 curl
    if command -v curl &> /dev/null; then
        success "curl 已安装"
    else
        error "curl 未安装"
        missing_deps=1
    fi
    
    # 检查 wget
    if command -v wget &> /dev/null; then
        success "wget 已安装"
    else
        warn "wget 未安装（可选）"
    fi
    
    # 检查 git
    if command -v git &> /dev/null; then
        success "git 已安装"
    else
        warn "git 未安装（可选）"
    fi
    
    # 检查 Node.js
    if command -v node &> /dev/null; then
        local node_version
        node_version=$(node -v)
        success "Node.js 已安装: $node_version"
    else
        error "Node.js 未安装"
        missing_deps=1
    fi
    
    # 检查 npm
    if command -v npm &> /dev/null; then
        local npm_version
        npm_version=$(npm -v)
        success "npm 已安装: $npm_version"
    else
        error "npm 未安装"
        missing_deps=1
    fi
    
    echo ""
    return $missing_deps
}

install_curl() {
    warn "正在安装 curl..."
    if command -v apt-get &> /dev/null; then
        sudo apt-get update
        sudo apt-get install -y curl
        success "curl 安装完成"
    fi
}

install_node() {
    warn "正在安装 Node.js..."
    if command -v apt-get &> /dev/null; then
        # 添加 NodeSource 仓库
        curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
        sudo apt-get install -y nodejs
        success "Node.js 安装完成"
    else
        error "无法检测包管理器"
        return 1
    fi
}

install_openclaw() {
    echo ""
    info "通过 npm 安装 OpenClaw..."
    
    if ! command -v npm &> /dev/null; then
        error "npm 未找到，无法继续安装"
        return 1
    fi
    
    # 安装 OpenClaw
    npm install -g openclaw
    
    if command -v openclaw &> /dev/null; then
        success "OpenClaw 安装成功！"
        
        local openclaw_version
        openclaw_version=$(openclaw --version 2>/dev/null || echo "已安装")
        info "OpenClaw 版本: $openclaw_version"
        return 0
    else
        error "OpenClaw 安装失败"
        return 1
    fi
}

verify_installation() {
    echo ""
    info "验证安装..."
    
    if command -v openclaw &> /dev/null; then
        success "OpenClaw 命令可用"
        
        # 尝试显示帮助信息
        if openclaw --help > /dev/null 2>&1; then
            success "OpenClaw 命令响应正常"
            return 0
        else
            warn "OpenClaw 命令可用但响应异常"
        fi
    else
        error "OpenClaw 命令不可用"
        return 1
    fi
}

show_next_steps() {
    echo ""
    echo -e "${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    success "安装完成！"
    echo -e "${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    info "下一步:"
    echo "  1. 运行 OpenClaw:"
    echo "     openclaw"
    echo ""
    echo "  2. 查看帮助:"
    echo "     openclaw --help"
    echo ""
    echo "  3. 查看版本:"
    echo "     openclaw --version"
    echo ""
    echo "  4. 访问官方网站:"
    echo "     https://openclaw.ai"
    echo ""
}

main() {
    print_header
    
    # 检测系统
    detect_system
    
    # 检查依赖
    if ! check_dependencies; then
        echo ""
        warn "缺少某些必需依赖，正在尝试安装..."
        
        if ! command -v curl &> /dev/null; then
            install_curl
        fi
        
        if ! command -v node &> /dev/null; then
            install_node
        fi
        
        if ! command -v npm &> /dev/null; then
            error "npm 仍未安装，无法继续"
            return 1
        fi
    fi
    
    # 安装 OpenClaw
    if install_openclaw; then
        # 验证安装
        if verify_installation; then
            # 显示下一步
            show_next_steps
            success "所有步骤完成！"
            return 0
        fi
    fi
    
    error "安装过程中出错"
    return 1
}

# 运行主程序
main "$@"
