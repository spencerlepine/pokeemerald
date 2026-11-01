"""Ship approved walkers into the wiki: python batches/ship.py report.jsonl

Each line of the report is a worker's JSON line: {"name", "path", "note", "verify_ok", ...}.
For each: copy output/<name>/<name>.png to wiki/art/<path>, add or replace its row in
wiki/mapping/art_ready.csv, then run wiki/tools/mark_art_ready.py. Lines with verify_ok false are
skipped and listed.
"""
import csv
import json
import shutil
import subprocess
import sys
from pathlib import Path

TOOL = Path(__file__).resolve().parents[1]
WIKI = TOOL.parents[1] / "wiki"
READY = WIKI / "mapping" / "art_ready.csv"

lines = [json.loads(l) for l in Path(sys.argv[1]).read_text().splitlines() if l.strip().startswith("{")]
with READY.open(encoding="utf-8", newline="") as f:
    r = csv.DictReader(f)
    cols, rows = r.fieldnames, list(r)
by_id = {x["asset_id"]: x for x in rows}
skipped = []
for d in lines:
    if not d.get("verify_ok"):
        skipped.append(d["name"]); continue
    png = TOOL / "output" / d["name"] / f"{d['name']}.png"
    if not png.exists():
        skipped.append(d["name"]); continue
    dst = WIKI / "art" / d["path"]
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(png, dst)
    row = {"asset_id": d["path"], "art_file": f"art/{d['path']}",
           "drawn_by": f"sprite-walker-generator (art/{d['name']}.yaml)", "notes": d.get("note", "")}
    if d["path"] in by_id:
        by_id[d["path"]].update(row)
    else:
        rows.append(row); by_id[d["path"]] = row
with READY.open("w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=cols, lineterminator="\n")
    w.writeheader(); w.writerows(rows)
subprocess.run([sys.executable, "tools/mark_art_ready.py"], cwd=WIKI, check=True, stdout=subprocess.DEVNULL)
print(f"shipped {len(lines) - len(skipped)}; skipped {skipped}")
