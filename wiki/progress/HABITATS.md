# Habitats (E2)

Encounter tables are unchanged from Emerald, so balance is identical. This report checks each wild companion's
home planet against the planets where it can be caught, and explains every one that lives off its home world.
Source: `tools/habitats.py`, hand notes in `mapping/habitat_notes.csv`, output `database/species_habitats.csv`.

| decision | species |
|---|---|
| FACILITY | 15 |
| HOME | 45 |
| MIGRANT | 38 |
| RESERVE | 32 |
| SEA | 5 |
| STORY | 1 |
| WIDESPREAD | 7 |

## Off-world companions

| companion | home | found on | decision | why |
|---|---|---|---|---|
| WARMASSIFF | TATOOINE | ENDOR | MIGRANT | Imperial patrols brought massiffs to Endor as guard beasts; the packs went wild. |
| SCURRYDASH | TATOOINE | ENDOR | MIGRANT | Scurriers stow away in cargo and turn up on any world with scrap to dig through. |
| BOGLING | BOGANO | SULLUST, TATOOINE | MIGRANT | Traders carried boglings off Bogano; they thrive in oasis pools and hot-spring ponds. |
| BOGTROT | NABOO | SULLUST | MIGRANT | Traders carried boglings off Bogano; they thrive in oasis pools and hot-spring ponds. |
| LEAFTRICK | ENDOR | SULLUST | MIGRANT | A rare stray in Sullust's hills; seeds blow in on ash winds. |
| HAWKBATKIT | CORUSCANT | TATOOINE | MIGRANT | Hawk-bats roost in every busy spaceport; Mos Eisley's flocks spread across Tatooine. |
| HAWKBAT | CORUSCANT | TATOOINE | MIGRANT | Hawk-bats roost in every busy spaceport; Mos Eisley's flocks spread across Tatooine. |
| AURALET | DAGOBAH | TATOOINE | STORY | Force sprites drift from Dagobah toward Force-sensitive people; one waits for Luke on Route 102. |
| FELUSPORE | FELUCIA | TATOOINE | MIGRANT | Felucian spores ride starships and take root in the Jundland's shaded canyons. |
| SPOREFIST | FELUCIA | FACILITY | FACILITY | Only in Grand Arena facilities. |
| SLOTHLET | NAL HUTTA | TATOOINE | MIGRANT | Kept as pets by Hutt-world traders; a few escaped into the Jundland Wastes. |
| MISTKIN | DATHOMIR | KASHYYYK, TATOOINE | MIGRANT | Mist foxes vanish and reappear far away; they turn up in caves on many worlds. |
| HIVEGRUB | GEONOSIS | TATOOINE | MIGRANT | Hive grubs came to Tatooine in Geonosian ore shipments and dug in. |
| MOGU | KASHYYYK | ILUM | MIGRANT | Mogu wander into Ilum's caves to train; only the strongest reach them. |
| HORNFIN | NABOO | ENDOR, ILUM, RESERVE, SULLUST, TATOOINE | WIDESPREAD | Found across the galaxy. |
| KINGFIN | NABOO | RESERVE | RESERVE | The Felucia Reserve keeps beasts from many worlds. |
| COLOFRY | NABOO | BESPIN, DAGOBAH, ENDOR, HOTH, ILUM, JEDHA, KAMINO, KASHYYYK, RESERVE, SULLUST, TATOOINE, YAVIN 4 | WIDESPREAD | Found across the galaxy. |
| COLOCLAW | NABOO | DAGOBAH | MIGRANT | Colo claw fish grow huge in any deep water; one lurks under the Dagobah arena. |
| BLOOPRAT | NABOO | ENDOR, RESERVE, SULLUST, TATOOINE | WIDESPREAD | Found across the galaxy. |
| BOULDWART | TATOOINE | ILUM, MUSTAFAR | MIGRANT | Rock warts follow heat and minerals; they crowd the Empire's volcanic hideouts and Ilum's caves. |
| LOTHKIT | LOTHAL | TATOOINE | MIGRANT | Loth-cats travel as ship pets and sometimes go wild. |
| MYNOCK | SPACE | , DAGOBAH, FACILITY, HOTH, ILUM, KASHYYYK, SULLUST | WIDESPREAD | Found across the galaxy. |
| MYNOCKMAW | SPACE | , DAGOBAH, FACILITY, HOTH, ILUM, SULLUST | WIDESPREAD | Found across the galaxy. |
| DIANOGA | KAMINO | KASHYYYK | MIGRANT | Dianogas live wherever there is dark water; the old Republic wreck is full of them. |
| BUZZDROID | SPACE | ILUM | MIGRANT | Buzz droids left over from the Clone Wars still crawl through Ilum's caves. |
| OCTUPTARRA | KASHYYYK | ILUM | MIGRANT | Abandoned octuptarra droids guard Ilum's Crystal Caves. |
| B1 DROID | MUSTAFAR | SULLUST | MIGRANT | The Empire salvaged old B1 droids to work Sullust's mines. |
| KATHPUP | DANTOOINE | ENDOR, TATOOINE | MIGRANT | Kath hounds spread from Dantooine to open plains on many worlds. |
| KATHHOUND | DANTOOINE | ENDOR | MIGRANT | Kath hounds spread from Dantooine to open plains on many worlds. |
| KAADU | NABOO | RESERVE | RESERVE | The Felucia Reserve keeps beasts from many worlds. |
| KAADULORD | NABOO | RESERVE | RESERVE | The Felucia Reserve keeps beasts from many worlds. |
| OPEEFRY | NABOO | ENDOR | MIGRANT | Opee fry swarm in any warm river; Endor's are a released stock. |
| OPEEKILLER | NABOO | DAGOBAH, ENDOR, JEDHA, KAMINO, TATOOINE, YAVIN 4 | WIDESPREAD | Found across the galaxy. |
| AIWHA | KAMINO | DAGOBAH | MIGRANT | Aiwhas fly between water worlds and rest in Dagobah's seas. |
| LAVAGRUB | MUSTAFAR | SULLUST | MIGRANT | Lava grubs crawl out of any lava flow; Sullust's volcanoes are full of them. |
| MUCKLING | CORUSCANT | SULLUST | MIGRANT | Muck crawls out of mine runoff on Sullust as it does in Coruscant's lower levels. |
| BELDONLET | BESPIN | SULLUST | MIGRANT | Beldon calves drift down from Bespin's gas layers into volcanic vents. |
| VELKLET | BESPIN | SULLUST, TATOOINE | MIGRANT | Velker chicks ride high winds to warm worlds. |
| VELKER | BESPIN | FACILITY | FACILITY | Only in Grand Arena facilities. |
| KOUHUN | GEONOSIS | FACILITY, SULLUST | MIGRANT | Kouhuns are smuggled as assassins' tools and escape into the wild. |
| KYBERSUN | ILUM | SULLUST | MIGRANT | Living kyber crystals fell to Sullust as meteorites. |
| BOGWHISKR | DAGOBAH | ENDOR, ILUM, SULLUST, TATOOINE | WIDESPREAD | Found across the galaxy. |
| BOGTITAN | DAGOBAH | ILUM, SULLUST | MIGRANT | Bog titans live in any deep |
| CRABDROID | UTAPAU | TATOOINE | MIGRANT | Crab droids were dumped on Tatooine after the Clone Wars and still scuttle in its oases. |
| HOLOSHARD | JEDHA | TATOOINE | MIGRANT | Holocron shards lie scattered among Tatooine's desert ruins. |
| HOLOCRON | JEDHA | FACILITY | FACILITY | Only in Grand Arena facilities. |
| SHIMMERFIN | DAGOBAH | FACILITY | FACILITY | Only in Grand Arena facilities. |
| STARCORAL | KAMINO | BESPIN | MIGRANT | Star corals wash up on the shores of many worlds. |
| HOLLOWDOLL | JEDHA | FACILITY | FACILITY | Only in Grand Arena facilities. |
| SITHWRAITH | JEDHA | FACILITY | FACILITY | Only in Grand Arena facilities. |
| LOTHWOLF | LOTHAL | ENDOR | MIGRANT | The Loth-wolf appears wherever disaster is coming. |
| VULPTEX | CRAIT | JEDHA | MIGRANT | Vulptex fur is prized; escaped pets now live on Jedha's mountain. |
| IONRAT | FELUCIA | RESERVE | RESERVE | The Felucia Reserve keeps beasts from many worlds. |
| BOGDUCK | NABOO | RESERVE | RESERVE | The Felucia Reserve keeps beasts from many worlds. |
| BOGDRAKE | NABOO | RESERVE | RESERVE | The Felucia Reserve keeps beasts from many worlds. |
| YSALAKIT | MYRKR | DAGOBAH | MIGRANT | Ysalamiri hatchlings cling to driftwood and wash up on far islands. |
| YSALAMIRI | MYRKR | FACILITY, RESERVE | RESERVE | The Felucia Reserve keeps beasts from many worlds. |
| CONVORLET | LOTHAL | RESERVE | RESERVE | The Felucia Reserve keeps beasts from many worlds. |
| CONVOR | LOTHAL | RESERVE | RESERVE | The Felucia Reserve keeps beasts from many worlds. |
| FALUMPASET | NABOO | RESERVE | RESERVE | The Felucia Reserve keeps beasts from many worlds. |
| MUDHORNLET | ARVALA | RESERVE | RESERVE | The Felucia Reserve keeps beasts from many worlds. |
| KILLIK | ALDERAAN | RESERVE | RESERVE | The Felucia Reserve keeps beasts from many worlds. |
| HORNBEETLE | FELUCIA | RESERVE | RESERVE | The Felucia Reserve keeps beasts from many worlds. |
| RANCORPUP | DATHOMIR | RESERVE | RESERVE | The Felucia Reserve keeps beasts from many worlds. |
| PEARLCLAM | KAMINO | DAGOBAH, YAVIN 4 | SEA | Roams the open water between worlds. |
| RELICFISH | KAMINO | DAGOBAH, YAVIN 4 | SEA | Roams the open water between worlds. |
| CORALITH | KAMINO | DAGOBAH, ILUM | SEA | Roams the open water between worlds. |
| LUMIRAY | KAMINO | DAGOBAH, YAVIN 4 | SEA | Roams the open water between worlds. |
| HEARTFIN | KAMINO | DAGOBAH, ILUM | SEA | Roams the open water between worlds. |
| DACTHATCH | UTAPAU | SULLUST | MIGRANT | Dactillion hatchlings were brought to Sullust's caves by traders. |
| SPROUTLIZ | KASHYYYK | FACILITY | FACILITY | Only in Grand Arena facilities. |
| BUDLIZARD | KASHYYYK | FACILITY | FACILITY | Only in Grand Arena facilities. |
| BLOOMBEAST | KASHYYYK | FACILITY | FACILITY | Only in Grand Arena facilities. |
| EMBERLIZ | MUSTAFAR | FACILITY | FACILITY | Only in Grand Arena facilities. |
| MAGMANDER | MUSTAFAR | FACILITY | FACILITY | Only in Grand Arena facilities. |
| LAVADRAGON | MUSTAFAR | FACILITY | FACILITY | Only in Grand Arena facilities. |
| SHELLPUP | MON CALA | FACILITY | FACILITY | Only in Grand Arena facilities. |
| SHELLWARD | MON CALA | FACILITY | FACILITY | Only in Grand Arena facilities. |
| SHIFTBLOB | ZOLAN | TATOOINE | MIGRANT | A shapeshifter can be anything; a colony hides in Tatooine's desert underpass. |
| DUSKOWL | ENDOR | RESERVE | RESERVE | The Felucia Reserve keeps beasts from many worlds. |
| DOTBUG | NABOO | RESERVE | RESERVE | The Felucia Reserve keeps beasts from many worlds. |
| KRYKLING | LOTHAL | RESERVE | RESERVE | The Felucia Reserve keeps beasts from many worlds. |
| NERFLET | ALDERAAN | FACILITY, RESERVE | RESERVE | The Felucia Reserve keeps beasts from many worlds. |
| TAILMONK | FELUCIA | FACILITY, RESERVE | RESERVE | The Felucia Reserve keeps beasts from many worlds. |
| SUNSEED | TATOOINE | RESERVE | RESERVE | The Felucia Reserve keeps beasts from many worlds. |
| OGGDOLET | BOGANO | RESERVE | RESERVE | The Felucia Reserve keeps beasts from many worlds. |
| OGGDO | BOGANO | RESERVE | RESERVE | The Felucia Reserve keeps beasts from many worlds. |
| DEKALET | SPACE | FACILITY, RESERVE | RESERVE | The Felucia Reserve keeps beasts from many worlds. |
| SCORPWING | GEONOSIS | RESERVE | RESERVE | The Felucia Reserve keeps beasts from many worlds. |
| ANOOBLET | TATOOINE | RESERVE | RESERVE | The Felucia Reserve keeps beasts from many worlds. |
| SHELLSAP | FELUCIA | FACILITY, RESERVE | RESERVE | The Felucia Reserve keeps beasts from many worlds. |
| GORAXCUB | ENDOR | FACILITY, RESERVE | RESERVE | The Felucia Reserve keeps beasts from many worlds. |
| JETSQUID | KAMINO | RESERVE | RESERVE | The Felucia Reserve keeps beasts from many worlds. |
| OCTOCANNON | KAMINO | RESERVE | RESERVE | The Felucia Reserve keeps beasts from many worlds. |
| FYRNOCK | LOTHAL | FACILITY, RESERVE | RESERVE | The Felucia Reserve keeps beasts from many worlds. |
| IKOPI | NABOO | FACILITY, RESERVE | RESERVE | The Felucia Reserve keeps beasts from many worlds. |
| PAINTKIT | TATOOINE | FACILITY | FACILITY | Only in Grand Arena facilities. |
| SHAAK | NABOO | RESERVE | RESERVE | The Felucia Reserve keeps beasts from many worlds. |
