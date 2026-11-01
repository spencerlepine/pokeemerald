# sprite-trainer-back-generator (player and partner back pics)

**Status: IN REVIEW (round 1).** A repaint tool, like `../sprite-trainer-generator` (its D8):
each back pic starts from a vanilla back pic strip, recoloured and kitbashed on all four frames
at once. Category B2.

| Back pic | Character | Spec | Base |
| --- | --- | --- | --- |
| `brendan.png` | KAEL (player, boy) | `art/kael_back.yaml` | Brendan's own back pic |
| `may.png` | MIRA (player, girl) | `art/mira_back.yaml` | May's own back pic |
| `wally.png` | LUKE SKYWALKER (catching tutorial) | `art/luke_back.yaml` | Wally's own back pic |
| `steven.png` | LEIA ORGANA (multi battle partner) | `art/leia_back.yaml` | Steven's own back pic |
| `brendan_rs.png`, `may_rs.png` | Ruby/Sapphire link-battle leftovers | none yet | |
| `red.png`, `leaf.png` | FireRed leftovers | kept | |

Review sheets: `output/round1-backs.png` (front pic, the four frames, frame 0 in battle) and
`output/round1-throws.gif` (the four throws at game speed).

## Setup

Self-contained (D1): its own package, requirements, decisions, corpus, art and output; it reads
only the game (this repo's `../../game`, or `EMERALD_DIR`).

```bash
pip install -r requirements.txt     # pillow, pyyaml
```

## Commands

```bash
python -m trainer_back_sprite build   art/<name>.yaml [--front x.png]  # strip + previews + lint
python -m trainer_back_sprite verify  art/<name>.yaml                  # gbagfx round trip (8192 bytes)
python -m trainer_back_sprite install art/<name>.yaml                  # over the vanilla strip (+ shared .pal)
python -m trainer_back_sprite inspect <vanilla back png> out.png       # which index is which material
python -m trainer_back_sprite shifts  <vanilla back png>               # how far the head moves per frame
python -m trainer_back_sprite review  out.png [a.yaml ...]             # owner sheet
python -m trainer_back_sprite status                                   # worklist from the wiki
python -m trainer_back_sprite corpus                                   # re-measure the vanilla back pics
```

Previews in `output/<name>/preview/`: `zoom.png` (four frames at 6x with coordinates),
`throw.gif` (game timing), `battle.png` (frame 0 in battle next to the vanilla pic, 2x and
1x), `pair.png` (front pic and back frames in the shared palette), `showcase.png` (all of it).

## Format (what the game needs)

- `graphics/trainers/back_pics/<name>.png`: 64x256 indexed, four 64x64 frames stacked, built
  with `INCGFX_U8(png, ".4bpp")` (uncompressed, 8192 bytes). `back_pic_anims.h` plays
  0 (24 ticks), 1 (9), 2 (24), 0 (9), 3 (50): idle, wind-up, throw, idle, follow-through.
  Red and Leaf are 5 frames (64x320) and are kept.
- **The palette is the front pic's** (D3). `back_pic_tables.h` loads `gTrainerPalette_Brendan`
  etc.: `graphics/trainers/palettes/{brendan,may,wally}.pal`, and for Steven his front pic PNG.
  The back pic's own PNG palette is ignored. So front and back of one character use the same
  16 colours *index for index*: copy the front spec's `palette:` and `legend:` into the back
  spec. `build` errors if they differ from the paired front pic (`front:` in the spec or
  `--front`).
- Shown at centre (80, 80) in battle, under the text box from row 112.

## Drawing a back pic (repaint)

1. The front pic comes first (`../sprite-trainer-generator`): it fixes the palette and the look.
2. `inspect` the vanilla strip; `shifts` it: every vanilla back pic is one head drawing moved
   per frame (Brendan +5,+1 / -6,+2 / +4,-1), so a head edit is written once with a `shift:`.
3. Write `art/<name>_back.yaml`: the front's `palette` and `legend`, `repaint: {pic, remap}`
   (one remap for all frames; map whole ramps to whole ramps), then `layers:` from the front
   tool's rig (`erase`, `recolour`, shaded shapes, `pixels`, `edge`, and the silhouette ops
   `graft`, `move`, `rows`, `cols`, `trim`, `fringe`, `speckle`; reference: the docstring in
   `trainer_back_sprite/rig.py`). Each layer runs on every frame unless it has `frames: [..]`;
   `shift: {frame: [dx, dy]}` moves it on the frames where the body moved. `patches:` per frame
   for single pixels.
4. `build`, look at `zoom.png` and `throw.gif`, fix, `verify`, then a `review` sheet.

## Known gaps

- Bodies and poses are the four vanilla throws; only heads, hair, clothes and props change.
- `dark_outline` warns on Luke: Wally's vanilla pic uses selective (non-black) outlines too.
