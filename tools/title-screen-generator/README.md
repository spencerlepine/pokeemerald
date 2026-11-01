# title-screen-generator

Mockups for the STAR WARS: KYBER title screen (wiki rows `graphics/title_screen/*`, `graphics/intro/copyright.png`,
all `HUMAN-TODO` in `wiki/mapping/branding.csv`). Status: **DONE**. Shipped 2026-11-01 with `python3 ship.py` (picks listed at the top of ship.py).

    python3 mockups.py OUT_DIR

- `gba_title.py` composes the screen the way `src/title_screen.c` does (BG0 creature, BG1 sky blended 6/16 over it,
  BG2 logo, banner/press-start sprites). `python3 gba_title.py` renders the vanilla screen as a check.
- `glyphs.py` original block lettering (logo, banner) and a 6px caps font (copyright lines).
- `logo.py`, `banner.py`, `backdrop.py`, `copyright.py`: three variants each.

Final pieces: `sw_logo.py` (stacked STAR / WARS, Kyber Gold from wiki/bible/PALETTE.md, one-line KYBER VERSION banner),
`bg_round.py` (Emerald's gradient bands recoloured, Exogorth silhouettes, cloud/nebula layers). `ship.py` writes
pokemon_logo.png/.bin/.pal, emerald_version.png, rayquaza.png/.bin, rayquaza_and_clouds.pal and the banner position
defines in src/title_screen.c; clouds.png/.bin stay Emerald's (recoloured by the palette). Review scripts: `round3.py`, `bg_review.py`.
Round 1 (`mockups.py`, `logo.py`, `banner.py`, `backdrop.py`) was rejected but kept for reference.
