#!/usr/bin/env python3
"""Generate every pending trainer front pic in parallel, auto-pick a take, install it in the wiki, commit.

No human review: each trainer gets one generation (1 image, ~3 Buzz); if that take fails the
automatic checks it gets one retry with a new seed, then it is skipped and reported.

    python batch.py --list                      # what is still pending
    python batch.py --budget 300 -j 4           # run them all, stop before spending more than 300 Buzz
    python batch.py steven wally --no-push      # just these

Automatic checks on a finished take (from civitai_trainer.py finish):
  * palette-enforcer `check` PASS (4bpp, 15 colours + transparent, GBA steps)
  * the pixel grid was found (8 px, so 96 native), figure at least 34 px tall and 18 px wide
  * at least 8 colours and 500 opaque pixels in the 64x64 cell (not a speck or a blank)

A picked take is copied to wiki/art/<asset path> (and its .pal next to the shared-palette files for
the trainers whose back pic shares the palette), its pending_art.csv row goes to ART_READY, a row is
added to wiki/mapping/art_ready.csv, and that one trainer is committed and pushed (rebase first).
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
JOBS = json.loads((HERE / "jobs.json").read_text())
SHARED_PAL = {"brendan", "brendan_rs", "may", "may_rs", "wally", "steven"}  # palettes/<stem>.pal
COST = 3  # Buzz per 1-image jpeg job (measured whatif)
AUTHOR = "spencerlepine <60903378+spencerlepine@users.noreply.github.com>"

git_lock = threading.Lock()
spend_lock = threading.Lock()
spent = 0
stop = threading.Event()


def pending() -> list[dict]:
    rows = []
    with CSV.open(newline="") as f:
        for r in csv.DictReader(f):
            if r["art_status"] != "PENDING_ART":
                continue
            if (r["kind"] == "trainers" and r["subkind"] == "front_pics") or r["path"] == "graphics/birch_speech/birch.png":
                rows.append(r)
    return rows


def all_rows() -> list[dict]:
    with CSV.open(newline="") as f:
        return [r for r in csv.DictReader(f) if (r["kind"] == "trainers" and r["subkind"] == "front_pics")
                or r["path"] == "graphics/birch_speech/birch.png"]


def stem_of(r: dict) -> str:
    return Path(r["path"]).stem


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


def judge(final: Path, log: str, pair: bool = False) -> tuple[bool, str]:
    m = re.search(r"grid (\d+)px -> native (\d+), figure (\d+)x(\d+)", log)
    if "PASS" not in log or not m:
        return False, "check failed"
    period, _, fw, fh = map(int, m.groups())
    a = np.array(Image.open(final).convert("RGBA"))
    opaque = a[..., 3] > 0
    colours = len(np.unique(a[opaque][:, :3], axis=0))
    if period < 6 or period > 10:
        return False, f"grid {period}px"
    if fh < 34 or fw < 18:
        return False, f"figure {fw}x{fh} too small"
    if opaque.sum() < 500 or colours < 8:
        return False, f"{opaque.sum()} px, {colours} colours"
    nat = final.with_name(final.stem + "_native.png")
    if figures(nat) >= (3 if pair else 2):
        return False, "extra figures (duplicate or turnaround)"
    if pair and figures(nat, 0.15) < 2:
        return False, "pair pic with one figure"
    na = np.array(Image.open(nat).convert("RGBA"))[..., 3] > 0
    if na[0, 0] and na[0, -1] and na[-1, 0] and na[-1, -1]:
        return False, "background box left"
    if max(na[0].mean(), na[:, 0].mean(), na[:, -1].mean()) > 0.8:  # a solid bbox edge = a box
        return False, "background box left"
    return True, f"figure {fw}x{fh}, {colours} colours"


def generate(stem: str) -> tuple[Path | None, str]:
    """One paid take. Returns (finished png or None, log)."""
    global spent
    with spend_lock:
        if stop.is_set() or spent + COST > args.budget:
            stop.set()
            return None, "budget reached"
        spent += COST
    r = subprocess.run([sys.executable, str(HERE / "civitai_trainer.py"), "run", stem, "-n", "1", "--currency", args.currency],
                       capture_output=True, text=True, cwd=HERE)
    log = r.stdout + r.stderr
    if "Insufficient" in log or "insufficientBuzz" in log:
        stop.set()
        return None, "insufficient Buzz"
    if r.returncode:
        return None, log.strip().splitlines()[-1][:300] if log.strip() else f"exit {r.returncode}"
    m = re.findall(r"-> (tools/\S+\.png)", log)
    return (REPO / m[-1] if m else None), log


def install(row: dict, final: Path, log: str, note: str) -> list[Path]:
    stem = stem_of(row)
    dst = ART / row["path"]
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(final, dst)
    out = [dst]
    if stem in SHARED_PAL:
        pal = ART / "graphics" / "trainers" / "palettes" / f"{stem}.pal"
        pal.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(final.with_suffix(".pal"), pal)
        out.append(pal)
    meta = json.loads(final.parent.parent.joinpath("raw", final.name).with_suffix(".json").read_text())
    j = JOBS.get(stem, {})
    pal_note = (f"palette written to art/graphics/trainers/palettes/{stem}.pal (the back pic must adopt it)"
                if stem in SHARED_PAL else "palette from the PNG")
    notes = (f"art: art/{row['path']}; {j.get('subject', row['sw_subject'])} front pic; Civitai LoRA "
             f"159333@{meta['lora']['id']} on SDXL base, seed {meta['seed']}, {note}, {j.get('theme', 'factions')}; "
             f"{pal_note}; auto-picked, no human review")
    drawn = f"sprite-trainer-generator/civitai (jobs.json {stem})"
    return out, notes, drawn


def update_wiki(row: dict, notes: str, drawn: str):
    with CSV.open(newline="") as f:
        rd = csv.DictReader(f)
        fields, rows = rd.fieldnames, list(rd)
    for r in rows:
        if r["asset_id"] == row["asset_id"]:
            r["art_status"], r["drawn_by"], r["art_notes"] = "ART_READY", drawn, notes
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=fields, lineterminator="\n")
    w.writeheader(); w.writerows(rows)
    CSV.write_text(buf.getvalue())
    lines = [l for l in ART_READY.read_text().splitlines(keepends=True)
             if not l.startswith(row["asset_id"] + ",")]
    buf = io.StringIO()
    csv.writer(buf, lineterminator="\n").writerow([row["asset_id"], f"art/{row['path']}", drawn, notes.split("; ", 1)[1]])
    ART_READY.write_text("".join(lines) + buf.getvalue())


def git(*a, check=True):
    return subprocess.run(["git", *a], cwd=REPO, capture_output=True, text=True, check=check)


def commit(row: dict, files: list[Path], notes: str, drawn: str):
    stem = stem_of(row)
    with git_lock:
        if args.push:
            git("pull", "--rebase", "--autostash", "-q", "origin", "master")
        update_wiki(row, notes, drawn)
        paths = [str(p.relative_to(REPO)) for p in files] + [
            str(CSV.relative_to(REPO)), str(ART_READY.relative_to(REPO)),
            str((HERE / "runs" / stem).relative_to(REPO))]
        git("add", "--", *paths)
        subject = JOBS.get(stem, {}).get("subject", row["sw_subject"])
        git("-c", "user.name=spencerlepine", "-c", "user.email=60903378+spencerlepine@users.noreply.github.com",
            "commit", "-q", f"--author={AUTHOR}", "-m",
            f"sprite-trainer-generator: {subject} ({stem}) front pic to wiki/art, ART_READY (auto-picked)")
        if args.push:
            for _ in range(4):
                if git("push", "-q", "origin", "HEAD:master", check=False).returncode == 0:
                    break
                git("pull", "--rebase", "--autostash", "-q", "origin", "master")


def do(row: dict) -> str:
    stem = stem_of(row)
    reasons = []
    for attempt in range(2):
        final, log = generate(stem)
        if final is None:
            reasons.append(log if len(log) < 300 else "error")
            if stop.is_set():
                break
            continue
        ok, note = judge(final, log, bool(JOBS.get(stem, {}).get("pair")))
        if ok:
            files, notes, drawn = install(row, final, log, note)
            commit(row, files, notes, drawn)
            return f"DONE {stem}: {note}"
        reasons.append(note)
    return f"SKIP {stem}: {'; '.join(reasons)}"


def refinish(row: dict) -> str:
    """Re-run the (free) finisher on the picked raw of an auto-picked row and re-install it."""
    stem = stem_of(row)
    m = re.search(r"seed (\d+)", row["art_notes"])
    raws = sorted((HERE / "runs" / stem / "raw").glob(f"*_s{m.group(1)}.png")) if m else []
    if not raws:
        return f"FAIL {stem}: raw not found"
    theme = JOBS.get(stem, {}).get("theme", "factions")
    r = subprocess.run([sys.executable, str(HERE / "civitai_trainer.py"), "finish", str(raws[-1]), "--theme", theme],
                       capture_output=True, text=True, cwd=HERE)
    log = r.stdout + r.stderr
    final = raws[-1].parent.parent / "finished" / raws[-1].name
    ok, note = judge(final, log, bool(JOBS.get(stem, {}).get("pair")))
    if not ok:
        return f"BAD {stem}: {note}"
    files, notes, drawn = install(row, final, log, note)
    with git_lock:
        update_wiki(row, notes, drawn)
    return f"OK {stem}: {note}"


def main():
    global args
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("only", nargs="*", help="trainer stems (default: every pending row)")
    ap.add_argument("--redo", action="store_true", help="regenerate the named trainers even if ART_READY")
    ap.add_argument("--refinish", action="store_true", help="re-finish every auto-picked row from its raw (free), no commit")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--budget", type=int, default=0, help="max Buzz to spend this run (required)")
    ap.add_argument("--currency", default="green", help="Buzz account(s): green (bought), blue (earned), yellow")
    ap.add_argument("-j", type=int, default=4, help="parallel jobs")
    ap.add_argument("--no-push", dest="push", action="store_false")
    args = ap.parse_args()
    rows = [r for r in pending() if not args.only or stem_of(r) in args.only]
    if args.redo:
        rows = [r for r in all_rows() if stem_of(r) in args.only]
    if args.refinish:
        done = [r for r in all_rows() if "auto-picked" in r["art_notes"] and (not args.only or stem_of(r) in args.only)]
        with cf.ThreadPoolExecutor(args.j) as ex:
            for res in ex.map(refinish, done):
                print(res, flush=True)
        return
    if args.list or not args.budget:
        for r in rows:
            print(f"{stem_of(r):24} {r['sw_subject']}")
        print(f"{len(rows)} pending, about {len(rows) * COST} Buzz for one take each")
        return
    with cf.ThreadPoolExecutor(args.j) as ex:
        for res in ex.map(do, rows):
            print(res, flush=True)
    print(f"spent about {spent} Buzz")


if __name__ == "__main__":
    main()
