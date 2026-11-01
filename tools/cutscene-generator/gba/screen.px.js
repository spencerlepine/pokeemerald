// gbaScreen(): preview a GBA screen made of scrolling text BGs and OBJ sprites, as an animation.
// include("<tool>/gba/screen.px.js") from an art file, then:
//
//   gbaScreen("screen", {
//     frames: 32, fps: 30, w: 240, h: 160,            // GBA screen; 60 fps hardware, 30 is plenty to judge motion
//     bg:  [{ asset: "bg3", speed: 1/256, y: 0 }, ...],  // back to front; speed = px per game frame (HOFS -= speed)
//     obj: [{ asset: "kael_0" | (f) => name, x, y }],    // top-left corner, back to front
//     swap: { asset: ["bg3"], a: "#f86040", b: "#806858", every: 8 },  // palette-cycle two colors (CycleSceneryPalette)
//     step: 2,                                         // game frames per preview frame (60 fps / fps)
//   })
//
// BGs wrap every 256 px like the hardware. Each preview frame f shows game frame f * step.
function gbaScreen(name, o) {
  const frames = o.frames ?? 32, fps = o.fps ?? 30, step = o.step ?? Math.round(60 / fps)
  anim(name, { w: o.w ?? 240, h: o.h ?? 160, frames, fps }, (c) => {
    const g = c.frame * step
    for (const b of o.bg ?? []) {
      const lit = o.swap && o.swap.asset.includes(b.asset) && Math.floor(g / (o.swap.every ?? 8)) % 2 === 1
      const opts = lit ? { swap: { [o.swap.a]: o.swap.b, [o.swap.b]: o.swap.a } } : undefined
      const x = ((Math.round((b.speed ?? 0) * g) % 256) + 256) % 256
      for (const xx of [x - 256, x]) c.stamp(b.asset, xx, -(b.y ?? 0), opts)
    }
    for (const s of o.obj ?? []) c.stamp(typeof s.asset === "function" ? s.asset(g, c.frame) : s.asset, s.x, s.y)
  })
}
