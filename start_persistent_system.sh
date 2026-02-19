#!/bin/bash

# 持久化系統啟動腳本
# Persistent System Launcher - Task Panel + Image Upload + Chat Interface
# 保持任務面板、圖像上傳和對話框界面一直開著

PROJECT_ROOT="/root/comic_ai"
cd "$PROJECT_ROOT"

# 設置顏色
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}🚀 Comic AI 持久化系統啟動${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"

# 檢查 tmux 是否已安裝
if ! command -v tmux &> /dev/null; then
    echo -e "${YELLOW}⚠️  tmux 未安裝，正在安裝...${NC}"
    apt-get update && apt-get install -y tmux
fi

# 設置會話名稱
SESSION_NAME="comic_ai_persistent"
TIMESTAMP=$(date +%s)

# 檢查會話是否已存在
if tmux has-session -t "$SESSION_NAME" 2>/dev/null; then
    echo -e "${YELLOW}⚠️  會話已存在，正在附加...${NC}"
    tmux attach-session -t "$SESSION_NAME"
    exit 0
fi

echo -e "${GREEN}✅ 正在創建新會話: $SESSION_NAME${NC}"

# 創建新會話 (分離模式)
tmux new-session -d -s "$SESSION_NAME" -x 200 -y 50

# ─────────────────────────────────────────
# 窗口 1: 任務面板 (Task Panel)
# ─────────────────────────────────────────
echo -e "${BLUE}📌 設置窗口 1: 任務面板${NC}"
tmux new-window -t "$SESSION_NAME" -n "task-panel"
tmux send-keys -t "$SESSION_NAME:task-panel" "cd $PROJECT_ROOT && python task_panel_optimized.py" Enter

# ─────────────────────────────────────────
# 窗口 2: 圖像上傳處理 (Image Upload Handler)
# ─────────────────────────────────────────
echo -e "${BLUE}🖼️  設置窗口 2: 圖像上傳處理${NC}"
tmux new-window -t "$SESSION_NAME" -n "image-upload"
tmux send-keys -t "$SESSION_NAME:image-upload" "cd $PROJECT_ROOT && python intelligent_file_processor_cli.py" Enter

# ─────────────────────────────────────────
# 窗口 3: OpenCode 對話界面 (Chat Interface)
# ─────────────────────────────────────────
echo -e "${BLUE}💬 設置窗口 3: OpenCode 對話界面${NC}"
tmux new-window -t "$SESSION_NAME" -n "opencode-chat"
tmux send-keys -t "$SESSION_NAME:opencode-chat" "cd $PROJECT_ROOT && opencode" Enter

# ─────────────────────────────────────────
# 窗口 4: 日誌監視器 (Log Monitor)
# ─────────────────────────────────────────
echo -e "${BLUE}📊 設置窗口 4: 日誌監視器${NC}"
tmux new-window -t "$SESSION_NAME" -n "logs"
tmux send-keys -t "$SESSION_NAME:logs" "cd $PROJECT_ROOT && tail -f logs/*.log 2>/dev/null | head -50" Enter

# ─────────────────────────────────────────
# 窗口 5: 儀表板 (Dashboard)
# ─────────────────────────────────────────
echo -e "${BLUE}📈 設置窗口 5: 儀表板${NC}"
tmux new-window -t "$SESSION_NAME" -n "dashboard"
tmux send-keys -t "$SESSION_NAME:dashboard" "cd $PROJECT_ROOT && python logging_dashboard.py" Enter

# ─────────────────────────────────────────
# 窗口 6: 命令行界面 (CLI Interface)
# ─────────────────────────────────────────
echo -e "${BLUE}⚙️  設置窗口 6: 命令行界面${NC}"
tmux new-window -t "$SESSION_NAME" -n "cli"
tmux send-keys -t "$SESSION_NAME:cli" "cd $PROJECT_ROOT && python src/cli/cli.py" Enter

# ─────────────────────────────────────────
# 設置第 0 個窗口為控制中心
# ─────────────────────────────────────────
echo -e "${BLUE}🎛️  設置窗口 0: 控制中心${NC}"
tmux send-keys -t "$SESSION_NAME:0" "cat << 'WELCOME'
${BLUE}═══════════════════════════════════════════════════════════${NC}
🚀 Comic AI 持久化系統已啟動
${BLUE}═══════════════════════════════════════════════════════════${NC}

📌 可用窗口:
  1️⃣  task-panel     - 實時任務面板
  2️⃣  image-upload   - 圖像上傳和處理
  3️⃣  opencode-chat  - OpenCode 對話界面
  4️⃣  logs           - 日誌監視器
  5️⃣  dashboard      - 儀表板
  6️⃣  cli            - 命令行界面
  0️⃣  control        - 此窗口 (控制中心)

🎮 操作指令:
  Ctrl+b :list-windows           - 列出所有窗口
  Ctrl+b :select-window -t <N>   - 切換到窗口 N
  Ctrl+b d                       - 分離會話
  tmux attach -t comic_ai_persistent - 重新附加

📝 快速命令:
  tmux kill-session -t comic_ai_persistent    - 停止會話
  tmux send-keys -t comic_ai_persistent:task-panel 'command' Enter - 發送命令

${BLUE}═══════════════════════════════════════════════════════════${NC}
WELCOME
" Enter

# 選擇第一個窗口
tmux select-window -t "$SESSION_NAME:1"

echo ""
echo -e "${GREEN}✅ 系統已啟動!${NC}"
echo -e "${YELLOW}會話名稱: $SESSION_NAME${NC}"
echo ""
echo -e "${BLUE}命令:${NC}"
echo "  • 附加會話: ${GREEN}tmux attach -t $SESSION_NAME${NC}"
echo "  • 列出窗口: ${GREEN}tmux list-windows -t $SESSION_NAME${NC}"
echo "  • 停止會話: ${GREEN}tmux kill-session -t $SESSION_NAME${NC}"
echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"

# 附加會話
tmux attach-session -t "$SESSION_NAME"
