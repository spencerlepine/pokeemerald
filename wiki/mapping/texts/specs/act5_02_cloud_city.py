# Bespin: Cloud City (Lilycove) and the Hutt Hideout (Aqua Hideout) in an old TIBANNA mine under the city.
# Cloud City floats over a sea of clouds, so Emerald's "sea" becomes the cloud sea; the AIWHALET (Wailmer) the
# cartel trains in the cove are cloud-swimmers blocking the cloud cars. Boba Fett (Matt) guards the hideout:
# few words, all business. Lilycove's harbor is the STAR TIDAL starliner dock.
KEEP_REST_MAPS = ("map:lilycove-city", "map:aqua-hideout")
L = "LilycoveCity_Text_"
LC = "LilycoveCity_"
AH = "AquaHideout_"


def pl(*olds):
    return [(o, o.replace("COMPANION", "COMPANIONS")) for o in olds]


BOSS_GONE = r"What? What? What do you want with\nthe CARTEL?\pThe mighty JABBA isn't here! {}\p… …\n{}\pWahaha! Do you really think I'd tell\nyou something that crucial?$"
FIX = {
# --- Hutt Hideout ---
AH+"1F_Text_OurBossIsSnatchingSomething": BOSS_GONE.format(r"He's gone\noff to snatch something important!", "Where did he go?"),
AH+"1F_Text_BossWentToJackASubmarine": BOSS_GONE.format(r"\nHe's gone off to jack a submarine!", "Where did he go?"),
AH+"1F_Text_BossIsOnRoute122": BOSS_GONE.format(r"He's on his\nway to the JEDHA TEMPLE!", "Why did he go?"),
AH+"1F_Text_BossIsInSlateportCity": BOSS_GONE.format(r"\nHe's on his way to MOS EISLEY!", "Why did he go?"),
AH+"1F_Text_WhereMightMagmaHideoutBe": r"What? What?\nAre you an EMPIRE spy?\pI hear that the EMPIRE is trying to\nawaken an awesome COMPANION at their\lFORTRESS.\pBut where might their FORTRESS be?$",
AH+"1F_Text_TeamMagmaAtMtChimney": r"What? What?\nAre you an EMPIRE spy?\pI hear that the EMPIRE is after\nan awesome COMPANION at MUSTAFAR PEAK.\pBut what is that COMPANION like?$",
AH+"1F_Text_Grunt1PostBattle": r"I took the loss for the CARTEL,\nbut I did my job…$",
AH+"B1F_Text_Grunt5PostBattle": r"If you scurry too much, other CARTEL\nthugs might get you.$",
AH+"B1F_Text_Grunt7Intro": r"Hey!\nYou there!\pWhich do you think is cooler?\nThe CARTEL's outfits or the EMPIRE's?$",
AH+"B2F_Text_MattIntro": r"BOBA FETT: …\pSo. You got this far.\pThe others were paid to slow you\ndown. I'm paid to stop you.\pNothing personal, kid.$",
AH+"B2F_Text_MattDefeat": r"…Not bad.\nNot bad at all.$",
AH+"B2F_Text_OurBossGotThroughHisPreparations": r"BOBA FETT: You fight well.\pBut while we were busy, JABBA\nfinished his preparations.$",
AH+"B2F_Text_MattPostBattle": r"BOBA FETT: JABBA has gone to some\ncave under the sea.\pIf you want to give chase, search\nthe deep waters past YAVIN 4.\pYou won't find it.\nBut I'll be watching if you do.$",
AH+"B2F_Text_Grunt4PostBattle": r"Mighty JABBA…\nIs this good enough?$",
AH+"B2F_Text_Grunt6PostBattle": [("If I fail to guard it, our BOSS will\nchew me out…", "If I fail to guard it, JABBA will\nfeed me to the RANCOR…")],
AH+"B2F_Text_Grunt8Intro": r"When I joined the CARTEL, the first\nthing I had to learn was how these\lwarp panels connected.$",
# --- Rivals ---
L+"MayShoppingLetsBattle": [("raising COMPANION properly, {PLAYER}{KUN}.", "raising COMPANIONS properly, {PLAYER}{KUN}."), ("me your COMPANION, {PLAYER}{KUN}.", "me your COMPANIONS, {PLAYER}{KUN}.")],
L+"MayBattleMe": pl("check out your COMPANION!"),
L+"MayWontBeBeaten": r"MIRA: The COMPANIONS I raised won't be\nbeaten by yours, {PLAYER}{KUN}!$",
L+"BrendanShoppingLetsBattle": pl("raising COMPANION better?"),
L+"BrendanYouGoingToPokemonLeague": pl("if I trained my COMPANION\na bit more"),
L+"BrendanYouGoingToBattleFrontier": pl("if I train my COMPANION a bit more,"),
# --- Cartel thugs in town ---
L+"MovedLootIntoHideoutToday": [],
L+"ChanceToDoBigThings": r"I'm just a THUG, so I don't know what\nthe mighty JABBA is thinking…\pBut being in the CARTEL, I know I'll get\nthe chance to do big things!\pWh-who are you?!\nI was just talking to myself!$",
L+"DontGoNearCaveInCove": r"Hey, you!\pDon't go near the old mine under\nthe city!\pWhy? You don't need a reason why!\nI'm an adult, so you just listen to me!$",
L+"IfWorldBecomesOurs": r"If this whole wide galaxy becomes ours,\nthe CARTEL's, it will be a happier\lplace for COMPANIONS, too.$",
L+"WailmerLeapOutOfWater": r"There! AIWHALET!\nLeap out of the clouds now!$",
L+"StrangeCaveInCove": r"Have you seen that strange old mine\nin the under-levels of the city?$",
L+"TeamAquaBeenTrainingWailmer": r"The CARTEL's been training their\nAIWHALET by the docks.\pWe PILOTS can't get our cloud cars\nout with them in the way!$",
L+"SomeonePuntedTeamAquaOut": r"Hey, did you know?\pSomeone punted the CARTEL out of\nthe way for us!\pThat got the AIWHALET away from the\ndocks, so our cloud cars can fly again.$",
L+"SomeoneStoleMyPokemon": r"I was taking a relaxing snooze at the\nsky inn to the sound of the wind…\pWhen someone stole my COMPANION!\pWho's the abductor?\nThe CARTEL? Is it the CARTEL?$",
L+"TeamAquaRenovatedCavern": r"Hm, you know of the old TIBANNA mine\nunder the city?\pIt had been abandoned for years,\nbut then that CARTEL lot came\lalong and made their renovations.\pThey call themselves\n“honest businessmen”!\pBut what they do and what they say\ndon't match at all!$",
L+"TeamAquaLotGoneForGood": r"That old mine under the city…\pI didn't notice it right away,\nbut it's completely empty now.\pThat CARTEL lot, they must\nhave gone away for good.$",
# --- Town ---
L+"ContestHallInTown": [("COMPANION will\ncome from all over the country.", "COMPANIONS will\ncome from all over the galaxy.")],
L+"GoingToMoveDeleterForHMs": [("I'm going to teach my COMPANION some new\nmoves", "I'll teach my COMPANIONS some new\nmoves")],
L+"ImFromKanto": r"I came from the CORE WORLDS.\pThe OUTER RIM is beautiful with\nall its wild worlds and nature.\pHunh? Wait a second…\pCould there be rare COMPANIONS that live\nonly in this area?$",
L+"SeaRemainsForeverYoung": r"Even as we grow old and wrinkled,\nthe cloud sea remains forever young\lwith the vivid brilliance of life…\pFwohoho fwohohohoho…$",
L+"SixtyYearsAgoHusbandProposed": r"It was sixty years ago that my husband\nproposed to me here.\lThe clouds remain as beautiful as ever.\pMufufufu mufufufufufu…$",
L+"CitySign": r"CLOUD CITY\p“The city that floats above\nthe clouds.”$",
L+"HarborSignUnderConstruction": r"CLOUD CITY LANDING PLATFORM\p“The starliner STAR TIDAL is under\nconstruction in MOS EISLEY.\p“Service is scheduled to begin\nshortly.”$",
L+"HarborSign": r"CLOUD CITY LANDING PLATFORM\p“Enjoy a delightful cruise on\nthe starliner STAR TIDAL.”$",
L+"HeardTowerCalledSkyPillar": r"I heard there's a tower somewhere out\nin the stars.\pIt's called the ASTEROID SPIRE, I hear.$",
L+"BerrySuitsYou": [("a crisp breeze suits the sea.", "a crisp breeze suits the clouds.")],
L+"PokeblocksSuitPokemon": pl("perfectly suit COMPANION."),
# --- Showcase hall ---
LC+"ContestHall_Text_GiveItBestSmartAppeal": pl("Okay, SMART COMPANION and their"),
LC+"ContestHall_Text_EnteredWrongContest": pl("I entered this tough COMPANION in"),
LC+"ContestHall_Text_RaisedMonToBeSmart": [("young pup's COMPANION.", "young pup's COMPANIONS.")],
LC+"ContestHall_Text_GanderAtAllThosePrettyPokemon": pl("pretty COMPANION!"),
LC+"ContestHall_Text_CantWinOnBeautyAlone": [],
LC+"ContestHall_Text_PokemonLooksLikeYoungerMe": [("spewed the coffee he was drinking.", "spewed the caf he was drinking.")],
LC+"ContestHall_Text_ThatGirlThereIsCutest": pl("judging\nCOMPANION by"),
LC+"ContestHall_Text_BeautyContestStage": r"BEAUTY SHOWCASE STAGE\nBE ALLURED BY BEAUTIFUL COMPANIONS!$",
LC+"ContestHall_Text_CuteContestStage": r"CUTENESS SHOWCASE STAGE\nBE CHARMED BY CUTE COMPANIONS!$",
LC+"ContestHall_Text_SmartContestStage": r"SMARTNESS SHOWCASE STAGE\nBE IMPRESSED BY SMART COMPANIONS!$",
# --- Motel (the developers' in-joke room; the guests book in as FAN PROJECT, owner 2026-11-01) ---
LC+"CoveLilyMotel_1F_Text_GuestsDoubledByMascot": pl("by\nusing COMPANION as"),
LC+"CoveLilyMotel_1F_Text_NoGuestsWithTeamAqua": r"Oh, sorry, sorry!\nI was too involved in the HOLONET!\pSince that CARTEL came to town,\nthe tourists have been staying away.$",
LC+"CoveLilyMotel_1F_Text_CantSeeTheTV": r"Hey, down in front!\nI can't see the HOLONET!$",
LC+"CoveLilyMotel_1F_Text_HeardAquaHideoutBusted": r"Oh, sorry, sorry!\nI was too involved in the HOLONET!\pI heard that someone busted\nthe CARTEL HIDEOUT.\pThanks to that, we just booked\na reservation from a big group.\pIt was a company called… Uh…\nGAME something…$",
LC+"CoveLilyMotel_1F_Text_BetterGetWorkingOnGuestsDinner": [("I was too involved in watching HOLONET.", "I was too involved in the HOLONET."), ("They booked in as GAME FREAK,", "They booked in as FAN PROJECT,")],
LC+"CoveLilyMotel_2F_Text_ImTheGraphicArtist": r"I'm the GRAPHIC ARTIST! Aren't the\nOUTER RIM's COMPANIONS interesting?$",
LC+"CoveLilyMotel_2F_Text_SeaBreezeTicklesHeart": r"The breeze over the clouds tickles my\nheart. It feels wonderful here!$",
LC+"CoveLilyMotel_2F_Text_NeverLeaveWithoutGameBoy": [("my GAME BOY ADVANCE.", "my HOLOGAME.")],
L+"MayGoingBackToLittleroot": [("I've caught a decent group of COMPANIONS,\nand my DATAPAD", "I've caught a good group of COMPANIONS,\nand my DATAPAD")],
LC+"CoveLilyMotel_2F_Text_SnoozingPreferBattles": [("like the ARENAS, SHOWCASES, BATTLE TENT,\lthe whole works!", "like the ARENAS, SHOWCASES, the\lBATTLE TENT, the whole works!")],
LC+"CoveLilyMotel_2F_Text_ContestsDoTakeStrategy": [("Devising SHOWCASE strategies is one way\nof becoming", "SHOWCASE strategy is one way\nof becoming")],
LC+"DepartmentStore_1F_Text_WelcomeToDeptStore": r"Welcome to the CLOUD CITY\nDEPARTMENT STORE.$",
# --- Department store ---
LC+"DepartmentStoreRooftop_Text_SetDatesForClearOutSales": [("I watch HOLONET, but they never show any\ncommercials.", "I watch the HOLONET, but they never\nshow any ads.")],
LC+"DepartmentStore_3F_Text_ItemsBestForTougheningPokemon": pl("For quickly toughening up COMPANION,"),
LC+"DepartmentStore_4F_Text_AttackOrDefenseTM": pl("taught to COMPANION…"),
LC+"DepartmentStore_5F_Text_GettingDollInsteadOfPokemon": pl("raise COMPANION,"),
LC+"DepartmentStore_1F_Text_TicketMatchesPCMon": [("your TERMINAL-boxed", "your stored")],
# --- Starliner landing platform ---
LC+"Harbor_Text_FerryUnavailable": [("You're looking for a ship?", "You're looking for a flight?"), ("the ferry service isn't", "the starliner service isn't")],
LC+"Harbor_Text_MayISeeYourTicket": [("are you here for the ferry?", "are you here for the starliner?")],
LC+"Harbor_Text_NoTicket": [("to board\nthe ferry.", "to board\nthe starliner.")],
LC+"Harbor_Text_SailAnotherTime": r"Please fly with us another time!$",
LC+"Harbor_Text_PleaseBoard": r"Please board the starliner and wait\nfor departure.$",
LC+"Harbor_Text_SailorFerryUnavailable": r"Until they finish building the\nstarliner, we crew have nothing to do…\pI wish they'd get a move on, the folks\nat the SHIPYARD in MOS EISLEY.$",
LC+"Harbor_Text_SailorFerryAvailable": r"The starliner STAR TIDAL is finally\nin service.\pThe SHIPYARD folks in MOS EISLEY\nmust've worked extra hard.\pWell, it's my turn to get busy now!$",
# --- Houses ---
LC+"House4_Text_MysteriesAtBottomOfSea": r"The galaxy's biggest mysteries are\nat the bottom of its seas.\pSomebody said that, but I don't know…$",
LC+"House4_Text_UnderwaterTrenchMossdeepSootopolis": r"There's a deep underwater trench\nnear YAVIN 4 that leads to DAGOBAH.\pThat's what someone told me, anyway.$",
# --- Museum ---
LC+"LilycoveMuseum_1F_Text_WelcomeToLilycoveMuseum": pl("featuring COMPANION."),
LC+"LilycoveMuseum_1F_Text_PaintingOfGrassPokemon": pl("of GRASS COMPANION\nswaying"),
LC+"LilycoveMuseum_1F_Text_MuseumTouristDestination": [("No, great for the OUTER RIM region!", "No, great for the OUTER RIM!")],
LC+"LilycoveMuseum_2F_Text_PleaseObtainPaintingsForExhibit": pl("You must encounter lively COMPANION\n"),
LC+"LilycoveMuseum_2F_Text_ItsPaintingOfPokemon": r"It's a painting of COMPANIONS.$",
LC+"LilycoveMuseum_2F_Text_NewPaintingsSurprisedMe": [("I wish someone would paint my COMPANION\nthis pretty.", "I wish someone would paint my\nCOMPANIONS this pretty.")],
LC+"LilycoveMuseum_2F_Text_ThesePaintingsOfYourPokemon": pl("These paintings are of your COMPANION."),
LC+"MoveDeletersHouse_Text_ICanMakeMonForgetMove": [("I can make COMPANION forget their moves.", "I can make COMPANIONS forget moves.")],
# --- Bacta center, fan club ---
LC+"PokemonCenter_1F_Text_HowManyKindsOfPokemon": r"I wonder how many kinds of COMPANIONS\nthere are in the galaxy.\pIt'd be great to cross the stars and\ntrade COMPANIONS with people far away.$",
LC+"PokemonCenter_1F_Text_HeardAboutRottenScoundrels": pl("who steal COMPANION and rip"),
LC+"PokemonCenter_1F_Text_HaventSeenRottenScoundrels": pl("who steal\nCOMPANION and"),
LC+"PokemonTrainerFanClub_Text_NoOneCanKnockYouButTrainerStronger": pl("caring to\nCOMPANION."),
LC+"PokemonTrainerFanClub_HopeYouCatchTVSpecial": r"There's going to be a HOLONET special\non {STR_VAR_1} very soon.\pI hope you catch it!$",
}
NOTES = {
AH+"B2F_Text_MattIntro": "Boba Fett (Matt): terse bounty hunter, paid by Jabba; never catchable",
L+"TeamAquaRenovatedCavern": "Aqua Hideout = old Tibanna mine under Cloud City",
L+"CitySign": "Cloud City floats above Bespin's cloud sea",
}

REFLOW = True
