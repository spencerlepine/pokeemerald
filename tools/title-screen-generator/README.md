# title-screen-generator

Mockups for the STAR WARS: KYBER title screen (wiki rows `graphics/title_screen/*`, `graphics/intro/copyright.png`,
all `HUMAN-TODO` in `wiki/mapping/branding.csv`). Status: **IN-REVIEW** (owner picks one variant per piece).

    python3 mockups.py OUT_DIR

- `gba_title.py` composes the screen the way `src/title_screen.c` does (BG0 creature, BG1 sky blended 6/16 over it,
  BG2 logo, banner/press-start sprites). `python3 gba_title.py` renders the vanilla screen as a check.
- `glyphs.py` original block lettering (logo, banner) and a 6px caps font (copyright lines).
- `logo.py`, `banner.py`, `backdrop.py`, `copyright.py`: three variants each.

Not done yet (after the pick): convert the chosen pieces to game format (logo 8bpp tiles + `pokemon_logo.bin` + `.pal`,
creature/sky 4bpp tiles + `rayquaza.bin`/`clouds.bin` sharing one 16-colour palette, banner 16 colours, copyright strips),
and move the logo's BG2X offset in `src/title_screen.c` so the wider wordmark is centred.
