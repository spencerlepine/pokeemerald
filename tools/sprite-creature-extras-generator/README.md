# sprite-creature-extras-generator

The creature sprites that are not a species (category A5 plus the `egg/` and `question_mark/` pics):
the Companion Egg, the question-mark placeholders and Wobblekit's (Spinda's) spot masks. **Engine: Python**,
no image model.

```sh
python3 extras.py --out out                 # everything (Egg in the chosen scheme)
python3 extras.py --egg jungle --out out    # another Egg scheme: dune (default), kyber, jungle
python3 extras.py --egg-options eggs.png    # every Egg scheme side by side
```

## What it makes

| Files | How |
|---|---|
| `egg/front.png`, `anim_front.png`, `hatch.png`, `shard.png`, `normal.pal` | Vanilla's pixels kept (the hatch cracks and shell shards line up with the hatching code), new `normal.pal`. The `dune` scheme: a sand-coloured leathery shell with rust mottling, like a krayt or dewback egg. |
| `egg/icon.png` | The vanilla Egg icon recoloured the same way, snapped to the fitted shared icon banks (bank 1). |
| `question_mark/circled/*`, `double/*` (front, anim_front, back, normal.pal, shiny.pal) | Vanilla's pixels kept, recoloured as a blue "no data" hologram (shiny: amber). |
| `question_mark/icon.png` | The same hologram recolour, bank 0. |
| `spinda/spots/spot_0-3.png` | Redrawn 16x16 1-bit round patches. The game paints a spot only on front pixels with index 1-3 (Wobblekit's light fur and face) and shifts it 0-15 px by personality, from bases (16,7), (40,8), (22,25), (34,26) in `src/pokemon.c`. Big patch for the face, smaller for the ear and the chest and hands. |

The `question_mark/footprint.png` placeholder print is kept vanilla. Every PNG goes through
`palette-enforcer` `check` (4bpp on its bank; the spots 1bpp).

## Outputs

`out/graphics/pokemon/...` (git-ignored), copied to `../../wiki/art/` and listed in
`../../wiki/mapping/art_ready.csv` (16 rows, ART_READY on 2026-11-02). The Egg and placeholder icon banks are in
`../sprite-creature-icon-generator/icon_palette_indices.csv`.

## Install (not done yet)

Copy the files into `../../game/graphics/pokemon/`. No code changes: `gMonIconPaletteIndices[SPECIES_EGG]` is
already 1, the placeholders' entry 0. Then set `game_status` DONE.
