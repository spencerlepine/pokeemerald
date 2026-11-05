-- Map seam check (scripts/seam-check.sh): for each line of $SEAM_SPOTS ("name group num x y DIR steps"),
-- teleport to the spot and dump the map buffer the game built (gBackupMapLayout: the map plus what it shows of
-- its neighbours), walk `steps` steps toward DIR across the seam, dump the three field BG tilemaps, then load the
-- map the player stands on afresh at the same place and dump them again. A tilemap that differs after walking
-- means the screen was not redrawn right when crossing. wiki/tools/port_world.py seams verify reads the dumps.
local OUT = os.getenv("PLAYTEST_OUT") .. "/"
local function sym(n) return tonumber(os.getenv("SYM_" .. n), 16) end
local SB1P, CB2, CB2_LOADMAP = sym("gSaveBlock1Ptr"), sym("gMain") + 4, sym("CB2_LoadMap")
local BACKUP, CAM = sym("gBackupMapLayout"), sym("sFieldCameraOffset")
local BGS = {sym("gOverworldTilemapBuffer_Bg1"), sym("gOverworldTilemapBuffer_Bg2"), sym("gOverworldTilemapBuffer_Bg3")}
local K = {RIGHT=4, LEFT=5, UP=6, DOWN=7}
local function sb1() return emu:read32(SB1P) end
local function log(s) local h = io.open(OUT .. "log.txt", "a"); h:write(s .. "\n"); h:close() end
local function teleport(g, n, x, y)
  local b = sb1()
  emu:write8(b+4, g); emu:write8(b+5, n); emu:write8(b+6, 0xFF)
  emu:write16(b+8, x); emu:write16(b+10, y); emu:write16(b+0, x); emu:write16(b+2, y)
  emu:write32(CB2, CB2_LOADMAP | 1)
end
local function where() local b = sb1(); return emu:read8(b+4), emu:read8(b+5), emu:read16(b+0), emu:read16(b+2) end
local function save(name, data) local h = io.open(OUT .. name, "wb"); h:write(data); h:close() end
local function dump_backup(name)
  local w, h, p = emu:read32(BACKUP), emu:read32(BACKUP + 4), emu:read32(BACKUP + 8)
  save(name, emu:readRange(BACKUP, 8) .. emu:readRange(p, w * h * 2))
end
local function dump_tilemaps(name)
  local s = emu:readRange(CAM, 4)
  for _, a in ipairs(BGS) do s = s .. emu:readRange(emu:read32(a), 0x800) end
  save(name, s)
end
local steps = {}
local function add(s) steps[#steps+1] = s end
add({fn=function() emu:loadStateFile(OUT .. "../ui/overworld.ss0") end}); add({wait=30})
-- no wild battles on the way: the lead at level 100 and a long repel (VAR_REPEL_STEP_COUNT, 0x4021)
add({fn=function()
  local party = sym("gPlayerParty")
  for k = 0, emu:read8(sym("gPlayerPartyCount")) - 1 do emu:write8(party + k * 100 + 0x54, 100) end
  emu:write16(sb1() + tonumber(os.getenv("SB1_VARS")) + 0x21 * 2, 9999)
end})
for line in io.lines(os.getenv("SEAM_SPOTS")) do
  local name, g, n, x, y, dir, cnt = line:match("^(%S+)%s+(%d+)%s+(%d+)%s+(%d+)%s+(%d+)%s+(%u+)%s+(%d+)")
  if name then
    g, n, x, y, cnt = tonumber(g), tonumber(n), tonumber(x), tonumber(y), tonumber(cnt)
    add({fn=function() teleport(g, n, x, y); emu:write16(sb1() + tonumber(os.getenv("SB1_VARS")) + 0x21 * 2, 9999) end})
    add({wait=150})
    add({fn=function() dump_backup(name .. ".load") end})
    for _ = 1, cnt do add({key=dir, n=8}); add({wait=12}) end
    add({wait=40})
    add({fn=function()
      local g2, n2, x2, y2 = where()
      log(string.format("%s %d.%d %d,%d -> %d.%d %d,%d cb2 %08x", name, g, n, x, y, g2, n2, x2, y2, emu:read32(CB2)))
      dump_tilemaps(name .. ".walk")
      emu:screenshot(OUT .. name .. ".walk.png")
      teleport(g2, n2, x2, y2)
    end})
    add({wait=150})
    add({fn=function() dump_tilemaps(name .. ".ref"); dump_backup(name .. ".refload"); emu:screenshot(OUT .. name .. ".ref.png") end})
  end
end
local i, t = 1, 0
callbacks:add("frame", function()
  local s = steps[i]
  if not s then local h = io.open(OUT .. "DONE", "w"); h:write("ok"); h:close(); i = i + 1; return end
  if s.wait then t = t + 1; if t >= s.wait then t = 0; i = i + 1 end
  elseif s.key then
    if t == 0 then emu:addKey(K[s.key]) end
    t = t + 1; if t >= s.n then emu:clearKey(K[s.key]); t = 0; i = i + 1 end
  elseif s.fn then s.fn(); i = i + 1 end
end)
