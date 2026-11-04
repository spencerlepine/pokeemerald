-- World port check (scripts/world-check.sh): from ui-check's overworld.ss0, teleport to each spot listed in
-- $WORLD_SPOTS ("name group num x y" per line), wait, screenshot out/world/<name>.png, and log the map header
-- the game loaded (group, num, layout size) so a wrong map shows up in the log.
local OUT = os.getenv("PLAYTEST_OUT") .. "/"
local function sym(n) return tonumber(os.getenv("SYM_" .. n), 16) end
local SB1P, CB2, CB2_LOADMAP = sym("gSaveBlock1Ptr"), sym("gMain") + 4, sym("CB2_LoadMap")
local MAPHDR = sym("gMapHeader")
local K = {A=0,B=1,SELECT=2,START=3,RIGHT=4,LEFT=5,UP=6,DOWN=7}
local function sb1() return emu:read32(SB1P) end
local function log(s) console:log(s); local h = io.open(OUT .. "log.txt", "a"); h:write(s .. "\n"); h:close() end
local function teleport(g, n, x, y)
  local b = sb1()
  emu:write8(b+4, g); emu:write8(b+5, n); emu:write8(b+6, 0xFF)
  emu:write16(b+8, x); emu:write16(b+10, y); emu:write16(b+0, x); emu:write16(b+2, y)
  emu:write32(CB2, CB2_LOADMAP | 1)
end
local spots = {}
for line in io.lines(os.getenv("WORLD_SPOTS")) do
  local name, g, n, x, y, keys = line:match("^(%S+)%s+(%d+)%s+(%d+)%s+(%d+)%s+(%d+)%s*(.*)$")
  if name then spots[#spots+1] = {name, tonumber(g), tonumber(n), tonumber(x), tonumber(y), keys} end
end
local steps = {}
local function add(s) steps[#steps+1] = s end
add({fn=function() emu:loadStateFile(OUT .. "../ui/overworld.ss0") end}); add({wait=30})
for _, s in ipairs(spots) do
  add({fn=function() teleport(s[2], s[3], s[4], s[5]) end}); add({wait=200})
  for k, n in s[6]:gmatch("(%u+)(%d*)") do
    for _ = 1, (tonumber(n) or 1) do
      add({key=k, n=8}); add({wait=12})
      if os.getenv("WORLD_TRACE") then add({fn=function() local b = sb1()
        log(string.format("  %s %s step map %d.%d pos %d,%d", s[1], k, emu:read8(b+4), emu:read8(b+5), emu:read16(b+0), emu:read16(b+2))) end}) end
    end
    add({wait=60})
  end
  add({fn=function()
    local lay = emu:read32(MAPHDR)
    local b = sb1()
    log(string.format("%s map %d.%d pos %d,%d layout %dx%d cb2 %08x", s[1], emu:read8(b+4), emu:read8(b+5),
      emu:read16(b+0), emu:read16(b+2), emu:read32(lay), emu:read32(lay + 4), emu:read32(CB2)))
  end})
  add({shot=s[1]})
end
local i, t, held = 1, 0, nil
callbacks:add("frame", function()
  local s = steps[i]
  if not s then local h = io.open(OUT .. "DONE", "w"); h:write("ok"); h:close(); i = i + 1; return end
  if s.wait then t = t + 1; if t >= s.wait then t = 0; i = i + 1 end
  elseif s.key then
    if t == 0 then emu:addKey(K[s.key]) end
    t = t + 1; if t >= s.n then emu:clearKey(K[s.key]); t = 0; i = i + 1 end
  elseif s.fn then s.fn(); i = i + 1
  elseif s.shot then emu:screenshot(OUT .. s.shot .. ".png"); i = i + 1 end
end)
