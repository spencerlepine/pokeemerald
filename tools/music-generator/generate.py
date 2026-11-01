#!/usr/bin/env python3
"""music-generator: song models (song-schemas/*.yaml) -> Emerald songs (MIDI for mid2agb + an m4a preview).

  python3 generate.py render song-schemas/x.yaml [--loops 3]   check, .mid, .s (mid2agb), preview wav, loop check
  python3 generate.py check song-schemas/x.yaml                 limits only (fast)
  python3 generate.py vanilla MUS_ROUTE101 [--loops 2]          the vanilla song through the same preview (A/B)
  python3 generate.py voices [voicegroup]                       voicegroup catalog -> docs/voicegroups.md
  python3 generate.py survey                                    vanilla stats -> reference/vanilla_songs.json
  python3 generate.py install song-schemas/x.yaml [--game DIR]  write it into a game tree (owner-approved songs only)

Everything lands in out/<name>/: <name>.mid, <name>.s, <name>_preview.wav, report.md, report.json.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path

import numpy as np

import checks
import gba
import loopcheck
import midi
import preview
from song import ModelError, Note, Part, Song, load

HERE = gba.HERE
OUT = HERE / "out"
WIKI_MUSIC = HERE.parent.parent / "wiki" / "database" / "music.csv"


# ------------------------------------------------------------------ render

def cfg_line(song: Song) -> str:
    m = song.model
    args = f"-E -R{gba.REVERB} -G_{song.voicegroup.name} -V{int(m.get('master_volume', 80)):03d}"
    if m.get("song_priority") is not None:
        args += f" -P{int(m['song_priority'])}"
    return args


def midi_name_for(song: Song) -> str:
    """File stem in the game: the replaced song's (mus_route101) or a new mus_<name>."""
    rep = song.model.get("replaces")
    if rep:
        return rep.lower()
    const = song.model.get("constant")
    return const.lower() if const else f"mus_{song.name.replace('-', '_')}"


def render(path: Path, loops: int = 3, quiet: bool = False) -> dict:
    song = load(path)
    out = OUT / song.name
    out.mkdir(parents=True, exist_ok=True)
    stem = midi_name_for(song)
    mid = out / f"{stem}.mid"
    midi.write(song, mid)
    asm = None
    try:
        asm = gba.run_mid2agb(mid, out / f"{stem}.s", cfg_line(song))
    except Exception as e:                     # noqa: BLE001 - reported, not fatal for the preview
        song.errors.append(str(e).strip())
    mv = int(song.model.get("master_volume", 80))
    audio, stats = preview.render(song, loops=loops, master_volume=mv)
    preview.write_wav(out / f"{song.name}_preview.wav", audio)
    E, W = checks.check(song, asm, stats)
    lc = None
    looped = song.model.get("loop", True) and song.loop_clocks > 0
    if looped and loops >= 3:
        drums = {p.name for p in song.parts.values() if p.is_drums}
        stem_audio = None
        if drums:
            stem_audio, _ = preview.render(song, loops=loops, master_volume=mv,
                                           only={p for p in song.parts if p not in drums})
            stem_audio = stem_audio.T
        bars = song.loop_clocks // song.clocks_per_bar
        lc = loopcheck.validate(audio.T, preview.OUT_RATE, stats["intro_samples"], stats["samples_per_loop"],
                                max(1, bars), stem_audio, frame_exact=song.loop_clocks * 150 % song.tempo == 0)
    uses = checks.usage(song.voicegroup, checks.song_events(song), song.tempo)
    pk = checks.peaks(uses)
    rep = {
        "name": song.name, "replaces": song.model.get("replaces"), "constant": song.model.get("constant"),
        "midi": mid.name, "midi_cfg": f"{stem}.mid: {cfg_line(song)}", "tempo_bpm": song.tempo,
        "voicegroup": song.voicegroup.name, "intro_s": round(song.seconds(song.intro_clocks), 2),
        "loop_s": round(song.seconds(song.loop_clocks), 2) if looped else 0,
        "length_s": round(song.seconds(song.total_clocks), 2), "loops": bool(looped),
        "tracks": sum(1 for p in song.parts.values() if any(n.part == p.name for n in song.notes)),
        "notes": len(song.notes), "bytes": gba.song_bytes(asm) if asm else None,
        "max_pcm": pk["max_pcm"], "pcm_steals": stats["pcm_steals"], "cgb_clashes": len(pk["cgb_clash"]),
        "parts": {p.name: {"program": p.program, "voice": (song.voicegroup.slot(p.program).describe()
                                                          if song.voicegroup.slot(p.program) else "?"),
                           "notes": sum(1 for n in song.notes if n.part == p.name)} for p in song.parts.values()},
        "errors": E, "warnings": W,
        "loop_check": {"passed": lc["passed"], "checks": lc["checks"]} if lc else None,
    }
    (out / "report.json").write_text(json.dumps(rep, indent=1) + "\n")
    (out / "report.md").write_text(report_md(rep, lc))
    if not quiet:
        print(report_text(rep, lc))
    return rep


def report_text(rep: dict, lc: dict | None) -> str:
    L = [f"{rep['name']}: {rep['tempo_bpm']} bpm, voicegroup {rep['voicegroup']}, {rep['tracks']} tracks, "
         f"{rep['notes']} notes, {rep['bytes']} bytes",
         f"   intro {rep['intro_s']} s, loop {rep['loop_s']} s, max {rep['max_pcm']} Direct Sound notes at once, "
         f"{rep['pcm_steals']} steals, {rep['cgb_clashes']} Game Boy channel clashes",
         f"   midi.cfg  {rep['midi_cfg']}"]
    L += [f"   ERROR {e}" for e in rep["errors"]]
    L += [f"   warn  {w}" for w in rep["warnings"]]
    if lc:
        L += lc["lines"]
    L.append(f"   -> out/{rep['name']}/")
    return "\n".join(L)


def report_md(rep: dict, lc: dict | None) -> str:
    L = [f"# {rep['name']}", "",
         f"- replaces: `{rep['replaces'] or '-'}`, constant: `{rep['constant'] or '-'}`",
         f"- `{rep['midi_cfg']}`",
         f"- {rep['tempo_bpm']} bpm; intro {rep['intro_s']} s; loop {rep['loop_s']} s; total {rep['length_s']} s",
         f"- {rep['tracks']} tracks, {rep['notes']} notes, {rep['bytes']} bytes of track data",
         f"- up to {rep['max_pcm']} Direct Sound notes at once ({rep['pcm_steals']} voice steals), "
         f"{rep['cgb_clashes']} Game Boy channel clashes", "",
         "| part | program | voice | notes |", "| --- | --- | --- | --- |"]
    for k, p in rep["parts"].items():
        L.append(f"| {k} | {p['program']} | {p['voice']} | {p['notes']} |")
    L += ["", "## Errors", ""] + ([f"- {e}" for e in rep["errors"]] or ["none"])
    L += ["", "## Warnings", ""] + ([f"- {w}" for w in rep["warnings"]] or ["none"])
    if lc:
        L += ["", f"## Loop check: {'PASS' if lc['passed'] else 'FAIL'}", "", "| check | result | detail |",
              "| --- | --- | --- |"]
        L += [f"| {c['name']} | {'ok' if c['passed'] else 'FAIL'} | {c['detail']} |" for c in lc["checks"]]
    return "\n".join(L) + "\n"


# ------------------------------------------------------------------ vanilla songs through the same model

def vanilla_song(stem: str) -> tuple[Song, dict]:
    stem = stem.lower()
    cfg = gba.midi_cfg().get(f"{stem}.mid")
    if cfg is None:
        raise ValueError(f"{stem}.mid is not in midi.cfg")
    o = gba.cfg_args(cfg)
    if "voicegroup" not in o:
        raise ValueError("no -G voicegroup in midi.cfg (unused song)")
    vg = gba.voicegroups()[o["voicegroup"]]
    m = midi.read(gba.GAME / "sound" / "songs" / "midi" / f"{stem}.mid")
    bpm = round(60e6 / m["tempo_us"])
    scale = gba.MIDI_TPQN / m["tpqn"]
    song = Song(Path(stem), {"master_volume": o.get("volume", 127)}, stem, bpm, 4, 6, 16, 96, 0, vg)
    for i, trk in enumerate(m["tracks"]):
        if not trk["notes"]:
            continue
        ch = min(trk["channels"])
        name = f"t{i}"
        progs = sorted((t, p) for t, c, p in trk["programs"] if c == ch)
        vols = sorted((t, v) for t, c, n, v in trk["cc"] if c == ch and n == 7)
        pans = sorted((t, v) for t, c, n, v in trk["cc"] if c == ch and n == 10)
        song.parts[name] = Part(name, progs[0][1] if progs else 0, ch, vols[0][1] if vols else 100,
                                (pans[0][1] - 64) if pans else 0)

        def at(lst, t, default):
            v = default
            for tt, x in lst:
                if tt > t:
                    break
                v = x
            return v

        for t, d, c, key, vel in trk["notes"]:
            song.notes.append(Note(int(t * scale), max(1, int(d * scale)), key, vel, name, "", 0,
                                   program=at(progs, t, 0), volume=at(vols, t, 100), pan=at(pans, t, 64) - 64))
    song.notes.sort(key=lambda n: (n.tick, n.part))
    if m["loop"]:
        song.intro_clocks, song.total_clocks = int(m["loop"][0] * scale), int(m["loop"][1] * scale)
    else:
        song.intro_clocks = song.total_clocks = int(m["end"] * scale)
    return song, o


def cmd_vanilla(a) -> None:
    song, o = vanilla_song(a.song)
    audio, st = preview.render(song, loops=a.loops, master_volume=o.get("volume", 127))
    d = OUT / "vanilla"
    d.mkdir(parents=True, exist_ok=True)
    preview.write_wav(d / f"{song.name}.wav", audio)
    print(f"{song.name}: {len(audio) / preview.OUT_RATE:.1f} s, max {st['max_pcm']} PCM, {st['pcm_steals']} steals"
          f" -> out/vanilla/{song.name}.wav")


# ------------------------------------------------------------------ survey and catalog

def wiki_forms() -> dict[str, str]:
    if not WIKI_MUSIC.exists():
        return {}
    out = {}
    for r in csv.DictReader(WIKI_MUSIC.open()):
        f = r.get("asset_file", "")
        if f:
            out[Path(f).stem] = r.get("music_form", "")
    return out


def cmd_survey(_a) -> None:
    forms = wiki_forms()
    songs = {}
    for name, args in sorted(gba.midi_cfg().items()):
        stem = name[:-4]
        if not stem.startswith("mus_") or not name.endswith(".mid"):
            continue
        try:
            song, o = vanilla_song(stem)
        except Exception as e:      # noqa: BLE001
            print("skip", stem, e)
            continue
        pk = checks.peaks(checks.usage(song.voicegroup, checks.song_events(song), song.tempo))
        s_file = gba.GAME / "sound" / "songs" / "midi" / f"{stem}.s"
        asm = s_file.read_text() if s_file.exists() else None
        kinds = {}
        for u in checks.usage(song.voicegroup, checks.song_events(song), song.tempo):
            kinds[u.kind] = kinds.get(u.kind, 0) + 1
        songs[stem] = {"form": forms.get(stem, ""), "voicegroup": o["voicegroup"], "volume": o.get("volume"),
                       "priority": o.get("priority"), "tempo": song.tempo, "tracks": len(song.parts),
                       "loops": song.loop_clocks > 0,
                       "intro_s": round(song.seconds(song.intro_clocks), 2),
                       "loop_s": round(song.seconds(song.loop_clocks), 2),
                       "length_s": round(song.seconds(song.total_clocks), 2),
                       "max_pcm": pk["max_pcm"], "pcm_over": len(pk["pcm_over"]), "cgb_clash": len(pk["cgb_clash"]),
                       "kinds": kinds, "bytes": gba.song_bytes(asm) if asm else None}
    vals = list(songs.values())

    def pct(xs, p):
        return float(np.percentile(xs, p)) if xs else None

    ranges = {"max_pcm_p90": int(pct([v["max_pcm"] for v in vals], 90)),
              "tracks_max": max(v["tracks"] for v in vals),
              "tempo": [min(v["tempo"] for v in vals), max(v["tempo"] for v in vals)],
              "bytes_max": max(v["bytes"] or 0 for v in vals)}
    for form in ("LOOP", "AMBIENT"):
        xs = [v["loop_s"] for v in vals if v["form"] == form and v["loops"]]
        if xs:
            ranges[f"loop_s_{form}"] = [round(pct(xs, 5), 1), round(pct(xs, 95), 1)]
    for form in ("JINGLE", "CUE"):
        xs = [v["length_s"] for v in vals if v["form"] == form]
        if xs:
            ranges[f"length_s_{form}"] = [round(min(xs), 1), round(max(xs), 1)]
    (HERE / "reference").mkdir(exist_ok=True)
    checks.SURVEY.write_text(json.dumps({"ranges": ranges, "songs": songs}, indent=1) + "\n")
    print(json.dumps(ranges, indent=1))
    print(f"{len(songs)} songs -> {checks.SURVEY.relative_to(HERE)}")


def cmd_voices(a) -> None:
    vgs = gba.voicegroups()
    uses: dict[str, list[str]] = {}
    for name, args in gba.midi_cfg().items():
        vg = gba.cfg_args(args).get("voicegroup")
        if name.startswith("mus_") and vg:
            uses.setdefault(vg, []).append(name[:-4])
    if a.voicegroup:
        vg = vgs[a.voicegroup]
        for v in vg.voices:
            if not v.filler:
                print(f"{v.slot:3d}  {v.describe()}")
        return
    L = ["# Emerald voicegroups", "",
         "Generated by `python3 generate.py voices`. A song model's `voicegroup` is one of these; each part's "
         "`program` is a slot number. Empty slots (the square-wave filler) are left out. `pcm` slots are Direct "
         "Sound samples (count toward the 5 voices), the rest are Game Boy channels (one note each).", ""]
    for name in sorted(uses):
        vg = vgs.get(name)
        if not vg:
            continue
        L += [f"## {name}", "", f"Used by: {', '.join(sorted(uses[name]))}", "", "| slot | voice |", "| --- | --- |"]
        L += [f"| {v.slot} | {v.describe()} |" for v in vg.voices if not v.filler]
        L.append("")
    (HERE / "docs").mkdir(exist_ok=True)
    (HERE / "docs" / "voicegroups.md").write_text("\n".join(L))
    print(f"{len(uses)} voicegroups -> docs/voicegroups.md")


# ------------------------------------------------------------------ install

def install(path: Path, game: Path) -> list[str]:
    """Put a rendered song into a game tree. Hot-swap (`replaces: MUS_X`): overwrite mus_x.mid and its midi.cfg
    line, keeping the song id, player and every caller. Net-new (`constant: MUS_NEW`): new .mid + midi.cfg line,
    a free song id in songs.h / song_table.inc and the object in ld_script.ld. Returns what it changed."""
    song = load(path)
    rep = json.loads((OUT / song.name / "report.json").read_text()) if (OUT / song.name / "report.json").exists() \
        else render(path, quiet=True)
    if rep["errors"]:
        raise SystemExit(f"{song.name}: fix the errors first: {rep['errors']}")
    stem = midi_name_for(song)
    mid_dir = game / "sound" / "songs" / "midi"
    changed = []
    midi.write(song, mid_dir / f"{stem}.mid")
    changed.append(f"sound/songs/midi/{stem}.mid")
    stale = mid_dir / f"{stem}.s"
    if stale.exists():
        stale.unlink()
    cfg = mid_dir / "midi.cfg"
    lines = cfg.read_text().splitlines()
    line = f"{stem}.mid:" + " " * max(1, 31 - len(stem) - 5) + cfg_line(song)
    for i, l in enumerate(lines):
        if l.startswith(f"{stem}.mid:"):
            lines[i] = line
            break
    else:
        lines.append(line)
    cfg.write_text("\n".join(lines) + "\n")
    changed.append("sound/songs/midi/midi.cfg")
    if not song.model.get("replaces"):
        const = song.model["constant"]
        h_path = game / "include" / "constants" / "songs.h"
        h = h_path.read_text()
        if not re.search(rf"#define {const}\s", h):
            # new song ids go after the last one (PH_NURSE_SOLO, 609): the phoneme range is FIRST/LAST-bounded
            ids = [int(x) for x in re.findall(r"^#define \w+\s+(\d+)\b", h, re.M)]
            sid = max(i for i in ids if i < 0x7FFF) + 1
            st = game / "sound" / "song_table.inc"
            tl = st.read_text().splitlines()
            last = max(i for i, l in enumerate(tl) if l.strip().startswith("song "))
            assert last - tl.index("gSongTable::") == sid, "song_table.inc and songs.h disagree on the song count"
            tl.insert(last + 1, f"\tsong {stem}, MUSIC_PLAYER_BGM, 0")
            st.write_text("\n".join(tl) + "\n")
            tag = "// Star Wars music (music-generator)"
            hl = h.split("\n")
            k = max(i for i, l in enumerate(hl) if re.match(r"#define \w+\s+\d+\b", l) and int(l.split()[2]) == sid - 1)
            ins = ([""] + [tag] if tag not in h else []) + [f"#define {const:<27} {sid}"]
            hl[k + 1:k + 1] = ins
            h_path.write_text("\n".join(hl))
            changed += ["include/constants/songs.h", "sound/song_table.inc"]
        ld = game / "ld_script.ld"
        lt = ld.read_text().split("\n")
        obj = f"sound/songs/midi/{stem}.o(.rodata);"
        if not any(l.strip() == obj for l in lt):
            k = max(i for i, l in enumerate(lt) if re.match(r"\s*sound/songs/midi/mus_\w+\.o\(\.rodata\);", l))
            indent = lt[k][:len(lt[k]) - len(lt[k].lstrip())]
            lt.insert(k + 1, indent + obj)
            ld.write_text("\n".join(lt))
            changed.append("ld_script.ld")
    return changed


def cmd_install(a) -> None:
    for p in a.songs:
        print(p, "->", ", ".join(install(Path(p), Path(a.game))))


def main(argv=None) -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("render")
    r.add_argument("songs", nargs="+")
    r.add_argument("--loops", type=int, default=3)
    c = sub.add_parser("check")
    c.add_argument("songs", nargs="+")
    v = sub.add_parser("vanilla")
    v.add_argument("song")
    v.add_argument("--loops", type=int, default=2)
    vo = sub.add_parser("voices")
    vo.add_argument("voicegroup", nargs="?")
    sub.add_parser("survey")
    i = sub.add_parser("install")
    i.add_argument("songs", nargs="+")
    i.add_argument("--game", default=str(gba.GAME))
    a = ap.parse_args(argv)
    if a.cmd == "render":
        bad = 0
        for p in a.songs:
            try:
                bad += bool(render(Path(p), a.loops)["errors"])
            except ModelError as e:
                print(f"{p}: {e}")
                bad += 1
        sys.exit(1 if bad else 0)
    if a.cmd == "check":
        bad = 0
        for p in a.songs:
            try:
                song = load(Path(p))
            except ModelError as e:
                print(f"{p}: {e}")
                bad += 1
                continue
            E, W = checks.check(song)
            print(f"{song.name}: {len(E)} errors, {len(W)} warnings")
            for e in E:
                print("   ERROR", e)
            for w in W:
                print("   warn ", w)
            bad += bool(E)
        sys.exit(1 if bad else 0)
    {"vanilla": cmd_vanilla, "voices": cmd_voices, "survey": cmd_survey, "install": cmd_install}[a.cmd](a)


if __name__ == "__main__":
    main()
