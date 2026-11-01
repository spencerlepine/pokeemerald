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

## Planet borders (`net:hangar-*`, `net:border-*`)

These rows only change how a crossing looks and reads. Collision, warps and level bands stay as they are in Emerald.

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

Resolved with no slot swaps, so wild balance stays identical to Emerald. `database/species_habitats.csv` (built by `tools/habitats.py`) explains every companion that lives off its home world: it is either a migrant, part of the Felucia Reserve, widespread, a sea species, part of the story, or re-homed (the GNARLSPAWN line now lives on Endor).

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
