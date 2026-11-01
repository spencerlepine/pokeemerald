"""GBA / m4a hardware model for Emerald music. Every number here is sourced in CONSTRAINTS.md.

music-generator's own copy (the sfx and cry generators keep theirs; the tools share nothing on purpose).

What a song in Emerald is:
  * a type-1 MIDI file in game/sound/songs/midi/, converted by mid2agb at 24 clocks per beat into m4a
    track data, with a midi.cfg line: -E (exact gate times) -R50 (reverb) -G<voicegroup> -V<volume> [-P<prio>]
  * played by one m4a music player (BGM: 10 tracks) through one voicegroup: 128 program slots, each a
    Direct Sound sample, a Game Boy channel (square 1, square 2, wave, noise), a key split or a drum kit
  * mixed by m4a: at most 5 Direct Sound (PCM) voices at once at 13379 Hz in 8 bits, plus the 4 Game Boy
    channels (one note each), all shared with sound effects and cries.
"""
from __future__ import annotations

import os
import re
import struct
import subprocess
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
GAME = Path(os.environ.get("GAME_DIR", HERE.parent.parent / "game"))

# ---- m4a mixer (src/m4a.c m4aSoundInit; include/gba/m4a_internal.h) ----
MIXER_RATE = 13379                    # SOUND_MODE_FREQ_13379: every PCM voice is resampled to this
NYQUIST = MIXER_RATE / 2              # 6689 Hz: nothing above this exists on the PCM side
MAX_PCM_VOICES = 5                    # SOUND_MODE_MAXCHN = 5 (of the 12 the engine allows)
MASTER_VOLUME = 12 / 15               # SOUND_MODE_MASVOL = 12
DAC_BITS = 8                          # SOUND_MODE_DA_BIT_8
FRAME_HZ = 16777216 / 280896          # 59.7275 Hz VBlank: envelopes, pitch, volume update once a frame
SAMPLES_PER_FRAME = 224               # 13379 / 59.73
REVERB = 50                           # -R50 on 209 of 210 BGM lines in midi.cfg
REVERB_TAPS = (6 * 224, 7 * 224)      # m4a_1.s SoundMainRAM_Reverb: ring of pcmDmaPeriod = 7 frames

# ---- music players (sound/music_player_table.inc, include/gba/m4a_internal.h) ----
PLAYER_TRACKS = {"BGM": 10, "SE1": 3, "SE2": 9, "SE3": 1}
MAX_MUSICPLAYER_TRACKS = 16
VOICEGROUP_SLOTS = 128

# ---- mid2agb (tools/mid2agb) ----
CLOCKS_PER_BEAT = 24                  # default; -X gives 48 (no Emerald song uses it)
MIDI_TPQN = 24                        # every Emerald .mid uses 24 ticks per quarter note
MIDI_CC = {"mod": 1, "volume": 7, "pan": 10, "bend_range": 20, "lfo_speed": 21, "mod_type": 22,
           "tune": 24, "lfo_delay": 26, "priority": 33}
LOOP_BEGIN, LOOP_END = "[", "]"       # meta text events on the conductor track (mid2agb main loop)
MAX_TEMPO_BPM = 510                   # TEMPO is one byte holding bpm / 2 (agb.cpp: TEMPO , bpm*tbs/2)

# ---- CGB / PSG channels (GBATEK; m4a CgbSound in src/m4a.c) ----
SQUARE_DUTIES = {0: 0.125, 1: 0.25, 2: 0.5, 3: 0.75}
CGB_KINDS = ("square1", "square2", "wave", "noise")

# ---- what vanilla songs look like (generate.py survey over the 211 vanilla songs; reference/vanilla_songs.json)
FILLER_SLOT = "voice_square_1 60, 0, 0, 2, 0, 0, 15, 0"   # the empty-slot entry (17,792 of them)


# ------------------------------------------------------------------ voicegroups

@dataclass
class Voice:
    slot: int
    macro: str
    args: list[str]
    line: str

    @property
    def kind(self) -> str:
        m = self.macro
        if m.startswith("voice_directsound"):
            return "pcm"
        if m.startswith("voice_square_1"):
            return "square1"
        if m.startswith("voice_square_2"):
            return "square2"
        if m.startswith("voice_programmable_wave"):
            return "wave"
        if m.startswith("voice_noise"):
            return "noise"
        if m == "voice_keysplit":
            return "keysplit"
        if m == "voice_keysplit_all":
            return "drumset"
        return "?"

    @property
    def filler(self) -> bool:
        return self.line == FILLER_SLOT

    @property
    def base_key(self) -> int:
        return int(self.args[0]) if self.kind not in ("keysplit", "drumset") else 60

    @property
    def pan(self) -> int:
        return int(self.args[1]) if self.kind not in ("keysplit", "drumset") else 0

    @property
    def sample(self) -> str:
        return self.args[2].replace("DirectSoundWaveData_", "") if self.kind == "pcm" else ""

    @property
    def adsr(self) -> tuple[int, int, int, int]:
        a = [int(x) for x in self.args[-4:]]
        return a[0], a[1], a[2], a[3]

    @property
    def fixed_rate(self) -> bool:
        return self.macro == "voice_directsound_no_resample"

    def describe(self) -> str:
        k = self.kind
        if k == "pcm":
            return f"pcm {self.sample}" + (" (fixed pitch)" if self.fixed_rate else "")
        if k in ("square1", "square2"):
            duty = self.args[3] if k == "square1" else self.args[2]
            return f"{k} duty {SQUARE_DUTIES[int(duty) & 3] * 100:g}%"
        if k == "wave":
            return f"wave {self.args[2].replace('ProgrammableWaveData_', '')}"
        if k == "noise":
            return f"noise {'7-bit metallic' if int(self.args[2]) & 1 else '15-bit hiss'}"
        if k == "keysplit":
            return f"keysplit {self.args[0].replace('voicegroup_', '')} / {self.args[1].replace('keysplit_', '')}"
        if k == "drumset":
            return f"drumset {self.args[0].replace('voicegroup_', '')}"
        return self.line


@dataclass
class VoiceGroup:
    name: str
    start: int
    voices: list[Voice] = field(default_factory=list)
    file: str = ""

    def slot(self, n: int) -> Voice | None:
        i = n - self.start
        return self.voices[i] if 0 <= i < len(self.voices) else None


def _split_args(s: str) -> list[str]:
    return [a.strip() for a in s.split(",") if a.strip()]


@lru_cache(maxsize=1)
def voicegroups() -> dict[str, VoiceGroup]:
    """Every voice_group in sound/voicegroups/**/*.inc, by label (without the voicegroup_ prefix)."""
    out: dict[str, VoiceGroup] = {}
    for path in sorted((GAME / "sound" / "voicegroups").rglob("*.inc")):
        cur = None
        for raw in path.read_text().splitlines():
            line = raw.split("@")[0].strip()
            if not line:
                continue
            if line.startswith("voice_group "):
                a = _split_args(line[len("voice_group "):])
                cur = VoiceGroup(a[0], int(a[1]) if len(a) > 1 else 0, file=str(path.relative_to(GAME)))
                out[cur.name] = cur
                continue
            if cur is None or not line.startswith("voice_"):
                continue
            macro, _, rest = line.partition(" ")
            norm = f"{macro} {', '.join(_split_args(rest))}"
            cur.voices.append(Voice(cur.start + len(cur.voices), macro, _split_args(rest), norm))
    return out


@lru_cache(maxsize=1)
def keysplit_tables() -> dict[str, dict[int, int]]:
    """sound/keysplit_tables.inc: keysplit name -> {midi key: sub-voice index}."""
    out, cur, key = {}, None, 0
    for raw in (GAME / "sound" / "keysplit_tables.inc").read_text().splitlines():
        line = raw.split("@")[0].strip()
        if line.startswith("keysplit "):
            a = _split_args(line[len("keysplit "):])
            cur, key = {}, int(a[1]) if len(a) > 1 else 0
            out["keysplit_" + a[0]] = cur
        elif line.startswith("split ") and cur is not None:
            idx, top = (int(x) for x in _split_args(line[len("split "):]))
            for k in range(key, top):
                cur[k] = idx
            key = top
    return out


def resolve(vg: VoiceGroup, program: int, key: int) -> tuple[Voice | None, int]:
    """The voice m4a actually plays for (program, key), and the key it plays it at.
    Key splits keep the key; drum kits (keysplit_all) play the sub-voice at the sub-voice's own base key."""
    v = vg.slot(program)
    if v is None:
        return None, key
    if v.kind == "keysplit":
        sub = voicegroups().get(v.args[0].replace("voicegroup_", ""))
        idx = keysplit_tables().get(v.args[1], {}).get(key)
        if sub is None or idx is None:
            return None, key
        return (sub.voices[idx] if idx < len(sub.voices) else None), key
    if v.kind == "drumset":
        sub = voicegroups().get(v.args[0].replace("voicegroup_", ""))
        s = sub.slot(key) if sub else None
        return s, (s.base_key if s else key)
    return v, key


# ------------------------------------------------------------------ samples

@dataclass
class Sample:
    name: str
    data: np.ndarray        # float32 -1..1
    rate: float             # Hz at key 60
    loop_start: int | None  # None: one-shot
    loop_end: int


@lru_cache(maxsize=1)
def _sample_paths() -> dict[str, str]:
    """DirectSoundWaveData_<name> label -> .wav path, from sound/direct_sound_data.inc."""
    out, label = {}, None
    for line in (GAME / "sound" / "direct_sound_data.inc").read_text().splitlines():
        m = re.match(r"\s*(DirectSoundWaveData_\w+)::", line)
        if m:
            label = m[1].replace("DirectSoundWaveData_", "")
        m = re.search(r'\.incbin\s+"([^"]+)\.bin"', line)
        if m and label:
            out[label] = m[1] + ".wav"
            label = None
    return out


@lru_cache(maxsize=None)
def sample(name: str) -> Sample:
    path = GAME / _sample_paths()[name]
    d = path.read_bytes()
    i, fmt, smpl, agbp, agbl, data = 12, None, None, None, None, b""
    while i + 8 <= len(d):
        cid, n = d[i:i + 4], struct.unpack("<I", d[i + 4:i + 8])[0]
        body = d[i + 8:i + 8 + n]
        if cid == b"fmt ":
            fmt = struct.unpack("<HHIIHH", body[:16])
        elif cid == b"smpl":
            smpl = body
        elif cid == b"agbp":
            agbp = struct.unpack("<I", body[:4])[0]
        elif cid == b"agbl":
            agbl = struct.unpack("<I", body[:4])[0]
        elif cid == b"data":
            data = body
        i += 8 + n + (n & 1)
    bits = fmt[5]
    x = ((np.frombuffer(data, np.uint8).astype(np.float32) - 128) / 128 if bits == 8
         else np.frombuffer(data, "<i2").astype(np.float32) / 32768)
    rate = agbp / 1024 if agbp else float(fmt[2])
    ls, le = None, len(x)
    if smpl and struct.unpack("<I", smpl[28:32])[0] >= 1:
        ls = struct.unpack("<I", smpl[44:48])[0]
        le = struct.unpack("<I", smpl[48:52])[0] + 1
    if agbl:
        le = agbl
    return Sample(name, x, rate, ls, min(le, len(x)))


@lru_cache(maxsize=None)
def wave_pcm(label: str) -> np.ndarray:
    """ProgrammableWaveData_<n>: 16 bytes, 32 x 4-bit steps -> -1..1."""
    n = label.replace("ProgrammableWaveData_", "")
    raw = (GAME / "sound" / "programmable_wave_samples" / f"{int(n):02d}.pcm").read_bytes()[:16]
    steps = []
    for b in raw:
        steps += [b >> 4, b & 15]
    return (np.array(steps, np.float32) - 7.5) / 7.5


# ------------------------------------------------------------------ the game's own songs

def midi_cfg() -> dict[str, str]:
    out = {}
    for line in (GAME / "sound" / "songs" / "midi" / "midi.cfg").read_text().splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            out[k.strip()] = v.strip()
    return out


def cfg_args(args: str) -> dict:
    o = {"exact_gate": "-E" in args.split()}
    for a in args.split():
        for flag, key in (("-G", "voicegroup"), ("-V", "volume"), ("-R", "reverb"), ("-P", "priority")):
            if a.startswith(flag):
                o[key] = a[2:].lstrip("_") if flag == "-G" else int(a[2:])
    return o


# ------------------------------------------------------------------ mid2agb

def mid2agb_path() -> Path:
    exe = GAME / "tools" / "mid2agb" / "mid2agb"
    if not exe.exists():
        r = subprocess.run(["make", "-s"], cwd=exe.parent, capture_output=True, text=True)
        if r.returncode:
            raise RuntimeError(f"building mid2agb failed:\n{r.stderr[-2000:]}")
    return exe


def run_mid2agb(mid: Path, out_s: Path, args: str) -> str:
    """Convert like the game build does (audio_rules.mk). Returns the assembly text."""
    r = subprocess.run([str(mid2agb_path()), str(mid), str(out_s), *args.split()], capture_output=True, text=True)
    if r.returncode:
        raise RuntimeError(f"mid2agb rejected {mid.name}: {r.stdout}{r.stderr}")
    return out_s.read_text()


def song_bytes(asm: str) -> int:
    """ROM bytes of a mid2agb song: every .byte / .word / .4byte operand, plus the header."""
    n = 0
    for line in asm.splitlines():
        s = line.split("@")[0].strip()
        if s.startswith(".byte"):
            n += len(_split_args(s[5:]))
        elif s.startswith((".word", ".4byte")):
            n += 4 * len(_split_args(s.split(None, 1)[1]))
    return n
