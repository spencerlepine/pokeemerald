# Pokémon Emerald - Star Wars Adaptation

![Game Screenshot](TODO.png)

**Agents and returning contributors: start at [`AGENTS.md`](AGENTS.md)** (rules, how work flows, and the wiki and tools indexes).

## Project Structure

| Path | Contents |
| --- | --- |
| [`game/`](game/) | C game source code (decompiled by [pret/pokeemerald](https://github.com/pret/pokeemerald)). The wiki and tools never import it; content is ported in by hand. |
| [`wiki/`](wiki/) | The Star Wars adaptation as `.csv` tables: every creature, character, planet, item, move, line of dialogue, story event, image, VFX, song, sound effect and cry, mapped to its Star Wars version and pointing back at `game/`. Start at [`wiki/README.md`](wiki/README.md). |
| [`tools/`](tools/) | One tool per asset group for generating new game assets. The list of tools and which ones still have work left (TODO) is in [`tools/README.md`](tools/README.md). |
| [`AGENTS.md`](AGENTS.md) | Notes for agents: standing rules, how work flows, and the wiki and tools indexes. `CLAUDE.md` just points to it. |
| [`.github/`](.github/) | CI workflows to build/test/lint |
