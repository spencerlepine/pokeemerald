#!/usr/bin/env bash
# Boot a ROM headless, mash through New Game, give the player a party mon, walk in Route 101 tall grass
# until a wild battle starts, and screenshot the battle background twice (intro slide done, then settled).
#   scripts/rom-battle.sh ROM OUTDIR
# Writes OUTDIR/battle_150.png and battle_400.png and logs gBattleEnvironment (0 = tall grass).
# Same constraints as rom-shots.sh: mGBA 0.11 from the play-tester setup, files outside /tmp/claude-*.
set -euo pipefail
HERE="$(cd "$(dirname "$0")/.." && pwd)"; PT="$HERE/../play-tester"
ROM="$(realpath "$1")"; OUT="$(realpath -m "$2")"
mkdir -p "$OUT"; source "$PT/scripts/env.sh"
cat > "$OUT/battle.lua" <<LUA
local LOG = io.open("$OUT/battle.log", "w")
local function log(s) LOG:write(s .. "\n"); LOG:flush() end
dofile("$PT/lua/emerald.lua")
local f, phase, taps, n = 0, "boot", 0, 0
local CB2 = function() return emu:read32(E.ADDR.gMainCallback2) end
callbacks:add("frame", function()
  local ok, e = pcall(function()
    f = f + 1
    if phase == "boot" then
      if CB2() == 0x08085e5d then phase = "party"; f = 0; emu:setKeys(0); log("overworld " .. taps) end
      local k = f % 16
      if k == 0 then taps = taps + 1; emu:setKeys((taps % 8 == 0) and 8 or 1) elseif k == 4 then emu:setKeys(0) end
      return
    end
    if phase == "party" and f == 30 then
      E.writeMon(0, {species=280, level=30, exp=27000, moves={10,45,0,0}, pp={35,40,0,0}, base={45,60,40,45,70,50}, nick="TEST", personality=7})
      E.setFlag(0x860, true); E.teleport(0, 16, 3, 4); phase = "walk"; f = 0; log("teleported"); return
    end
    if phase == "walk" then
      if CB2() == 0x08038421 then phase = "battle"; f = 0; emu:setKeys(0); log("battle env " .. emu:read8(0x02022ff0)); return end
      if f > 200 then local k = (f // 20) % 2; emu:setKeys(k == 0 and 32 or 16) end
      if f > 6000 then log("no battle"); local h = io.open("$OUT/BDONE","w"); h:write("fail"); h:close(); phase = "done" end
      return
    end
    if phase == "battle" then
      n = n + 1
      if n == 150 or n == 400 then emu:screenshot("$OUT/battle_" .. n .. ".png"); log("shot " .. n) end
      if n == 401 then local h = io.open("$OUT/BDONE","w"); h:write("ok"); h:close() end
    end
  end)
  if not ok then log("err " .. tostring(e)) end
end)
LUA
rm -f "$OUT/BDONE"
timeout 400 xvfb-run -a mgba-qt --script "$OUT/battle.lua" -l 0 "$ROM" > "$OUT/mgba.log" 2>&1 &
PID=$!
for _ in $(seq 1 390); do [ -f "$OUT/BDONE" ] && break; sleep 1; done
kill -- -"$(ps -o pgid= "$PID" | tr -d ' ')" 2>/dev/null || true
cat "$OUT/battle.log"; ls "$OUT"/battle_*.png
