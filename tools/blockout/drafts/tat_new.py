import os; exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "common.py")).read())
H = "art:tatooine:homestead-dome"

# ---------------------------------------------------------------- BEN'S HUT (new, optional)
d = Draft.new("bens-hut", "BEN'S HUT", "TATOOINE", 26, 20, kind="landmark")
d.blob(13, 10, 11, 8, ".")
d.fill(0, 9, 0, 10, ".")
d.road([(0, 9), (12, 9)], 2, only=".T")
d.exit("west", [9, 10], "jundland-wastes")
d.building("Ben Kenobi's hut", H, 14, 4, 5, 4, door=2, to="bens-hut-interior")
d.road([(16, 8), (16, 9)], 1, only=".")
d.prop("Vaporator", "art:tatooine:moisture-vaporator", 21, 5, 1, 2)
d.prop("Sandstone boulder", "art:tatooine:sandstone-boulder", 6, 4, 2, 2)
d.prop("Rock spire", "art:tatooine:rock-spire", 20, 12, 2, 3)
d.prop("Bantha skeleton", "art:tatooine:bantha-skeleton", 9, 15, 1, 1)
d.person("Obi-Wan 'Ben' Kenobi", 15, 11, "story")
d.person("Tusken scout watching from the rocks", 5, 13, "trainer")
d.doc["story"] = "Optional: a hermit's hut on the edge of the Jundland Wastes. Obi-Wan, as old Ben, tells the player about the Force and the Cave of Evil long before he is needed."
d.doc["todo"] = ["New area: reached by a side path on the east edge of the Jundland Wastes.",
                 "New interior bens-hut-interior (one room, a chest, Ben's workbench).",
                 "New art rows needed: none (uses homestead-dome and planet-wide props)."]
link_all(d); d.save()

# ---------------------------------------------------------------- JABBA'S PALACE (new, optional)
d = Draft.new("jabbas-palace", "JABBA'S PALACE", "TATOOINE", 44, 34, kind="landmark")
d.blob(22, 18, 20, 15, ".", rough=0.1)
d.road([(0, 19), (22, 19)], 3)
d.fill(14, 18, 30, 22, ":")
d.exit("west", [19, 20, 21], "route-111")
d.building("Jabba's palace gate", "art:tatooine:jabbas-palace", 15, 4, 14, 9, door=7, to="jabbas-palace-throne-room")
d.road([(22, 13), (22, 17)], 1)
d.building("Sail barge dock shed", "art:tatooine:docking-bay", 33, 13, 6, 4, door=2, to="jabbas-palace-barge-dock")
d.road([(35, 17), (35, 19), (31, 19)], 1, only=".")
d.prop("Khetanna sail barge (moored)", "art:tatooine:sail-barge-wreck", 34, 22, 6, 3)
d.prop("Skiff", "art:shared:parked-landspeeder", 30, 26, 2, 1)
d.prop("Rancor pit grate", "art:tatooine:sarlacc-pit", 6, 15, 4, 4)
d.prop("Cargo crates", "art:shared:cargo-crates", 8, 24, 2, 2)
d.prop("Krayt bones", "art:tatooine:krayt-bones", 4, 9, 4, 3)
d.prop("Gonk droid", "art:shared:gonk-droid", 13, 23)
d.person("Cartel thug (gate guard)", 20, 14, "trainer"); d.person("Cartel thug (gate guard)", 24, 14, "trainer")
d.person("Cartel thug", 12, 20, "trainer"); d.person("Cartel thug", 31, 21, "trainer")
d.person("Bib Fortuna's errand droid", 26, 24); d.person("Jawa hoping to sell droids", 9, 22)
d.person("Bounty hunter waiting for work", 37, 28)
d.sign("Warning sign (in Huttese)", 6, 17)
d.doc["story"] = "Optional: Jabba's desert palace at the far edge of the Dune Sea. Cartel thugs guard the gate; inside, Jabba plots to catch the sea titan SANDO. A rematch ladder of Cartel trainers and a rancor pit."
d.doc["todo"] = ["New area: reached from a side track on Route 111's east edge.",
                 "New concept rows needed: art:tatooine:jabbas-palace (14x9 landmark), rancor pit (uses sarlacc-pit as a stand-in).",
                 "New interiors: jabbas-palace-throne-room, jabbas-palace-barge-dock.",
                 "Story check: Jabba is the Cartel boss after SANDO; this is a visit, not where he is beaten (that stays at the Hutt Hideout)."]
link_all(d); d.save()
