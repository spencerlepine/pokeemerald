# Asset tools

One tool per asset group: everything a group needs is scoped together so one tool can generate any asset in it.
Each tool takes a row from the wiki (`../wiki/database/pending_art.csv` or `pending_audio.csv`), generates the asset,
and the row's status is set to `DONE` when it lands in `../game`. Ghost rows (`swap_kind` `CUT`) need no tool: they are deletions.

Categories (A1, B3, ...) are the art categories of the master checklist
([emerald-art-pipeline-prototype/CHECKLIST.md](https://github.com/spencerlepine/emerald-art-pipeline-prototype/blob/main/CHECKLIST.md)).
Every PNG in `../game` belongs to exactly one category.

| Tool | Status | Covers | Categories | Wiki rows |
|---|---|---|---|---|
| [`play-tester/`](play-tester/) | DONE | Headless mGBA play-testing: scripts, Lua helpers, savestates | - | - |
| [`sprite-creature-generator/`](sprite-creature-generator/) | TODO | Companion battle sprites: front (2-frame anim), back, normal and shiny palettes, egg/hatch and form extras. | A1, A2, A5 | `pending_art.csv` kind `pokemon` (front, anim_front, back, palettes) for each species; 1,262 PNGs |
| [`sprite-icon-generator/`](sprite-icon-generator/) | TODO | Small fixed-size stills: item icons, fruit (berries), decoration icons, capture pods in battle, type labels, companion party icons and Datapad footprints. | A3, A4, C1, C2, C3, C5, C6 | `pending_art.csv` kinds `items`, `berries`, `decorations`, `balls`, `types`, plus `pokemon` icon/footprint files; 1,144 PNGs |
| [`sprite-walker-generator/`](sprite-walker-generator/) | TODO | Overworld walking sprites: people (player, rivals, NPCs), overworld companions, placed dolls and cushions. | A6, B3, C4 | `pending_art.csv` kind `object_events`; 207 PNGs |
| [`sprite-trainer-generator/`](sprite-trainer-generator/) | TODO | Trainer battle portraits and Prof. Korr's intro portrait. | B1, B4 | `pending_art.csv` kind `trainers` (front pics) and `birch_speech`; 95 PNGs |
| [`sprite-trainer-back-generator/`](sprite-trainer-back-generator/) | TODO | Player and partner battle back sprites (the capture-pod throw). | B2 | `pending_art.csv` kind `trainers` (back pics); 8 PNGs |
| [`tile-generator/`](tile-generator/) | TODO | Overworld tilesets per planet and building, their tile animations, metatiles, and battle backgrounds. | D1, D2, E1 | `pending_art.csv` kinds `tileset` and `battle_environment`; 247 PNGs plus their .pal, metatiles.bin and tilemaps |
| [`vfx-generator/`](vfx-generator/) | TODO | Animated effects: field effects (grass, sand, ash, ripples, emotes), doors, field objects, weather, move-animation particles, battle transitions, and the VFX rows (status/general/special battle animations, net-new VFX like hyperspace and lightsabers). | D3, D4, D5, D6, E3, E4 | `pending_art.csv` kinds `field_effects`, `door_anims`, `weather`, `battle_anims`, `battle_transitions`, `rotating_gates`, `battle_animation` and every `vfx_*` kind; 513 PNGs + 170 VFX rows |
| [`ui-skin-generator/`](ui-skin-generator/) | TODO | Tile-based screens: text windows, map popups, region map, battle HUD, menus, Datapad, comlink, PC, trainer card, minigames, Grand Arena screens. | D7, D8, E2, F1, F3-F10, H1-H5 | `pending_art.csv` UI kinds (`text_window`, `map_popup`, `battle_interface`, `pokedex`, `pokenav`, `pokemon_storage`, ...); 488 PNGs. Mostly kept: only re-skin what reads as Pokémon |
| [`font-generator/`](font-generator/) | TODO | Bitmap fonts and glyph sheets, only if a Star Wars font style is wanted. | F2 | `pending_art.csv` kind `fonts`; 17 PNGs |
| [`cutscene-generator/`](cutscene-generator/) | TODO | Title screen, intro movie, credits, the titan/EXOGORTH scene, evolution, trade and shuttle-ride scenes. | G1, G2, G3, G4 | `pending_art.csv` kinds `title_screen`, `intro`, `credits`, `rayquaza_scene`, `evolution_scene`, `trade`, `cable_car`; 83 PNGs |
| [`music-generator/`](music-generator/) | TODO | Background music, battle music and fanfares, from the briefs in the wiki. | audio: music | `pending_audio.csv` category `music`: 140 HOTSWAP + 5 NET_NEW (70 ghost rows are deletions, nothing to make) |
| [`sfx-generator/`](sfx-generator/) | TODO | Sound effects: the 26 mapped ones (capture pods, comlink, doors, hover-bike, kyber, freighter) and 17 net-new (blaster, lightsabers, Force, turbolaser, hyperspace, astromech, Vader's breath...). | audio: sfx | `pending_audio.csv` category `sfx`, swap_kind HOTSWAP or NET_NEW: 43 rows (277 KEEP rows need nothing) |
| [`cry-generator/`](cry-generator/) | TODO | One cry per companion: creature calls, droid beeps and servos. | audio: cry | `pending_audio.csv` category `cry`, HOTSWAP: 386 rows |

Not covered by a tool (support data, written by the tool that owns the asset): palettes (`.pal`), tilemaps and
metatiles (`.bin`), OBJ graphics tables. Kept as is: map layouts (`data/layouts`), instrument samples and voicegroups
(`sound/direct_sound_samples`, `sound/voicegroups`), game logic.
