#!/bin/bash

###############################################################################
# Cosmic AI - Hierarchical Dashboard Launcher
# 啟動分層儀表版系統 - 帶有4級進度系統
#
# 功能特徵:
# - 🟢 初級 (Novice): 3 個基本功能
# - 🟡 中級 (Intermediate): 5 個功能 (解鎖索引、組件)
# - 🔵 高級 (Advanced): 7 個功能 (解鎖健康檢查、進階控制)
# - 🔴 專家 (Expert): 11 個功能 (解鎖量子分析、深層診斷、原始數據)
#
# 級別進度:
# - 初級→中級: 5 個操作後
# - 中級→高級: 12 個操作後
# - 高級→專家: 25 個操作後
###############################################################################

set -e

# 確定指令碼目錄
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 打印歡迎消息
print_header() {
    clear
    echo -e "${CYAN}"
    echo "╔════════════════════════════════════════════════════════════════╗"
    echo "║                                                                ║"
    echo "║     🚀 Cosmic AI 分層儀表版系統 (Hierarchical Dashboard)     ║"
    echo "║                                                                ║"
    echo "║     🟢 初級 | 🟡 中級 | 🔵 高級 | 🔴 專家                  ║"
    echo "║                                                                ║"
    echo "╚════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    echo ""
}

# 檢查 Python
check_python() {
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}❌ 錯誤: 找不到 Python 3${NC}"
        echo "請先安裝 Python 3.8 或更高版本"
        exit 1
    fi
    
    PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
    echo -e "${GREEN}✅ Python 版本: $PYTHON_VERSION${NC}"
}

# 檢查必要的文件
check_dependencies() {
    if [ ! -f "$SCRIPT_DIR/hierarchical_dashboard.py" ]; then
        echo -e "${RED}❌ 錯誤: 找不到 hierarchical_dashboard.py${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ 所有依賴文件已找到${NC}"
}

# 顯示級別信息
show_level_info() {
    echo -e "${YELLOW}📊 級別進度系統:${NC}"
    echo ""
    echo -e "${GREEN}🟢 初級 (Novice)${NC}"
    echo "   • 功能數量: 3 個"
    echo "   • 升級要求: 完成 5 個操作"
    echo "   • 解鎖內容: 無"
    echo ""
    
    echo -e "${YELLOW}🟡 中級 (Intermediate)${NC}"
    echo "   • 功能數量: 5 個"
    echo "   • 升級要求: 完成 12 個總操作"
    echo "   • 解鎖內容: 🗂️ 索引, 🔍 組件狀態"
    echo ""
    
    echo -e "${CYAN}🔵 高級 (Advanced)${NC}"
    echo "   • 功能數量: 7 個"
    echo "   • 升級要求: 完成 25 個總操作"
    echo "   • 解鎖內容: 🏥 健康檢查, ⚙️ 進階控制"
    echo ""
    
    echo -e "${RED}🔴 專家 (Expert)${NC}"
    echo "   • 功能數量: 11 個"
    echo "   • 升級要求: 完成 50 個總操作"
    echo "   • 解鎖內容: 🌌 量子分析, 🔬 深層診斷, 📡 原始數據"
    echo ""
}

# 主函數
main() {
    print_header
    
    echo -e "${BLUE}🔍 檢查系統環境...${NC}"
    echo ""
    
    check_python
    check_dependencies
    
    echo ""
    show_level_info
    
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo -e "${GREEN}✅ 所有檢查完成！正在啟動儀表版...${NC}"
    echo ""
    
    sleep 2
    
    # 啟動儀表版
    cd "$PROJECT_ROOT"
    python3 "$SCRIPT_DIR/hierarchical_dashboard.py"
}

# 運行主函數
main "$@"
