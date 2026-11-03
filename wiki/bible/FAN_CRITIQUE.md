# Fan critique: does this game feel like Star Wars?

A critical read of the whole game as a Star Wars fan and as a game critic (owner's brief, 2026-11-03).
Nothing in this file changes a wiki row or the game by itself. An item lands only once the owner approves
it; then it goes into `STORY.md` and `NET_NEW_DESIGNS.md`, then the mapping rows, then a rebuild.

Inputs: the wiki (`mapping/`, `database/`, `world/GUIDE.md`, the bible), the owner's
[starwars-db](https://github.com/spencerlepine/starwars-db) (`../starwars-db/database`, 594 entities,
5,513 lines of film dialogue, 727 scenes), and `../game` for feasibility only.

Written piece by piece: sections 1 and 2 are Part 1 (characters), section 3 is Part 2 (transitions and set
pieces), sections 4 and 5 are Part 3 (side content, the light / dark paths, what to approve). Complete.

---

## 1. Prominence: who is in the game, who is missing, who is filler

### The scoring method

`tools/prominence.py` scores every character, creature, droid, species, vehicle and location in starwars-db
and writes `mapping/proposals/prominence.csv` (one row per entity, with where the game uses it) and
`mapping/proposals/prominence_slots.csv` (one row per visible slot in the game, with the score of the
person holding it). Rerun it after any mapping change; it needs the starwars-db checkout next to the repo
(or `STARWARS_DB_DIR`).

The database has no rank column, so the rank is built from what it does have:

| Signal | Source | How it is counted |
|---|---|---|
| `films_w` | `timeline_entities.csv`, relationship `appearance` | Each of the six films the entity appears in. A prequel counts 1.0, an original-trilogy film 1.5 (the era of the game and the deepest nostalgia). Maximum 7.5. |
| `lines_w` | `quotes.csv`, `speaker_entity_id` | Lines of dialogue, same per-film weights. Characters only. |
| `scenes_w` | `timeline_scene_entities.csv` | Scenes a location or vehicle is in, same weights. |
| `reach` | `metadata.csv`, field `appearances` | Other films and series the entity is in (The Clone Wars, Rebels, Rogue One, Solo...), capped at 6. |
| `fan` | Complex, [The Top 50 Star Wars Characters, Ranked](https://www.complex.com/pop-culture/a/jamieiovine/top-50-star-wars-characters-ranked) (read 2026-11-03) | Top 10: +30. 11 to 25: +20. 26 to 50: +10. Used only where the six films cannot settle it: characters famous from the series. Empire's staff list was paywalled; Dexerto's loaded only in part, so Complex is the one source. |

```
db_score = 10 * films_w + 22 * log10(1 + lines_w) + 15 * log10(1 + scenes_w) + 2 * reach
score    = db_score + fan
```

Lines and scenes are on a log scale so that 600 lines (Anakin) does not drown everything else, and a
character with 40 lines still clearly beats one with 4. Film count is linear: being in four films is the
strongest single signal of nostalgia.

What the score gets wrong, and how the lists below correct for it:

- **Silent icons score low.** Chewbacca has 0 matched lines; the bounty hunters of The Empire Strikes Back
  (IG-88, 4-LOM, Zuckuss, Dengar, Bossk) have none and one or two films. Their fame is the lineup, not the
  dialogue. They are kept as `known`, not filler, by judgement.
- **Background prequel politicians score high** on film count alone (Nute Gunray 69, Mas Amedda 58, Rune
  Haako 55, Orn Free Taa 47). None of them is a nostalgia pick and most are dead by 2 BBY. They are left out
  of the missing list.
- **Series characters have no six-film data** (Ahsoka, Thrawn, Kanan, Ezra, Sabine, Rex, Krennic, K-2SO,
  Chirrut, Baze, Hera, Hondo, Cad Bane, Saw Gerrera). They appear with the fan bonus only, flagged
  `fan-list` in `source`. The owner's must-have list is the authority for them, not the score.
- **Species rows** in starwars-db (Bith, Gungan, Hutt, Dug, Gamorrean) show as unused because the game uses
  the person (Figrin D'an, Jar Jar, Jabba, Sebulba, the palace guards), not the species row.

Bands used below: **classic** 60 and up, **known** 35 to 59, **filler** under 35, **original** for invented
people.

### The ranking: top 30 characters

| # | Character | Score | In the game as |
|---|---|---|---|
| 1 | Obi-Wan Kenobi | 177 | Ben's Hut, the Cave of Evil, the final battle at Ilum |
| 2 | C-3PO | 167 | NPC beside Sen. Organa, Bestine (`net:character-c-3po`) |
| 3 | Luke Skywalker | 160 | the rival Wally was |
| 4 | Leia Organa | 153 | mentor and courier (Steven's slot) |
| 5 | R2-D2 | 153 | NPC at the StarNAV bench, Bestine |
| 6 | Anakin Skywalker | 149 | the Fourth Trial (vision) |
| 7 | Darth Vader | 149 | the Empire's leader (Maxie's slot) |
| 8 | Yoda | 147 | Dagobah Arena Leader |
| 9 | Han Solo | 146 | the Falcon's pilot (Mr. Briney's slot) |
| 10 | Emperor Palpatine | 145 | hologram on the Death Star command deck |
| 11 | Boba Fett | 122 | Cartel lieutenant and bounty-hunt boss |
| 12 | Lando Calrissian | 108 | the Grand Arena's owner (Scott's slot) |
| 13 | **Padmé Amidala** | 101 | **missing** (dead 19 BBY) |
| 14 | Jabba the Hutt | 98 | Cartel boss (Archie's slot) |
| 15 | Chewbacca | 97 | rescued in Beggar's Canyon; Han's co-pilot |
| 16 | Wedge Antilles | 96 | Rebel pilot on Yavin 4, lines only |
| 17 | **Grand Moff Tarkin** | 89 | **missing** (alive, Governor of the Outer Rim in 2 BBY) |
| 18 | **Mace Windu** | 88 | **missing** (dead 19 BBY) |
| 19 | Qui-Gon Jinn | 86 | the Second Trial (Force spirit) |
| 20 | Count Dooku | 78 | holocron relic in the Mining Facility |
| 21 | Jar Jar Binks | 74 | the traveller, six stops |
| 22 | Owen Lars | 74 | Luke's uncle, gives SURF and SAND SKIM |
| 23 | Bail Organa | 69 | House Organa, gives the StarNAV |
| 24 | **Mon Mothma** | 68 | **missing** (alive, founds the Alliance in 2 BBY) |
| 25 | Admiral Piett | 67 | Death Star hangar boss |
| 26 | **Beru Lars** | 61 | text only ("Aunt BERU"); no character row |
| 27 | **Admiral Ackbar** | 61 | **missing** (alive) |
| 28 | Bib Fortuna | 59 | Jabba's majordomo |
| 29 | Watto | 58 | Mos Espa Arena Leader |
| 30 | Ki-Adi-Mundi | 56 | the Third Trial (vision) |

Of the top 30, 24 are in the game. The full list is in `prominence.csv`.

### Missing classics, ranked

Everyone with a score of 35 or more who is not in the game, plus the series names the fan list puts above
them, with the 2 BBY check from starwars-db (`appearances`) and a proposed place. Dead characters get the
vision, holocron or history treatment the bible already uses for Anakin and Qui-Gon.

| # | Who | Score | 2 BBY | Proposal | Cost |
|---|---|---|---|---|---|
| 1 | Grand Moff Tarkin | 89 | alive; Governor of the Outer Rim, Krennic's rival over the Death Star | NPC on Death Star deck 5 beside Krennic and the Emperor's hologram: the man Krennic answers to. Two lines; never fought. | cheap: one object, text |
| 2 | Padmé Amidala | 101 | dead 19 BBY | A holo-portrait on Sen. Organa's desk in Bestine ("a senator from Naboo; Leia has her eyes"). Sign text. | cheap |
| 3 | Mace Windu | 88 | dead 19 BBY | A holocron in the Massassi Temple arena: Kanan's master Depa Billaba was Mace's Padawan, so Kanan keeps it. Sign text. Option B: make him the Third Trial instead of Ki-Adi-Mundi (see swaps). | cheap |
| 4 | Mon Mothma | 68 | alive; declares the Rebel Alliance in 2 BBY (Rebels, "Secret Cargo") | NPC in the Yavin 4 Launch Tower 2F, and the voice of the ending's medal ceremony text. | cheap (NPC); the ceremony art is `HUMAN-TODO` anyway |
| 5 | Admiral Ackbar | 61 | alive; Mon Cala officer with the Rebellion | NPC in the Yavin 4 hangar, Mon Calamari class pic (MON CAL exists). Lines only. One of his lines fires when the Launch Tower is raided. | cheap |
| 6 | Beru Lars | 61 | alive | Give the Mos Entha "Wally's mother" object its row: `character:wallys-mother` = BERU. The text already calls her Aunt Beru. | bookkeeping |
| 7 | Jango Fett | 47 | dead 22 BBY | A record in the Tipoca City cloning hall (the template's helmet in a case; the scientist's line). Boba's stage-3 battle on Route 134 is on Kamino: one line about his father. | cheap |
| 8 | Jan Dodonna | 41 | alive; Rebel general (Rebels, Rogue One) | NPC in the Launch Tower 1F: the base commander. | cheap |
| 9 | Moff Jerjerrod | 38 | alive | Rename the DS-5 officer trainer JIR to JERJERROD (the Death Star's commander in Return of the Jedi). Same class, same party. | cheap: name |
| 10 | Captain Antilles | 36 | alive; captain of the Tantive IV | Pilot of the Rebel transport from Cloud City to Yavin 4 (section 3 makes that ship the Tantive IV). | cheap |
| 11 | Wicket W. Warrick | 27 (+10 fan) | alive | Rename the EWOK trainer HURKAL on Route 119 (Emerald's HIDEO) to WICKET. Teebo and Paploo are already there. | cheap: name |
| 12 | Shmi Skywalker | 56 | dead 22 BBY | Two grave markers behind the Lars homestead in Mos Entha (Shmi, Cliegg). Sign text. | cheap |
| 13 | Max Rebo, Sy Snootles, Droopy McCool | 17 to 25 | alive | The band on a stage in Jabba's throne room. Three NPCs with one line each; three walkers. | cheap text, art for 3 walkers |
| 14 | Oola, EV-9D9 | 24, 15 | alive | A dancer by the dais and the droid overseer in a side room of the palace. | cheap |
| 15 | Wullf Yularen | 21 | alive; ISB colonel in 2 BBY (Rebels), on the Death Star in A New Hope | Rename the DS-5 officer trainer DAINE to YULAREN. | cheap: name |
| 16 | Grand Admiral Thrawn | fan 20 | alive; hunts the Rebels in the Outer Rim, attacks Atollon at the end of 2 BBY (Rebels S3) | Imperial officer NPC at the Atollon hangar (post-game): he came for the Bendu. Lines only. | cheap |
| 17 | Cassian Andor | fan 20 | alive; K-2SO's partner from 2 BBY (Andor S2) | NPC beside K-2SO in the Death Star hangar. | cheap |
| 18 | Hera Syndulla, Chopper | fan 10 each | alive; pilot of the Ghost | The Rebel transport from Yavin 4 to Hoth, Kamino and Dagobah becomes the Ghost; Hera and Chopper stand in the Yavin 4 hangar. | cheap |
| 19 | Hondo Ohnaka | fan 10 | alive; Weequay pirate (Rebels) | Replace Gardulla the Hutt as the Grand Arena Pike ace: the Pike is luck and trickery, which is Hondo. | swap (below) |
| 20 | Cad Bane | fan 10 | alive (The Clone Wars; The Book of Boba Fett) | Replace Aurra Sing as the Tower ace (she is dead by 2 BBY, section 2). | swap (below) |
| 21 | Saw Gerrera | fan 10 | alive; on Geonosis in 2 BBY, Jedha by 1 BBY | A Partisan NPC in NiJedha's hostel; Saw himself as one line of dialogue. | cheap |
| 22 | Bo-Katan Kryze | fan 10 | alive; Mandalorian in exile | Name one MANDALORIAN trainer in Pirin's arena BO-KATAN (or URSA, Sabine's mother, if a smaller name is wanted). | cheap: name |
| 23 | Kitster, Gasgano, Ody Mandrell, Teemto Pagalies, Ben Quadinaros, Mawhonic, Dud Bolt | 10 to 27 | alive | Kitster: a SCRAP KID in Mos Espa. The six racers: the SWOOP RACER trainers on Route 110's course (Emerald's Cycling Road triathletes), one name each. | cheap: names |
| 24 | Lama Su, Taun We | 43, 38 | dead 18 BBY (The Bad Batch) | The Kaminoan scientist in the cloning hall is Nala Se's successor; one line names them. | cheap |

Left out on purpose: Nute Gunray, Rune Haako, Mas Amedda, Orn Free Taa, Boss Nass, Panaka, Typho, Jocasta
Nu, Plo Koon and the rest of the Jedi Council (dead, or on Naboo and Coruscant, which are not in the world).

### Filler in visible slots

Every visible slot with the score of its holder is in `prominence_slots.csv`. The ones that read as filler
to a fan, with a verdict:

| Slot | Holder | Score | Verdict |
|---|---|---|---|
| Grand Arena Tower ace (Anabel) | Aurra Sing | 22 | **Replace.** Dead by 2 BBY (section 2). |
| Grand Arena Pike ace (Lucy) | Gardulla the Hutt | 12 | **Replace** with Hondo Ohnaka. A second Hutt adds nothing next to Jabba. |
| Grand Arena Pyramid ace (Brandon) | Dexter Jettster | 34 | Keep. Dex was a prospector before the diner, which is the Pyramid's theme. |
| Grand Arena aces (Dome, Palace, Arena, Factory) | Dengar, Zuckuss, 4-LOM, IG-88 | 15 to 32 | Keep. The Empire Strikes Back lineup is the point; a fan reads the row as one joke. |
| Cartel lieutenant (Shelly) | Bossk | 32 | Keep. Boba's old partner, right beside him. |
| Kachirho Arena Leader (Brawly) | Tarfful | 12 | **Option:** Chewbacca as the leader (see swaps). Tarfful is correct but obscure. |
| Bright Tree Arena Leader (Winona) | Chief Chirpa | 17 | Keep. The Ewok chief is the right Ewok for the chair; Wicket joins as a trainer. |
| Mos Espa hover-bike shop (Rydel) | Wald | 17 | Keep. Anakin's Rodian friend is a true Mos Espa local; add Kitster next door. |
| Trick House (Trick Master) | Garindan | 15 | Keep. The Kubaz spy as the master of disguise is a perfect fit. |
| HoloNet reporter (Gabby & Ty) | Fode & Beed | 10 | Keep. |
| Mos Eisley shipyard (Capt. Stern) | Ric Olié | 35 | Keep, low priority. A Naboo pilot on Tatooine is a stretch; the only canon Mos Eisley spacer with a name is BoShek (score 15), which is a smaller name. |
| Sullust astronomer (Prof. Cozmo) | Dr. Tien (original) | - | Keep. No canon astronomer fits Sullust. |
| Storage system (Lanette) | Tess (original) | - | Keep. |
| Third Trial (Glacia) | Ki-Adi-Mundi | 56 | Keep (Mygeeto is literally the frozen betrayal), or swap for Mace Windu (option in the swaps). |
| Podrace boss | Sebulba | 27 | Keep: owner's must-have. |

### Proposed swaps, ranked by payoff

Same slot, same class picture, same role, same balance. Only names, lines and (where the pic is pending
anyway) the art change.

| # | Swap | Reason | What changes |
|---|---|---|---|
| 1 | Aurra Sing → **Cad Bane** (Tower ace) | Aurra Sing is dead by 2 BBY (Solo: Beckett pushed her to her death, around 13 BBY). Cad Bane is alive, a Clone Wars favourite, and a bounty hunter Lando would hire. | `characters.csv` row `character:anabel`; the Tower ace pic (pending art); her lines. |
| 2 | Gardulla the Hutt → **Hondo Ohnaka** (Pike ace) | The Battle Pike is luck and trickery. Hondo is the galaxy's luckiest trickster and a series favourite; a second Hutt beside Jabba is dead weight. | `character:lucy`; the Pike ace pic (pending art); lines. |
| 3 | Tarfful → **Chewbacca** (Kachirho Arena Leader), Tarfful becomes the great-hall elder | The most famous Wookiee holds the Wookiee arena. He is rescued in Act 1, flies with Han to Kachirho and "keeps the arena while the chieftain is away". A fan hit; Tarfful stays as the elder who gives the shard's lore. | `character:brawly` and `character:peeko` roles; Brawly's pic and walker (pending art); Han's line about his co-pilot. Chewie still lives in Rwookrrorro. Must stay a person, never a companion. |
| 4 | HURKAL → **WICKET** (EWOK trainer, Route 119) | The Ewok everyone knows is missing while Teebo and Paploo are in. | `trainers.csv` `name:HIDEO`. |
| 5 | JIR → **JERJERROD**, DAINE → **YULAREN** (Death Star deck 5 officers) | The Death Star's own commander and the ISB colonel who sat at Tarkin's table. | `people.csv` trainer names. |
| 6 | Six Route 110 SWOOP RACERs → **GASGANO, ODY MANDRELL, TEEMTO, QUADINAROS, MAWHONIC, DUD BOLT**; one Mos Espa SCRAP KID → **KITSTER** | The Boonta Eve grid on the Boonta Eve course. Clegg Holdfast is already there. | `trainers.csv` names; lines. |
| 7 | One Pirin MANDALORIAN → **BO-KATAN** (or URSA) | Sabine's clan deserves one name a fan knows. | `trainers.csv` name. |
| 8 | Ki-Adi-Mundi → **Mace Windu** (Third Trial, Betrayal) | Option only. The betrayal fans remember is Mace's. Against: Mygeeto explains the Ice team; Mace with an ice team does not. Recommendation: keep Ki-Adi, give Mace the holocron (missing list, item 3). | `character:glacia` if taken. |

No swap above touches a party, a level or a prize.

---

## 2. Placement and timeline problems

Each prominent character checked against 2 BBY (starwars-db `appearances` and the bible's canon policy,
section 1). Bends already recorded in `canon_note` are judged; new problems get a fix.

| # | Problem | Where | Fix | Cost |
|---|---|---|---|---|
| 1 | **Aurra Sing is dead.** Killed around 13 BBY (Solo). A dead bounty hunter runs the Battle Tower. | `character:anabel` | Swap 1 above. | cheap |
| 2 | **Tipoca City is rubble.** The Empire bombarded it in 18 BBY (The Bad Batch). The game's stilt city stands as if nothing happened. | `location:pacifidlog-town`, `net:kamino-cloning-hall` | Keep the city; add a `canon_note` and one line in the cloning hall: the Kaminoans rebuilt on new stilts after the Empire shelled the old city, which is why the hall is "mostly dark". | cheap |
| 3 | **"Luke's X-wing" sunk in Dagobah's swamp.** Luke crashes there in 3 ABY; in 2 BBY he has never left Tatooine. | `world_art.csv` `art:dagobah:sunken-x-wing` | Make it the player's borrowed X-wing, sunk on landing, raised by Yoda after the badge (section 3 set piece). Until then, describe it as a Clone Wars wreck. | cheap (note); medium (set piece) |
| 4 | **Luke lodges with Camie's father.** Emerald sends Wally to his uncle; fans expect Luke at the Lars homestead with Owen and Beru. | `character:wallys-uncle`, texts | Keep the structure, change the words: Luke "works at Camie's family farm in Anchorhead by day" and sleeps at home. Mos Entha's house is the Lars homestead (Owen, Beru). | cheap: text |
| 5 | **Beru has no row.** The text says "Aunt BERU"; `characters.csv` has no `wallys-mother`. | `characters.csv` | Add the row. | bookkeeping |
| 6 | **The Death Star's place.** In 2 BBY the station was built over Geonosis and then moved (Rebels, "Ghosts of Geonosis"). The wiki never says where it is. | `mapping/planets.csv` DEATH STAR | The shuttle ride text: "a secret orbit; the Empire moved it from Geonosis to hide it". One line for fans, no map. | cheap |
| 7 | **Leia as "senator".** At 17 she is not yet in the Senate (that is 0 BBY). | `character:steven` title and lines | Call her Princess Leia of Alderaan, running relief missions under her father's cover (Rebels S3, 2 BBY). "Senator" stays Bail's title. | cheap: text |
| 8 | **Kanan and Ezra on Yavin 4.** In 2 BBY the Ghost crew is at Chopper Base on Atollon; Yavin is 1 BBY. | `character:tate`, `character:liza` canon_note | Use it: "the arena moved to Yavin 4 after Thrawn hit Atollon", which ties to the post-game Atollon event and the Thrawn NPC (missing list, item 16). | cheap |
| 9 | **Sabine on Sullust.** In 2 BBY she is with the Ghost crew and on Krownest. | `character:flannery` | Owner-approved bend; keep. One line: "I keep the arena for the cell between runs." | none |
| 10 | **Maul lives.** In canon Obi-Wan kills him in this very year (Rebels, "Twin Suns"). The game has him leave after the duel. | `net:maul-duel` | Right call for the tone (villains are defeated, not killed). Say so in `canon_note`. | none |
| 11 | **Cody as a drill master.** The Bad Batch has Cody desert the Empire in 18 BBY. The owner's table calls him an Imperial officer. | `net:character-cody` | The wiki's version (an aged clone who stayed to keep the last cadets) fits the desertion better than an officer would. Fix the canon_note to say he left the Empire. | cheap: note |
| 12 | **Rex on Endor.** In 2 BBY Rex is with Phoenix cell on Atollon. | `net:character-rex` | Owner placement; keep. His line names the cell. | none |
| 13 | **Piett, Ozzel, Needa on the Death Star.** They are Death Squadron navy officers in 3 ABY, not station crew. | `net:character-*` | Keep as junior officers on a posting; swap 5 adds the two men who actually sat on the Death Star. | none |
| 14 | **Red Leader, Gold Leader, Porkins in Doran's arena.** Yavin's pilots as Tatooine gym trainers. | `trainers.csv` cameos | Harmless ("flying for Doran before Yavin"). Low priority; a fan would rather meet them in the Yavin 4 hangar, where the pilots' slots are taken by Wedge, Janson, Hobbie, Zev and Dak. | none |
| 15 | **Sio Bibble on the starliner.** Naboo's governor on a tourist ferry. | `trainers.csv` `name:THOMAS` | Harmless. | none |
| 16 | **Dianoga's home is Kamino.** The trash-compactor creature of A New Hope. | `species.csv` | Put a DIANOGA fixed battle in a Death Star garbage room (section 3). The home planet can stay. | cheap |
| 17 | **Sandtroopers are NPCs, not a trainer class.** The owner's list asked whether they are a real class picture. | `net:walker-sandtrooper` | They are overworld patrols with a walker. A sandtrooper trainer pic needs a new class (medium) because class pics are per class, not per map. Keep as NPCs unless the owner wants the class. | none / medium |

Judged fine as recorded: Han with the Falcon (he has flown it since about 10 BBY), Lando as a gambler
before Cloud City, Watto, Wald and Sebulba still in Mos Espa, Biggs home from the Academy, Boba working for
Jabba with Bossk, Chirrut and Baze on occupied Jedha, Krennic running the project, K-2SO with Cassian from
2 BBY (Andor), Ahsoka between worlds at the Mortis Gate, Jar Jar wandering (Aftermath puts him on Naboo as a
street performer; a traveller is a kinder reading), Yoda's hut, Fortress Vader (standing since before Rebels),
Rieekan and Derlin surveying Hoth years before Echo Base, Lobot already running Cloud City's systems, Wedge
and Hobbie defected in 2 BBY (Rebels), Nien Nunb smuggling for the cause.

### The must-have list, checked

| Character | 2 BBY (starwars-db) | In the game | Verdict |
|---|---|---|---|
| C-3PO, R2-D2 | with the Organas from 19 BBY (Rebels S1) | NPCs in House Organa's tower, Bestine | placed; never companions |
| Jawas | - | JAWA trainer class, sandcrawler, palace droid seller | good |
| Tusken Raiders | - | RAIDER class (`net:trainer-class-raider`), Ben's Hut, Tusken Ruins | good; the class still needs its pic |
| Sandtrooper | - | NPC patrols, Tosche Station and Mos Eisley | placed; see problem 17 |
| Stormtrooper | - | STORMTROOPER trainers everywhere the Empire is | good |
| Jar Jar Binks | alive | traveller, six stops | placed |
| Boba Fett | works for Jabba | four-stage hunt, Hutt Hideout | good |
| Watto | alive | Mos Espa Arena Leader | good |
| Darth Maul | alive, Twin Suns | vision at Ilum; real duel at Ben's Hut after the credits | good |
| Vader / Anakin | - | three real battles; the Fourth Trial | good |
| Sebulba | alive | SWOOP RACER boss at the grandstand | placed |
| Jabba | at his palace | Cartel boss, palace, Hutt Hideout | good |
| Leia | 17, Rebel courier | Shadowlands, Starfall, Launch Tower, Hall of Fame | good; title fix (problem 7); the "trapped in Jabba's palace" scene is in section 3 |
| Han | flies the Falcon | pilot; cantina booth | good; first meeting in the cantina is in section 3 |
| Yoda | on Dagobah | Arena Leader | good |
| Ahsoka | lost 3 BBY to 1 BBY | the Mortis Gate, lines only | placed |
| Obi-Wan | hermit | Ben's Hut, Cave of Evil, Ilum | good |
| Chewbacca | with Han | rescued; Rwookrrorro | good; swap 3 makes him an Arena Leader |
| Dooku, Grievous | dead | holocron; vision | placed |
| Luke | 17, on the farm | the rival Wally was | good |
| Commander Cody | deserted 18 BBY | Tipoca City cloning hall | placed; note fix (problem 11) |
| Director Krennic | runs the project | Death Star command deck boss | placed; Tarkin to join him |
| K-2SO | with Cassian | Death Star hangar | placed; Cassian to join him |
| Palpatine | Emperor | hologram, never fought | placed |
| General Veers | - | Vader's field commander | good |

---

## 3. Transitions and set pieces, planet by planet

Part 2. The question here is whether the trip between planets, and the big rooms on each planet, feel like the
films. Every ride in `mapping/hyperlanes.csv` is reviewed, then every planet's set pieces, then the classic
creatures and ships. Costs use one scale for the rest of this document:

| Cost | Means |
|---|---|
| Cheap | Text rows and script lines only (or one `world_art.csv` row for the usual art pipeline). No C. |
| Medium | A new room, a new sprite, or a C change under about fifty lines. |
| Expensive | A new system (battle code, a new vehicle, a new screen) or a new art kit. |

Every film line below was measured against the 208 px text box with the width table `tools/font_widths.json`;
each line as written fits. Lines are quoted from `quotes.csv` and cut, never reworded, unless marked *(new)*.

### 3.1 How a ride works now

Three rides have a cabin: the Falcon (one shared room, `hangar-tatooine-kashyyyk`, for both legs), the Rebel
shuttle (`hangar-tatooine-endor`) and the Sullustan transport (`hangar-tatooine-sullust`). They follow Mr.
Briney's boat (`data/maps/Route104_MrBrineysHouse/scripts.inc`, `..._EventScript_SailingIntro`): talk to the
pilot at the StarNAV console, fade, cabin, fade, the other hangar. The cable car keeps Emerald's scene
(`src/cable_car.c`). The star liner keeps the S.S. Tidal rooms. Every other ride is hangar to hangar with a
fade, like the Lilycove ferry (`data/maps/LilycoveCity_Harbor/scripts.inc`). The hyperspace jump has a VFX row
(`net:vfx-hyperspace-jump`).

That is sound. The problem is that most rides are silent: a console, a fade, a new planet. A film ride has one
beat: a line from the pilot, a thing seen from the viewport, a face on the pad. One beat per ride is two or
three text boxes in the hangar script, so almost every row below is Cheap.

### 3.2 Every ride

| Ride | Ship and pilot now | Proposed | The moment | Cost |
|---|---|---|---|---|
| Route 104 → Kachirho | Millennium Falcon, Han | Keep. | Chewie is just rescued and boards first. The cabin gets the dejarik table (`art:new:dejarik-table` exists). Han, at the console: "She may not look like much, but / she's got it where it counts, kid." The jump plays the hyperspace VFX. On the pad: Chewie leaves without a word; Han: "Kashyyyk. His home. Don't stare at the trees." *(new)* | Cheap |
| Kachirho → Mos Eisley | Falcon, Han | Keep. The parked freighter at Docking Bay 94 (`art:tatooine:freighter-parked`) is named as the Falcon from this ride on. | Han, before landing: "Old Ben calls Mos Eisley a wretched / hive of scum and villainy." *(new, from Obi-Wan's line)*. The Falcon stays parked in the docking bay for the rest of the game, so the town has the ship in it. | Cheap |
| Route 112 → Route 113 | Sullustan transport, no named pilot | **Nien Nunb flies it.** He is at Inyusu Tor with lines only (section 1); this gives him a job. | Nien speaks Sullustese; the console translates: "He says Sullust is hot. Keep your / companions out of the vents." *(new)*. The viewport shows the ash sky. | Cheap |
| Route 112 → Mustafar Peak | Shuttle (cable car) | Keep Emerald's cable-car scene as a mining tram over lava; the redrawn background is already a cutscene-generator row (G4). | Attendant, first ride: "They say a Jedi died up there. / Nobody says which one." *(new)*. On the Act 5 ride the fortress spire is visible in the background. | Cheap |
| Mos Espa → Route 118 | Rebel shuttle | Keep. Say what it is: a stolen Lambda-class Imperial shuttle (the Lambda slot). The cockpit art exists (`art:new:ship-cockpit`). | Pilot: "Stolen. The codes are older than me, / but they check out." *(new, after Piett)*. From orbit: "Forest moon. The Empire's been / surveying the far side. We go in low." *(new)* | Cheap |
| Route 121 → Cloud City | Cloud City shuttle | **A twin-pod cloud car.** Bespin's own ship; one `world_art.csv` row, greybox piece, parked on the landing platform (`art:bespin:landing-platform`). | The moment is silence: Lobot waits on the platform, nods, and walks off. He never speaks in the films, so he never speaks here. | Cheap (text) + 1 art row |
| Route 121 → Felucia Reserve | Reserve shuttle | Keep. | One warden line about the fungus forest. Nothing else; the reserve is its own set piece. | Cheap |
| Cloud City → Jedha pad | Pilgrim shuttle | Keep. | The pilgrims chant on the way: "I am one with the Force / and the Force is with me." (Chirrut's mantra; Rogue One, not in the six-film db, see section 1). From orbit: "Star Destroyers over the holy city." *(new)*: the Empire holds Jedha in 2 BBY. | Cheap |
| Jedha pad → Route 123 | Pilgrim shuttle | Keep. | A return drop. One line. | Cheap |
| Cloud City → Yavin 4 | Rebel transport | **The Tantive IV, Captain Antilles** (section 1 swap): Bail Organa's consular ship running Alliance friends to the Massassi base. | Antilles: "Senator Organa sends his regards. / We fly for the Alliance now." *(new)*. Option: the cabin is the white corridor (one interior yaml, `greybox room`). On the pad Dodonna meets the ship (section 1 add). | Cheap (text) / Medium (corridor room) |
| Yavin 4 → Hoth | Rebel survey shuttle | Keep. | Pilot: "Nothing lives out there but wampas / and tauntauns. Keep moving." *(new)*. The probe droid is a set piece below. | Cheap |
| Yavin 4 → Tipoca City | Rebel transport | Keep. | Pilot: "Kamino isn't on any Republic chart. / Somebody erased it." *(new, the archive erasure)*. Rain on the pad. | Cheap |
| Yavin 4 → Dagobah | Rebel transport | **A borrowed X-wing.** The player's first solo flight. It sinks into the bog on landing: the Empire Strikes Back homage moved onto the player, which fixes the "Luke's X-wing" landmark (section 2). Yoda raises it after the eighth shard. Details in 3.3. | The sink: a short scene on the pad (the X-wing object slides into the water, one sound, one line: "I have a bad feeling about this."). | Medium |
| Dagobah → Asteroid Spire | Player's ship | **Han's Falcon.** When the titans wake, Han flies in ("heard about the storm") and takes the player into the asteroid field. The Falcon cabin room exists; the player's X-wing is still in the bog, so Han is needed, not decorative. | At the jump: "Never tell me the odds!" At the Spire's mouth: "This is no cave." (the Spire's wild table already has MYNOCKMAW; the EXOGORTH is the space slug). Inside: "Mynocks. Chewie, check the outside." | Cheap |
| Dagobah → Ilum | Player's ship | The raised X-wing. | Yoda, at the pad: "Mind what you have learned. / Save you it can." | Cheap |
| Yavin 4 → Death Star | Captured Imperial shuttle | Keep (the second Lambda). | The deck officer clears the shuttle: "It's an older code, sir, but it / checks out." The viewport art exists (`art:new:death-star-viewport`). | Cheap |
| Cloud City / Mos Eisley → Grand Arena | Star liner (S.S. Tidal), Han as captain (Briney's role) | Keep the rooms. The liner is Lando's; Han flies it ("he owes me a ship"). | The lounge has a sabacc table: "Lando lost the Falcon at a table / like this one." *(new)*. Chewie on the lower deck. | Cheap |
| Cloud City → Tython, Atollon, Mortis, the Wellspring | Charter ship | Keep. | One line per destination at the Cloud City console. | Cheap |
| Jedha pad → Mustafar Peak | Imperial shuttle (captured) | Keep (Lambda). | The viewport: a Star Destroyer hangs over the lava; the shuttle flies under it and no one hails. The fortress below. Two boxes. | Cheap |

Twenty-three rides. Three need a decision from the owner (the X-wing, Han's return, the Tantive IV); the rest
are text.

### 3.3 One-way escapes

The owner asked for one-way escapes. Rule first: no planet is ever stranded. Every one-way ride ends on a
planet with a hangar, and Emerald's Fly (StarNAV) needs nothing new. Three escapes fit the story as it stands.

1. **The X-wing in the bog (Dagobah, Act 6).** The player lands on Dagobah in a borrowed X-wing and it sinks
   (ride above). For the whole of Act 6 the ship sits nose-down in the swamp beside the pad, which is what the
   sunken X-wing landmark (`art:dagobah:sunken-x-wing`) already draws; it just stops being Luke's. Han's Falcon
   carries the player to the asteroids. After the eighth shard, Yoda raises the ship: he walks to the water, the
   object rises (one fade, one sound), and he says "Do. Or do not. / There is no try." From then on it is the
   player's ship for Ilum. Cost: Medium. One X-wing object sprite (64x64; placeholder: the vanilla S.S. Tidal
   sprite scaled is wrong, so a greybox piece first), two short scripts in `world/dagobah/interiors/dagobah-hangar`
   (about eighty lines), three text rows. The hangar yaml's "Player's ship" (`art:new:player-ship`) becomes the X-wing. Nothing else
   changes: the hyperlane gates stay `event:sootopolis-crisis` and `flag:badge08-get`.
2. **Jabba's sail barge to the Pit of Carkoon (Tatooine, Act 3 side content).** The barge dock
   (`jabbas-palace-barge-dock`, `art:new:sail-barge`) is a prop today. Proposal: after the rancor pit, Bib
   Fortuna invites the player aboard; the barge sails to the Great Pit in the Dune Sea and the player is put on
   the plank. C-3PO's line, from a protocol droid on the deck: "In his belly, you will find a new / definition of
   pain and suffering." The drop is a fixed battle with a SARLACC (Swalot line) in the palace band (level 23,
   like the rancor), not catchable, same script shape as the rancor pit (`net:jabbas-palace`). Win, and the
   barge leaves without you: the way back is on foot through the Dune Sea with SAND SKIM, past the older barge
   wreck and the krayt bones, which gives the Dune Sea its reason to exist. Reward: an item only (no new power).
   Gate: the rancor flag (`flag:unused-0x029`) and HM09 SAND SKIM, which OWEN gives at Mos Entha after the fifth shard
   (`database/obtain.csv`), so the walk home is always possible. Cost: Medium: a warp with a fade, one short deck
   scene (about forty lines), one fixed battle, six text rows, one flag.
3. **The escape pod from the Death Star (post-game).** After Krennic on deck 5, the command deck's escape pod
   (`art:shared:escape-pod`) drops the player into the Dune Sea beside the sandcrawler, which is A New Hope's
   opening. The Jawas are already there. The shuttle from Yavin 4 flies back to the Death Star any time, so
   nothing is lost. Cost: Cheap: one warp, two text rows.

Not proposed: a one-way planet (the owner's loop through Tatooine needs every hangar open), and a ship the
player steers (section 4.3).

### 3.4 Set pieces, planet by planet

"There now" is what the wiki already places. "Add" is proposed, each with a cost. Beats are kept short on
purpose: a set piece in this engine is a room, a prop and three text boxes.

**Tatooine.** There now: Mos Pelgo and the freighter, Ben's Hut (Obi-Wan; the Maul duel post-game), the Lars
homestead at Tosche Station, Anchorhead with the T-16 prop, Beggar's Canyon (Chewie's rescue), the Cantina
(Wuher, the band, Ponda Baba and Evazan, Greedo's optional battle), the Spacer Museum (Jabba and Boba Fett), the
podrace grandstand (Sebulba), Watto's junk shop, Jabba's Palace (rancor pit, barge dock), the Dune Sea (sail
barge wreck, sandcrawler, krayt bones), the Tusken Ruins. That is the best-covered planet in the game. Add:

- **Shmi's and Cliegg's graves** at the homestead (section 1): two sign tiles, two text rows. Cheap.
- **The krayt call.** When the player first enters the Jundland Wastes, play GREATKRAYT's cry off-screen
  (`playmoncry`) and one line from a settler. Obi-Wan's trick in A New Hope. Cheap.
- **The binary sunset.** The cheap version is a sky strip in the Tosche Station tileset with two suns (one
  `terrain.csv` row). The real version is an evening palette on the homestead map for one scripted moment,
  which is a palette copy of the tileset and a fade: Medium. Recommend the cheap version now.
- **Han and Greedo in the booth** (the owner asked to consider a first meeting in the Cantina). Han has to be
  met on Route 104 in Act 1, because the Falcon flies in Act 1. What the Cantina can hold is the *first proper
  scene*: once, when the player enters with Han's flag set, Han and Greedo sit in the booth; Greedo backs down
  (he lives until 0 BBY). Greedo's optional battle is already designed (`net:cantina-greedo-battle`). Cheap.
- **The barge and the Sarlacc** (3.3). Medium.

**Kashyyyk.** There now: Kachirho (Tarfful), the Shadowlands (Leia), the Republic Wreck (a Venator hull from
the Clone Wars battle), Rwookrrorro (Chewbacca at home), the Ice Grotto. Add:

- **Yoda's escape pod.** In Revenge of the Sith Yoda fled Kashyyyk in a pod with Chewbacca's help. Put
  `art:shared:escape-pod` on the Republic Wreck's deck with one sign: "19 BBY. A Jedi left in this. Tarfful
  says no more." *(new)*. It sets up Yoda's arena four acts later. Cheap.
- **"Let the Wookiee win."** A dejarik table in Chewbacca's hut, one sign. Cheap.

**Sullust.** There now: Inyusu Tor (Nien Nunb), Starfall Cavern (the meteorite), Pirin (Sabine's arena), the
Magma Tunnels. Add: Nien flies the transport (3.2). Nothing else; Sullust is a short act.

**Mustafar.** There now: Mustafar Peak (first Vader battle), the Mining Facility (Veers, the SITH SHARD, the
duel record), Fortress Vader (Act 5), the lava viewport, the shuttle station. Add:

- **The high ground.** One more line in the duel record: "It's over. I have the high ground." Cheap.
- **An AT-AT at the Mining Facility.** Veers is there; the walker is his. One `world_art.csv` row (a large
  landmark, about 4x3 tiles). Cheap to list; the usual art pipeline.
- **Vader's chamber** on Fortress Vader 4F: a meditation pod prop with one line. Cheap.

**Endor.** There now: the treewalk routes, Bright Tree (Chirpa's arena), Endor Station (Bossk), the Endor
clearing (AT-ST wrecks, the Imperial bunker, the commando), Boba Fett stage 1, the Ancient Tomb, the Scorched
Hollow. Add:

- **The net.** The log trap art exists (`endor_log-trap`). First time into Bright Tree, the player is caught in
  a net (fade, one sound) and WICKET (section 1 swap) cuts them down. Six script lines, three text rows. Cheap.
- The Imperial bunker is a survey post in 2 BBY, not the shield generator; one line in its sign says so
  (section 2's timeline fixes).

**Felucia.** The reserve is its own set piece: catching. Option: a crashed Republic gunship with a sign about
Order 66 (Aayla Secura died here); one art row, one text. Cheap, low priority.

**Bespin.** There now: Cloud City (Lando, Lobot), the carbon-freezing chamber, the Hutt Hideout (Boba Fett;
Jabba beaten), the Tibanna Refinery (Lobot's side job), the galleria, the showcase hall. Add:

- **The carbonite trophy.** `new_carbonite-block` exists. Put it in the Hideout's throne room as Jabba's wall
  piece: "a smuggler who crossed him". Not Han; it is 2 BBY. One sign. Cheap.
- **The dinner.** Lando leads the player into the Hideout to "dinner", and Boba Fett is at the table: that is
  the Hideout's Boba battle already; one line makes it the Empire Strikes Back beat. Cheap.
- **An Ugnaught** in the refinery: the UGNAUGHT class exists (Emerald's hikers); place one. Cheap.
- The cloud car on the landing platform (3.2).

**Jedha.** There now: NiJedha (Chirrut, Baze, the kyber trader), the Temple of the Kyber (six floors, the
summit, Vader's troops take the BLUE KYBER), Boba Fett stage 2, the pilgrim shuttle. Add:

- **A stormtrooper patrol** in NiJedha's street: two trainers of the existing STORMTROOPER class, the Rogue One
  street. Cheap.
- The kyber trader reads the player's path (section 4.2). Cheap.
- Saw's Partisan (section 1). Cheap.

**Yavin 4.** There now: the Massassi Temple arena (Kanan and Ezra), the Launch Tower (the raid, the tag battle
with Leia against Vader and Veers), the X-wing hangar (Wedge and the pilots), the medal ceremony, the Sabacc
Den. Add: Dodonna, Mon Mothma and Ackbar (section 1), **Y-wings** beside the X-wings (one art row), and the
scanner table on Launch Tower 2F (`new_scanner-table`) as the briefing table with one sign. Cheap.

**Hoth.** There now: the tundra, the survey outpost (Rieekan, Derlin), the tauntaun shelter, the Wampa Cave (the
lost scout), the snowspeeder, the Echo Base hangar door. Add:

- **The WAMPA that has the scout.** When the player finds the lost scout he hangs from the ice like Luke, and
  a fixed battle with a WAMPA (Glalie line, the cave's band) starts; not catchable, same script shape as the
  rancor. Medium (one fixed battle, four text rows).
- **The probe droid.** An Imperial probe droid stands on the tundra; walk up to it and it self-destructs (fade,
  sound, a crater line). The Empire Strikes Back opening, two years early, which the timeline allows: the
  Empire probes everywhere. Medium: one 32x32 object sprite (the big walker kit is not built; placeholder: a
  vanilla sprite), one script.
- Not proposed: tauntaun riding. A new mount is the hover-bike code plus a rider sheet: Expensive.

**Kamino.** There now: Tipoca City, the cloning hall (Cody; PROTOCLONE's lab; the growth pods), the Sealed
Vault, Boba Fett stage 3 on Route 134. Add: Jango's record and the Lama Su line (section 1), and **Slave I** parked
on the Tipoca pad while Boba is at stage 3 (one art row, shown by the hunt var). Cheap.

**Dagobah.** There now: the swamp town (Yoda's arena), Yoda's hut, the Cave of Evil (Obi-Wan at the mouth), the
Drowned Cavern (Jabba wakes SANDO), the titans' clash, the sunken X-wing. Add: the X-wing sink and raise (3.3),
Han's Falcon (3.2), and Obi-Wan's line at the cave by the player's path (section 4.2). Qui-Gon's "There's always
a bigger fish." from a fisher on the pier after SANDO wakes. Cheap.

**Asteroid Field.** There now: the Spire and the EXOGORTH. Add Han's three lines (3.2). Cheap.

**Ilum.** There now: the Crystal Caves (Luke's last battle, Boba Fett's finale), the Four Trials, Obi-Wan, the
visions (Maul, Qui-Gon, Ki-Adi, Anakin), the supply depot. Add: **the Gathering**: at the temple door Yoda hands
the player a KYBER CRYSTAL, or Obi-Wan a SITH SHARD, by the player's path (section 4.2, stage 2). It is an
existing item, so no new power. Cheap.

**Death Star (post-game).** There now: five decks, the hangar (TIE rack, Imperial shuttle), Krennic on the
command deck, Piett on the hangar deck, K-2SO, the superlaser console, the turbolift, the viewport, the trench
wall. Add:

- **The trash compactor.** A garbage chute on deck 3 drops the player into a compactor room on deck 2: a fixed
  battle with a DIANOGA (Tentacruel line, deck band), then the walls close (two screen shakes, a fade) and K-2SO
  opens the hatch. Leia's line on the chute sign: "Into the garbage chute, wise guy." Medium (one room, one
  fixed battle, five text rows).
- **Cell 2187** in the detention block: one sign. Cheap.
- Tarkin on deck 5 (section 1). Cheap.
- The escape pod exit (3.3). Cheap.

**Grand Arena, Tython, Atollon, Mortis (post-game).** Add: the section 1 swaps (Cad Bane, Hondo), the liner's
sabacc line (3.2), Thrawn and the Bendu at Atollon (section 1; the Bendu is the balance voice in section 4.2).
Cheap.

### 3.5 Classic creatures and ships

**Creatures.** Checked against `mapping/species.csv` and `database/species_habitats.csv`. Every creature a
film fan would name is a species and lives where it should: BANTHA, DEWBACK, RONTO, EOPIE, WOMPRAT and KRAYT
on Tatooine (GREATKRAYT is the titan); SARLACC, RANCOR, DIANOGA, MYNOCK, EXOGORTH (the space slug); WAMPA and
TAUNTAUN on Hoth; NEXU, REEK and ACKLAY (the Geonosis arena beasts); OPEE, COLOCLAW, KAADU, FAMBAA and NUNA from
Naboo; AIWHA on Kamino; VARACTYL; KOWAKIAN; LOTHCAT, LOTHWOLF, TOOKA, PURRGIL and CONVOR from the series; MASSIFF.
Droids: B1 and B2, IG UNIT, MOUSEDROID, GONK, the R-units, BUZZDROID, VULTURE, OCTUPTARRA, PIT DROID, the
training REMOTE, the crab droid, FX-6 and MINDPROBE (the interrogation droid). PORG is the one sequel-era creature;
harmless.

Four icons have no row. The mapping is approved, so these are optional renames of rows whose basis is `original`
(an invented creature), listed for the owner's "more invented names swapped for canon ones" note:

| Missing | Why it matters | Row that could carry it |
|---|---|---|
| Droideka | The destroyer droid; every prequel fan expects it. | None fits well: every droid row is already a canon droid. Leave it. |
| Probe droid | The Empire Strikes Back opening. | Better as the Hoth object above than as a species. |
| Gundark | "Strong enough to pull the ears off a gundark." A big four-armed brute. | `species:slaking` SLOTHKING (line SLOTHLET, SLOTHFURY: all `original`) → GUNDARK. |
| Nerf | "Nerf herder." The galaxy's cattle. | No `original` herd beast is free. Leave it; the insult can still appear in text. |

**Ships.** Checked against `mapping/world_art.csv` and the greybox sheets.

| Ship | In the game now | Proposed | Cost |
|---|---|---|---|
| Millennium Falcon | Cabin room; the parked freighter at Mos Eisley | Name the freighter as the Falcon; Han's asteroid run (3.2) | Cheap |
| X-wing | Parked at Yavin 4; sunken on Dagobah | The player's X-wing (3.3) | Medium |
| Snowspeeder | Hoth | Keep | – |
| AT-ST, speeder bike | Wrecks on Endor | Keep | – |
| TIE fighter | The rack in the Death Star hangar | Keep | – |
| Lambda shuttle | The Imperial shuttle in the Death Star hangar; the Rebel shuttle and both captured shuttles are the same ship | Say so in each hangar's sign | Cheap |
| Sail barge | Jabba's dock; a wreck in the Dune Sea | The barge ride (3.3) | Medium |
| Podracers | Mos Espa, the course on Route 110 | Keep | – |
| Sandcrawler, landspeeder, escape pod | Dune Sea; every town | The pod as the Death Star exit (3.3) | Cheap |
| Republic cruiser | The wreck on Kashyyyk | Yoda's pod on its deck (3.4) | Cheap |
| S.S. Tidal | The star liner rooms | Lando's liner, Han flying (3.2) | Cheap |
| **AT-AT** | Missing | The Mining Facility, with Veers (3.4) | 1 art row |
| **Slave I** | Missing | The Tipoca pad at Boba's stage 3 (3.4) | 1 art row |
| **Star Destroyer** | Only a quarters interior | Seen from the Jedha → Mustafar shuttle viewport (3.2); never walked on | Cheap (text) |
| **Y-wing** | Missing | Beside the X-wings on Yavin 4 (3.4) | 1 art row |
| **Tantive IV** | Missing | The Bespin → Yavin ride (3.2) | Cheap / Medium |
| **Probe droid** | Missing | The Hoth tundra (3.4) | Medium |
| **Cloud car** | Missing | The Endor → Bespin ride (3.2) | 1 art row |
| Jedi starfighter, N-1, skiff | Missing | Not needed by any scene. Skip. | – |

The verdict for Part 2: the rooms are there. The game already has more film rooms than most fan games, and
nearly all of them in the right place. What it lacks is the *moment* on the way in: the line at the console, the
thing out the window, the face on the pad. Those are text, and they are the cheapest way to make a planet feel
like Star Wars rather than like Hoenn with new names.

## 4. Side content and the light / dark paths

Part 3. Three things: the bounty hunter side quest, the light / dark two-path feature (decided by the owner,
designed here in full), and the things the owner asked about that turn out not to be needed. Costs use the
scale from section 3. Feasibility was checked by reading `../game`; nothing in it was changed.

### 4.1 The bounty board

The game already has bounty hunters everywhere (Boba Fett's four stages, the seven Frontier Brains, the hunter
waiting for work in Jabba's Palace), but the player never hunts anything. A board fixes that cheaply.

**Where.** A WANTED board on the wall of the Mos Eisley Cantina (`mos-eisley-fan-club`), next to Wuher's bar.
Wuher is the broker: his drinks menu is already a multichoice, and the board is a second one (one new
`MULTI_` list in `src/data/script_menu.h`). Mos Eisley is the hub the player passes through most, so the board is
seen often.

**Two columns.** Hutt pucks (posted by the Cartel: paid in credits) and Alliance pucks (posted by the Rebellion:
paid in items). Which column a player works from feeds the light / dark score (4.2), so the board is also the
cheapest place for the player to *choose* a path by doing rather than by answering a question.

**The marks.** Six, every one an existing person or an existing class in an existing room, so no new map:

| # | Column | Mark | Where | Act | Payout |
|---|---|---|---|---|---|
| 1 | Hutt | Ponda Baba and Dr. Evazan: "the death sentence on twelve systems" is a bounty by definition. A double battle in the cantina's back booth (they are regulars already). | Cantina | 2 | 1,500 credits |
| 2 | Alliance | The cartel thug who robbed the Organa engineer in Act 1, hiding in the Tusken Ruins. | Tusken Ruins | 2 | a GREAT POD × 5 |
| 3 | Hutt | A Trandoshan slaver (BOUNTYHUNTER class) on the Route 109 beach, among the WOOKIEE CUB trainers, which explains why. | Route 109 | 2 | 2,000 credits |
| 4 | Alliance | The smuggler captain of the Tibanna Refinery (Lobot's side job already clears his crew; the captain comes back for the bounty). | Tibanna Refinery | 5 | a MAX REVIVE |
| 5 | Hutt | A deserter from the Mining Facility garrison (a STORMTROOPER class trainer) hiding on Ashen Pass. Jabba wants the Empire's gratitude. | Ashen Pass | 5 | 3,000 credits |
| 6 | Alliance | Cad Bane (section 1 swap) at the Grand Arena, post-game: the one mark who hunts back. | Grand Arena lounge | 8 | a LUCKY EGG |

Each mark is a trainer in its band (no balance change: payouts use existing trainer classes, prize items are
existing items with no new power). Taking a puck sets a flag that shows the mark; beating the mark sets a second
flag and the board pays (`addmoney` or `giveitem`). Twelve flags is too many for the unused list, so the pucks are
one var: `VAR_UNUSED_0x409D` as the bounty state (bits are awkward in scripts, so it is a counter: 0 none taken,
then the puck number taken and +10 when claimed; one special of eight lines, or plain `compare` chains).

**The player's own poster.** The board's last puck is the player, posted by the Hutt Cartel, and it rises with
Boba Fett's hunt var (`var:unused-0x404e`): "WANTED: KAEL. 5,000 credits. / Posted by the Hutt Cartel." at
stage 0, then 10,000, 25,000, 50,000, and "CANCELLED" after the finale. One sign script with five `compare`
branches. Cheap, and it is the single best joke the board can tell.

**Cost.** Cheap. Six trainer placements (existing classes and sprites), one var, one `MULTI_` list, about 150
script lines across seven maps, roughly 30 text rows. No C beyond the optional eight-line special.

### 4.2 The light / dark paths

The owner decided this feature. Below is the full design: the score, how it moves, where it locks, what it
changes, what it never changes, how the player sees it, the film echoes, the full cost, the risks, and three
stages. The guiding rule: **the dark path is Han's path, not a villain's.** Pragmatic over selfless, paid over
thanked, Vader's offer heard rather than refused. A child can play either side.

#### The score

| Item | Design |
|---|---|
| Storage | One var, `VAR_UNUSED_0x409B` → `VAR_ALIGNMENT`. Vars live in `gSaveBlock1Ptr->vars` (`include/global.h`), so there is no save layout change and old saves keep working. |
| Range | 0 to 200. New game sets 100 (one `setvar` in `EventScript_ResetAllMapFlags`, `data/scripts/new_game.inc`). |
| Bands | LIGHT at 140 and above. DARK at 60 and below. BALANCED between. A pure player reaches a band in Act 5, a mixed player stays balanced. |
| Moving it | Only by one-shot events: story choices, side errands, bounty pucks, and the two Force items (below). Every event fires once, so the score cannot be farmed. |
| Clamping | Two helper scripts in a new `data/scripts/alignment.inc`: `Common_EventScript_PathLight` and `Common_EventScript_PathDark`, each taking the amount in `VAR_0x8004`, with a `compare` guard before `subvar` (a u16 var wraps below zero) and a cap at 200. About forty lines, no C. |
| Decay | None. A choice stands. |
| Lock | At the Ilum temple door (`EverGrandeCity_PokemonLeague_1F_EventScript_DoorGuard`). The score is read once, one of two flags is set (`FLAG_UNUSED_0x039` → `FLAG_PATH_LIGHT`, `0x03A` → `FLAG_PATH_DARK`; neither set means balanced), and the score stops moving. The ending and the stage 3 evolutions read the flags, never the var. |
| Force items | Using a KYBER CRYSTAL moves +3 light, a SITH SHARD +3 dark, once per use. Both are sold at Pirin for 2,100, so a player can buy a band for about 28,000 credits: that is a choice too, and it is what the items are for. One `VarSet` line each in `ItemUseOutOfBattle_EvolutionStone` (`src/item_use.c`) or in the evolution callback (`src/party_menu.c`). Optional in stage 1; recommended in stage 2. |

#### How it is earned: the choice points

Thirteen, all inside scripts that already run exactly once (so no new flag per choice), all with `yesnobox` or
a two-item `multichoice`, all with the same outcome for the story. The B button is "no", which is never the
dark answer, so a player who skips through is balanced, not dark.

| # | Where | Act | The choice (prompt fits 208 px) | Light | Dark |
|---|---|---|---|---|---|
| 1 | Jundland Wastes, the robbed Organa engineer | 1 | Return every part, or keep one for yourself. | +10 | +10 |
| 2 | Ben's Hut, Obi-Wan | 1 | "Will you learn the ways of the Force?" / "I'd rather have a good blaster." | +5 | +5 |
| 3 | Beggar's Canyon, the thug after Chewie's rescue | 1 | Let him go, or take his credits (a payout in the Act 1 band). | +5 | +5 |
| 4 | The Cantina, after Greedo | 2 | "Tell Jabba I'm not for sale." / "Tell Jabba I'm for hire." | +5 | +5 |
| 5 | Jabba's Palace, the rancor keeper | 3 | Comfort him, or mock him (Return of the Jedi's weeping keeper). | +5 | +5 |
| 6 | Mustafar Peak, after Vader's first battle | 3 | "Join me. It is your destiny." Refuse, or listen. Vader leaves either way. | +10 | +10 |
| 7 | The Mining Facility, the SITH SHARD on the body | 3 | Leave it, or take it (it is still sold at Pirin). | +5 | +5 |
| 8 | Endor Station, the captured grunt | 4 | Hand him to the Ewoks, or claim Bossk's bounty on him. | +5 | +5 |
| 9 | The Hutt Hideout, Jabba beaten | 5 | "Work for me." Refuse, or accept (nothing follows; Jabba is beaten). | +10 | +10 |
| 10 | Jedha summit, after the BLUE KYBER is taken | 5 | Give your crystal to the temple, or take the officer's bled shard. | +10 | +10 |
| 11 | Fortress Vader, after the battle | 5 | "I am altering the deal. / Pray I don't alter it any further." Walk out, or ask the terms. | +10 | +10 |
| 12 | Yavin 4 Launch Tower, after the tag battle | 5 | Leia: stay with the Alliance, or "I work alone." | +5 | +5 |
| 13 | Cave of Evil, Obi-Wan at the mouth | 6 | "Your weapons, you will not need them." Leave them, or keep them. The cave is the same. | +5 | +5 |

Plus the one-shot side content, hooked into reward scripts that already exist (one line each):

| Source | Light | Dark |
|---|---|---|
| The six helping errands (Rwookrrorro chieftain, Chirrut, the Hoth scout, Cody, Lobot, the Endor commando) | +5 each | – |
| Alliance bounty pucks (4.1) | +3 each | – |
| Hutt bounty pucks (4.1) | – | +3 each |
| KYBER CRYSTAL / SITH SHARD used (stage 2) | +3 | +3 |

Reach: a player who always answers one way has 90 from the story, 30 from errands, and 9 from pucks, so 140 is
reached in Act 5 without the items. A player who splits stays within 80 to 120.

#### What changes

| Stage | Change | Where it lives |
|---|---|---|
| 1 | Flavour lines by band: the Bacta Center nurse, Yoda at the arena door, Obi-Wan at the Cave of Evil and Ben's Hut, Vader at Fortress Vader, the kyber trader in NiJedha, the Bendu on Atollon, Han on the liner. Each is `compare VAR_ALIGNMENT` and a second `msgbox`. | The map scripts named; `data/scripts/pkmn_center_nurse.inc` |
| 2 | Side events and rewards by band, items only: the Gathering at the Ilum door (a KYBER CRYSTAL from Yoda or a SITH SHARD from Obi-Wan's warning), Vader's gift at the Fortress (a SITH SHARD, dark only), Chirrut's blessing (a KYBER CRYSTAL, light only), a Bendu line for the balanced player that no one else hears. The trainer card line and the StarNAV line (below). | Four map scripts; `src/trainer_card.c`; `src/match_call.c` |
| 3 | The three light / dark lines evolve by level on the player's path, without the stone: AURADANCER → AURAREAVER on dark, KATHPUP → KATHWARDEN and ECHOWISP → WHILLGUARD on light. The stones keep working, so nobody is locked out. Two endings: the Champions Room and the medal ceremony say different things; the Hall of Fame scene is the same. | `include/constants/pokemon.h` (`EVO_LEVEL_LIGHT` 16, `EVO_LEVEL_DARK` 17), `src/pokemon.c` `GetEvolutionTargetSpecies` (two cases, about twelve lines), `src/data/pokemon/evolution.h` (one entry each; `EVOS_PER_MON` is 5 and each line uses 2); `data/maps/EverGrandeCity_ChampionsRoom/scripts.inc` |

#### What never changes

The arena ladder and every shard, every hyperlane unlock, the HMs, the Four Trials, Boba Fett's hunt, every
wild table, every trainer party, every level band, the Grand Arena. No door is ever closed by the score. The
paths split only inside a scene and rejoin before the player can walk:

| Split | Rejoin |
|---|---|
| Ben's Hut (Act 1) | The hut's door. |
| The Cantina (Act 2) | Greedo's booth. |
| Mustafar Peak, Vader's offer (Act 3) | Vader's shuttle leaves; the Pirin arena is next for everyone. |
| The Mining Facility (Act 3) | The shard is in the shop either way. |
| Endor Station, the Hideout, Jedha, Fortress Vader, the Launch Tower (Acts 4 and 5) | The same shard, the same shuttle, the same tag battle. |
| The Cave of Evil (Act 6) | The cave. |
| The Ilum door (Act 7): the lock | The Four Trials and Obi-Wan are the same fight; the ending text differs. |

#### How the player sees it

The var is hidden; the player sees a word, never a number.

| Where | What | Cost |
|---|---|---|
| Trainer card, back, row 1 | Row 1 is LINK BATTLES, which reads 0 for nearly every player of a hack. It becomes PATH: LIGHT / DARK / BALANCED. `PrintStatOnBackOfCard(1, …)` in `src/trainer_card.c`; the band is carried in the card struct's link-battle field so shared cards still work. About fifteen lines of C and one string. | Medium (small C) |
| Bacta Center | After the heal, one extra line by band: "The Force is strong with you." (light), "You look tired. Rest." *(new)* (dark), nothing (balanced). `Common_EventScript_PkmnCenterNurse`. | Cheap |
| An NPC who reads it | The kyber trader in NiJedha holds the player's crystal: "Your crystal sings. It is yours." *(new)* / "Your crystal has gone dark." *(new)* / "Not yet chosen." *(new)*. The Bendu says the same in his own words post-game. | Cheap |
| StarNAV | The Match Call: Obi-Wan's and Luke's general line picks by band. `GetGeneralMatchCallText` in `src/match_call.c` chooses from per-trainer text tables, so this is about thirty lines of C and data. Stage 2. | Medium |
| The Continue box | Could show PATH beside the shards (`gText_ContinueMenuBadges`, `src/main_menu.c`). Not proposed: the box is full and shards matter more. | – |

#### Film echoes

From `quotes.csv`, cut to lines of 208 px or less (measured), spoken by the character who said them or a stand-in
the story already has. *(new)* lines are written for the game.

| Speaker | Where | Band | Lines |
|---|---|---|---|
| Yoda | Dagobah arena, before the battle | light | "The Force is strong with you." *(Palpatine's words in the film; Yoda's here)* |
| Yoda | Dagobah arena | dark | "Fear is the path to the dark side." |
| Yoda | Dagobah arena | balanced | "Always in motion is the future." |
| Yoda | Raising the X-wing (3.3) | any | "Do. Or do not. / There is no try." |
| Yoda | The Ilum door, at the lock | light | "A Jedi uses the Force for knowledge / and defense, never for attack." |
| Yoda | The Ilum door | dark | "Once you start down the dark path, / forever will it dominate your destiny." |
| Yoda | The Ilum door | balanced | "Difficult to see." *(cut from the same line)* |
| Obi-Wan | Cave of Evil | any | "Only what you take with you." |
| Obi-Wan | Ben's Hut, the choice | – | "Stretch out with your feelings." |
| Obi-Wan | The Champions Room, light ending | light | "Remember, the Force will be / with you... always." |
| Obi-Wan | The Champions Room, dark ending | dark | "If you strike me down, I shall become / more powerful than you can / possibly imagine." *(he loses the fight either way)* |
| Vader | Mustafar Peak, the offer | – | "Join me. It is your destiny." |
| Vader | Fortress Vader, dark | dark | "Good. Use your aggressive feelings. / Let the hate flow through you." *(the Emperor's words; Vader repeats his master)* |
| Vader | Fortress Vader, light | light | "I find your lack of faith disturbing." |
| Vader | Fortress Vader, the second offer | – | "I am altering the deal. / Pray I don't alter it any further." |
| Vader | The Launch Tower, after the tag battle, light | light | "Obi-Wan has taught you well." |
| Han | The Cantina choice, dark answer | dark | "Hokey religions and ancient weapons / are no match for a good blaster / at your side, kid." |
| Han | The liner, any | any | "Great, kid! Don't get cocky." |
| Luke | The Ilum rival battle, light | light | "I'll never turn to the dark side." |
| Luke | The Ilum rival battle, dark | dark | "Your overconfidence is your weakness." |
| Dooku's holocron | Mustafar (`net:relic-dooku`) | dark | "Twice the pride, double the fall." |
| Palpatine | The hologram on the Death Star command deck (`net:character-palpatine`) | dark | "So be it... Jedi." / "Your faith in your friends is yours." |
| Boba Fett | Any stage, any | any | "He's no good to me dead." |
| Jar Jar | The traveller, any | any | "How wude." |
| Ackbar | Yavin 4 hangar | any | "It's a trap!" |

Thirty-six lines; the widest is 200 px.

#### Full cost

| Item | Stage | Where | Size |
|---|---|---|---|
| The var, its name and its start value | 1 | `include/constants/vars.h` (rename), `data/scripts/new_game.inc` | 2 lines |
| Helper scripts with clamps | 1 | `data/scripts/alignment.inc` (new) | ~40 lines asm |
| 13 choice points | 1 | the 13 map `scripts.inc` files above; 2 or 3 `MULTI_` lists in `src/data/script_menu.h` | ~260 lines asm |
| Side-errand hooks | 1 | 6 existing reward scripts | 6 lines |
| Flavour readers | 1 | `pkmn_center_nurse.inc` + 7 map scripts | ~80 lines asm |
| Text rows | 1 | `texts.csv`: prompts, two answers, two replies per choice, the flavour lines | ~70 rows |
| Trainer card row | 2 | `src/trainer_card.c`, `src/strings.c` | ~15 lines C |
| StarNAV line | 2 | `src/match_call.c` | ~30 lines C and data |
| Force item hook | 2 | `src/item_use.c` or `src/party_menu.c` | 2 lines C |
| Band-gated rewards | 2 | 4 map scripts, items only | ~60 lines asm, ~12 rows |
| The lock and its flags | 3 | `include/constants/flags.h` (2 renames), `EverGrandeCity_PokemonLeague_1F/scripts.inc` | ~20 lines asm |
| Evolutions | 3 | `include/constants/pokemon.h`, `src/pokemon.c`, `src/data/pokemon/evolution.h` | ~15 lines C, 3 table entries |
| Endings | 3 | `EverGrandeCity_ChampionsRoom/scripts.inc`; the medal ceremony text; optional one credits page in `src/data/credits.h` and `src/credits.c` | ~40 lines asm, ~10 rows; credits Medium |
| Save data | – | none: a var is always saved | 0 |
| Wiki | 1 | `NET_NEW_DESIGNS.md` slot table (one var, two flags), `net_new.csv` rows, `texts.csv` | – |

Stage 1 is about 400 script lines, 70 text rows and no C at all. Stage 2 is under 50 lines of C. Stage 3 is 15
lines of C plus text. The whole feature uses one var and two flags from the unused list (and one more var for the
bounty board), leaving 25 unused flags and 16 unused vars free (counted in `../game/include/constants/`).

**Testing plan.** `tools/play-tester` (headless mGBA, savestates, `E.setFlag`): add a `setVar` helper (about ten
lines of Lua reading the var's address from the symbol file; story vars are "not tried" in its README and this
is the first use). Then three savestates at the Ilum door, one per band, and a check matrix: every reader (the
nurse, the trader, the card, Yoda, Obi-Wan, Vader, the evolutions, the ending) times three bands is about
twenty-four checks, scripted. Regression: play the main path once per band from a savestate at each act's
start and confirm every shard, hyperlane and HM is reached at the same point. Two full runs, not three, since
balanced is the vanilla path.

#### Risk

1. **Choice fatigue.** Thirteen prompts over seven acts is one every half hour. Never more, and never on the
   critical path; a player who presses B is balanced.
2. **Farming.** Only the two items repeat, and they cost 2,100 each. Acceptable; it is the shop's purpose.
3. **Lock-out.** None: the stones still evolve the three lines on any path, and no reward is a power.
4. **Width.** Every proposed line was measured; the port tool's `overflow_risk` check catches any rewrite.
5. **Tone.** The dark answers are Han's, never cruelty. The owner should read the thirteen prompts before
   stage 1 is scripted; it is the one place where a judgement call shapes the player's path.
6. **Old saves.** A var not yet set reads 0, which is dark. The helper scripts and readers treat 0 as "unset:
   set to 100 first" (two lines), so a save from before the feature is balanced.

#### Stages

1. **Score and flavour.** The var, the helpers, the thirteen choices, the errand hooks, the nurse, the trader,
   Yoda, Obi-Wan, Vader. Cheap. Playable in one session of script work.
2. **Side events and rewards.** The Gathering, Vader's and Chirrut's gifts, the Bendu, the bounty columns, the
   items hook, the trainer card row, the StarNAV line. Cheap plus two small C changes.
3. **Evolutions and endings.** The lock, the two level evolutions, the two endings, the optional credits page.
   Medium.

### 4.3 What is not needed

- **Reputation.** The owner asked whether a reputation system is needed beside the score. No: the score *is*
  the reputation, read in words by the trader, the nurse and the card, and Boba's hunt var already tracks the
  player's notoriety for the poster. A second number would split one idea in two.
- **A ship you own.** Every hangar already has "Player's ship" and a StarNAV console; the X-wing (3.3) gives
  that ship a face and a story. No ship menu, no upgrades, no fuel: Expensive and the films do not do it either.
- **Day and night.** The binary sunset wants it; the engine has no clock use in the overworld, so it stays a
  one-off palette moment (3.4).

### 4.4 Feasibility, every idea

| Idea | Section | Cost | Files |
|---|---|---|---|
| The 23 ride moments | 3.2 | Cheap | hangar `scripts.inc` per hyperlane; `texts.csv` |
| Nien Nunb flies the Sullust transport | 3.2 | Cheap | `hangar-tatooine-sullust` script; `mapping/people.csv` |
| Cloud car | 3.2 | Cheap (1 art row) | `mapping/world_art.csv` |
| Tantive IV and Antilles | 3.2 | Cheap / Medium | hangar scripts; one interior yaml |
| The X-wing sink and raise | 3.3 | Medium | `dagobah-hangar` scripts; one object sprite; `world_art.csv` |
| Han's Falcon for the asteroid run | 3.2 | Cheap | `dagobah-hangar` script; the Falcon cabin room |
| The sail barge and the Sarlacc | 3.3 | Medium | `jabbas-palace-barge-dock` script; one fixed battle; one flag |
| The escape pod from the Death Star | 3.3 | Cheap | deck 5 script |
| Graves, krayt call, Han and Greedo's booth, Yoda's pod, the high ground, Vader's chamber, the net, the trophy, the dinner, the patrol, Y-wings, Cell 2187, the briefing table, the Gathering | 3.4 | Cheap each | one map script and 1 to 3 rows each |
| The binary sunset (sky strip) | 3.4 | Cheap | `terrain.csv` |
| The WAMPA fixed battle | 3.4 | Medium | Wampa Cave script |
| The probe droid | 3.4 | Medium | one object sprite; Hoth tundra script |
| The trash compactor | 3.4 | Medium | one room; deck 2 and 3 scripts; one fixed battle |
| AT-AT, Slave I, Y-wing | 3.5 | Cheap (1 art row each) | `world_art.csv` |
| GUNDARK rename | 3.5 | Cheap | `mapping/species.csv` |
| The bounty board and the poster | 4.1 | Cheap | cantina script; 6 trainer placements; 1 var; 1 `MULTI_` list |
| Light / dark stage 1 | 4.2 | Cheap | 13 map scripts; `alignment.inc`; `new_game.inc`; `texts.csv` |
| Light / dark stage 2 | 4.2 | Cheap + small C | `trainer_card.c`, `match_call.c`, `item_use.c`; 4 map scripts |
| Light / dark stage 3 | 4.2 | Medium | `pokemon.c`, `evolution.h`, `pokemon.h`; Champions Room; optional `credits.c` |
| Tauntaun riding, a ship menu, day and night | 3.4, 4.3 | Expensive | not proposed |

## 5. What to approve first

Ranked by payoff per cost. Each item is one approval; nothing lands before it.

1. **Light / dark stage 1** (4.2). Decided by the owner; Cheap; it touches every act. The thirteen prompts are
   the one thing to read first.
2. **Han's Falcon for the asteroid run** and **the X-wing in the bog** (3.2, 3.3). The two best film moments
   the game can add, and they fix the section 2 anachronism. Cheap plus one Medium.
3. **The three top swaps from section 1:** Aurra Sing → Cad Bane, Gardulla → Hondo, HURKAL → WICKET. Cheap;
   Wicket also carries the Ewok net (3.4).
4. **The bounty board and the WANTED poster** (4.1). Cheap; it makes the Cartel a presence instead of a word.
5. **The timeline fixes** (section 2, text only). Cheap; a fan notices every one of them.
6. **The 23 ride moments** (3.2). Cheap; the single biggest change in how the planets feel.
7. **The Tantive IV, Antilles, Dodonna, Mon Mothma and Ackbar** on the Bespin → Yavin ride and at the base
   (3.2, section 1). Cheap; Yavin 4 becomes the Rebellion's home instead of a town with a hangar.
8. **The sail barge and the Sarlacc** (3.3). Medium; the Dune Sea earns its tiles.
9. **The trash compactor and the escape pod** (3.3, 3.4). Cheap plus Medium; the Death Star post-game gets
   its two most famous rooms.
10. **Light / dark stage 2** (4.2): the Gathering, the gifts, the card, the StarNAV line.
11. **Missing ships** (3.5): AT-AT, Slave I, Y-wing, cloud car, the probe droid. Art rows; the pipeline does
    the rest.
12. **The small set pieces** (3.4): graves, the krayt call, the net, Yoda's pod, the trophy, the patrol, the
    WAMPA. Cheap each; approve as a batch.
13. **Light / dark stage 3** (4.2): evolutions and endings. Medium; last, because it needs stages 1 and 2
    tested.
14. **Optional:** the GUNDARK rename, the remaining section 1 swaps (JERJERROD, YULAREN, the racers,
    BO-KATAN), Tarkin and the series cast on the Death Star and Atollon.

Not recommended: Leia held in Jabba's Palace (the owner asked to consider it). At 2 BBY she is Bail Organa's
daughter and a senator-in-waiting; Jabba holding her would be an act of war against Alderaan, and the Return of
the Jedi beat is six years away. The cheaper version, the carbonite trophy and the barge, gives the palace its
menace without her. If the owner still wants it, it is Expensive: a new story event with its own flags, Leia's
walker in the throne room, and a rewrite of Act 2's Shadowlands delivery.
