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
python3 -m mockup builds                  # wiki/mockup/_buildings.png: every building type at three sizes
python3 -m mockup missing                 # art ids that have no shape in styles.yaml yet
```

- [`wiki/mockup/styles.yaml`](../../wiki/mockup/styles.yaml): the style catalogue. Terrain colours and the
  `nature` look per planet, building materials per planet, and one shape per art id (`build` or `kind`,
  colours, `form`, optional `variants`).
  A piece whose art id is missing is drawn as a plain box with a magenta outline.
- `wiki/mockup/overrides/<area>.yaml`: mockup-only changes for one area (`hide`, `move`, `add`, `restyle`),
  so dressing can be moved around without editing phase 1. Format at the bottom of `mockup/style.py`.
- `mockup/build.py`: buildings. The camera looks down at about 45 degrees, so footprints are squashed in
  depth (round buildings are ovals), walls rise up the screen and only south-facing walls show. Primitives:
  `prism` (any polygon footprint, straight or sloped walls), `cyl` (oval footprint; roof flat, dome, cone,
  ring, open bowl, deck), `pit` (sunken courtyard), `berm` (earth mound), `legs` (stilts). The `BUILDS` table
  composes them: block, L, oct, T, notch, court, wings, hall, palace, pitched, barrel, quonset, hangar, tower,
  round-tower, stepped, dome, domes2, dome-block, store, cone, sunken, sunken-dome, bunker, buried, stilts,
  stilts-dome, stilts-flat, deck, plant, lab, arena. See them all in `wiki/mockup/_buildings.png`.
- `mockup/draw.py`: terrain, props and people. `mockup/cli.py`: the commands.
