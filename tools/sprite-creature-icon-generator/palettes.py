"""Fit 3 shared icon banks to the new creature fronts.

Every vanilla icon is redrawn, so the vanilla banks (tuned to Hoenn's bright greens, yellows and
blues) can be replaced. This groups the species into 3 banks and fits 15 colours to each group:
assign each species to the bank that draws it best, refit each bank to its members (k-means in
CIELAB, weighted by pixel count), repeat. Index 0 stays the vanilla transparent green.

    python3 palettes.py            # writes palettes/icon_palette_{0,1,2}.pal and palettes/assign.csv
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

import numpy as np

import icongen
from icongen import core

HERE = Path(__file__).resolve().parent
OUT = HERE / "palettes"
KEY = (98, 156, 131)


def sources():
    """(name, front, anim_front) for every species folder with an approved front."""
    base = icongen.ART / "graphics/pokemon"
    for front in sorted(base.rglob("front.png")):
        d = front.parent
        yield str(d.relative_to(base)), front, d / "anim_front.png"


def kmeans(px_lab, px_rgb, w, k, iters=25, seed=0):
    rng = np.random.default_rng(seed)
    # k-means++ seeding in Lab
    c = [px_lab[rng.choice(len(px_lab), p=w / w.sum())]]
    for _ in range(k - 1):
        d = np.min(((px_lab[:, None] - np.array(c)[None]) ** 2).sum(-1), 1) * w
        c.append(px_lab[rng.choice(len(px_lab), p=d / d.sum())])
    c = np.array(c)
    for _ in range(iters):
        a = np.argmin(((px_lab[:, None] - c[None]) ** 2).sum(-1), 1)
        for j in range(k):
            m = a == j
            if m.any():
                c[j] = np.average(px_lab[m], 0, w[m])
    rgb = []
    for j in range(k):
        m = a == j
        rgb.append(np.average(px_rgb[m], 0, w[m]) if m.any() else px_rgb[0])
    return [core.snap(tuple(int(round(v)) for v in col)) for col in rgb]


def unique_px(sheet):
    m = sheet[..., 3] > 0
    px = np.round(sheet[..., :3][m]).astype(int)
    u, n = np.unique(px, axis=0, return_counts=True)
    return u.astype(float), n.astype(float)


def bank_error(u, n, bank):
    _, d = core.nearest(u, np.array(bank[1:], float))
    return float((n * d ** 2).sum())


def fit(sheets: dict, rounds=10):
    names = list(sheets)
    data = {s: unique_px(sheets[s]) for s in names}
    # start: split by mean hue/lightness into 3 groups
    feats = np.array([core.to_lab(np.average(*data[s], axis=0)[None] if False else np.average(data[s][0], 0, data[s][1])[None])[0] for s in names])
    order = np.argsort(np.arctan2(feats[:, 2], feats[:, 1]))
    assign = {names[i]: (rank * 3) // len(names) for rank, i in enumerate(order)}
    banks = None
    best = (1e18, None, None)
    for r in range(rounds):
        banks = []
        for b in range(3):
            members = [s for s in names if assign[s] == b]
            u = np.concatenate([data[s][0] for s in members])
            # each species weighs the same, whatever its size
            n = np.concatenate([data[s][1] / data[s][1].sum() for s in members])
            cols = kmeans(core.to_lab(u), u, n, 15, seed=r)
            cols = sorted(set(cols), key=core.luma, reverse=True)
            while len(cols) < 15:
                cols.append(cols[-1])
            banks.append([KEY] + cols)
        new = {s: int(np.argmin([bank_error(*data[s], bk) for bk in banks])) for s in names}
        moved = sum(new[s] != assign[s] for s in names)
        tot = sum(bank_error(*data[s], banks[new[s]]) / data[s][1].sum() for s in names)
        print(f"round {r}: moved {moved}, mean error {tot / len(names):.1f}", flush=True)
        if tot < best[0]:
            best = (tot, banks, new)
        assign = new
        if moved == 0:
            break
    return best[1], best[2]


def main():
    sheets = {}
    for name, front, anim in sources():
        sheets[name] = icongen.make_icon(front, anim)
    vanilla = sum(bank_error(*unique_px(s), icongen.BANKS[icongen.best_bank(s[..., :3], s[..., 3] > 0)]) / unique_px(s)[1].sum() for s in sheets.values())
    print(f"vanilla banks: mean error {vanilla / len(sheets):.1f}")
    banks, assign = fit(sheets)
    OUT.mkdir(exist_ok=True)
    for b, bank in enumerate(banks):
        core.write_jasc(OUT / f"icon_palette_{b}.pal", bank)
    with open(OUT / "assign.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["species", "bank"])
        for s in sorted(assign):
            w.writerow([s, assign[s]])


if __name__ == "__main__":
    main()
