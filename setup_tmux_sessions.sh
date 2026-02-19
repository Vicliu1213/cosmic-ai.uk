#!/bin/bash

# Comic AI Tmux 多會話啟動管理腳本
# Multi-session tmux launcher for Comic AI
# 用途: 同時啟動多個服務（HTTPS 伺服器、Dashboard、任務面板等）

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SESSION_NAME="comic-ai"
LOG_DIR="$SCRIPT_DIR/logs/tmux"

# 建立日誌目錄
mkdir -p "$LOG_DIR"

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Comic AI 多會話 Tmux 啟動系統${NC}"
echo "=================================="
echo ""

# 檢查是否已有該會話
if tmux has-session -t "$SESSION_NAME" 2>/dev/null; then
    echo -e "${YELLOW}⚠️  會話 '$SESSION_NAME' 已存在${NC}"
    echo ""
    echo "選項:"
    echo "  1) 重新啟動 (kill 並重建)"
    echo "  2) 附加到現有會話"
    echo "  3) 取消"
    echo ""
    read -p "請選擇 [1-3]: " choice
    
    case $choice in
        1)
            echo -e "${YELLOW}殺死現有會話...${NC}"
            tmux kill-session -t "$SESSION_NAME"
            ;;
        2)
            echo -e "${GREEN}附加到現有會話...${NC}"
            tmux attach-session -t "$SESSION_NAME"
            exit 0
            ;;
        *)
            echo "已取消"
            exit 0
            ;;
    esac
fi

# 建立新會話
echo -e "${BLUE}建立 Tmux 會話: $SESSION_NAME${NC}"
tmux new-session -d -s "$SESSION_NAME" -x 240 -y 50

# ============================================
# 視窗 0: HTTPS 伺服器
# ============================================
echo -e "${BLUE}設置視窗 0: HTTPS 伺服器${NC}"
tmux rename-window -t "$SESSION_NAME" "https-server"
tmux send-keys -t "$SESSION_NAME:0" "cd $SCRIPT_DIR && bash start_https_server_bg.sh" Enter

# ============================================
# 視窗 1: Dashboard Web UI
# ============================================
echo -e "${BLUE}設置視窗 1: Dashboard Web UI${NC}"
tmux new-window -t "$SESSION_NAME" -n "dashboard"
tmux send-keys -t "$SESSION_NAME:1" "cd $SCRIPT_DIR && python dashboard/app_ssl.py 2>&1 | tee $LOG_DIR/dashboard.log" Enter

# ============================================
# 視窗 2: 任務面板
# ============================================
echo -e "${BLUE}設置視窗 2: 任務面板${NC}"
tmux new-window -t "$SESSION_NAME" -n "task-panel"
tmux send-keys -t "$SESSION_NAME:2" "cd $SCRIPT_DIR && python task_panel_optimized.py 2>&1 | tee $LOG_DIR/task_panel.log" Enter

# ============================================
# 視窗 3: 主 CLI
# ============================================
echo -e "${BLUE}設置視窗 3: 主 CLI${NC}"
tmux new-window -t "$SESSION_NAME" -n "main-cli"
tmux send-keys -t "$SESSION_NAME:3" "cd $SCRIPT_DIR && python src/cli/cli.py" Enter

# ============================================
# 視窗 4: 監控和日誌
# ============================================
echo -e "${BLUE}設置視窗 4: 監控和日誌${NC}"
tmux new-window -t "$SESSION_NAME" -n "monitor"
tmux send-keys -t "$SESSION_NAME:4" "cd $SCRIPT_DIR && watch -n 5 'echo \"=== Comic AI Tmux Sessions ===\"; tmux list-windows -t $SESSION_NAME; echo \"\"; echo \"=== 系統狀態 ===\"; ps aux | grep python | grep -v grep | wc -l; echo \" Python 進程運行中\"; echo \"\"; tail -20 $LOG_DIR/dashboard.log 2>/dev/null | head -10'" Enter

# ============================================
# 視窗 5: Shell (控制台)
# ============================================
echo -e "${BLUE}設置視窗 5: Shell 控制台${NC}"
tmux new-window -t "$SESSION_NAME" -n "shell"
tmux send-keys -t "$SESSION_NAME:5" "cd $SCRIPT_DIR && echo '歡迎來到 Comic AI Shell 控制台'; bash" Enter

# 選擇第一個視窗
tmux select-window -t "$SESSION_NAME:0"

echo ""
echo -e "${GREEN}✅ Tmux 會話已成功建立！${NC}"
echo ""
echo "會話名稱: $SESSION_NAME"
echo "日誌目錄: $LOG_DIR"
echo ""
echo -e "${YELLOW}會話視窗列表:${NC}"
echo "  0️⃣  https-server  - HTTPS 伺服器"
echo "  1️⃣  dashboard     - Dashboard Web UI"
echo "  2️⃣  task-panel    - 任務面板"
echo "  3️⃣  main-cli      - 主 CLI"
echo "  4️⃣  monitor       - 監控和日誌"
echo "  5️⃣  shell         - Shell 控制台"
echo ""
echo -e "${BLUE}快速命令:${NC}"
echo "  tmux attach-session -t $SESSION_NAME              # 附加到會話"
echo "  tmux select-window -t $SESSION_NAME:0             # 切換視窗"
echo "  tmux kill-session -t $SESSION_NAME                # 停止會話"
echo ""
echo -e "${GREEN}正在附加到會話...${NC}"
sleep 1

# 附加到會話
tmux attach-session -t "$SESSION_NAME"
