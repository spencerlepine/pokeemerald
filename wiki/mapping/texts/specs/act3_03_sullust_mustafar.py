# Sullust and Mustafar: Inyusu Tor (Fallarbor), Starfall Cavern (Meteor Falls), Mustafar Peak (Mt. Chimney),
# Ashen Pass (Jagged Pass), Fiery Path, Pirin (Lavaridge, Sabine's arena).
# Vader's motive mirrors Jabba's: Jabba wants every world drowned into Hutt swamps; Vader wants land, order and
# industry he can control. Sabine Wren is female like Flannery; her grandfather was a keeper of the TRIALS OF ILUM.
KEEP_REST_MAPS = ("map:fallarbor", "map:meteor-falls", "map:mt-chimney", "map:jagged-pass", "map:fiery-path",
                  "map:lavaridge")
F = "FallarborTown_"
MF = "MeteorFalls_1F_1R_Text_"
MF2 = "MeteorFalls_1F_2R_Text_"
MC = "MtChimney_Text_"
JP = "JaggedPass_Text_"
L = "LavaridgeTown_"
LG = "LavaridgeTown_Gym_1F_Text_"
FIX = {
# --- Inyusu Tor ---
F+"Text_HaveYouChallengedFlannery": r"Have you already challenged SABINE,\nthe LEADER of PIRIN ARENA?\pHer grandfather was famous.\nHe was one of the FOUR TRIALS in the\lILUM TEMPLE at one point.\pI wouldn't be surprised if SABINE\nbecame a great TRAINER in her\lown right.$",
F+"Text_TownSign": r"INYUSU TOR\n“A farming town in the ashfall.”$",
F+"Text_MoveTutorSign": [("“New moves taught to COMPANION.”", "“New moves taught to COMPANIONS.”")],
F+"ContestHall_Text_MonAllTheseRibbons": [("Have your COMPANION earned any RIBBONS?", "Have yours earned any RIBBONS?")],
F+"BattleTentLobby_Text_FallarborTentMyFavorite": [("faith in\ltheir COMPANION.", "faith in\ltheir COMPANIONS.")],
F+"CozmosHouse_Text_MeteoriteWillNeverBeMineNow": [("conned into telling THE EMPIRE where", "conned into telling the EMPIRE where")],
F+"CozmosHouse_Text_IsThatMeteoriteMayIHaveIt": [("the METEORITE that THE EMPIRE\ntook", "the METEORITE that the EMPIRE\ntook")],
F+"CozmosHouse_Text_CozmoWentToMeteorFalls": [("some people from\lTHE EMPIRE.", "some people from\lthe EMPIRE.")],
F+"MoveRelearnersHouse_Text_ImTheMoveTutor": [("I know all the moves that COMPANION\nlearn", "I know all the moves that COMPANIONS\nlearn"), ("and I can\lteach COMPANION those moves.", "and I can\lteach COMPANIONS those moves.")],
F+"PokemonCenter_1F_Text_LanetteGreeting": [("access something on this TERMINAL.", "access something on this terminal.")],
F+"PokemonCenter_1F_Text_FossilManiacEdgeOfTown": [("I wonder what COMPANION looked like", "I wonder what COMPANIONS looked like")],
F+"Text_RegionKnownForMeteors": [("They say STARFALL CAVERN was gouged out\nby a falling meteorite long ago.", "They say STARFALL CAVERN was carved\nout by a falling meteorite long ago.")],
LG+"ExplainHeatBadgeTakeThis": [("If you have a MAGMA SHARD, all COMPANIONS\nup to Level 50,", "With a MAGMA SHARD, all COMPANIONS\nup to Level 50,"), ("And, it lets COMPANION use the HM move", "And, it lets COMPANIONS use the HM move")],
L+"House_Text_WifeWarmingEggInHotSprings": [("She left two COMPANIONS with the NURSERY.\nAnd they discovered that EGG!", "She left two COMPANIONS at the NURSERY.\nAnd they found that EGG!")],
# --- Starfall Cavern ---
MF+"DontExpectMercyFromMagma": [("in the way of THE EMPIRE, don't", "in the way of the EMPIRE, don't")],
MF+"HoldItRightThereMagma": r"Hold it right there, EMPIRE scum!\pYou're badly mistaken if you think you\ncan have your way with the galaxy!$",
MF+"BeSeeingYouTeamAqua": r"Hehehe!\nEven the CARTEL shows up!\pBut it's too much trouble to deal with\nyou all…\pHeh, it doesn't matter!\pWe've got the METEORITE, so off to\nMUSTAFAR PEAK we go!\pHehehe! Be seeing you, you CARTEL\nslimeballs!$",
MF+"ArchieSeenYouBefore": r"JABBA: Didn't I see you before?\nAt MOS EISLEY's MUSEUM?\pAh, so your name is {PLAYER}.\pAt the time, I thought you were one\nof the EMPIRE's goons.\pHo ho ho…\nYou're one odd kid.\pThe EMPIRE is a dangerous group of\ntotal fanatics.\pThey scorch and pave whole worlds,\nclaiming to bring order.\pThey are the rivals to us,\nthe swamp-loving CARTEL!$",
MF+"BossWeShouldChaseMagma": r"Mighty JABBA, we should give chase\nto the EMPIRE…$",
MF+"ArchieYesNoTellingWhatMagmaWillDo": [("There's no telling what THE EMPIRE\nwill do", "There's no telling what the EMPIRE\nwill do")],
MF+"ArchieFarewell": [("an eye out for THE EMPIRE, too.", "an eye out for the EMPIRE, too.")],
MF+"MeetProfCozmo": r"I… I'm TIEN…\nI'm a PROFESSOR…\pThe EMPIRE asked me to guide them\nto STARFALL CAVERN…\pBut they tricked me.\nThey even took my METEORITE away…\pAnd then another bunch,\nthe CARTEL, showed up.\pAfter that…\nI don't understand any of it.\pBut the EMPIRE…\pWhat are they going to do with that\nMETEORITE at MUSTAFAR PEAK?$",
MF+"WhatsTeamMagmaDoingAtMtChimney": r"DR. TIEN: But the EMPIRE…\pWhat are they going to do with that\nMETEORITE at MUSTAFAR PEAK?$",
MF2+"NicolasIntro": r"This is where we DRAGON users do our\ntraining.\pThey say a JEDI once trained here.\nNow do you see how special it is here?$",
MF2+"NicolasPostBattle": [("When will my COMPANION and I become", "When will my COMPANIONS and I become")],
MF2+"JohnIntro": [("We've always battled COMPANION\ntogether", "We've always battled COMPANIONS\ntogether")],
MF2+"JohnRematchIntro": [("We've always battled COMPANION\ntogether", "We've always battled COMPANIONS\ntogether")],
"MeteorFalls_StevensCave_Text_ShouldKnowHowGoodIAmExpectWorst": [("just a rock maniac?", "just a crystal maniac?"), ("the DAGOBAH LAUNCH TOWER.", "the YAVIN 4 LAUNCH TOWER.")],
"MeteorFalls_StevensCave_Text_MyPredictionCameTrue": r"LEIA: Come to think of it, ever since\nour paths first crossed in the\lSHADOWLANDS of KASHYYYK, I felt it.\pI thought that you would eventually\npass the TRIALS OF ILUM.\pMy predictions usually come true.\pAnd where will you go from here?\p… … … … … …\n… … … … … …\pFufufu, even I couldn't tell you that.$",
# --- Mustafar Peak ---
MC+"MaxieIntro": r"VADER: Hm?\nWho are you?\p… … … … … …\n… … … … … …\pJABBA has been complaining about a\nchild meddling in the CARTEL's\laffairs.\pIt must be you he meant.\pSo you think you can interfere\nwith the EMPIRE?\pNow you listen.\nWater breeds swamps, and swamps\lbreed disorder.\pSolid land can be ordered.\nIt can be built on and controlled.\pThe EMPIRE will expand the land of\nevery world in the galaxy.\pAnd for that, we need the power of\nwhat sleeps within this mountain…\pI have said too much.\pBut, no matter!\nI will show you the power of\lthe dark side!$",
MC+"MaxieDefeat": r"Impressive…\nMost impressive.$",
MC+"MaxieYouHaventSeenLastOfMagma": r"VADER: Enough.\nI will withdraw, for now.\pThe Force is strong with you…\nBut this is not the last you will\lsee of the EMPIRE.\pEven without the METEORITE, once\nI possess the BLUE KYBER…$",
MC+"TabithaIntro": [("from STARFALL CAVERN to the BOSS!", "from STARFALL CAVERN to LORD VADER!")],
MC+"TabithaDefeat": [("if our leader\nawakens that thing…", "if LORD VADER\nawakens that thing…")],
MC+"TabithaPostBattle": r"LORD VADER, hurry!\nGive it the METEORITE's energy!\pHehehe…$",
MC+"Grunt2Intro": [("We of THE EMPIRE are working hard for", "We of the EMPIRE are working hard for")],
MC+"Grunt2PostBattle": r"LORD VADER says, “It will bring order\nto everyone.”\pBut why does everyone keep getting\nin our way?$",
MC+"Grunt1PostBattle": r"A kid like you, you ought to be\nplaying in the sand!$",
MC+"TeamAquaAlwaysMessingWithPlans": r"That annoying CARTEL…\nThey always mess with our plans!$",
MC+"AquasNameSimilar": r"We're the EMPIRE!\pThey're the CARTEL!\pThey're nothing but smugglers\nin fancy robes!$",
MC+"ArchieGoStopTeamMagma": [("fanatics\nof THE EMPIRE are up to!", "fanatics\nof the EMPIRE are up to!")],
MC+"ArchieThankYou": r"JABBA: {PLAYER}!\nThank you!\pWith your help, we thwarted the\nEMPIRE's destructive plan!\pBut… You…\nWhose side are you on?\pHo ho ho, it doesn't matter.\pWe will remain vigilant and keep up\nour pursuit of the EMPIRE.\p{PLAYER}, we shall meet again!$",
MC+"MagmaOutnumbersUs": r"Darn… The EMPIRE outnumbers us!\nWe can't keep up with them!$",
MC+"LessHabitatForWaterPokemon": r"If they expand the land, there'll be\nfewer swamps for HUTTS!$",
MC+"MagmasNameSimilar": r"We're the CARTEL!\pThey're the EMPIRE!\pThey're nothing but bullies in\nshiny armor!$",
MC+"LavaCookiesJust200": r"ASH CAKES are MUSTAFAR PEAK's local\nspecialty.\pTry one. It's just 200 credits.$",
MC+"RouteSign": r"{DOWN_ARROW} ASHEN PASS\nPIRIN AHEAD$",
MC+"ShelbyRematchIntro": [("of your COMPANION, why,", "of your COMPANIONS, why,")],
MC+"ShelbyPostRematch": [("the hearts of your COMPANION.", "the hearts of your COMPANIONS.")],
MC+"SheilaIntro": [("I want to make my COMPANION battle!", "I want to make my COMPANIONS battle!")],
MC+"SheilaPostBattle": [("COOKIES as souvenirs.", "ASH CAKES as souvenirs.")],
MC+"ShelbyIntro": [("the hot springs", "the lava springs")],
MC+"ShirleyIntro": [("the hot springs", "the lava springs")],
MC+"ShirleyDefeat": [("out of the water.", "out of the springs.")],
MC+"ShirleyPostBattle": [("hot springs.", "lava springs.")],
"MtChimney_CableCarStation_Text_CableCarReadyGetOn": [("The SHUTTLE is ready to go down.", "The SHUTTLE is ready to go down.")],
# --- Ashen Pass ---
JP+"DianaPostBattle": [("bicycles", "bikes")],
JP+"JulioPostBattle": [("My bicycle bounced", "My bike bounced")],
JP+"DianaRematchIntro": [("Just like COMPANION!", "Just like COMPANIONS!")],
# --- Pirin (Lavaridge) ---
L+"Text_MayNiceBadgesTakeThis": [("good COMPANION…", "good COMPANIONS…")],
L+"Text_HaveEggWillYouTakeIt": [("kept together with COMPANION and", "kept together with COMPANIONS and"), ("your COMPANION radiate vitality.", "your COMPANIONS radiate vitality.")],
L+"Text_BatheInHotSpringsEveryDay": [("a beautiful and strong\nARENA LEADER", "a wise and strong\nARENA LEADER")],
L+"Text_IfPokemonInHotSprings": [("If people put COMPANION in hot springs,", "If people put COMPANIONS in hot springs,")],
L+"Text_TownSign": r"PIRIN\p“HOT SPRINGS OF SULLUST\nAn excellent place for relaxing!”$",
L+"Text_HerbShopSign": r"PIRIN HERB SHOP\n“Bitter taste--better cure!”$",
L+"Gym_1F_Text_GymGuideAdvice": r"Hey, how's it going, ILUM-bound\n{PLAYER}?\pPIRIN's ARENA LEADER SABINE\nuses FIRE-type COMPANIONS.\pHer passion for COMPANIONS burns\nhotter than a volcano.\pDon't get too close to her--you'll burn!\nHose her down with water and then\lgo for it!$",
LG+"GeraldIntro": [("Can your COMPANION withstand", "Can your COMPANIONS withstand")],
LG+"DaniellePostBattle": [("a pretty and strong\nTRAINER", "a quick and strong\nTRAINER")],
LG+"FlanneryIntro": r"Welcome… No, wait.\pPuny TRAINER, how good to see you've\nmade it here!\pI have been entrusted with the…\nNo, wait.\pI am SABINE, and I'm the ARENA\nLEADER here!\pUh…\nDare not underestimate me, though\lI have been LEADER only a short time!\pWith skills inherited from my grandfather,\nI shall, uh…demonstrate the hot\lmoves we have honed on SULLUST!$",
LG+"FlanneryDefeat": [("my COMPANION will be confused.", "my COMPANIONS will be confused.")],
LG+"ExplainOverheat": [("That move inflicts serious damage", "That move inflicts serious damage")],
LG+"FlanneryPreRematch": [("I love COMPANION.", "I love COMPANIONS.")],
LG+"FlanneryRematchNeedTwoMons": [("I love COMPANION.", "I love COMPANIONS.")],
L+"HerbShop_Text_HerbalMedicineWorksButMonWillDislike": [("But your COMPANION will dislike you for it.", "But your COMPANIONS will dislike you.")],
L+"PokemonCenter_1F_Text_HotSpringCanInvigorate": [("I wish I could let my COMPANION\nsoak, too.", "I wish I could let my COMPANIONS\nsoak, too.")],
}
NOTES = {
MC+"MaxieIntro": "Vader's motive mirrors Jabba's: land and order vs swamps (bible/STORY.md)",
F+"Text_HaveYouChallengedFlannery": "Sabine Wren keeps Flannery's grandfather",
"MeteorFalls_StevensCave_Text_ShouldKnowHowGoodIAmExpectWorst": "Emerald text says SOOTOPOLIS SPACE CENTER (source typo); the space center is on MOSSDEEP = YAVIN 4",
}

REFLOW = True
