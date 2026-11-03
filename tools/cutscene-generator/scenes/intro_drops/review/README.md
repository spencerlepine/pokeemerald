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

## Round 2 (2026-11-01): the drip source redrawn as a desert succulent

Owner: the rock overhang read as a brown leaf, which makes no sense in a desert ("we need to actually draw
something that makes logical sense"). Two mockups (`round2_mockups.png`): A, a moisture vaporator's drain pipe
from a farm on the rim, and B, a desert succulent on the rim beside the spring. The owner picked B.

- BG0 now uses its own palette bank 4 (canyon rock 1-9 as bank 3, sage greens 10-15): flat-topped rim ledges at
  both edges, an agave-like plant on each, and the right plant's long leaf follows the big drop's traced path
  down to the tip at (120, 80). Drop 1 falls from the left plant's drooping leaf at (48, 40), drop 2 from a
  leaf tooth at (196, 50).
- The GAME FREAK logo is back (owner: "restore the game freak logo during the transition, we should just keep it").
- `round2_succulent_rom.gif` (frames 250-1300 every 3rd, real speed) and `round2_succulent_sheet.png`.

## Round 3 (2026-11-03): a dry canyon, no water and no plants

Owner: Tatooine is rocky and sandy, with no water or plants here. Keep the ground and the backdrop, then the
pan to the skyline, and keep the music exactly as it is.

- BG1: the pool and its wet basin are gone. The canyon floor is now a dry sandy wash in the shade: talus at the
  foot of the walls, wind ripples, a few half-sunk boulders and grit. Bank 3 entries 11-13 (the water) are sand.
- BG0: both succulents and the drip spine are gone; the rock ledges at the top corners and the dark floor rim
  stay. BG0 now shares bank 3 with BG1 (bank 4 is unused).
- `src/intro.c`: the big drop, the two small drops (and their ripples) and the sparkles are no longer created.
  The GAME FREAK logo, every timer and `MUS_INTRO` are unchanged, so the pan starts on the same beat.
- `round3_rom.gif` (frames 250-1300 every 3rd, real speed) and `round3_sheet.png`.
