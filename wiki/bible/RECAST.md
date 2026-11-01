# Trainer recast (2026-11-01)

Many generic trainer classes were still Pokémon jobs with new names (Hiker, Bug Catcher, Breeder, Pokéfan…). Every class now reads as someone you could meet in a Star Wars film: a species, a droid or a job from the lore, picked to fit the planets where the class actually stands. Famous minor characters from the lore (starwars-db) became trainer names where the class pic matches them; the big names stay with the story cast (`bible/STORY.md` §5).

Rules kept: no trainer changes class, party or prize money (HOTSWAP). Only names, pictures, walkers and lines change. Classes whose identity already fit kept their art: VETERAN (cooltrainer), FORCE ADEPT, NIGHTSISTER, PATHFINDER, SPACER, FARMHAND, HOMESTEADER, ARISTOCRAT, SOCIALITE, YOUNG NOBLE, DIPLOMAT, LAVA MINER, AVIAN KEEPER, EXPERT, and every story class (Empire, Cartel, leaders, Trials, rivals, Grand Arena).

## Classes

| Emerald class | Was | Now | Who they are | New front pics |
|---|---|---|---|---|
| hiker | PROSPECTOR | **UGNAUGHT** | Ugnaught miners and haulers who work the canyons, caves and lava mines. | `hiker` |
| pkmn-breeder | BREEDER | **HANDLER** | Creature handlers who raise and drill companions, like Jabba's rancor keeper Malakili. | `pokemon_breeder_m`, `pokemon_breeder_f` |
| pokefan | BEASTFAN | **RACE FAN** | Podrace fans in team colours who dote on their companions like prize racers. | `pokefan_m`, `pokefan_f` |
| pokemaniac | BEASTMANIAC | **GAME HUNTER** | Rodian game hunters obsessed with rare companions. Greedo is one (Mos Eisley Cantina). | `pokemaniac` |
| bug-catcher | (Emerald name kept) | **JAWA** | Hooded Jawa scavengers who trade in scrap, droids and small critters. | `bug_catcher` |
| bug-maniac | (Emerald name kept) | **SHAMAN** | Ewok shamans with bone charms and swarms of forest bugs, like Logray. | `bug_maniac` |
| ninja-boy | INFILTRATOR | **EWOK** | Ewok scouts who ambush from the tall grass with spears and slings. | `ninja_boy` |
| youngster | (Emerald name kept) | **SCRAP KID** | Tatooine junkyard kids with goggles and hydrospanners who build their own droids and racers. | `youngster` |
| lass | (Emerald name kept) | **HANDMAIDEN** | Naboo handmaidens and court girls travelling with noble retinues. | none (art fits) |
| tuber-f | PADDLER | **WOOKIEE CUB** | Wookiee cubs who splash around the Kachirho lagoon on carved floats. | `tuber_f` |
| tuber-m | PADDLER | **WOOKIEE CUB** | Wookiee cubs who splash around the Kachirho lagoon on carved floats. | `tuber_m` |
| swimmer-m | (Emerald name kept) | **MON CAL** | Mon Calamari divers, at home in any sea. | `swimmer_m` |
| swimmer-f | (Emerald name kept) | **NAUTOLAN** | Nautolan divers with head-tails, fast in open water. | `swimmer_f` |
| sis-and-bro | (Emerald name kept) | **NAUTOLANS** | A Nautolan sister and brother who swim and battle together. | `sis_and_bro` |
| twins | (Emerald name kept) | **TWINS** | Twi'lek twin girls who battle as a pair. | `twins` |
| sr-and-jr | (Emerald name kept) | **PILOT&DROID** | A young pilot and her astromech droid, battling as a pair. | `sr_and_jr` |
| young-couple | (Emerald name kept) | **YOUNG COUPLE** | A young spacer couple: a human smuggler and his Zabrak pilot partner. | `young_couple` |
| old-couple | (Emerald name kept) | **OLD COUPLE** | An old Sullustan couple in miner's coats. | `old_couple` |
| triathlete | SWOOP RACER | **SWOOP RACER** | Swoop racers: on hovering swoop bikes, on foot in racing leathers, and crossing water with an aquata breather. | `cycling_triathlete_m`, `cycling_triathlete_f`, `running_triathlete_m`, `running_triathlete_f`, `swimming_triathlete_m`, `swimming_triathlete_f` |
| black-belt | BRAWLER | **WOOKIEE** | Wookiee warriors with bandoliers who test their strength in Tarfful's arena and beyond. | `black_belt` |
| battle-girl | WARRIOR | **MANDALORIAN** | Mandalorian warrior women in painted armour, Clan Wren's sparring partners for Sabine. | `battle_girl` |
| dragon-tamer | BEAST TAMER | **NIGHTBROTHER** | Dathomirian Zabrak Nightbrothers who tame great beasts. | `dragon_tamer` |
| fisherman | ANGLER | **ANGLER** | Quarren anglers with long poles and creels. | `fisherman` |
| aroma-lady | HERBALIST | **HERBALIST** | Ithorian herbalists who tend glowing flowers. | `aroma_lady` |
| parasol-lady | (Emerald name kept) | **MIRIALAN** | Mirialan ladies with geometric face tattoos, strolling under lace sunshades. | `parasol_lady` |
| collector | (Emerald name kept) | **JUNK DEALER** | Toydarian junk dealers hovering over crates of curios: Watto's rivals. | `collector` |
| ruin-maniac | RELIC HUNTER | **RELIC HUNTER** | Duros relic hunters in long coats with glow-lamps. | `ruin_maniac` |
| interviewer | HOLOREPORTER | **ANNOUNCER** | FODE AND BEED, the two-headed Troig podrace announcer, now a HoloNet interviewer. | `interviewer` |
| guitarist | MUSICIAN | **MUSICIAN** | Bith musicians with kloo horns, cousins of the Modal Nodes. | `guitarist` |
| school-kid | CADET | **CADET** | Imperial Academy cadets with datapads. | `school_kid_f` |

Species that don't speak Basic (Wookiees, Wookiee cubs, Ewoks, Jawas) have their lines shown as translations after a sound, the way KOTOR subtitles Shyriiwook.

## Lines

184 trainer lines in `mapping/texts/` were rewritten to match the new identities (their notes say `trainer recast 2026-11-01`):

- **WOOKIEE, WOOKIEE CUB, EWOK, SHAMAN, JAWA:** a sound, then the translation in brackets ("Rrraaaugh!\p(Might is right! Come on!)", "Utinni!", "Yub nub!"). Ewoks and Jawas met away from their home worlds say why (a Jawa sandcrawler stripping crashed walkers on Endor, an Ewok scout far from the forest moon).
- **PILOT&DROID:** the second speaker in each pair is the astromech, so R3, R4, R5 and R7 beep and are translated (R5's motivator blows when it loses). **FODE&BEED:** Beed speaks Huttese, as at the Boonta Eve.
- **SWOOP RACER:** the triathlon is a three-leg SWOOP RALLY (swim, swoop, run). **UGNAUGHT:** digging and hauling ore instead of hiking. **RACE FAN:** podrace talk. **GAME HUNTER:** hunting talk. **MANDALORIAN:** beskar and "This is the Way". **NIGHTBROTHER**, **ANGLER**, **MUSICIAN** (kloo horn), **JUNK DEALER** (Toydarian haggling): the lines that still named the old job.
- **Cameos:** Porkins, Red Leader Dreis and Dutch in Doran's arena, Malakili's beast that is "no rancor yet", Logray, Teebo and Paploo on Endor, Clegg Holdfast on the podrace course, Lor San Tekka at the Jedha temple, Sio Bibble on the starliner and Sabe.
- Names left over from Emerald in pair lines (AMY, LIV, PAUL, ROY) now use the new names.

## Art to-dos

- **36 trainer front pics** are PENDING_ART again, with new subjects in `mapping/art_subjects_src/trainer_pics.txt` and new briefs in `tools/sprite-trainer-generator/civitai/jobs.json` (the old per-pic cleanup overrides were dropped). Their wiki art and art_ready rows are deleted. The old pics are still in `game/` until new ones ship, so their `game_status` is back to NOT_STARTED. `python3 batch.py --list` shows them (about 108 Buzz for one take each).
- **15 walkers** now show someone else, so their drawn art was deleted from `wiki/art`, their art_ready rows removed, and they are PENDING_ART for a redraw. Their old recipes moved to `tools/sprite-walker-generator/art/retired/` and their built outputs were deleted.

| Walker | New subject | Who uses it |
|---|---|---|
| `hiker` | Ugnaught miner: pig snout, white whiskers, blue overalls, hard hat with a lamp | UGNAUGHT, RELIC HUNTER, townsfolk |
| `pokefan_m` | Stout podrace fan in a striped team vest, goggles on his head | RACE FAN, townsfolk |
| `pokefan_f` | Twi'lek woman (two head-tails) in a racing-team scarf | RACE FAN, townsfolk |
| `maniac` | Rodian (green skin, big black eyes, snout) in a hunter's vest | GAME HUNTER, SHAMAN (until re-pointed), JUNK DEALER, Greedo, townsfolk |
| `bug_catcher` | Jawa: small brown hooded robe, glowing yellow eyes, bandolier | JAWA |
| `ninja_boy` | Small kid in a hooded desert poncho | kids in houses (EWOK trainers move to the Ewok walker) |
| `youngster` | Scrap kid with goggles, patched tunic and a hydrospanner | SCRAP KID, townsfolk |
| `tuber_f` | Wookiee cub (f) with bead braids and a carved float | WOOKIEE CUB |
| `tuber_m` | Wookiee cub (m) with a carved log float | WOOKIEE CUB |
| `tuber_m_swimming` | Wookiee cub (m) paddling on a carved log float | WOOKIEE CUB |
| `swimmer_m` | Mon Calamari diver swimming (fish head, big side eyes) | MON CAL, swimming SWOOP RACERs |
| `swimmer_f` | Nautolan diver (f) swimming, head-tails trailing | NAUTOLAN, NAUTOLANS pair, swimming SWOOP RACERs |
| `twin` | Twi'lek kid with short head-tails in a simple tunic | TWINS, Twi'lek kids in towns |
| `black_belt` | Wookiee warrior with a bandolier | WOOKIEE, Grand Arena staff |
| `fisherman` | Quarren angler: face tentacles, slicker coat, long pole | ANGLER |

Shared generic walkers (man_5, woman_2, girl_3, man_3, woman_5, lass…) were left alone, so a few classes still walk as a generic person until the port re-points them (listed in `mapping/net_new.csv`, `net:walker-*`).

## Mos Eisley Cantina

The Slateport fan club building is now the **Mos Eisley Cantina** (`map:slateport-city-pokemon-fan-club`, design and every line in `bible/NET_NEW_DESIGNS.md`, row `net:mos-eisley-cantina`). It is flavour only: WUHER and his drinks (no droids!), FIGRIN D'AN and DOIKK NA'TS on the band stage, PONDA BABA (the SWAGGER tutor) and DR. EVAZAN at the bar, MOMAW NADON, a Twi'lek dancer, and an optional battle with GREEDO (the unused `TRAINER_TERRY` slot). The COMPANION FAN CLUB still meets in the back booth, so every fan club script keeps working. New walkers, all PENDING_ART with placeholders: `net:walker-wuher`, `net:walker-bith`, `net:walker-aqualish`, `net:walker-evazan`, `net:walker-ithorian`, `net:walker-protocol-droid` (outside the door), plus `net:walker-ewok` for the EWOK and SHAMAN trainers. The room's tileset (now with a cantina subject) and the music (`net:music-cantina-band`) are to-dos too.

## Lore cameos (trainer names)

Each name matches its class pic: humans in human classes, Ewoks as Ewoks, a Wookiee cub as a Wookiee cub.

| Trainer (Emerald) | Class | New name | Who |
|---|---|---|---|
| Randall (`randall`) | VETERAN | **PORKINS** | Jek Porkins, Rebel pilot, flying for Doran before Yavin |
| Parker (`parker`) | VETERAN | **DREIS** | Garven Dreis, Red Leader at Yavin |
| George (`george`) | VETERAN | **DUTCH** | Jon 'Dutch' Vander, Gold Leader at Yavin |
| Berke (`berke`) | VETERAN | **TIREE** | Dex Tiree, Gold Two at Yavin |
| Isaac (`isaac-1 + rematches`) | HANDLER | **MALAKILI** | Malakili, Jabba's rancor keeper |
| Yasu (`yasu`) | EWOK | **TEEBO** | Teebo, Ewok warrior |
| Takashi (`takashi`) | EWOK | **PAPLOO** | Paploo, the Ewok who stole a speeder bike |
| Jeffrey (`jeffrey-1 + rematches`) | SHAMAN | **LOGRAY** | Logray, Ewok shaman |
| Jacob (`jacob`) | SWOOP RACER | **CLEGG** | Clegg Holdfast, Boonta Eve racer and journalist |
| Ricky (`ricky-1 + rematches`) | WOOKIEE CUB | **LUMPY** | Lumpawarrump, Chewbacca's son |
| Haley (`haley-1 + rematches`) | HANDMAIDEN | **SABE** | Sabe, Padme's handmaiden and decoy |
| William (`william`) | FORCE ADEPT | **SAN TEKKA** | Lor San Tekka, Church of the Force pilgrim (Jedha) |
| Leah (`leah`) | NIGHTSISTER | **MERRIN** | Merrin, Nightsister of Dathomir |
| Thomas (`thomas`) | DIPLOMAT | **SIO BIBBLE** | Sio Bibble, Governor of Naboo, on the starliner |
| Calvin (`calvin-1 + rematches`) | SCRAP KID | **DEAK** | Deak, Luke's friend from Tosche Station |
| Allen (`allen`) | SCRAP KID | **WINDY** | Windy, Luke's friend from Tosche Station |
| Cristian (`cristian`) | WOOKIEE | **KITWARR** | Kitwarr, son of the Wookiee chieftain Wullffwarro (Rebels) |

Pairs: GABBY & TY are **FODE&BEED** (their lines now speak as FODE: and BEED:). The PILOT&DROID pairs are KESS & R5, AINA & R3, KAI & R4 and TARA & R7.

