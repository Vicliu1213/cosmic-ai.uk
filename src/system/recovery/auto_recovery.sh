#!/bin/bash
# 自動恢復系統 - 當對話中斷時恢復狀態
# Auto-recovery system - Restore state when conversation is interrupted

set -e

COSMIC_DIR="/workspaces/cosmic-ai.uk"
RECOVERY_STATE_FILE="$COSMIC_DIR/.recovery_state.json"
RECOVERY_LOG_FILE="$COSMIC_DIR/logs/recovery.log"

# 創建必要的目錄
mkdir -p "$COSMIC_DIR/logs"

# 初始化日誌
log_message() {
    local message="$1"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] $message" >> "$RECOVERY_LOG_FILE"
    echo "[$timestamp] $message"
}

# 保存當前狀態
save_recovery_state() {
    log_message "💾 正在保存恢復狀態..."
    
    local current_branch=$(git -C "$COSMIC_DIR" rev-parse --abbrev-ref HEAD 2>/dev/null || echo "unknown")
    local last_commit=$(git -C "$COSMIC_DIR" rev-parse --short HEAD 2>/dev/null || echo "unknown")
    local uncommitted_changes=$(git -C "$COSMIC_DIR" status --porcelain 2>/dev/null | wc -l || echo "0")
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    cat > "$RECOVERY_STATE_FILE" <<EOF
{
  "timestamp": "$timestamp",
  "current_branch": "$current_branch",
  "last_commit": "$last_commit",
  "uncommitted_changes": $uncommitted_changes,
  "status": "active"
}
EOF
    
    log_message "✅ 恢復狀態已保存"
}

# 恢復到上次狀態
restore_recovery_state() {
    if [ -f "$RECOVERY_STATE_FILE" ]; then
        log_message "🔄 檢測到之前的對話狀態，正在恢復..."
        cat "$RECOVERY_STATE_FILE"
        
        local saved_branch=$(grep -o '"current_branch": "[^"]*"' "$RECOVERY_STATE_FILE" | cut -d'"' -f4)
        
        if [ -n "$saved_branch" ] && [ "$saved_branch" != "unknown" ]; then
            log_message "🌿 恢復分支: $saved_branch"
            git -C "$COSMIC_DIR" checkout "$saved_branch" 2>/dev/null || true
        fi
        
        log_message "✅ 恢復完成"
        return 0
    else
        log_message "ℹ️  沒有找到上次的對話狀態 (首次執行)"
        return 1
    fi
}

# 顯示進度信息
show_progress() {
    echo ""
    echo "═══════════════════════════════════════════════════════════════"
    echo "📊 Cosmic AI 自動恢復系統 - Auto-Recovery System"
    echo "═══════════════════════════════════════════════════════════════"
    echo ""
    
    if restore_recovery_state; then
        echo ""
        echo "📋 重要提醒 - Important Reminders:"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "✅ 查看進度:           打開 /PROGRESS_TRACKER.md"
        echo "✅ 查看完整導覽:       打開 /INDEX.md"
        echo "✅ 查看整合計劃:       打開 /task/ETHANALGOX_INTEGRATION_ROADMAP.md"
        echo "✅ 查看激活紀錄:       打開 /memory.md"
        echo ""
    fi
    
    echo "📁 快速文件位置 - Quick File Locations:"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  進度追蹤    PROGRESS_TRACKER.md"
    echo "  導覽索引    INDEX.md"
    echo "  集成計劃    task/ETHANALGOX_INTEGRATION_ROADMAP.md"
    echo "  系統紀錄    memory.md"
    echo "  恢復日誌    logs/recovery.log"
    echo ""
    echo "═══════════════════════════════════════════════════════════════"
    echo ""
}

# 主程序
main() {
    show_progress
    save_recovery_state
}

main
