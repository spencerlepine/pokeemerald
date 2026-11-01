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
  // 1  the krayt slot (Groudon's bank). PLACEHOLDER art for now: 2 is the placeholder magenta; the rest is
  //    Emerald's (1 body black, 14 eye white, 15 the glow the game pulses blue -> red)
  1: V("8890f8 000000 f800e8 e87800 e88000 e88800 e89000 e89800 e8a000 e8a800 e8b000 e8b800 e8c000 e8d000 f8f8f8 0020c8"),
  2: V("8890f8 000000 0000f8 0810f8 1828f8 2838f8 3850f8 4860f8 5878f8 6890f8 f800e8 000000 000000 000000 f8f8f8 b00000"),
  // 3  sand: 1 deep shade .. 6 lit crest, 7-8 pebbles
  3: V("000000 603820 905830 b07840 c89050 d8a860 e8c070 f8d888 784828 a87048 000000 000000 000000 000000 000000 000000"),
  4: V("000000 002850 f8f8f8 000000 000000 000000 000000 000000 000000 88a8f8 6890d8 5078b8 306098 184878 003060 b00000"),
  5: V("000000 000000 001000 507060 f800e8 80a890 98b0a8 f8f8c0 f8f078 b0a060 609838 78a080 a03830 a8c8f0 f8f078 000000"),
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

// ------------------------------------------------------------------ the titans: PLACEHOLDERS

// GREATKRAYT, SANDO and the EXOGORTH are NOT drawn yet (owner, 2026-11-01: two hand-drawn rounds of the
// krayt were rejected; the titans are a follow-up task, see wiki/art/intro_titans.md). Until then each
// pose shows the project's placeholder sprite (z-day .dev/assets/16x16-placeholder-image-sprite.png,
// a magenta circle with a slash) scaled up, centred where Emerald's creature stood, so the scene runs
// and every camera move still lands on something.
const PLACEHOLDER = `
.....XXXXXX.....
...XX......XX...
..X.........XX..
.X.........XX.X.
.X........XX..X.
X........XX....X
X.......XX.....X
X......XX......X
X.....XX.......X
X....XX........X
XX..XX.........X
.X.XX.........X.
.XXX..........X.
..X..........X..
...XX......XX...
.....XXXXXX.....`
function placeholder(c, cx, cy, scale, key) {
  const rows = PLACEHOLDER.trim().split("\n"), x0 = Math.round(cx - 8 * scale), y0 = Math.round(cy - 8 * scale)
  rows.forEach((row, y) => [...row].forEach((ch, x) => { if (ch === "X") c.rect(x0 + x * scale, y0 + y * scale, scale, scale, key) }))
}
// Centres of Emerald's poses on the 512x512 affine maps (pixel bounding boxes of groudon.bin / kyogre.bin).
use(BANKS[1])
scene("krayt", { w: 512, h: 512 }, (c) => { for (const [x, y] of [[379, 44], [203, 169], [124, 392]]) placeholder(c, x, y, 5, "2") })
use(BANKS[2])
scene("sando", { w: 512, h: 512 }, (c) => { for (const [x, y] of [[176, 128], [176, 380], [432, 384]]) placeholder(c, x, y, 5, "a") })
// rayquaza.png is a text BG in bank 5: the light sky band (rows 32-127, index 13, which the game dims
// and flashes) with the creature on it, centred at (124, 80).
use(BANKS[5])
scene("exogorth", { w: 256, h: 256 }, (c) => { c.rect(0, 32, 240, 96, "d"); placeholder(c, 124, 80, 4, "4") })

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
gba(D + "kyogre.png", { affine: "sando", bank: 2, banks: BANKS, map: D + "kyogre.bin", mapBytes: 8192 })
gba(D + "rayquaza.png", { bg: ["exogorth"], map: D + "rayquaza.bin", pal: BANKS[5], palSlot: 5 })
gba(D + "legend_bg.png", { bg: ["sand", "sea"], slots: [3, 4], banks: BANKS, maps: [D + "groudon_bg.bin", D + "kyogre_bg.bin"], tiles: 1024 })
gba(D + "bg.pal", { banks: BANKS })

// previews: the krayt poses on the sand
scene("krayt_on_sand", { w: 512, h: 512 }, (c) => { for (const x of [0, 256]) for (const y of [0, 256]) c.stamp("sand", x, y); c.stamp("krayt", 0, 0) })
