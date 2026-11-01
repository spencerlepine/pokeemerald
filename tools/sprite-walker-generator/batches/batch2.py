"""Batch 2: three aliens/droids drawn from scratch (no vanilla silhouette fits), one tile high,
in Emerald's style (STYLE.md). Writes art/<name>.yaml. Run from the tool folder.

Each spec `accept`s the human-face rules it cannot meet, with the reason.
"""
import yaml

P = "graphics/object_events/pics/people/"
LEGEND = {".": 0, "1": 1, "2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 7, "8": 8, "9": 9,
          "A": 10, "B": 11, "C": 12, "D": 13, "E": 14, "F": 15}


def spec(name, gi, pal, replaces, desc, note, frames, steps, accept):
    for k, g in frames.items():
        for r in g:
            assert len(r) == 16, (name, k, len(r), r)
    for k, (b, py, rows) in steps.items():
        for r in rows:
            assert len(r) == 16, (name, k, len(r), r)
        assert py + len(rows) <= 32, (name, k)
    d = {"name": name, "description": desc, "kit": "person16x32", "replaces": P + replaces,
         "graphics_info": gi, "notes": note, "palette": pal, "palette_tag": f"OBJ_EVENT_PAL_TAG_{pal.upper()}",
         "legend": dict(LEGEND), "accept": accept, "frames": {}}
    for k in ("down", "up", "left"):
        d["frames"][k] = "\n".join(frames[k]) + "\n"
    for k, (b, py, rows) in steps.items():
        d["frames"][k] = {"base": b, "shift": 1, "patch_y": py, "rows": "\n".join(rows) + "\n"}
    open(f"art/{name}.yaml", "w").write(yaml.safe_dump(d, sort_keys=False, width=200))


def mirror(left8):
    """A symmetric 16-wide row from its left half."""
    assert len(left8) == 8, left8
    return left8 + left8[::-1]


# ---------------------------------------------------------------- YODA (replaces Juan, 16x32)
# NPC_3: green ramp 8/9/A for the skin, lavender-grey 5/6/7 for the robe, red-brown B/C/D for the
# gimer stick. Short (15 rows), wide head, ears out to the frame edge, wide-set eyes.
yoda = spec(
    "yoda", "Juan", "npc_3", "gym_leaders/juan.png",
    "YODA: small green Jedi Master with a gimer stick (replaces Juan).",
    "From scratch. Juan ships on NPC_4; Yoda moves to NPC_3 for the green ramp. 15 rows tall on purpose.",
    frames={
        "down": [
            mirror("......AA"), mirror("....AA88"), mirror("..AA9888"), mirror(".A989888"),
            "A9A9F888888F9A9A", ".AA9F888888F9AA.", mirror("...A9988"), mirror("....A999"),
            mirror("...75566"), mirror("..756667"), mirror("..756667"), "..756679966657..",
            mirror("..776667"), mirror("..777777"), "....A9A..A9A....", "................"],
        "up": [
            mirror("......AA"), "....AA8999AA....", mirror("..AA9999"), mirror(".A989999"),
            mirror("A9A99999"), mirror(".AA99999"), mirror("...A9999"), mirror("....A999"),
            mirror("...75666"), mirror("..756666"), mirror("..756666"), mirror("..756666"),
            mirror("..776666"), mirror("..777777"), "....A9A..A9A....", "................"],
        "left": [
            "......AAAA......", "....AA8888AA....", "...A988888899A..", "..A988888899989A",
            "..A9F8888999A...", "..AAF8888999AA..", "...A9988899A....", "..D.A99999A.....",
            "..C.75666657....", "..C7566666657...", "..C7566666657...", "..C9966666657...",
            "..C7766666677...", "..C777777777....", "..D.A9A.A9A.....", "................"],
    },
    steps={
        "down_a": ("down", 28, ["..756699666657..", mirror("..776666"), mirror("..777777"), "....A9A...AA...."]),
        "down_b": ("down", 28, ["..756666996657..", mirror("..776666"), mirror("..777777"), ".....AA..A9A...."]),
        "up_a": ("up", 29, [mirror("..776666"), mirror("..777777"), "....A9A...AA...."]),
        "up_b": ("up", 29, [mirror("..776666"), mirror("..777777"), ".....AA..A9A...."]),
        "left_a": ("left", 29, ["..C7766666677...", "..C777777777....", ".D.A9A...A9A...."]),
        "left_b": ("left", 29, ["..C7766666677...", "..C777777777....", "..D..A9AA9A....."]),
    },
    accept={"height": "15 rows: Yoda is a small species", "eye_row": "wide-set eyes sit high on a short bald head",
            "hair_rows": "bald; the skull top is two rows of skin", "skin_tones": "green skin uses ramp B (8/9/A), not the human skin ramp",
            "head_w": "head is 16 wide ear to ear, 12 without the ears", "step_change": "the robe hides the legs; hands, hem and toes move"},
)

# ---------------------------------------------------------------- IG-88 (replaces Noland, 16x32)
# NPC_4: greys B/C/D for the chassis, navy 5/6/7 for the limbs, pink 8/9 for the sensor lights.
# Tall (22 rows) and thin (6 wide head, 2 wide limbs), cylinder head seen from above.
ig88 = spec(
    "ig88", "Noland", "npc_4", "frontier_brains/noland.png",
    "IG-88: tall assassin droid with a cylindrical head (replaces Noland).",
    "From scratch. Noland ships on NPC_3; IG-88 moves to NPC_4 for the greys. 22 rows tall, 2 px limbs, on purpose.",
    frames={
        "down": [
            "......DDDD......", ".....DBBBCD.....", ".....DCCCCD.....", ".....D8CC8D.....",
            ".....DCCCCD.....", ".....D9CC9D.....", ".....DCCCCD.....", ".....DDCCDD.....",
            "......D77D......", "....DDDCCDDD....", "...DCDDCCDDDCD..", "...D6DDBCCDD6D..",
            "...D6D.DCCD.D6D.", "...D7D.D9CD.D7D.", "...DCD.DCCD.DCD.", "...DBD.DDDD.DBD.",
            ".......D77D.....", "......D7DD7D....", "......D6D.D6D...", "......D6D.D6D...",
            "......D7D.D7D...", ".....DCCD.DCCD..", "................"],
        "up": [
            "......DDDD......", ".....DBBBCD.....", ".....DCCCCD.....", ".....DCCCCD.....",
            ".....DCDDCD.....", ".....DCCCCD.....", ".....DCCCCD.....", ".....DDCCDD.....",
            "......D77D......", "....DDDCCDDD....", "...DCDDCCDDDCD..", "...D6DDCCCDD6D..",
            "...D6D.DCCD.D6D.", "...D7D.DCCD.D7D.", "...DCD.DCCD.DCD.", "...DBD.DDDD.DBD.",
            ".......D77D.....", "......D7DD7D....", "......D6D.D6D...", "......D6D.D6D...",
            "......D7D.D7D...", ".....DCCD.DCCD..", "................"],
        "left": [
            "......DDDD......", ".....DBBBCD.....", ".....DCCCCD.....", ".....D8CCCD.....",
            ".....DCCCCD.....", ".....D9CCCD.....", ".....DCCCCD.....", ".....DDCCDD.....",
            "......D77D......", ".....DDCCDD.....", ".....DCCCCD.....", "....D6DBCCD.....",
            "....D6DCCCD.....", "....D7D9CCD.....", "....DCDCCCD.....", "....DBDDDDD.....",
            "......D77D......", "......D77D......", "......D66D......", "......D66D......",
            "......D77D......", ".....DCCCD......", "................"],
    },
    steps={
        "down_a": ("down", 21, ["...D6DDBCCDD6D..", "...D6D.DCCD.DCD.", "...D7D.D9CD.DBD.", "...DCD.DCCD.....", "...DBD.DDDD.....",
                                ".......D77D.....", "......D7DD7D....", "......D6D.D6D...", "......D6D.D7D...", "......D7D.DCCD..", ".....DCCD......."]),
        "down_b": ("down", 21, ["...D6DDBCCDD6D..", "...DCD.DCCD.D6D.", "...DBD.D9CD.D7D.", ".......DCCD.DCD.", ".......DDDD.DBD.",
                                ".......D77D.....", "......D7DD7D....", "......D6D.D6D...", "......D7D.D6D...", "......DCCDD7D...", "..........DCCD.."]),
        "up_a": ("up", 21, ["...D6DDCCCDD6D..", "...D6D.DCCD.DCD.", "...D7D.DCCD.DBD.", "...DCD.DCCD.....", "...DBD.DDDD.....",
                            ".......D77D.....", "......D7DD7D....", "......D6D.D6D...", "......D6D.D7D...", "......D7D.DCCD..", ".....DCCD......."]),
        "up_b": ("up", 21, ["...D6DDCCCDD6D..", "...DCD.DCCD.D6D.", "...DBD.DCCD.D7D.", ".......DCCD.DCD.", ".......DDDD.DBD.",
                            ".......D77D.....", "......D7DD7D....", "......D6D.D6D...", "......D7D.D6D...", "......DCCDD7D...", "..........DCCD.."]),
        "left_a": ("left", 28, ["......D66D......", ".....D6DD6D.....", ".....D7D.D7D....", "....DCCD.DCCD..."]),
        "left_b": ("left", 28, ["......D66D......", "......D66D......", "......D77D......", ".....DCCCD......"]),
    },
    accept={"height": "22 rows: IG-88 towers over people", "head_w": "6 px cylinder head by design", "eye_row": "no eyes; pink sensors",
            "hair_rows": "no hair; the cylinder top is seen from above", "skin_tones": "a droid has no skin",
            "orphans": "machined surfaces: the only specks are the sensors and the hand highlights",
            "step_change": "2 px limbs: both arms and both legs swing and the body bobs, but thin limbs change few pixels"},
)

# ---------------------------------------------------------------- DEXTER JETTSTER (replaces Brandon)
# NPC_3: lavender-grey 5/6/7 as Besalisk hide, white apron (E), red-brown B/C/D trousers and crest.
# Bulky: 16 wide, four arms (upper pair at the sides, lower pair folded over the apron), crest.
dex = spec(
    "dexter", "Brandon", "npc_3", "frontier_brains/brandon.png",
    "DEXTER JETTSTER: four-armed Besalisk cook in an apron (replaces Brandon).",
    "From scratch, stays on NPC_3. Hide uses ramp A (grey-lavender) with 7 as its outline; the second pair of arms is folded over the apron.",
    frames={
        "down": [
            "....7CBBBC7.....", "...7755666577...", "..755666666657..", ".756EF6666FE657.",
            ".7566F6666F6657.", ".75666666666657.", "..756777777657..", "..775666666577..",
            "...77666666677..", ".7756EEEEEE6577.", "75667EEEEE676657", "75667E6EEEE76657",
            "75667EEEEEE76657", "7566755555576657", ".77667555576677.", "..77EEEE6EEE77..",
            "..7DCCCDDCCCD7..", "...DCCD..DCCD...", "...DDDD..DDDD...", "................"],
        "up": [
            ".....7CBBC7.....", "...7755666577...", "..755666666657..", ".75666666666657.",
            ".75666666666657.", ".75666666666657.", "..756666666657..", "..775666666577..",
            "...77666666677..", ".775666EE666577.", "7566766666676657", "7566766EE6676657",
            "7566766666676657", "7566766666676657", ".77666666666677.", "..777777777777..",
            "..7DCCCDDCCCD7..", "...DCCD..DCCD...", "...DDDD..DDDD...", "................"],
        "left": [
            "......7CBC7.....", "....775566677...", "...75566666657..", "..7F5666666657..",
            "..7F6666666657..", "..766666666657..", "..77766666657...", "...7766666667...",
            "....77666667....", "...75EEE66657...", "..756EEEE66657..", "..756EEEE66657..",
            "..756EEEE66657..", "..755555666657..", "...7755566657...", "...77EEEE6677...",
            "...7DCCCCCCD7...", "....DCCDDCCD....", "....DDDD.DDDD...", "................"],
    },
    steps={
        "down_a": ("down", 26, ["7567555557666657", ".77675555766677.", "..77EEEE6EEE77..", "..7DCCCDDCCCD7..", "...DCCD..DDDD...", "...DDDD........."]),
        "down_b": ("down", 26, ["7566675555576657", ".77666755557677.", "..77EEEE6EEE77..", "..7DCCCDDCCCD7..", "...DDDD..DCCD...", ".........DDDD..."]),
        "up_a": ("up", 29, ["..7DCCCDDCCCD7..", "...DCCD..DDDD...", "...DDDD........."]),
        "up_b": ("up", 29, ["..7DCCCDDCCCD7..", "...DDDD..DCCD...", ".........DDDD..."]),
        "left_a": ("left", 29, ["...7DCCCCCCD7...", "...DCCD...DCCD..", "...DDDD........."]),
        "left_b": ("left", 29, ["...7DCCCCCCD7...", ".....DCCDCCD....", "........DDDD...."]),
    },
    accept={"skin_tones": "Besalisk hide uses ramp A (5/6/7), not the human skin ramp", "eye_row": "eyes sit high on a crested, hairless head",
            "hair_rows": "no hair: a short crest, then skull", "step_change": "the lower arms are folded and the apron hangs straight; the bob, the forearms, the apron hem and the feet move",
            "orphans": "smooth hide and a plain apron; specks only on the apron and crest"},
)
print("ok")
