-- Raw teleport without the helper library. Equivalent to E.teleport(0, 9, 10, 10).
-- Teleport: rewrite SaveBlock1.location (WarpData) + pos, then hand gMain.callback2 to CB2_LoadMap
local GROUP, NUM, X, Y = 0, 9, 10, 10        -- MAP_LITTLEROOT_TOWN
local sb1 = emu:read32(0x03005d8c)
emu:write8(sb1+4, GROUP); emu:write8(sb1+5, NUM); emu:write8(sb1+6, 0xFF)  -- warpId = -1 (WARP_ID_NONE)
emu:write16(sb1+8, X); emu:write16(sb1+10, Y)
emu:write16(sb1+0, X); emu:write16(sb1+2, Y)
emu:write32(0x030022c4, 0x08085fcd)          -- gMain.callback2 = CB2_LoadMap (thumb bit)
return "ok"
