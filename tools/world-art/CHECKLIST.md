# world-art checklist (the resumable plan)

Owner direction (2026-11-02): build the tools first, one area end to end, then expand. Prototype,
mock up, combine the tools in one scene, keep the top-down projection / silhouettes / cel shading
exact; the palette is calibrated last. Commit and push at every checkpoint.

Status marks: `[ ]` not started, `[~]` in progress, `[x]` done, `[r]` waiting for the owner's review.

## Tools

- [x] Package scaffold, model loader (ported from z-day objgen), palettes per planet
- [x] Emerald-camera SDF renderer: projection, bands, dither, AO, outlines, textures, drop shadow
- [x] Review sheet (1x / 3x / 6x grid), tile + colour budget
- [~] Look pass against vanilla (bark ridges, canopy scallops, outline weight) on the redwood
- [ ] Scene mockup (`scene.py`): planet ground + placed objects, back to front, 1x and 3x
- [ ] Buildings: box / prism / dome parts, south-wall door and window parts, roof patterns, storey bands
- [ ] Walkable pieces: platforms, bridges (top-layer deck, the player walks on them)
- [ ] Metatile export: bottom/top layers + ground underlay, attributes, append to a planet secondary (with tile-generator `install`)
- [ ] Interiors (room kits), later

## Area 1: Bright Tree Village (Endor, vanilla Fortree City, 40x20)

Catalogue rows: `wiki/mapping/world_art.csv` planet ENDOR. Concept art: `wiki/art/concept/endor/`.

| Concept | Model | Status |
|---|---|---|
| redwood-trunk (3x4, edge) | `models/endor/redwood-trunk.yaml` | [~] first render |
| fern-undergrowth (1x1, walkable) | | [ ] |
| fallen-log (3x1, edge) | | [ ] |
| ewok-hut (3x3, landmark) on a platform | | [ ] |
| rope-bridge (1x1, walkable) | | [ ] |
| totem-and-drum (1x2, noise) | | [ ] |
| ewok-glider (1x2, noise) | | [ ] |
| log-trap (3x1), crashed-speeder-bike (2x1), at-st-wreck (3x3) | | [ ] route props, after the village |
| scene `bright-tree-village.yaml` | | [ ] |

## Later areas (same order of work per area)

Kachirho (Kashyyyk), Tatooine towns, Sullust, Hoth, Dagobah, Kamino, Death Star, Grand Arena: see
`wiki/mapping/world_art.csv`.
