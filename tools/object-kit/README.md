# object-kit: small world objects in greybox

Status: **round 1, in review (owner, 2026-11-04).** Shapes and light only, no colour or texture. Nothing
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
```

Everything is written to `output/` (not committed). Each line printed for a seed gives the hit box, the
drawn size (rows above the hit box are walk-behind), the unique 8x8 tiles, and `HIT BOX OVERFLOW` if the
piece stands on more ground than its hit box.

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

## Round 1 families

| Blueprint | Role | What varies |
|---|---|---|
| `tatooine/sandstone-boulder` | edge | round, slab or split; a pebble beside it |
| `tatooine/rock-spire` | edge | hoodoo (cap on a waist), needle, twin spire |
| `tatooine/dead-tree` | noise | limbs, lean, a rock at the foot |
| `kashyyyk/wroshyr-trunk` | edge | width, buttress roots, shelf fungus or a branch stub; cut off at 5 rows |
| `kashyyyk/fern-clump` | noise | frond count, spread and height |
| `dagobah/gnarltree` | edge | prop roots, trunk bend, crown, hanging moss |
| `felucia/giant-fungus` | edge | single or a cluster of 2-3, cap size, spots |
| `hoth/ice-spikes` | edge | spike count, height and lean on a snow mound |
| `sullust/basalt-columns` | edge | column size and peak |
| `ilum/snow-pine` | edge | tiers, height, width; snow on every skirt |
| `ilum/kyber-outcrop` | noise | crystal count and height |
| `mustafar/obsidian-spire` | edge | blade, pair or broken stump |
| `endor/fallen-log` | edge | length, root plate or broken end, moss |
| `shared/comm-tower` | landmark | block or leg base, dish, array or sensor ball |
| `shared/cargo-crates` | noise | stack size, a top crate, a barrel or canister |
| `shared/fuel-tanks` | noise | upright with a pipe, or lying on cradles |

## Next

Once the owner approves the look: the rest of the catalog, then write the designed rows into the wiki
(the `world_art.csv` rows that have an `art` id, coordinated with the scenery work) and export each
piece's tiles for the tile-generator.
