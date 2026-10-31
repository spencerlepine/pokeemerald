-- Emerald runtime helpers for mGBA Lua (addresses from this build's pokeemerald.sym)
E = E or {}
local ADDR = {
  gSaveBlock1Ptr = 0x03005d8c, gSaveBlock2Ptr = 0x03005d90,
  gPlayerPartyCount = 0x020244e9, gPlayerParty = 0x020244ec,
  gMainCallback2 = 0x030022c4, CB2_LoadMap = 0x08085fcc,
}
E.ADDR = ADDR
local function sb1() return emu:read32(ADDR.gSaveBlock1Ptr) end
local function sb2() return emu:read32(ADDR.gSaveBlock2Ptr) end
local function key() return emu:read32(sb2() + 0xAC) end

-- ---------- warp ----------
function E.teleport(group, num, x, y)
  local b = sb1()
  emu:write8(b+4, group); emu:write8(b+5, num); emu:write8(b+6, 0xFF) -- WARP_ID_NONE
  emu:write16(b+8, x); emu:write16(b+10, y)
  emu:write16(b+0, x); emu:write16(b+2, y)
  emu:write32(ADDR.gMainCallback2, ADDR.CB2_LoadMap | 1)
  return true
end

-- ---------- flags / money / items ----------
function E.setFlag(id, on)
  local a = sb1() + 0x1270 + (id >> 3)
  local v = emu:read8(a)
  if on == false then v = v & ~(1 << (id & 7)) else v = v | (1 << (id & 7)) end
  emu:write8(a, v & 0xFF)
end
function E.getFlag(id) return (emu:read8(sb1() + 0x1270 + (id >> 3)) >> (id & 7)) & 1 end
function E.setMoney(n) emu:write32(sb1() + 0x490, (n ~ key()) & 0xFFFFFFFF) end
function E.getMoney() return (emu:read32(sb1() + 0x490) ~ key()) & 0xFFFFFFFF end
function E.addItem(itemId, qty) -- Items pocket: 30 slots of {u16 id, u16 qty ^ key}
  local base, k = sb1() + 0x560, key() & 0xFFFF
  for i = 0, 29 do
    local a = base + i * 4
    local id = emu:read16(a)
    if id == itemId or id == 0 then
      emu:write16(a, itemId); emu:write16(a + 2, (qty ~ k) & 0xFFFF); return i
    end
  end
  return nil
end
function E.items()
  local base, k, out = sb1() + 0x560, key() & 0xFFFF, {}
  for i = 0, 29 do
    local id = emu:read16(base + i*4)
    if id ~= 0 then out[#out+1] = string.format("%d x%d", id, emu:read16(base + i*4 + 2) ~ k) end
  end
  return out
end

-- ---------- party (encrypted BoxPokemon) ----------
local ORDER = { -- personality % 24 -> position of {growth, attacks, evs, misc}
 {0,1,2,3},{0,1,3,2},{0,2,1,3},{0,3,1,2},{0,2,3,1},{0,3,2,1},{1,0,2,3},{1,0,3,2},
 {2,0,1,3},{3,0,1,2},{2,0,3,1},{3,0,2,1},{1,2,0,3},{1,3,0,2},{2,1,0,3},{3,1,0,2},
 {2,3,0,1},{3,2,0,1},{1,2,3,0},{1,3,2,0},{2,1,3,0},{3,1,2,0},{2,3,1,0},{3,2,1,0}}

local CHAR = {} -- minimal English charmap
for i = 0, 25 do CHAR[string.char(65+i)] = 0xBB + i; CHAR[string.char(97+i)] = 0xD5 + i end
for i = 0, 9 do CHAR[tostring(i)] = 0xA1 + i end
CHAR[" "] = 0x00
local function encode(s, n)
  local t = {}
  for i = 1, n do local c = s:sub(i, i); t[i] = (c ~= "" and CHAR[c]) or 0xFF end
  return t
end

-- sub: table of 4 substructs, each 12 bytes (array of byte values)
local function u16le(t, off, v) t[off+1] = v & 0xFF; t[off+2] = (v >> 8) & 0xFF end
local function u32le(t, off, v) for i = 0, 3 do t[off+1+i] = (v >> (8*i)) & 0xFF end end

local function calcStat(base, lvl, isHp)
  local v = ((2 * base + 31) * lvl) // 100
  if isHp then return v + lvl + 10 else return v + 5 end
end

-- spec = {species, level, exp, moves={..4}, pp={..4}, base={hp,atk,def,spe,spa,spd}, nick="...", personality=0, item=0}
function E.writeMon(slot, spec)
  local a = ADDR.gPlayerParty + slot * 100
  local b2 = sb2()
  local otId = emu:read32(b2 + 0x0A)
  local pid = spec.personality or 0
  local subs = {}
  for t = 0, 3 do subs[t] = {} for i = 1, 12 do subs[t][i] = 0 end end
  -- growth
  u16le(subs[0], 0, spec.species); u16le(subs[0], 2, spec.item or 0)
  u32le(subs[0], 4, spec.exp); subs[0][10] = 70 -- friendship
  -- attacks
  for i = 1, 4 do u16le(subs[1], (i-1)*2, spec.moves[i] or 0); subs[1][8+i] = spec.pp[i] or 0 end
  -- misc: met level / game(Emerald=3) / ball(Poke Ball=4) / otGender, IVs all 31
  local origin = (spec.level & 0x7F) | (3 << 7) | (4 << 11) | ((emu:read8(b2+8) & 1) << 15)
  u16le(subs[3], 2, origin)
  u32le(subs[3], 4, 0x3FFFFFFF) -- six IVs of 31, not egg, ability 0
  -- checksum over decrypted 48 bytes, u16 sum
  local order = ORDER[(pid % 24) + 1]
  local plain = {}
  for pos = 0, 3 do
    local t
    for k = 0, 3 do if order[k+1] == pos then t = k end end
    for i = 1, 12 do plain[pos*12 + i] = subs[t][i] end
  end
  local sum = 0
  for i = 1, 48, 2 do sum = (sum + plain[i] + (plain[i+1] << 8)) & 0xFFFF end
  -- header
  for i = 0, 99 do emu:write8(a + i, 0) end
  emu:write32(a, pid); emu:write32(a + 4, otId)
  local nick = encode(spec.nick, 10)
  for i = 1, 10 do emu:write8(a + 7 + i, nick[i]) end
  emu:write8(a + 0x12, 2)      -- language English
  emu:write8(a + 0x13, 0x02)   -- hasSpecies
  for i = 0, 6 do emu:write8(a + 0x14 + i, emu:read8(b2 + i)) end -- OT name = player
  emu:write16(a + 0x1C, sum)
  local xk = (pid ~ otId) & 0xFFFFFFFF
  for w = 0, 11 do
    local v = plain[w*4+1] | (plain[w*4+2] << 8) | (plain[w*4+3] << 16) | (plain[w*4+4] << 24)
    emu:write32(a + 0x20 + w*4, (v ~ xk) & 0xFFFFFFFF)
  end
  -- unencrypted party stats
  local L, B = spec.level, spec.base
  local hp = calcStat(B[1], L, true)
  emu:write8(a + 0x54, L); emu:write8(a + 0x55, 0xFF) -- no mail
  emu:write16(a + 0x56, hp); emu:write16(a + 0x58, hp)
  emu:write16(a + 0x5A, calcStat(B[2], L)); emu:write16(a + 0x5C, calcStat(B[3], L))
  emu:write16(a + 0x5E, calcStat(B[4], L)); emu:write16(a + 0x60, calcStat(B[5], L))
  emu:write16(a + 0x62, calcStat(B[6], L))
  if emu:read8(ADDR.gPlayerPartyCount) <= slot then emu:write8(ADDR.gPlayerPartyCount, slot + 1) end
  return sum
end

-- decrypt and validate a party slot (independent of writeMon)
function E.readMon(slot)
  local a = ADDR.gPlayerParty + slot * 100
  local pid, otId = emu:read32(a), emu:read32(a + 4)
  local xk = (pid ~ otId) & 0xFFFFFFFF
  local plain = {}
  for w = 0, 11 do
    local v = (emu:read32(a + 0x20 + w*4) ~ xk) & 0xFFFFFFFF
    for i = 0, 3 do plain[w*4 + i + 1] = (v >> (8*i)) & 0xFF end
  end
  local sum = 0
  for i = 1, 48, 2 do sum = (sum + plain[i] + (plain[i+1] << 8)) & 0xFFFF end
  local order = ORDER[(pid % 24) + 1]
  local g = order[1] * 12; local at = order[2] * 12
  local function rd16(off) return plain[off+1] | (plain[off+2] << 8) end
  return {
    species = rd16(g), exp = rd16(g+4) | (rd16(g+6) << 16),
    moves = {rd16(at), rd16(at+2), rd16(at+4), rd16(at+6)},
    level = emu:read8(a + 0x54), hp = emu:read16(a + 0x56),
    checksumOk = (sum == emu:read16(a + 0x1C)),
  }
end


-- ---------- warp table lookups from ROM (gMapGroups) ----------
E.ADDR.gMapGroups = 0x08486578
function E.mapHeader(group, num)
  local grp = emu:read32(E.ADDR.gMapGroups + group * 4)
  return emu:read32(grp + num * 4)
end
function E.warpsOf(group, num)
  local ev = emu:read32(E.mapHeader(group, num) + 4)
  local n, w, out = emu:read8(ev + 1), emu:read32(ev + 8), {}
  for i = 0, n - 1 do
    local a = w + i * 8
    out[#out+1] = {i = i, x = emu:read16(a), y = emu:read16(a + 2), toGroup = emu:read8(a + 7), toNum = emu:read8(a + 6)}
  end
  return out
end
-- land on a map's warp tile (a door), which is always a walkable spot
function E.teleportToWarp(group, num, warpIdx)
  local w = E.warpsOf(group, num)[warpIdx + 1]
  return E.teleport(group, num, w.x, w.y)
end

return "emerald helpers loaded"
