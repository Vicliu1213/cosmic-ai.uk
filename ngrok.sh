#!/usr/bin/env bash
# ── ngrok launcher (runs in separate process tree) ──
set -e
CONFIG="/workspaces/cosmic-ai.uk/config/ngrok.yml"

# Kill old
OLD_PIDS=$(pgrep -f "ngrok" 2>/dev/null || true)
if [ -n "$OLD_PIDS" ]; then
  for p in $OLD_PIDS; do
    kill -9 "$p" 2>/dev/null || true
  done
fi
sleep 2

# Start fresh
exec ngrok start cosmic-synergy-panel --config "$CONFIG" --log=stdout
