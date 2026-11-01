"""python -m vfx <command> ... (see README.md)."""
from __future__ import annotations

import argparse
import csv
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from . import catalog, lint, preview
from .game import GAME, HERE, OUT, WIKI, WIKI_ART
from .sheet import read_indexed


def cmd_catalog(a):
    cat = catalog.build()
    ents = cat["entries"].values()
    from collections import Counter
    print(f"{len(cat['entries'])} sheets -> corpus/catalog.json")
    for g, n in sorted(Counter(e["group"] for e in ents).items()):
        print(f"  {g:22s} {n}")


def cmd_show(a):
    for key in a.sheet:
        e = catalog.find(key)
        p = e["palette"]
        print(f"{e['id']}  ({e['group']})")
        print(f"  file      {e['path']}  {e.get('size')}  {e.get('mode')}  {e.get('bitdepth')}bpp")
        print(f"  frames    {e.get('frame')} x {e.get('frame_slots')} slots; the game shows {e.get('frames_used')}"
              + (f"; tile order -mwidth {e['mwidth']} -mheight {e['mheight']}" if e.get("mwidth", 1) > 1 else ""))
        if e.get("tags"):
            print(f"  tags      {', '.join(e['tags'])}  ({e.get('bytes')} bytes)")
        print(f"  palette   {p.get('kind')}: {p.get('source')}" + (f"  SHARED with {p['shared_with_tags']}" if p.get("shared_with_tags") else ""))
        if p.get("note"):
            print(f"            {p['note']}")
        for t in p.get("touched_by", [])[:6]:
            print(f"  runtime   {t}")
        for t in e.get("templates", [])[:8]:
            seq = [f"{c['tile']}:{c['dur']}" for an in t["anims"] for c in an["cmds"] if "tile" in c][:10]
            print(f"  template  {t['name']} {t.get('frame')} cb={t.get('callback')} anim[{' '.join(seq)}]"
                  + (f" users={','.join(t.get('users', [])[:4])}" if t.get("users") else ""))
        if e.get("users"):
            print(f"  used by   {', '.join(e['users'][:20])}" + (" ..." if len(e["users"]) > 20 else ""))
        w = e.get("wiki", {})
        if w.get("asset_id"):
            print(f"  wiki      {w['asset_id']} {w['art_status']} {w['swap_kind']} {w.get('sw_subject', '')}")
        if a.card and e.get("exists"):
            d = OUT / "_inspect"
            d.mkdir(parents=True, exist_ok=True)
            out = d / (e["id"].replace("/", "__") + ".png")
            preview.sheet_card(GAME / e["path"], e["frame"], e.get("mwidth", 1), e.get("mheight", 1),
                               title=e["id"], used=e.get("frames_used")).save(out)
            print(f"  card      {out}")


def cmd_corpus(a):
    d = lint.corpus()
    print(f"{len(d['sheets'])} vanilla sheets measured -> corpus/style.json")
    for g, b in d["bands"].items():
        print(f"  {g}: n={b['coverage']['n']}")


def cmd_lint(a):
    for f in a.png:
        pix, cols = read_indexed(f)
        if a.like:
            e = catalog.find(a.like)
            frame, group, mw, mh = e["frame"], e["group"], e.get("mwidth", 1), e.get("mheight", 1)
            van = lint.load_corpus()["sheets"].get(e["id"])
        else:
            frame, group, mw, mh, van = [pix.shape[1], pix.shape[0]], a.group, 1, 1, None
        m = lint.metrics(pix, cols, frame, mw, mh)
        s, lines = lint.score(m, group, van)
        print(f"{f}: STYLE SCORE {s}/100")
        for l in lines:
            print("  " + l)


def cmd_build(a):
    from .pipeline import run
    from .spec import load_spec
    worst = 0
    for p in a.spec:
        r = run(load_spec(p))
        print("\n".join(r["lines"]))
        b = r["built"]
        print(f"  -> {b.png}")
        for k in ("gif", "strip"):
            if r.get(k):
                print(f"  -> {r[k]}")
        print()
        gate_fail = any(l.startswith("palette gate: FAIL") for l in r["lines"])
        worst = max(worst, 2 if gate_fail else (1 if r["score"] < 80 else 0))
    sys.exit(2 if worst == 2 else 0)


def cmd_review(a):
    """One sheet for the owner: per spec, vanilla vs new sheet cards and the battle/overworld still."""
    from PIL import Image
    from .spec import load_spec
    rows = []
    for p in a.spec:
        s = load_spec(p)
        d = OUT / s["name"]
        parts = []
        for f in ("sheet.png", "battle_strip.png", "overworld_still.png"):
            if (d / f).exists():
                parts.append(Image.open(d / f).convert("RGB"))
        if not parts:
            print(f"{p}: not built yet")
            continue
        w = max(x.width for x in parts)
        h = sum(x.height for x in parts) + 8 * len(parts)
        im = Image.new("RGB", (w, h), preview.BG_RGB)
        y = 0
        for x in parts:
            im.paste(x, (0, y))
            y += x.height + 8
        rows.append(im)
    if not rows:
        return
    w = max(r.width for r in rows)
    h = sum(r.height for r in rows) + 16 * len(rows)
    out = Image.new("RGB", (w, h), (12, 12, 16))
    y = 0
    for r in rows:
        out.paste(r, (0, y))
        y += r.height + 16
    out.save(a.out)
    print(a.out)


def cmd_verify(a):
    """Round trip through pokeemerald's own gbagfx: PNG -> .4bpp (+ .gbapal) -> PNG, pixels identical."""
    gbagfx = GAME / "tools/gbagfx/gbagfx"
    if not gbagfx.exists():
        sys.exit("gbagfx not built: run `make -C ../../game/tools/gbagfx` (or the play-tester setup)")
    from .spec import load_spec
    ok_all = True
    for p in a.spec:
        s = load_spec(p)
        d = OUT / s["name"]
        info = json.loads((d / "build.json").read_text())
        png = d / info["png"]
        try:
            e = catalog.find(info["replaces"])
        except KeyError:
            e = None   # a NEW sheet: no vanilla contract
        opts = (e or {}).get("gfx_opts", "") or ""
        with tempfile.TemporaryDirectory() as td:
            t = Path(td)
            subprocess.run([str(gbagfx), str(png), str(t / "a.4bpp")] + opts.split(), check=True)
            subprocess.run([str(gbagfx), str(png), str(t / "a.gbapal")], check=True)
            w = info["size"][0]
            back_args = ["-width", str(w // 8)] + opts.split() + ["-palette", str(t / "a.gbapal")]
            subprocess.run([str(gbagfx), str(t / "a.4bpp"), str(t / "b.png")] + back_args, check=True)
            p1, c1 = read_indexed(png)
            p2, c2 = read_indexed(t / "b.png")
            same = p1.shape == p2.shape and (p1 == p2).all()
            # gbagfx expands 5-bit colour back as (v << 3) | (v >> 2): compare the 15-bit values
            pal_same = [tuple(v >> 3 for v in x) for x in c1[:16]] == [tuple(v >> 3 for v in x) for x in c2[:16]]
            nbytes = (t / "a.4bpp").stat().st_size
        exp = (e or {}).get("bytes")
        size_ok = exp is None or nbytes >= exp
        print(f"{s['name']}: pixels {'identical' if same else 'DIFFER'}, palette {'identical' if pal_same else 'DIFFERS'}, "
              f"{nbytes} bytes of tiles" + (f" (game loads {exp})" if exp else "") + ("" if size_ok else " TOO SMALL"))
        ok_all &= same and pal_same and size_ok
    sys.exit(0 if ok_all else 1)


def cmd_install(a):
    """Copy built sheets to the wiki art folder (default: approved art waiting to be ported) or into game/."""
    from gba_palette import check as pcheck
    from .spec import load_spec
    for p in a.spec:
        s = load_spec(p)
        d = OUT / s["name"]
        info = json.loads((d / "build.json").read_text())
        png = d / info["png"]
        rep = pcheck.check_png(png, pal=[tuple(c) for c in info["palette"]] if info["palette_locked"] else None)
        if not rep.ok:
            sys.exit(f"{s['name']}: palette gate fails, not installing:\n" + "\n".join(rep.lines()))
        target_rel = info["replaces"]
        root = GAME if a.to == "game" else WIKI_ART
        dst = root / target_rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(png, dst)
        print(f"{s['name']}: {png.name} -> {dst}")
        if a.to == "wiki" and a.mark_ready:
            ready = WIKI / "mapping" / "art_ready.csv"
            rows = list(csv.reader(open(ready, encoding="utf-8")))
            if not any(r and r[0] == target_rel for r in rows[1:]):
                with open(ready, "a", encoding="utf-8", newline="") as f:
                    w = csv.writer(f)
                    hdr = rows[0]
                    rec = {h: "" for h in hdr}
                    rec[hdr[0]] = target_rel
                    if "drawn_by" in rec:
                        rec["drawn_by"] = "vfx-generator"
                    w.writerow([rec[h] for h in hdr])
                print(f"  + {ready.name} row (run python3 ../../wiki/tools/mark_art_ready.py)")


def cmd_story(a):
    from . import anim
    from .game import GAME
    if a.action == "build":
        syms = anim.GameSymbols(GAME)
        kits = [anim.build_kit(anim.load_story(p), run_pipeline=not a.no_build) for p in a.story]
        files, notes = anim.patches(GAME, kits, syms)
        for sb in kits:
            d = OUT / sb.name / "anim"
            d.mkdir(parents=True, exist_ok=True)
            (d / "script.s").write_text(anim.script_block(sb, syms, kits)[0])
            (d / f"battle_anim_sw_{sb.name}.c").write_text(files[f"src/battle_anim_sw_{sb.name}.c"])
            print(f"# {sb.name} on {sb.host}: {len(sb.sheets)} sheets, {len(sb.story.get('templates') or {})} templates")
            for l in sb.notes:
                print("  " + l)
            print(f"  -> {d / 'script.s'}")
        for n in notes:
            print("  NOTE " + n)
        print(f"patches {len(files)} game files: " + ", ".join(sorted(files)))
    elif a.action == "romtest":
        from .animtest import run as rt
        rt(a)
    elif a.action == "install":
        from .animtest import install
        install(a)


def cmd_romtest(a):
    from .romtest import run as rt
    rt(a)


def main(argv=None):
    ap = argparse.ArgumentParser(prog="python -m vfx", description="Star Wars VFX in Emerald's format")
    sp = ap.add_subparsers(dest="cmd", required=True)
    s = sp.add_parser("catalog", help="re-read the game source into corpus/catalog.json")
    s.set_defaults(fn=cmd_catalog)
    s = sp.add_parser("show", help="the contract of a vanilla sheet (frames, palette, users)")
    s.add_argument("sheet", nargs="+")
    s.add_argument("--card", action="store_true", help="also write a zoomed card to output/_inspect/")
    s.set_defaults(fn=cmd_show)
    s = sp.add_parser("corpus", help="measure the vanilla style into corpus/style.json")
    s.set_defaults(fn=cmd_corpus)
    s = sp.add_parser("lint", help="style score of any sheet")
    s.add_argument("png", nargs="+")
    s.add_argument("--like", help="score as a replacement for this vanilla sheet")
    s.add_argument("--group", default="battle_anim_sprite")
    s.set_defaults(fn=cmd_lint)
    s = sp.add_parser("build", help="spec -> sheet + gate + style score + previews")
    s.add_argument("spec", nargs="+")
    s.set_defaults(fn=cmd_build)
    s = sp.add_parser("review", help="owner review sheet for several built specs")
    s.add_argument("out")
    s.add_argument("spec", nargs="+")
    s.set_defaults(fn=cmd_review)
    s = sp.add_parser("verify", help="round trip through the game's gbagfx")
    s.add_argument("spec", nargs="+")
    s.set_defaults(fn=cmd_verify)
    s = sp.add_parser("install", help="copy built sheets to wiki/art (default) or game/")
    s.add_argument("spec", nargs="+")
    s.add_argument("--to", choices=["wiki", "game"], default="wiki")
    s.add_argument("--mark-ready", action="store_true", help="also add the wiki/mapping/art_ready.csv row")
    s.set_defaults(fn=cmd_install)
    s = sp.add_parser("romtest", help="build a scratch ROM with the sheets and film them in a real battle")
    s.add_argument("spec", nargs="+")
    s.add_argument("--fresh", action="store_true")
    s.set_defaults(fn=cmd_romtest)
    s = sp.add_parser("story", help="storyboards: build the kit + script, film it in a ROM, install into game/")
    s.add_argument("action", choices=["build", "romtest", "install"])
    s.add_argument("story", nargs="+", help="art/moves/<name>.yaml (or just the name)")
    s.add_argument("--fresh", action="store_true")
    s.add_argument("--no-build", action="store_true", help="reuse the sheets already in output/")
    s.set_defaults(fn=cmd_story)
    a = ap.parse_args(argv)
    a.fn(a)
