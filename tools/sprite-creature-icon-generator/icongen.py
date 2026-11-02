"""Party / PC box icon from an approved battle front.

The front (64x64) is cropped, reduced to fit the 32x32 icon cell, given a dark outline, snapped to the
closest of the 3 shared icon banks, and placed feet-down like vanilla. Frame 2 (the wiggle) comes from
the front's own second pose (anim_front frame 2) reduced the same way, plus a 1 px squash.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(REPO / "tools" / "palette-enforcer"))
from gba_palette import check, core, enforce  # noqa: E402

GAME = REPO / "game"
ART = REPO / "wiki" / "art"
BANKS = [core.load_jasc(GAME / f"graphics/pokemon/icon_palettes/icon_palette_{n}.pal") for n in range(3)]

# Vanilla icons: the creature sits feet-down at row 29-30, at most ~30 wide and 24 tall.
MAX_W, MAX_H, BOTTOM = 30, 25, 30
SCALE = 0.50
MODE = "medoid"
PUNCH = 0.2  # extra chroma and contrast after reduction, so the icon reads at 1x


def load_rgba(path: Path, top: int = 0, height: int = 64) -> np.ndarray:
    im = Image.open(path)
    im = im.crop((0, top, im.width, top + height))
    arr = np.array(im.convert("RGBA")).astype(np.float64)
    if im.mode == "P":
        arr[..., 3] = np.where(np.array(im) == 0, 0, 255)
    return arr


def bbox(a: np.ndarray):
    ys, xs = np.where(a[..., 3] > 0)
    return ys.min(), ys.max() + 1, xs.min(), xs.max() + 1


def reduce(src: np.ndarray, box, scale: float, out_h: int, out_w: int, cover: float = 0.35):
    """Area-average reduction in linear light over the crop `box`; returns (rgb float, mask bool)."""
    y0, y1, x0, x1 = box
    crop = src[y0:y1, x0:x1]
    h, w = crop.shape[:2]
    rgb = np.zeros((out_h, out_w, 3))
    mask = np.zeros((out_h, out_w), bool)
    lab = core.to_lab(crop[..., :3].reshape(-1, 3)).reshape(h, w, 3)
    for oy in range(out_h):
        sy0, sy1 = oy / scale, (oy + 1) / scale
        for ox in range(out_w):
            sx0, sx1 = ox / scale, (ox + 1) / scale
            ys = slice(int(np.floor(sy0)), min(h, int(np.ceil(sy1))))
            xs = slice(int(np.floor(sx0)), min(w, int(np.ceil(sx1))))
            blk = crop[ys, xs]
            if blk.size == 0:
                continue
            op = blk[..., 3] > 0
            if op.mean() < cover:
                continue
            mask[oy, ox] = True
            px = blk[op][:, :3]
            if MODE == "medoid":
                lb = lab[ys, xs][op]
                u, inv = np.unique(px, axis=0, return_inverse=True)
                ul = core.to_lab(u)
                cost = ((ul[:, None] - lb[None]) ** 2).sum(-1) ** 0.5
                rgb[oy, ox] = u[np.argmin(cost.sum(1))]
                continue
            if MODE == "mean":
                rgb[oy, ox] = px.mean(0)
                continue
            # Keep contrast: favour the darkest third when the block mixes outline and fill,
            # otherwise average. This keeps eyes and outlines that plain averaging washes out.
            L = lab[ys, xs][op][:, 0]
            if L.max() - L.min() > 35:
                dark = px[L <= np.percentile(L, 34)]
                rgb[oy, ox] = dark.mean(0) if (L < L.min() + 12).mean() > 0.25 else px.mean(0)
            else:
                rgb[oy, ox] = px.mean(0)
    return rgb, mask


def punch(rgb: np.ndarray, mask: np.ndarray, k: float) -> np.ndarray:
    """Stretch contrast and saturation around the creature's mean, in RGB (small k, ~0.15-0.3)."""
    if k <= 0 or not mask.any():
        return rgb
    out = rgb.copy()
    px = rgb[mask]
    grey = px.mean(1, keepdims=True)
    px = grey + (px - grey) * (1 + k)            # saturation
    m = px.mean()
    px = m + (px - m) * (1 + k * 0.6)            # contrast
    out[mask] = px.clip(0, 255)
    return out


def outline(rgb: np.ndarray, mask: np.ndarray, factor: float = 0.42) -> np.ndarray:
    """Darken the silhouette's edge pixels, like vanilla's 1 px outline."""
    rgb = punch(rgb, mask, PUNCH)
    pad = np.pad(mask, 1)
    edge = mask & ~(pad[:-2, 1:-1] & pad[2:, 1:-1] & pad[1:-1, :-2] & pad[1:-1, 2:])
    out = rgb.copy()
    out[edge] = out[edge] * factor
    return out


def best_bank(rgb: np.ndarray, mask: np.ndarray, banks=None) -> int:
    px = rgb[mask]
    errs = []
    for bank in banks or BANKS:
        _, d = core.nearest(px, np.array(bank[1:], float))
        errs.append(float((d ** 2).sum()))
    return int(np.argmin(errs))


def to_cell(rgb, mask, cell_h=32, cell_w=32, dy=0):
    h, w = mask.shape
    out = np.zeros((cell_h, cell_w, 4))
    oy = BOTTOM - h + dy
    ox = (cell_w - w) // 2
    out[oy:oy + h, ox:ox + w, :3] = rgb
    out[oy:oy + h, ox:ox + w, 3] = np.where(mask, 255, 0)
    return out


def squash(rgb, mask):
    """Frame-2 squash: drop the top row's height by 1 px, feet stay planted."""
    h = mask.shape[0]
    if h < 6:
        return rgb, mask
    keep = [r for r in range(h) if r != h // 3]  # remove one row from the upper body
    return rgb[keep], mask[keep]


def make_icon(front: Path, anim: Path | None):
    f1 = load_rgba(front)
    f2 = load_rgba(anim, 64) if anim and anim.exists() else f1
    b1, b2 = bbox(f1), bbox(f2)
    box = (min(b1[0], b2[0]), max(b1[1], b2[1]), min(b1[2], b2[2]), max(b1[3], b2[3]))
    h, w = box[1] - box[0], box[3] - box[2]
    scale = min(SCALE, MAX_W / w, MAX_H / h)
    oh, ow = max(1, round(h * scale)), max(1, round(w * scale))
    frames = []
    for src in (f1, f2):
        rgb, mask = reduce(src, box, scale, oh, ow)
        frames.append((rgb, mask))
    # Trim empty rows/cols shared by both frames so the creature sits on the floor.
    union = frames[0][1] | frames[1][1]
    rows, cols = np.where(union.any(1))[0], np.where(union.any(0))[0]
    frames = [(r[rows.min():rows.max() + 1, cols.min():cols.max() + 1], m[rows.min():rows.max() + 1, cols.min():cols.max() + 1]) for r, m in frames]
    same = (frames[0][1] == frames[1][1]).mean() > 0.97 and np.abs(frames[0][0] - frames[1][0]).mean() < 6
    if same:
        frames[1] = squash(*frames[0])
    cells = []
    for i, (rgb, mask) in enumerate(frames):
        if i == 1 and same:
            pass
        cells.append(to_cell(outline(rgb, mask), mask))
    return np.concatenate(cells, 0)


def finish(sheet: np.ndarray, banks=None):
    """Snap a float RGBA sheet onto the best of the shared banks; returns (indexed image, bank)."""
    banks = banks or BANKS
    bank = best_bank(sheet[..., :3], sheet[..., 3] > 0, banks)
    img = Image.fromarray(sheet.clip(0, 255).astype(np.uint8), "RGBA")
    out, _ = enforce.enforce(img, bpp=4, pal=banks[bank])
    return out, bank


def main(argv):
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("species", nargs="+", help="folder under graphics/pokemon, e.g. treecko or unown/a")
    ap.add_argument("--out", default=str(HERE / "out"))
    ap.add_argument("--banks", default=None, help="folder with icon_palette_{0,1,2}.pal (default: vanilla)")
    a = ap.parse_args(argv)
    banks = [core.load_jasc(Path(a.banks) / f"icon_palette_{n}.pal") for n in range(3)] if a.banks else BANKS
    for sp in a.species:
        d = ART / "graphics/pokemon" / sp
        img, bank = finish(make_icon(d / "front.png", d / "anim_front.png"), banks)
        dst = Path(a.out) / sp / "icon.png"
        dst.parent.mkdir(parents=True, exist_ok=True)
        enforce.save(img, dst, 4)
        rep = check.check_png(dst, pal=banks[bank])
        print(sp, "bank", bank, "ok" if rep.ok else "\n".join(rep.lines()))


if __name__ == "__main__":
    main(sys.argv[1:])
