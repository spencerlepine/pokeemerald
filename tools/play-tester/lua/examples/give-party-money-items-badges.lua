-- Requires lua/emerald.lua to have been loaded first in the same session (defines global E).
-- Rayquaza Lv50 (slow growth: 5*50^3/4 exp), Torchic Lv5 (medium slow: 6/5n^3-15n^2+100n-140 = 135)
E.writeMon(0, {species=406, level=50, exp=156250, moves={337,19,200,245}, pp={15,15,10,5},
               base={105,150,90,95,150,90}, nick="RAYQUAZA", personality=0})
E.writeMon(1, {species=280, level=5, exp=135, moves={10,45,0,0}, pp={35,40,0,0},
               base={45,60,40,45,70,50}, nick="TORCHIC", personality=25*7})
E.setFlag(0x860, true)                      -- FLAG_SYS_POKEMON_GET (menu shows POKEMON)
for f = 0x867, 0x86E do E.setFlag(f, true) end -- all 8 badges
E.setMoney(999999)
E.addItem(68, 99)                           -- ITEM_RARE_CANDY = 68 (verified in the bag)
return {m0=E.readMon(0), m1=E.readMon(1), money=E.getMoney(), items=E.items(), count=emu:read8(0x020244e9)}
