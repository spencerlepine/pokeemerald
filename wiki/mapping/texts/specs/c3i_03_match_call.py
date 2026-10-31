# Match call (C3i part 3): the COMLINK calls from trainers, rivals, Mom, Korr, Leia and Lando, plus the
# trainer profile blurbs. Ocean worlds keep their seas and beaches (Kamino, Yavin 4, Dagobah's swamps).
# Han is a pilot, not a sailor, and Chewie is his co-pilot, not a pet.
KEEP_REST_FILES = ("data/text/match_call.inc", "src/data/text/match_call_messages.h")
REFLOW = True


def pl(*olds):
    return [(o, o.replace("COMPANION", "COMPANIONS")) for o in olds]


FIX = {
"MatchCall_NegativeBattleText8": pl("How are your COMPANION doing?"),
"MatchCall_NegativeBattleText11": pl("How are your COMPANION?"),
"MatchCall_PositiveBattleText9": pl("How are your COMPANION holding up?"),
"MatchCall_SameRouteBattleRequestText6": pl("How are your COMPANION keeping?"),
"MatchCall_DifferentRouteBattleRequestText3": pl("with your COMPANION"),
"MatchCall_DifferentRouteBattleRequestText7": pl("Are your COMPANION growing?"),
"MatchCall_DifferentRouteBattleRequestText9": pl("How are your COMPANION doing?", "My COMPANION keep"),
"MatchCall_DifferentRouteBattleRequestText11": pl("seeing your COMPANION,"),
"MatchCall_DifferentRouteBattleRequestText13": pl("Are your COMPANION keeping well?"),
"MatchCall_PersonalizedText30": pl("help of COMPANION can"),
"MatchCall_PersonalizedText41": pl("How are your COMPANION doing?"),
"MatchCall_PersonalizedText54": pl("Are your COMPANION fit"),
"MatchCall_PersonalizedText60": pl("enjoy COMPANION whatever"),
"MatchCall_Text_Mom1": pl("captivated by COMPANION.", "charm of COMPANION?"),
"MatchCall_Text_Scott1": pl("how COMPANION can be found"),
"MatchCall_Text_May1": r"MIRA: Hi, {PLAYER}{KUN}!\pHAN says he's retired from smuggling,\nbut I still see him flying around\lwith CHEWIE sometimes.\pHe must love flying still.$",
"MatchCall_Text_Brendan1": r"KAEL: Hey, {PLAYER}!\pHAN says he's retired from smuggling,\nbut I still see him flying around\lwith CHEWIE sometimes.\pI guess he must love\nflying still.$",
"MatchCall_Text_Steven1": [("visit the BIKE SHOP\nand get a SWOOP BIKE.", "visit the bike shop\nand get a SWOOP BIKE."), ("GRANITE\nCAVE", "SHADOWLANDS\nof KASHYYYK")],
"gText_MatchCallSchoolKid_Karen_Pokemon": r"I love any kind of COMPANIONS!",
"gText_MatchCallPokefan_Miguel_Intro2": pl("trust with your COMPANION."),
"gText_MatchCallSwimmer_Jenny_Intro2": r"I was interviewed on the HOLONET.",
}
NOTES = {
"MatchCall_Text_May1": "Han (Briney) is a retired smuggler; Chewie (Peeko) is his co-pilot, not a pet",
}

# --- Biggs Darklighter replaces Roxanne (he/him) ---
FIX["MatchCall_PersonalizedText25"] = [("I don't dislike her or anything.", "I don't dislike him or anything.")]
FIX["MatchCall_PersonalizedText26"] = [("battle with her\nyesterday.", "battle with him\nyesterday."), ("let me challenge her!", "let me challenge him!"), ("more I admire her!", "more I admire him!")]
