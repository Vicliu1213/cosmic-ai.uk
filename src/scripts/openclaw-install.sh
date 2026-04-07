#!/bin/bash
# OpenClaw 官方安装器 - 修复版本
# 使用完整路径以确保所有命令都可用

set -euo pipefail

# 定义完整路径
CURL="/usr/bin/curl"
MKTEMP="/bin/mktemp"
BASH="/bin/bash"
RM="/bin/rm"
CAT="/bin/cat"

# 颜色定义
BOLD='\033[1m'
ACCENT='\033[38;2;255;77;77m'
INFO='\033[38;2;136;146;176m'
SUCCESS='\033[38;2;0;229;204m'
WARN='\033[38;2;255;176;32m'
ERROR='\033[38;2;230;57;70m'
MUTED='\033[38;2;90;100;128m'
NC='\033[0m'

DEFAULT_TAGLINE="All your chats, one OpenClaw."

TMPFILES=()

cleanup_tmpfiles() {
    local f
    for f in "${TMPFILES[@]:-}"; do
        $RM -rf "$f" 2>/dev/null || true
    done
}
trap cleanup_tmpfiles EXIT

mktempfile() {
    local f
    f="$($MKTEMP)"
    TMPFILES+=("$f")
    echo "$f"
}

download_file() {
    local url="$1"
    local output="$2"
    
    $CURL -fsSL --proto '=https' --tlsv1.2 --retry 3 --retry-delay 1 --retry-connrefused -o "$output" "$url"
}

ui_info() {
    local msg="$*"
    echo -e "${MUTED}·${NC} ${msg}"
}

ui_warn() {
    local msg="$*"
    echo -e "${WARN}!${NC} ${msg}"
}

ui_success() {
    local msg="$*"
    echo -e "${SUCCESS}✓${NC} ${msg}"
}

ui_error() {
    local msg="$*"
    echo -e "${ERROR}✗${NC} ${msg}"
}

print_installer_banner() {
    echo -e "${ACCENT}${BOLD}"
    echo "  🦞 OpenClaw 安装器"
    echo -e "${NC}${INFO}  ${DEFAULT_TAGLINE}${NC}"
    echo ""
}

detect_os_or_die() {
    OS="unknown"
    if [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
    elif [[ "$OSTYPE" == "linux-gnu"* ]] || [[ -n "${WSL_DISTRO_NAME:-}" ]]; then
        OS="linux"
    fi

    if [[ "$OS" == "unknown" ]]; then
        ui_error "不支持的操作系统"
        echo "本安装器支持 macOS 和 Linux（包括 WSL）"
        exit 1
    fi

    ui_success "检测到: $OS"
}

main() {
    print_installer_banner
    
    # 检测OS
    detect_os_or_die
    
    # 验证curl可用
    if [[ ! -x "$CURL" ]]; then
        ui_error "curl 不可用"
        exit 1
    fi
    
    ui_success "curl 已找到: $CURL"
    
    # 下载官方安装器
    ui_info "下载官方 OpenClaw 安装器..."
    local installer_script
    installer_script="$(mktempfile)"
    
    if download_file "https://openclaw.ai/install.sh" "$installer_script"; then
        ui_success "下载完成"
        
        # 运行官方安装器
        ui_info "运行官方安装器..."
        $BASH "$installer_script" "$@"
    else
        ui_error "下载安装器失败"
        exit 1
    fi
}

main "$@"
