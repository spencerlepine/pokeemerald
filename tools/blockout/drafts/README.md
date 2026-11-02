# Blockout draft scripts

The scripts that laid out every area in `wiki/world/`. The area files are the source of truth; these show how
each was made and can be re-run to rebuild an area after a tool change. Each script is idempotent
(`retheme` re-imports the vanilla map first; hand-drawn areas start from a fresh canvas). `travel:` links and
planet layout positions survive a re-import.

Run from anywhere, in this order (later scripts fix links that earlier ones cut):

    python3 tools/blockout/drafts/<script>.py

| Order | Script | Areas |
|---|---|---|
| 1 | `tosche.py`, `tat_towns.py`, `tat_towns2.py` | Tatooine towns |
| 2 | `tat_routes.py`, `tat_new.py`, `tat_caves.py` | Tatooine routes, new areas (Ben's hut, Jabba's palace), caves |
| 3 | `kashyyyk.py`, `sullust.py` | Kashyyyk; Sullust and Mustafar |
| 4 | `endor_etc.py` | Endor, Bespin, Jedha, Yavin 4 |
| 5 | `frontier.py` | Hoth, Dagobah, Kamino, Ilum |
| 6 | `postgame.py` | Grand Arena, Felucia, Tython, Atollon, Mortis, Asteroid Spire, Altering Cave |
| 7 | `interiors.py` | New rooms, then kit notes on every vanilla interior still `TODO` |
| 8 | `deathstar.py` | Death Star construction site (post-game, net:death-star-site) |
| 9 | `links.py` | `travel:` links (ships, shuttles, tides, dives, scripted moves) and graph fixes |

Then, from `tools/blockout/`: `python3 -m blockout layout <PLANET>` for each planet (not FELUCIA: its six
zones keep vanilla's positions), and `python3 -m blockout world`, `index`, `guide`, `check`.

`common.py` holds the shared helpers (`retheme`, `drop_exit`, `unblock`).
