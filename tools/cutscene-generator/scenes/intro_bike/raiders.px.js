// Tusken raiders for intro scene 2: they replace Manectric, Torchic, Volbeat and Flygon.
// Included from intro_bike.px.js. Two sheets share one palette (RAIDERS, OBJ palette tag TAG_RAIDER):
//   raider_near.png  32x64 frames: a raider behind a sandstone rock on the near ground. The rock is
//                    part of every frame, so popping up is just a frame change (code: SpriteCB_RaiderNear).
//   raider_far.png   16x32 frames: a small raider on the horizon. OBJ priority 2 puts it behind the
//                    ground (BG1) and in front of the homesteads (BG2), so the dune lip hides its legs
//                    and it pops up by moving up (code: SpriteCB_RaiderFar).
//
// Letters (mapped to palette indices below):
//   O outline   W wraps light   M wraps mid   N wraps shade   R robe light   r robe   D robe dark
//   S metal light   s metal   X metal dark   E goggle lens   G glint   L rock lit   K rock   k rock shade

const RAIDERS = [
  "#48b8a8", // 0  transparent
  "#403028", // 1  outline (warm dark)
  "#f0e0b8", // 2  wraps light
  "#c8b088", // 3  wraps mid
  "#988060", // 4  wraps shade
  "#a87850", // 5  robe light
  "#805838", // 6  robe
  "#583828", // 7  robe dark
  "#d0d0c8", // 8  metal light
  "#909090", // 9  metal
  "#585860", // 10 metal dark
  "#202030", // 11 goggle lens
  "#f8f8f0", // 12 glint
  "#f0c890", // 13 rock lit (matches the ground's lit sand)
  "#c89060", // 14 rock
  "#906040", // 15 rock shade
]
const RK = { O: "1", W: "2", M: "3", N: "4", R: "5", r: "6", D: "7", S: "8", s: "9", X: "a", E: "b", G: "c", L: "d", K: "e", k: "f" }
const rk = (s) => s.replace(/[A-Za-z]/g, (ch) => RK[ch] ?? ch)

use(RAIDERS)

// ---- near raider (front view, mirrored half; the right column of the half is the center-left)
const R_HEAD = `
.....MMMM
...MMWWWW
..MWWWWWW
.MWWWWWWW
.MWWNNNNX
.MXXXXXSS
.XEEEXSSs
.XEGEXSss
.MXXXSsss
..MWNNsSX
..MWNssSX
...MNsXXs
...MMsXX.
....MNXs.`
const R_BODY = `
....NWWNN
..rrrrNNr
.rRRrrrrD
rRRrrrrDD
rRrrrrDDS
rRrrrrDrr
rRrrrDDrr
rRrrDDrrr
rRrDDrrrr
rrDDrrrrr
.NXXXXXXX
..rrrrrrr
..rRrrrrr
..rRrrrrD
..rRrrrDD
..rrrrDD.
...MWWN..
...MWWN..
...MWWN..
...MWWN..
..DDDDD..
.DDDDDD..`
// arms down (hands at the hips), arms up (fists by the head)
const R_ARMS_DOWN = `
rr.
rR.
rR.
rR.
rR.
rR.
MW.
MW.`
const R_ARMS_UP = `
WM.
WM.
rR.
rR.
rR.
rR.
rR.
rR.
rR.
rR.
rR.
rR.
rR.
.rR
.rR`

// The figure is 18 wide (two mirrored halves of 9) plus 3 px of arm each side.
sprite("_raider_down", { w: 24, h: 40, mx: true },
  grid(3, 0, rk(R_HEAD)), grid(3, 14, rk(R_BODY)), grid(0, 16, rk(R_ARMS_DOWN)))
sprite("_raider_up", { w: 24, h: 40, mx: true },
  grid(3, 0, rk(R_HEAD)), grid(3, 14, rk(R_BODY)), grid(0, 1, rk(R_ARMS_UP)))

// Gaffi stick: a metal staff with a hooked blade at one end and a knob at the other.
function gaffiFlat(c, x, y) {             // held overhead, horizontal
  c.hline(x, y, 28, "9"); c.hline(x, y - 1, 28, "8")
  c.rect(x - 2, y - 3, 3, 5, "a"); c.px(x - 3, y - 4, "9"); c.px(x - 3, y - 5, "8")      // hook blade
  c.rect(x + 27, y - 2, 3, 4, "a"); c.px(x + 28, y - 2, "9")                          // knob
}
function gaffiDiag(c, x, y) {             // held at the side, diagonal
  c.line(x, y, x + 6, y + 22, "9"); c.line(x + 1, y, x + 7, y + 22, "8")
  c.rect(x - 2, y - 3, 4, 4, "a"); c.px(x - 3, y - 4, "8")
}

// A sandstone rock, lit from the upper left, flat bands + checker like the scenery.
function rockNear(c, y) {
  c.poly([1, 63, 2, y + 8, 6, y + 3, 12, y, 21, y + 1, 27, y + 4, 30, y + 10, 30, 63], "e")
  c.poly([2, y + 8, 6, y + 3, 12, y, 18, y + 1, 14, y + 4, 8, y + 7, 4, y + 12], "d")
  // shaded right face: a 2 px checker where it turns, then flat shade
  c.clip((x, yy) => c.is(x, yy, "e") && x + (yy - y) * 0.15 > 21, () => c.dither(18, y, 14, 30, "e", "f", 0.5))
  c.clip((x, yy) => c.is(x, yy, "ef") && x + (yy - y) * 0.15 > 23, () => c.rect(18, y, 14, 30, "f"))
  c.hline(3, 62, 27, "f"); c.hline(2, 63, 28, "f")
}
const ROCK_TOP = 44
// Frame list: [figure, rise (px the figure sits lower than standing), stick].
const NEAR_FRAMES = [
  ["_raider_down", 40, null],   // 0 hidden behind the rock
  ["_raider_down", 24, "diag"], // 1 peeking
  ["_raider_down", 10, "diag"], // 2 rising
  ["_raider_up", 0, "flat"],    // 3 up, gaffi overhead
  ["_raider_up", -2, "flat"],   // 4 the shake: up 2 px
]
NEAR_FRAMES.forEach(([fig, rise, stick], i) => {
  // the figure and its stick get the dark outline; the rock is drawn after, unoutlined like the scenery
  sprite("_raider_fig_" + i, { w: 30, h: 62, outline: "1" }, (c) => {
    const top = 14 + rise
    if (rise >= 40) return
    if (stick === "flat") gaffiFlat(c, 2, top + 1)
    c.stamp(fig, 3, top)
    if (stick === "diag") gaffiDiag(c, 23, top + 10)
  })
  sprite("raider_near_" + i, { w: 32, h: 64 }, stamp("_raider_fig_" + i, 0, 0), (c) => rockNear(c, ROCK_TOP))
})

// ---- far raider: 12 px tall, on the horizon
const FAR_DOWN = `
..MMM.
.MWWWM
.XEXES
.MWsSs
..Ns..
.rrrrD
rRrrrD
rRrrDD
WrrrDN
.rrrr.
.MW.N.
.MW.N.
.DD.D.`
const FAR_UP = `
W....W
MMMM.M
WWWWMS
XEXESs
MWsSs.
.Ns...
rrrrD.
RrrrD.
RrrDD.
rrrr..
MW.N..
MW.N..
DD.D..`
// 14x30 + outline = 16x32
sprite("raider_far_0", { w: 14, h: 30, outline: "1" }, grid(4, 13, rk(FAR_DOWN)), line(11, 11, 12, 25, "9"))
sprite("raider_far_1", { w: 14, h: 30, outline: "1" }, grid(4, 12, rk(FAR_UP)), hline(1, 11, 12, "9"), px(0, 10, "a"))
sprite("raider_far_2", { w: 14, h: 30, outline: "1" }, grid(4, 11, rk(FAR_UP)), hline(1, 10, 12, "9"), px(0, 9, "a"))
