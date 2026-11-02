import os; exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "common.py")).read())
def fresh(area_id, w, h, fill="T"):
    d = Draft.load(area_id); d.g = [[fill] * w for _ in range(h)]
    d.clear(); d.doc["exits"] = []; d.doc["status"] = "BLOCKOUT"; return d
TRUNK = ("Redwood trunk", "art:endor:redwood-trunk", 3, 3)

# ================================================================ ENDOR
def r118(d):
    d.building("Rebel shuttle clearing (from Tatooine)", "art:tatooine:docking-bay", 6, 2, 8, 4, door=4, to="hangar-tatooine-endor")
retheme("route-118", extra=r118, story="Forest edge where Rebel shuttles from Tatooine set down. The road runs east along a river towards the redwoods; Route 119 climbs north.",
        props=[TRUNK + ((30, 5),), ("Fallen log", "art:endor:fallen-log", 3, 1, (60, 14)), ("Crashed speeder bike", "art:endor:crashed-speeder-bike", 2, 1, (50, 4))],
        todo=["The shuttle clearing replaces vanilla's west road to Mos Espa (planet border)."])
retheme("route-119", "Treewalk forest: a long climb north through redwoods and ferns, with Endor Station (the Imperial research bunker the Cartel has taken) and Bossk inside.",
        art_house="art:endor:imperial-bunker", props=[TRUNK + ((20, 60),), TRUNK + ((10, 100),), ("AT-ST wreck", "art:endor:at-st-wreck", 3, 3, (25, 20)), ("Log trap", "art:endor:log-trap", 3, 1, (15, 80))])
def r120(d):
    open_exit(d, "east", 20, "endor-battlefield")
retheme("route-120", extra=r120, story="Deep Endor forest east of Bright Tree, where TAOZIN hide. The Ancient Tomb and the Scorched Hollow are off the trail; a side path east leads to the old battlefield.",
        props=[TRUNK + ((25, 30),), ("Fallen log", "art:endor:fallen-log", 3, 1, (15, 80)), ("Ewok glider", "art:endor:ewok-glider", 1, 2, (30, 45))])
retheme("route-121", "Forest road east of Route 120 past the reserve shuttle stop. Vanilla's east road to Cloud City and south road to Jedha are cut.",
        props=[TRUNK + ((20, 8),), ("Totem and drum", "art:endor:totem-and-drum", 1, 2, (60, 10))],
        todo=["Vanilla's Safari Zone gate is now the shuttle stop to Felucia (a ship link)."])
retheme("route-123", "River valley in southern Endor with the berry grower's lodge.", art_house="art:endor:ewok-hut",
        props=[TRUNK + ((80, 5),), ("Fallen log", "art:endor:fallen-log", 3, 1, (110, 12))])
retheme("ancient-tomb", "Stone tomb in the forest; home of DURAWARDEN.")
retheme("scorched-hollow", "Sun-baked hollow under the forest canopy.")

d = Draft.new("endor-battlefield", "ENDOR BATTLEFIELD", "ENDOR", 40, 30, kind="landmark")
d.blob(20, 15, 17, 12, ".")
d.blob(26, 18, 8, 6, '"')
d.fill(0, 14, 4, 15, ".")
d.exit("west", [14, 15], "route-120")
d.prop("AT-ST wreck", "art:endor:at-st-wreck", 10, 6, 3, 3)
d.prop("AT-ST wreck", "art:endor:at-st-wreck", 28, 7, 3, 3)
d.prop("Crashed speeder bike", "art:endor:crashed-speeder-bike", 16, 21, 2, 1)
d.prop("Log trap", "art:endor:log-trap", 21, 5, 3, 1)
d.prop("Redwood trunk", "art:endor:redwood-trunk", 33, 18, 3, 3)
d.building("Abandoned shield bunker", "art:endor:imperial-bunker", 16, 9, 6, 5, door=3, to="endor-battlefield-bunker")
d.person("Stormtrooper straggler", 12, 11, "trainer"); d.person("Stormtrooper straggler", 26, 13, "trainer")
d.person("Ewok scout", 8, 18); d.person("Rebel commando", 30, 23, "trainer")
d.doc["story"] = "Optional: the forest clearing where the battle was fought: AT-ST wrecks, log traps, and an abandoned shield bunker. Stormtrooper stragglers still patrol; Ewok scouts keep watch."
d.doc["todo"] = ["New interior: endor-battlefield-bunker."]
link_all(d); d.save()

# ================================================================ BESPIN
d = fresh("cloud-city", 70, 46, "~")
d.blob(35, 22, 24, 17, ".", rough=0.06)
d.road([(34, 6), (34, 40)], 2); d.road([(12, 22), (58, 22)], 2)
d.fill(28, 17, 41, 27, ":")
d.fill(3, 20, 11, 25, "="); d.fill(59, 20, 66, 25, "=")         # landing platforms, east and west
d.fill(33, 0, 36, 5, "=")
d.building("Galleria (department store)", "art:bespin:department-store", 26, 5, 8, 6, door=4, to="cloud-city-galleria-1f")
d.building("Museum", "art:bespin:cloud-city-tower", 40, 6, 5, 6, door=2, to="cloud-city-museum-1f")
d.road([(42, 12), (42, 16)], 1, only=".")
d.building("Showcase hall", "art:bespin:cloud-city-tower", 18, 12, 5, 6, door=2, to="cloud-city-showcase-lobby")
d.road([(20, 18), (20, 21)], 1, only=".")
d.building("Bacta Center", "art:shared:bacta-center", 46, 13, 5, 4, door=2, to="cloud-city-bacta-center-1f")
d.road([(48, 17), (48, 21)], 1, only=".")
d.building("Companion fan club", "art:bespin:cloud-city-tower", 46, 26, 5, 6, door=2, to="cloud-city-pokemon-trainer-fan-club")
d.building("Sky motel", "art:bespin:cloud-city-tower", 20, 26, 5, 6, door=2, to="cloud-city-cove-lily-motel-1f")
d.building("Move deleter's flat", "art:bespin:cloud-city-tower", 26, 30, 5, 6, door=2, to="cloud-city-move-deleters-house")
d.building("Lando's flat", "art:bespin:cloud-city-tower", 38, 30, 5, 6, door=2, to="cloud-city-house-1")
d.building("Ugnaught family flat", "art:bespin:cloud-city-tower", 52, 9, 5, 6, door=2, to="cloud-city-house-2")
d.road([(54, 15), (54, 21)], 1, only=".")
d.building("Tibanna trader's flat", "art:bespin:cloud-city-tower", 14, 27, 5, 6, door=2, to="cloud-city-house-3")
d.building("Cloud car pilot's flat", "art:bespin:cloud-city-tower", 52, 30, 5, 6, door=2, to="cloud-city-house-4")
d.building("West landing platform (ships)", "art:bespin:landing-platform", 4, 15, 5, 5, door=2, to="cloud-city-hangar")
d.building("Under-levels lift (Hutt Hideout)", "art:bespin:cloud-city-tower", 60, 14, 5, 6, door=2, to="hutt-hideout-1f")
for x, y in ((29, 18), (39, 18), (29, 25), (39, 25)):
    d.prop("Promenade railing", "art:bespin:promenade-railing", x, y)
d.prop("Cloud car", "art:shared:parked-landspeeder", 62, 23, 2, 1)
d.prop("Cloud car", "art:shared:parked-landspeeder", 6, 23, 2, 1)
d.person("Lando", 37, 24, "story"); d.person("Showcase MC", 21, 20); d.person("Ugnaught worker", 56, 20)
d.person("Wing guard", 33, 13, "trainer"); d.person("Wing guard", 44, 21, "trainer"); d.person("Tourist", 30, 20)
d.person("Cloud car pilot", 64, 24); d.person("Blend master", 25, 21)
d.sign("City sign", 32, 8); d.sign("Galleria sign", 25, 11)
d.doc["story"] = "Floating city over Bespin's cloud sea: the Galleria, museum, Showcase hall and Lando's flat round a central plaza. Ships land on the west platform; the lift in the east goes down to the under-levels where the Cartel hides."
d.doc["todo"] = ["'~' on Bespin is the open cloud sea, crossed by cloud car (Surf).",
                 "Vanilla's roads west (Endor) and east (Yavin 4) are cut: the west landing platform is the ship link.",
                 "North platform: a cloud car stop to the Tibanna refinery (new optional area)."]
d.exit("north", [33, 34, 35, 36], "tibanna-refinery")
link_all(d); d.save()

d = Draft.new("tibanna-refinery", "TIBANNA REFINERY", "BESPIN", 40, 26, kind="landmark", fill="~")
d.blob(20, 12, 16, 9, ".")
d.fill(18, 20, 21, 25, "=")
d.exit("south", [18, 19, 20, 21], "cloud-city")
d.building("Gas refinery", "art:bespin:cloud-city-tower", 8, 4, 5, 6, door=2, to="tibanna-refinery-interior")
d.building("Carbon-freezing annex", "art:bespin:cloud-city-tower", 26, 4, 5, 6, door=2, to="tibanna-refinery-annex")
d.prop("Gas tanks", "art:shared:fuel-tanks", 16, 6, 2, 2); d.prop("Gas tanks", "art:shared:fuel-tanks", 21, 6, 2, 2)
d.person("Ugnaught foreman", 19, 12); d.person("Cartel thug", 14, 15, "trainer"); d.person("Cartel thug", 26, 15, "trainer")
d.doc["story"] = "Optional: a Tibanna gas refinery on a separate platform north of Cloud City, reached by cloud car or the north skybridge. Ugnaughts work the tanks; Cartel thugs are smuggling gas."
d.doc["todo"] = ["New interiors: tibanna-refinery-interior, tibanna-refinery-annex."]
link_all(d); d.save()

# ================================================================ JEDHA
def r122(d):
    d.building("Pilgrim landing pad", "art:shared:landing-pad", 2, 2, 4, 4)
    open_exit(d, "east", 18, "nijedha")
retheme("route-122", extra=r122, story="Holy waters round the island of the Jedha Temple. Pilgrim ships land on the north-west pad; a causeway east leads to NiJedha.",
        props=[("Toppled statue", "art:jedha:toppled-statue", 3, 3, (30, 8))])
retheme("jedha-temple-exterior", "The Jedha Temple's outer terraces: graves of fallen companions and pilgrims climbing to the summit.",
        props=[("Prayer candles", "art:jedha:prayer-candles", 1, 1, (12, 30)), ("Toppled statue", "art:jedha:toppled-statue", 3, 3, (25, 25))])
retheme("jedha-temple-summit", "Summit of the Jedha Temple where the Guardians of the Whills keep the RED and BLUE KYBER.",
        props=[("Prayer candles", "art:jedha:prayer-candles", 1, 1, (18, 8))])

d = Draft.new("nijedha", "NIJEDHA", "JEDHA", 44, 34, kind="town")
d.fill(0, 0, 43, 33, "#")
d.blob(22, 17, 19, 14, ".")
d.road([(0, 17), (43, 17)], 2); d.road([(21, 3), (21, 30)], 2)
d.fill(16, 13, 27, 21, ":")
d.exit("west", [17, 18], "route-122")
d.building("Temple of the Kyber", "art:jedha:temple-of-the-kyber", 18, 3, 8, 6, door=4, to="nijedha-temple-of-the-kyber")
d.building("Bacta Center", "art:shared:bacta-center", 6, 8, 5, 4, door=2, to="nijedha-bacta-center")
d.road([(8, 12), (8, 16)], 1, only=".")
d.building("Supply Depot", "art:shared:supply-depot", 31, 8, 4, 4, door=1, to="nijedha-supply-depot")
d.road([(32, 12), (32, 16)], 1, only=".")
d.building("Guardians' quarters", "art:tatooine:sunken-courtyard-home", 7, 21, 6, 6, door=3, to="nijedha-guardians-quarters")
d.road([(10, 19), (10, 20)], 1, only=".")
d.building("Pilgrim hostel", "art:tatooine:homestead-dome", 30, 22, 5, 4, door=2, to="nijedha-hostel")
d.road([(32, 19), (32, 21)], 1, only=".")
d.prop("Toppled statue", "art:jedha:toppled-statue", 34, 26, 3, 3)
for x, y in ((17, 14), (26, 14), (17, 20), (26, 20)):
    d.prop("Prayer candles", "art:jedha:prayer-candles", x, y)
d.prop("Market stall", "art:tatooine:market-stall", 13, 14, 2, 2)
d.person("Guardian of the Whills", 22, 11, "story"); d.person("Guardian of the Whills", 11, 19, "story")
d.person("Pilgrim", 19, 19); d.person("Stormtrooper patrol", 28, 18, "trainer"); d.person("Kyber trader", 15, 16)
d.sign("City sign", 4, 16)
d.doc["story"] = "New town: NiJedha, the holy city on Jedha's moon, with the Temple of the Kyber where the Guardians of the Whills live. Pilgrims rest here before crossing the holy waters to the Jedha Temple."
d.doc["todo"] = ["New town (replaces: new). New interiors: nijedha-temple-of-the-kyber, nijedha-bacta-center, nijedha-supply-depot, nijedha-guardians-quarters, nijedha-hostel.",
                 "Gives Jedha a hub; the Guardians already exist in characters.csv."]
link_all(d); d.save()

# ================================================================ YAVIN 4
d = fresh("yavin-4", 70, 44)
d.blob(35, 22, 32, 20, ".", rough=0.08)
d.road([(0, 22), (69, 22)], 2); d.road([(30, 0), (30, 3)], 2); d.road([(36, 0), (36, 40)], 2)
d.fill(25, 18, 37, 26, ":")
d.exit("west", [22, 23], "route-124"); d.exit("north", [58, 59], "route-125")
d.road([(58, 0), (58, 21)], 2)
d.building("Massassi Temple (arena)", "art:yavin-4:massassi-temple", 26, 4, 10, 8, door=5, to="yavin-4-arena")
d.road([(31, 12), (31, 17)], 1, only=".")
d.building("Rebel hangar", "art:yavin-4:rebel-hangar", 48, 8, 8, 5, door=4, to="yavin-4-launch-tower-1f")
d.road([(52, 13), (52, 21)], 1, only=".")
d.building("Bacta Center", "art:shared:bacta-center", 12, 12, 5, 4, door=2, to="yavin-4-bacta-center-1f")
d.road([(14, 16), (14, 21)], 1, only=".")
d.building("Supply Depot", "art:shared:supply-depot", 40, 14, 4, 4, door=1, to="yavin-4-supply-depot")
d.road([(41, 18), (41, 21)], 1, only=".")
d.building("Leia's quarters", "art:yavin-4:rebel-hangar", 8, 27, 8, 5, door=4, to="yavin-4-stevens-house")
d.road([(12, 24), (12, 26)], 1, only=".")
d.building("Pilots' barracks", "art:tatooine:homestead-dome", 20, 30, 5, 4, door=2, to="yavin-4-house-1")
d.building("Sabacc den", "art:tatooine:homestead-dome", 28, 30, 5, 4, door=2, to="yavin-4-sabacc-den-1f")
d.building("Mechanics' barracks", "art:tatooine:homestead-dome", 38, 30, 5, 4, door=2, to="yavin-4-house-2")
d.building("Medic's hut", "art:tatooine:homestead-dome", 46, 27, 5, 4, door=2, to="yavin-4-house-3")
d.building("Scout's hut", "art:tatooine:homestead-dome", 56, 27, 5, 4, door=2, to="yavin-4-house-4")
d.prop("X-wing (parked)", "art:yavin-4:x-wing-parked", 62, 15, 4, 3)
d.prop("X-wing (parked)", "art:yavin-4:x-wing-parked", 61, 9, 4, 3)
d.prop("Massassi jungle tree", "art:yavin-4:massassi-jungle-tree", 4, 6, 2, 3)
d.prop("Massassi jungle tree", "art:yavin-4:massassi-jungle-tree", 63, 33, 2, 3)
d.prop("Jungle vines", "art:yavin-4:jungle-vines", 22, 8); d.prop("Jungle vines", "art:yavin-4:jungle-vines", 40, 7)
d.prop("Cargo crates", "art:shared:cargo-crates", 44, 9, 2, 2)
d.person("Leia", 11, 25, "story"); d.person("Kanan Jarrus", 29, 13, "story"); d.person("Ezra Bridger", 33, 13, "story")
d.person("Rebel pilot", 55, 19); d.person("Rebel mechanic", 59, 13); d.person("Rebel trooper", 26, 24, "trainer")
d.person("Launch tech", 50, 15)
d.sign("Base sign", 4, 21); d.sign("Temple sign", 25, 12)
d.doc["story"] = "Secret Rebel base in the jungle: the Massassi Temple is Kanan and Ezra's Force arena, X-wings wait by the hangar (vanilla Space Center) and Leia keeps quarters here."
d.doc["todo"] = ["Vanilla's south sea (Route 127, Dagobah) is cut.", "Vanilla Steven's house becomes Leia's quarters."]
link_all(d); d.save()
retheme("route-124", extra=lambda d: drop_exit(d, "route-125"), story="Jungle river delta west of the base: deep channels to dive in and the treasure divers' hut.", art_house="art:tatooine:homestead-dome",
        props=[("Massassi jungle tree", "art:yavin-4:massassi-jungle-tree", 2, 3, (30, 30))])
retheme("route-125", extra=lambda d: drop_exit(d, "route-124"), story="Jungle lakes north of the base. Vanilla's Shoal Cave door (Hoth) is cut.",
        props=[("Massassi jungle tree", "art:yavin-4:massassi-jungle-tree", 2, 3, (40, 20))])
for a in ("underwater-route-124", "underwater-route-125"):
    retheme(a, "Under the jungle river.")
