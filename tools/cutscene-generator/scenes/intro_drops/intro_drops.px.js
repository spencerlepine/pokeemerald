// Intro scene 1, redrawn for Star Wars: KYBER.
// Emerald: water drops fall from jungle leaves into a dark pool, the GAME FREAK logo forms, then the
//          camera pans up past bushes and tall grass to mountains, and a Flygon silhouette flies off.
// Here:    condensation drips from a canyon overhang into a shadowed pool before dawn (no logo: the
//          owner chose "just the drip"), then the camera rises past the canyon walls, boulders and a
//          dune crest to the twin suns coming up over the Jundland flats, and a transport ship flies off.
//
// Layout follows the game exactly (src/intro.c, Task_Scene1_Load / Task_Scene1_PanUp):
//   one tileset (bg.png, 8-bit PNG holding 16 BG palettes) + one map per BG, 256x256 each:
//   BG0 bg0_map.bin bank 3  front: overhangs on top, dark floor rim at rows 175+   VOFS 40 -> -218 (0.75 px/frame)
//   BG1 bg1_map.bin bank 3  canyon walls on top, the dark pool basin below row 110  VOFS 24 -> -148 (0.5 px/frame)
//   BG2 bg2_map.bin bank 2  dune crest at rows 25-50, boulders below               VOFS 80 -> -49  (0.375 px/frame)
//   BG3 bg3_map.bin bank 5  dawn sky, suns, mesas, the flats                         VOFS 0 (static)
//   The pan runs game frames 560-904 (gIntroFrameCounter); the map's second screen block is empty, so a
//   layer that slides past its bottom simply leaves the screen.
//   OBJ: flygon.png (64x32, one color, affine-scaled as it flies off) becomes the ship.
// Water drops, ripples and sparkles (drops_logo.png, sparkle.png) are plain water and stay Emerald's.
//
// Build: node ../../bin/pxl.js build intro_drops.px.js   (game files land in out/game/)

include("../../gba/screen.px.js")
const D = "graphics/intro/scene_1/"

// ------------------------------------------------------------------ palettes (GBA steps of 8)

// Bank 3: BG0 + BG1, the canyon before dawn. Rock warms toward the top, where the dawn light reaches.
const B3 = [
  "#000000", // 0  transparent
  "#100818", // 1  pool black
  "#181828", // 2  deep shadow
  "#282038", // 3  shadow violet
  "#383048", // 4  rock in shadow
  "#504058", // 5  rock dark
  "#705060", // 6  rock mid (cool)
  "#906068", // 7  rock mid (warm)
  "#b07870", // 8  rock lit
  "#d09880", // 9  dawn rim light
  "#f0c8a0", // 10 brightest rim
  "#202840", // 11 water, dark
  "#384868", // 12 water, mid
  "#587898", // 13 water glint
  "#403040", // 14 rock crevice
  "#683848", // 15 warm crevice
]
// Bank 2: BG2, boulders and the dune crest in the first light.
const B2 = [
  "#000000", "#201828", "#503038", "#805040", "#b07850", "#d8a070", "#f0c890", "#f8e0b0",
  "#a06850", "#784838", "#c08868", "#000000", "#000000", "#000000", "#000000", "#000000",
]
// Bank 5: BG3, the sky and the flats.
const B5 = [
  "#000000", // 0
  "#283868", // 1  sky top
  "#485890", // 2
  "#7878a8", // 3
  "#b090a8", // 4
  "#e0a8a0", // 5
  "#f8c8a0", // 6
  "#f8e0b8", // 7  horizon
  "#f8f8e0", // 8  the suns
  "#f8e8c0", // 9  sun halo
  "#a07888", // 10 far mesas
  "#886878", // 11 mesa shade
  "#e8b880", // 12 flats, lit
  "#d0a070", // 13 flats
  "#b88860", // 14 flats, far shade
  "#c09088", // 15 mesa lit edge
]
// OBJ palette for the drops and ripples (drops.pal): Emerald's leaf-green water, made cool and clear.
const DROPS = ["#000000", "#000000", "#000000", "#000000", "#000000", "#000000",
  "#102038", "#203858", "#385078", "#506890", "#6880a8", "#8098b8", "#a0b8d0", "#c0d0e0", "#e0e8f0", "#f8f8f8"]
// OBJ palette for the ship (flygon.png): one dark silhouette color, as Emerald's.
const SHIP = ["#000000", "#383040", "#000000", "#000000", "#000000", "#000000", "#000000", "#000000",
  "#000000", "#000000", "#000000", "#000000", "#000000", "#000000", "#000000", "#000000"]

// ------------------------------------------------------------------ helpers

// Emerald's gradients: flat bands with an 8-row 50% checker between neighbours.
function bands(c, y, rows) {
  for (let i = 0; i < rows.length; i++) {
    const [k, h] = rows[i]
    c.rect(0, y, 256, h, k); y += h
    if (i + 1 < rows.length) { c.dither(0, y, 256, 8, k, rows[i + 1][0], 0.5); y += 8 }
  }
  return y
}
// A ragged edge: the height at each x, from a few sines (tileable over 256).
function edge(x, base, amp, seed) {
  const t = (x / 256) * Math.PI * 2
  return Math.round(base + amp * (0.55 * Math.sin(t * 2 + seed) + 0.3 * Math.sin(t * 5 + seed * 2.1) + 0.15 * Math.sin(t * 11 + seed * 0.7)))
}

// ------------------------------------------------------------------ BG3: dawn sky, twin suns, mesas, the flats

use(B5)
scene("bg3", { w: 256, h: 256 }, (c) => {
  const y = bands(c, 0, [[1, 6], [2, 6], [3, 6], [4, 6], [5, 6], [6, 6], [7, 10]])
  c.rect(0, y, 256, 256 - y, 7)
  // the twin suns just clearing the horizon, left of center (light from the upper left)
  c.circ(78, 60, 9, 9); c.circ(78, 60, 7, 8)
  c.circ(100, 64, 5, 9); c.circ(100, 64, 4, 8)
  // far mesas (flat tops, sunlit left edges)
  for (const [x, w, top] of [[0, 40, 58], [44, 22, 62], [128, 56, 54], [196, 30, 60], [232, 34, 57]]) {
    const s = Math.round((70 - top) / 3)
    c.poly([x, 72, x + s, top, x + w - s, top, x + w, 72], 10)
    c.line(x, 71, x + s, top, 15); c.hline(x + s, top, Math.max(1, w - 2 * s), 15)
    c.poly([x + w - s - 3, top + 1, x + w - s, top, x + w, 72, x + w - 6, 72], 11)
  }
  c.rect(0, 70, 256, 4, 10)
  // the flats: far shade, then lit sand, banded toward the viewer
  bands(c, 74, [[14, 8], [13, 16], [12, 200]])
  // a few low ridges on the flats
  for (const [x, yy, w] of [[20, 100, 50], [140, 112, 70], [90, 130, 40], [200, 138, 50]]) {
    c.hline(x, yy, w, 13); c.hline(x + 4, yy - 1, w - 8, 13)
  }
})

// ------------------------------------------------------------------ shading helpers

// Point-in-polygon for flat [x0,y0,x1,y1,...] lists.
function inPoly(pts, x, y) {
  let inside = false
  for (let i = 0, j = pts.length - 2; i < pts.length; j = i, i += 2) {
    const xi = pts[i], yi = pts[i + 1], xj = pts[j], yj = pts[j + 1]
    if ((yi > y) !== (yj > y) && x < ((xj - xi) * (y - yi)) / (yj - yi) + xi) inside = !inside
  }
  return inside
}
// Paint a rock mass from a mask, lit from above-left by the dawn: a bright rim where the top meets
// the sky, warm bands below it, a dark underside, a checker seam between each step (Emerald's way).
//   ramp: colors from the lit rim down into the shade; under: the underside color.
function shadeMass(c, w, h, mask, ramp, under, seed) {
  const r = c.rng(seed)
  for (let x = 0; x < w; x++) {
    let depth = -1
    for (let y = 0; y < h; y++) {
      if (!mask(x, y)) { depth = -1; continue }
      depth++
      let below = 0
      while (below < 3 && mask(x, y + below + 1)) below++
      const leftOpen = !mask(x - 1, y)
      let k = Math.min(ramp.length - 1, Math.floor(depth / 3))
      const seam = depth % 3 === 2 && k + 1 < ramp.length && (x + y) % 2 === 0
      let col = ramp[seam ? k + 1 : k]
      if (leftOpen && depth > 0 && k > 0) col = ramp[k - 1]
      if (below < 2) col = under
      if (below < 1 && (x + y) % 2) col = under
      c.px(x, y, col)
    }
  }
  return r
}

// ------------------------------------------------------------------ BG2: dune crest and boulders

use(B2)
// A sandstone boulder sitting on the ground at `base`: shade body, lit cap to the upper left, a
// highlight, a cast shadow to the lower right on the sand.  tone: [shadow, shade, mid, lit, glint]
function boulder(c, cx, base, rx, ry, tone) {
  const [sh, d, m, l, g] = tone, cy = base - ry
  const inE = (x, y, ex, ey, ax, ay) => ((x - ex) / ax) ** 2 + ((y - ey) / ay) ** 2 <= 1
  for (let y = cy - ry - 1; y <= base + 2; y++) for (let x = cx - rx - 2; x <= cx + rx + 8; x++) {
    if (inE(x, y, cx + 4, base, rx + 2, 3) && y >= base - 1 && !inE(x, y, cx, cy, rx, ry)) c.px(x, y, sh)
  }
  for (let y = cy - ry; y <= base; y++) for (let x = cx - rx; x <= cx + rx; x++) {
    if (!inE(x, y, cx, cy, rx, ry)) continue
    const u = (x - cx) / rx, v = (y - cy) / ry, lit = -0.7 * u - 0.9 * v
    let col = d
    if (lit > -0.35) col = (lit > -0.15 || (x + y) % 2) ? m : d
    if (lit > 0.45) col = (lit > 0.6 || (x + y) % 2) ? l : m
    if (lit > 0.95) col = g
    if (y >= base - 1) col = sh
    c.px(x, y, col)
  }
}
scene("bg2", { w: 256, h: 256 }, (c) => {
  // dune crest: a sharp lit lip, the windward face, shade falling into the boulder field
  for (let x = 0; x < 256; x++) {
    const top = edge(x, 34, 7, 1.3)
    c.vline(x, top, 60 - top, 6)
    c.px(x, top, 7); if (x % 3) c.px(x, top + 1, 7)
  }
  c.dither(0, 44, 256, 8, 6, 5, 0.5)
  c.rect(0, 52, 256, 30, 5)
  c.dither(0, 82, 256, 8, 5, 4, 0.5)
  c.rect(0, 90, 256, 166, 4)
  // wind ripples: short lit strokes with a shade line under, scattered on the face
  const rw = c.rng(9)
  for (let i = 0; i < 16; i++) {
    const x = Math.floor(rw() * 240), y = 44 + Math.floor(rw() * 30), w = 6 + Math.floor(rw() * 10), top = y < 52 ? 7 : 6, low = y < 52 ? 5 : 10
    c.hline(x, y, w, top); c.hline(x + 2, y + 1, w - 3, low)
  }
  // back row of boulders on the lit sand, front row darker as it nears the canyon
  const r = c.rng(5)
  const back = [], front = []
  for (let i = 0; i < 8; i++) back.push([i * 33 + 10 + Math.floor(r() * 12), 80 + Math.floor(r() * 6), 8 + Math.floor(r() * 5), 6 + Math.floor(r() * 3)])
  for (let i = 0; i < 7; i++) front.push([i * 38 + 6 + Math.floor(r() * 14), 122 + Math.floor(r() * 8), 13 + Math.floor(r() * 6), 9 + Math.floor(r() * 4)])
  back.sort((a, b) => a[1] - b[1]).forEach(([x, b, rx, ry]) => boulder(c, x, b, rx, ry, [9, 8, 10, 5, 6]))
  // pebbles
  for (let i = 0; i < 24; i++) { const x = Math.floor(r() * 256), y = 92 + Math.floor(r() * 20); c.px(x, y, 9); c.px(x - 1, y - 1, 5) }
  c.dither(0, 104, 256, 8, 4, 3, 0.5)
  c.rect(0, 112, 256, 24, 3)
  front.sort((a, b) => a[1] - b[1]).forEach(([x, b, rx, ry]) => boulder(c, x, b, rx, ry, [2, 9, 8, 4, 5]))
  c.dither(0, 136, 256, 8, 3, 2, 0.5)
  c.rect(0, 144, 256, 112, 2)
  c.dither(0, 154, 256, 8, 2, 1, 0.5)
  c.rect(0, 162, 256, 94, 1)
})

// ------------------------------------------------------------------ BG1: canyon walls over the pool

use(B3)
scene("bg1", { w: 256, h: 256 }, (c) => {
  const r = c.rng(11)
  const rim = (x) => edge(x, 12, 8, 0.4)
  // strata: ledge lines; each band's rock gets darker and cooler the deeper into the canyon it is
  const ledges = [24, 38, 54, 70, 86, 102]
  const tone = [8, 7, 7, 6, 5, 5, 4]
  const ledgeY = (k, x) => edge(x, ledges[k], 2, k * 1.7 + 0.3)
  for (let x = 0; x < 256; x++) {
    const top = rim(x)
    for (let y = top; y < 112; y++) {
      let k = 0
      while (k < ledges.length && y >= ledgeY(k, x)) k++
      const base = tone[k], up = y - (k ? ledgeY(k - 1, x) : top)
      let col = base
      if (up === 0) col = k ? Math.min(10, base + 1) : 10          // lit ledge top / the rim
      else if (up === 1 && !k) col = 9
      else if (up === 1) col = 14                                  // the ledge's shadow
      else if (up === 2 && (x + y) % 2) col = 14
      c.px(x, y, col)
    }
  }
  // vertical joints: irregular cracks, some running the full band, some stopping short, lit on the left
  for (let k = 0; k <= ledges.length; k++) {
    const y0 = k ? ledges[k - 1] + 3 : 22, y1 = k < ledges.length ? ledges[k] - 1 : 110
    let x = Math.floor(r() * 40)
    while (x < 256) {
      const yEnd = r() < 0.5 ? y1 : y0 + Math.floor((y1 - y0) * (0.4 + r() * 0.4))
      let xx = x
      for (let y = y0; y < yEnd; y++) {
        if (r() < 0.2) xx += r() < 0.5 ? -1 : 1
        c.px(xx, y, 14); if (y & 1) c.px(xx - 1, y, Math.min(9, tone[k] + 1))
      }
      x += 34 + Math.floor(r() * 50)
    }
  }
  // weathering specks and a few warm stains running down from the ledges
  for (let i = 0; i < 90; i++) {
    const x = Math.floor(r() * 256), y = 18 + Math.floor(r() * 92)
    if (c.is(x, y, "5678")) c.px(x, y, c.is(x, y, "78") ? 15 : 14)
  }
  for (let i = 0; i < 14; i++) {
    const x = Math.floor(r() * 256), k = Math.floor(r() * ledges.length), len = 4 + Math.floor(r() * 9)
    c.clip((xx, yy) => c.is(xx, yy, "45678"), () => { for (let y = ledges[k] + 3; y < ledges[k] + 3 + len; y += 1) if (y % 2 || y < ledges[k] + 6) c.px(x, y, 15) })
  }
  // the basin: wet rock, darkening to the pool
  c.dither(0, 110, 256, 8, 4, 3, 0.5)
  c.rect(0, 118, 256, 138, 3)
  c.dither(0, 130, 256, 8, 3, 2, 0.5)
  c.rect(0, 138, 256, 118, 2)
  // the pool: a ragged shore, dark water that holds the dawn sky in a few streaks
  const shore = (x, y) => {
    const dx = (x - 128) / 122, dy = (y - 152) / (24 + 2 * Math.sin(x / 9) + 1.5 * Math.sin(x / 4 + 1))
    return dx * dx + dy * dy <= 1
  }
  for (let y = 120; y < 184; y++) for (let x = 0; x < 256; x++) {
    if (!shore(x, y)) { if (shore(x, y - 1) || shore(x, y + 2)) c.px(x, y, 4); continue }
    const edgeRow = !shore(x, y - 1) || !shore(x, y - 2)
    let col = 11
    if (edgeRow) col = 1                                           // the bank's shadow on the water
    else if (y > 168) col = (x + y) % 2 ? 11 : 1
    c.px(x, y, col)
  }
  // sky reflections: broken horizontal streaks, brightest toward the middle
  for (const [x, y, w, k] of [[70, 140, 46, 12], [130, 143, 30, 12], [92, 147, 60, 12], [56, 152, 22, 12], [176, 150, 34, 12],
    [104, 141, 14, 13], [120, 148, 8, 13], [150, 156, 26, 12], [84, 160, 40, 12], [188, 162, 18, 12], [40, 164, 16, 12]]) {
    for (let i = 0; i < w; i++) if ((i + y) % 7 !== 0) c.px(x + i, y, k)
  }
  // a lit lip of wet stone along the far bank
  for (let x = 12; x < 244; x++) for (let y = 120; y < 152; y++) if (!shore(x, y) && shore(x, y + 1) && y < 140) { c.px(x, y, 7); c.px(x, y - 1, 5); break }
})

// ------------------------------------------------------------------ BG0: overhangs and the floor rim

const LOBE_L = [0, 6, 12, 1, 28, 4, 46, 0, 66, 5, 84, 11, 96, 19, 92, 26, 76, 30, 62, 33, 52, 37, 44, 35, 34, 40, 18, 46, 0, 52]
// The right lobe's underside is the big drop's path (traced from the ROM: it slides from (236,-14) down
// to hang at screen (120,41), i.e. bg0 row 81 at the start VOFS of 40), so the drop runs along the rock.
const LOBE_R = [150, 12, 166, 3, 190, 0, 214, 4, 236, 0, 256, 2, 256, 30, 240, 33, 222, 39, 204, 45, 187, 49, 172, 51, 160, 53,
  150, 56, 142, 59, 135, 62, 130, 65, 125, 70, 122, 76, 120, 80, 118, 76, 117, 68, 121, 58, 128, 48, 136, 38, 142, 28]
scene("bg0", { w: 256, h: 256 }, (c) => {
  const lobe = (x, y) => x >= 0 && x < 256 && y >= 0 && (inPoly(LOBE_L, x + 0.5, y + 0.5) || inPoly(LOBE_R, x + 0.5, y + 0.5))
  shadeMass(c, 256, 100, lobe, [10, 8, 7, 6, 5, 5, 4, 4, 4, 4, 4], 3, 3)
  // drip tips: short stone teeth at x 48 (row 40, drop 1) and x 196 (row 50, drop 2), wet highlights
  for (const [x, y0, y1] of [[48, 34, 40], [196, 44, 50]]) {
    for (let y = y0; y <= y1; y++) { c.px(x, y, 4); if (y < y1 - 3) c.px(x + 1, y, 3) }
    c.px(x, y1 + 1, 13); c.px(x - 1, y0 + 2, 6)
  }
  // cracks and pits in the lobes
  const r = c.rng(21)
  for (let i = 0; i < 40; i++) {
    const x = Math.floor(r() * 256), y = 4 + Math.floor(r() * 70)
    if (lobe(x, y) && lobe(x + 2, y + 2) && c.is(x, y, "4567")) { c.px(x, y, 14); c.px(x + 1, y + 1, 14); if (r() < 0.5) c.px(x + 2, y + 1, 3) }
  }
  // floor rim: a row of dark foreground rocks, rounded tops caught by the faintest light
  const lumps = []
  for (let x = -10; x < 270; x += 16 + Math.floor(r() * 18)) lumps.push([x, 12 + Math.floor(r() * 10), 186 + Math.floor(r() * 10)])
  const floorTop = (x) => Math.min(...lumps.map(([lx, rx, ty]) => {
    const d = (x - lx) / rx
    return d * d <= 1 ? ty - Math.round(Math.sqrt(1 - d * d) * 8) : 999
  }), 200)
  const floor = (x, y) => y >= floorTop(x)
  for (let x = 0; x < 256; x++) {
    const top = floorTop(x)
    for (let y = top; y < 256; y++) {
      const d = y - top
      let col = d === 0 ? 5 : d === 1 ? 4 : d < 5 ? ((x + y) % 2 ? 3 : 4) : d < 12 ? 3 : d < 20 ? ((x + y) % 2 ? 2 : 3) : d < 30 ? 2 : (d < 38 && (x + y) % 2) ? 2 : 1
      c.px(x, y, col)
    }
  }
  // seams between the lumps
  for (const [lx] of lumps) for (let y = floorTop(lx + 1); y < floorTop(lx + 1) + 10; y++) if (floor(lx, y)) c.px(lx, y, 1)
})

// ------------------------------------------------------------------ OBJ: the ship (flygon.png)

use(SHIP)
// Seen from below as it flies off: a transport with swept wings and twin engines. Symmetric, one color.
sprite("ship", { w: 64, h: 32, mx: true }, `
................................
................................
................................
................................
...............................1
..............................11
.............................111
1111.........................111
.1111111....................1111
..111111111.................1111
....11111111111..........1111111
......111111111111111111111.1111
........11111111111111111111.111
...........1111111111111111.1111
..............11111111111111111.
.................111111111111111
...................1111111111111
....................111111111111
.....................11111111111
......................1111111111
.......................111111111
........................11111111
.........................1111111
..........................111111
...........................11111
............................1111
.............................111
..............................11
...............................1
................................
................................
................................`)

// ------------------------------------------------------------------ game files

gba(D + "bg.png", {
  bg: ["bg0", "bg1", "bg2", "bg3"], slots: [3, 3, 2, 5], banks: { 2: B2, 3: B3, 5: B5 },
  maps: [D + "bg0_map.bin", D + "bg1_map.bin", D + "bg2_map.bin", D + "bg3_map.bin"],
})
gba(D + "flygon.png", { image: "ship", pal: SHIP })
gba(D + "drops.pal", { pal: DROPS })

// ------------------------------------------------------------------ preview: the pan at its real speeds

// Each layer's VOFS: start - speed * t over the 344-frame pan; rows past 255 are empty (cleared block).
gbaPan("pan_new", ["bg3", "bg2", "bg1", "bg0"])
function gbaPan(name, layers) {
  const start = [0, 80, 24, 40], speed = [0, 0.375, 0.5, 0.75], frames = 344, step = 8
  anim(name, { w: 240, h: 160, frames: Math.ceil(frames / step), fps: 60 / step }, (c) => {
    const t = c.frame * step
    layers.forEach((n, i) => {
      const v = Math.floor(start[i] - speed[i] * t)
      for (const off of [-512, 0, 512]) if (-v + off > -256 && -v + off < 160) c.stamp(n, 0, -v + off)
    })
  })
}
