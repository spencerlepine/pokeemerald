"""The three warden battle wipes in Aurebesh (Emerald: Regice / Registeel / Regirock Braille dot patterns).

    python3 transitions/aurebesh_wipes.py preview   # out/: before/after of each wipe (nothing in ../../game changes)
    python3 transitions/aurebesh_wipes.py install   # writes regis.png, regice/registeel/regirock.bin, num_tiles in battle_transition.c

Emerald draws each wipe from one shared tile sheet (graphics/battle_transitions/regis.png, one big dot) and a
32x32 tilemap per warden that places the dots in that Regi's Braille pattern. The palettes (regice.pal ...)
and the code stay as they are. This tool writes a new shared sheet and the three tilemaps: each warden's
element in big Aurebesh letters, ICE / DURA / ROCK, from the approved letters in
../glyph-maker/aurebesh.py, shaded like the dots (dark rim index 10, mid 11, bright 12).
"""
from __future__ import annotations

import re
import struct
import sys
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
GAME = ROOT / "game"
GFX = GAME / "graphics" / "battle_transitions"
OUT = HERE.parent / "output" / "aurebesh_wipes"
sys.path.insert(0, str(ROOT / "tools" / "glyph-maker"))
from aurebesh import LETTERS, grid  # noqa: E402  (the approved Aurebesh letters, 8x9 ASCII art)

WORDS = {"regice": "ICE", "registeel": "DURA", "regirock": "ROCK"}  # ICEWARDEN, DURAWARDEN, ROCKWARDEN
SCALE = 5          # one letter pixel = 5x5 screen pixels: a letter is 40x45 before the stroke is thickened
GAP = 14           # screen pixels between letters
STROKE = 3         # the ink is grown by this radius (round), so the 1-pixel art becomes a solid carved stroke
RIM, MID, LIT = 10, 11, 12   # palette indices of the dot's shading (see regice.pal)
SCREEN = (240, 160)


def word_mask(word: str) -> set[tuple[int, int]]:
    w = len(word) * 8 * SCALE + (len(word) - 1) * GAP
    x0, y0 = (SCREEN[0] - w) // 2, (SCREEN[1] - 9 * SCALE) // 2
    ink = set()
    for i, ch in enumerate(word):
        for y, row in enumerate(grid(LETTERS[ch])):
            for x, c in enumerate(row):
                if c == "#":
                    lx = x0 + i * (8 * SCALE + GAP) + x * SCALE
                    ink |= {(lx + dx, y0 + y * SCALE + dy) for dx in range(SCALE) for dy in range(SCALE)}
    disk = [(dx, dy) for dx in range(-STROKE, STROKE + 1) for dy in range(-STROKE, STROKE + 1)
            if dx * dx + dy * dy <= STROKE * STROKE + 1]
    return {(x + dx, y + dy) for x, y in ink for dx, dy in disk}


def screen(word: str) -> list[list[int]]:
    ink = word_mask(word)
    px = [[0] * SCREEN[0] for _ in range(SCREEN[1])]
    near = lambda x, y, r: any((x + dx, y + dy) not in ink for dx in range(-r, r + 1) for dy in range(-r, r + 1))
    for x, y in ink:
        px[y][x] = RIM if near(x, y, 1) else MID if near(x, y, 2) else LIT
    return px


def build():
    tiles, index, maps = [tuple([0] * 64)], {tuple([0] * 64): (0, 0, 0)}, {}
    for name, word in WORDS.items():
        px = screen(word)
        ents = [0] * 1024
        for r in range(20):
            for c in range(30):
                t = tuple(px[r * 8 + y][c * 8 + x] for y in range(8) for x in range(8))
                if t not in index:
                    n = len(tiles)
                    tiles.append(t)
                    rows = [t[i * 8:i * 8 + 8] for i in range(8)]
                    for hf in (0, 1):
                        for vf in (0, 1):
                            rr = [row[::-1] if hf else row for row in (rows[::-1] if vf else rows)]
                            index.setdefault(tuple(v for row in rr for v in row), (n, hf, vf))
                n, hf, vf = index[t]
                ents[r * 32 + c] = (0xF000 if n else 0) | (vf << 11) | (hf << 10) | n
        maps[name] = ents
    assert len(tiles) <= 256, f"{len(tiles)} tiles: the wipe loads at most 256"
    return tiles, maps


def sheet(tiles) -> Image.Image:
    rows = (len(tiles) + 15) // 16
    img = Image.new("P", (128, rows * 8), 0)
    img.putpalette(Image.open(GFX / "regis.png").getpalette())
    for n, t in enumerate(tiles):
        for i, v in enumerate(t):
            img.putpixel((n % 16 * 8 + i % 8, n // 16 * 8 + i // 8), v)
    return img


def render(tileset: Image.Image, ents, pal: str) -> Image.Image:
    vals = (GFX / f"{pal}.pal").read_text().split()[3:]
    colours = [tuple(map(int, vals[i:i + 3])) for i in range(0, 48, 3)]
    im = Image.new("RGB", SCREEN, (40, 48, 56))
    for r in range(20):
        for c in range(30):
            e = ents[r * 32 + c]
            n, hf, vf = e & 0x3FF, e >> 10 & 1, e >> 11 & 1
            t = tileset.crop((n % 16 * 8, n // 16 * 8, n % 16 * 8 + 8, n // 16 * 8 + 8))
            if hf:
                t = t.transpose(Image.FLIP_LEFT_RIGHT)
            if vf:
                t = t.transpose(Image.FLIP_TOP_BOTTOM)
            for y in range(8):
                for x in range(8):
                    v = t.getpixel((x, y))
                    if v:
                        im.putpixel((c * 8 + x, r * 8 + y), colours[v])
    return im


def read_bin(name: str):
    d = (GFX / f"{name}.bin").read_bytes()
    return list(struct.unpack(f"<{len(d) // 2}H", d))


def preview() -> None:
    from PIL import ImageDraw
    OUT.mkdir(parents=True, exist_ok=True)
    tiles, maps = build()
    new, old = sheet(tiles), Image.open(GFX / "regis.png")
    out = Image.new("RGB", (2 * 250 + 10, 3 * 175 + 30), (255, 255, 255))
    d = ImageDraw.Draw(out)
    d.text((10, 8), f"warden wipes: Braille (before) vs Aurebesh (after); {len(tiles)} tiles", fill=(0, 0, 0))
    for i, name in enumerate(WORDS):
        out.paste(render(old, read_bin(name), name), (10, 30 + i * 175))
        out.paste(render(new, maps[name], name), (260, 30 + i * 175))
    out.resize((out.width * 2, out.height * 2), Image.NEAREST).save(OUT / "before_after.png")
    print("wrote", OUT / "before_after.png", f"({len(tiles)} tiles)")


def install() -> None:
    tiles, maps = build()
    sheet(tiles).save(GFX / "regis.png")
    for name, ents in maps.items():
        (GFX / f"{name}.bin").write_bytes(struct.pack("<1024H", *ents))
    c = GAME / "src" / "battle_transition.c"
    src = c.read_text(encoding="utf-8")
    src, n = re.subn(r'(graphics/battle_transitions/regis\.png", "\.4bpp", "-num_tiles )\d+', rf"\g<1>{len(tiles)}", src)
    assert n == 1
    c.write_text(src, encoding="utf-8")
    print("installed", len(tiles), "tiles and", len(maps), "tilemaps")


if __name__ == "__main__":
    {"preview": preview, "install": install}[sys.argv[1] if len(sys.argv) > 1 else "preview"]()
