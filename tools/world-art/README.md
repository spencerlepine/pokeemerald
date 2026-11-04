# world-art: new overworld shapes rendered from 3D models

Draws new objects in the Emerald overworld style from small text models: a model is a set of 3D
shapes, and the renderer can only draw it the way the vanilla overworld is drawn. The tile-generator
(`../tile-generator`) re-colours vanilla tilesets; this tool is for shapes vanilla does not have.

**Only approved work lives here**, with one exception: the scenery greyboxes in `models/scenery/`,
which are work in review (below). The owner reviews each object side by side with vanilla before it
comes in. What failed is recorded in `../tile-generator/STYLE.md` section 9, not kept as code.

## Approved so far

| Model | What it proves | Reference |
|---|---|---|
| `models/calibration/hoenn-tree.yaml` | The renderer can reproduce the vanilla Hoenn route tree in vanilla colours. Approved by the owner on 2026-11-02. | `approved/hoenn-tree.png` |

In review: `models/calibration/cone-rock.yaml`, the Route 111 cone rock (Route 111 layout, cells 16-18 by
100-102) built as one low-poly hull. It matches vanilla's outline, size, light and shadow band; the crag
texture is not modelled. It is the reference for every low-poly scenery model.

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

## Scenery greyboxes (owner 2026-11-03)

Every `scenery` row in `../../wiki/mapping/world_art.csv` (wrecks, walkers, fossils, ruins) gets a low-poly
model here: `models/scenery/<id>.yaml`, where `<id>` is the art id without `art:` and with `:` as `_`
(`art:hoth:frozen-at-at` is `hoth_frozen-at-at.yaml`). It is modelled like the real object from the films,
then rendered by the Emerald camera into a grey sprite. Grey only: no colour, outline or texture yet.

- **Shapes for low poly.** Besides the smooth shapes there are three flat-faced ones, each with `round`
  (the soft bevel on every edge, 0.02-0.08 m; more blurs the facets):
  - `hull: {points: [[x,y,z], ...]}`: the convex hull of a few points. Rocks, hulls, heads.
  - `prism: {poly: [[x,y], ...], z: [z0, z1], top: s, lean: [dx, dy]}`: a footprint polygon pushed up,
    its top scaled by `top` (a wedge or a pyramid stump) and shifted by `lean`.
  - `extrude: {axis: x|y, profile: [[a, z], ...], span: [s0, s1], end: s}`: a side profile pushed along
    an axis, its far end scaled by `end` (a fuselage tapering to its nose).
- **Palette** `palettes/greybox.yaml`: four grey ramps (`light`, `mid`, `dark`, `bone`), the ground grey and
  the grey-blue drop shadow vanilla uses. One material per part: `{ramp, bands}`; `bands` are the cuts in
  the light (0-1) between the four tones. Flat tops get about 0.78 of the light, so bands of
  `[0.25, 0.55, 0.85]` put them in the second-lightest tone and `[0.1, 0.45, 0.8]` in the lightest.
- **Drop shadow** `drop_shadow: [{dx, dy, color, below}]`: the outline shifted right and down, painted
  only on empty ground, `below` = in the bottom n cells. **cleanup**: true removes single stray pixels.
- **Size is checked against the wiki.** `cells` must equal the row's `drawn` and `footprint` (bottom rows)
  the depth of its hit box. Drawn rows = plan depth + height, so a tall object needs a shallow plan.
- **What reads at 16 px a metre:** the south face shows whole, east and west faces are edge-on and north
  faces are hidden. Put the parts that identify an object where they show: a TIE's hexagon wing stands up
  facing south (flat on the ground it is a line), a fallen AT-AT's legs point south, not north. A tall light
  part on a mid-grey body (the AAT's pods, the AT-AT's leg plates) reads better than all-light.

```bash
python3 -m worldart scenery hoth_frozen-at-at    # render one (or several, or --all)
python3 -m worldart scenery --status             # every scenery row's model status
python3 -m worldart scenery --set art:hoth:frozen-at-at APPROVED
```

A render writes `output/scenery/<id>/{sprite,review,scene}.png`. `scene.png` is the in-game check: one
15x10-cell screen with a greyed vanilla house, the vanilla cone rock and the player standing south of the
piece, its hit box in red, at 1x and 3x. The sprite and scene are copied to `../../wiki/world/models/`, and
the wiki row gets `model` (the yaml), `model_png`, `model_tiles` (unique 8x8 tiles after flips) and
`model_status`: `TODO` (no model), `IN-PROGRESS` (a model file exists), `IN-REVIEW` (rendered, for the
owner), `APPROVED`. List them with `python3 -m blockout todo --model IN-REVIEW` (in `../blockout`).
None of this goes into `../../game` yet.

## Commands

```bash
cd tools/world-art && pip install -r requirements.txt
python3 -m worldart compare models/calibration/hoenn-tree.yaml   # -> output/compare/hoenn-tree.png: vanilla | ours | ours in the vanilla map
python3 -m worldart render models/calibration/hoenn-tree.yaml    # -> output/hoenn-tree/{sprite.png, review.png, meta.json, indices.npy}
python3 -m worldart budget models/calibration/hoenn-tree.yaml    # unique 8x8 tiles and colours
python3 -m worldart compare models/calibration/cone-rock.yaml    # the low-poly calibration
```

`compare` reads the vanilla map through `../tile-generator` (set `TILEGEN_DIR` to point elsewhere).
Its output for an approved model should match `approved/<name>.png` pixel for pixel.

Not built yet: export of a rendered object into a tileset, colour and texture for the scenery models,
building and interior kits. Each comes back only once something it draws is approved.
