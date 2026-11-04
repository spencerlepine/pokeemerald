"""The slicer spike: what the player throws at a droid instead of a capture pod (net:droid-slicing).

    python3 slicer/slicer_spike.py preview   # output/slicer_spike/preview.png (8x, the 3 frames and the sparks)
    python3 slicer/slicer_spike.py install   # writes graphics/balls/slicer_spike.png and slicer_sparks.pal in ../../game

The spike uses the pod's own sprite layout: a 16x48 sheet of three 16x16 frames on one 16-colour bank.
Frame 0 is the spike closed (in flight and while it shakes), frame 1 has the probe and prongs coming out,
frame 2 is fully jacked in, with sparks (the pod's "open" frame). The game code is in src/pokeball.c
(gSlicerSpike*) and src/battle_anim_throw.c (the throw, the spark burst, the cyan fade).

The sparks reuse the vanilla particle sheet (graphics/battle_anims/sprites/particles.png) with a cyan copy of
its palette (circle_impact): slicer_sparks.pal.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
GAME = ROOT / "game"
OUT = HERE.parent / "output" / "slicer_spike"
ENFORCER = ROOT / "tools" / "palette-enforcer"

# 16 colours, GBA steps of 8. 0 is transparent.
PALETTE = [
    (0, 0, 0),         # 0 transparent
    (24, 24, 40),      # 1 outline
    (64, 72, 88),      # 2 dark metal
    (112, 120, 136),   # 3 metal
    (168, 176, 192),   # 4 light metal
    (232, 240, 248),   # 5 highlight
    (0, 104, 152),     # 6 cyan, dark
    (56, 192, 232),    # 7 cyan
    (200, 248, 248),   # 8 cyan, bright
    (248, 168, 40),    # 9 amber status light
    (136, 80, 16),     # 10 amber, dark
    (8, 8, 8), (16, 16, 16), (32, 32, 32), (40, 40, 40), (48, 48, 48),   # 11-15 unused
]

# '.' = 0, digits = index, 'a' = 10.
CLOSED = """
................
......1111......
.....145531.....
.....149a31.....
.....143321.....
....11111111....
.....145321.....
.....132221.....
.....145321.....
.....132221.....
.....145321.....
....11111111....
......1431......
......1321......
.......11.......
................
"""

OPENING = """
................
......1111......
.....145531.....
.....147631.....
.....143321.....
....11111111....
.....145321.....
.....132221.....
.....145321.....
.....132221.....
....11453211....
...1111111111...
...161.1431.161.
...1...1781...1.
.......1871.....
........11......
"""

JACKED = """
................
......1111......
.....145531.....
.....148731.....
.....143321.....
....11111111....
.....145321.....
.....132221.....
.....145321.....
..1..132221..1..
..1111453211111.
.161111111111161
.16....1781...16
8.7....1871...7.
..8...178871..8.
.....8.7887.8...
"""


def grid(art: str) -> list[list[int]]:
    rows = [r for r in art.strip("\n").split("\n")]
    assert len(rows) == 16 and all(len(r) == 16 for r in rows), [len(r) for r in rows]
    return [[0 if c == "." else int(c, 16) for c in r] for r in rows]


def sheet() -> Image.Image:
    img = Image.new("P", (16, 48))
    img.putpalette([c for rgb in PALETTE for c in rgb])
    for f, art in enumerate((CLOSED, OPENING, JACKED)):
        for y, row in enumerate(grid(art)):
            for x, i in enumerate(row):
                img.putpixel((x, 16 * f + y), i)
    return img


def sparks_pal() -> list[tuple[int, int, int]]:
    """circle_impact's bank with the particle colours turned cyan (streaks 1-2, sparkle 12-15)."""
    src = Image.open(GAME / "graphics/battle_anims/sprites/circle_impact.png").getpalette()[:48]
    pal = [tuple(src[i:i + 3]) for i in range(0, 48, 3)]
    pal[1], pal[2] = (216, 248, 248), (56, 192, 232)
    pal[12], pal[13], pal[14], pal[15] = (200, 248, 248), (56, 192, 232), (0, 104, 152), (248, 248, 248)
    return [tuple(v // 8 * 8 for v in c) for c in pal]


def write_pal(path: Path, pal) -> None:
    path.write_text("JASC-PAL\r\n0100\r\n16\r\n" + "".join(f"{r} {g} {b}\r\n" for r, g, b in pal))


def check(path: Path) -> None:
    subprocess.run([sys.executable, "-m", "gba_palette", "check", str(path)], cwd=ENFORCER, check=True)


def _rgba(img: Image.Image) -> Image.Image:
    """An indexed image with index 0 see-through."""
    out = img.convert("RGBA")
    out.putalpha(img.point(lambda i: 255 if i else 0, "L"))
    return out


def preview() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    spike = _rgba(sheet())
    parts = Image.open(GAME / "graphics/battle_anims/sprites/particles.png")
    parts.putpalette([c for rgb in sparks_pal() for c in rgb])
    parts = _rgba(parts)
    board = Image.new("RGBA", (16 * 3 + 6 * 4 + 8, 64), (40, 48, 64, 255))
    for f in range(3):
        board.alpha_composite(spike.crop((0, 16 * f, 16, 16 * f + 16)), (6 + 22 * f, 24))
    board.alpha_composite(parts, (6 + 22 * 3, 0))
    board.resize((board.width * 8, board.height * 8), Image.NEAREST).save(OUT / "preview.png")
    sheet().save(OUT / "slicer_spike.png")
    check(OUT / "slicer_spike.png")
    print(OUT / "preview.png")


def install() -> None:
    dst = GAME / "graphics/balls/slicer_spike.png"
    sheet().save(dst)
    check(dst)
    write_pal(GAME / "graphics/balls/slicer_sparks.pal", sparks_pal())
    check(GAME / "graphics/balls/slicer_sparks.pal")
    print("installed", dst, "and slicer_sparks.pal")


if __name__ == "__main__":
    {"preview": preview, "install": install}[sys.argv[1] if len(sys.argv) > 1 else "preview"]()
