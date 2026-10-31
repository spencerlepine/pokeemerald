KEEP_REST_MAPS = ("map:route104", "map:petalburg-woods", "map:rustboro-city", "map:route116", "map:rusturf")
CH = "CHEWIE: Rrrwaaaghh!$"
FIX = {
# Jundland Wastes (Petalburg Woods)
"PetalburgWoods_Text_HaveYouSeenShroomish": [("any COMPANION\ncalled FELUSPORE", "a COMPANION\ncalled FELUSPORE")],
"PetalburgWoods_Text_HandOverThosePapers": [("those papers!", "those schematics!")],
"PetalburgWoods_Text_YouveGotSomeNerve": [("I'm out of\nCOMPANION…", "I'm out of\nCOMPANIONS…")],
"PetalburgWoods_Text_ThatWasAwfullyClose": [("these important papers.", "these important schematics.")],
"PetalburgWoods_Text_TeamAquaAfterSomethingInRustboro": [("Didn't that THE CARTEL thug say", "Didn't that CARTEL thug say")],
"PetalburgWoods_Text_GoBugPokemonTeam": [("a whole bunch of COMPANION!", "a whole bunch of COMPANIONS!")],
"PetalburgWoods_Text_ImOutOfPokeBalls": [("I caught a bunch of COMPANION.", "I caught a bunch of COMPANIONS.")],
"PetalburgWoods_Text_InstantlyPopularWithBugPokemon": [("If you take BUG COMPANIONS to school,", "If you take BUG COMPANIONS to class,")],
"PetalburgWoods_Text_IWantRematch1": [("my BUG\nCOMPANION grow up!", "my BUG\nCOMPANIONS grow up!")],
"PetalburgWoods_Text_IWantRematch2": [("my BUG \nCOMPANION grow up!", "my BUG\nCOMPANIONS grow up!")],
"PetalburgWoods_Text_IveBeenTrainingHard": [("strong COMPANION, right?", "strong COMPANIONS, right?")],
"PetalburgWoods_Text_StayOutOfTallGrass": [("of tall grass.$", "of the scrub.$")],
"PetalburgWoods_Text_MiracleSeedExplanation": [("items for COMPANION\lto hold.", "items for COMPANIONS\lto hold.")],
# Route 104 and Han's landing pad
"Route104_Text_BrineyLivesInSeasideCottage": r"That shack by the landing pad is where\nHAN lives.\pThey say he's the best pilot in the\nOUTER RIM. Just ask him!$",
"Route104_Text_WhatsItLikeAtBottomOfSea": r"The water, huh?\pI wonder what's at the bottom of\nthe lake?$",
"Route104_Text_OnlyThrowBallAtWildPokemon": [("only at\nwild COMPANION.", "only at\nwild COMPANIONS.")],
"Route104_Text_MrBrineysCottage": r"HAN'S LANDING PAD$",
"Route104_Text_RouteSignPetalburg": [("ROUTE 1O4", "ROUTE 104")],
"Route104_Text_RouteSignRustboro": [("ROUTE 1O4", "ROUTE 104")],
"Route104_Text_PrettyPetalFlowShop": r"DESERT BLOOM FLOWER SHOP$",
"Route104_Text_TrainerTipsDoubleBattles": [("In the OUTER RIM region there are pairs", "In the OUTER RIM there are pairs")],
"Route104_Text_MayHaventRaisedPokemon": [("your\nCOMPANION very much?", "your\nCOMPANIONS very much?")],
"Route104_Text_MayPostBattle": [("handle COMPANION.", "handle COMPANIONS."), ("friends with\nCOMPANION, too.", "friends with\nCOMPANIONS, too."), ("be like HAN.", "be like HAN and CHEWIE.")],
"Route104_Text_BrendanNoConfidence": [("in your COMPANION?", "in your COMPANIONS?")],
"Route104_Text_BrendanPostBattle": [("at handling COMPANION.", "at handling COMPANIONS."), ("making COMPANION battle.", "making COMPANIONS battle."), ("Like HAN, it's important to\nbecome friends with your COMPANION.", "Like HAN and CHEWIE, you should\nbe real partners with your COMPANIONS.")],
"Route104_MrBrineysHouse_Text_WaitUpPeeko": r"HAN: Hold on, kid!\nWait up, CHEWIE!$",
"Route104_MrBrineysHouse_Text_ItsYouLetsSailToDewford": r"Hm? You're {PLAYER}{KUN}!\nYou saved my buddy CHEWIE!\lI owe you one, kid.\pWhat's that?\nYou need a ride?\pHeh…\pYou've got a MESSAGE DISC for KACHIRHO\nand a package for MOS EISLEY, huh?\pQuite the busy life you must lead!\pSure, what you're asking is\nno problem at all.\pYou've come to the right pilot!\nWe'll fly to KASHYYYK first.$",
"Route104_MrBrineysHouse_Text_SetSailForDewford": r"HAN: KASHYYYK it is, then!\pPunch it, CHEWIE!$",
"Route104_MrBrineysHouse_Text_DeclineDeliverySail": r"HAN: Is that so?\nYour deliveries can wait?\pJust tell me whenever you're\nready to fly!$",
"Route104_MrBrineysHouse_Text_NeedToMakeDeliveriesSailToDewford": r"HAN: Hey, kid!\nI know exactly what you want to say!\pYou're to deliver a MESSAGE DISC to\nKACHIRHO and a package to MOS EISLEY.\pNo problem at all. You're looking at\nthe best pilot in the OUTER RIM!\pFirst, we'll head for KASHYYYK.$",
"Route104_MrBrineysHouse_Text_NeedToDeliverPackageSailToDewford": r"HAN: Hey, kid!\nI know exactly what you want to say!\pYou're to deliver a package to\nRIC OLIé in MOS EISLEY.\pNo problem at all. You're looking at\nthe best pilot in the OUTER RIM!\pFirst, we'll head for KASHYYYK.$",
"Route104_MrBrineysHouse_Text_WhereAreWeBound": r"HAN: Hey, kid!\nFor you, the FALCON flies anytime!\pSo, where are we headed?$",
"Route104_MrBrineysHouse_Text_TellMeWheneverYouWantToSail": r"HAN: Is that so?\nWell, CHEWIE owes you one.\pJust tell me whenever you're\nready to fly!$",
"Route104_MrBrineysHouse_Text_Peeko": CH,
# Route 116
"Route116_Text_ScoundrelMadeOffWithPeeko": r"Ohhh, what am I gonna do?\pCHEWIE and I were picking up parts\nwhen some cartel thug jumped us…\pThat scoundrel made off with my\nco-pilot! With CHEWIE!\pCHEWIIIIEEEE!$",
"Route116_Text_DiggingTunnelWhenGoonOrderedMeOut": [("filled with COMPANION\nthat react", "filled with COMPANIONS\nthat react")],
"Route116_Text_ThankYouTokenOfAppreciation": [("Why, if I were a rain cloud, I would\nshower you with gratitude and hail\lyou as a hero!", "Why, if I were a sandstorm, I would\nbury you in gratitude and hail\lyou as a hero!")],
"Route116_Text_RusturfTunnelSign": [("BEGGAR'S CANYON\n“Linking BESTINE and ANCHORHEAD", "BEGGAR'S CANYON TUNNEL\n“Linking BESTINE and ANCHORHEAD”")],
"Route116_TunnelersRestHouse_Text_WeHadToStopBoring": [("wild COMPANION in\lthe area.", "wild COMPANIONS in\lthe area.")],
"Route116_TunnelersRestHouse_Text_ManDiggingHisWayToVerdanturf": [("disturb COMPANION,", "disturb COMPANIONS,")],
"Route116_TunnelersRestHouse_Text_GetToVerdanturfWithoutTunnel": r"To get to ANCHORHEAD without using\nthis TUNNEL, you'd have to fly to\lKASHYYYK, then MOS EISLEY,\lthen travel through MOS ESPA.$",
# Bestine town
"RustboroCity_Text_GymLeaderIsntEasyWithFire": [("with\nmy FIRE-type COMPANION…", "with\nmy FIRE-type COMPANIONS…"), ("against ROCK-type COMPANION…", "against ROCK-type COMPANIONS…")],
"RustboroCity_Text_MrBrineyWalksInTheTunnel": r"The pilot HAN has a landing pad\nsouth of here.\pHe goes poking around in the canyon\nevery so often.$",
"RustboroCity_Text_MrBrineyLovesPeeko": r"The pilot HAN has a landing pad\nsouth of here.\pHe said he was going to MOS EISLEY\nfor parts with his co-pilot, CHEWIE.\pThose two are never apart.$",
"RustboroCity_Text_WowYouHavePokemon": [("you have COMPANION with you, too.", "you have COMPANIONS with you, too."), ("places with COMPANION, too.", "places with COMPANIONS, too.")],
"RustboroCity_Text_CatchRarePokemonIfIGoToSchool": [("rare COMPANION easily?", "rare COMPANIONS easily?")],
"RustboroCity_Text_WaitDontTakeMyGoods": [("Don't take my GOODS!", "Don't take my PARTS!")],
"RustboroCity_Text_MayPassedBrineyWantToBattle": [("I guess he's on his way home to his\ncottage by the sea.", "I guess he's on his way back to his\nlanding pad.")],
"RustboroCity_Text_MayOhHaventRaisedPokemonEnough": [("your\nCOMPANION very much?", "your\nCOMPANIONS very much?")],
"RustboroCity_Text_MayMrBrineyHint": [("but HAN\lwas once a revered seafarer.", "but HAN\lis a legendary pilot.")],
"RustboroCity_Text_BrendanPassedBrineyWantToBattle": [("I bet he was on his way home to his\ncottage by the sea.", "I bet he was on his way back to his\nlanding pad.")],
"RustboroCity_Text_BrendanNoConfidenceInPokemon": [("in your COMPANION?", "in your COMPANIONS?")],
"RustboroCity_Text_BrendanMrBrineyHint": [("HAN was once a great sailor.", "HAN is a legendary pilot.")],
"RustboroCity_Text_GymSign": [("“The ROCK-loving honors student!”", "“The ROCK-loving teacher!”")],
"RustboroCity_Text_TrainersSchoolSign": [("about\nCOMPANION!”", "about\nCOMPANIONS!”")],
"RustboroCity_Text_DevelopedNewPokenavFeature": [("The one our PRESIDENT gave you?", "The one the SENATOR gave you?")],
"RustboroCity_Text_AddedMatchCallPleaseCallMrStone": [("our PRESIDENT STONE should\nbe registered", "SENATOR ORGANA should\nbe registered"), ("Please give our PRESIDENT a call.", "Please give the SENATOR a call.")],
"RustboroCity_CuttersHouse_Text_YouCanPutThisHMToGoodUse": [("your well-trained COMPANION…", "your well-trained COMPANIONS…")],
"RustboroCity_CuttersHouse_Text_ExplainCut": [("by COMPANION outside of battle.", "by COMPANIONS outside of battle."), ("Any COMPANION that's learned VIBROBLADE can\nchop down thin trees", "A COMPANION that knows VIBROBLADE can\nslice through thin trees")],
"RustboroCity_CuttersHouse_Text_DadHelpedClearLandOfTrees": [("He made his COMPANION use VIBROBLADE to clear\nthe land of trees.", "His COMPANIONS used VIBROBLADE to\nclear the land of trees.")],
# House Organa
"RustboroCity_DevonCorp_1F_Text_RocksMetalDisplay": [("got its start as\na producer of stones from quarries.", "got its start as\na mining company."), ("produced iron from\nfilings in the sand.", "refined durasteel\nfrom desert ore.")],
"RustboroCity_DevonCorp_1F_Text_ProductDisplay": [("“In addition to industrial products,\nHOUSE ORGANA now markets sundries and\lpharmaceuticals for better lifestyles.", "“In addition to starfighters,\nHOUSE ORGANA now markets droids and\lmedical supplies for better lives.")],
"RustboroCity_DevonCorp_2F_Text_DeviceForTalkingToPokemon": [("talking\nwith COMPANION.", "talking\nwith COMPANIONS.")],
"RustboroCity_DevonCorp_2F_Text_WeFinallyMadeNewBalls": [("catch COMPANION you've caught before.", "catch COMPANIONS you've caught before.")],
"RustboroCity_DevonCorp_2F_Text_WowThatsAPokenav": [("our\nPRESIDENT's desire to learn about\lthe feelings of COMPANION.", "the\nSENATOR's wish to keep people\lin touch across the stars.")],
"RustboroCity_DevonCorp_2F_Text_DeviceToVisualizePokemonDreams": [("dreams of\lCOMPANION…", "dreams of\lCOMPANIONS…")],
"RustboroCity_DevonCorp_2F_Text_DevelopDeviceToResurrectFossils": [("resurrects COMPANION from fossils…", "revives COMPANIONS from fossils…")],
"RustboroCity_DevonCorp_2F_Text_HandedFossilToResearcher": [],
"RustboroCity_DevonCorp_2F_Text_ReceivedMonFromResearcher": [],
"RustboroCity_DevonCorp_3F_Text_MrStoneIHaveFavor": r"I'm BAIL ORGANA, senator of ALDERAAN\nand head of HOUSE ORGANA.\pI'd just got word about you!\pYou saved our staff not just once,\nbut twice!\pI have a favor to ask of an amazing\nperson like you.\pI understand that you're delivering\na package to MOS EISLEY's SHIPYARD.\pWell, on the way, could you stop off on\nKASHYYYK?\pMy daughter LEIA is there. Please\ndeliver this MESSAGE DISC to her.$",
"RustboroCity_DevonCorp_3F_Text_MrStoneWantYouToHaveThis": r"SEN. ORGANA: Now, a senator never asks\na favor for nothing in return.\pThat's why I want you to have this!$",
"RustboroCity_DevonCorp_3F_Text_MrStoneExplainPokenavRestUp": r"SEN. ORGANA: That device…\pIt's a COMMUNICATION LINK, or COMLINK\nfor short.\pIt's an indispensable tool for any\nTRAINER on an adventure.\pIt has a star chart of the OUTER RIM.\pYou can find KASHYYYK and\nMOS EISLEY easily!\pBy the way, I've heard that the\nEMPIRE and the CARTEL have been\lmaking trouble far and wide.\pI think it would be best if you rested\nup before you go on your way.$",
"RustboroCity_DevonCorp_3F_Text_NotFamiliarWithTrends": [("Since my youth, I've immersed\nmyself in work.", "Since my youth, I've immersed\nmyself in politics."), ("TRAINERS in the ILUM TEMPLE?", "TRAINERS at the ILUM TEMPLE?")],
"RustboroCity_DevonCorp_3F_Text_ThisIs3rdFloorWaitHere": [("Our PRESIDENT's OFFICE is on\nthis floor.", "The CHAIRMAN's OFFICE is on\nthis floor.")],
"RustboroCity_DevonCorp_3F_Text_WordWithPresidentComeWithMe": [("Our PRESIDENT would like to have\na word with you.", "SENATOR ORGANA would like to have\na word with you.")],
"RustboroCity_DevonCorp_3F_Text_RareRocksDisplay": [("assembled by the PRESIDENT.", "assembled by the SENATOR.")],
"RustboroCity_Flat1_1F_Text_PokemonStrange": r"COMPANIONS are such strange beings.$",
"RustboroCity_Flat1_2F_Text_ThankYouIllGiveYouWallpaper": [("BOXES in the TERMINAL\lCOMPANION Storage System.", "BOXES in the HoloNet\lCOMPANION Storage System.")],
"RustboroCity_Flat2_3F_Text_PresidentCollectsRareStones": r"SENATOR ORGANA likes to collect\nrare stones.$",
"RustboroCity_Flat2_3F_Text_PresidentsSonAlsoCollectsRareStones": r"I think the SENATOR's daughter also\ncollects rare crystals.$",
# Bestine arena
"RustboroCity_Gym_Text_GymGuideAdvice": [("Would you like to become the CHAMPION?", "Would you like to reach ILUM?"), ("We'll aim for the\nCOMPANION CHAMPIONSHIP together!", "We'll aim for the\nTRIALS OF ILUM together!"), ("is a user\nof ROCK-type COMPANION.", "is a user\nof ROCK-type COMPANIONS.")],
"RustboroCity_Gym_Text_GymGuidePostVictory": [("the stairs to the CHAMPIONSHIP!", "the road to ILUM!")],
"RustboroCity_Gym_Text_MarcPostBattle": [("It took smarts and sense for her to\npick the ROCK type at her young age.", "It took smarts and sense for him to\npick the tough ROCK type.")],
"RustboroCity_Gym_Text_RoxanneIntro": [("so that I might\napply what I learned at the BESTINE\lACADEMY in battle.", "so that I might\napply what I teach at the\lACADEMY in battle."), ("and with which COMPANION?", "and with which COMPANIONS?")],
"RustboroCity_Gym_Text_RoxanneDefeat": [("Please accept the official COMPANION\nLEAGUE DUNE SHARD.", "Please accept the official ILUM\nTEMPLE DUNE SHARD.")],
"RustboroCity_Gym_Text_StoneBadgeInfoTakeThis": [("power of your COMPANION.", "power of your COMPANIONS.")],
"RustboroCity_Gym_Text_RoxannePostRematch": [("battling COMPANION.", "battling COMPANIONS.")],
"RustboroCity_Gym_Text_RoxanneRematchNeedTwoMons": [("one more\nCOMPANIONS.", "one more\nCOMPANION.")],
"RustboroCity_House1_Text_AllSortsOfPlaces": [("sorts of COMPANION and people.", "sorts of COMPANIONS and people.")],
"RustboroCity_House2_Text_RoxanneKnowsALot": [("a lot about COMPANION.\pShe's really strong, too!", "a lot about COMPANIONS.\pHe's really strong, too!")],
"RustboroCity_House3_Text_IGivePerfectlySuitedNicknames": [("For my own COMPANION, I give them", "For my own COMPANIONS, I give them")],
"RustboroCity_Mart_Text_ShouldBuySuperPotionsInstead": [("BACTA PATCHS", "BACTA PATCHES")],
"RustboroCity_PokemonCenter_1F_Text_MaleAndFemalePokemon": [("female COMPANION.", "female COMPANIONS.")],
"RustboroCity_PokemonSchool_Text_BlackboardListsStatusChanges": [("affect COMPANION in battle.", "affect COMPANIONS in battle.")],
"RustboroCity_PokemonSchool_Text_ExplainQuickClaw": [("held by COMPANION.", "held by COMPANIONS.")],
"RustboroCity_PokemonSchool_Text_TradingRightNow": [("I'm trading COMPANION with", "I'm trading COMPANIONS with")],
"RustboroCity_PokemonSchool_Text_PokemontCantUseManMadeItems": [("COMPANION can hold items, but they", "COMPANIONS can hold items, but they")],
"RustboroCity_PokemonSchool_Text_ConfusedPokemonAttacksItself": [("some COMPANIONS moves can", "some COMPANION moves can")],
"RustboroCity_PokemonSchool_Text_PokemonHealItselfWithBerry": [("items that\nCOMPANION can hold…", "items that\nCOMPANIONS can hold…")],
"RustboroCity_PokemonSchool_Text_StudentsNotes": [("catches\nCOMPANION, raises them,", "catches\nCOMPANIONS, raises them,")],
"RustboroCity_PokemonSchool_Text_ScottMetAlreadyCut": [("COMPANION battle experts.", "COMPANION battle experts. Heh."), ("So, what brings you to this SCHOOL?", "So, what brings you to this ACADEMY?")],
"RustboroCity_PokemonSchool_Text_ScottStoneBadge": [("from a LEAGUE SHARD.", "from a SHARD alone.")],
"RustboroCity_PokemonSchool_Text_ScottMetAlreadyStoneBadge": [("from a LEAGUE SHARD.", "from a SHARD alone.")],
# Beggar's Canyon (Rusturf Tunnel)
"RusturfTunnel_Text_Peeko": CH,
"RusturfTunnel_Text_GruntIntro": [("Grah, keelhaul it all!", "Grah, blast it all!"), ("That hostage COMPANION turned out to\nbe worthless!", "That WOOKIEE hostage turned out\nto be nothing but trouble!")],
"RusturfTunnel_Text_PeekoGladToSeeYouSafe": r"CHEWIE!\nAm I glad to see you, buddy!$",
"RusturfTunnel_Text_ThankYouLetsGoHomePeeko": r"CHEWIE says he owes you a life debt.\pName's HAN. HAN SOLO.\nAnd, you are?\p… … … … … … … …\n… … … … … … … …\pAh, so you're {PLAYER}{KUN}!\nThanks, kid. I mean it.\pIf you ever need a ride somewhere,\ndon't hesitate to ask!\pYou can usually find me at my\nlanding pad near JUNDLAND WASTES.\pCome on, CHEWIE, let's get out\nof here.\pCHEWIE: Hrrrnnn!$",
"RusturfTunnel_Text_WhyCantTheyKeepDigging": [("in ANCHORHEAD\nTOWN just beyond here…", "in ANCHORHEAD\njust beyond here…")],
"RusturfTunnel_Text_ToGetToVerdanturf": r"To get from BESTINE to ANCHORHEAD,\nyou need to fly to KASHYYYK, then\lMOS EISLEY, then pass MOS ESPA…$",
"RusturfTunnel_Text_ExplainStrength": [("If a muscular COMPANIONS were to learn", "If a muscular COMPANION were to learn")],
"RusturfTunnel_Text_MikeIntro": [("a wild man up in the\nmountains? A mountain man, right?", "a wild man out in the\ncanyon? A canyon man, right?"), ("a COMPANION in\nthe mountains a mountain COMPANION?", "a COMPANION in\nthe canyon a canyon COMPANION?")],
"RusturfTunnel_Text_MikeDefeat": [("My COMPANION…\nRan out of power…", "My COMPANIONS…\nRan out of power…")],
"RusturfTunnel_Text_MikePostBattle": [("to\nprotect COMPANION, right?", "to\nprotect COMPANIONS, right?")],
}
NOTES = {"RustboroCity_DevonCorp_3F_Text_MrStoneIHaveFavor": "Bail is chairman of House Organa; Leia is his daughter (so 'the PRESIDENT's son' = Leia)",
         "RusturfTunnel_Text_ThankYouLetsGoHomePeeko": "Chewie is Han's co-pilot, a character (never a creature)"}
FIX["PetalburgWoods_Text_IWantRematch2"] = [("my BUG \nCOMPANIONS grow up!", "my BUG\nCOMPANIONS grow up!")]
FIX["PetalburgWoods_Text_StayOutOfTallGrass"] = [("If your COMPANIONS are weak and you want\nto avoid battles, you should stay out\lof tall grass.", "If your COMPANIONS are weak and you\nwant to avoid battles, stay out\lof the scrub.")]
FIX["PetalburgWoods_Text_TrainerTipsPP"] = [("In addition to Hit Points (HP), COMPANIONS\nhave Power Points (PP)", "Besides Hit Points (HP), COMPANIONS\nhave Power Points (PP)")]
FIX["Route104_Text_MayPostBattle"] = r"MIRA: I can tell you've gotten pretty\ngood at handling COMPANIONS.\pBut instead of only making them\nbattle, be like HAN and CHEWIE.\pIt's important to become friends with\nyour COMPANIONS, too.$"
FIX["RustboroCity_DevonCorp_3F_Text_ThankYouForDeliveringLetter"] = [("SEN. ORGANA: You delivered my MESSAGE DISC?\nThank you kindly!", "SEN. ORGANA: You delivered my\nMESSAGE DISC? Thank you kindly!")]
FIX["RustboroCity_DevonCorp_3F_Text_NotFamiliarWithTrends"] = [("SEN. ORGANA: Since my youth, I've immersed\nmyself in work.", "SEN. ORGANA: Since my youth, I've\nimmersed myself in politics."), ("TRAINERS in the ILUM TEMPLE?", "TRAINERS at the ILUM TEMPLE?")]
FIX["RustboroCity_DevonCorp_3F_Text_VisitCaptSternShipyard"] = [("If you visit the SHIPYARD in MOS EISLEY,\nyou should go see RIC OLIé.", "At the SHIPYARD in MOS EISLEY,\nyou should go see RIC OLIé.")]
FIX["RustboroCity_Gym_Text_RoxanneIntro"] = [("I became an ARENA LEADER so that I might\napply what I learned at the BESTINE\lACADEMY in battle.", "I became an ARENA LEADER so that I\ncould apply what I teach at the\lACADEMY in battle."), ("and with which COMPANION?", "and with which COMPANIONS?")]
FIX["RustboroCity_PokemonSchool_Text_ScottMetAlreadyCut"] = [("COMPANION battle experts.", "COMPANION battle experts. Heh."), ("So, what brings you to this SCHOOL?", "So, what brings you to this ACADEMY?"), ("have a COMPANION learn the move VIBROBLADE.", "teach a COMPANION VIBROBLADE.")]

REFLOW = True

# --- House Organa grammar ---
FIX["RustboroCity_Text_WeShortenItToDevon"] = r"HOUSE ORGANA of ALDERAAN…\nWe all just shorten it to ORGANA.\pThey make all sorts of\nconvenient products.$"
FIX["RustboroCity_DevonCorp_2F_Text_WeFinallyMadeNewBalls"] = [("developed by\nthe HOUSE ORGANA.", "developed by\nHOUSE ORGANA.")]
FIX["RustboroCity_DevonCorp_3F_Text_ThisIs3rdFloorWaitHere"] = [("This is the HOUSE ORGANA's\nthird floor.", "This is the third floor of\nHOUSE ORGANA.")]
