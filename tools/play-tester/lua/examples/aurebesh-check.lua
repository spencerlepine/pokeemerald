-- One-shot scenario runner for scripts/aurebesh-check.sh (SCENARIO env var). Addresses are the modern
-- build's (arm-none-eabi-nm game/pokeemerald_modern.elf); re-read them if the game code moves.
-- boot skips the Star Wars intro crawl (A, UP to YES, A) and waits until the player can move in the truck.
local OUT = os.getenv("PLAYTEST_OUT") .. "/"
local SC = os.getenv("SCENARIO")
local SB1P, CB2, CB2_OVERWORLD, CB2_LOADMAP = 0x030071f4, 0x030036d4, 0x08142180, 0x08142350
local K = {A=0,B=1,SELECT=2,START=3,RIGHT=4,LEFT=5,UP=6,DOWN=7}
local function sb1() return emu:read32(SB1P) end
local function setFlag(id, on)
  local a = sb1() + 0x1270 + (id >> 3); local v = emu:read8(a)
  if on then v = v | (1 << (id & 7)) else v = v & ~(1 << (id & 7)) end
  emu:write8(a, v & 0xFF)
end
local function teleport(g, n, x, y)
  local b = sb1()
  emu:write8(b+4, g); emu:write8(b+5, n); emu:write8(b+6, 0xFF)
  emu:write16(b+8, x); emu:write16(b+10, y); emu:write16(b+0, x); emu:write16(b+2, y)
  emu:write32(CB2, CB2_LOADMAP | 1)
end
local function log(s) console:log(s); local h = io.open(OUT .. "log.txt", "a"); h:write(s .. "\n"); h:close() end
local function done() local h = io.open(OUT .. "DONE", "w"); h:write("ok"); h:close() end

-- steps: {wait=n} | {key=K, n=frames} | {fn=function} | {shot=name}
local steps, i, t = {}, 1, 0
local function add(s) steps[#steps+1] = s end
local function press(k, n) add({key=k, n=n or 4}); add({wait=10}) end

if SC == "boot" then
  local taps = 0
  add({loop=function()
    if emu:read32(CB2) == (CB2_OVERWORLD | 1) then return true end
    taps = taps + 1
    if emu:read32(CB2) == 0x08114649 then return false, ({"A", "UP", "A"})[taps % 3 + 1] end  -- intro crawl: skip? YES
    return false, (taps % 8 == 0) and "START" or "A"
  end})
  add({wait=1200})
  add({fn=function() emu:saveStateFile(OUT .. "overworld.ss0"); log("saved overworld") end})
  add({shot="overworld"})
else
  add({fn=function() emu:loadStateFile(OUT .. "overworld.ss0") end})
  add({wait=30})
  local S = {
    sign_outer = {24, 71, 5, 7, nil}, sign_inner = {24, 72, 14, 9, nil},
    sign_inner6 = {24, 72, 14, 19, nil},
    regirock = {24, 6, 8, 8, 0x3A7}, regice = {24, 67, 8, 8, 0x3A9}, registeel = {24, 68, 8, 8, 0x3A8},
  }
  local s = S[SC]
  add({fn=function() if s[5] then setFlag(s[5], false) end; teleport(s[1], s[2], s[3], s[4]) end})
  add({wait=240})
  press("UP", 2); add({wait=20}); press("A", 4)
  if SC:sub(1,4) == "sign" then
    add({wait=150}); add({shot=SC})
  else
    add({fn=function() local b = sb1(); log(string.format("pos %d,%d map %d.%d", emu:read16(b), emu:read16(b+2), emu:read8(b+4), emu:read8(b+5))) end})
    for f = 1, 40 do add({wait=8}); add({shot=SC .. string.format("_%02d", f)}) end
  end
end
add({fn=done})

local held, holdN = nil, 0
callbacks:add("frame", function()
  if emu:currentFrame() % 300 == 0 then if emu:currentFrame() % 1500 == 0 then emu:screenshot(OUT .. "dbg_" .. emu:currentFrame() .. ".png") end; log(string.format("f%d cb2 %08x step %d", emu:currentFrame(), emu:read32(CB2), i)) end
  if held then
    holdN = holdN - 1
    if holdN <= 0 then emu:clearKey(K[held]); held = nil; t = 6 end
    return
  end
  if t > 0 then t = t - 1; return end
  local s = steps[i]; if not s then return end
  if s.wait then t = s.wait; i = i + 1
  elseif s.key then emu:addKey(K[s.key]); held = s.key; holdN = s.n; i = i + 1
  elseif s.fn then s.fn(); i = i + 1
  elseif s.shot then emu:screenshot(OUT .. s.shot .. ".png"); i = i + 1
  elseif s.loop then
    local ok, k = s.loop()
    if ok then i = i + 1 else emu:addKey(K[k]); held = k; holdN = 4; t = 0 end
  end
end)
