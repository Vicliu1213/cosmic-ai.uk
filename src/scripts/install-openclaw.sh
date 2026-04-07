#!/bin/bash
set -euo pipefail

# OpenClaw Installer for macOS and Linux
# Usage: curl -fsSL --proto '=https' --tlsv1.2 https://openclaw.ai/install.sh | bash
# Or locally: bash src/scripts/install-openclaw.sh

BOLD='\033[1m'
ACCENT='\033[38;2;255;77;77m'       # coral-bright  #ff4d4d
ACCENT_BRIGHT='\033[38;2;255;110;110m' # lighter coral
INFO='\033[38;2;136;146;176m'       # text-secondary #8892b0
SUCCESS='\033[38;2;0;229;204m'      # cyan-bright   #00e5cc
WARN='\033[38;2;255;176;32m'        # amber (no site equiv, keep warm)
ERROR='\033[38;2;230;57;70m'        # coral-mid     #e63946
MUTED='\033[38;2;90;100;128m'       # text-muted    #5a6480
NC='\033[0m' # No Color

DEFAULT_TAGLINE="All your chats, one OpenClaw."

ORIGINAL_PATH="${PATH:-}"

TMPFILES=()
cleanup_tmpfiles() {
    local f
    for f in "${TMPFILES[@]:-}"; do
        rm -rf "$f" 2>/dev/null || true
    done
}
trap cleanup_tmpfiles EXIT

mktempfile() {
    local f
    f="$(mktemp)"
    TMPFILES+=("$f")
    echo "$f"
}

resolve_brew_bin() {
    local brew_bin=""
    brew_bin="$(command -v brew 2>/dev/null || true)"
    if [[ -n "$brew_bin" ]]; then
        echo "$brew_bin"
        return 0
    fi
    if [[ -x "/opt/homebrew/bin/brew" ]]; then
        echo "/opt/homebrew/bin/brew"
        return 0
    fi
    if [[ -x "/usr/local/bin/brew" ]]; then
        echo "/usr/local/bin/brew"
        return 0
    fi
    return 1
}

activate_brew_for_session() {
    local brew_bin=""
    brew_bin="$(resolve_brew_bin || true)"
    if [[ -z "$brew_bin" ]]; then
        return 1
    fi
    if [[ -z "$(command -v brew 2>/dev/null || true)" && "${BREW_SHELLENV_ANNOUNCED:-0}" != "1" ]]; then
        ui_info "Found Homebrew at ${brew_bin}; exporting shellenv"
        BREW_SHELLENV_ANNOUNCED=1
    fi
    eval "$("$brew_bin" shellenv)"
    return 0
}

DOWNLOADER=""
detect_downloader() {
    if command -v curl &> /dev/null; then
        DOWNLOADER="curl"
        return 0
    fi
    if command -v wget &> /dev/null; then
        DOWNLOADER="wget"
        return 0
    fi
    ui_error "Missing downloader (curl or wget required)"
    exit 1
}

download_file() {
    local url="$1"
    local output="$2"
    if [[ -z "$DOWNLOADER" ]]; then
        detect_downloader
    fi
    if [[ "$DOWNLOADER" == "curl" ]]; then
        curl -fsSL --proto '=https' --tlsv1.2 --retry 3 --retry-delay 1 --retry-connrefused -o "$output" "$url"
        return
    fi
    wget -q --https-only --secure-protocol=TLSv1_2 --tries=3 --timeout=20 -O "$output" "$url"
}

run_remote_bash() {
    local url="$1"
    local tmp
    tmp="$(mktempfile)"
    download_file "$url" "$tmp"
    /bin/bash "$tmp"
}

GUM_VERSION="${OPENCLAW_GUM_VERSION:-0.17.0}"
GUM=""
GUM_STATUS="skipped"
GUM_REASON=""

is_non_interactive_shell() {
    if [[ "${NO_PROMPT:-0}" == "1" ]]; then
        return 0
    fi
    if [[ ! -t 0 || ! -t 1 ]]; then
        return 0
    fi
    return 1
}

gum_is_tty() {
    if [[ -n "${NO_COLOR:-}" ]]; then
        return 1
    fi
    if [[ "${TERM:-dumb}" == "dumb" ]]; then
        return 1
    fi
    if [[ -t 2 || -t 1 ]]; then
        return 0
    fi
    if [[ -r /dev/tty && -w /dev/tty ]]; then
        return 0
    fi
    return 1
}

gum_detect_os() {
    case "$(uname -s 2>/dev/null || true)" in
        Darwin) echo "Darwin" ;;
        Linux) echo "Linux" ;;
        *) echo "unsupported" ;;
    esac
}

gum_detect_arch() {
    case "$(uname -m 2>/dev/null || true)" in
        x86_64|amd64) echo "x86_64" ;;
        arm64|aarch64) echo "arm64" ;;
        i386|i686) echo "i386" ;;
        armv7l|armv7) echo "armv7" ;;
        armv6l|armv6) echo "armv6" ;;
        *) echo "unknown" ;;
    esac
}

verify_sha256sum_file() {
    local checksums="$1"
    if command -v sha256sum >/dev/null 2>&1; then
        sha256sum --ignore-missing -c "$checksums" >/dev/null 2>&1
        return $?
    fi
    if command -v shasum >/dev/null 2>&1; then
        shasum -a 256 --ignore-missing -c "$checksums" >/dev/null 2>&1
        return $?
    fi
    return 1
}

bootstrap_gum_temp() {
    GUM=""
    GUM_STATUS="skipped"
    GUM_REASON=""

    if is_non_interactive_shell; then
        GUM_REASON="non-interactive shell (auto-disabled)"
        return 1
    fi

    if ! gum_is_tty; then
        GUM_REASON="terminal does not support gum UI"
        return 1
    fi

    if command -v gum >/dev/null 2>&1; then
        GUM="gum"
        GUM_STATUS="found"
        GUM_REASON="already installed"
        return 0
    fi

    if ! command -v tar >/dev/null 2>&1; then
        GUM_REASON="tar not found"
        return 1
    fi

    local os arch asset base gum_tmpdir gum_path
    os="$(gum_detect_os)"
    arch="$(gum_detect_arch)"
    if [[ "$os" == "unsupported" || "$arch" == "unknown" ]]; then
        GUM_REASON="unsupported os/arch ($os/$arch)"
        return 1
    fi

    asset="gum_${GUM_VERSION}_${os}_${arch}.tar.gz"
    base="https://github.com/charmbracelet/gum/releases/download/v${GUM_VERSION}"

    gum_tmpdir="$(mktemp -d)"
    TMPFILES+=("$gum_tmpdir")

    if ! download_file "${base}/${asset}" "$gum_tmpdir/$asset"; then
        GUM_REASON="download failed"
        return 1
    fi

    if ! download_file "${base}/checksums.txt" "$gum_tmpdir/checksums.txt"; then
        GUM_REASON="checksum unavailable or failed"
        return 1
    fi

    if ! (cd "$gum_tmpdir" && verify_sha256sum_file "checksums.txt"); then
        GUM_REASON="checksum unavailable or failed"
        return 1
    fi

    if ! tar -xzf "$gum_tmpdir/$asset" -C "$gum_tmpdir" >/dev/null 2>&1; then
        GUM_REASON="extract failed"
        return 1
    fi

    gum_path="$(find "$gum_tmpdir" -type f -name gum 2>/dev/null | sort | tail -n1 || true)"
    if [[ -z "$gum_path" ]]; then
        GUM_REASON="gum binary missing after extract"
        return 1
    fi

    chmod +x "$gum_path" >/dev/null 2>&1 || true
    if [[ ! -x "$gum_path" ]]; then
        GUM_REASON="gum binary is not executable"
        return 1
    fi

    GUM="$gum_path"
    GUM_STATUS="installed"
    GUM_REASON="temp, verified"
    return 0
}

ui_info() {
    local msg="$*"
    if [[ -n "$GUM" ]]; then
        "$GUM" log --level info "$msg"
    else
        echo -e "${MUTED}·${NC} ${msg}"
    fi
}

ui_warn() {
    local msg="$*"
    if [[ -n "$GUM" ]]; then
        "$GUM" log --level warn "$msg"
    else
        echo -e "${WARN}!${NC} ${msg}"
    fi
}

ui_success() {
    local msg="$*"
    if [[ -n "$GUM" ]]; then
        local mark
        mark="$("$GUM" style --foreground "#00e5cc" --bold "✓")"
        echo "${mark} ${msg}"
    else
        echo -e "${SUCCESS}✓${NC} ${msg}"
    fi
}

ui_error() {
    local msg="$*"
    if [[ -n "$GUM" ]]; then
        "$GUM" log --level error "$msg"
    else
        echo -e "${ERROR}✗${NC} ${msg}"
    fi
}

print_installer_banner() {
    if [[ -n "$GUM" ]]; then
        local title tagline hint card
        title="$("$GUM" style --foreground "#ff4d4d" --bold "🦞 OpenClaw Installer")"
        tagline="$("$GUM" style --foreground "#8892b0" "$DEFAULT_TAGLINE")"
        hint="$("$GUM" style --foreground "#5a6480" "modern installer mode")"
        card="$(printf '%s\n%s\n%s' "$title" "$tagline" "$hint")"
        "$GUM" style --border rounded --border-foreground "#ff4d4d" --padding "1 2" "$card"
        echo ""
        return
    fi

    echo -e "${ACCENT}${BOLD}"
    echo "  🦞 OpenClaw Installer"
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
        ui_error "Unsupported operating system"
        echo "This installer supports macOS and Linux (including WSL)."
        exit 1
    fi

    ui_success "Detected: $OS"
}

check_node() {
    if command -v node &> /dev/null; then
        local node_version
        node_version="$(node -v 2>/dev/null || echo 'unknown')"
        ui_success "Node.js $node_version found"
        return 0
    else
        ui_info "Node.js not found, installing it now"
        return 1
    fi
}

check_git() {
    if command -v git &> /dev/null; then
        ui_success "Git already installed"
        return 0
    fi
    ui_info "Git not found, installing it now"
    return 1
}

is_root() {
    [[ "$(id -u)" -eq 0 ]]
}

install_node() {
    if [[ "$OS" == "macos" ]]; then
        ui_info "Installing Node.js via Homebrew"
        if ! command -v brew &> /dev/null; then
            ui_info "Installing Homebrew first..."
            /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        fi
        brew install node@22
        ui_success "Node.js installed"
    elif [[ "$OS" == "linux" ]]; then
        ui_info "Installing Node.js via apt/dnf/yum"
        if command -v apt-get &> /dev/null; then
            if is_root; then
                apt-get update && apt-get install -y nodejs
            else
                sudo apt-get update && sudo apt-get install -y nodejs
            fi
        elif command -v dnf &> /dev/null; then
            if is_root; then
                dnf install -y nodejs
            else
                sudo dnf install -y nodejs
            fi
        elif command -v yum &> /dev/null; then
            if is_root; then
                yum install -y nodejs
            else
                sudo yum install -y nodejs
            fi
        fi
        ui_success "Node.js installed"
    fi
}

main() {
    print_installer_banner
    
    # Bootstrap gum if available
    bootstrap_gum_temp || true
    
    # Detect OS
    detect_os_or_die
    
    # Check Node.js
    if ! check_node; then
        install_node
    fi
    
    # Check Git
    if ! check_git; then
        ui_warn "Git not found - some features may be unavailable"
    fi
    
    # Install OpenClaw via npm
    ui_info "Installing OpenClaw via npm..."
    if command -v npm &> /dev/null; then
        npm install -g openclaw
        ui_success "OpenClaw installed successfully!"
        
        # Show next steps
        echo ""
        ui_info "Next steps:"
        echo "  1. Run: openclaw"
        echo "  2. Configure your settings"
        echo "  3. Start chatting!"
        echo ""
    else
        ui_error "npm not found - cannot install OpenClaw"
        exit 1
    fi
}

# Run main
main "$@"
