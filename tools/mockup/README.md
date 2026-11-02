# mockup: phase 2, shapes and colours

Draws every area of the world blockout (phase 1, [`wiki/world/`](../../wiki/world/README.md)) as a flat
shapes-and-colours mockup: planet-coloured terrain, buildings in the game's top-down 3/4 view, props as basic shapes (trees, rocks, crates, tanks, ships, bones), and
pink-family figures for people (gold ring = story, red ring = trainer). 16 px per map cell, like the game.

It is a layer on top of phase 1: it **reads** `wiki/world/` and **writes only** `wiki/mockup/`, so the mockup
can be scrapped and redone without touching a layout.

Needs pillow, pyyaml and numpy.

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
    dome, domes2, dome-block, dome-porch, store, cone, glass-dome, bunker, buried, stilts, stilts-dome,
    stilts-flat, deck, pad, bay, plant, lab, arena, and the sci-fi set: spire, saucer, comm-tower,
    cliff-door, obelisk, hipped. A prop whose style has a `build` (the landing pad) is a 3D
    model too. Sunken courtyards were dropped (owner: doors can't sit at the bottom of a pit like that). `python3 -m mockup builds [--grey]` draws them all.
  - **Giants** (`GIANTS` in build.py) are huge pieces for the edges of a map, modelled at true scale and
    only partly drawn: the sprite is clipped to its box, so a Star Destroyer runs off the map and the player
    sees just its bow. ship-hull (`facing: east|west`), debris, palace-wall, trench-wall, stilt-city,
    undercity-rim (`rim: [cx, cy, a, b]` in cells; its deck top is see-through and the city side drops
    below ground level), temple-stairs, cliff-town, city-edge, hangar-wall, fortress-wall, cliff-door.
    Solids are hidden below ground unless made with `below=True`. They sit on blocked border cells and are placed only by mockup
    overrides (`wiki/mockup/overrides/<area>.yaml`, `add: buildings`), never in phase 1.
    `python3 -m mockup builds --giants [--grey]` draws them.
  - Every round footprint uses one depth-to-width ratio (`OVAL` = 0.6), so all round things match the view.
    The owner prefers roofed buildings; keep round ones for iconic places only.
  - `render --grey` draws buildings in neutral grey (the pure greybox look); `--out DIR` writes elsewhere.
- `mockup/draw.py`: terrain, props and people. `mockup/cli.py`: the commands.
