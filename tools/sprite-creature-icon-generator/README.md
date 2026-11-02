# sprite-creature-icon-generator

Companion party and PC box icons (category A3): the small creature that wiggles in the party menu, PC
boxes, day-care, mail and Union Room. **Engine: Python**, no image model. Each icon is made from the
creature's approved battle front in `../../wiki/art/graphics/pokemon/<species>/`.

```sh
python3 icongen.py treecko unown/a --banks palettes --out out   # a few, for review
python3 icongen.py --all --banks palettes --out out             # every icon row in the wiki
python3 palettes.py                                             # refit the 3 shared banks (see below)
```

## How an icon is made

1. Crop `front.png` and frame 2 of `anim_front.png` to the box that holds both.
2. Reduce to fit 30x25 (at most half size). Each icon pixel takes the source colour that best stands for
   its block (the medoid in CIELAB), so colours stay crisp instead of averaging to mud.
3. A little extra saturation and contrast, then a dark 1 px outline on the silhouette edge.
4. Place feet-down at row 30, centred, in a 32x32 cell. Frame 1 is the front; **frame 2 is the creature's own
   second battle pose** (anim_front frame 2) reduced the same way. If that pose barely differs, frame 2 is a
   1 px squash instead.
5. Snap to whichever of the 3 shared icon banks draws it best (`palette-enforcer` `enforce --pal`, then
   `check`). That bank is the species' `gMonIconPaletteIndices` entry.

Castform's icon is drawn from `castform/normal`. The Egg and `question_mark` icons wait for their fronts from
`sprite-creature-extras-generator`. Deoxys's `icon_speed*.png` are not rows (unused in Emerald).

## Palettes

Icons have no palette of their own: each uses one of 3 shared 16-colour banks. The vanilla banks are tuned to
Hoenn's bright colours and draw the new creatures badly, so `palettes.py` fits 3 new banks to all the new
fronts (group species by bank, k-means 15 colours per bank, repeat; index 0 stays the vanilla key green).
The owner chose the fitted banks on 2026-11-02 (about 3x lower colour error than vanilla). They are in
`palettes/` and in the wiki at `art/graphics/pokemon/icon_palettes/`. Every icon is redrawn, so changing the
banks recolours nothing old. Refitting the banks means redrawing every icon.

## Outputs

- `out/graphics/pokemon/<species>/icon.png` (git-ignored), copied to `../../wiki/art/` and listed in
  `../../wiki/mapping/art_ready.csv` (413 rows, ART_READY on 2026-11-02).
- `icon_palette_indices.csv`: species → bank (0-2).

## Install (not done yet)

Copy each `icon.png` and the 3 banks into `../../game/graphics/pokemon/`, and set `gMonIconPaletteIndices` in
`../../game/src/pokemon_icon.c` from `icon_palette_indices.csv` (Unown letters share `SPECIES_UNOWN_*`
entries, all bank of `unown/a` unless the csv differs). Then set `game_status` DONE.
