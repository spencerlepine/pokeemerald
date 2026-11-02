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
    stilts-flat, deck, pad, bay, plant, lab, arena, and hipped. A prop whose style has a `build` (the landing pad) is a 3D
    model too. Sunken courtyards were dropped (owner: doors can't sit at the bottom of a pit like that). `python3 -m mockup builds [--grey]` draws them all.
  - **Giants** (`GIANTS` in build.py) are huge pieces for the edges of a map, modelled at true scale and
    only partly drawn: the sprite is clipped to its box, so a wall or a city runs off the map and the player
    sees only its base. Only trench-wall is kept. Giants draw first, behind every
    building, so they never cover playable content.
    Solids are hidden below ground unless made with `below=True`. They sit on blocked border cells and are placed only by mockup
    overrides (`wiki/mockup/overrides/<area>.yaml`, `add: buildings`), never in phase 1.
    `python3 -m mockup builds --giants [--grey]` draws them.
  - **The projection rule for round things** is enforced in `solid.py`, not left to each model: seen through
    the game's 45° camera, a true circle of radius r is an oval r wide and r·K deep and a height h shows as
    h·K (K = cos 45° ≈ 0.707). `cylinder`, `dome` and `cone` take only the true radius and derive the depth;
    a dome is never taller than a hemisphere. A round building that doesn't fit its box gets narrower,
    never squashed (`fit_round` in build.py).
    The owner prefers roofed buildings; keep round ones for iconic places only.
  - **Cleaned up (owner, 2026-11-02):** scrapped as weak art: debris, cliff-town, hangar-wall, fortress-wall,
    palace-wall, temple-stairs, cliff-door, comm-tower, obelisk, spire, saucer, ship-hull, undercity-rim, stilt-city, city-edge (and earlier shield-gen, turret). New buildings come **one category at a
    time**, small and high quality, each reviewed before the next. No batches.
  - **Categories** (`mockup/kit.py`, owner 2026-11-02): new pieces live in `CATEGORIES` and register into
    `BUILDS`. A **simplicity guardrail** runs on every piece: at most 16 solids, and colours only from the
    piece palette (wall, roof, trim, glass, light, dark). Variation comes from the seed, not from detail.
    `python3 -m mockup kit <category> [--grey] [--planet P]` draws `wiki/mockup/kit/<category>.png`: every
    piece at its sizes in three seeded variations on plain ground (no trees), with a person and a 4x3 house
    for scale. The owner reviews pieces side by side, not placed in towns.
    1. `doorless`: utility and signal structures with no door: vaporator, mast, dish, beacon, tanks, stack,
       relay, crates, core.
    2. `sunken`: pieces cut into the ground: pit-home, stairwell, hatch, grate, trench, sunken-bay, well,
       mineshaft. The terrain is a see-through slab (`hide_top`, `below`), a pit is a cut allowed below
       ground, so the ray sees a pit's north wall and floor. Doors in a pit go in its north wall.
    3. `imperial`: angular military pieces with sloped walls, dark slits and blast doors:
       barricade, sentry, garage, barracks, pillbox, command, gate. Shown in Imperial greys
       (`kit.MATERIAL`), since the look belongs to the faction rather than a planet.
    Sunken pieces are allowed again now that the projection rule is enforced (owner, 2026-11-02).
    4. `nature`: pine, boulder, shard (ice or crystal), fungus. Broadleaf trees are parked until the end (hard to get right). What a `T` cell becomes, and
       only where a planet has it.
    5. `landform`: mesa, spire, arch, boulders, ridge, crater. Large natural borders instead of a ring of trees.
  - **Scrapped (owner, 2026-11-02):** tree, bush, the checkpoint barrier gate and the power pole. They read as
    human-made, z-day-style objects. Design from Star Wars sci-fi, not from z-day or Earth.
  - **Relief for every phase-1 area** (`mockup/relief.py`): heights derived from the grid, no hand-written
    grids. A rock mass (`#`, `x`) is a plateau: in each column the southern cells of a rock run are its
    cliff face (1-2 cells: all face; 3-5: one level; 6+: two levels; none if it runs off the bottom edge),
    the rest is rock top. Rock sides get a lip, ground east of rock gets its shadow, water sits below its
    banks, ledges stay one level, and `T` cells become kit models (pine, boulder, shard, fungus by the
    planet's nature kind). The map stays on the game grid. `python3 -m mockup render --all --relief`
    writes `wiki/mockup/relief/<planet>/<area>.png`; `relief.heights(grid)` returns the levels.
  - **Greybox areas in three layers** (owner, 2026-11-02: build a whole planet in greybox, breadth first):
    1. Terrain (`mockup/terrain.py`): a heights grid (0-9 levels, one level = one 16 px ledge) and a surface
       grid (`.` ground, `:` path, `"` wild, `~` water, `b` berm, `H` stairs, `T` nature). Drawn north to
       south in the same projection: cliffs (strata), 1-high ledges (lit lip), berms (soft slope), water a
       little below its banks, waterfalls where water drops a level. Side drops get a rock lip.
    2. Large structures: `landform` pieces (and the trench wall giant) placed on the terrain at its level.
    3. Town: any kit or building piece, placed on flat ground.
    `python3 -m mockup scene <name> [--grey]` composes `wiki/mockup/scenes/<name>.yaml` into a `.png`,
    drawing pieces row by row with the terrain so nearer cliffs hide what is behind them. A scene lists
    `planet`, `heights`, `surface`, `pieces` (`build`, `at`, `size`, optional `door`, `material`, colours),
    `people`, and `nature` (what `T` cells become). Demos: `desert-outskirts` (no trees), `forest-river`.
  - **Solids combine in order** (`Scene.solid_at`): a cut removes only what was added before it, so a pit
    can be cut and then furnished with steps, a pad or a ladder.
  - `render --grey` draws buildings in neutral grey (the pure greybox look); `--out DIR` writes elsewhere.
- `mockup/draw.py`: terrain, props and people. `mockup/cli.py`: the commands.
