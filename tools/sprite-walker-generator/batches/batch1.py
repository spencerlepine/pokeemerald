"""Batch 1 (v3): generic kids and a brawler, composed from the vanilla sheets they replace
(STYLE.md 6). Writes art/<name>.yaml. Run from the tool folder: python batches/batch1.py

Step frames bob 1 px, so a patch drawn for `down` is repeated on down_a/down_b one row lower.
"""
import yaml

P = "graphics/object_events/pics/people/"
STEPS = {"down": ("down_a", "down_b"), "up": ("up_a", "up_b"), "left": ("left_a", "left_b")}
LEGEND = {".": 0, "1": 1, "2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 7, "8": 8, "9": 9,
          "A": 10, "B": 11, "C": 12, "D": 13, "E": 14, "F": 15, "_": -1}


def spec(name, gi, pal, desc, note, base=None, recolor=None, parts=None, patches=None, legend_extra=None):
    """patches: {stand_frame: [ {x, y, rows} ]}; each is also applied to that frame's two step
    frames one row lower."""
    legend = {k: v for k, v in LEGEND.items() if k != "_"}
    d = {"name": name, "description": desc, "kit": "person16x32", "replaces": P + f"{base or name}.png",
         "graphics_info": gi, "notes": note, "palette": pal, "palette_tag": f"OBJ_EVENT_PAL_TAG_{pal.upper()}",
         "base_sheet": P + f"{base or name}.png", "legend": legend}
    if recolor:
        d["recolor"] = recolor
    if parts:
        d["parts"] = parts
    frames = {}
    for stand, pts in (patches or {}).items():
        frames[stand] = {"patches": pts}
        for step in STEPS[stand]:
            frames[step] = {"patches": [{**p, "y": p["y"] + 1} for p in pts]}
    if frames:
        d["frames"] = frames
    text = yaml.safe_dump(d, sort_keys=False, width=100, default_style=None)
    open(f"art/{name}.yaml", "w").write(text)


# 1. Black Belt -> Teras Kasi brawler. Swap ramps A<->C: the lavender-white gi becomes a red-brown
#    training wrap... v3b: rotate the three ramps instead: wrap green, belt red-brown, hair grey. White headband stays.
spec("black_belt", "BlackBelt", "npc_3",
     "Teras Kasi brawler in a training wrap (replaces the Emerald BLACK BELT walker).",
     "Composed from black_belt.png: ramps rotated (wrap green, belt red-brown, hair grey).",
     recolor={5: 8, 6: 9, 7: 10, 8: 11, 9: 12, 10: 13, 11: 5, 12: 6, 13: 7})

# 2. Boy 1 -> moisture-farm kid: the lavender shirt already reads as a dusty tunic; add goggles
#    pushed up on the hair (lavender lenses, dark rims) front, side and the strap at the back.
spec("boy_1", "Boy1", "npc_3",
     "Moisture-farm kid in a desert tunic and goggles (replaces the Emerald BOY 1 walker).",
     "Composed from boy_1.png plus goggles on the brow (rows 15-16).",
     patches={
         "down": [{"x": 2, "y": 15, "rows": "D7565D565D7D"}, {"x": 2, "y": 16, "rows": "_D777_777D__"}],
         "left": [{"x": 2, "y": 15, "rows": "D7565D"}, {"x": 3, "y": 16, "rows": "D777D"}],
         "up": [{"x": 2, "y": 15, "rows": "D7777777777D"}],
     })

# 3. Boy 2 -> spaceport kid in a flight jacket: same art on NPC_2, where ramp A is the yellow-orange
#    of a flight jacket and ramp B the red of the trousers (Emerald recolours by palette tag too).
spec("boy_2", "Boy2", "npc_2",
     "Spaceport kid in a padded flight jacket (replaces the Emerald BOY 2 walker).",
     "boy_2.png moved from NPC_1 to NPC_2: orange jacket, red shorts, brown hair; collar seams stay.")

# 4. Boy 3 -> market-town kid with a toy blaster: shirt magenta -> grey, the toy in pink so it
#    reads as plastic, held in the right hand (down) and pointed ahead (left).
spec("boy_3", "Boy3", "npc_4",
     "Market-town kid with a toy blaster (replaces the Emerald BOY 3 walker).",
     "Composed from boy_3.png: shirt to ramp C (grey); pink toy blaster patched into the hand.",
     recolor={8: 11, 9: 12, 10: 13},
     patches={
         "down": [{"x": 12, "y": 24, "rows": "_A9A\n_A8A\n__A_"}],
         "left": [{"x": 9, "y": 24, "rows": "AA98A\n_A9A_"}],
     })

# 5. Bug Catcher -> kid with a bug net: a net on a pole (olive pole, white mesh) carried upright
#    beside him; the straw hat and blue shirt are already right.
NET = "_AA_\nAE8A\nA8EA\nAE8A\n_AA_"  # a 4x5 mesh bag: white and light blue, outlined dark blue
NET_R = [{"x": 12, "y": 11, "rows": NET}] + [{"x": 13, "y": 16 + i, "rows": "D"} for i in range(15)]
NET_L = [{"x": 0, "y": 11, "rows": NET}] + [{"x": 2, "y": 16 + i, "rows": "D"} for i in range(15)]
spec("bug_catcher", "BugCatcher", "npc_1",
     "Kid with a bug net and specimen jar (replaces the Emerald BUG CATCHER walker).",
     "Composed from bug_catcher.png plus a bug net on a pole (right side facing down, left side facing up/left).",
     patches={"down": NET_R, "up": NET_L, "left": NET_L})
print("ok")
