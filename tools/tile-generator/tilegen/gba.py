"""Read and render pokeemerald tilesets, metatiles and map layouts.

Formats (from game/include/fieldmap.h and global.fieldmap.h):

- tiles.png: indexed PNG, 128 px wide, 8x8 tiles in row-major order. The PNG's own palette is
  only a preview; in the game every tile is drawn with the 16-colour bank its metatile names.
- palettes/NN.pal: JASC-PAL, 16 entries. Banks 0-5 come from the primary tileset, 6-12 from the
  secondary, 13-15 belong to the UI.
- metatiles.bin: 8 u16 per metatile = 2 layers x 4 tiles (TL, TR, BL, BR). u16 bits 0-9 tile id
  (secondary tiles start at NUM_TILES_IN_PRIMARY = 512), bit 10 hflip, bit 11 vflip, bits 12-15 bank.
- metatile_attributes.bin: u16 per metatile. bits 0-7 behaviour, bits 12-15 layer type
  (0 NORMAL: middle+top, 1 COVERED: bottom+middle, 2 SPLIT: bottom+top).
- layouts/<name>/map.bin: u16 per cell, bits 0-9 metatile id (secondary metatiles start at
  NUM_METATILES_IN_PRIMARY = 512), bits 10-11 collision, bits 12-15 elevation.
"""
from __future__ import annotations

import json
import os
import struct
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

import numpy as np
from PIL import Image

NUM_TILES_IN_PRIMARY = 512
NUM_METATILES_IN_PRIMARY = 512
NUM_PALS_IN_PRIMARY = 6
NUM_PALS_TOTAL = 13  # 13-15 are the UI's
TILE = 8
METATILE = 16

LAYER_NORMAL, LAYER_COVERED, LAYER_SPLIT = 0, 1, 2
LAYER_NAMES = {0: "normal", 1: "covered", 2: "split"}


def game_dir() -> Path:
    env = os.environ.get("EMERALD_DIR")
    if env:
        return Path(env)
    return Path(__file__).resolve().parents[3] / "game"


# ----------------------------------------------------------------------------- palettes

def read_pal(path: Path) -> list[tuple[int, int, int]]:
    lines = Path(path).read_text().splitlines()
    assert lines[0].strip() == "JASC-PAL", path
    n = int(lines[2])
    out = []
    for ln in lines[3:3 + n]:
        r, g, b = (int(v) for v in ln.split())
        out.append((r, g, b))
    return out


def write_pal(path: Path, colours: Iterable[tuple[int, int, int]]) -> None:
    colours = list(colours)
    assert len(colours) == 16
    txt = "JASC-PAL\n0100\n16\n" + "\n".join(f"{r} {g} {b}" for r, g, b in colours) + "\n"
    Path(path).write_text(txt)


def gba_snap(c: tuple[int, int, int]) -> tuple[int, int, int]:
    return tuple((v >> 3) << 3 for v in c)  # type: ignore[return-value]


# ----------------------------------------------------------------------------- tiles

def load_tiles(png: Path) -> np.ndarray:
    """Return (n_tiles, 8, 8) uint8 array of palette indices."""
    im = Image.open(png)
    if im.mode != "P":
        raise ValueError(f"{png}: expected an indexed PNG, got {im.mode}")
    a = np.array(im, dtype=np.uint8)
    h, w = a.shape
    assert w % TILE == 0 and h % TILE == 0, (png, a.shape)
    cols, rows = w // TILE, h // TILE
    tiles = a.reshape(rows, TILE, cols, TILE).transpose(0, 2, 1, 3).reshape(rows * cols, TILE, TILE)
    return tiles


def tiles_to_image(tiles: np.ndarray, width_tiles: int = 16) -> np.ndarray:
    n = len(tiles)
    rows = (n + width_tiles - 1) // width_tiles
    pad = rows * width_tiles - n
    if pad:
        tiles = np.concatenate([tiles, np.zeros((pad, TILE, TILE), np.uint8)])
    return tiles.reshape(rows, width_tiles, TILE, TILE).transpose(0, 2, 1, 3).reshape(rows * TILE, width_tiles * TILE)


# ----------------------------------------------------------------------------- tilesets

@dataclass
class Tileset:
    name: str            # e.g. "general" / "petalburg"
    path: Path
    secondary: bool
    tiles: np.ndarray    # (n, 8, 8) indices
    palettes: list[list[tuple[int, int, int]]]  # 16 banks of 16 colours (only 0-5 or 6-12 meaningful)
    metatiles: np.ndarray    # (n_meta, 2, 4) u16 raw entries
    attributes: np.ndarray   # (n_meta,) u16

    @property
    def n_metatiles(self) -> int:
        return len(self.metatiles)

    def layer_type(self, meta_id: int) -> int:
        return (int(self.attributes[meta_id]) >> 12) & 0xF

    def behaviour(self, meta_id: int) -> int:
        return int(self.attributes[meta_id]) & 0xFF

    @staticmethod
    def load(path: Path, secondary: bool, name: str | None = None) -> "Tileset":
        path = Path(path)
        tiles = load_tiles(path / "tiles.png")
        pals = [read_pal(path / "palettes" / f"{i:02d}.pal") for i in range(16)]
        raw = (path / "metatiles.bin").read_bytes()
        mt = np.frombuffer(raw, dtype="<u2").reshape(-1, 2, 4)
        attrs = np.frombuffer((path / "metatile_attributes.bin").read_bytes(), dtype="<u2")
        return Tileset(name or path.name, path, secondary, tiles, pals, mt, attrs)


# C header name -> data folder, from game/src/data/tilesets/graphics.h ("gTilesetTiles_X" -> path)
_HEADER_CACHE: dict[str, Path] | None = None


def tileset_folders(game: Path | None = None) -> dict[str, Path]:
    """Map 'gTileset_Petalburg' -> game/data/tilesets/secondary/petalburg."""
    global _HEADER_CACHE
    if _HEADER_CACHE is not None:
        return _HEADER_CACHE
    game = game or game_dir()
    gfx = (game / "src/data/tilesets/graphics.h").read_text() + (game / "src/graphics.c").read_text()
    hdr = (game / "src/data/tilesets/headers.h").read_text()
    import re
    tilepaths = dict(re.findall(r"gTilesetTiles_(\w+)\[\] = INCGFX_U32\(\"(data/tilesets/[^\"]+)/tiles\.png\"", gfx))
    out: dict[str, Path] = {}
    for m in re.finditer(r"const struct Tileset gTileset_(\w+) =\s*\{(.*?)\};", hdr, re.S):
        name, body = m.group(1), m.group(2)
        t = re.search(r"\.tiles = gTilesetTiles_(\w+)", body)
        if t and t.group(1) in tilepaths:
            out["gTileset_" + name] = game / tilepaths[t.group(1)]
    _HEADER_CACHE = out
    return out


def load_tileset_by_header(header: str, game: Path | None = None) -> Tileset:
    game = game or game_dir()
    folder = tileset_folders(game)[header]
    return Tileset.load(folder, secondary="/secondary/" in folder.as_posix(), name=folder.name)


# ----------------------------------------------------------------------------- rendering

@dataclass
class TilesetPair:
    primary: Tileset
    secondary: Tileset

    @property
    def tiles(self) -> np.ndarray:
        p = self.primary.tiles
        if len(p) < NUM_TILES_IN_PRIMARY:
            p = np.concatenate([p, np.zeros((NUM_TILES_IN_PRIMARY - len(p), TILE, TILE), np.uint8)])
        return np.concatenate([p[:NUM_TILES_IN_PRIMARY], self.secondary.tiles])

    @property
    def palettes(self) -> list[list[tuple[int, int, int]]]:
        return [self.primary.palettes[i] if i < NUM_PALS_IN_PRIMARY else self.secondary.palettes[i] for i in range(16)]

    def metatile(self, meta_id: int) -> tuple[Tileset, int]:
        if meta_id < NUM_METATILES_IN_PRIMARY:
            return self.primary, meta_id
        return self.secondary, meta_id - NUM_METATILES_IN_PRIMARY

    def render_tile(self, entry: int) -> tuple[np.ndarray, np.ndarray]:
        """Return (rgb 8x8x3 uint8, alpha 8x8 bool) for one u16 metatile entry."""
        tiles = self.tiles
        tid = entry & 0x3FF
        hflip = (entry >> 10) & 1
        vflip = (entry >> 11) & 1
        bank = (entry >> 12) & 0xF
        t = tiles[tid] if tid < len(tiles) else np.zeros((TILE, TILE), np.uint8)
        if hflip:
            t = t[:, ::-1]
        if vflip:
            t = t[::-1, :]
        pal = np.array(self.palettes[bank], dtype=np.uint8)
        rgb = pal[t]
        alpha = t != 0
        return rgb, alpha

    def render_metatile(self, meta_id: int, backdrop: tuple[int, int, int] | None = None) -> np.ndarray:
        """16x16x4 RGBA; the two layers composited bottom then top."""
        ts, local = self.metatile(meta_id)
        if local >= ts.n_metatiles:
            return np.zeros((METATILE, METATILE, 4), np.uint8)
        out = np.zeros((METATILE, METATILE, 4), np.uint8)
        if backdrop is not None:
            out[..., :3] = backdrop
            out[..., 3] = 255
        for layer in range(2):
            for i in range(4):
                rgb, a = self.render_tile(int(ts.metatiles[local, layer, i]))
                y, x = (i // 2) * TILE, (i % 2) * TILE
                sub = out[y:y + TILE, x:x + TILE]
                sub[a, :3] = rgb[a]
                sub[a, 3] = 255
        return out

    def render_metatile_sheet(self, which: str = "secondary", cols: int = 8, backdrop=None) -> Image.Image:
        ts = self.secondary if which == "secondary" else self.primary
        base = NUM_METATILES_IN_PRIMARY if which == "secondary" else 0
        n = ts.n_metatiles
        rows = (n + cols - 1) // cols
        sheet = np.zeros((rows * METATILE, cols * METATILE, 4), np.uint8)
        for i in range(n):
            r, c = divmod(i, cols)
            sheet[r * METATILE:(r + 1) * METATILE, c * METATILE:(c + 1) * METATILE] = self.render_metatile(base + i, backdrop)
        return Image.fromarray(sheet, "RGBA")


@dataclass
class Layout:
    id: str
    name: str
    width: int
    height: int
    primary: str
    secondary: str
    map_bin: Path
    border_bin: Path
    replace: dict | None = None     # metatile id -> id, applied on read (recipe `layout_edits`)

    def cells(self) -> np.ndarray:
        raw = np.frombuffer(self.map_bin.read_bytes(), dtype="<u2").reshape(self.height, self.width).copy()
        for a, b in (self.replace or {}).items():
            hit = (raw & 0x3FF) == int(a)
            raw[hit] = (raw[hit] & ~np.uint16(0x3FF)) | np.uint16(int(b))   # keeps collision/elevation bits
        return raw

    def edited(self, replace: dict) -> "Layout":
        import dataclasses
        return dataclasses.replace(self, replace=replace)


def layouts(game: Path | None = None) -> dict[str, Layout]:
    game = game or game_dir()
    data = json.loads((game / "data/layouts/layouts.json").read_text())["layouts"]
    out = {}
    for l in data:
        out[l["name"]] = Layout(l["id"], l["name"], l["width"], l["height"], l["primary_tileset"], l["secondary_tileset"],
                                game / l["blockdata_filepath"], game / l["border_filepath"])
        out[l["id"]] = out[l["name"]]
    return out


def render_layout(layout: Layout, game: Path | None = None, pair: TilesetPair | None = None) -> Image.Image:
    game = game or game_dir()
    if pair is None:
        pair = TilesetPair(load_tileset_by_header(layout.primary, game), load_tileset_by_header(layout.secondary, game))
    cells = layout.cells()
    H, W = cells.shape
    out = np.zeros((H * METATILE, W * METATILE, 3), np.uint8)
    cache: dict[int, np.ndarray] = {}
    for y in range(H):
        for x in range(W):
            mid = int(cells[y, x]) & 0x3FF
            if mid not in cache:
                cache[mid] = pair.render_metatile(mid, backdrop=(0, 0, 0))
            out[y * METATILE:(y + 1) * METATILE, x * METATILE:(x + 1) * METATILE] = cache[mid][..., :3]
    return Image.fromarray(out, "RGB")


# ----------------------------------------------------------------------------- analysis helpers

def metatile_banks(ts: Tileset) -> dict[int, set[int]]:
    """Which palette banks each metatile touches."""
    out = {}
    for i in range(ts.n_metatiles):
        banks = set()
        for e in ts.metatiles[i].ravel():
            if (int(e) & 0x3FF) != 0:
                banks.add((int(e) >> 12) & 0xF)
        out[i] = banks
    return out


def used_tiles(ts: Tileset) -> set[int]:
    s = set()
    for e in ts.metatiles.ravel():
        s.add(int(e) & 0x3FF)
    return s
