# Savestates

Made with mGBA 0.11.0-dev (`543a197`) against the byte-identical ROM
(sha1 `f3ae088181bf583e55daf962a92bb46f4f1d07b7`). They will not match a ROM
after the game source is changed. Regenerate them then
(`scripts/new-game-to-overworld.sh`).

| File | State |
| --- | --- |
| `truck-after-new-game.ss0` | New Game (player "AA", boy), first overworld frame inside the moving truck. Party empty, ¥3000. |
| `littleroot-after-teleport.ss0` | Teleported from the truck to Littleroot Town (10,13). Story vars are still at "in truck". |
| `evergrande-party-badges-money.ss0` | Ever Grande City outside the Pokémon Center. Party is Rayquaza Lv50 + Torchic Lv6, 8 badges, ¥999999, Rare Candy x98. |
| `pokeemerald-8badges-littleroot.sav` | Battery save (flash), saved in Littleroot with the injected party/badges. Copy it next to the ROM as `pokeemerald.sav` to boot to CONTINUE. |

Load with:

```bash
scripts/live.sh up savestates/evergrande-party-badges-money.ss0
# or inside a running session:
scripts/live.sh lua 'return emu:loadStateFile("'$PWD'/savestates/truck-after-new-game.ss0")'
```
