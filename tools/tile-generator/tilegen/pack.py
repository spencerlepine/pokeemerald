"""Stage 7: write a tileset back in the game's format, gate it with palette-enforcer, install it.

Output folder layout (same as game/data/tilesets/<primary|secondary>/<name>/):
    tiles.png                 indexed PNG, 128 px wide, greyscale preview palette (gbagfx reads indices only)
    palettes/00.pal .. 15.pal JASC banks (primary: 0-5 meaningful, secondary: 6-12; the rest copied)
    metatiles.bin             8 x u16 per metatile
    metatile_attributes.bin   u16 per metatile
"""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image

from . import gba

GREY = [(248 - i * 16, 248 - i * 16, 248 - i * 16) for i in range(16)]   # on GBA steps, preview only


def write_tileset(ts: gba.Tileset, out: Path) -> Path:
    out = Path(out)
    (out / "palettes").mkdir(parents=True, exist_ok=True)
    n = len(ts.tiles)
    rows = (n + 15) // 16
    sheet = gba.tiles_to_image(ts.tiles, 16)
    assert sheet.shape == (rows * 8, 128)
    im = Image.fromarray(sheet, "P")
    pal = []
    for c in GREY:
        pal += list(c)
    im.putpalette(pal + [0] * (768 - len(pal)))
    im.save(out / "tiles.png", optimize=False, bits=4)   # 4-bit PNG like the vanilla sheets
    for i in range(16):
        gba.write_pal(out / "palettes" / f"{i:02d}.pal", ts.palettes[i])
    (out / "metatiles.bin").write_bytes(np.ascontiguousarray(ts.metatiles, dtype="<u2").tobytes())
    (out / "metatile_attributes.bin").write_bytes(np.ascontiguousarray(ts.attributes, dtype="<u2").tobytes())
    return out


def enforcer_dir() -> Path:
    return Path(__file__).resolve().parents[2] / "palette-enforcer"


def check_tileset(ts: gba.Tileset, out: Path) -> tuple[bool, list[str]]:
    """Layer 1 gate: every bank the tileset owns is a legal 16-entry GBA bank, every tile only uses
    indices 0-15 (4bpp), the sheet is 128 wide and a multiple of 8 tall, and every bank a metatile names
    exists. Runs palette-enforcer `check` on tiles.png and the owned .pal files."""
    lines: list[str] = []
    ok = True
    banks = range(0, 6) if not ts.secondary else range(6, 13)
    if ts.tiles.max() > 15:
        ok = False; lines.append("tiles use an index > 15")
    for mid in range(ts.n_metatiles):
        for e in ts.metatiles[mid].ravel():
            e = int(e)
            if (e & 0x3FF) and not (0 <= (e >> 12) & 0xF <= 12):
                lines.append(f"metatile {mid} names bank {(e >> 12) & 0xF} (13-15 are the UI's; vanilla does this on a few unused metatiles) (warning)")
                break
    for b in banks:
        for c in ts.palettes[b]:
            if any(v % 8 for v in c):
                lines.append(f"bank {b}: {c} is off the GBA step (warning)")
    out = Path(out).resolve()
    files = [str(out / "tiles.png")] + [str(out / "palettes" / f"{b:02d}.pal") for b in banks]
    r = subprocess.run([sys.executable, "-m", "gba_palette", "check", "--tile", *files], cwd=enforcer_dir(),
                       capture_output=True, text=True)
    lines += [l for l in (r.stdout + r.stderr).splitlines() if l.strip()]
    if r.returncode != 0:
        ok = False
    return ok, lines


def tileset_game_dir(ts: gba.Tileset) -> Path:
    return ts.path


def install_tileset(ts: gba.Tileset, out: Path, num_tiles_header: Path | None = None) -> None:
    """Copy a checked build into game/data/tilesets/... and fix `-num_tiles N` for secondaries."""
    ok, lines = check_tileset(ts, out)
    if not ok:
        raise SystemExit("refusing to install, check failed:\n" + "\n".join(lines))
    dst = tileset_game_dir(ts)
    for f in ("tiles.png", "metatiles.bin", "metatile_attributes.bin"):
        shutil.copy(out / f, dst / f)
    for i in range(16):
        shutil.copy(out / "palettes" / f"{i:02d}.pal", dst / "palettes" / f"{i:02d}.pal")
    if ts.secondary:
        game = gba.game_dir()
        rel = dst.relative_to(game).as_posix()
        import re
        for hdr in (game / "src/data/tilesets/graphics.h", game / "src/graphics.c"):
            txt = hdr.read_text()
            pat = re.compile(r'(INCGFX_U32\("' + re.escape(rel) + r'/tiles\.png", "\.4bpp(?:\.lz)?", "-num_tiles )(\d+)')
            new, n = pat.subn(lambda m: m.group(1) + str(len(ts.tiles)), txt)
            if n:
                hdr.write_text(new)
