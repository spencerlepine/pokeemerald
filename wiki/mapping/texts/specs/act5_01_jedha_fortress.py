# Jedha (Mt. Pyre -> JEDHA TEMPLE, Route 122) and Fortress Vader (Magma Hideout, on Mustafar).
# Vader takes the BLUE KYBER at the temple first; Jabba takes the RED KYBER. The elders at the summit are the
# Guardians of the Whills. Imperial grunts wear armor (not hoods) and say LORD VADER.
KEEP_REST_MAPS = ("map:mt-pyre", "map:route122", "map:magma-hideout")
MH = "MagmaHideout_"
MP = "MtPyre_"
SU = "MtPyre_Summit_Text_"


def pl(*olds):
    return [(o, o.replace("COMPANION", "COMPANIONS")) for o in olds]


FIX = {
# --- Fortress Vader ---
MH+"1F_Text_Grunt1Intro": r"When the EMPIRE has roll call, we get\nimportant guard posts in the order\lthat we line up.\pThat's why I'm stuck off in this corner.\nI'm always late to roll call!$",
MH+"1F_Text_Grunt2Intro": [("Our leader told us to dig into", "LORD VADER told us to dig into")],
MH+"2F_1R_Text_Grunt14Intro": r"What, what, what?\pOnly EMPIRE troops are supposed\nto be in here!\pBut you're not wearing the EMPIRE's\narmor…\pYou rouse my suspicion!\nBattle with me!$",
MH+"2F_1R_Text_Grunt14Defeat": r"Aiyiyi…\nMy pride as a STORMTROOPER…$",
MH+"2F_1R_Text_Grunt14PostBattle": r"If you suffer from chills, you should\njoin the EMPIRE. It's warm here.$",
MH+"2F_2R_Text_Grunt15PostBattle": [("All that's left is for our leader to…", "All that's left is for LORD VADER to…")],
MH+"2F_2R_Text_Grunt6Intro": r"I can't stand heat. Maybe I should've\njoined the CARTEL instead…$",
MH+"2F_2R_Text_Grunt6Defeat": r"Yeah, I really may not be right for\nthe EMPIRE…$",
MH+"2F_2R_Text_Grunt6PostBattle": r"Don't you miss fresh air, being\nin a place like this?$",
MH+"2F_2R_Text_Grunt7Intro": [("Or is it GROU…", "Or is it GREAT…")],
MH+"2F_2R_Text_Grunt7PostBattle": [("THE EMPIRE's goal is about to be\nreached!", "The EMPIRE's goal is about to be\nreached!")],
MH+"3F_1R_Text_Grunt9PostBattle": r"Do you think it's odd that we wear\nfull armor in a lava-filled fortress?$",
MH+"3F_1R_Text_Grunt16Intro": r"We serve LORD VADER and his vision\nof order.\pI don't care if you're with the CARTEL\nor if you're just some kid passing by.\pNo one interferes with us and gets\naway with it!$",
MH+"3F_1R_Text_Grunt16PostBattle": r"Listen to me.\nThe EMPIRE is right!\pDon't listen to the CARTEL.\nDon't believe their lies!$",
MH+"3F_2R_Text_Grunt10Intro": r"I follow every order LORD VADER\ngives. But you know what?\pDoing stuff like digging up a super-\nancient COMPANION and ripping off\lsomeone's METEORITE…\pI think we're going a little too far.\nWhat do you think?$",
MH+"3F_2R_Text_Grunt10PostBattle": r"You know, losing to you cleared my mind.\pThe next time I see LORD VADER…\nWell… Maybe I'll keep quiet.$",
MH+"4F_Text_Grunt12PostBattle": r"LORD VADER!\nAn intruder is headed your way!$",
MH+"4F_Text_TabithaIntro": [("VADER went to GREATKRAYT just seconds\nago!", "LORD VADER went to GREATKRAYT just\nseconds ago!")],
MH+"4F_Text_TabithaPostBattle": [("VADER should have awakened GREATKRAYT…", "LORD VADER will have awakened\nGREATKRAYT…")],
MH+"4F_Text_MaxieOhItWasYou": r"VADER: So. It was you.\pI have sensed you poking around\nuninvited here and there…\pI see it now.\nYou have used the Force against me!$",
MH+"4F_Text_MaxieDefeat": r"The Force is strong with you…\nStronger than I had foreseen.$",
MH+"4F_Text_MaxieImGoingAfterGroudon": r"VADER: There has to be some reason\nwhy GREATKRAYT fled…\pThat's what you're trying to say,\nisn't it?\p… … … … … …\n… … … … … …\pYou think I did not know that?\pWith GREATKRAYT gone, I have no\nfurther need for this volcano.\pI am going after GREATKRAYT.\nThis is where we part!$",
# --- Jedha Temple ---
MP+"1F_Text_TakeThisForYourOwnGood": [("of JEDHA TEMPLE…", "of the JEDHA TEMPLE…")],
MP+"1F_Text_ComeToPayRespects": r"Did you come to pay your respects\nto the spirits of departed COMPANIONS?\pYou must care for your COMPANIONS a lot.$",
MP+"2F_Text_MarkIntro": pl("Are you searching for COMPANION?"),
MP+"2F_Text_LeahPostBattle": [("It is my duty to protect this\nmountain…", "It is my duty to protect this\ntemple…")],
MP+"3F_Text_WilliamIntro": [("The rich atmosphere of the mountain\nhas elevated", "The Force in this holy place\nhas elevated")],
MP+"3F_Text_GabriellePostBattle": [("COMPANION no longer of this world.", "COMPANIONS no longer of this world."), ("And the COMPANION that you will meet", "And the COMPANIONS you will meet")],
MP+"3F_Text_GabriellePostRematch": [("COMPANION no longer of this world.", "COMPANIONS no longer of this world."), ("And the COMPANION that you will meet", "And the COMPANIONS you will meet")],
MP+"3F_Text_GabrielleRegister": pl("I would like to see your COMPANION\nwhen"),
MP+"6F_Text_ValeriePostBattle": pl("of COMPANION in fitful sleep"),
MP+"6F_Text_ValeriePostRematch": pl("The COMPANION at rest here…"),
SU+"Grunt1Intro": r"No! Those EMPIRE goons got\nhere ahead of us!\pWe can't fall behind!$",
SU+"Grunt1Defeat": r"I thought you were one of the\nSTORMTROOPERS coming back…$",
SU+"Grunt2Intro": r"Hah!\nToo bad for you!\pIf you came earlier, you only would've\nhad to battle the wimpy EMPIRE.\pBut since you arrived now, you have\nto take on us toughies!$",
SU+"Grunt2Defeat": r"Urgh… I should've let you take on\nthe EMPIRE first…$",
SU+"Grunt3Intro": [("You don't belong to either TEAM,", "You're not EMPIRE or CARTEL,")],
SU+"Grunt3Defeat": r"If you're going to mess with anyone,\nlet it be the EMPIRE…$",
SU+"Grunt3PostBattle": r"Heh, it doesn't matter!\nWe bought ourselves some time!\pThe mighty JABBA should have snatched\nwhat he was after!$",
SU+"Grunt4Intro": r"Oh, I know!\nYou tried to join the EMPIRE,\lbut they wouldn't have you!\pWell, don't think that we'll let you\njoin the CARTEL!$",
SU+"Grunt4Defeat": r"If you want to join the CARTEL that\nbadly, we can consider it…$",
SU+"Grunt4PostBattle": r"We have a great thing going with\nus thugs and the mighty JABBA.$",
SU+"ArchieWeGotTheOrbLetsGo": r"JABBA: The EMPIRE's VADER got ahead\nof us, but we also got what we wanted.\pThe RED KYBER kept at JEDHA TEMPLE…\nI, JABBA, now have it in my possession!\pHo ho ho… Now every dry world will\nbecome a swamp fit for a HUTT!\pCome, my thugs!\nWe're pulling out!$",
SU+"BothOrbsTakenMagmaLeftThis": [("The BLUE KYBER and RED KYBER must never\nbe separated.", "The BLUE and RED KYBER must never\nbe separated."), ("the two ORBS?", "the two crystals?"), ("Oh, yes. Was it THE EMPIRE who came", "Oh, yes. Was it the EMPIRE who came")],
SU+"GroudonKyogreAwakened": [("You say that both GREATKRAYT and SANDO\nhave been awakened?", "You say GREATKRAYT and SANDO\nhave both been awakened?"), ("of the ORBS still exists.", "of the crystals still exists."), ("exactly, the ORBS belong to.", "exactly, the crystals belong to.")],
SU+"ThoseTwoMenReturnedOrbs": [("The two men who took the ORBS came", "The two who took the crystals came")],
SU+"SuperAncientPokemonTaughtUs": r"The embodiments of the land, sea,\nand the stars…\pThat is said to be the identities of\nthe super-ancient COMPANIONS…\pIn the same way that we humans and\nCOMPANIONS have life, every world, too,\lis alive…\pThe super-ancient COMPANIONS have\ntaught us that…$",
SU+"WillYouHearOutMyTale": [("JEDHA TEMPLE is where we calm the spirits\nof COMPANIONS that have passed on…", "Here at the TEMPLE we calm the\nspirits of departed COMPANIONS…"), ("This is a high place where one can\nsee all of OUTER RIM…", "This is a high place where one can\nsee the stars of the OUTER RIM…")],
SU+"GroudonKyogreTale": r"It happened long, long ago…\pThe worlds were wracked by a ferocious\nclash between the COMPANION of the land\land the COMPANION of the sea…\pThe COMPANION of the land raised\nmountains and dried up the seas…\pThe COMPANION of the sea raised huge\nwaves and drowned the lands…\pTheir fierce duel raged without end.\pThe worlds were engulfed in massive\ninfernos and vicious storms.\pThe BLUE and RED KYBER brought\nan end to the calamity.\pLight poured from the two crystals and\ncalmed the enraged adversaries.\pThe pair, made docile, dove deep into\nthe sea where eventually they\ldisappeared…$",
SU+"HoennTrioTale": r"It happened long, long ago…\pThe worlds were wracked by a ferocious\nclash between the COMPANION of the land\land the COMPANION of the sea…\pThe COMPANION of the land raised\nmountains and dried up the seas…\pThe COMPANION of the sea raised huge\nwaves and drowned the lands…\pTheir fierce duel raged without end.\pThe worlds were engulfed in massive\nfires and vicious storms.\pIt was then that the COMPANION of\nthe stars descended from the void.\pThe COMPANION, shining a vivid green,\ncalmed the two enraged COMPANIONS.\pThen, its duty done, the green COMPANION\nflew off into the starry black…$",
SU+"HearTheNewLegendOfHoenn": [("And the crisis that just ended in\nDAGOBAH rewrote a legend…", "And the crisis that just ended on\nDAGOBAH rewrote a legend…")],
}
NOTES = {
SU+"ArchieWeGotTheOrbLetsGo": "Jabba's swamp motive (bible/STORY.md)",
MH+"4F_Text_MaxieDefeat": "Vader's second loss: he senses the player's Force strength",
SU+"HoennTrioTale": "EXOGORTH (Rayquaza) is the creature of the stars",
}

REFLOW = True
