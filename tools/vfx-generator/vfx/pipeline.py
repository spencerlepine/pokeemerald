"""build = draw (spec.py) -> palette gate -> style score -> previews. One call per spec."""
from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

from gba_palette import check as pcheck
from gba_palette import themes as pthemes

from . import lint, preview
from .game import GAME
from .pal import load_palette_file
from .spec import Built, build as build_spec


def gate(b: Built) -> list[str]:
    theme = None
    th = b.spec.get("theme")
    if th:
        try:
            theme = pthemes.resolve(th if isinstance(th, list) else [th])
        except Exception as ex:   # noqa: BLE001
            return [f"WARN theme {th!r}: {ex}"]
    rep = pcheck.check_png(b.png, pal=b.pal.colours[:16] if b.pal.locked else None, theme=theme)
    lines = rep.lines()
    return (["palette gate: PASS"] if rep.ok else ["palette gate: FAIL"]) + ["  " + l for l in lines]


def _template_seq(entry: dict, motion: dict, frame) -> list:
    per = (frame[0] // 8) * (frame[1] // 8)
    if motion.get("anim"):
        cmds = [{"tile": int(f) * per, "dur": int(d), "hflip": False, "vflip": False} for f, d in motion["anim"]]
        cmds.append({"jump": 0} if motion.get("loop", True) else {"end": True})
        return preview.anim_sequence(cmds, per)
    tpls = [t for t in entry.get("templates", []) if t.get("frame") == list(frame) and t.get("anims")]
    ti = int(motion.get("template", 0))
    if tpls:
        t = tpls[min(ti, len(tpls) - 1)]
        ai = int(motion.get("anim_index", 0))
        cmds = t["anims"][min(ai, len(t["anims"]) - 1)]["cmds"]
        tile_start = entry.get("tile_start", 0) or 0
        cmds = [dict(c, tile=c["tile"] - tile_start) if "tile" in c else c for c in cmds]
        return preview.anim_sequence(cmds, per)
    return preview.anim_sequence([], per)


def battle_mockup(b: Built) -> tuple[Path | None, Path | None]:
    pv = b.spec.get("preview") or {}
    if pv.get("scene", "battle") != "battle":
        return None, None
    motion = pv.get("motion", {"kind": "projectile", "frames": 30})
    scene = preview.Scene(pv.get("env", "tall_grass"), pv.get("attacker", "piloswine"), pv.get("target", "porygon"))
    length = int(pv.get("length", motion.get("frames", 30) + 20))
    seq = _template_seq(b.entry, motion, b.frame)
    mw, mh = b.entry.get("mwidth", 1), b.entry.get("mheight", 1)
    new = preview.SheetFrames(b.png, b.frame, mw, mh)
    panels_new = preview.simulate(scene, new, motion, seq, length)
    panels_old = None
    if b.entry.get("exists"):
        old = preview.SheetFrames(GAME / b.entry["path"], b.frame, mw, mh)
        panels_old = preview.simulate(scene, old, pv.get("vanilla_motion", motion), seq, length)
    frames = []
    for k in range(length):
        row = [("NEW: " + b.spec.get("title", b.spec["name"]), panels_new[k])]
        if panels_old:
            row = [("VANILLA", panels_old[k])] + row
        frames.append(preview.labelled([(t, preview.zoom(p, 2)) for t, p in row]))
    gif = b.out_dir / "battle.gif"
    imgs = [f.convert("P", palette=Image.ADAPTIVE, colors=255, dither=Image.NONE) for f in frames[::2]]
    imgs[0].save(gif, save_all=True, append_images=imgs[1:], duration=33, loop=0, optimize=False)
    # still strip: 6 moments of the new effect, 2x
    picks = [int(x) for x in np.linspace(0, max(0, min(length, motion.get("frames", 30) + 4) - 1), 6)]
    strip = preview.labelled([(f"f{k}", preview.zoom(panels_new[k], 2)) for k in picks])
    png = b.out_dir / "battle_strip.png"
    strip.save(png)
    return gif, png


def overworld_mockup(b: Built) -> tuple[Path | None, Path | None]:
    pv = b.spec.get("preview") or {}
    if pv.get("scene") != "overworld":
        return None, None
    motion = pv.get("motion", {"kind": "still"})
    bg = preview.overworld_bg(pv.get("layout", "LAYOUT_LITTLEROOT_TOWN"), *pv.get("at", [10, 9]))
    pals = []
    pk = b.entry.get("palette", {})
    if pk.get("kind") == "player":
        pals = [("boy", load_palette_file(GAME / pk["source"])),
                ("girl", load_palette_file(GAME / pk.get("alt_sources", [pk["source"]])[0]))]
    else:
        pals = [("", None)]
    mw, mh = b.entry.get("mwidth", 1), b.entry.get("mheight", 1)
    seq = _template_seq(b.entry, motion, b.frame)
    length = int(pv.get("length", 60))
    rows = []
    for gender, pal in pals:
        sheets = [("NEW", preview.SheetFrames(b.png, b.frame, mw, mh, pal))]
        if b.entry.get("exists"):
            sheets.insert(0, ("VANILLA", preview.SheetFrames(GAME / b.entry["path"], b.frame, mw, mh, pal)))
        pl = preview.player_walker("boy" if gender != "girl" else "girl")
        per = []
        for label, sf in sheets:
            out = []
            for f in range(length):
                im = bg.copy()
                px, py = 120, 88
                im.alpha_composite(pl, (px - 8, py - 24))
                u = f / max(1, length - 1)
                if motion.get("kind") == "fly_across":
                    x = 260 - 200 * u
                    y = py - 40 + 30 * math.sin(math.pi * u)
                elif motion.get("kind") == "fly_in":
                    x = 120 + 140 * (1 - u)
                    y = py - 8 - 60 * (1 - u)
                else:
                    x, y = px + motion.get("offset", [0, 0])[0], py + motion.get("offset", [0, 0])[1]
                k, hf, vf = seq[min(f, len(seq) - 1)]
                spr = sf.get(k, hf ^ bool(motion.get("hflip")), vf)
                preview._blit(im, spr, x, y)
                out.append(im)
            per.append((f"{label} {gender}".strip(), out))
        rows.append(per)
    frames = []
    for k in range(length):
        panels = []
        for per in rows:
            for label, out in per:
                panels.append((label, preview.zoom(out[k], 2)))
        frames.append(preview.labelled(panels))
    gif = b.out_dir / "overworld.gif"
    imgs = [f.convert("P", palette=Image.ADAPTIVE, colors=255, dither=Image.NONE) for f in frames[::2]]
    imgs[0].save(gif, save_all=True, append_images=imgs[1:], duration=33, loop=0, optimize=False)
    png = b.out_dir / "overworld_still.png"
    frames[length // 2].save(png)
    return gif, png


def run(spec: dict) -> dict:
    b = build_spec(spec)
    lines = [f"# {spec['name']}: {spec.get('title', '')}", f"replaces: {b.entry['path']}" if b.entry.get("exists")
             else f"new sheet: {b.entry['path']}", f"sheet {b.size[0]}x{b.size[1]}, frame {b.frame[0]}x{b.frame[1]}, "
             f"slots drawn {b.slots}, game uses {b.entry.get('frames_used')}"]
    lines += b.notes
    lines += gate(b)
    m = lint.metrics(b.sheet, b.pal.colours, b.frame, b.entry.get("mwidth", 1), b.entry.get("mheight", 1), b.slots)
    van = lint.load_corpus()["sheets"].get(b.entry["id"])
    sc, rl = lint.score(m, b.entry.get("group", "battle_anim_sprite"), van, spec.get("lint_allow"))
    lines += [f"STYLE SCORE {sc}/100 (group {b.entry.get('group')})"] + ["  " + l for l in rl]
    # cards
    card_new = preview.sheet_card(b.png, b.frame, b.entry.get("mwidth", 1), b.entry.get("mheight", 1),
                                  title=f"NEW {Path(b.png).name}", used=b.entry.get("frames_used"))
    panels = [("", card_new)]
    if b.entry.get("exists"):
        card_old = preview.sheet_card(GAME / b.entry["path"], b.frame, b.entry.get("mwidth", 1), b.entry.get("mheight", 1),
                                      title=f"VANILLA {Path(b.entry['path']).name}", used=b.entry.get("frames_used"))
        panels.insert(0, ("", card_old))
    preview.labelled(panels).save(b.out_dir / "sheet.png")
    gif, strip = battle_mockup(b)
    ogif, ostill = overworld_mockup(b)
    (b.out_dir / "lint.txt").write_text("\n".join(lines) + "\n")
    (b.out_dir / "metrics.json").write_text(json.dumps({"metrics": m, "vanilla": van, "score": sc}, indent=1))
    return {"built": b, "score": sc, "lines": lines, "gif": gif or ogif, "strip": strip or ostill}
