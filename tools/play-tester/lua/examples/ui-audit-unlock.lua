-- Unlocks everything the UI audit needs (run after lua/emerald.lua, in the overworld):
-- Pokedex + StarNAV + match call + ribbons + Frontier Pass flags, all Hoenn dex seen/caught, every Fly town,
-- full bag + PC items, 5 Pokeblocks, a few decorations, 500 coins, 10 ribbons on party slot 1,
-- 12 PC box mons (copies of party slots 1-2), the 16 box wallpapers.
local a=emu:read32(0x03005d8c); local b=emu:read32(0x03005d90); local key=emu:read16(b+0xAC)
for _,f in ipairs({0x861,0x862,0x12F,0x130,0xD8,0xFD,0x119,0xD6,0x132,0x1D3,0x1D4,0x89B,0x8D2}) do E.setFlag(f,true) end
for f=0x86F,0x87E do E.setFlag(f,true) end
for i=0,51 do emu:write8(b+0x28+i,0xFF); emu:write8(b+0x5C+i,0xFF); emu:write8(a+0x988+i,0xFF); emu:write8(a+0x3B24+i,0xFF) end
local function put(off, list) for i,v in ipairs(list) do local s=a+off+(i-1)*4; emu:write16(s,v[1]); emu:write16(s+2,(v[2] ~ key)&0xFFFF) end end
put(0x560,{{13,20},{22,15},{19,5},{85,3},{86,10},{121,2},{200,1},{68,20}})
put(0x5D8,{{259,1},{272,1},{260,1},{261,1},{262,1},{264,1},{266,1},{268,1},{270,1},{273,1}})
put(0x650,{{4,30},{3,20},{2,10},{1,1},{10,5}})
put(0x690,{{289,1},{290,1},{312,1},{339,1},{340,1}})
put(0x790,{{133,5},{135,3},{139,7},{142,2}})
emu:write16(a+0x498,13); emu:write16(a+0x49A,4); emu:write16(a+0x49C,121); emu:write16(a+0x49E,1)
local blocks={{1,20,0,0,0,0,10},{2,0,30,0,0,0,15},{3,0,0,25,0,0,12},{4,0,0,0,40,0,20},{5,0,0,0,0,35,8}}
for i,bl in ipairs(blocks) do for j,v in ipairs(bl) do emu:write8(a+0x848+(i-1)*7+(j-1),v) end end
emu:write8(a+0x2734,1); emu:write8(a+0x2735,2); emu:write8(a+0x2734+10,10); emu:write8(a+0x2798,77); emu:write8(a+0x2799,78)
emu:write16(a+0x494,(500 ~ key)&0xFFFF)
-- ribbons on party slot 1
local p=0x020244ec; local pid,otId=emu:read32(p),emu:read32(p+4); local xk=(pid ~ otId)&0xFFFFFFFF
local w={} for i=0,11 do w[i]=(emu:read32(p+0x20+i*4) ~ xk)&0xFFFFFFFF end
local ORD={"GAEM","GAME","GEAM","GEMA","GMAE","GMEA","AGEM","AGME","AEGM","AEMG","AMGE","AMEG","EGAM","EGMA","EAGM","EAMG","EMGA","EMAG","MGAE","MGEA","MAGE","MAEG","MEGA","MEAG"}
local mpos=ORD[(pid%24)+1]:find("M")-1
w[mpos*3+2]=0x000F9249|(w[mpos*3+2]&0xF8000000)
local sum=0 for i=0,11 do sum=(sum+(w[i]&0xFFFF)+(w[i]>>16))&0xFFFF end
for i=0,11 do emu:write32(p+0x20+i*4,(w[i] ~ xk)&0xFFFFFFFF) end; emu:write16(p+0x1C,sum)
-- PC boxes
local s=emu:read32(0x03005d94)
for i=0,11 do local src=p+(i%2)*100; for j=0,79 do emu:write8(s+4+i*80+j, emu:read8(src+j)) end end
for bx=0,13 do emu:write8(s+33730+bx, bx) end; emu:write8(s+33730+12,14); emu:write8(s+33730+11,15)
return "unlocked"
