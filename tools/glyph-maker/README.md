# glyph-maker (temporary)

Draws the COMPANION ligature glyphs, the Star Wars version of Emerald's PkMn glyph, into the game fonts.
Emerald writes POKéMON's short form with two glyphs, PK (0x53) and MN (0x54): a tall capital with a second
capital set lower and to the right. The game font is the GBA's own 1-bit-style pixel font, not ASCII.
This tool draws COMPANION the same way in five glyphs (CO MP AN IO N; plural ends in NS) for every Latin font.

```sh
python3 glyph_maker.py preview   # out/: before_after_lines.png, before_after_fonts.png, glyph_cells.png
python3 glyph_maker.py install   # writes ../../game/graphics/fonts/latin_*.png, widths in src/fonts.c, charmap.txt
```

- Text uses `{COMPANION}` / `{COMPANIONS}` (charmap.txt). Installed 2026-11-03.
- Tweak at the top of `glyph_maker.py`: the letters (ASCII art, `#` = ink, TALL for normal/short/narrow and
  SMALL for the small fonts), the letter pairs per glyph, the slots and per-font placement. The shadow is added
  automatically. Re-run `preview`, then `install` (it is idempotent).
- Slots 0x37-0x3C are hiragana codes the English fonts leave blank. In the two small fonts those cells held
  kana, which the English game never shows; they are overwritten.
- `out/` is scratch (not committed).

## Aurebesh signs (`aurebesh.py`)

The ancient signs (Sealed Chamber, the three warden tombs) print in the Braille font. `aurebesh.py` redraws
each Braille cell as its Aurebesh letter: the cell for A becomes Aurek, and so on, plus the punctuation.
The cell numbers stay, so the sign texts (`.braille "..."` in `data/text/braille.inc`), puzzles and windows
work as before. Installed 2026-11-03.

```sh
python3 aurebesh.py preview   # out/: aurebesh_before_after.png, aurebesh_letters.png (letter next to its chart glyph)
python3 aurebesh.py install   # writes ../../game/graphics/fonts/braille.png (idempotent)
```

- Tweak the ASCII art at the top (`#` = ink, 8 wide and 9 tall). The shadow is added automatically.
- The letters follow the Aurebesh chart in `../sprite-creature-generator/civitai/refs/unown/`.
- "Before" is Emerald's Braille sheet redrawn from the dot numbers, so it still works after install.

## StarNAV header (`starnav_header.py`)

The StarNAV title bar is an image (`graphics/pokenav/header.png` + `header.bin`), so its letters are tiles, not
font text. `starnav_header.py` rebuilds Emerald's header (read from git) as STAR NAVIGATOR, top title and bottom
bar, from the header's own letters plus a drawn S, and re-tiles it into the same 53 tiles. Installed 2026-11-04.

```sh
python3 starnav_header.py preview   # out/starnav_header.png (before above, after below)
python3 starnav_header.py install   # writes ../../game/graphics/pokenav/header.png and header.bin (idempotent)
```

## StarNAV map strip (`starnav_map_header.py`)

The strip above the StarNAV map (`graphics/pokenav/left_headers/hoenn_map.png`) said HOENN MAP. This script
rebuilds it from Emerald's image (read from git) as STAR MAP: A, M and P are the strip's own letters, S, T and R
are drawn to match. GALAXY MAP is too wide for the strip. Installed 2026-11-04.

```sh
python3 starnav_map_header.py preview   # out/starnav_map_header.png
python3 starnav_map_header.py install   # writes ../../game/graphics/pokenav/left_headers/hoenn_map.png
```

## StarNAV menu button (`starnav_menu_button.py`)

The StarNAV main menu's map button (`graphics/pokenav/options/hoenn_map.png`, four 32x16 frames side by side)
said HOENN MAP. This script rebuilds it as STAR MAP with the same letters as the map strip. Installed 2026-11-04.

```sh
python3 starnav_menu_button.py preview   # out/starnav_menu_button.png
python3 starnav_menu_button.py install   # writes ../../game/graphics/pokenav/options/hoenn_map.png
```

## Datapad count label (`datapad_dex_label.py`)

With the national Datapad, the list screen shows two count labels, HOENN and NATIONAL, as 32x8 sprite frames in
`graphics/pokedex/interface.png`. OUTER RIM does not fit 32 px in that font, so the label says REGIONAL: IONAL
is copied from NATIONAL, and R, E and G are drawn to match. Installed 2026-11-04.

```sh
python3 datapad_dex_label.py preview   # out/datapad_dex_label.png
python3 datapad_dex_label.py install   # writes ../../game/graphics/pokedex/interface.png
```
