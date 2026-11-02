"""Palettes (tools/greybox/palettes.yaml), per-art colour overrides (tools/greybox/styles.yaml) and the asset list
(wiki/mapping/world_art.csv), resolved into one style dict per piece."""
import csv
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[3]
WORLD = ROOT / "wiki" / "world"
HERE = Path(__file__).resolve().parents[1]
OUT = WORLD / "greybox"
ASSETS = ROOT / "wiki" / "mapping" / "world_art.csv"


def hexrgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def shade(c, k):
    """k < 0 darkens, k > 0 lightens (fraction)."""
    if k < 0:
        return tuple(max(0, int(v * (1 + k))) for v in c)
    return tuple(min(255, int(v + (255 - v) * k)) for v in c)


class Styles:
    def __init__(self):
        self.raw = yaml.safe_load(open(HERE / "palettes.yaml"))
        self.shapes = (yaml.safe_load(open(HERE / "styles.yaml")) or {}).get("shapes") or {}
        self.roles = self.raw.get("roles") or {}
        self.assets = {r["concept_id"]: r for r in csv.DictReader(open(ASSETS))}

    def terrain(self, planet):
        t = dict(self.raw["terrain"]["default"])
        t.update(self.raw["terrain"].get(planet) or {})
        kind = t.pop("nature_kind", "tree")
        return {k: hexrgb(v) for k, v in t.items()}, kind

    def material(self, planet):
        m = dict(self.raw["material"]["default"])
        m.update(self.raw["material"].get(planet) or {})
        return {k: hexrgb(v) for k, v in m.items()}

    def shape(self, art, planet, piece_kind, seed=None):
        """Resolved style for one piece: its catalogue entry, filled in from the planet material.
        `variants` (a list of partial entries) picks one by `seed`, so the same art can vary per spot."""
        s = dict(self.shapes.get(art) or {})
        mat = self.material(planet)
        if not s:
            s = {"kind": "box" if piece_kind == "building" else "slab", "unknown": True}
        row = self.assets.get(art)
        if row and row.get("build"):        # the wiki decides the model
            s["build"] = row["build"]
            s.pop("unknown", None)
            if row.get("variants"):
                s["variants"] = [{"build": row["build"]}] + [{"build": b} for b in row["variants"].split()]
        vs = s.pop("variants", None)
        if vs and seed is not None:
            s.update(vs[seed % len(vs)])
        out = dict(s)
        out.setdefault("kind", "box")
        for k in ("label", "form", "big", "tall", "count", "mark", "unknown"):
            out.setdefault(k, None)
        out["wall"] = hexrgb(s["wall"]) if "wall" in s else mat["wall"]
        out["roof"] = hexrgb(s["roof"]) if "roof" in s else mat["roof"]
        out["trim"] = hexrgb(s["trim"]) if "trim" in s else mat["trim"]
        out["fill"] = hexrgb(s["fill"]) if "fill" in s else mat["wall"]
        out["ring"] = hexrgb(s["ring"]) if "ring" in s else mat["trim"]
        for k, v in list(out.items()):      # any other colour key (field, rock, glass)
            if isinstance(v, str) and v.startswith("#"):
                out[k] = hexrgb(v)
        return out


def load_area(path):
    return yaml.safe_load(open(path))
