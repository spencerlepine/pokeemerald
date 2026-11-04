# world_port

Ports the wiki world (`wiki/world/`) into `../game`: terrain, buildings and props, warps, connections and
people. Run from the repo root:

```sh
python3 wiki/tools/port_world.py install TATOOINE -mos-pelgo   # planets or area ids; -AREA leaves one out
cd game && make -j4
```

It always starts from the vanilla snapshot (commit `c663bddf`, extracted once into `.base/`, not committed), so
it can run again and gives the same files. Areas outside the run keep their vanilla maps.

## What it writes

- **Terrain** (`terrain.py`). A vanilla map with the same grid keeps its vanilla cells; a route or cave with a few
  cells changed (hybrid) keeps vanilla cells where the grid is unchanged; a redrawn town and every new area is
  drawn from the grid with tile-generator's terrain items. A terrain role the tileset pair has no tile for
  (Dune Sea, wroshyr trunks...) is the pink placeholder over a grey fill, its own metatile per role. So is a
  ground or water cell whose learned vanilla tile does something underfoot (a door, warp, slide, ladder...).
  Interiors keep their vanilla cells (no planet kit indoors).
- **Pieces** (`pieces.py`). Every building and sized prop is solid, drawn with its building-kit render, else its
  greybox render, else the pink placeholder, one metatile per cell. A building's door cell warps (non-animated
  door). In a vanilla or hybrid map only pieces set on ground vanilla has open are drawn (vanilla buildings keep
  their tiles), and a redrawn building moves up to 3 cells so its door is the vanilla door (scripts use it).
- **Tilesets** (`tiles.py`, `pins.py`). An area with new metatiles gets its own secondary tileset in
  `data/tilesets/secondary/sw/<area-id>/`, declared in `src/data/tilesets/sw_*.h`. A map that replaces a vanilla
  one keeps every vanilla metatile id, the tiles scripts name (`metatile_labels.h`) and the animated tiles; new
  tiles take the unused slots. New tiles use one grey and magenta palette in a free slot.
- **Layouts**. A map's own vanilla layout is rewritten in place; a shared one or a new area gets
  `LAYOUT_SW_<ID>`.
- **Warps and connections** (`warps.py`). A map that replaces a vanilla one keeps every vanilla warp at its index
  (scripts, heal spots and other maps name warps by index): each wiki door takes the vanilla warp at its cell or
  to the same place, new doors come after, a vanilla warp with no wiki door stays where it was (inert on a
  blocked cell in a redrawn map). A map edge in `exits:` connects to the area it names, the offset from the two
  areas' `pos`.
- **New maps** go in `gMapGroup_StarWars` (`MAP_SW_<ID>`), with the music and map section of the nearest vanilla
  map they are reached from. **Music** set in `mapping/music.csv` `maps` wins on every map the port writes (a new
  area by `map:<id>`, a vanilla map by its map id): the per-planet splits and the songs of new areas.
- **People and signs** (`events.py`). Vanilla and hybrid maps keep their vanilla objects (one under a new building
  moves to the nearest open cell, unless a script places it). A yaml person with no vanilla object on its cell,
  and every person of a new map, is a new object with a script from `mapping/people.csv` (lines, trainer, boss,
  wild battle, flag). A `character:mart-clerk` sells the `item:` tokens of its party column, else a stock
  set by the planet's badges on arrival; a `character:nurse` heals like a Bacta Center nurse. Scripts and texts go in a managed block of the map's `scripts.inc`; a people.csv row with `npc_id` `npc:<vanilla map>:<n>`
  takes over vanilla object n: its walker, and its lines when the vanilla script only talks. A `flag` of
  `hide:FLAG_X` makes it the object's flag (a road warden stands until the story sets FLAG_X). A label of the same name
  written by hand outside the block replaces the generated one. An `Item ball` person takes the area's next
  `item_ball` row of `mapping/obtain_extra.csv` (item and flag).

- **Redrawn towns** (`towns.py`). A redrawn town keeps every vanilla object, trigger and sign; a hand-checked spec,
  `towns/<area-id>.yaml`, says where each goes on the wiki layout (a yaml person, a cell, or dropped), rewrites the
  story movements (`movements:`, steps like `D8 d7 r21 u ifr`), patches script lines (also in other maps, such as
  the gym's warp back to its door), sets the heal spot, and walks each listed movement on the new layout to check it
  ends where it should and crosses no solid cell. Ported: every Tatooine town, Kachirho, Inyusu Tor, Pirin, Bright Tree, Yavin 4, Tipoca City, Ilum, Cloud City,
  Dagobah. A map holds at most 64 objects; the rest are left out with a note.

Art stays pending in the wiki: a placeholder or greybox tile goes in as a real tile in its own slot, so it can
be redrawn later without touching the maps.

- **Hyperlanes** (`lanes.py`, from `mapping/hyperlanes.csv`). A shared cabin (one room for both ends) shuts the
  exit the player did not come in by until its pilot has flown; the pilot flies only once the lane's `unlock` is
  met (the way back is always open). A one-door hangar's pilot offers every lane that touches the room, one by
  one, and lands the player on the far room's first warp. Lanes vanilla already flies are left alone: Han's
  first hop, the cable car, the S.S. Tidal and its ticket islands. Han's boat sails are hyperspace hops
  (patches in `towns/kachirho.yaml`). A new `unlock` token needs its game flag in `lanes.UNLOCK`.

The game's `ld_script.ld` no longer pins the creature pics to fixed addresses: the full world does not fit
below them.

## Check

`tools/play-tester/scripts/world-check.sh SPOTS` teleports to each spot (`name group num x y [KEYS]`), presses
the keys (`VAR4057=2` and `FLAG2D6=0` among them set a story var or flag before the teleport) and screenshots it into `tools/play-tester/out/world/`. `WORLD_TRACE=1` logs the map and cell after every
step. Run `UI_ROM=$PWD/game/pokeemerald.gba tools/play-tester/scripts/ui-check.sh boot` after each build first.
