#!/usr/bin/env python3
"""Port the Star Wars creature sizes into ../game: Datapad height and weight, the height and weight orders, and
the size screen ("SIZE COMPARED TO KAEL") scales.

Sources:
  mapping/creature_sizes.csv  the 386 Emerald species: `height_m`, `weight_kg`, `screen_m` (see below), `basis`.
  mapping/new_species.csv     the 12 net-new species: `height_m`, `weight_kg`.

What it writes in ../game:
  src/data/pokemon/pokedex_entries.h  `.height`, `.weight` (tenths of a metre and of a kilogram) and the four
                                      size-screen fields of every entry.
  src/data/pokemon/pokedex_orders.h   gPokedexOrder_Weight and gPokedexOrder_Height, sorted again.
  src/data/pokemon/battle_weights.h   Emerald's weights (and the net-new rows' own), read by Low Kick, so a new
                                      Datapad weight never changes battle damage (balance rule).

The size screen draws the player's front portrait and the creature's front (frame 1 of anim_front, the pic the
Datapad shows) as black silhouettes, side by side on one ground line, shrunk by an affine matrix (256 = full
size; the GBA cannot draw them bigger). Each figure's real outline (its non-transparent pixels) is measured, so
the scale follows the drawn art, not Emerald's. The player is PLAYER_HEIGHT_M tall. The figure's height spans
`height_m`; when `screen_m` is set (long bodies: fish, serpents, whales, wings spread, where the Datapad height
is a length), the figure's longest side spans `screen_m` instead. The bigger of the two figures is drawn at full
size and the other is shrunk to match.

Limits checked: height <= 30.4 m (the Datapad prints feet with two digits), weight <= 2,000 kg (PrintMonWeight
multiplies the weight by 100,000 in 32 bits).

  python3 tools/port_sizes.py          # write ../game
  python3 tools/port_sizes.py check    # exit 1 if ../game is not up to date; no writes
  python3 tools/port_sizes.py report   # also write database/creature_sizes.csv (every entry, the scales used)

Run it after tools/port_creatures.py (which adds the net-new species). Idempotent. Needs Pillow.
"""
import csv
import re
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
GAME = ROOT.parent / "game"
MAP = ROOT / "mapping"
DB = ROOT / "database"

PLAYER_HEIGHT_M = 1.6        # KAEL and MIRA, both drawn 64 px tall in their front portraits
GROUND_Y = 88                # screen row under the feet; Emerald's player stands on it at full size
SPRITE_Y = 56                # both sprites are created centred on y 56 (Task_LoadSizeScreen)
MAX_SCALE = 8192             # 1/32 size; a safety cap, never reached by the current rows
MAX_HEIGHT_DM = 304
MAX_WEIGHT_HG = 20000

ENTRIES = "src/data/pokemon/pokedex_entries.h"
ORDERS = "src/data/pokemon/pokedex_orders.h"
WEIGHTS = "src/data/pokemon/battle_weights.h"


def read_csv(path):
    with open(path, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def figure_box(path):
    """Bounding box (x0, y0, x1, y1) of the non-transparent pixels in the top 64x64 frame of an indexed PNG."""
    im = Image.open(path)
    if im.mode != "P":
        raise SystemExit(f"{path}: not an indexed PNG")
    px = im.load()
    xs, ys = [], []
    for y in range(64):
        for x in range(64):
            if px[x, y] != 0:
                xs.append(x)
                ys.append(y)
    if not xs:
        raise SystemExit(f"{path}: empty frame")
    return min(xs), min(ys), max(xs), max(ys)


def union(boxes):
    return (min(b[0] for b in boxes), min(b[1] for b in boxes), max(b[2] for b in boxes), max(b[3] for b in boxes))


def front_pics():
    """NATIONAL_DEX key -> the PNG (or PNGs, for Unown) the Datapad draws for it."""
    pics = dict(re.findall(r'const u32 (gMonFrontPic_\w+)\[\] = INCGFX_U32\("([^"]+)"',
                           (GAME / "src/anim_mon_front_pics.c").read_text()))
    table = dict(re.findall(r"SPECIES_SPRITE\((\w+), (gMonFrontPic_\w+)\)",
                            (GAME / "src/data/pokemon_graphics/front_pic_table.h").read_text()))
    out = {}
    for species, sym in table.items():
        path = pics[sym]
        if path.endswith(".4bpp"):  # Castform: four forms joined at build time; the Datapad shows the normal one
            path = "graphics/pokemon/castform/normal/anim_front.png"
        out[species] = [GAME / path]
    # Unown: the Datapad shows whichever letter was seen first, so the scale must fit every letter
    out["UNOWN"] = [GAME / p for s, p in pics.items() if re.fullmatch(r"gMonFrontPic_Unown\w", s) or s in (
        "gMonFrontPic_UnownExclamationMark", "gMonFrontPic_UnownQuestionMark")]
    return out


def national_keys():
    """Species constant -> NATIONAL_DEX constant (they are the same name, plus the old-Unown aliases)."""
    hdr = (GAME / "include/constants/pokedex.h").read_text()
    return set(re.findall(r"NATIONAL_DEX_(\w+),", hdr))


def key_of(emerald_id):
    return emerald_id.removeprefix("species:").upper().replace("-", "_")


def sizes():
    """NATIONAL_DEX key -> row (height_m, weight_kg, screen_m, battle weight in hg)."""
    rows = {}
    for r in read_csv(MAP / "creature_sizes.csv"):
        k = key_of(r["emerald_id"])
        rows[k] = dict(r, battle_hg=round(float(r["emerald_weight_kg"]) * 10))
    for r in read_csv(MAP / "new_species.csv"):
        k = r["slot"].removeprefix("SPECIES_") if r.get("slot", "").startswith("SPECIES_") else key_of(r["emerald_id"])
        rows[k] = dict(r, screen_m="", basis="net-new", battle_hg=round(float(r["weight_kg"]) * 10))
    return rows


def compute(rows):
    pics = front_pics()
    trainer = [figure_box(GAME / f"graphics/trainers/front_pics/{t}.png") for t in ("brendan", "may")]
    th = sum(b[3] - b[1] + 1 for b in trainer) / len(trainer)       # the two portraits' mean figure height
    tbottom = max(b[3] for b in trainer)
    out = {}
    for k, r in rows.items():
        h_dm = round(float(r["height_m"]) * 10)
        w_hg = round(float(r["weight_kg"]) * 10)
        if not 0 < h_dm <= MAX_HEIGHT_DM:
            raise SystemExit(f"{k}: height {r['height_m']} m is outside 0.1-30.4 m")
        if not 0 < w_hg <= MAX_WEIGHT_HG:
            raise SystemExit(f"{k}: weight {r['weight_kg']} kg is outside 0.1-2000 kg")
        if k not in pics:
            raise SystemExit(f"{k}: no front pic in front_pic_table.h")
        box = union([figure_box(p) for p in pics[k]])
        fw, fh = box[2] - box[0] + 1, box[3] - box[1] + 1
        if r["screen_m"]:
            span_m, span_px = float(r["screen_m"]), max(fw, fh)
        else:
            span_m, span_px = float(r["height_m"]), fh
        # pixels per metre at which the bigger figure is drawn at full size
        ppm = min(span_px / span_m, th / PLAYER_HEIGHT_M)
        mon_scale = min(MAX_SCALE, round(256 * span_px / (ppm * span_m)))
        tr_scale = min(MAX_SCALE, round(256 * th / (ppm * PLAYER_HEIGHT_M)))
        mon_off = round(GROUND_Y - SPRITE_Y - (box[3] + 1 - 32) * 256 / mon_scale)
        tr_off = round(GROUND_Y - SPRITE_Y - (tbottom + 1 - 32) * 256 / tr_scale)
        out[k] = dict(height=h_dm, weight=w_hg, pokemonScale=mon_scale, pokemonOffset=mon_off,
                      trainerScale=tr_scale, trainerOffset=tr_off, battle=r["battle_hg"],
                      figure=f"{fw}x{fh}", pic=str(pics[k][0].relative_to(GAME)) + (" (+ every letter)" if k == "UNOWN" else ""),
                      sw_name=r["sw_name"], basis=r["basis"], screen_m=r["screen_m"])
    return out


FIELDS = ("height", "weight", "pokemonScale", "pokemonOffset", "trainerScale", "trainerOffset")


def write_entries(text, vals):
    seen = set()

    def fix(m):
        k = m.group(1)
        if k not in vals:
            return m.group(0)
        seen.add(k)
        block = m.group(0)
        for f in FIELDS:
            block, n = re.subn(rf"(\.{f} = )-?\d+,", lambda mm: f"{mm.group(1)}{vals[k][f]},", block, count=1)
            if n != 1:
                raise SystemExit(f"{ENTRIES}: no .{f} in NATIONAL_DEX_{k}")
        return block

    text = re.sub(r"^    \[NATIONAL_DEX_(\w+)\] =[^\n]*\n    \{.*?\n    \},\n", fix, text, flags=re.S | re.M)
    missing = set(vals) - seen
    if missing:
        raise SystemExit(f"{ENTRIES}: no entry for {sorted(missing)}")
    return text


def write_orders(text, vals):
    for order, f in (("Weight", "weight"), ("Height", "height")):
        m = re.search(rf"(const u16 gPokedexOrder_{order}\[\] =\n\{{\n)(.*?)(\}};)", text, re.S)
        cur = re.findall(r"NATIONAL_DEX_(\w+)", m.group(2))
        if sorted(cur) != sorted(vals):
            raise SystemExit(f"gPokedexOrder_{order} lists {sorted(set(cur) ^ set(vals))} differently from the entries")
        cur.sort(key=lambda k: (vals[k][f], NATPOS[k]))  # ties: national Datapad order
        text = text[:m.start(2)] + "".join(f"    NATIONAL_DEX_{k},\n" for k in cur) + text[m.end(2):]
    return text


def battle_weights(vals):
    lines = ["// Generated by wiki/tools/port_sizes.py. Do not edit.",
             "// Weight in tenths of a kilogram that Low Kick reads: Emerald's weight for every Emerald species and",
             "// mapping/new_species.csv's for the net-new ones. The Datapad shows the Star Wars weight",
             "// (gPokedexEntries), which must not change battle damage.",
             "static const u16 sBattleWeights[] =", "{", "    [NATIONAL_DEX_NONE] = 0,"]
    for k in sorted(vals, key=lambda k: NATPOS[k]):
        lines.append(f"    [NATIONAL_DEX_{k}] = {vals[k]['battle']},")
    lines += ["};", ""]
    return "\n".join(lines)


NATPOS = {}


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "write"
    if mode not in ("write", "check", "report"):
        raise SystemExit(__doc__)
    hdr = (GAME / "include/constants/pokedex.h").read_text()
    NATPOS.update({k: i for i, k in enumerate(re.findall(r"NATIONAL_DEX_(\w+),", hdr))})
    rows = sizes()
    unknown = set(rows) - set(NATPOS)
    if unknown:
        raise SystemExit(f"not national Datapad keys: {sorted(unknown)}")
    vals = compute(rows)
    files = {ENTRIES: write_entries((GAME / ENTRIES).read_text(), vals),
             ORDERS: write_orders((GAME / ORDERS).read_text(), vals),
             WEIGHTS: battle_weights(vals)}
    stale = [p for p, t in files.items() if not (GAME / p).exists() or (GAME / p).read_text() != t]
    if mode == "check":
        print("up to date" if not stale else f"stale: {', '.join(stale)}")
        sys.exit(1 if stale else 0)
    for p in stale:
        (GAME / p).write_text(files[p])
        print(f"wrote {p}")
    if mode == "report":
        cols = ["key", "sw_name", "basis", "height", "weight", "screen_m", "pic", "figure", "pokemonScale",
                "pokemonOffset", "trainerScale", "trainerOffset", "battle"]
        with open(DB / "creature_sizes.csv", "w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=cols, lineterminator="\n")
            w.writeheader()
            for k in sorted(vals, key=lambda k: NATPOS[k]):
                w.writerow({"key": k, **{c: vals[k][c] for c in cols[1:]}})
        print(f"wrote database/creature_sizes.csv ({len(vals)} rows)")
    print(f"{len(vals)} entries, {len(stale)} files changed")


if __name__ == "__main__":
    main()
