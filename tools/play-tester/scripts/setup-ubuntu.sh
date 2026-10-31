#!/usr/bin/env bash
# One-time setup on Ubuntu 24.04 (verified 2026-10-31 on a clean container, 4 cores, no GPU).
#   1. apt toolchain + agbcc -> builds game/pokeemerald.gba (sha1 must match game/rom.sha1)
#   2. mGBA 0.11-dev from source -> /opt/mgba-0.11 (released 0.10.x has NO --script flag)
#   3. MCP servers cloned into tools/play-tester/.deps (mgba-live-mcp = the one to use)
# Re-runnable: each step is skipped if its output already exists.
set -euo pipefail
cd "$(dirname "$0")/.."
source scripts/env.sh
SUDO=""; [ "$(id -u)" -ne 0 ] && SUDO="sudo"
DEPS="$PLAYTEST_ROOT/.deps"; mkdir -p "$DEPS"
MGBA_COMMIT=543a197582c30364584d773a974d7f991892fa43   # same pin mgba-live-mcp tests against (reports 0.11.0)

echo "== apt packages"
$SUDO apt-get update
DEBIAN_FRONTEND=noninteractive $SUDO apt-get install -y \
  build-essential binutils-arm-none-eabi git libpng-dev \
  cmake pkg-config qtbase5-dev qtmultimedia5-dev qttools5-dev qttools5-dev-tools \
  liblua5.4-dev zlib1g-dev libsqlite3-dev libepoxy-dev libsdl2-dev \
  xvfb xauth imagemagick python3 curl

if ! command -v uv >/dev/null; then
  echo "== installing uv"; curl -LsSf https://astral.sh/uv/install.sh | sh; export PATH="$HOME/.local/bin:$PATH"
fi

echo "== agbcc + ROM"
if [ ! -x "$REPO_ROOT/game/tools/agbcc/bin/agbcc" ]; then
  [ -d "$DEPS/agbcc" ] || git clone --depth 1 https://github.com/pret/agbcc "$DEPS/agbcc"
  (cd "$DEPS/agbcc" && ./build.sh && ./install.sh "$REPO_ROOT/game")
fi
(cd "$REPO_ROOT/game" && make -j"$(nproc)" && make syms && sha1sum -c rom.sha1 || echo "WARN: sha1 differs (expected once the game source is modified)")

echo "== mGBA 0.11-dev"
if [ ! -x "$MGBA_PREFIX/bin/mgba-qt" ]; then
  [ -d "$DEPS/mgba-src" ] || git clone https://github.com/mgba-emu/mgba "$DEPS/mgba-src"
  (cd "$DEPS/mgba-src" && git checkout -q "$MGBA_COMMIT" && mkdir -p build-playtest && cd build-playtest && \
    cmake .. -DCMAKE_BUILD_TYPE=Release -DBUILD_QT=ON -DFORCE_QT_VERSION=5 \
      -DENABLE_SCRIPTING=ON -DUSE_LUA=5.4 -DUSE_PNG=ON -DUSE_ZLIB=ON \
      -DUSE_LIBZIP=OFF -DUSE_FFMPEG=OFF -DCMAKE_INSTALL_PREFIX="$MGBA_PREFIX" && \
    make -j"$(nproc)" && $SUDO make install)
fi
"$MGBA_PREFIX/bin/mgba-qt" --help | grep -q -- "--script" && echo "mgba-qt has --script: OK"

echo "== MCP servers"
for r in penandlim/mgba-live-mcp struktured-labs/mgba-mcp; do
  d="$DEPS/${r#*/}"; [ -d "$d" ] || git clone --depth 1 "https://github.com/$r" "$d"
  (cd "$d" && uv sync)
done
echo "Done. Next: scripts/smoke-screenshot.sh"
