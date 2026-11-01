// KAEL and MIRA on the speeder bike, for intro scene 2 (brendan.png / may.png, 4 frames of 64x64).
// Included from intro_bike.px.js after use(PLAYER).
//
// The figures are written with material letters, then mapped to palette indices per character,
// so both riders share one pose and differ only in head, hair and colors (they share player.pal).
//   H hair   h hair dark   B band   b band light   K skin   k skin shade   E eye
//   T top    L top light   S top shade             P legs   Q legs dark    G gloves/boots
//   W band tails (blow back, animated per frame)

const MAT = {
  kael: { H: "a", h: "f", B: "c", b: "b", W: "c", w: "b", K: "8", k: "9", E: "1", T: "e", L: "d", S: "a", P: "a", Q: "f", G: "7" },
  mira: { H: "a", h: "f", B: "5", b: "6", W: "5", w: "6", K: "8", k: "9", E: "1", T: "d", L: "4", S: "e", P: "d", Q: "e", G: "7" },
}
const paint = (who, s) => s.replace(/[A-Za-z]/g, (ch) => MAT[who][ch] ?? ch)

// Head, facing left, 3/4 profile. Origin = top-left of the figure (see RIDER_X/Y).
const HEAD = {
  kael: `
......H.HHH.H.....
....HHHHHHHHHH....
...HHHHHHHHHHHh...
..HHHHHHHHHHHHhh..
..BBBBBBBBHHHHhh..
.BbbBBBBBBBBHHhh..
.BBBBBBBBBBBHhhh..
.KKKKkKKHHHHhhh...
.KKEKKKKHHhHhh....
KKKEKKKKKkkHhh....
.KKKKKKKkkkhh.....
KKKKKKKKkkkh......
.KKKKKkkkkk.......
...kkkkkkk........`,
  mira: `
.....HHHHHH.......
...HHHHHHHHHH.hh..
..HHHHHHHHHHHhHHh.
.HHHHHHHHHHHhHHHHh
.BBBBBBBBHHHhHHHHh
BbbBBBBBBBBBhhHHhh
BBBBBBBBBBBBHhhhh.
.KKKKkKKHHHHhh....
.KKEKKKKHHhHHh....
KKKEKKKKKkkHHhh...
.KKKKKKKkkkHHhh...
KKKKKKKKkkkhHhh...
.KKKKKkkkkk.hhh...
...kkkkkkk........`,
}

// Body: leaning into the ride, arm reaching down to the grip, near leg bent onto the footrest.
const BODY = `
....kkkLLLL.......
...LLLLLLLLLT.....
..LLLTTTTTTTS.....
..LTTTTTTTTTSS....
..LTTTTTTTTTTSS...
...TTTTTTTTTTTSS..
...TTTTTTTTTTTSS..
....TTTTTTTTTTTSS.
....STTTTTTTTTTSS.
.....QQQQQQQQQQQQ.
.....PPPPPPPPPPPQ.
....PPPPPPPPPPPPQ.
..PPPPPPPPPPPPPQQ.
.PPPPPPPPPPPPPQQ..
.PPPPPPPQQQQQQ....
.PPPPQ............
..PPPQ............
..PPPQ............
..PPPQ............
.GGGGQ............
GGGGGGG...........`
// The near arm, drawn over the torso with its own dark edge, reaching down to the grip.
const ARM = `
........1LL
.......1LLT
......1LLT1
.....1LLT1.
....1LLT1..
...1LLT1...
..1LLT1....
GGLLT1.....
GGG11......`

// Band tails streaming back from the knot, 4 frames.
const TAILS = [
  `
WW.....
WwWW...
.WWwWW.
...WWW.`,
  `
WW.....
WWwW...
.WWWwWW
....WW.`,
  `
WW.....
WwWWW..
..WWwW.
...WWWW`,
  `
WW.....
WWwWW..
.WWWWw.
..WW...`,
]

const RIDER_X = 20, RIDER_Y = 7
for (const who of ["kael", "mira"]) {
  sprite("_" + who + "_body", { w: 62, h: 62 },
    grid(RIDER_X + 2, RIDER_Y + 13, paint(who, BODY)),
    grid(RIDER_X, RIDER_Y, paint(who, HEAD[who])),
    grid(RIDER_X - 4, RIDER_Y + 15, paint(who, ARM)),
  )
  for (let f = 0; f < 4; f++) {
    const bob = f === 1 || f === 2 ? 1 : 0
    sprite(who + "_" + f, { w: 62, h: 62, outline: 1 },
      grid(RIDER_X + 13, RIDER_Y + 5 + bob, paint(who, TAILS[f])),
      stamp("_" + who + "_body", 0, bob),
    )
  }
}
