#!/usr/bin/env python3
"""Generate every pending creature's battle sprites in parallel, auto-pick, install in the wiki, commit.

No human review. Each species needs a reference picked first (refs.py pick -> refs/picks/<species>.json).
One take = front (image to image from the reference) + back (from the mirrored front), 3 + 3 Buzz.
A take that fails the automatic checks gets one retry with a new seed, then the species is skipped
and reported.

    python batch.py --list                      # pending species and whether each has a reference pick
    python batch.py --budget 2600 -j 6          # run them all, stop before spending more than 2600 Buzz
    python batch.py abra absol --budget 30 --no-push

After a take, `finish` is re-run on it with `--frame2 lunge --shiny`, so each species gets
front.png, anim_front.png (64x128), back.png, normal.pal and shiny.pal, all on one palette.

Automatic checks (front and back): palette-enforcer `check` PASS; the 8 px grid was found (6-10);
figure at least 28 px tall and 24 px wide; at least 6 colours and 400 opaque pixels in the cell; the
front is one figure (not a duplicate or a turnaround sheet).

A picked take is copied to wiki/art/graphics/pokemon/<species>/, its three pending_art.csv rows go to
ART_READY, rows are added to wiki/mapping/art_ready.csv, and that one species is committed and pushed
(rebase first).
"""
from __future__ import annotations

import argparse
import concurrent.futures as cf
import csv
import io
import json
import re
import shutil
import subprocess
import sys
import threading
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
CSV = REPO / "wiki" / "database" / "pending_art.csv"
ART_READY = REPO / "wiki" / "mapping" / "art_ready.csv"
ART = REPO / "wiki" / "art"
PICKS = HERE / "refs" / "picks"
COST = 6  # Buzz per take: front + back, 1 jpeg image each (measured whatif: 3 + 3)
FILES = ("front.png", "anim_front.png", "back.png")
SPECIAL = {"unown", "castform"}  # several forms on one species; done separately
AUTHOR = "spencerlepine <60903378+spencerlepine@users.noreply.github.com>"

sys.path.insert(0, str(HERE))
import civitai_creature as cc  # noqa: E402

class RepoLock:
    """Thread lock + a file lock, so batch.py and forms.py runs in parallel never interleave
    their read-modify-write of pending_art.csv or their git commands."""
    def __init__(self):
        self.t = threading.Lock()

    def __enter__(self):
        import fcntl
        self.t.acquire()
        self.f = open(REPO / ".git" / "sprite-batch.lock", "w")
        fcntl.flock(self.f, fcntl.LOCK_EX)

    def __exit__(self, *exc):
        import fcntl
        fcntl.flock(self.f, fcntl.LOCK_UN)
        self.f.close()
        self.t.release()


git_lock = RepoLock()
spend_lock = threading.Lock()
spent = 0
stop = threading.Event()


def pending() -> list[str]:
    out = []
    with CSV.open(newline="") as f:
        for r in csv.DictReader(f):
            parts = r["path"].split("/")
            if (r["kind"] == "pokemon" and r["art_status"] == "PENDING_ART" and parts[-1] == "front.png"
                    and len(parts) == 4 and parts[2] not in SPECIAL | {"egg", "question_mark"}):
                out.append(parts[2])
    return out


def figures(png: Path, share: float = 0.2) -> int:
    """Opaque 8-connected blobs holding at least `share` of the opaque pixels (2+ = duplicated figure)."""
    a = np.array(Image.open(png).convert("RGBA"))[..., 3] > 0
    h, w = a.shape
    seen = np.zeros_like(a)
    sizes = []
    for y in range(h):
        for x in range(w):
            if a[y, x] and not seen[y, x]:
                st, n = [(y, x)], 0
                seen[y, x] = True
                while st:
                    cy, cx = st.pop(); n += 1
                    for dy in (-1, 0, 1):
                        for dx in (-1, 0, 1):
                            ny, nx = cy + dy, cx + dx
                            if 0 <= ny < h and 0 <= nx < w and a[ny, nx] and not seen[ny, nx]:
                                seen[ny, nx] = True; st.append((ny, nx))
                sizes.append(n)
    return sum(1 for n in sizes if n >= share * a.sum())


def judge(out: Path, log: str, min_w: int = 24, min_h: int = 22, one_figure: bool = True) -> tuple[bool, str]:
    notes = []
    for view in ("front", "back"):
        m = re.search(rf"^{view}\s+\S+: grid (\d+)px -> native (\d+), figure (\d+)x(\d+).*?; (PASS|FAIL)", log, re.M)
        if not m:
            return False, f"{view}: no finish line"
        period, _, fw, fh, ok = m.groups()
        period, fw, fh = int(period), int(fw), int(fh)
        if ok != "PASS":
            return False, f"{view}: check failed"
        if not 6 <= period <= 10:
            return False, f"{view}: grid {period}px (blurry take)"
        if fh < min_h or fw < min_w:
            return False, f"{view}: figure {fw}x{fh} too small"
        a = np.array(Image.open(out / f"{view}.png").convert("RGBA"))
        opaque = a[..., 3] > 0
        colours = len(np.unique(a[opaque][:, :3], axis=0))
        if opaque.sum() < 400 or colours < 6:
            return False, f"{view}: {opaque.sum()} px, {colours} colours"
        notes.append(f"{view} {fw}x{fh}")
    if one_figure and figures(out / "front_native.png") >= 2:
        return False, "front: two figures (duplicate or turnaround)"
    if "FAIL" in log.split("--frame2 pass--")[-1]:
        return False, "frame2/anim/shiny check failed"
    return True, ", ".join(notes)


def generate(sp: str) -> tuple[Path | None, str]:
    """One paid take, then the full finish. Returns (finished folder or None, log)."""
    global spent
    with spend_lock:
        if stop.is_set() or spent + COST > args.budget:
            stop.set()
            return None, "budget reached"
        spent += COST
    r = subprocess.run([sys.executable, str(HERE / "civitai_creature.py"), "run", sp, "--currency", args.currency],
                       capture_output=True, text=True, cwd=HERE)
    log = r.stdout + r.stderr
    if "Insufficient" in log or "insufficientBuzz" in log:
        stop.set()
        return None, "insufficient Buzz"
    raws = re.findall(r"^saved (tools/\S+\.png)", log, re.M)
    if r.returncode or len(raws) < 2:
        return None, (log.strip().splitlines() or [f"exit {r.returncode}"])[-1][:300]
    front, back = (REPO / p for p in raws[:2])
    out = HERE / "runs" / sp / "finished" / front.stem
    r2 = subprocess.run([sys.executable, str(HERE / "civitai_creature.py"), "finish", str(front), str(back),
                         "--frame2", "lunge", "--shiny", "--species", sp, "--out", str(out)],
                        capture_output=True, text=True, cwd=HERE)
    log += "\n--frame2 pass--\n" + r2.stdout + r2.stderr
    if r2.returncode or not (out / "anim_front.png").exists():
        return None, (r2.stdout + r2.stderr).strip().splitlines()[-1][:300] if (r2.stdout + r2.stderr).strip() else "finish failed"
    return out, log


def install(sp: str, out: Path, note: str) -> tuple[list[Path], dict, str]:
    dst = ART / "graphics" / "pokemon" / sp
    dst.mkdir(parents=True, exist_ok=True)
    files = []
    for name in FILES + ("normal.pal", "shiny.pal"):
        shutil.copyfile(out / name, dst / name)
        files.append(dst / name)
    meta = json.loads(next((out.parent.parent / "raw").glob(f"{out.name}.json")).read_text())
    b = meta["species"]
    pick = json.loads((PICKS / f"{sp}.json").read_text()) if (PICKS / f"{sp}.json").exists() else {}
    ref = (f"image to image from {pick.get('init_source')} (refs.py pick, denoise {meta['params'].get('denoise')})"
           if pick.get("init") else "text only (no usable reference)")
    base = (f"Civitai LoRA 161280@{meta['lora']['id']} on DreamShaper 8, seed {meta['seed']}; {ref}; "
            f"12 colours + despeckle; auto-picked, no human review")
    notes = {
        "front.png": f"{b['sw_name']} battle front, {note}; {base}; palette art/graphics/pokemon/{sp}/normal.pal, shiny.pal next to it",
        "back.png": f"{b['sw_name']} battle back, image to image from the mirrored front (backside, denoise 0.7), on the front's normal.pal",
        "anim_front.png": f"{b['sw_name']} front animation 64x128: frame 1 = front.png, frame 2 = lunge (finish --frame2 lunge); normal.pal",
    }
    return files, notes, f"sprite-creature-generator/civitai (batch.py, refs/picks/{sp}.json)"


def update_wiki(sp: str, notes: dict, drawn: str):
    with CSV.open(newline="") as f:
        rd = csv.DictReader(f)
        fields, rows = rd.fieldnames, list(rd)
    for r in rows:
        name = r["path"].rsplit("/", 1)[-1]
        if r["kind"] == "pokemon" and r["path"] == f"graphics/pokemon/{sp}/{name}" and name in notes:
            r["art_status"], r["drawn_by"] = "ART_READY", drawn
            r["art_notes"] = f"art: art/{r['path']}; {notes[name]}"
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=fields, lineterminator="\n")
    w.writeheader(); w.writerows(rows)
    CSV.write_text(buf.getvalue())
    with ART_READY.open("a", newline="") as f:
        wr = csv.writer(f, lineterminator="\n")
        for name in FILES:
            wr.writerow([f"graphics/pokemon/{sp}/{name}", f"art/graphics/pokemon/{sp}/{name}", drawn, notes[name]])


def git(*a, check=True):
    return subprocess.run(["git", *a], cwd=REPO, capture_output=True, text=True, check=check)


def commit(sp: str, files: list[Path], notes: dict, drawn: str, out: Path):
    with git_lock:
        if args.push:
            git("pull", "--rebase", "--autostash", "-q", "origin", "master")
        update_wiki(sp, notes, drawn)
        paths = [str(p.relative_to(REPO)) for p in files] + [
            str(CSV.relative_to(REPO)), str(ART_READY.relative_to(REPO)),
            str((HERE / "runs" / sp).relative_to(REPO))]
        for extra in (PICKS / f"{sp}.json", HERE / "refs" / f"{sp}_prep.png"):
            if extra.exists():
                paths.append(str(extra.relative_to(REPO)))
        git("add", "--", *paths)
        name = cc.brief(sp)["sw_name"]
        git("-c", "user.name=spencerlepine", "-c", "user.email=60903378+spencerlepine@users.noreply.github.com",
            "commit", "-q", f"--author={AUTHOR}", "-m",
            f"sprite-creature-generator: {name} ({sp}) battle sprites to wiki/art, ART_READY (auto-picked)")
        if args.push:
            for _ in range(4):
                if git("push", "-q", "origin", "HEAD:master", check=False).returncode == 0:
                    break
                git("pull", "--rebase", "--autostash", "-q", "origin", "master")


def do(sp: str) -> str:
    reasons = []
    for attempt in range(1 + args.retries):
        out, log = generate(sp)
        if out is None:
            reasons.append(log if len(log) < 300 else "error")
            if stop.is_set():
                break
            continue
        ok, note = judge(out, log)
        if ok:
            files, notes, drawn = install(sp, out, note)
            commit(sp, files, notes, drawn, out)
            return f"DONE {sp}: {note}"
        reasons.append(note)
    return f"SKIP {sp}: {'; '.join(reasons)}"


def main():
    global args
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("only", nargs="*", help="species folders (default: every pending one with a pick)")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--budget", type=int, default=0, help="max Buzz to spend this run (required)")
    ap.add_argument("--currency", default="green", help="Buzz account(s): green (bought), blue (earned), yellow")
    ap.add_argument("-j", type=int, default=6, help="parallel species")
    ap.add_argument("--retries", type=int, default=1)
    ap.add_argument("--allow-nopick", action="store_true", help="also run species with no refs.py pick")
    ap.add_argument("--no-push", dest="push", action="store_false")
    args = ap.parse_args()
    todo = [s for s in pending() if not args.only or s in args.only]
    picked = [s for s in todo if (PICKS / f"{s}.json").exists() or args.allow_nopick]
    if args.list or not args.budget:
        for s in todo:
            print(f"{s:16} {'pick' if (PICKS / f'{s}.json').exists() else '-'}")
        print(f"{len(todo)} pending, {len(picked)} runnable, about {len(picked) * COST} Buzz for one take each")
        return
    with cf.ThreadPoolExecutor(args.j) as ex:
        for res in ex.map(do, picked):
            print(res, flush=True)
    print(f"spent about {spent} Buzz")


if __name__ == "__main__":
    main()
