"""Previews: zoomed sheets, frame playback, and mockups over a real battle or overworld scene.

The battle scene is rebuilt from the game's own data (battle environment tiles + tilemap + palette,
creature pics at sBattlerCoords with their y offsets), at 240x160, so an effect is judged at the size
and against the colours it will really have. Motion presets replay roughly what the animation's
callback does (a projectile from attacker to target, a burst at the target, a stream of orbs...);
they are for judging the art, the ROM check (`romtest`) is the final word.
"""
from __future__ import annotations

import math
import re
import struct
import sys
from functools import lru_cache
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from .game import GAME, TOOLS, WIKI_ART
from .pal import load_palette_file
from .sheet import read_indexed, split_frames, to_rgba

BG_RGB = (24, 24, 30)
ZOOM = 3


def font(size=10):
    for p in ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"):
        if Path(p).exists():
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def zoom(im: Image.Image, z: int) -> Image.Image:
    return im.resize((im.width * z, im.height * z), Image.NEAREST)


# -- battle scene ------------------------------------------------------------------------------


@lru_cache(maxsize=8)
def battle_bg(env: str = "tall_grass") -> Image.Image:
    d = GAME / "graphics/battle_environment" / env
    tiles, _ = read_indexed(d / "tiles.png")
    pal = load_palette_file(d / "palette.pal") if False else None
    words = (d / "palette.pal").read_text().split()
    n = int(words[2])
    vals = list(map(int, words[3:3 + 3 * n]))
    cols = [tuple(vals[i:i + 3]) for i in range(0, 3 * n, 3)]
    m = (d / "map.bin").read_bytes()
    tw = tiles.shape[1] // 8
    out = np.zeros((256, 512, 3), np.uint8)
    for i in range(len(m) // 2):
        e = struct.unpack_from("<H", m, i * 2)[0]
        sb, j = divmod(i, 1024)
        cx, cy = sb * 32 + j % 32, j // 32
        ti, hf, vf, pb = e & 0x3FF, (e >> 10) & 1, (e >> 11) & 1, e >> 12
        ty, tx = divmod(ti, tw)
        t = tiles[ty * 8:ty * 8 + 8, tx * 8:tx * 8 + 8]
        if t.shape != (8, 8):
            t = np.zeros((8, 8), np.uint8)
        if hf:
            t = t[:, ::-1]
        if vf:
            t = t[::-1, :]
        bank = ((pb - 2) % max(1, len(cols) // 16)) * 16
        lut = np.array([cols[min(bank + k, len(cols) - 1)] if k else cols[0] for k in range(16)], np.uint8)
        out[cy * 8:cy * 8 + 8, cx * 8:cx * 8 + 8] = lut[t]
    im = Image.fromarray(out[:160, :240], "RGB").convert("RGBA")
    # text box area: a plain console-blue box so the scene reads like a battle
    dr = ImageDraw.Draw(im)
    dr.rectangle((0, 112, 239, 159), fill=(16, 24, 40, 255))
    dr.rectangle((2, 114, 237, 157), outline=(88, 104, 136, 255))
    return im


def _coords(species: str, back: bool) -> int:
    f = "back_pic_coordinates.h" if back else "front_pic_coordinates.h"
    t = (GAME / "src/data/pokemon_graphics" / f).read_text()
    m = re.search(r'\[SPECIES_' + species.upper() + r'\]\s*=\s*\{[^}]*\.y_offset\s*=\s*(\d+)', t)
    return int(m.group(1)) if m else 0


def _elevation(species: str) -> int:
    t = (GAME / "src/data/pokemon_graphics/enemy_mon_elevation.h").read_text()
    m = re.search(r'\[SPECIES_' + species.upper() + r'\]\s*=\s*(\d+)', t)
    return int(m.group(1)) if m else 0


@lru_cache(maxsize=16)
def mon_pic(species: str, back: bool) -> Image.Image:
    for root in (WIKI_ART / "graphics/pokemon", GAME / "graphics/pokemon"):
        d = root / species
        p = d / ("back.png" if back else "front.png")
        if p.exists():
            pix, cols = read_indexed(p)
            if (d / "normal.pal").exists():
                cols = load_palette_file(d / "normal.pal")
            return to_rgba(pix[:64, :64], cols)
    return Image.new("RGBA", (64, 64))


BATTLERS = {"attacker": (72, 80), "target": (176, 40)}


class Scene:
    def __init__(self, env="tall_grass", attacker="piloswine", target="porygon"):
        self.env, self.attacker, self.target = env, attacker, target
        self.bg = battle_bg(env)
        ay = 80 + _coords(attacker, True)
        ty = 40 + _coords(target, False) - _elevation(target)
        # anim coords of the mons' centres (what GetBattlerSpriteCoord returns, roughly)
        self.pos = {"attacker": (72, ay - 16 + 8), "target": (176, ty - 16 + 8)}
        self.pics = {"attacker": (mon_pic(attacker, True), (72 - 32, ay - 32)),
                     "target": (mon_pic(target, False), (176 - 32, ty - 32))}

    def base(self, dim: float = 0.0) -> Image.Image:
        """dim: blend the battle background toward black (scripts do this, e.g. HYPER BEAM's
        simple_palette_blend F_PAL_BG ... 16 = fully black)."""
        im = self.bg.copy()
        if dim:
            im = Image.blend(im, Image.new("RGBA", im.size, (0, 0, 0, 255)), min(1.0, dim))
        for pic, (x, y) in self.pics.values():
            im.alpha_composite(pic, (x, y))
        return im


# -- sprites and motion ------------------------------------------------------------------------


class SheetFrames:
    """The frames of a sheet as RGBA images, plus the anim sequence the game plays."""

    def __init__(self, png: Path, frame: tuple[int, int], mw=1, mh=1, pal_override: list | None = None):
        pix, cols = read_indexed(png)
        if pal_override:
            cols = pal_override
        self.cols = cols
        self.frames_pix = split_frames(pix, frame[0], frame[1], mw, mh)
        self.frames = [to_rgba(f, cols) for f in self.frames_pix]
        self.frame = frame

    def get(self, k: int, hflip=False, vflip=False, rot: float = 0.0, scale: float = 1.0) -> Image.Image:
        im = self.frames[k % len(self.frames)]
        if hflip:
            im = im.transpose(Image.FLIP_LEFT_RIGHT)
        if vflip:
            im = im.transpose(Image.FLIP_TOP_BOTTOM)
        if scale != 1.0:
            im = im.resize((max(1, round(im.width * scale)), max(1, round(im.height * scale))), Image.NEAREST)
        if rot:
            im = im.rotate(rot, resample=Image.NEAREST, expand=True)
        return im


def anim_sequence(cmds: list[dict], per: int, total: int = 600) -> list[tuple[int, bool, bool]]:
    """ANIMCMD list -> per-game-frame (frame_index, hflip, vflip) for `total` frames."""
    if not cmds:
        return [(0, False, False)] * total
    out, pc, guard = [], 0, 0
    while len(out) < total and guard < 10000:
        guard += 1
        if pc >= len(cmds):
            break
        c = cmds[pc]
        if "tile" in c:
            out += [(c["tile"] // per, c["hflip"], c["vflip"])] * max(1, c["dur"])
            pc += 1
        elif "jump" in c:
            pc = c["jump"]
        else:
            break
    if not out:
        out = [(0, False, False)]
    while len(out) < total:
        out.append(out[-1])
    return out[:total]


def _blit(im: Image.Image, spr: Image.Image, cx: float, cy: float):
    im.alpha_composite(spr, (int(round(cx - spr.width / 2)), int(round(cy - spr.height / 2))))


def simulate(scene: Scene, sf: SheetFrames, motion: dict, seq: list, length: int) -> list[Image.Image]:
    """Render `length` game frames of a motion preset. Returns RGBA frames at 1x."""
    kind = motion.get("kind", "projectile")
    a = scene.pos[motion.get("from", "attacker")]
    b = scene.pos[motion.get("to", "target")]
    off = motion.get("offset", [0, 0])
    a = (a[0] + off[0], a[1] + off[1])
    b = (b[0] + motion.get("to_offset", [0, 0])[0], b[1] + motion.get("to_offset", [0, 0])[1])
    dur = int(motion.get("frames", 30))
    spin = float(motion.get("spin", 0))
    out = []
    for f in range(length):
        im = scene.base(float(motion.get("dim", 0.0)))
        sprites = []
        if kind == "projectile":
            count, stagger = int(motion.get("count", 1)), int(motion.get("stagger", 6))
            for k in range(count):
                lf = f - k * stagger
                if 0 <= lf <= dur:
                    u = lf / dur
                    x = a[0] + (b[0] - a[0]) * u
                    y = a[1] + (b[1] - a[1]) * u - motion.get("arc", 0) * math.sin(math.pi * u)
                    sprites.append((x, y, lf))
        elif kind == "at_target" or kind == "at_attacker":
            p = b if kind == "at_target" else a
            if f <= dur:
                sprites.append((p[0], p[1], f))
        elif kind == "stream":
            every, life = int(motion.get("every", 2)), dur
            wob = float(motion.get("wobble", 0))
            for s in range(0, length, every):
                lf = f - s
                if 0 <= lf <= life and s <= motion.get("spawn_until", length):
                    u = lf / life
                    x = a[0] + (b[0] - a[0]) * u
                    y = a[1] + (b[1] - a[1]) * u + wob * math.sin(s * 1.7)
                    sprites.append((x, y, lf))
        elif kind == "burst":
            count, radius = int(motion.get("count", 8)), float(motion.get("radius", 30))
            for k in range(count):
                ang = 2 * math.pi * k / count
                u = min(1.0, f / max(dur, 1))
                if f <= dur + int(motion.get("hold", 0)):
                    sprites.append((b[0] + math.cos(ang) * radius * u, b[1] + math.sin(ang) * radius * u, f))
        elif kind == "still":
            sprites.append((b[0], b[1], f))
        for x, y, lf in sprites:
            k, hf, vf = seq[min(lf, len(seq) - 1)] if motion.get("animate", True) else seq[0]
            if "frame" in motion:
                k = int(motion["frame"])
            spr = sf.get(k, hf, vf, rot=spin * lf, scale=float(motion.get("scale", 1.0)))
            _blit(im, spr, x, y)
        out.append(im)
    return out


def save_gif(frames: list[Image.Image], path: Path, game_frames_per_gif_frame: int = 2, z: int = 2):
    imgs = []
    for k in range(0, len(frames), game_frames_per_gif_frame):
        im = zoom(frames[k].convert("RGB"), z)
        imgs.append(im.convert("P", palette=Image.ADAPTIVE, colors=255, dither=Image.NONE))
    if not imgs:
        return
    imgs[0].save(path, save_all=True, append_images=imgs[1:], duration=int(1000 * game_frames_per_gif_frame / 60),
                 loop=0, disposal=1, optimize=False)


def labelled(panels: list[tuple[str, Image.Image]], gap=8, bg=BG_RGB) -> Image.Image:
    f = font(11)
    w = sum(p.width for _, p in panels) + gap * (len(panels) + 1)
    h = max(p.height for _, p in panels) + 22 + gap
    im = Image.new("RGB", (w, h), bg)
    d = ImageDraw.Draw(im)
    x = gap
    for t, p in panels:
        d.text((x, 4), t, fill=(230, 230, 230), font=f)
        im.paste(p.convert("RGB"), (x, 20))
        x += p.width + gap
    return im


def sheet_card(png: Path, frame, mw=1, mh=1, z=6, title="", pal_override=None, used=None) -> Image.Image:
    """A sheet at zoom with its frame grid, slot numbers (used slots marked) and palette swatches."""
    pix, cols = read_indexed(png)
    if pal_override:
        cols = pal_override
    frames = split_frames(pix, frame[0], frame[1], mw, mh)
    f = font(10)
    fw, fh = frame[0] * z, frame[1] * z
    per_row = max(1, min(len(frames), 8 if fw <= 96 else 4))
    rows = math.ceil(len(frames) / per_row)
    W = max(per_row * (fw + 6) + 6, 16 * 14 + 12)
    H = 20 + rows * (fh + 18) + 30
    im = Image.new("RGB", (W, H), BG_RGB)
    d = ImageDraw.Draw(im)
    d.text((6, 4), title, fill=(235, 235, 235), font=f)
    checker = Image.new("RGB", (fw, fh), (40, 42, 52))
    cd = ImageDraw.Draw(checker)
    for yy in range(0, fh, z * 2):
        for xx in range(0, fw, z * 2):
            if (xx // (z * 2) + yy // (z * 2)) % 2 == 0:
                cd.rectangle((xx, yy, xx + z * 2 - 1, yy + z * 2 - 1), fill=(52, 54, 66))
    for k, fr in enumerate(frames):
        r, c = divmod(k, per_row)
        x, y = 6 + c * (fw + 6), 20 + r * (fh + 18)
        cell = checker.copy()
        rgba = zoom(to_rgba(fr, cols), z)
        cell.paste(rgba, (0, 0), rgba)
        im.paste(cell, (x, y))
        mark = "*" if used is None or k in used else ""
        d.text((x, y + fh + 2), f"{k}{mark}", fill=(200, 200, 120) if mark else (120, 120, 120), font=f)
    y = H - 24
    usedidx = sorted({int(v) for v in np.unique(pix)})
    for i in range(16):
        x = 6 + i * 14
        d.rectangle((x, y, x + 12, y + 12), fill=tuple(cols[i][:3]) if i < len(cols) else (0, 0, 0),
                    outline=(255, 255, 255) if i in usedidx else (60, 60, 60))
    return im


# -- overworld scene -------------------------------------------------------------------------


@lru_cache(maxsize=4)
def overworld_bg(layout: str = "LAYOUT_LITTLEROOT_TOWN", cx: int = 10, cy: int = 9) -> Image.Image:
    """A 240x160 crop of a vanilla map, rendered by tile-generator's map renderer."""
    tg = TOOLS / "tile-generator"
    if str(tg) not in sys.path:
        sys.path.insert(0, str(tg))
    try:
        from tilegen import gba as tgba   # type: ignore
        lay = tgba.layouts(GAME)
        key = layout if layout in lay else next((k for k in lay if layout.lower() in k.lower()), None)
        full = tgba.render_layout(lay[key], GAME).convert("RGBA")
        x0 = max(0, min(full.width - 240, cx * 16 + 8 - 120))
        y0 = max(0, min(full.height - 160, cy * 16 - 80))
        return full.crop((x0, y0, x0 + 240, y0 + 160))
    except Exception:   # noqa: BLE001 - fall back to a flat field
        return Image.new("RGBA", (240, 160), (120, 184, 112, 255))


def player_walker(gender: str = "boy") -> Image.Image:
    name = "brendan" if gender == "boy" else "may"
    for root in (WIKI_ART, GAME):
        p = root / f"graphics/object_events/pics/people/{name}/walking.png"
        if p.exists():
            pix, _ = read_indexed(p)
            cols = load_palette_file(GAME / f"graphics/object_events/palettes/{name}.pal")
            return to_rgba(pix[:32, :16], cols)
    return Image.new("RGBA", (16, 32))
