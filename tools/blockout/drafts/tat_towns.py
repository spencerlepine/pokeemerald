import os, sys; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from blockout.draft import Draft, link_all

def fresh(area_id, w, h, fill="T"):
    d = Draft.load(area_id)
    d.g = [[fill] * w for _ in range(h)]
    d.clear(); d.doc["exits"] = []; d.doc["status"] = "BLOCKOUT"
    return d

HOME = "art:tatooine:homestead-dome"

# ---------------------------------------------------------------- MOS ENTHA (Petalburg)
d = fresh("mos-entha", 38, 32)
d.blob(19, 16, 17, 14, ".")
d.road([(0, 15), (37, 15)], 2)
d.road([(18, 6), (18, 26)], 2)
d.fill(14, 12, 23, 19, ":")
d.exit("west", [15, 16], "route-104"); d.exit("east", [15, 16], "route-102")
d.building("Mos Entha arena (Doran)", "art:tatooine:mos-entha-arena", 15, 4, 7, 5, door=3, to="mos-entha-arena")
d.building("Lars homestead (Owen and Luke)", "art:tatooine:lars-family-home", 4, 5, 6, 4, door=2, to="mos-entha-lars-home")
d.road([(6, 9), (6, 14)], 1, only=".")
d.building("Bacta Center", "art:shared:bacta-center", 26, 6, 5, 4, door=2, to="mos-entha-bacta-center-1f")
d.road([(28, 10), (28, 14)], 1, only=".")
d.building("Supply Depot", "art:shared:supply-depot", 27, 19, 4, 4, door=1, to="mos-entha-supply-depot")
d.road([(28, 17), (28, 18)], 1, only=".")
d.building("Farmer's home", HOME, 5, 20, 5, 4, door=2, to="mos-entha-house-1")
d.road([(7, 17), (7, 19)], 1, only=".")
d.building("Pilot's widow's home", HOME, 13, 24, 5, 4, door=2, to="mos-entha-house-2")
d.road([(15, 28), (17, 28)], 1, only=".")
d.prop("Market stall", "art:tatooine:market-stall", 21, 21, 2, 2)
d.prop("Market stall", "art:tatooine:market-stall", 24, 21, 2, 2)
d.prop("Dewback trough", "art:tatooine:dewback-trough", 11, 9, 2, 1)
for x, y in ((3, 10), (11, 6), (33, 12), (33, 22), (3, 18)):
    d.prop("Vaporator", "art:tatooine:moisture-vaporator", x, y, 1, 2)
d.prop("Parked landspeeder", "art:shared:parked-landspeeder", 10, 12, 2, 1)
d.prop("Old Clone Wars starfighter (Doran's)", "art:shared:landing-pad", 30, 25, 4, 4)
d.person("Owen Lars", 8, 11, "story"); d.person("Doran's student", 20, 10)
d.person("Farmer", 24, 17); d.person("Kid with a pit droid", 12, 19); d.person("Market trader", 23, 23)
d.person("Spacer admiring the starfighter", 29, 27)
d.sign("Town holo-sign", 25, 14); d.sign("Arena sign", 22, 9); d.sign("Lars homestead sign", 10, 10)
d.doc["story"] = "Farm town where the player's father Doran leads the Normal arena. Owen Lars and Luke live in the homestead on the west side. A market square sits at the crossroads."
d.doc["todo"] = ["Vanilla's Wally's house becomes the Lars homestead (interior id mos-entha-lars-home).",
                 "Doran's old starfighter on its pad is new: a talk spot about his Clone Wars days."]
link_all(d); d.save()

# ---------------------------------------------------------------- BESTINE (Rustboro)
d = fresh("bestine", 48, 62)
d.blob(24, 31, 22, 29, ".", rough=0.1)
d.road([(22, 0), (22, 61)], 3)                       # the long main street, north to south
d.road([(23, 6), (47, 6)], 2)                        # east road to route-116
d.fill(15, 28, 31, 35, ":")                          # government plaza
d.exit("north", [22, 23, 24], "route-115"); d.exit("south", [23, 24], "route-104"); d.exit("east", [6, 7], "route-116")
d.building("House Organa office tower", "art:tatooine:house-organa-office-tower", 8, 9, 8, 7, door=4, to="bestine-organa-tower-1f")
d.road([(12, 16), (12, 18), (21, 18)], 1, only=".")
d.building("Bestine arena (Biggs)", "art:shared:arena", 30, 17, 6, 5, door=3, to="bestine-arena")
d.road([(33, 22), (33, 24), (25, 24)], 1, only=".")
d.building("Academy", "art:tatooine:academy", 32, 30, 6, 4, door=3, to="bestine-academy")
d.road([(35, 34), (35, 36), (32, 36)], 1, only=".")
d.building("Bacta Center", "art:shared:bacta-center", 14, 38, 5, 4, door=2, to="bestine-bacta-center-1f")
d.road([(16, 42), (16, 43), (21, 43)], 1, only=".")
d.building("Supply Depot", "art:shared:supply-depot", 27, 39, 4, 4, door=1, to="bestine-supply-depot")
d.road([(28, 43), (28, 44), (25, 44)], 1, only=".")
d.building("Flats (east)", "art:tatooine:sunken-courtyard-home", 9, 24, 6, 6, door=2, to="bestine-flat-1-1f")
d.building("Flats (south)", "art:tatooine:sunken-courtyard-home", 6, 50, 6, 6, door=3, to="bestine-flat-2-1f")
d.road([(9, 56), (9, 57), (21, 57)], 1, only=".")
d.building("Vibroblade smith", HOME, 6, 39, 5, 4, door=2, to="bestine-cutters-house")
d.road([(8, 43), (8, 46), (21, 46)], 1, only=".")
d.building("Retired podracer's home", HOME, 37, 10, 5, 4, door=2, to="bestine-house-1")
d.building("Biggs's family home", HOME, 37, 24, 5, 4, door=2, to="bestine-house-2")
d.road([(39, 28), (39, 29)], 1, only=".")
d.building("Trader's home", HOME, 30, 48, 5, 4, door=2, to="bestine-house-3")
d.road([(32, 52), (32, 53), (25, 53)], 1, only=".")
d.prop("Skyhopper on a pad", "art:shared:landing-pad", 38, 39, 4, 4)
for i, (x, y) in enumerate(((17, 30), (27, 30), (17, 33), (27, 33))):
    d.prop("Market stall", "art:tatooine:market-stall", x, y, 2, 2)
d.prop("Fountain (Organa gift)", "art:shared:fuel-tanks", 21 - 4, 20, 2, 2)
for x, y in ((5, 20), (42, 33), (12, 47), (36, 55), (4, 32)):
    d.prop("Vaporator", "art:tatooine:moisture-vaporator", x, y, 1, 2)
d.prop("Cargo crates", "art:shared:cargo-crates", 26, 10, 2, 2)
d.person("Sen. Organa (visiting the tower)", 13, 17, "story")
d.person("Biggs's student", 31, 23); d.person("Organa engineer", 16, 18); d.person("Academy kid", 34, 35)
d.person("Market trader", 19, 31); d.person("Market trader", 29, 31); d.person("Old spacer", 25, 48)
d.person("Guard at the tower", 21, 15); d.person("Speeder racer", 40, 44)
d.sign("City holo-sign", 21, 4); d.sign("Arena sign", 29, 22); d.sign("Academy sign", 31, 34); d.sign("Organa tower sign", 17, 16)
d.doc["story"] = "Tatooine's capital: one long main street from the Dune Sea road in the south to Route 115 in the north, with the House Organa office tower, the academy and Biggs's Rock arena round a market plaza."
d.doc["todo"] = ["The fountain is a placeholder prop; it needs its own concept row.", "Two flats buildings keep vanilla's two apartment interiors."]
link_all(d); d.save()
