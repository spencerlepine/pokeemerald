"""Layer 1 of a greybox area: the ground in 3D. Heights, ledges, cliffs, berms, water and waterfalls.

A scene's terrain is two grids of one character per 16 px cell:
  heights  0-9   the cell's level; one level is one cell (16 px) of cliff, the game's ledge height
  surface  .     open ground          :  path          "  wild ground (scrub, grass, ash)
           ~     water (its surface sits a little below the bank)
           b     berm: a low mound half a level high with a soft sloped face
           H     stairs cut into the face below this cell
Cells are drawn north to south, so a higher cell further south hides what is behind it, the same rule
as the buildings: one cell north and one level up both move 16 px up the screen. Only top faces and
south faces show. A south face higher than one level is a cliff (strata lines), exactly one is a ledge
(a lit lip), a half level is a berm. Water that drops to a lower cell is a waterfall.

Colours come from the planet palette (ground, path, wild, water, cliff, ledge). `grey=True` gives the
pure greybox look.
"""
from PIL import Image, ImageDraw

from .style import shade

C = 16
GREY = {"ground": (196, 196, 196), "path": (214, 214, 214), "wild": (176, 176, 176), "water": (120, 132, 150),
        "cliff": (150, 150, 150), "ledge": (170, 170, 170)}


def _h(*v):
    x = 2166136261
    for n in v:
        x = ((x ^ (n & 0xFFFFFFFF)) * 16777619) & 0xFFFFFFFF
    return x


class Terrain:
    def __init__(self, heights, surface, pal, grey=False):
        self.hs = [r for r in heights.strip("\n").split("\n")]
        self.sf = [r for r in surface.strip("\n").split("\n")]
        self.H = len(self.hs)
        self.W = max(len(r) for r in self.hs)
        self.pal = GREY if grey else {k: pal.get(k, pal["ground"]) for k in GREY}
        if not grey:
            self.pal["ledge"] = pal.get("ledge", shade(pal["cliff"], 0.25))

    def surf(self, x, y):
        if 0 <= y < len(self.sf) and 0 <= x < len(self.sf[y]):
            return self.sf[y][x]
        return "."

    def level(self, x, y):
        """The height of the cell's top in levels (berms add half a level, water sits a quarter below)."""
        x = min(max(x, 0), self.W - 1)
        y = min(max(y, 0), self.H - 1)
        row = self.hs[y]
        c = row[x] if x < len(row) else "0"
        lv = float(int(c)) if c.isdigit() else 0.0
        s = self.surf(x, y)
        if s == "b":
            lv += 0.5
        return lv

    def top(self):
        return max(self.level(x, y) for y in range(self.H) for x in range(self.W))

    # ------------------------------------------------------------------------------------------------ drawing
    def size(self):
        return self.W * C, (self.H + int(self.top() + 0.99)) * C

    def oy(self):
        return int(self.top() + 0.99) * C

    def cell_y(self, y, lv):
        """Screen y of the north edge of cell row y at level lv."""
        return self.oy() + y * C - round(lv * C)

    def draw_row(self, img, d, y):
        """Draw map row y: every cell's top face, then its south face."""
        for x in range(self.W):
            self._top(d, x, y)
        for x in range(self.W):
            self._south(d, x, y)

    def _top(self, d, x, y):
        p = self.pal
        s = self.surf(x, y)
        lv = self.level(x, y)
        x0, y0 = x * C, self.cell_y(y, lv)
        wet = s == "~"
        base = {"~": p["water"], ":": p["path"], '"': p["wild"]}.get(s, p["ground"])
        drop = 3 if wet else 0
        d.rectangle([x0, y0, x0 + C - 1, y0 + C - 1], fill=base)
        r = _h(x, y)
        if wet:
            d.rectangle([x0, y0, x0 + C - 1, y0 + drop - 1], fill=shade(p["cliff"], -0.1)) if self.surf(x, y - 1) != "~" else None
            light = shade(base, 0.25)
            off = (y % 2) * 4
            d.line([(x0 + 1 + off, y0 + 7), (x0 + 6 + off, y0 + 7)], fill=light)
            d.line([(x0 + 7 - off, y0 + 12), (x0 + 12 - off, y0 + 12)], fill=light)
        elif s == '"':
            dark = shade(base, -0.25)
            for tx, ty in ((2, 5), (9, 3), (5, 11), (12, 12)):
                d.line([(x0 + tx, y0 + ty + 3), (x0 + tx + 1, y0 + ty), (x0 + tx + 2, y0 + ty + 3)], fill=dark)
        elif s == "b":
            d.rectangle([x0, y0, x0 + C - 1, y0 + 2], fill=shade(base, 0.12))
        else:
            for k in range(2):
                rr = _h(x, y, k)
                d.point((x0 + rr % 16, y0 + (rr >> 8) % 16), fill=shade(base, -0.07))
        # shadow from a higher cell to the west (the light comes from the south-west)
        lw = self.level(x - 1, y) if x > 0 else lv
        if lw > lv:
            w = min(C, int((lw - lv) * 9))
            d.rectangle([x0, y0, x0 + w - 1, y0 + C - 1], fill=(0, 0, 0, 50))
        # a rock lip on a side that drops to a lower neighbour (side faces don't show in this view)
        if not wet:
            for nx, ex in ((x + 1, x0 + C - 3), (x - 1, x0)):
                if 0 <= nx < self.W and self.level(nx, y) <= lv - 1:
                    d.rectangle([ex, y0, ex + 2, y0 + C - 1], fill=p["cliff"] if lv - self.level(nx, y) > 1 else p["ledge"])
        # outline where a neighbour is lower, so plateaus read from above
        edge = shade(base, -0.35)
        if x + 1 < self.W and self.level(x + 1, y) < lv:
            d.line([x0 + C - 1, y0, x0 + C - 1, y0 + C - 1], fill=edge)
        if x > 0 and self.level(x - 1, y) < lv:
            d.line([x0, y0, x0, y0 + C - 1], fill=edge)
        if y > 0 and self.level(x, y - 1) < lv:
            d.line([x0, y0, x0 + C - 1, y0], fill=edge)
        del r

    def _south(self, d, x, y):
        p = self.pal
        lv = self.level(x, y)
        ls = self.level(x, y + 1) if y + 1 < self.H else lv
        if ls >= lv:
            return
        x0 = x * C
        ya, yb = self.cell_y(y, lv) + C, self.cell_y(y, ls) + C
        s = self.surf(x, y)
        drop = lv - ls
        if s == "~":
            base = p["water"]
            d.rectangle([x0, ya, x0 + C - 1, yb - 1], fill=shade(base, 0.12))
            for k in range(3):
                xx = x0 + 2 + (_h(x, y, k) % 12)
                d.line([xx, ya + 1, xx, yb - 3], fill=shade(base, 0.45))
            d.rectangle([x0, yb - 3, x0 + C - 1, yb - 1], fill=shade(base, 0.7))
            return
        if s == "b" and drop <= 0.5:
            col = p["ground"]
            for i in range(yb - ya):
                d.line([x0, ya + i, x0 + C - 1, ya + i], fill=shade(col, -0.04 - 0.12 * i / max(1, yb - ya)))
            return
        cliff = p["cliff"] if drop > 1 else p["ledge"]
        d.rectangle([x0, ya, x0 + C - 1, yb - 1], fill=cliff)
        d.line([x0, ya, x0 + C - 1, ya], fill=shade(cliff, 0.35))
        if drop > 1:
            for z in range(ya + 8, yb - 3, 8):
                j = _h(x, z) % 3
                d.line([x0, z + j - 1, x0 + C - 1, z + (_h(x + 1, z) % 3) - 1], fill=shade(cliff, -0.18))
            xx = x0 + 3 + _h(x, y) % 10
            d.line([xx, ya + 2, xx + 1, yb - 3], fill=shade(cliff, -0.14))
        d.line([x0, yb - 1, x0 + C - 1, yb - 1], fill=shade(cliff, -0.4))
        if self.surf(x, y + 1) == "H" or s == "H":
            for z in range(ya + 2, yb - 1, 4):
                d.rectangle([x0 + 3, z, x0 + 12, z + 1], fill=shade(cliff, 0.3))
        # a darker edge where the face ends beside a higher neighbour, so cliffs read as blocks
        for nx in (x - 1, x + 1):
            if 0 <= nx < self.W and self.level(nx, y) < lv and self.level(nx, y + 1) < lv:
                ex = x0 if nx < x else x0 + C - 1
                d.line([ex, ya, ex, yb - 1], fill=shade(cliff, -0.4))


def render(heights, surface, pal, grey=False):
    t = Terrain(heights, surface, pal, grey)
    img = Image.new("RGB", t.size(), t.pal["ground"])
    d = ImageDraw.Draw(img, "RGBA")
    for y in range(t.H):
        t.draw_row(img, d, y)
    return img, t
