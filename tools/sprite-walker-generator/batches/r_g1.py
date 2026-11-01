"""Group 1 of the B-style rollout (worker 1): 14 NPC sheets redrawn as STAR WARS: KYBER walkers.
Each sprite keeps the vanilla body it replaces as material regions (base + remap) and patches in
only the new head and costume cues; the learned shader picks the tones.
Writes art/<name>.yaml. Run from the tool folder: python batches/r_g1.py
"""
import sys

sys.path.insert(0, "batches")
from helpers import block, spec  # noqa: E402

# ====================================================================== MAN_2 -> spaceport worker
# Ground-crew jumpsuit (J, orange-brown ramp c) with a grey zip (Z), a grey cap (Q crown, V brim)
# and ear-defender headset cups (E), a green utility belt (G).
M2_D = block(0, 11, """
....QQQQQQQQ....
...QQQQQQQQQQ...
..QQQQQWWQQQQQ..
..QQQQQWWQQQQQ..
.VVVVVVVVVVVVVV.
.EH__________HE.
.EEH________HEE.
.EE__________EE.""")
M2_U = block(0, 11, """
....QQQQQQQQ....
...QQQQQQQQQQ...
..QQQQQQQQQQQQ..
..QQQQQQQQQQQQ..
..QQQQQQQQQQQQ..
.E____________E.
.EE__________EE.
.EE__________EE.""")
M2_L = block(0, 11, """
......QQQQQQQ...
....QQQQQQQQQQ..
...QQQQQQQQQQQ..
..QQQQQQQQQQQQ..
VVVVVVVQQQQQQQ..
________________
_________EE_____
_________EE_____
_________EE_____""")
M2_BELT = block(0, 26, "___GGGGGGGGGG___")
spec("man_2", "Man2", "npc_3", "man_2.png",
     "Spaceport ground-crew worker in an orange jumpsuit and headset cap (replaces Man 2).",
     "Group 1, B style: Man 2's own body as regions (shirt and trousers -> jumpsuit J, tie -> grey zip Z), new grey cap with ear-defender cups, green utility belt. Stays on NPC_3.",
     materials={"Q": "a", "V": "a", "E": "a", "H": "c", "J": "c", "Z": "a", "G": "b"}, legend={"k": 15, "W": 14},
     accept={},
     base="man_2.png", remap={"c": "H", "b": "J", "w": "J", "a": "Z"},
     patches={"down": [M2_D, M2_BELT], "up": [M2_U, M2_BELT], "left": [M2_L]})

# ====================================================================== MAGMA M -> stormtrooper
# White armour (A, white edged in grey) hand-shaded with hard greys (l, m, d), black bodyglove
# (U near-black navy, u its sheen), helmet with slanted black lenses, a grey frown vent and
# blue-grey ear discs (e).
ST_D = block(0, 11, """
.....AAAAAA.....
....AAAAAAAA....
...AAAAAAAAAA...
..AAAAAAAAAAAA..
..AlllAAAAlllA..
.AAkkkAAAAkkkAA.
.eAlkkAAAAkklAe.
.eAAAAAmmAAAAAe.
..lAAmkmmkmAAl..
...lAAkddkAAl...
....UUUUUUUU....""")
ST_U = block(0, 11, """
.....AAAAAA.....
....AAAAAAAA....
...AAAAAAAAAA...
..AAAAAAAAAAAA..
..AAAAAAAAAAAA..
.AAAAAAAAAAAAAA.
.eeeeeeeeeeeeee.
.lAAAAAAAAAAAAl.
..lAmAAmAAmAAl..
...llAAAAAAll...
....UUUUUUUU....""")
ST_L = block(0, 11, """
......AAAAA.....
....AAAAAAAAA...
...AAAAAAAAAAA..
..AAAAAAAAAAAA..
.AAAAAAAAAAAAA..
.AkkAAAAAAAAAA..
.kkkAAAmeemAAA..
.AlAAAAmeemAAA..
.mkmlAAAmmAAAl..
..mklAAAAAAAl...
...lllAAAAll....""")
ST_TORSO_L = block(5, 22, """
UAAAAAAU
AAAAAAAA
UAAlAAAA
UUAAUUUU
AmAAAAmA
_UUUUUU_""")
ST_TORSO_D = block(3, 21, """
UUAAAAAAUU
_AAAAAAAA_
_AmAAAAmA_
_lAAAAAAl_
_UuUUUUuU_
_AAmAAmAA_""")
ST_TORSO_U = block(3, 21, """
UUAAAAAAUU
_AAAAAAAA_
_AAAAAAAA_
_lAAAAAAl_
_UuUUUUuU_
_AmAAAAmA_""")
spec("magma_member_m", "MagmaMemberM", "npc_4", "team_magma/magma_member_m.png",
     "STORMTROOPER (m): white armour and helmet over a black bodyglove (replaces the Magma grunt).",
     "Group 1, B style: the Magma grunt's body as regions (uniform -> white armour A, black -> bodyglove U), new stormtrooper helmet with slanted black lenses, a grey frown vent and blue-grey ear discs; chest plate, black abdomen and a white belt with grey boxes.",
     materials={"A": "w/c"}, legend={"k": 15, "W": 14, "l": 11, "m": 12, "d": 13, "U": 7, "u": 6, "e": 5},
     accept={"skin_tones": "no skin: full armour and helmet", "hair_rows": "no hair: helmet", "eye_row": "black helmet lenses, not eye bars",
             "ramp_tones_min": "armour is white with hand-placed greys; the bodyglove is flat near-black"},
     base="team_magma/magma_member_m.png", remap={"b": "A", "s": "A", "k": "U", "c": "A"},
     patches={"down": [ST_D, ST_TORSO_D], "up": [ST_U, ST_TORSO_U], "left": [ST_L, ST_TORSO_L]})

# ====================================================================== WOMAN_1 -> desert townswoman
# Sand headscarf (C, olive ramp c) with a dusty-rose hem (A) over the brow, a cowl (W) wrapped
# round the neck with a tail over one shoulder; blue dress kept (B); apron -> rose sash (A).
W1_D = block(0, 11, """
......CCCC......
....CCCCCCCC....
...CCCCCCCCCC...
..CCCCCCCCCCCC..
..CCCCCCCCCCCC..
.CCCCAAAAAACCCC.
.CCC________CCC.
.CCC__k__k__CCC.
.CCC__k__k__CCC.
..CCC______CCC..
..CCC______CCC..
..CC________CC..""")
W1_U = block(0, 11, """
......CCCC......
....CCCCCCCC....
...CCCCCCCCCC...
..CCCCCCCCCCCC..
..CCCCCCCCCCCC..
.CCCCCCCCCCCCCC.
.CCCCCCCCCCCCCC.
.CCCCCCCCCCCCCC.
.CCCCCCCCCCCCCC.
..CCCCCCCCCCCC..
..CCCCCCCCCCCC..
__BBBCCCCCCBBB__
_____CCCCCC_____
______CCCC______""")
W1_L = block(0, 11, """
......CCCCC.....
....CCCCCCCCC...
...CCCCCCCCCCC..
..CCCCCCCCCCCC..
..CCCCCCCCCCCC..
.CAAAAACCCCCCCC.
..______CCCCCCC.
..___k__CCCCCC..
..___k__CCCCCC..
...______CCCCC..
....____CCCCC...
______CCCCC_____
_______CCC______""")
spec("woman_1", "Woman1", "npc_1", "woman_1.png",
     "Desert townswoman in a sand headscarf (replaces Woman 1).",
     "Group 1, B style: Woman 1's own body as regions (dress B, apron -> dusty-rose sash A), new sand-coloured headscarf with a rose hem framing the face, a cowl wrapped round the neck and a tail over the shoulder.",
     materials={"C": "c", "R": "c", "B": "b", "A": "a"}, legend={"k": 15, "W": 14},
     accept={},
     base="woman_1.png", remap={"c": "C", "b": "B", "a": "A"},
     patches={"down": [W1_D], "up": [W1_U], "left": [W1_L]})


# ====================================================================== DEVON_EMPLOYEE -> Organa engineer
# Same vanilla body as Man 2, as regions: grey jumpsuit (J, ramp c), navy-black hair (H, ramp a),
# work goggles pushed up on the forehead (G strap on the maroon ramp b, white lenses), a maroon
# tool belt with a white buckle and a white House Organa chest flash.
DE_D = block(0, 14, """
___GLWGGGGLWG___""")
DE_U = block(0, 14, """
__GGGGGGGGGGGG__""")
DE_L = block(0, 14, """
___GLWGGGGGGG___""")
DE_BELT_D = [block(0, 26, "___GGGGWWGGGG___"), block(4, 23, "W")]
DE_BELT_U = [block(0, 26, "___GGGGGGGGGG___")]
spec("devon_employee", "DevonEmployee", "npc_4", "devon_employee.png",
     "HOUSE ORGANA engineer in a grey jumpsuit with work goggles (replaces the Devon employee).",
     "Group 1, B style: the Devon employee's own body as regions (shirt and trousers -> grey jumpsuit J, tie -> zip Z), navy-black hair, work goggles pushed up on the forehead, maroon tool belt, white chest flash.",
     materials={"H": "a", "J": "c", "Z": "a", "G": "b"}, legend={"k": 15, "W": 14, "L": 5},
     accept={},
     base="devon_employee.png", remap={"c": "H", "b": "J", "w": "J", "a": "Z"},
     patches={"down": [DE_D] + DE_BELT_D, "up": [DE_U] + DE_BELT_U, "left": [DE_L]})

# ====================================================================== FAT_MAN -> portly merchant
# Heavy brown coat (K, ramp c) with a white fur collar (F), open over a red tunic (B) with gold
# buttons; a round red merchant's cap (Q) with a gold band (Y), gold sash.
FM_D = [block(0, 11, """
.....QQQQQQ.....
...QQQQQQQQQQ...
..yyyyyyyyyyyy.."""), block(0, 20, """
.FFFFssssssFFFF.
_K____BBBB____K_
KK____BoBB____KK
KK____BBBB____KK
_K____BoBB____K_
__zzzzzoozzzzz__""")]
FM_U = [block(0, 11, """
.....QQQQQQ.....
...QQQQQQQQQQ...
..QQQQQQQQQQQQ..
.yyyyyyyyyyyyyy.
.HHHHHHHHHHHHHH.
..HHHHHHHHHHHH..
.sHHHHHHHHHHHHs.
.sHHHHHHHHHHHHs.
..HHHHHHHHHHHH.."""), block(0, 20, """
.FFFFFFFFFFFFFF.
_K____________K_
KK____________KK
KK____________KK
_K____________K_
__zzzzzzzzzzzz__""")]
FM_L = [block(0, 11, """
.......QQQQQ....
.....QQQQQQQQQ..
....yyyyyyyyyyy."""), block(0, 20, """
...FFFFFFFFFF...""")]
spec("fat_man", "FatMan", "npc_2", "fat_man.png",
     "Portly spaceport merchant in a heavy fur-collared coat and a round cap (replaces the Fat Man).",
     "Group 1, B style: the Fat Man's own body as regions (shirt -> heavy brown coat K, trousers T), white fur collar, the coat open over a red tunic with gold buttons, gold sash, round red merchant's cap with a gold band.",
     materials={"K": "c", "B": "b", "T": "c", "H": "c", "F": "w/c", "Q": "b"}, legend={"k": 15, "W": 14, "y": 6, "z": 7, "o": 5},
     accept={"hair_rows": "a low round cap over the brow, as vanilla's short hair (vanilla shares it)", "eye_row": "vanilla's own face rows, eyes at row 16 (vanilla shares it)"},
     base="fat_man.png", remap={"b": "K", "a": "T", "c": "H"},
     patches={"down": FM_D, "up": FM_U, "left": FM_L})

# ====================================================================== GAMEBOY_KID -> hologame kid
# Olive-brown hair (H), pink shirt (T), navy shorts (P), a navy hologame handheld (D) held in
# both hands with a glowing blue screen (hard light blue L and white W).
GK_D = block(0, 21, """
..ssTTTTTTTTss..
.ssTDDDDDDDDTss.
.sssDLLLLLLDsss.
..ssDLWLLWLDss..
..TTDDDDDDDDTT..""")
GK_U = block(0, 21, """
..ssTTTTTTTTss..
.ssTTTTTTTTTTss.
.sssTTTTTTTTsss.
..ssTTTTTTTTss..
..TTTTTTTTTTTT..""")
spec("gameboy_kid", "GameboyKid", "npc_1", "gameboy_kid.png",
     "Kid playing a handheld hologame (replaces the Game Boy kid).",
     "Group 1, B style: the Game Boy kid's own body as regions (hair H, shirt T, shorts P), the handheld redrawn as a navy hologame with a glowing blue screen held in both hands.",
     materials={"H": "c", "D": "b", "T": "a", "P": "b"}, legend={"k": 15, "W": 14, "L": 8},
     accept={},
     base="gameboy_kid.png", remap={"b": "H", "a": "T", "w": "T", "c": "P"},
     patches={"down": [GK_D], "up": [GK_U], "left": [GK_D]}, kit="person16x32_still")

# ====================================================================== LIZA -> Ezra Bridger
# Spiky dark hair (H, maroon-brown ramp c), orange jacket (J, ramp a) open over a white shirt
# (S), red belt (R), dark trousers (P).
def _r(*parts):
    row = "".join(parts)
    assert len(row) == 16, (len(row), row)
    return row


# Hair is hand-shaded with hard tones so it reads near-black: k outline, h body (13), g streaks (12).
EZ_HAIR_D = [
    "....h...h...h...",
    "...hgh.hgh.hgh..",
    _r("..h", "ghhhghhhghh", "h."),
    _r(".h", "hghhhghhhghhh", "h"),
    _r(".h", "h" * 13, "h"),
    _r(".h", "h" * 13, "h"),
    _r(".h", "hhh", "11", "hhh", "11", "hhh", "h"),
]
EZ_FACE_D = [  # hand-toned like STYLE.md 7: 1 light, 2 base, 3 shade, 4 outline
    _r("..h", "2111111112", "h.."),
    _r(".", "42", "111", "k", "11", "k", "111", "24", "."),
    _r("..", "43", "22", "k", "11", "k", "22", "34", ".."),
    _r("...", "43", "222222", "34", "..."),
    _r("....", "43", "3333", "34", "...."),
]
EZ_BODY_D = [
    "...JJSSSSSSJJ...",
    "..JJJJSSSSJJJJ..",
    "..JJJJJSSJJJJJ..",
    "..JJJJJSSJJJJJ..",
    "..sJJJJSSJJJJs..",
    "...PRRRRRRRRP...",
    "....PPPPPPPP....",
    "....kPPkkPPk....",
    ".....kk..kk.....",
]
EZ_D = block(0, 10, "\n".join(EZ_HAIR_D + EZ_FACE_D + EZ_BODY_D))
EZ_U = block(0, 10, "\n".join(EZ_HAIR_D[:6] + [
    _r(".h", "h" * 13, "h"),
    _r("..h", "h" * 10, "h.."),
    _r(".sk", "h" * 10, "ks."),
    _r("..h", "h" * 10, "h.."),
    _r("...k", "h" * 8, "k..."),
    _r("....", "JJJJJJJJ", "...."),
    "...JJJJJJJJJJ...",
    "..JJJJJJJJJJJJ..",
    "..JJJJJJJJJJJJ..",
    "..JJJJJJJJJJJJ..",
    "..sJJJJJJJJJJs..",
    "...PRRRRRRRRP...",
    "....PPPPPPPP....",
    "....kPPkkPPk....",
    ".....kk..kk.....",
]))
EZ_L = block(0, 10, "\n".join([
    "......h...h.....",
    ".....hgh.hgh.h..",
    _r("....h", "ghhhghhhg", "h."),
    _r("...h", "hghhhghhhgh", "h"),
    _r("..h", "h" * 12, "h"),
    _r("..h", "h" * 12, "h"),
    _r("..h", "1", "h" * 11, "h"),
    _r("..", "1111", "2", "h" * 7, "h."),
    _r("..", "21", "k", "12", "h" * 6, "h.."),
    _r("..", "32", "k", "2223", "h" * 3, "h..."),
    _r("...", "432223", "hhh", "h..."),
    _r("....", "4333334", "....."),
    ".....SJJJJJ.....",
    "....JJJJJJJ.....",
    "....JJJJJJJ.....",
    "....JsssJJJ.....",
    "....JsssJJJ.....",
    ".....RRRRRR.....",
    ".....PPPPPP.....",
    ".....kPPPPk.....",
    "......kkkk......",
]))
spec("liza", "Liza", "npc_2", "gym_leaders/liza.png",
     "EZRA BRIDGER: teenage Padawan with spiky dark hair in an orange jacket (replaces Liza).",
     "Group 1, B style: Liza's own outline as the frame, a new spiky dark head and an orange jacket open over a white shirt, red belt, dark trousers.",
     materials={"J": "a", "S": "w/c", "R": "b", "P": "c"}, legend={"k": 15, "W": 14, "h": 13, "g": 12, "1": 1, "2": 2, "3": 3, "4": 4},
     accept={},
     base="gym_leaders/liza.png", remap={"b": "J", "a": "R"},
     patches={"down": [EZ_D], "up": [EZ_U], "left": [EZ_L]}, kit="person16x32_still")

# ====================================================================== HEX_MANIAC -> Nightsister
# Crimson hooded robe (R hood, O robe, both on the red ramp b), gold hood trim and sash (Y,
# ramp a), dark maroon inner hood (I, ramp c) framing a face with black chin tattoo stripes.
NS_D = block(0, 10, """
......RRRR......
.....RRRRRR.....
....RRRRRRRR....
...RRRRRRRRRR...
..RRRRRRRRRRRR..
..RRYYYYYYYYRR..
.RRRJJJJJJJJRRR.
.RRIssssssssIRR.
.RRIssksskssIRR.
.RRIssksskssIRR.
.RRRRssssssRRRR.
.RRRRRRYYRRRRRR.""")
NS_U = block(0, 10, """
......RRRR......
.....RRRRRR.....
....RRRRRRRR....
...RRRRRRRRRR...
..RRRRRRRRRRRR..
..RRRRRRRRRRRR..
.RRRRRRRRRRRRRR.
.RRRRRRRRRRRRRR.
.RRRRRRRRRRRRRR.
.RRRRRRRRRRRRRR.
.RRRRRRRRRRRRRR.
.RRRRRRRRRRRRRR.
RRRRRRRRRRRRRRRR""")
NS_L = block(0, 10, """
.......RRRR.....
......RRRRRR....
.....RRRRRRRR...
....RRRRRRRRRR..
...RRRRRRRRRRR..
..YYRRRRRRRRRRR.
.IIIIRRRRRRRRRR.
.sssssRRRRRRRRR.
.skssssRRRRRRRR.
.skssssRRRRRRRR.
..sssssRRRRRRRR.
...YYYRRRRRRRRR.""")
spec("hex_maniac", "HexManiac", "npc_2", "hex_maniac.png",
     "NIGHTSISTER in crimson hooded robes with a gold trim (replaces the Hex Maniac).",
     "Group 1, B style: the Hex Maniac's own body as regions (robe O on the red ramp, sash Y gold), new peaked crimson hood with a gold trim and dark inner lining framing a face with black chin tattoos.",
     materials={"R": "b", "O": "b", "Y": "a"}, legend={"k": 15, "W": 14, "I": 13, "J": 12, "r": 10},
     accept={},
     base="hex_maniac.png", remap={"k": "O", "c": "O", "b": "O", "a": "Y"},
     patches={"down": [NS_D], "up": [NS_U], "left": [NS_L]})

# ====================================================================== ARTIST -> holo-artist
# White smock (M, white edged grey) splashed with paint (hard magenta, steel blue, peach), navy
# hair (H) under a smaller magenta beret (B), a navy holo-tablet (T) with a glowing face at the
# hip and a white stylus in the other hand.
AR_D = [block(0, 10, """
....BBBBBBBB....
...BBBBBBBBBBB..
..BBBBBBBBBBBBB.
..BBBBBBBBBBBB..
..HHHHHHHHHHHH..
.HHHHHHHHHHHHHH.
.HHHHssHHssHHHH.
.sHssssssssssHs.
.sHssssssssssHs.
.HsssskssksssH..
..HssssssssssH..
..HssssssssssH..
...HHssssssHH..."""), block(0, 23, """
____pp__________
__q______oo_____
__qq______o_____
_____________pp_
____vv________p_""")]
AR_U = [block(0, 10, """
....BBBBBBBB....
..BBBBBBBBBBB...
.BBBBBBBBBBBBB..
..BBBBBBBBBBBB..
..HHHHHHHHHHHH..
.HHHHHHHHHHHHHH.
.HHHHHHHHHHHHHH.
.sHHHHHHHHHHHHs.
.sHHHHHHHHHHHHs.
.HHHHHHHHHHHHHH.
..HHHHHHHHHHHH..
..MHHHHHHHHHHM..""")]
AR_L = [block(0, 10, """
....BBBBBBBB....
..BBBBBBBBBBBB..
.BBBBBBBBBBBBB..
..BBBBBBBBBBBB..
..HHHHHHHHHHHH..
..HHHHHHHHHHHHH.
..ssHHHHHHHHHH..
..ssssssHHHHHH..
..ssssssHHHHHH..
..sskssHHHHHHH..
...sssssHHHHH...
....sssssHHH...."""), block(0, 23, """
____TTT_________
___TLLWT________
____TTT____p____
_______v________""")]
spec("artist", "Artist", "npc_4", "artist.png",
     "Holo-artist in a paint-splashed smock with a beret and a holo-tablet (replaces the Artist).",
     "Group 1, B style: the Artist's own body as regions (smock -> white M edged in grey, folds F), navy hair under a magenta beret, paint splashes in magenta, steel blue and peach, a glowing holo-tablet in the side view.",
     materials={"B": "b", "H": "a", "M": "w/c", "F": "c", "T": "a"}, legend={"k": 15, "W": 14, "p": 9, "q": 8, "v": 5, "o": 2, "L": 11},
     accept={},
     base="artist.png", remap={"b": "B", "c": "M", "w": "F", "a": "T"},
     patches={"down": AR_D, "up": AR_U, "left": AR_L})

# ====================================================================== MAUVILLE_OLD_MAN_1 -> storyteller
# Sand hood (C, olive ramp c) over a long white beard (W2 = Y, white edged in olive), bushy white
# brows, khaki robe (R), a blue sash and the blue holo-scroll he tells from (base a -> B).
OM_D = block(0, 10, """
......CCCC......
....CCCffCCC....
...CCCCffCCCC...
..CCCCCCCCCCCC..
..CCCssssssCCC..
.CCCssssssssCCC.
.CCCYYYssYYYCCC.
.CCCssksskssCCC.
.CCCssksskssCCC.
.CCCYYssssYYCCC.
..CCYYYYYYYYCC..
..CCYYYYYYYYCC..
..CCCYYYYYYCCC..
...CCCYYYYCCC...
______YY________""")
OM_U = block(0, 10, """
......CCCC......
....CCCffCCC....
...CCCCffCCCC...
..CCCCCffCCCCC..
..CCCCCffCCCCC..
.CCCCCCffCCCCCC.
.CCCCCCffCCCCCC.
.CCCCCCCCCCCCCC.
.CCCCCCCCCCCCCC.
.CCCCCCCCCCCCCC.
..CCCCCCCCCCCC..
..CCCCCCCCCCCC..
..CCCCCCCCCCCC..""")
OM_L = block(0, 10, """
......CCCCC.....
....CCCCCCCCC...
...CCCCCCCCCCC..
..CCCCCCCCCCCC..
..CsssCCCCCCCC..
.CssssCCCCCCCCC.
.YYYsssCCCCCCCC.
..skssCCCCCCCCC.
..skssCCCCCCCCC.
.YYsssCCCCCCCCC.
.YYYYYsCCCCCCC..
.YYYYYCCCCCCC...
..YYYYCCCCCC....
...YYYCCCCC.....
....YY__________""")
spec("mauville_old_man_1", "Bard", "npc_1", "mauville_old_man_1.png",
     "Old Mos Espa storyteller in a sand hood with a long white beard (replaces the Mauville old man / Bard).",
     "Group 1, B style: the old man's own body as regions (shirt and trousers -> khaki robe R, hands and belt -> blue sash and holo-scroll B), new sand hood framing bushy white brows and a long white beard to the chest.",
     materials={"C": "c", "R": "c", "Y": "w/c", "B": "b", "A": "a"}, legend={"k": 15, "W": 14, "f": 13},
     accept={"step_change": "the long beard and robe hang still; the bob, hem and feet move"},
     base="mauville_old_man_1.png", remap={"b": "R", "c": "R", "a": "B", "w": "R"},
     patches={"down": [OM_D, block(0, 25, "___BBBBBBBBBB___\n___BBBBBBBBBB___"), block(1, 26, "AAA\nAAA\nAAA")],
              "up": [OM_U, block(0, 25, "___BBBBBBBBBB___\n___BBBBBBBBBB___"), block(12, 26, "AAA\nAAA\nAAA")],
              "left": [OM_L, block(9, 25, "AAA\nAAA\nAAA")]})

# ====================================================================== PICNICKER -> homesteader
# Brown hair (H, ramp c) in a bun (N), grey work dress (D, ramp a) with white sleeves, a woven
# brown basket (K) on the arm with green produce (V, ramp b).
PK_D = [block(0, 9, """
................
......NNNN......
.....NNNNNN.....
....HNNNNNNH....
...HHHHHHHHHH...
..HHHHHHHHHHHH..
.HHHHHHHHHHHHHH.
.HHHHssHHssHHHH.
.HHHssssssssHHH.
.HHsssksskssHHH.
..HssksskssssH..
...ssssssssss..."""), block(11, 23, """
_KKK_
K___K
VVVVV
KKKKK
_KKK_""")]
PK_U = [block(0, 9, """
................
......NNNN......
.....NNNNNN.....
....HNNNNNNH....
...HHHHHHHHHH...
..HHHHHHHHHHHH..
.HHHHHHHHHHHHHH.
.HHHHHHHHHHHHHH.
.HHHHHHHHHHHHHH.
.HHHHHHHHHHHHHH.
..HHHHHHHHHHHH..
...HHHHHHHHHH..."""), block(0, 23, """
_KKK____________
K___K___________
VVVVV___________
KKKKK___________
_KKK____________""")]
PK_L = [block(0, 9, """
................
.......NNNN.....
......NNNNNN....
....HHNNNNNN....
...HHHHHHHHHH...
..HHHHHHHHHHHH..
..HHHHHHHHHHHH..
..HHsHHHHHHHHH..
..sssssHHHHHHH..
..sskssHHHHHH...
..sskssHHHHHH...
...sssssHHHH...."""), block(3, 23, """
_KKK_
K___K
VVVVV
KKKKK
_KKK_""")]
spec("picnicker", "Picnicker", "npc_3", "picnicker.png",
     "Moisture-farm homesteader with her hair in a bun, carrying a basket of produce (replaces the Picnicker).",
     "Group 1, B style: the Picnicker's own body as regions (dress -> grey work dress D, trims -> white), new brown hair in a homesteader's bun, a woven basket of green produce on the arm.",
     materials={"H": "c", "N": "c", "D": "a", "P": "a", "K": "c", "V": "b"}, legend={"k": 15, "W": 14},
     accept={},
     base="picnicker.png", remap={"b": "D", "c": "H", "a": "P"},
     patches={"down": PK_D, "up": PK_U, "left": PK_L})

# ====================================================================== REPORTER_M -> HoloNet reporter
# Slick navy-black hair (H, ramp a) with a side part, no glasses; the vanilla body as regions
# with a grey suit (S, ramp c), white shirt and magenta tie kept; a small round grey holocam
# droid (D) with a magenta lens (L) hovering at his shoulder.
RP_HEAD_D = block(0, 11, """
......HHHH......
....HHHHHHHH....
...HHHHHHHHHH...
..HHHHHHHHHHHH..
..HHHHHHHHHsHH..
..HHsssssssHHH..
.sHssssssssssHs.
.sHssskssksssHs.
..sssskssksss...
...ssssssssss...""")
RP_HEAD_U = block(0, 11, """
......HHHH......
....HHHHHHHH....
...HHHHHHHHHH...
..HHHHHHHHHHHH..
..HHHHHHHHHHHH..
..HHHHHHHHHHHH..
.sHHHHHHHHHHHHs.
.sHHHHHHHHHHHHs.
..HHHHHHHHHHHH..
...HHHHHHHHHH...""")
RP_HEAD_L = block(0, 11, """
......HHHH......
....HHHHHHHH....
...HHHHHHHHHH...
..HHHHHHHHHHHH..
..sHHHHHHHHHHH..
..sssssHHHHHHH..
..ssssssHHHHHH..
..sskssssHHHHH..
..sskssssHHHH...
..ssssssssHH....""")
RP_DROID_D = block(12, 17, """
.DD.
DLWD
DDDD
.DD.""")
RP_DROID_U = block(0, 17, """
.DD.
DDDD
DDDD
.DD.""")
RP_DROID_L = block(12, 16, """
.DD.
DDDD
DDLD
.DD.""")
spec("reporter_m", "ReporterM", "npc_4", "reporter_m.png",
     "HOLONET reporter with a microphone and a hovering holocam droid (replaces the male reporter).",
     "Group 1, B style: the reporter's own body as regions (grey suit S, white shirt, magenta tie and his microphone kept), new slick navy-black hair with a side part, a small round grey holocam droid with a magenta lens hovering at his shoulder.",
     materials={"H": "a", "S": "c", "D": "c@"}, legend={"k": 15, "W": 14, "L": 9},
     accept={},
     base="reporter_m.png", remap={"c": "S"},
     patches={"down": [RP_HEAD_D, RP_DROID_D], "up": [RP_HEAD_U, RP_DROID_U], "left": [RP_HEAD_L, RP_DROID_L]})

# ====================================================================== SCHOOL_KID_M -> academy cadet
# Khaki cadet tunic (T, olive ramp c) and peaked cadet cap (Q crown, V band), dark blue hair (H),
# navy trousers (P), a maroon satchel (A) on a strap across the chest.
SK_D = [block(0, 11, """
....QQQQQQQQ....
...QQQQQQQQQQ...
...QQQQWWQQQQ...
..VVVVVVVVVVVV..
..HHHssssssHHH..
..HssssssssssH..
.sHssssssssssHs.
.sHssskssksssHs.
..sssskssksss...
...ssssssssss..."""), block(0, 22, """
___TTTTTTTTA____
__TTTTTTTTATTT__
___TTTTTTATT____
____TTTTATTT____
_AAAA___________
_AAAA___________""")]
SK_U = [block(0, 11, """
....QQQQQQQQ....
...QQQQQQQQQQ...
...QQQQQQQQQQ...
..VVVVVVVVVVVV..
..HHHHHHHHHHHH..
..HHHHHHHHHHHH..
.HHHHHHHHHHHHHH.
.HHHHHHHHHHHHHH.
..HHHHHHHHHHHH..
...HHHHHHHHHH..."""), block(0, 22, """
____ATTTTTTT____
___TTATTTTTTT___
____TTATTTTT____
_____TTATTTT____
___________AAAA_
___________AAAA_""")]
SK_L = [block(0, 11, """
.....QQQQQQQ....
....QQQQQQQQQ...
...QQQQQQQQQQ...
.VVVVVVVVVVVV...
..HsssHHHHHHH...
..sssssHHHHHH...
..ssssssHHHHH...
..sskssHHHHH....
..sskssssHHH....
...sssssssss...."""), block(0, 22, """
____TTTTTTT_____
____AAAAA_______
____AAAAA_______""")]
spec("school_kid_m", "SchoolKidM", "npc_1", "school_kid_m.png",
     "Academy cadet in a khaki tunic and peaked cap with a satchel (replaces the schoolboy).",
     "Group 1, B style: the schoolboy's own body as regions (shirt -> khaki cadet tunic T, shorts -> navy trousers P), new peaked cadet cap with a white badge over dark blue hair (glasses dropped), a maroon satchel on a strap across the chest.",
     materials={"Q": "c", "V": "c", "H": "b", "T": "c", "P": "b", "A": "a"}, legend={"k": 15, "W": 14},
     accept={},
     base="school_kid_m.png", remap={"b": "T", "w": "T", "c": "P"},
     patches={"down": SK_D, "up": SK_U, "left": SK_L})

# ====================================================================== SWIMMER_M -> diver
# The swim cap becomes a navy dive hood (B) pulled down over the ears, the goggles stay as a
# dive mask, an A99-style brass breather (C, olive ramp c) at the mouth, and a navy dive suit
# (D) over the shoulders in the surf.
SW_D = block(0, 21, """
.B____________B.
.B____________B.
________________
__wD__CCCC__Dw__
.wDDDDDDDDDDDDw.
.DDDD______DDDD.
.DDDD______DDDD.
__DD________DD__""")
SW_U = block(0, 21, """
.B____________B.
.B____________B.
________________
__wDDDDDDDDDDw__
.wDDDDDDDDDDDDw.
.DDDD______DDDD.
.DDDD______DDDD.
__DD________DD__""")
SW_L = block(0, 20, """
________________
__BB____________
__BBB___________
___BB___________
_CC_____________""")
spec("swimmer_m", "SwimmerM", "npc_1", "swimmer_m.png",
     "Diver (m) in a dive hood and mask with an A99-style breather (replaces the male swimmer).",
     "Group 1, B style: the swimmer's own body, goggles and surf as regions, the cap pulled down into a navy dive hood, a dive suit over the shoulders and a brass breather at the mouth.",
     materials={"B": "b", "D": "b", "C": "c"}, legend={"k": 15, "W": 14, "L": 8},
     accept={"height": "swimming: only the head and shoulders show above the surf (vanilla shares it)"},
     base="swimmer_m.png", remap={"b": "B"},
     patches={"down": [SW_D], "up": [SW_U], "left": [SW_L]})

print("ok")
