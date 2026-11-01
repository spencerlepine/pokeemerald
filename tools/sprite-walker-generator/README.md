# sprite-walker-generator (overworld walkers)

**Status: READY** for the 16x32 people kit (category B3). Other kits (32x32 big, 16x16 small,
bike/surf/fishing/field-move sheets, creature walkers A6, dolls/cushions C4) are not built.

Reference: `art/vader.yaml` -> `output/vader/` (approved, helmet variant A).

## Setup

This folder is a self-contained tool: its own Python package, requirements, decision log,
corpus, art and output. It needs nothing outside this folder except the game (this repo's `../../game`).

```bash
# from this folder
pip install -r requirements.txt     # pillow, pyyaml
# the game is found automatically: this repo's game/ folder (pokeemerald/tools/<tool> ->
# pokeemerald/game). Set EMERALD_DIR only to point at a different checkout.
# export EMERALD_DIR=/path/to/pokeemerald/game
```

| Path | What |
| --- | --- |
| `walker_sprite/` | The Python package (`python -m walker_sprite ...`) |
| `art/<name>.yaml` | Walker specs: what the LLM writes |
| `art/retired/` | Specs of walkers whose character was recast (wiki/bible/RECAST.md). Kept for reuse only: their art was deleted from the wiki and the slots are PENDING_ART again, so never install these |
| `output/<name>/` | Built game-ready PNG, `lint.txt`, `metrics.json`, `preview/` (zoom, walk.gif, scene, showcase) |
| `palettes/` | Copies of Emerald's four shared NPC palettes (D6) |
| `corpus/people16x32.json` | Style metrics measured on the 90 vanilla 16x32 walkers (`python -m walker_sprite corpus`) |

`D1`, `D2`... are the decisions in this folder's [DECISIONS.md](DECISIONS.md): read it before changing
the tool.

## Commands

```bash
python -m walker_sprite build   art/<name>.yaml               # PNG + previews + lint
python -m walker_sprite verify  art/<name>.yaml               # round trip through pokeemerald's gbagfx
python -m walker_sprite install art/<name>.yaml               # copy into pokeemerald, set the palette tag
python -m walker_sprite compare output/<x>.png a.yaml b.yaml  # variant review sheet
python -m walker_sprite lint    <any_sheet.png>               # lint an existing sheet
python -m walker_sprite corpus                                # re-measure vanilla walkers
```

## Spec

`kit: person16x32` (the default), `palette: npc_1..4`, `replaces:`, `graphics_info:`,
`palette_tag:`, `legend:` (one character -> one palette index), and the nine frames
`down up left down_a down_b up_a up_b left_a left_b`. A frame is a 16-wide grid
(bottom-anchored), `half:` (left half, mirrored, optional `mirror_shade`), `base:` + `shift` +
`patch_y`/`rows` (D4), or `mirror_of:`; any of them plus `patches:`.

Kits (`kit:`), one per sheet layout Emerald uses for one-tile objects:

| Kit | Sheet | Frames | Used by |
|---|---|---|---|
| `person16x32` | 144x32 | the nine above | most people, Kirlia, Mew, Dusclops |
| `person16x32_still` | 48x32 | down, up, left | gym leaders, Elite Four, Sudowoodo |
| `person16x32_bow` | 64x32 | down, up, left, bow | the Pokemon Center nurse |
| `person16x32_single` | 16x32 | down | the player decorating a secret base |
| `person16x16` | 144x16 | the nine above | little kids, tubers, ninja boy |
| `person16x16_still` | 48x16 | down, up, left | small overworld Pokemon (Pikachu, Skitty...) |
| `flyer16x16` | 96x16 | down, down_a, up, up_a, left, left_a | Wingull (one flap frame per facing) |
| `person32x32` | 288x32 | the nine above | bikes, big Pokemon (not used yet) |

The style score was measured on 16x32 people; for other kits compare with the vanilla score that
`lint.txt` prints under the report. `palettes/kael.pal` and `palettes/mira.pal` are the player
palettes in NPC index order (the vanilla player palettes use another layout).

## Format (what the game needs)

| Fact | Value | Source |
| --- | --- | --- |
| Sheet | 144x32 PNG = 9 frames of 16x32, side by side | `graphics/object_events/pics/people/**` (90 vanilla sheets) |
| Frame order | 0 face down, 1 face up, 2 face left, 3-4 walk down, 5-6 walk up, 7-8 walk left | `sPicTable_*` + `sAnimTable_Standard` |
| East | Frames 2/7/8 drawn with `hFlip`; there is no right-facing art | `sAnim_GoEast` in `object_event_anims.h` |
| Walk cycle | step A, stand, step B, stand; 8 ticks per frame at normal speed | `sAnim_GoSouth` etc. |
| Palette | **Shared**: one of four NPC palettes (`npc_1..4.pal`) for ~107 sprites. Indices 1-4 are the same skin ramp in all four | `graphics/object_events/palettes/`, `.paletteTag` in `object_event_graphics_info.h` |
| Slot | `.paletteTag` and `.paletteSlot` must agree (`OBJ_EVENT_PAL_TAG_NPC_4` + `PALSLOT_NPC_4`) | same |
| Size | `.size = 256` bytes per frame (16x32 at 4bpp) | same |

Measured style of the 90 vanilla sheets (`corpus/people16x32.json`, rebuilt with
`python -m walker_sprite corpus`): art starts on row 10-13 and stands on row 30, is 18-21 px
tall and 14-16 px wide, ~226 opaque pixels, 10-15 colours, outlined in near-black on almost
every edge pixel, and a step frame changes ~70% of pixels (the whole body bobs 1 px plus legs
and arms).

### Rules for all GBA 4bpp art

- The game builds from **indexed PNGs** (mode `P`) via pokeemerald's `tools/gbagfx`, which
  reads pixel *indices*; the colours on screen come from the palette the game loads.
- Max 16 colours per palette, index 0 is transparent.
- GBA colour is 15-bit: each channel keeps 5 bits (`v >> 3 << 3`). Colours that differ only in
  the low 3 bits look identical in game, so use multiples of 8.
- Sizes are multiples of 8 (tiles are 8x8).
- Replacing a PNG at the same path needs no code change; a new asset needs C table entries.

### Palette gate (required: [`../PALETTES.md`](../PALETTES.md))

`build` runs the shared [`palette-enforcer`](../palette-enforcer/) check on the sheet and lists its errors and
warnings in `lint.txt`; `install` refuses a sheet that fails it. The sheet must use the locked NPC/player bank
named in `palette:` index for index (an inline `palette:` list is new art and must sit on GBA steps). Add
`theme: <id>` (a theme or group from `../../wiki/bible/PALETTE.md`, e.g. `imperial-order`) to a spec to see how
far the bank is from the character's faction; it is a warning only, because a shared bank cannot follow every
faction. Giving a faction its own walker bank is an owner decision (a new palette tag).

## Making a walker (read STYLE.md first)

The owner rejected the first hand-drawn batches: black outlines, flat ramps, no top-down
perspective ("they look nothing alike, the Pokémon one is way better"). `STYLE.md` measures what
Emerald does; the tool now scores every build against it and the LLM iterates **until the score
passes before a human sees anything**.

1. Find the row in `../../wiki/database/pending_art.csv` (`kind = object_events`): the vanilla
   file it replaces and the Star Wars brief (`sw_subject`).
2. **Compose, don't redraw.** Open `corpus/parts.png` (all 90 vanilla walkers with palette and
   head rows; `python -m walker_sprite parts` rebuilds it). Start the spec from the vanilla sheet
   the row replaces (`base_sheet:`), move it to the NPC palette whose ramps have the right colours
   (`palette:` / `palette_tag:`), remap ramps (`recolor:`), borrow a head or body from another
   vanilla sheet (`parts:`), and patch in only what is new (props, insignia, goggles) with
   coloured outlines and full ramps (`frames.<name>.patches`, repeated one row lower on the two
   step frames). `batches/batch1.py` is the worked example.
3. Draw from scratch only when no vanilla silhouette fits (droids, Hutts, Yoda, Vader). Then
   follow STYLE.md literally: outline each material in its dark ramp tone, all four skin tones,
   hair/hat rows above the eyes, dark tone at the bottom of every shape.
4. `python -m walker_sprite build art/<name>.yaml`. Read the **STYLE SCORE** block: every FAIL
   names the rule and the fix. Also read `output/<name>/preview/showcase.png`. Fix, rebuild,
   repeat. Gate: score >= 90, no FAIL that the vanilla sheet itself does not have (the report
   prints the vanilla sheet's score), and the round trip in `verify` identical.
5. `python -m walker_sprite review output/<batch>-review.png art/a.yaml ...` makes the sheet the
   owner reviews: each new walker beside the vanilla sheet it replaces, plus an in-game lineup
   (vanilla group vs new group) at 1x and 3x. Only then show the owner, in batches of five.
6. On approval: copy the PNG to `../../wiki/art/<game path>`, add the row to
   `../../wiki/mapping/art_ready.csv`, run `python3 ../../wiki/tools/mark_art_ready.py`.

### Shade mode (D13): draw regions, let the tool pick the tones

```yaml
shade: true
materials: {g: skin-b, G: b, c: "c!", w: w/c}   # letter -> ramp; distinct letters = distinct volumes
legend: {k: 15, W: 14}                         # hard pixels only (eyes, lights, wisps)
base_sheet: graphics/object_events/pics/people/fat_man.png   # optional: a vanilla body as regions
remap: {s: h, b: w, c: b}                      # rename the vanilla body's letters
frames: ...                                    # rows of letters; patches work the same way
```

Material forms: `s a b c` (3-tone ramp, shaded like vanilla cloth/hair; `s` like a face),
`skin-b` (ramp b shaded like a face: bald alien heads), `w` / `k` (flat white / black),
`w/c` (white edged in ramp c's dark tone), and a trailing `!` (`c!`) to shade that letter by the
volume rules instead of the learned table (flat robes, aprons, plating). `python -m walker_sprite
regions <sheet.png>` prints any sheet as letters; `shader` relearns the table from the game and
writes `corpus/shader-check.png` (vanilla over re-shaded) to judge it by eye.

### Commands added for this loop

```bash
python -m walker_sprite parts                                   # corpus/parts.{json,png}: vanilla catalogue
python -m walker_sprite review out.png art/a.yaml art/b.yaml    # owner review sheet vs vanilla
python -m walker_sprite lint <sheet.png>                        # style score of any sheet (vanilla too)
```

## Drafting in batches

A batch file in `batches/` writes `art/<name>.yaml` for a few rows at a time from `base_sheet` +
`recolor` + `parts` + patches, or from regions in shade mode (so the step-frame offsets are
generated, not hand-copied). Run it
from this folder (`python batches/batch1.py`), build each spec, then `review`.
