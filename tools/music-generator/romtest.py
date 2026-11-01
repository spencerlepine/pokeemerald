#!/usr/bin/env python3
"""Hear songs from the real ROM: build a scratch copy of ../../game with the songs installed (generate.py
install, the same code path as a real install) and a small test hook, then record each one out of mGBA.
For hot-swaps the vanilla song is recorded first, so the two can be compared.

  python3 romtest.py song-schemas/x.yaml [...] [--seconds 60]   -> out/rom/<name>.wav, out/rom/vanilla_<mus_x>.wav
  python3 romtest.py --vanilla MUS_ROUTE101 [--seconds 40]        -> out/rom/vanilla_mus_route101.wav only

Needs the play-tester setup (../play-tester/scripts/setup-ubuntu.sh: agbcc, mGBA 0.11, Xvfb). Nothing in
../../game is touched: the copy lives in $TMPDIR/music-romtest. The hook (never committed) reads a mailbox at
0x0203FF00 (free EWRAM above the game's last symbol) that mGBA cheat codes write every frame; once the boot has
run for a moment it starts the song on the BGM player and parks the main loop, so nothing else changes the
music. Sound keeps running from the VBlank and VCount interrupts (m4aSoundMain, m4aSoundVSync) as in game.
"""
from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
import wave
from pathlib import Path

import numpy as np

import gba
from song import load

HERE = gba.HERE
GAME = HERE.parent.parent / "game"
WORK = Path(os.environ.get("TMPDIR", "/tmp")) / "music-romtest"
MGBA = Path(os.environ.get("MGBA_PREFIX", "/opt/mgba-0.11")) / "bin" / "mgba"
RATE = 44100

HOOK = """        {   // MUSIC ROMTEST HOOK (scratch copy only, never committed)
            vu16 *mb = (vu16 *)0x0203FF00;
            if (mb[0] == 0xF00D && gMain.vblankCounter1 > (u32)mb[3])
            {
                m4aMPlayAllStop();
                m4aSongNumStart(mb[1]);
                for (;;)
                    VBlankIntrWait();
            }
        }
"""


def prepare(fresh: bool) -> Path:
    if fresh or not (WORK / "game").exists():
        shutil.rmtree(WORK, ignore_errors=True)
        WORK.mkdir(parents=True)
        shutil.copytree(GAME, WORK / "game", symlinks=True,
                        ignore=shutil.ignore_patterns("*.gba", "*.elf", "*.map"))
    g = WORK / "game"
    src = (GAME / "src" / "main.c").read_text()
    anchor = "    for (;;)\n    {\n        ReadKeys();\n"
    assert anchor in src, "src/main.c main loop changed; update romtest.HOOK"
    src = src.replace(anchor, anchor + HOOK, 1)
    for inc in ('#include "m4a.h"',):
        if inc not in src:
            src = src.replace('#include "main.h"', '#include "main.h"\n' + inc, 1)
    (g / "src" / "main.c").write_text(src)
    return g


def build(g: Path) -> None:
    r = subprocess.run(["make", f"-j{os.cpu_count()}"], cwd=g, capture_output=True, text=True)
    if r.returncode:
        sys.exit(r.stdout[-3000:] + r.stderr[-3000:])


def song_id(g: Path, const: str) -> int:
    h = (g / "include" / "constants" / "songs.h").read_text()
    m = re.search(rf"#define {const}\s+(\d+)", h)
    if not m:
        raise SystemExit(f"{const} is not in songs.h")
    return int(m.group(1))


def ensure_display() -> None:
    if "DISPLAY" not in os.environ:
        os.environ["DISPLAY"] = ":97"
        subprocess.Popen(["Xvfb", ":97", "-screen", "0", "640x480x24"], stdout=subprocess.DEVNULL,
                         stderr=subprocess.DEVNULL)


def record(rom: Path, ident: int, seconds: float, out: Path) -> np.ndarray:
    """Boot, start song `ident` at frame 30, record the SDL disk audio (s16 stereo 44.1 kHz) for `seconds`."""
    env = dict(os.environ, SDL_AUDIODRIVER="disk", LD_LIBRARY_PATH=str(MGBA.parent.parent / "lib"))
    with tempfile.TemporaryDirectory() as t:
        t = Path(t)
        (t / "c.cheats").write_text(f"# romtest\n8203FF00 F00D\n8203FF02 {ident:04X}\n8203FF06 001E\n")
        env["SDL_DISKAUDIOFILE"] = str(t / "out.raw")
        try:
            subprocess.run([str(MGBA), "-c", str(t / "c.cheats"), str(rom)], env=env, timeout=seconds + 3,
                           capture_output=True)
        except subprocess.TimeoutExpired:
            pass
        x = np.fromfile(t / "out.raw", "<i2").reshape(-1, 2)
    # the boot is silent until the song starts (the copyright screen plays nothing): cut to the first sound
    loud = np.where(np.abs(x.astype(np.int32)).max(axis=1) > 40)[0]
    if not len(loud):
        raise SystemExit(f"{out.name}: the ROM played nothing (song id {ident})")
    y = x[max(0, loud[0] - 64):]
    out.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(out), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(RATE)
        w.writeframes(y.astype("<i2").tobytes())
    print(f"  {out.relative_to(HERE)}  {len(y) / RATE:.1f} s")
    return y


def main(argv=None) -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("songs", nargs="*")
    ap.add_argument("--vanilla", action="append", default=[], help="also record this vanilla MUS_ constant")
    ap.add_argument("--seconds", type=float, default=0, help="record length (default: intro + 2 loops + 2 s)")
    a = ap.parse_args(argv)
    import generate                         # noqa: PLC0415 - generate imports this module's siblings
    ensure_display()
    songs = [(Path(p), load(Path(p))) for p in a.songs]
    g = prepare(fresh=True)
    build(g)
    outd = HERE / "out" / "rom"
    vanilla = list(a.vanilla) + [s.model["replaces"] for _, s in songs if s.model.get("replaces")]
    if vanilla:
        print("vanilla:")
    for const in dict.fromkeys(vanilla):
        record(g / "pokeemerald.gba", song_id(g, const), a.seconds or 40, outd / f"vanilla_{const.lower()}.wav")
    if not songs:
        return
    for p, s in songs:
        generate.render(p, quiet=True)
        generate.install(p, g)
    prepare(fresh=False)                    # re-apply the hook (install never touches main.c)
    build(g)
    print("new:")
    for p, s in songs:
        const = s.model.get("replaces") or s.model["constant"]
        secs = a.seconds or s.seconds(s.intro_clocks + 2 * max(s.loop_clocks, 0) or s.total_clocks) + 2
        record(g / "pokeemerald.gba", song_id(g, const), secs, outd / f"{s.name}.wav")


if __name__ == "__main__":
    main()
