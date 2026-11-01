"""Guard rails: format rules (errors) and style metrics measured against Emerald (warnings).

Format rules come from how pokeemerald loads a walker (see README.md, "Format").
Style metrics are measured on all 90 vanilla 16x32 people walkers; a value outside the
corpus's 5th-95th percentile is a warning, because it means "no Emerald artist did this".
"""
from __future__ import annotations

import json
import statistics as st
from pathlib import Path

from . import palette as pal
from .spec import KITS

CORPUS_FILE = Path(__file__).resolve().parents[1] / "corpus" / "people16x32.json"

N4 = ((1, 0), (-1, 0), (0, 1), (0, -1))


def _opaque(g):
    return [(x, y) for y, row in enumerate(g) for x, v in enumerate(row) if v != 0]


def _edge(g, x, y):
    h, w = len(g), len(g[0])
    return any(not (0 <= x + dx < w and 0 <= y + dy < h) or g[y + dy][x + dx] == 0 for dx, dy in N4)


def frame_metrics(g, colours) -> dict:
    px = _opaque(g)
    if not px:
        return {"empty": True}
    xs = [p[0] for p in px]
    ys = [p[1] for p in px]
    edge = [(x, y) for x, y in px if _edge(g, x, y)]
    dark_edge = sum(1 for x, y in edge if pal.luma(colours[g[y][x]]) <= 100) / len(edge)
    h, w = len(g), len(g[0])
    orphans = sum(
        1
        for x, y in px
        if not any(0 <= x + dx < w and 0 <= y + dy < h and g[y + dy][x + dx] == g[y][x] for dx, dy in N4)
    )
    return {
        "top": min(ys),
        "feet": max(ys),
        "height": max(ys) - min(ys) + 1,
        "width": max(xs) - min(xs) + 1,
        "area": len(px),
        "dark_outline": round(dark_edge, 3),
        "orphans": round(orphans / len(px), 3),
    }


# Palette layout shared by the four NPC palettes (see STYLE.md section 2).
SKIN = (1, 2, 3, 4)
RAMPS = {"A": (5, 6, 7), "B": (8, 9, 10), "C": (11, 12, 13)}


def style_metrics(g) -> dict:
    """Emerald-specific conventions on one stand frame (indices, not colours): coloured outlines,
    full ramps, shadow weight, perspective (hair above the eyes), eye bars. See STYLE.md."""
    px = _opaque(g)
    if not px:
        return {}
    top = min(y for _, y in px)
    edge = [(x, y) for x, y in px if _edge(g, x, y)]
    inner = [(x, y) for x, y in px if (x, y) not in set(edge)]
    used = {g[y][x] for x, y in px}
    m = {
        "edge_black": round(sum(1 for x, y in edge if g[y][x] == 15) / len(edge), 3),
        "inner_black": round(sum(1 for x, y in inner if g[y][x] == 15) / max(1, len(inner)), 3),
        "skin_tones": len(used & set(SKIN)),
    }
    ramp_tones, dark_share = [], []
    for name, ramp in RAMPS.items():
        cnt = [sum(1 for x, y in px if g[y][x] == i) for i in ramp]
        if sum(cnt) >= 12:  # a ramp that is really used
            ramp_tones.append(sum(1 for c in cnt if c))
            dark_share.append(cnt[2] / sum(cnt))
    m["ramp_tones_min"] = min(ramp_tones) if ramp_tones else 0
    m["ramp_dark_share"] = round(min(dark_share), 3) if dark_share else 0
    skin_rows = [y for y in range(len(g)) if any(g[y][x] in SKIN[:3] for x in range(len(g[0])))]
    eyes = [(x, y) for x, y in px if g[y][x] == 15 and skin_rows and skin_rows[0] <= y < skin_rows[0] + 8]
    m["hair_rows"] = (skin_rows[0] - top) if skin_rows else 0
    m["eye_row"] = (min(y for _, y in eyes) - top) if eyes else -1
    widths = [sum(1 for v in row if v) for row in g]
    m["head_w"] = max(widths[top:top + 9])
    m["body_w"] = max(widths[top + 9:31]) if top + 9 < 31 else 0
    return m


def step_change(a, b) -> float:
    """Share of pixels that differ between two frames, over the union of opaque pixels."""
    union = diff = 0
    for ra, rb in zip(a, b):
        for va, vb in zip(ra, rb):
            if va or vb:
                union += 1
                diff += va != vb
    return diff / union if union else 0.0


def sheet_metrics(frames: dict, colours, kit="person16x32") -> dict:
    k = KITS[kit]
    stand = {n: frame_metrics(frames[n], colours) for n in k["stand"]}
    used = {v for g in frames.values() for row in g for v in row} - {0}
    steps = []
    if not k.get("still"):
        for seq in k["walk"].values():
            steps += [step_change(frames[seq[1]], frames[seq[0]]), step_change(frames[seq[1]], frames[seq[2]])]
    agg = {m: round(st.median(s[m] for s in stand.values()), 3) for m in ("top", "feet", "height", "width", "area", "dark_outline", "orphans")}
    agg["colours"] = len(used)
    agg["step_change"] = round(st.median(steps), 3) if steps else None
    # style conventions are judged on the facing-down frame (the one players see most)
    agg.update(style_metrics(frames[k["stand"][0]]))
    return {"stand": stand, "summary": agg}


def load_corpus() -> dict | None:
    return json.loads(CORPUS_FILE.read_text()) if CORPUS_FILE.exists() else None


def lint(frames: dict, colours, kit="person16x32") -> tuple[list[str], list[str], dict]:
    errors, warnings = [], []
    w, h = KITS[kit]["frame"]
    for n in KITS[kit]["order"]:
        g = frames[n]
        if len(g) != h or any(len(r) != w for r in g):
            errors.append(f"{n}: frame must be {w}x{h}")
    m = sheet_metrics(frames, colours, kit)
    if m["summary"]["colours"] > 15:
        errors.append(f"{m['summary']['colours']} colours used; a 4bpp sprite has 15 + transparent")
    for n, s in m["stand"].items():
        if s.get("empty"):
            errors.append(f"{n}: empty frame")
            continue
        if s["feet"] != h - 2:
            warnings.append(f"{n}: feet on row {s['feet']}, Emerald stands on row {h - 2} (shadow and grass overlap assume it)")
        if s["top"] < 8 and KITS[kit]["frame"] == (16, 32):
            warnings.append(f"{n}: art starts on row {s['top']}; vanilla people start on rows 10-15 (taller reads as a giant)")
    corpus = load_corpus()
    if corpus and KITS[kit]["frame"] == (16, 32):
        for key, v in m["summary"].items():
            if key not in corpus["p5"] or v is None:
                continue
            lo, hi = corpus["p5"][key], corpus["p95"][key]
            if not lo <= v <= hi:
                warnings.append(f"style: {key} = {v} is outside Emerald's p5-p95 range [{lo}, {hi}]")
    return errors, warnings, m


# Style rules (STYLE.md). Each is (metric, test against the corpus, weight, what to fix).
# A rule passes when the value is inside the corpus p5-p95 band, or meets the fixed bound.
STYLE_RULES = [
    ("edge_black", "max_p75", 25, "outline every material in its own dark ramp tone; black only on eyes, soles, creases (STYLE.md 1)"),
    ("inner_black", "max_p95", 5, "too much black inside the figure"),
    ("skin_tones", "min_p5", 10, "use all four skin tones: 1 light above the eyes, 2 base, 3 shade under the chin, 4 outline (STYLE.md 4)"),
    ("ramp_tones_min", "min_p25", 10, "every ramp you use needs its light, mid and dark tone (STYLE.md 2)"),
    ("ramp_dark_share", "min_p25", 10, "shade from above: the dark tone should carry ~40% of each ramp, at the bottom of every shape (STYLE.md 2)"),
    ("hair_rows", "min_p25", 10, "top-down view: hair/hat occupies several rows above the face (STYLE.md 3)"),
    ("eye_row", "min_p25", 5, "eyes sit on row ~7 from the top of the sprite (STYLE.md 3-4)"),
    ("head_w", "band", 5, "head should be ~14 wide (STYLE.md 3)"),
    ("height", "band", 5, "18-21 rows tall, feet on row 30 (STYLE.md 3)"),
    ("step_change", "min_p5", 10, "step frames should change ~70% of pixels: bob the body, swing both legs and the arms (STYLE.md 5)"),
    ("orphans", "band", 5, "add single-pixel highlights and creases; vanilla art is not flat"),
]


# Rules about pixel sizes only hold for the 16x32 people kit the corpus was measured on; the
# index-based rules (outline colour, ramps, shading, perspective) hold at any frame size.
SIZE_RULES = {"head_w", "height", "eye_row", "orphans"}


# Rules that assume a bare human face; a spec declares `accept:` with a reason to skip them
# (helmets, masks, droids, aliens without skin tones). Every accepted rule is printed, so a
# reviewer sees the claim.
FACE_RULES = {"skin_tones", "hair_rows", "eye_row"}


def score(summary: dict, corpus: dict | None = None, kit: str = "person16x32", accept: dict | None = None) -> tuple[int, list[tuple[str, bool, str]]]:
    """0-100 style score and the per-rule verdicts (name, passed, message). `accept` maps a rule
    name to the reason it does not apply to this character (e.g. no face under a helmet)."""
    corpus = corpus or load_corpus()
    accept = accept or {}
    if not corpus or "edge_black" not in corpus["p5"]:
        return 0, [("corpus", False, "run `python -m walker_sprite corpus` first")]
    got, total, verdicts = 0, 0, []
    for key, mode, weight, fix in STYLE_RULES:
        v = summary.get(key)
        if v is None or (KITS[kit]["frame"] != (16, 32) and key in SIZE_RULES):
            continue
        if key in accept:
            verdicts.append((key, True, f"{key} = {v}: accepted, {accept[key]}"))
            continue
        lo, hi = corpus["p5"][key], corpus["p95"][key]
        q1, q3 = corpus.get("p25", corpus["p5"])[key], corpus.get("p75", corpus["p95"])[key]
        ok = {"max_p95": v <= hi, "max_p75": v <= q3, "min_p5": v >= lo, "min_p25": v >= q1, "band": lo <= v <= hi}[mode]
        total += weight
        got += weight if ok else 0
        bound = {"max_p95": f"<= {hi}", "max_p75": f"<= {q3}", "min_p5": f">= {lo}", "min_p25": f">= {q1}", "band": f"{lo}..{hi}"}[mode]
        verdicts.append((key, ok, f"{key} = {v} (want {bound}; Emerald median {corpus['median'][key]}): {fix}"))
    return round(100 * got / total) if total else 0, verdicts


def build_corpus(emerald_dir: str | Path) -> dict:
    """Measure every vanilla 16x32 people walker (9-frame standard layout)."""
    from .sheet import read_frames

    order = KITS["person16x32"]["order"]
    rows = {}
    for f in sorted(Path(emerald_dir, "graphics/object_events/pics/people").rglob("*.png")):
        try:
            frames, colours = read_frames(f)
        except ValueError:
            continue
        if len(frames) != 9:
            continue
        rows[str(f.relative_to(emerald_dir))] = sheet_metrics(dict(zip(order, frames)), colours)["summary"]
    keys = next(iter(rows.values())).keys()

    def pct(vals, p):
        vals = sorted(vals)
        return vals[min(len(vals) - 1, max(0, round(p / 100 * (len(vals) - 1))))]

    out = {"count": len(rows), "p5": {}, "p25": {}, "median": {}, "p75": {}, "p95": {}, "sprites": rows}
    for k in keys:
        vals = [r[k] for r in rows.values()]
        for name, p in (("p5", 5), ("p25", 25), ("median", 50), ("p75", 75), ("p95", 95)):
            out[name][k] = round(pct(vals, p), 3)
    CORPUS_FILE.parent.mkdir(exist_ok=True)
    CORPUS_FILE.write_text(json.dumps(out, indent=1))
    return out
