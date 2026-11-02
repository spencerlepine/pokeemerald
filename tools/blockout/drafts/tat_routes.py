import os; exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "common.py")).read())
H = "art:tatooine:homestead-dome"
V = ("Vaporator", "art:tatooine:moisture-vaporator", 1, 2)
B = ("Sandstone boulder", "art:tatooine:sandstone-boulder", 2, 2)
def v(near): return V + (near,)
def b(near): return B + (near,)

retheme("route-101", "Short desert track from Mos Pelgo up to Tosche Station, where Prof. Korr is cornered by a wild companion and the player picks a starter from his dropped bag.",
        props=[v((3, 3)), v((17, 9)), b((15, 2)), ("Bantha skeleton", "art:tatooine:bantha-skeleton", 1, 1, (3, 16))])
retheme("route-102", "Scrubland between Tosche Station and Mos Entha: first trainers, first wild scrub patches and a dry oasis pond.",
        props=[v((5, 8)), v((30, 4)), b((20, 12)), ("Dead tree", "art:tatooine:dead-tree", 2, 2, (44, 12)),
               ("Bantha skeleton", "art:tatooine:bantha-skeleton", 1, 1, (12, 3))])
retheme("route-103", "Road north from Tosche Station along the salt lake, where the rival waits. The east end opens onto the podrace course; the cave is Altering Cave's Tatooine twin.",
        props=[v((8, 6)), b((19, 12)), ("Krayt bones", "art:tatooine:krayt-bones", 4, 3, (60, 6)), ("Dead tree", "art:tatooine:dead-tree", 2, 2, (75, 12))],
        todo=["'~' on Tatooine is the planet's surf medium: salt lake water here."])
retheme("route-104", "Coast road from Mos Entha north to Bestine past the Jundland Wastes. Han's hangar (vanilla Mr. Briney's cottage) is where the Falcon leaves for Kashyyyk.",
        art_house=H, props=[v((10, 60)), b((20, 40)), ("Tusken camp", "art:tatooine:tusken-camp", 3, 2, (30, 20)), ("Parked landspeeder", "art:shared:parked-landspeeder", 2, 1, (14, 70))],
        todo=["Han's hangar is the Tatooine/Kashyyyk planet border (net:hangar-tatooine-kashyyyk)."])
retheme("jundland-wastes", extra=lambda d: open_exit(d, "east", 20, "bens-hut"), story="Rocky canyon badlands between the two halves of Route 104: Tusken territory, where the Organa engineer is robbed. A side path east climbs to Ben's hut.", name="JUNDLAND WASTES",
        props=[("Tusken camp", "art:tatooine:tusken-camp", 3, 2, (12, 10)), ("Rock spire", "art:tatooine:rock-spire", 2, 3, (35, 30)),
               ("Krayt bones", "art:tatooine:krayt-bones", 4, 3, (24, 20)), b((40, 8))])
retheme("route-110", "The Boonta Eve podrace course: the raised speeder road runs from Mos Espa south to Mos Eisley over the canyon, with the Trick House (Garindan's) and side paths underneath.",
        art_house=H, props=[("Podrace course markers", "art:tatooine:podrace-course-markers", 1, 2, (20, 30)), ("Podrace course markers", "art:tatooine:podrace-course-markers", 1, 2, (20, 60)),
                            ("Pod-race junk", "art:tatooine:pod-race-junk", 2, 2, (8, 45)), v((30, 80))])
def _r111(d):
    open_exit(d, "east", 60, "jabbas-palace", 3)
    for x, y in ((11, 93), (10, 94)):
        if d.get(x, y) in (".", ":", '"'):
            d.warp("Krayt Graveyard tunnel", x, y, "krayt-graveyard"); break
    for p in d.doc["people"]:
        if p["name"] == "Victor":
            p["at"] = [12, 115]
retheme("route-111", extra=_r111, story="The Dune Sea: open desert north of Mos Espa with sandstorms (SAND GOGGLES), the Krayt Graveyard tunnels, the Tusken Ruins and the wandering Sandcrawler. The Pit of Carkoon and the sail barge wreck are optional side spots, and a track east leads to Jabba's palace.",
        art_house=H, props=[("Sarlacc pit (Pit of Carkoon)", "art:tatooine:sarlacc-pit", 4, 4, (8, 60)), ("Sail barge wreck", "art:tatooine:sail-barge-wreck", 6, 3, (30, 50)),
                            ("Krayt bones", "art:tatooine:krayt-bones", 4, 3, (25, 90)), ("Dune ripples", "art:tatooine:dune-ripple-ledges", 1, 1, (15, 40)), b((35, 20))],
        todo=["The Sandcrawler (vanilla Mirage Tower) appears in the Dune Sea only after a sandstorm."])
retheme("route-112", "Canyon road north of the Dune Sea. The shuttle station (vanilla cable car) flies up to Mustafar Peak; the north edge was Sullust and is now cut.",
        art_house=H, props=[b((10, 20)), ("Rock spire", "art:tatooine:rock-spire", 2, 3, (30, 10)), ("Landing pad", "art:shared:landing-pad", 4, 4, (8, 30))],
        todo=["Route 112 north (Sullust) and the shuttle to Mustafar become ship links; see net_new.csv borders."])
retheme("route-115", "Coastal cliffs north of Bestine: a beach of wrecked pod parts, Starfall Cavern's Tatooine mouth and long grass for training.",
        props=[b((20, 30)), ("Pod-race junk", "art:tatooine:pod-race-junk", 2, 2, (10, 50)), ("Dead tree", "art:tatooine:dead-tree", 2, 2, (20, 15))])
retheme("route-116", "East road from Bestine to Beggar's Canyon, where Fixer is digging a tunnel by hand to Anchorhead. The tunnellers' rest house sits by the canyon mouth.",
        art_house=H, props=[v((30, 8)), ("Tusken camp", "art:tatooine:tusken-camp", 3, 2, (50, 12)), b((70, 5))])
retheme("route-117", "Farm road from Anchorhead east to Mos Espa past the Creature Nursery, a ranch with pens and a dewback trough.",
        art_house=H, props=[("Dewback trough", "art:tatooine:dewback-trough", 2, 1, (30, 12)), v((15, 5)), v((45, 15)), ("Bantha skeleton", "art:tatooine:bantha-skeleton", 1, 1, (55, 4))])
