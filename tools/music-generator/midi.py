"""Song -> type-1 MIDI exactly like Emerald's own: 24 ticks per quarter, track 0 is the conductor (tempo, time
signature and the `[` `]` loop markers mid2agb reads), then one track per part on its own channel with its
program, volume, pan and LFO controllers at tick 0."""
from __future__ import annotations

import struct

import gba
from song import Song


def _vlq(n: int) -> bytes:
    out = [n & 0x7F]
    n >>= 7
    while n:
        out.append(0x80 | (n & 0x7F))
        n >>= 7
    return bytes(reversed(out))


def _track(events: list[tuple[int, int, bytes]], end: int = 0) -> bytes:
    """events: (tick, order, raw bytes without delta). Sorted, delta-encoded, end-of-track at `end`."""
    events = sorted(events, key=lambda e: (e[0], e[1]))
    body, last = b"", 0
    for t, _, raw in events:
        body += _vlq(t - last) + raw
        last = t
    body += _vlq(max(0, end - last)) + b"\xff\x2f\x00"
    return b"MTrk" + struct.pack(">I", len(body)) + body


def _meta_text(text: str) -> bytes:
    b = text.encode()
    return b"\xff\x06" + _vlq(len(b)) + b     # marker event (type 6), as in the vanilla files


def write(song: Song, path) -> None:
    num, den = song.model.get("time_signature", [4, 4])
    us = round(60_000_000 / song.tempo)
    cond = [(0, 0, b"\xff\x51\x03" + us.to_bytes(3, "big")),
            (0, 1, b"\xff\x58\x04" + bytes([num, {1: 0, 2: 1, 4: 2, 8: 3, 16: 4}[den], 24, 8]))]
    looped = song.intro_clocks < song.total_clocks
    if looped:
        cond.append((song.intro_clocks, 2, _meta_text(gba.LOOP_BEGIN)))
        cond.append((song.total_clocks, 3, _meta_text(gba.LOOP_END)))
    tracks = [_track(cond, song.total_clocks)]
    for part in song.parts.values():
        c = part.channel
        ev = [(0, 0, bytes([0xC0 | c, part.program])),
              (0, 1, bytes([0xB0 | c, gba.MIDI_CC["volume"], max(0, min(127, part.volume))])),
              (0, 2, bytes([0xB0 | c, gba.MIDI_CC["pan"], max(0, min(127, 64 + part.pan))]))]
        if part.bend_range != 2:
            ev.append((0, 3, bytes([0xB0 | c, gba.MIDI_CC["bend_range"], part.bend_range])))
        for k, cc in (("lfo_speed", "lfo_speed"), ("mod_type", "mod_type"), ("lfo_delay", "lfo_delay"), ("mod", "mod")):
            v = getattr(part, k)
            if v:
                ev.append((0, 4, bytes([0xB0 | c, gba.MIDI_CC[cc], v])))
        if part.priority is not None:
            ev.append((0, 5, bytes([0xB0 | c, gba.MIDI_CC["priority"], int(part.priority)])))
        for n in song.notes:
            if n.part != part.name:
                continue
            ev.append((n.tick, 20, bytes([0x90 | c, n.key, n.vel])))
            ev.append((n.tick + n.dur, 10, bytes([0x80 | c, n.key, 0])))    # offs sort before ons at a tick
        tracks.append(_track(ev, song.total_clocks))
    data = b"MThd" + struct.pack(">IHHH", 6, 1, len(tracks), gba.MIDI_TPQN) + b"".join(tracks)
    path.write_bytes(data)


# ------------------------------------------------------------------ reading (vanilla songs, round-trip checks)

def _rvlq(d: bytes, i: int) -> tuple[int, int]:
    v = 0
    while True:
        b = d[i]
        i += 1
        v = (v << 7) | (b & 0x7F)
        if not b & 0x80:
            return v, i


def read(path) -> dict:
    """Any type-0/1 MIDI -> {tpqn, tempo_us, loop: (begin, end) ticks or None, end, tracks: [{channels, notes,
    programs, cc}]}. notes are (tick, dur, channel, key, vel); programs/cc are (tick, channel, number[, value])."""
    d = open(path, "rb").read()
    if d[:4] != b"MThd":
        raise ValueError(f"{path}: not a MIDI file")
    _fmt, ntrk, tpqn = struct.unpack(">HHH", d[8:14])
    i, out = 14, {"tpqn": tpqn, "tempo_us": 500000, "loop": None, "end": 0, "tracks": []}
    begin = end = None
    while i < len(d) and d[i:i + 4] == b"MTrk":
        ln = struct.unpack(">I", d[i + 4:i + 8])[0]
        j, stop, t, run = i + 8, i + 8 + ln, 0, 0
        trk = {"channels": set(), "notes": [], "programs": [], "cc": []}
        on: dict[tuple[int, int], list[tuple[int, int]]] = {}
        while j < stop:
            dt, j = _rvlq(d, j)
            t += dt
            st = d[j]
            if st == 0xFF:
                typ = d[j + 1]
                n, j = _rvlq(d, j + 2)
                data = d[j:j + n]
                j += n
                if typ == 0x51 and n == 3 and t == 0:
                    out["tempo_us"] = int.from_bytes(data, "big")
                elif typ in (0x01, 0x06) and data == gba.LOOP_BEGIN.encode():
                    begin = t
                elif typ in (0x01, 0x06) and data == gba.LOOP_END.encode():
                    end = t
                continue
            if st in (0xF0, 0xF7):
                n, j = _rvlq(d, j + 1)
                j += n
                continue
            if st & 0x80:
                run, j = st, j + 1
            hi, ch = run & 0xF0, run & 0x0F
            a = d[j]
            b = d[j + 1] if hi not in (0xC0, 0xD0) else 0
            j += 1 if hi in (0xC0, 0xD0) else 2
            trk["channels"].add(ch)
            if hi == 0x90 and b:
                on.setdefault((ch, a), []).append((t, b))
            elif hi in (0x80, 0x90):
                if on.get((ch, a)):
                    t0, v = on[(ch, a)].pop(0)
                    trk["notes"].append((t0, t - t0, ch, a, v))
            elif hi == 0xC0:
                trk["programs"].append((t, ch, a))
            elif hi == 0xB0:
                trk["cc"].append((t, ch, a, b))
        out["end"] = max(out["end"], t)
        trk["notes"].sort()
        out["tracks"].append(trk)
        i = stop
    if begin is not None and end is not None:
        out["loop"] = (begin, end)
    return out
