#!/usr/bin/env python3
"""Battle sprites for the species with several forms: AUREBESH (unown, 28 letters on ONE shared
palette) and CLIMADROID (castform, 4 weathers, each with its own palettes). Same checks, install
and per-form commit as batch.py.

    python forms.py --list
    python forms.py unown --budget 200          # letter a first (it owns unown/normal.pal), then the rest
    python forms.py castform --budget 40

Unown starts: refs/unown/<letter>_glyph.png is the glyph cut from Wookieepedia's Aurebesh chart
(File:Aurebesh-GMSR.png); <letter>_prep.png is that glyph as a 96 px creature start (slate body,
light top edge, outline, one eye). Castform starts from refs/castform_prep.png (refs.py pick: the
Marksman-H training remote), with the weather drawn in by the prompt.
"""
from __future__ import annotations

import argparse
import concurrent.futures as cf
import csv
import re
import shutil
import subprocess
import sys
import threading
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import batch  # noqa: E402

REPO, ART, CSV = batch.REPO, batch.ART, batch.CSV
TAIL = ("pokemon, single creature, full body, {pose}, ({colour} body:1.3), limited palette, muted colours, "
        "pixel art, game sprite, crisp dark outlines, white background, simple background")
UNOWN = ("gen3, (aurebesh:1.1), (living dark letter glyph creature with one big white eye:1.3), "
         "floating symbol creature, psychictype, " + TAIL)
CASTFORM = "gen3, (climadroid:1.1), (small round floating weather probe droid:1.2), ({form}:1.2), " + TAIL
CAST = {  # form: (look, colour, denoise)
    "normal": ("white sphere shell with red sensor rings", "white and red", 0.5),
    "sunny": ("glowing orange sun shaped shell with flare spikes", "orange and yellow", 0.65),
    "rainy": ("blue raindrop shaped shell with a water swirl", "blue", 0.65),
    "snowy": ("pale icy shell with frost crystal spikes", "pale blue and white", 0.65),
}
LETTERS = "a b c d e f g h i j k l m n o p q r s t u v w x y z question_mark exclamation_mark".split()
NAMES = {"question_mark": "?", "exclamation_mark": "!"}


def pending(species: str) -> list[str]:
    out = []
    with CSV.open(newline="") as f:
        for r in csv.DictReader(f):
            p = r["path"].split("/")
            if r["kind"] == "pokemon" and len(p) == 5 and p[2] == species and p[4] == "front.png" \
                    and r["art_status"] == "PENDING_ART":
                out.append(p[3])
    return out


def cc(*a) -> str:
    r = subprocess.run([sys.executable, str(HERE / "civitai_creature.py"), *a], capture_output=True, text=True, cwd=HERE)
    return r.stdout + r.stderr + (f"\nexit {r.returncode}" if r.returncode else "")


def spend() -> bool:
    with batch.spend_lock:
        if batch.stop.is_set() or batch.spent + batch.COST > args.budget:
            batch.stop.set()
            return False
        batch.spent += batch.COST
        return True


def take(species: str, form: str, shared_pal: Path | None) -> tuple[Path | None, str]:
    if not spend():
        return None, "budget reached"
    if species == "unown":
        prompt, init, denoise, label = UNOWN, f"refs/unown/{form}_prep.png", 0.5, f"letter {NAMES.get(form, form)}"
        prompt = prompt.format(pose="facing viewer", colour="dark slate")
    else:
        look, colour, denoise = CAST[form]
        prompt, init, label = CASTFORM.format(form=look, pose="facing left", colour=colour), "refs/castform_prep.png", f"{form} form"
    common = ["--currency", args.currency, "--prompt"]
    log = cc("gen", species, "--init", init, "--denoise", str(denoise), *common, prompt)
    raws = re.findall(r"^saved (tools/\S+\.png)", log, re.M)
    if "Insufficient" in log or "insufficientBuzz" in log:
        batch.stop.set()
        return None, "insufficient Buzz"
    if not raws:
        return None, log.strip().splitlines()[-1][:300]
    front = REPO / raws[0]
    back_prompt = "backside, back view, " + prompt.replace("facing left", "seen from behind").replace("facing viewer", "seen from behind")
    log2 = cc("gen", species, "--view", "back", "--init", str(front), "--flip", "--denoise", "0.7", *common, back_prompt)
    raws2 = re.findall(r"^saved (tools/\S+\.png)", log2, re.M)
    if not raws2:
        return None, log2.strip().splitlines()[-1][:300]
    out = HERE / "runs" / species / form / front.stem
    fin = ["finish", str(front), str(REPO / raws2[0]), "--frame2", "lunge", "--shiny", "--out", str(out)]
    if shared_pal:
        fin += ["--pal", str(shared_pal)]
    flog = cc(*fin)
    if "exit" in flog.splitlines()[-1] or not (out / "anim_front.png").exists():
        return None, flog.strip().splitlines()[-1][:300]
    return out, f"{label}|{flog}\n--frame2 pass--\n{flog}"


def do(species: str, form: str, shared_pal: Path | None) -> str:
    reasons = []
    for _ in range(1 + args.retries):
        out, log = take(species, form, shared_pal)
        if out is None:
            reasons.append(log)
            if batch.stop.is_set():
                break
            continue
        label, log = log.split("|", 1)
        ok, note = (batch.judge(out, log, min_w=8, min_h=14, one_figure=False) if species == "unown"
                    else batch.judge(out, log))
        if not ok:
            reasons.append(note)
            continue
        install(species, form, out, label, note, shared_pal)
        return f"DONE {species}/{form}: {note}"
    return f"SKIP {species}/{form}: {'; '.join(reasons)}"


def install(species, form, out, label, note, shared_pal):
    key = f"{species}/{form}"
    dst = ART / "graphics" / "pokemon" / key
    dst.mkdir(parents=True, exist_ok=True)
    files = []
    for n in batch.FILES:
        shutil.copyfile(out / n, dst / n); files.append(dst / n)
    pal_dir = dst.parent if species == "unown" else dst  # unown: one bank for every letter
    for n in ("normal.pal", "shiny.pal"):
        if species == "unown" and shared_pal and (pal_dir / n).exists():
            continue
        shutil.copyfile(out / n, pal_dir / n); files.append(pal_dir / n)
    name = "AUREBESH" if species == "unown" else "CLIMADROID"
    src = ("the Aurebesh glyph from Wookieepedia File:Aurebesh-GMSR.png (forms.py start image)" if species == "unown"
           else "Wookieepedia Marksman-H training remote (refs/castform_prep.png), weather drawn by the prompt")
    pal_note = (f"palette art/graphics/pokemon/unown/normal.pal shared by all 28 letters" if species == "unown"
                else f"palette art/graphics/pokemon/{key}/normal.pal, shiny.pal next to it")
    notes = {
        "front.png": f"{name} {label} battle front, {note}; image to image from {src}; 12 colours; {pal_note}; auto-picked, no human review",
        "back.png": f"{name} {label} battle back, image to image from the mirrored front (backside, denoise 0.7), same palette",
        "anim_front.png": f"{name} {label} front animation 64x128: frame 2 = lunge; same palette",
    }
    drawn = f"sprite-creature-generator/civitai (forms.py {species})"
    with batch.git_lock:
        if args.push:
            batch.git("pull", "--rebase", "--autostash", "-q", "origin", "master")
        batch.update_wiki(key, notes, drawn)
        paths = [str(p.relative_to(REPO)) for p in files] + [str(CSV.relative_to(REPO)), str(batch.ART_READY.relative_to(REPO)),
                                                            str(out.relative_to(REPO)), str((HERE / "refs" / species).relative_to(REPO)) if species == "unown" else "tools/sprite-creature-generator/civitai/refs/castform_prep.png",
                                                            str((HERE / "runs" / species / "raw").relative_to(REPO))]
        batch.git("add", "--", *[p for p in paths if (REPO / p).exists()])
        batch.git("-c", "user.name=spencerlepine", "-c", "user.email=60903378+spencerlepine@users.noreply.github.com",
                  "commit", "-q", f"--author={batch.AUTHOR}", "-m",
                  f"sprite-creature-generator: {name} {label} ({key}) battle sprites to wiki/art, ART_READY (auto-picked)")
        if args.push:
            for _ in range(4):
                if batch.git("push", "-q", "origin", "HEAD:master", check=False).returncode == 0:
                    break
                batch.git("pull", "--rebase", "--autostash", "-q", "origin", "master")


def main():
    global args
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("species", nargs="?", choices=["unown", "castform"])
    ap.add_argument("forms", nargs="*")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--budget", type=int, default=0)
    ap.add_argument("--currency", default="green")
    ap.add_argument("-j", type=int, default=6)
    ap.add_argument("--retries", type=int, default=1)
    ap.add_argument("--no-push", dest="push", action="store_false")
    args = ap.parse_args()
    batch.args = args
    if args.list or not args.species or not args.budget:
        for s in ("unown", "castform"):
            print(s, " ".join(pending(s)))
        return
    todo = [f for f in pending(args.species) if not args.forms or f in args.forms]
    shared = None
    if args.species == "unown":
        shared = ART / "graphics" / "pokemon" / "unown" / "normal.pal"
        if not shared.exists():  # the first letter done owns the bank
            first = "a" if "a" in todo else todo[0]
            print(do("unown", first, None), flush=True)
            todo.remove(first)
            if not shared.exists():
                sys.exit("first letter failed; not running the rest")
    with cf.ThreadPoolExecutor(args.j) as ex:
        for res in ex.map(lambda f: do(args.species, f, shared), todo):
            print(res, flush=True)
    print(f"spent about {batch.spent} Buzz")


if __name__ == "__main__":
    main()
