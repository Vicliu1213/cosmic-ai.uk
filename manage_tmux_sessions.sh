#!/bin/bash

# Comic AI Tmux 會話管理腳本
# Tmux Session Management Script

set -e

SESSION_NAME="comic-ai"

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 函數: 顯示菜單
show_menu() {
    echo -e "${BLUE}╔════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║  Comic AI Tmux 會話管理控制台      ║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${CYAN}會話: $SESSION_NAME${NC}"
    echo ""
    echo "操作選項:"
    echo "  1) 附加到會話 (attach)"
    echo "  2) 列出所有視窗"
    echo "  3) 切換視窗 (select window)"
    echo "  4) 查看會話狀態"
    echo "  5) 查看服務日誌"
    echo "  6) 殺死進程/重啟服務"
    echo "  7) 停止會話"
    echo "  8) 退出"
    echo ""
}

# 函數: 列出視窗
list_windows() {
    echo -e "${CYAN}會話視窗列表:${NC}"
    echo ""
    if tmux has-session -t "$SESSION_NAME" 2>/dev/null; then
        tmux list-windows -t "$SESSION_NAME" -F "#{window_index}: #{window_name} - #{window_title} (#{window_panes} pane(s))"
    else
        echo -e "${RED}會話不存在${NC}"
    fi
    echo ""
}

# 函數: 切換視窗
select_window() {
    if ! tmux has-session -t "$SESSION_NAME" 2>/dev/null; then
        echo -e "${RED}❌ 會話不存在${NC}"
        return 1
    fi
    
    list_windows
    read -p "輸入視窗編號 (0-5): " window_num
    
    if [[ "$window_num" =~ ^[0-5]$ ]]; then
        tmux select-window -t "$SESSION_NAME:$window_num"
        tmux attach-session -t "$SESSION_NAME"
    else
        echo -e "${RED}❌ 無效的視窗編號${NC}"
    fi
}

# 函數: 查看會話狀態
show_status() {
    echo -e "${CYAN}會話狀態:${NC}"
    echo ""
    
    if tmux has-session -t "$SESSION_NAME" 2>/dev/null; then
        echo -e "${GREEN}✅ 會話存在${NC}"
        echo ""
        echo "進程信息:"
        ps aux | grep python | grep -v grep | while read line; do
            echo "  $line"
        done
        echo ""
        echo "視窗狀態:"
        tmux list-windows -t "$SESSION_NAME" -F "  #{window_index}: #{window_name} (#{pane_current_command})"
    else
        echo -e "${RED}❌ 會話不存在${NC}"
    fi
    echo ""
}

# 函數: 查看日誌
view_logs() {
    SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
    LOG_DIR="$SCRIPT_DIR/logs/tmux"
    
    echo -e "${CYAN}可用日誌:${NC}"
    echo ""
    ls -lh "$LOG_DIR"/*.log 2>/dev/null | awk '{print $9, "(" $5 ")"}' || echo "未找到日誌"
    echo ""
    
    read -p "輸入日誌文件路徑或 tail -f 日誌 [留空跳過]: " log_file
    
    if [ -n "$log_file" ]; then
        if [ -f "$log_file" ]; then
            tail -f "$log_file"
        else
            echo -e "${RED}❌ 文件不存在${NC}"
        fi
    fi
}

# 函數: 殺死進程
kill_processes() {
    echo -e "${YELLOW}選擇要殺死的進程:${NC}"
    echo ""
    echo "  1) 殺死所有 Python 進程"
    echo "  2) 殺死特定進程"
    echo "  3) 重啟會話"
    echo "  4) 返回"
    echo ""
    
    read -p "選擇 [1-4]: " choice
    
    case $choice in
        1)
            echo -e "${YELLOW}殺死所有 Python 進程...${NC}"
            pkill -f python || echo "未找到進程"
            sleep 2
            show_status
            ;;
        2)
            ps aux | grep python | grep -v grep
            read -p "輸入進程 PID: " pid
            if [ -n "$pid" ]; then
                kill -9 "$pid" 2>/dev/null && echo -e "${GREEN}✅ 進程已殺死${NC}" || echo -e "${RED}❌ 殺死失敗${NC}"
            fi
            ;;
        3)
            echo -e "${YELLOW}重啟會話...${NC}"
            tmux kill-session -t "$SESSION_NAME" 2>/dev/null || true
            sleep 1
            exec "$SCRIPT_DIR/setup_tmux_sessions.sh"
            ;;
        4)
            return 0
            ;;
    esac
}

# 函數: 停止會話
stop_session() {
    read -p "確定要停止會話嗎? (y/n): " confirm
    if [ "$confirm" = "y" ]; then
        echo -e "${YELLOW}停止會話 '$SESSION_NAME'...${NC}"
        tmux kill-session -t "$SESSION_NAME" 2>/dev/null && echo -e "${GREEN}✅ 會話已停止${NC}" || echo -e "${RED}❌ 會話不存在${NC}"
    else
        echo "已取消"
    fi
    echo ""
}

# 主循環
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

while true; do
    show_menu
    read -p "輸入選項 [1-8]: " choice
    echo ""
    
    case $choice in
        1)
            if tmux has-session -t "$SESSION_NAME" 2>/dev/null; then
                tmux attach-session -t "$SESSION_NAME"
            else
                echo -e "${RED}❌ 會話不存在，請先運行 setup_tmux_sessions.sh${NC}"
            fi
            ;;
        2)
            list_windows
            ;;
        3)
            select_window
            ;;
        4)
            show_status
            ;;
        5)
            view_logs
            ;;
        6)
            kill_processes
            ;;
        7)
            stop_session
            ;;
        8)
            echo -e "${GREEN}退出${NC}"
            exit 0
            ;;
        *)
            echo -e "${RED}❌ 無效選項${NC}"
            ;;
    esac
    
    read -p "按 Enter 繼續..."
    clear
done
