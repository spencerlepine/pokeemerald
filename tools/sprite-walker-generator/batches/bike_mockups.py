"""Hover bike mockups: 3 speeder (Acro Bike) + 3 swoop (Mach Bike) concepts, side/front/back,
drawn inside the vanilla bicycle footprint and composited under the shipped Kael and Mira riders."""
from PIL import Image, ImageDraw
import sys
ROOT = "/home/claude/pokeemerald/"
L = {".": 0, "W": 14, "a": 5, "b": 6, "c": 7, "d": 8, "e": 9, "f": 10, "g": 11, "h": 12, "i": 13, "K": 15}
# side view: 26 wide, placed at x=3, bottom row = 31 (facing left: nose on the left)
# front (facing down) / back (facing up): 14 wide, placed at x=9, bottom row = 31
B = {}
B["speeder_A"] = dict(title="Speeder A: Endor 74-Z (long boom, twin front vanes)", side="""
cc........................
Wc........................
WWc.......................
Wbccccccccccccccccccccccc.
WbaaaaaaaaWWWWWWWWWWWWWWbc
bcc......cbbbbbbbbbbbbbbbc
cc........ccccccccccccccci
....................cc.cc.
""", front="""
cc..........cc
Wc...cccc...Wc
Wbc.cWWWWc.cWb
Wbcc.cbbc.ccWb
bc...cbbc...cb
cc...cccc...cc
......ihhi....
""", back="""
cc..........cc
Wc..cccccc..Wc
Wbccbbbbbbccbc
bc..cWWWWc..cb
cc..cbiibc..cc
.....chhc.....
......ii......
""")
B["speeder_B"] = dict(title="Speeder B: compact scout (short boom, big vanes, blue thrusters)", side="""
ccc.......................
WWbc......................
WWbc...........ccccccc....
WWbccccccccccccWWWWWWbcc..
WbbaaaaaaaaaaaaaaaaaaabWic
bbcc..........cbbbbbbbcgic
ccc............ccccccccci.
..........................
""", front="""
ccc........ccc
WWbc.cccc.cWWb
WWbccWWWWccWWb
WbbccbaabccbbW
bbcc.cbbc.ccbb
ccc..cccc..ccc
..............
""", back="""
ccc........ccc
WWbc......cWWb
WWbcccccccccbb
Wbbc.cWWc.cbbW
bbcc.ciic.ccbb
ccc..chhc..ccc
......ii......
""")
B["speeder_C"] = dict(title="Speeder C: sport (single nose vane, sleek wedge, rear fin)", side="""
..........................
cc...................cc...
Wc..................cWc...
WbcccccccccccccccccccWbc..
WbaaaaaWWWWWWWWWWWWWWWbbc.
bc.cccccbbbbbbbbbbbbbbbbc.
c.......cccccccccccccccchg
.......................ih.
""", front="""
.....cccc.....
....cWWWWc....
...cWWWWWWc...
..cbaaWWaabc..
...cbbbbbbc...
....cccccc....
.....ihhi.....
""", back="""
......cc......
.....cWWc.....
...ccWWWWcc...
..cbbbbbbbbc..
...cbihhibc...
....cccccc....
.....ihhi.....
""")
B["swoop_A"] = dict(title="Swoop A: big engine pod up front, rider behind", side="""
...cfff...................
..fddddf..................
.fdgggddfffffffffff.......
fdhgigdddddddddddddff.....
fdgigddeeeeeeeeeeeeedf....
.fdddeeffffffffffffeef....
..fffff..........fffhgi...
..........................
""", front="""
....ffffff....
...fddddddf...
..fdghhhgdf...
..fdhiiihdf...
..fdghhhgdf...
...feeeeef....
....ffffff....
""", back="""
....ffffff....
...fddddddf...
..fdeeeeeedf..
..fefhiihfef..
...ffhiihff...
....fgiigf....
.....hiih.....
""")
B["swoop_B"] = dict(title="Swoop B: twin stacked engines, sand trim", side="""
.ffff.....................
fddddff...................
fdgidddfffffffffffff......
.fffffaaaaaaaaaaaaaaaf....
fddddddddddddddddddddef...
fdgidddeeeeeeeeeeeeeeef...
.ffffffffffffffffffffgh...
.....................ih...
""", front="""
...ffff.ffff..
..fddddfddddf.
..fdhidfdhidf.
..fdiidfdiidf.
..faaaaaaaaaf.
...feeeeeeef..
....fffffff...
""", back="""
...ffff.ffff..
..fddddfddddf.
..faaaaaaaaaf.
..fehhefehhef.
..fhiihfhiihf.
...fhhf.fhhf..
....ii...ii...
""")
B["swoop_C"] = dict(title="Swoop C: racing wedge with handlebar horns and tail fin", side="""
...f......................
..fdf...............ff....
..fdfffff..........fdf....
.fddddddddfffffffffddf....
fdgiddddddddddddddddddff..
fdhiaaaaaaaaaaaaaaaaaeef..
.fffeeeeeeeeeeeeeeeeefhg..
....ffffffffffffffffff.ih.
""", front="""
.f..........f.
fdf.ffffff.fdf
.fdfddddddfdf.
..fdghhhhgdf..
..fdhiiiihdf..
...faaaaaaf...
....ffffff....
""", back="""
.f....ff....f.
fdf..fddf..fdf
.fdffddddffdf.
..fddeeeeddf..
..fdfhiihfdf..
...ffhiihff...
.....ihhi.....
""")

def grid(t):
    return [r for r in t.strip("\n").split("\n")]

def rgba(png):
    im = Image.open(png); idx = im.load(); out = im.convert("RGBA"); px = out.load()
    for y in range(im.height):
        for x in range(im.width):
            if idx[x, y] == 0:
                px[x, y] = (0, 0, 0, 0)
    return im, out

def load_pal(name):
    rows = open(ROOT + f"tools/sprite-walker-generator/palettes/{name}.pal").read().split()[3:]
    v = list(map(int, rows)); return [tuple(v[i:i+3]) for i in range(0, 48, 3)]

def frame_with_bike(who, pal, view, g):
    """Shipped rider frame (mach_bike sheet: 0 down, 1 up, 2 left), old hull cleared, new bike drawn."""
    im = Image.open(ROOT + f"wiki/art/graphics/object_events/pics/people/{who}/mach_bike.png")
    px = im.load(); f = {"front": 0, "back": 1, "side": 2}[view]
    fr = [[px[f * 32 + x, y] for x in range(32)] for y in range(32)]
    clear_from = {"front": 26, "back": 29, "side": 25}[view]
    for y in range(clear_from, 32):
        fr[y] = [0] * 32
    x0 = 3 if view == "side" else 9
    rows = grid(g)
    y0 = 32 - len(rows)
    for j, r in enumerate(rows):
        for i, ch in enumerate(r):
            if ch != ".":
                fr[y0 + j][x0 + i] = L[ch]
    out = Image.new("RGBA", (32, 32), (0, 0, 0, 0)); o = out.load()
    for y in range(32):
        for x in range(32):
            if fr[y][x]:
                o[x, y] = pal[fr[y][x]] + (255,)
    return out

def bike_only(pal, g, w):
    rows = grid(g)
    out = Image.new("RGBA", (w, 8), (0, 0, 0, 0)); o = out.load()
    for j, r in enumerate(rows):
        for i, ch in enumerate(r):
            if ch != ".":
                o[i, 8 - len(rows) + j] = pal[L[ch]] + (255,)
    return out

kael, mira = load_pal("kael"), load_pal("mira")
GR = (115, 197, 164)
Z = 4
order = ["speeder_A", "speeder_B", "speeder_C", "swoop_A", "swoop_B", "swoop_C"]
cellw = 32 * Z + 6
rowh = 20 + 32 * Z + 8 + 8 * Z + 16
W = 10 + 7 * cellw + 260
im = Image.new("RGB", (W, 40 + len(order) * rowh), (24, 24, 30)); d = ImageDraw.Draw(im)
d.text((10, 8), "Hover bike mockups. Per concept: Kael down / up / left, Mira down / up / left, then the bike alone (Kael colours) and a 1x strip.", fill=(220, 220, 220))
y = 30
for k in order:
    b = B[k]
    for v in ("side", "front", "back"):
        rows = grid(b[v]); w = 26 if v == "side" else 14
        assert all(len(r) == w for r in rows), (k, v, [len(r) for r in rows])
    d.text((10, y), b["title"], fill=(240, 240, 240))
    x = 10
    tiles = []
    for who, pal in (("brendan", kael), ("may", mira)):
        for v in ("front", "back", "side"):
            t = frame_with_bike(who, pal, v, b[v]); tiles.append(t)
            bg = Image.new("RGBA", (32, 32), GR + (255,)); bg.alpha_composite(t)
            im.paste(bg.resize((32 * Z, 32 * Z), Image.NEAREST), (x, y + 16)); x += cellw
            if v == "side": x += 8
    # bike alone
    bx = x
    for v, w in (("side", 26), ("front", 14), ("back", 14)):
        t = bike_only(kael, b[v], w)
        bg = Image.new("RGBA", (w, 8), GR + (255,)); bg.alpha_composite(t)
        im.paste(bg.resize((w * 3, 24), Image.NEAREST), (bx, y + 16)); bx += w * 3 + 6
    # 1x strip on grass
    strip = Image.new("RGBA", (6 * 34 + 4, 36), GR + (255,))
    for i, t in enumerate(tiles):
        strip.alpha_composite(t, (2 + i * 34, 2))
    im.paste(strip, (x, y + 16 + 40)); im.paste(strip.resize((strip.width * 2, 72), Image.NEAREST), (x - 0, y + 16 + 80)) if False else None
    y += rowh
out = sys.argv[1] if len(sys.argv) > 1 else "/mnt/project-files/walkers/hover-bike-mockups.png"
im.save(out); print(out, im.size)
