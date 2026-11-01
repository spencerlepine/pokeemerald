# Asset tools

One tool per asset group: everything a group needs is scoped together so one tool can generate any asset in it.
Each tool takes a row from the wiki (`../wiki/database/pending_art.csv` or `pending_audio.csv`), generates the asset,
and the row's status is set to `DONE` when it lands in `../game`. Ghost rows (`swap_kind` `CUT`) need no tool: they are deletions.
Rows marked `todo` `HUMAN-TODO` (logo, title screen, intro, credits, story cutscenes, menu images with Pokémon
branding; decided in `../wiki/mapping/branding.csv`) are replaced by hand, not by a tool, and generic menu art is
`KEEP_ART`. So `ui-skin-generator` and `cutscene-generator` only matter if you later want to restyle the kept UI.

Categories (A1, B3, ...) are listed under [Art categories](#art-categories) below: every PNG in `../game` belongs to
exactly one. They were first audited in the prototype repo
([emerald-art-pipeline-prototype/CHECKLIST.md](https://github.com/spencerlepine/emerald-art-pipeline-prototype/blob/main/CHECKLIST.md)),
which is no longer maintained; everything useful from it is copied here. This file is the list of tools; the per-file
work (which file becomes which Star Wars subject) stays in the wiki. Update this file in the same commit as the work.

## Palettes (every art tool)

Every tool that writes art follows [`PALETTES.md`](PALETTES.md): layer 1 is the GBA hardware (15-bit colour, 16-entry
banks with index 0 transparent, shared and locked banks per asset), layer 2 the themes chosen inside it
([`../wiki/bible/PALETTE.md`](../wiki/bible/PALETTE.md)). The shared [`palette-enforcer/`](palette-enforcer/) is the last
post-processing step of every pipeline (diffusion, img2img, script or hand edit): `enforce` makes the pixels legal,
`check` decides whether they install. A tool that is not built yet has a **Palette** section in its README/TODO
saying which bank and theme it uses; building the tool includes wiring that step in.

## Status legend

| Status | Meaning |
|---|---|
| **TODO** | No tool yet. The scope is mapped and counted only (`TODO.md` in the folder). |
| **PENDING** | Approach decided and researched; the build waits on something outside this repo (e.g. a GPU for an image model). |
| **IN-REVIEW** | Tool works end to end; samples are with the owner for feedback. |
| **READY** | Owner approved the samples; agents can generate the group at scale by following the tool's guide. |
| **DONE** | Finished. |
| **OUT-OF-SCOPE** | Never shown in game, not redrawn (ghost rows in the wiki). |

## Tools

| Tool | Status | Covers | Categories | Wiki rows |
|---|---|---|---|---|
| [`palette-enforcer/`](palette-enforcer/) | DONE | Shared palette gate and post-processor: GBA hardware rules plus the wiki themes ([`PALETTES.md`](PALETTES.md)). Every art tool calls it last. | all art | - |
| [`play-tester/`](play-tester/) | DONE | Headless mGBA play-testing: scripts, Lua helpers, savestates | - | - |
| [`sprite-creature-generator/`](sprite-creature-generator/) | IN PROGRESS (2026-11-01: hosted Civitai pipeline in `civitai/`, creature LoRA on SD 1.5, image to image from a prepped movie reference; MASSIFF front, frame 2, back and palettes shipped to the wiki; placement data still to build) | Companion battle sprites: front, second animation frame, back, normal and shiny palettes, battle placement data; Unown and Castform forms. | A1, A2 | `pending_art.csv` kind `pokemon` (front, anim_front, back) for each species and form; 1,248 PNGs |
| [`sprite-creature-icon-generator/`](sprite-creature-icon-generator/) | TODO | Companion party and PC box icons (2-frame wiggle) and their shared-palette index. | A3 | `pending_art.csv` kind `pokemon` icon files; 417 PNGs |
| [`sprite-creature-footprint-generator/`](sprite-creature-footprint-generator/) | TODO | Companion Datapad footprints. | A4 | `pending_art.csv` kind `pokemon` footprint files; 387 PNGs |
| [`sprite-creature-extras-generator/`](sprite-creature-extras-generator/) | TODO | The Egg (pics, hatch and shard sheets), Spinda's spot masks, question-mark placeholder pics. | A5 | `pending_art.csv` kind `pokemon` subkinds `egg`, `question_mark`, `spinda` spots; 14 PNGs |
| [`sprite-icon-generator/`](sprite-icon-generator/) | TODO | Small fixed-size stills: item icons, fruit (berries), decoration icons, capture pods in battle, type labels. | C1, C2, C3, C5, C6 | `pending_art.csv` kinds `items`, `berries`, `decorations`, `balls`, `types`; 340 PNGs |
| [`sprite-walker-generator/`](sprite-walker-generator/) | IN-REVIEW (style gate and vanilla composition added after the owner rejected the first batches; 16x32 people kit only) | Overworld walking sprites: people (player, rivals, NPCs), overworld companions, placed dolls and cushions. | A6, B3, C4 | `pending_art.csv` kind `object_events`; 207 PNGs |
| [`sprite-trainer-generator/`](sprite-trainer-generator/) | DONE (2026-11-01: hosted Civitai pipeline in `civitai/`, trainer LoRA on SDXL, paid in Buzz; Darth Vader shipped to the wiki) | Trainer battle portraits and Prof. Korr's intro portrait. | B1, B4 | `pending_art.csv` kind `trainers` (front pics) and `birch_speech`; 95 PNGs |
| [`sprite-trainer-back-generator/`](sprite-trainer-back-generator/) | PENDING (old repaint tool scrapped; plan in its README: same trainer LoRA, back views untested) | Player and partner battle back sprites (the capture-pod throw). | B2 | `pending_art.csv` kind `trainers` (back pics); 8 PNGs |
| [`tile-generator/`](tile-generator/) | TODO | Overworld tilesets per planet and building, their tile animations, metatiles, and battle backgrounds. | D1, D2, E1 | `pending_art.csv` kinds `tileset` and `battle_environment`; 247 PNGs plus their .pal, metatiles.bin and tilemaps |
| [`vfx-generator/`](vfx-generator/) | IN-REVIEW | Animated effects: field effects (grass, sand, ash, ripples, emotes), doors, field objects, weather, move-animation particles, battle transitions, and the VFX rows (status/general/special battle animations, net-new VFX like hyperspace and lightsabers). | D3, D4, D5, D6, E3, E4 | `pending_art.csv` kinds `field_effects`, `door_anims`, `weather`, `battle_anims`, `battle_transitions`, `rotating_gates`, `battle_animation` and every `vfx_*` kind; 513 PNGs + 170 VFX rows |
| [`ui-skin-generator/`](ui-skin-generator/) | TODO | Tile-based screens: text windows, map popups, region map, battle HUD, menus, Datapad, comlink, PC, trainer card, minigames, Grand Arena screens. | D7, D8, E2, F1, F3-F10, H1-H5 | `pending_art.csv` UI kinds (`text_window`, `map_popup`, `battle_interface`, `pokedex`, `pokenav`, `pokemon_storage`, ...); 488 PNGs. Mostly kept: only re-skin what reads as Pokémon |
| [`title-screen-generator/`](title-screen-generator/) | DONE (shipped 2026-11-01; `ship.py` writes the picks into ../game) | Title screen logo, KYBER VERSION banner, Exogorth, sky, copyright lines. | - | `branding.csv` title_screen and intro copyright rows |
| [`cutscene-generator/`](cutscene-generator/) | READY (pxl + GBA output, style guide, ROM preview; draft intro scene 2 in `scenes/intro_bike/`: backgrounds approved, characters need work, not imported) | Title screen, intro movie, credits, the titan/EXOGORTH scene, evolution, trade and shuttle-ride scenes. | G1, G2, G3, G4 | `pending_art.csv` kinds `title_screen`, `intro`, `credits`, `rayquaza_scene`, `evolution_scene`, `trade`, `cable_car`; 83 PNGs |
| [`music-generator/`](music-generator/) | READY (2026-11-01: song models -> MIDI on the game's voicegroups, m4a preview, hardware checks, loop check, film-cue analyzer, ROM recorder; 2 prototypes, nothing installed; limits in its CONSTRAINTS.md) | Background music, battle music and fanfares, from the briefs and film cues in the wiki. | audio: music | `music.csv`: 178 songs TODO (140 HOTSWAP + 38 NET_NEW), each with a film cue (`ref_use` ARRANGE / STYLE / SCRATCH) |
| [`sfx-generator/`](sfx-generator/) | DONE (approved 2026-11-01; GB-chip emulation + PCM synth, ROM-verified; first 8 SFX shipped into ../game; limits in its CONSTRAINTS.md) | Sound effects: the 26 mapped ones (capture pods, comlink, doors, hover-bike, kyber, freighter) and 17 net-new (blaster, lightsabers, Force, turbolaser, hyperspace, astromech, Vader's breath...). | audio: sfx | `pending_audio.csv` category `sfx`, swap_kind HOTSWAP or NET_NEW: 43 rows (277 KEEP rows need nothing) |
| [`cry-generator/`](cry-generator/) | DONE (approved 2026-11-01; creature/droid synth, DPCM-exact output, ROM-verified; first 6 cries shipped into ../game; limits in its CONSTRAINTS.md) | One cry per companion: creature calls, droid beeps and servos. | audio: cry | `pending_audio.csv` category `cry`, HOTSWAP: 386 rows |

### Prototype progress to carry over

These were built in the prototype repo. When a tool moves into this repo, start from its prototype. Ported so far: `sprite-walker-generator/` (each folder is self-contained; follow its own `README.md`).

| Tool here | Prototype tool | Prototype status | Notes |
|---|---|---|---|
| `sprite-walker-generator/` | `walker` | **READY** for the 16x32 nine-frame people kit (Vader approved, 1 drawn). **Ported here.** | Other kits (32x32 big, 16x16 small, bike / surf / fish / field-move sheets, creature walkers) not built. Its `install` step writes the OBJ palette tag. Guide: [`sprite-walker-generator/README.md`](sprite-walker-generator/README.md). |
| `sprite-trainer-generator/` | `trainer-front` | Scrapped 2026-11-01 | The ported repaint tool did not work and was deleted (in git history). Replaced by an image-model plan: [`sprite-trainer-generator/README.md`](sprite-trainer-generator/README.md). |
| `sprite-trainer-back-generator/` | `trainer-back` | Scrapped 2026-11-01 | Built here directly, did not work, deleted (in git history). Image-model plan: [`README.md`](sprite-trainer-back-generator/README.md). |
| `sprite-creature-generator/` | `creature` | **IN PROGRESS** (Civitai, no GPU; front `--colours 15 --write-pal normal.pal`, back `--pal normal.pal`) | Research in the prototype's `tools/sprite-creature-generator/research/`; model and GPU plan in [`sprite-creature-generator/README.md`](sprite-creature-generator/README.md). |
| `sprite-icon-generator/` | `icon` | TODO | Item icons first (218), then fruit, decorations, capture pods, type labels. |
| `tile-generator/` | `tileset` | TODO | Do one biome end to end first (e.g. a desert secondary tileset for Tatooine) with palettes, metatiles and animations; then battle backgrounds. |
| `vfx-generator/` | `obj-anim` | IN-REVIEW | |
| `ui-skin-generator/` | `ui-skin` | TODO | Text windows and map popups first (seen constantly), then menus, battle HUD, minigames. |
| `cutscene-generator/` | `cutscene` | TODO | Title screen, intro, legendary scene first. |

Paths in the Notes column are in the prototype repo unless linked.

## One creature, every sprite

Everything a single companion needs, so one creature can be made as a batch. Audited on 2026-11-01 against
`../wiki/database/pending_art.csv` (kind `pokemon`: 5 PNG rows per standard species) and the species folders and
tables in `../game`. **SD** = a Stable Diffusion model on a rented GPU; **Python** = a deterministic script, no GPU.

### Every species

| # | Asset | File in `game/graphics/pokemon/<species>/` | Format | Wiki row | Tool | Engine |
|---|---|---|---|---|---|---|
| 1 | Battle front | `front.png` | 64x64, 4bpp | yes | `sprite-creature-generator` | SD + Python finisher |
| 2 | Front animation (frame 1 = front, frame 2 = second pose) | `anim_front.png` | 64x128 | yes | `sprite-creature-generator` | SD img2img + Python finisher |
| 3 | Battle back | `back.png` | 64x64, 4bpp | yes | `sprite-creature-generator` | SD (`backside`) + Python finisher |
| 4 | Battle palette | `normal.pal` | 16 colours, shared by 1-3 | no | `sprite-creature-generator` | Python |
| 5 | Shiny palette | `shiny.pal` | 16 colours, same indices | no | `sprite-creature-generator` | Python (optionally guided by SD `shiny`) |
| 6 | Battle placement, motion preset, Datapad scale | `src/data/pokemon_graphics/*.h`, `src/pokemon.c`, `src/pokemon_animation.c`, `pokedex_entries.h` | C tables | no | `sprite-creature-generator` | Python |
| 7 | Party / PC box icon | `icon.png` | 32x64 (2-frame wiggle), one of 3 shared icon palettes | yes | `sprite-creature-icon-generator` | Python (from the approved front) |
| 8 | Icon palette index | `gMonIconPaletteIndices` in `src/pokemon_icon.c` | 0-2 | no | `sprite-creature-icon-generator` | Python |
| 9 | Datapad footprint | `footprint.png` | 16x16, 1 bit (blank for 87 vanilla species) | yes | `sprite-creature-footprint-generator` | Python |
| 10 | Cry | `sound/direct_sound_samples/cries/` | audio | `pending_audio.csv` | `cry-generator` | audio |

The front is reused everywhere else a creature appears (summary, Datapad, trade, evolution, Hall of Fame, contests,
treat feeding), so there is no separate art for those screens.

### Forms and one-offs

| Species | Extra files | Tool | Engine |
|---|---|---|---|
| Unown | 28 letter folders, each with front, anim_front, back, icon; one shared `normal.pal` / `shiny.pal` | `sprite-creature-generator` (pics), `sprite-creature-icon-generator` (icons) | as rows 1-8 |
| Castform | 4 weather folders, each with front, anim_front, back and palettes; one icon | `sprite-creature-generator`, `sprite-creature-icon-generator` | as rows 1-8 |
| Deoxys | `icon_speed.png`, `icon_speed_wide.png` | `sprite-creature-icon-generator` | Python |
| Spinda | `spots/spot_0-3.png`, 16x16 masks painted on at runtime | `sprite-creature-extras-generator` | Python |
| Egg | front, anim_front, `hatch.png`, `shard.png`, `normal.pal` (icon: row 7) | `sprite-creature-extras-generator` | Python + hand |
| `question_mark` placeholders | circled and double front, anim_front, back, palettes (icon, footprint: rows 7, 9) | `sprite-creature-extras-generator` | Python + hand |

### Only some species

These show one specific creature outside the species folder. They are drawn by the tool for that screen, after the
creature's battle front is approved.

| Where | Files | Tool |
|---|---|---|
| Overworld walkers (legendaries, story companions, Kecleon, Sudowoodo...) | `graphics/object_events/pics/pokemon/*.png` (A6) | `sprite-walker-generator` |
| Placed dolls and cushions | `graphics/object_events/pics/dolls/*.png` (C4) | `sprite-walker-generator` |
| Doll decoration icons | `graphics/decorations/*_doll.png` (C3) | `sprite-icon-generator` |
| PC wallpaper motifs | `graphics/pokemon_storage/wallpapers/` creature wallpapers and icons (F7) | `ui-skin-generator` |
| Minigame actors | `dodrio_berry_picking/dodrio.png`, `pokemon_jump/venusaur.png` (H3); `roulette/*.png`, `slot_machine/reel_time_pikachu.png` (H4) | `ui-skin-generator` |
| Intro and legendary scene actors | `graphics/intro/`, `graphics/rayquaza_scene/` (G2, G3) | `cutscene-generator` |
| Battle transitions and field effects | `battle_transitions/{groudon,kyogre,rayquaza}.png` (E4), `field_effects/pics/deoxys_rock_fragment_*.png` (D4) | `vfx-generator` |
| Sootopolis storm water | `data/tilesets/secondary/sootopolis/anim/stormy_water/*_{groudon,kyogre}.png` (D2) | `tile-generator` |

### Batch order for one creature

1. `sprite-creature-generator`: rows 1-6. Owner approves the front.
2. `sprite-creature-icon-generator` and `sprite-creature-footprint-generator`: rows 7-9, from the approved front.
3. `cry-generator`: row 10 (independent).
4. Only-some-species art, if the creature has any.

Wiki gap: the wiki tracks rows 1, 2, 3, 7 and 9 only. Palettes and the C tables have no rows; the tools write them
alongside the PNGs.

## Order of work

Work one tool at a time: build it, show the owner samples, iterate, mark it READY, then generate the whole group.

1. ~~The 16x32 `sprite-walker-generator` kit: port from the prototype~~ (ported, READY).
2. `sprite-trainer-generator` and `sprite-trainer-back-generator`: rebuild on the trainer LoRA once a GPU is rented; test it side by side with the creature LoRA first.
3. The creature set, one creature at a time once all four are built (see [One creature, every sprite](#one-creature-every-sprite)): `sprite-creature-generator` (front, frame 2, back, palettes), then `sprite-creature-icon-generator` and `sprite-creature-footprint-generator` from the approved front; `sprite-creature-extras-generator` once for the Egg and placeholders.
4. `sprite-icon-generator`: item icons, then fruit, decorations, pods, type labels.
5. `sprite-walker-generator` extra kits.
6. `tile-generator`: one biome first, then the rest and battle backgrounds.
7. `vfx-generator`: field effects, doors, field objects, weather, move particles, transitions, VFX rows.
8. `ui-skin-generator`: text windows and map popups first.
9. `cutscene-generator`: title screen, intro, legendary scene.
10. Audio (`music-generator`, `sfx-generator`, `cry-generator`) can run in parallel with any of the above.

## Art categories

Counts verified on 2026-10-31: 4,076 PNGs (the same number of image rows as `../wiki/database/pending_art.csv`), 4,064
to draw across 48 categories plus 12 unused. 3 shared UI/misc `.pal` files sit outside any category; they belong to the
tool that edits that screen.

### A. Creatures

| # | Category | Where it shows | Format | PNGs | .pal | Tool |
|---|---|---|---|---|---|---|
| A1 | Creature battle front (2 frames) | Battle (opponent side), Datapad, summary | front.png 64x64 + anim_front.png 64x128 (2 frames), own palette | 838 | 783 | `sprite-creature-generator` |
| A2 | Creature battle back | Battle (your side) | back.png 64x64, same palette as the front | 418 | | `sprite-creature-generator` |
| A3 | Creature party/PC icons | Party menu, PC boxes | icon.png 32x64 (2-frame wiggle), one of 3 shared icon palettes | 417 | 3 | `sprite-creature-icon-generator` |
| A4 | Creature footprints | Datapad | 16x16, 1 colour | 387 | | `sprite-creature-footprint-generator` |
| A5 | Eggs, hatching and special-form extras | Day-care egg, hatch scene, Spinda spots, Unown/Castform/Deoxys forms | egg hatch/shard sheets, spot masks | 6 | | `sprite-creature-extras-generator` (the Unown/Castform form pics count under A1/A2) |
| A6 | Overworld creature walkers | Overworld (legendaries, NPC companions) | 16x16 to 64x64 frames, shared NPC palettes | 23 | | `sprite-walker-generator` |

### B. People

| # | Category | Where it shows | Format | PNGs | .pal | Tool |
|---|---|---|---|---|---|---|
| B1 | Trainer battle front pics | Trainer battles, trainer card, Hall of Fame, Grand Arena | 64x64, 1 frame, own 16-colour palette taken from the PNG | 93 | | `sprite-trainer-generator` |
| B2 | Player battle back pics | Your side when a battle starts (pod throw) | 64x256 / 64x320 = 4-5 frames of 64x64, palette in graphics/trainers/palettes | 8 | 6 | `sprite-trainer-back-generator` |
| B3 | People overworld walkers | NPCs, player, rivals | 16x32 x 9 frames (standard), plus 32x32 big, 16x16 small and special sheets (bike, surf, fish, field move) | 133 | 36 | `sprite-walker-generator` |
| B4 | Professor speech portrait | New-game intro | 64x64 still + shadow/unused frames | 2 | | `sprite-trainer-generator` |

### C. Items and icons

| # | Category | Where it shows | Format | PNGs | .pal | Tool |
|---|---|---|---|---|---|---|
| C1 | Item icons | Bag, shops, PC | 24x24, own palette (graphics/items/icon_palettes) | 218 | 253 | `sprite-icon-generator` |
| C2 | Fruit (berry) pictures | Fruit tag, blender | 48x48, own palette | 43 | | `sprite-icon-generator` |
| C3 | Decoration icons | Hideout decoration menu | 24x24 | 43 | 3 | `sprite-icon-generator` |
| C4 | Placed dolls and cushions | Hideouts | 16x16 / 32x32 OBJ sprites | 51 | | `sprite-walker-generator` |
| C5 | Capture pod battle sprites | Throw, send-out, capture | 16x48 = 3 frames of 16x16 | 13 | | `sprite-icon-generator` |
| C6 | Type and showcase-category labels | Summary, Datapad, move info | 32x16 | 23 | 3 | `sprite-icon-generator` |

### D. Overworld (biomes, objects, effects)

| # | Category | Where it shows | Format | PNGs | .pal | Tool |
|---|---|---|---|---|---|---|
| D1 | Tilesets (biome and building tile sheets) | Every map | tiles.png 128 wide of 8x8 tiles; 16-colour palettes (primary 0-5, secondary 6-12); metatiles.bin + attributes | 89 | 1200 | `tile-generator` |
| D2 | Tileset animations | Water, flowers, waterfalls, lava, TVs, lights | frames of tiles swapped in at runtime | 137 | | `tile-generator` |
| D3 | Door animations | Every enterable building | 16x96 (3 frames of 16x32), some 32 wide | 53 | | `vfx-generator` |
| D4 | Field effects | Grass rustle, ripples, footprints, sand, ash, emote bubbles, Cut, shadows | 8x8 to 32x32 OBJ frames | 59 | 22 | `vfx-generator` |
| D5 | Field objects | Boulders, cut trees, breakable rocks, truck, Mirage Tower, rotating gates, fruit trees | 16x16 to 64x64 OBJ frames | 56 | | `vfx-generator` |
| D6 | Weather overlays | Rain, snow, ash, fog, sandstorm, bubbles | OBJ frames + scrolling layers | 10 | 4 | `vfx-generator` |
| D7 | Map name popups | Entering a new area | 80x24 frame styles + outlines | 12 | 1 | `ui-skin-generator` |
| D8 | Region map | Town map, comlink map, Fly, Datapad area | tiles + tilemap, map icons and cursors | 14 | 4 | `ui-skin-generator` |

### E. Battle

| # | Category | Where it shows | Format | PNGs | .pal | Tool |
|---|---|---|---|---|---|---|
| E1 | Battle backgrounds | Behind every battle | tiles + tilemap + anim tiles + palette per environment | 21 | 23 | `tile-generator` |
| E2 | Battle HUD | Health boxes, HP/EXP bars, pod tray, status | OBJ/BG tiles | 32 | 4 | `ui-skin-generator` |
| E3 | Move animation sprites and backgrounds | Every move animation | particle sprites, BG overlays, masks | 312 | 47 | `vfx-generator` |
| E4 | Battle transitions | Wild/trainer/leader battle start | BG tiles + OBJ pieces | 23 | 18 | `vfx-generator` |

### F. Screens and UI

| # | Category | Where it shows | Format | PNGs | .pal | Tool |
|---|---|---|---|---|---|---|
| F1 | Text windows and frames | Every dialogue/menu box (20 player-selectable frames) | 24x24 frame tiles + palette | 21 | 4 | `ui-skin-generator` |
| F2 | Fonts | All text | glyph sheets 1-2bpp, Latin + Japanese + Braille | 17 | | none: kept vanilla; the Braille sheet is replaced by hand |
| F3 | Shared interface pieces | Cursors, scroll arrows, status icons, markings, menu info | small OBJ/BG tiles | 18 | 11 | `ui-skin-generator` |
| F4 | Bag, party and summary screens | Start menu screens | full-screen tiles + tilemap; bag pictures 64x64 x 6 pockets | 17 | 8 | `ui-skin-generator` |
| F5 | Datapad (Pokédex) screens | Datapad | tiles + tilemaps | 9 | 5 | `ui-skin-generator` |
| F6 | Comlink (PokéNav) screens | Condition, match call, ribbons | tiles + tilemaps + OBJ | 48 | 17 | `ui-skin-generator` |
| F7 | Terminal storage and wallpapers | PC boxes | 16 wallpapers (tiles + tilemap) + menus | 89 | 10 | `ui-skin-generator` |
| F8 | Trainer card, Arena Pass, diploma | Player ID screens | tiles + tilemaps, shard/medal icons | 13 | 23 | `ui-skin-generator` |
| F9 | Naming, Easy Chat, shop, mail, misc menus | Text entry, shops, mail, wall clock, picture frames | tiles + tilemaps | 50 | 29 | `ui-skin-generator` |
| F10 | Link, wireless and Mystery Gift screens | Trade/record-mixing setup, Union Room chat, Wonder Card/News | tiles + tilemaps | 36 | 28 | `ui-skin-generator` |

### G. Cutscenes and story screens

| # | Category | Where it shows | Format | PNGs | .pal | Tool |
|---|---|---|---|---|---|---|
| G1 | Title screen | Boot | logo, version banner, legendary, clouds | 6 | 3 | `cutscene-generator` |
| G2 | Intro and credits | Intro movie, staff roll | BG tiles + OBJ actors | 36 | 15 | `cutscene-generator` |
| G3 | Legendary story scene | Titans vs EXOGORTH cutscene | BG tiles + large OBJ actors | 25 | 3 | `cutscene-generator` |
| G4 | Evolution, trade and shuttle scenes | Evolution, trading, the shuttle (cable car) ride | BG tiles + OBJ | 16 | 18 | `cutscene-generator` |

### H. Minigames and facilities

| # | Category | Where it shows | Format | PNGs | .pal | Tool |
|---|---|---|---|---|---|---|
| H1 | Showcases (contests) | Showcase halls | audience, meters, interface tiles | 23 | 3 | `ui-skin-generator` |
| H2 | Fruit blender, crush, pokéblocks | Fruit minigames, treat case/feeding | tiles + OBJ | 20 | 19 | `ui-skin-generator` |
| H3 | Link minigames (Dodrio picking, Pokémon Jump) | Wireless minigames | tiles + OBJ actors | 14 | 4 | `ui-skin-generator` |
| H4 | Sabacc Den (slots, roulette) | Mos Espa Sabacc Den | reels, symbols, boards | 55 | 10 | `ui-skin-generator` |
| H5 | Grand Arena screens | Grand Arena facilities | Factory rental screen, Arena judgment, Dome bracket | 17 | 11 | `ui-skin-generator` |

### X. Not drawn

| # | Category | Where it shows | Format | PNGs | .pal | Tool |
|---|---|---|---|---|---|---|
| X1 | Unused vanilla art | Nowhere (left in the source) | - | 12 | 7 | none, OUT-OF-SCOPE. The wiki marks the 11 `graphics/unused/*.png` files as ghost rows (`swap_kind` `CUT`) to delete. |

## Not PNGs, but changed alongside the art

Nothing draws these, but a tool has to write them so its art works in game.

| Data | Where | Written by |
|---|---|---|
| Palettes (`.pal`, JASC) | next to most PNGs; shared NPC palettes in `graphics/object_events/palettes/` | each tool writes the palette its art uses (the `.pal` column above), through `palette-enforcer` ([`PALETTES.md`](PALETTES.md)) |
| Tilemaps (`.bin`, 435 files) | screens, battle backgrounds, wallpapers, region map | `ui-skin-generator`, `tile-generator`, `cutscene-generator` (layout kept, tiles redrawn) |
| Metatiles and attributes (`metatiles.bin`, `metatile_attributes.bin`) | `data/tilesets/**` | `tile-generator` |
| Creature battle placement and motion (`front_pic_coordinates.h`, `back_pic_coordinates.h`, `enemy_mon_elevation.h`, `front_pic_anims.h`, `sMonFrontAnimIdsTable` / `sMonAnimationDelayTable` in `src/pokemon.c`, `sSpeciesToBackAnimSet` in `src/pokemon_animation.c`, `pokemonScale` / `pokemonOffset` in `pokedex_entries.h`) | `src/data/pokemon_graphics/`, `src/` | `sprite-creature-generator` |
| Creature icon palette index (`gMonIconPaletteIndices`) | `src/pokemon_icon.c` | `sprite-creature-icon-generator` |
| OBJ graphics info and pic tables | `src/data/object_events/*.h`, `src/data/graphics/*.h` | `sprite-walker-generator` (palette tag), later tools as needed |
| Move and VFX animation scripts | `data/battle_anim_scripts.s`, `data/field_effect_scripts.s`, `src/battle_transition.c`, `src/field_weather.c` | kept unless the wiki row is HOTSWAP or NET_NEW (`vfx-generator`); only the sprites they draw change |

Not covered by a tool at all: map layouts (`data/layouts`), map events and scripts, text (the wiki's `texts.csv` is
ported by hand), instrument samples and voicegroups (`sound/direct_sound_samples`, `sound/voicegroups`; the new music
plays through them), game logic.

