"""Batch 1 (v4): composed from the vanilla sheets they replace (STYLE.md 6), then reshaped, not
just recoloured: a new head, hat, hem, collar or prop per character. Writes art/<name>.yaml.
Run from the tool folder: python batches/batch1.py

Owner rules: hand-held props stay short (a tall pole does not sit right when the sprite walks);
shapes change, not only paint. Step frames bob 1 px, so a patch drawn for `down` is repeated on
down_a/down_b one row lower.
"""
import yaml

P = "graphics/object_events/pics/people/"
STEPS = {"down": ("down_a", "down_b"), "up": ("up_a", "up_b"), "left": ("left_a", "left_b")}
LEGEND = {".": 0, "1": 1, "2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 7, "8": 8, "9": 9,
          "A": 10, "B": 11, "C": 12, "D": 13, "E": 14, "F": 15}


def spec(name, gi, pal, desc, note, base=None, recolor=None, parts=None, patches=None, accept=None):
    d = {"name": name, "description": desc, "kit": "person16x32", "replaces": P + f"{base or name}.png",
         "graphics_info": gi, "notes": note, "palette": pal, "palette_tag": f"OBJ_EVENT_PAL_TAG_{pal.upper()}",
         "base_sheet": P + f"{base or name}.png", "legend": dict(LEGEND)}
    if recolor:
        d["recolor"] = recolor
    if parts:
        d["parts"] = parts
    if accept:
        d["accept"] = accept
    frames = {}
    for stand, pts in (patches or {}).items():
        for p in pts:
            for ln in p["rows"].split("\n"):
                assert p["x"] + len(ln) <= 16, (name, stand, p)
        frames[stand] = {"patches": pts}
        for step in STEPS[stand]:
            frames[step] = {"patches": [{**p, "y": p["y"] + 1} for p in pts]}
    if frames:
        d["frames"] = frames
    open(f"art/{name}.yaml", "w").write(yaml.safe_dump(d, sort_keys=False, width=100))


def block(x, y, text):
    """One patch from a multi-line string (rows must be equal length; `_` keeps the pixel)."""
    return {"x": x, "y": y, "rows": text.strip("\n")}


# 1. Black Belt -> Teras Kasi brawler: ramps rotated (wrap green, belt red-brown, hair grey), then a
#    new head: shaved skull with a grey topknot instead of the spiky hair; forehead shows under the band.
BALD_DOWN = block(2, 10, """
....656.....
...47674....
..41122224..
.41112222234
411122222334
7EE111122EE7
75EE1111EE57""")
BALD_UP = block(2, 10, """
....656.....
...47674....
..41122224..
.41112222234
411122222334
7EE222233EE7
75EE2233EE57""")
BALD_LEFT = block(2, 10, """
....656.....
...47674....
..41122224..
.41112222234
411122222334
7EE111223EE7
75EE1123EE57""")
spec("black_belt", "BlackBelt", "npc_3",
     "Teras Kasi brawler in a training wrap (replaces the Emerald BLACK BELT walker).",
     "black_belt.png with ramps rotated (wrap green, belt red-brown, hair grey) and a shaved head with a topknot drawn over the hair rows.",
     recolor={5: 8, 6: 9, 7: 10, 8: 11, 9: 12, 10: 13, 11: 5, 12: 6, 13: 7},
     patches={"down": [BALD_DOWN], "up": [BALD_UP], "left": [BALD_LEFT]},
     accept={"hair_rows": "shaved head: skin starts one row under the topknot"})

# 2. Boy 1 -> moisture-farm kid: goggles pushed up on the hair, and the shirt becomes a knee-length
#    tunic (the shorts rows are redrawn as hem), so the silhouette is a straight tunic, not shirt+shorts.
spec("boy_1", "Boy1", "npc_3",
     "Moisture-farm kid in a desert tunic and goggles (replaces the Emerald BOY 1 walker).",
     "boy_1.png plus goggles on the brow (rows 15-16) and a tunic hem over the shorts (rows 27-28).",
     patches={
         "down": [block(2, 15, "D7565D565D7D"), block(2, 16, "_D777_777D__"), block(3, 27, "7666666667\n7766666677")],
         "left": [block(2, 15, "D7565D"), block(3, 16, "D777D"), block(4, 27, "7666667\n7766677")],
         "up": [block(2, 15, "D7777777777D"), block(3, 27, "7666666667\n7766666677")],
     })

# 3. Boy 2 -> spaceport kid: NPC_2 turns the shirt orange and the shorts red (a flight jacket), and a
#    red leather flight cap with ear flaps replaces the hair (brown would vanish into the brown hair), with puffed shoulders on the jacket.
CAP_DOWN = block(3, 12, """
..AAAAAA..
.AA9999AA.
A98999998A
A99999999A
AA999999AA
A2A9999A2A""")
CAP_UP = block(3, 12, """
..AAAAAA..
.AA9999AA.
A98999998A
A99999999A
AA999999AA
A9A9999A9A""")
CAP_LEFT = block(3, 12, """
..AAAAA...
.AA9999AA.
A99999998A
A99999999A
AA999999AA
A1AA9999AA""")
spec("boy_2", "Boy2", "npc_2",
     "Spaceport kid in a padded flight jacket (replaces the Emerald BOY 2 walker).",
     "boy_2.png on NPC_2 (orange jacket, red shorts) with a red flight cap with ear flaps over the hair and wider shoulders.",
     patches={
         "down": [CAP_DOWN, block(1, 22, "AA9944334499AA")],
         "up": [CAP_UP, block(1, 22, "AA8FFDDDDFF8AA")],
         "left": [CAP_LEFT],
     })

# 4. Boy 3 -> market-town kid: a pink cap with a brim replaces the hair, the shirt is grey with dark
#    vest edges, and a short pink toy blaster sits in the hand (held low, never above the shoulder).
spec("boy_3", "Boy3", "npc_4",
     "Market-town kid with a toy blaster (replaces the Emerald BOY 3 walker).",
     "boy_3.png: cap with a brim over the hair (ramp B pink), shirt to ramp C grey with vest edges, toy blaster in the hand.",
     recolor={8: 11, 9: 12, 10: 13},
     patches={
         "down": [block(2, 12, "....AAAA....\n..AA9999AA..\n.A99988999A.\nA9999999999A\nAAAAAAAAAAAA"),
                  block(5, 23, "D____D\nD____D\nD____D"), block(12, 24, "_A9A\n_A8A\n__A_")],
         "up": [block(2, 12, "....AAAA....\n..AA9999AA..\n.A99999999A.\nA9999999999A\nAAAAAAAAAAAA")],
         "left": [block(2, 12, "....AAAA....\n..AA9999AA..\n.A99988999A.\nA9999999999A\nAAAAAAAAAAA_"),
                  block(9, 24, "AA98A\n_A9A_")],
     })

# 5. Bug Catcher -> kid with a bug net: a short net held low at the hip (mesh 3x4, a 2 px handle to
#    the hand) instead of a tall pole; straw hat and blue shirt are already right.
NET = "_AA\nAE8\nA8E\n_AA"
spec("bug_catcher", "BugCatcher", "npc_1",
     "Kid with a bug net and specimen jar (replaces the Emerald BUG CATCHER walker).",
     "bug_catcher.png plus a short-handled net held at the hip (down: right side; up/left: left side).",
     patches={
         "down": [block(13, 23, NET), block(13, 22, "D")],
         "up": [block(0, 23, NET), block(2, 22, "D")],
         "left": [block(0, 24, "_AA_\nAE8D\nA8EA\n_AA_")],
     })
print("ok")
