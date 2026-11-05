"""Turn the approved titan sprites (sprites/final/*.png, 128x96 RGBA) into titans.data.js for the scene.

Each sprite is snapped to GBA colour steps (each channel truncated to a multiple of 8, as the game reads
it), then its rarest colours are merged into their nearest neighbour until it fits the bank entries it may
use. The data file holds, per titan, the palette (entry -> hex) and the rows as bank index characters
(0 = transparent). intro_legends.px.js includes it.

    python3 titans/export.py
"""
import json
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).parent
# Bank entries each titan may use. Bank 1 / 2 entry 15 is the glow intro.c pulses; bank 5 entries
# 8, 12, 13 and 14 are flashed by intro.c (13 is the sky band), so the EXOGORTH keeps off them.
SLOTS = {
    "krayt": list(range(1, 15)),
    "sando": list(range(1, 15)),
    "exogorth": [1, 2, 3, 4, 5, 6, 7, 9, 10, 11, 15],
}


def export(name, slots):
    a = np.array(Image.open(HERE / "sprites/final" / f"{name}.png").convert("RGBA"))
    op = a[..., 3] > 0
    rgb = (a[..., :3] // 8 * 8).astype(int)
    cols, inv, cnt = np.unique(rgb[op], axis=0, return_inverse=True, return_counts=True)
    cols = [tuple(c) for c in cols]
    lab = np.full(op.shape, -1)
    lab[op] = inv.ravel()
    cnt = list(cnt)
    alive = set(range(len(cols)))
    while len(alive) > len(slots):
        r = min(alive, key=lambda i: cnt[i])
        alive.discard(r)
        n = min(alive, key=lambda i: sum((np.array(cols[i]) - cols[r]) ** 2))
        lab[lab == r] = n
        cnt[n] += cnt[r]
    # darkest first, so the palette reads in order
    order = sorted(alive, key=lambda i: sum(cols[i]))
    slot = {i: slots[k] for k, i in enumerate(order)}
    pal = {slots[k]: "#%02x%02x%02x" % cols[i] for k, i in enumerate(order)}
    rows = ["".join("0" if v < 0 else "%x" % slot[v] for v in row) for row in lab]
    return {"pal": pal, "rows": rows}


data = {n: export(n, s) for n, s in SLOTS.items()}
out = "// Written by titans/export.py from titans/sprites/final/*.png. Do not edit.\nvar TITANS = " + json.dumps(data, indent=1) + "\n"
(HERE / "titans.data.js").write_text(out)
for n, d in data.items():
    print(n, len(d["pal"]), "colours", d["pal"])
