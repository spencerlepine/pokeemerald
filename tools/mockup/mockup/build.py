"""Buildings in the game's top-down 3/4 view (about 45 degrees).

The camera looks down and north, so:
- a footprint is drawn squashed in depth: a round building is an OVAL, never a circle;
- walls rise straight up the screen, and only the south-facing walls show;
- the roof is the footprint lifted up the screen by the wall height.

Each building fills its cell box (`at` and `size` from phase 1). The box holds the footprint on the ground
at the bottom and the roof, domes and spires above it. A `build` name picks a composition of primitives:

    prism    any polygon footprint, straight or sloped (bunker) walls, roof: flat, pitched, barrel, none
    cyl      a round (oval) footprint, roof: flat, dome, cone, ring, bowl (open arena), deck (platform)
    pit      a sunken courtyard or a dug-in hall: a rim, the far inner wall and the floor below
    berm     an earth mound for buried and half-buried buildings
    legs     stilts under a raised building

Builds are listed in BUILDS below. styles.yaml picks one per art id, plus colours and optional `variants`.
"""
import math

from .style import shade

C = 16
OUTLINE_K = -0.45
LIGHT_X = 0.22          # west faces lighter, east faces darker


def _out(c):
    return shade(c, OUTLINE_K)


class Ctx:
    """One building being drawn: the box, its colours, a random source and the front profile for the door."""

    def __init__(self, d, b, st, seed):
        (cx, cy), (cw, ch) = b["at"], b["size"]
        self.d, self.st, self.seed = d, st, seed
        self.cw, self.ch = cw, ch
        self.x0, self.y0 = cx * C, cy * C
        self.x1, self.y1 = self.x0 + cw * C - 1, self.y0 + ch * C - 1
        self.W, self.H = cw * C, ch * C
        self.wall, self.roof, self.trim = st["wall"], st["roof"], st["trim"]
        self.ground = st.get("ground", (200, 190, 170))
        self.front = []          # (xa, xb, fn(x) -> ground y, wall height) for door placement
        self.door = b.get("door")
        self.door_px = None if self.door is None else self.x0 + int(self.door) * C + C // 2
        self.tall = float(st.get("height") or 1.0)

    def r(self, k, n):
        return ((self.seed >> (k * 3)) & 0xFFFF) % n

    # standard wall height: one cell, up to two for big boxes, scaled by `height`
    def wall_h(self, k=1.0):
        return int(max(9, min(self.H * 0.38, 2 * C)) * self.tall * k)


# --------------------------------------------------------------------------------------------- geometry
def _inside(pt, poly):
    x, y = pt
    n, c = len(poly), False
    for i in range(n):
        (ax, ay), (bx, by) = poly[i], poly[(i + 1) % n]
        if (ay > y) != (by > y) and x < (bx - ax) * (y - ay) / ((by - ay) or 1e-9) + ax:
            c = not c
    return c


def _normals(poly):
    """Outward unit normal for each edge."""
    out = []
    n = len(poly)
    for i in range(n):
        (ax, ay), (bx, by) = poly[i], poly[(i + 1) % n]
        ex, ey = bx - ax, by - ay
        L = math.hypot(ex, ey) or 1
        nx, ny = ey / L, -ex / L
        mx, my = (ax + bx) / 2, (ay + by) / 2
        if _inside((mx + nx * 0.6, my + ny * 0.6), poly):
            nx, ny = -nx, -ny
        out.append((nx, ny))
    return out


def _inset(poly, t):
    """Offset a polygon inward by t px (mitred)."""
    if not t:
        return list(poly)
    ns = _normals(poly)
    n = len(poly)
    out = []
    for i in range(n):
        n1, n2 = ns[i - 1], ns[i]
        sx, sy = -(n1[0] + n2[0]), -(n1[1] + n2[1])
        dot = n1[0] * n2[0] + n1[1] * n2[1]
        k = t / (1 + dot) if dot > -0.9 else t
        out.append((poly[i][0] + sx * k, poly[i][1] + sy * k))
    return out


def _up(poly, h):
    return [(x, y - h) for x, y in poly]


def _ell(cx, cy, rx, ry, a0, a1, n=24):
    """Points on an ellipse, angles in degrees (0 = east, 90 = south on screen)."""
    return [(cx + rx * math.cos(math.radians(a0 + (a1 - a0) * i / n)),
             cy + ry * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]


def _ell_y(cx, cy, rx, ry, x):
    t = max(-1.0, min(1.0, (x - cx) / (rx or 1)))
    return cy + ry * math.sqrt(1 - t * t)


def _box(c, u0, v0, u1, v1):
    """A sub-box of the building's cell box, in fractions."""
    return (c.x0 + c.W * u0, c.y0 + c.H * v0, c.x0 + c.W * u1 - 1, c.y0 + c.H * v1 - 1)


# --------------------------------------------------------------------------------------------- primitives
def shadow(c, poly):
    c.d.polygon([(x + 4, y + 1) for x, y in poly], fill=(0, 0, 0, 55))


def prism(c, poly, h, roof="flat", taper=0, lift=0, wall=None, rooft=None, windows=True, front=True):
    """Extrude a ground polygon by h px. taper > 0 slopes the walls inward (bunkers, pyramids)."""
    d = c.d
    wall = wall or c.wall
    rooft = rooft or c.roof
    base = _up(poly, lift)
    top = _up(_inset(base, taper), h)
    ns = _normals(base)
    faces = []
    n = len(base)
    for i in range(n):
        nx, ny = ns[i]
        if ny < -0.05:
            continue
        if ny < 0.05 and not taper:
            continue
        p, q = base[i], base[(i + 1) % n]
        tp, tq = top[i], top[(i + 1) % n]
        faces.append(((p[1] + q[1]) / 2, [p, q, tq, tp], nx, ny, p, q))
    faces.sort(key=lambda f: f[0])
    for _, quad, nx, ny, p, q in faces:
        col = shade(wall, -LIGHT_X * nx) if abs(nx) > 0.05 else wall
        d.polygon(quad, fill=col, outline=_out(wall))
        if front and ny > 0.5 and not taper:
            xa, xb = min(p[0], q[0]), max(p[0], q[0])
            ya, yb = p[1], q[1]
            c.front.append((xa, xb, (lambda x, xa=p[0], ya=ya, xb=q[0], yb=yb:
                                     ya + (yb - ya) * (x - xa) / ((xb - xa) or 1)), h))
            if windows and h >= 11:
                _windows(c, xa, xb, (ya + yb) / 2, h)
    _roof(c, top, roof, rooft)
    return top


def _windows(c, xa, xb, gy, h):
    d = c.d
    k = int(xa) + 6
    while k + 5 < xb - 3:
        if c.door_px is None or abs(k + 2 - c.door_px) > 9:
            wy = gy - h * 0.62
            d.rectangle([k, wy - 2, k + 4, wy + 2], fill=shade(c.trim, 0.25), outline=_out(c.trim))
        k += 16


def _roof(c, top, kind, col):
    d = c.d
    xs, ys = [p[0] for p in top], [p[1] for p in top]
    rx0, ry0, rx1, ry1 = min(xs), min(ys), max(xs), max(ys)
    if kind == "none":
        return
    if kind == "pitched":
        ov = 2
        ridge = ry0 + (ry1 - ry0) * 0.38
        d.polygon([(rx0 - ov, ridge), (rx1 + ov, ridge), (rx1 + ov - 3, ry0), (rx0 - ov + 3, ry0)],
                  fill=shade(col, -0.18), outline=_out(col))
        d.polygon([(rx0 - ov, ridge), (rx1 + ov, ridge), (rx1 + ov, ry1 + 2), (rx0 - ov, ry1 + 2)],
                  fill=col, outline=_out(col))
        d.line([(rx0 - ov, ridge), (rx1 + ov, ridge)], fill=shade(col, 0.35), width=2)
        for k in range(int(rx0) + 4, int(rx1), 6):
            d.line([(k, ridge + 3), (k, ry1)], fill=shade(col, -0.08))
        return
    if kind == "barrel":       # vault running north-south, seen from above: bands across
        d.polygon(top, fill=col, outline=_out(col))
        w = rx1 - rx0
        for i, k in enumerate((-0.2, -0.05, 0.12, 0.22, 0.12, -0.05, -0.2)):
            xa = rx0 + w * i / 7
            d.rectangle([xa + 1, ry0 + 2, xa + w / 7, ry1 - 1], fill=shade(col, k))
        for yy in range(int(ry0) + 5, int(ry1), 6):
            d.line([(rx0 + 2, yy), (rx1 - 2, yy)], fill=shade(col, -0.12))
        return
    d.polygon(top, fill=col, outline=_out(col))
    if kind == "flat":
        d.line(top + [top[0]], fill=shade(col, 0.25), width=1)
        inner = _inset(top, 3)
        d.line(inner + [inner[0]], fill=shade(col, -0.1), width=1)
        if (rx1 - rx0) > 30 and (ry1 - ry0) > 14:     # a roof vent
            vx = rx0 + (rx1 - rx0) * (0.25 + 0.5 * c.r(1, 2))
            vy = ry0 + (ry1 - ry0) * 0.45
            d.rectangle([vx - 4, vy - 3, vx + 4, vy + 2], fill=shade(col, -0.2), outline=_out(col))
            d.rectangle([vx - 4, vy - 3, vx + 4, vy - 1], fill=shade(col, 0.15))


def cyl(c, box, h, roof="dome", lift=0, dome=None, wall=None, rooft=None, ry_k=0.55, bands=0, windows=True):
    """A round building: oval footprint across the box width, walls h px, then a roof."""
    d = c.d
    bx0, by0, bx1, by1 = box
    rx = (bx1 - bx0) / 2
    cx = (bx0 + bx1) / 2
    dh = dome if dome is not None else ({"dome": rx * 0.55, "cone": rx * 0.8}.get(roof, 0))
    room = (by1 - by0) - h - lift - dh
    ry = max(3, min(rx * ry_k, room / 2))
    if room / 2 < rx * ry_k * 0.7 and roof in ("dome", "cone"):      # tight box: squash the dome instead
        dh = max(4, (by1 - by0) - h - lift - 2 * rx * ry_k * 0.7)
        ry = max(3, min(rx * ry_k, ((by1 - by0) - h - lift - dh) / 2))
    gy = by1 - ry                  # ground ellipse centre
    wall = wall or c.wall
    rooft = rooft or c.roof
    if not lift:
        d.ellipse([cx - rx + 4, gy - ry + 1, cx + rx + 4, gy + ry + 1], fill=(0, 0, 0, 55))
    by = gy - lift                 # base of the walls
    ty = by - h                    # top ellipse centre
    if h > 0:
        band = _ell(cx, by, rx, ry, 0, 180)[::-1] + [(cx - rx, ty), (cx + rx, ty)]
        band = [(cx + rx, ty)] + _ell(cx, by, rx, ry, 0, 180) + [(cx - rx, ty)]
        d.polygon(band, fill=wall, outline=_out(wall))
        # light from the west: a highlight strip left, shade right
        for a0, a1, k in ((115, 150, 0.18), (25, 70, -0.18)):
            pts = _ell(cx, by, rx, ry, a0, a1, 8)
            strip = pts + [(pts[-1][0], ty), (pts[0][0], ty)]
            d.polygon(strip, fill=shade(wall, k))
        for i in range(bands):
            yy = ty + h * (i + 1) / (bands + 1)
            d.line(_ell(cx, yy, rx, ry, 0, 180), fill=shade(c.trim, 0), width=2)
        c.front.append((cx - rx, cx + rx, lambda x, cx=cx, by=by, rx=rx, ry=ry: _ell_y(cx, by, rx, ry, x), h))
        if windows and h >= 12:
            for a in (125, 105, 75, 55) if rx > 30 else (120, 60):
                wx, wy = cx + rx * math.cos(math.radians(a)) * 0.92, by + ry * math.sin(math.radians(a)) - h * 0.6
                if c.door_px is None or abs(wx - c.door_px) > 9:
                    d.rectangle([wx - 2, wy - 2, wx + 2, wy + 2], fill=shade(c.trim, 0.25), outline=_out(c.trim))
    if roof == "dome":
        # a hemisphere seen from above and in front: a tall half-oval on top of the rim oval
        dh = max(dh, ry)
        d.chord([cx - rx, ty - dh, cx + rx, ty + dh], 180, 360, fill=rooft)
        d.chord([cx - rx, ty - ry, cx + rx, ty + ry], 0, 180, fill=rooft)
        d.chord([cx - rx * 0.55, ty - dh * 0.98, cx + rx, ty + ry], 270, 450, fill=shade(rooft, -0.12))
        d.ellipse([cx - rx * 0.62, ty - dh * 0.82, cx - rx * 0.05, ty - dh * 0.3], fill=shade(rooft, 0.22))
        d.ellipse([cx - rx * 0.48, ty - dh * 0.74, cx - rx * 0.24, ty - dh * 0.52], fill=shade(rooft, 0.45))
        d.arc([cx - rx, ty - dh, cx + rx, ty + dh], 180, 360, fill=_out(rooft))
        d.arc([cx - rx, ty - ry, cx + rx, ty + ry], 0, 180, fill=_out(rooft))
        d.ellipse([cx - 2, ty - dh - 1, cx + 2, ty - dh + 2], fill=shade(c.trim, 0.1), outline=_out(c.trim))
    elif roof == "cone":
        pts = [(cx, ty - dh)] + _ell(cx, ty, rx + 2, ry + 1, 0, 180)
        d.polygon(pts, fill=rooft, outline=_out(rooft))
        for a in range(10, 180, 20):
            px, py = cx + (rx + 2) * math.cos(math.radians(a)), ty + (ry + 1) * math.sin(math.radians(a))
            d.line([(cx, ty - dh + 2), (px, py)], fill=shade(rooft, -0.18))
        d.polygon([(cx, ty - dh)] + _ell(cx, ty, rx + 2, ry + 1, 120, 170, 6), fill=shade(rooft, 0.15))
    elif roof in ("flat", "ring", "deck"):
        d.ellipse([cx - rx, ty - ry, cx + rx, ty + ry], fill=rooft, outline=_out(rooft))
        if roof == "ring":
            d.ellipse([cx - rx * 0.7, ty - ry * 0.7, cx + rx * 0.7, ty + ry * 0.7], outline=shade(rooft, -0.25), width=2)
            d.ellipse([cx - rx * 0.3, ty - ry * 0.45, cx + rx * 0.3, ty + ry * 0.15], fill=shade(rooft, 0.2),
                      outline=_out(rooft))
        elif roof == "deck":
            d.ellipse([cx - rx * 0.78, ty - ry * 0.78, cx + rx * 0.78, ty + ry * 0.78], outline=shade(c.trim, 0.3), width=2)
            s = rx * 0.25
            d.line([(cx - s, ty - s * 0.5), (cx - s, ty + s * 0.5)], fill=shade(c.trim, 0.3), width=2)
            d.line([(cx + s, ty - s * 0.5), (cx + s, ty + s * 0.5)], fill=shade(c.trim, 0.3), width=2)
            d.line([(cx - s, ty), (cx + s, ty)], fill=shade(c.trim, 0.3), width=2)
        else:
            d.ellipse([cx - rx + 3, ty - ry + 2, cx + rx - 3, ty + ry - 2], outline=shade(rooft, 0.2))
    elif roof == "bowl":         # open-top arena: rim, stands on the far side, field in the middle
        d.ellipse([cx - rx, ty - ry, cx + rx, ty + ry], fill=rooft, outline=_out(rooft))
        ir, iry = rx * 0.78, ry * 0.72
        d.ellipse([cx - ir, ty - iry, cx + ir, ty + iry], fill=shade(c.wall, -0.25))
        fl = c.st.get("field", (110, 150, 80))
        d.ellipse([cx - ir * 0.8, ty - iry * 0.45, cx + ir * 0.8, ty + iry * 0.95], fill=fl, outline=_out(fl))
        d.line([(cx, ty - iry * 0.4), (cx, ty + iry * 0.9)], fill=shade(fl, 0.3))
        d.ellipse([cx - 4, ty + iry * 0.25 - 3, cx + 4, ty + iry * 0.25 + 3], outline=shade(fl, 0.3))
    return cx, ty, rx, ry


def legs(c, xs, top, bottom, col=None):
    col = col or shade(c.trim, -0.1)
    for x in xs:
        c.d.rectangle([x - 1, top, x + 1, bottom], fill=col, outline=_out(col))


def pit(c, box, depth=None, rim=None):
    """A sunken courtyard: an oval hole with a rim, the far inner wall and the floor."""
    d = c.d
    bx0, by0, bx1, by1 = box
    rx, cx = (bx1 - bx0) / 2, (bx0 + bx1) / 2
    ry = min(rx * 0.62, (by1 - by0) / 2)
    cy = by1 - ry
    rim = rim or c.roof
    d.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=rim, outline=_out(rim))
    d.arc([cx - rx + 1, cy - ry + 1, cx + rx - 1, cy + ry - 1], 160, 290, fill=shade(rim, 0.3), width=2)
    ir, iry = rx - 5, ry - 4
    depth = depth if depth is not None else min(10, iry * 0.8)
    d.ellipse([cx - ir, cy - iry, cx + ir, cy + iry], fill=shade(c.wall, -0.15), outline=_out(rim))
    # floor: the lower part of the hole, its far edge pushed down by the depth
    fl = shade(c.ground, -0.12)
    d.chord([cx - ir + 1, cy - iry + depth, cx + ir - 1, cy + iry - 1], 0, 180, fill=fl)
    d.ellipse([cx - ir + 2, cy - iry + depth, cx + ir - 2, cy + iry - 1], fill=fl)
    d.arc([cx - ir, cy - iry, cx + ir, cy + iry], 0, 180, fill=_out(rim))
    # doors into the far wall
    for a in (235, 305) if ir > 24 else (270,):
        wx = cx + ir * 0.8 * math.cos(math.radians(a))
        wy = cy - iry * 0.55
        d.rectangle([wx - 3, wy - 1, wx + 3, wy + depth * 0.7], fill=shade(c.trim, -0.3))
    c.front.append((cx - rx, cx + rx, lambda x: by1, 0))
    return cx, cy, rx, ry


def berm(c, box, col=None):
    """An earth mound (the ground colour, a little darker) for buried and half-buried buildings."""
    col = col or shade(c.ground, -0.12)
    bx0, by0, bx1, by1 = box
    c.d.ellipse([bx0 + 3, by0 + 3, bx1 + 3, by1 + 1], fill=(0, 0, 0, 45))
    c.d.ellipse([bx0, by0, bx1, by1], fill=col, outline=shade(col, -0.3))
    c.d.arc([bx0 + 3, by0 + 2, bx1 - 3, by1 - 2], 190, 280, fill=shade(col, 0.25), width=2)


def dish(c, x, y, r=7):
    d = c.d
    d.line([(x, y), (x, y - r)], fill=_out(c.trim), width=2)
    d.ellipse([x - r, y - r * 1.9, x + r, y - r * 0.6], fill=shade(c.wall, 0.15), outline=_out(c.wall))
    d.ellipse([x - r * 0.5, y - r * 1.6, x + r * 0.5, y - r * 0.9], fill=shade(c.wall, -0.15))
    d.line([(x, y - r * 1.25), (x + r * 0.6, y - r * 2.1)], fill=_out(c.trim))


def door(c, wide=False):
    if c.door_px is None:
        return
    x = c.door_px
    gy, h = c.y1, 14
    best = None
    for xa, xb, fn, wh in c.front:
        if xa - 1 <= x <= xb + 1:
            y = fn(x)
            if best is None or y > best[0]:
                best = (y, wh)
    if best:
        gy, h = best[0], best[1] or 14
    dh = max(6, min(13, h - 3))
    half = 9 if wide else 4
    col = shade(c.trim, -0.25)
    c.d.rectangle([x - half, gy - dh, x + half, gy], fill=col, outline=_out(c.trim))
    c.d.rectangle([x - half + 1, gy - dh + 1, x + half - 1, gy - dh + 3], fill=shade(c.trim, 0.3))
    c.d.line([(x - half, gy), (x + half, gy)], fill=shade(c.trim, -0.5))


# --------------------------------------------------------------------------------------------- footprints
def fp(c, kind, box=None, h=0, extra=0):
    """Ground polygon of a footprint in the box. The roof needs h + extra px above it."""
    bx0, by0, bx1, by1 = box or (c.x0, c.y0, c.x1, c.y1)
    gy0 = by0 + h + extra
    w, dpt = bx1 - bx0, by1 - gy0
    P = lambda u, v: (bx0 + w * u, gy0 + dpt * v)
    if kind == "L":
        a = 0.5 + 0.1 * c.r(2, 2)
        if c.r(3, 2):
            return [P(0, 0), P(a, 0), P(a, 0.45), P(1, 0.45), P(1, 1), P(0, 1)]
        return [P(1 - a, 0), P(1, 0), P(1, 1), P(0, 1), P(0, 0.45), P(1 - a, 0.45)]
    if kind == "oct":
        k = min(0.22, 7 / max(w, 1))
        kv = min(0.3, 7 / max(dpt, 1))
        return [P(k, 0), P(1 - k, 0), P(1, kv), P(1, 1 - kv), P(1 - k, 1), P(k, 1), P(0, 1 - kv), P(0, kv)]
    if kind == "T":
        return [P(0, 0), P(1, 0), P(1, 0.5), P(0.7, 0.5), P(0.7, 1), P(0.3, 1), P(0.3, 0.5), P(0, 0.5)]
    if kind == "notch":    # rect with an entry recess at the front
        return [P(0, 0), P(1, 0), P(1, 1), P(0.62, 1), P(0.62, 0.8), P(0.38, 0.8), P(0.38, 1), P(0, 1)]
    return [P(0, 0), P(1, 0), P(1, 1), P(0, 1)]


def _door_ok(c, poly):
    """True when the door column reaches the front row of the footprint."""
    if c.door_px is None:
        return True
    ys = [p[1] for p in poly]
    bottom = max(ys)
    for i in range(len(poly)):
        (ax, ay), (bx, by) = poly[i], poly[(i + 1) % len(poly)]
        if abs(ay - bottom) < 1 and abs(by - bottom) < 1 and min(ax, bx) + 3 <= c.door_px <= max(ax, bx) - 3:
            return True
    return False


# --------------------------------------------------------------------------------------------- builds
def b_block(c, foot="rect", roof="flat"):
    h = c.wall_h()
    extra = 4 if roof == "pitched" else 0
    poly = fp(c, foot, h=h, extra=extra)
    if not _door_ok(c, poly):
        poly = fp(c, "rect", h=h, extra=extra)
    shadow(c, poly)
    prism(c, poly, h, roof)
    door(c)


def b_court(c):
    """A block around an open courtyard."""
    h = c.wall_h(0.85)
    poly = fp(c, "rect", h=h)
    shadow(c, poly)
    top = prism(c, poly, h, "flat")
    xs, ys = [p[0] for p in top], [p[1] for p in top]
    ix0, ix1 = min(xs) + max(8, c.W * 0.25), max(xs) - max(8, c.W * 0.25)
    iy0, iy1 = min(ys) + 5, max(ys) - 5
    if ix1 - ix0 > 6 and iy1 - iy0 > 6:
        c.d.rectangle([ix0, iy0, ix1, iy1], fill=shade(c.ground, -0.05), outline=_out(c.roof))
        c.d.rectangle([ix0, iy0, ix1, iy0 + min(h * 0.6, (iy1 - iy0) * 0.5)], fill=shade(c.wall, -0.1))
        c.d.ellipse([(ix0 + ix1) / 2 - 3, iy1 - 7, (ix0 + ix1) / 2 + 3, iy1 - 3], fill=(90, 140, 70))
    door(c)


def b_wings(c, towers=False, dome_mid=False):
    """A tall centre block with lower wings on both sides."""
    h = c.wall_h(1.1)
    hw = int(h * 0.6)
    a, b_ = 0.3, 0.7
    for u0, u1 in ((0, a + 0.02), (b_ - 0.02, 1)):
        bx = _box(c, u0, 0.3, u1, 1)
        poly = fp(c, "rect", bx, h=hw)
        shadow(c, poly)
        prism(c, poly, hw, "flat", rooft=shade(c.roof, -0.08))
    bx = _box(c, a, 0, b_, 1)
    poly = fp(c, "rect", bx, h=h)
    shadow(c, poly)
    top = prism(c, poly, h, "pitched" if c.st.get("roof_kind") == "pitched" else "flat")
    if dome_mid:
        xs, ys = [p[0] for p in top], [p[1] for p in top]
        cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
        r = (max(xs) - min(xs)) * 0.3
        c.d.ellipse([cx - r, cy - r * 0.9, cx + r, cy + r * 0.5], fill=shade(c.roof, 0.1), outline=_out(c.roof))
    if towers:
        for u in (0.0, 0.84):
            cyl(c, _box(c, u, 0.25, u + 0.16, 1.0), int(h * 1.2), "dome", windows=False, dome=6)
    door(c, wide=c.cw >= 6)


def b_dome(c, k_h=0.55):
    h = int(c.wall_h() * k_h)
    cyl(c, (c.x0, c.y0, c.x1, c.y1), h, "dome")
    door(c)


def b_domes2(c):
    """A big dome with a smaller dome joined to one side (cantina, junk shop)."""
    left = c.r(4, 2)
    big = (0.0, 0.0, 0.66, 1.0) if left else (0.34, 0.0, 1.0, 1.0)
    small = (0.6, 0.35, 1.0, 1.0) if left else (0.0, 0.35, 0.4, 1.0)
    h = int(c.wall_h() * 0.55)
    # connecting block between them
    cb = _box(c, 0.25, 0.45, 0.75, 1.0)
    poly = fp(c, "rect", cb, h=h)
    prism(c, poly, h, "flat", windows=False)
    cyl(c, _box(c, *small), int(h * 0.8), "dome", windows=False)
    cyl(c, _box(c, *big), h, "dome")
    door(c)


def b_dome_block(c):
    """A flat block with a dome beside it (homestead with garage)."""
    h = int(c.wall_h() * 0.7)
    left = c.r(5, 2)
    blk = (0.0, 0.3, 0.55, 1.0) if left else (0.45, 0.3, 1.0, 1.0)
    dm = (0.4, 0.0, 1.0, 1.0) if left else (0.0, 0.0, 0.6, 1.0)
    poly = fp(c, "rect", _box(c, *blk), h=h)
    shadow(c, poly)
    prism(c, poly, h, "flat")
    cyl(c, _box(c, *dm), h, "dome")
    door(c)


def b_sunken(c):
    """A courtyard dug into the ground (Lars homestead): rim, inner wall, floor, and a small entry dome."""
    cx, cy, rx, ry = pit(c, (c.x0, c.y0 + 6, c.x1, c.y1))
    if c.door_px is not None:
        ex = c.door_px
        ew = min(12, rx * 0.45)
        cyl(c, (ex - ew, c.y1 - ew * 1.6, ex + ew, c.y1), 5, "dome", windows=False, ry_k=0.5)
    door(c)


def b_sunken_dome(c):
    """A low dome sitting in a ring trench (a dug-in den)."""
    cx, cy, rx, ry = pit(c, (c.x0, c.y0 + 4, c.x1, c.y1), depth=4)
    k = 0.25
    cyl(c, (c.x0 + c.W * k, c.y0, c.x1 - c.W * k, cy + ry * 0.55), 4, "dome", windows=False)
    door(c)


def b_bunker(c):
    """Low, sloped concrete walls in an earth berm, a gun-slit window, a recessed door."""
    berm(c, (c.x0 - 2, c.y0 + c.H * 0.25, c.x1 + 2, c.y1 + 2))
    h = max(9, int(c.wall_h(0.6)))
    poly = fp(c, "rect", (c.x0 + 3, c.y0, c.x1 - 3, c.y1 - 1), h=h, extra=4)
    top = prism(c, poly, h, "flat", taper=5, windows=False)
    ys = [p[1] for p in top]
    sy = max(ys) + h * 0.45
    c.d.rectangle([c.x0 + 8, sy - 1, c.x1 - 8, sy + 1], fill=(20, 20, 24))
    c.front.append((c.x0, c.x1, lambda x: c.y1 - 1, h))
    door(c)


def b_buried(c):
    """A dome mostly underground: a mound with the top of the dome and a framed entry."""
    berm(c, (c.x0 - 1, c.y0 + c.H * 0.2, c.x1 + 1, c.y1 + 1))
    cyl(c, (c.x0 + c.W * 0.12, c.y0, c.x1 - c.W * 0.12, c.y1 - c.H * 0.18), 0, "dome", windows=False)
    if c.door_px is not None:
        x = c.door_px
        poly = [(x - 8, c.y1 - 2), (x + 8, c.y1 - 2), (x + 8, c.y1 - 10), (x - 8, c.y1 - 10)]
        prism(c, poly, 10, "flat", windows=False)
    door(c)


def b_quonset(c, wide_door=False):
    """A barrel-vault hut: the vault runs north-south, the arched end faces the camera."""
    h = c.wall_h(0.9)
    bx0, bx1 = c.x0 + 1, c.x1 - 1
    w = bx1 - bx0
    arch_h = min(h + 6, w * 0.5)
    rooftop = c.y0 + 2
    front_top = c.y1 - arch_h
    shadow(c, [(bx0, c.y0 + arch_h), (bx1, c.y0 + arch_h), (bx1, c.y1), (bx0, c.y1)])
    poly = [(bx0, rooftop + arch_h * 0.5), (bx1, rooftop + arch_h * 0.5), (bx1, c.y1 - arch_h * 0.5),
            (bx0, c.y1 - arch_h * 0.5)]
    _roof(c, [(bx0, rooftop), (bx1, rooftop), (bx1, c.y1 - arch_h * 0.5), (bx0, c.y1 - arch_h * 0.5)],
          "barrel", c.roof)
    c.d.chord([bx0, front_top, bx1, c.y1 + arch_h], 180, 360, fill=c.wall, outline=_out(c.wall))
    c.d.chord([bx0 + 3, front_top + 3, bx1 - 3, c.y1 + arch_h - 3], 180, 360, outline=shade(c.wall, -0.15))
    c.front.append((bx0, bx1, lambda x: c.y1, arch_h))
    door(c, wide=wide_door or c.cw >= 5)


def b_stilts(c, roof="pitched", round_=False):
    """A building raised on legs (tree village, sea platform)."""
    lift = max(8, int(c.H * 0.22))
    h = c.wall_h(0.75)
    if round_:
        cx = (c.x0 + c.x1) / 2
        rx = c.W / 2
        legs(c, [cx - rx * 0.6, cx - rx * 0.2, cx + rx * 0.2, cx + rx * 0.6], c.y1 - lift - 6, c.y1)
        c.d.ellipse([c.x0 + 4, c.y1 - 8, c.x1 + 4, c.y1 + 2], fill=(0, 0, 0, 50))
        cyl(c, (c.x0, c.y0, c.x1, c.y1 - lift), h, roof if roof != "pitched" else "dome")
    else:
        poly = fp(c, "rect", (c.x0 + 1, c.y0, c.x1 - 1, c.y1 - lift), h=h, extra=4 if roof == "pitched" else 0)
        shadow(c, [(x, y + lift) for x, y in poly])
        xs = [p[0] for p in poly]
        legs(c, [min(xs) + 4, (min(xs) + max(xs)) / 2, max(xs) - 4], max(p[1] for p in poly) - 4, c.y1)
        # a deck in front of the door
        prism(c, poly, h, roof)
    # stairs or a ramp down from the door
    if c.door_px is not None:
        x = c.door_px
        top = max((fn(x) for xa, xb, fn, _ in c.front if xa <= x <= xb), default=c.y1 - lift)
        for k, yy in enumerate(range(int(top), c.y1 + 1, 3)):
            c.d.line([(x - 4, yy), (x + 4, yy)], fill=shade(c.trim, -0.2), width=2)
        door(c)


def b_cone(c):
    h = int(c.wall_h() * 0.6)
    cyl(c, (c.x0 + 1, c.y0, c.x1 - 1, c.y1), h, "cone")
    door(c)


def b_tower(c):
    h = int(min(c.H * 0.62, c.H - 18))
    poly = fp(c, "oct" if c.r(6, 2) else "rect", (c.x0 + 1, c.y0, c.x1 - 1, c.y1), h=h)
    shadow(c, poly)
    top = prism(c, poly, h, "flat", windows=False)
    gy = max(p[1] for p in poly)
    for row in range(1, max(2, h // 11)):
        wy = gy - row * 11 - 2
        if wy < min(p[1] for p in top) + 4:
            break
        for wx in range(int(c.x0) + 6, int(c.x1) - 6, 8):
            c.d.rectangle([wx, wy, wx + 3, wy + 4], fill=shade(c.trim, 0.25))
    c.front.append((c.x0, c.x1, lambda x: gy, 14))
    door(c)


def b_round_tower(c):
    """Cloud City: a tall cylinder with trim bands and a ringed flat roof (or a dome with `top: dome`)."""
    h = int(min(c.H * 0.55 * c.tall, c.H - 22))
    top = c.st.get("top", "ring")
    cyl(c, (c.x0, c.y0, c.x1, c.y1), h, top, bands=max(1, h // 22), dome=c.W * 0.2 if top == "dome" else None)
    door(c)


def b_stepped(c, tiers=3):
    """A temple: tiers that step back as they rise."""
    h = max(7, c.wall_h(0.45))
    poly = fp(c, "rect", h=h * tiers + 4)
    shadow(c, poly)
    cur = poly
    for t in range(tiers):
        top = prism(c, cur, h, "flat" if t == tiers - 1 else "none", lift=h * t if False else 0,
                    taper=2, windows=False, front=(t == 0), rooft=shade(c.roof, 0.08 * t))
        if t < tiers - 1:
            c.d.polygon(top, fill=shade(c.roof, 0.06 * t), outline=_out(c.roof))
            xs, ys = [p[0] for p in top], [p[1] for p in top]
            iw = (max(xs) - min(xs)) * 0.13
            idp = (max(ys) - min(ys)) * 0.15
            cur = [(min(xs) + iw, min(ys) + idp * 0.4), (max(xs) - iw, min(ys) + idp * 0.4),
                   (max(xs) - iw, max(ys) - idp), (min(xs) + iw, max(ys) - idp)]
    if c.door_px is not None:     # a stair up the front
        x = c.door_px
        c.d.polygon([(x - 6, c.y1), (x + 6, c.y1), (x + 4, c.y1 - h * 1.8), (x - 4, c.y1 - h * 1.8)],
                    fill=shade(c.wall, 0.15), outline=_out(c.wall))
    c.front.append((c.x0, c.x1, lambda x: c.y1, h))
    door(c)


def b_deck(c):
    """A landing platform: a flat oval deck on a central pylon."""
    lift = max(6, int(c.H * 0.15))
    cx = (c.x0 + c.x1) / 2
    c.d.ellipse([cx - c.W * 0.15 + 4, c.y1 - 8, cx + c.W * 0.15 + 4, c.y1], fill=(0, 0, 0, 50))
    c.d.rectangle([cx - 5, c.y1 - lift - 6, cx + 5, c.y1 - 2], fill=shade(c.wall, -0.2), outline=_out(c.wall))
    cyl(c, (c.x0, c.y0, c.x1, c.y1 - lift), 4, "deck", windows=False, ry_k=0.5)
    c.front.append((c.x0, c.x1, lambda x: c.y1, 12))
    door(c)


def b_plant(c):
    """A power station: a block with round silos behind it."""
    h = c.wall_h(0.8)
    n = 2 if c.cw < 6 else 3
    for i in range(n):
        u = 0.1 + 0.8 * i / max(1, n - 1) - 0.1
        cyl(c, _box(c, u, 0.0, u + 0.2, 0.6), int(h * 0.9), "flat", windows=False, bands=1)
    poly = fp(c, "rect", _box(c, 0, 0.4, 1, 1), h=h)
    shadow(c, poly)
    prism(c, poly, h, "flat")
    door(c)


def b_lab(c):
    """An L-shaped lab with a dish antenna on the roof."""
    h = c.wall_h()
    poly = fp(c, "L", h=h)
    if not _door_ok(c, poly):
        poly = fp(c, "notch", h=h)
    shadow(c, poly)
    top = prism(c, poly, h, "flat")
    xs, ys = [p[0] for p in top], [p[1] for p in top]
    dish(c, max(xs) - 9 if c.r(3, 2) else min(xs) + 9, max(ys) - 5)
    door(c)


def b_arena(c):
    """An oval stadium: outer wall, stands, the field inside."""
    h = c.wall_h(0.8)
    cyl(c, (c.x0, c.y0, c.x1, c.y1), h, "bowl", ry_k=0.6, bands=1)
    door(c, wide=True)


def b_hangar(c):
    b_quonset(c, wide_door=True)


def b_store(c):
    """A big round hall with a glass dome."""
    h = c.wall_h(0.9)
    cyl(c, (c.x0, c.y0, c.x1, c.y1), h, "dome", bands=1, dome=c.W * 0.22)
    door(c, wide=c.cw >= 5)


BUILDS = {
    "block": b_block, "box": b_block,
    "L": lambda c: b_block(c, "L"), "oct": lambda c: b_block(c, "oct"), "T": lambda c: b_block(c, "T"),
    "notch": lambda c: b_block(c, "notch"),
    "pitched": lambda c: b_block(c, "rect", "pitched"), "barrel": lambda c: b_block(c, "rect", "barrel"),
    "court": b_court, "wings": b_wings, "palace": lambda c: b_wings(c, towers=True),
    "hall": lambda c: b_wings(c, dome_mid=True),
    "dome": b_dome, "domes2": b_domes2, "dome-block": b_dome_block, "store": b_store,
    "sunken": b_sunken, "sunken-dome": b_sunken_dome, "bunker": b_bunker, "buried": b_buried,
    "quonset": b_quonset, "hangar": b_hangar,
    "stilts": b_stilts, "stilts-dome": lambda c: b_stilts(c, "dome", round_=True),
    "stilts-flat": lambda c: b_stilts(c, "flat"),
    "cone": b_cone, "tower": b_tower, "round-tower": b_round_tower, "stepped": b_stepped,
    "deck": b_deck, "plant": b_plant, "lab": b_lab, "arena": b_arena,
}
# the first-pass `kind` names, so an old catalogue entry still draws
KIND_TO_BUILD = {"box": "block", "dome": "dome", "pitched": "pitched", "stepped": "stepped", "tower": "tower",
                 "hall": "hall", "dish": "sunken", "platform": "deck"}


def building(d, b, st, seed):
    c = Ctx(d, b, st, seed)
    name = st.get("build") or KIND_TO_BUILD.get(st.get("kind"), "block")
    BUILDS.get(name, b_block)(c)
