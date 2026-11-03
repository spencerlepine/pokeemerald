# Net-new designs

One section per `net:` row in `mapping/net_new.csv`. Each design lists the maps it touches, the story flags and vars it
needs, its level band (taken from `database/area_progression.csv`, so nothing sits outside the band of the act it is in),
and the placeholder assets the port can use until the art is drawn the real art.

The new flags and vars come only from slots that `emerald-db/database/story_flags.csv` marks as unused
(`unused=true`), so no existing script is affected.

| Reserved slot | Used by |
|---|---|
| `flag:unused-0x020` | Boba Fett hunt: stage 1 won |
| `flag:unused-0x021` | Boba Fett hunt: stage 2 won |
| `flag:unused-0x022` | Boba Fett hunt: stage 3 won |
| `flag:unused-0x023` | Boba Fett hunt: finale won |
| `var:unused-0x404e` | Boba Fett hunt: current stage (0-4) |
| `flag:unused-0x024` | Death Star site unlocked |
| `flag:unused-0x025` | Death Star site cleared |
| `var:unused-0x4083` | Death Star site: deepest floor reached |
| `var:unused-0x408b` | Dune Sea storm of the day (0 calm, 1 storm) |
| `trainer:terry` (`TRAINER_TERRY`, never placed in Emerald) | Mos Eisley Cantina: Greedo's battle |
| `flag:unused-0x026` | Ben's Hut: Ben's talk heard (Act 1) |
| `flag:unused-0x027` | Maul duel won (post-game, Ben's Hut) |
| `flag:unused-0x028` | Sebulba beaten (podrace grandstand) |
| `flag:unused-0x029` | Jabba's Palace: rancor pit battle done, KING'S ROCK taken |
| `flag:unused-0x02a` | Jabba's Palace: Bib Fortuna's errand done (the Jawa's droid delivered) |
| `flag:unused-0x02b` | Rwookrrorro: the chieftain's TM given |
| `flag:unused-0x02c` | Rwookrrorro: the bowcaster maker's trade done |
| `flag:unused-0x02d` | Mining Facility: the SITH SHARD taken |
| `flag:unused-0x02e` | Endor clearing: the commando's MAX ELIXIR given |
| `flag:unused-0x02f` | Tibanna Refinery: smugglers cleared, Lobot's SMOKE BALL given |
| `flag:unused-0x030` | NiJedha: Chirrut's TWISTEDSPOON given |
| `flag:unused-0x031` | Hoth: the lost scout found |
| `flag:unused-0x032` | Hoth: Rieekan's reward given |
| `flag:unused-0x033` | Kamino: Cody's FOCUS BAND given |
| `var:unused-0x4091` | Jar Jar's next stop (0-6) |
| `flag:unused-0x034` to `0x038` | Death Star item balls, decks 1-5 |

## Planet borders (`net:hangar-*`, `net:border-*`)

Decided 2026-11-02 (owner): every planet is its own map, so every walkable border is cut and replaced by a ship link.
The planet graph is `mapping/hyperlanes.csv` (one row per edge, with the hangar at each end and the unlock), kept
consistent by `python3 -m blockout check` and listed in `world/GUIDE.md`. The rows below are the original per-border
notes; where they differ, `hyperlanes.csv` wins. Level bands stay as they are in Emerald.

| Row | Emerald link | Step 4 change | Level band (both sides) | Placeholder |
|---|---|---|---|---|
| hangar-tatooine-kashyyyk | Mr. Briney's boat, Route 104 → Dewford | The boat becomes Han's freighter. Same script, same flag (`flag:badge01-get`). | badges 0-1, trainers 5-15 | Briney's boat sprite and cottage interior |
| border-tatooine-sullust | Route 112 ↔ Route 113 (walkable edge) | Keep the walk, add a sign "SULLUST LANDING ZONE". Optional later: cut the edge and add a landing pad + shuttle NPC with the same destination. | badges 3, wild 14-16, trainers 16-19 | Route 112 sign, Lilycove ferry NPC |
| border-tatooine-mustafar | Cable car, Route 112 → Mt. Chimney | The cable car becomes a shuttle ride. The script and fade are unchanged. | badges 3, trainers 18-25 | Cable car sprite |
| border-sullust-tatooine-115 | Meteor Falls 1F ↔ Route 115 | Cave mouth signposted as a lava tube. No change. | badges 3-5 | Meteor Falls tiles |
| border-tatooine-endor | Route 118 (Mauville east) | Add a hangar building at the east exit with a pilot NPC. Walking through still works, so badge gating is unchanged (`item:hm-surf`, `flag:badge05-get`). | badges 5, trainers 14-26 | Pokémon Center exterior recolored, sailor NPC |
| border-endor-bespin | Route 121 → Lilycove | Sign "CLOUD CITY SHUTTLE" at the edge. | badges 6, trainers 25-34 | Route sign |
| border-bespin-jedha | Lilycove → Route 122 (Surf) | Surf text becomes "skim the cloud sea". | badges 6 | none |
| border-seas | Routes 124-134 | Surf text becomes "hyperlane skim" (Step 4 text pass only). | badges 6-7, trainers 32-34 | none |

## Boba Fett's bounty hunt (`net:boba-fett-hunt`)

A side story where Boba Fett tracks the player across four worlds. Boba is a person: he is a boss trainer and is never
catchable, never traded and never joins the party. His companions are droids and beasts.

| Stage | Map (Emerald) | Trigger | Boba's team | Band check |
|---|---|---|---|---|
| 1 | Route 121, Endor (south of the Safari Zone) | `flag:badge06-get`, var = 0 | 3 companions, levels 31-33 | trainers here are 25-32, Cloud City 31-34 |
| 2 | Mt. Pyre summit, Jedha | stage 1 won, var = 1 | 4 companions, levels 33-34 | summit trainer is 32 |
| 3 | Route 134, Kamino (Boba's home world) | `flag:badge07-get`, var = 2 | 4 companions, levels 35-36 | route trainers 32-34, Dagobah arena 35-46 |
| Finale | Victory Road B1F, Ilum (Crystal Caves) | stage 3 won, var = 3 | 5 companions, levels 43-45 | cave trainers 41-45 |

- Each win sets its flag and raises `var:unused-0x404e`. Losing has no penalty, and Boba waits at the same spot.
- Prize money uses Matt's trainer class, so the payout scale doesn't change. The finale gives a held item only (QUICK CLAW), with no new power.
- Placeholders: Matt's trainer pic and overworld sprite (`aqua_admin_m`); his battle music; party slots start from Matt's story team (MIGHTYENA and GOLBAT at level 34), filled out and re-leveled to each stage band.
- Texts: four intro, defeat and post-battle triples (12 new texts), written in Step 4 in the same voice as his story lines.

## Slicing droids (`net:droid-slicing`)

- Droid companions are "sliced" with a SLICER SPIKE instead of caught in a pod. This is a text and animation change only.
- A pod thrown at a droid shows the slicing text. The catch formula is untouched: the item keeps the ball ID, catch modifier and price of the pod it stands in for.
- Step 4 needs a list of droid species. It comes from `mapping/species.csv` (sw_basis or description says droid).
- Placeholders: the POKé BALL throw animation with a palette swap; item icon from `item:poke-ball`.
- No flags. No level band, because it applies everywhere.

## Death Star construction site (`net:death-star-site`)

- **Entry:** a new shuttle NPC in the Yavin 4 Space Center 1F (`map:mossdeep-city-space-center-1f`). It appears once `flag:sys-game-clear` is set and then sets `flag:unused-0x024`.
- **Maps:** 5 new floors (DS-1 to DS-5). They are built by copying the Trainer Hill floor layout, since it already has elevators and a lobby. Each floor has 3 stormtrooper or officer trainers and one item ball. DS-5 holds a final officer battle that sets `flag:unused-0x025`.
- **Level band:** trainers 60-70, wild none. This matches the Grand Arena "open level" band, and the area is post-game only, so main-story progression is unaffected.
- **Rewards:** items only (rare candy, PP up, one of each held item already sold at the Grand Arena). There are no new companions.
- **Placeholders:** Trainer Hill tileset and elevator scripts; stormtrooper overworld = Team Magma grunt sprite; trainer pics `magma_grunt_m`, `magma_admin`.

## Dune Sea and SAND SKIM (`net:dune-sea`, `net:move-sand-skim`, `net:hm09-sand-skim`, `net:dune-sea-encounters`, `net:trainer-class-skiff-rider`)

Owner decision (2026-11-03): Tatooine's sea is sand, and the player crosses it on a sand skiff with its own move,
not SURF. Every other planet keeps SURF on its water (and on Bespin's cloud sea).

**What the player sees.** Deep, soft dunes fill the places where Emerald had sea on Tatooine. Walking stops at
their edge. A companion that knows SAND SKIM pulls the player across on a skiff. It plays like SURF:
wild companions appear while skimming and trainers wait out on the dunes. There is no fishing: a rod can't be
cast on the Dune Sea (owner, 2026-11-03).

**Where.** Every `~` cell on Tatooine: Routes 102, 103, 104, 110, 111, 115 and 117 (and the dock in the Mos Eisley
star-liner room, which is scenery). Same cells as Emerald's sea, so no map changes shape. The Route 111 desert
stays walkable sand; the Dune Sea is the deep sand around it. Mos Entha's pond and the Mos Eisley harbour left
those towns when they were made compact, so in the new layout their Dune Sea tables never run. The
current game still has those cells, so their tables are set like the rest.

**The move: SAND SKIM.**

| Field | Value |
|---|---|
| Type | Ground |
| Power / accuracy / PP | 80 / 100 / 15 |
| Target | both foes (like SURF) |
| Contact / side effect | none / none |
| Contest | SURF's data |
| Taught by | HM09 only (no level-up or tutor) |
| Field use | crosses the Dune Sea; needs badge 5, like SURF |
| Animation (placeholder) | SURF's wave recoloured to sand |

80 power keeps it under SURF (95) and EARTHQUAKE (100, TM26 around badge 7). Ground hits five types
super-effectively and Water only three, so an equal 95 would make it the better move. Flying companions and
LEVITATE ignore it, which also keeps it in check.

**The HM.** HM09 SAND SKIM takes the unused item slot right after HM08 (`ITEM_15B`), so the HM range stays
one block. OWEN gives it in Mos Entha together with HM03 SURF, at the moment Emerald gives HM03 (after the
fifth badge). Both arrive together, so nothing anywhere opens earlier or later than in Emerald, and the blockout
reach checks need no change: on Tatooine, `item:hm-surf` in the balance table means HM09.

**Who can learn it.** A rule list, kept in `mapping/sand_skim_rules.csv` (one row per type or species, with the
reason). `python3 tools/sand_skim.py` applies it to every species and writes `database/sand_skim.csv` (types,
SURF for comparison, SAND SKIM, the rule and where the species is first caught).

| Rule | Learns | Why |
|---|---|---|
| Ground type (either slot) | yes | They burrow, dig or stride over sand: dewbacks, krayts, banthas, rontos, rock warts. |
| SUNSTRIDER, SUNBLAZER (Torchic line) | yes | Long-legged desert runners of Tatooine. |
| EOPIE, FATHIER (Ponyta line) | yes | Pack and racing beasts bred to haul over sand. |
| JOOPA (Dunsparce) | yes | Young burrowing sand worm that swims through loose sand. |
| A species that learns no TM or HM at all | no | Same rule as every HM. |
| Everything else | no | |

That is 42 species. To add a type (say Rock) or a species, add a row to the rules file and re-run the tool.

**Balance checks (run by the tool).**
- Two of the three starters can learn it: the Mudkip line (MARSHRUNNR, MARSHTITAN) and the Torchic line (SUNSTRIDER, SUNBLAZER). A Treecko player catches one.
- Seven learners are catchable before the fifth badge: HIVEGRUB (Route 116), ROCKWART (Granite Cave), BANTHACALF (Jagged Pass), BOGWHISKR (Meteor Falls), and DEWLING, KRAYTHATCH and HOLOSHARD in the Route 111 desert.
- No one can be stuck: the HM, the badge and the learners are all in hand before the first Dune Sea cell matters.

**Encounters on the Dune Sea.** The Dune Sea has its own table: Emerald's sea ("water") table of that map, with
every slot, level and rate kept and the sea species swapped for sand species (`mapping/dune_sea_swaps.csv`; a
row can be limited to some maps and slots). The fishing tables of these maps are deleted, because the Dune Sea has
no fishing. The result is `database/dune_sea_encounters.csv`, one row per slot with its stat-total change.

| Emerald sea species | Dune Sea species | Where | Why |
|---|---|---|---|
| DIANOGLET (Tentacool) | KRAYTHATCH (Trapinch) | all | Krayt hatchlings dig their pits in deep dunes. |
| BLOOPRAT (Marill), 30% slot | CRABDROID (Corphish) | Mos Entha, Routes 102 and 117 | Its only home was the rods on these maps, so it moves here. |
| BLOOPRAT (Marill) | DEWLING (Sandshrew) | all other slots | Dewback hatchlings roll through the sand. |
| HORNFIN (Goldeen), 1% | SARLACLET (Gulpin) | all | A young sarlacc waiting under the sand. |
| SHYYYOLET, SHYYYO | kept | all | Birds glide over the dunes. |

The tool checks that no species loses its last wild home. Cutting the rods only touched CRABDROID, which is
why it takes the 30% slot on its three maps (levels 10-20, inside its old rod range). Everything else that was
fished there is still wild elsewhere. No new species enter the Hoenn dex.

**In the game (2026-11-03).** `python3 tools/sand_skim.py --install` writes these tables into
`../game/src/data/wild_encounters.json` (sea species swapped, fishing tables removed); a plain run reports
whether the game still matches. `../game/src/data/dune_sea_maps.h` lists the Dune Sea maps, and
`CanFish()` in `src/item_use.c` refuses the rod on them (Dad's "not the time" line). SURF still crosses the
Dune Sea until SAND SKIM is ported.

**Trainers.** The two Route 103 trainers out on the Dune Sea (POLESH and ILI) become a new class, SKIFF RIDER,
with the swimmer classes' prize money and AI. Their parties do not change. Their lines are rewritten for skiffs.

**Texts.** Rewritten in `mapping/texts/` (notes say "Dune Sea"): Dad's badge speech, OWEN's gift and his tip,
Alexia, WATTO's ESPA GENERATOR hint, the Route 103 shortcut hint, the Route 104 lake line, POLESH, ILI, and the
two swoop-rally racers (swimming becomes skimming). New field texts for the port:

| Text | Line |
|---|---|
| Facing the Dune Sea, no SAND SKIM | `Deep, soft sand rolls on like a sea.\nA COMPANION may be able to cross it.$` |
| Facing the Dune Sea, can skim | `The dunes roll on like a sea…\nWould you like to use SAND SKIM?$` |
| Using it | `{STR_VAR_1} used SAND SKIM!$` |
| Trying SURF on the Dune Sea | `This is sand, not water.\nSURF won't work here.$` |
| Item description | `Teaches SAND SKIM. Lets a\nCOMPANION pull a skiff over sand.` |

**Art (placeholders until drawn).** Player while skimming: the SURF sprite (owner, 2026-11-03), later a sand skiff
with the companion towing. Wake: the SURF ripple, later a sand spray. Battles on the Dune Sea: the sand battle
background that Emerald already has. Dune Sea tiles: the `sw-tatooine` `dune-sea` rows in `mapping/terrain.csv`.

**In the game (2026-11-03).** SAND SKIM is playable. SURF stays as it was everywhere else.
- `MOVE_SAND_SKIM` (355, after the last move; `MOVES_COUNT` 356): battle data, name, description, contest data
  (Tough, no combo) and animation (SURF's wave in MUDDY WATER's brown, SURF's sound) in `data/battle_anim_scripts.s`.
- `ITEM_HM09` takes the unused `ITEM_15B` slot; `NUM_HIDDEN_MACHINES` 9; `F(SAND_SKIM)` ends `FOREACH_HM` in
  `include/constants/tms_hms.h`, which gives `ITEM_HM_SAND_SKIM`, the learnset bit and the TM/HM move table entry.
  HM range checks (`field_specials.c`, `item_menu.c`) run to HM09. The Ground HM icon palette.
- Learnsets: `python3 tools/sand_skim.py --install` writes `.SAND_SKIM = TRUE` into `src/data/pokemon/tmhm_learnsets.h`
  for exactly the species in `database/sand_skim.csv`; a plain run reports any difference.
- Field use: `FIELD_MOVE_SAND_SKIM` in the party menu (needs badge 5). The Dune Sea is the map list in
  `src/data/dune_sea_maps.h` (`IsCurrentMapDuneSea()`): there SAND SKIM crosses, SURF does not ("You can't SURF
  here"), facing the sand offers `EventScript_UseSandSkim` (`data/scripts/surf.inc`, texts in `data/text/surf.inc`),
  and the battle background is sand. Facing the sand without SAND SKIM shows "Deep, soft sand rolls on like a
  sea. A COMPANION may be able to cross it." (`EventScript_CantSandSkim`).
- The skiff: on Dune Sea maps `FldEff_SurfBlob` uses `gFieldEffectObjectTemplate_SandSkiff`, a placeholder
  (`graphics/field_effects/pics/sand_skiff.png`, the surf blob in sand colours with a plank seam; row
  `net:vfx-sand-skiff`). The player still uses the SURF sprite.
- `TRAINER_CLASS_SKIFF_RIDER` (0x42, the first unused class slot) for POLESH and ILI, 2 money per level like the
  swimmers. Their pics and overworld sprites are still the swimmer ones.
- HM09 can't be forgotten (it is an HM), and the last companion that knows it can't be released.
- OWEN gives HM09 right after HM03, in the same script and under the same flag.
- Tested in the emulator: the rod and SURF are refused on Route 103, SAND SKIM prompts and crosses, a wild
  encounter on the Dune Sea uses the sand background, OWEN hands over both HMs, SURF still works in Kachirho,
  the no-skim line shows, the skiff shows under the player, and "SKIFF RIDER POLESH" battles.

Still to do: `MB_DUNE_SEA` (an unused metatile behaviour) once the `dune-sea` tiles exist, which can then replace
the map list; the final skiff art and a skimming player sprite; SKIFF RIDER pics and overworld sprites.
Crossing a map connection between Dune Sea and real water while surfing keeps the old blob until the next mount
(cosmetic only).

## Light and dark evolutions (`net:light-dark-evolutions`, `net:item-kyber-crystal`, `net:item-sith-shard`, `net:species-aurareaver`, `net:species-kathwarden`, `net:species-whillguard`)

Owner decision (2026-11-03): a few companion lines can evolve two ways. One way is the usual evolution. The
other is a light-side form (KYBER CRYSTAL) or a dark-side form (SITH SHARD). Kept small: three lines, one met
early, one in the middle and one late.

| Line | Usual evolution | New branch | Item | Types | Stats (HP/Atk/Def/Spe/SpA/SpD) |
|---|---|---|---|---|---|
| AURADANCER (Kirlia), Act 1 | AURAWARDEN, level 30 | AURAREAVER (dark) | SITH SHARD | Psychic / Dark | 68/65/55/110/135/85 = 518 |
| KATHPUP (Electrike), Act 2-3 | KATHHOUND, level 26 | KATHWARDEN (light) | KYBER CRYSTAL | Electric / Psychic | 70/55/90/80/85/95 = 475 |
| ECHOWISP (Shuppet), Act 5 | HOLLOWDOLL, level 37 | WHILLGUARD (light) | KYBER CRYSTAL | Ghost / Psychic | 64/55/95/50/96/95 = 455 |

Rules:
- The new form has the same base stat total as the usual one, split differently: light leans to the defences,
  dark to speed and power. In Emerald, Psychic and Dark moves are special, so the dark form gains special attack.
- Same abilities, learnsets, EXP yield, catch rate and egg data as the usual form. Its eggs hatch into the
  first stage of the line.
- Nothing else moves: no wild table, trainer party or level evolution changes. The usual evolution still
  happens by level; the item is an extra way.

Items: KYBER CRYSTAL and SITH SHARD are used like evolution stones. Both are sold for 2100 at the Pirin Depot
(Lavaridge Mart), right after Mustafar Peak, where the player first meets Vader.

**In the game (2026-11-03).**
- Items in the unused slots after LEAF STONE: `ITEM_KYBER_CRYSTAL` (was `ITEM_063`) and `ITEM_SITH_SHARD`
  (was `ITEM_064`), with the evolution-stone item effect, descriptions, and the BLUE / RED CRYSTAL shard icons
  as placeholders. On sale in `data/maps/LavaridgeTown_Mart/scripts.inc`.
- New forms in the unused old-Unown species slots `SPECIES_OLD_UNOWN_B`, `_C`, `_D`, with the aliases
  `SPECIES_AURAREAVER`, `SPECIES_KATHWARDEN`, `SPECIES_WHILLGUARD` in `include/constants/species.h`
  (`_J` is left alone: the game uses it for the "?" icon). Every species table has an entry: name, stats,
  learnsets, pics, palettes, icon, footprint, coordinates and animations. The pics and icon are the usual
  form's. The battle palette is a tinted copy (`graphics/pokemon/<name>/normal.pal`): red-black for dark,
  blue-white for light.
- `src/data/pokemon/evolution.h`: one `EVO_ITEM` line under KIRLIA, ELECTRIKE and SHUPPET.
- Cries: `SpeciesToCryId` plays the usual form's cry.
- Tested in the emulator: the bag shows both items, each evolves only its own line ("No use." on the others),
  all three evolution scenes play, and the summary shows the new types.

Still to do (TODO rows): front, back, icon and footprint art for the three forms; their cries
(`net:cry-*` in `mapping/audio.csv`); item icons; Datapad entries. The Datapad lists 386 species, so the
old-Unown slots have no Datapad page yet and the forms are not counted in it. More lines can follow the same
pattern while old-Unown slots remain (B to Z, minus J).

## New moves (`net:move-force-choke`, `net:move-blaster-shot`, `net:move-saber-slash`)

Each new move clones an existing move's data row. Only the name, description and animation are new.

| New move | Clone of | Type / power / accuracy / PP | Who learns it |
|---|---|---|---|
| FORCE CHOKE | CRUNCH | Dark 80 / 100 / 15 | Replaces CRUNCH in the learnsets of Dark lines that already learn it (same level) |
| BLASTER SHOT | SWIFT | Normal 60 / -- / 20 | Replaces SWIFT for droid lines that already learn it |
| SABER SLASH | SLASH | Normal 70 / 100 / 20 | Replaces SLASH (same level) for lines that wield blades and already learn it |

- **Placeholder animation:** the source move's animation, recolored (red for FORCE CHOKE, blue bolt for BLASTER SHOT).
- **No new TMs or tutors**, so there are no changes to the learnset count or the power curve.

## Sandstorm encounter table (`net:weather-sandstorm-spawns`)

- **Map:** Route 111, the desert part of the Dune Sea.
- **How it works:** a daily roll stored in `var:unused-0x408b` (reset by the existing daily-event timer) picks "storm" or "calm" for the day. On storm days the desert uses an alternate land table.
- **Balance:** the alternate table copies Route 111's slot levels (desert land 19-22) and rates. It reorders which species fill the slots, using only species already in Route 111's table (sandshrew line, trapinch line, cacnea line, baltoy). Catch availability and levels are therefore the same on both tables.
- **Placeholder:** Emerald's existing sandstorm weather effect. No new art is needed.

## Habitat swaps (`net:habitat-swaps`)

Owner decision (2026-11-03): `home_planet` is the placement rule. A species is wild on its home planet; Emerald's
slots, rates and levels never move, only the species in a slot. `mapping/habitat_swaps.csv` lists every swap
(planet, from, to, optional maps and methods, reason); `tools/encounters.py` applies them after the Dune Sea
swaps and writes `database/encounters.csv`, the table the game will get (every map, method, slot, rate, levels,
Emerald species, Star Wars species, source, stat change). `tools/habitats.py` then explains what is left off
its home world in `database/species_habitats.csv` (HOME, MIGRANT, WIDESPREAD, SEA, RESERVE, FACILITY, STORY,
EVENT). Rules:

- A swap keeps the slot's stat total within 150 of Emerald's (the tool warns past that), so a route is never
  much harder or easier than it was.
- Each ocean world has its own water life: Kamino's steeds and lanterns, Dagobah's bog fish and crocodiles,
  Hoth's seals, Bespin's cloud drifters. The WIDE set (COLOFRY, DIANOGLET, AIWHALET, SHYYYO) stays on the open
  routes between worlds (Kashyyyk's archipelago, Yavin 4, Jedha's holy waters, Endor's rivers, Ilum's harbour).
- The Felucia Reserve keeps beasts from many worlds by design (RESERVE); seven of its slots went to Felucia
  natives so the reserve shows its own life too.
- The Altering Cave's Mystery Event table is EVENT: never placed, never swapped.
- Nine free slots hold new species (below), each placed in one foreign slot on its home planet.
- New areas get their own tables in `mapping/wild_extra.csv` (the Hoth tundra: tauntauns, seals, scrabblers, a
  rare wampa; the frozen lake by SURF and rod).

## New species in the free slots (`net:species-*`)

Owner decision (2026-11-03): up to 21 species in `SPECIES_OLD_UNOWN_B` to `_Z` (minus `_J`); three hold the
light/dark forms. Nine more are canon creatures the game was missing, each on its home planet in one slot a
foreign species held. Stats, types and the Emerald species whose abilities, learnset, EXP yield, catch rate and
egg data each copies are in its `net:species-*` row; none evolves. Datapad text is in `mapping/datapad.csv`,
the cry brief in `mapping/audio.csv`.

| Slot | Species | Planet | Types | Total | Copies | Where |
|---|---|---|---|---|---|---|
| E | WYYYSCHOKK | Kashyyyk | Bug / Dark | 410 | ARIADOS | Shadowlands B1F-B2F, the rare slots |
| F | KNOBSPIDER | Dagobah | Bug / Grass | 380 | SPINARAK | Cave of Evil 1F |
| G | SLEEN | Dagobah | Water / Ground | 395 | QUAGSIRE | every Dagobah water route, the common surf slot |
| H | JUBBABIRD | Dagobah | Flying / Psychic | 420 | XATU | Cave of Evil entrance and 1F, MYNOCKMAW's slot |
| I | SLYYYG | Kashyyyk | Poison / Grass | 290 | GULPIN | the Shadowlands, the common slot |
| K | JAKRAB | Tatooine | Normal | 280 | SENTRET | Route 110 |
| L | BOARWOLF | Endor | Dark / Normal | 450 | MIGHTYENA | Route 120, the rare slot |
| M | PROFOGG | Tatooine | Normal / Ground | 270 | SANDSHREW | Route 116 |
| N | YUZZUM | Endor | Normal / Fighting | 430 | VIGOROTH | Route 118 |

Twelve slots (O to Z) stay free. In the game each needs the same work as the light/dark forms: species info,
graphics tables, a cry remap, a name, and the swapped encounter slot (`tools/encounters.py --install`, to be
written in step 6).

## Mos Eisley Cantina (`net:mos-eisley-cantina`)

Chalmun's Spaceport Cantina in MOS EISLEY (Slateport City). It is flavour only: no story flag, no new level band, and
the main story never needs it. It takes over the Slateport **Pokémon Fan Club** building (`map:slateport-city-pokemon-fan-club`),
so the door, warps and town map stay exactly where they are. The COMPANION FAN CLUB is not removed: its chairman now
holds court in the cantina's back booth, and every fan club script (condition check, scarves, SOOTHE BELL, SWAGGER tutor)
keeps working unchanged.

**Rows:** `net:mos-eisley-cantina` (this design), `net:walker-wuher`, `net:walker-bith`, `net:walker-aqualish`,
`net:walker-evazan`, `net:walker-ithorian`, `net:walker-protocol-droid`, `net:cantina-greedo-battle`,
`net:music-cantina-band`. The renamed map and the re-skinned regulars are `mapping/world_objects.csv` rows.

### Room

Same layout id (`LAYOUT_SLATEPORT_CITY_POKEMON_FAN_CLUB`), same 14x11 size, same door at (6,10)-(7,10). Only the
metatiles are re-arranged: the couch lounge becomes a round bar in the middle (counter ring x 5-8, y 3-6, floor inside),
a band stage in the top-left corner (x 1-4, y 1-2), and booths in the wall niches (back booth top-right, two booths on
the right wall, one on the left). Until the new tiles are drawn the port uses the fan club tileset
(`gTileset_PokemonFanClub`, now PENDING_ART with the cantina subject; reference art `art:tatooine:cantina-interior`).
The bar ring uses counter metatiles (`MB_COUNTER`), so WUHER is spoken to across the bar like a mart clerk.

The room holds 14 object events (the 9 from the fan club plus 5 new ones). The engine shows 16 at once including the
player, so that is the most it should hold; that is why the band is two Bith and not the whole Modal Nodes.

| # | Who | Graphics | Tile | Script |
|---|---|---|---|---|
| 1 | MOMAW NADON (was Man 1) | `net:walker-ithorian` (placeholder `OBJ_EVENT_GFX_GENTLEMAN`) | (12,6), right booth | `SlateportCity_PokemonFanClub_EventScript_Man` |
| 2 | Twi'lek dancer (was Twin) | `OBJ_EVENT_GFX_POKEFAN_F` (now a Twi'lek woman) | (3,5), dance floor | `..._EventScript_Twin` |
| 3 | HOLONET reporter | `OBJ_EVENT_GFX_REPORTER_F` | (12,3), back booth | `..._EventScript_Reporter` |
| 4 | Moisture farmer (was the SOOTHE BELL woman) | `OBJ_EVENT_GFX_WOMAN_1` | (1,7), left booth | `..._EventScript_SootheBellWoman` |
| 5 | Fan club chairman | `OBJ_EVENT_GFX_GENTLEMAN` | (11,2), back booth | `..._EventScript_Chairman` |
| 6 | SCURRIER (companion) | `OBJ_EVENT_GFX_ZIGZAGOON_2` | (3,9), by the door | `..._EventScript_Zigzagoon` |
| 7 | LOTHKIT (the chairman's companion) | `OBJ_EVENT_GFX_SKITTY` | (10,2), back booth | `..._EventScript_Skitty` |
| 8 | BLOOPHARE (Momaw's companion) | `OBJ_EVENT_GFX_AZUMARILL` | (11,6), right booth | `..._EventScript_Azumarill` |
| 9 | PONDA BABA (was the SWAGGER tutor) | `net:walker-aqualish` (placeholder `OBJ_EVENT_GFX_MAN_4`) | (9,4), bar stool | `..._EventScript_SwaggerTutor` |
| 10 | WUHER, bartender | `net:walker-wuher` (placeholder `OBJ_EVENT_GFX_MAN_4`) | (6,4), behind the bar | new `..._EventScript_Wuher` |
| 11 | FIGRIN D'AN, kloo horn | `net:walker-bith` (placeholder `OBJ_EVENT_GFX_PSYCHIC_M`) | (2,2), stage | new `..._EventScript_Figrin` |
| 12 | DOIKK NA'TS, fizzz | `net:walker-bith` | (3,2), stage | new `..._EventScript_Doikk` |
| 13 | DR. EVAZAN | `net:walker-evazan` (placeholder `OBJ_EVENT_GFX_MAN_3`) | (9,5), bar stool | new `..._EventScript_Evazan` |
| 14 | GREEDO (optional battle) | `OBJ_EVENT_GFX_MANIAC` (now a Rodian) | (12,8), right booth | new `..._EventScript_Greedo` |

Outside, in MOS EISLEY (`map:slateport-city`), one more new object event: a **protocol droid** (`net:walker-protocol-droid`,
placeholder `OBJ_EVENT_GFX_DEVON_EMPLOYEE`) standing next to the cantina door (the door warp is at (4,26); (5,27) is
walkable and keeps the tile below the door free), with the script `SlateportCity_EventScript_CantinaDroid`. MOS EISLEY then has
36 object events, well under the 64-template limit.

### Wuher's drinks

WUHER runs a small shop with the standard `pokemart` command and Emerald's own prices, so nothing gets cheaper:

| From | Sells | Why it is safe |
|---|---|---|
| Always | JAWA JUICE (soda pop) 300 | The ROUTE 109 Seashore House next door already sells it at 300 at this point |
| After `flag:badge06-get` | adds BLUE MILK (fresh water) 200 and MEILOORUN (lemonade) 350 | CLOUD CITY's rooftop vending machines sell all three from badge 6 |

The bar's one rule: if the lead companion is a droid (the droid list from `net:droid-slicing`), WUHER says his
"we don't serve their kind" line and does not open the shop. Moving a non-droid to the front lets the player buy. The
port needs one small special (`IsLeadMonDroid`) or an inline species check; no flag.

### Greedo's battle (`net:cantina-greedo-battle`)

- **Slot:** `TRAINER_TERRY`, which Emerald defines but never places (not on any map, not in any script). Its data changes
  to class POKEMANIAC (GAME HUNTER), pic `TRAINER_PIC_POKEMANIAC` (the Rodian front pic), name `GREEDO`, intense
  encounter music, no items, `AI_SCRIPT_CHECK_BAD_MOVE`. No placed trainer changes.
- **Party:** KOWAKIAN (whismur) lv17 and NEXU (zangoose) lv18. MOS EISLEY is a badge-2 town; the routes beside it hold
  trainers of levels 12-27 (Route 109) and 6-20 (Route 110) in `database/area_progression.csv`, so he sits inside the
  band. Prize money is the normal GAME HUNTER class rate for lv18.
- **Trigger:** talk to him (sight range 0, so he never stops the player). One battle, `trainerbattle_single`, no rematch.
- **Why Greedo:** the player reaches MOS EISLEY on HAN's freighter (`net:hangar-tatooine-kashyyyk`), so Jabba's least
  frightening hunter takes the player for Han's crew. It is a cameo, not a plot thread: nothing else refers to it.

### Music (`net:music-cantina-band`)

A new short loop, `MUS_CANTINA_BAND`: an original upbeat swing tune for a small alien band (kloo horn, fizzz, clarinet-like
lead, brushed drums), in the spirit of the Modal Nodes but **not** the film's melody. Made with `tools/music-generator`.
Until it exists, the map plays `MUS_GAME_CORNER` (already being redone as `MUS_SABACC_DEN`, "smoky alien jazz band",
in `database/pending_audio.csv`), which fits better than `MUS_SLATEPORT`. Change `music` in the map's `map.json`.

### New lines

Emerald text format (`\n` new line, `\l` scroll, `\p` new box, `$` end). Species that don't speak Basic show a sound
and then the translation in brackets, like PONDA BABA's tutor lines. The re-skinned regulars' lines are already in
`mapping/texts/` (`act2_02_mos_eisley.csv`, `c3i_01_field_systems.csv`).

**WUHER** (`SlateportCity_PokemonFanClub_Text_WuherIntro`, then `pokemart`, then `..._Text_WuherBye`):

```
WUHER: What'll it be?\pAnd keep your companion off\nthe bar.$
```
```
WUHER: Drink up and move along.$
```

**WUHER, lead companion is a droid** (`..._Text_WuherNoDroids`):

```
WUHER: Hey! We don't serve their\nkind here!\pYour droids. They'll have to wait\noutside.\pPut it away, and then we'll talk.$
```

**WUHER, first time after badge 6** (`..._Text_WuherNewStock`, shown once before the shop; uses no flag if the port
prefers to show it every time after badge 6):

```
WUHER: BLUE MILK came in from the\nfarms. MEILOORUN, too.\pDon't ask where from.$
```

**FIGRIN D'AN** (`..._Text_Figrin`):

```
FIGRIN D'AN: (He keeps playing the\nkloo horn without missing a note.)\p…You want a request?\pWe know two songs. You've heard\nthis one.\pThe other one is JABBA's favourite.\nYou don't want to hear that one.$
```

**DOIKK NA'TS** (`..._Text_Doikk`):

```
DOIKK NA'TS: Fizzz-whee-dee!\pThat's my DORENIAN BESHNIQUEL.\nEveryone just calls it a fizzz.\pWe played right through the last\nblaster fight in here.\pNobody stopped dancing. That's\nMOS EISLEY for you.$
```

**DR. EVAZAN** (`..._Text_Evazan`):

```
DR. EVAZAN: He doesn't like you.\p…\pI don't like you either.\pYou just watch yourself. We're\nwanted men.\pI have the death sentence on\ntwelve systems.$
```

**GREEDO**, Huttese with the translation in brackets (`..._Text_GreedoIntro`, `..._Text_GreedoDefeat`,
`..._Text_GreedoPostBattle`):

```
GREEDO: Oota goota, kid?\p(Going somewhere?)\p(You came in on SOLO's freighter.\nJABBA wants his money.)\p(Maybe your companions can pay\nhis debt!)$
```
```
GREEDO: Koona t'chuta!\p(JABBA is going to hear about\nthis!)$
```
```
GREEDO: (Tell SOLO I'm waiting right\nhere in this booth.)\p(And next time, I shoot first.)$
```

**Protocol droid outside** (`SlateportCity_Text_CantinaDroid`):

```
PROTOCOL DROID: Oh, dear. They don't\nallow droids inside.\pI have been waiting out here for my\nmaster for three hours.\pI do hope everything is all right in\nthere. I could swear I heard\lblasterfire.$
```

**Port checklist:** re-arrange the layout's metatiles; change `music`; re-point objects 1, 2, 4 and 9 and move every object
to the tiles above; add objects 10-14 and their scripts; add the droid in MOS EISLEY; change `TRAINER_TERRY`'s data and
party; add the 11 new texts above. Placeholders keep every step playable before the new walkers are drawn.

## The main path and its fixes (owner, 2026-11-03: "run it autonomously")

The audit of 2026-11-03 found the main path is Emerald's and holds together, with three faults: the four-flight
backtrack from Jedha to Fortress Vader, Act 5 opening five planets at once with nothing new on them, and 14 new
playable areas with sprites but no gate, band, trainers or rewards. `mapping/planets.csv` records each planet's
role, act and arrival (`database/planets.csv` adds its bands); `mapping/area_progression_extra.csv` gives every new
area a gate, badge count, story chapter and level band, merged into `database/area_progression.csv`; and each new
area's yaml names its `net:` row in `todo`, so `python3 -m blockout guide` checks it. The fixes, one row each:

| Row | Planet | Gate | Levels | What it adds |
|---|---|---|---|---|
| `net:hyperlane-jedha-mustafar` | Jedha, Mustafar | `event:mt-pyre-orbs` (6 badges) | none | The Imperial shuttle from the Jedha pad to Mustafar Peak |
| `net:bens-hut` | Tatooine | open | 7-9 | Obi-Wan in Act 1: the Force, the Cave of Evil, Ilum |
| `net:maul-duel` | Tatooine | `flag:sys-game-clear` | 60-65 | Maul in person, one boss battle, after the Hall of Fame |
| `net:podrace-sebulba` | Tatooine | `flag:badge03-get` | 22-24 | Sebulba, SWOOP RACER boss at the grandstand |
| `net:jabbas-palace` | Tatooine | `item:go-goggles` (4 badges) | 19-23 | Jabba's court, the rancor pit, Bib Fortuna's errand |
| `net:rwookrrorro` | Kashyyyk | `item:hm-surf` (5 badges) | 25-27 | Wookiee village, Chewbacca at home, a TM and a trade |
| `net:mustafar-mining-facility` | Mustafar | `flag:badge03-get` | 20-22 | Veers's drills, a SITH SHARD, the duel record |
| `net:endor-battlefield` | Endor | `item:devon-scope` (6 badges) | 28-30 | Scout-walker wrecks, a Rebel commando, a MAX ELIXIR |
| `net:tibanna-refinery` | Bespin | `flag:badge06-get` | 32-34 | Lobot's side job against Cartel smugglers |
| `net:nijedha` | Jedha | `item:hm-surf` (6 badges) | 31-33 | The holy city: Chirrut, Baze, the kyber trader |
| `net:hoth-survey` | Hoth | `flag:badge06-get` | 32-35 | Rieekan, Derlin, the lost scout, NEVER-MELT ICE |
| `net:kamino-cloning-hall` | Kamino | `flag:badge06-get` | 33-35 | Cody, the clone cadets, PROTOCLONE's lab |
| `net:jar-jar-traveller` | six stops | none | none | Jar Jar one planet ahead of the player, a BIG PEARL at the end |

Every band is read from `database/area_progression.csv` for the area the new one hangs off, and sits inside it with
the five levels of slack the guide allows. No reward carries new power: TMs the game already has, held items the
game already sells, and the two evolution items already stocked in Pirin.

### Imperial shuttle, Jedha to Mustafar (`net:hyperlane-jedha-mustafar`)

- **Where:** the Jedha hangar (`jedha-hangar`) to the Mustafar Peak shuttle station. Row `hl-jedha-mustafar` in
  `mapping/hyperlanes.csv`, unlock `event:mt-pyre-orbs`.
- **Story:** Vader's troops take the BLUE KYBER at the temple summit and leave by walker; their shuttle stays on the
  pad with one pilot. The Guardians' IMPERIAL CODE gets the player aboard. It lands at the Mustafar Peak station,
  three screens from the Fortress Vader door, the way Emerald's Jagged Pass sits under Mt. Chimney.
- **Balance:** none. The gate is Emerald's (six badges, the Mt. Pyre scene). The player lands with the team they
  would have walked in with.
- **Placeholder:** the cable-car station interior and its script.

### Ben's Hut and the Maul duel (`net:bens-hut`, `net:maul-duel`)

- **Where:** `bens-hut` and `bens-hut-interior`, a side path east of the Jundland Wastes. Open from Act 1.
- **Act 1:** old Ben sits on the porch. He names the Force, says the Cave of Evil on Dagobah and the temple on
  Ilum are tests not places, and sends the player on. Sets `flag:unused-0x026`; the Dagobah scene (Emerald's
  Wallace at the Cave of Origin) and the Ilum entrance quote his line back. One Tusken scout watches from the
  rocks (RAIDER class, levels 7-9: Jundland Wastes is 3-9).
- **Post-game:** with `flag:sys-game-clear` Darth Maul stands on the path to the hut (canon: Rebels, Twin Suns,
  2 BBY: Maul finds Kenobi on Tatooine). He takes the player for Kenobi's apprentice and fights: SITH LORD class,
  five companions, levels 60-65, dark-side species. One battle; winning sets `flag:unused-0x027`, Ben steps out,
  Maul leaves, and Ben hands over Maul's SITH SHARD. Maul is a person and never catchable. Losing has no cost;
  he waits.
- **Placeholders:** Lanette's house for the hut; Sidney's trainer pic and party (re-leveled) for Maul.

### Sebulba's challenge (`net:podrace-sebulba`)

- **Where:** `mos-espa-podrace-arena`, the grandstand over Route 110's course (Emerald's Cycling Road). Open with
  Mos Espa; Sebulba appears after the Mos Espa badge (`flag:badge03-get`).
- **Battle:** Sebulba (SWOOP RACER, the Triathlete class renamed), four companions, levels 22-24, fast ground and
  flying types. Mos Espa's arena band is 17-24. One battle; winning sets `flag:unused-0x028` and gives a SCOPE LENS.
  Prize money uses the Triathlete scale.
- **Why:** the Boonta Eve course is already the Cycling Road; the race itself needs no new system, only its champion
  standing in the pit lane.
- **Placeholder:** a Cycling Road triathlete's pic and party.

### Jabba's Palace (`net:jabbas-palace`)

- **Where:** `jabbas-palace`, `jabbas-palace-throne-room`, `jabbas-palace-barge-dock`, east of Route 111's desert.
  The desert needs the GO-GOGGLES (four badges), so does the palace.
- **People:** two gate guards and two thugs (CARTEL THUG, 19-23), two Gamorrean guards in the throne room
  (WOOKIEE class renamed per trainer: GAMORREAN, 21-23), one skiff rider at the dock (20-22), Jabba on the dais
  (lines only: he is beaten at the Hutt Hideout), Bib Fortuna, Salacious Crumb, a Jawa droid seller, a bounty hunter
  waiting for work (Boba is not here: he is on Endor by then).
- **Side jobs:** the trapdoor drops the player into the rancor pit: a fixed battle with a level 23 RANCOR that
  cannot be caught (the pod is refused, as with the Emerald sealed-chamber statues); win and the keeper's chest
  holds a KING'S ROCK (`flag:unused-0x029`). Bib Fortuna wants the Jawa's droid (a MOUSEDROID the Jawa sells for
  500 credits); deliver it for a RARE CANDY (`flag:unused-0x02a`).
- **Placeholders:** Aqua Hideout tiles and the grunt sprites.

### Rwookrrorro (`net:rwookrrorro`)

- **Where:** `rwookrrorro` and three huts above Route 107 (a ladder up a wroshyr trunk). Route 107 is reached by
  skimming from Kachirho with SURF, so five badges; its band is 24-27.
- **People:** two Wookiee hunters (WOOKIEE, 25-27), the elder, a cub, the chieftain, the bowcaster maker.
  Chewbacca stands in the chieftain's hut whenever Han is not flying the player (he has a line about Han).
- **Rewards:** the chieftain gives TM31 BRICK BREAK once (`flag:unused-0x02b`). The bowcaster maker trades his
  WROSEED for any TATOOINE companion (an in-game trade, the fourth; `flag:unused-0x02c`).
- **Placeholders:** Fortree's treehouse tiles; Black Belt sprites.

### Mining Facility (`net:mustafar-mining-facility`)

- **Where:** `mustafar-mining-facility` and `mustafar-mining-control`, south of Ashen Pass (Act 3, three badges,
  band 19-22).
- **People:** two stormtroopers on the catwalks and one officer in the control center (20-22). Veers drills them:
  an NPC here with two lines (he is fought on Mustafar Peak and in Fortress Vader, as Emerald's Tabitha).
- **Rewards:** an item ball with a SITH SHARD (`flag:unused-0x02d`) in the control center, next to a holo-table
  that replays a few seconds of the duel on the lava river with no names. The Ilum trial of ANAKIN quotes it.
- **Placeholder:** New Mauville tiles.

### Endor clearing (`net:endor-battlefield`)

- **Where:** `endor-battlefield` and its bunker, east of Route 120 (six badges, Devon Scope, band 27-30).
- **Canon:** in 2 BBY the Battle of Endor is years away. The clearing is an Imperial survey site the Ewoks ended
  with log traps: two scout walkers down, a bunker left behind. The Empire chose this moon for its bunker later.
- **People:** two stormtrooper stragglers (28-30), one more in the bunker, Ewok scouts, and a Rebel commando who
  wants the bunker's scanner table. Beat the bunker straggler and the commando gives a MAX ELIXIR
  (`flag:unused-0x02e`).
- **Placeholders:** Route 120 tiles, Magma grunt sprites.

### Tibanna Refinery (`net:tibanna-refinery`)

- **Where:** `tibanna-refinery`, its interior and annex, over Cloud City's north skybridge (six badges, band 31-34).
- **People:** Lobot at the bridge (he opens it and asks for help), the Ugnaught foreman, two Cartel thugs outside
  (32-34) and one inside at the siphon. Clearing the three sets `flag:unused-0x02f`; Lobot gives a SMOKE BALL.
  The carbon-freezing annex is dressing: a line about the city's new freezing rig.
- **Placeholder:** New Mauville interior tiles.

### NiJedha (`net:nijedha`)

- **Where:** `nijedha` and five interiors, west gate from Route 122 (six badges, Jedha's band 31-33).
- **People:** Chirrut Imwe and Baze Malbus in the Temple of the Kyber (the Guardians of the Whills, canon Rogue
  One, alive here in 2 BBY), a pilgrim, a stormtrooper patrol (31-33), the kyber trader, the hostel keeper.
- **Rewards:** Chirrut gives a TWISTEDSPOON (`flag:unused-0x030`) after the temple summit scene. The kyber trader's
  stall is a second shop for KYBER CRYSTAL and SITH SHARD, at Pirin's price.
- **Placeholder:** Verdanturf's town tiles.

### Hoth survey (`net:hoth-survey`)

- **Where:** `hoth-tundra`, the survey outpost, the tauntaun shelter; the Wampa Cave (Shoal Cave) beyond. Survey
  shuttle from Yavin 4 at six badges.
- **People:** General Rieekan in the outpost, Major Derlin on the tundra with three Rebel scouts (PATHFINDER class,
  32-35), a tauntaun handler, a technician, and a lost scout at the cave mouth.
- **Quest:** Derlin says a scout is missing. The scout stands at the Wampa Cave mouth (`flag:unused-0x031`) and
  gives a NEVER-MELT ICE; Rieekan then gives TM07 HAIL (`flag:unused-0x032`). Canon: Echo Base is built later;
  this survey picks the site.
- **Placeholders:** Shoal Cave tiles, Ranger sprites.

### Tipoca City cloning hall (`net:kamino-cloning-hall`)

- **Where:** `tipoca-city-cloning-hall`, the great hall of Tipoca City (six badges, Kamino's band 32-34).
- **People:** Commander Cody, aged, keeping two clone cadets in training (CADET class, 33-35); a Kaminoan
  scientist by the sealed lab. Canon: the Empire ended Kamino's cloning (The Bad Batch); Cody's whereabouts in
  2 BBY are open, so he is here (`canon_note`).
- **Rewards:** beat the cadets and Cody gives a FOCUS BAND (`flag:unused-0x033`). The scientist tells PROTOCLONE's
  story (Mewtwo's slot, unobtainable in Emerald; still unobtainable here).
- **Placeholder:** the Launch Tower 2F lab tiles.

### Jar Jar the traveller (`net:jar-jar-traveller`)

- **Stops:** Tosche Station (Act 1), Kachirho (Act 2), Pirin (Act 3), Bright Tree (Act 4), Cloud City (Act 5),
  Dagobah (Act 6). `var:unused-0x4091` is the next stop; each stop advances it so he is only ever in one place.
- **Lines:** always a story about the last planet, always one planet ahead of the player. At Dagobah he gives a
  BIG PEARL ("from Otoh Gunga") and goes home. He is an NPC, never a trainer, never a companion.
- **Canon:** after the Clone Wars Jar Jar lost his seat and became a street performer on Naboo (Aftermath: Empire's
  End); here he spends 2 BBY wandering the Outer Rim.
- **Placeholder:** a Gentleman sprite until `net:walker-jar-jar` is drawn (step 3).

## People (`mapping/people.csv`)

One row per person placed by hand in the world (step 3, 2026-11-03): every NPC, trainer, boss, story character,
vision and relic in a new area, every must-have character taking over an Emerald object event (`npc_id`), and
every new object on an Emerald map (`yaml_name` empty: still to be placed in the area's yaml). Columns: `area`
(the world yaml), `yaml_name` and `yaml_index` (which person in that yaml), `npc_id`, `kind` (`npc`, `trainer`,
`boss`, `story`, `wild`, `vision`, `relic`), `character`, `trainer_class`, `trainer_name` (10 characters at most),
`party` (`species:<id>@<level>|...`), `flag`, `lines` (the one line that defines them) and `notes`.
`tools/build.py` checks every id, that the person exists in the yaml, and that the party sits in the band of the
area's map (`database/area_progression.csv`, five levels of slack; post-game up to 70), and writes
`database/people.csv` with the planet, map id, band and the check. Trainer classes are Emerald's (STORMTROOPER,
OFFICER, CARTEL THUG, WOOKIEE, PATHFINDER, CADET, VETERAN, SWOOP RACER, SITH LORD, SKIFF RIDER) plus
RAIDER (`net:trainer-class-raider`). Placeholders: each `net:character-*` row names the Emerald trainer or
object event whose pic, sprite and party it starts from.
