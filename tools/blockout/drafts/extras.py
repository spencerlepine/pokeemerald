import os; exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "common.py")).read())
# Places in wiki/mapping/locations.csv that are not their own vanilla map, found by the coverage audit.

# Mirage Isle: vanilla swaps Route 130 to an alternate layout on the days the island shows.
rows, _ = V.terrain_grid("Route130", layout="LAYOUT_ROUTE130_MIRAGE_ISLAND")
d = Draft.new("mirage-isle", "MIRAGE ISLE", "DAGOBAH", len(rows[0]), len(rows), kind="landmark",
              replaces="Route130")
d.g = [list(r) for r in rows]
d.doc["story"] = ("Route 130 on the days Mirage Isle rises out of the far bog: a misty islet with a rare berry tree "
                  "and companions found nowhere else.")
d.doc["travel"] = [{"to": "route-130", "via": "mirage", "name": "The isle sinks again (same route, normal layout)"}]
d.doc["todo"] = ["Alternate layout of Route 130, not its own map: the game picks it with IsMirageIslandPresent.",
                 "Shown without exits so it does not overlap Route 130 on the planet sheet."]
place_near(d, "Mirage Isle berry tree", "art:dagobah:gnarltree", 1, 1, (len(rows[0]) // 2, len(rows) // 2), radius=40)
d.save()
dd = Draft.load("route-130")
dd.doc["travel"] = [t for t in dd.doc.get("travel") or [] if t["to"] != "mirage-isle"] + \
    [{"to": "mirage-isle", "via": "mirage", "name": "Mirage Isle rises (some days)"}]
dd.save(render=False)

# Hideouts (vanilla secret bases): 28 template rooms the player furnishes; one shared kit stands for them.
d = Draft.new("hideout-kit", "HIDEOUT (KIT)", "SHARED", 11, 9, kind="interior", replaces="new",
              fill="|", folder="interiors")
d.fill(1, 2, 9, 7, "_"); d.set(5, 8, "_"); d.warp("Entrance (back to the route)", 5, 8, "MAP_DYNAMIC")
d.prop("Hideout PC", "art:new:hideout-pc", 5, 2, 1, 1)
d.doc["story"] = ("A player hideout: a hollow, tree or bush on a route that the player claims and furnishes "
                  "(vanilla secret base). Decorations come from the Supply Depots.")
d.doc["todo"] = ["Stands for all 28 vanilla secret base templates (4 sizes each of red, brown, blue and yellow caves, trees and shrubs).",
                 "Per-planet hideout spots (Tatooine rock hollows, Endor tree hollows, Hoth ice caves) are picked in the art phase."]
d.save()
dd = Draft.load("route-102")
dd.doc["travel"] = [t for t in dd.doc.get("travel") or [] if t["to"] != "hideout-kit"] + \
    [{"to": "hideout-kit", "via": "hideout", "name": "Any hideout spot on a route (first one the player can claim)"}]
dd.save(render=False)
