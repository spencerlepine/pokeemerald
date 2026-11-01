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
Palette: the pieces are in `kyber-gold` (`../../wiki/bible/PALETTE.md`); `ship.py` ends by running the shared palette gate
(`../palette-enforcer`, rules in `../PALETTES.md`) on everything it wrote and exits non-zero on a hardware error.
Round 1 (`mockups.py`, `logo.py`, `banner.py`, `backdrop.py`) was rejected but kept for reference.

Boot copyright screen: `python3 boot_copyright.py [--preview OUT.png]` rewrites `game/graphics/intro/copyright.png/.bin`.
It keeps the vanilla ©Pokémon and ©Nintendo rows, drops Creatures and GAME FREAK, and adds `©1977-2005 STAR WARS` and
`©&™ 2005 Lucasfilm Ltd.` in the vanilla thin font (glyphs copied from the Creatures/GAME FREAK lines; missing letters
drawn to match). Text is set by the constants at the top. Idempotent.

## Character collage (shipped 2026-11-01)

The Exogorth (BG0) is replaced by a collage of Rebels (left: Obi-Wan, Kael, Leia, Mira) and the Empire (right: a
stormtrooper, Vader, Boba Fett) standing behind the logo, in front of the clouds, with a dark foreground ridge over
their feet. Owner's pick: round 2 `v6` in `collage/round2.py`, with Kael's cape recoloured from blue to tan
(`collage/final/kael.png`). Figures are new-pose Civitai takes (`title_*` jobs in
`../sprite-trainer-generator/civitai/jobs.json`), never the battle pics; the back row is darkened toward the backdrop.

    cd collage && python3 ship_collage.py [PREVIEW_DIR]

writes `game/graphics/title_screen/collage/<figure>.png/.pal` (OBJ tile strips + one palette each, OBJ slots 1-7),
`game/graphics/title_screen/rayquaza.png/.bin` (BG0 = the ridge only, priority 1; file names kept so the build rules stay)
and `game/src/data/title_screen_collage.h` (subsprite tables, slide table), then renders the screen and the slide-in back
from those game files and runs the palette gate. `src/title_screen.c` creates one Sprite per figure (OBJ priority 2) when
the clouds come up; they slide in from their side (back row first, ease-out over 32 frames) and slide back out when the
first-boot crawl starts, while the ridge sinks. Budget: 345 OBJ tiles, 35 OAM entries, 36 BG0 tiles.

Running `ship.py` again would overwrite `rayquaza.png/.bin` with the old gradient + creature: run `collage/ship_collage.py` after it.
The crawl now starts on the flat backdrop (BG0 has no gradient left for the crawl-out to copy).
Exploration scripts kept for reference: `collage/blocking.py`, `compose.py`, `round2.py`, `creature_init.py`.
