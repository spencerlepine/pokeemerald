"""Stage 3: the Emerald camera. A tiny software rasteriser that draws 3D primitives the way the
vanilla overworld is drawn, so geometry can never break the top-down illusion.

The projection (measured on vanilla houses, trees and signs; see STYLE.md):

    screen_x = x
    screen_y = y - z * HEIGHT_SCALE        (y = depth into the map, "north" is -y; z = height)

Horizontal faces are drawn in plan at full size; faces that look south (toward the player) are drawn
head-on at full height; east/west faces are edge-on and vanish; north faces are hidden. Nothing is
foreshortened and there is no vanishing point: a house is its roof plan stacked on its front elevation.

Units are pixels: 16 px = one metatile = one map cell. A one-storey wall is ~24 px tall.

Lighting: one directional light from the upper left, in front and above (so tops are lightest, fronts
mid). Each material is a ramp of 3-4 tones; the shade is quantised to the ramp with a 50% checker band
at each threshold for curved surfaces (Emerald's dither idiom), flat faces snap to one tone.

Outlines: 1 px in the material's darkest tone around the silhouette and at depth steps; a drop shadow on
the ground row under the base (ellipse for round footprints, a line for boxes).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Sequence

import numpy as np

HEIGHT_SCALE = 1.0
LIGHT = np.array([-0.35, 0.42, 0.84])   # from the upper left, in front (south) and above
LIGHT = LIGHT / np.linalg.norm(LIGHT)


# ----------------------------------------------------------------------------- materials

@dataclass
class Material:
    """A ramp: tones from light to dark (RGB), plus how the shade maps onto it."""
    name: str
    tones: list[tuple[int, int, int]]            # light ... dark, 3 or 4 entries
    outline: tuple[int, int, int] | None = None  # default: darkest tone
    smooth: bool = False                         # curved: dither bands between tones
    thresholds: Sequence[float] | None = None    # shade cut points, len = len(tones)-1, descending
    emissive: bool = False                       # ignore light: always tone 0
    texture: str | None = None                   # "scallop" (leaf canopy), "brick", "plank", None
    highlight: bool = False                      # 1 px light rim along the top-left inside the silhouette

    def tone_for(self, shade: np.ndarray, checker: np.ndarray) -> np.ndarray:
        """shade in [0,1] (n.l) -> tone index array."""
        n = len(self.tones)
        if self.emissive:
            return np.zeros_like(shade, dtype=np.int32)
        th = self.thresholds
        if th is None:
            th = {3: (0.72, 0.40), 4: (0.78, 0.55, 0.30), 2: (0.55,), 1: ()}[n]
        idx = np.zeros_like(shade, dtype=np.int32)
        for t in th:
            idx += (shade < t).astype(np.int32)
        if self.smooth:
            band = 0.045
            for i, t in enumerate(th):
                near_above = (shade >= t) & (shade < t + band)    # just lighter than the cut: dither to darker
                near_below = (shade < t) & (shade >= t - band)
                idx = np.where(near_above & checker, i + 1, idx)
                idx = np.where(near_below & checker, i, idx)
        return np.clip(idx, 0, n - 1)

    @property
    def outline_rgb(self):
        return self.outline if self.outline is not None else self.tones[-1]


def ramp(name: str, base: tuple[int, int, int], n: int = 3, spread: float = 18.0, hue_shift: float = -8.0,
         smooth=False, **kw) -> Material:
    """Make a material from one base colour: tones spaced `spread` L* apart around it (darker tones get
    the hue shifted toward blue/purple like Emerald does)."""
    from . import colour
    lch = colour.srgb_to_lch(np.array(base, float))
    tones = []
    for i in range(n):
        k = i - (n - 1) / 2
        L = lch[0] - k * spread
        C = lch[1] * (1.0 + 0.08 * k)
        H = (lch[2] + k * hue_shift) % 360
        tones.append(tuple(int(v) for v in colour.gba_snap(colour.lch_to_srgb(np.array([np.clip(L, 4, 98), max(C, 0), H])))))
    return Material(name, tones, smooth=smooth, **kw)


# ----------------------------------------------------------------------------- meshes

@dataclass
class Mesh:
    verts: np.ndarray            # (N,3) float, x right, y into the map (south = +y), z up
    faces: np.ndarray            # (M,3) int
    material: Material
    smooth: bool = False         # per-vertex normals (spheres) vs flat
    vnormals: np.ndarray | None = None

    def translated(self, dx=0.0, dy=0.0, dz=0.0) -> "Mesh":
        return Mesh(self.verts + np.array([dx, dy, dz]), self.faces, self.material, self.smooth, self.vnormals)


def _mesh(verts, faces, mat, smooth=False, vnormals=None):
    return Mesh(np.asarray(verts, float), np.asarray(faces, int), mat, smooth, vnormals)


def box(w, d, h, mat: Material, x=0.0, y=0.0, z=0.0) -> Mesh:
    """Axis-aligned box; (x,y) is the top-left of its footprint in plan, z its base height."""
    x0, x1, y0, y1, z0, z1 = x, x + w, y, y + d, z, z + h
    v = [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0), (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)]
    f = [(4, 5, 6), (4, 6, 7),            # top
         (3, 2, 6), (3, 6, 7),            # south (front)
         (0, 1, 5), (0, 5, 4),            # north
         (1, 2, 6), (1, 6, 5),            # east
         (0, 3, 7), (0, 7, 4),            # west
         (0, 2, 1), (0, 3, 2)]            # bottom
    return _mesh(v, f, mat)


def gable_roof(w, d, h, mat: Material, x=0.0, y=0.0, z=0.0, ridge_along_x=True, overhang=0.0) -> Mesh:
    """A prism roof: eaves at z, ridge at z+h. ridge_along_x: slopes face north and south."""
    x0, x1, y0, y1 = x - overhang, x + w + overhang, y - overhang, y + d + overhang
    if ridge_along_x:
        ym = y + d / 2
        v = [(x0, y0, z), (x1, y0, z), (x1, y1, z), (x0, y1, z), (x0, ym, z + h), (x1, ym, z + h)]
        f = [(3, 2, 5), (3, 5, 4),        # south slope
             (0, 1, 5), (0, 5, 4),        # north slope
             (1, 2, 5), (0, 4, 3)]        # gable ends
    else:
        xm = x + w / 2
        v = [(x0, y0, z), (x1, y0, z), (x1, y1, z), (x0, y1, z), (xm, y0, z + h), (xm, y1, z + h)]
        f = [(0, 4, 3), (4, 5, 3), (1, 2, 5), (1, 5, 4), (0, 1, 4), (3, 5, 2)]
    return _mesh(v, f, mat)


def ellipsoid(rx, ry, rz, mat: Material, cx=0.0, cy=0.0, cz=0.0, segs=24, rings=12, top_only=False) -> Mesh:
    """UV sphere scaled; smooth normals. top_only: a dome (z >= cz)."""
    verts, norms = [], []
    ring_ids = list(range(0, rings // 2 + 1)) if top_only else list(range(0, rings + 1))
    for i in ring_ids:
        phi = np.pi * i / rings          # 0 top .. pi bottom
        for j in range(segs):
            th = 2 * np.pi * j / segs
            nx, ny, nz = np.sin(phi) * np.cos(th), np.sin(phi) * np.sin(th), np.cos(phi)
            verts.append((cx + rx * nx, cy + ry * ny, cz + rz * nz))
            n = np.array([nx / rx, ny / ry, nz / rz]); norms.append(n / np.linalg.norm(n))
    faces = []
    nr = len(ring_ids) - 1
    for i in range(nr):
        for j in range(segs):
            a = i * segs + j; b = i * segs + (j + 1) % segs
            c = (i + 1) * segs + j; d = (i + 1) * segs + (j + 1) % segs
            faces.append((a, c, d)); faces.append((a, d, b))
    return _mesh(verts, faces, mat, smooth=True, vnormals=np.array(norms))


def cylinder(r, h, mat: Material, cx=0.0, cy=0.0, z=0.0, segs=24, rx=None, ry=None) -> Mesh:
    rx = r if rx is None else rx; ry = r if ry is None else ry
    verts, norms, faces = [], [], []
    for k, zz in enumerate((z, z + h)):
        for j in range(segs):
            th = 2 * np.pi * j / segs
            verts.append((cx + rx * np.cos(th), cy + ry * np.sin(th), zz)); norms.append((np.cos(th), np.sin(th), 0.0))
    for j in range(segs):
        a, b = j, (j + 1) % segs
        faces.append((a, segs + a, segs + b)); faces.append((a, segs + b, b))
    side = _mesh(verts, faces, mat, smooth=True, vnormals=np.array(norms))
    # caps: flat
    top_v = [(cx + rx * np.cos(2 * np.pi * j / segs), cy + ry * np.sin(2 * np.pi * j / segs), z + h) for j in range(segs)] + [(cx, cy, z + h)]
    top_f = [(j, (j + 1) % segs, segs) for j in range(segs)]
    cap = _mesh(top_v, top_f, mat)
    return merge([side, cap])


def cone(r, h, mat: Material, cx=0.0, cy=0.0, z=0.0, segs=24, r_top=0.0) -> Mesh:
    verts, norms, faces = [], [], []
    for k, (rr, zz) in enumerate(((r, z), (r_top, z + h))):
        for j in range(segs):
            th = 2 * np.pi * j / segs
            verts.append((cx + rr * np.cos(th), cy + rr * np.sin(th), zz))
            n = np.array([np.cos(th) * h, np.sin(th) * h, (r - r_top)]); norms.append(n / np.linalg.norm(n))
    for j in range(segs):
        a, b = j, (j + 1) % segs
        faces.append((a, segs + a, segs + b)); faces.append((a, segs + b, b))
    return _mesh(verts, faces, mat, smooth=True, vnormals=np.array(norms))


def merge(meshes: Sequence[Mesh]) -> Mesh:
    """Concatenate meshes that share a material (keeps smooth flag of the first)."""
    vs, fs, ns, off = [], [], [], 0
    smooth = any(m.smooth for m in meshes)
    for m in meshes:
        vs.append(m.verts); fs.append(m.faces + off); off += len(m.verts)
        if smooth:
            ns.append(m.vnormals if m.vnormals is not None else _flat_vertex_normals(m))
    return Mesh(np.concatenate(vs), np.concatenate(fs), meshes[0].material, smooth, np.concatenate(ns) if smooth else None)


def _flat_vertex_normals(m: Mesh) -> np.ndarray:
    n = np.zeros_like(m.verts)
    for f in m.faces:
        a, b, c = m.verts[f]
        fn = np.cross(b - a, c - a)
        for i in f:
            n[i] += fn
    l = np.linalg.norm(n, axis=1, keepdims=True); l[l == 0] = 1
    return n / l


# ----------------------------------------------------------------------------- rasteriser

@dataclass
class Render:
    rgb: np.ndarray        # (H,W,3) uint8
    alpha: np.ndarray      # (H,W) bool
    depth: np.ndarray      # (H,W) float, smaller = closer (y - z)
    height: np.ndarray     # (H,W) float world z of the visible surface
    mat_id: np.ndarray     # (H,W) int, -1 = none
    tone: np.ndarray       # (H,W) int tone index
    materials: list[Material]

    def colours(self) -> list[tuple[int, int, int]]:
        """Every distinct colour used (for the bank budget)."""
        seen = []
        for c in np.unique(self.rgb[self.alpha].reshape(-1, 3), axis=0):
            seen.append(tuple(int(v) for v in c))
        return seen


def _project(verts: np.ndarray) -> np.ndarray:
    sx = verts[:, 0]
    sy = verts[:, 1] - verts[:, 2] * HEIGHT_SCALE
    key = verts[:, 1] + verts[:, 2]          # view-ray parameter: bigger = farther from the camera? no:
    # camera direction toward the scene is (0, +1, -1): points farther along it are deeper.
    # For two points on one screen pixel, the one with larger (y + z)... derive: P + t*(0,1,-1) keeps
    # sx, sy. Depth along the ray is t ~ y - (-z)?? Use d = y + z: moving into the scene (t>0) raises y by t
    # and lowers z by t -> y+z constant. So y+z is constant along the ray: it is NOT a depth. The depth is
    # the ray parameter itself: t = (y - sy_proj)... Simplest: depth = y (then z follows). For two points on
    # the same pixel, larger y means the point sits further north... no: sy = y - z, so same pixel with
    # larger y has larger z: it is the HIGHER point, which is nearer the camera (camera is above & south).
    key = -(verts[:, 1])                      # larger y (and so larger z) = closer => depth = -y
    return np.stack([sx, sy, key], axis=1)


def render(meshes: Sequence[Mesh], width: int, height: int, origin=(0.0, 0.0), backface_cull=True) -> Render:
    """origin: world (x, y) that lands at screen (0, 0) for z = 0."""
    ox, oy = origin
    W, H = width, height
    depth = np.full((H, W), np.inf)
    zworld = np.zeros((H, W))
    mat_id = np.full((H, W), -1, dtype=np.int32)
    shade = np.zeros((H, W))
    materials: list[Material] = []
    mat_index: dict[int, int] = {}

    ys, xs = np.mgrid[0:H, 0:W]
    px = xs + 0.5 + ox
    py = ys + 0.5 + oy   # screen y in world units (y - z)

    for m in meshes:
        mid = mat_index.setdefault(id(m.material), len(materials))
        if mid == len(materials):
            materials.append(m.material)
        P = _project(m.verts)
        vn = m.vnormals if (m.smooth and m.vnormals is not None) else None
        centroid = m.verts.mean(axis=0)
        for fi, f in enumerate(m.faces):
            a, b, c = m.verts[f]
            fn = np.cross(b - a, c - a)
            nl = np.linalg.norm(fn)
            if nl == 0:
                continue
            fn = fn / nl
            # orient outward (primitives are convex-ish solids; winding is not trusted)
            if fn @ ((a + b + c) / 3 - centroid) < 0:
                fn = -fn
            # visibility: the camera sits south (+y) and above (+z); a face shows if n . (0, 1, 1) > 0
            facing = fn[1] + fn[2]
            if backface_cull and facing <= 1e-6:
                continue
            pa, pb, pc = P[f]
            # bounding box
            x0 = max(int(np.floor(min(pa[0], pb[0], pc[0]) - ox)), 0); x1 = min(int(np.ceil(max(pa[0], pb[0], pc[0]) - ox)), W)
            y0 = max(int(np.floor(min(pa[1], pb[1], pc[1]) - oy)), 0); y1 = min(int(np.ceil(max(pa[1], pb[1], pc[1]) - oy)), H)
            if x1 <= x0 or y1 <= y0:
                continue
            X = px[y0:y1, x0:x1]; Y = py[y0:y1, x0:x1]
            # barycentric
            det = (pb[0] - pa[0]) * (pc[1] - pa[1]) - (pc[0] - pa[0]) * (pb[1] - pa[1])
            if abs(det) < 1e-9:
                continue
            l1 = ((pb[0] - X) * (pc[1] - Y) - (pc[0] - X) * (pb[1] - Y)) / det
            l2 = ((pc[0] - X) * (pa[1] - Y) - (pa[0] - X) * (pc[1] - Y)) / det
            l0 = 1 - l1 - l2
            # note: with det sign, l's are (wa, wb, wc) in order a,b,c
            wa, wb, wc = l0, l1, l2
            inside = (wa >= -1e-6) & (wb >= -1e-6) & (wc >= -1e-6)
            if not inside.any():
                continue
            d = wa * pa[2] + wb * pb[2] + wc * pc[2]
            zz = wa * a[2] + wb * b[2] + wc * c[2]
            sub_depth = depth[y0:y1, x0:x1]
            win = inside & (d < sub_depth)
            if not win.any():
                continue
            if vn is not None:
                na, nb, nc = vn[f]
                nx = wa * na[0] + wb * nb[0] + wc * nc[0]
                ny = wa * na[1] + wb * nb[1] + wc * nc[1]
                nz = wa * na[2] + wb * nb[2] + wc * nc[2]
                ln = np.sqrt(nx * nx + ny * ny + nz * nz); ln[ln == 0] = 1
                s = (nx * LIGHT[0] + ny * LIGHT[1] + nz * LIGHT[2]) / ln
            else:
                s = np.full_like(d, float(fn @ LIGHT))
            sub_depth[win] = d[win]
            zworld[y0:y1, x0:x1][win] = zz[win]
            mat_id[y0:y1, x0:x1][win] = mid
            shade[y0:y1, x0:x1][win] = s[win]

    alpha = mat_id >= 0
    shade = np.clip((shade + 0.15) / 1.15, 0, 1)   # a little ambient so undersides are not black
    checker = ((xs + ys) % 2) == 0
    tone = np.zeros((H, W), dtype=np.int32)
    rgb = np.zeros((H, W, 3), dtype=np.uint8)
    for mid, mat in enumerate(materials):
        sel = mat_id == mid
        if not sel.any():
            continue
        t = mat.tone_for(shade, checker)
        tone[sel] = t[sel]
        pal = np.array(mat.tones, dtype=np.uint8)
        rgb[sel] = pal[t[sel]]
    depth[~alpha] = np.inf
    return Render(rgb, alpha, depth, zworld, mat_id, tone, materials)


# ----------------------------------------------------------------------------- pixel-art passes

def outline(r: Render, depth_step: float = 3.0, inner: bool = True) -> None:
    """1 px outline in the nearer material's dark tone: around the silhouette (drawn inside the shape so
    the footprint stays exact) and along depth steps between surfaces."""
    H, W = r.alpha.shape
    a = r.alpha
    edge = np.zeros_like(a)
    for dy, dx in ((0, 1), (0, -1), (1, 0), (-1, 0)):
        nb = np.roll(a, (dy, dx), axis=(0, 1))
        if dy == 1: nb[0, :] = False
        if dy == -1: nb[-1, :] = False
        if dx == 1: nb[:, 0] = False
        if dx == -1: nb[:, -1] = False
        edge |= a & ~nb                                   # silhouette: my neighbour is empty
        nd = np.roll(r.depth, (dy, dx), axis=(0, 1))
        nh = np.roll(r.height, (dy, dx), axis=(0, 1))
        # depth step: neighbour is farther by more than depth_step, or materially lower
        with np.errstate(invalid="ignore"):
            step = a & nb & np.isfinite(nd) & ((nd - r.depth) > depth_step) & ((r.height - nh) > depth_step)
        edge |= step
    for mid, mat in enumerate(r.materials):
        sel = edge & (r.mat_id == mid)
        r.rgb[sel] = mat.outline_rgb
        r.tone[sel] = len(mat.tones) - 1
    r.edge = edge


def texture(r: Render) -> None:
    """Per-material surface patterns, applied to the tone map before outlining."""
    H, W = r.alpha.shape
    ys, xs = np.mgrid[0:H, 0:W]
    for mid, mat in enumerate(r.materials):
        if mat.texture is None:
            continue
        sel = (r.mat_id == mid)
        n = len(mat.tones)
        t = r.tone.copy()
        if mat.texture == "scallop":
            # leaf scallops: rows of 5x4 arcs, every other row offset; the arc's underside is one tone
            # darker, its crown one tone lighter (Emerald's tree canopies)
            cw, ch = 5, 4
            row = ys // ch
            x = (xs + (row % 2) * (cw // 2)) % cw
            y = ys % ch
            under = (y == ch - 1) & (x != 0)                  # bottom of the arc
            side = (y == ch - 2) & ((x == 0) | (x == cw - 1))
            crown = (y == 0) & (x == cw // 2)
            t = np.where(under | side, np.minimum(t + 1, n - 1), t)
            t = np.where(crown, np.maximum(t - 1, 0), t)
        elif mat.texture == "brick":
            bw, bh = 8, 4
            row = ys // bh
            x = (xs + (row % 2) * (bw // 2)) % bw
            mortar = (ys % bh == bh - 1) | (x == bw - 1)
            t = np.where(mortar, np.minimum(t + 1, n - 1), t)
        elif mat.texture == "plank":
            t = np.where((ys % 4 == 3), np.minimum(t + 1, n - 1), t)
        r.tone[sel] = t[sel]
        pal = np.array(mat.tones, dtype=np.uint8)
        r.rgb[sel] = pal[r.tone[sel]]


def highlight(r: Render) -> None:
    """A 1 px light rim just inside the outline on the top and left edges of smooth materials."""
    a = r.alpha
    edge = getattr(r, "edge", None)
    if edge is None:
        return
    inner = a & ~edge
    up = np.roll(edge, 1, axis=0); up[0, :] = False
    left = np.roll(edge, 1, axis=1); left[:, 0] = False
    rim = inner & (up | left)
    # only where the surface faces up/left: use the stored shade proxy = tone 0/1
    for mid, mat in enumerate(r.materials):
        if not mat.highlight:
            continue
        sel = rim & (r.mat_id == mid) & (r.tone <= 1)
        r.rgb[sel] = mat.tones[0]
        r.tone[sel] = 0


def drop_shadow(r: Render, colour_rgb: tuple[int, int, int], rows: int = 2, kind: str = "line") -> np.ndarray:
    """Return an (H,W) bool mask of ground shadow pixels under the object (not drawn into r)."""
    H, W = r.alpha.shape
    col_has = r.alpha.any(axis=0)
    bottom = np.where(r.alpha.any(axis=1))[0]
    mask = np.zeros_like(r.alpha)
    if len(bottom) == 0:
        return mask
    # the lowest alpha pixel per column
    ys = np.where(r.alpha, np.arange(H)[:, None], -1).max(axis=0)
    for x in range(W):
        if not col_has[x]:
            continue
        for k in range(1, rows + 1):
            y = ys[x] + k
            if y < H and not r.alpha[y, x]:
                if kind == "checker" and (x + y) % 2:
                    continue
                mask[y, x] = True
    return mask


def composite(base: np.ndarray, r: Render, x: int, y: int, shadow: np.ndarray | None = None,
              shadow_rgb=(0, 0, 0), shadow_alpha: float = 0.35) -> None:
    """Paste a render onto an RGB array at (x, y) top-left."""
    H, W = r.alpha.shape
    bh, bw = base.shape[:2]
    x0, y0 = max(x, 0), max(y, 0)
    x1, y1 = min(x + W, bw), min(y + H, bh)
    if x1 <= x0 or y1 <= y0:
        return
    sub = base[y0:y1, x0:x1]
    rr = r.rgb[y0 - y:y1 - y, x0 - x:x1 - x]
    aa = r.alpha[y0 - y:y1 - y, x0 - x:x1 - x]
    if shadow is not None:
        ss = shadow[y0 - y:y1 - y, x0 - x:x1 - x]
        sub[ss] = (sub[ss] * (1 - shadow_alpha) + np.array(shadow_rgb) * shadow_alpha).astype(np.uint8)
    sub[aa] = rr[aa]
