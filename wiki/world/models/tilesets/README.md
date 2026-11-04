# Model tilesets (greybox)

One sheet per planet: the unique 8x8 tiles of every world-art model drawn
for it, all variants, 128 px wide like a game `tiles.png`. Made by `python3 -m worldart scenery --tilesets`
in `tools/world-art`. A tileset holds 512 tiles, shared with the terrain and buildings. The game's limit is
per loaded map, not per planet: at import each map's secondary tileset gets only the pieces it shows
(see `wiki/bible/WORLD_ART.md`, Tile budget).

| Planet | Models | Unique tiles |
|---|---|---|
| ASTEROID FIELD | 1 | 107 |
| ATOLLON | 2 | 122 |
| BESPIN | 8 | 835 |
| DAGOBAH | 9 | 589 |
| DEATH STAR | 7 | 560 |
| ENDOR | 15 | 810 |
| FELUCIA | 4 | 413 |
| GRAND ARENA | 6 | 806 |
| HOTH | 8 | 729 |
| ILUM | 7 | 729 |
| JEDHA | 6 | 436 |
| KAMINO | 9 | 762 |
| KASHYYYK | 14 | 1016 |
| MORTIS | 2 | 172 |
| MUSTAFAR | 7 | 740 |
| SHARED | 55 | 2754 |
| SULLUST | 12 | 754 |
| TATOOINE | 52 | 3976 |
| TYTHON | 2 | 78 |
| YAVIN 4 | 9 | 871 |
