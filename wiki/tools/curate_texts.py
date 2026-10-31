r"""Write a curated dialogue file (mapping/texts/*.csv) from a small Python spec.

    python3 tools/curate_texts.py spec.py mapping/texts/act1_03_x.csv

The spec is a Python file defining
    FIX = {text_id: [(old, new), ...] | "full replacement text" | []}
    NOTES = {text_id: "note"}            (optional)
KEEP_REST_MAPS = ("map:x", ...) (optional) accepts every other AUTO draft on
those maps as reviewed. The tool rebuilds without the output file first, so pairs always apply to
fresh AUTO drafts. A list of (old, new) pairs is applied to the current AUTO draft (an empty list
keeps the draft as reviewed). Write "\\n" as a plain \n inside normal strings;
\l and \p can be typed as is. Pairs whose new text is already present are
skipped, so a spec still works after a glossary fix. The output CSV is the
source of truth; the spec is just a convenience and need not be committed.
"""
import csv, re, sys, runpy, warnings
warnings.simplefilter("ignore")
E = lambda x: x.replace("\n", "\\n")
spec = runpy.run_path(sys.argv[1]); FIX = spec["FIX"]; NOTES = spec.get("NOTES", {})
# work from fresh AUTO drafts: rebuild without the file being (re)written
import os, subprocess
from pathlib import Path
outp = Path(sys.argv[2]); bak = outp.with_suffix(".csv.bak")
if outp.exists():
    outp.rename(bak)
try:
    subprocess.run([sys.executable, "tools/build.py"], check=True, stdout=subprocess.DEVNULL)
finally:
    if bak.exists():
        bak.unlink()
auto = {r["text_id"]: r for r in csv.DictReader(open("database/texts.csv", encoding="utf-8"))}
out = []
for tid, fx in FIX.items():
    assert tid in auto, tid
    base = auto[tid]["sw_text_raw"] if auto[tid]["text_status"] != "CURATED" or tid in spec.get("REDO", ()) else auto[tid]["sw_text_raw"]
    if isinstance(fx, str):
        s = E(fx)
    else:
        s = base
        for a, b in fx:
            a, b = E(a), E(b)
            if a not in s and b in s: continue
            if a not in s:
                print(f"MISS {tid}: {a!r}\n     in {s!r}")
                continue
            s = s.replace(a, b)
    out.append([tid, s, NOTES.get(tid, "")])
# KEEP_REST_FILES: same, for whole shared source files ("data/text/battle_dome.inc")
# KEEP_REST_MAPS: every other text on these maps was read and its AUTO draft is accepted as is
# Trainer battle lines (data/text/trainers.inc) and a few map-specific shared files have no map_id: derive it from
# the text id prefix ("Route131_..." -> map:route131). Other shared systems (TV, match call, day care, contests)
# are reviewed in C3i, not here.
MAP_TEXT_FILES = ("data/text/trainers.inc", "data/text/braille.inc", "data/text/shoal_cave.inc")


def map_of(tid, r):
    if r["map_id"]:
        return r["map_id"]
    if r.get("source_file") not in MAP_TEXT_FILES:
        return ""
    head = tid.split("_")[0]
    return "map:" + re.sub(r"(?<=[a-z0-9])(?=[A-Z])", "-", head).lower() if head[:1].isupper() else ""


for tid, r in auto.items():
    on_map = map_of(tid, r) and map_of(tid, r).startswith(tuple(spec.get("KEEP_REST_MAPS", ())))
    in_file = r.get("source_file") in spec.get("KEEP_REST_FILES", ())
    if tid not in FIX and (on_map or in_file) and r["text_status"] in ("AUTO", "UNCHANGED"):
        out.append([tid, r["sw_text_raw"], "reviewed AUTO draft" if r["text_status"] == "AUTO" else "reviewed, no change needed"])
# REFLOW = True: a paragraph with a line wider than the text box (208 px, or the widest original line) is
# re-wrapped greedily; its first break stays \n and later breaks become \l (scroll).
if spec.get("REFLOW"):
    import build

    def reflow(text, raw):
        lim = max([208] + [build.line_px(x) for x in re.split(r"\\[nlp]", raw)])
        end = "$" if text.endswith("$") else ""
        paras = (text[:-1] if end else text).split("\\p")
        for i, para in enumerate(paras):
            lines = re.split(r"\\[nl]", para)
            if all(build.line_px(x) <= lim for x in lines):
                continue
            words, cur, new = " ".join(lines).split(" "), "", []
            for wd in words:
                t = (cur + " " + wd) if cur else wd
                if build.line_px(t) > lim and cur:
                    new.append(cur); cur = wd
                else:
                    cur = t
            new.append(cur)
            paras[i] = "\\n".join(new[:2]) + "".join("\\l" + x for x in new[2:])
        return "\\p".join(paras) + end

    for row in out:
        row[1] = reflow(row[1], auto[row[0]]["emerald_text_raw"])
w = csv.writer(open(sys.argv[2], "w", newline="", encoding="utf-8"))
w.writerow(["text_id", "sw_text_raw", "notes"]); w.writerows(out)
print(len(out), "rows ->", sys.argv[2])
