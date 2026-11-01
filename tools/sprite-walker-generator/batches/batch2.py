"""Batch 2 (v3): three non-humans, built the way D13 says: vanilla anatomy as material regions
(a kid's body for Yoda, the fat man's body for Dexter), new heads and props drawn as regions,
tones chosen by the learned shader. IG-88 has no vanilla body and is drawn as regions outright.
Writes art/<name>.yaml. Run from the tool folder: python batches/batch2.py
"""
import yaml

P = "graphics/object_events/pics/people/"
STEPS = {"down": ("down_a", "down_b"), "up": ("up_a", "up_b"), "left": ("left_a", "left_b")}


def block(x, y, text):
    rows = text.strip("\n").split("\n")
    assert len({len(r) for r in rows}) == 1, rows
    assert x + len(rows[0]) <= 16, (x, rows[0])
    return {"x": x, "y": y, "rows": "\n".join(rows)}


def spec(name, gi, pal, replaces, desc, note, materials, legend, accept, base=None, remap=None,
         patches=None, frames=None, steps=None):
    d = {"name": name, "description": desc, "kit": "person16x32", "replaces": P + replaces,
         "graphics_info": gi, "notes": note, "palette": pal, "palette_tag": f"OBJ_EVENT_PAL_TAG_{pal.upper()}",
         "shade": True, "materials": materials, "legend": legend, "accept": accept}
    if base:
        d["base_sheet"] = P + base
        if remap:
            d["remap"] = remap
    fr = {}
    for stand, pts in (patches or {}).items():
        fr[stand] = {"patches": pts}
        for step in STEPS[stand]:
            fr[step] = {"patches": [{**p, "y": p["y"] + 1} for p in pts]}
    for k, g in (frames or {}).items():
        for r in g:
            assert len(r) == 16, (name, k, len(r), r)
        fr[k] = "\n".join(g) + "\n"
    for k, (b, py, rows) in (steps or {}).items():
        for r in rows:
            assert len(r) == 16, (name, k, len(r), r)
        fr[k] = {"base": b, "shift": 1, "patch_y": py, "rows": "\n".join(rows) + "\n"}
    d["frames"] = fr
    open(f"art/{name}.yaml", "w").write(yaml.safe_dump(d, sort_keys=False, width=200))


# ------------------------------------------------------------------ YODA (replaces Juan)
# Regions only: no vanilla body is 16 rows tall with a 16-wide head. Identity at 1x: green,
# ears out to the frame edges at eye level, two white wisps, rust robe open on a cream tunic.
# g = green hide (ramp b on NPC_3), c = robe (ramp c), w = tunic (white, edged in ramp c),
# W = hard white wisps, k = hard black eyes.
YODA = {
    "down": [
        "................", "................", "................", "................",
        "................", "................", "................", "................",
        "................", "................", "................", "................",
        "................", "................", "................",
        ".....GGGGGG.....",  # 15 crown (G: skull dome, its own volume)
        "...WGGGGGGGGW...",  # 16 wisps
        "..GGGGGGGGGGGG..",  # 17
        "E.GGGGGGGGGGGG.E",  # 18 ear tips (E: ears)
        "EEEgggggggggggEE",  # 19 ears, face starts
        "EEEggkggggkggEEE",  # 20 eyes
        ".EEggkggggkggEE.",  # 21
        "..gggggggggggg..",  # 22
        "...gggggggggg...",  # 23
        "....gggggggg....",  # 24 chin
        "...CccwwwwccC...",  # 25 sleeves C, tunic V
        "..CCccwwwwccCC..",  # 26
        ".gCCcccwwcccCCg.",  # 27 hands
        "..cccccccccccc..",  # 28
        "..cccccccccccc..",  # 29
        "...gg......gg...",  # 30 toes
        "................"],
    "left": [
        "................", "................", "................", "................",
        "................", "................", "................", "................",
        "................", "................", "................", "................",
        "................", "................", "................",
        "....GGGGGG......",  # 15
        "..WGGGGGGGG.....",  # 16
        "..GGGGGGGGGG....",  # 17
        ".GGGGGGGGGGG..E.",  # 18 back ear tip
        ".gggggggggGGEEEE",  # 19 back ear
        ".ggkggggggggEEE.",  # 20 eye at the front
        ".ggkggggggggEE..",  # 21
        "..gggggggggg....",  # 22
        "...ggggggggg....",  # 23
        "....gggggggg....",  # 24
        "...cwwcccccc....",  # 25 tunic at the chest
        "..ccwwCCcccccc..",  # 26 near sleeve
        "..ccwcCCccccc...",  # 27
        "..ccccggcccccc..",  # 28 near hand
        "..cccccccccccc..",  # 29
        "....gg...gg.....",  # 30
        "................"],
}
YODA["up"] = [r.replace("k", "g") for r in YODA["down"][:24]] + [
    "...cccccccccc...",  # 24 hood collar
    "..CCccccccccCC..",  # 25 sleeves
    "..CCccccccccCC..",  # 26
    ".gCCccccccccCCg.",  # 27 hands
    "..cccccccccccc..",  # 28
    "..cccccccccccc..",  # 29
    "...gg......gg...",  # 30
    "................"]
spec("yoda", "Juan", "npc_3", "gym_leaders/juan.png",
     "YODA: small green Jedi Master in a rust robe (replaces Juan).",
     "D13 regions only: 16 rows tall by design (a small species), ears to the frame edges, wisps, robe open on a cream tunic. Toes and hem move in the step frames.",
     materials={"g": "skin-b", "G": "b", "E": "b", "c": "c!", "C": "c!", "w": "w/c"}, legend={"k": 15, "W": 14},
     accept={"height": "Yoda is a small species: 16 rows", "eye_row": "eyes sit high on a short bald head",
             "hair_rows": "two wisps, no hair mass", "skin_tones": "green hide uses ramp B", "head_w": "16 wide ear to ear",
             "step_change": "the robe hides the legs; the bob, the hem, the hands and the toes move"},
     frames=YODA,
     steps={
         "down_a": ("down", 27, [".gCCccccccccCCg.", "..cccccccccccc..", "..cccccccccccc..", "...gg..........."]),
         "down_b": ("down", 27, [".gCCccccccccCCg.", "..cccccccccccc..", "..cccccccccccc..", "...........gg..."]),
         "up_a": ("up", 27, [".gCCccccccccCCg.", "..cccccccccccc..", "..cccccccccccc..", "...gg..........."]),
         "up_b": ("up", 27, [".gCCccccccccCCg.", "..cccccccccccc..", "..cccccccccccc..", "...........gg..."]),
         "left_a": ("left", 27, ["..ccccCCccccc...", "..cccccggccccc..", "..cccccccccccc..", "...gg..........."]),
         "left_b": ("left", 27, ["..cCCccccccc....", "..cggccccccccc..", "..cccccccccccc..", ".........gg....."]),
     })

# ------------------------------------------------------------------ IG-88 (replaces Noland)
# Regions only. Identity at 1x: a tall narrow cylinder head with a dark sensor band and three
# lights, a thin neck, a boxy chest on a shoulder bar, pipe limbs with dark joints, 23 rows tall.
# c = chassis (ramp c greys on NPC_4), d = dark steel band/joints (ramp a), p/P = hard pink
# sensors (8, 9), W = hard white light, e = chest panel (ramp a as its own volume).
IG = {
    "down": [
        "................", "................", "................", "................",
        "................", "................", "................",
        ".....cccccc.....",  # 7  dome top
        "....cccccccc....",  # 8
        "....cccccccc....",  # 9
        "....ddpWWpdd....",  # 10 sensor band
        "....dddddddd....",  # 11
        "....cccccccc....",  # 12
        "....ccdccdcc....",  # 13 slits
        "....ccdccdcc....",  # 14
        ".....cccccc.....",  # 15
        "......dddd......",  # 16 neck
        "......dddd......",  # 17
        ".cccccccccccccc.",  # 18 shoulder bar
        ".cc.cccccccc.cc.",  # 19
        ".dd.cceeeecc.dd.",  # 20 arms / chest panel
        ".dd.cceeeecc.dd.",  # 21
        ".cc.cccccccc.cc.",  # 22
        ".cc..dddddd..cc.",  # 23 waist
        ".dd...dddd...dd.",  # 24
        ".....cc..cc.....",  # 25 thighs
        ".....cc..cc.....",  # 26
        ".....dd..dd.....",  # 27 knees
        ".....cc..cc.....",  # 28
        ".....cc..cc.....",  # 29
        "....ddd..ddd....",  # 30 feet
        "................"],
    "left": [
        "................", "................", "................", "................",
        "................", "................", "................",
        ".....cccccc.....",  # 7
        "....cccccccc....",  # 8
        "....cccccccc....",  # 9
        "....dpWdddd.....",  # 10 band wraps round
        "....dddddddd....",  # 11
        "....cccccccc....",  # 12
        "....cdccdccc....",  # 13
        "....cdccdccc....",  # 14
        ".....cccccc.....",  # 15
        "......dddd......",  # 16
        "......dddd......",  # 17
        "....cccccccc....",  # 18 shoulders (narrow from the side)
        "....cccccccc....",  # 19
        "...ddcccccc.....",  # 20 near arm in front
        "...ddcccccc.....",  # 21
        "...cccccccc.....",  # 22
        "...cc.dddddd....",  # 23
        "...dd..dddd.....",  # 24
        "......cccc......",  # 25
        "......cccc......",  # 26
        "......dddd......",  # 27
        "......cccc......",  # 28
        "......cccc......",  # 29
        ".....ddddd......",  # 30
        "................"],
}
IG["up"] = [r.replace("p", "d").replace("W", "d").replace("e", "c") for r in IG["down"]]
IG["up"][13] = IG["up"][14] = "....cccccccc...."
spec("ig88", "Noland", "npc_4", "frontier_brains/noland.png",
     "IG-88: tall assassin droid with a cylindrical sensor head (replaces Noland).",
     "D13 regions only (no vanilla body is this shape). NPC_4 for the greys; 23 rows tall on purpose. Limbs swing in the step frames.",
     materials={"c": "c", "d": "a", "e": "a"}, legend={"p": 9, "W": 14},
     accept={"height": "23 rows: IG-88 towers over people", "head_w": "8 px cylinder head by design", "eye_row": "no eyes; a sensor band",
             "hair_rows": "no hair; the dome is seen from above", "skin_tones": "a droid has no skin",
             "orphans": "machined surfaces; the only specks are the sensor lights", "step_change": "thin limbs change few pixels although all four swing"},
     frames=IG,
     steps={
         "down_a": ("down", 19, [".cc.cccccccc.dd.", ".dd.cceeeecc.dd.", ".dd.cceeeecc.cc.", ".cc.cccccccc.cc.", ".cc..dddddd.....", ".....ddddd...dd.",
                                 ".....cc..cc.....", ".....cc..dd.....", ".....dd..cc.....", ".....cc..cc.....", "....ddd.........", "........ddd....."]),
         "down_b": ("down", 19, [".dd.cccccccc.cc.", ".dd.cceeeecc.dd.", ".cc.cceeeecc.dd.", ".cc.cccccccc.cc.", "......dddddd.cc.", ".dd..ddddd......",
                                 ".....cc..cc.....", ".....dd..cc.....", ".....cc..dd.....", ".....cc..cc.....", "........ddd.....", "....ddd........."]),
         "up_a": ("up", 19, [".cc.cccccccc.dd.", ".dd.cccccccc.dd.", ".dd.cccccccc.cc.", ".cc.cccccccc.cc.", ".cc..dddddd.....", ".....ddddd...dd.",
                             ".....cc..cc.....", ".....cc..dd.....", ".....dd..cc.....", ".....cc..cc.....", "....ddd.........", "........ddd....."]),
         "up_b": ("up", 19, [".dd.cccccccc.cc.", ".dd.cccccccc.dd.", ".cc.cccccccc.dd.", ".cc.cccccccc.cc.", "......dddddd.cc.", ".dd..ddddd......",
                             ".....cc..cc.....", ".....dd..cc.....", ".....cc..dd.....", ".....cc..cc.....", "........ddd.....", "....ddd........."]),
         "left_a": ("left", 25, ["....cc..cc......", "....cc..cc......", "....dd..dd......", "....cc..cc......", "...ddd..ddd....."]),
         "left_b": ("left", 25, ["......cccc......", "......cccc......", "......dddd......", "......cccc......", ".....ddddd......"]),
     })

# ------------------------------------------------------------------ DEXTER JETTSTER (replaces Brandon)
# Body: fat_man's regions (shirt -> apron w, skin -> hide, trousers -> blue b). Head drawn new:
# a wide bald dome with a crest ridge (r: ramp c as its own thin volume -> reads dark),
# wide-set small eyes, a very wide mouth (m) with a wattle (j) under it. A second pair of arms
# (H) folded across the apron. NPC_1: ramp c is olive hide, ramp b blue, white apron.
DEX_HEAD_D = block(0, 9, """
.......rr.......
......rrrr......
.....hhrrhh.....
...hhhhrrhhhh...
..hhhhhhhhhhhh..
..hhhhhhhhhhhh..
.hhkhhhhhhhhkhh.
.hhkhhhhhhhhkhh.
.hhhMMMMMMMMhhh.
.hhjjjjjjjjjjhh.
..hhjjjjjjjjhh..
...hhhhhhhhhh...""")
DEX_HEAD_U = block(0, 9, """
.......rr.......
......rrrr......
.....hhrrhh.....
...hhhhrrhhhh...
..hhhhhrrhhhhh..
..hhhhhhhhhhhh..
.hhhhhhhhhhhhhh.
.hhhhhhhhhhhhhh.
.hhhhhhhhhhhhhh.
.hhhhhhhhhhhhhh.
..hhhhhhhhhhhh..
...hhhhhhhhhh...""")
DEX_HEAD_L = block(0, 9, """
.......rr.......
......rrrr......
.....hhhrrh.....
...hhhhhhrrhh...
..hhhhhhhhhrhh..
..hhhhhhhhhhhh..
..hkhhhhhhhhhhh.
..hkhhhhhhhhhhh.
.MMMMMMMhhhhhhh.
.jjjjjjjhhhhhhh.
..jjjjjjhhhhhh..
...hhhhhhhhhh...""")
# second pair of arms: raised and spread, so the silhouette has four limbs
UP_ARMS_D = [block(0, 19, "U.\nUU\nUU\n.U".replace("\\n", "\n")), block(14, 19, ".U\nUU\nUU\nU.".replace("\\n", "\n"))]
UP_ARMS_L = [block(1, 19, "U.\nUU\n.U".replace("\\n", "\n"))]
spec("dexter", "Brandon", "npc_3", "frontier_brains/brandon.png",
     "DEXTER JETTSTER: four-armed Besalisk cook in an apron (replaces Brandon).",
     "D13: fat_man's body as regions (shirt -> apron, skin -> olive hide, trousers -> blue), new crested head with a wide mouth and wattle, second pair of arms raised at the shoulders. Moves to NPC_1 for the olive ramp.",
     materials={"h": "skin-a", "U": "a", "r": "a", "j": "skin-a", "w": "w/a!", "b": "c!"}, legend={"k": 15, "M": 7},
     accept={"height": "22 rows: the crest adds 2 on top of fat_man's 20", "skin_tones": "Besalisk hide uses ramp A, not the human skin ramp", "eye_row": "small eyes high on a wide hairless head",
             "hair_rows": "no hair: a short crest", "step_change": "the folded arms and apron hang still; the bob, hem and feet move"},
     base="fat_man.png", remap={"s": "h", "b": "w", "c": "b", "a": "b"},
     patches={"down": [DEX_HEAD_D, *UP_ARMS_D],
              "up": [DEX_HEAD_U, *UP_ARMS_D],
              "left": [DEX_HEAD_L, *UP_ARMS_L]})
print("ok")
