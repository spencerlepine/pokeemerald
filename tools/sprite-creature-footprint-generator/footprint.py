"""Datapad footprints: one 16x16, 1-bit stamp per companion.

Each species has a foot type in feet.csv (chosen by hand from its Star Wars brief). The stamp for that type
is drawn here as shapes on a 16-unit grid, scaled to the creature's size (read from its approved battle
front), supersampled 8x and thresholded to 1 bit, then passed through palette-enforcer.

    python3 footprint.py treecko mudkip --out out      # a few
    python3 footprint.py --all --out out                # every footprint row in the wiki
    python3 footprint.py --sheet sheet.png              # every foot type at 3 sizes
"""
from __future__ import annotations

import argparse
import csv
import math
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(REPO / "tools" / "palette-enforcer"))
from gba_palette import check  # noqa: E402
from grids import GRIDS, grid  # noqa: E402

GAME = REPO / "game"
ART = REPO / "wiki" / "art"
SS = 8  # supersampling
# vanilla footprint.png palette: index 0 white (paper), index 1 dark grey (ink)
PALETTE = [255, 255, 255, 98, 98, 98]


class Pen:
    """Draws in 16-unit footprint space, scaled by `s` around the centre."""

    def __init__(self, s: float):
        self.s = s
        self.im = Image.new("L", (16 * SS, 16 * SS), 0)
        self.d = ImageDraw.Draw(self.im)

    def p(self, x, y):
        return ((8 + (x - 8) * self.s) * SS, (8 + (y - 8) * self.s) * SS)

    def ell(self, x, y, rx, ry, fill=255):
        (ax, ay), (bx, by) = self.p(x - rx, y - ry), self.p(x + rx, y + ry)
        self.d.ellipse([ax, ay, bx, by], fill=fill)

    def poly(self, pts, fill=255):
        self.d.polygon([self.p(*q) for q in pts], fill=fill)

    def line(self, pts, w, fill=255):
        """A stroke `w` units wide (never thinner than ~1.1 px, so it survives the threshold)."""
        width = max(1.15 * SS, w * self.s * SS)
        q = [self.p(*a) for a in pts]
        self.d.line(q, fill=fill, width=int(round(width)), joint="curve")
        r = width / 2
        for x, y in (q[0], q[-1]):
            self.d.ellipse([x - r, y - r, x + r, y + r], fill=fill)

    def rect(self, x0, y0, x1, y1, fill=255):
        (ax, ay), (bx, by) = self.p(x0, y0), self.p(x1, y1)
        self.d.rectangle([ax, ay, bx, by], fill=fill)

    def mask(self) -> np.ndarray:
        a = np.array(self.im.resize((16, 16), Image.BOX))
        return a >= 118


def toe_line(pen, x0, y0, x1, y1, w):
    pen.line([(x0, y0), (x1, y1)], w)


# --- foot types -------------------------------------------------------------------------------------

def paw(pen):
    pen.ell(8, 10.6, 3.7, 3.0)
    pen.poly([(4.6, 11.5), (8, 7.2), (11.4, 11.5), (8, 14)])
    for x, y in ((3.3, 6.6), (6.4, 3.9), (9.6, 3.9), (12.7, 6.6)):
        pen.ell(x, y, 1.55, 1.9)


def claw(pen):
    """Three long clawed toes and a heel (lizards, crocs, dragons)."""
    pen.ell(8, 12.2, 2.9, 2.6)
    for tx, ty in ((2.6, 3.4), (8, 1.3), (13.4, 3.4)):
        pen.line([(8, 11), (tx + (8 - tx) * 0.18, ty + (11 - ty) * 0.18)], 2.1)
        pen.line([(tx + (8 - tx) * 0.18, ty + (11 - ty) * 0.18), (tx, ty)], 1.0)


def talon(pen):
    """Bird: three thin forward toes and one back toe."""
    for tx, ty in ((2.4, 3.6), (8, 1.4), (13.6, 3.6)):
        pen.line([(8, 10), (tx, ty)], 1.5)
    pen.line([(8, 10), (8, 14.8)], 1.5)
    pen.ell(8, 10, 1.6, 1.6)


def webbed(pen):
    talon_pts = ((2.2, 3.4), (8, 1.4), (13.8, 3.4))
    for tx, ty in talon_pts:
        pen.line([(8, 11.5), (tx, ty)], 1.6)
    pen.poly([(8, 12), (2.2, 3.4), (4.6, 5.6), (8, 1.4), (11.4, 5.6), (13.8, 3.4)])
    pen.ell(8, 11.8, 2.2, 2.2)


def hoof(pen):
    """Cloven hoof: two crescents."""
    pen.ell(5.6, 8.2, 2.6, 5.4)
    pen.ell(10.4, 8.2, 2.6, 5.4)
    pen.rect(7.6, 1, 8.4, 15.5, fill=0)


def round_(pen):
    """Big padded foot with toenails (banthas, rontos, turtles)."""
    pen.ell(8, 9.6, 5.8, 5.4)
    for x in (3.6, 6.5, 9.5, 12.4):
        pen.ell(x, 4.3, 1.5, 1.3, fill=0)
    for x in (3.6, 6.5, 9.5, 12.4):
        pen.ell(x, 2.6, 1.3, 1.2)
    pen.rect(1, 3.6, 15, 4.4, fill=0)


def foot(pen):
    """Two-legged walker's bare foot: sole and five toes."""
    pen.ell(8.4, 10.2, 3.1, 4.6)
    pen.ell(7.2, 6.6, 2.4, 2.2)
    for x, y, r in ((4.6, 3.6, 1.35), (7.0, 2.3, 1.15), (9.2, 2.2, 1.05), (11.1, 3.0, 0.95), (12.5, 4.5, 0.85)):
        pen.ell(x, y, r, r * 1.1)


def hand(pen):
    """Knuckle-walker / ape: broad palm, four fingers and a thumb."""
    pen.ell(8, 10.2, 4.2, 3.6)
    for x, y in ((4.4, 4.6), (7.0, 3.4), (9.6, 3.4), (12.2, 4.6)):
        pen.ell(x, y, 1.3, 2.2)
    pen.line([(4.2, 11.5), (1.8, 9.2)], 1.8)


def bug(pen):
    """Six small leg dots in pairs."""
    for x, y in ((4.4, 3.4), (11.6, 3.4), (2.8, 8), (13.2, 8), (4.4, 12.6), (11.6, 12.6)):
        pen.ell(x, y, 1.25, 1.25)


def spider(pen):
    """Mechanical leg tips (spider and crab droids): four spikes."""
    for x, y, a in ((3, 3, 45), (13, 3, 135), (3, 13, -45), (13, 13, -135)):
        dx, dy = math.cos(math.radians(a)), math.sin(math.radians(a))
        pen.poly([(x + dy * 1.4, y - dx * 1.4), (x - dy * 1.4, y + dx * 1.4), (x + dx * 4.0, y + dy * 4.0)])
        pen.ell(x, y, 1.4, 1.4)


def droid(pen):
    """Droid footplate: square-toed sole with grip grooves and a heel."""
    pen.poly([(4.4, 2.2), (11.6, 2.2), (12, 4), (12, 8.6), (4, 8.6), (4, 4)])
    pen.rect(5, 10.2, 11, 14.6)
    for y in (4.4, 6.6):
        pen.rect(3, y, 13, y + 0.75, fill=0)


def tread(pen):
    """Astromech / tank treads: two tracks with cleats."""
    for x0 in (2.6, 9.4):
        pen.rect(x0, 1.2, x0 + 4.0, 14.8)
        for y in np.arange(2.6, 14.5, 2.4):
            pen.rect(x0 + 0.9, y, x0 + 3.1, y + 0.8, fill=0)


def wheel(pen):
    """Rolling droid: one dashed wheel track."""
    pen.rect(6.0, 1.2, 10.0, 14.8)
    for y in np.arange(2.4, 14.5, 2.2):
        pen.rect(5, y, 11, y + 0.75, fill=0)


def root(pen):
    """Walking plant: a root splayed into tendrils."""
    pen.line([(8, 4), (8, 11)], 2.0)
    pen.line([(8, 10), (3.4, 13.8)], 1.4)
    pen.line([(8, 10), (12.6, 13.8)], 1.4)
    pen.line([(8, 11), (8, 15)], 1.3)
    pen.line([(8, 6), (4, 2.6)], 1.2)
    pen.line([(8, 6), (12, 2.6)], 1.2)


def slime(pen):
    """Slug trail: a wobbly smear."""
    pts = [(8 + 3.4 * math.sin(t * 1.1) * (0.6 + 0.4 * math.cos(t * 2.3)), 1.5 + t * 1.3) for t in np.linspace(0, 10, 40)]
    for i, (x, y) in enumerate(pts):
        r = 2.2 + 0.8 * math.sin(i * 0.7)
        pen.ell(x, y, r, 1.3)


def suction(pen):
    """Tentacles: three suckers (rings)."""
    for x, y, r in ((5, 5, 2.8), (11.2, 6.2, 2.4), (7.4, 11.6, 2.6)):
        pen.ell(x, y, r, r)
        pen.ell(x, y, r * 0.42, r * 0.42, fill=0)


def none(pen):
    pass


TYPES = {
    "paw": paw, "claw": claw, "talon": talon, "webbed": webbed, "hoof": hoof, "round": round_,
    "foot": foot, "hand": hand, "bug": bug, "spider": spider, "droid": droid, "tread": tread,
    "wheel": wheel, "root": root, "slime": slime, "suction": suction, "none": none,
}


def size_of(species: str) -> float:
    """Stamp scale 0.5-1.0 from the creature's approved front (taller and wider fronts leave bigger prints)."""
    f = ART / "graphics/pokemon" / species / "front.png"
    if not f.exists():
        return 0.75
    a = np.array(Image.open(f)) > 0
    ys, xs = np.where(a)
    extent = ((ys.max() - ys.min() + 1) * (xs.max() - xs.min() + 1)) ** 0.5
    return float(np.clip(0.5 + (extent - 24) / 36 * 0.5, 0.5, 1.0))


def stamp(kind: str, s: float) -> np.ndarray:
    if kind in GRIDS:
        return np.array(grid(kind, "S" if s < 0.67 else "M" if s < 0.85 else "L"))
    pen = Pen(max(s, 0.6))
    TYPES[kind](pen)
    return pen.mask()


def to_png(mask: np.ndarray) -> Image.Image:
    im = Image.fromarray(mask.astype(np.uint8), "P")
    im.putpalette(PALETTE)
    return im


def save(mask: np.ndarray, dst: Path):
    dst.parent.mkdir(parents=True, exist_ok=True)
    to_png(mask).save(dst, bits=1, optimize=False)
    rep = check.check_png(dst, bpp=1)
    if not rep.ok:
        raise SystemExit(f"{dst}: " + "\n".join(rep.lines()))


def feet():
    with open(HERE / "feet.csv") as f:
        return {r["species"]: r for r in csv.DictReader(f)}


def rows():
    with open(REPO / "wiki/database/pending_art.csv") as f:
        for r in csv.DictReader(f):
            if r["kind"] == "pokemon" and r["path"].endswith("/footprint.png") and r["swap_kind"] != "CUT":
                yield r["path"].split("/")[2], r["path"]


def make(species: str, table: dict):
    row = table.get(species)
    if row is None:
        raise SystemExit(f"{species}: no foot type in feet.csv")
    kind = row["foot"]
    if kind == "keep":
        return None
    return stamp(kind, float(row.get("scale") or 0) or size_of(species))


def sheet(dst: Path, sc: int = 6):
    kinds = [k for k in TYPES if k != "none"]
    sizes = (0.5, 0.75, 1.0)
    out = Image.new("RGB", (len(kinds) * (16 * sc + 8), len(sizes) * (16 * sc + 8)), (236, 236, 228))
    for i, k in enumerate(kinds):
        for j, s in enumerate(sizes):
            im = to_png(stamp(k, s)).convert("RGB").resize((16 * sc, 16 * sc), Image.NEAREST)
            out.paste(im, (i * (16 * sc + 8) + 4, j * (16 * sc + 8) + 4))
    out.save(dst)


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("species", nargs="*")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--out", default=str(HERE / "out"))
    ap.add_argument("--sheet")
    a = ap.parse_args(argv)
    if a.sheet:
        return sheet(Path(a.sheet))
    table = feet()
    todo = list(rows()) if a.all else [(s, f"graphics/pokemon/{s}/footprint.png") for s in a.species]
    n = 0
    for sp, path in todo:
        m = make(sp, table)
        if m is None:
            continue
        save(m, Path(a.out) / path)
        n += 1
    print(n, "footprints written to", a.out)


if __name__ == "__main__":
    main(sys.argv[1:])
