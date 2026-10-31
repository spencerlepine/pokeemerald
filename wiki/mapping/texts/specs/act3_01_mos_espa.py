# Mos Espa (Mauville): Watto's arena, Wald's bike shop (SWOOP / SPEEDER BIKE), the Sabacc Den
# (Game Corner, COINS -> CHIPS), Luke's first battle, and the Espa Generator (New Mauville).
KEEP_REST_MAPS = ("map:mauville", "map:new-mauville")
M = "MauvilleCity_"
FIX = {
M+"Text_UncleHesTooPeppy": [("It's because of COMPANION that\nthis boy's got more pep,", "It's because of COMPANIONS that\nthis boy's got more pep,")],
M+"Text_UncleYourePushingIt": [("Since you started living with COMPANION,", "Since you started living with COMPANIONS,"), ("Since you started living with COMPANIONS,\nyou have grown quite a lot stronger.", "Since you started raising COMPANIONS,\nyou have grown quite a lot stronger.")],
M+"Text_ThankYouNotEnoughToBattle": [("It's not enough just to have COMPANION\nand make them battle.", "It's not enough just to have COMPANIONS\nand make them battle.")],
M+"Text_NurseHurtMonBackToHealth": [("it's cool to have COMPANION\nbattles and stuff…", "it's cool to have COMPANION\nbattles and stuff…")],
M+"Text_PokemonCanJumpYouOnBike": [("wild COMPANION could jump you.", "wild COMPANIONS could jump you.")],
M+"Text_CitySign": r"MOS ESPA\n“Home of the BOONTA EVE CLASSIC!”$",
M+"Text_GymSign": [("“The cheerfully electrifying man!”", "“The junk dealer with a spark!”")],
M+"Text_BikeShopSign": r"“Ride the dunes and shake up your\nsoul!”\lWALD'S BIKES$",
M+"Text_RydelVeryGenerous": [("Have you been to WALD'S CYCLES yet?", "Have you been to WALD'S BIKES yet?")],
M+"Text_ExplainTV": r"Hi, do you check out the HoloNet\nat all?\pThey've added a bunch of cool new\nshows recently.\pThe HoloNet is so cool. I've seen my\nfriends on it just out of the blue.\pAnd, sometimes, they even put you on\nwithout telling you.\pI wish I would be on the HoloNet\nsometime.\pThat's why I think you should check\nout HoloNet screens whenever you can.$",
M+"Text_BeenCheckingOutTV": r"Hi, have you been checking out the\nHoloNet?$",
M+"BikeShop_Text_RydelGreeting": [("I'm the owner of this cycle shop.", "I'm the owner of this bike shop.")],
M+"BikeShop_Text_ExplainBikesChooseWhichOne": [("The SWOOP BIKE is for cyclists who want\nto feel the wind with their bodies!", "The SWOOP BIKE is for riders who want\nto feel the wind in their faces!")],
M+"BikeShop_Text_HowToRideMachBike": [("It will speed up once it gets rolling.", "It will speed up once it gets going.")],
M+"BikeShop_Text_SandySlopes": [("small sandy slopes\nthroughout the OUTER RIM region.", "small sandy slopes\nall over the OUTER RIM.")],
M+"BikeShop_Text_Wheelies": r"Press the B Button while riding,\nand the nose of the bike lifts up.\pYou can zip around with the nose\nup using the + Control Pad.\pThis technique is called a wheelie.\pWant to read a different page?$",
M+"GameCorner_Text_WereYouLookingForCoins": [("It's ¥1000 for 50 CHIPS.", "It's 1000 credits for 50 CHIPS.")],
M+"Gym_Text_GymGuideAdvice": [("Hey, how's it going, CHAMPION-\nbound {PLAYER}?", "Hey, how's it going, ILUM-\nbound {PLAYER}?"), ("uses ELECTRIC-type COMPANION.", "uses ELECTRIC-type COMPANIONS."), ("with WATER-type\nCOMPANION, he'll zap them!", "with WATER-type\nCOMPANIONS, he'll zap them!")],
M+"Gym_Text_KirkPostBattle": r"COMPANIONS and rock, it's all about\nheart, whoa-yeah!$",
M+"BikeShop_Text_ExchangedAcroForMach": r"{PLAYER} traded the SPEEDER BIKE\nfor a SWOOP BIKE.$",
M+"BikeShop_Text_ExchangedMachForAcro": r"{PLAYER} traded the SWOOP BIKE\nfor a SPEEDER BIKE.$",
M+"Gym_Text_ShawnPostBattle": [("He was battling even before your\ndaddy was born, that tough coot.", "He was betting on podraces before\nyour daddy was born, that old coot.")],
M+"Gym_Text_VivianPostBattle": r"I've heard that WATTO has run his\njunk shop in MOS ESPA for ages.\pHe was a TRAINER long before we\nbecame TRAINERS.\lHe must know all sorts of things!$",
M+"Gym_Text_AngeloPostBattle": r"MOS ESPA ARENA's WATTO has wings\nthat buzz so fast they hum.\lIt makes me happy!$",
M+"Gym_Text_WattsonIntro": r"I've given up betting on podraces,\nI have. That SKYWALKER boy cost me\leverything.\pAnd so, I put my time into making\ndoor traps in my ARENA.\pOh? Now, what are you doing here?\pWhat's that? You say you've gotten\npast all my rigged doors?\pWahahahah!\nNow, that is amusing!\pThen, I, WATTO, the LEADER of\nMOS ESPA ARENA, shall electrify you!$",
M+"Gym_Text_ExplainDynamoBadgeTakeThis": [("With the SPARK SHARD, COMPANION can\nuse ROCK SMASH out of battle.", "With the SPARK SHARD, COMPANIONS can\nuse ROCK SMASH out of battle."), ("make your COMPANION a little\nbit faster, too.", "make your COMPANIONS a little\nbit faster, too.")],
M+"Gym_Text_WattsonPreRematch": [("You want to battle my COMPANION!", "You want to battle my COMPANIONS!")],
M+"Gym_Text_WattsonRematchNeedTwoMons": [("You want to battle my COMPANION!", "You want to battle my COMPANIONS!")],
M+"House2_Text_BuyHarborMailAtSlateport": [("it'd be easy to cycle to\nMOS EISLEY", "it'd be easy to ride to\nMOS EISLEY")],
M+"Mart_Text_ItemsToTemporarilyElevateStats": [("the stats of COMPANION.", "the stats of COMPANIONS.")],
M+"PokemonCenter_1F_Text_MyDataUpdatedFromRecordCorner": [],
"NewMauville_Inside_Text_GeneratorRadiatingHeat": [("The generator is radiating heat that\ncan be felt even at a distance.", "The ESPA GENERATOR is radiating heat\nthat can be felt even at a distance.")],
}
NOTES = {M+"Gym_Text_WattsonIntro": "Watto lost Anakin (and Shmi) on the Boonta Eve bet; canon nod"}
FIX["MauvilleCity_BikeShop_Text_OhYourBikeIsInPC"] = [("Oh, I get it, you stored it using your TERMINAL.", "Oh, I get it, you stored it using\nyour TERMINAL.")]

REFLOW = True
