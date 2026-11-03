AbandonedShip_Corridors_1F_MapScripts::
	.byte 0

AbandonedShip_Corridors_1F_EventScript_Youngster::
	msgbox AbandonedShip_Corridors_1F_Text_IsntItFunHere, MSGBOX_NPC
	end

AbandonedShip_Corridors_1F_EventScript_Charlie::
	trainerbattle_single TRAINER_CHARLIE, AbandonedShip_Corridors_1F_Text_CharlieIntro, AbandonedShip_Corridors_1F_Text_CharlieDefeat
	msgbox AbandonedShip_Corridors_1F_Text_CharliePostBattle, MSGBOX_AUTOCLOSE
	end

AbandonedShip_Corridors_1F_Text_CharlieIntro:
	.string "Rrrip!\p"
	.string "(What's so funny about bringing my\n"
	.string "log float aboard the wreck?)$"

AbandonedShip_Corridors_1F_Text_CharlieDefeat:
	.string "Mrrraa!\p"
	.string "(Whoa, you overwhelmed me!)$"

AbandonedShip_Corridors_1F_Text_CharliePostBattle:
	.string "It's not easy throwing CAPTURE PODS\n"
	.string "while hanging on to an inner tube!$"

AbandonedShip_Corridors_1F_Text_IsntItFunHere:
	.string "Isn't it fun here?\n"
	.string "I get excited just being here!$"
