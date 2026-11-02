"""The style catalogue (wiki/mockup/styles.yaml) and per-area overrides (wiki/mockup/overrides/<area>.yaml)."""
import copy
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[3]
WORLD = ROOT / "wiki" / "world"
MOCK = ROOT / "wiki" / "mockup"


def hexrgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def shade(c, k):
    """k < 0 darkens, k > 0 lightens (fraction)."""
    if k < 0:
        return tuple(max(0, int(v * (1 + k))) for v in c)
    return tuple(min(255, int(v + (255 - v) * k)) for v in c)


class Styles:
    def __init__(self, path=MOCK / "styles.yaml"):
        raw = yaml.safe_load(open(path))
        self.raw = raw
        self.shapes = raw.get("shapes") or {}
        self.roles = raw.get("roles") or {}

    def terrain(self, planet):
        t = dict(self.raw["terrain"]["default"])
        t.update(self.raw["terrain"].get(planet) or {})
        kind = t.pop("nature_kind", "tree")
        return {k: hexrgb(v) for k, v in t.items()}, kind

    def material(self, planet):
        m = dict(self.raw["material"]["default"])
        m.update(self.raw["material"].get(planet) or {})
        return {k: hexrgb(v) for k, v in m.items()}

    def shape(self, art, planet, piece_kind):
        """Resolved style for one piece: its catalogue entry, filled in from the planet material."""
        s = dict(self.shapes.get(art) or {})
        mat = self.material(planet)
        if not s:
            s = {"kind": "box" if piece_kind == "building" else "slab", "unknown": True}
        out = {"kind": s["kind"], "label": s.get("label"), "form": s.get("form"), "big": s.get("big"),
               "tall": s.get("tall"), "count": s.get("count"), "mark": s.get("mark"), "unknown": s.get("unknown")}
        out["wall"] = hexrgb(s["wall"]) if "wall" in s else mat["wall"]
        out["roof"] = hexrgb(s["roof"]) if "roof" in s else mat["roof"]
        out["trim"] = hexrgb(s["trim"]) if "trim" in s else mat["trim"]
        out["fill"] = hexrgb(s["fill"]) if "fill" in s else mat["wall"]
        out["ring"] = hexrgb(s["ring"]) if "ring" in s else mat["trim"]
        return out


def load_area(path):
    return yaml.safe_load(open(path))


def apply_overrides(doc):
    """Phase 2 changes for one area, kept beside phase 1 instead of in it:
        hide:  [piece name, ...]            # drop pieces from the mockup only
        move:  {piece name: [x, y]}         # move a piece in the mockup only
        add:   {props: [...], buildings: [...], people: [...]}   # mockup-only extra dressing
        restyle: {piece name: art id}       # draw a piece as another catalogue entry
    """
    p = MOCK / "overrides" / f"{doc['id']}.yaml"
    doc = copy.deepcopy(doc)
    if not p.exists():
        return doc
    ov = yaml.safe_load(open(p)) or {}
    # a key is a piece name (every piece with that name) or "name#n" (the n-th one, counted from 1)
    def hit(keys, o, n):
        return next((keys[k] for k in (f"{o.get('name')}#{n}", o.get("name")) if k in keys), None)
    hide = {k: True for k in ov.get("hide") or []}
    for k in ("buildings", "props", "people", "signs", "warps"):
        seen, items = {}, []
        for o in doc.get(k) or []:
            n = seen[o.get("name")] = seen.get(o.get("name"), 0) + 1
            if hit(hide, o, n):
                continue
            mv, rs = hit(ov.get("move") or {}, o, n), hit(ov.get("restyle") or {}, o, n)
            if mv:
                o["at"] = list(mv)
            if rs:
                o["art"] = rs
            items.append(o)
        doc[k] = items + list((ov.get("add") or {}).get(k) or [])
    return doc
