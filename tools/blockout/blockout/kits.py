"""World kits: everything the world needs drawn that is not terrain, a building, a room shell or a room
object. One row per item and planet in wiki/mapping/world_kits.csv (`kit:<category>:<planet>:<item>`).

The rows are wired to areas by a scan, not by hand: `scan()` reads every area yaml and, for areas built
into a vanilla map, that map in ../game (object events, metatile behaviours, warps, tilesets, weather,
border, secret-base spots). Each hit is a (category, item) for the area's planet. `python3 -m blockout kits`
writes `used_in` and `areas` and lists hits with no row (`--add` writes those rows from the templates
below). `blockout check` fails if a hit has no row, a row is used by no area, or a placeholder is missing.

Categories (the `category` column):
  field-object   sprites on the map the player moves, cuts, smashes or picks up (boulders, item pods...)
  mechanic       special floor tiles with a rule (ice, cracked floor, currents, slopes, warps in gyms...)
  door           door animations, one per planet and building kind
  warp           ladders, holes, escalators, cave mouths, dive doors, lifts
  tile-anim      animated tiles (water, waterfalls, flowers, lava, flags, lights...)
  underwater     the dive maps' seafloor kit
  battle-bg      battle backgrounds, one per planet and environment, plus the special ones
  hideout        hideout entrances per planet and the hideout decorations
  location-ui    the map name popup frame and the StarNAV region map, per planet
  field-effect   effects drawn on the player's tile (footprints, grass rustle, splashes...)
  weather        weather overlays per planet
  border         the tiles drawn past the map edge, per planet
  field-prop     big moving props in story scenes (the star liner, the cargo hauler, the shuttle...)
  interactive    interior tiles with a script (wall maps, bookshelves, trash cans, surveys)
"""
import csv
import glob
import json
import re
from collections import defaultdict

import yaml

from .vanilla import GAME, ROOT

PATH = ROOT / "wiki" / "mapping" / "world_kits.csv"
COLS = ["kit_id", "category", "planet", "item", "name", "emerald", "drawn", "hit_box", "used_in", "areas", "status",
        "tool", "description", "notes", "placeholder"]

# item -> (category, name, Emerald piece, drawn WxH, hit box (rooms.csv codes), tool, description)
ITEMS = {
    # field objects (object events)
    "strength-boulder": ("field-object", "Strength boulder", "OBJ_EVENT_GFX_PUSHABLE_BOULDER", "1x1", "#", "vfx-generator", "A boulder the player shoves with STRENGTH."),
    "cut-tree": ("field-object", "Cut obstacle", "OBJ_EVENT_GFX_CUTTABLE_TREE", "1x1", "#", "vfx-generator", "A small growth the player slices with CUT, in the planet's flora."),
    "smash-rock": ("field-object", "Smash rock", "OBJ_EVENT_GFX_BREAKABLE_ROCK", "1x1", "#", "vfx-generator", "A cracked rock the player breaks with ROCK SMASH."),
    "item-pod": ("field-object", "Item pod", "OBJ_EVENT_GFX_ITEM_BALL", "1x1", "#", "vfx-generator", "A capture-pod shaped item container on the ground."),
    "fruit-tree": ("field-object", "Fruit plant", "OBJ_EVENT_GFX_BERRY_TREE and MB_BERRY_TREE_SOIL", "1x2", "o/#", "vfx-generator", "A fruit plant in a soil patch, with its growth stages."),
    "puzzle-statue": ("field-object", "Puzzle statue", "OBJ_EVENT_GFX_TRICK_HOUSE_STATUE", "1x2", "o/#", "vfx-generator", "Statue the Puzzle House uses as a pushable block."),
    # mechanics (metatile behaviours)
    "ice-floor": ("mechanic", "Slide floor", "MB_ICE", "1x1", ".", "tile-generator", "Slippery floor: the player slides until something stops them."),
    "thin-ice": ("mechanic", "Cracking floor", "MB_THIN_ICE, MB_CRACKED_ICE", "1x1", ".", "tile-generator", "Floor that cracks when stepped on and breaks the second time."),
    "cracked-floor": ("mechanic", "Crumbling floor", "MB_CRACKED_FLOOR, MB_CRACKED_FLOOR_HOLE", "1x1", ".", "tile-generator", "Floor that falls away unless the player speeds over it."),
    "current": ("mechanic", "Water current", "MB_*WARD_CURRENT", "1x1", "~", "tile-generator", "Fast water that carries the surfing player along."),
    "waterfall": ("mechanic", "Waterfall", "MB_WATERFALL", "1x1", "~", "tile-generator", "Falling water climbed with WATERFALL."),
    "muddy-slope": ("mechanic", "Slide slope", "MB_MUDDY_SLOPE", "1x1", "s", "tile-generator", "Slope only a fast swoop bike can climb."),
    "bumpy-slope": ("mechanic", "Bumpy slope", "MB_BUMPY_SLOPE", "1x1", "s", "tile-generator", "Rough slope crossed by hopping the speeder bike."),
    "bike-rail": ("mechanic", "Bike rail", "MB_*_RAIL", "1x1", ".", "tile-generator", "Narrow rail the speeder bike balances along."),
    "deep-sand": ("mechanic", "Deep sand", "MB_DEEP_SAND", "1x1", ".", "tile-generator", "Sinking sand that slows the player."),
    "hot-spring": ("mechanic", "Hot spring", "MB_HOT_SPRINGS", "1x1", ".", "tile-generator", "Warm pool the player wades into."),
    "slide-tile": ("mechanic", "Push tile", "MB_SLIDE_SOUTH", "1x1", ".", "tile-generator", "Tile that pushes the player one way."),
    "spin-warp": ("mechanic", "Teleport pad", "MB_MOSSDEEP_GYM_WARP", "1x1", "d", "tile-generator", "Pad that beams the player to another pad."),
    "sand-geyser": ("mechanic", "Steam vent warp", "MB_LAVARIDGE_GYM_1F_WARP, MB_LAVARIDGE_GYM_B1F_WARP", "1x1", "d", "tile-generator", "Vent that shoots the player to the floor above, or a sand pit that drops them."),
    "pyramid-warp": ("mechanic", "Maze warp", "MB_BATTLE_PYRAMID_WARP", "1x1", "d", "tile-generator", "Floor glyph that sends the player to the next maze floor."),
    "hideout-warp": ("mechanic", "Hideout warp pad", "MB_AQUA_HIDEOUT_WARP", "1x1", "d", "tile-generator", "Warp pad in the hideout maze."),
    "puzzle-door": ("mechanic", "Puzzle door", "MB_TRICK_HOUSE_PUZZLE_DOOR, MB_TRICK_HOUSE_PUZZLE_8_FLOOR", "1x2", "o/d", "tile-generator", "The Puzzle House's scroll door and puzzle floor."),
    "rotating-gate": ("mechanic", "Rotating gate", "rotating_gate.c (Fortree Gym, Trick House 6)", "4x4", "####/####/####/####", "vfx-generator", "Turnstile arms that turn as the player pushes them."),
    "electric-gate": ("mechanic", "Charged gate", "Mauville Gym barriers (mauville_gym anim)", "1x1", "#", "tile-generator", "Crackling barrier flipped by floor switches."),
    "impassable-edge": ("mechanic", "One-way edge", "MB_IMPASSABLE_*", "1x1", ".", "tile-generator", "Railing or rope that blocks one side of a tile."),
    "no-running": ("mechanic", "No running floor", "MB_NO_RUNNING", "1x1", ".", "tile-generator", "Floor where the player cannot run."),
    "bike-bridge": ("mechanic", "Bike-only bridge", "MB_BIKE_BRIDGE_OVER_BARRIER", "1x1", ".", "tile-generator", "Bridge crossed only on the bike."),
    "log-bridge": ("mechanic", "Sinking log bridge", "MB_PACIFIDLOG_*_LOG_*", "1x1", ".", "tile-generator", "Floating walkway that dips when stepped on."),
    "puddle": ("mechanic", "Puddle", "MB_PUDDLE", "1x1", ".", "tile-generator", "Shallow puddle that splashes."),
    "pyre-hole": ("mechanic", "Drop hole", "MB_MT_PYRE_HOLE", "1x1", "d", "tile-generator", "Hole in the floor that drops the player a level."),
    "trainer-timer": ("mechanic", "Timer panel", "MB_TRAINER_HILL_TIMER", "1x1", "#", "tile-generator", "Start and goal timer of the Trial Spire."),
    # doors (field_door.c animations; one per planet and building kind)
    "door-home": ("door", "Home door", "door_anims (Littleroot, Oldale, Rustboro...)", "1x2", "o/d", "vfx-generator", "Door of the planet's homes, opening in three frames."),
    "door-bacta": ("door", "Bacta Center door", "door_anims/pokemon_center", "1x2", "o/d", "vfx-generator", "Sliding Bacta Center door, in the planet's town material."),
    "door-depot": ("door", "Supply Depot door", "door_anims/pokemart", "1x2", "o/d", "vfx-generator", "Sliding Supply Depot door."),
    "door-arena": ("door", "Arena door", "door_anims/gym", "1x2", "o/d", "vfx-generator", "The arena's big door."),
    "door-hangar": ("door", "Hangar door", "door_anims (harbor, space center)", "1x2", "o/d", "vfx-generator", "Blast door into a hangar or landing bay."),
    "door-landmark": ("door", "Landmark door", "door_anims (museum, dept store, league...)", "1x2", "o/d", "vfx-generator", "Door of a big unique building (palace, temple, tower, lab)."),
    "door-shop": ("door", "Shop door", "door_anims (bike shop, flower shop...)", "1x2", "o/d", "vfx-generator", "Door of a small shop or market stall."),
    "door-interior": ("door", "Inner door", "door_anims (abandoned ship, elevators, battle facilities)", "1x2", "o/d", "vfx-generator", "Animated door between two rooms."),
    # warps
    "ladder": ("warp", "Ladder", "MB_LADDER", "1x1", "d", "tile-generator", "Ladder or hatch to another level."),
    "escalator": ("warp", "Moving walkway", "MB_UP_ESCALATOR, MB_DOWN_ESCALATOR", "2x2", "ss/dd", "tile-generator", "Moving stairs between floors."),
    "cave-mouth": ("warp", "Cave mouth", "MB_CAVE and cave warps", "1x1", "d", "tile-generator", "Entrance into a cave or tunnel from the overworld."),
    "dive-door": ("warp", "Dive door", "MB_WATER_DOOR, MB_WATER_SOUTH_ARROW_WARP", "1x1", "d", "tile-generator", "Doorway reached under water."),
    "drop-hole": ("warp", "Hole down", "MB_CRACKED_FLOOR_HOLE, MB_DEEP_SOUTH_WARP, MB_FALL_WARP", "1x1", "d", "tile-generator", "Hole the player drops through."),
    "lift": ("warp", "Lift", "elevator maps (dept store, Battle Tower, Trainer Hill)", "2x2", "oo/dd", "vfx-generator", "Lift doors and the lift's floor display."),
    "sealed-door": ("warp", "Sealed door", "MB_SKY_PILLAR_CLOSED_DOOR, the Sealed Chamber door", "1x2", "o/#", "tile-generator", "A door that opens after a story event."),
    # animated tiles (tileset_anims.c)
    "anim-water": ("tile-anim", "Water shimmer", "general/anim/water", "1x1", "~", "tile-generator", "The surface of the planet's water, 8 frames."),
    "anim-water-edge": ("tile-anim", "Shore lapping", "general/anim/land_water_edge, sand_water_edge", "1x1", "~", "tile-generator", "Water lapping at the shore."),
    "anim-waterfall": ("tile-anim", "Waterfall flow", "general/anim/waterfall", "1x1", "~", "tile-generator", "Falling water frames."),
    "anim-flower": ("tile-anim", "Swaying plants", "general/anim/flower, mauville flowers, ever_grande flowers", "1x1", ".", "tile-generator", "Small plants that sway on walkable ground."),
    "anim-lava": ("tile-anim", "Lava flow", "cave/anim/lava", "1x1", "~", "tile-generator", "Glowing lava frames."),
    "anim-steam": ("tile-anim", "Steam vents", "lavaridge/anim/steam", "1x1", ".", "tile-generator", "Steam rising from vents."),
    "anim-flag": ("tile-anim", "Banners", "dewford, battle frontier flags", "1x1", "#", "tile-generator", "Banners waving on poles."),
    "anim-fountain": ("tile-anim", "Fountain", "rustboro/anim/fountain", "1x1", "#", "tile-generator", "Fountain jet."),
    "anim-windy-water": ("tile-anim", "Windblown water", "rustboro/anim/windy_water", "1x1", "~", "tile-generator", "Rippling water in a wind."),
    "anim-balloons": ("tile-anim", "Floating lights", "slateport/anim/balloons", "1x1", "#", "tile-generator", "Market lanterns bobbing."),
    "anim-stormy-water": ("tile-anim", "Storm water", "sootopolis/anim/stormy_water", "1x1", "~", "tile-generator", "Water churned by the titans' storm."),
    "anim-log-bridge": ("tile-anim", "Bobbing walkway", "pacifidlog/anim/log_bridges", "1x1", ".", "tile-generator", "Floating walkway bobbing."),
    "anim-current": ("tile-anim", "Current flow", "pacifidlog/anim/water_currents", "1x1", "~", "tile-generator", "Arrows of fast water."),
    "anim-seaweed": ("tile-anim", "Swaying sea plants", "underwater/anim/seaweed", "1x1", ".", "tile-generator", "Sea plants swaying under water."),
    "anim-torch": ("tile-anim", "Torches", "battle_pyramid/anim/torch, statue_shadow", "1x1", "#", "tile-generator", "Flickering torches."),
    "anim-floor-lights": ("tile-anim", "Floor and wall lights", "elite_four/anim/floor_light, wall_lights", "1x1", ".", "tile-generator", "Pulsing lights in floors and walls."),
    "anim-electric-gates": ("tile-anim", "Charged gate crackle", "mauville_gym/anim/electric_gates", "1x1", "#", "tile-generator", "Crackling barrier frames."),
    "anim-blinking-lights": ("tile-anim", "Blinking panels", "bike_shop/anim/blinking_lights", "1x1", "#", "tile-generator", "Blinking console lights."),
    "anim-screen-on": ("tile-anim", "HoloNet screen on", "building/anim/tv_turned_on", "1x1", "#", "tile-generator", "A screen switched on."),
    "anim-gym-waterfall": ("tile-anim", "Arena falls", "sootopolis_gym/anim/front_waterfall, side_waterfall", "1x1", "~", "tile-generator", "Falls inside Yoda's arena."),
    # underwater
    "seafloor": ("underwater", "Seafloor", "underwater tileset floor", "1x1", ".", "tile-generator", "Seabed the diving player swims over."),
    "seaweed": ("underwater", "Sea plants", "MB_SEAWEED, MB_SEAWEED_NO_SURFACING", "1x1", ".", "tile-generator", "Tall sea plants where wild companions hide."),
    "sea-rock": ("underwater", "Sea rock wall", "underwater tileset walls", "1x1", "#", "tile-generator", "Rock that walls the dive routes."),
    "surface-spot": ("underwater", "Surfacing light", "dark/light water patches", "1x1", ".", "tile-generator", "Light from above where the player can surface."),
    # battle backgrounds (BattleSetup_GetEnvironmentId)
    "bg-grass": ("battle-bg", "Battle: grass", "battle_environment/tall_grass", "15x10", "", "tile-generator", "Background for battles in encounter grass."),
    "bg-long-grass": ("battle-bg", "Battle: long grass", "battle_environment/long_grass", "15x10", "", "tile-generator", "Background for battles in long grass."),
    "bg-sand": ("battle-bg", "Battle: sand", "battle_environment/sand", "15x10", "", "tile-generator", "Background for battles on sand."),
    "bg-water": ("battle-bg", "Battle: open water", "battle_environment/water", "15x10", "", "tile-generator", "Background for battles while surfing."),
    "bg-pond": ("battle-bg", "Battle: pond", "battle_environment/pond_water", "15x10", "", "tile-generator", "Background for battles on calm water."),
    "bg-rock": ("battle-bg", "Battle: rock", "battle_environment/rock", "15x10", "", "tile-generator", "Background for battles on rocky heights."),
    "bg-cave": ("battle-bg", "Battle: cave", "battle_environment/cave", "15x10", "", "tile-generator", "Background for battles in caves."),
    "bg-building": ("battle-bg", "Battle: indoors", "battle_environment/building", "15x10", "", "tile-generator", "Background for battles inside."),
    "bg-underwater": ("battle-bg", "Battle: under water", "battle_environment/underwater", "15x10", "", "tile-generator", "Background for battles while diving."),
    "bg-plain": ("battle-bg", "Battle: open ground", "battle_environment/plain", "15x10", "", "tile-generator", "Background for battles on plain ground."),
    "bg-arena": ("battle-bg", "Battle: arena", "battle_environment/gym and leader", "15x10", "", "tile-generator", "The planet's arena floor for leader battles."),
    "bg-special": ("battle-bg", "Battle: special", "battle_environment magma, aqua, sidney, phoebe, glacia, drake, champion, groudon, kyogre, rayquaza, frontier", "15x10", "", "tile-generator", "Story backgrounds: the Empire, the Cartel, the four trials, Obi-Wan, the titans, the Grand Arena."),
    # hideout
    "hideout-spot": ("hideout", "Hideout entrance", "MB_SECRET_BASE_SPOT_*", "1x2", "o/d", "tile-generator", "Where the player opens a hideout: a hollow in the planet's rock, tree or bush."),
    "hideout-interior": ("hideout", "Hideout interior", "secret base layouts (cave, tree, shrub)", "11x9", "", "", "The empty hideout room behind each entrance kind."),
    # location ui
    "map-popup": ("location-ui", "Map name popup", "graphics/map_popup (frame styles)", "5x2", "", "", "The frame the area name slides in on, one style per planet."),
    "region-map": ("location-ui", "StarNAV map section", "graphics/pokenav/region_map", "15x10", "", "", "The planet's panel on the StarNAV galaxy map, with town and route icons."),
    # field effects
    "fx-footprints": ("field-effect", "Footprints", "field_effects sand footprints", "1x1", ".", "vfx-generator", "Footprints the player leaves in sand or snow."),
    "fx-grass-rustle": ("field-effect", "Grass rustle", "field_effects tall_grass", "1x1", ".", "vfx-generator", "Encounter growth rustling as the player walks through."),
    "fx-long-grass": ("field-effect", "Long grass rustle", "field_effects long_grass", "1x1", ".", "vfx-generator", "Tall growth closing over the player."),
    "fx-ash": ("field-effect", "Ash puff", "field_effects ash", "1x1", ".", "vfx-generator", "Ash kicked up from ash-covered growth."),
    "fx-splash": ("field-effect", "Splash", "field_effects splash, ripple", "1x1", ".", "vfx-generator", "Splash and ripple in puddles and shallow water."),
    "fx-sand-pile": ("field-effect", "Sinking sand", "field_effects deep_sand", "1x1", ".", "vfx-generator", "Sand around the player's feet in deep sand."),
    "fx-hot-spring": ("field-effect", "Hot-spring steam", "field_effects hot_springs_water", "1x1", ".", "vfx-generator", "Water ring and steam around the wading player."),
    "fx-bubbles": ("field-effect", "Dive bubbles", "field_effects bubbles", "1x1", ".", "vfx-generator", "Bubbles from the diving player."),
    # weather
    "weather-sun": ("weather", "Harsh sun", "WEATHER_SUNNY", "1x1", "", "vfx-generator", "Bright overlay and heat shimmer."),
    "weather-shade": ("weather", "Shade", "WEATHER_SHADE", "1x1", "", "vfx-generator", "Dim light under a canopy or cloud."),
    "weather-fog": ("weather", "Mist", "WEATHER_FOG_HORIZONTAL", "1x1", "", "vfx-generator", "Drifting mist layer."),
    "weather-ash": ("weather", "Ashfall", "WEATHER_VOLCANIC_ASH", "1x1", "", "vfx-generator", "Falling ash flakes."),
    "weather-bubbles": ("weather", "Bubbles", "WEATHER_UNDERWATER_BUBBLES", "1x1", "", "vfx-generator", "Rising bubbles under water."),
    "weather-sandstorm": ("weather", "Sandstorm", "WEATHER_SANDSTORM", "1x1", "", "vfx-generator", "Blowing sand over the desert routes."),
    "weather-rain": ("weather", "Rain", "WEATHER_RAIN, WEATHER_RAIN_THUNDERSTORM", "1x1", "", "vfx-generator", "Rain and storm."),
    "weather-snow": ("weather", "Snow", "WEATHER_SNOW (net:weather-blizzard)", "1x1", "", "vfx-generator", "Falling snow; a blizzard on the worst days."),
    # border
    "map-border": ("border", "Map edge fill", "layout border.bin", "2x2", "##/##", "tile-generator", "The 2x2 tiles drawn past the map edge, in the planet's border kit."),
    # field props (object events)
    "prop-star-liner": ("field-prop", "Star liner", "OBJ_EVENT_GFX_SS_TIDAL", "6x4", "", "vfx-generator", "The passenger liner at the docks."),
    "prop-cargo-hauler": ("field-prop", "Cargo hauler", "OBJ_EVENT_GFX_TRUCK", "3x3", "", "vfx-generator", "The family's moving transport in the opening."),
    "prop-shuttle-cab": ("field-prop", "Shuttle cab", "OBJ_EVENT_GFX_CABLE_CAR", "4x4", "", "vfx-generator", "The cab of the peak shuttle line."),
    "prop-sub-shadow": ("field-prop", "Sub shadow", "OBJ_EVENT_GFX_SUBMARINE_SHADOW", "4x2", "", "vfx-generator", "The Cartel sub's shadow under the water."),
    "prop-moving-box": ("field-prop", "Moving crate", "OBJ_EVENT_GFX_MOVING_BOX", "1x1", "#", "vfx-generator", "The family's crates in the hauler and the new home."),
    # interactive interior tiles (behaviours with a script)
    "wall-map": ("interactive", "Wall StarNAV map", "MB_REGION_MAP", "2x1", "##", "tile-generator", "Wall map that opens the galaxy map."),
    "bookshelf": ("interactive", "Datacard shelf", "MB_BOOKSHELF, MB_POKEMON_CENTER_BOOKSHELF, MB_PICTURE_BOOK_SHELF", "1x2", "o/#", "tile-generator", "Shelf the player reads from."),
    "trash-can": ("interactive", "Waste bin", "MB_TRASH_CAN", "1x1", "#", "tile-generator", "Bin with a joke or a hidden item."),
    "vase": ("interactive", "Jar", "MB_VASE", "1x1", "#", "tile-generator", "Jar the player looks into."),
    "survey-terminal": ("interactive", "Survey terminal", "MB_QUESTIONNAIRE", "1x1", "#", "tile-generator", "Terminal with the Holonet survey."),
    "blueprint": ("interactive", "Blueprint screen", "MB_BLUEPRINT", "1x1", "#", "tile-generator", "Engineering drawings on a screen."),
    "results-box": ("interactive", "Link results screen", "MB_WIRELESS_BOX_RESULTS, MB_CABLE_BOX_RESULTS_2", "1x1", "#", "tile-generator", "Screen of link battle records."),
    "shop-shelf": ("interactive", "Shop shelf", "MB_SHOP_SHELF", "1x1", "#", "tile-generator", "Shelf the player browses."),
    "game-table": ("interactive", "Game table", "MB_SLOT_MACHINE, MB_ROULETTE", "1x1", "#", "tile-generator", "Sabacc and jubilee wheel seats."),
}

BEH = {  # metatile behaviour -> (category, item)
    "MB_ICE": "ice-floor", "MB_THIN_ICE": "thin-ice", "MB_CRACKED_ICE": "thin-ice", "MB_CRACKED_FLOOR": "cracked-floor",
    "MB_CRACKED_FLOOR_HOLE": "drop-hole", "MB_EASTWARD_CURRENT": "current", "MB_WESTWARD_CURRENT": "current",
    "MB_NORTHWARD_CURRENT": "current", "MB_SOUTHWARD_CURRENT": "current", "MB_WATERFALL": "waterfall",
    "MB_MUDDY_SLOPE": "muddy-slope", "MB_BUMPY_SLOPE": "bumpy-slope", "MB_HORIZONTAL_RAIL": "bike-rail",
    "MB_VERTICAL_RAIL": "bike-rail", "MB_ISOLATED_HORIZONTAL_RAIL": "bike-rail", "MB_ISOLATED_VERTICAL_RAIL": "bike-rail",
    "MB_DEEP_SAND": "deep-sand", "MB_HOT_SPRINGS": ("hot-spring", "fx-hot-spring"), "MB_SLIDE_SOUTH": "slide-tile",
    "MB_MOSSDEEP_GYM_WARP": "spin-warp", "MB_LAVARIDGE_GYM_1F_WARP": "sand-geyser", "MB_LAVARIDGE_GYM_B1F_WARP": "sand-geyser",
    "MB_BATTLE_PYRAMID_WARP": "pyramid-warp", "MB_AQUA_HIDEOUT_WARP": "hideout-warp", "MB_TRICK_HOUSE_PUZZLE_DOOR": "puzzle-door",
    "MB_TRICK_HOUSE_PUZZLE_8_FLOOR": "puzzle-door", "MB_IMPASSABLE_EAST": "impassable-edge", "MB_IMPASSABLE_NORTH": "impassable-edge",
    "MB_IMPASSABLE_SOUTH": "impassable-edge", "MB_IMPASSABLE_SOUTH_AND_NORTH": "impassable-edge", "MB_NO_RUNNING": "no-running",
    "MB_BIKE_BRIDGE_OVER_BARRIER": "bike-bridge", "MB_PACIFIDLOG_HORIZONTAL_LOG_LEFT": "log-bridge",
    "MB_PACIFIDLOG_VERTICAL_LOG_TOP": "log-bridge", "MB_PUDDLE": "puddle", "MB_MT_PYRE_HOLE": "pyre-hole",
    "MB_TRAINER_HILL_TIMER": "trainer-timer", "MB_LADDER": "ladder", "MB_UP_ESCALATOR": "escalator",
    "MB_DOWN_ESCALATOR": "escalator", "MB_WATER_DOOR": "dive-door", "MB_WATER_SOUTH_ARROW_WARP": "dive-door",
    "MB_DEEP_SOUTH_WARP": "drop-hole", "MB_FALL_WARP": "drop-hole", "MB_SKY_PILLAR_CLOSED_DOOR": "sealed-door",
    "MB_SEAWEED": "seaweed", "MB_SEAWEED_NO_SURFACING": "seaweed", "MB_BERRY_TREE_SOIL": "fruit-tree",
    "MB_REGION_MAP": "wall-map", "MB_BOOKSHELF": "bookshelf", "MB_POKEMON_CENTER_BOOKSHELF": "bookshelf",
    "MB_PICTURE_BOOK_SHELF": "bookshelf", "MB_TRASH_CAN": "trash-can", "MB_VASE": "vase", "MB_QUESTIONNAIRE": "survey-terminal",
    "MB_BLUEPRINT": "blueprint", "MB_WIRELESS_BOX_RESULTS": "results-box", "MB_CABLE_BOX_RESULTS_2": "results-box",
    "MB_SHOP_SHELF": "shop-shelf", "MB_SLOT_MACHINE": "game-table", "MB_ROULETTE": "game-table",
    # surfaces -> field effects and battle backgrounds
    "MB_SAND": ("fx-footprints", "bg-sand"), "MB_DEEP_SAND": ("deep-sand", "fx-sand-pile", "bg-sand"),
    "MB_TALL_GRASS": ("fx-grass-rustle", "bg-grass"), "MB_LONG_GRASS": ("fx-long-grass", "bg-long-grass"),
    "MB_ASHGRASS": ("fx-ash", "bg-grass"), "MB_SHALLOW_WATER": "fx-splash", "MB_POND_WATER": ("bg-pond", "anim-water"),
    "MB_OCEAN_WATER": ("bg-water", "anim-water"), "MB_DEEP_WATER": ("bg-water", "anim-water"),
    "MB_INTERIOR_DEEP_WATER": "bg-water", "MB_MOUNTAIN_TOP": "bg-rock", "MB_NO_SURFACING": ("seafloor", "bg-underwater"),
}
for _k in ("MB_SECRET_BASE_SPOT_RED_CAVE", "MB_SECRET_BASE_SPOT_BROWN_CAVE", "MB_SECRET_BASE_SPOT_BLUE_CAVE",
           "MB_SECRET_BASE_SPOT_YELLOW_CAVE", "MB_SECRET_BASE_SPOT_TREE_LEFT", "MB_SECRET_BASE_SPOT_TREE_RIGHT",
           "MB_SECRET_BASE_SPOT_SHRUB"):
    BEH[_k] = "hideout-spot"
GFX = {"PUSHABLE_BOULDER": "strength-boulder", "CUTTABLE_TREE": "cut-tree", "BREAKABLE_ROCK": "smash-rock",
       "ITEM_BALL": "item-pod", "BERRY_TREE": "fruit-tree", "TRICK_HOUSE_STATUE": "puzzle-statue",
       "SS_TIDAL": "prop-star-liner", "TRUCK": "prop-cargo-hauler", "CABLE_CAR": "prop-shuttle-cab",
       "SUBMARINE_SHADOW": "prop-sub-shadow", "MOVING_BOX": "prop-moving-box"}
ANIM = {"general": ["anim-water", "anim-water-edge", "anim-waterfall", "anim-flower"], "building": ["anim-screen-on"],
        "mauville": ["anim-flower"], "ever_grande": ["anim-flower"], "lavaridge": ["anim-steam"], "cave": ["anim-lava"],
        "dewford": ["anim-flag"], "battle_frontier_outside_west": ["anim-flag"], "battle_frontier_outside_east": ["anim-flag"],
        "rustboro": ["anim-fountain", "anim-windy-water"], "slateport": ["anim-balloons"], "sootopolis": ["anim-stormy-water"],
        "pacifidlog": ["anim-log-bridge", "anim-current"], "underwater": ["anim-seaweed"], "battle_pyramid": ["anim-torch"],
        "elite_four": ["anim-floor-lights"], "mauville_gym": ["anim-electric-gates", "electric-gate"],
        "bike_shop": ["anim-blinking-lights"], "sootopolis_gym": ["anim-gym-waterfall"]}
WEATHER = {"WEATHER_SUNNY": "weather-sun", "WEATHER_SHADE": "weather-shade", "WEATHER_FOG_HORIZONTAL": "weather-fog",
           "WEATHER_FOG_DIAGONAL": "weather-fog", "WEATHER_VOLCANIC_ASH": "weather-ash", "WEATHER_UNDERWATER_BUBBLES": "weather-bubbles",
           "WEATHER_SANDSTORM": "weather-sandstorm", "WEATHER_RAIN": "weather-rain", "WEATHER_RAIN_THUNDERSTORM": "weather-rain",
           "WEATHER_DOWNPOUR": "weather-rain", "WEATHER_SNOW": "weather-snow", "WEATHER_ROUTE119_CYCLE": "weather-rain",
           "WEATHER_ROUTE123_CYCLE": "weather-rain", "WEATHER_SUNNY_CLOUDS": "weather-shade", "WEATHER_DROUGHT": "weather-sun",
           "WEATHER_FOG": "weather-fog"}
ROTATING_GATE_MAPS = {"FortreeCity_Gym", "Route110_TrickHousePuzzle6"}
SPECIAL_BG = {  # vanilla map prefix -> special battle background
    "SootopolisCity_Gym": "bg-arena", "PetalburgCity_Gym": "bg-arena", "RustboroCity_Gym": "bg-arena", "DewfordTown_Gym": "bg-arena",
    "MauvilleCity_Gym": "bg-arena", "LavaridgeTown_Gym": "bg-arena", "FortreeCity_Gym": "bg-arena", "MossdeepCity_Gym": "bg-arena",
    "MagmaHideout": "bg-special", "AquaHideout": "bg-special", "EverGrandeCity_SidneysRoom": "bg-special",
    "EverGrandeCity_PhoebesRoom": "bg-special", "EverGrandeCity_GlaciasRoom": "bg-special", "EverGrandeCity_DrakesRoom": "bg-special",
    "EverGrandeCity_ChampionsRoom": "bg-special", "SkyPillar_Top": "bg-special", "MarineCave_End": "bg-special",
    "TerraCave_End": "bg-special", "BattleFrontier_Battle": "bg-special"}
# planet words for the row text
LOOK = {"TATOOINE": "sand and sandstone", "KASHYYYK": "wroshyr wood and sea", "SULLUST": "basalt and ash",
        "MUSTAFAR": "lava rock and black metal", "ENDOR": "forest-moon timber and fern", "FELUCIA": "giant fungus",
        "BESPIN": "white Cloud City plating and cloud", "JEDHA": "pale desert stone", "YAVIN 4": "jungle and Massassi stone",
        "HOTH": "snow and ice", "DAGOBAH": "swamp mud and roots", "KAMINO": "white stilts and storm sea",
        "ILUM": "ice and kyber crystal", "GRAND ARENA": "gold and cream plaza", "TYTHON": "ancient Jedi stone and grass",
        "ATOLLON": "grey rock and the Bendu's spires", "MORTIS": "Force-realm rock and light",
        "ASTEROID FIELD": "pitted asteroid rock", "DEATH STAR": "Imperial grey panels", "SHARED": "the shared kit"}
DOOR_KIND = {"bacta": "door-bacta", "depot": "door-depot", "arena": "door-arena", "hangar": "door-hangar", "pad": "door-hangar",
             "landmark": "door-landmark", "tower": "door-landmark", "shop": "door-shop", "market": "door-shop",
             "home": "door-home", "hut": "door-home", "fill": "door-home"}


def slug(p):
    return p.lower().replace(" ", "-")


def _game_map(name):
    p = GAME / "data" / "maps" / name / "map.json"
    return json.loads(p.read_text()) if p.exists() else None


def _script_weather(name):
    """Weather a map's scripts set with `setweather`."""
    p = GAME / "data" / "maps" / name / "scripts.inc"
    return re.findall(r"setweather (WEATHER_\w+)", p.read_text()) if p.exists() else []


def scan():
    """{(category, item, planet): set(area ids)} from every area yaml and the vanilla maps they are built into."""
    from . import vanilla as V
    gba = V._gba()
    lays = gba.layouts()
    inv = {v: k for k, v in V.behaviours().items()}
    bkind = {}
    for r in csv.DictReader(open(ROOT / "wiki" / "mapping" / "buildings.csv")):
        bkind[r["art"]] = bkind.get(r["art"]) or r["kind"]
    hits = defaultdict(set)

    def hit(item, planet, area):
        hits[(ITEMS[item][0], item, planet)].add(area)

    for p in sorted(glob.glob(str(ROOT / "wiki" / "world" / "**" / "*.yaml"), recursive=True)):
        d = yaml.safe_load(open(p))
        aid, planet, kind, rep = d["id"], d.get("planet", ""), d.get("kind", ""), d.get("replaces", "new")
        grid = d.get("grid") or ""
        # yaml: the world as laid out (covers net-new areas too)
        for b in d.get("buildings") or []:
            k = bkind.get(b.get("art", ""))
            hit(DOOR_KIND.get(k, "door-landmark" if b.get("art", "").startswith("art:shared:") else "door-home"), planet, aid)
        for w in d.get("warps") or []:
            n = str(w.get("name", "")).lower()
            if re.search(r"ladder|hatch", n):
                hit("ladder", planet, aid)
            elif re.search(r"lift|elevator", n):
                hit("lift", planet, aid)
            elif re.search(r"cave|tunnel|canyon|graveyard|mouth|crystal|wampa", n) and kind != "interior":
                hit("cave-mouth", planet, aid)
        for x in d.get("people") or []:
            if x.get("role") == "item":
                hit("item-pod", planet, aid)
            elif x.get("role") == "berry":
                hit("fruit-tree", planet, aid)
        if "~" in grid:
            hit("anim-water", planet, aid)
        if kind in ("town", "route", "landmark"):
            hit("map-popup", planet, aid)
            hit("region-map", planet, aid)
            hit("map-border", planet, aid)
            if '"' in grid:
                hit("fx-grass-rustle", planet, aid)
                hit("bg-grass", planet, aid)
            hit("bg-plain", planet, aid)
        elif kind == "dungeon":
            if aid.startswith("underwater"):
                for item in ("seafloor", "sea-rock", "surface-spot", "seaweed", "fx-bubbles", "weather-bubbles"):
                    hit(item, planet, aid)
            hit("map-popup", planet, aid)
            hit("map-border", planet, aid)
            hit("bg-underwater" if aid.startswith("underwater") else "bg-cave", planet, aid)
        elif kind == "interior":
            hit("bg-building", planet, aid)
        if planet in ("HOTH", "ILUM") and kind in ("route", "town", "landmark"):
            hit("weather-snow", planet, aid)
            hit("fx-footprints", planet, aid)
        if aid == "hideout-kit":
            hit("hideout-interior", "SHARED", aid)
        # vanilla map: object events, behaviours, tilesets, weather
        mj = _game_map(rep) if rep and rep != "new" else None
        if not mj:
            continue
        for o in mj.get("object_events") or []:
            g = o["graphics_id"].replace("OBJ_EVENT_GFX_", "")
            if g in GFX:
                hit(GFX[g], planet, aid)
        for wname in [mj.get("weather")] + [c.get("weather", "").replace("COORD_EVENT_", "")
                                            for c in mj.get("coord_events") or [] if c.get("type") == "weather"] + _script_weather(rep):
            if wname in WEATHER:
                hit(WEATHER[wname], planet, aid)
        if rep in ROTATING_GATE_MAPS:
            hit("rotating-gate", planet, aid)
        for pre, item in SPECIAL_BG.items():
            if rep.startswith(pre):
                hit(item, planet, aid)
        lay = lays.get(mj["layout"])
        if not lay:
            continue
        for ts in (lay.primary, lay.secondary):
            folder = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", "_", ts.replace("gTileset_", "")).lower()
            for item in ANIM.get(folder, []):
                hit(item, planet, aid)
        seen = set()
        for v in lay.cells().flatten():
            seen.add(inv.get(V._behaviour(gba, lay, int(v) & 0x3FF), ""))
        for b in seen:
            items = BEH.get(b)
            for item in ([items] if isinstance(items, str) else list(items or [])):
                hit(item, planet, aid)
        if "MB_ANIMATED_DOOR" in seen and kind in ("interior", "dungeon"):
            hit("door-interior", planet, aid)
        if "MB_CAVE" in seen and kind in ("route", "town", "landmark"):
            hit("cave-mouth", planet, aid)
    return hits


def kit_id(cat, item, planet):
    return f"kit:{cat}:{slug(planet)}:{item}"


def new_row(cat, item, planet):
    c, name, emerald, drawn, hb, tool, desc = ITEMS[item]
    pl = planet if planet else "SHARED"
    return {"kit_id": kit_id(cat, item, pl), "category": cat, "planet": pl, "item": item,
            "name": f"{name} ({pl.title()})", "emerald": emerald, "drawn": drawn, "hit_box": hb, "used_in": "0", "areas": "",
            "status": "pending-mockup", "tool": "",
            "description": f"{desc} Drawn in {LOOK.get(pl, pl.lower())}.",
            "notes": f"No art yet. Drawn later with {tool} (" + ("not built for this yet" if tool else "no tool yet") + ").",
            "placeholder": f"world/kits/placeholders/{cat}/{slug(pl)}/{item}.png"}


def hideout_decorations():
    """One row per hideout decoration (hideout category), from the decoration list in ../game and its Star Wars name."""
    names = {r["emerald_id"]: r["sw_name"] for r in csv.DictReader(open(ROOT / "wiki" / "mapping" / "world_objects.csv"))}
    text = (GAME / "src" / "data" / "decoration" / "header.h").read_text()
    rows = []
    for m in re.finditer(r"\[(DECOR_\w+)\]\s*=\s*\{(.*?)\n    \}", text, re.S):
        const, body = m.group(1), m.group(2)
        if const == "DECOR_NONE":
            continue
        shape = re.search(r"DECORSHAPE_(\d+)x(\d+)", body)
        w, h = (int(shape.group(1)), int(shape.group(2))) if shape else (1, 1)
        eid = "decoration:" + const[6:].lower().replace("_", "-")
        item = "decor-" + const[6:].lower().replace("_", "-")
        sw = names.get(eid, const[6:].replace("_", " "))
        rows.append({"kit_id": f"kit:hideout:shared:{item}", "category": "hideout", "planet": "SHARED", "item": item,
                     "name": sw.title(), "emerald": const, "drawn": f"{w}x{h}", "hit_box": "", "used_in": "1",
                     "areas": "hideout-kit", "status": "pending-mockup", "tool": "",
                     "description": f"Hideout decoration {sw} (Emerald {const[6:].replace('_', ' ').title()}), placed by the player.",
                     "notes": "No art yet. Its icon (C3) and placed sprite (C4) are pending_art.csv rows for sprite-icon-generator and sprite-walker-generator.",
                     "placeholder": f"world/kits/placeholders/hideout/shared/{item}.png"})
    return rows


def load():
    return {r["kit_id"]: r for r in csv.DictReader(open(PATH))} if PATH.exists() else {}


def save(rows):
    with open(PATH, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=COLS)
        w.writeheader()
        w.writerows(sorted(rows.values(), key=lambda r: (r["category"], r["planet"], r["item"])))


def update(add=False):
    """Write used_in / areas from a fresh scan; return the hits that have no row (added with add=True)."""
    rows = load()
    hits = scan()
    missing = []
    for (cat, item, planet), areas in hits.items():
        kid = kit_id(cat, item, planet or "SHARED")
        if kid not in rows:
            missing.append(kid)
            if not add:
                continue
            rows[kid] = new_row(cat, item, planet or "SHARED")
        a = sorted(areas)
        rows[kid]["used_in"] = str(len(a))
        rows[kid]["areas"] = " ".join(a[:6]) + (" ..." if len(a) > 6 else "")
    if add:
        for r in hideout_decorations():
            rows.setdefault(r["kit_id"], r)
    keys = {kit_id(c, i, p or "SHARED") for c, i, p in hits}
    for kid, r in rows.items():
        if kid not in keys and r["category"] != "hideout":
            r["used_in"], r["areas"] = "0", ""
    save(rows)
    return missing


def check(hits=None):
    rows = load()
    out = []
    if not rows:
        return ["world_kits.csv is missing (run `python3 -m blockout kits --add`)"]
    for kid, r in rows.items():
        if r["used_in"] in ("", "0"):
            out.append(f"{kid}: used by no area")
        if not (ROOT / "wiki" / r["placeholder"]).exists():
            out.append(f"{kid}: placeholder {r['placeholder']} is missing (run wiki/world/kits/make_placeholders.py)")
    if hits is not None:
        for c, i, p in hits:
            if kit_id(c, i, p or "SHARED") not in rows:
                out.append(f"{kit_id(c, i, p or 'SHARED')}: the scan finds it but it has no row (run `python3 -m blockout kits --add`)")
    return out
