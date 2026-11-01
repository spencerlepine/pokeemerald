"""python -m gba_palette <command> ...   (run from tools/palette-enforcer/, see README.md)

  themes                      list the wiki's themes and groups, and lint them
  check   <png|pal>...        the gate: exit 1 on any error
  enforce <in> <out>          post-process a render into a legal indexed PNG
  audit   <dir>               check every PNG and .pal under a folder (summary)
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import check, core, enforce, themes


def _theme(names):
    return themes.resolve(names) if names else None


def _pal(path):
    return core.load_jasc(path) if path else None


def cmd_themes(a) -> int:
    ts = themes.load()
    for t in ts.values():
        print(f"{t.id:22} {len(t.swatches):2} colours  {t.title}")
        if a.verbose:
            for s in t.swatches:
                print(f"    {core.hex_of(s.colour)}  {s.role:10} {s.name}")
    for g, ids in themes.GROUPS.items():
        print(f"{g:22} group: {' + '.join(ids)}")
    errs = themes.lint()
    for e in errs:
        print("error:", e)
    return 1 if errs else 0


def cmd_check(a) -> int:
    bad = 0
    th, pal = _theme(a.theme), _pal(a.pal)
    for p in a.paths:
        if p.endswith(".pal"):
            rep = check.check_pal(p, strict_step=not a.lenient)
        else:
            rep = check.check_png(p, bpp=a.bpp, pal=pal, theme=th, strict_theme=a.strict_theme,
                                  tolerance=a.tolerance, strict_step=not a.lenient, tile=a.tile)
        bad += not rep.ok
        print("\n".join(rep.lines()))
    return 1 if bad else 0


def cmd_enforce(a) -> int:
    key = None
    if a.key:
        key = "auto" if a.key == "auto" else core.parse_hex(a.key)
    palette = enforce.enforce_file(
        a.src, a.dst, write_pal=a.write_pal, bpp=a.bpp, pal=_pal(a.pal), theme=_theme(a.theme),
        tolerance=a.tolerance, free=0 if a.strict_theme else a.free, colours=a.colours, key=key,
        zero=core.parse_hex(a.zero) if a.zero else None,
    )
    rep = check.check_png(a.dst, bpp=a.bpp, pal=_pal(a.pal), theme=_theme(a.theme),
                          strict_theme=a.strict_theme, tolerance=a.tolerance,
                          strict_step=not a.pal)  # a locked palette is vanilla's file, kept verbatim
    print("\n".join(rep.lines()))
    if a.write_pal:
        print(f"wrote {a.write_pal}")
    return 0 if rep.ok else 1


def cmd_audit(a) -> int:
    root = Path(a.dir)
    n = bad = 0
    for p in sorted(list(root.rglob("*.png")) + list(root.rglob("*.pal"))):
        rep = check.check_pal(p, strict_step=not a.lenient) if p.suffix == ".pal" else \
            check.check_png(p, strict_step=not a.lenient)
        n += 1
        if not rep.ok or (a.verbose and rep.warnings):
            print("\n".join(rep.lines()))
        bad += not rep.ok
    print(f"{n} files, {bad} failing")
    return 1 if bad else 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="gba_palette", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("themes")
    s.add_argument("-v", "--verbose", action="store_true")
    s.set_defaults(fn=cmd_themes)

    def lock_args(s):
        s.add_argument("--bpp", type=int, choices=[1, 2, 4, 8], help="target bit depth (check: default from the PNG; enforce: 4)")
        s.add_argument("--pal", help="locked .pal: indices and colours must match it (shared palettes)")
        s.add_argument("--theme", action="append", help="theme id or group from `themes` (repeatable)")
        s.add_argument("--strict-theme", action="store_true", help="every colour must come from the theme")
        s.add_argument("--tolerance", type=float, default=12.0, help="Delta E within which a colour counts as the theme colour (default 12)")

    s = sub.add_parser("check")
    s.add_argument("paths", nargs="+")
    lock_args(s)
    s.add_argument("--lenient", action="store_true", help="off-step colours are warnings (vanilla files)")
    s.add_argument("--tile", action="store_true", help="size must be a multiple of 8")
    s.set_defaults(fn=cmd_check)

    s = sub.add_parser("enforce")
    s.add_argument("src")
    s.add_argument("dst")
    lock_args(s)
    s.add_argument("--free", type=int, help="with --theme: at most N colours may stay off-theme (default: any beyond --tolerance)")
    s.add_argument("--colours", "--colors", type=int, help="at most N colours (default: all the bit depth allows)")
    s.add_argument("--key", help="#RRGGBB background to make transparent, or 'auto' (top-left pixel)")
    s.add_argument("--zero", help="#RRGGBB for index 0 (default: the key, else #F800F8)")
    s.add_argument("--write-pal", help="also write the palette as JASC .pal")
    s.set_defaults(fn=cmd_enforce, bpp=None)

    s = sub.add_parser("audit")
    s.add_argument("dir")
    s.add_argument("--lenient", action="store_true")
    s.add_argument("-v", "--verbose", action="store_true")
    s.set_defaults(fn=cmd_audit)

    a = ap.parse_args(argv)
    if a.cmd == "enforce" and a.bpp is None:
        a.bpp = 4
    return a.fn(a)


if __name__ == "__main__":
    sys.exit(main())
