# Fan critique: does this game feel like Star Wars?

A critical read of the whole game as a Star Wars fan and as a game critic (owner's brief, 2026-11-03).
Nothing in this file changes a wiki row or the game by itself. An item lands only once the owner approves
it; then it goes into `STORY.md` and `NET_NEW_DESIGNS.md`, then the mapping rows, then a rebuild.

Inputs: the wiki (`mapping/`, `database/`, `world/GUIDE.md`, the bible), the owner's
[starwars-db](https://github.com/spencerlepine/starwars-db) (`../starwars-db/database`, 594 entities,
5,513 lines of film dialogue, 727 scenes), and `../game` for feasibility only.

Written piece by piece. Sections 1 and 2 are Part 1 (characters). Sections 3 to 5 follow.

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

Written in the next piece.

## 4. Side content and the light / dark paths

Written in the next piece.

## 5. What to approve first

Written with sections 3 and 4.
