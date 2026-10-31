# Net-new designs (E3)

One section per `net:` row in `mapping/net_new.csv`. Each design lists the maps it touches, the story flags and vars it
needs, its level band (taken from `database/area_progression.csv`, so nothing sits outside the band of the act it is in),
and the placeholder assets Step 4 can use until Step 5 draws the real art.

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

Resolved in E2 with no slot swaps, so wild balance stays identical to Emerald. `progress/HABITATS.md` explains every companion that lives off its home world: it is either a migrant, part of the Felucia Reserve, widespread, a sea species, part of the story, or re-homed (the GNARLSPAWN line now lives on Endor).
