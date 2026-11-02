# world-art: new shapes for the Star Wars overworld

**Entry point for world building.** The tile-generator (`../tile-generator`) re-colours Emerald's
tilesets per planet: ground and water are done that way and still look like Hoenn's shapes. This
tool group draws the **new shapes** from `wiki/mapping/world_art.csv` (buildings, interiors,
objects, nature; concept art in `wiki/art/concept/`) inside Emerald's constraints, so a whole
planet can be rebuilt from text models and a palette, and rebuilt again when the style changes.

Progress and the order of work live in [`CHECKLIST.md`](CHECKLIST.md): read it first, it is what a
later session picks up from. The first area built end to end is **Bright Tree Village (Endor)**,
the treehouse town (vanilla Fortree); its scene is `scenes/bright-tree-village.yaml`.

## The guard rails (why this is a tool and not a brush)

1. **The camera** (`worldart/render.py`, `../tile-generator/STYLE.md` 1): ground in plan, south faces
   head-on at full height, east/west faces edge-on, nothing foreshortened. A model is 3D; the
   renderer can only ever draw it the Emerald way, so a new shape never breaks the top-down illusion.
2. **The cell grid**: an object is a rectangle of 16x16 cells, 16 px per metre; its bottom
   `footprint` rows are solid (bottom layer, impassable) and the rows above are walk-behind (top
   layer). Nothing hangs over a neighbour (a 1 px margin is enforced, `WARNING` = error).
3. **Cel shading**: ramps of 3-4 tones, hard snaps on flat faces, a 50% checker band at each cut on
   round ones (`dither: true`), ambient occlusion in crevices, 1 px outline in the material's
   darkest tone, a checker drop shadow.
4. **The palette**: every colour comes from `palettes/<planet>.yaml` (GBA-safe, roles from
   `wiki/bible/PALETTE.md`); an object may use at most **15 colours** (one bank). `budget` counts
   its unique 8x8 tiles, the other thing a tileset runs out of.

Textures are tone-level patterns (`texture: scallop | ridge | plank | brick | speck`), so they
dedupe into tiles and never add colours.

## Tools

| Tool | What | Status |
|---|---|---|
| `worldart/model.py`, `sdf.py` | Model files: parts (ellipsoid, cone, box), smooth-union groups, generators (`scatter`, `branches`, `tiers`), noise, instances. Ported from the z-day object generator (`spencerlepine/z-day`, `.claude/tools/art/world/props/objgen`), whose file format this keeps. | works |
| `worldart/render.py` | The Emerald camera + shading + outlines + textures + shadow | works, iterating on the look |
| `worldart/preview.py` | `review.png`: 1x on three ground tones, 3x, 6x with grid, footprint (red), feet (blue) | works |
| `worldart/tiles.py` | 8x8 tile split with flips, colour count, bottom/top layer split | counts; export to a tileset comes with install |
| `worldart/scene.py` | Mockup: place rendered objects on a planet ground at cell coords, back to front | planned |
| buildings | Box/prism/dome parts with doors and windows (south face), roof patterns | planned, same renderer |
| interiors | Room kits | later |

```bash
cd tools/world-art && pip install -r requirements.txt
python3 -m worldart render models/endor/redwood-trunk.yaml --preview-only   # -> output/preview-only/<name>/review.png
python3 -m worldart render models/endor/*.yaml                              # -> output/<name>/{sprite.png, review.png, meta.json, indices.npy}
python3 -m worldart budget models/endor/*.yaml
python3 -m worldart scene scenes/bright-tree-village.yaml                   # -> output/scenes/<name>.png
```

## Model file (short form; the z-day README documents every key)

```yaml
name: redwood-trunk        # = the world_art.csv concept slug
palette: endor             # palettes/endor.yaml
cells: [3, 4]              # w x h cells; the image is 48x64
foot: [24, 61]             # px where the trunk meets the ground (world origin)
box: [40, 14]              # collider, px, centred on foot x, bottom edge on foot y
footprint: 1               # bottom rows the player cannot enter (default: rows the box touches)
shadow: {rx: 20, ry: 3}
materials:
  bark: {ramp: redwood_bark, bands: [-0.05, 0.38, 0.76], dither: true, texture: ridge}
groups: {trunk: {k: 0.12}}
parts:
  - {name: trunk, group: trunk, mat: bark, cone: {a: [0, 0, 0], b: [0, 0, 3.6], r1: 0.5, r2: 0.42}}
  - scatter: {count: 22, within: {c: [0, 0, 3.3], r: [1.25, 0.85, 0.3]}, size: [0.3, 0.45]}
    mat: needle
```

World units are metres (1 m = 1 cell = 16 px): X east, Y north, Z up, origin at the foot. `bands`
are N.L cuts darkest -> lightest; the light is from the upper left, in front and above
(`render.light`, world space).

## Output

`output/` is git-ignored; review sheets for the owner go to `/mnt/project-files/tile-generator/world-art/`.
Approved objects are later packed into the planet's tileset by the tile-generator `install`
(`wiki/bible/TILESET_INSTALL.md`); nothing here touches `game/`.
