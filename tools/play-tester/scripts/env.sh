# Source this: `source scripts/env.sh` (from tools/play-tester)
# Shared environment for headless mGBA 0.11 + the MCP servers.
PLAYTEST_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export PLAYTEST_ROOT
export REPO_ROOT="$(cd "$PLAYTEST_ROOT/../.." && pwd)"
export ROM="${ROM:-$REPO_ROOT/game/pokeemerald.gba}"
export MGBA_PREFIX="${MGBA_PREFIX:-/opt/mgba-0.11}"
export PATH="$MGBA_PREFIX/bin:$PATH"                 # mgba-mcp looks up `mgba-qt` on PATH
export LD_LIBRARY_PATH="$MGBA_PREFIX/lib${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
export QT_QPA_PLATFORM=xcb SDL_AUDIODRIVER=dummy LIBGL_ALWAYS_SOFTWARE=1 QT_X11_NO_MITSHM=1
export PLAYTEST_DISPLAY="${PLAYTEST_DISPLAY:-:99}"
export LIVE_CLI="$PLAYTEST_ROOT/.deps/mgba-live-mcp/.venv/bin/mgba-live-cli"
export LIVE_MCP="$PLAYTEST_ROOT/.deps/mgba-live-mcp/.venv/bin/mgba-live-mcp"
export PLAYTEST_OUT="${PLAYTEST_OUT:-$PLAYTEST_ROOT/out}"
mkdir -p "$PLAYTEST_OUT"
