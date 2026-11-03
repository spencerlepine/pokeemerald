LilycoveCity_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, LilycoveCity_OnTransition
	map_script MAP_SCRIPT_ON_LOAD, LilycoveCity_OnLoad
	.byte 0

LilycoveCity_OnTransition:
	setflag FLAG_VISITED_LILYCOVE_CITY
	setvar VAR_CONTEST_HALL_STATE, 0
	setflag FLAG_HIDE_LILYCOVE_CONTEST_HALL_REPORTER
	call_if_set FLAG_SYS_WEATHER_CTRL, Common_EventScript_SetAbnormalWeather
	call Common_EventScript_SetupRivalGfxId
	end

LilycoveCity_OnLoad:
	call_if_unset FLAG_TEAM_AQUA_ESCAPED_IN_SUBMARINE, LilycoveCity_EventScript_SetWailmerMetatiles
	end

LilycoveCity_EventScript_SetWailmerMetatiles::
	setmetatile 76, 12, METATILE_Lilycove_Wailmer0, TRUE
	setmetatile 77, 12, METATILE_Lilycove_Wailmer1, TRUE
	setmetatile 76, 13, METATILE_Lilycove_Wailmer2, TRUE
	setmetatile 77, 13, METATILE_Lilycove_Wailmer3, TRUE
	setmetatile 76, 14, METATILE_Lilycove_Wailmer0_Alt, TRUE
	setmetatile 77, 14, METATILE_Lilycove_Wailmer1_Alt, TRUE
	setmetatile 76, 15, METATILE_Lilycove_Wailmer2, TRUE
	setmetatile 77, 15, METATILE_Lilycove_Wailmer3, TRUE
	setmetatile 77, 16, METATILE_Lilycove_Wailmer0_Alt, TRUE
	setmetatile 78, 16, METATILE_Lilycove_Wailmer1_Alt, TRUE
	setmetatile 77, 17, METATILE_Lilycove_Wailmer2, TRUE
	setmetatile 78, 17, METATILE_Lilycove_Wailmer3, TRUE
	return
@ People who used to be in the Showcase hall (removed 2026-11-03); they stand outside now.
LilycoveCity_EventScript_ShowcaseReceptionist::
	msgbox LilycoveCity_Text_ShowcaseReceptionist, MSGBOX_NPC
	end

LilycoveCity_EventScript_ShowcaseLinkReceptionist::
	msgbox LilycoveCity_Text_ShowcaseLinkReceptionist, MSGBOX_NPC
	end

LilycoveCity_EventScript_BlendMaster::
	msgbox LilycoveCity_Text_BlendMaster, MSGBOX_NPC
	end

LilycoveCity_EventScript_PlazaMan::
	msgbox LilycoveCity_Text_PlazaMan, MSGBOX_NPC
	end

LilycoveCity_EventScript_PlazaTwin::
	msgbox LilycoveCity_Text_PlazaTwin, MSGBOX_NPC
	end

LilycoveCity_EventScript_PlazaPokefanF::
	msgbox LilycoveCity_Text_PlazaPokefanF, MSGBOX_NPC
	end

LilycoveCity_EventScript_Reporter::
	msgbox LilycoveCity_Text_Reporter, MSGBOX_NPC
	end

LilycoveCity_EventScript_PlazaBoy::
	msgbox LilycoveCity_Text_PlazaBoy, MSGBOX_NPC
	end

LilycoveCity_EventScript_PlazaGirl::
	msgbox LilycoveCity_Text_PlazaGirl, MSGBOX_NPC
	end

LilycoveCity_EventScript_Artist::
	msgbox LilycoveCity_Text_Artist, MSGBOX_NPC
	end

LilycoveCity_EventScript_LittleGirl::
	msgbox LilycoveCity_Text_LittleGirl, MSGBOX_NPC
	end

LilycoveCity_EventScript_Girl2::
	msgbox LilycoveCity_Text_Girl2, MSGBOX_NPC
	end

LilycoveCity_EventScript_FatMan2::
	msgbox LilycoveCity_Text_FatMan2, MSGBOX_NPC
	end

LilycoveCity_EventScript_NinjaBoy::
	msgbox LilycoveCity_Text_NinjaBoy, MSGBOX_NPC
	end

LilycoveCity_EventScript_BlackBelt::
	msgbox LilycoveCity_Text_BlackBelt, MSGBOX_NPC
	end

LilycoveCity_EventScript_Fisherman::
	msgbox LilycoveCity_Text_Fisherman, MSGBOX_NPC
	end

LilycoveCity_EventScript_Sailor3::
	msgbox LilycoveCity_Text_Sailor3, MSGBOX_NPC
	end

LilycoveCity_EventScript_Boy1::
	msgbox LilycoveCity_Text_Boy1, MSGBOX_NPC
	end

LilycoveCity_EventScript_Boy2::
	msgbox LilycoveCity_Text_Boy2, MSGBOX_NPC
	end

LilycoveCity_EventScript_Girl3::
	msgbox LilycoveCity_Text_Girl3, MSGBOX_NPC
	end

LilycoveCity_EventScript_Judge1::
	msgbox LilycoveCity_Text_Judge1, MSGBOX_NPC
	end

LilycoveCity_EventScript_Judge2::
	msgbox LilycoveCity_Text_Judge2, MSGBOX_NPC
	end

LilycoveCity_EventScript_Judge3::
	msgbox LilycoveCity_Text_Judge3, MSGBOX_NPC
	end

LilycoveCity_EventScript_Host1::
	msgbox LilycoveCity_Text_Host1, MSGBOX_NPC
	end

LilycoveCity_EventScript_Host2::
	msgbox LilycoveCity_Text_Host2, MSGBOX_NPC
	end

LilycoveCity_EventScript_Host3::
	msgbox LilycoveCity_Text_Host3, MSGBOX_NPC
	end

LilycoveCity_EventScript_TeaFan1::
	msgbox LilycoveCity_Text_TeaFan1, MSGBOX_NPC
	end

LilycoveCity_EventScript_TeaFan2::
	msgbox LilycoveCity_Text_TeaFan2, MSGBOX_NPC
	end

LilycoveCity_EventScript_TeaFan3::
	msgbox LilycoveCity_Text_TeaFan3, MSGBOX_NPC
	end

LilycoveCity_EventScript_TeaFan4::
	msgbox LilycoveCity_Text_TeaFan4, MSGBOX_NPC
	end

LilycoveCity_EventScript_TeaFan5::
	msgbox LilycoveCity_Text_TeaFan5, MSGBOX_NPC
	end

LilycoveCity_EventScript_TeaFan6::
	msgbox LilycoveCity_Text_TeaFan6, MSGBOX_NPC
	end

LilycoveCity_EventScript_OldTimer::
	msgbox LilycoveCity_Text_OldTimer, MSGBOX_NPC
	end

LilycoveCity_EventScript_Sketcher1::
	msgbox LilycoveCity_Text_Sketcher1, MSGBOX_NPC
	end

LilycoveCity_EventScript_Sketcher2::
	msgbox LilycoveCity_Text_Sketcher2, MSGBOX_NPC
	end

LilycoveCity_EventScript_Trainer1::
	msgbox LilycoveCity_Text_Trainer1, MSGBOX_NPC
	end

LilycoveCity_EventScript_Trainer2::
	msgbox LilycoveCity_Text_Trainer2, MSGBOX_NPC
	end

LilycoveCity_EventScript_Trainer3::
	msgbox LilycoveCity_Text_Trainer3, MSGBOX_NPC
	end

LilycoveCity_EventScript_Trainer4::
	msgbox LilycoveCity_Text_Trainer4, MSGBOX_NPC
	end

LilycoveCity_EventScript_Trainer5::
	msgbox LilycoveCity_Text_Trainer5, MSGBOX_NPC
	end

LilycoveCity_EventScript_Trainer6::
	msgbox LilycoveCity_Text_Trainer6, MSGBOX_NPC
	end

LilycoveCity_EventScript_Shopper1::
	msgbox LilycoveCity_Text_Shopper1, MSGBOX_NPC
	end

LilycoveCity_EventScript_Shopper2::
	msgbox LilycoveCity_Text_Shopper2, MSGBOX_NPC
	end

LilycoveCity_EventScript_Shopper3::
	msgbox LilycoveCity_Text_Shopper3, MSGBOX_NPC
	end

LilycoveCity_EventScript_Shopper4::
	msgbox LilycoveCity_Text_Shopper4, MSGBOX_NPC
	end

LilycoveCity_EventScript_Shopper5::
	msgbox LilycoveCity_Text_Shopper5, MSGBOX_NPC
	end

LilycoveCity_EventScript_Shopper6::
	msgbox LilycoveCity_Text_Shopper6, MSGBOX_NPC
	end

LilycoveCity_EventScript_Shopper7::
	msgbox LilycoveCity_Text_Shopper7, MSGBOX_NPC
	end

LilycoveCity_EventScript_Shopper8::
	msgbox LilycoveCity_Text_Shopper8, MSGBOX_NPC
	end

LilycoveCity_EventScript_Shopper9::
	msgbox LilycoveCity_Text_Shopper9, MSGBOX_NPC
	end

LilycoveCity_EventScript_Visitor1::
	msgbox LilycoveCity_Text_Visitor1, MSGBOX_NPC
	end

LilycoveCity_EventScript_Visitor2::
	msgbox LilycoveCity_Text_Visitor2, MSGBOX_NPC
	end

LilycoveCity_EventScript_Visitor3::
	msgbox LilycoveCity_Text_Visitor3, MSGBOX_NPC
	end

LilycoveCity_EventScript_Guest1::
	msgbox LilycoveCity_Text_Guest1, MSGBOX_NPC
	end

LilycoveCity_EventScript_Guest2::
	msgbox LilycoveCity_Text_Guest2, MSGBOX_NPC
	end

LilycoveCity_EventScript_Patient1::
	msgbox LilycoveCity_Text_Patient1, MSGBOX_NPC
	end

LilycoveCity_EventScript_Patient2::
	msgbox LilycoveCity_Text_Patient2, MSGBOX_NPC
	end


LilycoveCity_EventScript_BerryGentleman::
	lock
	faceplayer
	dotimebasedevents
	goto_if_set FLAG_DAILY_LILYCOVE_RECEIVED_BERRY, LilycoveCity_EventScript_ReceivedBerry
	msgbox LilycoveCity_Text_BerrySuitsYou, MSGBOX_DEFAULT
	random 10
	addvar VAR_RESULT, FIRST_BERRY_INDEX
	giveitem VAR_RESULT
	goto_if_eq VAR_RESULT, FALSE, Common_EventScript_ShowBagIsFull
	setflag FLAG_DAILY_LILYCOVE_RECEIVED_BERRY
	msgbox LilycoveCity_Text_BecauseYoureTrainer, MSGBOX_DEFAULT
	release
	end

LilycoveCity_EventScript_ReceivedBerry::
	msgbox LilycoveCity_Text_PokeblocksSuitPokemon, MSGBOX_DEFAULT
	release
	end

LilycoveCity_EventScript_Man3::
	msgbox LilycoveCity_Text_ContestHallInTown, MSGBOX_NPC
	end

LilycoveCity_EventScript_Girl::
	lock
	faceplayer
	goto_if_set FLAG_BADGE07_GET, LilycoveCity_EventScript_GirlAquaGone
	msgbox LilycoveCity_Text_StrangeCaveInCove, MSGBOX_DEFAULT
	release
	end

LilycoveCity_EventScript_GirlAquaGone::
	msgbox LilycoveCity_Text_GoingToMoveDeleterForHMs, MSGBOX_DEFAULT
	release
	end

LilycoveCity_EventScript_RichBoy::
	msgbox LilycoveCity_Text_ImFromKanto, MSGBOX_NPC
	end

LilycoveCity_EventScript_Sailor2::
	lock
	faceplayer
	goto_if_set FLAG_TEAM_AQUA_ESCAPED_IN_SUBMARINE, LilycoveCity_EventScript_Sailor2AquaGone
	msgbox LilycoveCity_Text_TeamAquaBeenTrainingWailmer, MSGBOX_DEFAULT
	release
	end

LilycoveCity_EventScript_Sailor2AquaGone::
	msgbox LilycoveCity_Text_SomeonePuntedTeamAquaOut, MSGBOX_DEFAULT
	release
	end

LilycoveCity_EventScript_Woman2::
	lock
	faceplayer
	goto_if_set FLAG_TEAM_AQUA_ESCAPED_IN_SUBMARINE, LilycoveCity_EventScript_Woman2AquaGone
	msgbox LilycoveCity_Text_SomeoneStoleMyPokemon, MSGBOX_DEFAULT
	release
	end

LilycoveCity_EventScript_Woman2AquaGone::
	msgbox LilycoveCity_Text_MissingPokemonCameBack, MSGBOX_DEFAULT
	release
	end

LilycoveCity_EventScript_Man2::
	msgbox LilycoveCity_Text_ImArtDealer, MSGBOX_NPC
	end

LilycoveCity_EventScript_ExpertM1::
	msgbox LilycoveCity_Text_SeaRemainsForeverYoung, MSGBOX_SIGN
	end

LilycoveCity_EventScript_ExpertF::
	msgbox LilycoveCity_Text_SixtyYearsAgoHusbandProposed, MSGBOX_SIGN
	end

LilycoveCity_EventScript_ExpertM2::
	lock
	faceplayer
	goto_if_set FLAG_BADGE07_GET, LilycoveCity_EventScript_ExpertM2AquaGone
	msgbox LilycoveCity_Text_TeamAquaRenovatedCavern, MSGBOX_DEFAULT
	release
	end

LilycoveCity_EventScript_ExpertM2AquaGone::
	msgbox LilycoveCity_Text_TeamAquaLotGoneForGood, MSGBOX_DEFAULT
	release
	end

LilycoveCity_EventScript_Sailor1::
	msgbox LilycoveCity_Text_HeardTowerCalledSkyPillar, MSGBOX_NPC
	end

LilycoveCity_EventScript_FatMan::
	msgbox LilycoveCity_Text_SawTallTowerOnRoute131, MSGBOX_NPC
	end

LilycoveCity_EventScript_Man1::
	lockall
	msgbox LilycoveCity_Text_JustArrivedAndSawRarePokemon, MSGBOX_NPC
	applymovement LOCALID_LILYCOVE_MAN_1, Common_Movement_FaceOriginalDirection
	end

LilycoveCity_EventScript_Woman1::
	lockall
	msgbox LilycoveCity_Text_HoneymoonVowToSeeRarePokemon, MSGBOX_NPC
	applymovement LOCALID_LILYCOVE_WOMAN_1, Common_Movement_FaceOriginalDirection
	end

LilycoveCity_EventScript_CitySign::
	msgbox LilycoveCity_Text_CitySign, MSGBOX_SIGN
	end

LilycoveCity_EventScript_ContestHallSign::
	msgbox LilycoveCity_Text_ContestHallSign, MSGBOX_SIGN
	end

LilycoveCity_EventScript_MotelSign::
	msgbox LilycoveCity_Text_MotelSign, MSGBOX_SIGN
	end

LilycoveCity_EventScript_MuseumSign::
	lockall
	specialvar VAR_0x8004, CountPlayerMuseumPaintings
	switch VAR_0x8004
	case 0, LilycoveCity_EventScript_MuseumSignNoPaintings
	msgbox LilycoveCity_Text_MuseumSignPlayersExhibit, MSGBOX_DEFAULT
	releaseall
	end

LilycoveCity_EventScript_MuseumSignNoPaintings::
	msgbox LilycoveCity_Text_MuseumSign, MSGBOX_DEFAULT
	releaseall
	end

LilycoveCity_EventScript_HarborSign::
	lockall
	goto_if_set FLAG_SYS_GAME_CLEAR, LilycoveCity_EventScript_HarborSignFerryReady
	msgbox LilycoveCity_Text_HarborSignUnderConstruction, MSGBOX_DEFAULT
	releaseall
	end

LilycoveCity_EventScript_HarborSignFerryReady::
	msgbox LilycoveCity_Text_HarborSign, MSGBOX_DEFAULT
	releaseall
	end

LilycoveCity_EventScript_TrainerFanClubSign::
	msgbox LilycoveCity_Text_TrainerFanClubSign, MSGBOX_SIGN
	end

LilycoveCity_EventScript_DepartmentStoreSign::
	msgbox LilycoveCity_Text_DepartmentStoreSign, MSGBOX_SIGN
	end

LilycoveCity_EventScript_MoveDeletersHouseSign::
	msgbox LilycoveCity_Text_MoveDeletersHouseSign, MSGBOX_SIGN
	end

LilycoveCity_EventScript_WailmerTrainerGrunt::
	lockall
	goto_if_set FLAG_MET_WAILMER_TRAINER, LilycoveCity_EventScript_MetWailmerTrainer
	msgbox LilycoveCity_Text_WailmerLeapOutOfWater, MSGBOX_DEFAULT
	applywaitmovement VAR_LAST_TALKED, Common_Movement_FacePlayer
	msgbox LilycoveCity_Text_GetLostMessingUpTraining, MSGBOX_DEFAULT
	applywaitmovement VAR_LAST_TALKED, Common_Movement_FaceOriginalDirection
	setflag FLAG_MET_WAILMER_TRAINER
	releaseall
	end

LilycoveCity_EventScript_MetWailmerTrainer::
	msgbox LilycoveCity_Text_WailmerLeapOutOfWater, MSGBOX_DEFAULT
	releaseall
	end

LilycoveCity_EventScript_AquaGrunt1::
	msgbox LilycoveCity_Text_MovedLootIntoHideoutToday, MSGBOX_NPC
	end

LilycoveCity_EventScript_AquaGrunt2::
	msgbox LilycoveCity_Text_ChanceToDoBigThings, MSGBOX_NPC
	end

LilycoveCity_EventScript_AquaGrunt3::
	msgbox LilycoveCity_Text_DontGoNearCaveInCove, MSGBOX_NPC
	end

LilycoveCity_EventScript_AquaGrunt4::
	msgbox LilycoveCity_Text_IfWorldBecomesOurs, MSGBOX_NPC
	end

LilycoveCity_EventScript_Rival::
	lock
	faceplayer
	checkplayergender
	goto_if_eq VAR_RESULT, MALE, LilycoveCity_EventScript_May
	goto_if_eq VAR_RESULT, FEMALE, LilycoveCity_EventScript_Brendan
	end

LilycoveCity_EventScript_May::
	playbgm MUS_ENCOUNTER_MAY, TRUE
	call_if_set FLAG_DECLINED_RIVAL_BATTLE_LILYCOVE, LilycoveCity_EventScript_MayAskToBattleAgain
	call_if_unset FLAG_DECLINED_RIVAL_BATTLE_LILYCOVE, LilycoveCity_EventScript_MayAskToBattle
	goto_if_eq VAR_RESULT, NO, LilycoveCity_EventScript_DeclineMayBattle
	msgbox LilycoveCity_Text_MayWontBeBeaten, MSGBOX_DEFAULT
	switch VAR_STARTER_MON
	case 0, LilycoveCity_EventScript_BattleMayTreecko
	case 1, LilycoveCity_EventScript_BattleMayTorchic
	case 2, LilycoveCity_EventScript_BattleMayMudkip
	end

LilycoveCity_EventScript_MayAskToBattleAgain::
	msgbox LilycoveCity_Text_MayBattleMe, MSGBOX_YESNO
	return

LilycoveCity_EventScript_MayAskToBattle::
	msgbox LilycoveCity_Text_MayShoppingLetsBattle, MSGBOX_YESNO
	return

LilycoveCity_EventScript_DeclineMayBattle::
	setflag FLAG_DECLINED_RIVAL_BATTLE_LILYCOVE
	msgbox LilycoveCity_Text_MayNotRaisingPokemon, MSGBOX_DEFAULT
	savebgm MUS_DUMMY
	fadedefaultbgm
	release
	end

LilycoveCity_EventScript_Brendan::
	playbgm MUS_ENCOUNTER_BRENDAN, TRUE
	call_if_set FLAG_DECLINED_RIVAL_BATTLE_LILYCOVE, LilycoveCity_EventScript_BrendanAskToBattleAgain
	call_if_unset FLAG_DECLINED_RIVAL_BATTLE_LILYCOVE, LilycoveCity_EventScript_BrendanAskToBattle
	goto_if_eq VAR_RESULT, NO, LilycoveCity_EventScript_DeclineBrendanBattle
	msgbox LilycoveCity_Text_BrendanWontBeBeaten, MSGBOX_DEFAULT
	switch VAR_STARTER_MON
	case 0, LilycoveCity_EventScript_BattleBrendanTreecko
	case 1, LilycoveCity_EventScript_BattleBrendanTorchic
	case 2, LilycoveCity_EventScript_BattleBrendanMudkip
	end

LilycoveCity_EventScript_BrendanAskToBattleAgain::
	msgbox LilycoveCity_Text_BrendanBattleMe, MSGBOX_YESNO
	return

LilycoveCity_EventScript_BrendanAskToBattle::
	msgbox LilycoveCity_Text_BrendanShoppingLetsBattle, MSGBOX_YESNO
	return

LilycoveCity_EventScript_DeclineBrendanBattle::
	setflag FLAG_DECLINED_RIVAL_BATTLE_LILYCOVE
	msgbox LilycoveCity_Text_BrendanNoConfidence, MSGBOX_DEFAULT
	savebgm MUS_DUMMY
	fadedefaultbgm
	release
	end

LilycoveCity_EventScript_BattleMayTreecko::
	trainerbattle_no_intro TRAINER_MAY_LILYCOVE_TREECKO, LilycoveCity_Text_MayDefeat
	goto LilycoveCity_EventScript_DefeatedMay
	end

LilycoveCity_EventScript_BattleMayTorchic::
	trainerbattle_no_intro TRAINER_MAY_LILYCOVE_TORCHIC, LilycoveCity_Text_MayDefeat
	goto LilycoveCity_EventScript_DefeatedMay
	end

LilycoveCity_EventScript_BattleMayMudkip::
	trainerbattle_no_intro TRAINER_MAY_LILYCOVE_MUDKIP, LilycoveCity_Text_MayDefeat
	goto LilycoveCity_EventScript_DefeatedMay
	end

LilycoveCity_EventScript_BattleBrendanTreecko::
	trainerbattle_no_intro TRAINER_BRENDAN_LILYCOVE_TREECKO, LilycoveCity_Text_BrendanDefeat
	goto LilycoveCity_EventScript_DefeatedBrendan
	end

LilycoveCity_EventScript_BattleBrendanTorchic::
	trainerbattle_no_intro TRAINER_BRENDAN_LILYCOVE_TORCHIC, LilycoveCity_Text_BrendanDefeat
	goto LilycoveCity_EventScript_DefeatedBrendan
	end

LilycoveCity_EventScript_BattleBrendanMudkip::
	trainerbattle_no_intro TRAINER_BRENDAN_LILYCOVE_MUDKIP, LilycoveCity_Text_BrendanDefeat
	goto LilycoveCity_EventScript_DefeatedBrendan
	end

LilycoveCity_EventScript_DefeatedMay::
	msgbox LilycoveCity_Text_MayGoingBackToLittleroot, MSGBOX_DEFAULT
	setvar VAR_RESULT, FALSE
	call_if_set FLAG_BADGE06_GET, LilycoveCity_EventScript_CheckFinalBadge
	call_if_eq VAR_RESULT, FALSE, LilycoveCity_EventScript_MayCollectBadges
	call_if_eq VAR_RESULT, TRUE, LilycoveCity_EventScript_MayPokemonLeague
	clearflag FLAG_HIDE_LITTLEROOT_TOWN_MAYS_HOUSE_RIVAL_BEDROOM
	clearflag FLAG_HIDE_LITTLEROOT_TOWN_MAYS_HOUSE_2F_PICHU_DOLL
	goto LilycoveCity_EventScript_RivalFlyAway
	end

LilycoveCity_EventScript_CheckFinalBadge::
	goto_if_set FLAG_BADGE08_GET, LilycoveCity_EventScript_HasFinalBadge
	return

LilycoveCity_EventScript_HasFinalBadge::
	setvar VAR_RESULT, TRUE
	return

LilycoveCity_EventScript_MayCollectBadges::
	msgbox LilycoveCity_Text_MayYouGoingToCollectBadges, MSGBOX_DEFAULT
	return

LilycoveCity_EventScript_MayPokemonLeague::
	goto_if_set FLAG_SYS_GAME_CLEAR, LilycoveCity_EventScript_MayBattleFrontier
	msgbox LilycoveCity_Text_MayYouGoingToPokemonLeague, MSGBOX_DEFAULT
	return

LilycoveCity_EventScript_MayBattleFrontier::
	msgbox LilycoveCity_Text_MayYouGoingToBattleFrontier, MSGBOX_DEFAULT
	return

LilycoveCity_EventScript_DefeatedBrendan::
	msgbox LilycoveCity_Text_BrendanGoingBackToLittleroot, MSGBOX_DEFAULT
	setvar VAR_RESULT, FALSE
	call_if_set FLAG_BADGE06_GET, LilycoveCity_EventScript_CheckFinalBadge
	call_if_eq VAR_RESULT, FALSE, LilycoveCity_EventScript_BrendanCollectBadges
	call_if_eq VAR_RESULT, TRUE, LilycoveCity_EventScript_BrendanPokemonLeague
	clearflag FLAG_HIDE_LITTLEROOT_TOWN_BRENDANS_HOUSE_RIVAL_BEDROOM
	clearflag FLAG_HIDE_LITTLEROOT_TOWN_BRENDANS_HOUSE_2F_SWABLU_DOLL
	goto LilycoveCity_EventScript_RivalFlyAway
	end

LilycoveCity_EventScript_BrendanCollectBadges::
	msgbox LilycoveCity_Text_BrendanYouGoingToCollectBadges, MSGBOX_DEFAULT
	return

LilycoveCity_EventScript_BrendanPokemonLeague::
	goto_if_set FLAG_SYS_GAME_CLEAR, LilycoveCity_EventScript_BrendanBattleFrontier
	msgbox LilycoveCity_Text_BrendanYouGoingToPokemonLeague, MSGBOX_DEFAULT
	return

LilycoveCity_EventScript_BrendanBattleFrontier::
	msgbox LilycoveCity_Text_BrendanYouGoingToBattleFrontier, MSGBOX_DEFAULT
	return

LilycoveCity_EventScript_RivalFlyAway::
	closemessage
	applywaitmovement VAR_LAST_TALKED, Common_Movement_WalkInPlaceFasterDown
	delay 50
	setfieldeffectargument 0, 1
	dofieldeffect FLDEFF_NPCFLY_OUT
	delay 15
	removeobject VAR_LAST_TALKED
	waitfieldeffect FLDEFF_NPCFLY_OUT
	savebgm MUS_DUMMY
	fadedefaultbgm
	setflag FLAG_MET_RIVAL_LILYCOVE
	release
	end

LilycoveCity_EventScript_SchoolKidM::
	lock
	faceplayer
	msgbox LilycoveCity_Text_DoYouKnowAboutBerryBlender, MSGBOX_DEFAULT
	release
	end

LilycoveCity_EventScript_KnowAboutBerryBlender::
	msgbox LilycoveCity_Text_FasterSpinBetterPokeblocks, MSGBOX_DEFAULT
	return

LilycoveCity_EventScript_DontKnowAboutBerryBlender::
	msgbox LilycoveCity_Text_ExplainBerryBlender, MSGBOX_DEFAULT
	return

LilycoveCity_Text_MayShoppingLetsBattle:
	.string "MIRA: Oh, hey?\n"
	.string "{PLAYER}{KUN}, are you shopping, too?\p"
	.string "I bought a whole bunch of DOLLS and\n"
	.string "POSTERS.\p"
	.string "Of course, I've also caught a lot of\n"
	.string "COMPANIONS, and I'm raising them\l"
	.string "properly, too.\p"
	.string "Actually, I'm more worried if you're\n"
	.string "raising COMPANIONS properly, {PLAYER}{KUN}.\p"
	.string "I'll battle with you, so you can show\n"
	.string "me your COMPANIONS, {PLAYER}{KUN}.$"

LilycoveCity_Text_MayNotRaisingPokemon:
	.string "MIRA: Oh, why? {PLAYER}{KUN}, haven't you\n"
	.string "been raising your COMPANIONS?\p"
	.string "That's not a very good showing as a\n"
	.string "TRAINER…$"

LilycoveCity_Text_MayBattleMe:
	.string "MIRA: Come on, battle with me, so I can\n"
	.string "check out your COMPANIONS!$"

LilycoveCity_Text_MayWontBeBeaten:
	.string "MIRA: The COMPANIONS I raised won't be\n"
	.string "beaten by yours, {PLAYER}{KUN}!$"

LilycoveCity_Text_MayDefeat:
	.string "… … … … … … … …\p"
	.string "I remember the battle I had with you,\n"
	.string "{PLAYER}{KUN}, on ROUTE 103.\p"
	.string "That battle helped you become this\n"
	.string "strong, {PLAYER}{KUN}, didn't it?$"

LilycoveCity_Text_MayGoingBackToLittleroot:
	.string "MIRA: I'm thinking of going back to\n"
	.string "MOS PELGO soon.\p"
	.string "I've caught a good group of\n"
	.string "COMPANIONS, and my DATAPAD is coming\l"
	.string "along, so I'm going home to show my dad.$"

LilycoveCity_Text_MayYouGoingToCollectBadges:
	.string "{PLAYER}{KUN}, what are you going to do?\p"
	.string "Collect all the ARENA SHARDS and take\n"
	.string "the ILUM TEMPLE challenge?\p"
	.string "Well, while you're collecting SHARDS,\n"
	.string "{PLAYER}{KUN}, I'm going to work on my\l"
	.string "DATAPAD. I'll complete it before you!\p"
	.string "See you!$"

LilycoveCity_Text_MayYouGoingToPokemonLeague:
	.string "{PLAYER}{KUN}, what are you going to do?\p"
	.string "Are you taking the ILUM TEMPLE\n"
	.string "challenge?\p"
	.string "Or, are you going to complete your\n"
	.string "DATAPAD?\p"
	.string "I might've lost to you in battling,\n"
	.string "but I'll finish my DATAPAD before you!\p"
	.string "See you!$"

LilycoveCity_Text_MayYouGoingToBattleFrontier:
	.string "{PLAYER}{KUN}, what are you going to do?\p"
	.string "Are you taking the GRAND ARENA\n"
	.string "challenge?\p"
	.string "Or, are you going to complete your\n"
	.string "DATAPAD?\p"
	.string "I might've lost to you in battling,\n"
	.string "but I'll finish my DATAPAD before you!\p"
	.string "See you!$"

LilycoveCity_Text_BrendanShoppingLetsBattle:
	.string "KAEL: Oh, hey, it's {PLAYER}.\p"
	.string "I'm running an errand for my dad.\n"
	.string "No, I'm not buying any DOLLS.\p"
	.string "Anyways, it's been a while.\p"
	.string "Want to have a battle to see who's been\n"
	.string "raising COMPANIONS better?$"

LilycoveCity_Text_BrendanNoConfidence:
	.string "KAEL: Oh, what's the matter?\n"
	.string "Don't have the confidence?$"

LilycoveCity_Text_BrendanBattleMe:
	.string "KAEL: Want to battle to see who's\n"
	.string "been raising COMPANIONS better?$"

LilycoveCity_Text_BrendanWontBeBeaten:
	.string "KAEL: Aww, but you know I'm not\n"
	.string "going to lose to no {PLAYER}.$"

LilycoveCity_Text_BrendanDefeat:
	.string "Humph…\n"
	.string "You've done a lot of raising.\p"
	.string "That stings a bit--I had a head start\n"
	.string "on you as a TRAINER…$"

LilycoveCity_Text_BrendanGoingBackToLittleroot:
	.string "KAEL: I…\n"
	.string "I plan on going home to MOS PELGO.\p"
	.string "You know I'm helping out my dad on his\n"
	.string "DATAPAD. It's coming together pretty\l"
	.string "decently, so I should go show him.$"

LilycoveCity_Text_BrendanYouGoingToCollectBadges:
	.string "{PLAYER}, what are you going to do?\p"
	.string "Collect all the ARENA SHARDS and take\n"
	.string "the ILUM TEMPLE challenge?\p"
	.string "Maybe I'll do that, too…\p"
	.string "Well, anyway, hang in there!$"

LilycoveCity_Text_BrendanYouGoingToPokemonLeague:
	.string "{PLAYER}, what are you going to do?\p"
	.string "Since you're that strong, are you\n"
	.string "taking the ILUM TEMPLE challenge?\p"
	.string "Heh, even me--if I trained my\n"
	.string "COMPANIONS a bit more, I should be\l"
	.string "stronger than you, {PLAYER}.\p"
	.string "Well, anyway, hang in there!$"

LilycoveCity_Text_BrendanYouGoingToBattleFrontier:
	.string "{PLAYER}, what are you going to do?\p"
	.string "Are you taking the GRAND ARENA\n"
	.string "challenge?\p"
	.string "Or, are you going to complete your\n"
	.string "DATAPAD?\p"
	.string "Since you're that strong, you should\n"
	.string "consider the GRAND ARENA.\p"
	.string "Heh, if I train my COMPANIONS a bit more,\n"
	.string "I'll get stronger than you, {PLAYER}.\p"
	.string "Maybe I should go to the GRAND\n"
	.string "ARENA.\p"
	.string "Well, anyway, hang in there!$"

LilycoveCity_Text_MovedLootIntoHideoutToday:
	.string "Fufufu…\p"
	.string "We moved more loot into our secret\n"
	.string "HIDEOUT today…\p"
	.string "Wh-who are you?!\n"
	.string "I was just talking to myself!$"

LilycoveCity_Text_ChanceToDoBigThings:
	.string "I'm just a THUG, so I don't know what\n"
	.string "the mighty JABBA is thinking…\p"
	.string "But being in the CARTEL, I know I'll get\n"
	.string "the chance to do big things!\p"
	.string "Wh-who are you?!\n"
	.string "I was just talking to myself!$"

LilycoveCity_Text_DontGoNearCaveInCove:
	.string "Hey, you!\p"
	.string "Don't go near the old mine under\n"
	.string "the city!\p"
	.string "Why? You don't need a reason why!\n"
	.string "I'm an adult, so you just listen to me!$"

LilycoveCity_Text_IfWorldBecomesOurs:
	.string "If this whole wide galaxy becomes ours,\n"
	.string "the CARTEL's, it will be a happier\l"
	.string "place for COMPANIONS, too.$"

LilycoveCity_Text_WailmerLeapOutOfWater:
	.string "There! AIWHALET!\n"
	.string "Leap out of the clouds now!$"

LilycoveCity_Text_GetLostMessingUpTraining:
	.string "Hunh? What do you want?\p"
	.string "You're messing up our training,\n"
	.string "so can you, like, get lost?$"

LilycoveCity_Text_ContestHallInTown:
	.string "CLOUD CITY draws TRAINERS from\n"
	.string "all over the galaxy.\p"
	.string "That means well-raised COMPANIONS\n"
	.string "come through here every day.\p"
	.string "My heart swells with excitement!$"

LilycoveCity_Text_StrangeCaveInCove:
	.string "Have you seen that strange old mine\n"
	.string "in the under-levels of the city?$"

LilycoveCity_Text_GoingToMoveDeleterForHMs:
	.string "I'll teach my COMPANIONS some new\n"
	.string "moves for the GRAND ARENA.\p"
	.string "So, I'm going to see the MOVE DELETER\n"
	.string "and make it forget HM moves.$"

LilycoveCity_Text_ImFromKanto:
	.string "I came from the CORE WORLDS.\p"
	.string "The OUTER RIM is beautiful with\n"
	.string "all its wild worlds and nature.\p"
	.string "Hunh? Wait a second…\p"
	.string "Could there be rare COMPANIONS that\n"
	.string "live only in this area?$"

LilycoveCity_Text_TeamAquaBeenTrainingWailmer:
	.string "The CARTEL's been training their\n"
	.string "AIWHALET by the docks.\p"
	.string "We PILOTS can't get our cloud cars\n"
	.string "out with them in the way!$"

LilycoveCity_Text_SomeonePuntedTeamAquaOut:
	.string "Hey, did you know?\p"
	.string "Someone punted the CARTEL out of\n"
	.string "the way for us!\p"
	.string "That got the AIWHALET away from the\n"
	.string "docks, so our cloud cars can fly again.$"

LilycoveCity_Text_SomeoneStoleMyPokemon:
	.string "I was taking a relaxing snooze at the\n"
	.string "sky inn to the sound of the wind…\p"
	.string "When someone stole my COMPANION!\p"
	.string "Who's the abductor?\n"
	.string "The CARTEL? Is it the CARTEL?$"

LilycoveCity_Text_MissingPokemonCameBack:
	.string "My missing COMPANION…\n"
	.string "It came back without me noticing!$"

LilycoveCity_Text_ImArtDealer:
	.string "I'm an ART DEALER.\p"
	.string "I am a buyer and seller of fine art,\n"
	.string "especially paintings.\p"
	.string "I've heard that the MUSEUM here has\n"
	.string "magnificent works on exhibit…$"

LilycoveCity_Text_SeaRemainsForeverYoung:
	.string "Even as we grow old and wrinkled,\n"
	.string "the cloud sea remains forever young\l"
	.string "with the vivid brilliance of life…\p"
	.string "Fwohoho fwohohohoho…$"

LilycoveCity_Text_SixtyYearsAgoHusbandProposed:
	.string "It was sixty years ago that my husband\n"
	.string "proposed to me here.\l"
	.string "The clouds remain as beautiful as ever.\p"
	.string "Mufufufu mufufufufufu…$"

LilycoveCity_Text_TeamAquaRenovatedCavern:
	.string "Hm, you know of the old TIBANNA mine\n"
	.string "under the city?\p"
	.string "It had been abandoned for years,\n"
	.string "but then that CARTEL lot came\l"
	.string "along and made their renovations.\p"
	.string "They call themselves\n"
	.string "“honest businessmen”!\p"
	.string "But what they do and what they say\n"
	.string "don't match at all!$"

LilycoveCity_Text_TeamAquaLotGoneForGood:
	.string "That old mine under the city…\p"
	.string "I didn't notice it right away,\n"
	.string "but it's completely empty now.\p"
	.string "That CARTEL lot, they must\n"
	.string "have gone away for good.$"

LilycoveCity_Text_CitySign:
	.string "CLOUD CITY\p"
	.string "“The city that floats above\n"
	.string "the clouds.”$"

LilycoveCity_Text_ContestHallSign:
	.string "SHOWCASE HALL\n"
	.string "“The gathering place for TRAINERS!”$"

LilycoveCity_Text_MotelSign:
	.string "COVE LILY MOTEL\p"
	.string "“Remember us as COVE LILY of\n"
	.string "CLOUD CITY.”$"

LilycoveCity_Text_MuseumSign:
	.string "CLOUD CITY MUSEUM\p"
	.string "“COMPANION Masterpiece Collection\n"
	.string "on exhibit!”$"

LilycoveCity_Text_MuseumSignPlayersExhibit:
	.string "CLOUD CITY MUSEUM\p"
	.string "“{PLAYER}'s COMPANION Collection\n"
	.string "on exhibit!”$"

LilycoveCity_Text_HarborSignUnderConstruction:
	.string "CLOUD CITY LANDING PLATFORM\p"
	.string "“The starliner STAR TIDAL is under\n"
	.string "construction in MOS EISLEY.\p"
	.string "“Service is scheduled to begin\n"
	.string "shortly.”$"

LilycoveCity_Text_HarborSign:
	.string "CLOUD CITY LANDING PLATFORM\p"
	.string "“Enjoy a delightful cruise on\n"
	.string "the starliner STAR TIDAL.”$"

LilycoveCity_Text_TrainerFanClubSign:
	.string "COMPANION TRAINER FAN CLUB\p"
	.string "The names of TRAINERS are scribbled\n"
	.string "all over the sign…$"

LilycoveCity_Text_DepartmentStoreSign:
	.string "CLOUD CITY DEPARTMENT STORE\p"
	.string "“Overflowing with great merchandise\n"
	.string "and excitement!\p"
	.string "“A great place to find that something\n"
	.string "you need!”$"

LilycoveCity_Text_MoveDeletersHouseSign:
	.string "MOVE DELETER'S HOUSE\p"
	.string "“Unwanted COMPANION moves deleted.”$"

LilycoveCity_Text_DoYouKnowAboutBerryBlender:
	.string "Have you been to the GALLERIA?\p"
	.string "They sell all kinds of things on\n"
	.string "every floor. I could shop all day!$"

LilycoveCity_Text_FasterSpinBetterPokeblocks:
	.string "People have to work together to get it\n"
	.string "to spin faster.\p"
	.string "The faster you can make it spin, the\n"
	.string "better {POKEBLOCK}S you can get, I've heard.$"

LilycoveCity_Text_ExplainBerryBlender:
	.string "It's used for making a kind of candy\n"
	.string "called a {POKEBLOCK}.\p"
	.string "If you give a good {POKEBLOCK} to a POKéMON,\n"
	.string "its condition will improve by a lot.$"

LilycoveCity_Text_HeardTowerCalledSkyPillar:
	.string "I heard there's a tower somewhere out\n"
	.string "in the stars.\p"
	.string "It's called the ASTEROID SPIRE, I hear.$"

LilycoveCity_Text_SawTallTowerOnRoute131:
	.string "I saw this tall tower somewhere\n"
	.string "around ROUTE 131.\p"
	.string "Could that possibly be…?$"

LilycoveCity_Text_JustArrivedAndSawRarePokemon:
	.string "We just arrived here on our\n"
	.string "honeymoon vacation.\p"
	.string "We happened to see a DRAGON-type\n"
	.string "COMPANION flying way up in the sky.\p"
	.string "Do cool COMPANIONS like that live in\n"
	.string "the OUTER RIM region?$"

LilycoveCity_Text_HoneymoonVowToSeeRarePokemon:
	.string "On our honeymoon, we vowed to see as\n"
	.string "many rare COMPANIONS as we can.\p"
	.string "So we were delighted to see a rare\n"
	.string "COMPANION as soon as we arrived.\p"
	.string "I mean, we are totally happy!$"

LilycoveCity_Text_ShowcaseReceptionist:
	.string "Welcome to CLOUD CITY!\p"
	.string "The old hall here was torn down,\n"
	.string "so now we greet visitors outside.\p"
	.string "Enjoy the city breeze!$"

LilycoveCity_Text_ShowcaseLinkReceptionist:
	.string "I used to work at a counter inside.\p"
	.string "Now I just point lost travelers\n"
	.string "toward the GALLERIA and the\l"
	.string "BACTA CENTER!$"

LilycoveCity_Text_BlendMaster:
	.string "Hohoho! I am known as the\n"
	.string "BLEND MASTER.\p"
	.string "These days I blend nothing but tea.\p"
	.string "A fine cup and a fine view of the\n"
	.string "clouds… That is all I need!$"

LilycoveCity_Text_PlazaMan:
	.string "This square is the best place in\n"
	.string "CLOUD CITY to watch the sunset.$"

LilycoveCity_Text_PlazaTwin:
	.string "We play tag around the trees here.\n"
	.string "You're it!$"

LilycoveCity_Text_PlazaPokefanF:
	.string "My COMPANION loves the open sky.\n"
	.string "It can't stop looking at the clouds!$"

LilycoveCity_Text_Reporter:
	.string "I'm a reporter for the HOLONET.\p"
	.string "I'm looking for a good story in\n"
	.string "CLOUD CITY. Got any tips?$"

LilycoveCity_Text_PlazaBoy:
	.string "When I grow up, I want to battle\n"
	.string "at the GRAND ARENA!$"

LilycoveCity_Text_PlazaGirl:
	.string "The flowers here grow so well up\n"
	.string "above the clouds!$"

LilycoveCity_Text_Artist:
	.string "I'm painting the MUSEUM from out\n"
	.string "here. The light is just right!$"

LilycoveCity_Text_LittleGirl:
	.string "I'm waiting for my mom.\n"
	.string "She's shopping at the GALLERIA.$"

LilycoveCity_Text_Girl2:
	.string "Did you know the whole city floats\n"
	.string "on a single giant repulsorlift?$"

LilycoveCity_Text_FatMan2:
	.string "I came to CLOUD CITY for the food.\n"
	.string "I'm not leaving until I try it all!$"

LilycoveCity_Text_NinjaBoy:
	.string "I'm training my legs by walking\n"
	.string "up and down all day!$"

LilycoveCity_Text_BlackBelt:
	.string "I train my COMPANIONS in the wind\n"
	.string "of the cloud sea every morning. Hah!$"

LilycoveCity_Text_Fisherman:
	.string "They say you can't fish in a cloud\n"
	.string "sea. I'm going to prove them wrong!$"

LilycoveCity_Text_Sailor3:
	.string "I fly cargo between CLOUD CITY and\n"
	.string "the outer systems. Busy work!$"

LilycoveCity_Text_Boy1:
	.string "I'm exploring every corner of\n"
	.string "CLOUD CITY today!$"

LilycoveCity_Text_Boy2:
	.string "My big sister says the best TRAINERS\n"
	.string "all pass through CLOUD CITY.$"

LilycoveCity_Text_Girl3:
	.string "I like to sit here and watch the\n"
	.string "ships come and go.$"

LilycoveCity_Text_Judge1:
	.string "I spent years as a judge.\p"
	.string "Now I judge sunsets. Tonight's\n"
	.string "gets a perfect score!$"

LilycoveCity_Text_Judge2:
	.string "My eyes are trained to spot talent.\p"
	.string "You and your COMPANIONS have it.\n"
	.string "I'm sure of it!$"

LilycoveCity_Text_Judge3:
	.string "Retirement suits me.\p"
	.string "I watch the cloud cars go by and\n"
	.string "give each one a score.$"

LilycoveCity_Text_Host1:
	.string "I used to host big shows!\p"
	.string "Now I give tours of CLOUD CITY.\n"
	.string "Right this way, please!$"

LilycoveCity_Text_Host2:
	.string "Ladies and gentlemen…\p"
	.string "Oh, sorry. Old habits!$"

LilycoveCity_Text_Host3:
	.string "I still practice my announcer voice.\p"
	.string "CLOUD CITY! Wooo!$"

LilycoveCity_Text_TeaFan1:
	.string "The BLEND MASTER makes the best tea\n"
	.string "in the whole city. I'm here for a cup!$"

LilycoveCity_Text_TeaFan2:
	.string "I followed the BLEND MASTER all the\n"
	.string "way up here. He walks so fast!$"

LilycoveCity_Text_TeaFan3:
	.string "That old man by the plaza is the\n"
	.string "BLEND MASTER. He's famous!$"

LilycoveCity_Text_TeaFan4:
	.string "I'm studying how tibanna gas keeps\n"
	.string "the city afloat. Fascinating!$"

LilycoveCity_Text_TeaFan5:
	.string "I come here every day to relax.\n"
	.string "The air is so fresh up here.$"

LilycoveCity_Text_TeaFan6:
	.string "I'm a ninja! You didn't see me!\p"
	.string "Wait… You did see me?$"

LilycoveCity_Text_OldTimer:
	.string "I've lived in CLOUD CITY my whole\n"
	.string "life. It never gets old.$"

LilycoveCity_Text_Sketcher1:
	.string "I'm sketching the city skyline.\n"
	.string "Hold still, please!$"

LilycoveCity_Text_Sketcher2:
	.string "I paint the clouds every day.\n"
	.string "No two are ever the same.$"

LilycoveCity_Text_Trainer1:
	.string "My COMPANION and I train every day.\n"
	.string "We're aiming for the GRAND ARENA!$"

LilycoveCity_Text_Trainer2:
	.string "Wisdom comes with age. Good battles\n"
	.string "come with wisdom. Hohoho!$"

LilycoveCity_Text_Trainer3:
	.string "I know everything about COMPANIONS!\p"
	.string "Ask me anything! …Maybe later.$"

LilycoveCity_Text_Trainer4:
	.string "I sense great power in you…\p"
	.string "And in your COMPANIONS.$"

LilycoveCity_Text_Trainer5:
	.string "I'm going to beat every TRAINER\n"
	.string "in CLOUD CITY!$"

LilycoveCity_Text_Trainer6:
	.string "Raising COMPANIONS takes patience.\p"
	.string "And a lot of snacks.$"

LilycoveCity_Text_Shopper1:
	.string "Shopping is so tiring.\n"
	.string "I need a break.$"

LilycoveCity_Text_Shopper2:
	.string "I love browsing here, even when\n"
	.string "I don't buy anything.$"

LilycoveCity_Text_Shopper3:
	.string "Can I have that? No? Okay…$"

LilycoveCity_Text_Shopper4:
	.string "My husband is still upstairs.\n"
	.string "He always takes forever!$"

LilycoveCity_Text_Shopper5:
	.string "This place has everything!$"

LilycoveCity_Text_Shopper6:
	.string "I'm just waiting for my friend.\n"
	.string "She said five minutes an hour ago.$"

LilycoveCity_Text_Shopper7:
	.string "I came up from the under-levels.\n"
	.string "It's much brighter up here!$"

LilycoveCity_Text_Shopper8:
	.string "Have you tried the food in this city?\n"
	.string "It's out of this world!$"

LilycoveCity_Text_Shopper9:
	.string "I'm looking for a gift for my\n"
	.string "COMPANION. What would it like?$"

LilycoveCity_Text_Visitor1:
	.string "I'm lost! Where's my mom?$"

LilycoveCity_Text_Visitor2:
	.string "I'm on my day off.\n"
	.string "The paintings here are so calming.$"

LilycoveCity_Text_Visitor3:
	.string "My COMPANION's coat shines brighter\n"
	.string "than any painting in here!$"

LilycoveCity_Text_Guest1:
	.string "We're staying here on vacation!\n"
	.string "The view from our room is amazing!$"

LilycoveCity_Text_Guest2:
	.string "Brushing my COMPANION every night\n"
	.string "keeps it happy!$"

LilycoveCity_Text_Patient1:
	.string "My COMPANION can do a backflip!\p"
	.string "Well, almost. That's why we're here.$"

LilycoveCity_Text_Patient2:
	.string "I named my COMPANION after my\n"
	.string "favorite pilot!$"

