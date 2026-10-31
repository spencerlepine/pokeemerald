# Ships and event islands left out of the area chunks: the REPUBLIC WRECK (Abandoned Ship, Kashyyyk), the
# STAR TIDAL starliner (S.S. Tidal; Han is its honorary captain), and the post-game event islands.
# Peeko (Briney's Wingull) is Chewbacca, a person: he roars, never "Pihyo".
KEEP_REST_MAPS = ("map:abandoned-ship", "map:ss-tidal", "map:faraway-island", "map:southern-island",
                  "map:birth-island", "map:navel-rock", "map:island-cave")
A = "AbandonedShip_"
T = "SSTidal"


def pl(*olds):
    return [(o, o.replace("COMPANION", "COMPANIONS")) for o in olds]


FIX = {
# --- Republic Wreck ---
A+"CaptainsOffice_Text_ThisIsSSCactus": r"This ship was the REPUBLIC cruiser\nTIDE RUNNER. It's from the Clone Wars.$",
A+"Corridors_1F_Text_CharlieIntro": [("aboard the ship?", "aboard the wreck?")],
A+"Corridors_B1F_Text_DuncanIntro": r"When we go out to sea, we SAILORS\nalways bring our COMPANIONS.\lHow about a quick battle?$",
A+"Corridors_B1F_Text_YayItsAShip": r"Yay!\nIt's a starship!$",
A+"Rooms2_1F_Text_KiraPostRematch": pl("our COMPANION some more"),
A+"Rooms_1F_Text_ThaliaIntro": [("What on earth would compel you", "What in the galaxy would compel you")],
A+"Rooms_1F_Text_ThaliaRematchIntro": [("What on earth would compel you", "What in the galaxy would compel you")],
A+"Rooms_B1F_Text_GettingQueasy": [],
A+"CaptainsOffice_Text_NoSuccessFindingScanner": [("He also asked me to find a DATA SCANNER,\nbut I haven't had any success…", "He asked me to find a DATA SCANNER,\nbut I haven't had any luck…")],
A+"Corridors_B1F_Text_DuncanPostBattle": [("If a COMPANION knew how to go underwater,\nwe might", "If a COMPANION could go underwater,\nwe might")],
A+"Rooms2_1F_Text_DanRematchIntro": [("Our COMPANIONS have grown stronger, too.", "Our COMPANIONS have grown stronger.")],
# --- STAR TIDAL ---
T+"_Text_FastCurrentsHopeYouEnjoyVoyage": r"This starliner is built to fly\nthrough the roughest hyperlanes.\pWe hope you enjoy your voyage with us.\nFeel free to explore the ship.$",
T+"_Text_HopeYouEnjoyVoyage": r"We hope you enjoy your voyage on\nour starliner.$",
T+"_Text_MadeLandInSlateport": r"We have landed at MOS EISLEY.\nThank you for flying with us.$",
T+"_Text_MadeLandInLilycove": r"We have landed at CLOUD CITY.\nThank you for flying with us.$",
T+"Corridor_Text_CanRestInCabin2": [("before we make land,", "before we land,")],
T+"Corridor_Text_VisitOtherCabins": [("bored of the boat trip", "bored of the flight")],
T+"Corridor_Text_HorizonSpreadsBeyondPorthole": r"Stars streak past beyond\nthe viewport.$",
T+"Corridor_Text_BrineyWelcomeAboard": r"HAN: Welcome aboard, {PLAYER}{KUN}!\pThey made me honorary captain of\nthe STAR TIDAL!\pYou can call me CAPTAIN HAN now!\pYou know, I swore I'd never fly a\nbig, slow liner like this…\pBut look at her! She stirred my\nsleeping soul as a pilot!$",
T+"Corridor_Text_Peeko": r"CHEWIE: Rrrwaaaghh!$",
T+"Corridor_Text_ScottBattleFrontierInvite": r"LANDO: Well, hi, hi!\n{PLAYER}{KUN}, {PLAYER}{KUN}!\pSomething's come up, so I have to\ndisembark, but am I glad to see you!\pCongratulations, ILUM CHAMPION!\pThere's a place I'd like to invite\nsomeone like you.\pIt's the…\nGRAND ARENA!\pWhat's the place like?\nYou'll understand when you see it!\pI've spoken with the ship's CAPTAIN\nabout this.\pThe next time you take the starliner,\nyou should be able to fly to\lthe GRAND ARENA.\pOkay, {PLAYER}{KUN}, I'll be waiting for you\nat the GRAND ARENA!$",
T+"LowerDeck_Text_LeonardIntro": [("It'll be alright for a COMPANION battle.", "It'll be all right for a battle.")],
T+"Rooms_Text_ColtonIntro": r"I often fly to CLOUD CITY.\pI enjoy attending SHOWCASES,\nyou see.$",
T+"Rooms_Text_ColtonPostBattle": r"I get so excited imagining what kinds\nof COMPANIONS I'll see in the next\lSHOWCASE. The anticipation thrills!$",
T+"Rooms_Text_GarretPostBattle": [("acquire\na yacht for me.\lA yacht for me and COMPANIONS!", "acquire\na yacht for me.\lA star yacht for me and COMPANIONS!")],
T+"Rooms_Text_NaomiPostBattle": r"A galaxy cruise on a luxury liner has\nits charms, I must say…\pBut, I will admit there is an appealing\nside to touring the OUTER RIM like this.$",
T+"Rooms_Text_MicahPostBattle": r"Friends need not be human.\nFor me, COMPANIONS are true friends!$",
T+"Rooms_Text_JedIntro": r"JOSS: I feel a little shy, but…\nWe'll show you our lovey-dovey power!$",
T+"Rooms_Text_JedPostBattle": r"JOSS: It's the first time our lovey-\ndovey power couldn't prevail!\lYou must be an awesome TRAINER!$",
# --- Event islands ---
"FarawayIsland_Entrance_Text_SailorReturn": r"CAPTAIN HAN can be so maddeningly\nfickle…\pDo you want to return to CLOUD CITY?$",
"FarawayIsland_Interior_Text_Mew": r"Myuu…$",
}
NOTES = {
T+"Corridor_Text_Peeko": "Chewbacca is a person, not a Wingull",
A+"CaptainsOffice_Text_ThisIsSSCactus": "S.S. CACTUS -> REPUBLIC cruiser TIDE RUNNER (Republic Wreck)",
}

REFLOW = True
