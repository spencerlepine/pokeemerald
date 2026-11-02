import os; exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "common.py")).read())
HUT = "art:kashyyyk:wookiee-hut"
TREE = ("Wroshyr tree", "art:kashyyyk:wroshyr-tree", 3, 3)

# ---------------------------------------------------------------- KACHIRHO (Dewford)
d = Draft.load("kachirho"); d.g = [["T"] * 46 for _ in range(38)]; d.clear(); d.doc["exits"] = []; d.doc["status"] = "BLOCKOUT"
d.blob(23, 16, 20, 14, ".")
d.fill(0, 28, 45, 37, "~")                                  # the lagoon
d.blob(23, 27, 18, 4, ".", only="~T")                       # beach
d.road([(22, 0), (22, 26)], 2)
d.road([(23, 13), (45, 13)], 2)
d.exit("north", [22, 23], "route-106"); d.exit("east", [13, 14], "route-107")
# tree-city level: platforms on the giant trunks, joined by walkways, ladders down
d.fill(4, 4, 15, 9, "="); d.fill(29, 3, 41, 8, "="); d.fill(16, 6, 28, 6, "=")
d.set(9, 10, "H"); d.set(35, 9, "H"); d.set(9, 11, "."); d.set(35, 10, ".")
d.building("Tarfful's arena hall", "art:kashyyyk:arena-hall", 31, 3, 7, 5, door=3, to="kachirho-arena", ground="=")
d.building("Great hall (HoloNet trends)", HUT, 6, 4, 5, 4, door=2, to="kachirho-hall", ground="=")
d.building("Bacta Center", "art:shared:bacta-center", 4, 15, 5, 4, door=2, to="kachirho-bacta-center-1f")
d.road([(6, 19), (6, 20), (21, 20)], 1, only=".")
d.building("Supply Depot", "art:shared:supply-depot", 13, 15, 4, 4, door=1, to="kachirho-supply-depot")
d.building("Wookiee family hut", HUT, 30, 17, 5, 4, door=2, to="kachirho-house-1")
d.road([(32, 21), (32, 22)], 1, only=".")
d.building("Elder's hut", HUT, 38, 17, 5, 4, door=2, to="kachirho-house-2")
d.building("Falcon hangar (from Tatooine)", "art:tatooine:docking-bay", 34, 23, 8, 4, door=3, to="hangar-tatooine-kashyyyk")
d.prop("Catamaran dock", "art:kashyyyk:catamaran-dock", 12, 28, 4, 3)
d.prop("Millennium Falcon (landed)", "art:shared:landing-pad", 26, 22, 4, 4)
for x, y in ((1, 11), (40, 10), (1, 21), (17, 10), (26, 9)):
    d.prop(*TREE, )if False else d.prop("Wroshyr tree", "art:kashyyyk:wroshyr-tree", x, y, 3, 3)
d.prop("Bowcaster rack", "art:kashyyyk:bowcaster-rack", 29, 13)
d.prop("Root arch", "art:kashyyyk:root-arch", 5, 24, 3, 2)
d.person("Tarfful", 34, 9, "story"); d.person("Han Solo", 27, 26, "story"); d.person("Chewie (after the rescue)", 29, 26, "story")
d.person("Wookiee guard", 21, 10); d.person("Wookiee fisher", 16, 31 - 4); d.person("Trader from Mos Eisley", 10, 21)
d.person("Wookiee cub", 24, 17)
d.sign("Town sign", 20, 3); d.sign("Arena sign", 38, 8)
d.doc["story"] = "Wookiee lagoon city at the foot of the wroshyr trees. The Falcon lands by the beach; Tarfful's Fighting arena and the great hall sit up on the tree platforms, reached by ladders."
d.doc["todo"] = ["Vanilla Dewford has no Supply Depot; one is added (new interior kachirho-supply-depot).",
                 "The tree platforms are one level up; ladders at the west and east trunks."]
link_all(d); d.save()

retheme("route-105", "Open lagoon north of Kachirho between wroshyr islets. The Ice Grotto sits on a cold islet. Vanilla's north edge (Tatooine's Route 104) is cut.",
        props=[TREE + ((20, 30),), ("Beach rocks", "art:kashyyyk:beach-rocks", 1, 1, (8, 22))])
retheme("route-106", "Shore path west of Kachirho to the Shadowlands, the dark lower levels of the wroshyr forest.",
        props=[TREE + ((40, 10),), ("Root arch", "art:kashyyyk:root-arch", 3, 2, (50, 12)), ("Fern clump", "art:kashyyyk:fern-clump", 1, 1, (55, 15))])
retheme("route-107", extra=lambda d: open_exit(d, "north", 30, "rwookrrorro"), story="Lagoon crossing east of Kachirho, swimmers and fishers on the water. A trail north climbs a wroshyr trunk to Rwookrrorro.",
        props=[("Beach rocks", "art:kashyyyk:beach-rocks", 1, 1, (20, 10))])
retheme("route-108", "Open water around the Republic Wreck, a cruiser that went down in the Battle of Kashyyyk.",
        props=[("Republic cruiser hull", "art:kashyyyk:cruiser-hull", 8, 4, (30, 10))])
retheme("route-109", "Kashyyyk's southern beach and its seaside hut. Vanilla's north edge to Mos Eisley is cut: Kashyyyk is reached by the Falcon.",
        art_house=HUT, props=[TREE + ((20, 20),), ("Catamaran dock", "art:kashyyyk:catamaran-dock", 4, 3, (15, 10))])
for a, s in [("shadowlands-1f", "Dark lower levels of the wroshyr forest, first level: roots and hollow trunks."),
             ("shadowlands-b1f", "Shadowlands, lower: cracked root floors that drop to the level below."),
             ("shadowlands-b2f", "Shadowlands, deepest level, where Leia waits."),
             ("shadowlands-leias-room", "The hollow where Leia waits with Sen. Organa's message."),
             ("ice-grotto", "Cold cave on a lagoon islet; home of ICEWARDEN."),
             ("republic-wreck-deck", "Republic Wreck: the tilted deck above water."),
             ("republic-wreck-corridors-1f", "Republic Wreck: crew corridors."), ("republic-wreck-corridors-b1f", "Republic Wreck: flooded lower corridors."),
             ("republic-wreck-rooms-1f", "Republic Wreck: crew cabins."), ("republic-wreck-rooms-2-1f", "Republic Wreck: officers' cabins."),
             ("republic-wreck-rooms-b1f", "Republic Wreck: flooded cabins."), ("republic-wreck-rooms-2-b1f", "Republic Wreck: flooded officers' cabins."),
             ("republic-wreck-room-b1f", "Republic Wreck: storeroom."), ("republic-wreck-captains-office", "Republic Wreck: the captain's office and the scanner part."),
             ("republic-wreck-hidden-floor-corridors", "Republic Wreck: the sealed hold, opened with keys found aboard."),
             ("republic-wreck-hidden-floor-rooms", "Republic Wreck: sealed hold rooms with the keys' prizes."),
             ("republic-wreck-underwater-1", "Republic Wreck: dive into the sunken hull."), ("republic-wreck-underwater-2", "Republic Wreck: the sunken hull's inner room."),
             ("underwater-route-105", "Under the lagoon on Route 105.")]:
    retheme(a, s)

# ---------------------------------------------------------------- RWOOKRRORRO (new, optional)
d = Draft.new("rwookrrorro", "RWOOKRRORRO", "KASHYYYK", 36, 28, kind="landmark")
d.fill(0, 0, 35, 27, "T")
d.blob(18, 14, 15, 11, "=")
d.fill(17, 24, 18, 27, "H")
d.exit("south", [17, 18], "route-107")
d.building("Chieftain's hut", HUT, 15, 4, 5, 4, door=2, to="rwookrrorro-chief-hut", ground="=")
d.building("Weaver's hut", HUT, 6, 16, 5, 4, door=2, to="rwookrrorro-hut-1", ground="=")
d.building("Bowcaster maker's hut", HUT, 25, 16, 5, 4, door=2, to="rwookrrorro-hut-2", ground="=")
d.prop("Wroshyr tree", "art:kashyyyk:wroshyr-tree", 27, 6, 3, 3)
d.prop("Wroshyr tree", "art:kashyyyk:wroshyr-tree", 6, 6, 3, 3)
d.prop("Bowcaster rack", "art:kashyyyk:bowcaster-rack", 24, 13)
d.person("Wookiee elder", 18, 11); d.person("Wookiee hunter", 12, 14, "trainer"); d.person("Wookiee hunter", 23, 21, "trainer")
d.person("Wookiee cub", 18, 19)
d.doc["story"] = "Optional: a Wookiee village built across the treetops east of Kachirho, all on one high platform level. Wookiee hunters battle here and a bowcaster maker trades."
d.doc["todo"] = ["New area off Route 107's north edge (a ladder up a wroshyr trunk).", "New interiors: rwookrrorro-chief-hut, rwookrrorro-hut-1, rwookrrorro-hut-2 (Wookiee hut kit)."]
link_all(d); d.save()
