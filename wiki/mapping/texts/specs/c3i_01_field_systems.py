# Shared field systems (C3i part 1): battle messages, Bacta Center nurse, day care, field moves, berry trees,
# the Felucia Reserve, move tutors, the Datapad rating, HOLONET NEWS, hideouts and the event-pass dialogue.
# The PC is a TERMINAL; a POKé BALL is a CAPTURE POD. ¥ stays as the money glyph (Step 5 redraws it as credits).
KEEP_REST_FILES = (
    "src/battle_message.c",
    "data/scripts/field_move_scripts.inc", "data/text/obtain_item.inc", "data/text/pkmn_center_nurse.inc",
    "data/event_scripts.s", "data/scripts/day_care.inc", "data/scripts/berry_tree.inc", "data/text/berries.inc",
    "data/scripts/safari_zone.inc", "data/text/move_tutors.inc", "data/text/pokedex_rating.inc",
    "data/text/pokemon_news.inc", "data/text/lottery_corner.inc", "data/scripts/roulette.inc",
    "data/scripts/profile_man.inc", "data/text/event_ticket_1.inc", "data/scripts/secret_base.inc",
    "data/text/secret_base_trainers.inc", "data/maps/LittlerootTown_BrendansHouse_1F/scripts.inc",
)
REFLOW = True


def pl(*olds):
    return [(o, o.replace("COMPANION", "COMPANIONS")) for o in olds]


FIX = {
# --- battle ---
"sText_TrainerBlockedBall": r"The TRAINER blocked the POD!",
"sText_ItDodgedBall": r"It dodged the thrown POD!\nThis COMPANION can't be caught!",
"sText_PkmnSentToPC": r"{B_OPPONENT_MON1_NAME} was sent to\n{B_PC_CREATOR_NAME} TERMINAL.",
"sText_YouThrowABallNowRight": r"You throw a POD now, right?\nI… I'll do my best!",
"gText_SafariZoneMenu": r"POD{CLEAR_TO 56}{POKEBLOCK}\nGO NEAR{CLEAR_TO 56}RUN",
# --- terminals ---
"gText_PlayerHouseBootPC": r"{PLAYER} booted up the TERMINAL.$",
"SecretBase_Text_BootUpPC": r"{PLAYER} booted up the TERMINAL.$",
"SecretBase_Text_AllDecorationsWillBeReturned": [("returned to your PC.", "returned to your TERMINAL.")],
"gText_TheDecorWasTransferredToThePC": r"The {STR_VAR_2} was transferred\nto the TERMINAL.$",
"gText_PokemonTrainerSchoolEmail": r"There's a message from the TRAINER\nACADEMY.\p… … … … … …\pA COMPANION may learn up to four moves.\pA TRAINER's expertise is tested on the\nmove sets chosen for COMPANIONS.\p… … … … … …$",
# --- toy holoprojectors (were toy TVs) ---
"SecretBase_Text_ToyTV": r"A realistic toy HOLOPROJECTOR. It could\nbe easily mistaken for the real thing.$",
"SecretBase_Text_SeedotTV": r"A toy HOLOPROJECTOR shaped like an\nACORNLET. It looks ready to roll away\lon its own…$",
"SecretBase_Text_SkittyTV": r"A toy HOLOPROJECTOR shaped like a\nLOTHKIT. It looks ready to stroll away…$",
# --- Bacta Center nurse: she takes the whole team ---
"gText_WouldYouLikeToRestYourPkmn": r"Hello, and welcome to\nthe BACTA CENTER.\pWe restore your tired COMPANIONS\nto full health.\pWould you like to rest your COMPANIONS?$",
"gText_IllTakeYourPkmn": r"Okay, I'll take your COMPANIONS\nfor a few seconds.$",
"gText_IllTakeYourPkmn2": r"Okay, I'll take your COMPANIONS\nfor a few seconds.$",
"gText_RestoredPkmnToFullHealth": r"Thank you for waiting.\pWe've restored your COMPANIONS\nto full health.$",
"gText_NoticesGoldCard": [("resting your COMPANION!", "resting your COMPANIONS!")],
# --- day care ---
"Route117_Text_SeeWifeIfYoudLikeMeToRaiseMon": pl("the precious\nCOMPANION of TRAINERS"),
# --- Felucia Reserve ---
"SafariZone_South_Text_Man": [("forgot to bring a BIKE.", "forgot to bring a SPEEDER BIKE.")],
"SafariZone_North_Text_Fisherman": r"I'm on a mission to find WATER\nCOMPANIONS you don't see anywhere else\lin the OUTER RIM.\pDo you have any idea where the lake is?$",
# --- datapad rating (Korr counts them) ---
"gBirchDexRatingText_SoYouveSeenAndCaught": r"Hmhm…\pSo, you've seen {STR_VAR_1} COMPANIONS,\nand you've caught {STR_VAR_2} COMPANIONS…$",
"gBirchDexRatingText_OnANationwideBasis": r"Hmhm…\nAcross the whole galaxy…\pYou've seen {STR_VAR_1} COMPANIONS,\nand you've caught {STR_VAR_2} COMPANIONS…$",
# --- lottery ---
"LilycoveCity_DepartmentStore_1F_Text_LotteryCornerDrawTicket": pl("any of your COMPANION,"),
# --- event passes: Cloud City starliner, Captain Han ---
"EventTicket_Text_ShowOldSeaMap": r"The starliner to MOS EISLEY is…\pI beg your pardon?\nCan we fly to this place on the map?\pI know someone who will help you better.\nPlease wait.$",
"EventTicket_Text_ThatPass": r"The starliner to MOS EISLEY is…\pOh?\nThat PASS…$",
"EventTicket_Text_ShowEonTicket": r"HAN: Hey, kid, are you the one who\nbrought that mighty odd PASS?\pI'll tell you, you're trying to reach a\ntiny rock of an isle way out past\lthe charts.\pNo telling what we'll run into\nonce we get there.\lI've got a bad feeling about this.\pAll aboard!$",
"EventTicket_Text_SouthernIslandSailBack": r"HAN: Kid, there's nothing here to\nsee or do on this forgettable rock.\pWhat say we fly back to CLOUD CITY?$",
}
NOTES = {
"sText_PkmnSentToPC": "PC -> TERMINAL across shared systems",
"EventTicket_Text_ShowEonTicket": "Briney's sea-dog lines -> Captain Han ('bad feeling about this')",
"gText_WouldYouLikeToRestYourPkmn": "the nurse heals the whole team: plural",
}
