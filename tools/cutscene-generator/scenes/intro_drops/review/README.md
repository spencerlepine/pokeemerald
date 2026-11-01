# intro_drops review captures (intro scene 1)

## Round 1 (2026-11-01): APPROVED, shipped ("perfect ship it!")

Emerald's leaf drips, GAME FREAK logo and jungle pan become: condensation dripping off canyon rock into a
shadowed pool before dawn, then the camera rises past the canyon walls, a boulder field and a dune crest to the
twin suns over the flats, and a transport ship flies off. No logo (owner's call: "No logo, just the drip").

- `round1_rom.gif`: the real ROM, game frames 250-1300 every 3rd frame at 20 fps, so it plays at true speed
  (`scripts/rom-capture.sh <out> 250 1300 3`). Scene 2 starts at the very end.
- `round1_sheet.png`: every 90th game frame.
- `round1_layers.png`: the four BG layers (BG3 sky, BG2 dune and boulders, BG1 canyon and pool, BG0 overhangs).

Code changes in `game/src/intro.c`: the GAME FREAK logo sprites and their blend tasks are gone; drop 2 now falls
from the rock tooth at (196, 10) instead of (200, 60). The drops and ripples are recolored (drops.pal) from leaf
green to clear blue. The big drop's slide path was traced from the ROM and the right overhang follows it.
