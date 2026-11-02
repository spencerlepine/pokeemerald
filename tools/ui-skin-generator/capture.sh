#!/usr/bin/env bash
# Capture "after" screenshots of the themed UI into after/v2/<name>.png, same names as reference/v1.
#   ./capture.sh boot            restart mGBA on the current ROM with the all-unlocked save, to the overworld
#   ./capture.sh <screen>...     run one or more named sequences below (each starts from the overworld, idle)
# Needs tools/play-tester (scripts/live.sh, Xvfb, mGBA). The save is play-tester/savestates/ui-audit.sav.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
PT="$HERE/../play-tester"; L="$PT/scripts/live.sh"; OUT="$HERE/after/v2"; mkdir -p "$OUT"
k()    { for key in "$@"; do "$L" tap "$key" 6 >/dev/null; sleep 0.15; done; }   # tap keys in order
w()    { sleep "${1:-0.5}"; }
shot() { "$L" shot "$OUT/$1.png" >/dev/null; echo "shot $1"; }
lua()  { "$L" lua "$1" >/dev/null; }
tp()   { "$L" luafile "$PT/lua/emerald.lua" >/dev/null; lua "E.teleport($1,$2,$3,$4); return 1"; sleep 3; }
menu0() { lua 'emu:write8(0x0203760e, 0); return 1'; }   # start menu cursor back to the top (sStartMenuCursorPos)
town()  { tp 0 0 17 18; nopopup; k DOWN; w 0.5; }          # Petalburg City, outdoors, popup hidden
nopopup() { lua 'emu:write8(0x020375fc, emu:read8(0x020375fc) | 1); return 1'; }   # hide the map-name popup

boot() {
  "$L" down >/dev/null 2>&1 || true
  cp "$PT/savestates/ui-audit.sav" "$PT/../../game/pokeemerald.sav"
  "$L" up >/dev/null; sleep 6; k A; sleep 3; k A; sleep 3
}

# ---------- family 1: text windows, start menu, options, save ----------
s00() { python3 "$HERE/frames_sheet.py" "$OUT/00_text_window_frames_1-20.png"; echo "shot 00_text_window_frames_1-20"; }
s01() { town; menu0; k START; w; shot 01_start_menu; k B; w; }
s05() { tp 26 31 4 8; k UP A; w 1.5; shot 05_overworld_dialogue_npc; k B B B B B B; w; }
s06() { tp 0 0 17 17; nopopup; k UP; w 0.3; k A; w 1.5; shot 06_sign_box; k B B; w; }
s42() { menu0; k START DOWN DOWN DOWN DOWN DOWN DOWN A; w 1.5; shot 42_options;
        k DOWN DOWN DOWN DOWN DOWN; w 0.5; shot 42b_options_frame; k B; w 1; k B; w; }
s43() { town; menu0; k START DOWN DOWN DOWN DOWN DOWN A; w 1.5; shot 43_save_prompt; k B; w 0.5; k B B; w; }

for s in "$@"; do "$s" 2>/dev/null || "s$s"; done
