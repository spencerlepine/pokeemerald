# mockup: phase 2, shapes and colours

Draws every area of the world blockout (phase 1, [`wiki/world/`](../../wiki/world/README.md)) as a flat
shapes-and-colours mockup: planet-coloured terrain, buildings in the game's top-down 3/4 view, props as basic shapes (trees, rocks, crates, tanks, ships, bones), and
pink-family figures for people (gold ring = story, red ring = trainer). 16 px per map cell, like the game.

It is a layer on top of phase 1: it **reads** `wiki/world/` and **writes only** `wiki/mockup/`, so the mockup
can be scrapped and redone without touching a layout.

```bash
cd tools/mockup
python3 -m mockup render --all            # every area -> wiki/mockup/<planet>/<area>.png
python3 -m mockup render mos-eisley       # one or more areas by id
python3 -m mockup render --planet HOTH    # one planet
python3 -m mockup world                   # wiki/mockup/<planet>/_planet.png and wiki/mockup/_world.png
python3 -m mockup builds [--grey]         # wiki/mockup/_buildings[-grey].png: every building type, three sizes
python3 -m mockup missing                 # art ids that have no shape in styles.yaml yet
```

- [`wiki/mockup/styles.yaml`](../../wiki/mockup/styles.yaml): the style catalogue. Terrain colours and the
  `nature` look per planet, building materials per planet, and one shape per art id (`build` or `kind`,
  colours, `form`, optional `variants`).
  A piece whose art id is missing is drawn as a plain box with a magenta outline.
- `wiki/mockup/overrides/<area>.yaml`: mockup-only changes for one area (`hide`, `move`, `add`, `restyle`),
  so dressing can be moved around without editing phase 1. Format at the bottom of `mockup/style.py`.
- **Buildings are real 3D greyboxes**, the method of z-day's building generator
  (`.claude/tools/art/world/structures/buildings` in the z-day repo). Each building is modelled as simple
  convex solids (boxes, oval prisms, half-ellipsoid domes, cones, gables, barrel vaults, sloped bunker walls,
  with subtractive cuts for doors, windows, courtyards and pits), then one ray per pixel is cast in the
  game's projection and shaded by the surface normal with a cast shadow and outlines.
  - Projection: a screen row is the line y + z = const, so one cell north and one cell up both move 16 px up
    the screen. A footprint W x D px with walls h px fills exactly D + h rows of the phase-1 cell box. Only
    top and south faces show. Round footprints are ovals because they fill the box's footprint rows.
  - `mockup/solid.py`: solids, ray casting, shading. `mockup/build.py`: the models in `BUILDS`: block, L,
    oct, T, notch, court, wings, hall, palace, pitched, barrel, quonset, hangar, tower, round-tower, stepped,
    dome, domes2, dome-block, store, cone, sunken, sunken-dome, bunker, buried, stilts, stilts-dome,
    stilts-flat, deck, plant, lab, arena. `python3 -m mockup builds [--grey]` draws them all.
  - `render --grey` draws buildings in neutral grey (the pure greybox look); `--out DIR` writes elsewhere.
- `mockup/draw.py`: terrain, props and people. `mockup/cli.py`: the commands.
