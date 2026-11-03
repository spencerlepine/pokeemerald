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
