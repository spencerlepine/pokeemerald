"""ROM test for storyboards: patch a scratch copy of the game with the kits and scripts, film the move.

Reuses romtest's scratch trees (/var/tmp/vfx-romtest/{vanilla,new}/game), make, Lua filming and report.
Source patches are tracked in <tree>/patched.json so a later run restores the originals first.
"""
from __future__ import annotations

import json
import shutil
from pathlib import Path

from . import anim, romtest
from .game import GAME, OUT


def _apply(g: Path, files: dict[str, str], installs: dict[str, Path]):
    man = g.parent / "patched.json"
    prev = json.loads(man.read_text()) if man.exists() else []
    for rel in prev:
        src = GAME / rel
        dst = g / rel
        if src.exists():
            shutil.copy2(src, dst)
        elif dst.exists():
            dst.unlink()
    for rel, text in files.items():
        dst = g / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_text(text)
    for rel, src in installs.items():
        dst = g / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
    man.write_text(json.dumps(sorted(set(files) | set(installs))))


def run(a):
    kits = []
    for p in a.story:
        st = anim.load_story(p)
        kits.append(anim.build_kit(st, run_pipeline=not a.no_build))
    syms = anim.GameSymbols(GAME)
    files, notes = anim.patches(GAME, kits, syms)
    installs = anim.installs(kits)
    for sb in kits:
        d = OUT / sb.name / "anim"
        d.mkdir(parents=True, exist_ok=True)
        (d / "script.s").write_text(anim.script_block(sb, syms, kits)[0])
        (d / f"battle_anim_sw_{sb.name}.c").write_text(files[f"src/battle_anim_sw_{sb.name}.c"])
    for n in notes:
        print("  NOTE " + n)
    for sb in kits:
        rt = sb.story.get("romtest") or {}
        mv = rt.get("move")
        if not mv:
            raise SystemExit(f"{sb.name}: storyboard needs romtest.move")
        print(f"== {sb.name}: {mv} on {sb.host}")
        gv = romtest._prepare("vanilla", {}, mv, a.fresh)
        _apply(gv, {}, {})
        gn = romtest._prepare("new", {}, mv, a.fresh)
        _apply(gn, files, installs)
        for g in (gv, gn):
            print(f"  make {g}")
            romtest._make(g)
        mid = romtest._move_id(mv)
        res = {}
        species, capture = int(rt.get("species", 280)), int(rt.get("capture", 900))
        hpf, tap_until = float(rt.get("hp", 1.0)), int(rt.get("tap_until", 660))
        for which, g in (("vanilla", gv), ("new", gn)):
            out = romtest.WORK / which / "film"
            ok = romtest._film(g / "pokeemerald.gba", out, mid, species, capture, romtest._sym(g, "CB2_Overworld"),
                               romtest._sym(g, "BattleMainCB2"), hpf, tap_until)
            print(f"  film {which}: {'ok' if ok else 'FAILED'}")
            res[which] = out if ok else None
        if all(res.values()):
            romtest._report({"name": sb.name}, res["vanilla"], res["new"])


def install(a):
    """Apply the kits to ../../game (the real tree). Only after the owner approved the ROM film."""
    kits = [anim.build_kit(anim.load_story(p), run_pipeline=not a.no_build) for p in a.story]
    syms = anim.GameSymbols(GAME)
    files, notes = anim.patches(GAME, kits, syms, ship=True)
    for n in notes:
        print("  NOTE " + n)
    for rel, text in files.items():
        (GAME / rel).parent.mkdir(parents=True, exist_ok=True)
        (GAME / rel).write_text(text)
        print(f"  patched {rel}")
    for rel, src in anim.installs(kits).items():
        (GAME / rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, GAME / rel)
        print(f"  {src.name} -> {rel}")
