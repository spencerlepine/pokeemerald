# building-kit: outdoor buildings from a kit of parts

Status: **round 1, in review with the owner** (started 2026-11-04). Greybox only: shapes and light, no
colour or texture. Nothing here writes the wiki or `../../game` yet.

Vanilla Emerald has a few square houses copied all over the map. This game has many more towns on very
different planets, so buildings are made from a **kit**: walls, roofs, doors, windows and decor as
reusable templates, put together by **blueprints** that pick sizes, roofs and extras from a seed. One
blueprint gives a whole family of buildings that look like the same street but are never copies.

Buildings are designed from the films (Mos Eisley, the Lars homestead, Echo Base, Cloud City...), not from
Hoenn's houses. They stay low poly and big: a door is about one cell wide, a window at least half a cell,
no fine detail.

Rendering is the world-art camera (`../world-art`, imported, never edited): ground in plan, south faces
head-on, 16 px a metre and a cell. See [`../world-art/README.md`](../world-art/README.md) for the part
shapes (`box`, `cylinder`, `ellipsoid`, `prism`, `hull`, `extrude`), templates and expressions.

Needs pillow, pyyaml and numpy.

## Commands

```bash
cd tools/building-kit
python3 -m bkit list                                  # every blueprint
python3 -m bkit try block-house --seed 3 [--width 5] [--set roof=dome]   # one building, 6x
python3 -m bkit variants block-house -n 12            # 12 seeds side by side
python3 -m bkit parts tatooine                        # every kit piece alone
python3 -m bkit sheet --style tatooine -n 4           # every blueprint of a style, 4 seeds each
python3 -m bkit street --style tatooine --seed 1      # a random street, a vanilla house for scale
```

Everything is written to `output/` (not committed).

## Files

- `kits/common.yaml`: materials (greybox ramps) and the pieces every style uses: `door-arch`, `door-slab`,
  `window-round`, `window-slot`, `vent`, `crate`.
- `kits/<style>.yaml`: a planet's pieces. `uses:` pulls in other kit files (Tatooine uses the world-art
  vaporator). A template with `preview:` shows on `parts`.
- `blueprints/<style>/<name>.yaml`: a building family. The format is in `bkit/compose.py`:
  - `width`: cells, one picked per seed.
  - `choose`: params picked per seed: `[lo, hi]`, `{pick: [...], weights: [...]}`, `{int: [lo, hi]}` or
    `"=expr"` of earlier ones. `W` (cells), `w_max` (metres usable) and `seed` are always there.
  - `parts`: world-art parts and `use:` templates, plus `when`/`else`, `chance`, `pick` (with `set` for
    params of that option) and `repeat` (with `i`).
- Axes: x east (0 = the sprite's middle), y north (0 = the front of the building), z up. The sprite is `W`
  cells wide and cropped to whole cells above the art.

## Tatooine (round 1)

| Blueprint | From the films | Varies |
|---|---|---|
| `dome-hut` | The Lars homestead huts | dome size and squash, entry block, second dome or side vault, vent, vaporator |
| `block-house` | Mos Eisley / Mos Espa blocks | size, wall lean, roof (band, dome, stepped upper block, flat), arch or slab door, round or slot window, buttresses, vent |
| `dome-cluster` | The Mos Eisley cantina | domes (2-3), entry block, vent tower |
| `tower` | Mos Espa towers | 2-3 stepped tiers, dome or band on top, door |

## Next

More Tatooine bases (walled courtyard, docking-bay ring, garage, market awning), then a kit per planet
(Imperial, Wookiee, Ewok, Kamino, Bespin, Sullust, Yavin, Hoth). Once the owner approves the look, the kit
takes over the 40 `building` rows in `../../wiki/mapping/world_art.csv` (after the world-art greybox pass
on those rows, coordinated with that work), and an export writes each building's tiles for the
tile-generator.
