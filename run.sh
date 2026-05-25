#!/usr/bin/env bash
set -e
# ═══════════════════════════════════════════════════════════════
#  Cosmic Engine v3.0 ─ 快速啟動 (引擎 only, 無 ngrok)
# ═══════════════════════════════════════════════════════════════
cd /workspaces/cosmic-ai.uk
echo "啟動引擎..."
COSMIC_KEEP_RUNNING=1 python3 main.py &
EPID=$!
echo "$EPID" > /tmp/cosmic.pid
echo "PID=$EPID — tail -f cosmic_engine.log 查看進度"
