Move_SLASH:
	loadspritegfx ANIM_TAG_SW_SABER_BLADE
	loadspritegfx ANIM_TAG_SW_SABER_BLADE_RED
	loadspritegfx ANIM_TAG_SW_SABER_ARC
	loadspritegfx ANIM_TAG_SW_SABER_SCORCH
	loadspritegfx ANIM_TAG_IMPACT
	monbg ANIM_TARGET
	setalpha 12, 8
	@ ignite: the arena dims, the blade snaps out beside the attacker
	simple_palette_blend selector=F_PAL_BG, delay=2, initial_blend_y=0, target_blend_y=6, color=RGB_BLACK
	createvisualtask AnimTask_IsTargetPlayerSide, 2
	jumprettrue SaberSlashRedBlade
	createsprite gSaberBladeSpriteTemplate, ANIM_ATTACKER, 2, 18, -16, 0, 0
	goto SaberSlashIgnite
SaberSlashRedBlade:
	createsprite gSaberBladeRedSpriteTemplate, ANIM_ATTACKER, 2, 18, -16, 0, 0
SaberSlashIgnite:
	playsewithpan SE_SABER_IGNITE, SOUND_PAN_ATTACKER
	delay 10
	loopsewithpan SE_SABER_HUM, SOUND_PAN_ATTACKER, 12, 4
	@ lunge
	createvisualtask AnimTask_WindUpLunge, 2, ANIM_ATTACKER, -8, 0, 8, 6, 14, 6
	delay 16
	@ slash: crossing arcs over the target, a one-frame flash
	playsewithpan SE_M_RAZOR_WIND, SOUND_PAN_TARGET	@ placeholder for SE_SABER_SWING (net:se-saber-swing)
	createvisualtask AnimTask_IsTargetPlayerSide, 2
	jumprettrue SaberSlashRedArc
	createsprite gSaberArcSpriteTemplate, ANIM_TARGET, 3, 0, -4, 1, 0
	goto SaberSlashImpact
SaberSlashRedArc:
	createsprite gSaberArcRedSpriteTemplate, ANIM_TARGET, 3, 0, -4, 1, 0
SaberSlashImpact:
	delay 3
	invert_screen_color scenery=TRUE, attacker=TRUE, target=TRUE
	delay 1
	invert_screen_color scenery=TRUE, attacker=TRUE, target=TRUE
	@ impact: white flash, hard shake, hitsplat, scorch mark
	createvisualtask AnimTask_BlendMonInAndOut, 5, ANIM_TARGET, RGB_WHITE, 12, 2, 1
	createvisualtask AnimTask_ShakeMon, 5, ANIM_TARGET, 0, 8, 12, 1
	playsewithpan SE_M_RAZOR_WIND, SOUND_PAN_TARGET
	create_basic_hitsplat_sprite ANIM_ATTACKER, 2, x=0, y=-2, relative_to=ANIM_TARGET, animation=1
	createsprite gSaberScorchSpriteTemplate, ANIM_TARGET, 4, 2, 6, 1, 0
	delay 26
	@ retract (the blade anim plays its last frames), lights up
	playsewithpan SE_M_SWORDS_DANCE, SOUND_PAN_ATTACKER	@ placeholder for SE_SABER_RETRACT (net:se-saber-retract)
	waitforvisualfinish
	clearmonbg ANIM_TARGET
	blendoff
	simple_palette_blend selector=F_PAL_BG, delay=2, initial_blend_y=6, target_blend_y=0, color=RGB_BLACK
	waitforvisualfinish
	end
