import os; exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "common.py")).read())
import glob, os, re
from blockout.area import Area

# ---------------------------------------------------------------- 1. point pilots' doors at real interior ids
for town, fix in {"mos-entha": {"mos-entha-lars-home": "mos-entha-wallys-house"},
                  "anchorhead": {"anchorhead-camies-home": "anchorhead-wandas-house"}}.items():
    d = Draft.load(town)
    for b in d.doc["buildings"]:
        b["to"] = fix.get(b.get("to"), b.get("to"))
    d.save(render=False)

# ---------------------------------------------------------------- 2. new rooms
def room(rid, name, planet, w, h, back, story, props=(), people=(), todo=(), doors=(), replaces="new"):
    d = Draft.new(rid, name, planet, w, h, kind="interior", replaces=replaces, fill="|", folder="interiors")
    d.fill(1, 2, w - 2, h - 2, "_")
    x = w // 2
    d.set(x, h - 1, "_")
    d.warp("Door", x, h - 1, back)
    for n, x2, y2, to in doors:
        d.set(x2, y2, "_"); d.warp(n, x2, y2, to)
    for p in props:
        n, art, px, py, pw, ph = p
        d.prop(n, art, px, py, pw, ph); d.fill(px, py, px + pw - 1, py + ph - 1, "_", only="|")
    for n, px, py, role in people:
        d.person(n, px, py, role)
    d.doc["story"] = story
    d.doc["todo"] = (["New interior (replaces: new); placeholder room, sized for its contents."] if replaces == "new" else
                     [f"Redrawn inside vanilla {replaces}; its scripts and people move here."]) + list(todo)
    d.save()

NEW = "art:new:"
SHIP = ("Ship (nose in the bay)", "art:shared:landing-pad", 0, 0, 0, 0)
def hangar(rid, name, planet, back, ship="Player's ship", extra_people=()):
    room(rid, name, planet, 16, 12, back,
         f"{name}: the player's ship waits in the bay. Talk to the pilot or use the StarNAV console to fly to another planet.",
         props=[(ship, "art:shared:landing-pad", 4, 2, 8, 5), ("StarNAV flight console", NEW + "starnav-console", 13, 7, 1, 1),
                ("Cargo crates", "art:shared:cargo-crates", 1, 7, 2, 2)],
         people=[("Pilot", 8, 8, "story")] + list(extra_people),
         todo=["Ship travel menu = vanilla boat/ferry ticket script; the StarNAV console lists unlocked planets."])

for rid, name, planet, back in [
        ("hoth-hangar", "Hoth survey pad hangar", "HOTH", "hoth-tundra"),
        ("dagobah-hangar", "Dagobah bog landing", "DAGOBAH", "dagobah"),
        ("ilum-hangar", "Ilum landing hangar", "ILUM", "ilum"),
        ("tipoca-city-hangar", "Tipoca landing platform", "KAMINO", "tipoca-city"),
        ("tython-hangar", "Tython landing pad", "TYTHON", "tython-isle-exterior"),
        ("felucia-hangar", "Felucia reserve shuttle gate", "FELUCIA", "felucia-reserve-south"),
        ("asteroid-spire-hangar", "Asteroid docking hollow", "ASTEROID FIELD", "asteroid-spire-entrance")]:
    hangar(rid, name, planet, back)
for rid, a, b, ship in [("hangar-tatooine-kashyyyk", "mos-eisley", "kachirho", "Millennium Falcon"),
                        ("hangar-tatooine-endor", "mos-espa", "route-118", "Rebel shuttle"),
                        ("hangar-tatooine-sullust", "mos-eisley", "pirin", "Sullustan transport")]:
    room(rid, f"{ship} cabin", "SHARED", 18, 12, a,
         f"Ship link between {a} and {b}: the {ship}'s cabin. The pilot flies to the other end; each end's door leads out on its planet.",
         props=[(ship + " cockpit", NEW + "ship-cockpit", 6, 2, 6, 2), ("Dejarik table", NEW + "dejarik-table", 2, 6, 2, 2),
                ("StarNAV flight console", NEW + "starnav-console", 14, 3, 1, 1)],
         people=[("Pilot", 9, 5, "story")],
         doors=[("Ramp (other end)", 17, 9, b)],
         todo=["One cabin for both ends; the script swaps which ramp opens. See net_new.csv for unlock flags."])

room("tosche-station-power-station", "Tosche Station power room", "TATOOINE", 18, 12, "tosche-station",
     "Tosche Station's power converter room: the converters Luke always wanted to pick up. Fixer tinkers here.",
     props=[("Power converters", NEW + "power-converters", 2, 2, 4, 2), ("Generator", "art:shared:fuel-tanks", 12, 2, 3, 3)],
     people=[("Fixer", 8, 5, "npc"), ("Station hand", 4, 8, "npc")])
room("mos-eisley-fan-club", "Mos Eisley Cantina", "TATOOINE", 24, 16, "mos-eisley",
     "The cantina: Wuher at the round bar, the band on the stage, Ponda Baba and Dr. Evazan in a booth, and Greedo looking for Han's crew.",
     props=[("Round bar", NEW + "cantina-bar", 9, 5, 6, 4), ("Band stage", NEW + "band-stage", 2, 2, 5, 2),
            ("Booth", NEW + "cantina-booth", 18, 3, 3, 2), ("Booth", NEW + "cantina-booth", 18, 9, 3, 2), ("Booth", NEW + "cantina-booth", 2, 10, 3, 2)],
     people=[("Wuher", 12, 4, "story"), ("Figrin D'an (band)", 4, 4, "npc"), ("Ponda Baba", 17, 4, "npc"),
             ("Dr. Evazan", 21, 5, "npc"), ("Greedo", 6, 12, "trainer"), ("Patron", 15, 12, "npc")],
     todo=["Vanilla fan club building becomes the cantina (owner's story notes); no story event, Greedo is optional."],
     replaces="SlateportCity_PokemonFanClub")
room("mos-espa-podrace-arena", "Mos Espa podrace grandstand", "TATOOINE", 22, 14, "mos-espa",
     "Podrace grandstand over the course: bookies, pit droids and a view of the Boonta Eve start line.",
     props=[("Grandstand rows", NEW + "grandstand", 2, 2, 18, 3), ("Podracer engine", NEW + "podracer-engine", 3, 8, 3, 2)],
     people=[("Bookie", 12, 7, "npc"), ("Pit droid", 7, 9, "npc"), ("Podrace fan", 16, 10, "npc")])
room("bens-hut-interior", "Ben's hut", "TATOOINE", 14, 10, "bens-hut",
     "Obi-Wan's hermit hut: a sleeping alcove, a work bench and the old chest.",
     props=[("Old chest", NEW + "old-chest", 2, 2, 2, 1), ("Work bench", NEW + "work-bench", 9, 2, 3, 1)],
     people=[("Obi-Wan (Ben)", 6, 4, "story")])
room("jabbas-palace-throne-room", "Jabba's throne room", "TATOOINE", 26, 18, "jabbas-palace",
     "Jabba's throne room: the dais, the band, Bib Fortuna and a trapdoor over the rancor pit (optional battle below).",
     props=[("Jabba's dais", NEW + "jabba-dais", 10, 2, 6, 3), ("Rancor trapdoor grate", NEW + "trapdoor-grate", 11, 8, 4, 2),
            ("Band stage", NEW + "band-stage", 2, 3, 4, 2)],
     people=[("Jabba", 12, 5, "story"), ("Bib Fortuna", 9, 6, "npc"), ("Gamorrean guard", 4, 10, "trainer"),
             ("Gamorrean guard", 21, 10, "trainer"), ("Salacious Crumb", 16, 5, "npc")],
     doors=[("Barge dock stairs", 24, 2, "jabbas-palace-barge-dock")],
     todo=["New interior jabbas-palace-rancor-pit (optional battle) under the trapdoor."])
room("jabbas-palace-barge-dock", "Jabba's barge dock", "TATOOINE", 22, 12, "jabbas-palace-throne-room",
     "Dock under the palace where the sail barge is moored; skiff crews idle by the ramp.",
     props=[("Sail barge (moored)", NEW + "sail-barge", 3, 2, 12, 4)], people=[("Skiff guard", 17, 6, "trainer"), ("Barge crewman", 6, 8, "npc")])

room("kachirho-supply-depot", "Kachirho supply depot", "KASHYYYK", 14, 10, "kachirho",
     "Supply Depot in a Wookiee tree hall (shared kit).", props=[("Counter", "art:shared:supply-depot-interior", 2, 2, 4, 1)],
     people=[("Wookiee clerk", 3, 3, "npc")])
room("rwookrrorro-chief-hut", "Rwookrrorro chief's hut", "KASHYYYK", 16, 12, "rwookrrorro",
     "The village chief's hall high in the wroshyr branches.", props=[("Carved throne", NEW + "wookiee-throne", 7, 2, 2, 2)],
     people=[("Village chief", 8, 5, "story"), ("Wookiee elder", 4, 7, "npc")])
for i in (1, 2):
    room(f"rwookrrorro-hut-{i}", f"Rwookrrorro hut {i}", "KASHYYYK", 12, 10, "rwookrrorro", "A Wookiee family hut.",
         props=[("Bed nest", NEW + "wookiee-bed", 2, 2, 3, 2)], people=[("Wookiee", 6, 5, "npc")])
room("mustafar-mining-control", "Mustafar mining control", "MUSTAFAR", 20, 14, "mustafar-mining-facility",
     "Control room over the lava collectors; Imperial overseers and droid workers.",
     props=[("Control consoles", NEW + "control-console", 4, 2, 12, 2), ("Lava viewport", NEW + "lava-viewport", 2, 6, 3, 3)],
     people=[("Imperial overseer", 10, 5, "trainer"), ("Mining droid", 15, 9, "npc")])
room("endor-battlefield-bunker", "Abandoned shield bunker", "ENDOR", 20, 14, "endor-battlefield",
     "The ruined shield-generator bunker: dead consoles, a locked blast door and a straggler holding out.",
     props=[("Dead consoles", NEW + "control-console", 3, 2, 8, 2), ("Blast door (locked)", NEW + "blast-door", 15, 2, 3, 2)],
     people=[("Stormtrooper straggler", 10, 7, "trainer")])
room("tibanna-refinery-interior", "Tibanna refinery", "BESPIN", 20, 14, "tibanna-refinery",
     "Gas processing hall: tanks, pipes and Ugnaught crews.", props=[("Gas tanks", "art:shared:fuel-tanks", 3, 2, 3, 3), ("Gas tanks", "art:shared:fuel-tanks", 14, 2, 3, 3)],
     people=[("Ugnaught", 9, 6, "npc"), ("Cartel thug", 12, 10, "trainer")])
room("tibanna-refinery-annex", "Carbon-freezing annex", "BESPIN", 18, 14, "tibanna-refinery",
     "The carbon-freezing chamber annex: the pit, the hoses and a frozen block nobody claims.",
     props=[("Carbon-freezing pit", "art:bespin:carbon-freezing-chamber", 6, 3, 6, 4), ("Frozen block", NEW + "carbonite-block", 14, 3, 1, 2)],
     people=[("Ugnaught foreman", 4, 9, "npc")])
for rid, name, story, ppl in [
        ("nijedha-temple-of-the-kyber", "Temple of the Kyber", "Hall of the Guardians of the Whills, kyber lamps along the walls.", [("Chirrut Îmwe", 9, 5, "story"), ("Baze Malbus", 12, 5, "story")]),
        ("nijedha-guardians-quarters", "Guardians' quarters", "Plain rooms where the Guardians rest.", [("Guardian", 6, 5, "npc")]),
        ("nijedha-hostel", "Pilgrim hostel", "Bunks for pilgrims crossing to the temple.", [("Pilgrim", 5, 5, "npc"), ("Innkeeper", 9, 3, "npc")])]:
    room(rid, name, "JEDHA", 18 if "temple" in rid else 14, 12 if "temple" in rid else 10, "nijedha", story, people=ppl,
         todo=["Check Chirrut and Baze against characters.csv before writing their lines."] if "temple" in rid else [])
room("nijedha-bacta-center", "NiJedha Bacta Center", "JEDHA", 14, 10, "nijedha", "Bacta Center (shared kit).",
     props=[("Bacta counter", "art:shared:bacta-center-interior", 4, 2, 6, 1)], people=[("Medic droid", 7, 3, "npc")])
for rid, back, planet in (("nijedha-supply-depot", "nijedha", "JEDHA"), ("ilum-supply-depot", "ilum", "ILUM"),
                          ("tipoca-city-supply-depot", "tipoca-city", "KAMINO")):
    room(rid, "Supply Depot", planet, 14, 10, back, "Supply Depot (shared kit).",
         props=[("Counter", "art:shared:supply-depot-interior", 2, 2, 4, 1)], people=[("Clerk", 3, 3, "npc")])
room("hoth-survey-outpost", "Rebel survey outpost", "HOTH", 20, 14, "hoth-tundra",
     "Prefab survey camp: a scanner table, heaters and bunks. The surveyor hands out a cold-weather item.",
     props=[("Scanner table", NEW + "scanner-table", 7, 3, 5, 2), ("Heater", NEW + "heater", 2, 2, 1, 1), ("Bunks", NEW + "bunks", 15, 2, 3, 3)],
     people=[("Rebel surveyor", 9, 6, "story"), ("Rebel technician", 4, 9, "npc")])
room("hoth-tauntaun-shelter", "Tauntaun shelter", "HOTH", 16, 12, "hoth-tundra", "Stalls for the survey team's tauntauns.",
     props=[("Tauntaun stalls", NEW + "tauntaun-stall", 2, 2, 12, 2)], people=[("Tauntaun handler", 8, 6, "npc")])
room("tipoca-city-cloning-hall", "Tipoca cloning hall", "KAMINO", 26, 16, "tipoca-city",
     "Optional: white halls of growth pods and Kaminoan scientists; a sealed lab tells PROTOCLONE's story.",
     props=[("Growth pods", NEW + "growth-pods", 2, 2, 9, 2), ("Growth pods", NEW + "growth-pods", 15, 2, 9, 2), ("Growth pods", NEW + "growth-pods", 2, 7, 8, 2),
            ("Growth pods", NEW + "growth-pods", 16, 7, 8, 2), ("Sealed lab door", NEW + "blast-door", 12, 2, 2, 1)],
     people=[("Kaminoan scientist", 12, 6, "story"), ("Clone cadet", 6, 11, "trainer"), ("Clone cadet", 19, 11, "trainer")])

# ---------------------------------------------------------------- 3. imported interiors: kit stories
LEADER = {"bestine": "Biggs Darklighter (Rock)", "kachirho": "Tarfful (Fighting)", "mos-espa": "Watto (Electric)",
          "pirin": "Sabine Wren (Fire)", "mos-entha": "Doran, the player's father (Normal)", "bright-tree": "Chief Chirpa (Flying)",
          "yavin-4": "Kanan Jarrus and Ezra Bridger (Force)", "dagobah": "Yoda (Water)"}
def kit_story(a):
    i, town = a.id, None
    for t in LEADER:
        if i.startswith(t + "-"):
            town = t
    if re.search(r"bacta-center-1f$", i): return "Bacta Center: heal counter with the medic droid and the StarNAV terminal (shared kit)."
    if re.search(r"bacta-center-2f$", i): return "Bacta Center upstairs: link and trade lounge (vanilla Cable Club, shared kit)."
    if "supply-depot" in i: return "Supply Depot: counter and shelves (shared kit)."
    if re.search(r"-arena(-|$)", i) and town: return f"{LEADER[town]}'s arena: puzzle floor and arena trainers kept from vanilla."
    if re.search(r"house|home|flat|hut", i): return f"{a.name.title()}: a home; residents keep vanilla's spots and scripts."
    return f"{a.name.title()}: vanilla room layout kept for the blockout."
done = 0
for f in sorted(glob.glob(os.path.join(os.path.dirname(K.__file__), "../../../wiki/world/*/interiors/*.yaml"))):
    a = Area(f)
    if a.status != "TODO" or a.id not in BY_AREA:
        continue
    retheme(a.id, kit_story(a), todo=["Vanilla layout kept; dress with the planet's interior kit in the art phase."])
    done += 1
print("kit interiors:", done)
