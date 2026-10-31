# The rest of the shared systems (C3i part 6): credits, Mauville's storyteller and giddy man, the cable club
# and HOLONET CLUB, battle tents, naming screen, Cloud City's favor/quiz/contest ladies, the fruit blender,
# trick house mechadolls, landmarks, in-game trades, Mystery Gift passes, saves, and stray one-liners.
# The staff credits keep the real names; the title line names this version.
KEEP_REST_FILES = (
    "data/maps/InsideOfTruck/scripts.inc",
    "data/maps/LittlerootTown/scripts.inc",
    "data/maps/LittlerootTown_BrendansHouse_2F/scripts.inc",
    "data/maps/LittlerootTown_MaysHouse_1F/scripts.inc",
    "data/maps/LittlerootTown_ProfessorBirchsLab/scripts.inc",
    "data/maps/Route101/scripts.inc",
    "data/scripts/berry_blender.inc",
    "data/scripts/gift_altering_cave.inc",
    "data/scripts/gift_aurora_ticket.inc",
    "data/scripts/gift_battle_card.inc",
    "data/scripts/gift_mystic_ticket.inc",
    "data/scripts/gift_old_sea_map.inc",
    "data/scripts/gift_pichu.inc",
    "data/scripts/gift_stamp_card.inc",
    "data/scripts/gift_trainer.inc",
    "data/scripts/lilycove_lady.inc",
    "data/scripts/mauville_man.inc",
    "data/scripts/repel.inc",
    "data/scripts/secret_power_tm.inc",
    "data/scripts/shared_secret_base.inc",
    "data/scripts/test_signpost.inc",
    "data/text/abnormal_weather.inc",
    "data/text/battle_tent.inc",
    "data/text/birch_speech.inc",
    "data/text/blend_master.inc",
    "data/text/cable_club.inc",
    "data/text/check_furniture.inc",
    "data/text/event_ticket_2.inc",
    "data/text/mart_clerk.inc",
    "data/text/mauville_man.inc",
    "data/text/pc.inc",
    "data/text/pc_transfer.inc",
    "data/text/questionnaire.inc",
    "data/text/record_mix.inc",
    "data/text/save.inc",
    "data/text/surf.inc",
    "data/text/trick_house_mechadolls.inc",
    "src/battle_main.c",
    "src/battle_records.c",
    "src/berry_blender.c",
    "src/data/trade.h",
    "src/berry_fix_program.c",
    "src/data/credits.h",
    "src/daycare.c",
    "src/dodrio_berry_picking.c",
    "src/easy_chat.c",
    "src/evolution_scene.c",
    "src/field_player_avatar.c",
    "src/landmark.c",
    "src/link.c",
    "src/map_name_popup.c",
    "src/match_call.c",
    "src/menu_specialized.c",
    "src/mystery_event_msg.c",
    "src/mystery_gift_scripts.c",
    "src/naming_screen.c",
    "src/pokedex.c",
    "src/pokemon_storage_system.c",
    "src/pokemon_summary_screen.c",
    "src/pokenav_ribbons_summary.c",
    "src/pokenav_ribbons_list.c",
    "src/pokenav_match_call_gfx.c",
    "src/text_input_strings.c",
    "src/trainer_card.c",
    "src/union_room_chat.c",
)
# REFLOW stays off: several of these are fixed UI windows (credits, naming screen, the fruit fix program)
M = "MauvilleCity_PokemonCenter_1F_Text_"
CC = "CableClub_Text_"
T = "BattleTentLobby_Text_"


def pl(*olds):
    return [(o, o.replace("COMPANION", "COMPANIONS")) for o in olds]


FIX = {
"sCreditsText_PkmnEmeraldVersion": r"EMERALD SW VERSION",
"sCreditsText_JapanBrailleLibrary": [],
# --- Mauville storyteller ---
M+"BikeTradesTitle": r"The Speeder-Loving TRAINER$",
M+"BikeTradesAction": r"Traded bikes$",
M+"BikeTradesStory": r"This is a tale of a TRAINER\nnamed {STR_VAR_3}.\pThis TRAINER swapped bikes\n{STR_VAR_1} times!\p{STR_VAR_3} must love speeders deeply\nand passionately!$",
M+"EggsHatchedStory": [("hatched {STR_VAR_1} COMPANION\nfrom EGGS!", "hatched {STR_VAR_1}\nCOMPANIONS from EGGS!")],
M+"SafariGamesStory": [("went into the FELUCIA RESERVE\n{STR_VAR_1} times!", "went into the FELUCIA\nRESERVE {STR_VAR_1} times!")],
M+"TVWatchedStory": r"This is a tale of a TRAINER\nnamed {STR_VAR_3}.\pThis TRAINER watched the HOLONET\n{STR_VAR_1} times!\p{STR_VAR_3} must love the HOLONET!$",
# --- battle tents ---
"SlateportCity_BattleTentLobby_Text_HoldMonsForSafekeeping": pl("hold your COMPANION for"),
"SlateportCity_BattleTentLobby_Text_ReturnRentalMonsSaveResults": [("I will return your COMPANION in exchange\nfor our rental COMPANION.", "I will return your COMPANIONS\nin exchange for our rental COMPANIONS.")],
"SlateportCity_BattleTentLobby_Text_ReturnMonsExchangeRentals": r"I will return your COMPANIONS\nin exchange for our rental COMPANIONS.$",
"SlateportCity_BattleTentLobby_Text_WonThreeMatchesReturnMons": [("I will return your COMPANION in exchange\nfor our rental COMPANION.", "I will return your COMPANIONS\nin exchange for our rental COMPANIONS.")],
"VerdanturfTown_BattleTentLobby_Text_ExplainNatureRules": [("Another COMPANION may prefer to protect\nitself", "Another COMPANION may prefer to\nprotect itself")],
"VerdanturfTown_BattleTentLobby_Text_ExplainUnderpoweredRules": [("a COMPANION may be unable to effectively\luse", "a COMPANION may be unable to\leffectively use")],
T+"ExplainLevelRules": pl("levels of your COMPANION."),
# --- cable club / HOLONET CLUB ---
CC+"TradeUsingLinkCable": r"Trade COMPANIONS with another player\nusing a COMLINK cable.$",
CC+"YouMayTradeHere": pl("trade your COMPANION here"),
CC+"CantMixWithJapaneseGame": r"Sorry, there is a transmission error.\pYou may not mix records with games\nfrom another region.$",
CC+"ExplainWirelessClubFirstTime": [("battle COMPANION\nwith", "battle COMPANIONS\nwith"), ("I hope you enjoy the Wireless \nCommunication System.", "I hope you enjoy the COMLINK\nNetwork.")],
CC+"ExplainWirelessClub": [("battle COMPANION\nwith", "battle COMPANIONS\nwith"), ("I hope you enjoy the Wireless \nCommunication System.", "I hope you enjoy the COMLINK\nNetwork.")],
"MossdeepCity_GameCorner_1F_Text_OnlyDodrioAllowed": r"KAADULORD FRUIT-PICKING is a game\nthat only KAADULORD may enter.$",
# --- event passes: Captain Han ---
"EventTicket_Text_BrineyLetsSail": [("We'll sail right away, of course!", "We'll fly right away, of course!"), ("Let's find this island on", "Let's find this isle on")],
"EventTicket_Text_OddTicketGetOnBoard": [("ticket?", "PASS?"), ("an island\nthat's far, far away.", "an isle\nthat's far, far out past the charts."), ("excites my blood\nas a sailing man!", "gets my blood going\nas a pilot!"), ("Get on board, youngster!", "Get on board, kid!")],
"EventTicket_Text_OddTicketsWhereTo": [("odd tickets?", "odd PASSES?"), ("These tickets will get you to islands\nthat are far, far away.", "These PASSES will get you to places\nfar out past the charts."), ("excites my blood\nas a sailing man!", "gets my blood going\nas a pilot!"), ("Get on board, youngster!\nWhere shall we sail first?", "Get on board, kid!\nWhere do we fly first?")],
"BirthIsland_Harbor_Text_SailorReturn": r"What an oddly shaped rock, eh?\nDo you want to return to CLOUD CITY?$",
# --- misc ---
"sText_AuroraTicketBagFull": [("store something on your TERMINAL,\nthen", "store something in your\nTERMINAL, then")],
"sText_MysticTicketBagFull": [("store something on your TERMINAL,\nthen", "store something in your\nTERMINAL, then")],
"sText_MysteryGiftOldSeaMapBagFull": [("store something on your TERMINAL,\nthen", "store something in your\nTERMINAL, then")],
M+"SendDecorToYourPC": r"Then we'll trade!\nI'll send my decoration to your\lTERMINAL.$",
"Text_PictureBookShelf": r"There's a set of COMPANION picture\nbooks.$",
"sText_BerryProgramWillBeUpdatedPressA": r"The FRUIT Program on your older\nversion will be updated.\n{COLOR RED}{SHADOW LIGHT_RED}Press the A Button.",
"sText_TurnOffPowerHoldingStartSelect": r"Please turn on the power of the older\nversion while holding START and\nSELECT simultaneously. Then, ensure\nthe picture above appears.",
"sText_BerryProgramUpdate": r"FRUIT Program Update",
}
NOTES = {
"sCreditsText_PkmnEmeraldVersion": "title line; the staff credits keep the real names",
"EventTicket_Text_OddTicketGetOnBoard": "Briney -> Captain Han (pilot, says 'kid')",
CC+"CantMixWithJapaneseGame": "English only: region lock text made generic",
}

# --- COMPANION widths ---
FIX["InsideOfTruck_Text_BoxPrintedWithMonLogo"] = [("The box is printed with a COMPANION logo.", "The box has a COMPANION logo on it.")]
FIX["MauvilleCity_PokemonCenter_1F_Text_PokemonEvolvedStory"] = [("This TRAINER made {STR_VAR_1} COMPANION\nevolve!", "This TRAINER made {STR_VAR_1}\nCOMPANIONS evolve!")]
FIX["FallarborTown_BattleTentLobby_Text_ExplainFallarborTent"] = [("During battle, the COMPANION will appear\none at a time", "In battle, the COMPANIONS will appear\none at a time")]
FIX["VerdanturfTown_BattleTentLobby_Text_ExplainVerdanturfTent"] = [("their COMPANION in and out.", "their COMPANIONS in and out."), ("command their COMPANION.", "command their COMPANIONS."), ("The COMPANIONS are to behave according\nto their nature", "The COMPANIONS will behave according\nto their nature"), ("your trust in your\nCOMPANION and", "your trust in your\nCOMPANIONS and")]
FIX["VerdanturfTown_BattleTentLobby_Text_ExplainWhenInDangerRules"] = [("Depending on its nature, a COMPANION may\nstart using moves that don't match its\lnature when it is in trouble.", "Depending on its nature, a COMPANION\nmay start using moves that don't match\lits nature when it is in trouble.")]
