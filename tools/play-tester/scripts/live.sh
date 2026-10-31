#!/usr/bin/env bash
# Persistent session helper around mgba-live-mcp's CLI (same backend as its MCP server).
#   scripts/live.sh up [savestate]     start Xvfb (if needed) + an mGBA session named $SESSION
#   scripts/live.sh down               stop the session
#   scripts/live.sh lua 'return 1+1'   run inline Lua in the session
#   scripts/live.sh luafile lua/emerald.lua
#   scripts/live.sh tap A [frames]     press a button (A B START SELECT UP DOWN LEFT RIGHT L R)
#   scripts/live.sh shot out/x.png     screenshot
#   scripts/live.sh cli <args...>      raw mgba-live-cli passthrough
set -euo pipefail
cd "$(dirname "$0")/.."
source scripts/env.sh
SESSION="${SESSION:-emerald}"
export DISPLAY="$PLAYTEST_DISPLAY"
ensure_xvfb() {
  if ! xdpyinfo -display "$DISPLAY" >/dev/null 2>&1 && ! pgrep -f "Xvfb $DISPLAY" >/dev/null; then
    nohup Xvfb "$DISPLAY" -screen 0 1024x768x24 -nolisten tcp > "$PLAYTEST_OUT/xvfb.log" 2>&1 &
    sleep 2
  fi
}
cmd="${1:-}"; shift || true
case "$cmd" in
  up)
    ensure_xvfb
    extra=(); [ -n "${1:-}" ] && extra=(--savestate "$(realpath "$1")")
    # A stopped session's directory lingers and blocks reusing its id ("session_exists").
    # `status --all` archives confirmed-dead sessions into ~/.mgba-live-mcp/runtime/archived_sessions/.
    "$LIVE_CLI" status --all >/dev/null 2>&1 || true
    # --fast = fps target 600 (still ~40-60 fps real on software GL)
    "$LIVE_CLI" start --rom "$ROM" --mgba-path "$MGBA_PREFIX/bin/mgba-qt" --session-id "$SESSION" \
      --ready-timeout 40 --fast "${extra[@]}" ;;
  down)    "$LIVE_CLI" stop --session "$SESSION"; "$LIVE_CLI" status --all >/dev/null 2>&1 || true ;;
  lua)     "$LIVE_CLI" run-lua --session "$SESSION" --code "$1" ;;
  luafile) "$LIVE_CLI" run-lua --session "$SESSION" --file "$(realpath "$1")" ;;
  tap)     "$LIVE_CLI" input-tap --session "$SESSION" --key "$1" --frames "${2:-6}" ;;
  shot)    "$LIVE_CLI" screenshot --session "$SESSION" --out "$(realpath -m "${1:-$PLAYTEST_OUT/shot.png}")" ;;
  cli)     "$LIVE_CLI" "$@" ;;
  *) sed -n '2,10p' "$0"; exit 1 ;;
esac
