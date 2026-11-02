# world-art checklist (the resumable plan)

Owner direction (2026-11-02): build the tools first, one area end to end, then expand. Prototype,
mock up, combine the tools in one scene, keep the top-down projection / silhouettes / cel shading
exact; the palette is calibrated last. Commit and push at every checkpoint.

Status marks: `[ ]` not started, `[~]` in progress, `[x]` done, `[r]` waiting for the owner's review.

## Second pass (2026-11-02): calibrate against vanilla first

Owner review of the first pass: sprites cropped, objects did not share one structure, the mockup did
not look like a game, and vanilla trees/terrain were left in place. New rule: **before drawing a new
object, the tool must reproduce the vanilla object it replaces** (`python -m worldart compare
models/calibration/<x>.yaml`: vanilla | ours | ours swapped into the vanilla map). Only when the swap
is hard to spot do we draw the Star Wars version on the same structure (same cells, ramps, outline,
swatches), and then replace vanilla art from scratch.

Lessons measured so far (keep adding):
- Vanilla trees are 2x2, crown ~30x22 px filling the cell width (they tile; no margin), left/right
  mirrored, leaf scales ~5x4 px in fans from the top centre, a dark crown-shadow ellipse holding a
  short grey trunk stub, a mid-green rim and a ground-shade halo. -> `texture: fan`, `ground_shadow`.
- Buildings are pattern-driven flat faces: the look is the swatch (logs: 8-row period, 3 lit rows +
  shadow line, knots), not the lighting. -> `swatch:` per face (south/top/side) in palette files.
- Buildings share one slate outline (#4a4a5a), not the material's darkest tone. -> `outline_shared`.
- A material is decided per pixel from the surface that owns it (fixed: two materials sharing
  colours lost their swatch).

| Calibration | Model | Status |
|---|---|---|
| Hoenn route tree (General 468/469/476/477) | `models/calibration/hoenn-tree.yaml` | [~] close at 3x in the map; leaf highlights still too even |
| Fortree tree house (Fortree 548-598) | `models/calibration/fortree-house.yaml` | [~] logs, walls, door, frond roof right; roof must cover the wall tops, door frame/shutters, log ends, ladder |
| Fortree forest tree (dense tiling canopy) | | [ ] |
| Rope bridge (Fortree) | | [ ] |
| A Hoenn house (Littleroot) | | [ ] |

## Tools

- [x] Package scaffold, model loader (ported from z-day objgen), palettes per planet
- [x] Emerald-camera SDF renderer: projection, bands, dither, AO, outlines, textures, drop shadow
- [x] Review sheet (1x / 3x / 6x grid), tile + colour budget
- [~] Look pass against vanilla (bark ridges, canopy scallops, outline weight) on the redwood
- [x] Scene mockup (`scene.py`): planet ground + paths + placed objects, back to front, 1x and 3x; or a real layout through a tile-generator recipe with `clear:` rects
- [~] Buildings: `cylinder` (flat-capped) parts, `op: subtract` door recess, `rows`/`plank` textures; still to do: windows, flat and gable roofs, storey bands, square-plan houses
- [~] Walkable pieces: the rope bridge cell; platforms as part of the hut so far
- [ ] Metatile export: bottom/top layers + ground underlay, attributes, append to a planet secondary (with tile-generator `install`)
- [ ] Interiors (room kits), later

## Area 1: Bright Tree Village (Endor, vanilla Fortree City, 40x20)

Catalogue rows: `wiki/mapping/world_art.csv` planet ENDOR. Concept art: `wiki/art/concept/endor/`.

| Concept | Model | Status |
|---|---|---|
| redwood-trunk (3x4, edge) | `models/endor/redwood-trunk.yaml` | [r] in the mockup |
| fern-undergrowth (1x1, walkable) | `models/endor/fern-undergrowth.yaml` | [~] reads as noise at 1x; STYLE lesson says keep the recoloured vanilla tall grass for walkable grass. Decide with the owner |
| fallen-log (3x1, edge) | `models/endor/fallen-log.yaml` | [r] in the mockup |
| ewok-hut (3x4, landmark) on a stilt platform | `models/endor/ewok-hut.yaml` | [r] in the mockup; next: ladder cell, a porch row the player stands on |
| rope-bridge (1x1, walkable) | `models/endor/rope-bridge.yaml` | [r] in the mockup |
| totem-and-drum (1x2, noise) | | [ ] |
| ewok-glider (1x2, noise) | | [ ] |
| ladder (1x1, walkable) | `models/endor/ladder.yaml` | [r] in the Fortree mockup |
| imperial-bunker (6x5, landmark) | `models/endor/imperial-bunker.yaml` | [r] first box building: door recess, rim, dish, `panels` texture |
| log-trap (3x1), crashed-speeder-bike (2x1), at-st-wreck (3x3) | | [ ] route props, after the village |
| scene `bright-tree-village.yaml` | `scenes/bright-tree-village.yaml` | [r] first mockup, 22x12 cells on flat ground |
| scene `fortree-endor.yaml` | `scenes/fortree-endor.yaml` | [r] the real Fortree layout through the Endor recipe, vanilla houses cleared, new objects placed |

## Later areas (same order of work per area)

Kachirho (Kashyyyk), Tatooine towns, Sullust, Hoth, Dagobah, Kamino, Death Star, Grand Arena: see
`wiki/mapping/world_art.csv`.
