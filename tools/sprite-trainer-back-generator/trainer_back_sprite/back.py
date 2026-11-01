"""Trainer back pics (kit `trainerback64x4`): lint, corpus and previews.

Format (pokeemerald `src/data/graphics/trainers.h`): a 64x256 indexed PNG, four 64x64 frames
stacked, converted with `INCGFX_U8(png, ".4bpp")` (uncompressed, 8192 bytes). The palette is
NOT in the PNG: `back_pic_tables.h` loads the front pic's palette (`gTrainerPalette_Brendan`
= graphics/trainers/palettes/brendan.pal, same for May and Wally; Steven's comes from his
front pic PNG). So front and back of one character share 16 colours, index for index.
Shown at centre (80, 80) in battle; frame 0 slides in, then the throw plays.

Previews:
- zoom.png    the four frames at 6x with a grid and row/column numbers (the LLM's editor view)
- throw.gif   the throw animation at the game's timing, on the battle background, 3x
- battle.png  frame 0 in a mock Emerald battle next to the vanilla pic it replaces, 2x and 1x
- pair.png    front pic and back pic side by side in their shared palette (needs a front)
- showcase.png  zoom + battle + pair, for the owner
"""
from __future__ import annotations

import json
import statistics as st
import struct
from pathlib import Path

from PIL import Image, ImageDraw

from . import palette as pal
from .metrics import frame_metrics, rgba_frame

TOOL = Path(__file__).resolve().parents[1]
CORPUS_FILE = TOOL / "corpus" / "back64.json"
KEYS = ("top", "height", "width", "area", "dark_outline", "orphans")
PLAYER_TOPLEFT = (48, 48)  # centre (80, 80), battle_controller_player.c
OPP_TOPLEFT = (144, 8)  # opponent front pic centre (176, 40)
VANILLA = ["brendan", "may", "wally", "steven", "brendan_rs", "may_rs"]


def read_strip(png: Path) -> tuple[list[list[list[int]]], list[tuple[int, int, int]]]:
    im = Image.open(png)
    if im.mode != "P" or im.width != 64 or im.height % 64:
        raise ValueError(f"{png}: not a 64-wide indexed strip")
    raw = (im.getpalette() or [])[:48]
    px = im.load()
    frames = [[[px[x, f * 64 + y] for x in range(64)] for y in range(64)] for f in range(im.height // 64)]
    return frames, [tuple(raw[i : i + 3]) for i in range(0, len(raw), 3)]


def vanilla_palette(emerald: Path, stem: str) -> list[tuple[int, int, int]]:
    p = emerald / "graphics/trainers/palettes" / f"{stem}.pal"
    if p.exists():
        return pal.load_jasc(p)
    return read_strip(emerald / "graphics/trainers/front_pics" / f"{stem}.png")[1]


def metrics(g, colours) -> dict:
    m = frame_metrics(g, colours)
    return {k: m[k] for k in KEYS if k in m}


def load_corpus() -> dict | None:
    return json.loads(CORPUS_FILE.read_text()) if CORPUS_FILE.exists() else None


def build_corpus(emerald: Path) -> dict:
    rows = {}
    for stem in VANILLA:
        f = emerald / "graphics/trainers/back_pics" / f"{stem}.png"
        if not f.exists():
            continue
        frames, _ = read_strip(f)
        cols = vanilla_palette(emerald, stem)
        for i, g in enumerate(frames[:4]):
            rows[f"{stem}:{i}"] = metrics(g, cols)

    def pct(vals, p):
        vals = sorted(vals)
        return vals[min(len(vals) - 1, max(0, round(p / 100 * (len(vals) - 1))))]

    out = {"count": len(rows), "p5": {}, "median": {}, "p95": {}, "frames": rows}
    for k in KEYS:
        vals = [r[k] for r in rows.values()]
        out["p5"][k], out["median"][k], out["p95"][k] = (round(v, 3) for v in (pct(vals, 5), st.median(vals), pct(vals, 95)))
    CORPUS_FILE.parent.mkdir(exist_ok=True)
    CORPUS_FILE.write_text(json.dumps(out, indent=1))
    return out


def lint(frames, colours, front_colours=None) -> tuple[list[str], list[str], list[dict]]:
    errors, warnings = [], []
    used = {v for g in frames for row in g for v in row}
    if len(used - {0}) > 15:
        errors.append(f"{len(used - {0})} colours used; 4bpp allows 15 + transparent")
    for i, c in enumerate(colours):
        if i and pal.gba15(c) != tuple(c):
            warnings.append(f"palette[{i}] {tuple(c)} is not a multiple of 8 per channel; the GBA shows {pal.gba15(c)}")
    for i in range(1, 16):
        for j in range(i + 1, 16):
            if i in used and j in used and pal.gba15(colours[i]) == pal.gba15(colours[j]):
                warnings.append(f"palette[{i}] and palette[{j}] are the same colour on the GBA")
    if front_colours is not None:
        diff = [i for i in range(16) if pal.gba15(colours[i]) != pal.gba15(tuple(front_colours[i]))]
        if diff:
            errors.append(f"palette differs from the front pic's at indices {diff}; front and back share one palette in game")
    corpus = load_corpus()
    ms = []
    for f, g in enumerate(frames):
        m = metrics(g, colours)
        ms.append(m)
        if m.get("area", 0) == 0:
            errors.append(f"frame {f} is empty")
            continue
        bottom = max(y for y, row in enumerate(g) for v in row if v)
        if bottom < 62:
            warnings.append(f"frame {f}: art ends on row {bottom}; vanilla back pics run off the frame bottom (row 63)")
        if corpus:
            for k, v in m.items():
                lo, hi = corpus["p5"][k], corpus["p95"][k]
                if not lo <= v <= hi:
                    warnings.append(f"frame {f}: style: {k} = {v} is outside Emerald's p5-p95 range [{lo}, {hi}]")
    return errors, warnings, ms


# ---- previews ------------------------------------------------------------------------------

def zoom(frames, colours, out: Path, z: int = 6) -> Image.Image:
    pad, lab = 22, 14
    n = len(frames)
    im = Image.new("RGB", (pad + n * (64 * z + 10), lab + 64 * z + 2), (40, 40, 48))
    d = ImageDraw.Draw(im)
    names = ["0 idle", "1 wind-up", "2 throw", "3 follow-through"]
    for f, g in enumerate(frames):
        x0 = pad + f * (64 * z + 10)
        fr = Image.new("RGB", (64, 64), (115, 197, 164))
        r = rgba_frame(g, colours)
        fr.paste(r, (0, 0), r)
        im.paste(fr.resize((64 * z, 64 * z), Image.NEAREST), (x0, lab))
        for i in range(0, 65, 8):
            d.line([(x0 + i * z, lab), (x0 + i * z, lab + 64 * z)], fill=(60, 110, 90))
            d.line([(x0, lab + i * z), (x0 + 64 * z, lab + i * z)], fill=(60, 110, 90))
        for i in range(0, 64, 8):
            d.text((x0 + i * z + 1, 1), str(i), fill=(160, 160, 170))
        d.text((x0 + 64 * z - 110, 1), names[f] if f < 4 else str(f), fill=(230, 230, 230))
    for i in range(0, 64, 8):
        d.text((2, lab + i * z + 1), str(i), fill=(160, 160, 170))
    im.save(out)
    return im


def _battle_bg(emerald: Path, env: str = "tall_grass") -> Image.Image:
    d = emerald / "graphics/battle_environment" / env
    tiles = Image.open(d / "tiles.png")
    tp = tiles.load()
    vals = list(map(int, (d / "palette.pal").read_text().split()[3:]))
    pals = [[tuple(vals[j * 3 : j * 3 + 3]) for j in range(i * 16, i * 16 + 16)] for i in range(len(vals) // 48)]
    m = (d / "map.bin").read_bytes()
    im = Image.new("RGB", (256, 256), pals[0][1])
    for i in range(1024):
        v = struct.unpack_from("<H", m, i * 2)[0]
        idx, hf, vf, pi = v & 0x3FF, v >> 10 & 1, v >> 11 & 1, v >> 12
        tx, ty = (idx % 16) * 8, (idx // 16) * 8
        for y in range(8):
            for x in range(8):
                c = tp[tx + x, ty + y] if ty + y < tiles.height else 0
                if c:
                    im.putpixel(((i % 32) * 8 + (7 - x if hf else x), (i // 32) * 8 + (7 - y if vf else y)), pals[max(pi - 2, 0)][c])
    return im.crop((0, 0, 240, 160))


def _text_box(im: Image.Image) -> None:
    d = ImageDraw.Draw(im)  # Emerald's battle text box (rows 112-159), drawn over the sprites
    d.rectangle([0, 112, 239, 159], fill=(40, 80, 104))
    d.rectangle([2, 114, 237, 157], outline=(248, 248, 248))
    d.rectangle([4, 116, 235, 155], fill=(40, 80, 104), outline=(208, 160, 64))


def _opponent(emerald: Path) -> Image.Image | None:
    p = emerald / "graphics/trainers/front_pics/youngster.png"
    if not p.exists():
        return None
    frames, cols = read_strip(p)
    return rgba_frame(frames[0], cols)


def battle_scene(g, colours, emerald: Path, bg: Image.Image | None = None) -> Image.Image:
    im = (bg or _battle_bg(emerald)).copy()
    opp = _opponent(emerald)
    if opp:
        im.paste(opp, OPP_TOPLEFT, opp)
    pic = rgba_frame(g, colours)
    im.paste(pic, PLAYER_TOPLEFT, pic)
    _text_box(im)
    return im


def battle(frames, colours, out: Path, emerald: Path, replaces: str | None) -> Image.Image:
    bg = _battle_bg(emerald)
    scenes = [("ours", battle_scene(frames[0], colours, emerald, bg))]
    if replaces and (emerald / replaces).exists():
        vf, _ = read_strip(emerald / replaces)
        scenes.append(("vanilla: " + Path(replaces).stem, battle_scene(vf[0], vanilla_palette(emerald, Path(replaces).stem), emerald, bg)))
    gap, lab = 8, 14
    W = gap + len(scenes) * (480 + gap) + 240 + gap
    im = Image.new("RGB", (W, lab + 320 + gap), (24, 24, 30))
    d = ImageDraw.Draw(im)
    x = gap
    for name, sc in scenes:
        d.text((x, 1), f"{name} (2x)", fill=(230, 230, 230))
        im.paste(sc.resize((480, 320), Image.NEAREST), (x, lab))
        x += 480 + gap
    d.text((x, 1), "ours (1x)", fill=(230, 230, 230))
    im.paste(scenes[0][1], (x, lab))
    im.save(out)
    return im


def throw_gif(frames, colours, out: Path, emerald: Path | None, kit_anim, z: int = 3) -> None:
    """The throw at the game's timing (60 ticks a second), cropped to the player's corner."""
    bg = _battle_bg(emerald) if emerald else None
    imgs, durs = [], []
    for f, ticks in list(kit_anim) + [(0, 40)]:
        if bg is not None:
            sc = bg.copy()
            pic = rgba_frame(frames[f], colours)
            sc.paste(pic, PLAYER_TOPLEFT, pic)
            _text_box(sc)
            sc = sc.crop((16, 32, 144, 128))
        else:
            sc = Image.new("RGB", (64, 64), (115, 197, 164))
            pic = rgba_frame(frames[f], colours)
            sc.paste(pic, (0, 0), pic)
        imgs.append(sc.resize((sc.width * z, sc.height * z), Image.NEAREST))
        durs.append(round(ticks * 1000 / 60))
    imgs[0].save(out, save_all=True, append_images=imgs[1:], duration=durs, loop=0)


def pair(front_g, front_cols, frames, colours, out: Path, z: int = 4) -> Image.Image:
    """Front pic and back frames side by side, each in its own stored palette (they must match)."""
    n = 1 + len(frames)
    im = Image.new("RGB", (n * (64 * z + 8) + 8, 64 * z + 24), (24, 24, 30))
    d = ImageDraw.Draw(im)
    cells = [("front", front_g, front_cols)] + [(f"back {i}", g, colours) for i, g in enumerate(frames)]
    for i, (name, g, cols) in enumerate(cells):
        x = 8 + i * (64 * z + 8)
        bg = Image.new("RGB", (64, 64), (115, 197, 164))
        r = rgba_frame(g, cols)
        bg.paste(r, (0, 0), r)
        im.paste(bg.resize((64 * z, 64 * z), Image.NEAREST), (x, 18))
        d.text((x, 3), name, fill=(230, 230, 230))
    im.save(out)
    return im


def showcase(out_dir: Path) -> None:
    parts = [Image.open(out_dir / n) for n in ("zoom.png", "battle.png", "pair.png") if (out_dir / n).exists()]
    W = max(p.width for p in parts)
    H = sum(p.height for p in parts) + 8 * (len(parts) - 1)
    im = Image.new("RGB", (W, H), (24, 24, 30))
    y = 0
    for p in parts:
        im.paste(p, (0, y))
        y += p.height + 8
    im.save(out_dir / "showcase.png")


def review(items: list, out: Path, emerald: Path | None) -> None:
    """Owner review sheet: per character one row, front pic then the four back frames (4x),
    then frame 0 in battle (2x crop)."""
    z = 3
    cw = 64 * z
    rows = []
    bg = _battle_bg(emerald) if emerald else None
    for name, front, frames, colours in items:
        cells = []
        if front:
            cells.append(("front", front[0], front[1]))
        cells += [(n, g, colours) for n, g in zip(("idle", "wind-up", "throw", "follow"), frames)]
        rows.append((name, cells, frames, colours))
    W = 8 + 5 * (cw + 6) + (2 * 128 + 8 if bg is not None else 0)
    H = 8 + len(rows) * (cw + 22)
    im = Image.new("RGB", (W, H), (24, 24, 30))
    d = ImageDraw.Draw(im)
    for r, (name, cells, frames, colours) in enumerate(rows):
        y = 8 + r * (cw + 22)
        d.text((8, y), name, fill=(240, 240, 240))
        for i, (lab, g, cols) in enumerate(cells):
            x = 8 + i * (cw + 6)
            c = Image.new("RGB", (64, 64), (115, 197, 164))
            p = rgba_frame(g, cols)
            c.paste(p, (0, 0), p)
            im.paste(c.resize((cw, cw), Image.NEAREST), (x, y + 14))
            d.text((x + cw - 50, y), lab, fill=(150, 150, 160))
        if bg is not None:
            sc = battle_scene(frames[0], colours, emerald, bg).crop((16, 16, 144, 112))
            im.paste(sc.resize((256, 192), Image.NEAREST).crop((0, 0, 256, cw)), (8 + 5 * (cw + 6), y + 14))
    im.save(out)
