# Working notes

## Decisions

- **Same ids as emerald-db.** Every row is keyed by the Emerald id; the Star Wars name lives in `sw_name` / `sw_title` and the proposed C constant in `sw_constant`. Net-new rows use `net:*` ids.
- **Generated output only in database/.** Hand-written input lives in `mapping/` and `bible/`.
- **Unchanged game data is not copied** (learnsets, parties, encounters, scripts, flags): join emerald-db by id. Only tables with Star Wars content are generated here.
- **Auto drafts for text.** `texts.csv` swaps every mapped name and glossary term (uppercase, whole word, longest first). The glossary wins over derived names; trainer-class names are not used in text (CHAMPION, LEADER, PSYCHIC are generic words in dialogue). Ambiguous terms are left alone and listed in `text_terms.csv`.
- **Plurals.** Emerald's POKéMON is singular and plural; COMPANION isn't. The build fixes the obvious cases ("COMPANIONS are", "all your COMPANIONS"); the rest is curated text work (C3).
- **Every image is PENDING_ART** because Step 5 redraws everything. Move animations default to KEEP_ANIM; only the renamed moves that want a Star Wars VFX are PENDING_ART.
- **Named characters are people, never creatures.** The player is one fixed character chosen at the start; there is no party member that is a story character. (Owner, 2026-10-31.)
- **Timeline frame: ~2 BBY**, starting on Tatooine (owner's primer). Dead-by-2-BBY prequel figures appear only as visions (the Four Trials), as Order 66 survivors (Kanan Jarrus, Obi-Wan), or in lore.

## Gotchas

- emerald-db's PR #1 is merged, but this session's checkout of emerald-db was on branch `claude/project-thread-vu8ith`; `origin/main` has the same data (commit 99e771c).
- Item shards (RED SHARD …) are renamed to RED CRYSTAL etc. so they never collide with arena SHARDS (badges).
- `species.csv` covers the 386 real species; the 25 `old-unown-*` placeholders, Unown letter forms and the Egg are KEEP by default.
- Kanto/Sevii region-map sections (FireRed leftovers) are KEEP; they are not reachable in Emerald.

## Open questions for the owner

- **Decided 2026-10-31:** COMPANION is the word for Pokémon (was CREATURE). Devon is HOUSE ORGANA, Alderaan's royal house; Bail Organa (Mr. Stone) heads it, its engineers make the COMLINK, ORGANA SCOPE and ORGANA PARTS.
- **Decided 2026-10-31 (decision card): swap for beasts.** All 48 sentient or named species slots now hold beasts or droids (applied from `mapping/proposals/sentient_swap.csv`). Jawas, Wookiees, Ewoks and the rest appear only as people.
- **Decided 2026-10-31 (decision cards):** Gym 7 is Kanan Jarrus & Ezra Bridger (master and Padawan, both alive in 2 BBY). Arena leader 1 is Biggs Darklighter (Rock, Bestine), arena leader 4 is Sabine Wren (Fire, Pirin). The owner also asked for a canon-creature pass on invented species names.
- Many national-dex creatures are `original` names; happy to swap any for canon creatures you prefer.

## Text drafting: control codes

`build.py` matches terms whole-word. Emerald's `\n`, `\l`, `\p` put a letter right before the next word, so the lookbehind also accepts a preceding control code. Before this fix about 190 texts silently kept Pokémon terms.

## Berries

All berries are `<NAME> FRUIT` (max 14 chars). Canon where Star Wars has a fruit (jogan, muja, pallie, shuura, blba, hubba), original names otherwise. Dialogue uses FRUIT for BERRY and BERRIES (FRUIT BLENDER, FRUIT MASTER). Effects unchanged.

## Text overflow check (pixel based)

`overflow_risk` now measures each line in pixels with Emerald's normal font (glyph widths from
`pokeemerald/src/fonts.c` through `charmap.txt`, saved in `tools/font_widths.json`). The field
text box is 208 px: no Emerald script line without placeholders is wider. A line is flagged when
it is wider than max(208, the widest line of the original text). Placeholders count as
{PLAYER}/{RIVAL} 42 px, {STR_VAR_n} 60 px, {KUN} 0. This replaced a character count (36) and cut
the flagged texts from 466 to about 130.

## Glossary additions (round 2)

Plural and compound forms that the single-word rules got wrong: POKé BALLS, POKéMON MART(S),
POKéMON CENTERS, CONTESTS, GYMS, GYM LEADERS, POKéMON NEWS (HOLONET NEWS), POKéMON WIRELESS CLUB
(HOLONET CLUB), and the article fix "a GYM" → "an ARENA". Item names also get an automatic plural
(POTIONS → BACTA SPRAYS).

## Dialogue conventions (C3)

COMPANIONS for plural POKéMON; tall grass → scrub or dunes on Tatooine; PC → terminal (storage is
"over the HoloNet"); TV → HoloNet; clock → chrono; sea → water or stars on desert worlds. Luke is
restless and reckless, not frail; Owen and Beru are his uncle and aunt.

## Water on desert worlds (open question)

Emerald's Tatooine maps (Mos Eisley, Routes 103/104/109/110) have sea tiles, and SURF works there.
Curated text keeps it neutral ("the water", "deep-water expedition"). Option for Step 5: draw those
tiles as the DUNE SEA and theme SURF on Tatooine as sand-skimming (art only; mechanics unchanged).
Not decided; needs the owner.

## Jabba's and Vader's motives

Jabba (Archie) wants to drown the dry worlds into swamps "fit for a HUTT" (SANDO = sea titan).
Vader (Maxie) should mirror it with land: an Imperial plan to dry out worlds for industry and
garrisons (GREATKRAYT = land titan). Use this when curating the Empire's lines.

## Sullust and Mustafar (C3c)

- Sabine Wren (PIRIN ARENA, Lavaridge) is female like Flannery; Flannery's grandfather stays her grandfather, a former keeper of the TRIALS OF ILUM.
- Vader's lines use his canon voice: "Impressive… Most impressive." on defeat; he withdraws saying the Force is strong with the player and names the BLUE KYBER as the next goal (Vader takes the BLUE KYBER at Jedha, Jabba the RED).
- Mt. Chimney's hot springs are "lava springs" on the peak; Lavaridge keeps hot springs (Sullust).
- Leia's Meteor Falls line: Emerald's source says SOOTOPOLIS SPACE CENTER (a typo in the original); written as the YAVIN 4 LAUNCH TOWER.
- Pair trainers ("JOHN & JAY") were hand-renamed, and `build.py` now swaps each member's speaker label ("JOHN:" → "JARO:") in dialogue.

## Endor (C3d)

- Chief Chirpa (Winona) is male. Bossk (Shelly) hisses and hunts trophies. Leia is female everywhere (some Emerald lines say "he" for Steven).
- Routes that lead off-world end at shuttle pads: Route 118 west sign reads HANGAR TO TATOOINE; Route 121's pier is the SHUTTLE PAD to JEDHA TEMPLE; the Safari Zone gate is the FELUCIA RESERVE SHUTTLE. Step 4 keeps the maps; only signs and dialogue change (the hangar rows in `net_new.csv` are the real gating).
- Plural rule round 3 in `build.py` (`PLURAL_ADJ`): type words and bare prepositions before COMPANION pluralize it.

## Bespin (C3e)

- Cloud City floats over a sea of clouds: Emerald's "sea" in Lilycove is the cloud sea, Wailmer (AIWHALET) swim in it, sailors are cloud-car pilots, the harbor is the STAR TIDAL landing platform.
- The Aqua Hideout is an old TIBANNA mine under the city. Boba Fett (Matt) guards it: short, professional lines, paid by Jabba.
- GAME FREAK's motel room stays (developer in-joke); GAME BOY ADVANCE → HOLOGAME. Link-cable and "Game Pak" system strings are left for C3i.

## Shared systems (C3i)

- PC is a TERMINAL everywhere (SOMEONE'S TERMINAL, TESS'S TERMINAL, {PLAYER}'s TERMINAL). The PC menu sizes to its longest entry.
- Wireless Adapter and Game Link cable are both the COMLINK.
- The `{PKMN}` glyph token becomes the plain word COMPANION (glossary), since there is no COMPANION glyph.
- ¥ stays as the money glyph; Step 5 can redraw it as a credits sign.
- Captain Han (Briney) handles the event-pass voyages from Cloud City.
- UI strings in fixed-size windows (menus, party, Datapad headers) are 6–48 px wider than the original in 68 cases (COMPANION is wider than {PKMN}; TERMINAL is wider than PC). The 208 px dialogue check does not catch these: they need a per-window check in C5 or a window resize in Step 5.
- `tools/curate_texts.py` REFLOW re-wraps overflowing dialogue paragraphs only; UI specs leave it off, because UI windows do not scroll.

## Datapad entries (C4)

- `mapping/datapad.csv`: one row per species with `sw_category` (max 11 characters) and `sw_datapad_text` (written unwrapped; the build wraps it to at most 4 lines of 224 px into `entities.datapad_text`, keeping Emerald's category in `emerald_dex_category`).
- Entries keep each creature's Emerald behaviour (moves, abilities, evolution hints) so the text matches what the creature does in battle. Height and weight are unchanged.
- The 48 sentient or named slots were swapped for beasts and droids (owner's decision, 2026-10-31), and each has its own entry (notes column: `beast swap`). Showcase-rival nicknames were regenerated from the new names.

## Canon-creature pass (owner's decision, 2026-10-31)

- 15 invented companions were renamed to canon Star Wars creatures where one fits the type and role: `mapping/proposals/canon_pass.csv` lists each change with its new datapad entry. Types, stats, abilities and evolutions are unchanged.
- Lines: Hawk-bat (TAILLOW, SWELLOW), Shyyyo bird (WINGULL, PELIPPER), Bogling (LOTAD), Oggdo (WOOPER, QUAGSIRE), Rawka (MURKROW), Ikopi (STANTLER), Puffer pig (SPOINK, GRUMPIG), Thala-siren (SEEL, DEWGONG), Mogu (MAKUHITA, HARIYAMA).
- The other invented names stay because no canon creature fits without breaking a line or a type (most canon creatures are already used). Nicknames, dolls and dialogue follow `species.csv` automatically.

## Habitats and net-new (E2, E3)

- Wild encounter tables stay exactly as in Emerald. `tools/habitats.py` explains every companion found off its home world (migrant, reserve, widespread, sea, story); `species.habitat_note` is superseded by it.
- Net-new content designs live in `progress/NET_NEW_DESIGNS.md`. New flags/vars use only Emerald's unused slots (`flag:unused-0x020`-`0x025`, `var:unused-0x404e`, `0x4083`, `0x408b`).
