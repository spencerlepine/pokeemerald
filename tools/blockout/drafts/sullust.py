import os; exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "common.py")).read())
HOME = "art:sullust:sullustan-home"
def fresh(area_id, w, h, fill="T"):
    d = Draft.load(area_id); d.g = [[fill] * w for _ in range(h)]
    d.clear(); d.doc["exits"] = []; d.doc["status"] = "BLOCKOUT"; return d

# ---------------------------------------------------------------- PIRIN (Lavaridge)
d = fresh("pirin", 42, 34, "#")
d.blob(21, 17, 19, 15, ".")
d.blob(12, 24, 6, 4, "~")                          # hot spring pool
d.road([(20, 2), (20, 32)], 2)
d.fill(15, 14, 26, 19, ":")
d.warp("Magma Tunnels mouth", 20, 2, "magma-tunnels")
d.building("Sabine's arena", "art:sullust:sabine-s-arena", 4, 6, 7, 5, door=3, to="pirin-arena-1f")
d.road([(7, 11), (7, 16), (19, 16)], 1, only=".")
d.building("Hot-spring bathhouse", "art:sullust:hot-spring-bathhouse", 5, 18, 6, 4, door=3, to="pirin-herb-shop")
d.building("Bacta Center", "art:shared:bacta-center", 25, 5, 5, 4, door=2, to="pirin-bacta-center-1f")
d.road([(27, 9), (27, 13)], 1, only=".")
d.building("Supply Depot", "art:shared:supply-depot", 33, 7, 4, 4, door=1, to="pirin-supply-depot")
d.road([(34, 11), (34, 15), (27, 15)], 1, only=".")
d.building("Sullustan home", HOME, 27, 21, 5, 4, door=2, to="pirin-house")
d.road([(29, 20), (29, 20)], 1, only=".")
d.building("Spaceport hangar (from Tatooine)", "art:tatooine:docking-bay", 30, 26, 8, 4, door=3, to="hangar-tatooine-sullust")
d.road([(33, 30), (33, 31), (22, 31)], 1, only=".")
for x, y in ((16, 9), (36, 17), (3, 13), (15, 29)):
    d.prop("Steam vent", "art:sullust:steam-vent", x, y)
d.prop("Basalt column", "art:sullust:basalt-column", 36, 21, 2, 2)
d.prop("Fungus stalks", "art:sullust:fungus-stalks", 24, 11)
d.person("Sabine Wren", 9, 12, "story"); d.person("Bathhouse keeper", 12, 22); d.person("Spring bather", 13, 26)
d.person("Sullustan miner", 23, 21); d.person("Pilot fresh off the shuttle", 28, 29)
d.sign("Town sign", 18, 30); d.sign("Arena sign", 12, 10)
d.doc["story"] = "Sullustan hot-spring town in a volcanic bowl. Ships from Tatooine land at the spaceport; Sabine's Fire arena, the bathhouse and the hot spring pool. The Magma Tunnels lead north."
d.doc["todo"] = ["Vanilla's east road to Route 112 is cut: the spaceport hangar is the Tatooine/Sullust border (net:border-tatooine-sullust).",
                 "Vanilla's herb shop becomes the bathhouse front desk (herbs and hot-spring treats)."]
link_all(d); d.save()

# ---------------------------------------------------------------- INYUSU TOR (Fallarbor)
d = fresh("inyusu-tor", 40, 28)
d.blob(20, 14, 18, 12, '.')
d.road([(0, 13), (39, 13)], 2)
d.exit("west", [13, 14], "route-114"); d.exit("east", [13, 14], "route-113")
d.building("Ash farm (Showcase hall)", "art:sullust:ash-farm", 6, 4, 6, 4, door=3, to="inyusu-tor-battle-tent-lobby")
d.road([(9, 8), (9, 12)], 1, only=".")
d.building("Bacta Center", "art:shared:bacta-center", 17, 4, 5, 4, door=2, to="inyusu-tor-bacta-center-1f")
d.road([(19, 8), (19, 12)], 1, only=".")
d.building("Supply Depot", "art:shared:supply-depot", 27, 4, 4, 4, door=1, to="inyusu-tor-supply-depot")
d.road([(28, 8), (28, 12)], 1, only=".")
d.building("Dr. Tien's observatory", HOME, 8, 17, 5, 4, door=2, to="inyusu-tor-cozmos-house")
d.road([(10, 15), (10, 16)], 1, only=".")
d.building("Move tutor's home", HOME, 26, 17, 5, 4, door=2, to="inyusu-tor-move-relearners-house")
d.road([(28, 15), (28, 16)], 1, only=".")
d.prop("Ash greenhouse", "art:sullust:ash-greenhouse", 16, 18, 3, 3)
d.prop("Ash greenhouse", "art:sullust:ash-greenhouse", 20, 18, 3, 3)
d.prop("Basalt column", "art:sullust:basalt-column", 34, 18, 2, 2)
d.person("Dr. Tien", 13, 20, "story"); d.person("Ash farmer", 23, 16); d.person("Showcase fan", 13, 10)
d.sign("Town sign", 4, 12)
d.doc["story"] = "Ash-covered farm town: greenhouses grow crops in volcanic ash. Dr. Tien, the astronomer whose meteorite the Empire steals, lives in the observatory."
link_all(d); d.save()

retheme("route-113", extra=lambda d: d.warp("Magma Tunnels mouth", 74, 18, "magma-tunnels"),
        story="Ash fields east of Inyusu Tor where ash falls like snow; the glassblower collects it. The Magma Tunnels open on the south side.",
        art_house=HOME, props=[("Basalt column", "art:sullust:basalt-column", 2, 2, (20, 10)), ("Steam vent", "art:sullust:steam-vent", 1, 1, (60, 10))])
retheme("route-114", "Rocky road west of Inyusu Tor down to Starfall Cavern, with Tess's workshop (the companion storage system) and the fossil collector's home.",
        art_house=HOME, props=[("Lava flow", "art:sullust:lava-flow", 1, 1, (20, 50)), ("Fungus stalks", "art:sullust:fungus-stalks", 1, 1, (15, 20))],
        todo=["Vanilla's Lanette's house is Tess's workshop."])
def fix_tunnels(d):
    # vanilla's two doors both led to Route 112 (Tatooine) and are cut; re-add them as the Sullust ends
    d.doc["warps"] = [w for w in d.doc["warps"] if w["to"] not in ("pirin", "route-113")]
    d.warp("Exit to Route 113", 26, 4, "route-113")
    d.warp("Exit to Pirin", 26, 36, "pirin")
    d.doc["todo"] = [t for t in d.doc["todo"] if "route-112" not in t]
retheme("magma-tunnels", "Volcanic tunnels joining Pirin to Route 113's ash fields.", extra=fix_tunnels)
for a, s in [("starfall-cavern-1f-1r", "Cavern where a meteorite fell; Empire and Cartel clash at the entrance."),
             ("starfall-cavern-1f-2r", "Starfall Cavern, upper falls."), ("starfall-cavern-b1f-1r", "Starfall Cavern, lower pools."),
             ("starfall-cavern-b1f-2r", "Starfall Cavern, deepest pool: dragon companions."), ("starfall-cavern-hidden-cave", "Starfall Cavern's hidden room (post-game).")]:
    retheme(a, s)

# ---------------------------------------------------------------- MUSTAFAR
def peak(d):
    for e in list(d.doc["exits"]): pass
retheme("mustafar-peak", "Lava summit where the shuttle from Tatooine lands and Vader is fought for the first time; the Empire's machine drills into the volcano.",
        props=[("Obsidian spire", "art:mustafar:obsidian-spire", 2, 3, (8, 10)), ("Mining collector", "art:mustafar:mining-collector", 3, 4, (30, 12))])
retheme("ashen-pass", extra=lambda d: open_exit(d, "south", 14, "mustafar-mining-facility"), story="Steep ash trail down from Mustafar Peak to the gate of Fortress Vader. Its foot, once Route 112, now leads to the old mining facility.",
        props=[("Obsidian spire", "art:mustafar:obsidian-spire", 2, 3, (5, 30))])
for a, s in [("fortress-vader-1f", "Fortress Vader gate hall, cut into the cliff above the lava."),
             ("fortress-vader-2f-1r", "Fortress Vader: west hall."), ("fortress-vader-2f-2r", "Fortress Vader: lava conduits."),
             ("fortress-vader-2f-3r", "Fortress Vader: guard rooms."), ("fortress-vader-3f-1r", "Fortress Vader: upper west hall."),
             ("fortress-vader-3f-2r", "Fortress Vader: upper conduits."), ("fortress-vader-3f-3r", "Fortress Vader: barracks."),
             ("fortress-vader-4f", "Fortress Vader: the meditation chamber over the lava, where GREATKRAYT is woken.")]:
    retheme(a, s)

d = Draft.new("mustafar-mining-facility", "MINING FACILITY", "MUSTAFAR", 40, 30, kind="landmark", fill="#")
d.blob(20, 15, 17, 12, ".")
d.fill(2, 22, 37, 29, "~")
d.road([(19, 0), (19, 21)], 2, ch="=")
d.exit("north", [19, 20], "ashen-pass")
d.building("Separatist control center", "art:mustafar:fortress-halls", 13, 6, 8, 5, door=4, to="mustafar-mining-control")
d.prop("Mining collector", "art:mustafar:mining-collector", 4, 10, 3, 4)
d.prop("Mining collector", "art:mustafar:mining-collector", 31, 10, 3, 4)
d.prop("Obsidian spire", "art:mustafar:obsidian-spire", 26, 4, 2, 3)
d.person("Stormtrooper", 16, 14, "trainer"); d.person("Stormtrooper", 24, 16, "trainer"); d.person("Veers", 18, 12, "story")
d.person("Mining droid", 9, 17)
d.doc["story"] = "Optional: the old Separatist mining facility on a lava river below Ashen Pass, where Anakin fell. Veers runs Stormtrooper drills here; the control center holds rare items and an echo of the past for the Ilum trials."
d.doc["todo"] = ["New area off Ashen Pass's south end; lava ('~') is impassable.", "New interior: mustafar-mining-control."]
link_all(d); d.save()
