#!/usr/bin/env bash
# Headless one-shot: boot the ROM under xvfb-run, screenshot frames 300/900/1800, kill mGBA.
# Output: $PLAYTEST_OUT/frame_{300,900,1800}.png  (~45 s on 4 CPU cores with software GL)
set -euo pipefail
cd "$(dirname "$0")/.."
source scripts/env.sh
rm -f "$PLAYTEST_OUT/DONE"
timeout 180 xvfb-run -a mgba-qt --script lua/examples/oneshot-screenshots.lua -l 0 "$ROM" > "$PLAYTEST_OUT/mgba.log" 2>&1 &
PID=$!
for _ in $(seq 1 170); do [ -f "$PLAYTEST_OUT/DONE" ] && break; sleep 1; done
# emu:quit() is unreliable; kill the xvfb-run process group. (Don't use `pkill -f mgba-qt`
# inside a shell whose own command line contains "mgba-qt": it kills that shell.)
kill -- -"$(ps -o pgid= "$PID" | tr -d ' ')" 2>/dev/null || kill "$PID" 2>/dev/null || true
ls -la "$PLAYTEST_OUT"/frame_*.png
