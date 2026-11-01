"""Hard limits (errors) and Emerald-style guidelines (warnings) for a song. Numbers: gba.py and CONSTRAINTS.md;
the guideline ranges come from the 211 vanilla songs (generate.py survey -> reference/vanilla_songs.json)."""
from __future__ import annotations

import json
from dataclasses import dataclass

import gba
from song import Song, midi_name

SURVEY = gba.HERE / "reference" / "vanilla_songs.json"


@dataclass
class Use:
    tick: int
    end: int
    kind: str          # pcm / square1 / square2 / wave / noise / ?
    part: str
    key: int
    voice: gba.Voice | None


def usage(vg: gba.VoiceGroup, events, tempo: int) -> list[Use]:
    """events: (tick, dur, program, key, part). Resolves each note to the voice that plays it. A one-shot sample
    (a drum hit) frees its voice when the sample ends, even if the MIDI note is held longer."""
    out = []
    for t, d, prog, key, part in events:
        v, k = gba.resolve(vg, prog, key)
        kind = v.kind if v is not None and not v.filler else "?"
        end = t + d
        if kind == "pcm":
            try:
                smp = gba.sample(v.sample)
            except Exception:       # noqa: BLE001
                smp = None
            if smp is not None and smp.loop_start is None:
                rate = smp.rate if v.fixed_rate else smp.rate * 2 ** ((k - 60) / 12)
                clocks = len(smp.data) / rate * tempo * gba.CLOCKS_PER_BEAT / 60
                end = min(end, t + max(1, int(clocks)))
        out.append(Use(t, end, kind, str(part), k, v))
    return out


def peaks(uses: list[Use]) -> dict:
    """Most notes sounding at once (gate time, not counting release) per voice kind, and CGB clashes: two parts
    on the same Game Boy channel at the same time (the later note takes the channel)."""
    res = {"max_pcm": 0, "pcm_over": [], "cgb_clash": []}
    ev = sorted([(u.tick, 1, u) for u in uses if u.kind == "pcm"] + [(u.end, 0, u) for u in uses if u.kind == "pcm"],
                key=lambda e: (e[0], e[1]))
    n = 0
    for t, typ, _u in ev:
        n += 1 if typ else -1
        if n > res["max_pcm"]:
            res["max_pcm"] = n
        if typ and n > gba.MAX_PCM_VOICES:
            res["pcm_over"].append(t)
    for kind in gba.CGB_KINDS:
        us = sorted((u for u in uses if u.kind == kind), key=lambda u: u.tick)
        for a, b in zip(us, us[1:]):
            if b.tick < a.end and a.part != b.part:
                res["cgb_clash"].append((b.tick, kind, a.part, b.part))
    return res


def song_events(song: Song):
    return [(n.tick, n.dur, song.parts[n.part].program, n.key, n.part) for n in song.notes]


def survey_ranges() -> dict:
    if SURVEY.exists():
        return json.loads(SURVEY.read_text()).get("ranges", {})
    return {}


def where(song: Song, tick: int) -> str:
    for s in reversed(song.sections):
        if tick >= s["start"]:
            return f"{s['name']} bar {(tick - s['start']) // song.clocks_per_bar + 1}"
    return f"tick {tick}"


def check(song: Song, asm: str | None = None, stats: dict | None = None) -> tuple[list[str], list[str]]:
    """(errors, warnings). Errors break the game or the build; warnings are things vanilla songs never do."""
    E, W = list(song.errors), list(song.warnings)
    m = song.model
    player = m.get("player", "BGM")
    if player not in gba.PLAYER_TRACKS:
        E.append(f"player {player!r}: one of {sorted(gba.PLAYER_TRACKS)}")
    else:
        used = [p for p in song.parts.values() if any(n.part == p.name for n in song.notes)]
        if len(used) > gba.PLAYER_TRACKS[player]:
            E.append(f"{len(used)} parts with notes; the {player} player has {gba.PLAYER_TRACKS[player]} tracks "
                     f"(extra tracks are dropped)")
    if song.tempo % 2 or not 2 <= song.tempo <= gba.MAX_TEMPO_BPM:
        E.append(f"tempo {song.tempo}: must be even and 2..{gba.MAX_TEMPO_BPM} (m4a stores bpm / 2 in one byte)")
    vol = int(m.get("master_volume", 80))
    if not 0 < vol <= 127:
        E.append(f"master_volume {vol}: 1..127 (midi.cfg -V)")
    for p in song.parts.values():
        if not 0 <= p.channel <= 15:
            E.append(f"part {p.name}: channel {p.channel} (0..15)")
        if not 0 <= p.program < gba.VOICEGROUP_SLOTS:
            E.append(f"part {p.name}: program {p.program} (0..127)")
            continue
        v = song.voicegroup.slot(p.program)
        if v is None or v.filler:
            E.append(f"part {p.name}: program {p.program} is an empty slot in voicegroup {song.voicegroup.name} "
                     f"(see docs/voicegroups.md)")
        if not 0 <= p.volume <= 127 or not -64 <= p.pan <= 63:
            E.append(f"part {p.name}: volume 0..127, pan -64..63")
        if p.priority is not None and not 0 <= int(p.priority) <= 127:
            E.append(f"part {p.name}: priority 0..127")
    if m.get("loop", True) and song.loop_clocks <= 0:
        E.append("loop: the loop is empty (loop_start is the last section?)")

    uses = usage(song.voicegroup, song_events(song), song.tempo)
    bad = sorted({(u.part, midi_name(u.key)) for u in uses if u.kind == "?"})
    for part, key in bad[:10]:
        E.append(f"part {part}: {key} hits an empty slot (key split / drum kit has no voice there)")
    pk = peaks(uses)
    if pk["pcm_over"]:
        W.append(f"{len(pk['pcm_over'])} notes start while 5 Direct Sound voices already play (first at "
                 f"{where(song, pk['pcm_over'][0])}); m4a steals a voice, so a note cuts out")
    rng = survey_ranges()
    head = rng.get("max_pcm_p90")
    if head and pk["max_pcm"] > head and not pk["pcm_over"]:
        W.append(f"up to {pk['max_pcm']} Direct Sound notes at once; 90% of vanilla songs stay at {head} or fewer, "
                 f"leaving voices for sound effects and cries")
    for t, kind, a, b in pk["cgb_clash"][:5]:
        W.append(f"{where(song, t)}: parts {a} and {b} both play the {kind} channel at once (one note per channel)")
    for p in song.parts.values():
        kinds = {u.kind for u in uses if u.part == p.name}
        if kinds & set(gba.CGB_KINDS):
            starts = {}
            for u in uses:
                if u.part == p.name:
                    starts[u.tick] = starts.get(u.tick, 0) + 1
            if max(starts.values(), default=1) > 1:
                W.append(f"part {p.name}: chords on a Game Boy channel play one note (set mono or use a PCM voice)")
    hi_step = 0.0
    for u in uses:
        if u.kind == "pcm" and u.voice is not None and not u.voice.fixed_rate:
            try:
                s = gba.sample(u.voice.sample)
            except Exception:
                continue
            hi_step = max(hi_step, s.rate * 2 ** ((u.key - 60) / 12) / gba.MIXER_RATE)
    if hi_step > 4:
        W.append(f"a sample plays {hi_step:.1f}x faster than the mixer rate (key too high for its voice): "
                 f"harsh aliasing; vanilla songs stay under 4x")
    for n in song.notes:
        if n.tick + n.dur > song.total_clocks:
            W.append(f"part {n.part}: a note at {where(song, n.tick)} rings past the end; cut at the loop point")
            break
    loop_s = song.seconds(song.loop_clocks)
    form = m.get("form", "LOOP")
    lo, hi = (rng.get(f"loop_s_{form}") or [None, None])
    if lo and m.get("loop", True) and not lo <= loop_s <= hi:
        W.append(f"loop is {loop_s:.1f} s; vanilla {form} songs loop in {lo:.0f}..{hi:.0f} s")
    if asm is not None:
        size = gba.song_bytes(asm)
        mx = rng.get("bytes_max")
        if mx and size > mx:
            W.append(f"{size} bytes of track data; the largest vanilla song is {mx}")
        if m.get("loop", True) and "GOTO" not in asm:
            E.append("mid2agb output has no GOTO: the loop markers were not read")
    if stats:
        if stats.get("unresolved"):
            E.append(f"preview could not resolve {stats['unresolved'][:3]}")
        if stats.get("pcm_clip", 0) > 0.001:
            W.append(f"PCM mix clips {stats['pcm_clip'] * 100:.1f}% of the time: lower part volumes or master_volume")
    return E, W
