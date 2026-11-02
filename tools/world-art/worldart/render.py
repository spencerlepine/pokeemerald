"""The Emerald camera: ray-march the model's signed-distance field the way the vanilla overworld
is drawn, then cel-shade, pixelise, outline and ground it (`../../tile-generator/STYLE.md`).

Projection (measured on the vanilla art): world X east, Y north, Z up, 16 px per metre and one
metre per map cell. A point lands on screen at `col = x`, `row = -(y + z)`: ground is drawn in
plan at full size, a south face head-on at full height, east/west faces edge-on, north faces
hidden. Nothing is foreshortened. The nearest point on a pixel's line `y + z = const` is the one
with the largest z (and most southern y), so a ray starts high in the south and walks north and
down at 45 degrees until it hits the field or the ground.

Shading: one light from the upper left, in front and above; every material is a ramp of 3-4 tones
cut by N.L thresholds, with a 50% checker band at each cut for `dither` (round) materials and a
hard snap for flat ones; an ambient-occlusion term darkens crevices (leaf clumps). Outlines are
1 px in the material's own darkest tone, around the silhouette and at depth steps. A checker
ellipse of the ground's shade tone sits under each instance.
"""
import math

import numpy as np
from PIL import Image

RAY_D = np.array([0.0, 1.0, -1.0]) / math.sqrt(2.0)     # north and down


def _raymarch(inst, yaw, us, ws, zhi, max_steps=240):
    """us: world x per sample; ws: y + z per sample. Returns (hit, t, points)."""
    o = np.stack([us, ws - zhi, np.full_like(us, zhi)], axis=1)
    tmax = (zhi + 0.02) * math.sqrt(2.0)
    t = np.zeros(len(us))
    alive = np.ones(len(us), bool)
    hit = np.zeros(len(us), bool)
    for _ in range(max_steps):
        idx = np.nonzero(alive)[0]
        if len(idx) == 0:
            break
        dist = inst.sdf(o[idx] + t[idx, None] * RAY_D, yaw)
        h = dist < 8e-4
        hit[idx[h]] = True
        alive[idx[h]] = False
        t[idx] += np.maximum(dist, 3e-4) * 0.7
        alive[idx[t[idx] > tmax]] = False
    return hit, t, o + t[:, None] * RAY_D


def _shade(obj, inst, yaw, p, px, py):
    """Tone index per hit sample. px, py: whole-pixel coords of each sample (for the checker)."""
    rnd = obj.rnd
    _, pid, Q = inst.sdf(p, yaw, want=True)
    eps = 3e-3
    n = np.zeros_like(p)
    for k in range(3):
        dv = np.zeros(3)
        dv[k] = eps
        n[:, k] = inst.sdf(p + dv, yaw) - inst.sdf(p - dv, yaw)
    n /= np.linalg.norm(n, axis=1, keepdims=True) + 1e-12
    L = np.asarray(rnd["light"], float)
    L /= np.linalg.norm(L)
    ndl = n @ L

    ao = rnd.get("ao") or {}
    drop = np.zeros(len(p), int)
    if float(ao.get("strength", 0)) > 0:
        occ = np.zeros(len(p))
        hs = (0.05, 0.11, 0.2)
        for h in hs:
            occ += np.clip((h - inst.sdf(p + n * h, yaw)) / h, 0, 1)
        occ = occ / len(hs) * float(ao["strength"])
        drop = (occ > float(ao["threshold"])).astype(int) + (occ > float(ao["threshold"]) * 1.9).astype(int)

    checker = ((px + py) & 1) == 0
    dw = float(rnd.get("dither", 0.06))
    names = inst.material_of(pid, Q)
    out = np.empty(len(p), dtype=np.int32)
    for name in set(names):
        m = names == name
        mat = obj.mats[name]
        if mat["emissive"]:
            out[m] = mat["idx"][-1]
            continue
        v = ndl[m]
        band = np.zeros(m.sum(), int)
        for th in mat["bands"]:
            band += (v > th).astype(int)
        if mat["dither"]:
            ck = checker[m]
            for th in mat["bands"]:
                above = (v > th) & (v <= th + dw) & ck
                below = (v <= th) & (v > th - dw) & ~ck
                band = np.where(above, band - 1, band)
                band = np.where(below, band + 1, band)
        band = np.clip(band - drop[m], 0, len(mat["idx"]) - 1)
        out[m] = np.asarray(mat["idx"])[band]
    return out, names, n


def render_instance(obj, inst, yaw):
    """One instance into the object's frame: (indices[h, w], filled, holes, depth[h, w], normal_z[h, w])."""
    rnd = obj.rnd
    W, H = obj.size
    ss = int(rnd["supersample"])
    scale = float(rnd["px_per_m"])
    ax, ay = inst.foot

    lo, hi = inst.world_bounds()
    c0 = max(int(math.floor(ax + lo[0] * scale)) - 1, 0)
    c1 = min(int(math.ceil(ax + hi[0] * scale)) + 1, W)
    r0 = max(int(math.floor(ay - (hi[1] + hi[2]) * scale)) - 1, 0)
    r1 = min(int(math.ceil(ay - (lo[1] + lo[2]) * scale)) + 1, H)
    out = np.zeros((H, W), np.int32)
    zdepth = np.full((H, W), np.inf)
    nz = np.zeros((H, W))
    if c1 <= c0 or r1 <= r0:
        return out, out > 0, out > 0, zdepth, nz
    w, h = c1 - c0, r1 - r0
    cols = c0 + (np.arange(w * ss) + 0.5) / ss
    rows = r0 + (np.arange(h * ss) + 0.5) / ss
    cc, rr = np.meshgrid(cols, rows)
    us = ((cc - ax) / scale).ravel()
    ws = ((ay - rr) / scale).ravel()
    hit, t, p = _raymarch(inst, yaw, us, ws, float(hi[2]) + 0.05)
    idx = np.zeros(len(us), np.int32)
    cut = np.zeros(len(us), bool)
    nzs = np.zeros(len(us))
    if hit.any():
        px = np.floor(cc.ravel()[hit]).astype(int)
        py = np.floor(rr.ravel()[hit]).astype(int)
        hidx, names, n = _shade(obj, inst, yaw, p[hit], px, py)
        hcut = np.zeros(len(hidx), bool)
        for name in set(names):
            expr = obj.mats[name].get("cutout")
            if expr:
                m = names == name
                hcut[m] = np.asarray(eval(expr, {"np": np, "abs": np.abs}, {"px": px[m], "py": py[m]}), bool)
        hidx[hcut] = 0
        idx[hit] = hidx
        cut[hit] = hcut
        nzs[hit] = n[:, 2]
        hit = hit & ~cut
    depth = np.where(hit, t, np.inf)

    def blocks(a):
        return a.reshape(h, ss, w, ss).transpose(0, 2, 1, 3).reshape(h, w, ss * ss)
    bi, bd, bc, bn = blocks(idx), blocks(depth), blocks(cut), blocks(nzs)
    need = rnd["coverage"] * ss * ss
    holes = np.zeros((H, W), bool)
    holes[r0:r1, c0:c1] = bc.sum(-1) >= need
    npal = len(obj.palette)
    filled_n = (bi > 0).sum(-1)
    sub = np.zeros((h, w), np.int32)
    zsub = np.full((h, w), np.inf)
    nsub = np.zeros((h, w))
    for r, c in zip(*np.nonzero(filled_n >= need)):
        b = bi[r, c]
        m = b > 0
        counts = np.bincount(b[m], minlength=npal) * obj.priority
        sub[r, c] = int(np.argmax(counts))
        zsub[r, c] = np.median(bd[r, c][m])
        nsub[r, c] = np.median(bn[r, c][m])

    filled = sub > 0
    final = sub.copy()
    mode = rnd["inner_lines"]
    if mode and mode != "none":
        zp = np.pad(zsub, 1, constant_values=np.inf)
        nearer = np.zeros_like(filled)
        for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            nzp = zp[1 + dr:1 + dr + h, 1 + dc:1 + dc + w]
            with np.errstate(invalid="ignore"):
                nearer |= (zsub - nzp) > rnd["depth_jump"]
        sel = filled & nearer
        final[sel] = obj.shadow_of[sub[sel]] if mode == "selout" else obj.darkest_of[sub[sel]]
    out[r0:r1, c0:c1] = final
    zdepth[r0:r1, c0:c1] = zsub
    nz[r0:r1, c0:c1] = nsub
    return out, out > 0, holes & (out == 0), zdepth, nz


def outline(obj, ind, holes=None):
    """1 px silhouette ring in the darkest tone of the material next to it."""
    filled = ind > 0
    fp = np.pad(ind, 1)
    out = ind.copy()
    H, W = ind.shape
    for dr, dc in ((1, 0), (0, 1), (0, -1), (-1, 0)):
        nb = fp[1 + dr:1 + dr + H, 1 + dc:1 + dc + W]
        sel = (~filled) & (out == 0) & (nb > 0)
        if holes is not None:
            sel &= ~holes
        out[sel] = obj.darkest_of[nb[sel]]
    return out


def shadow_mask(obj):
    W, H = obj.size
    yy, xx = np.mgrid[0:H, 0:W] + 0.5
    m = np.zeros((H, W), bool)
    for inst in obj.instances:
        if inst.shadow:
            rx, ry, dx, dy = inst.shadow
            cx, cy = inst.foot[0] + dx, inst.foot[1] + dy
            m |= ((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2 <= 1.0
    return m


def apply_textures(obj, canvas, mats_px, nz):
    """STYLE 5: tiny periodic patterns, applied per material on the tone image.
    `scallop`: leaf scallops, 5x4, offset every other row (dark underside line on the lit tones).
    `plank`: a dark line every 4 rows on south faces. `brick`: staggered 8x4 roof tiles."""
    H, W = canvas.shape
    yy, xx = np.mgrid[0:H, 0:W]
    out = canvas.copy()
    for name, mat in obj.mats.items():
        tex = mat.get("texture")
        if not tex or len(mat["idx"]) < 2:
            continue
        m = mats_px == name
        if not m.any():
            continue
        idx = list(mat["idx"])
        tone = np.full((H, W), -1)
        for k, i in enumerate(idx):
            tone[(out == i) & m] = k
        darker = {idx[k]: idx[max(k - 1, 0)] for k in range(len(idx))}
        if tex == "scallop":
            row = yy % 4
            off = ((yy // 4) & 1) * 2
            col = (xx + off) % 5
            under = (row == 3) & (col != 4)
            edge = (row == 2) & ((col == 0) | (col == 4))
            sel = m & (tone >= 1) & (under | edge)
        elif tex == "plank":
            sel = m & (nz < 0.5) & (yy % 4 == 3)
        elif tex == "brick":
            off = ((yy // 4) & 1) * 4
            sel = m & (nz > 0.5) & ((yy % 4 == 3) | (((xx + off) % 8) == 7))
        elif tex == "rows":     # thatch, tiles: a dark line every 4 rows on every face
            sel = m & (tone >= 1) & (yy % 4 == 3)
        elif tex == "ridge":    # bark: a dark vertical line every 4 columns on the south face, broken every 6 rows
            sel = m & (nz < 0.5) & (xx % 4 == 3) & (((yy + xx // 4 * 2) % 6) != 0)
        elif tex == "speck":
            h = ((xx * 7 + yy * 13 + (xx * yy) % 11) * 2654435761) & 0xffff
            sel = m & (tone >= 1) & (h % 17 == 0)
        else:
            raise ValueError(f"material {name}: unknown texture {tex!r}")
        out[sel] = np.vectorize(lambda v: darker.get(int(v), int(v)))(out[sel]) if sel.any() else out[sel]
    return out


def render_object(obj, yaw=0.0):
    """Every instance, composited back to front. Returns (RGBA image, indices, warnings)."""
    W, H = obj.size
    canvas = np.zeros((H, W), np.int32)
    mats_px = np.full((H, W), "", dtype=object)
    nzc = np.zeros((H, W))
    warnings = []
    margin = int(obj.rnd.get("margin", 1))
    order = sorted(range(len(obj.instances)), key=lambda i: (-obj.instances[i].foot[1], obj.instances[i].foot[0]))
    order.reverse()   # draw northern (small row) feet first, southern last
    for i in order:
        inst = obj.instances[i]
        ind, filled, holes, zd, nz = render_instance(obj, inst, yaw)
        if margin:
            inner = np.zeros_like(filled)
            inner[margin:H - margin, margin:W - margin] = True
            if (filled & ~inner).any():
                warnings.append(f"{obj.name}: instance {i} touches the image edge (keep {margin}px clear)")
        if obj.rnd["outline"]:
            ind = outline(obj, ind, holes)
        sel = ind > 0
        canvas[sel] = ind[sel]
        nzc[sel] = nz[sel]
        for name, mat in obj.mats.items():
            mm = sel & np.isin(ind, mat["idx"])
            mats_px[mm] = name
    canvas = apply_textures(obj, canvas, mats_px, nzc)
    rgb = obj.palette[canvas]
    a = np.where(canvas > 0, 255, 0).astype(np.uint8)
    yy, xx = np.mgrid[0:H, 0:W]
    sm = shadow_mask(obj) & (canvas == 0) & (((xx + yy) & 1) == 0)
    canvas[sm] = obj.shadow_idx
    rgb[sm] = obj.palette[obj.shadow_idx]
    a[sm] = 255
    return Image.fromarray(np.dstack([rgb, a]), "RGBA"), canvas, warnings
