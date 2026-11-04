# building-kit: outdoor buildings from a kit of parts

Status: **278 greybox buildings drawn (2026-11-04), in review with the owner**: every building the areas
place (177) plus 97 town fill pieces and 4 signs, on 14 planets, all fitting their lots. Shapes and light
only, no colour or texture. `build` writes `../../wiki/mapping/buildings.csv` and
`../../wiki/world/buildings/`; nothing goes into `../../game` yet.

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
python3 -m bkit init                                  # a catalog entry for every area building that has none
python3 -m bkit build --planet tatooine --no-wiki     # render a planet's catalog to output/build/ (+ _sheet_<file>.png)
python3 -m bkit build [--only mos-eisley]             # render into the wiki (buildings.csv, pngs)
python3 -m bkit collage                               # every building on one image (wiki/world/buildings/_collage.png)
```

## The catalog: every building the game needs

`catalog/<file>.yaml` holds one entry per building design, with the planet at the top (a planet may be
split over several files). `init` makes an entry for each `buildings:` item in the area yamls
(`../../wiki/world/<planet>/<area>.yaml`): its lot `size` (drawn cells, W x H) and `door` column come from
the area. Extra buildings that no area places yet (markets, huts, the fill of a town) are entries with
`areas: []` and kind `fill`, `market` or `hut`. Every entry names its `blueprint` and `seed`, so each
building is its own design, even when twenty homes share one blueprint. The format is in
`bkit/catalog.py`.

`build` renders each entry at its lot's width with `H` (lot height) and `door_x` (the area's door) in the
blueprint's params, then checks it: drawn no taller than the lot (shorter is padded at the top), the
ground it stands on (`footprint`, W x rows from the front: the hit box) no deeper than the lot, the
door in the area's column. `buildings.csv` gets `size`, `drawn`, `footprint`, `door`, `door_found`, `fits`,
`tiles` and the png, so placing a building later only needs that row.

Every kind of building is redrawn per planet in that planet's style: each planet has its own Bacta
Center (always 5x4), Supply Depot (always 4x4) and arena (any shape). The sign in front of an arena,
Bacta Center or depot says what it is (the `sign` piece, placed with the building later), so the
buildings themselves can vary.

## Designing a planet

1. Read the planet's rows in `../../wiki/mapping/world_art.csv` (`description`) and look at its concept
   images in `../../wiki/art/concept/<planet>/`. Design from the films, never from Earth or Hoenn.
2. Write the planet's pieces in `kits/<planet>.yaml` (a kit lists `uses:` for other kits) and its
   building families in `blueprints/<planet>/`. A blueprint should give several clearly different
   buildings: two or more massing options, roof options, door styles, extras.
3. Size to the lot. Drawn rows = plan depth + height (+ a dome or roof rising above): a 5x4 lot is about
   2.3 m deep and 1.4 m of wall plus 0.3 m of roof. Use `H`, `W`, `w_max` in expressions. Put the
   entry named `door` at `door_x` when it is not None.
4. Keep it big and simple: doors about a cell wide, windows half a cell or more, nothing thinner than
   4 px, about 30 to 70 unique tiles a building (a tileset has 512).
5. `build --planet <p> --no-wiki` and look at `output/build/_sheet_<file>.png` until every entry fits
   and reads well.

Everything is written to `output/` (not committed).

## Files

- `kits/common.yaml`: materials (greybox ramps) and the pieces every style uses: `door-arch`, `door-slab`,
  `window-round`, `window-slot`, `vent`, `crate`.
- A blueprint part can carve with `op: subtract`; to carve only some parts, give them their own
  `group` plus `_new_group: true` (the pit of `courtyard-home`, the shell of `ruin`). The build finds the
  door from the `at` of the entry named `door`, so make the door a template use (`gate-gap`, `bay-door`).
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
| `bacta-center` | Mos Espa / Mos Eisley civic blocks | hall with a big dome, rotunda between wings, or hall between drum towers; wide slab, arch or porch door; beacon |
| `supply-depot` | Watto's shop | shop block, big dome behind a shop front, or stepped block; shade canopy or buttressed jambs; crates |
| `courtyard-home` | The Lars sunken courtyard | round pit with a rim, inner doorways, dome, drum or block entrance, rim vents or a store dome |
| `lars-home` | The Lars homestead garage | entrance dome on a drum, garage vault with a wide bay, the X-34 out front, vaporators |
| `farm-co-op` | Anchorhead | long hall, vaulted, banded or domed roof, storage drum, 2-4 vaporators behind |
| `gatehouse` | Mos Espa town gates | long block with a big arch, round or square towers, guard room or dome; taller lots, taller towers |
| `canopy-house` | Mos Espa backstreets | small dome or block beside a sloped shade canopy over crates, a tank or a bench |
| `landing-pad` | Mos Espa pads | round pad with a ring, dome or block control hut, beacon mast |
| `ruin` | The burned Lars farm | hollow dome with its roof caved in, wall stubs, rubble, a dead vaporator |
| `speeder-garage` | Watto's yard, podracer hangars | block or vault with a wide bay, a speeder or podracer engine out front |
| `walled-compound` | Mos Espa back streets | low wall round a yard with a gate, dome, block or twin houses, vaporator or trough |
| `market-row` | Mos Espa marketplace | 2-4 stalls under sloped awnings, pots or crates, a back wall on some |
| `water-tower` | Anchorhead water sellers | tall drum or tank on legs over a pump house, dome or flat cap, pipe |
| `jawa-stand` | The Jawas' droid sale | sloped tarp over salvage, an astromech or labour droid, a crate counter |
| `dome-row` | Mos Espa slave quarters | long low block with 2-4 small domes, a door under each |

## Kamino

| Blueprint | From the films | Varies |
|---|---|---|
| `stilt-dome` | Tipoca City saucers on stilts | plain, two-tier, twin pod, mast or lens body; dome, hub or cupola top; window band; 2-4 stilts |
| `hall` | The Tipoca main complex | great drum or domed capsule centre, capsule or saucer wings, 0-2 spire towers, entry pod |
| `capsule-block` | Tipoca barracks and store rooms | length, one or two tiers, pod or cargo door, end saucer pod, roof drum or mast, crates |
| `medbay` | Tipoca medical bays, bacta tanks | saucer, lens or capsule head on a glass drum, 0-2 bacta tanks, hub, entry hood |
| `platform` | The Tipoca landing pad | landing ring, rim lamps, access tube, control pod or mast; narrow ones are walkway hubs with rails |
| `storm-tower` | Tipoca's columns | one or two saucer heads, beacon, side pod |

## Hoth

| Blueprint | From the films | Varies |
|---|---|---|
| `ice-hangar` | The Echo Base hangar door | cliff skyline, door width and opening, ice overhang or snow lip, hatch, dish or stacks |
| `prefab` | Echo Base prefab buildings | module, stacked modules, arched quonset (one or two) or dome bunker; hatch or cargo door; drifts, dish, stacks, crates |
| `shelter` | The tauntaun pens | 1-3 snow-covered arched vaults with a dark mouth, berms, lamp, crates |
| `pad` | The landing area outside Echo Base | cross or bar markings, control module, fuel tanks or beacon mast, drifts |
| `sensor-tower` | The Echo Base ridge dishes, the generators | dish post or pole antenna over a hut, or a generator shed with stacks |

## Ilum

The Ilum kit uses the Hoth kit (`ice-block`, `drift`).

| Blueprint | From the films | Varies |
|---|---|---|
| `temple-gate` | The Ilum temple (Jedi: Fallen Order) | cliff skyline, monolith size, flanking pylons, 2-4 kyber clusters, steps |
| `stone-hall` | Jedi stone buildings, the Coruscant temple | base steps, snow-capped hipped or pyramid roof, stepped tier with a crystal, one or two spires, wing, crystal lamps |
| `ice-hut` | Shelters cut into the glacier | faceted mound, cut block or two blocks; Jedi or arched door; crystals, crates |
| `pad` | The landing shelf below the temple | emblem ring, crystal beacons or obelisks, drifts |

## Bespin

The Bespin kit's `oval` is a 12-sided squashed prism: a round tower shows five lit facets from the front.
Window bands are a dark ring broken by `oval-pier`s (a `repeat` in the blueprint).

| Blueprint | From the films | Varies |
|---|---|---|
| `cloud-tower` | Cloud City towers | drum, tapered, stacked or flared body; 1-3 window bands; saucer, glass dome, rings, spire or mast top; two wings, one wing, lift pylon or ribs; base ring; plain, canopy or porch door |
| `cc-hall` | The Galleria, Cloud City halls | long oval hall with bands; lid, saucer or terrace roof; domed atrium, glass front, end drums or plain |
| `landing-pad` | The Falcon's platform | round or eight-sided deck, landing ring, front ramp, one or two cloud cars or cargo, beacons |
| `works` | The Tibanna works, the carbon-freezing level | refinery block with stacks and tank, annex under a cone hood, Ugnaught shed, or tank row |
| `garage` | Cloud car bays | vaulted or oval hangar, wide mouth, a cloud car beside it or fuel and crates |

## Grand Arena

Lando's island in gold and white. The kit uses the Bespin kit and adds `ga-column`, `disc-roof` and `ga-steps`.

| Blueprint | From the films | Varies |
|---|---|---|
| `resort-hall` | Cloud City halls, gold-trimmed | disc, stepped or gold roof; column portico, glazed arcade, window band or door columns; rotunda, twin towers, gold dome or lantern |
| `pavilion` | Cloud City pods | mushroom disc, gold dome, stepped crown or cone roof; door columns, window band or plain |
| `spire-hall` | Stacked saucers of the concept art | 2-3 drums under gold-rimmed discs; gold dome, spire or saucer top; column or canopy porch |

A catalog `set:` is applied after every `choose` is worked out, so expressions that read a set param (sizes,
height budgets) still see the seed's own pick. The Bespin and Grand Arena entries use seeds whose own picks
are the wanted ones, with no `set`.

## Earlier notes

More Tatooine bases (walled courtyard, docking-bay ring, garage, market awning), then a kit per planet
(Imperial, Wookiee, Ewok, Kamino, Bespin, Sullust, Yavin, Hoth). Once the owner approves the look, the kit
takes over the 40 `building` rows in `../../wiki/mapping/world_art.csv` (after the world-art greybox pass
on those rows, coordinated with that work), and an export writes each building's tiles for the
tile-generator.
