#!/usr/bin/env python3
"""Render sounds with cry-generator / sfx-generator and store them in the wiki as AUDIO_READY.

    python3 wiki/tools/ship_audio.py tools/cry-generator/specs/mistkin.yaml [more specs...]
    python3 wiki/tools/ship_audio.py --all          # every spec in both tools not shipped or installed yet

For each spec: runs the tool's `make` (which fails unless every hard gate passes), then copies
  out/<name>.wav          -> wiki/audio/<game path>   (the exact file `install` would put in ../game)
  out/<name>_preview.wav  -> wiki/audio/previews/{cries,sfx}/<name>.wav   (44.1 kHz, as heard, for listening)
Cries land at sound/direct_sound_samples/cries/<slot>.wav (same slot and file name as the vanilla cry);
SEs at sound/direct_sound_samples/sw_sfx/<name>.wav (where `sfx.py install` puts them).

Nothing in ../game is touched. Run `python3 wiki/tools/mark_audio_ready.py` afterwards to list the shipped
files in mapping/audio_ready.csv and set audio_status AUDIO_READY in database/pending_audio.csv.
"""
import argparse
import shutil
import subprocess
import sys
from pathlib import Path

import yaml

WIKI = Path(__file__).resolve().parent.parent
REPO = WIKI.parent
TOOLS = {"cry": REPO / "tools" / "cry-generator", "sfx": REPO / "tools" / "sfx-generator"}


def kind_of(spec_path):
    p = Path(spec_path).resolve()
    for k, d in TOOLS.items():
        if d in p.parents:
            return k
    sys.exit(f"{spec_path}: not a spec under tools/cry-generator or tools/sfx-generator")


def wiki_paths(kind, spec):
    name = spec["name"]
    if kind == "cry":
        game = f"sound/direct_sound_samples/cries/{spec['slot']}.wav"
        prev = f"audio/previews/cries/{name}.wav"
    else:
        game = f"sound/direct_sound_samples/sw_sfx/{name}.wav"
        prev = f"audio/previews/sfx/{name}.wav"
    return f"audio/{game}", prev


def ship(spec_path, quiet=False):
    kind = kind_of(spec_path)
    spec = yaml.safe_load(Path(spec_path).read_text())
    tool = TOOLS[kind]
    cli = "cry.py" if kind == "cry" else "sfx.py"
    r = subprocess.run([sys.executable, cli, "make", str(Path(spec_path).resolve())], cwd=tool,
                       capture_output=True, text=True)
    if r.returncode != 0:
        print(f"FAIL  {spec_path}\n{r.stdout[-2500:]}{r.stderr[-1500:]}")
        return False
    name = spec["name"]
    audio, prev = wiki_paths(kind, spec)
    for src, dst in ((tool / "out" / f"{name}.wav", WIKI / audio), (tool / "out" / f"{name}_preview.wav", WIKI / prev)):
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dst)
    print(f"SHIPPED  {spec_path}  ->  wiki/{audio}")
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("specs", nargs="*")
    ap.add_argument("--all", action="store_true", help="every spec whose wiki file is missing")
    a = ap.parse_args()
    specs = list(a.specs)
    if a.all:
        import csv
        with (WIKI / "mapping" / "audio_done.csv").open(encoding="utf-8") as f:
            installed = {Path(r["game_file"]).name for r in csv.DictReader(f)}
        for k, d in TOOLS.items():
            for p in sorted((d / "specs").glob("*.yaml")):
                spec = yaml.safe_load(p.read_text())
                af = wiki_paths(k, spec)[0]
                if Path(af).name not in installed and not (WIKI / af).exists():
                    specs.append(str(p))
    bad = [s for s in specs if not ship(s)]
    if bad:
        print(f"{len(bad)} failed: " + " ".join(bad))
        sys.exit(1)


if __name__ == "__main__":
    main()
