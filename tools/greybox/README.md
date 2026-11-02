# greybox: world pieces as simple 3D models, rendered to pixels

Status: **READY** for buildings and structures (the owner approved the kit categories on 2026-11-02). Terrain
in relief works. Interiors: `room` draws the room shell and the `interiors` kit has 19 props (owner approved the first set).
Dungeons: `terrain` draws caves and station decks in cave mode (all 119 render). Surfaces: `~` is water, sea, swamp,
lava, ice, cloud or void by planet. Raised walkways, floating platforms and ships have no model yet; they stay
`pending-mockup` in the wiki until a model exists.

Every piece is a small 3D model of convex solids (boxes, oval prisms, domes, cones, gables, cuts), ray-cast one
pixel at a time in the game's top-down view and shaded, so round roofs come out as ovals, only south faces show,
and a footprint lands on whole 16 px cells. Greybox is the current phase: shapes and placeholder colours, no
texturing (the owner's call). Final art and the colour palette come later, tracked by the same wiki rows.

Needs pillow, pyyaml and numpy.

## What to draw

The wiki is the one list. Ask it, then draw, then record:

```bash
cd tools/blockout
python3 -m blockout todo --tool greybox --status pending-mockup     # pieces that still need a model
python3 -m blockout todo --status pending-final-art                 # pieces with a greybox, waiting for final art
python3 -m blockout todo --set art:tatooine:cantina pending-final-art
```

A piece is a row in [`wiki/mapping/world_art.csv`](../../wiki/mapping/world_art.csv): its `build` column names
the model here, `footprint` its size in cells, `tool` says `greybox piece`, `greybox` points at the rendered
PNG, `status` is one of `pending-mockup`, `pending-final-art`, `art-complete`, `imported-in-game`. An area is its
yaml in `wiki/world/<planet>/`, with `art_status` and `notes` (what it needs, in words).

## Commands

```bash
cd tools/greybox
python3 -m greybox piece art:shared:bacta-center          # -> wiki/world/greybox/shared_bacta-center.png
python3 -m greybox piece gym-hex --size 6x5 --seed 3      # any model by name, for trying things out
python3 -m greybox piece --all                            # every art id with a build; fills the `greybox` column
python3 -m greybox kit gyms [--grey]                      # one category side by side, for review
python3 -m greybox sheet [--grey] [--giants]              # every building model at three sizes
python3 -m greybox terrain hoth-tundra [--grey]           # one area in relief, with its pieces (caves: cave mode)
python3 -m greybox room mos-pelgo-lab [--grey]            # one interior as a room -> wiki/world/greybox/rooms/<area>.png
```

`--grey` gives pure greybox colours; otherwise the planet palette from `palettes.yaml` is used.

## Files

- `palettes.yaml`: terrain colours, building materials and people roles per planet (placeholders; colour
  direction is not decided).
- `styles.yaml`: per-art-id colour overrides and `variants` (partial entries picked by position). The model name
  itself lives in the wiki.
- `greybox/solid.py`: solids, ray casting, shading, shadows, outlines. **The projection rule for round things**
  lives here, not in each model: a true circle of radius r shows as an oval r wide and r·K deep (K = cos 45°),
  a dome is never taller than a hemisphere, a round piece that doesn't fit shrinks rather than squashes.
  Solids combine in order: a cut removes only what was added before it, so a pit can be dug and then furnished.
- `greybox/build.py`: the base building models (`BUILDS`: block, L, oct, T, notch, court, wings, hall, palace,
  pitched, barrel, tower, round-tower, stepped, dome, domes2, dome-block, dome-porch, store, cone, glass-dome,
  bunker, buried, stilts, stilts-dome, stilts-flat, pad, plant, lab, arena, hipped) and the one giant,
  trench-wall. `sprite()` renders one piece; `building()` pastes it on a map.
- `greybox/kit.py`: the categories added one at a time with the owner (`CATEGORIES`): doorless, sunken,
  imperial, nature, landform, hangars, gyms, interiors. Each piece passes a **simplicity guardrail** when it renders: at
  most 16 solids, colours only from its six-colour palette. Variation comes from the seed, never from detail.
  `MATERIAL` gives a category its own colours (Imperial greys); `SIGNED` categories get the game's sign drawn in
  front on the kit sheet (gyms).
- `greybox/relief.py`: heights for an area derived from its phase-1 grid. A rock run becomes a plateau with a
  cliff face on its south edge (1-2 cells: all face; 3-5: one level; 6+: two), rock sides get a lip and a shadow,
  water sits below its banks, and `T` cells become pine, boulder, shard or fungus by the planet's nature kind.
- `greybox/room.py`: an interior as a room. The `#` cells joined to the top edge are walls (two face cells above
  the floor, ceiling above that, a shadow on the floor below); every other `#` blob is furniture of unknown shape,
  drawn as a low slab (`r-block`). Props listed on the area with an `art` id use their kit model.
- `greybox/surface.py`: what a `~` cell is per planet (`SURFACE`: lava on Mustafar, cloud on Bespin, ice on Hoth
  and Ilum, swamp on Dagobah, sea on Kamino, void in the asteroid field; a plain water body of 200+ cells is sea),
  its drop below the bank (`DROP`) and its marks. Used by relief and cave mode.
- `greybox/cave.py`: cave mode, picked for every `dungeon` area with rock in it. Rock that touches no floor is the
  dark mass; rock above a floor cell is a wall two cells tall with a lit rim and a shadow on the floor; chambers
  get a rim on every side; the floor is the planet's ground darkened; `T` is a stalagmite (shard, fungus or
  boulder). Decks drawn with `|` and `_` (the Death Star) use the room shell. An open canyon with no rock keeps
  the outdoor relief.
- `greybox/draw.py`: terrain, flat props (the ones with no model yet), people, signs, labels.

## Rules learned with the owner

- One category at a time, small and high quality, reviewed before the next. No batches. Preview only the new
  pieces each round.
- Prefer roofed, angular, sci-fi shapes. No tubes or cylinders for hangars and shipyards; round shapes only
  where the planet's look calls for them (Tatooine domes). Gyms are varied boss houses sharing one bold
  doorway; the sign out front is the real marker.
- Design from Star Wars, never from z-day or Earth objects (the barrier gate and power pole were cut).
- Trees are parked until the end; pine is the only good one. Many planets have no trees at all.
- Giants (true-scale border pieces, partly seen) are allowed but only the Death Star trench wall survived review.
