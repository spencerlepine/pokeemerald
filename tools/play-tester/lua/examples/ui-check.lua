-- One-shot scenario runner for scripts/ui-check.sh (SCENARIO env var). Addresses come from the modern
-- build's symbols (the script reads them with arm-none-eabi-nm), so they follow any change to the game code.
-- boot skips the Star Wars intro crawl (A, UP to YES, A) and waits until the player can move in the truck.
local OUT = os.getenv("PLAYTEST_OUT") .. "/"
local SC = os.getenv("SCENARIO")
local function sym(n) return tonumber(os.getenv("SYM_" .. n), 16) end  -- set by scripts/ui-check.sh from nm
local SB1P, CB2, CB2_OVERWORLD, CB2_LOADMAP = sym("gSaveBlock1Ptr"), sym("gMain") + 4, sym("CB2_Overworld"), sym("CB2_LoadMap")
local CB2_INTRO_CRAWL = sym("CB2_IntroCrawl") | 1
local K = {A=0,B=1,SELECT=2,START=3,RIGHT=4,LEFT=5,UP=6,DOWN=7}
local function sb1() return emu:read32(SB1P) end
-- SYSTEM_FLAGS (include/constants/flags.h) moved from 0x860 to 0x888 when MAX_TRAINERS_COUNT went to 904 (2026-11-04);
-- every SaveBlock1 field after flags[] moved 6 bytes (VARS at 0x13A2, seen2 at 0x3B2A).
local SYS, VARS, SEEN2 = 0x888, 0x13A2, 0x3B2A
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
-- party, items and flags through lua/emerald.lua's helpers, pointed at this build's addresses
dofile(os.getenv("PLAYTEST_ROOT") .. "/lua/emerald.lua")
E.ADDR.gSaveBlock1Ptr, E.ADDR.gSaveBlock2Ptr = SB1P, sym("gSaveBlock2Ptr")
E.ADDR.gPlayerParty, E.ADDR.gPlayerPartyCount = sym("gPlayerParty"), sym("gPlayerPartyCount")
local function pocketItem(off, id, qty)  -- first free slot of a bag pocket (offset in SaveBlock1)
  local k = emu:read32(emu:read32(E.ADDR.gSaveBlock2Ptr) + 0xAC) & 0xFFFF
  emu:write16(sb1() + off, id); emu:write16(sb1() + off + 2, (qty ~ k) & 0xFFFF)
end
local function setupCreatures()  -- the net-new species (old-Unown slots) with the net-new moves
  local mons = {{255, "WYYYSCHOKK", {70,95,70,55,55,65}}, {252, "AURAREAVER", {68,65,55,110,135,85}},
                {257, "SLEEN", {75,70,80,50,50,70}}, {258, "JUBBABIRD", {60,55,60,80,85,80}},
                {262, "BOARWOLF", {80,95,70,85,50,70}}, {264, "YUZZUM", {85,85,60,75,55,70}}}
  for i, m in ipairs(mons) do
    E.writeMon(i - 1, {species=m[1], level=30, exp=27000, moves={356,357,358,33}, pp={15,20,20,35},
                       base=m[3], nick=m[2], personality=i})
  end
end
local function setupParty()
  E.writeMon(0, {species=280, level=12, exp=1400, moves={10,45,52,0}, pp={35,40,25,0},
                 base={45,60,40,45,70,50}, nick="SUNCHICK", personality=0})
  E.writeMon(1, {species=406, level=50, exp=156250, moves={337,19,200,245}, pp={15,15,10,5},
                 base={105,150,90,95,150,90}, nick="EXOGORTH", personality=7})
  setFlag(SYS, true); setFlag(SYS + 1, true); setFlag(SYS + 2, true)  -- COMPANION, DATAPAD, StarNAV menus
  for f = SYS + 7, SYS + 14 do setFlag(f, true) end                        -- badges
  E.addItem(13, 5)                       -- POTION (Items pocket)
  pocketItem(0x650, 4, 10)               -- POKE BALL (Poke Balls pocket)
  pocketItem(0x690, 289, 1)              -- TM01 (TMs & HMs pocket)
  pocketItem(0x790, 133, 3)              -- CHERI BERRY (Berries pocket)
  pocketItem(0x5D8, 259, 1)              -- MACH BIKE (Key Items pocket)
  local b2 = emu:read32(E.ADDR.gSaveBlock2Ptr)          -- every DATAPAD entry seen and owned
  for i = 0, 51 do emu:write8(b2 + 0x28 + i, 0xFF); emu:write8(b2 + 0x5C + i, 0xFF)
                   emu:write8(sb1() + 0x988 + i, 0xFF); emu:write8(sb1() + SEEN2 + i, 0xFF) end
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
    if emu:read32(CB2) == CB2_INTRO_CRAWL then return false, ({"A", "UP", "A"})[taps % 3 + 1] end  -- intro crawl: skip? YES
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
    regirock = {24, 6, 8, 8, 0x3A7}, battle = {24, 6, 8, 8, 0x3A7}, regice = {24, 67, 8, 8, 0x3A9}, registeel = {24, 68, 8, 8, 0x3A8},
  }
  local s = S[SC]
  if SC == "people" then s = {0, 9, 14, 13, nil} end  -- Mos Pelgo (Littleroot Town), among its townsfolk
  if SC == "creatures" then s = {24, 6, 8, 8, 0x3A7} end
  if SC == "tour" or SC == "dex" or SC == "creatures_dex" or SC:sub(1,4) == "menu" or SC:sub(1,7) == "starnav" then s = {0, 9, 5, 8, nil} end  -- Mos Pelgo (Littleroot Town): open ground
  add({fn=function() if SC == "tour" or SC == "battle" or SC == "dex" or SC:sub(1,4) == "menu" or SC == "people"
                        or SC:sub(1,9) == "creatures" or SC:sub(1,7) == "starnav" then setupParty() end
                     if SC:sub(1,7) == "starnav" then  -- every town visited (fly icons), Battle Frontier on the map
                       for f = SYS + 0xF, SYS + 0x1E do setFlag(f, true) end; setFlag(SYS + 0x48, true) end
                     if SC:sub(1,9) == "creatures" then setupCreatures() end
                     if s[5] then setFlag(s[5], false) end; teleport(s[1], s[2], s[3], s[4]) end})
  add({wait=240})
  local function shot(n, w) add({wait=w or 60}); add({shot=SC .. "_" .. n}) end
  if SC == "starnav" then  -- StarNAV map: galaxy, cursor jumps, zoom into a planet and out again
    local function frames(name, n, gap) for f = 1, n do add({wait=gap}); add({shot=string.format("%s_%s_%02d", SC, name, f)}) end end
    press("START"); add({wait=30}); press("DOWN"); press("DOWN"); press("DOWN"); press("A"); shot("01_menu", 150)
    press("A"); shot("02_galaxy", 150)
    press("RIGHT"); shot("03_right", 30); press("UP"); shot("04_up", 30); press("LEFT"); shot("05_left", 30)
    press("DOWN"); shot("06_down", 30)
    add({key="A", n=2}); frames("07_zoom_in", 12, 2); shot("08_planet", 60)
    press("RIGHT"); press("RIGHT"); press("UP"); shot("09_planet_cursor", 30)
    add({key="A", n=2}); frames("10_zoom_out", 12, 2); shot("11_galaxy_again", 60)
    for _ = 1, 3 do press("RIGHT") end; press("A"); shot("12_other_planet", 120)
    press("B"); shot("13_exit", 150)
  elseif SC == "starnav_town" then  -- the wall map in a Bacta Center (field_region_map.c)
    add({fn=function() emu:write32(CB2, sym("CB2_FieldShowRegionMap") | 1) end}); shot("01_open", 120)
    press("RIGHT"); shot("02_right", 30); press("A"); shot("03_planet", 120); press("DOWN"); shot("04_cursor", 30)
    press("A"); shot("05_galaxy", 120); press("B"); shot("06_exit", 150)
  elseif SC == "starnav_dex" then  -- the Datapad area screen keeps Emerald's map (pokedex_area_screen.c)
    press("START"); add({wait=30}); press("DOWN"); press("UP"); add({wait=20}); press("A"); add({wait=240})
    press("A"); shot("01_entry", 200); press("A"); shot("02_area", 200); press("B"); shot("03_back", 120)
  elseif SC == "starnav_reopen" then  -- leave the StarNAV zoomed in, reopen it, then fly from the Fly map
    press("START"); add({wait=30}); press("DOWN"); press("DOWN"); press("DOWN"); press("A"); add({wait=150})
    press("A"); add({wait=150}); press("A"); add({wait=60}); press("B"); add({wait=150})
    press("A"); shot("01_reopened", 150); press("B"); add({wait=150}); press("B"); add({wait=150})
    press("B"); add({wait=120})
    add({fn=function() emu:write8(sym("gMain") + 0x438, 0); emu:write32(CB2, sym("CB2_OpenFlyMap") | 1) end})
    shot("02_fly", 150); press("A"); shot("03_flying", 200); shot("04_landed", 300)
  elseif SC == "starnav_fly" then  -- the Fly map (region_map.c), opened straight from the field
    add({fn=function() emu:write8(sym("gMain") + 0x438, 0); emu:write32(CB2, sym("CB2_OpenFlyMap") | 1) end})
    shot("01_open", 150); press("RIGHT"); shot("02_cursor", 30)
    press("B"); shot("03_galaxy", 120); press("UP"); shot("04_jump", 30); press("A"); shot("05_planet", 120)
    press("B"); shot("06_galaxy", 120)
  elseif SC == "tour" then
    press("START"); shot("01_start_menu")
    press("DOWN"); press("A"); shot("02_party", 90)
    press("A"); shot("03_party_action", 30)
    press("A"); shot("04_summary_info", 90)
    press("RIGHT"); shot("05_summary_skills"); press("RIGHT"); shot("06_summary_moves")
    press("RIGHT"); shot("07_summary_showcase")
    press("B"); add({wait=90}); press("B"); add({wait=20}); press("B"); add({wait=90})
    press("DOWN"); press("A"); shot("08_bag_items", 90)
    for p = 1, 4 do press("RIGHT"); shot(string.format("%02d_bag_pocket%d", 8 + p, p + 1), 40) end
    press("B"); add({wait=90})
    press("DOWN"); press("A"); shot("13_starnav", 150); press("B"); add({wait=120})
    press("UP"); press("UP"); press("UP"); press("A"); shot("14_datapad", 120); press("B"); add({wait=120})
    for _ = 1, 4 do press("DOWN") end
    press("A"); shot("15_trainer_card", 90); press("B"); add({wait=90})
    press("DOWN"); press("A"); shot("16_save", 60); press("B"); add({wait=30})
    press("DOWN"); press("A"); shot("17_options", 90); press("B"); add({wait=60})
  elseif SC == "dex" then
    press("START"); add({wait=30}); press("DOWN"); press("UP"); add({wait=20}); press("A")
    add({fn=function() log(string.format("dex after A cb2 %08x", emu:read32(CB2))) end}); shot("1", 240)
    add({fn=function() log(string.format("dex later cb2 %08x", emu:read32(CB2))) end})
    press("A"); shot("2", 200); press("RIGHT"); shot("3", 100); press("RIGHT"); shot("4", 100)
    press("B"); add({wait=100}); for _ = 1, 20 do press("DOWN", 2) end; press("A"); shot("5", 200)
  elseif SC:sub(1,4) == "menu" then  -- menuN: open start menu entry N (0 = top), then a few A presses
    local n = tonumber(SC:sub(5)); press("START"); add({wait=30})
    for _ = 1, n do press("DOWN") end
    press("A"); add({fn=function() log(string.format("after A cb2 %08x", emu:read32(CB2))) end}); shot("1", 240); add({fn=function() log(string.format("later cb2 %08x", emu:read32(CB2))) end}); press("A"); shot("2", 120); press("A"); shot("3", 120)
  elseif SC == "creatures" then  -- party icons, summary pages, then a battle with a new species in front
    press("START"); press("DOWN"); press("A"); shot("01_party", 90)
    press("A"); press("A"); shot("02_summary_info", 90)
    press("RIGHT"); shot("03_summary_skills"); press("RIGHT"); shot("04_summary_moves")
    press("DOWN"); press("A"); shot("05_move_info", 60)
    for _ = 1, 6 do press("B"); add({wait=60}) end
    press("UP", 2); add({wait=20}); press("A", 4); add({wait=500})
    for f = 1, 6 do press("A"); shot(string.format("%02d_battle", 5 + f), 60) end
  elseif SC == "creatures_dex" then  -- the Datapad list's new end (203-214) and a new species' page
    -- open the list at No. 206 (the list remembers its last position; 0-based)
    add({fn=function() emu:write16(sym("sLastSelectedPokemon"), 205) end})
    press("START"); add({wait=30}); press("DOWN"); press("UP"); add({wait=20}); press("A"); add({wait=240})
    shot("02_list_end", 60); press("A"); shot("03_entry", 200); press("RIGHT"); shot("04_area", 100)
    press("RIGHT"); shot("05_cry", 100); press("RIGHT"); shot("06_size", 100)
  elseif SC == "people" then  -- each net-new walker in turn on the Littleroot NPCs (twin, fat man, boy)
    -- an object event's graphicsId (offset 5, 0x24 bytes each) is used again when the field reloads from a menu
    local OBJ, ids = sym("gObjectEvents"), {76, 77, 78, 79, 80, 81, 237, 238, 239}
    if os.getenv("PEOPLE_IDS") then ids = {}; for n in os.getenv("PEOPLE_IDS"):gmatch("%d+") do ids[#ids + 1] = tonumber(n) end end
    for r = 1, #ids do
      add({fn=function()
        for o = 0, 15 do
          local a = OBJ + o * 0x24; local g = emu:read8(a + 5)
          if (emu:read8(a) & 1) == 1 and (g == 6 or g == 17 or g == 9 or (g >= 76 and g <= 81) or g >= 237)
             then emu:write8(a + 5, ids[r]) end
        end end})
      press("START"); add({wait=30}); press("DOWN"); press("A"); add({wait=120}); press("B"); add({wait=120})
      press("B"); add({wait=60}); add({shot=string.format("people_%03d", ids[r])})
    end
  elseif SC == "battle" then
    press("UP", 2); add({wait=20}); press("A", 4); add({wait=500})
    for f = 1, 6 do press("A"); shot(string.format("%02d", f), 60) end
  else
  press("UP", 2); add({wait=20}); press("A", 4)
  end
  if SC == "tour" or SC == "battle" or SC == "dex" or SC:sub(1,4) == "menu" or SC:sub(1,9) == "creatures"
     or SC == "people" or SC:sub(1,7) == "starnav" then
  elseif SC:sub(1,4) == "sign" then
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
