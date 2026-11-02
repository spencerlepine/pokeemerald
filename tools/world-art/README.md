# world-art: new overworld shapes rendered from 3D models

Draws new objects in the Emerald overworld style from small text models: a model is a set of 3D
shapes, and the renderer can only draw it the way the vanilla overworld is drawn. The tile-generator
(`../tile-generator`) re-colours vanilla tilesets; this tool is for shapes vanilla does not have.

**Only approved work lives here.** The owner reviews each object side by side with vanilla before it
comes in. What failed is recorded in `../tile-generator/STYLE.md` section 9, not kept as code.

## Approved so far

| Model | What it proves | Reference |
|---|---|---|
| `models/calibration/hoenn-tree.yaml` | The renderer can reproduce the vanilla Hoenn route tree in vanilla colours. Approved by the owner on 2026-11-02. | `approved/hoenn-tree.png` |

Next to calibrate: the Fortree tree house (vanilla Fortree metatiles 548-598). After that, new Endor
objects for Bright Tree Village, then a mockup that swaps them into Fortree.

## How the approved tree is built

- **Camera** (`worldart/render.py`): ground in plan, south faces head-on, east/west faces edge-on,
  16 px per metre and per cell. Rays travel north and down at 45 degrees.
- **Shapes** (`worldart/model.py`, `sdf.py`): ellipsoids, cones, flat-capped cylinders and boxes,
  combined as signed-distance fields. The file format and generators are ported from the z-day object
  generator (`spencerlepine/z-day`, `.claude/tools/art/world/props/objgen`).
- **Leaf clumps** (`lobes` generator): the crown is about 20 small ellipsoids on a crown-shaped shell,
  each its own group. Each clump is cel-shaded as a small sphere, and a dark line is drawn wherever one
  clump stands in front of another (`inner_lines: black`, `depth_jump`). This is what makes it read
  like vanilla. Painted leaf patterns on a smooth crown did not.
- **Tones** (`shares`): the crown's tone cuts are set so each tone covers about the same share of the
  crown as in vanilla, darkest first.
- **Ground** (`ground_shadow`): ellipses drawn only on empty pixels, outermost first. These are the
  ground-shade halo on the grass and the dark crown-shadow ellipse holding the trunk stub.
- **Colours**: every colour comes from `palettes/<name>.yaml`. The tree uses 8 vanilla colours.

## Commands

```bash
cd tools/world-art && pip install -r requirements.txt
python3 -m worldart compare models/calibration/hoenn-tree.yaml   # -> output/compare/hoenn-tree.png: vanilla | ours | ours in the vanilla map
python3 -m worldart render models/calibration/hoenn-tree.yaml    # -> output/hoenn-tree/{sprite.png, review.png, meta.json, indices.npy}
python3 -m worldart budget models/calibration/hoenn-tree.yaml    # unique 8x8 tiles and colours
```

`compare` reads the vanilla map through `../tile-generator` (set `TILEGEN_DIR` to point elsewhere).
Its output for an approved model should match `approved/<name>.png` pixel for pixel.

Not built yet: export of a rendered object into a tileset, a scene mockup tool, building and interior
kits. Each comes back only once something it draws is approved.
