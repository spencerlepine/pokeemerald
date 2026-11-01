"""Stage 1: biome recolour. Re-theme a tileset pair by rewriting its palette banks, pixels untouched.

A recipe (YAML) is a list of **material rules** plus optional per-bank overrides. A rule matches the
*vanilla* colour (by LCh hue range, chroma and lightness) and says how to move it. Lightness is kept by
default so every ramp keeps its shading structure; hue and chroma are what make a biome.

```yaml
name: tatooine
rules:
  - name: ground            # the teal ground green and tufts
    match: {hue: [140, 170], chroma_min: 15}
    set:   {hue: 78, chroma: 26, light: +4}
  - name: canopy
    match: {hue: [75, 135], chroma_min: 20}
    set:   {hue: 85, chroma_scale: 0.55}
overrides:                  # bank-level exact values win over rules
  "general:5": {11: "#f0e0b0"}
skip_banks: ["general:4"]   # leave as is
```

A rule's `match` may add `banks: ["general:4"]` to act on named banks only, and `set` may use
`hue_by_light: [h_dark, h_light]` (hue follows lightness: lava, fire). `extends: base.yaml` makes a variant
whose rules are tried before the base recipe's.

`set` keys: `hue` (absolute degrees) or `hue_shift`; `chroma` (absolute) or `chroma_scale`; `light` (shift)
and `light_scale` (contrast about L=50). Colours no rule matches are kept. Results are snapped to GBA steps
and de-duplicated inside a bank (a duplicate is nudged 8 in L so two ramps never merge).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

from . import colour, gba

Colour = tuple[int, int, int]


@dataclass
class Rule:
    name: str
    hue: tuple[float, float] | None = None      # inclusive range, may wrap (350, 20)
    chroma_min: float = 0.0
    chroma_max: float = 1e9
    light_min: float = -1.0
    light_max: float = 101.0
    set: dict = field(default_factory=dict)
    banks: set[str] | None = None               # limit to banks, e.g. {"general:4"} (the water bank)

    def matches(self, lch, key: str | None = None) -> bool:
        if self.banks is not None and key not in self.banks:
            return False
        L, C, H = lch
        if C < self.chroma_min or C > self.chroma_max:
            return False
        if L < self.light_min or L > self.light_max:
            return False
        if self.hue is not None:
            a, b = self.hue
            if a <= b:
                if not (a <= H <= b):
                    return False
            else:
                if not (H >= a or H <= b):
                    return False
        return True

    def apply(self, lch):
        L, C, H = lch
        s = self.set
        if "hue" in s:
            H = float(s["hue"])
        if "hue_by_light" in s:                  # [hue at L=0, hue at L=100]: lava, fire, sunsets
            a, b = s["hue_by_light"]
            H = a + (b - a) * L / 100.0
        if "hue_shift" in s:
            H = (H + float(s["hue_shift"])) % 360
        if "chroma" in s:
            C = float(s["chroma"])
        if "chroma_scale" in s:
            C = C * float(s["chroma_scale"])
        if "light_scale" in s:
            L = 50 + (L - 50) * float(s["light_scale"])
        if "light" in s:
            L = L + float(s["light"])
        return np.array([np.clip(L, 0, 100), max(C, 0.0), H % 360])


@dataclass
class Recipe:
    name: str
    rules: list[Rule]
    overrides: dict[str, dict[int, Colour]] = field(default_factory=dict)
    skip_banks: set[str] = field(default_factory=set)
    notes: str = ""
    retexture: list[dict] = field(default_factory=list)   # stage 2 ops, see __main__._build_pair
    battle_rules: list[Rule] = field(default_factory=list)  # tried first on battle backgrounds only
    layout_edits: dict = field(default_factory=dict)        # layout name -> {metatile: metatile} swaps

    @staticmethod
    def load(path: Path) -> "Recipe":
        import yaml
        d = yaml.safe_load(Path(path).read_text())
        def parse(lst):
            out = []
            for r in lst or []:
                m = r.get("match", {})
                out.append(Rule(r.get("name", "?"), tuple(m["hue"]) if "hue" in m else None,
                                m.get("chroma_min", 0.0), m.get("chroma_max", 1e9),
                                m.get("light_min", -1.0), m.get("light_max", 101.0), r.get("set", {}),
                                set(m["banks"]) if "banks" in m else None))
            return out
        rules = parse(d.get("rules"))
        base = None
        if d.get("extends"):                    # a variant: its rules first, then the base recipe's
            base = Recipe.load(Path(path).parent / d["extends"])
            rules = rules + base.rules
        ov = dict(base.overrides) if base else {}
        for bank, entries in (d.get("overrides") or {}).items():
            ov[bank] = {int(k): colour.hex_to_rgb(v) for k, v in entries.items()}
        edits = {k: {int(a): int(b) for a, b in v.items()} for k, v in (d.get("layout_edits") or {}).items()}
        if base:
            return Recipe(d["name"], rules, ov, set(d.get("skip_banks") or []) | base.skip_banks,
                          d.get("notes", base.notes), d.get("retexture") or base.retexture,
                          parse(d.get("battle")) + base.battle_rules, {**base.layout_edits, **edits})
        return Recipe(d["name"], rules, ov, set(d.get("skip_banks") or []), d.get("notes", ""), d.get("retexture") or [],
                      parse(d.get("battle")), edits)

    def for_battle(self) -> "Recipe":
        return Recipe(self.name, self.battle_rules + self.rules, self.overrides, self.skip_banks, self.notes)


def recolour_bank(pal: list[Colour], recipe: Recipe, key: str, log: list[str] | None = None) -> list[Colour]:
    """One 16-entry bank -> new bank. Index 0 is kept (transparent / backdrop)."""
    trunc = lambda c: tuple((int(v) >> 3) << 3 for v in c)   # what gbagfx does to a vanilla value
    out: list[Colour] = [trunc(pal[0])]
    seen = {np.array(out[0], np.uint8).tobytes()}
    rgb = np.array(pal, dtype=np.float64)
    lch = colour.srgb_to_lch(rgb)
    overrides = recipe.overrides.get(key, {})
    for i in range(1, 16):
        # a vanilla duplicate (unused slot, or the same colour twice) stays a duplicate
        dup = next((j for j in range(1, i) if pal[j] == pal[i] and j not in overrides), None)
        if dup is not None and i not in overrides:
            out.append(out[dup])
            seen.add(np.array(out[-1], np.uint8).tobytes())
            if log is not None:
                log.append(f"{key}[{i:2d}] {colour.rgb_to_hex(pal[i])} -> {colour.rgb_to_hex(out[-1])}  (same as {dup})")
            continue
        if i in overrides:
            c = np.array(overrides[i], dtype=np.float64)
            why = "override"
        else:
            c = rgb[i]
            why = "kept"
            if key not in recipe.skip_banks:
                for r in recipe.rules:
                    if r.matches(lch[i], key):
                        c = colour.lch_to_srgb(r.apply(lch[i]))
                        why = r.name
                        break
        snapped = colour.gba_snap(c) if why != "kept" else np.array(trunc(c), np.uint8)
        # de-duplicate inside the bank by nudging lightness
        tries = 0
        while snapped.tobytes() in seen and tries < 6:
            l2 = colour.srgb_to_lch(snapped.astype(np.float64))
            l2[0] += 6 if l2[0] < 50 else -6
            snapped = colour.gba_snap(colour.lch_to_srgb(l2))
            tries += 1
        seen.add(snapped.tobytes())
        out.append(tuple(int(v) for v in snapped))
        if log is not None:
            log.append(f"{key}[{i:2d}] {colour.rgb_to_hex(pal[i])} -> {colour.rgb_to_hex(out[-1])}  ({why})")
    return out


def recolour_tileset(ts: gba.Tileset, recipe: Recipe, log: list[str] | None = None) -> gba.Tileset:
    banks = range(0, gba.NUM_PALS_IN_PRIMARY) if not ts.secondary else range(gba.NUM_PALS_IN_PRIMARY, gba.NUM_PALS_TOTAL)
    pals = [list(p) for p in ts.palettes]
    for b in banks:
        pals[b] = recolour_bank(ts.palettes[b], recipe, f"{ts.name}:{b}", log)
    return gba.Tileset(ts.name, ts.path, ts.secondary, ts.tiles, pals, ts.metatiles, ts.attributes)


def recolour_pair(pair: gba.TilesetPair, recipe: Recipe, log: list[str] | None = None) -> gba.TilesetPair:
    return gba.TilesetPair(recolour_tileset(pair.primary, recipe, log), recolour_tileset(pair.secondary, recipe, log))


def write_palettes(ts: gba.Tileset, out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    for i in range(16):
        gba.write_pal(out_dir / f"{i:02d}.pal", ts.palettes[i])
