// Volume shading for the scene 3 titans. A figure is a set of ellipsoids ("blobs"); every pixel takes
// the blob standing highest there, gets that blob's surface normal, and is shaded by one light from
// the upper left into a ramp of palette keys. Grooves (darker lines where blobs meet) and an outline
// come from the depth buffer, so the result has real volume at 1x without any smoothing step.
//
//   sculpt(c, blobs, { light, ramps })
//     blob: { cx, cy, rx, ry, rz?, ramp, rot? (degrees), z? (base height, stacks it in front) }
//     ramp: array of palette keys, dark -> light (6 bands)
//   Returns { depth(x, y), who(x, y) } for drawing details on top.

const SC_LIGHT = [-0.45, -0.7, 0.56]   // from the upper left, toward the viewer

function sculpt(c, blobs, opts = {}) {
  const L = opts.light ?? SC_LIGHT, ll = Math.hypot(...L), lx = L[0] / ll, ly = L[1] / ll, lz = L[2] / ll
  const W = c.w, H = c.h
  const depth = new Float32Array(W * H).fill(-1e9), who = new Int16Array(W * H).fill(-1)
  const nx = new Float32Array(W * H), ny = new Float32Array(W * H), nz = new Float32Array(W * H)
  blobs.forEach((b, i) => {
    const rz = b.rz ?? Math.min(b.rx, b.ry), base = b.z ?? 0, a = ((b.rot ?? 0) * Math.PI) / 180, ca = Math.cos(a), sa = Math.sin(a)
    const R = Math.max(b.rx, b.ry) + 1
    for (let y = Math.max(0, Math.floor(b.cy - R)); y <= Math.min(H - 1, Math.ceil(b.cy + R)); y++)
      for (let x = Math.max(0, Math.floor(b.cx - R)); x <= Math.min(W - 1, Math.ceil(b.cx + R)); x++) {
        const dx = x + 0.5 - b.cx, dy = y + 0.5 - b.cy
        const u = (dx * ca + dy * sa) / b.rx, v = (-dx * sa + dy * ca) / b.ry
        const q = 1 - u * u - v * v
        if (q <= 0) continue
        const z = base + rz * Math.sqrt(q), k = y * W + x
        if (z <= depth[k]) continue
        depth[k] = z; who[k] = i
        // gradient of the ellipsoid in local coords, rotated back
        let gx = u / b.rx, gy = v / b.ry, gz = Math.sqrt(q) / rz
        const wx = gx * ca - gy * sa, wy = gx * sa + gy * ca
        const n = Math.hypot(wx, wy, gz) || 1
        nx[k] = wx / n; ny[k] = wy / n; nz[k] = gz / n
      }
  })
  const bands = opts.bands ?? [0.72, 0.45, 0.18, -0.1, -0.42]
  for (let y = 0; y < H; y++) for (let x = 0; x < W; x++) {
    const k = y * W + x
    if (who[k] < 0) continue
    const b = blobs[who[k]], ramp = b.ramp
    const d = nx[k] * lx + ny[k] * ly + nz[k] * lz
    let i = 0
    while (i < bands.length && d < bands[i]) i++
    let key = ramp[Math.max(0, ramp.length - 1 - i)]
    // a crease where a lower blob meets a higher one in front: darken one step
    let crease = false
    for (const [ox, oy] of [[1, 0], [0, 1], [-1, 0], [0, -1]]) {
      const xx = x + ox, yy = y + oy
      if (xx < 0 || yy < 0 || xx >= W || yy >= H) continue
      const j = yy * W + xx
      if (who[j] >= 0 && who[j] !== who[k] && depth[j] > depth[k] + (opts.creaseDepth ?? 2.5)) crease = true
    }
    if (crease) key = ramp[Math.max(0, ramp.indexOf(key) - 1)]
    c.px(x, y, key)
  }
  return {
    depth: (x, y) => (x < 0 || y < 0 || x >= W || y >= H ? -1e9 : depth[y * W + x]),
    who: (x, y) => (x < 0 || y < 0 || x >= W || y >= H ? -1 : who[y * W + x]),
    inside: (x, y) => x >= 0 && y >= 0 && x < W && y < H && who[y * W + x] >= 0,
  }
}

// A 1 px outline of `key` around everything opaque in the canvas.
function outlineAll(c, key) {
  const W = c.w, H = c.h, op = []
  for (let y = 0; y < H; y++) for (let x = 0; x < W; x++) if (c.is(x, y, "*")) op.push(x, y)
  const seen = new Set(op.map((v, i, a) => (i % 2 ? null : a[i] + "," + a[i + 1])).filter(Boolean))
  for (let i = 0; i < op.length; i += 2) {
    const x = op[i], y = op[i + 1]
    for (const [ox, oy] of [[1, 0], [-1, 0], [0, 1], [0, -1]]) {
      const xx = x + ox, yy = y + oy
      if (xx < 0 || yy < 0 || xx >= W || yy >= H || seen.has(xx + "," + yy)) continue
      c.px(xx, yy, key); seen.add(xx + "," + yy)
    }
  }
}

// A chain of blobs along a polyline: [[x, y, r], ...] -> blobs every `step` px, radii interpolated.
function chain(pts, ramp, step = 3, squash = 1, extra = {}) {
  const out = []
  for (let i = 0; i + 1 < pts.length; i++) {
    const [x0, y0, r0] = pts[i], [x1, y1, r1] = pts[i + 1]
    const n = Math.max(1, Math.ceil(Math.hypot(x1 - x0, y1 - y0) / step))
    for (let k = 0; k < n; k++) { const t = k / n; const r = r0 + (r1 - r0) * t; out.push({ cx: x0 + (x1 - x0) * t, cy: y0 + (y1 - y0) * t, rx: r, ry: r * squash, rz: r, ramp, ...extra }) }
  }
  const [x, y, r] = pts[pts.length - 1]
  out.push({ cx: x, cy: y, rx: r, ry: r * squash, rz: r, ramp, ...extra })
  return out
}
