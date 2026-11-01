#!/usr/bin/env bash
# Boot a ROM headless, mash through New Game, teleport to each map and screenshot it.
#   scripts/rom-shots.sh ROM OUTDIR "group:num:x:y:name" ...
# e.g. scripts/rom-shots.sh test.gba out/rom 0:9:10:9:littleroot 0:0:15:12:petalburg
# Needs the play-tester setup (mGBA 0.11 with --script). Files must live outside /tmp/claude-*:
# mGBA's script host could not read the scratchpad there. ~2-4 min.
set -euo pipefail
HERE="$(cd "$(dirname "$0")/.." && pwd)"; PT="$HERE/../play-tester"
ROM="$(realpath "$1")"; OUT="$(realpath -m "$2")"; shift 2
mkdir -p "$OUT"; source "$PT/scripts/env.sh"
plan=""; for s in "$@"; do IFS=: read -r g n x y name <<<"$s"; plan+="{$g,$n,$x,$y,\"$name\"},"; done
cat > "$OUT/shots.lua" <<LUA
local LOG = io.open("$OUT/lua.log", "w")
local function log(s) LOG:write(s .. "\n"); LOG:flush() end
dofile("$PT/lua/emerald.lua")
local plan = { $plan }
local f, step, phase, taps = 0, 1, "boot", 0
callbacks:add("frame", function()
  local ok, e = pcall(function()
    f = f + 1
    if phase == "boot" then
      if emu:read32(E.ADDR.gMainCallback2) == 0x08085e5d then phase = "ow"; f = 0; emu:setKeys(0); log("overworld after " .. taps .. " taps"); return end
      local k = f % 16
      if k == 0 then taps = taps + 1; emu:setKeys((taps % 8 == 0) and 8 or 1) elseif k == 4 then emu:setKeys(0) end
      return
    end
    local p = plan[step]; if not p then return end
    if f == 120 then E.teleport(p[1], p[2], p[3], p[4]) end
    if f == 460 then emu:screenshot("$OUT/rom_" .. p[5] .. ".png"); log("shot " .. p[5]); step = step + 1; f = 0
      if not plan[step] then local h = io.open("$OUT/DONE", "w"); h:write("ok"); h:close() end end
  end)
  if not ok then log("err " .. tostring(e)) end
end)
LUA
rm -f "$OUT/DONE"
timeout 400 xvfb-run -a mgba-qt --script "$OUT/shots.lua" -l 0 "$ROM" > "$OUT/mgba.log" 2>&1 &
PID=$!
for _ in $(seq 1 390); do [ -f "$OUT/DONE" ] && break; sleep 1; done
kill -- -"$(ps -o pgid= "$PID" | tr -d ' ')" 2>/dev/null || true
cat "$OUT/lua.log"; ls "$OUT"/rom_*.png
