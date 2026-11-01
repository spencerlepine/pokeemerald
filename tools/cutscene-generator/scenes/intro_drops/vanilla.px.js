// Study: intro scene 1 as Emerald ships it (graphics/intro/scene_1).
include("../../gba/screen.px.js")
const D = "graphics/intro/scene_1/"
for (let i = 0; i < 4; i++) ref("v_bg" + i, D + "bg.png", { map: D + "bg" + i + "_map.bin" })
ref("v_logo", D + "drops_logo.png", { pal: D + "logo.pal" })
ref("v_flygon", D + "flygon.png")
