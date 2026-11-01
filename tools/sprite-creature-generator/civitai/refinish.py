#!/usr/bin/env python3
"""Free (no Buzz): re-process an installed creature from its saved full-size downloads with other
finish settings, e.g. a looser palette, then reinstall and commit it.

    python refinish.py skitty --colours 15 --despeckle 0       # 15 colours (the GBA max), keep fine detail
    python refinish.py skitty aggron --colours 14 --no-push
    python refinish.py skitty --colours 15 --preview           # write runs/<sp>/refinish/ only, no install
    python refinish.py kirlia --mirror-back                    # back = mirrored front download (free)
    python refinish.py altaria --pair runs/altaria/raw/<front>.png runs/altaria/raw/<back>.png   # install a chosen take

The raw 768x768 downloads live in runs/<species>/raw/ (front and back, with a .json of seed and prompt).
This finds the pair behind the installed sprites (the front by its finished folder; the back by
re-finishing each candidate and matching the installed back.png), remembers it in
runs/<species>/sources.json, and runs `finish` again with your settings.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import batch  # noqa: E402


def finish(sp: str, front: Path, back: Path, out: Path, extra: list[str]) -> str:
    r = subprocess.run([sys.executable, str(HERE / "civitai_creature.py"), "finish", str(front), str(back),
                        "--frame2", "lunge", "--shiny", "--species", sp, "--out", str(out), *extra],
                       capture_output=True, text=True, cwd=HERE)
    return r.stdout + r.stderr + (f"\nexit {r.returncode}" if r.returncode else "")


def sources(sp: str) -> tuple[Path, Path] | None:
    front = batch.installed_front_raw(sp)
    if not front:
        return None
    sj = HERE / "runs" / sp / "sources.json"  # the downloads behind the installed sprites
    if sj.exists():
        s = json.loads(sj.read_text())
        if HERE / s["front"] == front:  # stale after a --redo installed a new take
            return HERE / s["front"], HERE / s["back"]
    want = (batch.ART / "graphics" / "pokemon" / sp / "back.png").read_bytes()
    raw = HERE / "runs" / sp / "raw"
    cands = sorted((p for p in raw.glob("*_back_*.png") if p.stem > front.stem), key=lambda p: p.stem)
    seed = front.stem.split("_s")[-1]
    cands.sort(key=lambda p: (not p.stem.endswith(f"_s{seed}"), p.stem))  # same-seed back first
    for b, (c, d) in ((b, cd) for b in cands for cd in (("12", "1"), ("15", "0"))):  # batch settings before/after 2026-11-01 18:40
        with tempfile.TemporaryDirectory() as t:
            finish(sp, front, b, Path(t), ["--colours", c, "--despeckle", d])
            if (Path(t) / "back.png").exists() and (Path(t) / "back.png").read_bytes() == want:
                sj.write_text(json.dumps({"front": str(front.relative_to(HERE)), "back": str(b.relative_to(HERE))}, indent=1) + "\n")
                return front, b
    return None


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("species", nargs="+")
    ap.add_argument("--colours", type=int, default=15, help="sprite colours, max 15 (batch used 12)")
    ap.add_argument("--despeckle", type=int, default=0, help="lone-pixel cleanup passes (batch used 1)")
    ap.add_argument("--fit", choices=["auto", "trim", "shrink"])
    ap.add_argument("--preview", action="store_true", help="only write runs/<sp>/refinish/<front>/, do not install")
    ap.add_argument("--pair", nargs=2, metavar=("FRONT_RAW", "BACK_RAW"),
                    help="install this take instead (one species): raw front + back .png from runs/<sp>/raw/")
    ap.add_argument("--mirror-back", action="store_true",
                    help="back = the front download mirrored (same colours and shape, free; for backs that keep drifting)")
    ap.add_argument("--no-push", dest="push", action="store_false")
    a = ap.parse_args()
    if a.pair and len(a.species) != 1:
        sys.exit("--pair takes one species")
    batch.args = a
    extra = ["--colours", str(a.colours), "--despeckle", str(a.despeckle)] + (["--fit", a.fit] if a.fit else [])
    for sp in a.species:
        src = tuple(Path(p).resolve() for p in a.pair) if a.pair else sources(sp)
        if src and a.mirror_back:
            from PIL import Image
            m = src[0].with_name(src[0].stem + "_mirrorback.png")
            Image.open(src[0]).transpose(Image.FLIP_LEFT_RIGHT).save(m)
            src = (src[0], m)
        if not src:
            print(f"SKIP {sp}: could not find the downloads behind the installed sprites"); continue
        front, back = src
        out = HERE / "runs" / sp / ("refinish" if a.preview else "refinished") / front.stem
        log = finish(sp, front, back, out, extra)
        if "exit" in log.splitlines()[-1] or not (out / "anim_front.png").exists():
            print(f"SKIP {sp}: finish failed: {log.strip().splitlines()[-1][:200]}"); continue
        if a.preview:
            print(f"PREVIEW {sp}: {out.relative_to(batch.REPO)}"); continue
        if a.pair or a.mirror_back:
            (HERE / "runs" / sp / "sources.json").write_text(json.dumps({"front": str(front.relative_to(HERE)), "back": str(back.relative_to(HERE))}, indent=1) + "\n")
        files, notes, drawn = batch.install(sp, out, f"re-finished free from the saved downloads, {a.colours} colours, despeckle {a.despeckle}")
        if a.mirror_back:
            notes["back.png"] = notes["back.png"].split(",")[0] + ", the front download mirrored (generated backs kept drifting), same palette"
        batch.commit(sp, files, notes, drawn, out, msg=f"re-finished from the saved downloads ({a.colours} colours, despeckle {a.despeckle}), no Buzz")
        print(f"DONE {sp}: {a.colours} colours, despeckle {a.despeckle}")


if __name__ == "__main__":
    main()
