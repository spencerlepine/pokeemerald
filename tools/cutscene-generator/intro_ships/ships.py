"""Ship silhouette mockups for the intro's scene-1 fly-by sprite (64x32, one colour, like flygon.png)."""
from PIL import Image, ImageDraw
import math
S = 8; W, H = 64, 32
COL = (56, 48, 64)

def canvas():
    im = Image.new("L", (W * S, H * S), 0); return im, ImageDraw.Draw(im)

def P(pts): return [(x * S, y * S) for x, y in pts]
def rect(d, x0, y0, x1, y1): d.rectangle([x0 * S, y0 * S, x1 * S - 1, y1 * S - 1], fill=255)
def ell(d, cx, cy, rx, ry): d.ellipse([(cx - rx) * S, (cy - ry) * S, (cx + rx) * S, (cy + ry) * S], fill=255)
def poly(d, pts): d.polygon(P(pts), fill=255)
def line(d, a, b, w): d.line(P([a, b]), fill=255, width=int(w * S))

def finish(im):
    small = im.resize((W, H), Image.BOX).point(lambda v: 255 if v >= 110 else 0)
    return small

# ---------------- hero ships ----------------
def xwing_front():      # S-foils open, seen head-on: an X with engines and cannons
    im, d = canvas()
    cx, cy = 32, 16
    for sx in (-1, 1):
        for sy in (-1, 1):
            line(d, (cx, cy), (cx + sx * 22, cy + sy * 10), 2.2)
            ell(d, cx + sx * 9, cy + sy * 4, 2.6, 2.6)               # engines
            rect(d, cx + sx * 22 - 0.6, cy + sy * 10 - 3 if sy < 0 else cy + sy * 10 - 1, cx + sx * 22 + 0.7, cy + sy * 10 + 1 if sy < 0 else cy + sy * 10 + 3)  # cannon tips
    ell(d, cx, cy, 3.2, 3.2)
    return finish(im)

def xwing_top():        # top view, nose up: long nose, wings swept back, cannons forward
    im, d = canvas()
    poly(d, [(31.2, 0.5), (32.8, 0.5), (35, 16), (35.5, 30), (28.5, 30), (29, 16)])
    for s in (-1, 1):
        poly(d, [(32 + s * 3, 17), (32 + s * 25, 21), (32 + s * 25, 26), (32 + s * 3, 28)])
        line(d, (32 + s * 25, 9), (32 + s * 25, 27), 2.0)
        ell(d, 32 + s * 6.5, 25, 2.6, 4.5)
    return finish(im)

def awing():            # wedge
    im, d = canvas()
    poly(d, [(32, 2), (52, 26), (52, 29), (12, 29), (12, 26)])
    for s in (-1, 1):
        rect(d, *(sorted([32 + s * 20, 32 + s * 22])[0:1] + [14] + sorted([32 + s * 20, 32 + s * 22])[1:] + [29]))
        ell(d, 32 + s * 9, 28.5, 3.5, 2)
    return finish(im)

def ywing():            # long cockpit pod + two engine nacelles
    im, d = canvas()
    ell(d, 32, 7, 5, 5)
    rect(d, 29.5, 7, 34.5, 14)
    rect(d, 14, 12, 50, 15)
    for s in (-1, 1):
        x = 32 + s * 14
        rect(d, x - 2.2, 8, x + 2.2, 30)
        ell(d, x, 9, 2.6, 3)
    rect(d, 30.5, 14, 33.5, 22)
    return finish(im)

def freighter():        # light freighter: disc, two forward mandibles, side cockpit
    im, d = canvas()
    ell(d, 30, 19, 16, 11.5)
    poly(d, [(20, 12), (26, 12), (26, 1), (22, 1)])
    poly(d, [(34, 12), (40, 12), (38, 1), (34, 1)])
    rect(d, 45, 12, 52, 15)
    ell(d, 53, 13.5, 3, 2.3)
    rect(d, 24, 28, 36, 31)
    return finish(im)

def bwing_front():      # cross-shaped wing seen from the front
    im, d = canvas()
    rect(d, 6, 14, 58, 18)
    rect(d, 30, 1, 34, 31)
    ell(d, 32, 16, 5, 5)
    for x in (6, 58):
        rect(d, x - 1.5, 12, x + 1.5, 20)
    rect(d, 28.5, 1, 35.5, 4)
    return finish(im)

# ---------------- imperial ships ----------------
def tie_fighter():      # front view: two hexagon panels, ball cockpit
    im, d = canvas()
    for s in (-1, 1):
        x = 32 + s * 17
        poly(d, [(x - 3.5, 1), (x + 3.5, 1), (x + 5, 16), (x + 3.5, 31), (x - 3.5, 31), (x - 5, 16)])
    rect(d, 17, 14.5, 47, 17.5)
    ell(d, 32, 16, 6.5, 6.5)
    return finish(im)

def tie_interceptor():  # front view: dagger-tipped wings
    im, d = canvas()
    for s in (-1, 1):
        x = 32 + s * 16
        poly(d, [(x + s * 7.5, 0), (x + s * 1, 13), (x + s * 1, 19), (x + s * 7.5, 32), (x + s * 3.5, 32), (x - s * 2.5, 19), (x - s * 2.5, 13), (x + s * 3.5, 0)])
    rect(d, 16, 14.5, 48, 17.5)
    ell(d, 32, 16, 6, 6)
    return finish(im)

def tie_advanced():     # bent solar wings + ball with tail
    im, d = canvas()
    for s in (-1, 1):
        x = 32 + s * 15
        poly(d, [(x - s * 4, 4), (x + s * 7, 0), (x + s * 7, 32), (x - s * 4, 28), (x - s * 4, 19), (x + s * 0, 17), (x + s * 0, 15), (x - s * 4, 13)])
    rect(d, 20, 14.5, 44, 17.5)
    ell(d, 32, 16, 6.5, 6.5)
    rect(d, 30, 16, 34, 24)
    return finish(im)

def star_destroyer():   # top view dagger, nose up
    im, d = canvas()
    poly(d, [(32, 0.5), (54, 26), (54, 30), (10, 30), (10, 26)])
    poly(d, [(27, 18), (37, 18), (39, 24), (25, 24)])                  # superstructure
    rect(d, 24, 23, 40, 27)
    rect(d, 29, 13, 35, 18)
    for x in (20, 32, 44):
        ell(d, x, 30.5, 3.2, 1.6)
    return finish(im)

def lambda_shuttle():   # front view: tall fin, two folded-down wings
    im, d = canvas()
    poly(d, [(30.5, 0.5), (33.5, 0.5), (34.5, 20), (29.5, 20)])        # dorsal fin
    poly(d, [(26, 14), (38, 14), (39, 22), (25, 22)])                  # body
    for s in (-1, 1):
        poly(d, [(32 + s * 6, 15), (32 + s * 7.5, 15), (32 + s * 18, 31.5), (32 + s * 16, 31.5)])
    ell(d, 32, 21, 5, 3.5)
    return finish(im)

HERO = [("X-wing (front)", xwing_front), ("X-wing (top)", xwing_top), ("A-wing", awing), ("Y-wing", ywing), ("Light freighter", freighter)]
IMP = [("TIE fighter", tie_fighter), ("TIE interceptor", tie_interceptor), ("TIE advanced", tie_advanced), ("Star Destroyer", star_destroyer), ("Lambda shuttle", lambda_shuttle)]
