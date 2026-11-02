"""Signed-distance primitives, blending operators and value noise (all vectorised over N points).

Forked from .claude/tools/art/characters/body-sheets/spritegen/sdf.py; `value_noise` is new here (it is what roughens a
crown or a rock without hand-placing every bump).
"""
import numpy as np


def ellipsoid(p, c, r):
    """Approximate SDF of an axis-aligned ellipsoid (iq's bound)."""
    q = (p - c) / r
    k0 = np.linalg.norm(q, axis=-1)
    k1 = np.linalg.norm(q / r, axis=-1)
    return k0 * (k0 - 1.0) / np.maximum(k1, 1e-9)


def round_cone(p, a, b, r1, r2):
    """Exact SDF of a capsule that tapers from radius r1 at a to r2 at b."""
    ba = b - a
    l2 = ba @ ba
    rr = r1 - r2
    a2 = l2 - rr * rr
    il2 = 1.0 / l2
    pa = p - a
    y = pa @ ba
    z = y - l2
    w = pa * l2 - ba[None, :] * y[:, None]
    x2 = np.einsum("ij,ij->i", w, w)
    y2 = y * y * l2
    z2 = z * z * l2
    k = np.sign(rr) * rr * rr * x2
    d_b = np.sqrt(x2 + z2) * il2 - r2
    d_a = np.sqrt(x2 + y2) * il2 - r1
    d_m = (np.sqrt(np.maximum(x2 * a2 * il2, 0)) + y * rr) * il2 - r1
    return np.where(np.sign(z) * a2 * z2 > k, d_b,
                    np.where(np.sign(y) * a2 * y2 < k, d_a, d_m))


def round_box(p, c, half, radius):
    """Exact SDF of a box with half-extents `half`, corners rounded by `radius`."""
    q = np.abs(p - c) - (half - radius)
    outside = np.linalg.norm(np.maximum(q, 0.0), axis=-1)
    inside = np.minimum(np.max(q, axis=-1), 0.0)
    return outside + inside - radius


def smin(a, b, k):
    """Polynomial smooth minimum (union). k = blend radius in metres; 0 = hard."""
    if k <= 0:
        return np.minimum(a, b)
    h = np.maximum(k - np.abs(a - b), 0.0) / k
    return np.minimum(a, b) - h * h * k * 0.25


def ssub(a, b, k):
    """Smooth subtraction: carve b out of a."""
    return -smin(-a, b, k)


def _hash(ix, iy, iz, seed):
    h = (ix.astype(np.uint32) * np.uint32(0x8DA6B343)) ^ (iy.astype(np.uint32) * np.uint32(0xD8163841)) \
        ^ (iz.astype(np.uint32) * np.uint32(0xCB1AB31F)) ^ np.uint32(seed * 0x9E3779B1 & 0xFFFFFFFF)
    h ^= h >> np.uint32(15)
    h *= np.uint32(0x2C1B3C6D)
    h ^= h >> np.uint32(12)
    h *= np.uint32(0x297A2D39)
    h ^= h >> np.uint32(15)
    return h.astype(np.float64) / 4294967296.0


def value_noise(p, seed=0):
    """Smooth 3D value noise in [-1, 1], one octave, lattice spacing 1."""
    with np.errstate(over="ignore"):
        f = np.floor(p)
        t = p - f
        t = t * t * (3 - 2 * t)
        i = f.astype(np.int64)
        out = np.zeros(len(p))
        for dx in (0, 1):
            wx = t[:, 0] if dx else 1 - t[:, 0]
            for dy in (0, 1):
                wy = t[:, 1] if dy else 1 - t[:, 1]
                for dz in (0, 1):
                    wz = t[:, 2] if dz else 1 - t[:, 2]
                    out += wx * wy * wz * _hash(i[:, 0] + dx, i[:, 1] + dy, i[:, 2] + dz, seed)
    return out * 2 - 1


def capped_cone(p, a, b, ra, rb):
    """Exact SDF of a tapered cylinder with FLAT ends: radius ra at a, rb at b (iq's sdCappedCone).
    `round_cone` is a capsule (spheres at both ends); this is what walls, drums and roofs need."""
    ba = b - a
    baba = ba @ ba
    pa = p - a
    paba = (pa @ ba) / baba
    papa = np.einsum("ij,ij->i", pa, pa)
    x = np.sqrt(np.maximum(papa - paba * paba * baba, 0.0))
    cax = np.maximum(0.0, x - np.where(paba < 0.5, ra, rb))
    cay = np.abs(paba - 0.5) - 0.5
    rba = rb - ra
    k = rba * rba + baba
    f = np.clip((rba * (x - ra) + paba * baba) / k, 0.0, 1.0)
    cbx = x - ra - f * rba
    cby = paba - f
    s = np.where((cbx < 0.0) & (cay < 0.0), -1.0, 1.0)
    return s * np.sqrt(np.minimum(cax * cax + cay * cay * baba, cbx * cbx + cby * cby * baba))
