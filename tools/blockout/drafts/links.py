import os; exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "common.py")).read())
# Links that are not a door or an edge: ships (StarNAV), shuttles, tides, dives and scripted moves the
# vanilla data cannot show. They live in each area's `travel:` list; the graph is computed from them.
def travel(area, to, via, name):
    d = Draft.load(area)
    t = [x for x in d.doc.get("travel") or [] if x["to"] != to]
    d.doc["travel"] = t + [{"to": to, "via": via, "name": name}]
    d.save(render=False)

for a, n in [("route-122", "Pilgrim landing pad"), ("yavin-4-launch-tower-1f", "Rebel hangar flight deck"),
             ("grand-arena-reception-gate", "Arena dock"), ("wellspring-entrance", "Landing beach"),
             ("atollon-hangar", "Atollon landing strip"), ("mortis-gate-hangar", "Mortis landing"),
             ("cloud-city-hangar", "West landing platform")]:
    travel(a, "starnav", "ship", n)
travel("route-112-shuttle-station", "mustafar-peak-shuttle-station", "shuttle", "Shuttle up to Mustafar Peak")
travel("mustafar-peak-shuttle-station", "route-112-shuttle-station", "shuttle", "Shuttle down to Route 112")
travel("hoth-tundra", "wampa-cave-high-tide-entrance-room", "tide", "Cave mouth when the meltwater is high")
travel("mos-pelgo", "cargo-hold-inside-of-truck", "intro", "Opening scene in the freighter's hold")
for r in ("battle-colosseum-2-p", "battle-colosseum-4-p", "trade-center", "union-room", "record-corner"):
    travel("tosche-station-bacta-center-2f", r, "link", "Any Bacta Center upstairs (link lounge)")
travel("cloud-city-showcase-lobby", "showcase-hall", "script", "Showcase entry")
for i in range(1, 17):
    travel("grand-arena-battle-pyramid-floor", f"battle-pyramid-square-{i:02d}", "script", "Pyramid floor square")
for r in ("grand-arena-battle-pike-room-final", "grand-arena-battle-pike-room-normal", "grand-arena-battle-pike-room-wild-mons"):
    travel("grand-arena-battle-pike-three-path-room", r, "script", "Pike path")
for a, b, n in [("underwater-seafloor-cavern", "drowned-cavern-entrance", "Surface inside the Drowned Cavern"),
                ("underwater-marine-cave", "marine-cave-entrance", "Surface inside the Marine Cave"),
                ("underwater-sealed-chamber", "sealed-vault-outer-room", "Surface inside the Sealed Vault"),
                ("republic-wreck-underwater-2", "republic-wreck-hidden-floor-corridors", "Surface into the hidden floor")]:
    travel(a, b, "emerge", n)
for a, b, n in [("route-134", "underwater-sealed-chamber", "Dive spot over the vault"),
                ("route-134", "underwater-route-134", "Dive spot"),
                ("republic-wreck-room-b1f", "republic-wreck-underwater-1", "Dive into the flooded hold"),
                ("route-127", "underwater-marine-cave", "Roaming dive spot (Marine Cave)")]:
    travel(a, b, "dive", n)

d = Draft.load("krayt-graveyard")
for w in d.doc["warps"]:
    if w["to"] == "route-114-fossil-maniacs-tunnel":
        w["to"], w["name"] = "route-111", "Tunnel to the Dune Sea"
d.doc["todo"] = [t for t in d.doc["todo"] if "fossil" not in t.lower()] + ["Vanilla's far end was the fossil maniac's tunnel on Route 114 (Sullust); it now opens on Route 111."]
d.save()

for h in ("showcase-hall-beauty", "showcase-hall-cool", "showcase-hall-cute", "showcase-hall-smart", "showcase-hall-tough"):
    travel("cloud-city-showcase-lobby", h, "script", "Showcase entry")
travel("wampa-cave-high-tide-entrance-room", "wampa-cave-high-tide-inner-room", "tide", "Inner tunnels at high water")
