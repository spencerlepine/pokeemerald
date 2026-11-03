"""Swap Emerald terms for Star Wars ones in game text that has no curated row: item, move, ability, berry and
decoration descriptions.

    python3 tools/port_terms.py            # FILES below
    python3 tools/port_terms.py --dry-run  # only report

These strings are not in texts.csv, so they get the same automatic pass tools/build.py gives an uncurated
text: every `emerald_term` in database/text_terms.csv (POKéMON -> COMPANION, POKé BALL -> CAPTURE POD,
creature, item and place names...) with the article and plural fixes. A string is left alone when a new line
would be wider than the widest line of that file in Emerald (the description box), or when it is POKéBLOCK
text (that feature is being replaced). Left-alone strings go to database/term_port_report.csv.

A string the automatic pass gets wrong (singular COMPANION where Emerald meant plural, too wide) is written by
hand in mapping/descriptions.csv (`game_file`, `symbol`, `sw_text`); those rows win over the automatic pass.
On top of text_terms, this pass turns a bare BALL into POD (the capture-pod descriptions).
"""
from __future__ import annotations

import argparse
import csv
import os
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import build as B  # noqa: E402  (term regexes, plural and article fixes, font widths)

GAME = Path(os.environ.get("GAME_DIR", ROOT.parent / "game"))
REPORT = ROOT / "database" / "term_port_report.csv"
FILES = ["src/data/text/item_descriptions.h", "src/data/text/move_descriptions.h", "src/data/text/abilities.h",
         "src/data/decoration/description.h", "src/berry.c"]
SKIP = re.compile(r"POK[éE]BLOCK|\{POKEBLOCK\}", re.I)
STR = re.compile(r'"((?:[^"\\]|\\.)*)"')
BLOCK = re.compile(r'_\(\s*((?:"(?:[^"\\]|\\.)*"\s*)+)\)')


def load_terms() -> tuple[dict[str, str], re.Pattern]:
    terms = {}
    with (ROOT / "database" / "text_terms.csv").open(encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            if r["emerald_term"] != r["sw_term"]:
                terms[r["emerald_term"]] = r["sw_term"]
    terms.setdefault("BALL", "POD")
    terms.setdefault("BALLS", "PODS")
    keys = sorted(terms, key=lambda k: (-len(k), k))
    pat = re.compile(r"(?:(?<=\\[nlp])|(?<![A-Za-z0-9é]))(" + "|".join(re.escape(k) for k in keys)
                     + r")(?![A-Za-z0-9é])")
    return terms, pat


def swap(text: str, terms, pat) -> str:
    used = []

    def sub(m):
        used.append(m.group(1))
        return terms[m.group(1)]

    new = pat.sub(sub, text)
    if used:
        new = B.fix_articles(new, {terms[u] for u in used})
    if "COMPANION" in new:
        new = B.PLURAL_AFTER.sub("COMPANIONS", new)
        new = B.PLURAL_BEFORE.sub(lambda m: m.group(1) + "COMPANIONS", new)
        new = B.PLURAL_ADJ.sub(B._plural_adj, new)
    return new


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    terms, pat = load_terms()
    with (ROOT / "mapping" / "descriptions.csv").open(encoding="utf-8") as fh:
        hand = {(r["game_file"], r["symbol"]): r["sw_text"] for r in csv.DictReader(fh)}
    used_hand = set()
    stats, report = Counter(), []
    for f in FILES:
        path = GAME / f
        src = path.read_text(encoding="utf-8")
        blocks = list(BLOCK.finditer(src))
        widest = max((B.line_px(x) for m in blocks for x in re.split(r"\\[nlp]", "".join(STR.findall(m.group(1))))),
                     default=0)
        out, pos = [], 0
        for m in blocks:
            text = "".join(STR.findall(m.group(1)))
            if SKIP.search(text):
                stats["skipped"] += 1
                continue
            sym = re.search(r"(\w+)\s*\[\]\s*=\s*$", src[max(0, m.start() - 120):m.start()])
            key = (f, sym.group(1) if sym else "")
            if key in hand:
                new = hand[key]
                used_hand.add(key)
            else:
                new = swap(text, terms, pat)
            if new == text:
                continue
            if any(B.line_px(x) > widest for x in re.split(r"\\[nlp]", new)):
                stats["too_wide"] += 1
                report.append((f, src.count("\n", 0, m.start()) + 1, "too_wide", new))
                continue
            lits = STR.findall(m.group(1))
            if len(lits) == 1:
                body = f'"{new}"'
            else:
                indent = re.search(r"\n([ \t]*)\"", m.group(0))
                ind = indent.group(1) if indent else "    "
                parts = [p for p in re.split(r"(?<=\\n)", new) if p]
                body = f'"{parts[0]}"' + "".join(f'\n{ind}"{p}"' for p in parts[1:])
            out.append(src[pos:m.start(1)] + body)
            pos = m.end(1)
            stats["ported"] += 1
        out.append(src[pos:])
        new_src = "".join(out)
        if new_src != src and not args.dry_run:
            path.write_text(new_src, encoding="utf-8")
    for key in sorted(set(hand) - used_hand):
        stats["hand row not found"] += 1
        report.append((key[0], "", "hand row not found", key[1]))
    if not args.dry_run:
        with REPORT.open("w", encoding="utf-8", newline="") as fh:
            w = csv.writer(fh, lineterminator="\n")
            w.writerow(["game_file", "game_line", "result", "new_text"])
            w.writerows(report)
    print(", ".join(f"{k}: {v}" for k, v in sorted(stats.items())))
    for x in report[:20]:
        print("  ", *x)
    return 0


if __name__ == "__main__":
    sys.exit(main())
