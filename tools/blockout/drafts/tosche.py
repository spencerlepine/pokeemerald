import os, sys; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from blockout.draft import Draft, link_all
d = Draft.load("tosche-station")
d.g = [["T"] * 30 for _ in range(26)]
d.clear()
d.doc["exits"] = []
# a crossroads outpost: power station in the north-east, trading post round a plaza
d.blob(15, 13, 13, 11, ".")
d.road([(14, 0), (14, 25)], 2)          # north-south road: route-103 to route-101
d.road([(0, 12), (15, 12)], 2)          # west road to route-102
d.fill(10, 10, 19, 15, ":")             # plaza
d.exit("north", [14, 15], "route-103")
d.exit("south", [14, 15], "route-101")
d.exit("west", [12, 13], "route-102")
d.building("Tosche power station", "art:tatooine:power-station", 18, 3, 6, 4, door=2, to="tosche-station-power-station")
d.road([(20, 7), (20, 10)], 1, only=".")
d.building("Bacta Center", "art:shared:bacta-center", 4, 15, 5, 4, door=2, to="tosche-station-bacta-center-1f")
d.road([(6, 19), (6, 20), (13, 20)], 1, only=".")
d.building("Supply Depot", "art:shared:supply-depot", 20, 15, 4, 4, door=1, to="tosche-station-supply-depot")
d.road([(21, 19), (21, 20), (16, 20)], 1, only=".")
d.building("Converter dealer's home", "art:tatooine:homestead-dome", 5, 4, 5, 4, door=2, to="tosche-station-house-1")
d.road([(7, 8), (7, 11)], 1, only=".")
d.building("Station hand's home", "art:tatooine:homestead-dome", 18, 20, 5, 4, door=2, to="tosche-station-house-2")
for x, y in ((25, 4), (25, 6), (26, 8), (17, 8)):
    d.prop("Power converters", "art:tatooine:power-converters", x, y)
d.prop("Fuel tanks", "art:shared:fuel-tanks", 24, 9, 2, 2)
d.prop("Market stall", "art:tatooine:market-stall", 10, 7, 2, 2)
d.prop("Parked landspeeder", "art:shared:parked-landspeeder", 17, 10, 2, 1)
d.prop("Vaporator", "art:tatooine:moisture-vaporator", 3, 9, 1, 2)
d.prop("Gonk droid", "art:shared:gonk-droid", 19, 13)
d.person("Station girl", 22, 12)
d.person("Depot clerk on a break", 23, 20)
d.person("Spacer who walks in circles", 9, 11)
d.person("Rival (first meeting)", 15, 23, role="story")
d.person("Converter mechanic", 22, 8)
d.sign("Tosche Station holo-sign", 12, 9)
d.sign("Power station sign", 17, 7)
d.doc["status"] = "BLOCKOUT"
d.doc["story"] = "Crossroads trading post round the Tosche power station, where farm kids buy power converters. First Bacta Center and Supply Depot. Roads north, south and west."
d.doc["todo"] = ["New interior: the power station (converters, a mechanic who trades parts)."]
link_all(d); d.save()
