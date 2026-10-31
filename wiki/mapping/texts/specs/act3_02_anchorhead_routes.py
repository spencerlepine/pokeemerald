# Anchorhead (Verdanturf), Routes 111-117 (the Tatooine desert and the Sullust ash fields), the
# Sandcrawler (Mirage Tower), Krayt Graveyard (Desert Underpass), Tess's house, Winstrate family.
KEEP_REST_MAPS = ("map:verdanturf", "map:route111", "map:route112", "map:route113", "map:route114", "map:route115",
                  "map:route117", "map:desert", "map:mirage")
V = "VerdanturfTown_"
R1 = "Route111_"
FIX = {
R1+"Text_ToughToKeepWinningUpTheRanks": [("If you don't raise your COMPANION some\nmore,", "If you don't raise your COMPANIONS some\nmore,")],
R1+"Text_ShouldBeMirageTowerAroundHere": r"There should be a giant SANDCRAWLER\naround here somewhere.\pBut for some reason, you can see it\nsometimes, and sometimes not.\pThe JAWAS keep driving it around,\nI guess.$",
R1+"Text_MirageTowerClearlyVisible": r"I see it!\nThe SANDCRAWLER!\pThe one they said was a mirage\nis clearly visible!\pBut it looks so rusty…\nIt could fall apart anytime…\pI want to go inside it, but I can't\nget my courage up for it…$",
R1+"Text_ThatWasShockingSandRainedDown": r"Whoa…\nThat was shocking.\pThe SANDCRAWLER just fell apart all\nof a sudden.\pWhat was it like inside?\nWere there JAWAS and such?$",
R1+"Text_MirageTowerHasntBeenSeenSince": r"Since I spoke to you, the SANDCRAWLER\nhasn't been seen.\pPerhaps the JAWAS sold it for\nparts…$",
R1+"OldLadysRestStop_Text_RestUpHere": [("Aren't your COMPANION exhausted?", "Aren't your COMPANIONS exhausted?")],
R1+"OldLadysRestStop_Text_StillTiredTakeAnotherRest": [("Are your COMPANION still tired?", "Are your COMPANIONS still tired?")],
R1+"WinstrateFamilysHouse_Text_MySonIsStrongerThanYou": [("deploys COMPANION so masterfully.", "deploys COMPANIONS so masterfully.")],
R1+"WinstrateFamilysHouse_Text_LikeYouToHaveMachoBrace": [("strengthen our COMPANION\lin training.", "strengthen our COMPANIONS\lin training.")],
R1+"WinstrateFamilysHouse_Text_GrandsonStrong": [("He must be challenging the ILUM\nTEMPLE CHAMPION by now.\pKnowing my grandson, he could be the\nCHAMPION already!", "He must be taking the TRIALS OF\nILUM by now.\pKnowing my grandson, he could have\npassed them already!")],
R1+"WinstrateFamilysHouse_Text_GrandsonStrongShort": r"My grandson must be taking the\nTRIALS OF ILUM by now.\pKnowing my grandson, he could have\npassed them already!$",
"Route112_Text_LeaderGoingToAwakenThing": r"Hey, is LORD VADER really going\nto awaken that thing?$",
"Route112_Text_YeahWeNeedMeteorite": [("Sounds like it, yeah.", "Those are our orders.")],
"Route113_Text_FunWalkingThroughAsh": [("on the ground and grass.", "on the ground and scrub.")],
"Route114_Text_AllMyMonDoesIsRoarTakeThis": [("All my COMPANION does is ROAR…", "All my COMPANION does is ROAR…")],
"Route114_Text_ExplainRoar": [("sends COMPANION scurrying.", "sends COMPANIONS scurrying.")],
"Route114_Text_Poochyena": r"Grrrarf! Rrarf!$",
"Route114_FossilManiacsTunnel_Text_DevonCorpRevivingFossils": [("reviving COMPANION from\lFOSSILS…", "reviving COMPANIONS from\lFOSSILS…")],
"Route114_LanettesHouse_Text_ResearchNotesPage1": [("Design BOXES to hold 30 COMPANION each.", "BOXES should hold 30 COMPANIONS each."), ("420 COMPANION on the TERMINAL system.", "420 COMPANIONS on the system.")],
"Route114_LanettesHouse_Text_ResearchNotesPage2": [("make COMPANION easier to organize.", "make COMPANIONS easier to organize."), ("please\lthe stored COMPANION.", "please\lthe stored COMPANIONS.")],
"Route114_LanettesHouse_Text_EmailFromBill": r"There's a message from someone on\nthe terminal.\p“… … … … … … …\p“Your Storage System offers more\nconvenience than mine.\p“It has a lot of user-friendly features\nthat make it fun and useful, too.\p“It makes me proud that I played\na part in its development.\p“Here's hoping that you'll continue\nresearch in Storage Systems.\p“From LOBOT, CLOUD CITY\n… … … … … … … …”$",
"Route117_Text_DayCareSign": [("“Let us raise your COMPANION.”", "“Let us raise your COMPANIONS.”")],
V+"Text_ManTryingToDigTunnel": [("full of\ntimid COMPANION.", "full of\ntimid COMPANIONS.")],
V+"Text_AirCleanHere": r"The way the winds blow, sandstorms\nnever reach this far.\pThe air is clean and fresh here.\nLiving here should do wonders for\lanyone stuck on a moisture farm.$",
V+"Text_TownSign": r"ANCHORHEAD\p“The windswept town where moisture\nfarmers meet.”$",
V+"ContestHall_Text_RaisedMonToBeCute": [("you can put COMPANION in\na SHOWCASE", "you can put COMPANIONS in\na SHOWCASE")],
V+"Mart_Text_NestBallOnWeakenedPokemon": [("weakened COMPANION.", "weakened COMPANIONS.")],
V+"PokemonCenter_1F_Text_FaithInYourPokemon": [("in your COMPANION.", "in your COMPANIONS."), ("battling COMPANION can win", "battling COMPANIONS can win")],
V+"House_Text_TrainersGatherAtPokemonLeague": [("Far away, deep in ILUM,\nis the ILUM TEMPLE.", "Far away, on the ice world ILUM,\nis the ILUM TEMPLE.")],
V+"WandasHouse_Text_WallysNextDoor": [("This natural environment is doing\nwonders for LUKE's health.", "Getting off the farm is doing\nwonders for LUKE's spirits.")],
V+"WandasHouse_Text_WallyGoneThatFar": [("Well, I have to give him credit--he is\nmy little brother's son.", "Well, I have to give him credit--he\nhas his father's restless blood.")],
V+"WandasHouse_Text_MeetWanda": [("I'm LUKE's cousin.\nGlad to meet you!", "I've known LUKE since we were kids.\nGlad to meet you!"), ("I think LUKE's become a lot more lively\nand healthy since he came here.", "I think LUKE's grown a lot more\nconfident since he came here.")],
V+"WandasHouse_Text_DontWorryAboutWally": [("I know my little cousin, and he has\nCOMPANION with him, too.", "I know LUKE, and he has\nCOMPANIONS with him, too.")],
V+"WandasHouse_Text_IfAnythingHappenedToWally": [("I would never be able to look his\lparents in MOS ENTHA in the eye…", "I would never be able to look OWEN\land BERU in the eye…")],
V+"WandasHouse_Text_WallyWasInEverGrande": r"LUKE was on ILUM?\pOWEN and BERU would be astonished\nto hear that!$",
# --- overflow fixes (trainer lines) ---
"Route111_Text_DustyDefeat": r"While I have searched for ruins,\nI've not searched for strong\lCOMPANIONS.$",
"Route112_Text_BryantIntro": r"I caught hot COMPANIONS in the MAGMA\nTUNNELS! Take a look!$",
"Route113_Text_WyattIntro": r"Y-you want to battle with me?\nEven though I just caught my\lCOMPANION?$",
"Route117_Text_MariaIntro": r"I do my triathlon training with my\nCOMPANIONS, so I'm pretty confident\labout my speed.$",
}
NOTES = {R1+"Text_ShouldBeMirageTowerAroundHere": "Mirage Tower = a JAWA SANDCRAWLER that appears and vanishes",
         "Route114_LanettesHouse_Text_EmailFromBill": "BILL (Kanto) -> LOBOT of Cloud City"}
FIX["Route113_GlassWorkshop_Text_NoRoomInPC"] = [("You've no room in your TERMINAL, huff-puff?", "You've no room in your TERMINAL,\nhuff-puff?")]

REFLOW = True
