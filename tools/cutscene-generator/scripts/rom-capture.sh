#!/usr/bin/env bash
# Record a stretch of the real game as a phone-friendly GIF that plays at the game's true speed.
#
#   scripts/rom-capture.sh OUT_DIR FIRST LAST [STEP] [SYM=VALUE ...]
#
#   OUT_DIR  where to write frames/ capture.gif (real speed) and sheet.png (contact sheet)
#   FIRST..LAST  game frames since power-on (intro scene 2 is about 1026-1946)
#   STEP     keep every STEP-th frame (default 3: 20 fps, which GIF can time exactly; 60/STEP must
#            be a whole number of centiseconds apart, so use 2 (30 fps, rounded), 3, 5 or 6)
#   SYM=VALUE  write a u16 to an EWRAM symbol from pokeemerald.sym every frame, e.g.
#            sIntroCharacterGender=1 to force MIRA's intro (0 = KAEL; the game picks at random)
#
# Uses ../../game/pokeemerald.gba as built (run `make` in game/ first). Needs mGBA 0.11 with
# --script, as installed by tools/play-tester/scripts/setup-ubuntu.sh. Headless mGBA runs at
# roughly 6-10 game frames per wall second with screenshots on, so 900 frames take a couple of minutes.
set -euo pipefail
TOOL="$(cd "$(dirname "$0")/.." && pwd)"
REPO="$(cd "$TOOL/../.." && pwd)"
OUT="${1:?usage: rom-capture.sh OUT_DIR FIRST LAST [STEP] [SYM=VALUE ...]}"; FIRST="${2:?}"; LAST="${3:?}"
STEP="${4:-3}"; shift 3; [ $# -gt 0 ] && shift
ROM="$REPO/game/pokeemerald.gba"; SYM="$REPO/game/pokeemerald.sym"
[ -f "$ROM" ] || { echo "no $ROM: run make in game/"; exit 1; }
mkdir -p "$OUT"; OUT="$(cd "$OUT" && pwd)"; rm -rf "$OUT/frames"; mkdir -p "$OUT/frames"

POKES=""
for kv in "$@"; do
  name="${kv%%=*}" val="${kv#*=}"
  [ -f "$SYM" ] || (cd "$REPO/game" && make syms >/dev/null)
  addr="$(awk -v n="$name" '$4 == n { print $1 }' "$SYM")"
  [ -n "$addr" ] || { echo "symbol $name not in pokeemerald.sym"; exit 1; }
  POKES="$POKES emu:write16(0x$addr, $val)"
done

LUA="$OUT/capture.lua"
cat > "$LUA" <<EOF
local out = "$OUT/frames/"
callbacks:add("frame", function()
  local f = emu:currentFrame()
  if f >= 200 then $POKES end
  if f >= $FIRST and f <= $LAST and (f - $FIRST) % $STEP == 0 then emu:screenshot(out .. string.format("f%05d.png", f)) end
  if f == $LAST + 1 then local h = io.open(out .. "DONE", "w"); h:write("ok"); h:close() end
end)
EOF
source "$REPO/tools/play-tester/scripts/env.sh"
echo "== recording frames $FIRST-$LAST every $STEP"
timeout 1200 xvfb-run -a mgba-qt --script "$LUA" -l 0 "$ROM" > "$OUT/mgba.log" 2>&1 &
PID=$!
for _ in $(seq 1 1190); do [ -f "$OUT/frames/DONE" ] && break; sleep 1; done
# kill the xvfb-run process group (pkill -f would match this shell's own command line)
kill -- -"$(ps -o pgid= "$PID" | tr -d ' ')" 2>/dev/null || true
rm -f "$OUT/frames/DONE" "$LUA"
python3 "$TOOL/scripts/frames-to-gif.py" "$OUT/frames" "$OUT/capture.gif" --fps $((60 / STEP)) --sheet "$OUT/sheet.png"
