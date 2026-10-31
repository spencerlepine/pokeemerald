# Dagobah (Act 6): Sootopolis -> DAGOBAH (a village in a flooded crater deep in the swamp), Yoda's arena (Juan),
# the CAVE OF EVIL (Cave of Origin, a dark-side vergence), the DROWNED CAVERN (Seafloor Cavern) where Jabba wakes
# SANDO, Routes 126-130. Yoda speaks in his inverted style; he taught Obi-Wan as a youngling.
# Jabba laughs "Ho ho ho"; Bossk hisses; Vader never says please.
KEEP_REST_MAPS = ("map:sootopolis-city", "map:cave-of-origin", "map:seafloor-cavern", "map:route126", "map:route127",
                  "map:route128", "map:route129", "map:route130", "map:underwater")
S = "SootopolisCity_Text_"
SG = "SootopolisCity_Gym_1F_Text_"
SB = "SootopolisCity_Gym_B1F_Text_"
SF = "SeafloorCavern_"
R9 = "SeafloorCavern_Room9_Text_"


def pl(*olds):
    return [(o, o.replace("COMPANION", "COMPANIONS")) for o in olds]


FIX = {
# --- Cave of Evil (Obi-Wan) ---
"CaveOfOrigin_B1F_Text_WallaceStory": r"Ah, so you are {PLAYER}{KUN}?\nI've heard tales of your exploits.\pMy name is OBI-WAN.\pI was once the ARENA LEADER of\nDAGOBAH, but something came up.\pSo now, I've entrusted my old master\nYODA with the ARENA.\p… … … … … …\n… … … … … …\pGREATKRAYT and SANDO, the two\nCOMPANIONS wreaking havoc here, are\lsaid to be super-ancient COMPANIONS.\pBut there aren't just two super-\nancient COMPANIONS.\pThere is one more somewhere.\pSomewhere, there is a super-\nancient COMPANION named EXOGORTH.\pIt's said that it was EXOGORTH that\ncalmed the two combatants in\lthe distant past.\pBut even I have no clue as to\nEXOGORTH's whereabouts…$",
"CaveOfOrigin_B1F_Text_OldLadyDidntMentionThat": [("when I met the old lady there\nearlier", "when I met the GUARDIANS there\nearlier"), ("I very much doubt that the old lady\nwould try", "I very much doubt the GUARDIANS\nwould try")],
# --- Route 128: the deluge ---
"Route128_Text_ArchieWhatHappened": r"JABBA: What happened…\nWhat is this wretched scene…\pDid I… make a horrible mistake?$",
"Route128_Text_MaxieDoYouUnderstandNow": r"VADER: Do you understand now,\nJABBA?\pDo you finally see how disastrous\nyour dream turned out to be?\pWe must act! Before the situation\ngoes completely out of control!$",
"Route128_Text_MaxieResposibilityFallsToArchieAndMe": r"VADER: {PLAYER}, say nothing.\pI have no right to be critical\nof JABBA…\pBut the way things are now, I doubt\nthat anyone will be capable of\ldoing anything about it.\pBut neither can we stand by and\njust watch helplessly.\pThe responsibility for putting an end\nto this falls to JABBA and me…$",
"Route128_Text_MaxieThisDefiesBelief": r"VADER: This defies belief…\pThose super-ancient COMPANIONS…\pTheir power is unbelievable.\nThey have upset the balance of the\lForce itself…$",
"Route128_Text_StevenWholeWorldWillDrown": r"This is terrible…\pAfter the scorching heat wave ended,\nthis deluge began.\pIf this doesn't stop, all of the OUTER\nRIM… No, every world will drown.\pThis huge rain cloud is spreading\nfrom above DAGOBAH…\pWhat in the galaxy is taking place\nthere?\pThere's no point arguing here…\nDAGOBAH might provide answers…$",
# --- Drowned Cavern ---
SF+"Entrance_Text_HearMagmaNearMossdeep": r"Hey!\nI remember your face!\pIf you're here, it must mean that\nyou're about to mess with us again!\pA punk like you, do you really think\nyou can take on the CARTEL?\pI'd say you're too early by about\na trillion years!\pYou're a perfect fit for the likes of\nthe EMPIRE!\pSpeaking of the EMPIRE, I hear they\nwere spotted near YAVIN 4.\pThat bunch of goons, their armor\nwould rust near the sea!$",
SF+"Entrance_Text_HearMagmaNearMossdeepShort": r"A punk like you, do you really think\nyou can take on the CARTEL?\pI'd say you're too early by about\na trillion years!\pYou're a perfect fit for the likes of\nthe EMPIRE!\pSpeaking of the EMPIRE, I hear they\nwere spotted near YAVIN 4.\pThat bunch of goons, their armor\nwould rust near the sea!$",
SF+"Room1_Text_Grunt1PostBattle": r"I want to get a promotion so I can\nboss around the other THUGS…$",
SF+"Room3_Text_ShellyIntro": r"Hssssss!\pHow did you manage to get here without\na submarine?\lWhat an impressive child!\pBut… It won't do to have you\nmeddling about here.\pAnd BOSSK wants payback for what\nhappened at ENDOR STATION…\pI'm going to give you a little taste\nof pain! Resign yourself to it!$",
SF+"Room3_Text_ShellyPostBattle": r"Hssss!\nYou're so darn strong.\pIt's terribly disappointing that you're\nnot in the CARTEL.\pYou could have enjoyed the swampy\nparadise JABBA has promised as\lone of us…$",
SF+"Room3_Text_Grunt5Intro": r"For our dream to become real, we need\nthe power of COMPANIONS.\pBut meddlers like you use COMPANIONS\nto mess with us even at\la place like this!\pLife just doesn't work the way we\nneed it to!$",
SF+"Room3_Text_Grunt5PostBattle": r"You know, we don't dare question\nthe mighty JABBA.\pBut here you are, just some punk,\ngoing up against him.\pMaybe…\nYou must be something…$",
R9+"ArchieSoItWasYou": r"JABBA: Ho ho ho…\nSo it was you, after all.$",
R9+"ArchieWithThisRedOrb": r"JABBA: Ho ho ho…\pI commend you. I must recognize that\nyou are truly gifted.\pBut!\nI have this in my possession!\pWith this RED KYBER, I can make SANDO…$",
R9+"ArchieAMessageFromOutside": r"JABBA: Hm? It's a message from my\nthugs outside…$",
R9+"ArchieWhatRainingTooHard": r"JABBA: Yes, what is it?\pHm…\nIt's raining heavily?\pGood… That should have happened.\nThat is why we awakened SANDO,\lto drown the dry worlds in swamps.\pWhat?!\pIt's raining far harder than we\nenvisioned? You're in danger?\pThat can't be…\nThat's just not possible…\pHold your position and monitor\nthe situation!$",
R9+"MaxieWhatHaveYouWrought": r"VADER: What have you wrought?\pJABBA… You have finally awoken SANDO,\nhaven't you?\pWhat will happen to the galaxy if this\ndownpour continues for all eternity?\pEvery world's land will drown in\nthe deepening sea…$",
R9+"ArchieDontGetAllHighAndMighty": r"JABBA: W-what?!\nDon't get all high and mighty with me!\pWasn't it you, the EMPIRE, that\ninfuriated GREATKRAYT?\pSo long as I have this RED KYBER,\nI should be able to control SANDO…\pI should be able to control it…$",
R9+"MaxieWeDontHaveTimeToArgue": r"VADER: We don't have the time to\nargue about it here!\pGet outside and see for yourself!\pSee if what you have wrought is the\ngalaxy that we desired!$",
"Underwater_SeafloorCavern_Text_SubExplorer1": r"“SUBMARINE EXPLORER 1” is painted\non the hull.\pThis is the submarine the CARTEL\nstole in MOS EISLEY!\pThe CARTEL must have gone\nashore here.$",
# --- Dagobah village ---
S+"GymSign": r"DAGOBAH ARENA\nLEADER: YODA\p“Judge me by my size, do you?”$",
S+"CitySign": r"DAGOBAH\p“The swamp village where history\nslumbers.”$",
S+"PhysicallyFitLivingHere": [("If you live in this town,", "If you live in this village,")],
S+"GiantPokemonSuddenlyAppeared": [("These giant COMPANION suddenly appeared\nin the middle of the city!", "These giant COMPANIONS appeared out\nof nowhere in the village!")],
S+"FlyingMonStoppedRampage": [("from\nthe sky and stopped the rampaging\lCOMPANION…", "from\nthe sky and stopped the rampaging\lCOMPANIONS…")],
S+"WonderWhatWorldIsLike": r"I… I've never been out of this village.\pI wonder what the galaxy is like on\nthe other side of this round sky?$",
S+"SeeingLegendWithOwnEyes": pl("colossal battle between COMPANION."),
S+"SawLegendWithOwnEyes": pl("colossal battle between COMPANION."),
S+"PrettyMonCameFromSky": r"A pretty COMPANION came down from\nthe sky…$",
S+"CityRegainedCalm": r"The village has regained its calm…$",
S+"CaveOfOriginPleaseLeave": r"Who might you be?\pThis is the CAVE OF EVIL.\pWhat is in it is only what you take\nwith you, they say.\pPlease leave.$",
S+"AwakenedPokemonClash": r"Oh, my…\pThe clash between the two awakened\nCOMPANIONS was quelled by the awakening\lof a third COMPANION…$",
S+"SootopolisSkyBeautiful": r"DAGOBAH's village grew up in an old\ncrater deep in the swamp.\pIf you look up at the sky, the lip of\nthe crater is also visible.\lSo, all you see is the sky in a circle.\pBut that's what makes the sky above\nDAGOBAH the most beautiful.$",
S+"GroudonPleaseStop": r"VADER: GREATKRAYT…\nStop! I command you!\pI know the extent of your power now!\pIf you keep going, all of the OUTER RIM,\nnot just DAGOBAH, will be ruined!$",
S+"AfterAllOurScheming": r"VADER: So the super-ancient COMPANIONS\nwere not only GREATKRAYT and SANDO…\pAfter all our fruitless scheming and\nfrantic efforts, that one COMPANION's\lsimple action puts everything right\lagain as if nothing had happened…\pHmph…\nHahaha…$",
S+"KyogreCalmDown": [],
S+"TryingMeaninglessToPokemon": r"JABBA: SANDO and GREATKRAYT both\nflew off to who knows where.\pThe weather in the OUTER RIM has\nreturned to its normal state…\pHo…\nHo ho…\pMaybe what we were trying to do was\nsomething small, even meaningless,\lto COMPANIONS…$",
S+"InvolvedWithCrisisComeWithMe": [("LEIA: Those COMPANION fighting…", "LEIA: Those COMPANIONS fighting…")],
S+"HereWereAreHelpWallace": [],
S+"SoThatsRayquaza": pl("rampaging\nCOMPANION would"),
S+"MaxieArchieLeft": r"LEIA: It looks like both VADER and\nJABBA have gone away somewhere.\pPerhaps they've gone to JEDHA to\nreturn those crystals…$",
S+"AquaMagmaDidntMeanHarm": r"OBI-WAN: {PLAYER}{KUN}…\pThe leaders of the EMPIRE and CARTEL…\nThere is still good in them, I think.\pIt wouldn't hurt to hear what they\nhave to say for themselves.$",
S+"ThankYouForHelpAcceptThis": [("No, all of OUTER RIM was saved.", "No, all of the OUTER RIM was saved.")],
S+"DazzledByMentor": r"OBI-WAN: I'm sure that you will be\ndazzled by my old master's battle\lstyle. Size matters not.$",
"CaveOfOrigin_B1F_Text_WellHeadToSkyPillar": [("We'll head to the ASTEROID SPIRE right away!", "We'll head to the ASTEROID SPIRE\nright away!")],
S+"ExplainWaterfallGoToGym": [("If you have the SWAMP SHARD, a COMPANION\nthat has learned", "With the SWAMP SHARD, a COMPANION\nthat has learned"), ("And where does one get the SWAMP SHARD?", "Where does one get the SWAMP SHARD?")],
# --- Yoda's arena ---
SG+"GymGuideAdvice": r"Yo! How's it going, ILUM-\nbound {PLAYER}?\pDAGOBAH's ARENA LEADER YODA is\na master of WATER-type COMPANIONS.\pAnd, to get to YODA, an icy floor\nwill hamper your progress…\pListen, I'm sorry, but that's all the\nadvice that I have for you.\pThe rest of the way, you have to\ngo for it yourself!$",
SG+"GymGuidePostVictory": r"Yow! You've beaten even YODA, who\nwas said to be the best in the OUTER\nRIM!\pOkay! Check out your TRAINER CARD.\pIf you've gotten all the SHARDS, you're\nset for the ILUM TEMPLE challenge!$",
SG+"JuanIntro": r"Ask you something, I will.\nKnow this, did you?\pTaught OBI-WAN as a youngling, I did.\nEverything about COMPANIONS.\pOnce, my place as LEADER I gave up.\nTo OBI-WAN, the ARENA I entrusted.\pBut a reason to return, there was.\nHmm. Yes.\pEnough chatter. Begin, we shall.\pWitness our art, you will.\pA great illusion of water, shaped by\nmy COMPANIONS and me!$",
SG+"JuanDefeat": r"Hmm! Excellent!\nThe winner, you are.\pFrom you, a brilliant light I sense.\nOvercome all, your skill will.\pBut elegance, still you lack.\nCompared to OBI-WAN, or to me.\pLend you my robe, perhaps I should?\p… … … … … …\n… … … … … …\pHeh heh heh! Jesting, I am.\pInstead of my robe, take this you\nwill. The SWAMP SHARD!$",
SG+"ExplainRainBadgeTakeThis": r"With the SWAMP SHARD, obey every\ncommand all your COMPANIONS will.\pThe HM move WATERFALL, it also lets\nyou use, to scale walls of water.\pAnd, so forget our battle you never\nwill, take this…$",
SG+"ExplainWaterPulse": r"WATER PULSE, the TECHNICAL MACHINE\nI gave you contains.\pConfuse the target sometimes it will,\nwith ultrasonic waves.\p… … … … … …$",
SG+"JuanPostBattle": r"Gathered all the ARENA SHARDS of the\nOUTER RIM, a TRAINER has? Then go.\pTo the ILUM TEMPLE.\pTo the ice world ILUM, at the edge\nof the OUTER RIM, travel you must.\pThere, the TRIALS await.$",
SG+"GoGetFortreeBadge": r"One SHARD in the OUTER RIM, still\nremains for you.\pTake the TRIALS OF ILUM, you wish?\nThe last SHARD you must win, from\lthe ARENA on ENDOR.$",
SG+"JuanPreRematch": r"YODA: Returned to serenity, this ARENA\nhad…\pBut back, our young typhoon is,\nto test us again!\pHmm! Most certainly, my friend!\pDance with you as often as you wish,\nI shall!$",
SG+"JuanPostRematch": r"YODA: Ask you to be my apprentice,\nI could. Refuse, you would.\pMy robe, a gift to you I would make.\nBut again, refuse you would.\pAnd that, my friend, a certain sign\nof nobility it is!$",
SG+"JuanRematchNeedTwoMons": r"YODA: Returned to serenity, this ARENA\nhad…\pBut back, our young typhoon is,\nto test us again!\pHmm! Most certainly, my friend!\nDance with you, I shall…\pAh, no, no, no.\nBut one COMPANION, you have.\pReturn with two, perhaps more,\nCOMPANIONS, you must.$",
SB+"DaphnePostBattle": pl("to have found\nCOMPANION."),
SB+"BridgetIntro": r"The ARENA of the highest level\nin the OUTER RIM…\pThat's the DAGOBAH ARENA.$",
SB+"OliviaIntro": pl("I train my COMPANION together with"),
"SootopolisCity_House3_Text_JuanHasManyFansDoYou": [("Even more than his student OBI-WAN!", "Even more than his student OBI-WAN!")],
"SootopolisCity_House3_Text_TrainerFanClubWasWild": [("from even\noutside of OUTER RIM.", "from even\noutside the OUTER RIM.")],
"SootopolisCity_House2_Text_DidYouKnowAboutMtPyreOrbs": r"JEDHA TEMPLE…\pAt its peak are two kyber crystals\nplaced side by side. Did you know?$",
"SootopolisCity_House2_Text_YesTwoOrbsSideBySide": r"Yes, two crystals side by side…\pThe sight of them together…\nIt is somehow soothing…$",
"SootopolisCity_House7_Text_CityFromEruptedVolcano": r"Long ago, a volcano rose out of\nthe swamp and fell silent.\pIts crater filled with rainwater and\nthe swamp crept in.\pThat's how DAGOBAH's village came\ninto being.$",
"SootopolisCity_House7_Text_CaveMadeToKeepSomething": [("The cave that links DAGOBAH and\nthe outside world…", "The cave that links the village and\nthe swamp outside…")],
"SootopolisCity_MysteryEventsHouse_1F_Text_OnlyAmusementWatchingBattles": [("I traveled the world\nas a COMPANION TRAINER.", "I traveled the galaxy\nas a COMPANION TRAINER.")],
"SootopolisCity_PokemonCenter_1F_Text_WallaceToughestInHoenn": [("in the whole OUTER RIM region.", "in the whole OUTER RIM.")],
"SootopolisCity_PokemonCenter_1F_Text_ArentPokemonOurFriends": r"Aren't COMPANIONS our friends?\pWhy are they going wild this way?$",
# --- Routes 126-130 ---
"Route126_Text_DeanIntro": r"This towering wall of rock\nhides DAGOBAH's village.$",
"Route126_Text_DeanPostBattle": r"I can't find the way into the\nvillage. Where could it be?$",
"Route127_Text_HenryIntro": [("a SURFING COMPANION?", "a SURFING TRAINER?")],
"Route128_Text_KatelynPostRematch": r"You should give serious thought to\nthe challenges in the CRYSTAL CAVES.$",
"Route128_Text_WayneIntro": r"I want to reach ILUM, so I caught\nmyself a COMPANION that knows\lthe move WATERFALL to crest the falls.$",
"Route128_Text_HarrisonPostBattle": r"There are tough TRAINERS galore\naround ILUM.\pDo you think I may be out\nof my league?$",
"Route129_Text_AllisonPostBattle": [("against\lMother Nature!", "against\lthe elements!")],
"Route129_Text_ClarencePostBattle": r"You have your sights on the TRIALS\nOF ILUM? Keep at it!$",
"Route130_Text_KatiePostBattle": r"The galaxy's children dream\nof one day becoming\lthe ILUM CHAMPION.$",
}
NOTES = {
SG+"JuanIntro": "Yoda's inverted speech; he taught Obi-Wan as a youngling",
S+"CaveOfOriginPleaseLeave": "Cave of Evil line echoes Yoda's 'only what you take with you'",
S+"GroudonPleaseStop": "Vader commands, never begs",
}

REFLOW = True
