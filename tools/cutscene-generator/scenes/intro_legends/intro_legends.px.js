// Intro scene 3, redrawn for Star Wars: KYBER.
// Emerald: a Poké Ball spins and zooms, Groudon roars on red rock, Kyogre surfaces in the sea, storm
//          clouds gather and Rayquaza breaks the fight up.
// Here:    a capture pod spins and zooms, GREATKRAYT rears out of the desert sand, SANDO surfaces in
//          the sea, and the EXOGORTH ends it. All camera moves, flashes and palette pulses stay
//          Emerald's (src/intro.c, Task_Scene3_*); only the art changes.
//
// Layout (src/intro.c + src/data/graphics/intro_scene.h):
//   pokeball.png + pokeball_map.bin  affine 8bpp 256x256, own palette          -> the capture pod
//   groudon.png  + groudon.bin       affine 8bpp 512x512, bank 1 of bg.pal     -> GREATKRAYT, 3 poses
//     Each pose sits where Groudon's did (the camera cuts between them to animate the roar):
//     A neutral (293,1)  B reared, jaws open (118,123)  C coiled low (39,354).
//     Index 15 is the glow: intro.c pulses bank 1 entry 15 through bank 15 (blue -> red).
//   legend_bg.png + groudon_bg.bin / kyogre_bg.bin  4bpp text BG behind them: sand (bank 3), sea (bank 4)
//   bg.pal                           the 16 x 16 BG palette for the whole scene
//
// Build: node ../../bin/pxl.js build intro_legends.px.js   (game files land in out/game/)

include("../../gba/screen.px.js")
const D = "graphics/intro/scene_3/"

// ------------------------------------------------------------------ palettes (GBA steps of 8)

// bg.pal: banks 0, 2, 4-7 and 12-15 are Emerald's (kyogre, clouds, Rayquaza and the glow ramp), truncated to
// GBA steps exactly as the game reads them. Bank 1 (the krayt) and bank 3 (the sand) are new.
const V = (s) => s.split(" ").map((h) => "#" + h)
const BANKS = {
  0: V("000000 000000 000000 000000 000000 000000 000000 000000 000000 000000 000000 000000 000000 000000 000000 000000"),
  // 1  GREATKRAYT: 1 body black, 2 hide rim, 3 hide plate, 14 eye, 15 the glow (pulsed by the game)
  1: V("8890f8 000000 302830 484048 702028 e88000 e88800 e89000 e89800 e8a000 e8a800 e8b000 e8b800 e8c000 f8f8f8 0020c8"),
  2: V("8890f8 000000 0000f8 0810f8 1828f8 2838f8 3850f8 4860f8 5878f8 6890f8 000000 000000 000000 000000 f8f8f8 b00000"),
  // 3  sand: 1 deep shade .. 6 lit crest, 7-8 pebbles
  3: V("000000 603820 905830 b07840 c89050 d8a860 e8c070 f8d888 784828 a87048 000000 000000 000000 000000 000000 000000"),
  4: V("000000 002850 f8f8f8 000000 000000 000000 000000 000000 000000 88a8f8 6890d8 5078b8 306098 184878 003060 b00000"),
  5: V("000000 000000 001000 507060 709080 80a890 98b0a8 f8f8c0 f8f078 b0a060 609838 78a080 a03830 a8c8f0 f8f078 000000"),
  6: V("8890f8 000000 284830 507060 709080 80a890 98b0a8 a8c8f0 c0e0f8 d0f0f8 e8f8f8 f8c068 f8d080 d8d898 f8f078 f8f8c0"),
  7: V("000000 485050 586068 687880 7888a0 88a0b8 98b0d0 a8c8f0 000000 000000 e8f8f8 f8c068 f8d080 f8d898 f8f078 f8f8c0"),
  12: V("000000 485050 584848 684040 784038 883830 a03830 000000 000000 000000 000000 000000 000000 000000 000000 000000"),
  13: V("000000 485050 687058 889060 b0b068 d0d070 f8f078 000000 000000 000000 000000 000000 000000 000000 000000 000000"),
  14: V("000000 485050 687070 889090 b0b0b0 d0d0d0 f8f8f8 000000 000000 000000 000000 000000 000000 000000 000000 000000"),
  15: V("000000 0020c8 2018a0 401078 680850 880028 b00000 000000 000000 000000 000000 000000 000000 000000 000000 000000"),
}
// The capture pod's own palette (pokeball.png): 0 is the backdrop (white, as Emerald's).
const POD = V("f8f8f8 000000 302818 584830 887050 b88050 e0a070 f8d0a0 383848 585870 8088a8 b0b8d0 1860c0 58b0f8 c0f0f8 f8f8f8")

// ------------------------------------------------------------------ the capture pod

use(POD)
scene("pod", { w: 256, h: 256 }, (c) => {
  const cx = 128, cy = 128, R = 63
  const inC = (x, y, r) => (x - cx + 0.5) ** 2 + (y - cy + 0.5) ** 2 <= r * r
  for (let y = 0; y < 256; y++) for (let x = 0; x < 256; x++) {
    if (!inC(x, y, R + 1)) continue
    if (!inC(x, y, R - 1)) { c.px(x, y, 1); continue }
    const top = y < cy - 3, bot = y > cy + 3
    // shading: lit from the upper left, flat bands so it reads when the game zooms in 6x
    const l = ((x - cx) * -0.6 + (y - cy) * -0.8) / R
    let k
    if (top) k = l > 0.45 ? 7 : l > 0.05 ? 6 : l > -0.4 ? 5 : 4
    else if (bot) k = l > 0.1 ? 11 : l > -0.35 ? 10 : 9
    else k = 1
    c.px(x, y, k)
  }
  // the seam band round the middle, with clamp bolts
  c.rect(cx - R, cy - 3, 2 * R + 1, 7, 8); c.hline(cx - R, cy - 3, 2 * R + 1, 1); c.hline(cx - R, cy + 3, 2 * R + 1, 1)
  for (const bx of [-50, -36, 36, 50]) { c.rect(cx + bx - 1, cy - 1, 3, 3, 10); c.px(cx + bx - 1, cy - 1, 11) }
  // panel lines on the shell
  for (const [x0, y0, x1, y1] of [[cx - 44, cy - 44, cx - 22, cy - 22], [cx + 44, cy - 44, cx + 22, cy - 22], [cx - 44, cy + 44, cx - 22, cy + 22], [cx + 44, cy + 44, cx + 22, cy + 22]])
    c.line(x0, y0, x1, y1, y0 < cy ? 4 : 8)
  c.clip((x, y) => y < cy - 3, () => c.ring(cx, cy, 46, 4))
  c.clip((x, y) => y > cy + 3, () => c.ring(cx, cy, 46, 8))
  // the lens: a dark collar, a glowing kyber eye, a hard glint
  c.circ(cx, cy, 24, 1); c.circ(cx, cy, 22, 8); c.circ(cx, cy, 19, 1)
  c.circ(cx, cy, 17, 12); c.circ(cx - 2, cy - 2, 12, 13); c.circ(cx - 5, cy - 5, 5, 14)
  c.rect(cx - 9, cy - 10, 4, 3, 15); c.px(cx - 10, cy - 8, 15)
})

// ------------------------------------------------------------------ GREATKRAYT

use(BANKS[1])
// The body is a chain of discs along a spine; plates, spikes, horns and the glow follow the spine.
function spinePts(pts, step = 1) {
  const out = []
  for (let i = 0; i + 1 < pts.length; i++) {
    const [x0, y0, r0] = pts[i], [x1, y1, r1] = pts[i + 1]
    const n = Math.max(1, Math.ceil(Math.hypot(x1 - x0, y1 - y0) / step))
    for (let k = 0; k < n; k++) { const t = k / n; out.push([x0 + (x1 - x0) * t, y0 + (y1 - y0) * t, r0 + (r1 - r0) * t]) }
  }
  out.push(pts[pts.length - 1])
  return out
}
function krayt(c, ox, oy, pose) {
  const BODY = [[60, 58, 20], [82, 62, 23], [104, 60, 20], [124, 54, 16], [142, 45, 11], [156, 33, 7], [165, 20, 4], [170, 10, 1]]
  const P = {
    // the neck (spine start, [x, y, radius]) and head differ per pose; the body and tail are shared
    // so the three poses share tiles (an affine BG holds 256)
    A: { neck: [[28, 26, 12], [44, 44, 16]], head: [14, 16], jaw: 0.25, tilt: 0.15 },
    B: { neck: [[32, 18, 12], [42, 38, 16]], head: [24, 6], jaw: 0.9, tilt: -0.45 },
    C: { neck: [[26, 48, 12], [42, 56, 16]], head: [10, 44], jaw: 0.1, tilt: 0.35 },
  }[pose]
  const at = (list) => spinePts(list.map(([x, y, r]) => [x + ox, y + oy, r]))
  const body = at(BODY), neck = at([...P.neck, BODY[0]])
  const disc = (pts) => { for (const [x, y, r] of pts) c.circ(Math.round(x), Math.round(y), Math.max(1, Math.round(r)), 1) }
  // legs first (behind): thick clawed forelimbs planted in the sand (shared)
  for (const [lx, ly] of [[52, 72], [78, 80]]) {
    const x = ox + lx, y = oy + ly
    c.line(x, y - 12, x - 7, y + 3, 1, 6); c.line(x - 7, y + 3, x - 15, y + 5, 1, 4)
    for (const d of [-18, -13, -8]) c.line(x - 11, y + 5, x + d, y + 8, 1, 1)
  }
  disc(body); disc(neck)
  // dorsal spikes along the top of the spine, biggest over the shoulders
  const spikes = (pts, every, size) => {
    for (let i = every; i < pts.length - 4; i += every) {
      const [x, y, r] = pts[i], [x2, y2] = pts[Math.min(pts.length - 1, i + 3)]
      let ux = -(y2 - y), uy = x2 - x; const nl = Math.hypot(ux, uy) || 1; ux /= nl; uy /= nl
      if (uy > 0) { ux = -ux; uy = -uy }
      const h = size + r * 0.35, bx = x + ux * (r - 1), by = y + uy * (r - 1)
      c.poly([Math.round(bx - 3), Math.round(by + 1), Math.round(bx + 3), Math.round(by + 1), Math.round(bx + ux * h + 3), Math.round(by + uy * h)], 1)
    }
  }
  spikes(body, 8, 3); spikes(neck, 8, 2)
  // hide: a rim of lighter hide along the back, segment plates across the body
  for (let i = 0; i < body.length; i += 2) { const [x, y, r] = body[i]; if (r > 5) c.px(Math.round(x), Math.round(y - r + 2), 2) }
  for (let i = 12; i < body.length - 6; i += 14) { const [x, y, r] = body[i]; c.line(Math.round(x - 3), Math.round(y - r + 3), Math.round(x + 1), Math.round(y + r - 4), 3) }
  // the glow: a vein down the flank with branches toward the plates (index 15 pulses in game)
  const vein = body.filter((_, i) => i % 2 === 0 && i < body.length - 14).map(([x, y, r]) => [Math.round(x), Math.round(y + r * 0.3)])
  for (let i = 0; i + 1 < vein.length; i++) c.line(vein[i][0], vein[i][1], vein[i + 1][0], vein[i + 1][1], 15)
  for (let i = 4; i < vein.length - 2; i += 8) { const [x, y] = vein[i]; c.line(x, y, x + 5, y - 9, 15); c.line(x, y, x - 3, y + 7, 15) }
  // head: long armoured skull facing left, horns swept back, jaws open by `jaw`
  const [hx0, hy0] = P.head, hx = ox + hx0, hy = oy + hy0, t = P.tilt, j = P.jaw, S = 1.4
  const R = (dx, dy) => [Math.round(hx + S * (dx * Math.cos(t) - dy * Math.sin(t))), Math.round(hy + S * (dx * Math.sin(t) + dy * Math.cos(t)))]
  const poly = (list, k) => c.poly(list.flatMap(([dx, dy]) => R(dx, dy)), k)
  poly([[-16, -4], [-6, -9], [8, -10], [18, -6], [20, 6], [6, 4], [-14, 2]], 1)                       // skull + upper jaw
  poly([[-14, 4 + j * 10], [-4, 3 + j * 4], [12, 4], [18, 8], [6, 9 + j * 6], [-10, 7 + j * 11]], 1)    // lower jaw
  poly([[8, -9], [20, -16], [32, -18], [22, -12], [16, -5]], 1)                                         // great horn
  poly([[12, -5], [24, -8], [30, -3], [20, -1]], 1)                                                     // second horn
  poly([[-4, -8], [0, -14], [4, -9]], 1)                                                                // brow spike
  if (j > 0.2) {
    const m = [[-13, 3 + j * 1.5], [-2, 3.5 + j * 2], [8, 4], [8, 4 + j * 5], [-2, 6 + j * 7], [-12, 6 + j * 9]]
    poly(m, 4)                                                                                          // the mouth
    for (let k = 0; k < 4; k++) { const [x, y] = R(-11 + k * 5, 3 + j * 1.7); c.px(x, y, 14); const [x2, y2] = R(-9 + k * 5, 6 + j * 7.5); c.px(x2, y2, 14) }
  }
  // eye with the glow round it, plates on the skull
  { const [ex, ey] = R(2, -5); c.px(ex, ey, 14); c.px(ex - 1, ey, 14); c.px(ex + 1, ey - 1, 15); c.px(ex - 2, ey + 1, 15); c.px(ex + 2, ey - 1, 15) }
  { const [a, b] = R(-12, -2), [d, e] = R(10, -8); c.line(a, b, d, e, 3) }
  { const [a, b] = R(14, -7), [d, e] = R(26, -14); c.line(a, b, d, e, 15) }
}
scene("krayt", { w: 512, h: 512 }, (c) => {
  // anchors within 2 px of Groudon's, all congruent mod 8 so the shared body cuts into the same tiles
  krayt(c, 293, 1, "A")
  krayt(c, 117, 121, "B")
  krayt(c, 37, 353, "C")
})

// ------------------------------------------------------------------ the ground behind them (legend_bg.png)

// Sand (bank 3, behind GREATKRAYT): wind ripples in flat bands, pebbles. It wraps (the game scrolls it
// with a heat-shimmer wave), so every pattern repeats over 256.
use(BANKS[3])
scene("sand", { w: 256, h: 256 }, (c) => {
  c.rect(0, 0, 256, 256, 4)
  const r = c.rng(3)
  for (let row = 0; row < 16; row++) {
    const y0 = row * 16, ph = r() * 6.28, amp = 2 + r() * 2
    for (let x = 0; x < 256; x++) {
      const y = Math.round(y0 + 8 + amp * Math.sin((x / 256) * 6.28 * 3 + ph) + 1.2 * Math.sin((x / 256) * 6.28 * 7 + ph * 2))
      c.px(x, y - 2, 5); c.px(x, y - 1, 6); c.px(x, y, 7); c.px(x, y + 1, 3); if ((x + row) % 2) c.px(x, y + 2, 3)
      c.px(x, ((y + 3) & 255), 2)
    }
  }
  for (let i = 0; i < 90; i++) { const x = Math.floor(r() * 256), y = Math.floor(r() * 256); c.px(x, y, 9); c.px(x + 1, y, 8); c.px(x, y + 1, 1) }
})
// Sea (bank 4, behind SANDO): Emerald's look, bubbles of a few sizes on deep water, redrawn.
use(BANKS[4])
scene("sea", { w: 256, h: 256 }, (c) => {
  c.rect(0, 0, 256, 256, 11)
  const r = c.rng(8)
  for (let i = 0; i < 150; i++) {
    const x = Math.floor(r() * 256), y = Math.floor(r() * 256), s = r()
    if (s < 0.5) { c.px(x, y, 12); c.px(x + 1, y, 10) }
    else if (s < 0.85) { c.ring(x, y, 2, 12); c.px(x - 1, y - 1, 9) }
    else { c.ring(x, y, 4, 12); c.ring(x, y, 3, 10); c.px(x - 2, y - 2, 9); c.px(x - 1, y - 2, 9) }
  }
})

// ------------------------------------------------------------------ game files

gba(D + "pokeball.png", { affine: "pod", pal: POD, bank: 0, map: D + "pokeball_map.bin" })
gba(D + "groudon.png", { affine: "krayt", bank: 1, banks: BANKS, map: D + "groudon.bin", mapBytes: 8192 })
gba(D + "legend_bg.png", { bg: ["sand", "sea"], slots: [3, 4], banks: BANKS, maps: [D + "groudon_bg.bin", D + "kyogre_bg.bin"], tiles: 1024 })
gba(D + "bg.pal", { banks: BANKS })

// previews: the krayt poses on the sand
scene("krayt_on_sand", { w: 512, h: 512 }, (c) => { for (const x of [0, 256]) for (const y of [0, 256]) c.stamp("sand", x, y); c.stamp("krayt", 0, 0) })
