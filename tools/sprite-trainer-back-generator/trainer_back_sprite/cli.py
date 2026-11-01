"""trainer_back_sprite CLI (run from the tool folder).

    python -m trainer_back_sprite build   art/kael_back.yaml           # PNG + previews + lint
    python -m trainer_back_sprite verify  art/kael_back.yaml           # round trip through gbagfx
    python -m trainer_back_sprite install art/kael_back.yaml           # copy into the game (+ shared .pal)
    python -m trainer_back_sprite inspect <vanilla back png> out.png   # material map, all four frames
    python -m trainer_back_sprite review  out.png [a.yaml ...]         # owner sheet: front + 4 frames + battle
    python -m trainer_back_sprite shifts  <vanilla back png>           # how far the head moves per frame
    python -m trainer_back_sprite corpus                               # re-measure the vanilla back pics
    python -m trainer_back_sprite status                               # worklist from the wiki

Outputs go to output/<name>/ (name from the spec).

EMERALD_DIR (default: this repo's game/ folder) points at a pokeemerald checkout; it is read for
repaint bases, palettes, the corpus, battle previews and gbagfx, and written only by `install`.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image

from . import back, palette as pal, spec as spec_mod

TOOL = Path(__file__).resolve().parents[1]
OUT = TOOL / "output"


def emerald_dir() -> Path:
    env = os.environ.get("EMERALD_DIR")
    if env:
        return Path(env).resolve()
    for d in TOOL.parents:
        if (d / "game" / "graphics").is_dir():
            return (d / "game").resolve()
    return (TOOL.parent / "pokeemerald").resolve()


def out_dir(s) -> Path:
    return OUT / s.name


def write_strip(s, path: Path) -> None:
    frames = s.frames
    im = Image.new("P", (64, 64 * len(frames)), 0)
    px = im.load()
    for f, g in enumerate(frames):
        for y in range(64):
            for x in range(64):
                px[x, f * 64 + y] = g[y][x]
    im.putpalette(pal.flat(spec_mod.palette16(s))[:48])
    im.save(path, optimize=False)


def palette_source(em: Path, back_pic: str) -> str | None:
    """Where the game loads this back pic's palette from: back_pic_tables.h names a
    gTrainerPalette_X, and trainers.h says which file builds it (a shared .pal for Brendan, May
    and Wally; Steven's front pic PNG)."""
    gh = em / "src/data/graphics/trainers.h"
    tables = em / "src/data/trainer_graphics/back_pic_tables.h"
    if not (gh.exists() and tables.exists()):
        return None
    text = gh.read_text()
    m = re.search(r"gTrainerBackPic_(\w+)\[\]\s*=\s*INCGFX_U8\(\"" + re.escape(back_pic) + r"\"", text)
    if not m:
        return None
    sym = m.group(1)
    t = tables.read_text()
    # TRAINER_BACK_PAL(BRENDAN, gTrainerPalette_Brendan) / Ruby-Sapphire ones use their own names
    cands = re.findall(r"TRAINER_BACK_PAL\(\w+,\s*(gTrainer\w*Palette\w*)\)", t)
    want = [c for c in cands if c.endswith("_" + sym) or c.endswith(sym)]
    if not want:
        return None
    p = re.search(re.escape(want[0]) + r"\[\]\s*=\s*INCGFX_U32\(\"([^\"]+)\"", text)
    return p.group(1) if p else None


def front_for(s, em: Path, override: str | None = None):
    """The front pic to pair with: --front, else the spec's `front:` (relative to the spec or
    to EMERALD_DIR), else the game's front pic of the same name. Returns (grid, colours, label)."""
    cands = []
    if override:
        cands.append(Path(override))
    if s.front:
        cands += [(s.path.parent / s.front).resolve(), em / s.front]
    if s.replaces:
        cands.append(em / "graphics/trainers/front_pics" / Path(s.replaces).name)
    for c in cands:
        if c.exists():
            frames, cols = back.read_strip(c)
            if c.is_relative_to(em) and "front_pics" in str(c):
                cols = back.vanilla_palette(em, c.stem)
            return frames[0], cols, str(c)
    return None


def report(errors, warnings, ms, corpus) -> str:
    lines = [f"ERROR   {e}" for e in errors] + [f"warning {w}" for w in warnings]
    lines.append("")
    lines.append(f"{'metric':<14}" + "".join(f"{'f' + str(i):>8}" for i in range(len(ms))) + f"{'p5':>8}{'median':>8}{'p95':>8}")
    for k in back.KEYS:
        row = f"{k:<14}" + "".join(f"{m.get(k, ''):>8}" for m in ms)
        if corpus:
            row += f"{corpus['p5'][k]:>8}{corpus['median'][k]:>8}{corpus['p95'][k]:>8}"
        lines.append(row)
    return "\n".join(lines)


def cmd_build(a) -> int:
    s = spec_mod.load(a.spec)
    out = out_dir(s)
    (out / "preview").mkdir(parents=True, exist_ok=True)
    png = out / f"{s.name}.png"
    write_strip(s, png)
    cols = spec_mod.palette16(s)
    em = emerald_dir()
    fr = front_for(s, em, a.front)
    errors, warnings, ms = back.lint(s.frames, cols, fr[1] if fr and not str(fr[2]).startswith(str(em)) else None)
    if fr and str(fr[2]).startswith(str(em)):
        warnings.append(f"paired with the game's current front pic ({Path(fr[2]).name}); pass --front or `front:` to check our new front's palette")
    if not fr:
        warnings.append("no front pic found to pair with; the palette match is unchecked")
    back.zoom(s.frames, cols, out / "preview" / "zoom.png")
    have_game = (em / "graphics/battle_environment").exists()
    if have_game:
        back.battle(s.frames, cols, out / "preview" / "battle.png", em, s.replaces)
    back.throw_gif(s.frames, cols, out / "preview" / "throw.gif", em if have_game else None, spec_mod.KITS[s.kit]["anim"])
    if fr:
        back.pair(fr[0], fr[1], s.frames, cols, out / "preview" / "pair.png")
    back.showcase(out / "preview")
    text = report(errors, warnings, ms, back.load_corpus())
    (out / "lint.txt").write_text(text + "\n")
    (out / "metrics.json").write_text(json.dumps(ms, indent=1))
    print(f"wrote {png.relative_to(TOOL)} and previews in {(out / 'preview').relative_to(TOOL)}")
    print(text)
    return 1 if errors else 0


def _gbagfx() -> Path:
    g = emerald_dir() / "tools/gbagfx/gbagfx"
    if not g.exists():
        subprocess.run(["make", "-s", "-C", str(g.parent)], check=True)
    return g


def cmd_verify(a) -> int:
    """As trainers.h: png -> .4bpp (uncompressed), then back to PNG; indices must match."""
    s = spec_mod.load(a.spec)
    png = out_dir(s) / f"{s.name}.png"
    g = _gbagfx()
    with tempfile.TemporaryDirectory() as t:
        bpp, gpal, rt = Path(t) / "x.4bpp", Path(t) / "x.gbapal", Path(t) / "rt.png"
        subprocess.run([str(g), str(png), str(bpp)], check=True)
        subprocess.run([str(g), str(png), str(gpal)], check=True)
        subprocess.run([str(g), str(bpp), str(rt), "-width", "8", "-palette", str(gpal)], check=True)
        a_f, _ = back.read_strip(png)
        b_f, _ = back.read_strip(rt)
        size = bpp.stat().st_size
    n = len(s.frames)
    ok = a_f == b_f
    print(f"gbagfx: {png.name} -> {size} bytes of 4bpp (expect {2048 * n}); round-trip {'identical' if ok else 'DIFFERS'}")
    return 0 if ok and size == 2048 * n else 1


def cmd_install(a) -> int:
    """Copy the strip over the vanilla back pic. If the palette is a shared .pal (Brendan, May,
    Wally), write it too; it is the front pic's palette as well. Steven's palette lives in his
    front pic PNG, so install the front pic (sprite-trainer-generator) for the colours."""
    s = spec_mod.load(a.spec)
    if not s.replaces:
        print("spec has no `replaces:`")
        return 1
    em = emerald_dir()
    shutil.copyfile(out_dir(s) / f"{s.name}.png", em / s.replaces)
    print(f"copied -> {em / s.replaces}")
    src = palette_source(em, s.replaces)
    if src and src.endswith(".pal"):
        pal.write_jasc(em / src, spec_mod.palette16(s))
        print(f"wrote palette -> {em / src} (shared with the front pic)")
    elif src:
        print(f"palette comes from {src}: install the matching front pic for the colours")
    return 0


def cmd_inspect(a) -> int:
    """Material map of a back pic strip: each palette index in a false colour, all frames."""
    from PIL import ImageDraw

    em = emerald_dir()
    p = Path(a.png)
    frames, cols = back.read_strip(p)
    if (em / "graphics/trainers/palettes" / f"{p.stem}.pal").exists():
        cols = pal.load_jasc(em / "graphics/trainers/palettes" / f"{p.stem}.pal")
    elif (em / "graphics/trainers/front_pics" / p.name).exists():
        cols = back.read_strip(em / "graphics/trainers/front_pics" / p.name)[1]
    false = [(0, 0, 0), (255, 0, 0), (0, 200, 0), (0, 80, 255), (255, 200, 0), (255, 0, 255), (0, 220, 220), (255, 128, 0),
             (128, 0, 255), (0, 128, 64), (160, 80, 40), (255, 160, 200), (120, 120, 120), (200, 255, 120), (0, 0, 128), (255, 255, 255)]
    z = 4
    n = len(frames)
    out = Image.new("RGB", (n * 64 * z + 270, 2 * 64 * z + 8), (30, 30, 36))
    counts = {}
    for f, g in enumerate(frames):
        real = Image.new("RGB", (64, 64), (115, 197, 164))
        fc = Image.new("RGB", (64, 64), (40, 40, 48))
        for y in range(64):
            for x in range(64):
                v = g[y][x]
                counts[v] = counts.get(v, 0) + 1
                if v:
                    real.putpixel((x, y), tuple(cols[v]))
                    fc.putpixel((x, y), false[v])
        out.paste(real.resize((64 * z, 64 * z), Image.NEAREST), (f * 64 * z, 0))
        out.paste(fc.resize((64 * z, 64 * z), Image.NEAREST), (f * 64 * z, 64 * z + 8))
    d = ImageDraw.Draw(out)
    x0 = n * 64 * z + 10
    for i in range(16):
        y = 6 + i * 22
        d.rectangle([x0, y, x0 + 16, y + 16], fill=false[i])
        d.rectangle([x0 + 20, y, x0 + 36, y + 16], fill=tuple(cols[i]))
        d.text((x0 + 42, y + 3), f"{i:>2}  {tuple(cols[i])}  {counts.get(i, 0)} px", fill=(230, 230, 230))
        print(f"{i:>2} {tuple(cols[i])!s:<18} {counts.get(i, 0):>5} px")
    out.save(a.out)
    print(f"wrote {a.out}")
    return 0


def all_specs() -> list:
    return [spec_mod.load(p) for p in sorted((TOOL / "art").glob("*.yaml"))]


def cmd_review(a) -> int:
    specs = [spec_mod.load(p) for p in a.specs] if a.specs else all_specs()
    em = emerald_dir()
    items = []
    for s in specs:
        fr = front_for(s, em)
        items.append((s.name, (fr[0], fr[1]) if fr else None, s.frames, spec_mod.palette16(s)))
    back.review(items, Path(a.out), em if (em / "graphics/battle_environment").exists() else None)
    print(f"wrote {a.out}")
    return 0


def cmd_shifts(a) -> int:
    """How far the head moves between frames of a back pic strip: match frame 0's head box
    (`--box x y w h`, default the top-right where every vanilla head is) against each other
    frame. Use the result as a layer's `shift:` so one head edit lands on all four frames."""
    frames, _ = back.read_strip(Path(a.png))
    bx, by, bw, bh = a.box
    f0 = frames[0]
    for f in range(1, len(frames)):
        best = None
        for dy in range(-10, 11):
            for dx in range(-14, 15):
                sc = 0
                for y in range(by, by + bh):
                    for x in range(bx, bx + bw):
                        v = f0[y][x]
                        X, Y = x + dx, y + dy
                        if v and 0 <= X < 64 and 0 <= Y < 64 and frames[f][Y][X] == v:
                            sc += 1
                if best is None or sc > best[0]:
                    best = (sc, dx, dy)
        print(f"frame {f}: shift [{best[1]}, {best[2]}]  ({best[0]} pixels match)")
    return 0


def cmd_corpus(a) -> int:
    c = back.build_corpus(emerald_dir())
    print(f"measured {c['count']} vanilla back frames -> {back.CORPUS_FILE.relative_to(TOOL)}")
    for k in c["median"]:
        print(f"  {k:<14} p5 {c['p5'][k]:>7}  median {c['median'][k]:>7}  p95 {c['p95'][k]:>7}")
    return 0


def cmd_status(a) -> int:
    import csv

    import yaml

    f = TOOL.parents[1] / "wiki/mapping/art_subjects.csv"
    subj = {}
    if f.exists():
        with f.open() as fh:
            subj = {r["asset_id"]: r["sw_subject"] for r in csv.DictReader(fh) if "/trainers/back_pics/" in r["asset_id"]}
    by_pic = {}
    for p in sorted((TOOL / "art").glob("*.yaml")):
        d = yaml.safe_load(p.read_text())
        by_pic.setdefault(d.get("replaces"), []).append(d["name"])
    for pic in sorted(set(subj) | {k for k in by_pic if k}):
        names = by_pic.get(pic, [])
        brief = subj.get(pic, "(not in the wiki)")
        built = [n for n in names if (OUT / n / f"{n}.png").exists()]
        state = "keep" if "kept" in brief.lower() else ("built" if built else ("spec" if names else "todo"))
        print(f"{state:<6} {Path(pic).stem:<12} {','.join(names):<14} {brief}")
    return 0


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="trainer_back_sprite")
    sub = p.add_subparsers(dest="cmd", required=True)
    bp = sub.add_parser("build")
    bp.add_argument("spec")
    bp.add_argument("--front", help="front pic PNG to pair with and check the palette against")
    bp.set_defaults(fn=cmd_build)
    for name, fn in (("verify", cmd_verify), ("install", cmd_install)):
        sp = sub.add_parser(name)
        sp.add_argument("spec")
        sp.set_defaults(fn=fn)
    ip = sub.add_parser("inspect")
    ip.add_argument("png")
    ip.add_argument("out")
    ip.set_defaults(fn=cmd_inspect)
    rp = sub.add_parser("review")
    rp.add_argument("out")
    rp.add_argument("specs", nargs="*")
    rp.set_defaults(fn=cmd_review)
    shp = sub.add_parser("shifts")
    shp.add_argument("png")
    shp.add_argument("--box", type=int, nargs=4, default=[20, 0, 40, 36])
    shp.set_defaults(fn=cmd_shifts)
    sub.add_parser("corpus").set_defaults(fn=cmd_corpus)
    sub.add_parser("status").set_defaults(fn=cmd_status)
    a = p.parse_args(argv)
    try:
        return a.fn(a)
    except spec_mod.SpecError as e:
        print(f"spec error: {e}", file=sys.stderr)
        return 2
