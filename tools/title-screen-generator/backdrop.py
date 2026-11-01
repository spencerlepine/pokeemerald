"""Exogorth (BG0, replaces Rayquaza) and sky (BG1, replaces the clouds), drawn at 4x and reduced to crisp pixels.
BG0 and BG1 share one 16-colour palette in the game, so each theme keeps both under 15 colours."""
import math, random
from PIL import Image, ImageDraw, ImageChops
from fx import paint, shift, sub
from logo import hexc

S = 4                     # supersample
W, H = 240, 160


def reduce(m):
    return m.resize((m.size[0] // S, m.size[1] // S), Image.BOX).point(lambda v: 255 if v >= 128 else 0)


def canvas(w=W, h=H):
    return Image.new("L", (w * S, h * S), 0)


def worm_path(pts, r0, r1, n=400):
    """Catmull-Rom through pts; returns [(x, y, r, angle)] with radius tapering r0 (tail) -> r1 (head)."""
    out = []
    P = [pts[0]] + pts + [pts[-1]]
    segs = len(pts) - 1
    for i in range(n + 1):
        t = i / n * segs
        k = min(int(t), segs - 1); u = t - k
        p0, p1, p2, p3 = P[k], P[k + 1], P[k + 2], P[k + 3]
        f = lambda a, b, c, d: 0.5 * ((2 * b) + (-a + c) * u + (2 * a - 5 * b + 4 * c - d) * u * u + (-a + 3 * b - 3 * c + d) * u ** 3)
        out.append((f(p0[0], p1[0], p2[0], p3[0]), f(p0[1], p1[1], p2[1], p3[1]), r0 + (r1 - r0) * (i / n) ** 0.7))
    res = []
    for i, (x, y, r) in enumerate(out):
        j = min(i + 1, len(out) - 1); h = max(i - 1, 0)
        a = math.atan2(out[j][1] - out[h][1], out[j][0] - out[h][0])
        res.append((x, y, r, a))
    return res


def draw_worm(path, ring_every=14):
    body, rings = canvas(), canvas()
    db, dr = ImageDraw.Draw(body), ImageDraw.Draw(rings)
    for x, y, r, a in path:
        db.ellipse([(x - r) * S, (y - r) * S, (x + r) * S, (y + r) * S], fill=255)
    for i, (x, y, r, a) in enumerate(path):
        if i % ring_every == 0 and i < len(path) - 20:
            nx, ny = -math.sin(a), math.cos(a)
            dr.line([((x - nx * r) * S, (y - ny * r) * S), ((x + nx * r) * S, (y + ny * r) * S)], fill=255, width=S * 2)
    return body, rings


def maw(cx, cy, r, teeth=14, facing=0.0, squash=1.0):
    """Open mouth seen head-on: lip disc, dark throat, ring of teeth pointing inward."""
    lip, throat, tooth = canvas(), canvas(), canvas()
    ImageDraw.Draw(lip).ellipse([(cx - r) * S, (cy - r * squash) * S, (cx + r) * S, (cy + r * squash) * S], fill=255)
    ri = r * 0.72
    ImageDraw.Draw(throat).ellipse([(cx - ri) * S, (cy - ri * squash) * S, (cx + ri) * S, (cy + ri * squash) * S], fill=255)
    dt = ImageDraw.Draw(tooth)
    for k in range(teeth):
        a = facing + 2 * math.pi * k / teeth
        w = math.pi / teeth * 0.75
        p = lambda rr, aa: ((cx + rr * math.cos(aa)) * S, (cy + rr * math.sin(aa) * squash) * S)
        dt.polygon([p(ri + 1, a - w), p(ri + 1, a + w), p(ri * 0.55, a)], fill=255)
    return lip, throat, tooth


def rim(mask, dx=-1, dy=-1):
    return sub(mask, shift(mask, -dx * 2, -dy * 2))


def render(layers, size=(W, H)):
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    for mask, color in layers:
        paint(img, mask, hexc(color))
    return img


# ---------- Exogorth variants ----------

def exo_coil(pal=("041016", "08202a", "1a5464", "02080c", "3c7478", "0e3440")):
    dark, body_c, hi_c, throat_c, teeth_c, lip_c = pal
    path = worm_path([(-10, 150), (30, 112), (40, 60), (90, 26), (160, 30), (214, 72), (204, 124), (160, 132)], 7, 24)
    body, rings = draw_worm(path)
    lip, throat, tooth = maw(146, 118, 30, teeth=12, facing=0.2)
    body, rings, lip, throat, tooth = map(reduce, (body, rings, lip, throat, tooth))
    rings = ImageChops.multiply(rings, sub(body, lip))
    return render([(body, body_c), (rim(body), hi_c), (rings, dark), (lip, lip_c), (rim(lip), hi_c),
                   (throat, throat_c), (ImageChops.multiply(tooth, lip), teeth_c)])


def asteroid_mask(cx, cy, r, seed, bumps=9):
    rnd = random.Random(seed)
    m = canvas(); pts = []
    ph = [rnd.random() * 6.28 for _ in range(3)]
    for k in range(48):
        a = 2 * math.pi * k / 48
        rr = r * (1 + 0.10 * math.sin(3 * a + ph[0]) + 0.07 * math.sin(5 * a + ph[1]) + 0.05 * math.sin(bumps * a + ph[2]))
        pts.append(((cx + rr * math.cos(a)) * S, (cy + rr * math.sin(a) * 0.85) * S))
    ImageDraw.Draw(m).polygon(pts, fill=255)
    return m


def exo_asteroid(pal=("08061a", "0e0a24", "362c5c", "040210", "5c5088", "1c1638", "120e28", "08061a")):
    dark, body_c, hi_c, throat_c, teeth_c, lip_c, rock_c, crater_c = pal
    rock = asteroid_mask(52, 150, 78, 3)
    craters = canvas(); dc = ImageDraw.Draw(craters)
    for (x, y, r) in [(30, 120, 9), (78, 132, 6), (14, 150, 5), (100, 110, 4)]:
        dc.ellipse([(x - r) * S, (y - r * .7) * S, (x + r) * S, (y + r * .7) * S], fill=255)
    path = worm_path([(70, 92), (80, 60), (110, 34), (160, 30), (196, 56), (190, 92)], 12, 22)
    body, rings = draw_worm(path)
    lip, throat, tooth = maw(182, 96, 26, teeth=11, facing=0.5, squash=0.9)
    rock, craters, body, rings, lip, throat, tooth = map(reduce, (rock, craters, body, rings, lip, throat, tooth))
    rings = ImageChops.multiply(rings, sub(body, lip))
    return render([(body, body_c), (rim(body), hi_c), (rings, dark), (lip, lip_c), (rim(lip), hi_c),
                   (throat, throat_c), (ImageChops.multiply(tooth, lip), teeth_c),
                   (rock, rock_c), (rim(rock), hi_c), (ImageChops.multiply(craters, rock), crater_c)])


def exo_maw(pal=("0a0604", "180e08", "3a2412", "040201", "6a4e32", "2a1a0c")):
    dark, body_c, hi_c, throat_c, teeth_c, lip_c = pal
    cx, cy = 120, 104
    seg = canvas(); ds = ImageDraw.Draw(seg)
    for k, r in enumerate(range(150, 60, -14)):
        ds.ellipse([(cx - r) * S, (cy - r * .8) * S, (cx + r) * S, (cy + r * .8) * S], fill=255 if k % 2 == 0 else 0)
    body = canvas(); ImageDraw.Draw(body).ellipse([(cx - 150) * S, (cy - 120) * S, (cx + 150) * S, (cy + 120) * S], fill=255)
    lip, throat, tooth = maw(cx, cy, 62, teeth=16, squash=0.8)
    lip2, throat2, tooth2 = maw(cx, cy, 40, teeth=12, facing=0.2, squash=0.8)
    body, seg, lip, throat, tooth, lip2, throat2, tooth2 = map(reduce, (body, seg, lip, throat, tooth, lip2, throat2, tooth2))
    seg = sub(seg, lip)
    return render([(body, body_c), (seg, dark), (rim(seg, 0, -1), hi_c), (lip, lip_c), (rim(lip, 0, -1), hi_c),
                   (throat, throat_c), (ImageChops.multiply(tooth, lip), teeth_c),
                   (ImageChops.multiply(tooth2, throat), dark), (throat2, "000000"),
                   (ImageChops.multiply(tooth2, throat), teeth_c)])


EXO = {"coil": exo_coil, "asteroid": exo_asteroid, "maw": exo_maw}


# ---------- Sky variants (256x256, wraps vertically because the game scrolls it) ----------

def sky_stars(seed=7, cols=("ffffff", "a8d8ff", "6888b0")):
    rnd = random.Random(seed)
    img = Image.new("RGBA", (256, 256), (0, 0, 0, 0)); px = img.load()
    for _ in range(170):
        px[rnd.randrange(256), rnd.randrange(256)] = hexc(cols[2]) + (255,)
    for _ in range(45):
        px[rnd.randrange(256), rnd.randrange(256)] = hexc(cols[1]) + (255,)
    for _ in range(12):
        x, y = rnd.randrange(2, 254), rnd.randrange(2, 254)
        for dx, dy in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)):
            px[x + dx, (y + dy) % 256] = hexc(cols[0] if (dx, dy) == (0, 0) else cols[1]) + (255,)
    return img


def sky_nebula(seed=2, cols=("e0c8ff", "a080e0", "6050a8")):
    rnd = random.Random(seed)
    img = Image.new("RGBA", (256, 256), (0, 0, 0, 0)); px = img.load()
    waves = [(rnd.uniform(0.02, 0.05), rnd.uniform(0.04, 0.09), rnd.random() * 6.28) for _ in range(4)]
    for y in range(256):
        for x in range(256):
            v = sum(math.sin(x * fx_ + math.sin(y * 2 * math.pi / 256 * 2 + p) * 3 + p) * math.sin(y * 2 * math.pi / 256 * (k + 1) + p * 2)
                    for k, (fx_, fy, p) in enumerate(waves)) / 4
            d = ((x * 3 + y * 2) % 4) / 8.0  # ordered dither
            if v + d > 0.72:
                px[x, y] = hexc(cols[0]) + (255,)
            elif v + d > 0.56:
                px[x, y] = hexc(cols[1]) + (255,)
            elif v + d > 0.44 and (x + y) % 2 == 0:
                px[x, y] = hexc(cols[2]) + (255,)
    for _ in range(40):
        x, y = rnd.randrange(256), rnd.randrange(256)
        if px[x, y][3] == 0:
            px[x, y] = (255, 255, 255, 255)
    return img


def sky_asteroids(seed=11, cols=("d8d0c0", "8c8070", "4c4438", "ffffff")):
    rnd = random.Random(seed)
    img = Image.new("RGBA", (256, 256), (0, 0, 0, 0)); px = img.load()
    for _ in range(60):
        px[rnd.randrange(256), rnd.randrange(256)] = hexc(cols[3]) + (255,)
    for _ in range(22):
        r = rnd.choice([2, 2, 3, 3, 4, 5, 6])
        cx, cy = rnd.randrange(8, 248), rnd.randrange(256)
        m = Image.new("L", (64 * S, 64 * S), 0)
        pts = []
        for k in range(12):
            a = 2 * math.pi * k / 12
            rr = r * rnd.uniform(0.7, 1.15)
            pts.append(((32 + rr * math.cos(a)) * S, (32 + rr * math.sin(a)) * S))
        ImageDraw.Draw(m).polygon(pts, fill=255)
        m = m.resize((64, 64), Image.BOX).point(lambda v: 255 if v >= 128 else 0)
        mp = m.load()
        for y in range(64):
            for x in range(64):
                if mp[x, y]:
                    lit = not mp[x - 1, y - 1] if x and y else True
                    dark = not mp[min(63, x + 1), min(63, y + 1)]
                    c = cols[0] if lit else cols[2] if dark else cols[1]
                    px[(cx + x - 32) % 256, (cy + y - 32) % 256] = hexc(c) + (255,)
    return img


SKY = {"stars": sky_stars, "nebula": sky_nebula, "asteroids": sky_asteroids}
