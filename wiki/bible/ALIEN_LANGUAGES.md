# Alien languages

Background NPCs who are aliens speak their own language some of the time. This file is the phrasebook: every
alien word in the game, what it means, and where it comes from, so a fan can check it. The lines themselves are
`mapping/texts/lang_01_alien_npcs.csv` (one row per text, its meaning in `notes`).

## Rules

- **Who.** Only background NPCs: no story character, no trainer, no arena leader, no shop or facility clerk.
  Named characters and everyone who battles speak Basic (English).
- **Which species.** Taken from the NPC's walker (the `sw_subject` of its sprite in `database/pending_art.csv`).
- **Only real words.** Every alien word is an attested word with a known meaning, or a known untranslated film
  line. Nothing is made up. A language with no attested phrases stays English.
- **Hints stay readable.** An NPC who gives a hint, an item or a rule says one alien line, then the hint in Basic.
  A pure flavour line can be alien only.
- **Wookiees can't speak Basic.** They understand it but can't make the sounds. So a Wookiee says Shyriiwook and
  the meaning follows in brackets, like a film subtitle: `Hrung?` then `(Everything starts with focus!)`.
- **Charset and width.** Only characters the game font already has (letters, `'`, `-`, `!`, `?`, `.`, `,`, `…`,
  brackets). Every line fits the 208 px text box (checked with `tools/font_widths.json`).

## By species

| Species (walker) | Language | Used |
|---|---|---|
| Jawa | Jawa trade talk, Jawaese | alien only |
| Rodian, Twi'lek, Weequay | Huttese, the trade tongue of the Outer Rim (Oola and Bib Fortuna speak it in Return of the Jedi) | one opener, then Basic |
| Wookiee, Wookiee cub | Shyriiwook | Shyriiwook, then the meaning in brackets |
| Ugnaught | Basic, with the Ugnaught custom of closing a decision with "I have spoken." | appended |
| Ewok (Bright Tree villagers, once `net:walker-ewok` replaces their sprite) | Ewokese | one opener |
| Sullustan, Quarren, Mon Calamari, Nautolan, Gamorrean | no usable attested phrases found | English |

The Gamorrean-looking CARTEL thugs keep English: their lines are story beats.

## Phrasebook

| Word | Language | Meaning | Source |
|---|---|---|---|
| Utinni! | Jawa trade talk | Hurry! Let us proceed! (also surprise) | Heard in A New Hope; Wookieepedia, Jawa Trade Talk |
| Mob un loo? | Jawa trade talk | What is the price? | Wookieepedia, Jawa Trade Talk |
| Mombay m'bwa | Jawa trade talk | That belongs to me. | same |
| Togo togu! | Jawa trade talk | Do not touch! | same |
| M'um m'aloo | Jawaese | Hello | Wookieepedia, Jawaese |
| Achuta | Huttese | Hello | Wermo's Guide to Huttese (dictionary) |
| Koona t'chuta? | Huttese | Going somewhere? | Greedo, A New Hope (subtitled "Going somewhere, Solo?") |
| Chut chut | Huttese | Excuse me; never mind | Wermo's Guide |
| Pateesa | Huttese | Friend | Wermo's Guide |
| Punchee | Huttese | Pal | Wermo's Guide (Episode I Racer) |
| Inkabunga! | Huttese | Amazing! | Wermo's Guide |
| Pankpa | Huttese | Spaceship | Wermo's Guide |
| Bedwana | Huttese | To buy | Wermo's Guide |
| Poodoo | Huttese | Fodder; rubbish; an exclamation | Sebulba, The Phantom Menace; Wookieepedia, Poodoo |
| Chess ko! | Huttese | Careful! (a warning) | Huttese barricade tape (canon); Wookieepedia, Huttese |
| Bo shuda! | Huttese | Jabba's exclamation, never translated | Return of the Jedi (George Lucas's line) |
| Wyaaaaaa | Shyriiwook | Hello | Wookieepedia, Shyriiwook |
| Hrung? | Shyriiwook | Ready? | same |
| Uma | Shyriiwook | Yes | same |
| Ruh gwyaaaag | Shyriiwook | I am a friend. | same |
| Roooarrgh ur roo. | Shyriiwook | I have a bad feeling about this. | same |
| Yyyuurrrrrrruuunghh! | Shyriiwook | Roughly: what the Hutt is going on in here? | same |
| Grrgaaggaa! | Shyriiwook | Thanks (gratitude) | same |
| Mmmmmmrrrrr. | Shyriiwook | Agreement | same |
| Awwwrrrrrrrr. | Shyriiwook | Neither agreement nor disagreement | same |
| Arrrgrrr? | Shyriiwook | A question | same |
| Grrrrrupmprrr! | Shyriiwook | Disgust, irritation | same |
| Grrrrafffffffffgrrr! | Shyriiwook | Panic | same |
| Grrrrrrrraaaaaarrrrph! | Shyriiwook | A roar with no known translation | same |
| Yaa-yaah! | Ewokese | Greetings! | Wookieepedia, Ewokese |
| Yub nub! | Ewokese | Hooray! Freedom! | Return of the Jedi (the celebration song) |
| Ee chee wa maa! | Ewokese | Wow! | Wookieepedia, Ewokese |
| I have spoken. | Ugnaught custom (in Basic) | The decision is final. | Kuiil, The Mandalorian |

Sources: Wookieepedia (read through its mirror, [starwars.archivum.wiki](https://starwars.archivum.wiki/article/huttese)),
[The Complete Wermo's Guide to Huttese](https://www.completewermosguide.com/huttese.html), a fan dictionary built
from the films, Ben Burtt's Galactic Phrase Book and the games. Wermo's words are Legends-era or fan-compiled;
the film lines are canon. The Shyriiwook and Ewokese lists are Wookieepedia's; most of their entries come from
Legends books and games.

## Not used, and why

- **Sullustese.** Nien Nunb's lines are real Kikuyu (or Haya) spoken by Kipsang Rotich; no Sullustese word list
  could be checked.
- **Mando'a.** Well documented (Karen Traviss; Sabine's lines in Rebels, "Legacy of Mandalore"), but no background
  NPC is a Mandalorian. Ready for one: `Su cuy'gar` (hello, "you're still alive"), `Elek` (yes), `Nayc` (no),
  `Vor entye` (thank you), `K'oyacyi!` (stay alive, cheers), `Ret'urcye mhi` (goodbye).
- **Ugnaught, Quarrenese, Ryl, Gamorrese.** No attested phrases with meanings, or only single Legends words.
