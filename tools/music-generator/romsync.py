#!/usr/bin/env python3
"""Record a cutscene from the real ROM with its music, frame by frame, to check the music against the picture.

  python3 romsync.py song-schemas/intro-boot.yaml [--frames 2450] [--video]   # scratch ROM with the song installed
  python3 romsync.py --as-is [--frames 2450] [--video]                       # the game as it is

Writes out/rom-sync/<name>/:
  log.csv     one row per emulated frame from power-on: emu_frame, intro_frame (gIntroFrameCounter), bgm_header,
              bgm_status, bgm_clock (the BGM MusicPlayerInfo), so every cue maps to the clock the engine was really
              on, lag frames and the start offset included
  audio.wav   the ROM's audio from the frame the song plays clock 0 on (sample 0 = song frame 0)
  capture.mp4 (--video) picture and sound at true speed from 1.5 s before the song: what the owner watches
Then runs `cuesync.py rom` on the log and the recording.

The ROM runs in `romcap` (romcap/romcap.c, built here against libmgba from the play-tester's mGBA 0.11): headless,
as fast as the CPU goes, every audio sample and every frame the core produces, so picture, sound and log are
locked to the emulated frame. (The real-time frontends pad the audio with silence whenever the emulator falls
behind real time, which it does in a small container: useless for timing.) The scratch tree is
$TMPDIR/music-romsync/game, a copy of ../../game with the song installed through generate.py install;
../../game is not touched.
"""
from __future__ import annotations

import argparse
import csv
import os
import shutil
import subprocess
import sys
import wave
from pathlib import Path

import numpy as np

import gba

HERE = gba.HERE
GAME = HERE.parent.parent / "game"
WORK = Path(os.environ.get("TMPDIR", "/tmp")) / "music-romsync"
MGBA = Path(os.environ.get("MGBA_PREFIX", "/opt/mgba-0.11"))
FPS = gba.FRAME_HZ
W, H = 240, 160


def sym(game: Path, name: str) -> int:
    for line in (game / "pokeemerald.sym").read_text().splitlines():
        p = line.split()
        if len(p) >= 4 and p[3] == name:
            return int(p[0], 16)
    raise SystemExit(f"{name} is not in pokeemerald.sym")


def romcap() -> Path:
    exe = WORK / "romcap"
    src = HERE / "romcap" / "romcap.c"
    if not exe.exists() or exe.stat().st_mtime < src.stat().st_mtime:
        WORK.mkdir(parents=True, exist_ok=True)
        # the installed flags.h leaves ENABLE_DIRECTORIES out although libmgba is built with it (struct mCore layout)
        subprocess.run(["gcc", "-O2", "-DENABLE_DIRECTORIES", "-o", str(exe), str(src), f"-I{MGBA}/include",
                        f"-L{MGBA}/lib", "-lmgba", f"-Wl,-rpath,{MGBA}/lib"], check=True)
    return exe


def prepare(model: Path | None, fresh: bool) -> Path:
    if model is None:
        if not (GAME / "pokeemerald.sym").exists():
            subprocess.run(["make", "syms"], cwd=GAME, capture_output=True)
        return GAME
    if fresh or not (WORK / "game").exists():
        shutil.rmtree(WORK / "game", ignore_errors=True)
        WORK.mkdir(parents=True, exist_ok=True)
        shutil.copytree(GAME, WORK / "game", symlinks=True, ignore=shutil.ignore_patterns("*.gba", "*.elf", "*.map"))
    g = WORK / "game"
    env = dict(os.environ, GAME_DIR=str(g))
    r = subprocess.run([sys.executable, str(HERE / "generate.py"), "install", str(model)], env=env,
                       capture_output=True, text=True)
    if r.returncode:
        sys.exit(r.stdout + r.stderr)
    r = subprocess.run(["make", f"-j{os.cpu_count()}"], cwd=g, capture_output=True, text=True)
    if r.returncode:
        sys.exit(r.stdout[-3000:] + r.stderr[-3000:])
    subprocess.run(["make", "syms"], cwd=g, capture_output=True)
    return g


def capture(game: Path, out: Path, frames: int, video_from: int) -> int:
    """Run the ROM; returns the audio sample rate. Leaves log.csv, audio.raw (and video.raw) in out/."""
    bgm = sym(game, "gMPlayInfo_BGM")
    watch = [f"intro_frame={sym(game, 'gIntroFrameCounter'):#x}", f"bgm_header={bgm:#x}",
             f"bgm_status={bgm + 4:#x}", f"bgm_clock={bgm + 12:#x}"]
    subprocess.run([str(romcap()), str(game / "pokeemerald.gba"), str(out), str(frames), str(video_from)] + watch,
                   check=True)
    return int((out / "audio.rate").read_text())


def song_start(game: Path, out: Path, song: str = "mus_intro") -> int:
    """Emu frame on which the song plays clock 0: the first logged frame whose BGM clock is past 0."""
    hdr = sym(game, song)
    return next(int(r["emu_frame"]) for r in csv.DictReader(open(out / "log.csv"))
                if int(r["bgm_header"]) == hdr and int(r["bgm_clock"]) > 0)


def write_wav(path: Path, y: np.ndarray, rate: int) -> None:
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(y.astype("<i2").tobytes())


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("model", nargs="?")
    ap.add_argument("--as-is", action="store_true", help="record ../../game as it is")
    ap.add_argument("--frames", type=int, default=2450, help="emulated frames from power-on (intro + scene 2)")
    ap.add_argument("--video", action="store_true", help="also write capture.mp4")
    ap.add_argument("--lead", type=float, default=1.5, help="seconds of picture before the song in capture.mp4")
    ap.add_argument("--fresh", action="store_true", help="recopy the scratch game tree")
    args = ap.parse_args(argv)
    if not args.as_is and not args.model:
        ap.error("give a song model or --as-is")
    model = None if args.as_is else Path(args.model)
    name = "as-is" if model is None else model.stem
    out = HERE / "out" / "rom-sync" / name
    shutil.rmtree(out, ignore_errors=True)
    out.mkdir(parents=True)
    game = prepare(model, args.fresh)
    print(f"== ROM {game / 'pokeemerald.gba'}: {args.frames} frames")
    rate = capture(game, out, args.frames, 0 if args.video else -1)
    c0 = song_start(game, out)
    spf = rate / FPS
    x = np.fromfile(out / "audio.raw", "<i2").reshape(-1, 2)
    write_wav(out / "audio.wav", x[int(round(c0 * spf)):], rate)
    print(f"   MUS_INTRO plays clock 0 on emu frame {c0}; {out / 'audio.wav'} ({rate} Hz)")
    if args.video:
        v0 = max(0, c0 - int(round(args.lead * FPS)))
        write_wav(out / "mux.wav", x[int(round(v0 * spf)):], rate)
        cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}",
               "-framerate", f"{FPS:.4f}", "-i", str(out / "video.raw"), "-i", str(out / "mux.wav"),
               "-vf", f"trim=start_frame={v0},setpts=PTS-STARTPTS,scale={W * 2}:{H * 2}:flags=neighbor,format=yuv420p",
               "-c:v", "libx264", "-crf", "16", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-shortest",
               str(out / "capture.mp4")]
        subprocess.run(cmd, check=True)
        (out / "mux.wav").unlink()
        (out / "video.raw").unlink()
        print(f"   {out / 'capture.mp4'} (from emu frame {v0})")
    (out / "audio.raw").unlink()
    if model is not None:
        import cuesync
        return cuesync.rom(out / "log.csv", model, wav=out / "audio.wav")
    return 0


if __name__ == "__main__":
    sys.exit(main())
