// DARTH VADER for the title collage (right group, back row). Drawn new; the trainer pic
// magma_leader_maxie.png was concept only. One 16-color palette (OBJ-ready), index 0 transparent.
// Light from the upper left (STYLE.md 4); the cape is darker than the body so arms and legs read in front of it.
use(["#ff00ff",
  "#080810", // 1 k outline
  "#141420", // 2 C cape
  "#262634", // 3 K body black
  "#3a3c4e", // 4 D dark grey
  "#585e74", // 5 G grey
  "#8890a8", // 6 L light grey
  "#c0c8d8", // 7 S silver
  "#f0f0f8", // 8 W white
  "#a01820", // 9 r dark red
  "#e83838", // a R red
  "#f88080", // b p saber glow
  "#fff0f0", // c B saber core
  "#38b050", // d g green
  "#4878e0", // e u blue
])
pal({ k: 1, C: 2, K: 3, D: 4, G: 5, L: 6, S: 7, W: 8, r: 9, R: 10, p: 11, B: 12, g: 13, u: 14 })

const CX = 45
const HELMET = `
.......kKKKKKKk.......
.....kKLLGKKKKKKk.....
....kKLGGKKKKKKKKk....
...kKLGKKKKKKKKKKKk...
...kLGKKKKKKKKKKKKk...
..kKLKKKKKKKKKKKKKKk..
..kKGKKKKKKKKKKKKKKk..
..kKGKKKKKKKKKKKKKKk..
..kKDDDDDDDDDDDDDDKk..
..kDkkkkkDGDkkkkkDDk..
.kKDkLkkkDGDkLkkkDKKk.
.kKDkkkkDDGDDkkkkDKKk.
.kKKDDDDDGLGDDDDDKKKk.
kKKKDDDDGSSSGDDDDKKKKk
kKKDDDDGSkkkSGDDDDKKKk
kKDDDDDGSkGkSGDDDDDKKk
kGDDDDDGSkkkSGDDDDDDKk
kGDDDKKDGSkSGDKKDDDDKk
kGDDKKKKDGSGDKKKKDDDKk
.kKKk..kKDGDKk..kKKKk.
........kKKKk.........`

sprite("vader", { w: 82, h: 104, outline: "k" },
  // cape behind everything: shoulders to floor, flaring
  poly([CX - 15, 21, CX + 15, 21, CX + 31, 103, CX - 29, 103], "C"),
  line(CX - 16, 24, CX - 28, 102, "D"),                     // lit left edge
  line(CX - 21, 60, CX - 24, 102, "K"), line(CX + 19, 56, CX + 25, 102, "K"),   // folds
  poly([CX + 17, 40, CX + 21, 40, CX + 31, 103, CX + 26, 103], "k"),             // shadow side
  // legs, slightly apart, boots shiny
  poly([CX - 9, 60, CX - 1, 60, CX - 2, 92, CX - 10, 92], "K"),
  poly([CX + 1, 60, CX + 9, 60, CX + 11, 92, CX + 3, 92], "K"),
  line(CX - 8, 62, CX - 9, 90, "D"), line(CX + 2, 62, CX + 4, 90, "D"),
  vline(CX, 60, 32, "k"),
  poly([CX - 11, 90, CX - 1, 90, CX - 1, 102, CX - 13, 102], "K"),
  poly([CX + 2, 90, CX + 12, 90, CX + 14, 102, CX + 2, 102], "K"),
  line(CX - 10, 91, CX - 11, 100, "L"), line(CX - 9, 91, CX - 9, 99, "G"),
  line(CX + 3, 91, CX + 3, 100, "G"),
  hline(CX - 13, 102, 12, "k"), hline(CX + 2, 102, 13, "k"),
  // tunic skirt over the thighs
  poly([CX - 11, 50, CX + 11, 50, CX + 13, 66, CX - 13, 66], "K"),
  line(CX - 11, 52, CX - 12, 65, "G"), line(CX - 4, 54, CX - 5, 65, "D"), line(CX + 5, 54, CX + 6, 65, "k"),
  // torso
  poly([CX - 13, 22, CX + 13, 22, CX + 10, 50, CX - 10, 50], "K"),
  line(CX - 12, 24, CX - 10, 48, "D"),
  // shoulder armor
  poly([CX - 15, 22, CX - 6, 19, CX - 5, 25, CX - 14, 29], "D"),
  poly([CX + 15, 22, CX + 6, 19, CX + 5, 25, CX + 14, 29], "D"),
  line(CX - 14, 22, CX - 7, 20, "L"), line(CX + 7, 20, CX + 13, 22, "G"),
  // chest box
  rect(CX - 6, 30, 13, 9, "S"), rect(CX - 5, 31, 11, 7, "k"),
  px(CX - 4, 32, "R"), px(CX - 2, 32, "g"), px(CX, 32, "u"), px(CX + 2, 32, "R"), px(CX + 4, 32, "g"),
  hline(CX - 4, 34, 4, "L"), hline(CX + 1, 34, 4, "G"),
  px(CX - 4, 36, "r"), px(CX - 2, 36, "u"), px(CX + 2, 36, "g"), px(CX + 4, 36, "R"),
  // belt with silver boxes
  rect(CX - 11, 47, 23, 4, "D"), hline(CX - 11, 47, 23, "G"),
  rect(CX - 4, 46, 9, 6, "S"), rect(CX - 3, 47, 7, 4, "G"), px(CX - 2, 48, "R"), px(CX, 48, "g"), px(CX + 2, 48, "u"),
  rect(CX - 10, 48, 3, 2, "L"), rect(CX + 8, 48, 3, 2, "L"),
  // his left arm (screen right), hanging, fist clenched
  poly([CX + 13, 24, CX + 18, 27, CX + 19, 48, CX + 13, 48], "K"),
  line(CX + 13, 26, CX + 13, 47, "k"),
  poly([CX + 12, 48, CX + 20, 48, CX + 20, 55, CX + 12, 55], "K"), hline(CX + 13, 49, 6, "G"), hline(CX + 12, 55, 8, "k"),
  // his right arm (screen left): elbow out, fist up by the chest holding the saber
  poly([CX - 13, 23, CX - 18, 26, CX - 24, 42, CX - 18, 45], "K"),
  line(CX - 17, 27, CX - 23, 41, "L"),
  poly([CX - 24, 42, CX - 18, 45, CX - 16, 39, CX - 12, 34, CX - 15, 31], "K"),
  line(CX - 23, 42, CX - 15, 32, "G"),
  // glove + hilt
  rect(CX - 17, 29, 6, 6, "K"), hline(CX - 16, 30, 4, "L"),
  line(CX - 14, 37, CX - 12, 28, "S", 2), px(CX - 13, 33, "k"),
  // saber blade straight up, tilted toward the logo
  line(CX - 12, 27, CX - 30, -6, "p", 3),
  line(CX - 12, 27, CX - 30, -6, "B"),
  // helmet last
  HELMET.length && ((c) => {
    const rows = HELMET.trim().split("\n")
    rows.forEach((row, y) => [...row].forEach((ch, x) => { if (ch !== ".") c.px(CX - 11 + x, y, ch) }))
  }),
)
