#!/bin/bash

# Comic AI - TMUX Applications Setup
# 啟動所有 7 個應用程序到不同的 TMUX 會話

set -e

SESSION="comic-ai-apps"
PROJECT_DIR="/root/comic_ai"
LOG_DIR="$PROJECT_DIR/logs/tmux"

# 確保日誌目錄存在
mkdir -p "$LOG_DIR"

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  Comic AI - TMUX Applications Setup                        ║${NC}"
echo -e "${BLUE}║  啟動 7 個應用程序                                          ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# 如果會話已存在,刪除它
if tmux has-session -t "$SESSION" 2>/dev/null; then
    echo -e "${YELLOW}⚠️  會話 '$SESSION' 已存在,刪除中...${NC}"
    tmux kill-session -t "$SESSION"
    sleep 1
fi

# 激活虛擬環境
cd "$PROJECT_DIR"
source venv/bin/activate

echo -e "${GREEN}✅ 虛擬環境已激活${NC}"
echo ""

# 創建新會話
echo -e "${CYAN}創建 TMUX 會話: $SESSION${NC}"
tmux new-session -d -s "$SESSION" -x 250 -y 50

# 窗口 0: File Processor
echo -e "${CYAN}[1/7] 啟動 File Processor...${NC}"
tmux send-keys -t "$SESSION" "cd '$PROJECT_DIR' && source venv/bin/activate && python intelligent_file_processor_cli.py" Enter
tmux rename-window -t "$SESSION:0" "FileProcessor"
sleep 1

# 窗口 1: Logging Dashboard (端口 5000)
echo -e "${CYAN}[2/7] 啟動 Logging Dashboard (port 5000)...${NC}"
tmux new-window -t "$SESSION" -n "LoggingDash"
tmux send-keys -t "$SESSION:LoggingDash" "cd '$PROJECT_DIR' && source venv/bin/activate && python logging_dashboard.py 2>&1 | tee $LOG_DIR/logging_dashboard.log" Enter
sleep 1

# 窗口 2: Task Panel (端口 5001)
echo -e "${CYAN}[3/7] 啟動 Task Panel (port 5001)...${NC}"
tmux new-window -t "$SESSION" -n "TaskPanel"
tmux send-keys -t "$SESSION:TaskPanel" "cd '$PROJECT_DIR' && source venv/bin/activate && python task_panel_optimized.py 2>&1 | tee $LOG_DIR/task_panel.log" Enter
sleep 1

# 窗口 3: Cloud Dashboard (端口 5002)
echo -e "${CYAN}[4/7] 啟動 Hybrid Cloud Dashboard (port 5002)...${NC}"
tmux new-window -t "$SESSION" -n "CloudDash"
tmux send-keys -t "$SESSION:CloudDash" "cd '$PROJECT_DIR' && source venv/bin/activate && python hybrid_cloud_dashboard.py 2>&1 | tee $LOG_DIR/cloud_dashboard.log" Enter
sleep 1

# 窗口 4: Singularity Demo
echo -e "${CYAN}[5/7] 啟動 Singularity Multi-Agent Demo...${NC}"
tmux new-window -t "$SESSION" -n "Singularity"
tmux send-keys -t "$SESSION:Singularity" "cd '$PROJECT_DIR' && source venv/bin/activate && python demo_singularity_system.py 2>&1 | tee $LOG_DIR/singularity.log" Enter
sleep 1

# 窗口 5: Gemini Trading Analyst
echo -e "${CYAN}[6/7] 啟動 Gemini Trading Analyst Demo...${NC}"
tmux new-window -t "$SESSION" -n "GeminiAnalyst"
tmux send-keys -t "$SESSION:GeminiAnalyst" "cd '$PROJECT_DIR' && source venv/bin/activate && python demo_gemini_trading_analyst.py 2>&1 | tee $LOG_DIR/gemini_analyst.log" Enter
sleep 1

# 窗口 6: Main CLI
echo -e "${CYAN}[7/7] 啟動 Main CLI...${NC}"
tmux new-window -t "$SESSION" -n "MainCLI"
tmux send-keys -t "$SESSION:MainCLI" "cd '$PROJECT_DIR' && source venv/bin/activate && python src/cli/cli.py" Enter
sleep 1

echo ""
echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✅ 所有 7 個應用程序已啟動到 TMUX 會話${NC}"
echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"
echo ""

echo -e "${CYAN}會話信息:${NC}"
echo "  會話名稱: $SESSION"
echo "  日誌目錄: $LOG_DIR"
echo ""

echo -e "${CYAN}附加到會話:${NC}"
echo "  ${YELLOW}tmux attach-session -t $SESSION${NC}"
echo ""

echo -e "${CYAN}窗口列表:${NC}"
echo "  0: FileProcessor      - 文件上傳和分析"
echo "  1: LoggingDash        - 日誌儀表板 (http://localhost:5000)"
echo "  2: TaskPanel          - 任務面板 (http://localhost:5001)"
echo "  3: CloudDash          - 雲儀表板 (http://localhost:5002)"
echo "  4: Singularity        - 多智能體系統演示"
echo "  5: GeminiAnalyst      - 交易分析演示"
echo "  6: MainCLI            - 主命令行界面"
echo ""

echo -e "${CYAN}快速命令:${NC}"
echo "  • 附加: ${YELLOW}tmux attach-session -t $SESSION${NC}"
echo "  • 查看窗口: ${YELLOW}tmux list-windows -t $SESSION${NC}"
echo "  • 切換窗口: ${YELLOW}tmux select-window -t $SESSION:0${NC}"
echo "  • 停止會話: ${YELLOW}tmux kill-session -t $SESSION${NC}"
echo "  • 查看日誌: ${YELLOW}tail -f $LOG_DIR/*.log${NC}"
echo ""

echo -e "${YELLOW}💡 提示:${NC}"
echo "  • 按 Ctrl+B 然後 Ctrl+X 可以分離會話"
echo "  • 按 Ctrl+B 然後數字鍵可以切換窗口"
echo "  • 使用 manage_tmux_sessions.sh 管理會話"
echo ""
