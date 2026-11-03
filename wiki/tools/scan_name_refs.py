"""Find every place ../game names the player, the rival, the professor (and Pyramid ace Dexter) -> mapping/name_refs.csv.

    python3 tools/scan_name_refs.py            # write the table, print a summary
    python3 tools/scan_name_refs.py --check    # same, exit 1 if any Emerald name is still shown to the player

One row per text line the player can see that holds one of these names, old (Emerald) or new (Star Wars),
plus one row per source file whose code identifiers still carry the Emerald name (flags, map folders,
labels, sprite tables), with the count and a few examples.

  kind    text        a string the player sees (.string "..." in data/, _("...") in src/)
          code        identifiers in one file (`count` uses, `text` = examples); the player never sees them
  status  SWAPPED     text that shows the Star Wars name
          OLD         text that still shows the Emerald name: fix it in ../game, then re-run
          KEEP        code, left as is on purpose (renaming identifiers changes nothing on screen)

The characters and their names are in CHARACTERS below, matching mapping/characters.csv (`text_terms`).
Generated, never edit by hand. Deterministic: same game source gives a byte-identical file.
"""
from __future__ import annotations

import csv
import os
import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GAME = Path(os.environ.get("GAME_DIR", ROOT.parent / "game"))
OUT = ROOT / "mapping" / "name_refs.csv"
MAX_EXAMPLES = 4
COLS = ["character", "sw_name", "kind", "status", "old_term", "new_term", "source_file", "source_line",
        "label", "count", "text"]

# The 40 names Emerald picked from when the player left their name blank. Replaced by KAEL / MIRA.
OLD_PRESETS = ("STU MILTON TOM KENNY REID JUDE JAXSON EASTON WALKER TERU JOHNNY BRETT SETH TERRY CASEY "
               "DARREN LANDON COLLIN STANLEY QUINCY KIMMY TIARA BELLA JAYLA ALLIE LIANNA SARA MONICA "
               "CAMILA AUBREE RUTHIE HAZEL NADINE TANJA YASMIN NICOLA LILLIE TERRA LUCY HALIE").split()

# character id (mapping/characters.csv), shown name, (old -> new) text terms, regex for code identifiers.
CHARACTERS = [
    ("character:player", "KAEL / MIRA", [("BRENDAN", "KAEL"), ("MAY", "MIRA")], None),
    ("character:rival", "MIRA / KAEL", [("BRENDAN", "KAEL"), ("MAY", "MIRA")],
     r"\w*(?:Brendan|BRENDAN|Mays?(?=[A-Z_])|(?<=_)MAY(?=_|\b))\w*"),
    ("character:prof-birch", "PROF. KORR", [("BIRCH", "KORR")], r"\w*(?:Birch|BIRCH)\w*"),
    ("character:brandon", "DEXTER", [("BRANDON", "DEXTER")], r"\w*(?:Brandon|BRANDON)\w*"),
]
# Brendan and May are both the player's look and the rival's: the boy/girl the player did not pick is the
# rival. Dialogue names them only as the rival (the player is always {PLAYER}), so text rows go to the rival;
# the player gets the default-name rows below.
PLAYER_DEFAULTS = {"KAEL": "gText_DefaultNameKael", "MIRA": "gText_DefaultNameMira"}

STRING = re.compile(r'"(?:[^"\\]|\\.)*"')
LABEL = re.compile(r"^([A-Za-z_]\w*)::?")
CONST = re.compile(r"\b(g\w+|s\w+)\s*\[\]\s*=")
COMMENT = re.compile(r"//.*$|/\*.*?\*/|@.*$")


def game_files() -> list[str]:
    out = subprocess.run(["git", "ls-files", "data", "src", "include"], cwd=GAME, capture_output=True,
                         text=True, check=True).stdout.split()
    return sorted(f for f in out if f.endswith((".c", ".h", ".inc", ".s")))


def is_text_line(line: str) -> bool:
    return '.string "' in line or '_("' in line


def main() -> int:
    rows: list[dict] = []
    code: dict[tuple[str, str], list] = {}  # (character, file) -> [first line, count, identifiers]
    for f in game_files():
        try:
            lines = (GAME / f).read_text(encoding="utf-8").split("\n")
        except UnicodeDecodeError:
            continue
        label = ""
        for n, line in enumerate(lines, 1):
            m = LABEL.match(line) or CONST.search(line)
            if m:
                label = m.group(1)
            if is_text_line(line):
                text = " ".join(s[1:-1] for s in STRING.findall(line))
                if f == "src/strings.c" and label.startswith("gText_DefaultName"):
                    for old in OLD_PRESETS:
                        if re.search(rf"(?:(?<=\\[nlp])|\b){old}\b", text):
                            rows.append(row("character:player", "KAEL / MIRA", "text", "OLD", old, "KAEL / MIRA",
                                            f, n, label, 1, text))
                    for new, lab in PLAYER_DEFAULTS.items():
                        if label == lab and re.search(rf"(?:(?<=\\[nlp])|\b){new}\b", text):
                            rows.append(row("character:player", "KAEL / MIRA", "text", "SWAPPED", "", new,
                                            f, n, label, 1, text))
                    continue
                for cid, sw, terms, _ in CHARACTERS[1:]:
                    for old, new in terms:
                        if re.search(rf"(?:(?<=\\[nlp])|\b){old}\b", text):
                            rows.append(row(cid, sw, "text", "OLD", old, new, f, n, label, 1, text))
                        elif re.search(rf"(?:(?<=\\[nlp])|\b){new}\b", text):
                            rows.append(row(cid, sw, "text", "SWAPPED", old, new, f, n, label, 1, text))
                continue
            bare = COMMENT.sub("", line)
            for cid, sw, _, pat in CHARACTERS:
                if not pat:
                    continue
                for ident in re.findall(pat, bare):
                    entry = code.setdefault((cid, f), [n, 0, []])
                    entry[1] += 1
                    if ident not in entry[2]:
                        entry[2].append(ident)
    names = {c[0]: c[1] for c in CHARACTERS}
    for (cid, f), (n, cnt, idents) in sorted(code.items()):
        examples = " | ".join(idents[:MAX_EXAMPLES]) + (f" | +{len(idents) - MAX_EXAMPLES} more"
                                                        if len(idents) > MAX_EXAMPLES else "")
        rows.append(row(cid, names[cid], "code", "KEEP", "", "", f, n, "", cnt, examples))
    order = {c[0]: i for i, c in enumerate(CHARACTERS)}
    rows.sort(key=lambda r: (order[r["character"]], r["kind"] != "text", r["source_file"], int(r["source_line"])))
    with OUT.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, COLS, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)

    summary = defaultdict(lambda: defaultdict(int))
    for r in rows:
        summary[r["character"]][f'{r["kind"]} {r["status"]}'] += 1
    old = 0
    for cid, _, _, _ in CHARACTERS:
        s = summary[cid]
        old += s.get("text OLD", 0)
        print(f"{cid:22} " + ", ".join(f"{k}: {v}" for k, v in sorted(s.items())))
    print(f"wrote {OUT.relative_to(ROOT)} ({len(rows)} rows)")
    if "--check" in sys.argv and old:
        print(f"{old} text lines still show an Emerald name")
        return 1
    return 0


def row(cid, sw, kind, status, old, new, f, n, label, count, text) -> dict:
    return {"character": cid, "sw_name": sw, "kind": kind, "status": status, "old_term": old, "new_term": new,
            "source_file": f, "source_line": n, "label": label, "count": count, "text": text}


if __name__ == "__main__":
    sys.exit(main())
