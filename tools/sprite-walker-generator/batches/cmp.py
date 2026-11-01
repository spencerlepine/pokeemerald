"""Side-by-side critique sheet for one spec: every frame, vanilla above, new below, at 8x, plus a
1x and 2x strip on grass.  python batches/cmp.py <name> [out.png]"""
import sys, yaml
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from PIL import Image, ImageDraw
from walker_sprite import palette as palm
from walker_sprite.spec import KITS
T = Path(__file__).resolve().parents[1]
G = T.parents[1] / "game/graphics/object_events"
GR = (115, 197, 164)
PALTAG = {"groudon": "groudon", "kyogre": "kyogre", "lugia": "lugia", "ho_oh": "ho_oh", "deoxys": "deoxys",
          "vigoroth": "vigoroth", "poochyena": "poochyena", "enemy_zigzagoon": "enemy_zigzagoon",
          "rayquaza": "npc_3", "rayquaza_still": "npc_3", "latias_latios": "npc_2", "regi": "npc_2"}

def rgba(path, palf):
    im = Image.open(path); idx = im.load(); cols = palm.load_jasc(palf)
    o = Image.new("RGBA", im.size, (0, 0, 0, 0)); p = o.load()
    for y in range(im.height):
        for x in range(im.width):
            if idx[x, y]:
                p[x, y] = tuple(cols[idx[x, y]]) + (255,)
    return o

name = sys.argv[1]
d = yaml.safe_load(open(T / f"art/{name}.yaml"))
fs = KITS[d.get("kit", "person16x32")]["frame"][0]
van_path = G / "pics" / Path(d["replaces"]).relative_to("graphics/object_events/pics")
vp = PALTAG.get(Path(d["replaces"]).stem, "npc_1")
van = rgba(van_path, G / f"palettes/{vp}.pal")
new = rgba(T / f"output/{name}/{name}.png", T / f"palettes/{d['palette']}.pal")
n = new.width // fs
Z = 8
im = Image.new("RGB", (20 + n * (fs * Z + 8), 30 + 2 * (fs * Z + 8) + fs * 3 + 40), (24, 24, 30))
dr = ImageDraw.Draw(im)
dr.text((10, 6), f"{name}: vanilla (top) vs new (bottom), {Z}x; then 1x and 2x on grass", fill=(220, 220, 220))
for j, src in enumerate((van, new)):
    for i in range(min(n, src.width // fs)):
        f = src.crop((i * fs, 0, (i + 1) * fs, fs))
        bg = Image.new("RGBA", (fs, fs), GR + (255,)); bg.alpha_composite(f)
        im.paste(bg.resize((fs * Z, fs * Z), Image.NEAREST), (10 + i * (fs * Z + 8), 24 + j * (fs * Z + 8)))
y = 24 + 2 * (fs * Z + 8) + 6
strip = Image.new("RGBA", ((2 * n + 1) * (fs + 2), fs + 4), GR + (255,))
for i in range(n):
    strip.alpha_composite(van.crop((i * fs, 0, (i + 1) * fs, fs)), (2 + i * (fs + 2), 2))
    strip.alpha_composite(new.crop((i * fs, 0, (i + 1) * fs, fs)), (2 + (n + 1 + i) * (fs + 2), 2))
im.paste(strip, (10, y)); im.paste(strip.resize((strip.width * 2, strip.height * 2), Image.NEAREST), (20 + strip.width, y))
out = sys.argv[2] if len(sys.argv) > 2 else str(T / f"output/{name}/preview/cmp.png")
im.save(out); print(out)
