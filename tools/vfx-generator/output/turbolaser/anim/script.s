Move_HYPER_BEAM:
	loadspritegfx ANIM_TAG_SW_TURBOLASER_BEAM
	loadspritegfx ANIM_TAG_EXPLOSION
	loadspritegfx ANIM_TAG_SW_BLASTER_SMOKE
	@ charge: lights out, green energy gathers at the attacker
	simple_palette_blend selector=F_PAL_BG, delay=3, initial_blend_y=0, target_blend_y=16, color=RGB_BLACK
	waitforvisualfinish
	playsewithpan SE_M_CHARGE, SOUND_PAN_ATTACKER	@ placeholder for SE_TURBOLASER_CHARGE (net:se-turbolaser-charge)
	createsprite gTurbolaserChargeSpriteTemplate, ANIM_ATTACKER, 3, 22, -4, 0, 0
	createvisualtask AnimTask_BlendMonInAndOut, 5, ANIM_ATTACKER, RGB(8, 31, 10), 10, 3, 3
	createvisualtask AnimTask_ShakeMon, 2, ANIM_ATTACKER, 1, 0, 22, 1
	delay 44
	@ fire: the beam streams in, the arena shakes for the whole burst
	createsoundtask SoundTask_LoopSEAdjustPanning, SE_M_HYPER_BEAM, SOUND_PAN_ATTACKER, SOUND_PAN_TARGET, 1, 15, 0, 5	@ placeholder for SE_TURBOLASER (net:se-turbolaser)
	createvisualtask AnimTask_HorizontalShake, 5, MAX_BATTLERS_COUNT + 1, 3, 60
	call TurbolaserBurst
	call TurbolaserBurst
	@ impact: the target blinds white and shakes; explosions pop on it
	createvisualtask AnimTask_ShakeMon2, 2, ANIM_TARGET, 4, 0, 40, 1
	createvisualtask AnimTask_BlendBattleAnimPal, 10, F_PAL_TARGET, 2, 0, 11, RGB(25, 31, 25)
	playsewithpan SE_M_EXPLOSION, SOUND_PAN_TARGET
	createsprite gExplosionSpriteTemplate, ANIM_ATTACKER, 3, 0, -4, 1, 1
	call TurbolaserBurst
	delay 2
	playsewithpan SE_M_EXPLOSION, SOUND_PAN_TARGET
	createsprite gExplosionSpriteTemplate, ANIM_ATTACKER, 3, 14, -14, 1, 1
	call TurbolaserBurst
	delay 2
	playsewithpan SE_M_EXPLOSION, SOUND_PAN_TARGET
	createsprite gExplosionSpriteTemplate, ANIM_ATTACKER, 3, -10, 6, 1, 1
	call TurbolaserBurst
	delay 2
	playsewithpan SE_M_EXPLOSION, SOUND_PAN_TARGET
	createsprite gExplosionSpriteTemplate, ANIM_ATTACKER, 3, 8, 10, 1, 1
	call TurbolaserBurst
	delay 2
	playsewithpan SE_M_EXPLOSION, SOUND_PAN_TARGET
	createsprite gExplosionSpriteTemplate, ANIM_ATTACKER, 3, -14, -12, 1, 1
	call TurbolaserBurst
	delay 2
	playsewithpan SE_M_EXPLOSION, SOUND_PAN_TARGET
	createsprite gExplosionSpriteTemplate, ANIM_ATTACKER, 3, 4, 0, 1, 1
	call TurbolaserBurst
	delay 2
	call TurbolaserBurst
	call TurbolaserBurst
	createvisualtask AnimTask_BlendBattleAnimPal, 10, F_PAL_TARGET, 2, 11, 0, RGB(25, 31, 25)
	@ recharge: the beam stops, smoke, lights up
	delay 10
	createsprite gBlasterSmokeSpriteTemplate, ANIM_TARGET, 2, -8, 2, -1
	delay 4
	createsprite gBlasterSmokeSpriteTemplate, ANIM_TARGET, 2, 6, -2, 1
	waitforvisualfinish
	simple_palette_blend selector=F_PAL_BG, delay=3, initial_blend_y=16, target_blend_y=0, color=RGB_BLACK
	waitforvisualfinish
	end
TurbolaserBurst:
	createsprite gTurbolaserSegmentSpriteTemplate, ANIM_TARGET, 2, 20, -4, 0, 0, 8
	delay 1
	createsprite gTurbolaserSegmentSpriteTemplate, ANIM_TARGET, 2, 20, -2, 2, 2, 8
	delay 1
	createsprite gTurbolaserSegmentSpriteTemplate, ANIM_TARGET, 2, 20, -4, -2, -1, 8
	delay 1
	createsprite gTurbolaserSegmentSpriteTemplate, ANIM_TARGET, 2, 20, -3, 1, -2, 8
	delay 1
	return
	end
