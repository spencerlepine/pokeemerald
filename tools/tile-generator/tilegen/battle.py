"""Battle backgrounds (E1): graphics/battle_environment/<env>/{tiles.png, palette.pal, map.bin}.

Format (src/battle_bg.c): tiles go to BG char block 2, the tilemap (two 32x32 screen blocks, 4096 bytes)
to screen block 26 on BG3, and palette.pal (48 colours = 3 banks) to BG palettes 2-4. Tilemap entries are
u16: tile id (0-9), hflip (10), vflip (11), bank (12-15, so 2-4 here). The battle shows the top-left
240x160 of the first screen block (the second is used by the intro slide).
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
from PIL import Image

from . import gba, recolour

ENVS = ["tall_grass", "long_grass", "sand", "underwater", "water", "pond_water", "rock", "cave", "building", "sky", "stadium"]


@dataclass
class BattleEnv:
    name: str
    path: Path
    tiles: np.ndarray
    palette: list[tuple[int, int, int]]   # 48 colours
    tilemap: np.ndarray                   # (64, 32) u16? stored as 2 screens of 32x32

    @staticmethod
    def load(name: str, game: Path | None = None) -> "BattleEnv":
        game = game or gba.game_dir()
        p = game / "graphics/battle_environment" / name
        tiles = gba.load_tiles(p / "tiles.png")
        pal = gba.read_pal(p / "palette.pal")
        raw = np.frombuffer((p / "map.bin").read_bytes(), dtype="<u2")
        return BattleEnv(name, p, tiles, pal, raw.reshape(-1, 32, 32))

    def bank(self, b: int) -> list[tuple[int, int, int]]:
        i = (b - 2) * 16
        if 0 <= i < len(self.palette):
            out = list(self.palette[i:i + 16])
            return out + [(0, 0, 0)] * (16 - len(out))
        return [(40, 40, 48)] * 16          # outside the 3 banks: the text box area, hidden in battle

    def render(self, screen: int = 0, crop=(240, 160)) -> Image.Image:
        m = self.tilemap[screen]
        out = np.zeros((256, 256, 3), np.uint8)
        for ty in range(32):
            for tx in range(32):
                e = int(m[ty, tx])
                tid, hf, vf, b = e & 0x3FF, (e >> 10) & 1, (e >> 11) & 1, (e >> 12) & 0xF
                t = self.tiles[tid] if tid < len(self.tiles) else np.zeros((8, 8), np.uint8)
                if hf: t = t[:, ::-1]
                if vf: t = t[::-1, :]
                out[ty * 8:(ty + 1) * 8, tx * 8:(tx + 1) * 8] = np.array(self.bank(b), np.uint8)[t]
        im = Image.fromarray(out)
        return im.crop((0, 0) + crop) if crop else im

    def recoloured(self, rec: recolour.Recipe, log=None) -> "BattleEnv":
        pal = []
        rb = rec.for_battle()
        for b in range(len(self.palette) // 16):
            pal += recolour.recolour_bank(self.palette[b * 16:(b + 1) * 16], rb, f"battle:{self.name}:{b}", log)
        return BattleEnv(self.name, self.path, self.tiles, pal, self.tilemap)


def write(env: BattleEnv, out: Path) -> Path:
    """palette.pal (48 colours) plus unchanged tiles.png/map.bin copies, ready for the gate."""
    import shutil
    out = Path(out); out.mkdir(parents=True, exist_ok=True)
    txt = "JASC-PAL\n0100\n%d\n" % len(env.palette) + "\n".join(f"{r} {g} {b}" for r, g, b in env.palette) + "\n"
    (out / "palette.pal").write_text(txt)
    for f in ("tiles.png", "map.bin", "anim_tiles.png", "anim_map.bin"):
        if (env.path / f).exists():
            shutil.copy(env.path / f, out / f)
    return out
