CaveOfOrigin_B1F_MapScripts::
	.byte 0

CaveOfOrigin_B1F_EventScript_Wallace::
	lock
	faceplayer
	msgbox CaveOfOrigin_B1F_Text_WallaceStory, MSGBOX_DEFAULT
	closemessage
	applywaitmovement LOCALID_CAVE_OF_ORIGIN_WALLACE, Common_Movement_WalkInPlaceFasterUp
	delay 60
	playse SE_PIN
	applywaitmovement LOCALID_CAVE_OF_ORIGIN_WALLACE, Common_Movement_ExclamationMark
	applywaitmovement LOCALID_CAVE_OF_ORIGIN_WALLACE, Common_Movement_Delay48
	delay 30
	applywaitmovement LOCALID_CAVE_OF_ORIGIN_WALLACE, Common_Movement_FacePlayer
	message CaveOfOrigin_B1F_Text_WhereIsRayquaza
	waitmessage
	goto CaveOfOrigin_B1F_EventScript_WheresRayquaza

CaveOfOrigin_B1F_EventScript_WheresRayquaza::
	multichoice 0, 0, MULTI_WHERES_RAYQUAZA, FALSE
	switch VAR_RESULT
	case 0, CaveOfOrigin_B1F_EventScript_AtCaveOfOrigin
	case 1, CaveOfOrigin_B1F_EventScript_AtMtPyre
	case 2, CaveOfOrigin_B1F_EventScript_AtSkyPillar
	case 3, CaveOfOrigin_B1F_EventScript_DontRemember
	goto CaveOfOrigin_B1F_EventScript_DontRemember
	end

CaveOfOrigin_B1F_EventScript_AtCaveOfOrigin::
	message CaveOfOrigin_B1F_Text_ButWereInCaveOfOrigin
	waitmessage
	goto CaveOfOrigin_B1F_EventScript_WheresRayquaza

CaveOfOrigin_B1F_EventScript_AtMtPyre::
	message CaveOfOrigin_B1F_Text_OldLadyDidntMentionThat
	waitmessage
	goto CaveOfOrigin_B1F_EventScript_WheresRayquaza

CaveOfOrigin_B1F_EventScript_DontRemember::
	message CaveOfOrigin_B1F_Text_CantYouRememberSomehow
	waitmessage
	goto CaveOfOrigin_B1F_EventScript_WheresRayquaza

CaveOfOrigin_B1F_EventScript_AtSkyPillar::
	msgbox CaveOfOrigin_B1F_Text_WellHeadToSkyPillar, MSGBOX_DEFAULT
	closemessage
	playse SE_EXIT
	fadescreenspeed FADE_TO_BLACK, 4
	setflag FLAG_WALLACE_GOES_TO_SKY_PILLAR
	setvar VAR_SOOTOPOLIS_CITY_STATE, 3
	removeobject LOCALID_CAVE_OF_ORIGIN_WALLACE
	clearflag FLAG_HIDE_SKY_PILLAR_WALLACE
	fadescreen FADE_FROM_BLACK
	release
	end

CaveOfOrigin_B1F_Text_WallaceStory:
	.string "Ah, so you are {PLAYER}{KUN}?\n"
	.string "I've heard tales of your exploits.\p"
	.string "My name is OBI-WAN.\p"
	.string "I was once the ARENA LEADER of\n"
	.string "DAGOBAH, but something came up.\p"
	.string "So now, I've entrusted my old master\n"
	.string "YODA with the ARENA.\p"
	.string "… … … … … …\n"
	.string "… … … … … …\p"
	.string "GREATKRAYT and SANDO, the two\n"
	.string "COMPANIONS wreaking havoc here, are\l"
	.string "said to be super-ancient COMPANIONS.\p"
	.string "But there aren't just two super-\n"
	.string "ancient COMPANIONS.\p"
	.string "There is one more somewhere.\p"
	.string "Somewhere, there is a super-\n"
	.string "ancient COMPANION named EXOGORTH.\p"
	.string "It's said that it was EXOGORTH that\n"
	.string "calmed the two combatants in\l"
	.string "the distant past.\p"
	.string "But even I have no clue as to\n"
	.string "EXOGORTH's whereabouts…$"

CaveOfOrigin_B1F_Text_WhereIsRayquaza:
	.string "OBI-WAN: {PLAYER}{KUN}, do you perhaps\n"
	.string "know where EXOGORTH is now?\p"
	.string "If you do, please tell me.$"

CaveOfOrigin_B1F_Text_ButWereInCaveOfOrigin:
	.string "OBI-WAN: The CAVE OF EVIL?\p"
	.string "But that's right here!\n"
	.string "I need you to do better than that!\p"
	.string "Please, I need you to think about\n"
	.string "where EXOGORTH might be right now.$"

CaveOfOrigin_B1F_Text_OldLadyDidntMentionThat:
	.string "OBI-WAN: JEDHA TEMPLE?\p"
	.string "But when I met the GUARDIANS there\n"
	.string "earlier, she made no mention of it.\p"
	.string "I very much doubt the GUARDIANS\n"
	.string "would try to hide something from me…\p"
	.string "{PLAYER}{KUN}, could you think about this\n"
	.string "more carefully for me?$"

CaveOfOrigin_B1F_Text_CantYouRememberSomehow:
	.string "OBI-WAN: Huh? You don't remember?\n"
	.string "Hmm… That's a problem…\p"
	.string "Can't you remember somehow?$"

CaveOfOrigin_B1F_Text_WellHeadToSkyPillar:
	.string "OBI-WAN: The ASTEROID SPIRE?\p"
	.string "That's it!\n"
	.string "It must be the ASTEROID SPIRE!\p"
	.string "{PLAYER}{KUN}, there's not a moment to lose!\n"
	.string "We'll head to the ASTEROID SPIRE\n"
	.string "right away!$"

