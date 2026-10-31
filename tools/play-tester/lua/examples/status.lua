-- Prints map, position, player name bytes, money, party count and gMain.callback2.
-- callback2 == 08085e5d (CB2_Overworld|1) means the player is in the overworld.
local sb1 = emu:read32(0x03005d8c); local sb2 = emu:read32(0x03005d90)
local key = emu:read32(sb2 + 0xAC)
local name = {} for i=0,6 do name[#name+1] = string.format("%02x", emu:read8(sb2+i)) end
return {
  map = string.format("group %d num %d", emu:read8(sb1+4), emu:read8(sb1+5)),
  pos = string.format("%d,%d", emu:read16(sb1+0), emu:read16(sb1+2)),
  name_bytes = table.concat(name, " "), gender = emu:read8(sb2+8),
  money = emu:read32(sb1+0x490) ~ key, partyCount = emu:read8(0x020244e9),
  cb2 = string.format("%08x", emu:read32(0x030022c4)), frame = emu:currentFrame()
}
