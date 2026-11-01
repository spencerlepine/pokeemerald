Move_CRUNCH:
	loadspritegfx ANIM_TAG_SW_FORCE_GRIP
	loadspritegfx ANIM_TAG_SW_FORCE_DUST
	monbg ANIM_TARGET
	setalpha 12, 8
	@ reach: the arena falls to the dark side, the attacker leans in
	fadetobg BG_FORCE_DARK
	waitbgfadeout
	createvisualtask AnimTask_SetPsychicBackground, 5
	waitbgfadein
	loopsewithpan SE_M_BITE, SOUND_PAN_TARGET, 16, 6	@ placeholder for SE_FORCE_CHOKE (net:se-force-choke)
	createvisualtask AnimTask_SW_Knockback, 5, ANIM_ATTACKER, -6, 8, 86, 10
	delay 10
	@ lift: the target rises off the ground and leans back
	createvisualtask AnimTask_SW_Lift, 5, ANIM_TARGET, 14, 30, 64, 4
	createvisualtask AnimTask_RotateMonSpriteToSide, 2, 8, -256, ANIM_TARGET, 0
	delay 20
	createsprite gForceGripSpriteTemplate, ANIM_TARGET, 4, -8, -12, 1, 0
	delay 20
	@ squeeze: shaking in the air, darkening, the grip clenches three times
	createvisualtask AnimTask_ShakeMonInPlace, 2, ANIM_TARGET, 2, 0, 24, 1
	simple_palette_blend selector=F_PAL_TARGET, delay=2, initial_blend_y=0, target_blend_y=7, color=RGB_BLACK
	delay 10
	playsewithpan SE_M_BIND, SOUND_PAN_TARGET
	invert_screen_color scenery=TRUE, attacker=TRUE, target=TRUE
	delay 1
	invert_screen_color scenery=TRUE, attacker=TRUE, target=TRUE
	delay 15
	playsewithpan SE_M_BIND, SOUND_PAN_TARGET
	invert_screen_color scenery=TRUE, attacker=TRUE, target=TRUE
	delay 1
	invert_screen_color scenery=TRUE, attacker=TRUE, target=TRUE
	delay 15
	playsewithpan SE_M_BIND, SOUND_PAN_TARGET
	invert_screen_color scenery=TRUE, attacker=TRUE, target=TRUE
	delay 1
	invert_screen_color scenery=TRUE, attacker=TRUE, target=TRUE
	delay 12
	@ drop: it falls, hits the floor, dust
	playsewithpan SE_M_TAKE_DOWN, SOUND_PAN_TARGET
	createvisualtask AnimTask_RotateMonSpriteToSide, 2, 8, -256, ANIM_TARGET, 1
	delay 4
	createvisualtask AnimTask_ShakeMon, 5, ANIM_TARGET, 0, 4, 6, 1
	createsprite gForceDustSpriteTemplate, ANIM_TARGET, 2, -14, 18, 1, 0
	createsprite gForceDustSpriteTemplate, ANIM_TARGET, 2, 12, 20, 1, 0
	simple_palette_blend selector=F_PAL_TARGET, delay=2, initial_blend_y=7, target_blend_y=0, color=RGB_BLACK
	waitforvisualfinish
	clearmonbg ANIM_TARGET
	blendoff
	delay 1
	restorebg
	waitbgfadeout
	setarg 7, 0xFFFF
	waitbgfadein
	end
