#!/usr/bin/env bash
# See a scene in the real game without touching ../../game's sources:
#   scripts/rom-preview.sh scenes/intro_bike/out [FIRST LAST STEP]   (game frames since boot)
#
# 1. copies ../../game to a scratch dir (once; later runs reuse it and build incrementally),
# 2. drops <out>/game/** over it and runs make,
# 3. boots that ROM headless in mGBA (tools/play-tester must be set up: scripts/setup-ubuntu.sh)
#    and writes a screenshot every STEP frames from FIRST to LAST into <out>/rom/.
#
# mGBA only ran our Lua script for ROMs at ../../game/pokeemerald.gba in testing, so the scratch
# ROM is swapped into that path for the run and the original is put back afterwards (it is an
# ignored build artifact). Intro scene 2 (the bike ride) is on screen from about frame 1300 to 1950.
set -euo pipefail
TOOL="$(cd "$(dirname "$0")/.." && pwd)"
REPO="$(cd "$TOOL/../.." && pwd)"
OUT="$(cd "${1:?usage: rom-preview.sh <scene out dir> [first last step]}" && pwd)"
FIRST="${2:-1300}" LAST="${3:-1950}" STEP="${4:-10}"
SCRATCH="${PXL_ROM_SCRATCH:-${TMPDIR:-/tmp}/pxl-rom-preview}"

[ -d "$OUT/game" ] || { echo "no $OUT/game: build the scene first (pxl build)"; exit 1; }
# tools/PALETTES.md gate: every PNG and .pal the scene writes must pass the shared palette check.
( cd "$REPO/tools/palette-enforcer" && python3 -m gba_palette audit "$OUT/game" ) \
  || { echo "palette gate failed (tools/PALETTES.md): fix the scene's palettes before it goes near the ROM"; exit 1; }
if [ ! -d "$SCRATCH/game" ]; then
  echo "== copying game to $SCRATCH (first run)"
  mkdir -p "$SCRATCH"; cp -a "$REPO/game" "$SCRATCH/game"
fi
echo "== dropping in $(cd "$OUT/game" && find . -type f | wc -l) file(s) and building"
cp -r "$OUT/game/." "$SCRATCH/game/"
(cd "$SCRATCH/game" && make -j"$(nproc)" > "$SCRATCH/build.log" 2>&1) || { tail -20 "$SCRATCH/build.log"; exit 1; }

ROM_PATH="$REPO/game/pokeemerald.gba"
BACKUP="$SCRATCH/original.gba"
[ -f "$ROM_PATH" ] && cp "$ROM_PATH" "$BACKUP"
restore() { if [ -f "$BACKUP" ]; then cp "$BACKUP" "$ROM_PATH"; else rm -f "$ROM_PATH"; fi; }
trap restore EXIT
cp "$SCRATCH/game/pokeemerald.gba" "$ROM_PATH"

SHOTS="$OUT/rom"; rm -rf "$SHOTS"; mkdir -p "$SHOTS"
cat > "$SCRATCH/shots.lua" <<EOF
local out = "$SHOTS/"
callbacks:add("frame", function()
  local f = emu:currentFrame()
  if f >= $FIRST and f <= $LAST and (f - $FIRST) % $STEP == 0 then emu:screenshot(out .. string.format("f%05d.png", f)) end
  if f == $LAST + 1 then local h = io.open(out .. "DONE", "w"); h:write("ok"); h:close() end
end)
EOF
cd "$REPO/tools/play-tester"; source scripts/env.sh
echo "== running to frame $LAST (about 1 s of wall time per 6 game frames)"
timeout 900 xvfb-run -a mgba-qt --script "$SCRATCH/shots.lua" -l 0 "$ROM_PATH" > "$SCRATCH/mgba.log" 2>&1 &
PID=$!
for _ in $(seq 1 890); do [ -f "$SHOTS/DONE" ] && break; sleep 1; done
# Kill the xvfb-run process group (pkill -f would match this shell's own command line).
kill -- -"$(ps -o pgid= "$PID" | tr -d ' ')" 2>/dev/null || true
rm -f "$SHOTS/DONE"
echo "-> $(ls "$SHOTS" | wc -l) screenshot(s) in $SHOTS"
