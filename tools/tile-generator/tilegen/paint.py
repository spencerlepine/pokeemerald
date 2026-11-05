"""Paint: the Star Wars colours of every planet's ground, paths, rock and liquids (2026-11-05, prototype).

Pixels stay vanilla. Each palette colour of a tileset is sorted into a **class** by what it draws in Emerald
(ground green, foliage, water, cliff rock, dirt path, sand, roof red, grey stone) and then **snapped** to a
tone of the material the planet gives that class. Materials are fixed 5-tone ramps shared by the whole game
(`MATERIALS`, dark to light), so every planet draws from one small world palette (rules in
`wiki/bible/PALETTE.md`, "World terrain").

A colour keeps its place in its class's light range: the darkest vanilla grass becomes tone 0 of the planet's
ground, the lightest tone 4. Achromatic whites in a water bank are foam and take the liquid's top tone.

A planet has variants (`PLANETS[planet][variant]`). A net-new item (the Dune Sea, mud, cloud, deck...) is drawn
with a vanilla item's tiles and its own class overrides (`ITEM_PAINT`), e.g. the Dune Sea is the vanilla sea
with water painted as dune sand.
"""
from __future__ import annotations

import numpy as np

from . import colour, gba

# 5 tones, dark to light; every channel a multiple of 8 (GBA-exact)
MATERIALS = {
    # sand and stone
    "dune":       ["#886038", "#B08850", "#D0A868", "#E8C888", "#F8E0B0"],
    "hardpan":    ["#704830", "#986848", "#B88860", "#D0A878", "#E8C8A0"],
    "canyon":     ["#583028", "#804838", "#A86848", "#C88860", "#E0B088"],
    "sandstone":  ["#605048", "#807060", "#A09078", "#C0B098", "#E0D0B8"],
    "temple":     ["#383830", "#585848", "#787860", "#989880", "#B8B8A0"],
    # cold
    "snow":       ["#6878A0", "#98A8C8", "#C0D0E0", "#E0E8F0", "#F8F8F8"],
    "slush":      ["#485870", "#687890", "#8898B0", "#A8B8D0", "#C8D8E8"],
    "ice":        ["#305888", "#4880B0", "#70A8D0", "#A0D0E8", "#D0F0F8"],
    "frostrock":  ["#384058", "#586078", "#788898", "#A0B0C0", "#C8D8E0"],
    "crystal":    ["#202850", "#304880", "#5070B0", "#80A8D8", "#C0E0F8"],
    # fire
    "ash":        ["#302828", "#484040", "#686060", "#888080", "#A8A0A0"],
    "basalt":     ["#201818", "#382828", "#504040", "#706058", "#908078"],
    "ember":      ["#581810", "#883020", "#B04828", "#D07040", "#E89860"],
    "lava":       ["#701808", "#B83010", "#E86818", "#F8A830", "#F8E878"],
    "sulphur":    ["#004048", "#106868", "#309088", "#60B8A8", "#A0D8C8"],
    # green
    "moss":       ["#283818", "#385820", "#507830", "#709848", "#98B868"],
    "jungle":     ["#204018", "#306828", "#489038", "#70B050", "#A0D070"],
    "canopy":     ["#102818", "#184828", "#286838", "#409050", "#68B870"],
    "scrub":      ["#383818", "#585828", "#807840", "#A09858", "#C8C080"],
    "evergreen":  ["#183838", "#285858", "#407878", "#68A0A0", "#A0C8C8"],
    "loam":       ["#482818", "#683828", "#905038", "#B07050", "#C89068"],
    "forestfloor": ["#283018", "#405020", "#587030", "#789040", "#98B060"],
    "bark":       ["#382018", "#583020", "#784830", "#986040", "#B88058"],
    # swamp
    "bogmoss":    ["#283020", "#404830", "#586040", "#788058", "#98A078"],
    "mud":        ["#282018", "#403028", "#584838", "#786050", "#988068"],
    "bogwater":   ["#102010", "#203828", "#385040", "#507058", "#709078"],
    # liquids
    "clearwater": ["#183868", "#2858A0", "#4880C8", "#70A8E0", "#A8D0F0"],
    "river":      ["#103850", "#206078", "#388898", "#60B0B8", "#98D8D0"],
    "stormsea":   ["#102038", "#203850", "#385868", "#587888", "#8098A8"],
    # made
    "deck":       ["#384048", "#586068", "#788088", "#98A0A8", "#C0C8D0"],
    "durasteel":  ["#282830", "#404850", "#606870", "#889098", "#B0B8C0"],
    "plaza":      ["#605058", "#806870", "#A08888", "#C0A8A0", "#E0C8B8"],
    "cloud":      ["#886878", "#B89098", "#D8B0A8", "#F0D0B8", "#F8F0E0"],
    "void":       ["#000008", "#080818", "#181828", "#282840", "#403858"],
    "fungus":     ["#401838", "#702850", "#A04070", "#D07090", "#F0A8B8"],
    "adobe":      ["#683820", "#905030", "#B87048", "#D09060", "#E8B080"],
}

# class: what a vanilla colour draws, by LCh. (name, test). First match wins; anything else is kept.
# Light ranges are measured on General + the town secondaries.
CLASS_L = {"ground": (55, 85), "foliage": (28, 92), "water": (28, 80), "rock": (28, 90), "dirt": (40, 85),
           "sand": (62, 92), "roof": (40, 82), "grey": (20, 100)}


def _hin(h, a, b):
    return a <= h <= b if a <= b else (h >= a or h <= b)


def classify(lch) -> str | None:
    L, C, H = lch
    if C >= 100:                                  # vanilla's magenta "unused" slots
        return None
    if C < 6:
        return "grey"
    if _hin(H, 145, 185) and C >= 15:
        return "ground"
    if _hin(H, 105, 145) and C >= 30:
        return "foliage"
    if _hin(H, 225, 305) and C >= 28:
        return "water"
    if _hin(H, 315, 55) and C < 26:
        return "rock"
    if _hin(H, 5, 50) and C >= 45:
        return "roof"
    if _hin(H, 72, 112) and C >= 25:
        return "sand"
    if _hin(H, 15, 80) and C >= 20:
        return "dirt"
    return None


def tone_of(cls: str, L: float) -> float:
    a, b = CLASS_L.get(cls, (20, 100))
    return float(np.clip((L - a) / (b - a), 0, 1))


def _ramp(name):
    return [colour.hex_to_rgb(h) for h in MATERIALS[name]]


def paint_bank(pal, assign: dict, key: str = "") -> list:
    """One 16-entry bank -> painted bank. `assign` maps class -> material name (missing = keep)."""
    trunc = lambda c: tuple((int(v) >> 3) << 3 for v in c)
    rgb = np.array(pal, dtype=np.float64)
    lch = colour.srgb_to_lch(rgb)
    cls = [classify(lch[i]) for i in range(16)]
    waterbank = sum(c == "water" for c in cls[1:]) >= 3
    out = [trunc(pal[0])]
    for i in range(1, 16):
        c = cls[i]
        L = lch[i][0]
        if c == "grey" and waterbank and L >= 85 and "water" in assign:
            c, L = "water", 100                     # foam
        if c is None and lch[i][1] >= 100:
            out.append(trunc(pal[i]))              # magenta: vanilla's unused slots, the placeholder pink
            continue
        mat = assign.get(c or "other")
        if not mat:
            # not terrain (roofs, walls, signs): greybox grey, like the rest of the world for now
            g = lch[i].copy(); g[1] *= GREY_CHROMA
            out.append(tuple(int(v) for v in colour.gba_snap(colour.lch_to_srgb(g))))
            continue
        ramp = _ramp(mat)
        t = tone_of(c, L)
        out.append(ramp[int(round(t * (len(ramp) - 1)))])
    return out


def paint_tileset(ts: gba.Tileset, assign: dict) -> gba.Tileset:
    banks = range(0, gba.NUM_PALS_IN_PRIMARY) if not ts.secondary else range(gba.NUM_PALS_IN_PRIMARY, gba.NUM_PALS_TOTAL)
    pals = [list(p) for p in ts.palettes]
    for b in banks:
        pals[b] = paint_bank(ts.palettes[b], assign, f"{ts.name}:{b}")
    return gba.Tileset(ts.name, ts.path, ts.secondary, ts.tiles, pals, ts.metatiles, ts.attributes)


def paint_pair(p: gba.TilesetPair, assign: dict) -> gba.TilesetPair:
    return gba.TilesetPair(paint_tileset(p.primary, assign), paint_tileset(p.secondary, assign))


GREY_CHROMA = 0.0   # buildings and structures stay grey until their phase (owner, 2026-11-05)

# Planet looks: class -> material, per variant. "grey" and "roof" are left alone unless named (buildings come later).
_HOTH = {"ground": "snow", "foliage": "evergreen", "water": "ice", "rock": "frostrock", "dirt": "slush", "sand": "snow"}
PLANETS = {
    "TATOOINE": {
        "A": {"ground": "dune", "foliage": "scrub", "water": "clearwater", "rock": "canyon", "dirt": "hardpan", "sand": "dune"},
        "B": {"ground": "hardpan", "foliage": "scrub", "water": "clearwater", "rock": "canyon", "dirt": "adobe", "sand": "dune"},
        "C": {"ground": "sandstone", "foliage": "scrub", "water": "clearwater", "rock": "hardpan", "dirt": "dune", "sand": "dune"},
    },
    "HOTH": {"A": _HOTH, "B": {**_HOTH, "rock": "slush", "dirt": "frostrock"}, "C": {**_HOTH, "rock": "crystal"}},
    "ILUM": {"A": {**_HOTH, "rock": "crystal"}, "B": _HOTH, "C": {**_HOTH, "rock": "frostrock", "ground": "slush", "dirt": "snow"}},
    "SULLUST": {
        "A": {"ground": "ash", "foliage": "basalt", "water": "sulphur", "rock": "basalt", "dirt": "ash", "sand": "ash"},
        "B": {"ground": "basalt", "foliage": "ash", "water": "lava", "rock": "ash", "dirt": "ember", "sand": "ash"},
        "C": {"ground": "ash", "foliage": "basalt", "water": "lava", "rock": "canyon", "dirt": "hardpan", "sand": "ash"},
    },
    "MUSTAFAR": {"A": {"ground": "basalt", "foliage": "ash", "water": "lava", "rock": "ash", "dirt": "ember", "sand": "ash"}},
    "ENDOR": {
        "A": {"ground": "moss", "foliage": "canopy", "water": "river", "rock": "loam", "dirt": "loam", "sand": "hardpan"},
        "B": {"ground": "forestfloor", "foliage": "canopy", "water": "clearwater", "rock": "bark", "dirt": "loam", "sand": "hardpan"},
        "C": {"ground": "moss", "foliage": "evergreen", "water": "river", "rock": "temple", "dirt": "bark", "sand": "loam"},
    },
    "YAVIN 4": {
        "A": {"ground": "jungle", "foliage": "canopy", "water": "river", "rock": "temple", "dirt": "loam", "sand": "sandstone"},
        "B": {"ground": "moss", "foliage": "jungle", "water": "river", "rock": "temple", "dirt": "hardpan", "sand": "sandstone"},
        "C": {"ground": "jungle", "foliage": "canopy", "water": "clearwater", "rock": "sandstone", "dirt": "loam", "sand": "sandstone"},
    },
    "KASHYYYK": {
        "A": {"ground": "forestfloor", "foliage": "canopy", "water": "river", "rock": "bark", "dirt": "loam", "sand": "hardpan"},
        "B": {"ground": "moss", "foliage": "canopy", "water": "river", "rock": "loam", "dirt": "bark", "sand": "loam"},
        "C": {"ground": "jungle", "foliage": "canopy", "water": "clearwater", "rock": "bark", "dirt": "loam", "sand": "hardpan"},
    },
    "DAGOBAH": {
        "A": {"ground": "bogmoss", "foliage": "bogmoss", "water": "bogwater", "rock": "mud", "dirt": "mud", "sand": "mud"},
        "B": {"ground": "moss", "foliage": "canopy", "water": "bogwater", "rock": "mud", "dirt": "mud", "sand": "mud"},
        "C": {"ground": "bogmoss", "foliage": "evergreen", "water": "river", "rock": "loam", "dirt": "mud", "sand": "mud"},
    },
    "KAMINO": {
        "A": {"ground": "deck", "foliage": "evergreen", "water": "stormsea", "rock": "durasteel", "dirt": "deck", "sand": "deck"},
        "B": {"ground": "durasteel", "foliage": "evergreen", "water": "stormsea", "rock": "deck", "dirt": "deck", "sand": "slush"},
        "C": {"ground": "deck", "foliage": "evergreen", "water": "river", "rock": "slush", "dirt": "durasteel", "sand": "deck"},
    },
    "BESPIN": {
        "A": {"ground": "plaza", "foliage": "fungus", "water": "cloud", "rock": "cloud", "dirt": "deck", "sand": "cloud"},
        "B": {"ground": "deck", "foliage": "fungus", "water": "cloud", "rock": "plaza", "dirt": "plaza", "sand": "cloud"},
        "C": {"ground": "sandstone", "foliage": "fungus", "water": "cloud", "rock": "cloud", "dirt": "plaza", "sand": "cloud"},
    },
    "JEDHA": {
        "A": {"ground": "sandstone", "foliage": "scrub", "water": "stormsea", "rock": "temple", "dirt": "hardpan", "sand": "dune"},
        "B": {"ground": "hardpan", "foliage": "scrub", "water": "clearwater", "rock": "sandstone", "dirt": "dune", "sand": "dune"},
        "C": {"ground": "slush", "foliage": "evergreen", "water": "stormsea", "rock": "temple", "dirt": "sandstone", "sand": "sandstone"},
    },
    "FELUCIA": {"A": {"ground": "jungle", "foliage": "fungus", "water": "sulphur", "rock": "fungus", "dirt": "loam", "sand": "hardpan"}},
    "MORTIS": {"A": {"ground": "moss", "foliage": "crystal", "water": "clearwater", "rock": "temple", "dirt": "sandstone", "sand": "sandstone"}},
    "GRAND ARENA": {"A": {"ground": "plaza", "foliage": "canopy", "water": "clearwater", "rock": "sandstone", "dirt": "deck", "sand": "dune"}},
    "TYTHON": {"A": {"ground": "moss", "foliage": "canopy", "water": "clearwater", "rock": "temple", "dirt": "hardpan", "sand": "sandstone"}},
    "ATOLLON": {"A": {"ground": "slush", "foliage": "scrub", "water": "stormsea", "rock": "frostrock", "dirt": "hardpan", "sand": "sandstone"}},
    "ASTEROID FIELD": {"A": {"ground": "ash", "foliage": "basalt", "water": "void", "rock": "void", "dirt": "ash", "sand": "ash"}},
    "DEATH STAR": {"A": {"ground": "durasteel", "foliage": "deck", "water": "void", "rock": "durasteel", "dirt": "deck", "sand": "deck"}},
}

# Net-new items: (vanilla item whose tiles are drawn, class overrides on top of the planet's look)
ITEM_PAINT = {
    "dune-sea":         ("water-ocean", {"water": "dune"}),
    "cloud":            ("water-ocean", {"water": "cloud"}),
    "mud":              ("sand", {"sand": "mud", "dirt": "mud"}),
    "deck":             ("ground-path", {"dirt": "deck", "ground": "deck"}),
    "wroshyr-platform": (("bridge", "ground-path"), {}),
    "wroshyr":          ("tree", {"foliage": "canopy", "rock": "bark"}),
    "gnarltree":        ("tree", {"foliage": "bogmoss", "dirt": "mud"}),
    "fungus":           ("tree", {"foliage": "fungus"}),
    "cloud-edge":       ("cliff", {"rock": "cloud"}),
    "void-edge":        ("cliff", {"rock": "void"}),
    "platform-rail":    ("cliff", {"rock": "durasteel"}),
    "durasteel-wall":   ("cliff", {"rock": "durasteel"}),
}


CLASSES = ("ground", "foliage", "water", "rock", "dirt", "sand", "roof", "grey", "other")
# vanilla items whose every colour is one material (wooden walkways); `bridge` falls back to the path's tiles
ITEM_PAINT["bridge"] = (("bridge", "ground-path"), {})
ITEM_ALL = {"bridge": "bark", "wroshyr-platform": "bark"}
METAL_WORLDS = {"KAMINO", "BESPIN", "DEATH STAR", "GRAND ARENA", "ASTEROID FIELD"}   # walkways are deck plate

# vanilla grounds drawn in grey or white (Sootopolis stone, snow): their greys are the planet's ground
GREY_GROUNDS = {"ground-snow", "ground-rock"}


def look(planet: str, variant: str = "A", item: str | None = None) -> dict:
    vs = PLANETS.get(planet, {})
    base = dict(vs.get(variant) or vs.get("A") or {})
    if item in ITEM_PAINT:
        base.update(ITEM_PAINT[item][1])
    if item in ITEM_ALL:
        m = "deck" if planet in METAL_WORLDS and item == "bridge" else ITEM_ALL[item]
        # only the classes ground and paths never use: a walkway's bank is often the ground's bank too
        base.update({c: m for c in ("grey", "other", "roof")})
    if item in GREY_GROUNDS and "ground" in base:
        base["grey"] = base["ground"]
    return base


def item_key(item: str | None):
    """Cells of these items get their own painted pair."""
    return item if item in ITEM_PAINT or item in GREY_GROUNDS else None


def variants(planet: str) -> list[str]:
    return sorted(PLANETS.get(planet, {"A": {}}))
