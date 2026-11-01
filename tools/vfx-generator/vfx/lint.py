"""Style metrics and the style score.

`python -m vfx corpus` measures every vanilla VFX sheet the game actually loads and writes
corpus/style.json (per sheet, and the 5th-95th percentile band per group). A new sheet is scored
against its group's band and against the vanilla sheet it replaces: a FAIL names the rule and what to
change. STYLE.md explains each rule with examples.
"""
from __future__ import annotations

import colorsys
import json

import numpy as np

from . import catalog
from .draw import erode, neighbours
from .game import CORPUS, GAME
from .sheet import read_indexed, split_frames


def _luma(c):
    return 0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]


def _components(m: np.ndarray) -> int:
    seen = np.zeros_like(m, bool)
    h, w = m.shape
    count = 0
    for y in range(h):
        for x in range(w):
            if m[y, x] and not seen[y, x]:
                count += 1
                stack = [(y, x)]
                seen[y, x] = True
                while stack:
                    cy, cx = stack.pop()
                    for dy in (-1, 0, 1):
                        for dx in (-1, 0, 1):
                            ny, nx = cy + dy, cx + dx
                            if 0 <= ny < h and 0 <= nx < w and m[ny, nx] and not seen[ny, nx]:
                                seen[ny, nx] = True
                                stack.append((ny, nx))
    return count


def metrics(pix: np.ndarray, cols, frame, mw=1, mh=1, slots=None) -> dict:
    frames = split_frames(pix, frame[0], frame[1], mw, mh)
    if slots:
        frames = [frames[s] for s in slots if s < len(frames)]
    frames = [f for f in frames if (f > 0).any()]
    if not frames:
        return {"empty": True}
    lum = np.array([_luma(cols[i]) if i < len(cols) else 0 for i in range(256)])
    used, counts = np.unique(np.concatenate([f[f > 0] for f in frames]), return_counts=True)
    m = {"colours": int(len(used)), "frames": len(frames)}
    m["tiny_colours"] = int(sum(1 for c in counts if c < 3))
    cov, border, core, dark, lone, checker, clus = [], [], [], [], [], [], []
    for f in frames:
        o = f > 0
        area = o.size
        cov.append(o.sum() / area)
        b = np.zeros_like(o)
        b[0, :] = b[-1, :] = True
        b[:, 0] = b[:, -1] = True
        border.append((o & b).sum() / max(o.sum(), 1))
        e = o & ~erode(o)
        inner = o & ~e
        le, li = lum[f[e]], lum[f[inner]]
        core.append((li.mean() if li.size else (le.mean() if le.size else 0)) - (le.mean() if le.size else 0))
        dark.append((le < 64).mean() if le.size else 0)
        cnt = sum(n.astype(int) for n in neighbours(o, diag=True))
        lone.append((o & (cnt == 0)).sum() / max(o.sum(), 1))
        a, bb, c, d = f[:-1, :-1], f[:-1, 1:], f[1:, :-1], f[1:, 1:]
        win = (a > 0) & (bb > 0) & (c > 0) & (d > 0)
        chk = win & (a == d) & (bb == c) & (a != bb)
        checker.append(chk.sum() / max(win.sum(), 1))
        clus.append(_components(o))
    m["coverage"] = float(np.mean(cov))
    m["border"] = float(np.mean(border))
    m["core_bright"] = float(np.mean(core))
    m["dark_edge"] = float(np.mean(dark))
    m["lone"] = float(np.mean(lone))
    m["checker"] = float(np.mean(checker))
    m["clusters"] = float(np.mean(clus))
    ul = [_luma(cols[i]) for i in used]
    m["luma_range"] = float(max(ul) - min(ul)) if ul else 0.0
    sats = []
    for i, c in zip(used, counts):
        r, g, b_ = (v / 255 for v in cols[i][:3])
        sats += [colorsys.rgb_to_hsv(r, g, b_)[1]] * int(c)
    m["saturation"] = float(np.mean(sats)) if sats else 0.0
    if len(frames) > 1:
        deltas = [(frames[k] != frames[k + 1]).mean() for k in range(len(frames) - 1)]
        m["frame_delta"] = float(np.mean(deltas))
    return m


GROUPS = {"battle_anim_sprite": "battle_anim_sprite", "battle_anim_bg": "battle_anim_bg",
          "battle_anim_mask": "battle_anim_bg", "field_effect": "field_effect", "door": "door",
          "weather": "weather", "transition": "transition", "rotating_gate": "door", "new": "battle_anim_sprite"}


def corpus() -> dict:
    ents = catalog.load()["entries"]
    per, groups = {}, {}
    for e in ents.values():
        if not e.get("exists") or e.get("mode") != "P" or not e.get("frame"):
            continue
        if e["group"] == "battle_anim_unused":
            continue
        if e["kind"] == "battle_anims" and not e.get("users") and e["group"] == "battle_anim_sprite":
            continue        # never loaded: not part of the style
        try:
            pix, cols = read_indexed(GAME / e["path"])
            m = metrics(pix, cols, e["frame"], e.get("mwidth", 1), e.get("mheight", 1))
        except Exception as ex:   # noqa: BLE001
            m = {"error": str(ex)}
        if m.get("empty") or m.get("error"):
            continue
        per[e["id"]] = m
        groups.setdefault(GROUPS.get(e["group"], e["group"]), []).append(m)
    bands = {}
    for g, ms in groups.items():
        keys = sorted({k for m in ms for k in m if isinstance(m[k], (int, float))})
        bands[g] = {k: {"p5": float(np.percentile([m[k] for m in ms if k in m], 5)),
                        "p50": float(np.percentile([m[k] for m in ms if k in m], 50)),
                        "p95": float(np.percentile([m[k] for m in ms if k in m], 95)),
                        "n": sum(1 for m in ms if k in m)} for k in keys}
    data = {"sheets": per, "bands": bands}
    CORPUS.mkdir(parents=True, exist_ok=True)
    (CORPUS / "style.json").write_text(json.dumps(data, indent=1))
    return data


def load_corpus() -> dict:
    p = CORPUS / "style.json"
    return json.loads(p.read_text()) if p.exists() else corpus()


# rule: (metric, direction, severity, message). direction 'max' = must stay under p95, 'min' = over p5.
RULES = [
    ("tiny_colours", "max", "FAIL", "colours used by fewer than 3 pixels: stray noise colours. Merge them into a ramp step."),
    ("lone", "max", "WARN", "lone pixels (no opaque neighbour). Vanilla effects keep pixels in clusters; only sparks fly free."),
    ("checker", "max", "WARN", "checkerboard dithering. Emerald dithers only big glow edges; use hard bands."),
    ("dark_edge", "max", "WARN", "near-black edge pixels. Effects are rimmed in their own saturated dark step, not black."),
    ("core_bright", "min", "WARN", "the core is not brighter than the rim. Glows read as a white/pale core with a saturated edge."),
    ("luma_range", "min", "FAIL", "too little contrast between the lightest and darkest colours: it will vanish on the battle field."),
    ("coverage", "range", "WARN", "frame fill is outside what vanilla effects use (too empty or too packed)."),
    ("border", "max", "WARN", "art touches the frame edge: it will look clipped in game."),
]


def score(m: dict, group: str, vanilla: dict | None = None, allow: list[str] | None = None) -> tuple[int, list[str]]:
    bands = load_corpus()["bands"].get(GROUPS.get(group, group)) or {}
    allow = set(allow or [])
    lines, s = [], 100
    if m.get("empty"):
        return 0, ["FAIL  every frame is empty"]
    if m["colours"] > 15:
        s -= 30
        lines.append(f"FAIL  colours {m['colours']} > 15 (4bpp bank)")
    for key, direction, sev, msg in RULES:
        if key not in m or key not in bands:
            continue
        b = bands[key]
        v = m[key]
        van = vanilla.get(key) if vanilla else None
        hi = max(b["p95"], van if van is not None else -1e9)
        lo = min(b["p5"], van if van is not None else 1e9)
        bad = (direction == "max" and v > hi + 1e-9) or (direction == "min" and v < lo - 1e-9) or \
              (direction == "range" and (v > hi + 1e-9 or v < lo - 1e-9))
        ref = f"vanilla band {b['p5']:.2f}..{b['p95']:.2f}" + (f", replaced sheet {van:.2f}" if van is not None else "")
        if bad and key in allow:
            lines.append(f"ok    {key} {v:.2f} ({ref}) - allowed by spec")
        elif bad:
            s -= 15 if sev == "FAIL" else 5
            lines.append(f"{sev}  {key} {v:.2f} ({ref}): {msg}")
        else:
            lines.append(f"ok    {key} {v:.2f} ({ref})")
    return max(0, s), lines
