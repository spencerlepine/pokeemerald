# ui-skin-generator

**Status:** phase 3 done (2026-11-02). The Dune theme ships in the game as palette-only edits: tiles, tilemaps and
code paths are unchanged, so every screen behaves as before.

| Path | What it is |
|---|---|
| `reference/v1/` | 155 captures of every themed UI before the theme (headless mGBA, 240x160), plus `00_text_window_frames_1-20.png`. |
| `mockup.py`, `mockups/dune_v1/` | The approved mockups. `python3 mockup.py` regenerates them from `reference/v1/`. |
| `dune.py` | The Dune colour rule `tx(rgb, family)`, shared by the mockups and the game. |
| `apply.py` | Writes the theme into `game/`. Every family is listed in `FAMILIES` with the exact palette slots it touches. |
| `capture.sh` | Boots the ROM with `play-tester/savestates/ui-audit.sav` and captures after-shots into `after/v2/`. |
| `after/v2/` | 122 after-shots, same names as `reference/v1/`. |
| `gallery.py` | `python3 gallery.py OUT.html` builds the v1 / mockup / v2 comparison page. |
| `identify.py` | Dumps the live palette RAM and names the source file of each 16-colour bank. Use it to find a screen's palettes. |
| `frames_sheet.py` | Draws the 20 text-window frames into one sheet. |

## Use

```
python3 apply.py            # rewrite every family in DONE from the vanilla palettes (idempotent)
python3 apply.py --list     # print each recoloured slot, old > new
python3 apply.py --check    # exit 1 if game/ differs from what apply would write
cd ../../game && make       # incremental, about 7 s
./capture.sh boot 01 b01 h18      # restart mGBA on the new ROM, then run capture sequences
```

`apply.py` reads each file from git at `VANILLA_REF`, so a rule change re-runs cleanly. `.pal` files keep CRLF.
PNGs only get a new PLTE chunk. A few edits live in C: the options backdrop colour, the Pokédex cry arrow, and
the StarNAV menu headers, which point at Dune copies of their palette bank (`Append`).

Restart mGBA after every build (`./capture.sh boot`); a running session keeps the old ROM. The blender,
roulette, contest, factory and level-up sequences end inside their screen, so run them last or reboot after.

## What changed

Families 1-8 in `apply.py`: text windows and the 20 frames, party and summary, bag and Pokéblock, Pokédex, StarNAV,
PC storage, battle message box and naming screen, trainer card, shop, Easy Chat, Frontier Pass, berry tag, Berry
Blender, wall clock, contest appeal screen, slot machine, roulette credit box, Battle Factory rental screen.

## Kept vanilla on purpose

- Type chips and contest category labels and colours (owner's rule). The summary type chips, the StarNAV
  Cool/Beauty/Cute/Smart/Tough headers and option squares, and the contest painting frames stay.
- Text colours (palette slots 1-9 and runtime text colours). The mockup had turned some red and green text gold.
- HP bars, gender colours (also the pink female trainer-card backdrop and the clock face), hearts, applause meter.
- Creatures, items, maps, map popups, box wallpapers, mail, ribbons, the bag picture, and pending-art icons.
- Colour-coded game pieces: slot bet-line lamps and flashing lights, the roulette wheel and grid.
- Trainer card tiers stay distinct: green goes sand, bronze goes taupe, copper, silver and gold keep their faces.

Known limit: on the condition screens (StarNAV and Pokéblock) the striped backdrop shares palette slots 6-15 with
the contest colour circles, so it stays green and blue. Fixing it needs a new BG palette bank and tilemap edits.

Not captured in v2 (same palettes as captured screens, or kept vanilla): trainer battles, evolution, decorations,
mail, fly map, map popups, wallpapers, paintings.
