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

Every row in `../../wiki/mapping/world_art.csv` gets a low-poly model here: `scenery` rows (wrecks, walkers,
fossils, ruins) in `models/scenery/<id>.yaml`, every other category (buildings, objects, nature, landmarks,
interior props and rooms) in `models/world/<id>.yaml`, where `<id>` is the art id without `art:` and with `:`
as `_` (`art:hoth:frozen-at-at` is `hoth_frozen-at-at.yaml`). The four terrain surfaces (tool
`greybox terrain`) are tiles, not models: their `model_status` is `N/A`. It is modelled like the real object from the films,
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
- **Size is checked against the wiki.** Scenery: `cells` must equal the row's `drawn`. Other rows: `cells`
  is the footprint's width and at least its depth (taller where it rises above its hit box; the render
  writes `drawn`). Rooms (tool `greybox room`) are drawn whole at their footprint. `footprint` (bottom rows)
  is always the depth of the hit box. Drawn rows = plan depth + height, so a tall object needs a shallow plan.
- **What reads at 16 px a metre:** the south face shows whole, east and west faces are edge-on and north
  faces are hidden. Put the parts that identify an object where they show: a TIE's hexagon wing stands up
  facing south (flat on the ground it is a line), a fallen AT-AT's legs point south, not north. A tall light
  part on a mid-grey body (the AAT's pods, the AT-AT's leg plates) reads better than all-light.

- **Model the real thing, then pose it.** Build the object as it stands in the film, in its own axes,
  then pose the whole model: `tilt: [pitch, roll]` about `pivot` (a walker on its side is `tilt: [0, 90]`),
  `turn` (deg about z, any angle: the camera is 3D), `sink` (m into the ground; the ground cuts it flat),
  `scale` (fit it to the drawn size) and `mirror` (the e/w facing). `foot` is where the model's origin
  lands in the sprite, in px.
- **`ground`**: parts lying on the ground around the piece (snow, debris, a lost wing, a fallen head).
  They are never posed, so they stay flat when the piece tilts. Drawn under the piece.
- **Templates** (`templates:` in the model, or shared in a kit file listed under `kits:`, e.g.
  `models/scenery/kits/walkers.yaml`): a named list of parts with `params`. Use one with
  `{use: walker-leg, name: leg-fl, at: [x, y, z], turn: deg, mirror: y, with: {knee: 20}}`. Its parts are
  named `leg-fl/...`. Templates may use other templates.
- **Params and expressions**: `params:` at the top of the model; any value written `"=expr"` is computed
  from them (with sin, cos, radians, sqrt, pi, min, max): `at: ["=hx", "=-hy", "=hip_z"]`.
- **`limb`**: a jointed leg or arm from low-poly boxes: `{root, yaw, splay, segments: [{len, w, d, bend,
  taper, joint: {r}}], foot: {r, h, flat}}`. Each `bend` is added to the last, so a knee is a bend. The
  AT-AT leg in the walker kit is one.
- **`ring`**: `n` blocks evenly round a circle (`c`, `axis`, `r`, `size`, `arc`): wheel treads, hull
  ribs, a skeleton's rib arc. The tank droid's tread is one.
- **Kits so far:** `kits/walkers.yaml` (the AT-AT leg), `kits/tatooine.yaml` (the moisture vaporator).
- **Variants**: `variants: {name: {overrides}}` makes one model many outputs. Each variant is merged over
  the model: `params` key by key, any other key replaced (`tilt`, `turn`, `sink`, `scale`, `foot`,
  `ground`), and `drop: ["leg-br/*", "head/*"]` leaves parts out by name. The first variant is the one the
  wiki row shows. The AT-AT has five: toppled (on its side, legs up in the air behind it), toppled-three-legs,
  toppled-headless, standing, sunk (through the lake ice).

```bash
python3 -m worldart scenery hoth_frozen-at-at    # render one (or several, or --all), every variant
python3 -m worldart scenery hoth_frozen-at-at --variant toppled --try turn=10 --try params.fknee=40
                                                 # one variant with tweaks, to output/ only
python3 -m worldart scenery hoth_frozen-at-at --variant toppled --sweep "turn=-12,0,12"
                                                 # each value side by side: output/scenery/<id>/sweep.png
python3 -m worldart scenery --all --jobs 4 --tilesets --collage
                                                 # every model into the wiki, per-planet tilesets, one collage
python3 -m worldart scenery hoth_frozen-at-at --sweep 'params={fknee: 20};{fknee: 60}'
                                                 # use ";" between values that hold commas; a dict merges
python3 -m worldart scenery --status             # every scenery row's model status
python3 -m worldart scenery --set art:hoth:frozen-at-at APPROVED
```

A render writes `output/scenery/<id>/{sprite,review,scene}.png` (with variants, one folder per variant).
It warns when the art touches an edge of the sprite, where it would be cut off. `scene.png` is the in-game check: one
15x10-cell screen with a greyed vanilla house, the vanilla cone rock and the player standing south of the
piece, its hit box in red, at 1x and 3x. The sprites (`<id>--<variant>.png`), the first variant's scene and a
sheet of every variant (`<id>_variants.png`) are copied to `../../wiki/world/models/`. `--variant`, `--try`
and `--sweep` never touch the wiki, nor does `--no-csv` (for several people or agents working at once:
one final `--all` run writes the wiki). Each render also writes the model's unique 8x8 tiles as a
128 px wide sheet, `wiki/world/models/tiles/<id>.png`, and `--tilesets` writes one sheet per planet with
every model's tiles (`wiki/world/models/tilesets/`, with a README of the counts against 512). The wiki row gets `model` (the yaml), `model_png`, `model_variants`,
`model_tiles` (unique 8x8 tiles after flips) and
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
