# Kamino (Pacifidlog -> TIPOCA CITY, a stilt city on an ocean world; Routes 131-134 of storm-sea and currents;
# the Sealed Chamber -> SEALED VAULT) and the ASTEROID SPIRE (Sky Pillar), home of the EXOGORTH.
# The Sealed Chamber's Braille becomes Aurebesh in Step 5 art; its words say COMPANION now.
KEEP_REST_MAPS = ("map:pacifidlog-town", "map:route131", "map:route132", "map:route133", "map:route134",
                  "map:sky-pillar", "map:sealed-chamber")
P = "PacifidlogTown_"


def pl(*olds):
    return [(o, o.replace("COMPANION", "COMPANIONS")) for o in olds]


FIX = {
P+"Text_FastRunningCurrent": r"The sea around TIPOCA CITY has\na fast-running tide.\pIf you decide to SURF, you could end\nup swept away somewhere else.$",
P+"Text_NeatHousesOnWater": r"See, isn't it neat?\nThese houses stand on stilts over\lthe sea!\pI was born here!$",
P+"Text_SkyPillarTooScary": r"The ASTEROID SPIRE?\p…Oh, you must mean that tall, tall\nrock out among the asteroids.\pIf you asked me, I wouldn't climb it.\nIt's too scary to get up that high.\pLife at sea level in TIPOCA CITY,\nthat suits me fine.$",
P+"Text_TownSign": r"TIPOCA CITY\p“Where the rain never stops, and\nthe sea never sleeps.”$",
P+"House1_Text_RegiStory": r"In the OUTER RIM, there are three\nCOMPANIONS that represent the power of\lrock, ice, and steel.\pThey say they were built long ago\nto guard deep caves.\pThat's the story I heard when I was\njust a little kid.$",
P+"House2_Text_ChairmansYoungerBrotherOnVacation": pl("my vacation with\nCOMPANION,"),
P+"House2_Text_ViciousPokemonTakeThis": [("A frightening COMPANIONS like that", "A frightening COMPANION like that")],
P+"House4_Text_PeopleSawHighFlyingPokemon": r"People were saying they saw a COMPANION\nflying high above the OUTER RIM.\pIs it flying around all the time?\nDoesn't it need to rest somewhere?$",
P+"House4_Text_SkyPokemon": r"A star COMPANION!\nA star COMPANION!$",
P+"PokemonCenter_1F_Text_OnColonyOfCorsola": r"TIPOCA CITY stands on top of\na reef of CORALITH.\pIf I told you that, would you believe\nme?$",
P+"PokemonCenter_1F_Text_AncestorsLivedOnBoats": r"The ancestors of the people in\nTIPOCA CITY were said to have been\lborn on boats and then lived and died\laboard them.\pI understand that they lived that way\nbecause they were searching for\lsomething.$",
"Route131_Text_ReliPostBattle": r"RIA: The people of TIPOCA CITY live\nwith the sea and COMPANIONS from\lthe time they are born.$",
"Route131_Text_IanPostBattle": r"ISKO: You know how TIPOCA CITY is\na town on stilts?\pSo, wherever there is the sea,\nthat's a part of TIPOCA CITY!$",
"Route131_Text_TaliaPostBattle": r"There is an odd place nearby.\nThere's a huge spire out in the\lasteroids. Why don't you go look?$",
"Route132_Text_GilbertPostBattle": [("TRAINERS travel the fields and\nmountains,", "TRAINERS travel from world to\nworld,")],
"Route132_Text_KiyoIntro": r"I think about COMPANIONS all day long.\nHow could you possibly beat me?$",
"Route132_Text_KiyoPostBattle": r"Urggh…\nYou're a COMPANION fanatic, aren't you?\pYou must think about COMPANIONS all\nday long, don't you?$",
"Route133_Text_BeckPostBattle": [("I'd like to go back to BRIGHT TREE,", "I'd like to go back to ENDOR,")],
"Route134_Text_JackPostBattle": r"I think COMPANIONS enjoy the fast\ncurrents around these parts.$",
"Route134_Text_AaronPostBattle": [("We will return for more training at\nSTARFALL CAVERN.", "We will return for more training at\nSTARFALL CAVERN on SULLUST.")],
# --- Asteroid Spire ---
"SkyPillar_Outside_Text_GotToGoBackForSootopolis": [],
# --- Sealed Vault (Aurebesh in Step 5) ---
"SealedChamber_InnerRoom_Braille_WeOweAllToThePokemon": r"WE OWE ALL\nTO THE\nCOMPANION.$",
"SealedChamber_InnerRoom_Braille_ButWeSealedThePokemonAway": r"BUT, WE\nSEALED THE\nCOMPANION\nAWAY.$",
"SealedChamber_InnerRoom_Braille_OpenDoorEternalPokemonWaits": r"OPEN A DOOR.\nAN ETERNAL\nCOMPANION\nWAITS.$",
# --- overflow fixes (trainer lines) ---
"Route133_Text_WarrenIntro": r"I want to win like everyone else, but\nI won't raise COMPANIONS like everyone\lelse.$",
"Route134_Text_AlexPostBattle": r"My BIRD COMPANIONS get tired quickly\nafter a long flight…$",
}
NOTES = {
"SealedChamber_InnerRoom_Braille_WeOweAllToThePokemon": "Braille glyphs: Step 5 redraws as Aurebesh; keep line breaks",
P+"Text_TownSign": "Kamino: endless rain over an ocean world",
}

REFLOW = True
