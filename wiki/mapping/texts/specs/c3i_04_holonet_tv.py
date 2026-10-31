# HOLONET shows (C3i part 4): every TV program in data/text/tv.inc and the reporters who feed them.
# TV is the HOLONET (glossary). Ferries are starliners; BIKE tricks are speeder tricks.
KEEP_REST_FILES = ("data/text/tv.inc",)
REFLOW = True


def pl(*olds):
    return [(o, o.replace("COMPANION", "COMPANIONS")) for o in olds]


FIX = {
"SlateportCity_OceanicMuseum_1F_Text_InterviewRequest": [("with the HOLONET network.", "with a HOLONET network."), ("stories on COMPANION and", "stories on COMPANIONS and")],
"gTVFanClubOpinionsText04": pl("What do COMPANION\nmean to you?"),
"gTVTodaysRivalTrainerText10": [("who's on a ferry now.", "who's on a starliner now."), ("{STR_VAR_2} COMPANION in the DATAPAD.", "{STR_VAR_2} COMPANIONS in the DATAPAD.")],
"gTVHoennTreasureInvestigatorsText02": [("on a ferry.", "on a starliner.")],
"gTVTrainerFanClubText06": r"FANS: The TRAINER's amazing\nspeeder-riding techniques!$",
"TVSecretBaseSecrets_Text_UsedTV": r"The visitor is watching the HOLONET!\pLooks like we have a big HOLONET fan!$",
"gTVPokemonBattleUpdateText00": [],
"LilycoveCity_ContestLobby_Text_InterviewRequest": [],
}
NOTES = {
"gTVTrainerFanClubText06": "BIKE-riding -> speeder-riding (SWOOP BIKE / SPEEDER BIKE)",
}
