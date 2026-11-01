"""GBA colour rules: 15-bit colour, 16-colour banks, JASC .pal files, colour distance.

Layer 1 of tools/PALETTES.md (the hardware). Nothing here knows about themes.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np

Colour = tuple[int, int, int]

# Highest 8-bit value that maps exactly onto a 5-bit GBA channel (31 << 3).
MAX_STEP = 248

# Colours a palette can show besides index 0 (transparent / backdrop), by PNG bit depth.
VISIBLE = {1: 1, 2: 3, 4: 15, 8: 255}


def snap(c: Colour) -> Colour:
    """Nearest GBA step: each channel rounded to a multiple of 8, 0-248."""
    return tuple(min(MAX_STEP, int(round(v / 8.0)) * 8) for v in c[:3])


def truncate(c: Colour) -> Colour:
    """What gbagfx/the GBA keep of an 8-bit colour: the top 5 bits of each channel."""
    return tuple((v >> 3) << 3 for v in c[:3])


def on_step(c: Colour) -> bool:
    return all(v % 8 == 0 for v in c[:3])


def bgr555(c: Colour) -> int:
    r, g, b = c[:3]
    return (r >> 3) | ((g >> 3) << 5) | ((b >> 3) << 10)


def hex_of(c: Colour) -> str:
    return "#%02X%02X%02X" % tuple(c[:3])


def parse_hex(s: str) -> Colour:
    s = s.strip().lstrip("#")
    if len(s) != 6:
        raise ValueError(f"not a #RRGGBB colour: {s!r}")
    return tuple(int(s[i : i + 2], 16) for i in (0, 2, 4))


def load_jasc(path: str | Path) -> list[Colour]:
    words = Path(path).read_text().split()
    if not words or words[0] != "JASC-PAL":
        raise ValueError(f"{path}: not a JASC-PAL file")
    n = int(words[2])
    vals = list(map(int, words[3 : 3 + 3 * n]))
    return [tuple(vals[i : i + 3]) for i in range(0, 3 * n, 3)]


def write_jasc(path: str | Path, colours: list[Colour]) -> None:
    """JASC-PAL exactly as pokeemerald writes it: CRLF, one entry per line."""
    rows = ["JASC-PAL", "0100", str(len(colours))] + [f"{r} {g} {b}" for r, g, b in colours]
    Path(path).write_bytes(("\r\n".join(rows) + "\r\n").encode())


def png_bit_depth(path: str | Path) -> int:
    """Bit depth from the PNG header (byte 24 of IHDR): 1, 2, 4 or 8 for indexed PNGs."""
    with open(path, "rb") as f:
        head = f.read(26)
    if head[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError(f"{path}: not a PNG")
    return head[24]


# --- colour distance (CIELAB, D65), used to pick the nearest allowed colour -------------

def _lin(v: np.ndarray) -> np.ndarray:
    v = v / 255.0
    return np.where(v <= 0.04045, v / 12.92, ((v + 0.055) / 1.055) ** 2.4)


def to_lab(rgb) -> np.ndarray:
    """(..., 3) sRGB 0-255 -> (..., 3) CIELAB."""
    a = _lin(np.asarray(rgb, dtype=np.float64))
    m = np.array([[0.4124, 0.3576, 0.1805], [0.2126, 0.7152, 0.0722], [0.0193, 0.1192, 0.9505]])
    xyz = a @ m.T / np.array([0.95047, 1.0, 1.08883])
    f = np.where(xyz > 0.008856, np.cbrt(xyz), 7.787 * xyz + 16 / 116)
    L = 116 * f[..., 1] - 16
    A = 500 * (f[..., 0] - f[..., 1])
    B = 200 * (f[..., 1] - f[..., 2])
    return np.stack([L, A, B], axis=-1)


def nearest(colours, targets) -> tuple[np.ndarray, np.ndarray]:
    """For each colour, the index of the nearest target and the distance (Delta E 76)."""
    c = to_lab(np.asarray(colours, dtype=np.float64).reshape(-1, 3))
    t = to_lab(np.asarray(targets, dtype=np.float64).reshape(-1, 3))
    d = np.linalg.norm(c[:, None, :] - t[None, :, :], axis=2)
    i = d.argmin(axis=1)
    return i, d[np.arange(len(i)), i]


def luma(c: Colour) -> float:
    r, g, b = c[:3]
    return 0.299 * r + 0.587 * g + 0.114 * b
