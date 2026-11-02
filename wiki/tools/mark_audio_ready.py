#!/usr/bin/env python3
"""List generated sounds in mapping/audio_ready.csv and apply it to database/ without a full rebuild.

A sound is AUDIO_READY when a tool (cry-generator, sfx-generator) generated it, every hard gate passed, and
`tools/ship_audio.py` stored the game-format file in the wiki at `audio_file` (audio/<game path>), with a
44.1 kHz listening copy at `preview_file`. It is not in ../game yet: `game_status` stays NOT_STARTED until it
is installed with the tool's `install` command (then it moves to mapping/audio_done.csv and DONE).

This script
  1. rebuilds mapping/audio_ready.csv from every spec in tools/cry-generator/specs and
     tools/sfx-generator/specs whose wiki file exists (rows already in audio_done.csv are skipped), then
  2. sets audio_status AUDIO_READY and made_by in database/pending_audio.csv for each row.
build.py applies the same file, so a full rebuild gives the same result. Needs pyyaml for step 1.
"""
import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REPO = ROOT.parent
DB = ROOT / "database"
COLS = ["asset_id", "made_by", "audio_file", "preview_file", "spec", "notes"]


def read(path):
    with path.open(encoding="utf-8", newline="") as f:
        r = csv.DictReader(f)
        return r.fieldnames, list(r)


def write(path, cols, rows):
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


def collect(audio):
    import yaml
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from ship_audio import wiki_paths
    by_const = {a["sw_constant"]: a for a in audio if a["category"] == "sfx"}
    by_song = {a["sw_constant"]: a for a in audio if a["category"] == "music"}
    by_song.update({a["emerald_constant"]: a for a in audio if a["category"] == "music" and a["emerald_constant"]})
    _, done = read(ROOT / "mapping" / "audio_done.csv")
    done_ids = {d["asset_id"] for d in done}
    rows, bad = [], 0
    for kind, tool in (("cry", "cry-generator"), ("sfx", "sfx-generator"), ("music", "music-generator")):
        for p in sorted((REPO / "tools" / tool / ("song-schemas" if kind == "music" else "specs")).glob("*.yaml")):
            spec = yaml.safe_load(p.read_text())
            af, pf = wiki_paths(kind, spec)
            if not (ROOT / af).exists():
                continue
            if kind == "music":
                a = by_song.get(spec.get("replaces") or spec.get("constant", ""))
                if not a:
                    print(f"error: {p.name}: {spec.get('replaces') or spec.get('constant')} matches no music row"); bad += 1; continue
                aid = a["asset_id"]
            elif kind == "cry":
                aid = f"cry:{spec['slot']}"
            elif spec.get("replaces"):
                aid = f"audio:{spec['replaces']}"
            else:
                a = by_const.get(spec.get("constant", ""))
                if not a:
                    print(f"error: {p.name}: constant {spec.get('constant')} matches no sfx row"); bad += 1; continue
                aid = a["asset_id"]
            if aid in done_ids:
                continue
            title = spec.get("brief", "").split(":")[0].strip() or spec.get("title", "") or spec["name"]
            rows.append({"asset_id": aid, "made_by": tool, "audio_file": af, "preview_file": pf,
                         "spec": f"tools/{tool}/{'song-schemas' if kind == 'music' else 'specs'}/{p.name}",
                         "notes": f"{title}; generated, gates passed; install with the spec"})
    seen = {}
    for r in rows:
        if r["asset_id"] in seen:
            print(f"error: {r['asset_id']} shipped twice ({seen[r['asset_id']]} and {r['spec']})"); bad += 1
        seen[r["asset_id"]] = r["spec"]
    rows.sort(key=lambda r: r["asset_id"])
    write(ROOT / "mapping" / "audio_ready.csv", COLS, rows)
    return bad


def main():
    cols, audio = read(DB / "pending_audio.csv")
    bad = 0
    if "--no-collect" not in sys.argv:
        bad += collect(audio)
    _, ready = read(ROOT / "mapping" / "audio_ready.csv")
    by_id = {a["asset_id"]: a for a in audio}
    n = 0
    for d in ready:
        a = by_id.get(d["asset_id"])
        if not a:
            print(f"error: {d['asset_id']} is not in pending_audio.csv"); bad += 1; continue
        if not (ROOT / d["audio_file"]).exists():
            print(f"error: {d['audio_file']} missing"); bad += 1; continue
        if a["audio_status"] == "DONE":
            continue
        old = [x for x in a["notes"].split("; ") if x and not x.startswith("generated: ")]
        a.update(audio_status="AUDIO_READY", made_by=d.get("made_by", ""),
                 notes="; ".join([f"generated: wiki/{d['audio_file']} ({d['spec']})"] + old))
        n += 1
    if bad:
        sys.exit(1)
    write(DB / "pending_audio.csv", cols, audio)
    print(f"AUDIO_READY  {n} rows")
    # database/music.csv mirrors pending_audio's audio_status; a generated song is rewrite_status GENERATED
    # (composed and rendered, not installed in ../game yet). build_music.py does the same on a full rebuild.
    mcols, music = read(DB / "music.csv")
    by_id = {a["asset_id"]: a for a in audio}
    g = 0
    for m in music:
        a = by_id.get(m["asset_id"])
        if a and a["audio_status"] == "AUDIO_READY" and m["rewrite_status"] in ("TODO", "GENERATED"):
            m.update(audio_status="AUDIO_READY", rewrite_status="GENERATED")
            g += 1
    write(DB / "music.csv", mcols, music)
    print(f"music.csv  {g} songs GENERATED")


if __name__ == "__main__":
    main()
