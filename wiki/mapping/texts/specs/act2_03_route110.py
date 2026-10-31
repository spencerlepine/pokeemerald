# Route 110 (Mos Eisley -> Mos Espa): the podrace track (Cycling Road), Prof. Korr, rival, and
# Garindan's Trick House (the TRICK MASTER is GARINDAN, a Kubaz spy and master of disguise).
KEEP_REST_MAPS = ("map:route110",)
R = "Route110_"
FIX = {
R+"Text_MayLetsBattle": [("my COMPANION grew stronger.", "my COMPANIONS grew stronger.")],
R+"Text_RideBikeAtFullSpeed": [("Wouldn't it be great to ride a BIKE\nat full speed on PODRACE TRACK?", "Wouldn't it be great to race a\nBIKE down the PODRACE TRACK?")],
R+"Text_YouGotBikeFromRydel": [("It says right on your bike…", "It says right on your bike…")],
R+"Text_TwoRoads": [("A road each for people and COMPANIONS.", "A road each for racers and COMPANIONS.")],
R+"Text_WhichShouldIChoose": [("and look for COMPANION?", "and look for COMPANIONS?")],
R+"Text_ChallengeReactionBest": [("Your love of cycling", "Your love of racing")],
R+"Text_ChallengeReactionOk": [("the\nsheer pleasure of cycling.", "the\nsheer pleasure of racing.")],
R+"Text_ChallengeReactionBad": [("Your cycling skills border\non terrifying.", "Your piloting skills border\non terrifying.")],
R+"Text_ChallengeReactionWorst": [("this\nunfortunate cycling business.", "this\nunfortunate racing business.")],
R+"Text_SeasideParkingSign": r"SPEEDER PARKING$",
R+"Text_TrickHouseSign": [("to reach the wondrous TRICK HOUSE.”", "to reach GARINDAN's TRICK HOUSE.”")],
R+"SeasideCyclingRoadNorthEntrance_Text_GoAllOutOnCyclingRoad": [("and cycle as fast as you'd like.", "and race as fast as you'd like.")],
R+"SeasideCyclingRoadSouthEntrance_Text_GoAllOutOnCyclingRoad": [("and cycle as fast as you'd like.", "and race as fast as you'd like.")],
R+"SeasideCyclingRoadNorthEntrance_Text_TooDangerousToWalk": r"Sorry, you can't walk on the PODRACE\nTRACK. It's too dangerous.\pPlease come back with a BIKE.$",
R+"SeasideCyclingRoadSouthEntrance_Text_TooDangerousToWalk": r"Sorry, you can't walk on the PODRACE\nTRACK. It's too dangerous.\pPlease come back with a BIKE.$",
R+"TrickHouseEnd_Text_FountainOfIdeasRunDry": [("toured the country", "toured the galaxy")],
R+"TrickHouseEntrance_Text_TheyCallMeTrickMaster": r"Behold!\pFor I am the greatest living mystery\nof a spy in all of the OUTER RIM!\lThey call me GARINDAN…\pThe TRICK MASTER!\nWahahaha! Glad to meet you!$",
R+"TrickHouseEnd_Text_AllNightToMakeMechadolls": [("It took me all night to make QUIZ DROIDS\nand another to think up the quiz…", "It took me all night to build QUIZ\nDROIDS and another to write the quiz…")],
R+"Text_AcroBikesDoNotQualify": [("SPEEDER BIKES do not qualify for rating.\nThey are easy to turn, so it's not fair.", "SPEEDER BIKES don't qualify for rating.\nThey turn too easily. It's not fair.")],
R+"TrickHousePuzzle2_Text_GeorgiaPostBattle": [("Maybe even enough to be an ARENA LEADER!$", "Maybe even an ARENA LEADER!$")],
R+"TrickHousePuzzle5_Text_Mechadoll3Quiz2": [("Sell one DURASTEEL POD and buy\none BACTA SPRAY. How much money remains?", "Sell one DURASTEEL POD and buy one\nBACTA SPRAY. How much is left?")],
R+"TrickHouseEntrance_Text_MechadollWhichTent": [("MECHADOLL 5 I AM!", "QUIZ DROID 5 I AM!")],
R+"TrickHousePuzzle5_Text_Mechadoll2Quiz3": [("Which of these COMPANIONS did THE CARTEL\nuse in MOS ENTHA FOREST?", "Which of these COMPANIONS did the\nCARTEL use in JUNDLAND WASTES?"), ("Which of these COMPANIONS did THE CARTEL\nuse in JUNDLAND WASTES?", "Which of these COMPANIONS did the\nCARTEL use in JUNDLAND WASTES?")],
R+"TrickHousePuzzle5_Text_Mechadoll5Quiz3": [("how many\nTRIATHLETES were there?", "how many\nSWOOP RACERS were there?")],
R+"TrickHousePuzzle6_Text_BennyIntro": [("my BIRD COMPANION\nto fly over the wall…", "my BIRD COMPANION\nto fly me over the wall…")],
R+"TrickHousePuzzle8_Text_VincentPostBattle": [("You've beaten the ILUM TEMPLE\nCHAMPION? That's too much!", "You've passed the TRIALS OF\nILUM? That's too much!")],
# --- overflow fixes (trainer lines) ---
"Route110_Text_AnthonyPostBattle": r"Speed alone won't win me battles.\nI need to reconsider this…$",
"Route110_Text_EdwinPostBattle": r"When I see a COMPANION I don't know,\nmy passion as a collector is ignited!$",
"Route110_Text_TimmyIntro": r"I found some cool COMPANIONS in the\nscrub around here!$",
}

REFLOW = True
