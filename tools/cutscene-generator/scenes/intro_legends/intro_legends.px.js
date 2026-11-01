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
include("sculpt.px.js")
const D = "graphics/intro/scene_3/"

// ------------------------------------------------------------------ palettes (GBA steps of 8)

// bg.pal: banks 0, 2, 4-7 and 12-15 are Emerald's (kyogre, clouds, Rayquaza and the glow ramp), truncated to
// GBA steps exactly as the game reads them. Bank 1 (the krayt) and bank 3 (the sand) are new.
const V = (s) => s.split(" ").map((h) => "#" + h)
const BANKS = {
  0: V("000000 000000 000000 000000 000000 000000 000000 000000 000000 000000 000000 000000 000000 000000 000000 000000"),
  // 1  GREATKRAYT: 1 outline, 2-7 hide (dark -> lit), 8-10 mouth, 11-12 horn and claw, 13 eye, 14 teeth,
  //    15 the glow (the game pulses it blue -> red, as Groudon's veins)
  1: V("8890f8 100810 282020 403030 605048 807068 a09080 c0b0a0 401018 802030 b84858 585050 a8a098 181818 f0e8d8 0020c8"),
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

// The greater krayt dragon of the Jundland Wastes, side view facing left: a huge blunt head with a
// maw full of teeth, swept-back horns, a ridged back, stubby clawed legs, the tail diving into the
// sand. Sculpted from ellipsoids (sculpt.px.js) and shaded by one light from the upper left; the body
// is the same in every pose so the three poses share tiles (an affine BG holds 256).
use(BANKS[1])
const HIDE = ["2", "3", "4", "5", "6", "7"], HORN = ["b", "b", "b", "c", "c", "c"], MOUTH = ["8", "8", "9", "9", "a", "a"]
const DARKER = { 7: "6", 6: "5", 5: "4", 4: "3", 3: "2", 2: "2", c: "b", b: "b" }
function kraytBody(ox, oy) {
  const B = []
  // the trunk: neck base to the tail, which dives under the sand at the bottom right
  B.push(...chain([[76 + ox, 48 + oy, 24], [92 + ox, 50 + oy, 28], [112 + ox, 56 + oy, 25], [132 + ox, 62 + oy, 20], [150 + ox, 70 + oy, 14], [164 + ox, 80 + oy, 9], [176 + ox, 92 + oy, 5]], HIDE, 3, 0.9))
  // dorsal ridge plates, leaning back
  for (const [x, y, w, h, rot] of [[86, 18, 4, 13, -22], [100, 18, 4, 14, -24], [114, 26, 4, 13, -26], [128, 34, 4, 12, -28], [142, 44, 3.5, 10, -30], [156, 56, 3, 8, -34]])
    B.push({ cx: x + ox, cy: y + oy, rx: w, ry: h, rz: 5, rot, ramp: HORN, z: 4 })
  // stubby legs with the knee bent forward
  for (const [x, y] of [[82, 76], [108, 82], [134, 86]]) {
    B.push({ cx: x + ox, cy: y + oy, rx: 9, ry: 11, rz: 10, ramp: HIDE, z: 6, rot: 20 })      // upper leg
    B.push({ cx: x - 6 + ox, cy: y + 12 + oy, rx: 10, ry: 5, rz: 7, ramp: HIDE, z: 8, rot: -10 }) // foot
  }
  return B
}
function kraytHead(ox, oy, pose) {
  // the jaw swings open from a hinge below the eye; the skull stays put so the poses share tiles
  const jaw = { A: 4, B: 16, C: 2 }[pose], hy = oy
  const ang = (-jaw * 1.6 * Math.PI) / 180, hx = 50 + ox, hyy = 46 + hy    // hinge; negative = the jaw drops
  const J = (dx, dy) => ({ cx: hx + dx * Math.cos(ang) - dy * Math.sin(ang), cy: hyy + dx * Math.sin(ang) + dy * Math.cos(ang) })
  const B = []
  B.push({ cx: 52 + ox, cy: 38 + hy, rx: 38, ry: 22, rz: 26, ramp: HIDE, z: 2 })               // skull, long and low
  B.push({ cx: 44 + ox, cy: 22 + hy, rx: 26, ry: 8, rz: 9, ramp: HIDE, z: 8, rot: -4 })         // brow ridge
  B.push({ cx: 22 + ox, cy: 36 + hy, rx: 28, ry: 8, rz: 12, ramp: HIDE, z: 4, rot: -3 })         // snout / upper jaw
  B.push({ cx: 60 + ox, cy: 44 + hy, rx: 14, ry: 8, rz: 9, ramp: HIDE, z: 9, rot: -20 })         // cheek crest
  { const j = J(-28, 12); B.push({ ...j, rx: 28, ry: 7, rz: 9, ramp: HIDE, z: 3, rot: -jaw * 1.6 + 2 }) } // lower jaw
  { const j = J(-6, 16); B.push({ ...j, rx: 16, ry: 9, rz: 10, ramp: HIDE, z: 2, rot: -jaw * 1.2 }) }       // throat
  // horns swept back from the skull, a big one and a small one, and cheek spikes
  B.push({ cx: 86 + ox, cy: 12 + hy, rx: 26, ry: 3.5, rz: 5, ramp: HORN, z: 12, rot: -32 })
  B.push({ cx: 84 + ox, cy: 24 + hy, rx: 20, ry: 3, rz: 4, ramp: HORN, z: 12, rot: -18 })
  B.push({ cx: 80 + ox, cy: 36 + hy, rx: 14, ry: 2.5, rz: 4, ramp: HORN, z: 12, rot: -4 })
  return { B, hy, jaw, J }
}
function kraytPose(c, ox, oy, pose) {
  const head = kraytHead(ox, oy, pose), hy = head.hy, jaw = head.jaw, J = head.J
  // the mouth cavity, drawn first: the jaws cover its edges, the gap between them stays
  const lo = J(-52, 6), lo2 = J(-10, 8)
  c.poly([0 + ox, 42 + hy, 48 + ox, 40 + hy, 54 + ox, 50 + hy, Math.round(lo2.cx), Math.round(lo2.cy), Math.round(lo.cx), Math.round(lo.cy)], "8")
  c.poly([8 + ox, 44 + hy, 44 + ox, 43 + hy, 46 + ox, 48 + hy, Math.round(lo2.cx) - 6, Math.round(lo2.cy) - 2, Math.round(lo.cx) + 10, Math.round(lo.cy) - 2], "9")
  { const t = J(-30, 4); c.ellipse(Math.round(t.cx), Math.round(t.cy), 12, 3, "a") }
  const S = sculpt(c, [...kraytBody(ox, oy), ...head.B])
  // teeth: along the upper jaw's lower edge (pointing down) and the lower jaw's top (pointing up)
  for (let i = 0; i < 7; i++) {
    const x = 2 + ox + i * 6
    let y = 40 + hy; while (S.inside(x, y) && y < 58 + hy) y++
    if (c.is(x, y, "89a")) c.poly([x - 1, y - 1, x + 3, y - 1, x + 1, y + 4 + (i % 2)], "e")
    const t = J(-50 + i * 6, 6); let y2 = Math.round(t.cy) + 6, x2 = Math.round(t.cx)
    while (S.inside(x2, y2) && y2 > 40 + hy) y2--
    if (c.is(x2, y2, "89a")) c.poly([x2 - 1, y2 + 1, x2 + 3, y2 + 1, x2 + 1, y2 - 4 - (i % 2)], "e")
  }
  // eye: small, dark, under the brow, a glint and the glow round it
  c.circ(58 + ox, 30 + hy, 2, "d"); c.px(57 + ox, 29 + hy, "e")
  for (const [dx, dy] of [[-3, 0], [3, 0], [0, -3], [0, 3], [-2, -2], [2, -2], [-2, 2], [2, 2]]) c.px(58 + ox + dx, 30 + hy + dy, "f")
  // nostril and skull plates
  c.px(6 + ox, 36 + hy, "2"); c.px(7 + ox, 36 + hy, "2"); c.px(7 + ox, 37 + hy, "3")
  for (const [x, y] of [[30, 30], [40, 28], [48, 26]]) c.line(x + ox, y + hy, x + 4 + ox, y - 2 + hy, "4")
  // claws
  for (const [x, y] of [[82, 76], [108, 82], [134, 86]]) for (const d of [-15, -10, -5]) c.poly([x + d + ox, y + 14 + oy, x + d + 4 + ox, y + 13 + oy, x + d - 2 + ox, y + 19 + oy], "b")
  // segment grooves across the trunk, following the shading
  for (const gx of [92, 108, 124, 140, 154]) for (let y = 0; y < 100; y++) {
    const x = gx + ox + Math.round((y - 50) * 0.12), yy = y + oy
    if (S.who(x, yy) >= 0 && S.who(x, yy) < 60 && c.is(x, yy, "234567")) c.px(x, yy, DARKER[c.key(x, yy)])
  }
  // glowing veins (index 15) on the flank, 2 px wide so they read at 1x
  const vein = [[82, 54], [94, 60], [106, 62], [118, 66], [130, 68], [142, 72], [152, 78]]
  for (let i = 0; i + 1 < vein.length; i++) { c.line(vein[i][0] + ox, vein[i][1] + oy, vein[i + 1][0] + ox, vein[i + 1][1] + oy, "f"); c.line(vein[i][0] + ox, vein[i][1] + 1 + oy, vein[i + 1][0] + ox, vein[i + 1][1] + 1 + oy, "f") }
  for (const [x, y] of [[94, 60], [118, 66], [142, 72]]) { c.line(x + ox, y + oy, x + 6 + ox, y - 9 + oy, "f"); c.line(x + ox, y + 1 + oy, x - 4 + ox, y + 8 + oy, "f") }
}
scene("krayt", { w: 512, h: 512 }, (c) => {
  // anchors within 2 px of Groudon's and congruent mod 8, so the shared body cuts into the same tiles
  kraytPose(c, 293, 1, "A")
  kraytPose(c, 117, 121, "B")
  kraytPose(c, 37, 353, "A")
  outlineAll(c, "1")
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
