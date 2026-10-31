# Pokémon Emerald - Star Wars Adaptation

![Game Screenshot](TODO.png)

## Project Structure

| Path | Contents |
| --- | --- |
| [`game/`](game/) | C game source code (decompiled by [pret/pokeemerald](https://github.com/pret/pokeemerald)). The wiki and tools never import it; content is ported in by hand. |
| [`wiki/`](wiki/) | The Star Wars adaptation as `.csv` tables: every creature, character, planet, item, move, line of dialogue, story event, image, VFX, song, sound effect and cry, mapped to its Star Wars version and pointing back at `game/`. Start at [`wiki/README.md`](wiki/README.md). |
| [`tools/`](tools/) | One tool per asset group for generating new game assets, indexed in [`tools/INDEX.md`](tools/INDEX.md). |
| [`.github/`](.github/) | CI workflows to build/test/lint |

## Wiki: where to look

| File | What it is |
| --- | --- |
| [`wiki/bible/STORY.md`](wiki/bible/STORY.md) | The story: planets, factions, cast, acts. |
| [`wiki/bible/NET_NEW_DESIGNS.md`](wiki/bible/NET_NEW_DESIGNS.md) | Designs for content with no Emerald counterpart. |
| [`wiki/database/game_port.csv`](wiki/database/game_port.csv) | The port checklist: one row per change to make in `game/` (file, line, wiring, dependencies, status). |
| [`wiki/database/swap_map.csv`](wiki/database/swap_map.csv) | Every Emerald entity with its Star Wars name and C constant. |
| [`wiki/database/texts.csv`](wiki/database/texts.csv) | Every line of game text with its Star Wars version. |
| [`wiki/database/pending_art.csv`](wiki/database/pending_art.csv) | Every image, animation and VFX with its Star Wars subject and status. `todo` `HUMAN-TODO` marks what you replace by hand (logo, title screen, cutscenes, branded menus). |
| [`wiki/database/pending_audio.csv`](wiki/database/pending_audio.csv) | Every song, sound effect and cry with its brief and status. |
| [`wiki/database/`](wiki/database/) | The other generated tables (entities, timeline, net-new, area progression, habitats). |
| [`wiki/mapping/`](wiki/mapping/) | The hand-written decisions the database is built from ([`mapping/README.md`](wiki/mapping/README.md)). |
| [`wiki/tools/`](wiki/tools/) | `build.py` (mapping → database) and `scan_game_assets.py` (inventory of `game/` sound and VFX). |

## Tools

| Tool | Status |
| --- | --- |
| [`tools/play-tester/`](tools/play-tester/) | DONE: headless mGBA play-testing ([README](tools/play-tester/README.md)) |
| [`tools/sprite-creature-generator/`](tools/sprite-creature-generator/TODO.md), [`sprite-icon-generator/`](tools/sprite-icon-generator/TODO.md), [`sprite-walker-generator/`](tools/sprite-walker-generator/TODO.md), [`sprite-trainer-generator/`](tools/sprite-trainer-generator/TODO.md), [`sprite-trainer-back-generator/`](tools/sprite-trainer-back-generator/TODO.md) | TODO |
| [`tools/tile-generator/`](tools/tile-generator/TODO.md), [`vfx-generator/`](tools/vfx-generator/TODO.md), [`ui-skin-generator/`](tools/ui-skin-generator/TODO.md), [`font-generator/`](tools/font-generator/TODO.md), [`cutscene-generator/`](tools/cutscene-generator/TODO.md) | TODO |
| [`tools/music-generator/`](tools/music-generator/TODO.md), [`sfx-generator/`](tools/sfx-generator/TODO.md), [`cry-generator/`](tools/cry-generator/TODO.md) | TODO |

Statuses, scope, art categories and order of work: [`tools/INDEX.md`](tools/INDEX.md).
