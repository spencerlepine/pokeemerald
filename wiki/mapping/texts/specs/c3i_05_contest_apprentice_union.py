# Showcases, the Apprentice and the Union Room (C3i part 5): contest strings and the Cloud City showcase hall,
# the Apprentice at the Grand Arena, Union Room and Trading Board text, and ribbon descriptions.
# Link hardware is the COMLINK. Cross-cartridge text ("Pokemon Ruby or Sapphire Game Pak") becomes
# "this game" and "an older version".
KEEP_REST_FILES = ("data/text/apprentice.inc", "src/data/union_room.h", "data/text/contest_strings.inc",
                   "data/scripts/contest_hall.inc", "data/text/contest_painting.inc", "data/text/contest_link.inc",
                   "src/data/text/gift_ribbon_descriptions.h")
REFLOW = True
L = "LilycoveCity_ContestLobby_Text_"


def pl(*olds):
    return [(o, o.replace("COMPANION", "COMPANIONS")) for o in olds]


FIX = {
L+"ExplainContestRanks": [("four ranks of COMPANION\nSHOWCASES.", "four ranks of\nSHOWCASES.")],
L+"Explain4PlayerContest": [("connect\nover a COMLINK cable,", "connect\nover a COMLINK,")],
L+"PlayerAt4PCounterUseGMode": [("using a COMLINK cable.", "using COMLINK cables.")],
L+"ExplainLinkContest": r"This is a SHOWCASE for two to four\nplayers linked by COMLINK.\pParticipants are first asked to choose\nthe mode they wish to enter.\pThere are two different modes.\pE-MODE (EMERALD MODE) is for\ntwo to four players, each with\lthis game.\pG-MODE (GLOBAL MODE) is only for\nfour players, each with this game\lor an older version.\pThe players should discuss which mode\nthey want, then choose the same mode.\pOnce all the players have chosen\nthe same SHOWCASE in the same mode,\lthe entry registration is complete.\pAfter that, a SHOWCASE will start in\nthe usual manner.$",
L+"ExplainEMode": r"In E-MODE (EMERALD MODE),\na LINK SHOWCASE can be held with\ltwo to four players. Each player must\lhave this game.\pThe players must be linked with each\nother by COMLINK.\pIf there are fewer than four players,\nTRAINERS in the hall will join to fill\lthe 4-player SHOWCASE lineup.\pPlease be aware that E-MODE is not\navailable in older versions.$",
L+"ExplainGMode": r"G-MODE (GLOBAL MODE) is specifically\nfor four players who are linked using\lCOMLINK cables.\pEach player must have this game or\nan older version.\pThe SHOWCASE starts after all players\nchoose G-MODE (this game) or\lenter through the 4-player reception\lcounter (an older version).$",
L+"NoWirelessAdapterInGMode": r"I'm terribly sorry.\pG-MODE does not function\nwith a wireless COMLINK.\pPlease select E-MODE or try\nagain using a COMLINK cable.$",
"gText_ApprenticeWhichLevelMode10": [("I'll buy you a boat for that!", "I'll buy you a starship for that!")],
"gText_ApprenticeWhichMonFirst0": pl("line up my COMPANION\n"),
"gText_ApprenticeMonThanks9": [("I'll get one in a BALL, like, cram!", "I'll get one in a POD, like, cram!")],
"sText_RegisterMonAtTradingBoard": pl("one of\nyour COMPANION?"),
}
NOTES = {
L+"ExplainLinkContest": "Ruby/Sapphire cartridge references -> 'an older version'",
}
