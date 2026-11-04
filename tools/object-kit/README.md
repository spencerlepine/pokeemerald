# object-kit: rock families in greybox

Status: **paused (owner, 2026-11-04).** Only the rock shapes are kept: they were approved at the
`faceted` chunk level. Trees, plants and small structures were scrapped; a later tool will draw them.
Nothing here goes into `../../game` or the wiki yet. The wiki lists every small object, with a
placeholder sheet at its real size: [`../../wiki/mapping/objects.csv`](../../wiki/mapping/objects.csv).

Shapes and light only, no colour or texture. Rendering is the world-art camera (`../world-art`,
imported, never edited): it looks down at 45° like vanilla, so a top is drawn at its full plan depth
and a south face at its full height. 16 px is a metre and a cell. Needs pillow, pyyaml and numpy.

## Commands

```bash
cd tools/object-kit
python3 -m okit list                                   # every blueprint, with role and hit box options
python3 -m okit try tatooine/mesa --seed 3 [--footprint 5x3] [--set h=2.0]   # one seed, 6x, red hit box
python3 -m okit variants sullust/basalt-columns -n 8   # 8 seeds, a game-screen scene, a border strip
python3 -m okit sheet [--style hoth] -n 6              # variants of every blueprint (of a style)
python3 -m okit collage [-n 6]                         # every family on one image: output/_collage.png
```

Everything is written to `output/` (not committed). Each seed prints its hit box, its drawn size
(rows above the hit box are walk-behind), its unique 8x8 tiles, and warnings: `HIT BOX OVERFLOW`
if it stands on more ground than its hit box, `flat in plan` if it is much wider than it is deep
(the camera then sees almost no top and it reads as a side view).

## Families

| Blueprint | Hit box | What varies |
|---|---|---|
| `tatooine/sandstone-boulder` | 1x1 2x1 2x2 | dome, slab, or a big rock leaning on a small one |
| `tatooine/rock-spire` | 2x1 2x2 | hoodoo with a wide cap, a stepped stack of chunks, or a rounded butte |
| `tatooine/mesa` | 4x3 5x3 | height, which side the lower step is on; a cap rock over a tapering cliff, fallen chunks |
| `sullust/basalt-columns` | 2x1 2x2 3x2 | column size and peak |
| `mustafar/obsidian-spire` | 1x1 2x1 2x2 | two or three blunt shards on a rubble base |
| `hoth/ice-spikes` | 1x1 2x1 2x2 | two or three chunky ice stalagmites out of a snow drift |

## Rules the rocks follow

- The chunk dial (`okit/gens.py`, `LEVELS`): `faceted` (the default, the owner's pick), `chunky`,
  `soft`. It sets the bevel, the facets per ring, how far spike tops are cut flat and the thinnest
  spike. Pick one with `--chunk` or `OKIT_CHUNK`.
- One to three big masses; nothing ends in a point and nothing is thinner than about 3 px.
- Build about as deep as wide, so the top shows and is the biggest lit area.
- Hit box: the cells the player cannot enter (the bottom D rows). The tool measures the ground the
  piece stands on at knee height (0.1 m). Drawn rows = plan depth + height.
- `role` (`edge`, `noise`, `landmark`, `walkable`) is the wiki's signal-and-noise rule. Edge families
  set `fill: true` so a row of them tiles.

## Writing a blueprint

`blueprints/<style>/<name>.yaml`; the format is in `okit/compose.py`.

- `role`, `footprint` (one `[W, D]` or a list to pick from per seed), `fill`, `drawn`, `about`.
- `choose`: params per seed: `[lo, hi]`, `{pick: [...], weights: ...}`, `{int: [lo, hi]}` or `"=expr"`.
  `W`, `D`, `w_max`, `d_max` and `seed` are always there.
- `parts`: world-art parts and generators, `use:` templates, `when`/`else`, `chance`, `pick`, `repeat`.
  A part with its own `group` and `_new_group: true` gets a dark line round it (a cap rock, a step).
- Generators (`okit/gens.py`): `rock` (a convex hull of jittered rings; `rings` sets the profile),
  `spike` (a faceted, cut-off spike), `columns` (packed hex prisms with a height peak).
- Axes: x east (0 = the sprite's middle), y north (0 = the south edge of the hit box), z up, 1 m = 1 cell.
- `materials`: greybox ramps from `kits/common.yaml` (rock, stone, ice, dark, light).
