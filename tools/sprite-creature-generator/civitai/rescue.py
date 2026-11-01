#!/usr/bin/env python3
"""Free: re-judge a skipped species' earlier takes (raw front+back already paid for) with the current
checks, and install the first that passes.  python rescue.py bagon barboach ..."""
import argparse, re, subprocess, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import batch

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("species", nargs="+"); ap.add_argument("--no-push", dest="push", action="store_false")
    batch.args = a = ap.parse_args()
    for sp in a.species:
        raw = HERE / "runs" / sp / "raw"
        fronts = sorted(raw.glob("*_front_*.png"), reverse=True)
        backs = sorted(raw.glob("*_back_*.png"))
        res = f"SKIP {sp}: no takes"
        for f in fronts:
            seed = f.stem.split("_s")[-1]
            b = [x for x in backs if x.stem.endswith(f"_s{seed}") and x.stem > f.stem]
            if not b:
                continue
            out = HERE / "runs" / sp / "finished" / f.stem
            r = subprocess.run([sys.executable, str(HERE / "civitai_creature.py"), "finish", str(f), str(b[0]),
                                "--frame2", "lunge", "--shiny", "--species", sp, "--out", str(out)], capture_output=True, text=True, cwd=HERE)
            log = r.stdout + r.stderr
            if r.returncode:
                continue
            ok, note = batch.judge(out, log + "\n--frame2 pass--\n" + log)
            if ok:
                files, notes, drawn = batch.install(sp, out, note)
                batch.commit(sp, files, notes, drawn, out)
                res = f"DONE {sp}: {note} (rescued {f.stem})"; break
            res = f"SKIP {sp}: {note}"
        print(res, flush=True)

if __name__ == "__main__":
    main()
