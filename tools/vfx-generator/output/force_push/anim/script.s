Move_PSYCHIC:
	loadspritegfx ANIM_TAG_SW_FORCE_RING
	loadspritegfx ANIM_TAG_SW_FORCE_DUST
	monbg ANIM_DEF_PARTNER
	setalpha 8, 8
	@ gather: the arena falls into the Force, the attacker rears, a ring closes on it
	fadetobg BG_FORCE
	waitbgfadeout
	createvisualtask AnimTask_SetPsychicBackground, 5
	waitbgfadein
	playsewithpan SE_M_CHARGE, SOUND_PAN_ATTACKER
	createvisualtask AnimTask_RotateMonSpriteToSide, 2, 8, -256, ANIM_ATTACKER, 0
	createsprite gForceGatherRingSpriteTemplate, ANIM_ATTACKER, 3, 0, 0, 0, 0
	createvisualtask AnimTask_BlendMonInAndOut, 5, ANIM_ATTACKER, RGB(20, 24, 31), 10, 1, 1
	delay 22
	@ push: three rings leave the attacker, the arena shudders
	playsewithpan SE_M_SUPERSONIC, SOUND_PAN_ATTACKER	@ placeholder for SE_FORCE_PUSH (net:se-force-push)
	createsprite gForceRingSpriteTemplate, ANIM_TARGET, 3, 16, 0, 0, 0, 14, 0
	createvisualtask AnimTask_HorizontalShake, 5, MAX_BATTLERS_COUNT + 1, 2, 16
	delay 5
	createsprite gForceRingSpriteTemplate, ANIM_TARGET, 3, 16, 0, 0, 0, 14, 0
	delay 5
	createsprite gForceRingSpriteTemplate, ANIM_TARGET, 3, 16, 0, 0, 0, 14, 0
	delay 6
	@ impact: shoved back, squashed, dust at its feet, shaken; then it slides home
	playsewithpan SE_M_TAKE_DOWN, SOUND_PAN_TARGET
	createvisualtask AnimTask_SW_Knockback, 5, ANIM_TARGET, 20, 6, 14, 20
	createvisualtask AnimTask_ScaleMonAndRestore, 5, -20, 20, 8, ANIM_TARGET, 1
	createvisualtask AnimTask_BlendMonInAndOut, 5, ANIM_TARGET, RGB_WHITE, 12, 1, 1
	createsprite gForceDustSpriteTemplate, ANIM_TARGET, 2, -14, 18, 1, 0
	createsprite gForceDustSpriteTemplate, ANIM_TARGET, 2, 10, 20, 1, 0
	delay 6
	createvisualtask AnimTask_ShakeMon, 5, ANIM_TARGET, 0, 3, 10, 1
	createvisualtask AnimTask_RotateMonSpriteToSide, 2, 8, -256, ANIM_ATTACKER, 1
	waitforvisualfinish
	@ settle
	clearmonbg ANIM_DEF_PARTNER
	blendoff
	delay 1
	restorebg
	waitbgfadeout
	setarg 7, 0xFFFF
	waitbgfadein
	end
