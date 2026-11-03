"""Copy the Star Wars text from database/texts.csv into ../game.

    python3 tools/port_texts.py --maps LittlerootTown,Route101     # only these maps (map folder names)
    python3 tools/port_texts.py --files src/main_menu.c,data/scripts/players_house.inc
    python3 tools/port_texts.py --all                             # every row
    add --dry-run to only report

For each row it finds the text in `source_file` by its label (`text_id::` in scripts, `text_id[] = _(` in C),
reads what the game has now and:

  ported    the game still had Emerald's text (or Emerald's text with the names already swapped by
            scan_name_refs): it is replaced by `sw_text_raw`, split into one .string line per \\n, \\l, \\p.
  done      the game already has `sw_text_raw`.
  changed   the game has something else (edited by hand since). Left alone, listed for a person to check.
  missing   the label is not in the file. Left alone, listed.
  skipped   a row of a feature that is being cut (SKIP below, the POKéBLOCK / treat feature).

Rows that end up ported or done get `game_status` DONE in database/texts.csv (a rebuild keeps it).
Prints a summary and writes the changed / missing list to database/text_port_report.csv.
"""
from __future__ import annotations

import argparse
import csv
import os
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GAME = Path(os.environ.get("GAME_DIR", ROOT.parent / "game"))
TEXTS = ROOT / "database" / "texts.csv"
REPORT = ROOT / "database" / "text_port_report.csv"

# The POKéBLOCK feature is being deleted and replaced (owner, 2026-11-03): its text is not ported.
SKIP = re.compile(r"POK[éE]BLOCK|PokéBlock|Pokéblock|BLOCK CASE", re.I)
SKIP_FILES = ("src/pokeblock", "src/use_pokeblock", "src/pokeblock_feed", "data/text/blend_master",
              "src/berry_blender", "data/scripts/berry_blender", "src/data/pokeblock")
# Names already swapped in the game before this tool (tools/scan_name_refs.py): accept them as Emerald text.
NAME_SWAPS = [(r"\bBIRCH\b", "KORR"), (r"\bBRENDAN\b", "KAEL"), (r"\bMAY\b", "MIRA"), (r"\bBRANDON\b", "DEXTER"),
              (r"POKéNAV", "StarNAV")]  # an earlier pass renamed the POKéNAV in place

STR = re.compile(r'"((?:[^"\\]|\\.)*)"')
BREAK = re.compile(r"(\\[nlp])")


def name_swapped(text: str) -> str:
    for a, b in NAME_SWAPS:
        text = re.sub(r"(?:(?<=\\[nlp])|(?<![\w]))" + a.replace("\\b", "", 1), b, text)
    return text


def split_lines(text: str) -> list[str]:
    """Split raw text after each \\n, \\l, \\p, the way Emerald's .string lines are laid out."""
    parts, cur = [], ""
    for piece in BREAK.split(text):
        cur += piece
        if BREAK.fullmatch(piece):
            parts.append(cur)
            cur = ""
    if cur:
        parts.append(cur)
    return parts or [""]


def find_script(lines: list[str], tid: str):
    """Return (first, last) line index of the .string block under label `tid::`, or None."""
    lab = re.compile(rf"^{re.escape(tid)}::?\s*$")
    for i, line in enumerate(lines):
        if lab.match(line):
            j = i + 1
            while j < len(lines) and not lines[j].strip().startswith(".string"):
                if lines[j].strip() and not lines[j].strip().startswith(("@", "//")):
                    return None
                j += 1
            first = j
            while j < len(lines) and lines[j].strip().startswith(".string"):
                j += 1
            return (first, j - 1) if j > first else None
    return None


def script_text(lines, span) -> str:
    return "".join("".join(STR.findall(lines[k])) for k in range(span[0], span[1] + 1))


def find_c(src: str, tid: str):
    """Return (start, end) offsets of `_(...)` holding text `tid`, or None."""
    m = re.search(rf"\b{re.escape(tid)}\s*\[[^\]]*\]\s*=\s*_\(", src)
    if not m:
        return None
    i = m.end()
    j = i
    while True:
        while j < len(src) and src[j] in " \t\r\n":
            j += 1
        sm = STR.match(src, j)
        if not sm:
            break
        j = sm.end()
    while j < len(src) and src[j] in " \t\r\n":
        j += 1
    if j >= len(src) or src[j] != ")":
        return None
    return (m.end() - 2, j + 1)  # covers `_(` ... `)`


def c_text(src: str, span) -> str:
    return "".join(STR.findall(src[span[0]:span[1]]))


def wanted(row, args) -> bool:
    if args.all:
        return True
    f = row["source_file"]
    if args.files and f in args.files:
        return True
    if args.maps:
        m = re.match(r"data/maps/([^/]+)/", f)
        if m and m.group(1) in args.maps:
            return True
    return False


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--maps", default="")
    ap.add_argument("--files", default="")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    args.maps = {m for m in args.maps.split(",") if m}
    args.files = {f for f in args.files.split(",") if f}

    with TEXTS.open(encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        cols = reader.fieldnames
        rows = list(reader)

    by_file = defaultdict(list)
    for r in rows:
        if wanted(r, args):
            by_file[r["source_file"]].append(r)

    stats = Counter()
    report = []
    for f, frows in sorted(by_file.items()):
        path = GAME / f
        if not path.exists():
            for r in frows:
                stats["missing"] += 1
                report.append((r["text_id"], f, "missing", "file not in the game"))
            continue
        src = path.read_text(encoding="utf-8")
        is_script = frows[0]["text_origin"] == "script"
        lines = src.split("\n") if is_script else None
        dirty = False
        for r in frows:
            tid, emer, sw = r["text_id"], r["emerald_text_raw"], r["sw_text_raw"]
            if f.startswith(SKIP_FILES) or SKIP.search(emer):
                stats["skipped"] += 1
                continue
            if is_script:
                span = find_script(lines, tid)
                cur = script_text(lines, span) if span else None
            else:
                span = find_c(src, tid)
                cur = c_text(src, span) if span else None
            if cur is None:
                stats["missing"] += 1
                report.append((tid, f, "missing", "label not found"))
                continue
            if cur == sw:
                stats["done"] += 1
                r["game_status"] = "DONE"
                continue
            if emer.endswith("$$") and cur.endswith("$") and not cur.endswith("$$"):
                emer, sw = emer[:-1], sw[:-1] if sw.endswith("$$") else sw  # the text table doubled the $
            if cur not in (emer, name_swapped(emer)):
                stats["changed"] += 1
                report.append((tid, f, "changed", cur[:200]))
                continue
            stats["ported"] += 1
            r["game_status"] = "DONE"
            dirty = True
            if is_script:
                indent = re.match(r"\s*", lines[span[0]]).group(0)
                new = [f'{indent}.string "{p}"' for p in split_lines(sw)]
                lines[span[0]:span[1] + 1] = new
            else:
                src = src[:span[0]] + f'_("{sw}")' + src[span[1]:]
        if dirty and not args.dry_run:
            path.write_text("\n".join(lines) if is_script else src, encoding="utf-8")

    if not args.dry_run:
        with TEXTS.open("w", encoding="utf-8", newline="") as fh:
            w = csv.DictWriter(fh, cols, lineterminator="\n")
            w.writeheader()
            w.writerows(rows)
        with REPORT.open("w", encoding="utf-8", newline="") as fh:
            w = csv.writer(fh, lineterminator="\n")
            w.writerow(["text_id", "source_file", "result", "game_text"])
            w.writerows(sorted(report, key=lambda x: (x[1], x[0])))
    print(", ".join(f"{k}: {v}" for k, v in sorted(stats.items())))
    return 0


if __name__ == "__main__":
    sys.exit(main())
