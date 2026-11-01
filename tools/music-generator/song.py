"""Song model (song-schemas/*.yaml) -> note events in m4a clocks (24 per quarter note).

The notation is the z-day ai-music one (bars split by `|`, `A4:4` notes, `r` rests, `~` ties, `^1` chord tones,
`ch` whole chords, `>` accent, `_` soft, `'` staccato, drum grooves as `x.o.X...` lines), so models and habits
carry over. What changes is the target: instead of synthesizing audio, every part is one m4a track that plays
a program of an Emerald voicegroup, and every time is an integer number of mid2agb clocks.
See README.md ("Song model") for every field.
"""
from __future__ import annotations

import re
import zlib
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import yaml

import gba

NOTE_PC = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
PC_NAME = ["C", "C#", "D", "Eb", "E", "F", "F#", "G", "Ab", "A", "Bb", "B"]
CHORD_QUALITIES = {
    "": [0, 4, 7], "maj": [0, 4, 7], "m": [0, 3, 7], "min": [0, 3, 7],
    "dim": [0, 3, 6], "aug": [0, 4, 8], "sus2": [0, 2, 7], "sus4": [0, 5, 7], "sus": [0, 5, 7],
    "5": [0, 7], "6": [0, 4, 7, 9], "m6": [0, 3, 7, 9], "7": [0, 4, 7, 10],
    "m7": [0, 3, 7, 10], "maj7": [0, 4, 7, 11], "m7b5": [0, 3, 6, 10], "dim7": [0, 3, 6, 9],
    "mmaj7": [0, 3, 7, 11], "7sus4": [0, 5, 7, 10], "add9": [0, 4, 7, 14], "madd9": [0, 3, 7, 14],
    "9": [0, 4, 7, 10, 14], "m9": [0, 3, 7, 10, 14], "7b9": [0, 4, 7, 10, 13],
}
SCALES = {
    "major": [0, 2, 4, 5, 7, 9, 11], "ionian": [0, 2, 4, 5, 7, 9, 11], "dorian": [0, 2, 3, 5, 7, 9, 10],
    "phrygian": [0, 1, 3, 5, 7, 8, 10], "lydian": [0, 2, 4, 6, 7, 9, 11], "mixolydian": [0, 2, 4, 5, 7, 9, 10],
    "aeolian": [0, 2, 3, 5, 7, 8, 10], "minor": [0, 2, 3, 5, 7, 8, 10], "locrian": [0, 1, 3, 5, 6, 8, 10],
    "harmonic_minor": [0, 2, 3, 5, 7, 8, 11], "melodic_minor": [0, 2, 3, 5, 7, 9, 11],
    "hungarian_minor": [0, 2, 3, 6, 7, 8, 11], "chromatic": list(range(12)),
}
TOKEN = re.compile(r"^(?P<acc>[>_]?)(?P<p>r|~|ch|\^\d+[+-]*|[A-G][#b]*-?\d)(?P<stac>')?(?::(?P<d>\d+))?$")
DRUM_VEL = {"x": 96, "X": 127, "o": 52, "r": 80, "R": 120, "f": 100}
VEL = {"": 100, ">": 127, "_": 64}


class ModelError(ValueError):
    pass


def parse_pc(s: str) -> int:
    m = re.fullmatch(r"([A-G])([#b]*)", s)
    if not m:
        raise ModelError(f"bad pitch class {s!r}")
    return (NOTE_PC[m[1]] + m[2].count("#") - m[2].count("b")) % 12


def note_to_midi(s) -> int:
    if isinstance(s, int):
        return s
    m = re.fullmatch(r"([A-G])([#b]*)(-?\d)", str(s))
    if not m:
        raise ModelError(f"bad note {s!r} (expected e.g. A4, Bb3, C#5)")
    return NOTE_PC[m[1]] + m[2].count("#") - m[2].count("b") + 12 * (int(m[3]) + 1)


def midi_name(m: int) -> str:
    return f"{PC_NAME[m % 12]}{m // 12 - 1}"


@dataclass
class Chord:
    symbol: str
    root: int
    intervals: list[int]
    bass: int


def parse_chord(sym: str, transpose: int) -> Chord | None:
    if sym in ("N", "NC", "-"):
        return None
    m = re.fullmatch(r"([A-G][#b]?)([^/]*)(?:/([A-G][#b]?))?", sym)
    if not m or m[2] not in CHORD_QUALITIES:
        raise ModelError(f"unknown chord {sym!r}; qualities: {sorted(CHORD_QUALITIES)}")
    root = (parse_pc(m[1]) + transpose) % 12
    bass = (parse_pc(m[3]) + transpose) % 12 if m[3] else root
    return Chord(sym, root, CHORD_QUALITIES[m[2]], bass)


@dataclass
class Note:
    tick: int          # absolute clock from the song start
    dur: int           # gate length in clocks
    key: int
    vel: int
    part: str
    section: str
    bar: int           # 1-based bar inside its section
    program: int | None = None   # per-note overrides (vanilla songs change program / volume / pan mid-track)
    volume: int | None = None
    pan: int | None = None


@dataclass
class Part:
    name: str
    program: int
    channel: int
    volume: int = 100
    pan: int = 0
    octave: int = 4
    range: tuple[int, int] = (48, 72)
    role: str = "lead"
    gate: float = 0.95
    mono: bool = False
    transpose: int = 0
    mod: int = 0
    lfo_speed: int = 0
    mod_type: int = 0
    lfo_delay: int = 0
    bend_range: int = 2
    priority: int | None = None
    kit: dict[str, int] = field(default_factory=dict)
    is_drums: bool = False


@dataclass
class Song:
    path: Path
    model: dict
    name: str
    tempo: int
    spb: int                 # steps per quarter note (must divide 24)
    clocks_per_step: int
    steps_per_bar: int
    clocks_per_bar: int
    transpose: int
    voicegroup: gba.VoiceGroup
    parts: dict[str, Part] = field(default_factory=dict)
    sections: list[dict] = field(default_factory=list)
    intro_clocks: int = 0
    total_clocks: int = 0
    notes: list[Note] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def loop_clocks(self) -> int:
        return self.total_clocks - self.intro_clocks

    def seconds(self, clocks: int) -> float:
        return clocks / gba.CLOCKS_PER_BEAT * 60 / self.tempo


def expand(model: dict, name_or_text, table: str = "phrases") -> list[str]:
    src = model.get(table, {}) or {}
    if isinstance(name_or_text, str) and name_or_text in src:
        return expand(model, src[name_or_text], table)
    if isinstance(name_or_text, list):
        out = []
        for item in name_or_text:
            out += expand(model, item, table)
        return out
    if isinstance(name_or_text, str):
        return [b.strip() for b in name_or_text.split("|") if b.strip()]
    raise ModelError(f"cannot expand {table[:-1]} {name_or_text!r}")


def close_voicing(chord: Chord, lo: int, hi: int, prev: list[int] | None) -> list[int]:
    ivs = sorted(set(i % 12 for i in chord.intervals))[:4]
    cands = []
    for inv in range(len(ivs)):
        pcs = ivs[inv:] + [i + 12 for i in ivs[:inv]]
        for base in range(lo - 12, hi + 1):
            if (base - chord.root - pcs[0]) % 12:
                continue
            v = [base + p - pcs[0] for p in pcs]
            if v[0] >= lo and v[-1] <= hi:
                cands.append(v)
    if not cands:
        return [lo + (chord.root - lo) % 12 + i for i in ivs]
    centre = prev if prev else [(lo + hi) / 2] * 3
    return min(cands, key=lambda v: abs(np.mean(v) - np.mean(centre)) * 2
               + sum(min(abs(n - p) for p in centre) for n in v))


def load(path: Path) -> Song:
    model = yaml.safe_load(Path(path).read_text())
    vg_name = model.get("voicegroup")
    vgs = gba.voicegroups()
    if vg_name not in vgs:
        raise ModelError(f"voicegroup {vg_name!r} is not in game/sound/voicegroups (see docs/voicegroups.md)")
    num, den = model.get("time_signature", [4, 4])
    spb = int(model.get("steps_per_beat", 4))
    if gba.CLOCKS_PER_BEAT % spb:
        raise ModelError(f"steps_per_beat {spb} must divide {gba.CLOCKS_PER_BEAT} (1, 2, 3, 4, 6, 8, 12, 24)")
    steps_per_bar = num * spb * 4 // den
    tempo = int(model["tempo"])
    song = Song(Path(path), model, Path(path).stem, tempo, spb, gba.CLOCKS_PER_BEAT // spb, steps_per_bar,
                steps_per_bar * gba.CLOCKS_PER_BEAT // spb, int(model.get("transpose", 0)), vgs[vg_name])
    used_ch = set()
    for i, (pname, p) in enumerate((model.get("parts") or {}).items()):
        ch = int(p.get("channel", i))
        if ch in used_ch:
            raise ModelError(f"part {pname}: channel {ch} is used twice (one part = one MIDI channel = one m4a track)")
        used_ch.add(ch)
        lo, hi = (note_to_midi(x) for x in p.get("range", ["C3", "C5"]))
        part = Part(pname, int(p["program"]), ch, int(p.get("volume", 100)), int(p.get("pan", 0)),
                    int(p.get("octave", 4)), (lo, hi), p.get("role", "lead"), float(p.get("gate", 0.95)),
                    bool(p.get("mono", False)), int(p.get("transpose", 0)), int(p.get("mod", 0)),
                    int(p.get("lfo_speed", 0)), int(p.get("mod_type", 0)), int(p.get("lfo_delay", 0)),
                    int(p.get("bend_range", 2)), p.get("priority"),
                    {k: note_to_midi(v) for k, v in (p.get("kit") or {}).items()}, p.get("role") == "drums")
        song.parts[pname] = part

    arr = model["arrangement"]
    loop_start = model.get("loop_start", arr[0])
    if loop_start not in arr:
        raise ModelError(f"loop_start {loop_start!r} is not in arrangement")
    li = arr.index(loop_start)
    tick = 0
    for i, name in enumerate(arr):
        sec = (model.get("sections") or {}).get(name)
        if sec is None:
            raise ModelError(f"arrangement references unknown section {name!r}")
        song.sections.append({"name": name, "start": tick, "bars": int(sec["bars"]),
                              "region": "intro" if i < li else "loop", **sec})
        if i == li:
            song.intro_clocks = tick
        tick += int(sec["bars"]) * song.clocks_per_bar
    song.total_clocks = tick
    if model.get("loop", True) is False:
        song.intro_clocks = song.total_clocks   # a one-shot (fanfare, cue): no loop markers
    build_notes(song)
    return song


def section_chords(song: Song, sec: dict):
    spec = sec.get("chords")
    if spec is None:
        return []
    bars = expand(song.model, spec, "progressions")
    bars = (bars * -(-sec["bars"] // len(bars)))[: sec["bars"]]
    out, t = [], sec["start"]
    for b in bars:
        toks = b.split()
        fixed = sum(int(x.split(":")[1]) for x in toks if ":" in x)
        free = [x for x in toks if ":" not in x]
        each = (song.steps_per_bar - fixed) // max(1, len(free))
        for x in toks:
            sym, n = (x.split(":")[0], int(x.split(":")[1])) if ":" in x else (x, each)
            out.append((t, t + n * song.clocks_per_step, parse_chord(sym, song.transpose)))
            t += n * song.clocks_per_step
    return out


def chord_at(chords, tick):
    for a, b, c in chords:
        if a <= tick < b:
            return c
    return chords[-1][2] if chords else None


def build_notes(song: Song) -> None:
    m = song.model
    seed = int(m.get("seed", 0))
    swing = float(m.get("swing", 0.0))
    swing_unit = int(m.get("swing_unit", 2))
    voicing: dict[str, list[int]] = {}
    for sec in song.sections:
        chords = section_chords(song, sec)
        for pname, phrase in (sec.get("parts") or {}).items():
            if phrase is None:
                continue
            part = song.parts.get(pname)
            if part is None:
                raise ModelError(f"section {sec['name']}: unknown part {pname!r}")
            rng = np.random.default_rng([seed, zlib.crc32(pname.encode()), sec["start"]])
            hum_v = int((m["parts"][pname].get("humanize") or {}).get("vel", 0))
            gain = (sec.get("gain") or {}).get(pname, 0)          # velocity offset for the section
            ramp = (sec.get("ramp") or {}).get(pname)              # [from, to] velocity offsets

            def vel_at(v, tick, s0=sec["start"], n=sec["bars"] * song.clocks_per_bar):
                off = gain + (ramp[0] + (ramp[1] - ramp[0]) * (tick - s0) / n if ramp else 0)
                return int(max(1, min(127, round(v + off + (rng.integers(-hum_v, hum_v + 1) if hum_v else 0)))))

            def swung(step_tick):
                rel = (step_tick - sec["start"]) // song.clocks_per_step
                if swing and rel % (2 * swing_unit) == swing_unit:
                    return step_tick + int(round(swing * swing_unit * song.clocks_per_step))
                return step_tick

            if part.is_drums:
                _drums(song, sec, part, phrase, vel_at, swung)
                continue
            bars = expand(m, phrase)
            if sec["bars"] % len(bars):
                raise ModelError(f"section {sec['name']} part {pname}: phrase has {len(bars)} bars, "
                                 f"section has {sec['bars']} (must divide evenly)")
            bars = bars * (sec["bars"] // len(bars))
            tick = sec["start"]
            last_d = song.spb
            last: list[Note] = []
            for bi, bar in enumerate(bars):
                used = 0
                for tok in bar.split():
                    mt = TOKEN.match(tok)
                    if not mt:
                        raise ModelError(f"section {sec['name']} part {pname} bar {bi + 1}: bad token {tok!r}")
                    d = int(mt["d"]) if mt["d"] else last_d
                    last_d = d
                    p = mt["p"]
                    ch = chord_at(chords, tick)
                    keys: list[int] = []
                    if p == "~":
                        for n in last:
                            n.dur += d * song.clocks_per_step
                    elif p == "ch":
                        if ch is None:
                            raise ModelError(f"section {sec['name']} part {pname}: 'ch' with no chord")
                        keys = close_voicing(ch, *part.range, voicing.get(pname))
                        voicing[pname] = keys
                    elif p.startswith("^"):
                        if ch is None:
                            raise ModelError(f"section {sec['name']} part {pname}: '{p}' with no chord")
                        k = int(re.match(r"\^(\d+)", p)[1]) - 1
                        bass = part.role == "bass" and k == 0
                        root = 12 * (part.octave + 1) + (ch.bass if bass else ch.root)
                        key = root if bass else root + ch.intervals[k % len(ch.intervals)] + 12 * (k // len(ch.intervals))
                        keys = [key + 12 * (p.count("+") - p.count("-")) + part.transpose]
                    elif p != "r":
                        keys = [note_to_midi(p) + song.transpose + part.transpose]
                    if keys:
                        t0 = swung(tick)
                        g = 0.5 if mt["stac"] else part.gate
                        dur = max(1, int(round(d * song.clocks_per_step * g)))
                        v = VEL[mt["acc"]]
                        last = [Note(t0, dur, k, vel_at(v, tick), pname, sec["name"], bi + 1) for k in keys]
                        song.notes.extend(last)
                    tick += d * song.clocks_per_step
                    used += d
                if used != song.steps_per_bar:
                    raise ModelError(f"section {sec['name']} part {pname} bar {bi + 1}: durations sum to {used}, "
                                     f"expected {song.steps_per_bar}: '{bar}'")
    song.notes.sort(key=lambda n: (n.tick, n.part, n.key))


def _drums(song: Song, sec, part: Part, phrase, vel_at, swung) -> None:
    grooves = song.model.get("grooves") or {}
    if phrase not in grooves:
        raise ModelError(f"section {sec['name']}: unknown groove {phrase!r}")
    n_steps = sec["bars"] * song.steps_per_bar
    lines = {k: re.sub(r"[|\s]", "", v) for k, v in grooves[phrase].items()}
    fill = sec.get("fill")
    fill_lines = {k: re.sub(r"[|\s]", "", v) for k, v in grooves[fill].items()} if fill else None
    if fill and fill not in grooves:
        raise ModelError(f"section {sec['name']}: unknown fill {fill!r}")
    for name in sorted(set(lines) | set(fill_lines or {})):
        if name in part.kit:
            key = part.kit[name]
        else:
            try:
                key = note_to_midi(name if not str(name).isdigit() else int(name))
            except ModelError:
                raise ModelError(f"groove {phrase}: drum {name!r} is not in part {part.name}'s kit {sorted(part.kit)}")
        pat = lines.get(name, "")
        if pat and len(pat) % song.steps_per_bar:
            raise ModelError(f"groove {phrase}/{name}: length {len(pat)} is not a multiple of {song.steps_per_bar}")
        for i in range(n_steps):
            if fill_lines is not None and i >= n_steps - song.steps_per_bar:
                fp = fill_lines.get(name, "")
                c = fp[i - (n_steps - song.steps_per_bar)] if fp else "."
            else:
                c = pat[i % len(pat)] if pat else "."
            if c == ".":
                continue
            if c not in DRUM_VEL:
                raise ModelError(f"groove {phrase}/{name}: bad char {c!r} (use . x X o r R f)")
            tick = sec["start"] + i * song.clocks_per_step
            bar = i // song.steps_per_bar + 1
            half = max(1, song.clocks_per_step // 2)
            if c in "rR":
                song.notes.append(Note(swung(tick), half, key, vel_at(int(DRUM_VEL[c] * 0.85), tick), part.name, sec["name"], bar))
                song.notes.append(Note(swung(tick) + half, half, key, vel_at(DRUM_VEL[c], tick), part.name, sec["name"], bar))
            elif c == "f":
                song.notes.append(Note(max(0, swung(tick) - 1), 1, key, vel_at(40, tick), part.name, sec["name"], bar))
                song.notes.append(Note(swung(tick), song.clocks_per_step, key, vel_at(DRUM_VEL[c], tick), part.name, sec["name"], bar))
            else:
                song.notes.append(Note(swung(tick), song.clocks_per_step, key, vel_at(DRUM_VEL[c], tick), part.name, sec["name"], bar))
