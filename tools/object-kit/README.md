# object-kit: small world objects in greybox

Status: **round 4, in review (owner, 2026-11-04: rocks approved at `faceted`; 2x2 forest trees are fine as filler, the tool's real job is larger pieces, all in the 45° view).** Shapes and light only, no colour or texture. Nothing
goes into `../../game` or the wiki yet.

Small and medium world pieces: rocks, trees, plants, ice, crystals, and small structures (comm towers,
crates, tanks). Vanilla framed every map with one tree. This game frames each planet with its own
things, so each object is a **family**: a blueprint picks shapes and sizes from a seed, and one blueprint
gives many pieces that belong together but are never copies. Buildings are `../building-kit`; large
scenery (wrecks, walkers, fossils) is `../world-art` (`scenery`).

Rendering is the world-art camera (`../world-art`, imported, never edited): ground in plan, south faces
head-on, 16 px a metre and a cell. Keep it low poly and big: whole-cell pieces, simple shapes that read,
nothing thinner than about 3 px unless it is a post or an antenna.

Needs pillow, pyyaml and numpy.

## Commands

```bash
cd tools/object-kit
python3 -m okit list                                   # every blueprint, with role and hit box options
python3 -m okit try tatooine/rock-spire --seed 3 [--footprint 2x1] [--set kind=hoodoo]   # one, 6x
python3 -m okit variants dagobah/gnarltree -n 8        # 8 seeds, a game-screen scene, and a border strip for edge pieces
python3 -m okit sheet [--style hoth] -n 6              # variants of every blueprint (of a style)
python3 -m okit collage [-n 6]                         # every family on one image: output/_collage.png
python3 -m okit catalog [--planet sullust]             # the object list per planet, and what is designed
python3 -m okit build [--planet endor]                 # every designed catalog entry at its footprint: output/build/
python3 -m okit forest ilum/pine-block [--cols 6 --rows 4]   # a forest of blocks on vanilla's grid, beside Petalburg Woods
```

Everything is written to `output/` (not committed). Each line printed for a seed gives the hit box, the
drawn size (rows above the hit box are walk-behind), the unique 8x8 tiles, and `HIT BOX OVERFLOW` if the
piece stands on more ground than its hit box.

## The chunk dial (owner 2026-11-04)

Vanilla's rocks and trees are wide at the base, round on top and built from one to three big masses.
Nothing ends in a point and nothing is thinner than about 5 px. So the generators take their
defaults from one dial in `okit/gens.py` (`LEVELS`): `faceted` (the default, owner's pick), `chunky` and
`soft`. It sets the bevel on every edge, the facets per ring, how far spike tops are cut flat and the
thinnest spike. Pick a level with `--chunk` on any command or `OKIT_CHUNK`. Blueprints leave `n`,
`round` and `top` unset unless the shape needs them, so the dial moves every family at once.

Rules for writing a family under the dial:
- One to three big masses; no twigs, needles or thin fins. Limbs end in a round knob.
- Width about the same as the height; a tall piece is a stack of chunks, never a cone to a point.
- Leaf crowns and bushes are clumps lit as balls with dark lines between them (`lobes`, the method
  of the approved Hoenn tree).

## Build for the 45° camera (round 4)

The camera is the vanilla one: it looks down at 45°, so a top surface is drawn at its full plan depth and
a south face at its full height. A piece only reads as seen from above if it has a top to show. So:

- Make pieces about as deep as they are wide (round or square in plan), not flat billboards: crowns,
  caps and rock tops get their real depth, and their top is the biggest lit area.
- Roots, legs and limbs splay in every direction (`arc` 0 to 360), not only east, west and south.
- A crown's north half is seen too: give it clumps (a second `lobes` set centred further north).
- `try` warns `flat in plan` when a piece is much wider than it is deep. A log lying east-west may
  ignore it; a tree or a rock should not.

| Medium and large pieces | Hit box | What it is |
|---|---|---|
| `dagobah/mangrove` | 3x2 | round crown seen from above, prop roots all round a short trunk |
| `tatooine/mesa` | 4x3, 5x3 | cap rock with a lit top over a tapering cliff, a lower step, fallen chunks |
| `felucia/fungus-grove` | 3x2 | one giant mushroom and two small ones, round caps |
| `kashyyyk/wroshyr-giant` | 4x3, 5x3 | thick trunk on buttress fins, a two-shelf canopy |

## Trees are forest blocks (round 3)

A forest in vanilla is one tree on a plain grid: every tree a 2x2 block, its crown filling the block the
same way every time, so a wall of them closes up with no gaps. Trees that vary in size or leave gaps look
broken when tiled (owner, round 2). So every tree family is a forest block:

- `footprint: [2, 1]`, `fill: true`, `drawn: 2`: a 2x2 block, crown edge to edge, hit box the bottom row.
- `foot: [16, 28]` puts the trunk where vanilla's is; the crown top stays under `y + z` 1.6 m or it is cut.
- Seeds change small details only (a lean, a shift, a moss strip), never the size or the outline.
- `edge` (true by default) is the forest's south row: it shows the trunk and roots. The `forest` command
  draws the rows behind with `edge` false.
- `cylinder` with `r1`/`r2` is a flat-ended cone (a skirt); `cone` is a capsule with round ends.
- Give a part its own `group` plus `_new_group: true` to get a dark line around it (tiers, snow, moss).

| Block | What it is |
|---|---|
| `hoenn/broadleaf` | the approved Hoenn tree, as the calibration |
| `kashyyyk/wroshyr-tree` | flat-topped canopy of leaf plates, fronds on the rim, thick trunk and roots |
| `dagobah/gnarl-block` | dark drooping crown, moss strips, crooked roots on the edge |
| `felucia/fungus-block` | one big pale cap on a stalk, gills under it, a small side mushroom on the edge |
| `ilum/pine-block` | three stepped skirts, snow on top of each, green rims |
| `yavin-4/jungle-block` | wide flat crown, hanging clumps and vines |

## Hit box and drawn size

Every object has a **footprint**: the cells the player cannot enter (W x D, the bottom D rows of the
sprite). The sprite is as tall as the art needs; the rows above the footprint go in the metatiles' top
layer so the player walks behind them (wiki/bible/WORLD_ART.md, "Fill the tile"). The tool measures
the ground the piece really stands on (every solid at knee height, 0.1 m) and flags any piece that
spills out of its footprint. A tall piece needs a shallow plan: drawn rows = plan depth + height.

## Roles

`role` comes from the wiki's signal-and-noise rule: `edge` blocks and frames paths (the planet's
border instead of trees), `noise` sits in corners and dead space, `landmark` is one per map,
`walkable` is ground the player crosses. Edge families set `fill: true` (they may run edge to edge,
so a row of them tiles) and get a `border.png`: three rows of seeds packed north of a path, the way
they would replace a tree line.

## The catalog

`catalog/<planet>.yaml` lists every small object each planet needs: its role, footprint, the
`world_art.csv` row it draws (empty = new, not in the wiki yet) and the blueprint that draws it (empty =
still to design). Round 1 has 77 objects, 16 designed. The list was made from each planet's biome in
the wiki (`wiki/bible/WORLD_ART.md`, the `PLANET_KIT` borders, the nature and object rows) plus what the
films show there. The format is in `okit/catalog.py`. The wiki rows are not touched until the owner
approves the look; the scenery thread is greyboxing those rows in `../world-art` at the same time.

## Writing a blueprint

`blueprints/<style>/<name>.yaml`. The format is in `okit/compose.py`:

- `role`, `footprint` (one `[W, D]` or a list to pick from per seed), `fill`, `drawn` (fix the sprite's
  rows, for a trunk that runs off the top), `about`.
- `choose`: params picked per seed: `[lo, hi]`, `{pick: [...], weights: ...}`, `{int: [lo, hi]}` or
  `"=expr"`. `W`, `D` (hit box cells), `w_max`, `d_max` and `seed` are always there.
- `parts`: world-art parts (`ellipsoid`, `cone`, `cylinder`, `box`, `hull`, `prism`, `extrude`, and
  its generators `lobes`, `branches`, `tiers`, `scatter`, `ring`, `limb`), `use:` templates, plus
  `when`/`else`, `chance`, `pick` (with `set`) and `repeat` (with `i`).
- Object-kit generators (`okit/gens.py`), usable in kits too:
  - `rock`: a convex hull of jittered rings up an ellipsoid; `rings` sets the profile (boulders,
    hoodoos, needles).
  - `spike`: a faceted spike or cut-off prism (ice, obsidian, crystals).
  - `columns`: packed hex prisms with a height peak (basalt, crystal beds).
  - `roots`: roots from a trunk to the ground, `arch` (mangrove) or `wedge` (buttress fins).
- Axes: x east (0 = the sprite's middle), y north (0 = the south edge of the hit box), z up, 1 m = 1 cell.
- `materials`: greybox ramps from `kits/common.yaml` (rock, stone, bark, leaf, ice, fungus, metal,
  dark, light); a blueprint may override one (the snow pine darkens its needles so the snow reads).

## Round 1 families (rocks, structures; the round 1 trees are kept for reference)

| Blueprint | Role | What varies |
|---|---|---|
| `tatooine/sandstone-boulder` | edge | dome, slab, or a big rock leaning on a small one |
| `tatooine/rock-spire` | edge | hoodoo with a wide cap, a stepped stack of chunks, or a rounded butte |
| `tatooine/dead-tree` | noise | a thick trunk and two or three fat limbs with round knobs |
| `kashyyyk/wroshyr-trunk` | edge | width, buttress roots, shelf fungus or a branch stub; cut off at 5 rows |
| `kashyyyk/fern-clump` | noise | frond count, spread and height |
| `dagobah/gnarltree` | edge | three thick prop roots, trunk bend, a wide low clumped crown |
| `felucia/giant-fungus` | edge | single or a cluster of 2-3, cap size, spots |
| `hoth/ice-spikes` | edge | chunky blunt ice blocks out of a snow drift |
| `sullust/basalt-columns` | edge | column size and peak |
| `ilum/snow-pine` | edge | two or three fat skirts with snow caps, a round top |
| `ilum/kyber-outcrop` | noise | crystal count and height |
| `mustafar/obsidian-spire` | edge | two or three blunt shards on a rubble base |
| `endor/fallen-log` | edge | length, root plate or broken end, moss |
| `shared/comm-tower` | landmark | block or leg base, dish, array or sensor ball |
| `shared/cargo-crates` | noise | stack size, a top crate, a barrel or canister |
| `shared/fuel-tanks` | noise | upright with a pipe, or lying on cradles |

## Next

Once the owner approves the look: the rest of the catalog, then write the designed rows into the wiki
(the `world_art.csv` rows that have an `art` id, coordinated with the scenery work) and export each
piece's tiles for the tile-generator.
