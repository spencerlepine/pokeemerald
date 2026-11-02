import os; exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "common.py")).read())
def fresh(area_id, w, h, fill="T"):
    d = Draft.load(area_id); d.g = [[fill] * w for _ in range(h)]
    d.clear(); d.doc["exits"] = []; d.doc["status"] = "BLOCKOUT"; return d

# ================================================================ HOTH
d = Draft.new("hoth-tundra", "HOTH TUNDRA", "HOTH", 48, 40, kind="route", fill="#")
d.doc["pos"] = [0, 0]
d.blob(24, 20, 21, 17, ".", rough=0.12)
d.blob(36, 25, 7, 5, "~")
d.blob(12, 14, 7, 5, '"'); d.blob(31, 9, 6, 3, '"'); d.blob(13, 31, 6, 4, '"')
d.fill(18, 0, 29, 2, "#")
d.road([(23, 3), (23, 31)], 2)
d.warp("Wampa Cave mouth", 23, 3, "wampa-cave-low-tide-entrance-room")
d.building("Survey shuttle pad (ships)", "art:shared:landing-pad", 21, 32, 6, 4, door=3, to="hoth-hangar")
d.building("Rebel survey outpost", "art:hoth:echo-base-hangar-door", 4, 19, 8, 5, door=4, to="hoth-survey-outpost")
d.road([(8, 24), (23, 24)], 1)
d.building("Tauntaun shelter", "art:hoth:tauntaun-shelter", 29, 13, 5, 4, door=2, to="hoth-tauntaun-shelter")
d.road([(25, 17), (31, 17)], 1)
d.prop("Snowspeeder (parked)", "art:hoth:snowspeeder", 16, 27, 3, 2)
for x, y in ((9, 7), (39, 9), (40, 33), (33, 4)):
    d.prop("Ice stalagmites", "art:hoth:ice-stalagmites", x, y)
d.person("Rebel surveyor", 13, 24, "story"); d.person("Tauntaun handler", 34, 17)
d.person("Ice trekker", 12, 13, "trainer"); d.person("Ice trekker", 31, 9, "trainer"); d.person("Ice trekker", 13, 31, "trainer")
d.person("Lost scout", 41, 14)
d.sign("Outpost sign", 13, 23); d.sign("Cave warning sign", 25, 5)
d.doc["story"] = ("New area: Hoth's only overworld. A survey shuttle lands on the tundra; a Rebel survey team is "
                  "scouting the planet for a future base. The trail runs north past the tauntaun shelter to the Wampa Cave; "
                  "a frozen lake (Surf) and deep snow (wild encounters) fill the sides.")
d.doc["todo"] = ["New area (replaces: new): vanilla Shoal Cave was reached from Route 125, which is now Yavin 4.",
                 "New interiors: hoth-survey-outpost, hoth-tauntaun-shelter, hoth-hangar.",
                 "Vanilla's tides become meltwater: the cave mouth leads to the low or high water entrance room by time of day.",
                 "Echo Base does not exist yet in 2 BBY; the outpost uses the Echo Base hangar-door art as a survey camp."]
link_all(d); d.save()

def wampa_entry(d):
    d.warp("Cave mouth", 20, 30, "hoth-tundra")
for a in ("wampa-cave-low-tide-entrance-room", "wampa-cave-high-tide-entrance-room"):
    retheme(a, "Wampa Cave entrance: ice tunnels with meltwater pools that rise and fall.", extra=wampa_entry,
            todo=["The mouth now opens onto the Hoth tundra (was Route 125)."])
for a in ("wampa-cave-high-tide-inner-room", "wampa-cave-low-tide-inner-room", "wampa-cave-low-tide-lower-room",
          "wampa-cave-low-tide-stairs-room"):
    retheme(a, "Wampa Cave: frozen tunnels; a wampa's lair is somewhere deep inside.")
retheme("wampa-cave-low-tide-ice-room", "Wampa Cave ice room: slippery floor puzzle (vanilla ice room). The wampa's lair with bones and an old Rebel scout's pack.")

# ================================================================ DAGOBAH
d = fresh("dagobah", 60, 60, "T")
d.blob(30, 30, 26, 26, ".", rough=0.1)
d.blob(30, 32, 12, 9, "~")
d.blob(12, 44, 5, 4, '"'); d.blob(46, 12, 6, 4, '"'); d.blob(46, 52, 5, 3, '"')
d.road([(10, 18), (50, 18), (50, 46)], 2); d.road([(10, 18), (10, 46), (50, 46)], 2)
d.fill(29, 40, 30, 59, "~"); d.fill(29, 46, 30, 47, "=")
d.exit("south", [29, 30], "route-126")
d.building("Yoda's hut (arena)", "art:dagobah:yoda-s-hut", 26, 8, 8, 6, door=4, to="dagobah-arena-1f")
d.road([(30, 14), (30, 17)], 1)
d.prop("Cave of Evil mouth", "art:dagobah:cave-of-evil-mouth", 3, 4, 4, 3)
d.warp("Cave of Evil", 5, 7, "cave-of-evil-entrance")
d.road([(5, 8), (5, 18)], 1); d.road([(5, 18), (10, 18)], 1)
d.building("Bacta Center", "art:shared:bacta-center", 40, 10, 5, 4, door=2, to="dagobah-bacta-center-1f")
d.road([(42, 14), (42, 17)], 1)
d.building("Supply Depot", "art:shared:supply-depot", 15, 10, 4, 4, door=1, to="dagobah-supply-depot")
d.road([(16, 14), (16, 17)], 1)
huts = [((2, 22), "dagobah-house-1"), ((54, 22), "dagobah-house-2"), ((2, 32), "dagobah-house-3"), ((54, 32), "dagobah-house-4"),
        ((14, 50), "dagobah-house-5"), ((46, 49), "dagobah-house-6"), ((21, 52), "dagobah-house-7")]
names = ["Bog fisher's hut", "Hermit's hut", "Swamp healer's hut", "Moss gatherer's hut", "Old smuggler's hut",
         "Herbalist's hut", "Dragonsnake watcher's hut"]
for ((x, y), to), n in zip(huts, names):
    d.building(n, "art:dagobah:yoda-s-hut", x, y, 4, 3, door=1, to=to)
d.building("Gnarltree keeper's hut", "art:dagobah:yoda-s-hut", 54, 41, 4, 3, door=1, to="dagobah-lotad-and-seedot-house")
d.building("Old Jedi outpost (mystery events)", "art:dagobah:yoda-s-hut", 2, 41, 5, 4, door=2, to="dagobah-mystery-events-house-1f")
d.building("Bog landing (ships)", "art:shared:landing-pad", 36, 50, 6, 4, door=3, to="dagobah-hangar")
d.prop("Sunken X-wing", "art:dagobah:sunken-x-wing", 33, 27, 4, 3)
for x, y in ((21, 14), (37, 15), (4, 28), (56, 28)):
    d.prop("Gnarltree", "art:dagobah:gnarltree", x, y, 2, 2)
for x, y in ((13, 38), (47, 38), (25, 50)):
    d.prop("Hanging moss", "art:dagobah:hanging-moss", x, y)
for x, y in ((17, 23), (43, 23), (19, 40)):
    d.prop("Swamp reeds", "art:dagobah:swamp-reeds", x, y, 2, 1)
d.person("Yoda", 31, 16, "story"); d.person("Obi-Wan (guarding the cave)", 6, 9, "story")
d.person("Bog fisher", 18, 30); d.person("Herbalist", 46, 44); d.person("Swamp hermit", 12, 26)
d.person("Dagobah pilgrim", 38, 48, "trainer"); d.person("Smuggler stranded here", 41, 55)
d.sign("Hollow sign", 12, 17); d.sign("Arena sign", 25, 15)
d.doc["story"] = ("Dagobah's hidden swamp hollow: Yoda's hut is the arena, the Cave of Evil (a Force vergence) opens in the "
                  "north-west, and a bog lagoon fills the middle. Ships set down on the south-east bog landing; a surf channel "
                  "runs south to the swamp routes, and divers can still surface in the lagoon from Route 126.")
d.doc["todo"] = ["Same size as Sootopolis (60x60); the crater wall is now swamp trees, the crater lake the bog lagoon.",
                 "Vanilla's 7 houses become hermit huts; dagobah-house-1..7 interiors keep their ids.",
                 "New interior: dagobah-hangar. New exit: the south surf channel to Route 126 (vanilla had none).",
                 "Act 6: storms and the titans' clash play out over the lagoon; Obi-Wan stands at the cave until then."]
link_all(d); d.save()

SW = "art:dagobah:swamp-reeds"
def r126(d):
    open_exit(d, "north", 40, "dagobah", 2, ch="~")
retheme("route-126", extra=r126, story="Bog lakes round Dagobah's hollow. Deep water to dive into (the hollow's lagoon also surfaces here) and swamp islets with GNATLING.",
        props=[("Gnarltree", "art:dagobah:gnarltree", 2, 2, (20, 20)), ("Swamp reeds", SW, 2, 1, (60, 60))],
        todo=["The north channel leads to the Dagobah hollow (new link; vanilla's north edge was Route 124, Yavin 4)."])
retheme("route-127", "Misty swamp channels east of the hollow; SWAMPSLUG wallow on the islets.",
        props=[("Hanging moss", "art:dagobah:hanging-moss", 1, 1, (30, 30)), ("Gnarltree", "art:dagobah:gnarltree", 2, 2, (60, 20))])
retheme("route-128", "Deep swamp south of the hollow where the Drowned Cavern's dive spot lies; SANDO sleeps below.",
        props=[("Sunken X-wing", "art:dagobah:sunken-x-wing", 4, 3, (60, 20)), ("Swamp reeds", SW, 2, 1, (30, 10))],
        todo=["Vanilla's east coast to Ever Grande (Ilum) is cut; Ilum is reached by ship."])
retheme("route-129", "Wide bog lake with drifting logs and trainers on rafts.",
        props=[("Gnarltree", "art:dagobah:gnarltree", 2, 2, (40, 20))])
retheme("route-130", "The far bog. Mirage Isle, the islet that only appears sometimes, rises here.",
        props=[("Hanging moss", "art:dagobah:hanging-moss", 1, 1, (40, 20))],
        todo=["Vanilla's west edge to Route 131 (Kamino) is cut."])
for a in ("underwater-route-126", "underwater-route-127", "underwater-route-128", "underwater-route-129",
          "underwater-sootopolis-city", "underwater-seafloor-cavern", "underwater-marine-cave"):
    retheme(a, "Murky water under the swamp, roots and silt.")
for a in ("cave-of-evil-entrance", "cave-of-evil-1f", "cave-of-evil-b1f"):
    retheme(a, "Cave of Evil: a dark-side vergence under the gnarltree roots. Visions flicker on the walls; the titans clash in the deepest room in Act 6.")
for a in [f"drowned-cavern-room-{i}" for i in range(1, 10)] + ["drowned-cavern-entrance"]:
    retheme(a, "Drowned Cavern: flooded caves under Route 128 where Jabba wakes SANDO (vanilla Seafloor Cavern).")
for a in ("marine-cave-entrance", "marine-cave-end"):
    retheme(a, "Marine Cave: a roaming flooded cave, unused in Emerald; kept as an optional dive.")

# ================================================================ KAMINO
d = fresh("tipoca-city", 50, 36, "~")
d.fill(14, 8, 35, 20, "=")
d.road([(0, 17), (49, 17)], 2, "=")
d.fill(38, 3, 47, 10, "="); d.road([(42, 10), (42, 16)], 2, "=")
d.fill(3, 6, 11, 13, "="); d.road([(7, 13), (7, 16)], 1, "=")
d.fill(3, 22, 12, 30, "="); d.road([(7, 19), (7, 22)], 1, "=")
d.fill(15, 22, 35, 30, "="); d.road([(20, 19), (20, 22)], 1, "="); d.road([(31, 19), (31, 22)], 1, "=")
d.fill(37, 21, 48, 30, "="); d.road([(42, 19), (42, 21)], 1, "=")
d.exit("west", [17, 18], "route-132"); d.exit("east", [17, 18], "route-131")
d.building("Cloning hall", "art:kamino:cloning-hall", 19, 9, 12, 6, door=6, to="tipoca-city-cloning-hall")
d.building("Landing platform (ships)", "art:shared:landing-pad", 40, 4, 6, 4, door=3, to="tipoca-city-hangar")
d.building("Kaminoan dwelling", "art:kamino:stilt-dome", 5, 7, 5, 4, door=2, to="tipoca-city-house-4")
d.building("Bacta Center", "art:shared:bacta-center", 5, 23, 5, 4, door=2, to="tipoca-city-bacta-center-1f")
d.building("Clone trainer's quarters", "art:kamino:stilt-dome", 16, 23, 5, 4, door=2, to="tipoca-city-house-1")
d.building("Kaminoan dwelling", "art:kamino:stilt-dome", 23, 23, 5, 4, door=2, to="tipoca-city-house-2")
d.building("Supply Depot", "art:shared:supply-depot", 30, 23, 4, 4, door=1, to="tipoca-city-supply-depot")
d.building("Fisher's dome", "art:kamino:stilt-dome", 38, 22, 4, 4, door=1, to="tipoca-city-house-3")
d.building("Storm watcher's dome", "art:kamino:stilt-dome", 43, 22, 4, 4, door=1, to="tipoca-city-house-5")
d.prop("Cargo crates", "art:shared:cargo-crates", 46, 8, 2, 2)
d.prop("Storm swell", "art:kamino:storm-sea", 4, 33, 3, 1); d.prop("Storm swell", "art:kamino:storm-sea", 40, 33, 3, 1)
d.person("Kaminoan aide", 26, 16, "story"); d.person("Clone cadet", 10, 17, "trainer"); d.person("Clone cadet", 36, 18, "trainer")
d.person("Kaminoan scientist", 18, 29); d.person("Stilt fisher", 45, 29); d.person("Dock worker", 39, 9)
d.sign("City holo-sign", 14, 16); d.sign("Cloning hall sign", 32, 15)
d.doc["story"] = ("Tipoca City on Kamino's storm sea: domes on stilts joined by walkways round the great cloning hall. "
                  "Ships land on the north-east platform; the walkway runs west to Route 132 and east to Route 131.")
d.doc["todo"] = ["Grown from Pacifidlog (20x40) to 50x36; the 5 house and Bacta Center interiors keep their ids.",
                 "New interiors: tipoca-city-cloning-hall (PROTOCLONE lore, optional), tipoca-city-supply-depot, tipoca-city-hangar.",
                 "'~' is the open storm sea (Surf); '=' are the stilt walkways and platforms."]
link_all(d); d.save()

retheme("route-131", "Storm sea east of Tipoca City; rain never stops. Swimmers and clone cadets on training rigs.",
        props=[("Stilt walkway", "art:kamino:stilt-walkway", 3, 1, (30, 20))],
        todo=["Vanilla's east edge to Route 130 (Dagobah) is cut."])
retheme("route-132", "Strong currents west of Tipoca City push the player along (vanilla current tiles).")
retheme("route-133", "Currents and rocky stacks; DIANOGA lurk in the deep water.")
retheme("route-134", "Boba Fett's home waters. The Sealed Vault's dive spot is here, and Boba waits for the third rematch.",
        props=[("Storm swell", "art:kamino:storm-sea", 3, 1, (40, 20))],
        todo=["Vanilla's west edge to Slateport (now Mos Eisley, Tatooine) is cut; Route 134 ends in open sea."])
for a in ("underwater-route-134", "underwater-sealed-chamber"):
    retheme(a, "Deep water off Route 134 with the Sealed Vault's sunken door.")
for a in ("sealed-vault-outer-room", "sealed-vault-inner-room"):
    retheme(a, "Sealed Vault: Aurebesh carvings on the walls; reading them wakes the Wardens.")

# ================================================================ ILUM
d = fresh("ilum", 44, 60, "#")
d.blob(22, 49, 18, 8, ".", rough=0.1)
d.blob(22, 15, 18, 12, ".", rough=0.1)
d.blob(36, 41, 4, 3, '"'); d.blob(8, 54, 4, 2, '"')
d.road([(22, 11), (22, 47)], 2)
d.fill(22, 36, 23, 36, "v")
d.building("Jedi temple gate (the Four Trials)", "art:ilum:jedi-temple-gate", 16, 4, 12, 7, door=6, to="ilum-temple-1f")
d.road([(24, 20), (32, 20), (32, 26)], 1)
d.warp("Crystal Caves (north mouth)", 32, 27, "crystal-caves-1f")
d.warp("Crystal Caves (south mouth)", 12, 38, "crystal-caves-1f")
d.road([(12, 39), (12, 47)], 1)
d.road([(6, 47), (38, 47)], 2)
d.building("Bacta Center", "art:shared:bacta-center", 8, 43, 5, 4, door=2, to="ilum-bacta-center-1f")
d.building("Supply Depot", "art:shared:supply-depot", 15, 50, 4, 4, door=1, to="ilum-supply-depot")
d.building("Landing pad (ships)", "art:shared:landing-pad", 26, 50, 6, 4, door=3, to="ilum-hangar")
for x, y in ((7, 20), (36, 13), (35, 53)):
    d.prop("Kyber crystal outcrop", "art:ilum:kyber-crystal-outcrop", x, y, 2, 2)
for x, y in ((5, 52), (39, 45), (7, 10), (37, 22)):
    d.prop("Snow pine", "art:ilum:snow-pine", x, y, 1, 2)
d.person("Gate warden", 24, 12, "story"); d.person("Temple acolyte", 19, 21); d.person("Pilgrim", 15, 48)
d.person("Crystal hunter", 9, 41, "trainer"); d.person("Rebel pilot", 33, 55)
d.sign("Temple sign", 20, 12); d.sign("Crystal Caves sign", 13, 40)
d.doc["story"] = ("Ilum, the ice world of the kyber caves. Ships land in the south basin by the Bacta Center; the Crystal Caves "
                  "(vanilla Victory Road) cut through the cliff band to the north plateau, where the gate warden checks the eight "
                  "kyber shards before the Jedi temple gate opens to the Four Trials.")
d.doc["todo"] = ["Redrawn from Ever Grande (40x80) at 44x60. The ice slope at col 22-23 ends in a ledge (row 36): a quick way back down, never up.",
                 "New interiors: ilum-supply-depot, ilum-hangar. ilum-temple-1f and ilum-bacta-center-1f keep their ids.",
                 "Vanilla's west sea to Route 128 (Dagobah) is cut."]
link_all(d); d.save()
for a in ("crystal-caves-1f", "crystal-caves-b1f", "crystal-caves-b2f"):
    retheme(a, "Crystal Caves: kyber-lit ice tunnels; the final rival battle with Luke is on B1F, and Boba's finale rematch waits there too.")
