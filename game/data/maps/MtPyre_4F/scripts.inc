MtPyre_4F_MapScripts::
	.byte 0

@ Seems like the scripts for the 4F and 5F were swapped

MtPyre_5F_EventScript_Atsushi::
	trainerbattle_single TRAINER_ATSUSHI, MtPyre_5F_Text_AtsushiIntro, MtPyre_5F_Text_AtsushiDefeat
	msgbox MtPyre_5F_Text_AtsushiPostBattle, MSGBOX_AUTOCLOSE
	end

MtPyre_5F_Text_AtsushiIntro:
	.string "Hrrrmmm…\p"
	.string "(Elders of the forest…\n"
	.string "please watch over my progress!)$"

MtPyre_5F_Text_AtsushiDefeat:
	.string "Hrrnnn…\p"
	.string "(Elders… please forgive me!)$"

MtPyre_5F_Text_AtsushiPostBattle:
	.string "Until I improve, my teacher, who rests\n"
	.string "here, will never find true peace…$"

