Move_SWIFT:
	loadspritegfx ANIM_TAG_SW_BLASTER_BOLT
	loadspritegfx ANIM_TAG_SW_BLASTER_FX
	loadspritegfx ANIM_TAG_SW_BLASTER_SMOKE
	monbg ANIM_DEF_PARTNER
	setalpha 12, 8
	@ aim: the targeting bracket blinks on the target
	createsprite gBlasterLockSpriteTemplate, ANIM_TARGET, 4, 0, 0, 1, 0
	playsewithpan SE_M_LOCK_ON, SOUND_PAN_TARGET	@ placeholder for SE_TARGET_LOCK (net:se-target-lock)
	delay 16
	@ fire x5, fanned
	@ bolt 1
	createsprite gBlasterFlashSpriteTemplate, ANIM_ATTACKER, 3, 22, -6, 0, 0
	createsprite gBlasterBoltSpriteTemplate, ANIM_TARGET, 3, 20, -6, -4, -6, 10
	playsewithpan SE_BLASTER_BOLT, SOUND_PAN_ATTACKER
	delay 10
	createsprite gBlasterImpactSpriteTemplate, ANIM_TARGET, 4, -4, -6, 1, 0
	playsewithpan SE_M_SWIFT, SOUND_PAN_TARGET	@ placeholder for SE_BLASTER_IMPACT (net:se-blaster-impact)
	createvisualtask AnimTask_ShakeMon, 5, ANIM_TARGET, 2, 0, 4, 1
	@ bolt 2
	createsprite gBlasterFlashSpriteTemplate, ANIM_ATTACKER, 3, 22, -6, 0, 0
	createsprite gBlasterBoltSpriteTemplate, ANIM_TARGET, 3, 20, -6, 6, 2, 10
	playsewithpan SE_BLASTER_BOLT, SOUND_PAN_ATTACKER
	delay 10
	createsprite gBlasterImpactSpriteTemplate, ANIM_TARGET, 4, 6, 2, 1, 0
	playsewithpan SE_M_SWIFT, SOUND_PAN_TARGET	@ placeholder for SE_BLASTER_IMPACT (net:se-blaster-impact)
	createvisualtask AnimTask_ShakeMon, 5, ANIM_TARGET, 2, 0, 4, 1
	@ bolt 3
	createsprite gBlasterFlashSpriteTemplate, ANIM_ATTACKER, 3, 22, -10, 0, 0
	createsprite gBlasterBoltSpriteTemplate, ANIM_TARGET, 3, 20, -10, -2, 6, 10
	playsewithpan SE_BLASTER_BOLT, SOUND_PAN_ATTACKER
	delay 10
	createsprite gBlasterImpactSpriteTemplate, ANIM_TARGET, 4, -2, 6, 1, 0
	playsewithpan SE_M_SWIFT, SOUND_PAN_TARGET	@ placeholder for SE_BLASTER_IMPACT (net:se-blaster-impact)
	createvisualtask AnimTask_ShakeMon, 5, ANIM_TARGET, 2, 0, 4, 1
	@ bolt 4
	createsprite gBlasterFlashSpriteTemplate, ANIM_ATTACKER, 3, 22, -4, 0, 0
	createsprite gBlasterBoltSpriteTemplate, ANIM_TARGET, 3, 20, -4, 8, -4, 10
	playsewithpan SE_BLASTER_BOLT, SOUND_PAN_ATTACKER
	delay 10
	createsprite gBlasterImpactSpriteTemplate, ANIM_TARGET, 4, 8, -4, 1, 0
	playsewithpan SE_M_SWIFT, SOUND_PAN_TARGET	@ placeholder for SE_BLASTER_IMPACT (net:se-blaster-impact)
	createvisualtask AnimTask_ShakeMon, 5, ANIM_TARGET, 2, 0, 4, 1
	@ bolt 5
	createsprite gBlasterFlashSpriteTemplate, ANIM_ATTACKER, 3, 22, -8, 0, 0
	createsprite gBlasterBoltSpriteTemplate, ANIM_TARGET, 3, 20, -8, 0, 0, 10
	playsewithpan SE_BLASTER_BOLT, SOUND_PAN_ATTACKER
	delay 10
	createsprite gBlasterImpactSpriteTemplate, ANIM_TARGET, 4, 0, 0, 1, 0
	playsewithpan SE_M_SWIFT, SOUND_PAN_TARGET	@ placeholder for SE_BLASTER_IMPACT (net:se-blaster-impact)
	createvisualtask AnimTask_ShakeMon, 5, ANIM_TARGET, 6, 0, 10, 1
	@ aftermath: smoke rises, the target darkens a moment
	simple_palette_blend selector=F_PAL_TARGET, delay=1, initial_blend_y=0, target_blend_y=5, color=RGB_BLACK
	createsprite gBlasterSmokeSpriteTemplate, ANIM_TARGET, 2, -8, 4, -1
	delay 4
	createsprite gBlasterSmokeSpriteTemplate, ANIM_TARGET, 2, 6, 0, 1
	delay 4
	createsprite gBlasterSmokeSpriteTemplate, ANIM_TARGET, 2, 0, 8, 0
	delay 12
	simple_palette_blend selector=F_PAL_TARGET, delay=1, initial_blend_y=5, target_blend_y=0, color=RGB_BLACK
	waitforvisualfinish
	clearmonbg ANIM_DEF_PARTNER
	blendoff
	end
