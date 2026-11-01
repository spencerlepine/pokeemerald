// Intro scene 2 (the bike ride), redrawn for Star Wars: KYBER.
// Emerald: Brendan/May bike past pine trees and mountains (graphics/intro/scene_2).
// Here:    KAEL rides a white speeder bike past moisture vaporators, homestead domes and mesas.
//
// Layout follows the game exactly (src/intro_credits_graphics.c, LoadIntroPart2Graphics(1)):
//   BG3 = trees_map.bin screen 0 (sky, suns, mesas)       palette slot 0, scrolls 1/256 px/frame
//   BG2 = trees_map.bin screen 1 (vaporators, domes)     palette slot 0, scrolls 1/4 px/frame
//   BG1 = grass_map.bin (the ground)                     palette slot 15, scrolls 4 px/frame
//   OBJ = brendan.png (rider) + bicycle.png (vehicle, drawn 8 px lower), 4 frames of 64x64, player.pal
// BG palette entries 9 and 10 are swapped every 8 frames by CycleSceneryPalette(0): in Emerald
// that makes the trees shimmer; here 9 is the vaporators' warning light and 10 its "off" color.
//
// Build: node ../../bin/pxl.js build intro_bike.px.js   (game files land in out/game/)

include("../../gba/screen.px.js")
const D = "graphics/intro/scene_2/"

// ------------------------------------------------------------------ palettes (GBA-safe, steps of 8)

// BG palette slot 0, shared by BG3 and BG2 (trees.png). Index 0 is transparent.
const BG = [
  "#000000", // 0  transparent
  "#a0c0e0", // 1  sky, top
  "#b8d0e8", // 2  sky
  "#d0e0e8", // 3  sky, haze
  "#e8e8e0", // 4  haze
  "#f8f0d8", // 5  horizon glow
  "#c0a8a8", // 6  mesa (cool, hazy rose)
  "#e8d8c0", // 7  mesa sunlit cap
  "#c8c0c8", // 8  far range and far props (aerial haze)
  "#f86040", // 9  vaporator light (swaps with 10)
  "#806858", // 10 vaporator light off
  "#c09070", // 11 adobe / metal shade (warm)
  "#f8e8c8", // 12 adobe / metal lit
  "#d8c098", // 13 adobe / metal mid
  "#886858", // 14 doorways, metal dark
  "#fff8e0", // 15 the twin suns
]
// BG palette slot 15 (grass.png). Same index roles as Emerald's grass: 1 edge line, 13-15 the ground.
const GROUND = [
  "#000000", "#886850", "#a88060", "#f8f0d8", "#ffffff",
  "#000000", "#000000", "#000000", "#000000", "#000000", "#000000", "#000000", "#000000",
  "#d0a060", "#e8b878", "#f8d898",
]
// OBJ palette (player.pal), shared by the rider and the speeder.
const PLAYER = [
  "#48b8a8", // 0  transparent
  "#483838", // 1  outline (warm dark, like Emerald's #524a4a)
  "#888878", // 2  metal shade
  "#c8c0e0", // 3  metal light (Emerald's lavender-white)
  "#ffffff", // 4  white
  "#e86818", // 5  flight orange (scarf, stripe)
  "#f8a848", // 6  orange light
  "#303040", // 7  dark (seat, strap, grille)
  "#ffd898", // 8  skin light
  "#e0a088", // 9  skin shade
  "#a86048", // 10 hair light / skin outline
  "#58c8f8", // 11 kyber blue (thruster, lens glint)
  "#3878c0", // 12 deep blue (lens, thruster rim)
  "#e8d8b0", // 13 tunic light
  "#c0a070", // 14 tunic mid
  "#785838", // 15 tunic dark, boots, hair
]

// ------------------------------------------------------------------ BG3: sky, suns, mesas

use(BG)
// Emerald's sky: flat bands with an 8-row 50% checker between each pair.
function sky(c, rows) {
  let y = 0
  for (let i = 0; i < rows.length; i++) {
    const [k, h] = rows[i]
    c.rect(0, y, 256, h, k)
    y += h
    if (i + 1 < rows.length) { c.dither(0, y, 256, 8, k, rows[i + 1][0], 0.5); y += 8 }
  }
}
// A flat-topped butte, sunlit from the upper left (the suns sit left of center).
function butte(c, x, top, w, base, body, cap) {
  const s = Math.max(3, Math.round((base - top) / 3))
  c.poly([x, base, x + s, top + 2, x + s + 2, top, x + w - s - 2, top, x + w - s, top + 2, x + w, base], body)
  c.hline(x + s + 2, top, w - 2 * s - 4, cap)
  c.line(x, base - 1, x + s, top + 2, cap)
  c.px(x + s + 1, top + 1, cap)
}

scene("bg3", { w: 256, h: 256, bg: 6 }, (c) => {
  sky(c, [[1, 8], [2, 8], [3, 8], [4, 8], [5, 24]])
  // twin suns, upper left: the big one and its smaller companion
  c.circ(52, 20, 5, 15); c.ring(52, 20, 6, 5)
  c.circ(70, 28, 3, 15); c.ring(70, 28, 4, 5)
  for (const o of [0, -256]) {
    // far range: long hazy mesa line
    c.poly([0 + o, 64, 20 + o, 60, 60 + o, 58, 70 + o, 52, 110 + o, 52, 118 + o, 60, 170 + o, 62, 182 + o, 54, 214 + o, 54, 224 + o, 62, 256 + o, 64, 256 + o, 104, 0 + o, 104], 8)
    c.hline(70 + o, 52, 41, 7); c.hline(182 + o, 54, 33, 7)
    // nearer buttes
    butte(c, 14 + o, 62, 54, 104, 6, 7)
    butte(c, 92 + o, 70, 30, 104, 6, 7)
    butte(c, 150 + o, 58, 70, 104, 6, 7)
    butte(c, 236 + o, 66, 40, 104, 6, 7)
  }
  c.rect(0, 100, 256, 156, 6)
})

// ------------------------------------------------------------------ BG2: vaporators and homesteads
// Emerald's BG2 is a dense row of pines, darker and more saturated than the mountains behind
// (aerial perspective). Same here: warm, sunlit adobe and metal in front of cool, hazy mesas.

// Moisture vaporator: footing, tall shaft, two collars, condenser head, warning light on top.
function vaporator(c, x, base, h, far) {
  const L = far ? 8 : 12, M = far ? 8 : 13, S = far ? 8 : 11, Dk = far ? 8 : 14
  const top = base - h
  c.rect(x - 3, base - 3, 9, 3, S); c.hline(x - 3, base - 3, 9, M)              // footing
  c.rect(x, top + 6, 3, h - 6, M); c.vline(x, top + 6, h - 6, L); c.vline(x + 2, top + 6, h - 6, S)
  for (const dy of [Math.round(h * 0.45), Math.round(h * 0.75)]) {          // collars
    c.rect(x - 2, top + dy, 7, 2, M); c.hline(x - 2, top + dy, 7, L); c.hline(x - 2, top + dy + 2, 7, Dk)
  }
  c.rect(x - 1, top + 1, 5, 5, M); c.vline(x - 1, top + 1, 5, L); c.vline(x + 3, top + 1, 5, S)   // condenser head
  c.hline(x - 3, top + 3, 9, L); c.hline(x - 3, top + 4, 9, Dk)              // fins
  c.hline(x, top, 3, L)
  if (!far) c.px(x + 1, top - 1, 9)                                           // warning light (blinks)
}
// Igloo dome lit from the upper left, with an arched doorway.
function dome(c, cx, base, rx, ry, door = true, far = false) {
  if (far) { c.ellipse(cx, base, rx, ry, 8); return }
  // Emerald shades round things in flat bands joined by a 50% checker (see the pines and the sky).
  const lit = (x, y) => ((x - cx + rx * 0.4) / rx) ** 2 + ((y - base + ry * 0.55) / ry) ** 2
  const box = [cx - rx, base - ry, 2 * rx + 1, ry + 1]
  c.ellipse(cx, base, rx, ry, 13)
  c.clip((x, y) => c.is(x, y, "d") && lit(x, y) > 0.75, () => c.dither(...box, 13, 11, 0.5))
  c.clip((x, y) => c.is(x, y, "db") && lit(x, y) > 1.0, () => c.rect(...box, 11))
  c.clip((x, y) => c.is(x, y, "d") && lit(x, y) < 0.22, () => c.dither(...box, 13, 12, 0.5))
  c.clip((x, y) => c.is(x, y, "d") && lit(x, y) < 0.12, () => c.rect(...box, 12))
  c.hline(cx - rx + 1, base - 1, 2 * rx - 1, 11)                              // contact shadow
  if (!door) return
  const dw = Math.max(3, Math.round(rx / 2.5)), dh = Math.round(ry * 0.6), dx = cx - Math.round(rx * 0.35)
  c.rect(dx, base - dh + 1, dw, dh, 14); c.hline(dx + 1, base - dh, dw - 2, 14)
  c.hline(dx - 1, base - dh - 1, dw + 2, 12)                                  // lit lintel
}
// Low adobe wall with a stepped top.
function wall(c, x, base, w, h) {
  c.rect(x, base - h, w, h, 13); c.hline(x, base - h, w, 12)
  for (let i = 0; i < w; i += 6) c.rect(x + i, base - h - 2, 3, 2, 13), c.hline(x + i, base - h - 2, 3, 12)
  c.vline(x + w - 1, base - h, h, 11); c.hline(x, base - 1, w, 11)
}
// Sandstone boulder.
function rock(c, x, base, w, h) {
  c.poly([x, base, x + 2, base - h + 3, x + 5, base - h, x + w - 4, base - h + 1, x + w, base - 3, x + w, base], 11)
  c.poly([x + 2, base - h + 3, x + 5, base - h, x + w - 4, base - h + 1, x + w - 6, base - h + 4, x + 3, base - h + 5], 13)
}

scene("bg2", { w: 256, h: 256 }, (c) => {
  for (const o of [0, -256]) {
    // far props in haze
    dome(c, 52 + o, 102, 9, 7, false, true); vaporator(c, 66 + o, 102, 18, true)
    dome(c, 170 + o, 102, 8, 6, false, true); dome(c, 182 + o, 102, 5, 4, false, true)
    vaporator(c, 232 + o, 102, 16, true)
    // Lars-style homestead: big dome, small dome, wall
    wall(c, 84 + o, 102, 34, 8)
    dome(c, 102 + o, 102, 22, 20)
    dome(c, 132 + o, 102, 11, 10)
    // vaporators and rocks
    vaporator(c, 20 + o, 102, 42, false)
    vaporator(c, 40 + o, 102, 30, false)
    rock(c, 150 + o, 102, 16, 9)
    vaporator(c, 196 + o, 102, 38, false)
    dome(c, 226 + o, 102, 14, 12)
    rock(c, 244 + o, 102, 10, 6)
  }
  c.rect(0, 102, 256, 154, 11)
})

// ------------------------------------------------------------------ BG1: the ground

use(GROUND)
scene("bg1", { w: 256, h: 256 }, (c) => {
  const r = c.rng(7)
  c.rect(0, 100, 256, 156, "d")
  // sunlit lip of the dune, ragged top edge with Emerald's dark edge line
  for (let x = 0; x < 256; x++) {
    const top = 97 + ((x * 7 + (x >> 3) * 3) % 4 === 0 ? 0 : 1) + (x % 16 < 2 ? -1 : 0)
    c.px(x, top - 1, 1)
    c.vline(x, top, 104 - top, "f")
    c.vline(x, 104, 3, "e")
  }
  c.dither(0, 104, 256, 2, "f", "e", 0.5)
  c.dither(0, 107, 256, 2, "e", "d", 0.5)
  // wind ripples: short dashes, longer and further apart toward the viewer
  // Sparse, so the speed reads from the scroll and not from a pattern (Emerald's grass is flat).
  for (let row = 0; row < 4; row++) {
    const y = 114 + row * 13, len = 5 + row * 3, gap = 40 + row * 24
    for (let x = (row * 37) % gap; x < 256; x += gap + Math.floor(r() * 16)) {
      c.hline(x, y, len, "e"); c.hline(x + len, y - 1, 3 + row, "e"); c.hline(x + 1, y + 1, len - 1, 2)
    }
  }
  // pebbles
  for (let i = 0; i < 18; i++) { const x = Math.floor(r() * 256), y = 110 + Math.floor(r() * 50); c.px(x, y, 2); c.px(x + 1, y, 3) }
})

// ------------------------------------------------------------------ OBJ: small scenery (trees_small.png)

use(BG)
// Emerald's trees_small.png: 64x32, three cells (32x32, then two 16x32 at tile 16 and 24).
// Draw them side by side; cells: makes gba() write the game's 1D tile order.
const SMALL_CELLS = [[32, 32], [16, 32], [16, 32]]
// They scroll as sprites between BG2 and the ground. Here: a far vaporator pair and two rocks.
sprite("scenery_small", { w: 64, h: 32 }, (c) => {
  // Emerald's small pines are two-tone (lit left, mid body) like the big ones: same here.
  vaporator(c, 9, 32, 28, false); dome(c, 23, 32, 8, 7)
  vaporator(c, 39, 32, 20, false)
  c.poly([48, 32, 50, 26, 54, 23, 59, 24, 63, 29, 63, 32], 11); c.poly([50, 26, 54, 23, 59, 24, 57, 27, 52, 28], 13)
})

// ------------------------------------------------------------------ OBJ: KAEL on the speeder bike

use(PLAYER)
// Emerald's bicycle.png is 4 frames of 64x32, placed 8 px below the rider's center: the vehicle
// frame's top is 24 px below the rider frame's top. The hull is drawn in rider coordinates and
// shifted up 24 (layer y), so rider and vehicle line up by construction.
const VY = -24
// The hull, outlined (62x30 + outline = 64x32). Facing left like Emerald's sheets.
sprite("_hull", { w: 62, h: 30, outline: 1 }, layer("hull", { y: VY + 8 },
  // steering vanes at the nose
  poly([3, 27, 9, 26, 12, 30, 6, 31], 2), poly([3, 38, 6, 36, 12, 36, 9, 40], 2), hline(4, 27, 5, 3),
  // nose beam
  poly([2, 31, 26, 29, 30, 29, 30, 36, 26, 36, 2, 34], 3), hline(3, 31, 24, 4), hline(3, 34, 24, 2),
  // body
  poly([26, 28, 34, 25, 48, 24, 56, 27, 58, 33, 56, 38, 48, 40, 28, 39], 4),
  poly([28, 35, 56, 35, 56, 38, 48, 40, 28, 39], 3), hline(30, 39, 18, 2),
  hline(30, 33, 24, 5), hline(31, 32, 22, 6),
  // engine housing and grille
  rect(46, 27, 9, 10, 2), vline(48, 28, 8, 7), vline(50, 28, 8, 7), vline(52, 28, 8, 7), hline(46, 27, 9, 3),
  // seat
  poly([33, 25, 44, 23, 46, 24, 46, 26, 33, 27], 7), hline(34, 24, 10, 2),
  // grips
  rect(22, 27, 4, 2, 7), line(25, 28, 28, 30, 2),
  // footrest
  rect(36, 40, 6, 2, 2),
))

// Thruster flame and hover shadow: not outlined, so they stay soft.
const FLAME = [[3, 1], [5, 2], [4, 1], [6, 2]]
for (let f = 0; f < 4; f++) {
  const bob = f === 1 || f === 2 ? 1 : 0, [len, core] = FLAME[f], fy = 30 + VY + 8 + 1 + bob
  sprite("speeder_" + f, { w: 64, h: 32 },
    // shadow on the sand, a few px below the hull: it hovers
    (c) => { c.dither(10 + bob, 29, 44 - 2 * bob, 2, 15, ".", 0.5); c.hline(16, 30, 32, 15) },
    stamp("_hull", 0, bob),
    rect(59, fy, len, 6, 12), rect(59, fy + 1, len + core, 4, 11), hline(59, fy + 2, core + 1, 4), hline(59, fy + 3, core + 1, 4),
  )
}

// The rider, outlined. Leaning forward, hands on the grips, scarf streaming back.
// Keys: f/a hair dark/light, 8/9 skin, 1 eye, 7 goggle strap, c lens, b glint.
sprite("_kael_body", { w: 62, h: 62 },
  // back leg (far side) tucked behind
  line(40, 41, 34, 46, 15, 2),
  // torso, leaning forward
  poly([28, 22, 36, 20, 42, 23, 44, 36, 34, 38, 30, 31], 14),
  poly([28, 22, 36, 20, 38, 22, 33, 25, 31, 31, 30, 31], 13),
  line(39, 24, 43, 34, 15),                       // back in shade
  hline(33, 36, 11, 15), hline(34, 37, 10, 15),   // belt
  // near leg: thigh forward to the knee, shin down to the footrest
  poly([34, 36, 44, 35, 44, 39, 31, 42, 29, 40], 14), hline(33, 37, 10, 13), poly([29, 40, 32, 41, 35, 47, 31, 48], 14),
  rect(30, 47, 7, 3, 15), hline(30, 47, 6, 10),   // boot
  // arm reaching to the grip
  line(31, 24, 24, 33, 13, 3), line(32, 26, 26, 33, 14, 1),
  rect(21, 32, 4, 3, 7), px(21, 32, 2),           // glove
  // head
  grid(20, 6, `
    ....ffffff....
    ..ffaaaaaafff.
    .faaaaaaaaaaff
    .77777aaaaaaff
    7cbc77aaaaaaff
    7ccc7aaaaafff.
    .7778aaaaaaff.
    .88888aa8aaf..
    888888888aff..
    8818888889f...
    .88188889ff...
    ..88888999f...
    ...899999.....
    ....9999......`),
)
const SCARF = [
  [35, 21, 44, 20, 50, 22, 54, 20, 52, 24, 45, 25, 38, 25],
  [35, 21, 44, 21, 49, 19, 55, 22, 51, 24, 45, 24, 38, 25],
  [35, 21, 43, 22, 49, 21, 54, 18, 53, 23, 46, 25, 38, 25],
  [35, 21, 44, 20, 50, 23, 55, 21, 52, 25, 45, 25, 38, 25],
]
for (let f = 0; f < 4; f++) {
  const bob = f === 1 || f === 2 ? 1 : 0
  sprite("kael_" + f, { w: 62, h: 62, outline: 1 },
    stamp("_kael_body", 0, bob),
    poly(SCARF[f].map((v, i) => (i % 2 ? v + bob : v)), 5),
    line(36, 22 + bob, 44, 22 + bob, 6),
  )
}

// ------------------------------------------------------------------ game files

gba(D + "trees.png", { bg: ["bg3", "bg2"], map: D + "trees_map.bin", pal: BG })
gba(D + "grass.png", { bg: ["bg1"], map: D + "grass_map.bin", pal: GROUND, palSlot: 15 })
gba(D + "trees_small.png", { image: "scenery_small", pal: BG, cells: SMALL_CELLS })
gba(D + "brendan.png", { obj: ["kael_0", "kael_1", "kael_2", "kael_3"], pal: PLAYER })
// The intro picks Brendan or May at random; until MIRA is drawn, both show KAEL.
gba(D + "may.png", { obj: ["kael_0", "kael_1", "kael_2", "kael_3"], pal: PLAYER })
gba(D + "bicycle.png", { obj: ["speeder_0", "speeder_1", "speeder_2", "speeder_3"], pal: PLAYER })
gba(D + "player.pal", { pal: PLAYER })

// ------------------------------------------------------------------ previews: the screen as the GBA shows it

// Speeds from Task_Scene2_CreateSprites: CreateBicycleBgAnimationTask(1, 0x4000, 0x400, 0x10).
const SPEED = { bg1: 4, bg2: 0.25, bg3: 1 / 256 }
gbaScreen("screen_new", {
  frames: 32, fps: 30,
  bg: [{ asset: "bg3", speed: SPEED.bg3 }, { asset: "bg2", speed: SPEED.bg2 }, { asset: "bg1", speed: SPEED.bg1 }],
  swap: { asset: ["bg3", "bg2"], a: BG[9], b: BG[10], every: 8 },
  obj: [
    { asset: (f) => "speeder_" + (Math.floor(f / 4) % 4), x: 140, y: 92 },
    { asset: (f) => "kael_" + (Math.floor(f / 4) % 4), x: 140, y: 68 },
  ],
})

ref("v_bg3", D + "trees.png", { map: D + "trees_map.bin", screen: 0 })
ref("v_bg2", D + "trees.png", { map: D + "trees_map.bin", screen: 1 })
ref("v_bg1", D + "grass.png", { map: D + "grass_map.bin" })
ref("v_scenery_small", D + "trees_small.png", { cells: SMALL_CELLS })
for (let f = 0; f < 4; f++) {
  ref("v_may_" + f, D + "may.png", { frame: [64, 64, f], pal: D + "player.pal" })
  ref("v_bike_" + f, D + "bicycle.png", { frame: [64, 32, f], pal: D + "player.pal" })
}
gbaScreen("screen_vanilla", {
  frames: 32, fps: 30,
  bg: [{ asset: "v_bg3", speed: SPEED.bg3 }, { asset: "v_bg2", speed: SPEED.bg2 }, { asset: "v_bg1", speed: SPEED.bg1 }],
  obj: [
    { asset: (f) => "v_bike_" + (Math.floor(f / 4) % 4), x: 140, y: 92 },
    { asset: (f) => "v_may_" + (Math.floor(f / 4) % 4), x: 140, y: 68 },
  ],
})
