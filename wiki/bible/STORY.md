# Story bible: Star Wars Emerald

This is the creative source of truth for the rewrite. Every row in
`mapping/*.csv` should agree with this file. When a decision here changes,
update this file first, then the mapping rows, then rebuild.

Status: **approved** by the owner on 2026-10-31.

---

## 1. Frame

| | |
|---|---|
| Era | **~2 BBY**, the early Rebellion. Order 66 was 17 years ago. The Empire is consolidating, the first Death Star is under construction, Rebel cells are forming, bounty hunters are thriving. |
| Region | **The OUTER RIM** (replaces HOENN). Hoenn's one continent becomes a cluster of planets (section 3). |
| Player | A young, quietly Force-sensitive kid whose family moves to **Tatooine**. The player collects and battles *companions* (beasts and droids; never people). Default names **KAEL** / **MIRA**. |
| Tone | Pokémon's warmth and route-by-route discovery, Star Wars names, places and conflicts. Kid-friendly: villains are defeated, not killed. |
| Canon policy | This is an **alternate telling** set in the film era. Film characters keep their personality and their 2 BBY situation. Prequel figures who are dead by 2 BBY appear only as **Force visions** (Ilum crystal caves), as **Order 66 survivors** (Kanan Jarrus, Obi-Wan), or in history, holocrons and dialogue. Each row says how it bends canon (`canon_note`). |

### Why ~2 BBY

It is the only window where all the "must have" characters can be met in
person: Vader is hunting, Boba Fett works for Jabba, Obi-Wan is a hermit
watching Luke, Yoda is hidden on Dagobah, Leia is a young senator running
errands for the Rebellion, Han and Chewie fly the Falcon, Lando is a gambler,
Watto still runs his junk shop, and the Ewoks have never met an Imperial.

### The Anakin question

A literal "fight Anakin on Mustafar, then Vader on the Death Star" does not
fit one timeline: Anakin became Vader 17 years before the game. The bible
resolves it the other way round, which also fits Emerald's structure:

1. You fight **Darth Vader** for real on **Mustafar** (Mt. Chimney), in
   **Fortress Vader** (Magma Hideout) and at the **Yavin 4 base** (Space
   Center tag battle, with Leia at your side).
2. At the end, in Ilum's crystal caves (Pokémon League), the Force shows you
   a **vision of Anakin Skywalker** as the fourth trial (Drake's slot), right
   before the last real battle against **Obi-Wan Kenobi**, his old master.

So the player meets the man before they meet the memory.

---

## 2. Vocabulary (global replacements)

Full list: `mapping/glossary.csv`. The important ones:

| Emerald | Star Wars Emerald | Why |
|---|---|---|
| POKéMON | COMPANION | Covers beasts and droids. Decided by the owner on 2026-10-31. |
| POKé BALL | CAPTURE POD | Ball tiers become material tiers: DURASTEEL POD, BESKAR POD, KYBER POD. |
| POKéDEX | DATAPAD | Companion entries are "databank" style. |
| POKéNAV | COMLINK | Map, match call and news on one comlink. |
| POKéMON CENTER | BACTA CENTER | Healed by a 2-1B medical droid. |
| POKé MART | SUPPLY DEPOT | |
| GYM / GYM LEADER | ARENA / ARENA LEADER | |
| BADGE | SHARD | The eight **kyber shards** together form the key to the hidden Ilum temple (the Victory Road gate). |
| ELITE FOUR | FOUR TRIALS | Force visions inside the crystal caves of Ilum. |
| POKéMON LEAGUE | ILUM TEMPLE | |
| TEAM MAGMA | THE EMPIRE | Grunts are Stormtroopers. |
| TEAM AQUA | THE CARTEL | Jabba's Hutt Cartel. Grunts are cartel thugs. |
| HOENN | OUTER RIM | |
| PSYCHIC / GHOST type | FORCE / SPIRIT type | Display names only. The type chart is untouched. |
| MACH BIKE / ACRO BIKE | SWOOP BIKE / SPEEDER BIKE | Both are hover-bikes. Brown = swoop (raw speed), white = speeder bike (agile, tricks). |
| CONTEST | SHOWCASE | Cloud City galas. |
| GAME CORNER | SABACC DEN | |
| SAFARI ZONE | FELUCIA RESERVE | Explains the off-world (national dex) companions. |

---

## 3. The planets (location clusters)

Hoenn is one continent. In the 1:1 phase every Emerald location keeps its
place on the map and is **relabelled** to a planet. Where two planets touch
by walking, the edge is listed in `mapping/net_new.csv` as a
**planet border**: Step 4 can later cut that connection and put a hangar and
ship ride there (the way Mr. Briney's boat already works).

| Planet | Emerald locations | Arena | Notes |
|---|---|---|---|
| **TATOOINE** | Littleroot → MOS PELGO, Oldale → TOSCHE STATION, Petalburg → MOS ENTHA, Rustboro → BESTINE, Verdanturf → ANCHORHEAD, Mauville → MOS ESPA, Slateport → MOS EISLEY; Petalburg Woods → JUNDLAND WASTES, Rusturf Tunnel → BEGGAR'S CANYON, Mirage Tower → SANDCRAWLER, Desert Underpass → KRAYT GRAVEYARD, Desert Ruins → TUSKEN RUINS, New Mauville → ESPA GENERATOR; Routes 101–104, 110, 111 (DUNE SEA), 112 (south), 115–117 | Bestine (Biggs Darklighter, Rock), Mos Espa (Watto, Electric), Mos Entha (Dad, Normal) | Starting planet. Route 110's Cycling Road is the Boonta Eve podrace course. |
| **KASHYYYK** | Dewford → KACHIRHO, Granite Cave → SHADOWLANDS, Abandoned Ship → REPUBLIC WRECK, Island Cave, Routes 105–109 (archipelago seas) | Kachirho (Tarfful, Fighting) | Han flies you here on the Falcon (Mr. Briney's boat). |
| **SULLUST** | Lavaridge → PIRIN, Fallarbor → INYUSU TOR, Fiery Path → MAGMA TUNNELS, Jagged Pass → ASHEN PASS, Meteor Falls → STARFALL CAVERN, Routes 112 (north)–114 | Pirin (Sabine Wren, Fire) | Volcanic, ash fields, hot springs. |
| **MUSTAFAR** | Mt. Chimney → MUSTAFAR PEAK, Magma Hideout → FORTRESS VADER | none | Reached by the cable car (a shuttle). Vader's domain. |
| **ENDOR** | Fortree → BRIGHT TREE, Weather Institute → ENDOR STATION, Scorched Slab, Ancient Tomb, Routes 118–121, 123 | Bright Tree (Chief Chirpa, Flying) | Treewalk biome: Fortree's treehouses and bridges are already in the game. |
| **FELUCIA** | Safari Zone → FELUCIA RESERVE | none | Off-world companion preserve. |
| **BESPIN** | Lilycove → CLOUD CITY, Aqua Hideout → HUTT HIDEOUT | none | Department store, Showcase hall, museum. The Cartel hides in the city's under-levels; Boba Fett guards it. |
| **JEDHA** | Mt. Pyre → JEDHA TEMPLE, Route 122 | none | Holy moon. The Guardians of the Whills keep the RED and BLUE KYBER (the orbs). |
| **YAVIN 4** | Mossdeep → YAVIN 4, Space Center → LAUNCH TOWER, Routes 124–125 | Massassi Temple (Kanan Jarrus & Ezra Bridger, Force) | Secret Rebel base. Leia lives here. |
| **HOTH** | Shoal Cave → WAMPA CAVE | none | Ice caves. |
| **DAGOBAH** | Sootopolis → DAGOBAH, Cave of Origin → CAVE OF EVIL, Seafloor Cavern → DROWNED CAVERN, Routes 126–130, underwater routes | Dagobah (Yoda, Water) | Entered by diving (Dive). The titans clash at the Cave of Evil, a Force vergence. |
| **KAMINO** | Pacifidlog → TIPOCA CITY, Sealed Chamber → SEALED VAULT, Routes 131–134 | none | Stilt city on an ocean world. |
| **ASTEROID FIELD** | Sky Pillar → ASTEROID SPIRE | none | Home of the EXOGORTH (Rayquaza). |
| **ILUM** | Ever Grande → ILUM, Victory Road → CRYSTAL CAVES, Pokémon League → ILUM TEMPLE | Four Trials + Obi-Wan | The kyber shards open the temple. |
| Post-game | Battle Frontier → GRAND ARENA (Lando), Southern Island → TYTHON ISLE, Faraway Island → WELLSPRING, Birth Island → ATOLLON, Navel Rock → MORTIS GATE | | |

---

## 4. Factions

| Emerald | Star Wars | Leader | Lieutenants | Grunts | Goal (rewritten) |
|---|---|---|---|---|---|
| Team Magma | **Galactic Empire** (Vader's task force) | **Darth Vader** (Maxie) | **General Veers** (Tabitha) | Stormtroopers (sandtroopers, snowtroopers by planet) | Awaken the land titan **GREATKRAYT** (Groudon) and bend its power to the Death Star project. |
| Team Aqua | **Hutt Cartel** | **Jabba the Hutt** (Archie) | **Boba Fett** (Matt), **Bossk** (Shelly) | Cartel thugs (Gamorrean, Weequay, Nikto) | Awaken the sea titan **SANDO** (Kyogre) and hold whole worlds' ports to ransom. |
| Devon Corp. | **House Organa** | **Senator Bail Organa** (Mr. Stone) | Organa engineers | | Alderaan's royal house; its engineers build the comlink, ORGANA SCOPE and ORGANA PARTS; quietly helps the Rebellion. |
| Pokémon League | **Ilum Temple** | **Obi-Wan Kenobi** (Champion) | the Four Trials | | The last test before the player is ready. |

Both villains are humbled at the end of Act 6 when the **EXOGORTH**
(Rayquaza) comes down from the asteroid field and calms the titans. For Vader
this is a flicker of Anakin, not a redemption. That comes later, outside the
game.

---

Motives: Jabba (Archie) wants to drown the dry worlds into swamps "fit for a HUTT" (SANDO, the sea titan).
Vader (Maxie) mirrors it with land: an Imperial plan to dry out worlds for industry and garrisons
(GREATKRAYT, the land titan).

## 5. Cast (main characters)

Full list with ids and trainer links: `mapping/characters.csv`.

| Emerald | Star Wars | Role |
|---|---|---|
| Player (Brendan / May) | **KAEL / MIRA** (original) | Force-sensitive kid, new to Tatooine. |
| Rival (May / Brendan) | **MIRA / KAEL** (original) | Prof. Korr's kid, friendly rival. |
| Mom | Mom (original) | |
| Norman (Dad, Normal arena) | **DORAN** (original) | Ex-Republic veteran who runs the Mos Entha arena. |
| Prof. Birch | **PROF. KORR** (original) | Xenobiologist on Tatooine. Gives the three starters. |
| Wally | **Luke Skywalker** | Farm boy who catches his first companion (an AURALET) with the player's help, and is the last rival in the crystal caves. |
| Wally's father / mother | **Owen Lars / Beru Lars** | Owen thanks the player with HM03. |
| Wally's uncle, Wanda, her boyfriend | Camie's father (original), **Camie**, **Fixer** | Anchorhead friends. Fixer is digging Beggar's Canyon by hand. |
| Steven Stone | **Leia Organa** | Young senator and Rebel courier. Met in the Shadowlands, tag-battles Vader with you, gives the astromech (Beldum line) after the Trials. |
| Mr. Stone | **Bail Organa** | Sends the player with a message for Leia. |
| Mr. Briney + Peeko | **Han Solo + Chewbacca** | Chewie is kidnapped by cartel thugs; rescue him and Han flies you between planets. |
| Capt. Stern | **Ric Olié** | Veteran pilot building a deep-diving bongo sub at Mos Eisley. |
| Scott | **Lando Calrissian** | Talent scout who keeps showing up and runs the Grand Arena. |
| Rydel | **Wald** | Rodian who runs the Mos Espa hover-bike shop. |
| Gabby & Ty | **Fode & Beed** | Two-headed HoloNet reporter. |
| Mt. Pyre elders | **Chirrut Îmwe & Baze Malbus** | Guardians of the Whills. |
| Trick Master | **Garindan** | Master of disguise. |
| Pokémon Center nurse | **2-1B** | Medical droid. |
| Frontier Brains | Bounty hunters: **Aurra Sing, Dengar, Zuckuss, 4-LOM, IG-88, Gardulla the Hutt, Dexter Jettster** | Lando hires them for the Grand Arena. |

### Arena leaders (gyms), in badge order

| # | Emerald | Star Wars | Planet / town | Type | Shard |
|---|---|---|---|---|---|
| 1 | Roxanne | **Biggs Darklighter** (Luke's friend, home from the flight academy, teaches at the academy) | Tatooine / Bestine | Rock | DUNE SHARD |
| 2 | Brawly | **Tarfful** (Wookiee chieftain) | Kashyyyk / Kachirho | Fighting | WROSHYR SHARD |
| 3 | Wattson | **Watto** (Toydarian junk dealer) | Tatooine / Mos Espa | Electric | SPARK SHARD |
| 4 | Flannery | **Sabine Wren** (Mandalorian artist and explosives expert) | Sullust / Pirin | Fire | MAGMA SHARD |
| 5 | Norman | **Doran** (player's dad) | Tatooine / Mos Entha | Normal | BALANCE SHARD |
| 6 | Winona | **Chief Chirpa** (Ewok chief; glider riders) | Endor / Bright Tree | Flying | CANOPY SHARD |
| 7 | Tate & Liza | **Kanan Jarrus & Ezra Bridger** (Jedi master and Padawan) | Yavin 4 / Massassi Temple | Force | FORCE SHARD |
| 8 | Juan | **Yoda** | Dagobah | Water | SWAMP SHARD |

### The Four Trials and the final battle (Ilum)

| Emerald | Star Wars | Type | Trial |
|---|---|---|---|
| Sidney | vision of **Darth Maul** | Dark | Fear |
| Phoebe | **Qui-Gon Jinn** (Force spirit) | Spirit | Loss |
| Glacia | vision of **Ki-Adi-Mundi** on frozen Mygeeto | Ice | Betrayal (Order 66) |
| Drake | vision of **Anakin Skywalker** | Dragon | The fallen hero |
| Wallace (Champion) | **Obi-Wan Kenobi** (real) | Water | |

---

## 6. Story acts (follows Emerald's 45 timeline events 1:1)

The chapter-by-chapter rewrite is in `mapping/timeline.csv`. In short:

1. **Tatooine (Act 1).** The family's freighter lands at Mos Pelgo. Rescue
   Prof. Korr from a MASSIFF and pick a starter (KATARNKIT, SUNCHICK or
   MARSHLET). First rival battle. Help Luke catch an AURALET outside Mos Entha.
   Jundland Wastes: a cartel thug robs an Organa engineer. Biggs's arena in
   Bestine. Bail Organa asks you to carry a message to Leia. Rescue Chewie in
   Beggar's Canyon, and Han offers you the Falcon.
2. **Kashyyyk & Mos Eisley (Act 2).** Tarfful's arena, deliver the message to
   Leia in the Shadowlands. Han flies you on to Mos Eisley: Jabba and Boba
   Fett first appear at the spacer museum, hunting Ric Olié's sub parts.
3. **Mos Espa, Sullust, Mustafar (Act 3).** Watto's arena and the podrace
   course. Hover-bikes from Wald. The Empire steals a meteorite at Starfall
   Cavern; you climb Mustafar Peak and beat **Vader** for the first time. Sabine's
   arena in Pirin. Dad's arena back on Tatooine.
4. **Endor (Act 4).** Treewalk routes, Bright Tree Village, the cartel raids
   Endor Station (Bossk), Chief Chirpa's arena.
5. **Bespin, Jedha, Yavin 4 (Act 5).** Cloud City, Jabba steals the RED KYBER
   from Jedha's Guardians, the Hutt Hideout under Cloud City (Boba Fett),
   Fortress Vader, the Empire raids the Yavin 4 launch tower (tag battle with
   Leia against Vader and Veers), the Force arena of Kanan & Ezra.
6. **Dagobah (Act 6).** Jabba wakes SANDO in the Drowned Cavern, Vader wakes
   GREATKRAYT. Storms on Dagobah. Obi-Wan guards the Cave of Evil. You ride to
   the asteroid field to wake the EXOGORTH, which calms the titans. Yoda's
   arena.
7. **Ilum (Act 7).** Crystal caves, final rival battle with Luke, the Four
   Trials, Obi-Wan. Ending: a medal ceremony on Yavin 4 (Hall of Fame).
8. **Post-game.** Lando's Grand Arena with the bounty hunters, the Warden
   golems (Regis) behind Aurebesh puzzles, the Force twins ASHLA and BOGAN
   (Lati@s), Kamino, and the event islands.

---

## 7. Companion design rules

The roster is in `mapping/species.csv` (all 386 species). Rules used:

1. **Type and stats never change.** A species row only renames and re-themes
   a Pokémon. Its base stats, types, abilities, learnset, evolutions and
   wild/trainer placements stay exactly as in Emerald, so balance is
   untouched. When a theme needs a different type, that is a NET_NEW idea, not
   a row edit.
2. **Pick the Star Wars thing that fits the type and the evolution line.**
   Three-stage lines become young → adult → elder of one creature.
3. **People are never companions, and the player is one fixed character for the whole game.** Vader, Boba Fett, Chewbacca and
   others are characters, and sentient species (Wookiees, Jawas, Tuskens, Gungans, Ewoks, Hutts, clones...) appear only as
   people. The owner chose this on 2026-10-31; the 48 slots that held sentient species now hold beasts and droids
   (`mapping/proposals/sentient_swap.csv`).
4. **Droids are companions** (later: "slicing" as the catch method for droids,
   listed as NET_NEW).
5. **Prefer canon.** `sw_basis` is a `starwars-db` id when one exists,
   `canon:<name>` for Star Wars canon outside the six films' databank, or
   `original` for a new Star Wars-style companion. A canon pass (2026-10-31) swapped 15 invented names for canon
   creatures (`mapping/proposals/canon_pass.csv`).
6. **Names fit the game:** at most 10 characters, uppercase.
7. **Where the companion lives should make sense for its planet.** Encounter tables stay as in Emerald (balance identical);
   `database/species_habitats.csv` explains every companion found off its home world (migrant, reserve, sea, story...).

The starters: **KATARNKIT → KATARNJAW → KATARN** (Grass, Kashyyyk),
**SUNCHICK → SUNSTRIDER → SUNBLAZER** (Fire/Fighting, Tatooine),
**MARSHLET → MARSHRUNNR → MARSHTITAN** (Water/Ground, Naboo).

Legendaries: **GREATKRAYT** (Groudon), **SANDO** (Kyogre), **EXOGORTH**
(Rayquaza), **ROCKWARDEN / ICEWARDEN / DURAWARDEN** (Regis), **ASHLA /
BOGAN** (Lati@s), **WHILLSTAR** (Jirachi), **SHIFTSTAR** (Deoxys), **TIDEWING / DAWNWING** (Lugia / Ho-Oh).

---

## 8. Ideas waiting for Step 4+ (NET_NEW)

Tracked as rows in `mapping/net_new.csv`, not built yet. Designs (maps, flags, level bands, placeholders) are in `bible/NET_NEW_DESIGNS.md`:

- Boba Fett as a multi-stage bounty-hunt storyline (rival boss fights only; he is never catchable and never joins the party).
- Slicing droids instead of throwing capture pods.
- Hyperlane travel: hangars at every planet border, unlocked one by one.
- A Death Star construction site dungeon (multi-floor, elevators, stormtrooper patrols) for the post-game.
- Light side / dark side affinity that picks between evolution branches (the TOOKA line already splits JEDITOOKA / SITHTOOKA by day / night).
- Sandstorm and blizzard weather that changes encounters.
- New moves with new animations: FORCE CHOKE, BLASTER SHOT, SABER SLASH.
