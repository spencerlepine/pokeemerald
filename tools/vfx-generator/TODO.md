# vfx-generator

**Status:** TODO. Not built yet; this file marks the scope.

Animated effects: field effects (grass, sand, ash, ripples, emotes), doors, field objects, weather, move-animation particles, battle transitions, and the VFX rows (status/general/special battle animations, net-new VFX like hyperspace and lightsabers).

- **Categories:** D3, D4, D5, D6, E3, E4
- **Wiki rows:** `pending_art.csv` kinds `field_effects`, `door_anims`, `weather`, `battle_anims`, `battle_transitions`, `rotating_gates`, `battle_animation` and every `vfx_*` kind; 513 PNGs + 170 VFX rows
- **Format in the game:** small multi-frame OBJ sheets and BG overlays; animation scripts stay as they are unless the row is HOTSWAP or NET_NEW

## Palette (required: [`../PALETTES.md`](../PALETTES.md))

- **Hardware (layer 1):** 4bpp OBJ sheets and BG overlays. Many effects share a bank by tag (field effects, doors
  and weather reuse NPC or tileset colours), and some animations **fade or cycle entries by index** in code: those
  indices are locked. Map onto the vanilla `.pal` unless the row is NET_NEW.
- **Theme (layer 2):** lightsabers and blasters from the faction themes (`Saber Blue`, `Saber Red`, `Signal Red`),
  weather from the planet theme of its map, hyperspace from `kyber-gold` / `hyperspace-console`.
- **Post-processing:** `enforce raw.png fx.png --pal <vanilla>.pal` (or `--theme ... --write-pal` for NET_NEW),
  then `check`.

## Art audit (2026-11-01)

A pass over every VFX row in `wiki/database/pending_art.csv` (989 rows across the kinds above) and the move
scripts in `game/data/battle_anim_scripts.s`, to decide which effects reuse Emerald art and which need a new
drawing. Nothing was built and no CSV was changed; this is the list to work from.

**How it was checked.** Each `graphics/battle_anims/` sheet was traced from `src/graphics.c` to its
`ANIM_TAG_*` in `src/data/battle_anim.h`, then to every `Move_` / `General_` / `Status_` / `Special_` script
that loads it (following `call` / `goto` chains), plus sheets the C code loads directly (masks, Substitute,
stat shimmer, BG tasks). Field effects, doors, weather and transitions were checked against
`src/field_effect.c`, `src/field_door.c`, `src/battle_transition.c` and the wiki rows.

### Totals

| Bucket | Pieces | Meaning |
|---|---|---|
| **NEW** | **13** | Star Wars effects with no Emerald art to start from. Draw from scratch. |
| **RESKIN** | **33** | Emerald file shows Pokémon branding or an off-theme object. Redraw in place, same size and frames. |
| **MATCH TILESET** | **79** | Overworld effects and doors that must match a redrawn biome. Recolor or light redraw once `tile-generator` lands that area. |
| OPTIONAL | 7 (+9 weather recolors) | Flavor upgrades. Fine to ship as vanilla. |
| KEEP | 234 | Generic effects (fire, water, impacts, sparkles, shadows, emotes). Reuse as is. |
| SKIP | 111 | Never loaded by the game, or already marked CUT. No art. |

So the drawing list for a first playable pass is **46 pieces** (NEW + RESKIN). The 79 tileset matches come later
and are mostly palette work.

### 1. NEW: draw from scratch (13)

Battle move sheets. Add these as new sheets: most of the vanilla sheets these moves use are shared with other
moves that keep their look, so overwriting them would change those moves too.

| # | Effect | Row | Starts from (placeholder) | Notes |
|---|---|---|---|---|
| 1 | VIBROBLADE slash | `anim:Move_CUT` | `cut.png` | `cut.png` is shared by 6 moves (AERIAL ACE, FURY CUTTER...). New sheet. |
| 2 | TURBOLASER bolt + beam | `anim:Move_HYPER_BEAM` | `orbs.png` | `orbs.png` is shared by 12 moves. New sheet, green bolt. |
| 3 | FORCE PUSH shockwave | `anim:Move_PSYCHIC` | `backgrounds/psychic.png` | Psychic BG is shared by 17 moves. New ripple sprite or BG. |
| 4 | FORCE BOLT (Force lightning) | `anim:Move_SHOCK_WAVE` | `lightning.png`, `electric_orbs.png` | Both shared with THUNDER / CHARGE. New blue-white arcs. |
| 5 | ION CANNON orb | `anim:Move_ZAP_CANNON` | `black_ball_2.png` | `black_ball_2.png` is only used by this move, so it can be **redrawn in place**. |
| 6 | SABER SLASH arc + scorch | `net:vfx-saber-slash` | `slash.png` | Net-new move. `Saber Blue` / `Saber Red` themes. |
| 7 | BLASTER SHOT bolt + impact spark | `net:vfx-blaster-bolt` | `yellow_star.png` (SWIFT) | Also reused by raid cutscenes. `Signal Red`. |
| 8 | FORCE CHOKE grip | `net:vfx-force-choke` | CRUNCH (`sharp_teeth.png`) | Mostly motion (lift and shake); one small dark grip/glow sheet. |

Overworld and transitions:

| # | Effect | Row | Starts from | Notes |
|---|---|---|---|---|
| 9 | Hyperspace jump (starlines, flash, arrival) | `net:vfx-hyperspace-jump` | FLDEFF_USE_FLY | Plays on every planet ride. `kyber-gold` / `hyperspace-console`. |
| 10 | Lightsaber ignition (overworld) | `net:vfx-saber-ignite` | FLDEFF_SPARKLE | Vader, Obi-Wan, Luke cutscenes. Blue and red variants from one sheet. |
| 11 | Force push ripple (overworld) | `net:vfx-force-push-field` | FLDEFF_USE_STRENGTH | Optional flavor on STRENGTH boulders. |
| 12 | Vader battle transition (red blade slices screen) | `net:vfx-transition-vader` | `team_magma.png` wipe | |
| 13 | Boba Fett battle transition (reticle + T-visor wipe) | `net:vfx-transition-boba-fett` | `team_aqua.png` wipe | Unused `battle_anims/sprites/reticle.png` is a possible base. |

### 2. RESKIN: redraw the Emerald file in place (33)

**Move animation sheets (10).** Pokémon objects inside moves we keep.

| Sheet | Used by | Redraw as |
|---|---|---|
| `sprites/pokeball.png` | BATON PASS | capture pod |
| `sprites/substitute.png` + `substitute_back.png` | every Substitute | decoy (training remote or holo-decoy), front and back |
| `sprites/coin.png` | CREDIT TOSS | Imperial credit chips |
| `sprites/breaking_egg.png` | SELF REPAIR (was Soft-Boiled) | droid repair spark / spare part |
| `sprites/large_fresh_egg.png` | SEED BOMB (was Egg Bomb) | seed pod |
| `sprites/milk_bottle.png` | MILK DRINK | blue milk jug |
| `sprites/magnifying_glass.png` | FORESIGHT | macrobinoculars |
| `sprites/bent_spoon.png` | TELEKINESIS | floating stone or tool (the spoon is an Alakazam joke) |
| `sprites/pencil.png` | SKETCH | datapad stylus |

**Battle transitions (12).** Already `HUMAN-TODO` in the wiki.

| Sheet(s) | Redraw as |
|---|---|
| `big_pokeball.png`, `pokeball.png`, `pokeball_trail.png` | capture pod (big wipe, small wipe, trail) |
| `team_magma.png` | Imperial crest |
| `team_aqua.png` | Hutt Cartel crest |
| `groudon.png` / `kyogre.png` / `rayquaza.png` | GREATKRAYT / SANDO / EXOGORTH silhouettes |
| `regis.png` | Aurebesh glyphs instead of Braille dots |
| `frontier_logo.png`, `frontier_logo_center.png`, `frontier_logo_circles.png` | Grand Arena logo (post-game, lowest priority here) |

**Field effects (9).**

| Sheet | Effect | Redraw as |
|---|---|---|
| ~~`bird.png`~~ | Fly mount | **KEEP (owner, 2026-11-01):** the drawn shuttle was rejected; Emerald's bird stays as is. |
| `pokeball_glow.png` | Center heal | bacta vial glow |
| `pokecenter_monitor/0.png`, `1.png` | Center heal monitor | Bacta Center / 2-1B station screen |
| `spotlight.png` | Rayquaza descends | beam over Dagobah for EXOGORTH |
| `deoxys_rock_fragment_*.png` (4) | Birth Island rock | follows that legend's redesign (batched with its creature) |

**Doors (2).** `poke_center.png`, `poke_mart.png` carry the Poké logo, so they need redrawing even before their
tilesets ship.

### 3. MATCH TILESET: recolor or redraw when the biome lands (79)

These carry no branding. They only have to sit on the new ground and buildings, so do them after
`tile-generator` finishes the matching tileset, usually as a palette pass.

- **Field effects (24):** grass (`tall_grass`, `long_grass`, `short_grass`, `cut_grass`, `jump_tall_grass`,
  `jump_long_grass`, `unknown_17`), sand (`sand_footprints`, `deep_sand_footprints`, `bike_tire_tracks`,
  `sand_pile`, `sand_pillar/0-2`), ash on Sullust (`ash`, `ash_launch`, `ash_puff`), `hot_springs_water`,
  disguises (`mountain_disguise`, `tree_disguise`, `sand_disguise_placeholder`), secret base entrances
  (`secret_power_cave`, `secret_power_shrub`, `secret_power_tree`).
- **Doors (47):** one per building style. 32 story doors (towns, gyms, lab, Cycling Road,
  contest hall, Abandoned Ship, Trainer Hill = Death Star site) and 15 Grand Arena doors (`battle_*` and
  `battle_tent*`, post-game).
- **Rotating gates (8):** Bright Tree (Endor) arena turnstiles, `l1-l4`, `t1-t4`, as Ewok wood.

### 4. OPTIONAL flavor (7, plus weather)

| Sheet | Used by | Idea |
|---|---|---|
| `backgrounds/psychic.png` | 17 moves (FORCE WAVE, MIND TRICK, FORCE VISION, FORCE STORM...) | **Palette only:** Force blue / kyber instead of psychedelic pink. One file rethemes 17 moves; best value on this list. |
| `sprites/gold_ring.png` | FORCE WAVE, FORCE PULSE, SUPERSONIC... | Palette only: Force ripple blue |
| `sprites/duck.png` | confusion (status + 3 moves) | spinning stars or tiny probe droids |
| `sprites/sword.png` | SWORDS DANCE | vibroblades |
| `sprites/devil.png` | LOVELY KISS, Nightmare status | Sith mask, or keep |
| `sprites/angel.png` | SWEET KISS | keep or hearts |
| `sprites/item_bag.png` | item steal / knock off / TRICK / COVET | supply pouch |

**Weather (9):** keep all. Rain, fog, clouds, bubbles and snow are generic; ash fits Sullust and sandstorm fits
Tatooine's Dune Sea. Recolor per planet only if a map looks off.

### 5. KEEP: reuse as is (234)

- 191 move animation sheets: elemental particles, impacts, orbs, rings, emotes, BG overlays. Full list in the
  appendix.
- 23 field effects: `arrow`, `bubbles`, `emotion_*` (3), `field_move_streaks` (2), `ground_impact_dust`,
  `hof_monitor_big/small`, `jump_big_splash`, `jump_small_splash`, `record_mix_lights`, `ripple`, `shadow_*` (4),
  `sparkle`, `small_sparkle`, `splash`, `surf_blob`, `water_surfacing`.
- 9 weather sheets and 11 battle transition sheets already `KEEP_ART`.
- All animation scripts: 349 `KEEP_ANIM` move animations, 39 general/status/special, 30 transitions, 59 field
  effects and 14 weather effects keep their code; only the sheets above change.

### 6. SKIP: no art (111)

- **104 move animation sheets that no move loads.** Their `ANIM_TAG_*` is in the picture table but no script
  or C task loads it (Gen 3 leftovers: `hit.png`, `impact_2.png`, `explosion_2-5.png`, `pokeblock.png`,
  `monster_doll.png`, the egg variants, all of `unused/`...). Full list in the appendix. **They work as free tag
  slots for the NEW sheets above**, so the new sheets need no new tag constants.
- 3 field effects already `CUT`: `unused_grass_2`, `unused_grass_3`, `unused_sand`.
- 4 doors never placed on a map: `unused_top`, `unused_bottom` (not in the door table), `battle_tower_old`,
  `unused_battle_frontier` (in the table, no map uses them; check before deleting).

### Gaps found in the wiki

1. **Every PNG row is a blanket `PENDING_ART` / `HOTSWAP`.** All 312 move sheets, 59 field effects, 53 doors and
   9 weather sheets are marked as needing art, so the wiki counts 513 PNGs when about 125 need work. When the
   tool gets built, set KEEP rows to `KEEP_ART` and unused ones to `NO_ART` / `CUT` so the counts are honest.
2. **Field objects (D5) have no owner.** `tools/README.md` gives category D5 (boulders, cut trees, breakable
   rocks, truck, boats, item ball, berry trees) to this tool, but the row list above only names
   `rotating_gates`. The 14 `object_events/pics/misc/*` and 32 `object_events/pics/berry_trees/*` rows are
   claimed by no tool's TODO.
3. **Droid slicing has no VFX row.** `net:droid-slicing` (NET_NEW_DESIGNS.md) calls for a SLICER SPIKE throw
   animation, but nothing in `vfx.csv` tracks it. Placeholder today is the pod throw with a palette swap.
   Likely a 14th NEW piece (spike + data-spark), shared with `sprite-icon-generator` for the item.
4. **Aurebesh tomb puzzle has no field-effect sheet.** `vfx:FLDEFF_USE_TOMB_PUZZLE_EFFECT` changes Braille to
   Aurebesh, but that art lives in the Braille font sheet (F2) and the tomb tiles, not here.
5. **Psychic-themed moves were renamed to Force moves but kept the pink psychic look.** 17 of the 22 renamed
   moves reuse vanilla art (see `wiki/mapping/moves.csv`); the `psychic.png` recolor in section 4 covers most
   of them at once.

## Batches (owner approves 3 at a time)

| Batch | Effects | Status |
|---|---|---|
| 1 | ION CANNON orb, CREDIT TOSS chips, TURBOLASER (new sheet, needs a tag wired), ~~Fly shuttle~~ | APPROVED (shuttle rejected: keep `bird.png`) |
| 2 | blue milk jug (`milk_bottle.png`), macrobinoculars (`magnifying_glass.png`), datapad stylus (`pencil.png`) | IN-REVIEW, all 3 filmed in the ROM |

## To build

1. Read the rows above in `../../wiki/database/` (filter by `kind` / `category`; skip `KEEP*`, `NO_ART` / `NO_AUDIO` and `CUT`).
2. Build a tool that takes one row (its `sw_subject` is the brief, `path` / `asset_file` the Emerald original, `suggested_path` the new name) and generates the asset in the game's format.
3. Show the owner a few samples, iterate, then generate the rest and set each row's status to `DONE`.
4. Finish the pipeline with the palette step above (`palette-enforcer` `enforce`, then `check`); never install a file that fails `check`.

## Appendix: move animation sheets

### KEEP (191)

| Sheet | Used by |
|---|---|
| `backgrounds/attract.png` | Attract (C task) |
| `backgrounds/aurora.png` | AURORA BEAM |
| `backgrounds/cosmic.png` | COSMIC POWER, METEOR MASH |
| `backgrounds/dark.png` | CRUNCH, FAINT ATTACK, PURSUIT, THIEF |
| `backgrounds/drill.png` | AEROBLAST, HORN DRILL, MEGAHORN, SKY ATTACK |
| `backgrounds/fissure.png` | FISSURE |
| `backgrounds/ghost.png` | CONFUSE RAY, DESTINY BOND, GRUDGE, NIGHT SHADE, NIGHTMARE, SHADOW BALL, SHADOW PUNCH, SPITE |
| `backgrounds/guillotine.png` | GUILLOTINE |
| `backgrounds/highspeed.png` | BLIZZARD, EXTREME SPEED, MACH PUNCH, SILVER WIND |
| `backgrounds/ice.png` | ICE BALL, ICY WIND, SHEER COLD |
| `backgrounds/impact.png` | FOCUS PUNCH, HYPER FANG, MEGA KICK, MEGA PUNCH, SOLAR BEAM |
| `backgrounds/in_air.png` | SEISMIC TOSS, SKY UPPERCUT |
| `backgrounds/sandstorm_brew.png` | Sandstorm (C task) |
| `backgrounds/scary_face.png` | Scary Face (C task) |
| `backgrounds/thunder.png` | THUNDER |
| `backgrounds/water.png` | Surf, Muddy Water (C task) |
| `masks/cure_bubbles.png` | Refresh/Aromatherapy cure (C task) |
| `masks/curse.png` | Curse (C task) |
| `masks/light_beam.png` | Light beam (C task) |
| `masks/metal_shine.png` | Iron Defense/Metal shine (C task) |
| `sprites/air_wave.png` | AIR CUTTER, SONIC BLAST |
| `sprites/air_wave_2.png` | AEROBLAST, RAZOR WIND |
| `sprites/alert.png` | TELEKINESIS |
| `sprites/amnesia.png` | AMNESIA |
| `sprites/anger.png` | FRUSTRATION, RAGE, SWAGGER, TAUNT, TORMENT |
| `sprites/bell.png` | HEAL BELL |
| `sprites/bird.png` | SKY ATTACK |
| `sprites/black_ball.png` | OCTAZOOKA, SMOKESCREEN |
| `sprites/black_ball_2.png` | ION CANNON |
| `sprites/black_smoke.png` | SMOKESCREEN |
| `sprites/blue_star.png` | ABSORB, DREAM EATER, GIGA DRAIN, General_IngrainHeal, General_LeechSeedDrain, General_WishHeal, LEECH LIFE, MEGA DRAIN, MILK DRINK, MOONLIGHT, MORNING SUN, PRESENT, RECOVER, SELF REPAIR, SLACK OFF, SWALLOW, SYNTHESIS |
| `sprites/bluegreen_orb.png` | SKILL SWAP |
| `sprites/bone.png` | BONE CLUB, BONE RUSH, BONEMERANG |
| `sprites/breath.png` | BULK UP, SWAGGER |
| `sprites/bubble.png` | BUBBLE, BUBBLE BEAM, SECRET POWER |
| `sprites/circle_impact.png` | C task (rock/impact) |
| `sprites/circle_of_light.png` | BOGAN PURGE, CHARGE, FORCE BOLT, FORCE STORM, SUPERPOWER, TAIL GLOW, VOLT TACKLE |
| `sprites/clamp.png` | CLAMP, General_TurnTrap, Status_Clamp |
| `sprites/claw_slash.png` | CRUSH CLAW, DRAGON CLAW, METAL CLAW |
| `sprites/confetti.png` | FLATTER |
| `sprites/conversion.png` | CONVERSION, CONVERSION 2 |
| `sprites/cross_impact.png` | CROSS CHOP, LEAF BLADE |
| `sprites/cut.png` | AERIAL ACE, AIR CUTTER, FURY CUTTER, GUILLOTINE, VIBROBLADE, VICE GRIP |
| `sprites/dirt_mound.png` | DIG |
| `sprites/eclipsing_orb.png` | DEFENSE CURL |
| `sprites/electric_orbs.png` | CHARGE, FORCE BOLT |
| `sprites/electricity.png` | CHARGE, VOLT TACKLE |
| `sprites/explosion.png` | DETONATE, DYNAMIC PUNCH, General_DoomDesireHit, PRESENT, SEED BOMB, SELF DESTRUCT |
| `sprites/explosion_6.png` | DYNAMIC PUNCH |
| `sprites/eye.png` | MEAN LOOK |
| `sprites/eye_sparkle.png` | GLARE, SCARY FACE, TICKLE |
| `sprites/fang_attack.png` | HYPER FANG, POISON FANG, SUPER FANG |
| `sprites/finger.png` | FOLLOW ME, METRONOME |
| `sprites/finger_2.png` | TAUNT |
| `sprites/fire.png` | SACRED FIRE, TRI ATTACK |
| `sprites/fire_plume.png` | BLAST BURN, DRAGON RAGE, SACRED FIRE |
| `sprites/flat_rock.png` | SUPERPOWER |
| `sprites/flower_0.png` | AROMATHERAPY, PETAL DANCE |
| `sprites/flower_1.png` | AROMATHERAPY, PETAL DANCE |
| `sprites/flying_dirt.png` | General_Sandstorm, HEAT WAVE, SANDSTORM |
| `sprites/focus_energy.png` | ENDURE, FOCUS ENERGY, General_FocusPunchSetUp |
| `sprites/ghostly_spirit.png` | CURSE, Status_Curse |
| `sprites/glowy_red_orb.png` | SIGNAL BEAM, WATER SPORT, WATER SPOUT |
| `sprites/gold_stars.png` | METEOR MASH, WISH |
| `sprites/gray_orb.png` | REVERSAL, SPIT UP, STOCKPILE, SWALLOW |
| `sprites/gray_smoke.png` | OCTAZOOKA |
| `sprites/green_light_wall.png` | BARRIER, BRICK BREAK, CRUSH CLAW, LIGHT SCREEN, MAGIC COAT, MIRROR COAT, REFLECT |
| `sprites/green_sparkle.png` | MOONLIGHT, PRESENT |
| `sprites/green_spike.png` | NEEDLE ARM, SECRET POWER |
| `sprites/green_star.png` | MORNING SUN |
| `sprites/guard_ring.png` | SAFEGUARD |
| `sprites/gust.png` | GUST, RAZOR WIND, STEEL WING, WING ATTACK |
| `sprites/hail.png` | General_Hail, HAIL, WEATHER BALL |
| `sprites/hands_and_feet.png` | ARM THRUST, BEAT UP, BLAZE KICK, BRICK BREAK, COMET PUNCH, COUNTER, CROSS CHOP, DIZZY PUNCH, DOUBLE KICK, DYNAMIC PUNCH, FIRE PUNCH, FOCUS PUNCH, HI JUMP KICK, ICE PUNCH, JUMP KICK, KARATE CHOP, LOW KICK, MACH PUNCH, MEGA KICK, MEGA PUNCH, METEOR MASH, NEEDLE ARM, REVERSAL, ROCK SMASH, ROLLING KICK, SECRET POWER, SHADOW PUNCH, STOMP, THRASH, THUNDER PUNCH, TRIPLE KICK |
| `sprites/hollow_orb.png` | DRAGON DANCE, IMPRISON |
| `sprites/horn_hit.png` | FURY ATTACK, HORN ATTACK, HORN DRILL |
| `sprites/horn_hit_2.png` | MEGAHORN |
| `sprites/ice_chunk.png` | ICE BALL |
| `sprites/ice_crystals_0.png` | BLIZZARD, CRABHAMMER, General_Hail, HAIL, ICE BALL, ICE BEAM, ICE PUNCH, ICY WIND, POWDER SNOW, SECRET POWER, TRI ATTACK, WATERFALL, WEATHER BALL |
| `sprites/ice_crystals_1.png` | BLIZZARD, CRABHAMMER, General_Hail, HAIL, ICE BALL, ICE BEAM, ICE PUNCH, ICY WIND, POWDER SNOW, SECRET POWER, TRI ATTACK, WATERFALL, WEATHER BALL |
| `sprites/ice_crystals_2.png` | BLIZZARD, CRABHAMMER, General_Hail, HAIL, ICE BALL, ICE BEAM, ICE PUNCH, ICY WIND, POWDER SNOW, SECRET POWER, TRI ATTACK, WATERFALL, WEATHER BALL |
| `sprites/ice_crystals_3.png` | BLIZZARD, CRABHAMMER, General_Hail, HAIL, ICE BALL, ICE BEAM, ICE PUNCH, ICY WIND, POWDER SNOW, SECRET POWER, TRI ATTACK, WATERFALL, WEATHER BALL |
| `sprites/ice_crystals_4.png` | BLIZZARD, CRABHAMMER, General_Hail, HAIL, ICE BALL, ICE BEAM, ICE PUNCH, ICY WIND, POWDER SNOW, SECRET POWER, TRI ATTACK, WATERFALL, WEATHER BALL |
| `sprites/ice_cube_0.png` | SHEER COLD, Status_Freeze |
| `sprites/ice_cube_1.png` | SHEER COLD, Status_Freeze |
| `sprites/ice_cube_2.png` | SHEER COLD, Status_Freeze |
| `sprites/ice_cube_3.png` | SHEER COLD, Status_Freeze |
| `sprites/ice_spikes.png` | ICY WIND |
| `sprites/icicle_spear.png` | ICICLE SPEAR |
| `sprites/impact.png` | ABSORB, AEROBLAST, AIR CUTTER, ANCIENT POWER, ARM THRUST, BEAT UP, BIDE, BITE, BLAST BURN, BLAZE KICK, BODY SLAM, BOGAN PURGE, BONE CLUB, BONE RUSH, BONEMERANG, BOUNCE, BRICK BREAK, CLAMP, COMET PUNCH, COUNT, COUNTER, CREDIT TOSS, CRUNCH, DIG, DIZZY PUNCH, DOUBLE EDGE, DOUBLE KICK, DOUBLE SLAP, DRILL PECK, DYNAMIC PUNCH, ENDEAVOR, EXTREME SPEED, FAINT ATTACK, FALSE SWIPE, FIRE PUNCH, FLAIL, FLY, FOCUS PUNCH, FRENZY PLANT, FRUSTRATION, FURY ATTACK, GIGA DRAIN, GUILLOTINE, GUST, General_LeechSeedDrain, General_MonHit, General_TurnTrap, HEADBUTT, HI JUMP KICK, HORN ATTACK, HORN DRILL, ICE PUNCH, ICICLE SPEAR, IRON TAIL, JUMP KICK, KARATE CHOP, KNOCK OFF, LEECH LIFE, LOW KICK, MACH PUNCH, MAGICAL LEAF, MEGA DRAIN, MEGA KICK, MEGA PUNCH, MEGAHORN, METEOR MASH, NEEDLE ARM, OVERHEAT, PECK, PETAL DANCE, PIN MISSILE, POISON STING, POISON TAIL, POUND, PURSUIT, QUICK ATTACK, RAGE, RAPID SPIN, RAZOR LEAF, RAZOR WIND, RETURN, REVENGE, REVERSAL, ROCK BLAST, ROCK SMASH, ROLLING KICK, ROLLOUT, SECRET POWER, SEISMIC TOSS, SHADOW PUNCH, SKULL BASH, SKY ATTACK, SKY UPPERCUT, SLAM, SONIC BLAST, SPARK, SPIKE CANNON, SPIT UP, STEEL WING, STOMP, STRENGTH, STRUGGLE, SUBMISSION, SWIFT, Special_BallThrow, Status_Clamp, TACKLE, TAKE DOWN, THIEF, THRASH, THUNDER PUNCH, TRIPLE KICK, TWINEEDLE, TWISTER, VICE GRIP, VITAL THROW, WEATHER BALL, WING ATTACK |
| `sprites/jagged_music_note.png` | UPROAR |
| `sprites/leaf.png` | LEAF BLADE, MAGICAL LEAF, RAZOR LEAF, SECRET POWER, TWISTER |
| `sprites/leer.png` | LEER |
| `sprites/letter_z.png` | REST, SLEEP TALK, Status_Sleep |
| `sprites/lick.png` | LICK |
| `sprites/lightning.png` | FORCE BOLT, THUNDER, THUNDER PUNCH, TRI ATTACK |
| `sprites/lock_on.png` | TARGET LOCK |
| `sprites/magenta_heart.png` | ATTRACT, CHARM, COVET, LOVELY KISS, SWEET KISS, Status_Infatuation |
| `sprites/metal_sound_waves.png` | METAL SOUND |
| `sprites/meteor.png` | SUPERPOWER |
| `sprites/mist_cloud.png` | MIST, POISON GAS, SMOG |
| `sprites/moon.png` | MOONLIGHT |
| `sprites/movement_waves.png` | STRUGGLE |
| `sprites/mud_sand_0.png` | DIG, FISSURE, General_TurnTrap, MUD SLAP, MUD SPORT, ROLLOUT, SAND ATTACK, SAND TOMB, Status_SandTomb |
| `sprites/mud_sand_1.png` | DIG, FISSURE, General_TurnTrap, MUD SLAP, MUD SPORT, ROLLOUT, SAND ATTACK, SAND TOMB, Status_SandTomb |
| `sprites/music_notes.png` | BELLY DRUM, FAKE TEARS, GRASS WHISTLE, SING, TEETER DANCE |
| `sprites/music_notes_2.png` | HEAL BELL, PERISH SONG |
| `sprites/nail.png` | CURSE |
| `sprites/needle.png` | LEECH LIFE, PIN MISSILE, POISON STING, SPIKE CANNON, TWINEEDLE |
| `sprites/noise_line.png` | GROWL, HOWL, ROAR |
| `sprites/opening_eye.png` | MIND READER |
| `sprites/orbs.png` | ABSORB, DREAM EATER, GIGA DRAIN, General_IngrainHeal, General_LeechSeedDrain, INGRAIN, LEECH LIFE, MEGA DRAIN, MIMIC, RECOVER, SOLAR BEAM, TURBOLASER |
| `sprites/pain_split.png` | PAIN SPLIT |
| `sprites/paw_print.png` | ASSIST |
| `sprites/pink_cloud.png` | General_SmokeballEscape, YAWN |
| `sprites/pink_petal.png` | SWEET SCENT |
| `sprites/poison_bubble.png` | ACID, POISON FANG, POISON GAS, POISON POWDER, POISON STING, POISON TAIL, SLUDGE, SLUDGE BOMB, TOXIC |
| `sprites/poison_powder.png` | POISON POWDER, SLEEP POWDER, STUN SPORE |
| `sprites/protect.png` | PROTECT |
| `sprites/purple_flame.png` | GRUDGE |
| `sprites/purple_hand_outline.png` | BELLY DRUM |
| `sprites/purple_scratch.png` | REVENGE |
| `sprites/purple_swipe.png` | REVENGE |
| `sprites/rain_drops.png` | General_Rain, RAIN DANCE |
| `sprites/rainbow_rings.png` | AURORA BEAM |
| `sprites/rapid_spin.png` | RAPID SPIN |
| `sprites/razor_leaf.png` | MAGICAL LEAF, RAZOR LEAF, SECRET POWER |
| `sprites/recycle.png` | RECYCLE |
| `sprites/red_ball.png` | BARRAGE |
| `sprites/red_orb.png` | HIDDEN POWER |
| `sprites/rocks.png` | ANCIENT POWER, ROCK BLAST, ROCK SLIDE, ROCK SMASH, ROCK THROW, ROCK TOMB, ROLLOUT, SECRET POWER, SEISMIC TOSS, TWISTER, WEATHER BALL |
| `sprites/roots.png` | FRENZY PLANT, INGRAIN |
| `sprites/round_shadow.png` | BOUNCE, DIVE, FLY |
| `sprites/round_white_halo.png` | MIND READER |
| `sprites/scratch.png` | SCRATCH |
| `sprites/seed.png` | BULLET SEED, LEECH SEED |
| `sprites/shadow_ball.png` | SHADOW BALL |
| `sprites/sharp_teeth.png` | BITE, CRUNCH, SECRET POWER |
| `sprites/shock_3.png` | THUNDERBOLT |
| `sprites/slam_hit.png` | SECRET POWER, SLAM, VINE WHIP |
| `sprites/slam_hit_2.png` | KNOCK OFF |
| `sprites/slash.png` | FALSE SWIPE, SLASH |
| `sprites/small_bubbles.png` | ASHLA MIST, BUBBLE, BUBBLE BEAM, DIVE, FAKE TEARS, SECRET POWER, WATER GUN, WATER PULSE, WATERFALL, WEATHER BALL |
| `sprites/small_ember.png` | BLAZE KICK, DRAGON BREATH, DRAGON CLAW, DRAGON RAGE, EMBER, FIRE BLAST, FIRE PUNCH, FIRE SPIN, FLAME WHEEL, FLAMETHROWER, General_TurnTrap, OUTRAGE, OVERHEAT, Status_Burn, Status_FireSpin, WEATHER BALL |
| `sprites/small_red_eye.png` | GLARE |
| `sprites/smellingsalt_effect.png` | SMELLING SALT |
| `sprites/smokescreen_impact.png` | Smokescreen (C task) |
| `sprites/snore_z.png` | SNORE |
| `sprites/spark_0.png` | FORCE BOLT, THUNDER SHOCK, THUNDER WAVE, THUNDERBOLT, VOLT TACKLE |
| `sprites/spark_1.png` | FORCE BOLT, THUNDER SHOCK, THUNDER WAVE, THUNDERBOLT, VOLT TACKLE |
| `sprites/spark_2.png` | ION CANNON, SPARK, Status_Paralysis, THUNDER SHOCK, THUNDER WAVE, THUNDERBOLT |
| `sprites/spark_h.png` | THUNDER WAVE |
| `sprites/sparkle_1.png` | AROMATHERAPY, COSMIC POWER, General_HeldItemEffect, General_WishHeal, HEAL BELL, REFRESH, SYNTHESIS, WISH |
| `sprites/sparkle_3.png` | LIGHT SCREEN, MIRROR COAT |
| `sprites/sparkle_4.png` | DETECT, DISABLE, REFLECT |
| `sprites/sparkle_6.png` | SILVER WIND |
| `sprites/speed_dust.png` | EXTREME SPEED, TRICK |
| `sprites/sphere_to_cube.png` | SHARPEN |
| `sprites/spider_web.png` | SPIDER WEB |
| `sprites/spikes.png` | SPIKES |
| `sprites/spiral.png` | FORCE FOCUS |
| `sprites/splash.png` | DIVE |
| `sprites/spore.png` | COTTON SPORE, SPORE |
| `sprites/spotlight.png` | ENCORE, FLATTER |
| `sprites/string.png` | STRING SHOT |
| `sprites/sunlight.png` | General_Sun, SUNNY DAY |
| `sprites/sweat_bead.png` | ASTONISH, DIVE |
| `sprites/sweat_drop.png` | ENDEAVOR, FACADE |
| `sprites/swipe.png` | FURY SWIPES |
| `sprites/tag_hand.png` | ENCORE, HELPING HAND, SMELLING SALT |
| `sprites/teal_alert.png` | MIND READER |
| `sprites/tendrils.png` | CONSTRICT, General_TurnTrap, Status_BindWrap |
| `sprites/thin_ring.png` | AROMATHERAPY, CALM MIND, General_HeldItemEffect, HEAL BELL, HYPER VOICE, MILK DRINK, REFRESH, SELF REPAIR, UPROAR |
| `sprites/thought_bubble.png` | FAKE TEARS, METRONOME, TAUNT, TORMENT |
| `sprites/torn_metal.png` | BRICK BREAK, CRUSH CLAW |
| `sprites/toxic_bubble.png` | TOXIC |
| `sprites/tri_attack_triangle.png` | TRI ATTACK |
| `sprites/warm_rock.png` | ERUPTION |
| `sprites/water_impact.png` | CRABHAMMER, DIVE, HYDRO CANNON, HYDRO PUMP, SECRET POWER, WATER GUN, WATER SPOUT, WATERFALL |
| `sprites/water_orb.png` | General_TurnTrap, HYDRO CANNON, HYDRO PUMP, MUD SHOT, SECRET POWER, Status_Whirlpool, WHIRLPOOL |
| `sprites/weather_ball.png` | WEATHER BALL |
| `sprites/web_thread.png` | SPIDER WEB, STRING SHOT |
| `sprites/whirlwind_lines.png` | DRILL PECK, WHIRLWIND |
| `sprites/white_feather.png` | ASHLA MIST, FEATHER DANCE |
| `sprites/white_shadow.png` | DESTINY BOND |
| `sprites/wisp_fire.png` | WILL O WISP |
| `sprites/wisp_orb.png` | WILL O WISP |
| `sprites/x_sign.png` | BLOCK, IMPRISON, ROCK TOMB |
| `sprites/yellow_ball.png` | CONFUSE RAY |
| `sprites/yellow_star.png` | SWIFT |
| `stat_change/tiles.png` | every stat up/down shimmer |

### SKIP: never loaded (104)

`masks/unused_level_up.png`, `sprites/air_slash.png`, `sprites/bell_2.png`, `sprites/blue_burst.png`, `sprites/blue_flames.png`, `sprites/blue_flames_2.png`, `sprites/blue_lines.png`, `sprites/blue_shards.png`, `sprites/bone_2.png`, `sprites/brown_triangle.png`, `sprites/bubble_burst.png`, `sprites/bubble_burst_2.png`, `sprites/clapping.png`, `sprites/claw_slash_2.png`, `sprites/closing_eye.png`, `sprites/closing_eye_2.png`, `sprites/cracked_egg.png`, `sprites/explosion_2.png`, `sprites/explosion_3.png`, `sprites/explosion_4.png`, `sprites/explosion_5.png`, `sprites/fangs.png`, `sprites/fresh_egg.png`, `sprites/fury_swipes.png`, `sprites/gem_1.png`, `sprites/gem_2.png`, `sprites/gem_3.png`, `sprites/glass.png`, `sprites/glass_2.png`, `sprites/hatched_egg.png`, `sprites/hit.png`, `sprites/hit_duplicate.png`, `sprites/humanoid_foot.png`, `sprites/humanoid_hand.png`, `sprites/impact_2.png`, `sprites/impact_3.png`, `sprites/lightbulb.png`, `sprites/lightning_2.png`, `sprites/metal_ball.png`, `sprites/monster_doll.png`, `sprites/monster_foot.png`, `sprites/mud_unk.png`, `sprites/orange.png`, `sprites/orb.png`, `sprites/particles.png`, `sprites/pencil_2.png`, `sprites/petal.png`, `sprites/pink_glove.png`, `sprites/pink_heart_2.png`, `sprites/pink_orb.png`, `sprites/pokeblock.png`, `sprites/punch_impact.png`, `sprites/purple_coral.png`, `sprites/purple_droplet.png`, `sprites/purple_green_unk.png`, `sprites/red_fist.png`, `sprites/red_particles.png`, `sprites/red_tube.png`, `sprites/red_wand.png`, `sprites/reticle.png`, `sprites/ring.png`, `sprites/sap_drip.png`, `sprites/scratch_2.png`, `sprites/scratch_3.png`, `sprites/seed_2.png`, `sprites/shock.png`, `sprites/shock_2.png`, `sprites/shock_4.png`, `sprites/smoke.png`, `sprites/smoke_2.png`, `sprites/snowball.png`, `sprites/spinning_fire.png`, `sprites/spinning_green_orbs.png`, `sprites/sprout.png`, `sprites/string_2.png`, `sprites/sword_2.png`, `sprites/teeth.png`, `sprites/tied_bag.png`, `sprites/tongue.png`, `sprites/unknown.png`, `sprites/vine.png`, `sprites/vine_2.png`, `sprites/void_lines.png`, `sprites/water_column.png`, `sprites/water_droplet.png`, `sprites/water_droplet_2.png`, `sprites/waving_hand.png`, `sprites/web.png`, `sprites/whirlwind.png`, `sprites/whirlwind_2.png`, `sprites/white_bag.png`, `sprites/yellow_unk.png`, `sprites/yellow_unk_2.png`, `sprites/z.png`, `unused/goosuto.png`, `unused/lights.png`, `unused/line_sketch.png`, `unused/line_sketch_2.png`, `unused/metronome_hand_small.png`, `unused/music_notes.png`, `unused/old_beatup.png`, `unused/spinning_ball.png`, `unused/water_gfx.png`, `unused/water_splash.png`
