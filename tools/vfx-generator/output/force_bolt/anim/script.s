Move_SHOCK_WAVE:
	loadspritegfx ANIM_TAG_SW_FORCE_ARC
	loadspritegfx ANIM_TAG_ELECTRIC_ORBS
	loadspritegfx ANIM_TAG_SW_BLASTER_SMOKE
	monbg ANIM_TARGET
	setalpha 12, 8
	@ charge: dark-side backdrop, energy collapses into the attacker
	fadetobg BG_FORCE_DARK
	waitbgfadeout
	createvisualtask AnimTask_SetPsychicBackground, 5
	waitbgfadein
	createvisualtask AnimTask_ElectricChargingParticles, 2, ANIM_ATTACKER, 20, 0, 2
	playsewithpan SE_M_CHARGE, SOUND_PAN_ATTACKER
	createvisualtask AnimTask_BlendMonInAndOut, 5, ANIM_ATTACKER, RGB(20, 24, 31), 10, 2, 2
	delay 24
	@ arcs: three forked arcs crawl from the attacker to the target
	loopsewithpan SE_M_THUNDERBOLT, SOUND_PAN_TARGET, 9, 4	@ placeholder for SE_FORCE_LIGHTNING (net:se-force-lightning)
	createsprite gForceArcSpriteTemplate, ANIM_TARGET, 3, 0, 0, 36, 0
	invert_screen_color scenery=TRUE, attacker=TRUE, target=TRUE
	delay 1
	invert_screen_color scenery=TRUE, attacker=TRUE, target=TRUE
	createvisualtask AnimTask_ShakeMon, 5, ANIM_TARGET, 2, 0, 18, 1
	delay 3
	createsprite gForceArcSpriteTemplate, ANIM_TARGET, 3, -10, -8, 32, 1
	delay 4
	createsprite gForceArcSpriteTemplate, ANIM_TARGET, 3, 10, 6, 28, 2
	delay 4
	invert_screen_color scenery=TRUE, attacker=TRUE, target=TRUE
	delay 1
	invert_screen_color scenery=TRUE, attacker=TRUE, target=TRUE
	delay 11
	invert_screen_color scenery=TRUE, attacker=TRUE, target=TRUE
	delay 1
	invert_screen_color scenery=TRUE, attacker=TRUE, target=TRUE
	delay 12
	@ impact: white flashes, the pattern shake, a moment of black, smoke
	playsewithpan SE_M_TRI_ATTACK2, SOUND_PAN_TARGET
	createvisualtask AnimTask_BlendMonInAndOut, 5, ANIM_TARGET, RGB_WHITE, 12, 2, 1
	createvisualtask AnimTask_ShakeTargetInPattern, 2, 30, 3, TRUE, 0
	delay 8
	simple_palette_blend selector=F_PAL_TARGET, delay=0, initial_blend_y=8, target_blend_y=8, color=RGB_BLACK
	delay 12
	simple_palette_blend selector=F_PAL_TARGET, delay=1, initial_blend_y=8, target_blend_y=0, color=RGB_BLACK
	createsprite gBlasterSmokeSpriteTemplate, ANIM_TARGET, 2, -6, 2, -1
	delay 6
	createsprite gBlasterSmokeSpriteTemplate, ANIM_TARGET, 2, 6, 0, 1
	waitforvisualfinish
	clearmonbg ANIM_TARGET
	blendoff
	delay 1
	restorebg
	waitbgfadeout
	setarg 7, 0xFFFF
	waitbgfadein
	end
