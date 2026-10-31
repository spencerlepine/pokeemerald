# Ilum (Act 7): Ever Grande -> ILUM (the ice world), Victory Road -> CRYSTAL CAVES, the Pokemon League ->
# ILUM TEMPLE. The Four Trials are Force visions: MAUL (fear), QUI-GON's spirit (loss), KI-ADI on frozen Mygeeto
# (betrayal), ANAKIN (the fallen hero). Obi-Wan (Wallace) is the real Champion. Luke (Wally) is the last rival.
KEEP_REST_MAPS = ("map:ever-grande-city", "map:victory-road")
E = "EverGrandeCity_"
V = "VictoryRoad_"


def pl(*olds):
    return [(o, o.replace("COMPANION", "COMPANIONS")) for o in olds]


FIX = {
E+"Text_CitySign": r"ILUM\p“The ice world where the kyber\ncrystals grow.”$",
E+"Text_EnteringPokemonLeague": r"ENTERING THE ILUM TEMPLE\nCENTER GATE$",
# --- Trial of Fear: MAUL ---
E+"SidneysRoom_Text_IntroSpeech": r"MAUL: …\pSo, the next one comes.\nI am the TRIAL OF FEAR.\pI am what you dread in the dark.\nShow me that you do not run.\pAt last we will have a battle that\ncan only be staged here, in the\lILUM TEMPLE!$",
E+"SidneysRoom_Text_Defeat": r"…You did not run.\nThe vision fades.$",
E+"SidneysRoom_Text_PostBattleSpeech": r"Fear leads to anger.\nYou let it pass through you.\pYou have what it takes to go far.\nGo on to the next TRIAL.$",
# --- Trial of Loss: QUI-GON ---
E+"PhoebesRoom_Text_IntroSpeech": r"QUI-GON: Hello, young one.\pI am the TRIAL OF LOSS.\nI trained my spirit at the JEDHA\lTEMPLE, and it outlived me.\pThere, I learned to commune with\nSPIRIT-type COMPANIONS.\pThe bond I share with my COMPANIONS\nreaches past death itself.\pSo, come. See if you can even\ntouch my COMPANIONS!$",
E+"PhoebesRoom_Text_Defeat": r"Ah.\nWell done, young one.$",
E+"PhoebesRoom_Text_PostBattleSpeech": r"There's a deep bond between you\nand your COMPANIONS, too.\pNo one is ever truly gone.\nRemember that when you lose someone.\pI'd like to see how far your bond\nwill carry you.\pGo ahead, move on to the next TRIAL.$",
# --- Trial of Betrayal: KI-ADI ---
E+"GlaciasRoom_Text_IntroSpeech": r"I am KI-ADI, the TRIAL OF BETRAYAL.\pI fell on the frozen world MYGEETO,\nwhen my own troops turned on me.\pThe ice here holds that memory.\pAll I have seen since are weak\nTRAINERS and their COMPANIONS.\pWhat about you?\pIt would please me to no end if I could\ngo all out against you!$",
E+"GlaciasRoom_Text_Defeat": pl("You and your COMPANION…"),
E+"GlaciasRoom_Text_PostBattleSpeech": r"Your COMPANIONS will never betray you.\nDo not betray them.\pAdvance to the next room.\nThere, face the hardest TRIAL.$",
# --- Trial of the Fallen Hero: ANAKIN ---
E+"DrakesRoom_Text_IntroSpeech": r"I am ANAKIN, the last of the FOUR\nTRIALS, the DRAGON master!\pOnce I was a hero.\nThen I chose power over everything.\pIn their natural state, COMPANIONS are\nwild living things. They are free.\pAt times, they hinder us.\nAt times, they help us.\pFor us to battle with COMPANIONS as\npartners, do you know what it takes?\pIf you don't, then you will never\nprevail over me!$",
E+"DrakesRoom_Text_Defeat": r"Superb.\nYou are stronger than I was.$",
E+"DrakesRoom_Text_PostBattleSpeech": r"You deserve every credit for coming\nthis far as a TRAINER of COMPANIONS.\pYou do seem to know what is needed.\pYes, what a TRAINER needs is a\nvirtuous heart. I forgot that.\pCOMPANIONS touch the good hearts of\nTRAINERS and learn right from wrong.\pThey touch the good hearts of\nTRAINERS and grow strong.\pGo! Go onwards!\nOBI-WAN is waiting!$",
# --- Obi-Wan ---
E+"ChampionsRoom_Text_IntroSpeech": r"OBI-WAN: Hello there, {PLAYER}{KUN}.\pThat incident on DAGOBAH…\nThat was superb work, putting an end\lto that crisis.\pOh, forgive me.\pIt wouldn't be fair to say that you\nalone ended the crisis.\pYou overcame it by working as one\nwith your COMPANIONS.\pWe TRAINERS raise COMPANIONS by giving\nthem items and by teaching them new\ltechniques for battle.\pBut we ourselves also learn many\nthings from COMPANIONS.\pAnd this is where your achievements\nare put to the test.\pNow!\pWho fights in truest harmony with\ntheir COMPANIONS in the OUTER RIM?\pShow me right here and now!$",
E+"ChampionsRoom_Text_Defeat": r"I, the CHAMPION, fall in defeat…\pThat was wonderful work.\nThe Force is with you, truly.\lAnd it was glorious!\pWell done, {PLAYER}{KUN}!\pYou are a truly noble COMPANION\nTRAINER!$",
E+"ChampionsRoom_Text_PostBattleSpeech": r"OBI-WAN: The COMPANIONS you sent into\nbattle…\pAt times they moved like a spring\nbreeze, and at times they struck\llike lightning.\pWith light, yet surefooted, calm,\nyou led your COMPANIONS.\pEven I was moved by your\nmasterful performance!\pYou now stand at the peak\nof the ILUM TEMPLE.\pI now proclaim you to be the new\nCHAMPION of the OUTER RIM…$",
E+"ChampionsRoom_Text_BirchArriveRatePokedex": [("the CHAMPION!", "the ILUM CHAMPION!")],
E+"HallOfFame_Text_HereWeHonorLeagueChampions": r"OBI-WAN: This room…\pThis is where we keep records of\nCOMPANIONS that prevailed through\lharsh battles.\pIt is here that the ILUM CHAMPIONS\nare honored.$",
E+"PokemonCenter_1F_Text_BelieveInYourPokemon": pl("Believe in your COMPANION and give it\nyour very best!"),
E+"PokemonLeague_1F_Text_GoForth": pl("Believe in yourself and your\nCOMPANION,"),
# --- Crystal Caves (Luke) ---
V+"1F_Text_WallyNotGoingToLoseAnymore": r"LUKE: Hi! {PLAYER}!\pI bet you're surprised to see me here!\pI made it all the way here, and it's\nall thanks to you!\p{PLAYER}, losing to you that time\nmade me stronger!\pBut I'm not going to lose anymore!\pI'm going to win! For the COMPANIONS\nwho gave me courage and strength!\pOkay… Here I come!$",
V+"1F_Text_HopeIntro": r"These caves seem to go on forever.\nOnly the strong reach the TEMPLE.$",
V+"1F_Text_QuincyPostBattle": r"Getting through here safely--that's\nthe final test for any TRAINER aiming\lto become the ILUM CHAMPION.\pThe crystals here only glow for\nthose who keep going.$",
V+"B1F_Text_ShannonIntro": pl("the trust of your\lCOMPANION."),
V+"B1F_Text_ShannonPostBattle": pl("trust\ngrows between COMPANION and"),
V+"B1F_Text_MitchellPostBattle": pl("land your COMPANION."),
V+"B2F_Text_OwenPostBattle": [],
}
NOTES = {
E+"SidneysRoom_Text_IntroSpeech": "Four Trials are Force visions (bible/STORY.md); Maul = fear",
E+"ChampionsRoom_Text_IntroSpeech": "Obi-Wan: 'Hello there'",
}

REFLOW = True
