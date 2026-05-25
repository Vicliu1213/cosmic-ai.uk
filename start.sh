#!/usr/bin/env bash
set -e
# ═══════════════════════════════════════════════════════════════
#  Cosmic Engine v3.0 — 一鍵啟動
#  自動完成：引擎 → 協同面板 → ngrok 隧道
# ═══════════════════════════════════════════════════════════════

cd "$(dirname "$0")"
WS="/workspaces/cosmic-ai.uk"
ENV_FILE="$HOME/.hermes/.env"
NGROK_CFG="$WS/config/ngrok.yml"
NGROK_HOME_CFG="$HOME/.config/ngrok/ngrok.yml"

mkdir -p "$HOME/.hermes" "$HOME/.config/ngrok"

# ── 1. ngrok Authtoken ──
if ! grep -q 'NGROK_AUTHTOKEN=' "$ENV_FILE" 2>/dev/null; then
    echo "╔════════════════════════════════════════════╗"
    echo "║  需要 ngrok Authtoken                       ║"
    echo "║  → https://dashboard.ngrok.com               ║"
    echo "║    → get-started → your-authtoken 複製       ║"
    echo "╚════════════════════════════════════════════╝"
    read -rp "貼上你的 ngrok Authtoken: " TOKEN
    echo "NGROK_AUTHTOKEN=$TOKEN" >> "$ENV_FILE"
fi

source "$ENV_FILE"

# ── 2. 寫入 ngrok.yml ──
cat > "$NGROK_CFG" <<YAML
version: "3"
agent:
  authtoken: "$NGROK_AUTHTOKEN"
tunnels:
  cosmic-synergy-panel:
    proto: http
    addr: 8788
    inspect: true
    host_header: "localhost:8788"
YAML
ln -sf "$NGROK_CFG" "$NGROK_HOME_CFG"

# ── 3. 啟動引擎 ──
echo "╔════════════════════════════════════════════╗"
echo "║  宇宙智能體核心引擎 v3.0  啟動中...         ║"
echo "╚════════════════════════════════════════════╝"

COSMIC_KEEP_RUNNING=1 python3 "$WS/main.py" &
ENGINE_PID=$!
echo "引擎 PID: $ENGINE_PID"

# 等待 API 就緒
for i in $(seq 1 60); do
    if curl -sf http://localhost:8788/api/synergy/status >/dev/null 2>&1; then
        echo "✓ 協同面板就緒 (port 8788)"
        break
    fi
    sleep 2
done

# ── 4. 啟動 ngrok ──
echo "啟動 ngrok 隧道中..."
nohup ngrok start cosmic-synergy-panel --log=stdout > /tmp/ngrok.log 2>&1 &

sleep 5
NGROK_URL=""
for i in $(seq 1 10); do
    NGROK_URL=$(curl -sf http://localhost:4040/api/tunnels 2>/dev/null | python3 -c "
import sys,json
try:
    d=json.load(sys.stdin)
    for t in d.get('tunnels',[]):
        print(t['public_url'])
except: pass
" 2>/dev/null)
    [ -n "$NGROK_URL" ] && break
    sleep 2
done

# ── 5. 輸出摘要 ──
echo ""
echo "╔══════════════════════════════════════════════════════════╗"
echo "║  宇宙智能體核心引擎已啟動                                ║"
echo "╠══════════════════════════════════════════════════════════╣"
echo "║  引擎 PID:     $ENGINE_PID"
echo "║  本機面板:     http://localhost:8788/pages/synergy_panel.html"
echo "║  API 即時數據: http://localhost:8788/api/synergy/levels"
echo "║  公開網址:     ${NGROK_URL:-— ngrok 未就緒 (查看 /tmp/ngrok.log)}"
echo "║  引擎日誌:     $WS/cosmic_engine.log"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

wait "$ENGINE_PID"
