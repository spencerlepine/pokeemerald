# Endor (Act 4): Bright Tree Village (Fortree), Chief Chirpa's arena, Endor Station (Weather Institute, raided by
# Bossk and the cartel), the treewalk routes 118-121 and 123. Route 121's pier and the Safari Zone gate are
# shuttle pads to JEDHA and the FELUCIA RESERVE (hyperlane hangars, see net_new.csv).
# Chirpa is a male Ewok; Leia (Steven) is female; Bossk (Shelly) is a male Trandoshan who hunts for trophies.
KEEP_REST_MAPS = ("map:fortree-city", "map:route118", "map:route119", "map:route120", "map:route121",
                  "map:route123", "map:scorched-slab", "map:ancient-tomb")
FC = "FortreeCity_"
G = "FortreeCity_Gym_Text_"
WI = "Route119_WeatherInstitute_"
S = "Route121_SafariZoneEntrance_Text_"
P = "COMPANION"


def pl(*olds):
    """Plural fixes: each old snippet has COMPANION where COMPANIONS is meant."""
    return [(o, o.replace("COMPANION", "COMPANIONS")) for o in olds]


FIX = {
# --- Bright Tree Village ---
FC+"Text_SawGiganticPokemonInSky": [("Were you at a volcano or something?", "Were you on MUSTAFAR or something?")],
FC+"Text_TreesGrowByDrinkingRainwater": [("Our BRIGHT TREE exists because\nthere's both water and soil.", "BRIGHT TREE VILLAGE exists because\nthere's both water and soil.")],
FC+"Text_EveryoneHealthyAndLively": [("The CITY consists of homes built on\ntrees.", "The village is made of huts built\nhigh in the trees.")],
FC+"Text_PokemonThatEvolveWhenTraded": pl("There are COMPANION that evolve"),
FC+"Text_CitySign": r"BRIGHT TREE VILLAGE\n“The treetop home of the EWOKS.”$",
FC+"Text_GymSign": r"BRIGHT TREE ARENA\nLEADER: CHIRPA\p“The EWOK chief who rides the\nforest winds.”$",
FC+"DecorationShop_Text_MerchandiseSentToPC": [("your own TERMINAL.", "your own terminal.")],
FC+"House1_Text_TradingMemoriesWithOthers": pl("Trading COMPANION with others…"),
FC+"House2_Text_HiddenPowersArousedByNature": r"People… COMPANIONS…\pTheir hidden powers are awoken by\nliving close to the Force…$",
FC+"House2_Text_CoinInWhichHand": [("I hold a coin in my hand.", "I hold a credit chip in my hand.")],
FC+"House2_Text_CorrectTryAgainWhichHand": [("palmed the coin?", "palmed the chip?")],
FC+"House2_Text_CorrectTryAgainWhichHand2": [("palmed the coin?", "palmed the chip?")],
FC+"House2_Text_YourHiddenPowerHasAwoken": pl("power of your COMPANION."),
FC+"House3_Text_MetStevenHadAmazingPokemon": r"While speaking about DATAPADS,\nI remembered something.\pI met this TRAINER, LEIA, when\nI was searching for rare crystals.\pHoo, boy, she had some amazing\nCOMPANIONS with her.\pThey weren't just rare, they were\ntrained to terrifying extremes!\pShe might even be stronger than the\nARENA LEADER in this village…$",
FC+"House4_Text_BringsWorldCloserTogether": [("By being together with COMPANION,", "By being together with COMPANIONS,"), ("And that brings the world closer\ntogether.", "And that brings the galaxy closer\ntogether.")],
FC+"House5_Text_TreeHousesAreGreat": [("The tree houses of BRIGHT TREE are great!", "The tree huts of BRIGHT TREE are great!"), ("number one town for\nliving", "number one village for\nliving")],
FC+"House5_Text_AdaptedToNature": pl("COMPANION and people have"),
FC+"Mart_Text_RareCandyMakesMonGrow": [("makes a COMPANIONS grow", "makes a COMPANION grow")],
FC+"PokemonCenter_1F_Text_GoToSafariZone": [("Go to the FELUCIA RESERVE.", "Fly to the FELUCIA RESERVE.")],
# --- Chirpa's arena ---
G+"GymGuideAdvice": r"Yo, how's it going, ILUM-bound\n{PLAYER}?\pBRIGHT TREE ARENA LEADER CHIRPA is\na master of FLYING-type COMPANIONS.\pHe's waiting at the back of this ARENA,\nbehind the rotating doors.\pHe's waiting for new challengers\nwho are trying to take wing!\pOkay, go for it!$",
G+"FlintPostBattle": r"CHIEF CHIRPA is wise and strong.\nHe's the ultimate LEADER!\pYub nub!$",
G+"AshleyPostBattle": [("the people of\nBRIGHT TREE can live without fear.", "the EWOKS of\nBRIGHT TREE can live without fear.")],
G+"HumbertoIntro": r"When CHIRPA takes to battle, his face\nshines with fierce determination…\pI'm not letting you witness that\nproud sight!$",
G+"WinonaIntro": r"I am CHIRPA. I am the chief of\nBRIGHT TREE VILLAGE and its ARENA.\pI have become one with BIRD COMPANIONS\nand have glided over the forest…\pHowever grueling the battle, we have\ntriumphed with grace…\pWitness the elegant flight of\nmy BIRD COMPANIONS and I!$",
G+"WinonaDefeat": pl("command COMPANION with more grace"),
G+"WinonaPostBattle": pl("devoted to BIRD COMPANION."),
G+"WinonaPreRematch": r"CHIRPA: We EWOKS can never escape\ngravity's pull on the ground.\pBut by striving for excellence,\nwe have the power to soar!\pYou have passed the TRIALS\nOF ILUM.\pPlease, allow me to see your power\nat full flight!$",
G+"WinonaRematchNeedTwoMons": r"CHIRPA: We EWOKS can never escape\ngravity's pull on the ground.\pBut by striving for excellence,\nwe have the power to soar!\pYou have passed the TRIALS\nOF ILUM.\pPlease, allow me to see your power\nat full flight!\pOh, no… Do you have but one\nCOMPANION with you?\pPlease return with two COMPANIONS\nat the very least.$",
G+"JaredIntro": [],
# --- Route 118 / 119 ---
"Route118_Text_StevenQuestions": [("There are many, many kinds of COMPANIONS\nin this wide world of ours.", "There are so many kinds of COMPANIONS\nin this wide galaxy of ours."), ("We met in the cave near KACHIRHO.", "We met in the SHADOWLANDS.")],
"Route118_Text_CanCrossRiversWithSurf": [("cross rivers and the sea if you have", "cross rivers and lakes if you have"), ("\pCOMPANION can be counted on to do so\nmuch!", "\pCOMPANIONS can be counted on to do so\nmuch!")],
"Route118_Text_RouteSignMauville": r"ROUTE 118\n{LEFT_ARROW} HANGAR TO TATOOINE$",
"Route118_Text_RosePostBattle": r"Flowers, COMPANIONS…\nI love whatever smells nice.\pStinky things…\nI'll pass.$",
"Route118_Text_PerryPostBattle": pl("You've got great COMPANION."),
"Route118_Text_BarnyPostBattle": pl("by training COMPANION\nwhile"),
"Route118_Text_WadeIntro": pl("are COMPANION and heart"),
"Route118_Text_RosePostRematch": pl("properly,\nCOMPANION will be"),
"Route119_Text_BrendanIntro": pl("you've been looking for COMPANION?"),
"Route119_Text_BrendanIllGiveYouThis": pl("to search for COMPANION anywhere."),
"Route119_Text_MayExplainFly": [("You should FLY home and visit\nMOS PELGO for a change.", "You should FLY home to\nMOS PELGO for a change.")],
"Route119_Text_StayAwayFromWeatherInstitute": r"We're standing lookout here.\pHey, you! Stay away from ENDOR\nSTATION. It's not safe.$",
"Route119_Text_TallGrassSnaresBikeTires": r"Tch…\nIt's a no-go…\pThe ferns snag a BIKE's repulsors.\nThere's no way you can ride here.$",
"Route119_Text_CanYourMonMakeSecretBase": [("on a big pile of grass", "on a big pile of ferns")],
"Route119_Text_JacksonRematchIntro": pl("being together with COMPANION."),
"Route119_Text_JacksonPostRematch": pl("Believe in your COMPANION."),
"Route119_Text_CatherineRematchIntro": pl("journey with COMPANION\ngoing?"),
"Route119_Text_CatherinePostRematch": r"In the same way that you, as a TRAINER,\nrely on your COMPANIONS, your COMPANIONS\lrely on you.$",
"Route119_Text_PhilIntro": pl("my BIRD COMPANION!"),
"Route119_Text_HideoPostBattle": r"To hide a tree, use a forest!\nTo hide a COMPANION, use COMPANIONS!\pThere is no deep, hidden meaning\nto that.$",
"Route119_House_Text_RumorAboutCaveOfOrigin": [("I heard about a cave called the CAVE\nOF EVIL.", "I heard about a place called the\nCAVE OF EVIL.")],
# --- Endor Station (cartel raid, Bossk) ---
WI+"1F_Text_Grunt1Intro": r"JABBA got interested in the\nresearch they have going here,\lso he sent us out.\pYou quit meddling!$",
WI+"1F_Text_Grunt1PostBattle": r"The mighty JABBA knows everything.\pBut I'm just a THUG. What would I know\nabout what he's thinking?$",
WI+"1F_Text_WowYoureStrong": [],
WI+"1F_Text_ProfStudyingRain": [("The PROFESSOR loves rain.", "The PROFESSOR loves rain.")],
WI+"1F_Text_NoticingAbnormalWeather": [("On the 2nd floor of the INSTITUTE,", "On the 2nd floor of the STATION,")],
WI+"1F_Text_WhatWereAquasUpTo": [("what on\nearth the AQUAS were up to.", "what in the\ngalaxy the CARTEL was up to.")],
WI+"2F_Text_Grunt2Intro": [("The INSTITUTE created a type of", "The STATION built a type of"), ("We're here to take them!", "We're here to take it!")],
WI+"2F_Text_Grunt2PostBattle": [("then we of\lTHE CARTEL definitely need it!", "then we of\lthe CARTEL definitely need it!")],
WI+"2F_Text_Grunt3Intro": r"We're the CARTEL!\nWe show up wherever anything rare\lis found!$",
WI+"2F_Text_Grunt3PostBattle": [("what we of\nTHE CARTEL are working towards!", "what we of\nthe CARTEL are working towards!")],
WI+"2F_Text_ShellyIntro": r"Hssssss!\pYou're going to meddle in the CARTEL's\naffairs?\pYou're either absolutely fearless,\nsimply ignorant, or both!\pBOSSK has hunted bigger prey.\nYou'll make a fine trophy, kiddy!$",
WI+"2F_Text_ShellyDefeat": r"Hssss!\nYou're disgustingly strong!$",
WI+"2F_Text_ShellyPostBattle": r"It's bad enough to have the EMPIRE\nblunder about, but now there's you!\pWhat makes you want to sniff around\nin our business, anyway?$",
WI+"2F_Text_TeamMagmaJustPassedBy": r"We have a situation here!\pAn EMPIRE shuttle just flew past\nENDOR STATION.\pIt appears to be headed for the\nJEDHA TEMPLE!$",
WI+"2F_Text_WeHaveToHurryToMtPyre": r"What?!\pWe can't waste any more time here!\nWe have to hurry to JEDHA, too!\pHssssss!\nEMPIRE, just you wait!$",
WI+"2F_Text_PokemonChangesWithWeather": [("There're plenty of them in the\nINSTITUTE--go ahead and take it.", "There're plenty of them at the\nSTATION--go ahead and take it.")],
"Route119_Text_BrendanExplainFly": [("But you need the BRIGHT TREE ARENA SHARD \nto do that.", "But you need the ARENA SHARD from\nBRIGHT TREE to do that.")],
"Route119_Text_ScottWayToGoBeSeeingYou": [("I expect that you'll do well at the ARENA.", "I expect you'll do well at the ARENA.")],
FC+"Text_UsedDevonScopePokemonFled": [("An invisible COMPANION became completely\nvisible!", "An invisible COMPANION became fully\nvisible!")],
"Route120_Text_StevenUsedDevonScope": [("An invisible COMPANION became completely\nvisible!", "An invisible COMPANION became fully\nvisible!")],
# --- Route 120 (Leia and the ORGANA SCOPE) ---
"Route120_Text_StevenGreeting": [("are your COMPANION ready for\nbattle?", "are your COMPANIONS ready\nfor battle?")],
"Route120_Text_StevenReadyForBattle": pl("are your COMPANION\nready"),
"Route120_Text_StevenGiveDevonScope": [("since I first met you in KACHIRHO.", "since I first met you on KASHYYYK."), ("concealed COMPANION.", "concealed COMPANIONS.")],
"Route120_Text_StevenGoodbye": pl("I enjoy seeing COMPANION and TRAINERS"),
"Route120_Text_LorenzoIntro": pl("I'll check your COMPANION and see if"),
"Route120_Text_LorenzoDefeat": pl("With COMPANION that strong"),
"Route120_Text_JennaPostBattle": pl("I always run with my COMPANION."),
"Route120_Text_JeffreyPostRematch": pl("For my precious BUG COMPANION…"),
"Route120_Text_ClarissaDefeat": [],
"Route120_Text_ClarissaPostBattle": pl("for my COMPANION.\lSo I shield"),
"Route120_Text_KeigoIntro": [("I will adopt the movements of COMPANION\nand create new ninja techniques.", "I will copy the moves of COMPANIONS\nand create new ninja techniques.")],
"Route120_Text_CalliePostBattle": [("I wonder… Should I evolve my COMPANION?", "Should I evolve my COMPANIONS?")],
"Route120_Text_LeonelPostBattle": pl("with your favorite COMPANION."),
"Route120_Text_BerriesExpressionOfLoveIsntIt": [("FRUIT grow by soaking up sunlight.", "FRUIT grows by soaking up sunlight."), ("by watering\nthem regularly.", "by watering\nit regularly.")],
# --- Route 121 (shuttle pads to JEDHA and FELUCIA) ---
"Route121_Text_OkayMoveOutToMtPyre": r"Okay!\nWe're to fly out to JEDHA!$",
"Route121_Text_AheadLoomsMtPyre": r"Shuttles from this pad fly to JEDHA…\pIts TEMPLE is a monument to the\nspirits of departed COMPANIONS…$",
"Route121_Text_MtPyrePierSign": r"SHUTTLE PAD: JEDHA TEMPLE\p…The sign is old and worn out.\nThe words are barely legible…$",
"Route121_Text_SafariZoneSign": r"“Filled with rare COMPANIONS!”\nSHUTTLE TO THE FELUCIA RESERVE$",
"Route121_Text_VanessaPostBattle": pl("My COMPANION should have no problem"),
"Route121_Text_WalterIntro": r"With my COMPANIONS, I have traveled\nto the galaxy's four corners.\pYou might say I have some confidence\nin my abilities.$",
"Route121_Text_WalterRematchIntro": r"With my COMPANIONS, I have traveled\nto the galaxy's four corners.\pYou might say I have some confidence\nin my abilities.$",
"Route121_Text_WalterPostBattle": r"I would like to cross the galaxy once\nagain with my COMPANIONS.$",
"Route121_Text_WalterPostRematch": [("Your COMPANION and you…", "Your COMPANIONS and you…"), ("even overseas.", "even off-world.")],
"Route121_Text_JoyPostBattle": [("train with KATE,", "train with KESS,")],
"Route121_Text_JessicaPostBattle": [("at\nthe SAFARI.", "at\nthe RESERVE.")],
"Route121_Text_JessicaPostRematch": [("at\nthe SAFARI.", "at\nthe RESERVE.")],
"Route121_Text_MylesIntro": pl("other people's COMPANION!"),
"Route121_Text_MylesPostBattle": pl("They're great, your COMPANION!"),
"Route121_Text_CalePostBattle": [("It's up the road from here.", "It's a short flight from here.")],
S+"WelcomeToSafariZone": r"Welcome to the FELUCIA RESERVE\nSHUTTLE!\pOn FELUCIA, you may see many kinds\nof COMPANIONS rarely seen out here.\pAnd, you'll see them in their wild,\nuntamed state in natural habitats.\pWhat's more, the gates are open\nto COMPANION TRAINERS.\pYou're encouraged to catch COMPANIONS\nfor keeps!\pCome in and enjoy the FELUCIA RESERVE!$",
S+"FirstTimeInfo": [("When you enter the FELUCIA RESERVE, you\nstart", "When you enter the RESERVE, you\nstart"), ("catching COMPANION.", "catching COMPANIONS.")],
S+"WouldYouLikeToPlay": [("All you can catch for just ¥500!", "All you can catch for 500 credits!")],
S+"ThatWillBe500Please": r"That will be 500 credits, please.$",
S+"PCIsFull": r"Excuse me!\nYour storage BOX is full.$",
# --- Route 123 (Fruit Master) ---
"Route123_Text_LoveGrassMonsHaveAny": r"I love GRASS-type COMPANIONS!\pDo you have any GRASS-type COMPANIONS?$",
"Route123_Text_CheckTreesWithMyGrassMon": pl("GRASS-type\nCOMPANION."),
"Route123_Text_RouteSignMtPyre": r"{UP_ARROW} SHUTTLE PAD: JEDHA TEMPLE\n“Forbidden to the faint of heart.”$",
"Route123_Text_JackiIntro": pl("if your COMPANION\ndevelop"),
"Route123_Text_KindraIntro": r"JEDHA TEMPLE…\nWhere the spirits of COMPANIONS sleep…\lWill your COMPANIONS sleep?$",
"Route123_Text_KindraPostBattle": pl("Where the spirits of COMPANION sleep…"),
"Route123_Text_AlbertoPostBattle": [],
"Route123_Text_EdIntro": pl("I let my COMPANION battle each other."),
"Route123_Text_EdDefeat": pl("I kind of like your COMPANION."),
"Route123_BerryMastersHouse_Text_VisitPrettyPetalFlowerShop": [("flower shop near BESTINE.", "flower shop near BESTINE\lon TATOOINE.")],
"Route123_BerryMastersHouse_Text_JoyNeverGoesOutOfMyLife": [],
# --- overflow fixes (trainer lines) ---
"Kecleon_Text_UseDevonScopeMonAttacked": r"{PLAYER} used the ORGANA SCOPE.\pAn invisible COMPANION became fully\nvisible!\pThe startled COMPANION attacked!$",
"Route121_Text_MarcelIntro": r"My COMPANIONS have never lost!\nOn their next win, I'm entering them\lin SHOWCASES.$",
"Route123_Text_AlbertoDefeat": r"Even in defeat, BIRD COMPANIONS\nare cool!$",
}
NOTES = {
WI+"2F_Text_ShellyIntro": "Bossk (Shelly): Trandoshan trophy hunter, hisses",
"Route121_Text_AheadLoomsMtPyre": "Route 121's pier is a shuttle pad to Jedha (net:hangar rows)",
S+"WelcomeToSafariZone": "Safari Zone entrance = shuttle office to the Felucia Reserve",
G+"WinonaIntro": "Chief Chirpa is male; arena is in his village",
}

REFLOW = True
