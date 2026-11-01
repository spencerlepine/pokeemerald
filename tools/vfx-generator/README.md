# vfx-generator

**Status: RESET (2026-11-01).** The drawing pipeline works end to end (catalog, drawing, palette gate, style
score, previews, gbagfx round trip, real-ROM filming), but the owner rejected prop swaps: an effect is a
storyboard (script + art + sound), not a sticker. The design is in
[`../../wiki/bible/MOVE_EFFECTS.md`](../../wiki/bible/MOVE_EFFECTS.md); this tool grows a script layer next
(section 5 there). Kept art: ION CANNON orb, CREDIT TOSS chips, TURBOLASER beam (`art/`). Rejected specs are in
`art/rejected/`. The audit of what needs drawing is in [`TODO.md`](TODO.md); the measured style is in
[`STYLE.md`](STYLE.md).

Pure Python (pillow, numpy, pyyaml) plus the shared [`palette-enforcer`](../palette-enforcer/). No model,
no GPU: effects are built from pixel-art primitives (glows, beams, bolts, slashes, starbursts, rings,
sparks), hand-placed pixel grids with automatic volume shading, and vanilla frames recoloured. Everything
lands on a known palette index, so the output is game-legal by construction.

```bash
cd tools/vfx-generator
pip install -r requirements.txt
python -m vfx catalog                     # re-read the game source -> corpus/catalog.json (6 s)
python -m vfx corpus                      # measure the vanilla style -> corpus/style.json
python -m vfx show coin --card            # the contract of a vanilla sheet
python -m vfx build art/ion_cannon.yaml   # sheet + gate + STYLE SCORE + previews -> output/ion_cannon/
python -m vfx verify art/ion_cannon.yaml  # round trip through the game's own gbagfx
python -m vfx romtest art/ion_cannon.yaml # scratch ROM, film the move in a real battle (~4 min)
python -m vfx review output/review.png art/*.yaml
python -m vfx install art/ion_cannon.yaml [--to game] [--mark-ready]
```

## What each command knows

**`catalog`** reads `src/graphics.c`, `src/data/battle_anim.h`, every `SpriteTemplate`, `OamData` and
`AnimCmd` in `src/`, `data/battle_anim_scripts.s`, `graphics_file_rules.mk` and the field-effect tables,
and records for every VFX PNG (464 of them):

- sheet size, bit depth, tile order (`-mwidth/-mheight`), concatenated parts (`ice_cube_0..3`);
- frame size (from the OAM shape of the templates that use it), frame slots, and **the slots the game
  actually plays** (from the anim tables: PAY DAY only ever shows coin slot 2);
- the palette contract: own, from another file, **shared with another tag** (`sprites/pokeball` with
  `ANIM_TAG_SPOTLIGHT`), **set by code** (the Fly bird draws with the player's bank), and every script line
  or C call that blends/flashes it at runtime;
- every move / general / status animation that loads it, and the wiki row.

**`show`** prints that contract. **`build`** draws the spec, runs the palette gate, scores the style,
writes `output/<name>/`:

| File | What |
|---|---|
| `<vanilla name>.png` | the game-ready indexed sheet, same path name as the file it replaces |
| `build.json`, `lint.txt`, `metrics.json` | palette, ramps, notes, gate result, style score |
| `sheet.png` | vanilla vs new sheet at 6x, frame slots numbered (`*` = played by the game), palette |
| `battle.gif`, `battle_strip.png` | vanilla vs new over a real battle scene (battle environment tiles, real creature pics at their in-game coordinates) |
| `overworld.gif`, `overworld_still.png` | field effects over a real map (tile-generator's map renderer), under both player palettes when the sheet uses the player bank |
| `rom/rom.gif`, `rom/rom_strip.png`, `rom/report.txt` | from `romtest`: vanilla ROM vs new ROM, frame-aligned |

**`romtest`** copies the game twice to `/var/tmp/vfx-romtest` (vanilla, and with the sheets installed),
sets the test move's accuracy to 255 so it cannot miss (scratch copy only; 0 means always miss in this engine), boots each ROM headless in mGBA, gets a party member
that knows the move, walks into Route 101 grass, uses the move and films every 2nd frame. Identical
inputs make the runs frame-aligned, so the frames where they differ are exactly where the new art is on
screen. Needs the play-tester setup (`../play-tester/scripts/setup-ubuntu.sh`).

## Spec (`art/<name>.yaml`)

```yaml
name: ion_cannon
title: ION CANNON orb
row: anim:Move_ZAP_CANNON              # the wiki row
bucket: NEW                            # NEW / RESKIN / MATCH TILESET (from TODO.md)
replaces: graphics/battle_anims/sprites/black_ball_2.png   # or new: {path, size, frame}
brief: ...                             # what it should look like (the Star Wars subject)
theme: [kyber-gold]                    # wiki themes: off-theme colours are warnings
palette:
  mode: new                            # new (ramps as hex) | locked (keep a .pal/PNG bank) | vanilla
  transparent: "#A09088"
  ramps: {ion: ["#F8F8F8", "#B8F0F8", "#58C8F8", "#2878D8", "#183888"]}   # light -> dark
  # locked: source: graphics/object_events/palettes/brendan.pal, ramps: {hull: [14, 9, 5, 6]}
frames: [0, 1, 2, 3]                   # slots to draw (default: all)
vars: {turn: "=[0.3, 0.6, 1, 1][i]"}   # per-frame expressions
ops: [...]                             # drawn on every frame
frame_ops: {2: [...]}                  # drawn on one frame (by drawing position)
preview:
  scene: battle                        # battle | overworld
  env: tall_grass                      # battle environment; attacker/target species
  motion: {kind: projectile, frames: 30, arc: 0, spin: 0, count: 1, dim: 0}
  # kinds: projectile, stream (HYPER BEAM), burst, at_target, at_attacker, still; overworld: fly_in, fly_across, still
romtest: {move: MOVE_ZAP_CANNON, species: 280, capture: 900, hp: 0.5, tap_until: 660}   # hp: healing moves fail at full HP; tap_until: film a 2nd turn (SKETCH)
lint_allow: [lone]                     # style rules this effect breaks on purpose
```

Numbers anywhere in an op can be expressions (`"=3 + 4*t"`): `t` (0..1 over the frames), `i`, `n`,
`W`, `H`, `cx`, `cy`, the `vars`, `sin cos pi sqrt clamp lerp rnd(k)`.

### Ops

| Op | Draws |
|---|---|
| `disc` `{cx, cy, r, light: [dx, dy], falloff}` | glow or sphere; value 1 at the centre or the light point |
| `ellipse` `{cx, cy, rx, ry, angle}` | |
| `ring` `{cx, cy, r, thick, bright: center/inner/outer}` | shockwaves, halos |
| `beam` `{x0, y0, x1, y1, r0, r1}` | tapered capsule: blaster bolts, beams |
| `bolt` `{x0, y0, x1, y1, segments, amp, seed, r0, branches}` | lightning |
| `path` `{points, r0, r1}` | any polyline |
| `crescent` `{cx, cy, r, thick, a0, a1, bright}` | slash arcs |
| `star` `{cx, cy, r_in, r_out, points, rot, jitter}` | impact starbursts |
| `polygon`, `rect` | |
| `sparks` `{n, seed, cx, cy, r \| x, y, w, h, shape: dot/plus/cross/diamond}` | |
| `grid` `{x, y, rows, legend: {ch: ref}, shade: {ch: ramp}, light}` | hand-placed pixels; `shade` letters are lit as one volume |
| `vanilla` `{path, frame, luma: ramp \| remap: {old: new}}` | start from a vanilla frame |
| `copy` `{frame, dx, dy, flipx, scalex, rotate}` | reuse a frame drawn earlier |
| `transform`, `recolor`, `outline`, `selout {light}`, `despeckle` | post-process the frame |
| `python` `{module, func, args}` | escape hatch: a function `(canvas, ctx)` in `art/` |

Paint options on every shape: `ramp` (or `index`), `bands` (hot to cold thresholds), `offset`, `mode`
(`over`, `under`, `lighten`, `darken`, `erase`), `dither`.

## Making one (the loop)

1. Pick a row from `TODO.md`. `python -m vfx show <sheet> --card`: read the frame slots the game plays,
   the palette contract and every move that uses the sheet.
2. Write `art/<name>.yaml`. For a RESKIN copy the vanilla frame's footprint; for an effect start from
   the closest vanilla sheet (`vanilla: {luma: ramp}`) or from primitives.
3. `python -m vfx build`. Read `lint.txt` (gate PASS, STYLE SCORE >= 90, no WARNING notes) and look at
   `battle_strip.png` or `overworld_still.png`, not just the sheet. Iterate.
4. `python -m vfx verify` (gbagfx round trip identical) and, for in-place sheets, `python -m vfx romtest`.
5. Owner review: `python -m vfx review output/<batch>.png art/a.yaml ...`.
6. On approval: `python -m vfx install art/<name>.yaml --mark-ready` (copies to `../../wiki/art/<path>`
   and adds the `art_ready.csv` row), then `python3 ../../wiki/tools/mark_art_ready.py`. Port into
   `game/` with `--to game`.

## Porting a NEW sheet

In-place sheets (RESKIN, and NEW effects whose vanilla sheet only that move uses, like ION CANNON) need no
code. A NEW sheet that must not overwrite a shared vanilla sheet (TURBOLASER, VIBROBLADE, FORCE BOLT...)
needs: the PNG under `graphics/battle_anims/sprites/`, `gBattleAnimSpriteGfx_X` / `gBattleAnimSpritePal_X`
in `src/graphics.c`, an `ANIM_TAG_X` (or reuse one of the 104 never-loaded tags listed in `TODO.md`, which
needs no new constant), rows in `gBattleAnimPicTable` / `gBattleAnimPaletteTable`, a `SpriteTemplate`, and
the move's script pointing at it. Not automated yet.

## Palette (required: [`../PALETTES.md`](../PALETTES.md))

- **Layer 1:** 4bpp OBJ sheets. The palette mode follows the catalog: `new` only for sheets with their own
  unshared palette; `locked` for shared tags, `.pal` banks (field effects) and code-set banks (the player
  bank for the Fly bird). `build` warns when a spec's mode contradicts the contract.
- **Layer 2:** lightsabers and blasters from the faction themes (`Saber Blue`, `Saber Red`, `Signal Red`),
  Kyber Blue for ion/Force energy, Console Green for turbolasers, weather from the planet theme.
- **Gate:** every build runs `palette-enforcer` `check` (with `--pal` for locked banks); `install`
  refuses a sheet that fails it.

## Layout

| Path | What |
|---|---|
| `vfx/` | the package: `catalog`, `sheet` (tile model), `pal` (ramps), `draw` (primitives), `ops` (spec ops), `spec`, `lint`, `preview`, `pipeline`, `romtest`, `cli` |
| `art/` | specs |
| `output/` | built sheets and review material (committed) |
| `corpus/` | `catalog.json`, `style.json` (generated) |
