# Post-game GRAND ARENA (Battle Frontier): Lando's arena world, reached by the STAR TIDAL starliner. The seven
# ARENA BOSSES are bounty hunters Lando hired: AURRA (Salon Maiden), DENGAR (Dome Ace), ZUCKUSS (Palace Maven),
# 4-LOM (Arena Tycoon), IG-88 (Factory Head), GARDULLA (Pike Queen), DEXTER (Pyramid King). Trainer Hill keeps
# its name. Facility names (BATTLE TOWER, DOME, ...) stay; the FRONTIER PASS is the ARENA PASS (glossary).
KEEP_REST_MAPS = ("map:battle-frontier", "map:trainer-hill")
REFLOW = True  # several rule lines overflow once COMPANION becomes COMPANIONS
KEEP_REST_FILES = ("data/text/battle_dome.inc", "data/text/frontier_brain.inc")
B = "BattleFrontier_"


def pl(*olds):
    return [(o, o.replace("COMPANION", "COMPANIONS")) for o in olds]


FIX = {
# --- starliner dock (was the ferry) ---
B+"OutsideWest_Text_MayISeeYourTicket": r"Hello, are you here for the starliner?\nMay I see your STARLINER PASS?$",
B+"OutsideWest_Text_MustHaveTicketToBoard": r"{PLAYER} doesn't have the STARLINER\nPASS…\pI'm terribly sorry.\pYou must have a PASS to board\nthe starliner.$",
B+"OutsideWest_Text_PleaseBoardFerry": r"Please board the starliner and wait\nfor departure.$",
B+"OutsideWest_Text_GotSeasickOnWayHere": [("I got seasick…", "I got space-sick…")],
B+"OutsideEast_Text_ConquerLeagueAndFrontier": [("the GRAND ARENA and the ILUM\lTEMPLE.", "the GRAND ARENA and the TRIALS\lof ILUM.")],
# --- terminals (was PC) ---
B+"BattleDomeLobby_Text_LastWinnerWasTough": [("the monitor beside the TERMINAL.", "the monitor beside the terminal.")],
B+"ExchangeServiceCorner_Text_WellSendItToPC": r"Thank you!\nWe'll send it to your home terminal.$",
B+"ExchangeServiceCorner_Text_PCIsFull": r"I'm so sorry…\nYour terminal storage appears to\lbe full…$",
B+"PokemonCenter_1F_Text_NextStopBattleArena": r"Okay! Next stop, the BATTLE ARENA!\nI'd better get the right COMPANIONS from\lthe storage terminal.$",
# --- link play (GBA cable) ---
B+"BattleTowerLobby_Text_ExplainLinkMultisChallenge": [],
B+"BattleTowerLobby_Text_ExplainMultiLinkRules": [("These COMPANION must", "These COMPANIONS must")],
# --- plurals ---
B+"BattleDomeLobby_Text_ExplainMatchupRules": pl("toughness of COMPANION\l"),
B+"BattleFactoryLobby_Text_ReturnMonsSaveResults": [("I will return your COMPANION in exchange\nfor our rental COMPANION.", "I will return your COMPANIONS in exchange\nfor our rental COMPANIONS.")],
B+"BattleFactoryLobby_Text_ReturnMons": r"I will return your COMPANIONS in exchange\nfor our rental COMPANIONS.$",
B+"BattlePalaceLobby_Text_NatureAndMovesKeyHere": pl("nature of COMPANION\n"),
B+"BattlePikeLobby_Text_ExplainMonOrderRules": pl("sequence of COMPANION cannot"),
B+"Lounge1_Text_PokemonBreederIntro": [("raised COMPANION!", "raised COMPANIONS!"), ("abilities of COMPANION\l", "abilities of COMPANIONS\l")],
B+"ReceptionGate_Text_OpenLevelInfo": [("levels of COMPANION entering", "levels of COMPANIONS entering"), ("levels of\lyour COMPANION.", "levels of\lyour COMPANIONS.")],
B+"ReceptionGate_Text_MonEntryInfo": [("same kind of COMPANIONS are not", "same kind of COMPANION are not")],
"BattleDome_Text_RaisesMonsWellBalanced": r"Raises COMPANIONS in a well-balanced way.$",
}
NOTES = {
B+"OutsideWest_Text_MayISeeYourTicket": "the arena's dock is a starliner pad (STAR TIDAL)",
B+"BattleTowerLobby_Text_ExplainLinkMultisChallenge": "GBA link cable -> COMLINK",
}
