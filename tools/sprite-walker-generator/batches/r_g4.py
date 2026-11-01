"""Group 4 of the B-style rollout (BRIEF.md): 14 vanilla rows redrawn as Star Wars walkers.
Each sprite uses the vanilla sheet it replaces as material regions (base + remap) and patches
only what is new. Writes art/<name>.yaml. Run from the tool folder: python batches/r_g4.py
"""
import sys

import yaml

sys.path.insert(0, "batches")
sys.path.insert(0, ".")
from helpers import P, block, spec  # noqa: E402
from walker_sprite.shade import regions_of  # noqa: E402
from walker_sprite.sheet import read_frames  # noqa: E402
from walker_sprite.spec import game_dir  # noqa: E402

ORDER = ["down", "up", "left", "down_a", "down_b", "up_a", "up_b", "left_a", "left_b"]


def base_regions(base, remap):
    frs, _ = read_frames(game_dir() / (P + base))
    out = {}
    for n, f in zip(ORDER, frs):
        out[n] = ["".join(remap.get(c, c) for c in r) for r in regions_of(f)]
    return out


def recolor_patch(rows, y0, y1, mapping, xs=(0, 16)):
    """A patch over rows y0..y1 that renames letters (after remap) and keeps everything else."""
    out = []
    for y in range(y0, y1 + 1):
        out.append("".join(mapping.get(c, "_") if xs[0] <= x < xs[1] else "_" for x, c in enumerate(rows[y])))
    return {"x": 0, "y": y0, "rows": "\n".join(out)}


def mk(name, base, remap, recol=(), extra=None, **kw):
    """spec() plus per-frame recolours of the base body. recol: list of (y0, y1, mapping[, xs])
    with stand-frame rows (step frames get +1). extra: frame -> patches appended last."""
    kit = kw.pop("kit", "person16x32")
    spec(name, base=base, remap=remap, kit=kit, **kw)
    path = f"art/{name}.yaml"
    d = yaml.safe_load(open(path))
    regs = base_regions(base, remap)
    for fn in (["down", "up", "left"] if kit.endswith("_still") else ORDER):
        step = 1 if "_" in fn else 0
        pre = []
        for rc in recol:
            y0, y1, m = rc[:3]
            xs = rc[3] if len(rc) > 3 else (0, 16)
            if isinstance(xs, dict):
                xs = xs.get(fn.split("_")[0], (0, 16))
            pre.append(recolor_patch(regs[fn], y0 + step, min(31, y1 + step), m, xs))
        fr = d["frames"].get(fn) or {"patches": []}
        fr["patches"] = pre + fr.get("patches", []) + list((extra or {}).get(fn, []))
        d["frames"][fn] = fr
    open(path, "w").write(yaml.safe_dump(d, sort_keys=False, width=200))


# ====================================================================== CAMPER -> farmhand
# Moisture-farm hand: a wide-brimmed tan hat (crown H, brim R) seen from above, green work shirt
# (camper's own shirt), grey-blue overalls (O: bib, straps and trousers over the bare legs),
# brown boots, a steel wrench tucked in the bib pocket.
C_HAT_D = block(0, 10, """
.....HHHHHH.....
....HHHHHHHH....
....HHHHHHHH....
...HHHHHHHHHH...
...hhhhhhhhhh...
.RRRRRRRRRRRRRR.
RRRRRRRRRRRRRRRR
.RRRRRRRRRRRRRR.""")
C_HAT_U = C_HAT_D
C_HAT_L = block(0, 10, """
.....HHHHHH.....
....HHHHHHHH....
....HHHHHHHH....
...HHHHHHHHHH...
...hhhhhhhhhh...
RRRRRRRRRRRRRR..
RRRRRRRRRRRRRRR.
.RRRRRRRRRRRRR..""")
C_BIB_D = block(4, 22, """
O______O
OOOOOOOO
_OOOOOO_
_OOLLOO_
_OOOOOO_""")
C_BIB_U = block(4, 22, """
_O____O_
__O__O__
___OO___
__OOOO__
_OOOOOO_""")
C_BIB_L = block(4, 22, """
_____O__
OO___O__
OO______
OO______
_OO__OO_
_OOOOO__""")
mk("camper", "camper.png", {"b": "G", "c": "B", "a": "G", "w": "G"},
   gi="Camper", pal="npc_3", replaces="camper.png",
   desc="Moisture-farm hand in overalls and a wide hat (replaces Camper).",
   note="Group 4, B style: Camper's own body as regions (shirt -> green work shirt G, shoes -> boots B), wide tan hat (crown H, band h, brim R), grey-blue overalls O with straps and a wrench in the bib, trousers over the bare legs. Stays on NPC_3.",
   materials={"H": "c@", "h": "c", "R": "c", "G": "b", "B": "c", "O": "a", "L": "c"},
   legend={"k": 15}, accept={"hair_rows": "a wide hat brim, no hair"},
   recol=[(27, 31, {"s": "O", "G": "O"})],
   patches={"down": [C_HAT_D, C_BIB_D], "up": [C_HAT_U, C_BIB_U], "left": [C_HAT_L, C_BIB_L]})

# ====================================================================== PHOEBE -> Qui-Gon (spirit)
# Force spirit of Qui-Gon Jinn: long olive-brown hair (H) to the shoulders, a full beard (D) as
# its own volume, Jedi robe (R) and sleeves (S) on NPC_1's blue ramp for the spectral glow, a white
# tunic (T) edged in blue, a pink-brown sash (L), hands folded at the sleeves. Stand-only, so the
# whole figure is drawn over Phoebe's sheet (her body is bare-shouldered and too small for a robe).
Q_D = block(0, 10, """
.....HHHHHH.....
...HHHHHHHHHH...
..HHHHHHHHHHHH..
..HHHHHHHHHHHH..
.FHHHHssssHHHHF.
.FFHssssssssHFF.
.FFssssssssssFF.
.FFssskssksssFF.
.FFssskssksssFF.
.FFssDDDDDDssFF.
.FFsDDDDDDDDsFF.
..FFDDDDDDDDFF..
.RRFFDDDDDDFFRR.
SSRRTTDDDDTTRRSS
SSSRRTTDDTTRRSSS
SWSRRTTTTTTRRSSS
.SSRLLLLLLLLRSS.
.ssRRTTTTTTRWss.
..RWRTTTTTTRRR..
..RRRRTTTTRRRR..
...RRRBBBBRRR...""")
Q_U = block(0, 10, """
.....HHHHHH.....
...HHHHHHHHHH...
..HHHHHHHHHHHH..
..HHHHHHHHHHHH..
.FHHHHHHHHHHHHF.
.FFHHHHHHHHHHFF.
.FFHHHHHHHHHHFF.
.FFHHHHHHHHHHFF.
.FFFHHHHHHHHFFF.
.FFFGGGGGGGGFFF.
.FFFGGGGGGGGFFF.
..FFGGGGGGGGFF..
.RRFFGGGGGGFFRR.
SSRRRFGGGGFRRRSS
SSSRRRRFFRRRRSSS
SWSRRRRRRRRRRSSS
.SSRLLLLLLLLRSS.
.ssRRRRRRRRRRWs.
..RRRRRRRRRRRR..
..RRRRRRRRRRRR..
...RRRBBBBRRR...""")
Q_L = block(0, 10, """
......HHHHH.....
....HHHHHHHHH...
...HHHHHHHHHHH..
..HHHHHHHHHHHH..
..sssHHHHHHHHH..
.sssssHHHHHHHF..
.ssssssHHHHHFFF.
.sskssssHHHFFFF.
.sskssssHHFFFFF.
.DDDssssHFFFFFF.
.DDDDDsFFFFFFF..
..DDDDFFFFFFF...
...DDRRFFFFRR...
...TRRRRFFRRRR..
...SSSRRRRRRRR..
..SSSSRRRRRRRR..
..ssSLLLLLLLLR..
...ssRRRRRRRRR..
...RRRRRRRRWRR..
...RRRRRRRRRRR..
....RRBBBBRRR...""")
mk("phoebe", "elite_four/phoebe.png", {},
   gi="Phoebe", pal="npc_1", replaces="elite_four/phoebe.png",
   desc="QUI-GON JINN (Force spirit): long hair, beard, spectral blue Jedi robes (replaces Phoebe).",
   note="Group 4, B style: stand-only, drawn over Phoebe's sheet: long olive-brown hair H and a full beard D, blue Jedi robe R with sleeves S (the spectral tint), white tunic T, sash L, hands folded. Stays on NPC_1.",
   materials={"H": "c@", "F": "c", "G": "c", "D": "c", "R": "b", "S": "b", "T": "w/b", "B": "c"},
   legend={"k": 15, "L": 7, "W": 14}, accept={},
   patches={"down": [Q_D], "up": [Q_U], "left": [Q_L]}, kit="person16x32_still")

# ====================================================================== GRETA -> 4-LOM
# 4-LOM: an insect-faced protocol droid turned bounty hunter. A chrome dome (G, NPC_1's blue ramp
# lit like a face) with two big compound eyes (E, rose ramp) and white glints, a mandible grille
# (M) with a black mouth slit; Greta's body as regions turned into an olive long coat (C), chrome
# droid arms (A), a tan bandolier (L) and white coat trims kept as lapels (V).
L_HEAD_D = block(0, 11, """
......GGGG......
....GGGGGGGG....
...GGGGGGGGGG...
.EEEEGGGGGGEEEE.
EEWEEEGGGGEEEWEE
EEEEEEGGGGEEEEEE
.EEEEGGGGGGEEEE.
...GGGMMMMGGG...
....GMMkkMMG....
.....MMMMMM.....""")
L_HEAD_U = block(0, 11, """
......GGGG......
....GGGGGGGG....
...GGGGGGGGGG...
.EGGGGGGGGGGGGE.
EEGGGGGGGGGGGGEE
EEGGGGGGGGGGGGEE
.EGGGGGGGGGGGGE.
...GGGGGGGGGG...
....GGGGGGGG....
.....MMMMMM.....""")
L_HEAD_L = block(0, 11, """
.....GGGGG......
...GGGGGGGGG....
..GGGGGGGGGGG...
.EEEEGGGGGGGG...
EEEEEEGGGGGGG...
EEWEEEGGGGGGG...
.EEEEGGGGGGGG...
MMMGGGGGGGGG....
MkMMGGGGGGG.....
.MMMMGGGGG......""")
L_COAT_D = block(0, 21, """
...CCCCMMCCCC...
..DCCCCCCCCCCD..
.DDCLlCCCCCCCDD.
.DDCCLlCCCCCCDD.
.DDCCCLlVVCCCDD.
.AACCCCLVVCCCAA.
..CCCCCCVVCCCC..
..CCCCCCVVCCCC..""")
L_COAT_U = block(0, 21, """
...CCCCCCCCCC...
..DCCCCCCCCCCD..
.DDCCCCCCCLlCDD.
.DDCCCCCCLlCCDD.
.DDCCCCCLlCCCDD.
.AACCCCLlCCCCAA.
..CCCCCCCCCCCC..
..CCCCCCCCCCCC..""")
L_COAT_L = block(0, 21, """
....MMMCCCC.....
....CCCCCCCC....
....CDDDCCCC....
...CCDDDCCCC....
...CCDDDCCCC....
...CCAACCCCC....
...CCCCCCCCCC...
....CCCCCCCCC...""")
mk("greta", "frontier_brains/greta.png", {"s": "A", "b": "C", "a": "A", "w": "A"},
   gi="Greta", pal="npc_1", replaces="frontier_brains/greta.png",
   desc="4-LOM: insect-faced droid bounty hunter in a long coat (replaces Greta).",
   note="Group 4, B style: Greta's own body as regions (outfit -> olive long coat C with white lapels V, arms -> chrome droid arms A, details -> tan bandolier L), new insectoid droid head: chrome dome, two big rose compound eyes with glints, mandible grille.",
   materials={"G": "skin-b@", "E": "a@", "M": "b", "A": "b", "C": "c", "D": "c", "V": "b"},
   legend={"k": 15, "W": 14, "L": 2, "l": 4},
   accept={"skin_tones": "a droid: chrome is the blue ramp; the skin ramp is the tan bandolier", "hair_rows": "no hair: a chrome dome",
           "eye_row": "compound eyes, not eye bars", "head_w": "15 wide across the compound eyes"},
   patches={"down": [L_HEAD_D, L_COAT_D], "up": [L_HEAD_U, L_COAT_U], "left": [L_HEAD_L, L_COAT_L]})

# ====================================================================== GIRL_2 -> spaceport girl
# Spaceport girl: two long plaits (R and Q alternate down each braid so it reads as woven) with
# green ties (t), a centre-parted fringe; a short green flight jacket (J: Girl2's bare arms
# and shoulders recoloured) over a white top (T), her skirt in lavender-grey (K), boots (B).
G_HEAD_D = block(0, 12, """
......HHHH......
....HHHHHHHH....
...HHHHHHHHHH...
..HHHHHHHHHHHH..
..HHHHHHHHHHHH..
..HHHHssssHHHH..
.RHHssssssssHHR.
.QHssskssksssHQ.
.RQssskssksssQR.
.QRssssssssssRQ.
..Q_ssssssss_Q..
.RQ__________QR.
.QR__________RQ.
.tt__________tt.""")
G_HEAD_U = block(0, 12, """
......HHHH......
....HHHHHHHH....
...HHHHHHHHHH...
..HHHHHHHHHHHH..
..HHHHHHHHHHHH..
..HHHHHHHHHHHH..
.RHHHHHHHHHHHHR.
.QRHHHHHHHHHHRQ.
.RQHHHHHHHHHHQR.
.QRHHHHHHHHHHRQ.
..QRHHHHHHHHRQ..
..RQ________QR..
..QR________RQ..
..tt________tt..""")
G_HEAD_L = block(0, 12, """
.....HHHHHH.....
....HHHHHHHH....
...HHHHHHHHHH...
..HHHHHHHHHHHH..
..HHHHHHHHHHHH..
..sssHHHHHHHHH..
..sssssHHHHHHH..
..ssksssHHHHHH..
..ssksssHHHRQH..
...sssssssHQR...
....ssssssQR....
.....______RQ...
.....______QR...
.....______tt...""")
mk("girl_2", "girl_2.png", {"a": "K", "b": "B", "c": "H"},
   gi="Girl2", pal="npc_3", replaces="girl_2.png",
   desc="Spaceport girl with long plaits and a flight jacket (replaces Girl 2).",
   note="Group 4, B style: Girl2's own body as regions (bare arms and shoulders -> green flight jacket J over a white top T, skirt -> lavender skirt K), new hair: centre-parted fringe and two long plaits with green ties, one plait down the back in the side view. Stays on NPC_3.",
   materials={"H": "c@", "R": "c", "t": "b", "J": "b", "T": "w/a", "K": "a", "B": "c"},
   legend={"k": 15, "Q": 11}, accept={},
   recol=[(23, 25, {"s": "J", "B": "T"}, {"down": (0, 16), "up": (0, 16), "left": (0, 16)})],
   patches={"down": [G_HEAD_D], "up": [G_HEAD_U], "left": [G_HEAD_L]})

# ====================================================================== TATE -> Kanan Jarrus
# Kanan Jarrus: swept-back brown hair (H) tied in a ponytail (Q), a short beard (D), a round green
# pauldron (P) on his left shoulder, grey tunic (T) with sleeves (A), brown belt (L), grey
# trousers (K), black boots. Stand-only; drawn over Tate's sheet, his single-boy body is too
# short for a grown Jedi.
K_D = block(0, 11, """
......HHHH......
....HHhHHhHH....
...HHhHHHHhHH...
..HHHHHHHHHHHH..
..HHHHHHHHHHHH..
..HHHssssssHHH..
..HssssssssssH..
.sHssskssksssHs.
.sHssskssksssHs.
..HDssssssssDH..
...DDDssssDDD...
....DDDDDDDD...P
..TTTTTDDTTPWPPP
.ATTTTTTTTPPPPPP
.ATTTTTTTTTPPPPA
.ATTLLLuLLLLTTA.
.ssKKKKKKKKKKss.
...KKKKKKKKKK...
...KKKK..KKKK...
...kkkk..kkkk...""")
K_U = block(0, 11, """
......HHHH......
....HHhHHhHH....
...HHhHHHHhHH...
..HHhHHHHHHhHH..
..HHHHHHHHHHHH..
..HHHHHHHHHHHH..
..HHHHHHHHHHHH..
.sHHHHHyyHHHHHs.
.sHHHHHQQHHHHHs.
..HHHHHQQHHHHH..
...HHHHQQHHHH...
....sssQQsss....
PPWPPTTQTTTTT...
PPPPPPTTTTTTTTA.
APPPPTTTTTTTTTA.
.ATTLLLuLLLLTTA.
.ssKKKKKKKKKKss.
...KKKKKKKKKK...
...KKKK..KKKK...
...kkkk..kkkk...""")
K_L = block(0, 11, """
.....HHHHH......
...HHhHHHHHH....
..HHHHhhHHHHH...
..HHHHHHHHHHHH..
..sHHHHHHHHHHH..
..ssssHHHHHHyy..
.sssssHHHHHHQQ..
.ssksssssHHHQQ..
.ssksssssHHH.Q..
.DDsssssDHHH.Q..
.DDDssDDDHH.....
..DDDDDDD.......
...PPWPTTTTT....
..PPPPPPTTTT....
..PPPPPPTTTT....
...AAAATTTTT....
...ssLuLLLLL....
....KKKKKKK.....
....KKK.KKK.....
....kkk.kkk.....""")
mk("tate", "gym_leaders/tate.png", {},
   gi="Tate", pal="npc_3", replaces="gym_leaders/tate.png",
   desc="KANAN JARRUS: bearded Jedi with a ponytail and a green pauldron (replaces Tate).",
   note="Group 4, B style: stand-only, drawn over Tate's sheet: swept-back brown hair with a ponytail, short beard, round green armour pauldron on the left shoulder, grey tunic, brown belt, grey trousers, black boots; moves to OBJ_EVENT_PAL_TAG_NPC_3 (install sets paletteTag/paletteSlot).",
   materials={"H": "c", "D": "c", "P": "b@", "T": "a", "A": "a", "L": "c", "K": "a"},
   legend={"k": 15, "Q": 13, "y": 9, "h": 11, "W": 14, "u": 6}, accept={},
   patches={"down": [K_D], "up": [K_U], "left": [K_L]}, kit="person16x32_still")

# ====================================================================== LASS -> Naboo dress
# Young Naboo woman: hair (H) swept up into a tall updo with a silver headband (C) set with white
# pearls (W); Lass's body as regions turned into a magenta gown
# (G) that falls to the floor over her legs, long sleeves (S), a silver (N) and white (V) trimmed
# bodice.
N_HEAD_D = block(0, 10, """
.....HHHHHH.....
....HHHHHHHH....
...CCWCCCCWCC...
..HHHHHHHHHHHH..
.HHHHHHHHHHHHHH.
.HHHHHssssHHHHH.
.HHHssssssssHHH.
..HssssssssssH..
..HssskssksssH..
..HssskssksssH..
..HssssssssssH..
...ssssssssss...
...__________...
...__________...
...__________...""")
N_HEAD_U = block(0, 10, """
.....HHHHHH.....
....HHHHHHHH....
...CCCCCCCCCC...
..HHHHHHHHHHHH..
.HHHHHHHHHHHHHH.
.HHHHHHHHHHHHHH.
.HHHHHHHHHHHHHH.
..HHHHHHHHHHHH..
..HHHHHHHHHHHH..
..sHHHHHHHHHHs..
...HHHHHHHHHH...
....ssssssss....
..____________..
..____________..
..____________..""")
N_HEAD_L = block(0, 10, """
.....HHHHHH.....
....HHHHHHHH....
...CWCCCCCCC....
..HHHHHHHHHHHH..
..HHHHHHHHHHHHH.
..sssHHHHHHHHHH.
..sssssHHHHHHHH.
..ssssssHHHHHH..
..ssksssHHHHHH..
..ssksssssHHH...
..sssssssssH....
...ssssssss.....
....________....
....________....
....________....""")
mk("lass", "lass.png", {"a": "G", "c": "N", "w": "V"},
   gi="Lass", pal="npc_4", replaces="lass.png",
   desc="Young woman in a Naboo gown with an updo and headband (replaces Lass).",
   note="Group 4, B style: Lass's own body as regions (skirt -> floor-length magenta gown G over the legs, bare arms -> long sleeves S, top -> silver N and white V bodice), new head: navy updo with a pearl-set silver headband. Stays on NPC_4.",
   materials={"H": "a", "C": "c", "G": "b!", "S": "b", "N": "c", "V": "w/c"},
   legend={"k": 15, "W": 14}, accept={},
   recol=[(23, 25, {"s": "S"}), (27, 31, {"s": "G", "N": "G", "V": "G"}),
          (22, 25, {"V": "N"}, {"down": (0, 0), "left": (0, 0), "up": (0, 16)})],
   patches={"down": [N_HEAD_D], "up": [N_HEAD_U], "left": [N_HEAD_L]})

# ====================================================================== MAN_5 -> farmer
# Moisture farmer: short brown hair (H) with work goggles pushed up on the forehead (yellow lenses
# g, red strap r), a red neck bandana (R), Man5's own body as regions: shirt -> white farm tunic
# (T), suspenders -> yellow straps (Y), trousers -> brown (K), shoes -> boots (O); a
# hydrospanner (black shaft, yellow jaw and grip) hanging from the belt.
F_HEAD_D = block(0, 11, """
.....HHHHHH.....
...HHHHHHHHHH...
..HHHHHHHHHHHH..
..HrggrrrrggrH..
..HssssssssssH..
.sHssssssssssHs.
.sHssskssksssHs.
..HssskssksssH..
...ssssssssss...
....ssssssss....
_____RRRRRR_____""")
F_HEAD_U = block(0, 11, """
.....HHHHHH.....
...HHHHHHHHHH...
..HHHHHHHHHHHH..
..HrrrrrrrrrrH..
..HHHHHHHHHHHH..
.sHHHHHHHHHHHHs.
.sHHHHHHHHHHHHs.
..HHHHHHHHHHHH..
...HHHHHHHHHH...
....ssssssss....
_____RRRRRR_____""")
F_HEAD_L = block(0, 11, """
.....HHHHHH.....
....HHHHHHHHH...
...HHHHHHHHHHH..
..grrrrHHHHHHH..
..sssssHHHHHHH..
..sssssssHHHHH..
..sssssssHHHHH..
..ssksssssHHHH..
..ssksssssHHH...
...sssssssHH....
....RRRRRR......""")
F_TOOL_D = block(10, 26, """
gk
_k
_g""")
mk("man_5", "man_5.png", {"c": "T", "b": "K", "a": "Y"},
   gi="Man5", pal="npc_2", replaces="man_5.png",
   desc="Moisture farmer with work goggles and a hydrospanner on his belt (replaces Man 5).",
   note="Group 4, B style: Man5's own body as regions (shirt -> white farm tunic T edged in brown, suspenders -> yellow straps Y, trousers -> brown K, shoes -> boots O), new head: short brown hair with work goggles pushed up (yellow lenses, red strap), red neck bandana, a hydrospanner hanging from the belt. Stays on NPC_2.",
   materials={"H": "c@", "T": "w/c", "Y": "c", "K": "c", "O": "c", "R": "b", "r": "b"},
   legend={"k": 15, "g": 5}, accept={},
   recol=[(28, 31, {"Y": "O"})],
   patches={"down": [F_HEAD_D, F_TOOL_D], "up": [F_HEAD_U], "left": [F_HEAD_L]})

# ====================================================================== DELIVERYMAN -> courier
# Courier droid handler: the deliveryman's own cap and uniform as regions (cap U, uniform J), a
# rose courier insignia (I) on the cap, a black comlink headset with a mic (k), and a white
# parcel crate (X) with an olive tape band (Y) and a rose shipping label (W) held in both hands.
D_HEAD_D = block(0, 14, """
______IW________
_______W________
________________
________________
_k______________
_kk_____________
__kkk___________""")
D_BOX_D = block(0, 23, """
...XXXXXXXXXX...
..sXXXXYYXXXXs..
..sXWWXYYXXXXs..
...XXXXYYXXXX...""")
D_HEAD_L = block(0, 14, """
_______________.
________________
________________
________________
________k_______
_______kk_______
____kkk_________""")
D_BOX_L = block(0, 22, """
.XXXXXX_________
.XXYYXXs________
.XXYYXXs________
.XWWXXX_________""")
mk("mystery_event_deliveryman", "mystery_event_deliveryman.png", {"b": "J", "c": "B"},
   gi="MysteryEventDeliveryman", pal="npc_1", replaces="mystery_event_deliveryman.png",
   desc="Courier droid handler with a comlink headset and a parcel crate (replaces the Mystery Event deliveryman).",
   note="Group 4, B style: stand-only, the deliveryman's own cap and blue uniform as regions with a rose courier insignia on the cap, a black comlink headset with a mic, and a white parcel crate with an olive tape band and a rose shipping label held in both hands. Stays on NPC_1.",
   materials={"J": "b", "B": "c", "X": "w/c", "Y": "c"},
   legend={"k": 15, "W": 6, "I": 5}, accept={},
   recol=[(14, 15, {"s": "I"}), (11, 17, {"k": "J"}), (21, 28, {"k": "J"}), (19, 19, {"B": "k"}, {"down": (5, 11), "up": (0, 0), "left": (0, 0)})],
   patches={"down": [D_HEAD_D, D_BOX_D], "up": [], "left": [D_HEAD_L, D_BOX_L]}, kit="person16x32_still")

# ====================================================================== PROF_BIRCH -> Prof. Korr
# Field researcher: Birch's own messy hair as regions gone grey (H), his lab coat as a dusty tan
# field duster (C, rust-brown ramp), green field shirt (G), grey shorts and boots (K), and
# a black datapad with a glowing green screen (8/9) and a white key held at his chest.
R_PAD_D = block(6, 24, """
kkkk
k89k
kkkW""")
R_PAD_L = block(3, 24, """
kkkk
k89k
kkkk""")
mk("prof_birch", "prof_birch.png", {"c": "K", "a": "C", "w": "C", "b": "G"},
   gi="ProfBirch", pal="npc_3", replaces="prof_birch.png",
   desc="PROF. KORR: grey-haired field researcher in a dusty brown duster with a datapad (replaces Prof. Birch).",
   note="Group 4, B style: Prof. Birch's own body as regions (messy hair turned grey H, lab coat -> dusty rust-brown field duster C, shirt -> green G, shorts and boots grey K), a black datapad with a glowing green screen held at the chest. Stays on NPC_3.",
   materials={"H": "a@", "C": "c", "G": "b", "K": "a"},
   legend={"k": 15, "W": 14, "8": 8, "9": 9}, accept={},
   recol=[(10, 20, {"K": "H"})],
   patches={"down": [R_PAD_D], "up": [], "left": [R_PAD_L]})

# ====================================================================== RUNNING_TRIATHLETE_F -> swoop racer
# Swoop racer (f) out on a training run: her own hair and running body as regions, amber racing
# goggles (g, white glints) pushed up on the forehead with a dark red strap, a red racing suit (J:
# her bare arms, midriff, shorts and legs) with a yellow chest panel and stripes (Y: her top),
# and brown racing boots.
S_GOG_D = block(2, 15, """
qqgWqqqqgWqq""")
S_GOG_U = block(2, 15, """
qqqqqqqqqqqq""")
S_GOG_L = block(2, 15, """
gWgqqqqqqqqq""")
S_EYE_D = block(6, 18, """
k__k
k__k""")
S_EYE_L = block(5, 18, "k\nk")
mk("running_triathlete_f", "running_triathlete_f.png", {"b": "Y", "a": "J"},
   gi="RunningTriathleteF", pal="npc_2", replaces="running_triathlete_f.png",
   desc="Swoop racer (f) on a training run: racing goggles and a red-and-yellow racing suit (replaces the running Triathlete F).",
   note="Group 4, B style: the running Triathlete F's own body and walk as regions (bare arms, midriff, shorts and legs -> red racing suit J, top -> yellow chest panel Y, shoes -> brown boots), her hair kept, amber racing goggles with glints pushed up on the forehead. Stays on NPC_2.",
   materials={"J": "b", "Y": "a"},
   legend={"k": 15, "g": 6, "W": 14, "q": 10}, accept={},
   recol=[(21, 31, {"s": "J"}), (28, 31, {"Y": "c"})],
   patches={"down": [S_GOG_D, S_EYE_D], "up": [S_GOG_U], "left": [S_GOG_L, S_EYE_L]})

# ====================================================================== SCOTT -> Lando Calrissian
# Lando: short dark hair (H), a thin moustache (M) over a white smile (W), Scott's own blue shirt
# (T) with a white collar (V), dark trousers and boots (K), and the Bespin cape (P, blue) with its
# olive-gold lining (Y) slung over his left shoulder; in the side view it covers his near side.
O_HEAD_D = block(0, 11, """
......HHHH......
....HHhhhhHH....
...HhhhhhhhhH...
..HHhHHHhHHHhH..
..HHHHhHHHHhHH..
..HHssssssssHH..
.sHssssssssssHs.
.sHssskssksssHs.
..ssssksskssss..
...ssMMMMMMss...
....sssWWsss....""")
O_HEAD_U = block(0, 11, """
......HHHH......
....HHhhhhHH....
...HhhhhhhhhH...
..HHhHHHhHHHhH..
..HHHHhHHHHhHH..
..HhHHHHhHHHHH..
.sHHHHHHHHHhHHs.
.sHHHHHHHHHHHHs.
..sHHHHHHHHHHs..
...ssssssssss...
....ssssssss....""")
O_HEAD_L = block(0, 11, """
.....HHHHHH.....
....HHhhhhHH....
...HhhhhhhhhH...
..HHHhHHHhHHHH..
..HHHHHhHHHhHH..
..sssHHHHHHHHH..
..sssssHHHHHHH..
..ssksssssHHHH..
..ssksssssHHH...
..MMMssssssH....
...Wssssss......""")
O_CAPE_D = block(11, 22, """
PPPP.
PPfPP
YPfPf
YPfPf
YPPfP
YfPfP
.YfPP""")
O_CAPE_U = block(0, 22, """
.PPPP
PPfPP
fPfPP
fPfPf
PfPfP
PfPPf
PPfY.""")
O_CAPE_L = block(3, 22, """
_PPPPPPP
YPPfPPfP
YPPfPPfP
YPfPPfPP
YPfPPfPP
_YfPPPfP
__YPPfP_""")
mk("scott", "scott.png", {"b": "T", "a": "T", "w": "V", "c": "K"},
   gi="Scott", pal="npc_1", replaces="scott.png",
   desc="LANDO CALRISSIAN: moustache, a smile, blue shirt and the Bespin cape (replaces Scott).",
   note="Group 4, B style: Scott's own body as regions (shirt -> blue shirt T with a white collar V, legs and shoes -> dark trousers and boots K), new head with short dark hair, a thin moustache and a white smile (his sunglasses removed), and the blue Bespin cape with an olive-gold lining over his left shoulder. Stays on NPC_1.",
   materials={"T": "b", "V": "w/b", "K": "c", "P": "b!", "Y": "c"},
   legend={"k": 15, "W": 14, "M": 13, "H": 13, "h": 12, "f": 10},
   accept={"step_change": "the cape hangs over the near arm and hides its swing; the bob, the free arm and the legs move"},
   recol=[(28, 31, {"s": "K"})],
   patches={"down": [O_HEAD_D, O_CAPE_D], "up": [O_HEAD_U, O_CAPE_U], "left": [O_HEAD_L, O_CAPE_L]})

# ====================================================================== AQUA_MEMBER_M -> Gamorrean thug
# Cartel thug, Gamorrean-style: a huge round green head (G, NPC_3's green ramp lit like a face)
# with a pink pig snout (N, skin ramp) and nostrils, small wide-set eyes, white tusks (W), a
# grey iron cap (A) with two white horns (h); the grunt's own body as regions: green arms (Z),
# brown leather jerkin (L) with grey studs (T), a grey armoured kilt (K), black gauntlets.
B_HEAD_D = block(0, 10, """
.....AAAAAA.....
.hh.AAAAAAAA.hh.
..hAAAAAAAAAAh..
..GGGGGGGGGGGG..
.GGGGkGGGGkG8GG.
.GG8GkGGGGkGGGG.
.GGGGGGGGGGGGGG.
.GGGGGGGGGGGGGG.
GGGGGNNNNNNGGGGG
GGGGNNkNNkNNG8GG
.GGGNNNNNNNNGGG.
.GGWGGGGGGGGWGG.
...GGGGGGGGGG...""")
B_HEAD_U = block(0, 10, """
.....AAAAAA.....
.hh.AAAAAAAA.hh.
..hAAAAAAAAAAh..
..GGGGGGGGGGGG..
.GGGGGGGG8GGGGG.
.GG8GGGGGGGGGGG.
.GGGGGGGGGGGGGG.
.GGGGGGGGGGG8GG.
GGGGGGGGGGGGGGGG
GGGGG8GGGGGGGGGG
.GGGGGGGGGGGGGG.
..GGGGGGGGGGGG..
...GGGGGGGGGG...""")
B_HEAD_L = block(0, 10, """
......AAAAA.....
....AAAAAAAAhh..
...AAAAAAAAAAh..
..GGGGGGGGGGGG..
.GGkGGGGGG8GGGG.
.GGkGGGGGGGGGGG.
.GGGGGGGGGGGGGG.
.GGGGGGGGGGG8GG.
NNNGGGGGGGGGGGG.
NkNNGGGGGGGGGG..
NNNNGGGGG8GGGG..
.WGGGGGGGGGGG...
..GGGGGGGGGG....""")
mk("aqua_member_m", "team_aqua/aqua_member_m.png", {"s": "Z", "c": "L", "w": "T", "a": "K"},
   gi="AquaMemberM", pal="npc_3", replaces="team_aqua/aqua_member_m.png",
   desc="Cartel thug (m): Gamorrean-style brute in leathers (replaces the Aqua grunt m).",
   note="Group 4, B style: the Aqua grunt's own body as regions (arms -> green hide Z, shirt -> brown leather jerkin L with grey studs T, trousers -> grey armoured kilt K, black gauntlets kept), new Gamorrean head: huge round green head, pink pig snout, small eyes, white tusks, iron cap with horns; moves to OBJ_EVENT_PAL_TAG_NPC_3 (install sets paletteTag/paletteSlot).",
   materials={"G": "b@", "N": "s", "A": "a", "Z": "b", "L": "c", "T": "a", "K": "a"},
   legend={"k": 15, "W": 14, "h": 14, "8": 8},
   accept={"hair_rows": "no hair: an iron cap over a bald green head", "head_w": "16 wide: a Gamorrean head is huge",
           "eye_row": "small eyes set high under the iron cap, above the snout",
           "step_change": "the huge head is one smooth volume, so the 1 px bob changes few of its pixels; the body, arms and legs step as vanilla"},
   patches={"down": [B_HEAD_D, block(5, 24, "W____W")], "up": [B_HEAD_U, block(5, 25, "W____W")], "left": [B_HEAD_L, block(7, 26, "W")]})

# ====================================================================== UNUSED_WOMAN -> desert villager
# Tatooine villager woman: an ochre desert head wrap (crown S, folds f, drape D) framing the face, a wisp of brown hair (H)
# at the brow; her own body as regions: the low ponytail and shawl edges become the wrap's tail
# (D), the dress and black underskirt a brown homespun robe (R) to the ankles, the white trims a red sash (Y).
U_HEAD_D = block(0, 10, """
.....SSSSSS.....
...SSSSSSSSSS...
..SSSSSSSSSSSS..
..SSSSSSSSSSSS..
.DffSSSSSSSSffD.
.DDDHHssssHHDDD.
.DDHssssssssHDD.
.DDssssssssssDD.
.DDssskssksssDD.
.DDssskssksssDD.
.DDDssssssssDDD.
..DDDssssssDDD..
.DDDDDDDDDDDDDD.""")
U_HEAD_U = block(0, 10, """
.....SSSSSS.....
...SSSSSSSSSS...
..SSSSSSSSSSSS..
..SSSSSSSSSSSS..
.DffSSSSSSSSffD.
.DDDfSSSSSSfDDD.
.DDDDfSSSSfDDDD.
.DDDDDfSSfDDDDD.
.DDDDDDDDDDDDDD.
.DDDDDDDDDDDDDD.
.DDDDDDDDDDDDDD.
..DDDDDDDDDDDD..
.DDDDDDDDDDDDDD.""")
U_HEAD_L = block(0, 10, """
.....SSSSSS.....
...SSSSSSSSSS...
..SSSSSSSSSSSS..
..SSSSSSSSSSSS..
.SSSSSSSSSSffDD.
.SHHssSSSSfDDDD.
.SsssssSSfDDDDD.
.SssssssSDDDDDD.
.SsskssssDDDDDD.
.SsskssssDDDDDD.
..sssssssDDDDD..
...ssssssDDDD...
....DDDDDDDDD...""")
mk("unused_woman", "unused_woman.png", {"c": "D", "a": "R", "w": "Y"},
   gi="", pal="npc_2", replaces="unused_woman.png",
   desc="Tatooine villager woman in a desert head wrap and homespun robe (replaces the unused woman sheet).",
   note="Group 4, B style: the unused woman's own body as regions (ponytail and shawl -> the wrap's tail S, dress -> brown homespun robe R to the ankles, white trims -> red sash Y), new head: an ochre desert wrap framing the face with a wisp of brown hair; the sheet has no graphics_info, drawn for OBJ_EVENT_PAL_TAG_NPC_2.",
   materials={"S": "a@", "D": "a", "H": "c", "R": "c", "Y": "b"},
   legend={"k": 15, "f": 7}, accept={"hair_rows": "a desert head wrap, not hair"},
   recol=[(27, 28, {"s": "R"}), (23, 29, {"k": "R"})],
   patches={"down": [U_HEAD_D], "up": [U_HEAD_U], "left": [U_HEAD_L]})

# ====================================================================== WOMAN_4 -> mother
# Moisture-farm mother: her big curls replaced by olive-brown hair pulled back into a bun (U) tied
# with a navy ribbon (r), a light parting streak; her own body as regions (cardigan -> blue shawl S, dress -> rose tunic
# T, shoes -> olive boots); an olive market sack (G) with a bottle of blue milk (white cap W,
# blue 8) hanging from her hand.
W_HEAD_D = block(0, 10, """
......UUUU......
......UUUU......
....HHrrrrHH....
...HHHHHHHHHH...
..HHHHHHHHHHHH..
.HHHHHHhhHHHHHH.
.HHHHHssssHHHHH.
.HHHssssssssHHH.
..HssssssssssH..
..HssskssksssH..
..HssskssksssH..
...ssssssssss...
....ssssssss....
..SSS______SSS..
.______________.""")
W_HEAD_U = block(0, 10, """
......UUUU......
......UUUU......
....HHrrrrHH....
...HHHHHHHHHH...
..HHHHHHHHHHHH..
.HHHHHHhhHHHHHH.
.HHHHHHHHHHHHHH.
.HHHHHHHHHHHHHH.
..HHHHHHHHHHHH..
..sHHHHHHHHHHs..
...HHHHHHHHHH...
....ssssssss....
....ssssssss....
..SSSSSSSSSSSS..
.______________.""")
W_HEAD_L = block(0, 10, """
........UUUU....
........UUUU....
....HHHHrrrr....
...HHHHHHHHHH...
..HHHHHHHHHHHH..
..HHHhhHHHHHHHH.
..sssHHHHHHHHHH.
..sssssHHHHHHHH.
..ssssssHHHHHH..
..ssksssHHHHH...
..ssksssssHH....
...sssssssss....
....ssssss......
.....______.....
....________....""")
W_BAG_D = block(11, 24, """
___W_
___M_
_GGGG
_GGGG
_GGGG""")
W_BAG_U = block(0, 24, """
_W___
_M___
GGGG_
GGGG_
GGGG_""")
W_BAG_L = block(4, 25, """
_W___
_M___
GGGG_
GGGG_""")
mk("woman_4", "woman_4.png", {"b": "S", "a": "T", "c": "O"},
   gi="Woman4", pal="npc_1", replaces="woman_4.png",
   desc="Moisture-farm mother with her hair in a bun and a market sack with blue milk (replaces Woman 4).",
   note="Group 4, B style: Woman 4's own body as regions (cardigan -> blue shawl S, dress -> rose tunic T, shoes -> olive boots), new head with brown hair pulled back into a bun, an olive market sack with a bottle of blue milk hanging from her hand. Stays on NPC_1.",
   materials={"H": "c@", "U": "c@", "S": "b", "T": "a", "O": "c", "G": "c!"},
   legend={"k": 15, "W": 14, "M": 8, "h": 11, "r": 10},
   accept={"step_change": "the market sack hangs still from her hand; the bob, the free arm and the legs move"},
   patches={"down": [W_HEAD_D, W_BAG_D], "up": [W_HEAD_U, W_BAG_U], "left": [W_HEAD_L, W_BAG_L]})

print("ok")
