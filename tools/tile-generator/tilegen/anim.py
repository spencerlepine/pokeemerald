"""Stage 6: tileset animations (D2). Reads src/tileset_anims.c and plays the frames into a tileset pair.

An animation is a list of frame sheets (`anim/<name>/<n>.png`, 4bpp, 8 px wide or more) that the game copies
over a fixed range of tile ids every 16 game frames (`TilesetAnim_<Tileset>`: one queue per `timer % 16`
slot, the frame index is `timer / 16`). Frames are index maps, so a palette recolour animates for free; a
new animation keeps the destination tile id, tile count and frame count of the one it replaces.

Only the direct form is parsed (General water/edges/waterfall/flower, Lavaridge and Cave lava, ...):
    AppendTilesetAnimToBuffer(gTilesetAnims_X[i], (u16 *)(BG_VRAM + TILE_OFFSET_4BPP(DEST)), N * TILE_SIZE_4BPP)
Animations that pick a destination from a table (Mauville flowers, Pacifidlog currents) are listed as skipped.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from PIL import Image

from . import gba

STEP = 16   # game frames per animation step


@dataclass
class Anim:
    name: str              # e.g. "General_Water"
    dest: int              # first tile id in the pair's tile space (secondary ids start at 512)
    count: int             # tiles per frame
    frames: list[Path]     # one png per step, in play order (frames may repeat)

    def frame_tiles(self, i: int) -> np.ndarray:
        return gba.load_tiles(self.frames[i % len(self.frames)])[: self.count]


def parse(game: Path | None = None) -> tuple[list[Anim], list[str]]:
    game = game or gba.game_dir()
    src = (game / "src/tileset_anims.c").read_text()
    pngs = dict(re.findall(r"(gTilesetAnims_\w+?)\[\]\s*=\s*INCGFX_U16\(\"([^\"]+\.png)\"", src))
    lists = {m.group(1): re.findall(r"gTilesetAnims_\w+", m.group(2))
             for m in re.finditer(r"const u16 \*const (gTilesetAnims_\w+)\[\]\s*=\s*\{(.*?)\};", src, re.S)}
    out, skipped = [], []
    for m in re.finditer(r"AppendTilesetAnimToBuffer\((gTilesetAnims_\w+)\[\w+\],\s*\(u16 \*\)\(BG_VRAM \+ "
                         r"TILE_OFFSET_4BPP\(([^)]*)\)\),\s*(\d+) \* TILE_SIZE_4BPP\)", src):
        arr, dest, n = m.group(1), m.group(2).replace(" ", ""), int(m.group(3))
        d = dest.replace("NUM_TILES_IN_PRIMARY", str(gba.NUM_TILES_IN_PRIMARY))
        if not re.fullmatch(r"[\d+]+", d) or arr not in lists:
            skipped.append(arr); continue
        frames = [game / pngs[f] for f in lists[arr] if f in pngs]
        out.append(Anim(arr.removeprefix("gTilesetAnims_"), eval(d), n, frames))
    return out, skipped


def for_pair(pair: gba.TilesetPair, anims: list[Anim]) -> list[Anim]:
    """Animations the pair plays: the name prefix is the tileset (General_Water -> general, Lavaridge_Cave_Lava ->
    lavaridge, even though those frames live in secondary/cave)."""
    norm = lambda s: s.replace("_", "").lower()
    names = {norm(pair.primary.name), norm(pair.secondary.name)}
    return [a for a in anims if a.frames and norm(a.name.split("_")[0]) in names]


def render_frames(layout: gba.Layout, pair: gba.TilesetPair, steps: int = 8, crop=None) -> list[Image.Image]:
    """The layout once per animation step, the pair's animations played into its tiles."""
    anims = for_pair(pair, parse()[0])
    p0, s0 = pair.primary.tiles.copy(), pair.secondary.tiles.copy()
    frames = []
    for i in range(steps):
        p, s = p0.copy(), s0.copy()
        for a in anims:
            t = a.frame_tiles(i)
            base, sheet = (a.dest, p) if a.dest < gba.NUM_TILES_IN_PRIMARY else (a.dest - gba.NUM_TILES_IN_PRIMARY, s)
            sheet[base: base + len(t)] = t
        pair.primary.tiles, pair.secondary.tiles = p, s
        im = gba.render_layout(layout, pair=pair)
        frames.append(im.crop(crop) if crop else im)
    pair.primary.tiles, pair.secondary.tiles = p0, s0
    return frames


def save_gif(frames: list[Image.Image], path: Path, zoom: int = 2, ms: int = STEP * 1000 // 60) -> None:
    fr = [f.resize((f.width * zoom, f.height * zoom), Image.NEAREST) for f in frames]
    fr[0].save(path, save_all=True, append_images=fr[1:], duration=ms, loop=0, disposal=1)
