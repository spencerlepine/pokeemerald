"""See the effect in the real game.

Builds two scratch copies of ../../game (nothing in the repo is touched): `vanilla` and `new` (the built
sheets installed at their game paths). In both, the test move's accuracy is set to 255 (0 means "always misses" in this engine) so the
animation always plays. Each ROM boots headless in mGBA (play-tester setup), mashes through New Game,
gets a party member that knows the move, walks into Route 101 grass, and uses the move in the first
wild battle while every 2nd frame is screenshotted.

Both runs get identical inputs, so they are frame-aligned: the frames where the two screenshots differ
are exactly the frames where the new art is on screen. Output in output/<name>/rom/:
  rom.gif        vanilla | new, the window where the art shows (+ a little lead-in), 2x
  rom_strip.png  the six frames with the most new-art pixels
  report.txt     frames with art, first/last frame, timing

Spec keys (all optional):
  romtest:
    move: MOVE_ZAP_CANNON        # the move to use (default: the first user of the sheet)
    species: 280                 # the party member's species id (default Ralts)
    capture: 900                 # frames to film after the battle starts
    hp: 0.5                      # start the party member at this share of its HP (healing moves fail at full HP)
    tap_until: 660               # keep tapping A until this battle frame (raise it for a second turn, e.g. SKETCH
                                 # fails on turn 1 because the foe has not moved yet)
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import time
from pathlib import Path

import numpy as np
from PIL import Image

from . import catalog, preview
from .game import GAME, OUT, TOOLS
from .spec import load_spec

WORK = Path(os.environ.get("VFX_ROMTEST_DIR", "/var/tmp/vfx-romtest"))
PT = TOOLS / "play-tester"
MGBA = Path(os.environ.get("MGBA_PREFIX", "/opt/mgba-0.11")) / "bin" / "mgba-qt"


def _move_id(name: str) -> int:
    t = (GAME / "include/constants/moves.h").read_text()
    m = re.search(r'#define\s+' + re.escape(name) + r'\s+(\d+)', t)
    if not m:
        raise SystemExit(f"unknown move {name}")
    return int(m.group(1))


def _prepare(which: str, installs: dict[str, Path], move: str, fresh: bool) -> Path:
    g = WORK / which / "game"
    if fresh or not g.exists():
        shutil.rmtree(g, ignore_errors=True)
        g.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(GAME, g, symlinks=True)
    # restore anything a previous run installed, then install this run's sheets
    man = g.parent / "installed.json"
    prev = json.loads(man.read_text()) if man.exists() else []
    for rel in prev:
        src = GAME / rel
        if src.exists():
            shutil.copy2(src, g / rel)
    for rel, png in installs.items():
        shutil.copy2(png, g / rel)
        os.utime(g / rel, None)
    man.write_text(json.dumps(sorted(installs)))
    # the test move never misses (scratch copy only)
    bm = GAME / "src/data/battle_moves.h"
    t = bm.read_text()
    t2 = re.sub(r'(\[' + re.escape(move) + r'\]\s*=\s*\{[^}]*?\.accuracy\s*=\s*)\d+', r'\g<1>255', t, count=1)
    dst = g / "src/data/battle_moves.h"
    if dst.read_text() != t2:
        dst.write_text(t2)
    return g


def _make(g: Path):
    r = subprocess.run(["make", "-j", str(os.cpu_count() or 4)], cwd=g, capture_output=True, text=True)
    if r.returncode:
        raise SystemExit(f"make failed in {g}:\n{r.stdout[-2000:]}\n{r.stderr[-2000:]}")
    subprocess.run(["make", "syms"], cwd=g, capture_output=True, text=True)


def _sym(g: Path, name: str) -> int:
    for line in (g / "pokeemerald.sym").read_text().split("\n"):
        parts = line.split()
        if len(parts) >= 4 and parts[-1] == name:
            return int(parts[0], 16)
    raise SystemExit(f"{name} not in {g}/pokeemerald.sym")


LUA = r'''
local LOG = io.open("{out}/lua.log", "w")
local function log(s) LOG:write(s .. "\n"); LOG:flush() end
dofile("{pt}/lua/emerald.lua")
local OW, BATTLE = {ow}, {battle}
local f, phase, taps, n = 0, "boot", 0, 0
local CB2 = function() return emu:read32(E.ADDR.gMainCallback2) end
callbacks:add("frame", function()
  local ok, e = pcall(function()
    f = f + 1
    if phase == "boot" then
      if CB2() == OW then phase = "party"; f = 0; emu:setKeys(0); log("overworld " .. taps) end
      local k = f % 16
      if k == 0 then taps = taps + 1; emu:setKeys((taps % 8 == 0) and 8 or 1) elseif k == 4 then emu:setKeys(0) end
      if f > 20000 then log("never reached the overworld"); phase = "done"; local h = io.open("{out}/DONE","w"); h:write("fail"); h:close() end
      return
    end
    if phase == "party" and f == 30 then
      E.writeMon(0, {{species={species}, level=10, exp=560, moves={{{move},0,0,0}}, pp={{20,0,0,0}}, base={{90,90,90,90,90,90}}, nick="TEST", personality=7}})
      if {hpf} < 1 then local a = E.ADDR.gPlayerParty; emu:write16(a + 0x56, math.max(1, math.floor(emu:read16(a + 0x58) * {hpf}))) end
      E.setFlag(0x860, true); E.teleport(0, 16, 3, 4); phase = "walk"; f = 0; log("teleported"); return
    end
    if phase == "walk" then
      if CB2() == BATTLE then phase = "battle"; f = 0; emu:setKeys(0); log("battle"); return end
      if f > 200 then local k = (f // 20) % 2; emu:setKeys(k == 0 and 32 or 16) end
      if f > 9000 then log("no battle"); phase = "done"; local h = io.open("{out}/DONE","w"); h:write("fail"); h:close() end
      return
    end
    if phase == "battle" then
      n = n + 1
      -- A taps: dismiss the intro text, FIGHT, the move (extra taps are ignored during the animation)
      local press = n >= 240 and n <= {tap_until} + 3 and (n - 240) % 60 < 4
      emu:setKeys(press and 1 or 0)
      if n >= 200 and n % 2 == 0 and n < 200 + {capture} then emu:screenshot(string.format("{out}/f%05d.png", n)) end
      if n == 200 + {capture} then local h = io.open("{out}/DONE","w"); h:write("ok"); h:close(); phase = "done" end
    end
  end)
  if not ok then log("err " .. tostring(e)) end
end)
'''


def _film(rom: Path, out: Path, move_id: int, species: int, capture: int, ow: int, battle: int,
          hpf: float = 1.0, tap_until: int = 660) -> bool:
    shutil.rmtree(out, ignore_errors=True)
    out.mkdir(parents=True)
    lua = out / "film.lua"
    lua.write_text(LUA.format(out=out, pt=PT, ow=hex(ow | 1), battle=hex(battle | 1), species=species, move=move_id,
                              capture=capture, hpf=hpf, tap_until=tap_until))
    env = dict(os.environ, QT_QPA_PLATFORM="xcb", SDL_AUDIODRIVER="dummy", LIBGL_ALWAYS_SOFTWARE="1",
               QT_X11_NO_MITSHM="1", LD_LIBRARY_PATH=str(MGBA.parent.parent / "lib"))
    p = subprocess.Popen(["timeout", "900", "xvfb-run", "-a", str(MGBA), "--script", str(lua), "-l", "0", str(rom)],
                         stdout=open(out / "mgba.log", "w"), stderr=subprocess.STDOUT, env=env, start_new_session=True)
    t0 = time.time()
    while time.time() - t0 < 880 and not (out / "DONE").exists():
        time.sleep(1)
    try:
        os.killpg(os.getpgid(p.pid), 9)
    except ProcessLookupError:
        pass
    return (out / "DONE").exists() and (out / "DONE").read_text() == "ok"


def run(a):
    specs = [load_spec(p) for p in a.spec]
    if not MGBA.exists():
        raise SystemExit("mGBA 0.11 is missing: run ../play-tester/scripts/setup-ubuntu.sh first")
    installs, moves = {}, []
    for s in specs:
        info = json.loads((OUT / s["name"] / "build.json").read_text())
        installs[info["replaces"]] = OUT / s["name"] / info["png"]
        rt = s.get("romtest") or {}
        mv = rt.get("move")
        if not mv:
            users = [u for u in catalog.find(info["replaces"]).get("users", []) if u.startswith("Move_")]
            mv = "MOVE_" + users[0][5:] if users else None
        if not mv:
            raise SystemExit(f"{s['name']}: no move uses this sheet; set romtest.move")
        moves.append((s, mv, int(rt.get("species", 280)), int(rt.get("capture", 900)),
                      float(rt.get("hp", 1.0)), int(rt.get("tap_until", 660))))
    for s, mv, species, capture, hpf, tap_until in moves:
        print(f"== {s['name']}: {mv}")
        gv = _prepare("vanilla", {}, mv, a.fresh)
        gn = _prepare("new", {k: v for k, v in installs.items()}, mv, a.fresh)
        for g in (gv, gn):
            print(f"  make {g}")
            _make(g)
        mid = _move_id(mv)
        res = {}
        for which, g in (("vanilla", gv), ("new", gn)):
            out = WORK / which / "film"
            ok = _film(g / "pokeemerald.gba", out, mid, species, capture, _sym(g, "CB2_Overworld"), _sym(g, "BattleMainCB2"),
                       hpf, tap_until)
            print(f"  film {which}: {'ok' if ok else 'FAILED'} ({(out / 'lua.log').read_text().strip().splitlines()[-1:] if (out / 'lua.log').exists() else ''})")
            res[which] = out if ok else None
        if not all(res.values()):
            continue
        _report(s, res["vanilla"], res["new"])


def _report(s, vdir: Path, ndir: Path):
    dst = OUT / s["name"] / "rom"
    dst.mkdir(parents=True, exist_ok=True)
    names = sorted(p.name for p in ndir.glob("f*.png"))
    diffs = []
    for nm in names:
        if not (vdir / nm).exists():
            continue
        a = np.asarray(Image.open(vdir / nm).convert("RGB")).astype(int)
        b = np.asarray(Image.open(ndir / nm).convert("RGB")).astype(int)
        diffs.append((nm, int((np.abs(a - b).sum(axis=2) > 0).sum())))
    shown = [d for d in diffs if d[1] > 0]
    lines = [f"# {s['name']} in the ROM", f"frames filmed: {len(diffs)} (every 2nd game frame)",
             f"frames where the new art is on screen: {len(shown)}"]
    if not shown:
        lines.append("the new art never appeared: the move missed, the battle went another way, or the sheet is not used")
        (dst / "report.txt").write_text("\n".join(lines) + "\n")
        print("\n".join(lines))
        return
    i0 = max(0, diffs.index(shown[0]) - 15)
    i1 = min(len(diffs), diffs.index(shown[-1]) + 15)
    lines.append(f"first {shown[0][0]}, last {shown[-1][0]} ({(diffs.index(shown[-1]) - diffs.index(shown[0]) + 1) * 2} game frames)")
    frames = []
    for nm, _ in diffs[i0:i1]:
        va = Image.open(vdir / nm).convert("RGB")
        nw = Image.open(ndir / nm).convert("RGB")
        frames.append(preview.labelled([("VANILLA ROM", preview.zoom(va, 2)), ("NEW ROM", preview.zoom(nw, 2))]))
    imgs = [f.convert("P", palette=Image.ADAPTIVE, colors=255, dither=Image.NONE) for f in frames]
    imgs[0].save(dst / "rom.gif", save_all=True, append_images=imgs[1:], duration=33, loop=0, optimize=False)
    top = sorted(shown, key=lambda d: -d[1])[:6]
    top = sorted(top, key=lambda d: d[0])
    strip = preview.labelled([(nm[1:6], preview.zoom(Image.open(ndir / nm).convert("RGB"), 2)) for nm, _ in top])
    strip.save(dst / "rom_strip.png")
    for nm, _ in top[:1]:
        Image.open(ndir / nm).save(dst / "rom_best_new.png")
        Image.open(vdir / nm).save(dst / "rom_best_vanilla.png")
    (dst / "report.txt").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"  -> {dst / 'rom.gif'}\n  -> {dst / 'rom_strip.png'}")
