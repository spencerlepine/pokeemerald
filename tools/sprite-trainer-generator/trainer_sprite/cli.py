"""trainer_sprite CLI (run from the tool folder).

    python -m trainer_sprite build   art/vader.yaml              # PNG + previews + lint report
    python -m trainer_sprite verify  art/vader.yaml              # round-trip through pokeemerald's gbagfx
    python -m trainer_sprite install art/vader.yaml              # copy into a pokeemerald checkout
    python -m trainer_sprite inspect <vanilla.png> out.png       # material map of a pic's palette indices
    python -m trainer_sprite compare output/x.png a.yaml b.yaml  # side-by-side review sheet
    python -m trainer_sprite corpus                              # re-measure the vanilla trainer pics
    python -m trainer_sprite status                              # worklist: every wiki front pic, spec / built
    python -m trainer_sprite sheet  out.png [a.yaml ...]         # contact sheet (default: every spec in art/)

Outputs go to output/<name>/ (name from the spec).

EMERALD_DIR (default: this repo's game/ folder, else a pokeemerald clone beside any parent folder) points at a pokeemerald checkout; it is
read for repaint bases, the style corpus, battle previews and gbagfx, and written only by
`install`.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from . import sheet, spec as spec_mod, trainer

TOOL = Path(__file__).resolve().parents[1]
OUT = TOOL / "output"


def out_dir(s) -> Path:
    return OUT / s.name


def emerald_dir() -> Path:
    """EMERALD_DIR, else the game/ folder of the repo this tool sits in
    (pokeemerald/tools/<tool> -> pokeemerald/game), else the first `pokeemerald` folder found
    beside this tool or any parent folder (its game/ subfolder when it has one)."""
    env = os.environ.get("EMERALD_DIR")
    if env:
        return Path(env).resolve()
    for d in TOOL.parents:
        if (d / "game" / "graphics").is_dir():
            return (d / "game").resolve()
    for d in TOOL.parents:
        root = d / "pokeemerald"
        if root.is_dir():
            return (root / "game" if (root / "game" / "graphics").exists() else root).resolve()
    return (TOOL.parent / "pokeemerald").resolve()


def report(errors, warnings, m, corpus) -> str:
    lines = [f"ERROR   {e}" for e in errors] + [f"warning {w}" for w in warnings]
    lines.append("")
    lines.append(f"{'metric':<14}{'this':>8}{'Emerald p5':>12}{'median':>8}{'p95':>8}")
    for k, v in m.items():
        if corpus and k in corpus["median"]:
            lines.append(f"{k:<14}{v:>8}{corpus['p5'][k]:>12}{corpus['median'][k]:>8}{corpus['p95'][k]:>8}")
        else:
            lines.append(f"{k:<14}{v:>8}")
    return "\n".join(lines)


def cmd_build(a) -> int:
    s = spec_mod.load(a.spec)
    out = out_dir(s)
    (out / "preview").mkdir(parents=True, exist_ok=True)
    png = out / f"{s.name}.png"
    sheet.build_sheet(s).save(png, optimize=False)
    colours = sheet.spec_palette(s)
    g = s.frames["front"]
    errors, warnings, m = trainer.lint(g, colours)
    trainer.zoom(g, colours, out / "preview" / "zoom.png")
    em = emerald_dir()
    if (em / "graphics/battle_environment").exists():
        trainer.battle(g, colours, out / "preview" / "battle.png", em, s.replaces)
    else:
        print(f"note: no pokeemerald at {em}; skipped battle.png (set EMERALD_DIR)")
    trainer.showcase(out / "preview")
    text = report(errors, warnings, m, trainer.load_corpus() or {})
    (out / "lint.txt").write_text(text + "\n")
    (out / "metrics.json").write_text(json.dumps(m, indent=1))
    print(f"wrote {png.relative_to(TOOL)} and previews in {(out / 'preview').relative_to(TOOL)}")
    print(text)
    return 1 if errors else 0


def cmd_corpus(a) -> int:
    c = trainer.build_corpus(emerald_dir())
    print(f"measured {c['count']} vanilla trainer pics -> {trainer.CORPUS_FILE.relative_to(TOOL)}")
    for k in c["median"]:
        print(f"  {k:<14} p5 {c['p5'][k]:>7}  median {c['median'][k]:>7}  p95 {c['p95'][k]:>7}")
    return 0


def _gbagfx() -> Path:
    g = emerald_dir() / "tools/gbagfx/gbagfx"
    if not g.exists():
        subprocess.run(["make", "-s", "-C", str(g.parent)], check=True)
    return g


def cmd_verify(a) -> int:
    """As src/data/graphics/trainers.h: png -> .4bpp (no metatile args) and png -> .gbapal,
    then back to PNG; indices and GBA colours must match."""
    s = spec_mod.load(a.spec)
    png = out_dir(s) / f"{s.name}.png"
    g = _gbagfx()
    with tempfile.TemporaryDirectory() as t:
        bpp, gpal, back = Path(t) / "x.4bpp", Path(t) / "x.gbapal", Path(t) / "back.png"
        subprocess.run([str(g), str(png), str(bpp)], check=True)
        subprocess.run([str(g), str(png), str(gpal)], check=True)
        subprocess.run([str(g), str(bpp), str(back), "-width", "8", "-palette", str(gpal)], check=True)
        a_g, a_c = trainer.read_pic(png)
        b_g, b_c = trainer.read_pic(back)
        size, psize = bpp.stat().st_size, gpal.stat().st_size
    ok = a_g == b_g and [tuple(x >> 3 for x in c) for c in a_c] == [tuple(x >> 3 for x in c) for c in b_c]
    print(f"gbagfx: {png.name} -> {size} bytes of 4bpp (expect 2048) + {psize}-byte palette (expect 32); "
          f"round-trip {'identical' if ok else 'DIFFERS'}")
    return 0 if ok and size == 2048 and psize == 32 else 1


def palette_source(em: Path, pic: str) -> str | None:
    """Where the game loads this front pic's palette from (src/data/graphics/trainers.h).
    Most pics build it from the PNG itself; the player, rival, Wally and Steven pics share a
    .pal in graphics/trainers/palettes/ with their back pic, and the PNG's colours are ignored."""
    import re

    h = em / "src/data/graphics/trainers.h"
    if not h.exists():
        return None
    text = h.read_text()
    m = re.search(r"gTrainerFrontPic_(\w+)\[\]\s*=\s*INCGFX_U32\(\"" + re.escape(pic) + r"\"", text)
    if not m:
        return None
    p = re.search(r"gTrainerPalette_" + m.group(1) + r"\[\]\s*=\s*INCGFX_U32\(\"([^\"]+)\"", text)
    return p.group(1) if p else None


def cmd_install(a) -> int:
    """Copy the pic over the vanilla file it replaces. The palette travels inside the PNG, except
    for pics whose palette is a shared .pal (player, rival, Wally, Steven): that file is written
    too, and it is shared with the back pic, so the back pic must use the same 16 colours."""
    s = spec_mod.load(a.spec)
    if not s.replaces:
        print("spec has no `replaces:`")
        return 1
    em = emerald_dir()
    shutil.copyfile(out_dir(s) / f"{s.name}.png", em / s.replaces)
    print(f"copied -> {em / s.replaces}")
    src = palette_source(em, s.replaces)
    if src and src.endswith(".pal"):
        from . import palette as pal

        pal.write_jasc(em / src, sheet.spec_palette(s))
        print(f"wrote palette -> {em / src} (shared with the back pic: keep them identical)")
    return 0


def subjects() -> dict[str, str]:
    """Wiki brief per front pic: ../../wiki/mapping/art_subjects.csv (asset_id -> sw_subject)."""
    import csv

    f = TOOL.parents[1] / "wiki/mapping/art_subjects.csv"
    if not f.exists():
        return {}
    with f.open() as fh:
        return {r["asset_id"]: r["sw_subject"] for r in csv.DictReader(fh) if "/trainers/front_pics/" in r["asset_id"]}


def all_specs() -> list:
    out = []
    for p in sorted((TOOL / "art").glob("*.yaml")):
        try:
            out.append(spec_mod.load(p))
        except Exception as e:  # noqa: BLE001 - report and keep going
            print(f"skip {p.name}: {e}", file=sys.stderr)
    return out


def cmd_status(a) -> int:
    """The worklist for mass generation: every front pic the wiki lists, with its brief and
    whether a spec exists and is built. KEEP rows (FireRed leftovers) are listed as kept."""
    subj = subjects()
    by_pic = {}
    for p in sorted((TOOL / "art").glob("*.yaml")):
        import yaml

        d = yaml.safe_load(p.read_text())
        by_pic.setdefault(d.get("replaces"), []).append(d["name"])
    em = emerald_dir()
    rows = []
    pics = sorted(set(subj) | {k for k in by_pic if k})
    for pic in pics:
        names = by_pic.get(pic, [])
        built = [n for n in names if (OUT / n / f"{n}.png").exists()]
        brief = subj.get(pic, "(not in the wiki)")
        state = "keep" if "kept" in brief.lower() else ("built" if built else ("spec" if names else "todo"))
        paired = (em / "graphics/trainers/back_pics" / Path(pic).name).exists()
        rows.append((state, Path(pic).stem, ",".join(names), brief, "palette shared with its back pic" if paired else ""))
    counts = {}
    for r in rows:
        counts[r[0]] = counts.get(r[0], 0) + 1
    w = max(len(r[1]) for r in rows)
    for r in rows:
        print(f"{r[0]:<6} {r[1]:<{w}}  {r[2]:<18} {r[3]}" + (f"  [{r[4]}]" if r[4] else ""))
    print("\n" + ", ".join(f"{k}: {v}" for k, v in sorted(counts.items())))
    return 0


def cmd_sheet(a) -> int:
    """Contact sheet: every pic at 2x in a battle-scene crop, labelled with name and brief."""
    specs = [spec_mod.load(p) for p in a.specs] if a.specs else all_specs()
    em = emerald_dir()
    trainer.contact(specs, Path(a.out), em if (em / "graphics/battle_environment").exists() else None,
                    sheet.spec_palette, subjects(), cols=a.cols)
    print(f"wrote {a.out} ({len(specs)} pics)")
    return 0


def cmd_compare(a) -> int:
    """Side-by-side review sheet for variants: python -m trainer_sprite compare out.png a.yaml b.yaml ..."""
    specs = [spec_mod.load(p) for p in a.specs]
    em = emerald_dir()
    trainer.compare(specs, Path(a.out), em if (em / "graphics/battle_environment").exists() else None, sheet.spec_palette)
    print(f"wrote {a.out}")
    return 0


def cmd_cutpart(a) -> int:
    """Cut a part out of a built (approved) pic: python -m trainer_sprite cutpart
    output/boba/boba.png 26 1 17 22 --roles "1:K 2:1 3:2 4:3" > parts/x.yaml rows."""
    from . import parts as parts_mod

    roles = {int(k): v for k, v in (p.split(":") for p in a.roles.split())}
    for r in parts_mod.cut(Path(a.png), [a.x, a.y, a.w, a.h], roles):
        print("  " + r)
    return 0


def cmd_parts(a) -> int:
    """Contact sheet of every part in parts/, in a neutral test palette."""
    from PIL import Image, ImageDraw

    from . import parts as parts_mod

    test = {".": None, "K": (16, 16, 24), "1": (96, 104, 128), "2": (152, 160, 184), "3": (208, 216, 232), "4": (248, 248, 248),
            "5": (152, 64, 48), "6": (216, 104, 72), "7": (248, 168, 120), "8": (40, 48, 72), "9": (96, 168, 232),
            "W": (255, 255, 255), "s": (200, 136, 104), "t": (232, 176, 144), "u": (248, 224, 200)}
    names = sorted(p.stem for p in parts_mod.PARTS.glob("*.yaml"))
    z, cell = 8, 26
    im = Image.new("RGB", (len(names) * (cell * z + 8) + 8, cell * z + 24), (24, 24, 30))
    d = ImageDraw.Draw(im)
    for i, n in enumerate(names):
        p = parts_mod.load(n)
        x0 = 8 + i * (cell * z + 8)
        d.rectangle([x0, 18, x0 + cell * z - 1, 18 + cell * z - 1], fill=(115, 197, 164))
        d.text((x0, 3), n, fill=(230, 230, 230))
        for y, row in enumerate(p["rows"]):
            for x, ch in enumerate(row):
                if test.get(ch):
                    d.rectangle([x0 + x * z, 18 + y * z, x0 + x * z + z - 1, 18 + y * z + z - 1], fill=test[ch])
    im.save(a.out)
    print(f"wrote {a.out} ({len(names)} parts)")
    return 0


def cmd_inspect(a) -> int:
    """Material map of an indexed PNG: each palette index in a false colour with its number, so
    a repaint `remap:` can be written (which index is skin, hair, coat, outline...)."""
    from PIL import Image, ImageDraw

    im = Image.open(a.png)
    pal = im.getpalette()[:48]
    px = im.load()
    counts = {}
    for y in range(im.height):
        for x in range(im.width):
            counts[px[x, y]] = counts.get(px[x, y], 0) + 1
    false = [(0, 0, 0), (255, 0, 0), (0, 200, 0), (0, 80, 255), (255, 200, 0), (255, 0, 255), (0, 220, 220), (255, 128, 0),
             (128, 0, 255), (0, 128, 64), (160, 80, 40), (255, 160, 200), (120, 120, 120), (200, 255, 120), (0, 0, 128), (255, 255, 255)]
    z = 6
    W = im.width * z * 2 + 260
    out = Image.new("RGB", (W, max(im.height * z, 16 * 22 + 10)), (30, 30, 36))
    real = Image.new("RGB", im.size, (115, 197, 164))
    fc = Image.new("RGB", im.size, (40, 40, 48))
    for y in range(im.height):
        for x in range(im.width):
            v = px[x, y]
            if v:
                real.putpixel((x, y), tuple(pal[v * 3 : v * 3 + 3]))
                fc.putpixel((x, y), false[v])
    out.paste(real.resize((im.width * z, im.height * z), Image.NEAREST), (0, 0))
    out.paste(fc.resize((im.width * z, im.height * z), Image.NEAREST), (im.width * z, 0))
    d = ImageDraw.Draw(out)
    x0 = im.width * z * 2 + 10
    for i in range(16):
        y = 6 + i * 22
        d.rectangle([x0, y, x0 + 16, y + 16], fill=false[i])
        d.rectangle([x0 + 20, y, x0 + 36, y + 16], fill=tuple(pal[i * 3 : i * 3 + 3]))
        d.text((x0 + 42, y + 3), f"{i:>2}  {tuple(pal[i * 3 : i * 3 + 3])}  {counts.get(i, 0)} px", fill=(230, 230, 230))
        print(f"{i:>2} {tuple(pal[i * 3 : i * 3 + 3])!s:<18} {counts.get(i, 0):>5} px")
    out.save(a.out)
    print(f"wrote {a.out}")
    return 0


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="trainer_sprite")
    sub = p.add_subparsers(dest="cmd", required=True)
    for name, fn in (("build", cmd_build), ("verify", cmd_verify), ("install", cmd_install)):
        sp = sub.add_parser(name)
        sp.add_argument("spec")
        sp.set_defaults(fn=fn)
    sub.add_parser("corpus").set_defaults(fn=cmd_corpus)
    sub.add_parser("status").set_defaults(fn=cmd_status)
    cu = sub.add_parser("cutpart")
    for k in ("png",):
        cu.add_argument(k)
    for k in ("x", "y", "w", "h"):
        cu.add_argument(k, type=int)
    cu.add_argument("--roles", required=True)
    cu.set_defaults(fn=cmd_cutpart)
    pp = sub.add_parser("parts")
    pp.add_argument("out")
    pp.set_defaults(fn=cmd_parts)
    shp = sub.add_parser("sheet")
    shp.add_argument("out")
    shp.add_argument("specs", nargs="*")
    shp.add_argument("--cols", type=int, default=6)
    shp.set_defaults(fn=cmd_sheet)
    ip = sub.add_parser("inspect")
    ip.add_argument("png")
    ip.add_argument("out")
    ip.set_defaults(fn=cmd_inspect)
    cp = sub.add_parser("compare")
    cp.add_argument("out")
    cp.add_argument("specs", nargs="+")
    cp.set_defaults(fn=cmd_compare)
    a = p.parse_args(argv)
    try:
        return a.fn(a)
    except spec_mod.SpecError as e:
        print(f"spec error: {e}", file=sys.stderr)
        return 2
