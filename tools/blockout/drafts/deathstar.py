import os; exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "common.py")).read())
NEW = "art:new:"
def deck(rid, name, w, h, story, blocks, warps, people, props=(), todo=()):
    d = Draft.new(rid, name, "DEATH STAR", w, h, kind="dungeon", fill="|", folder="caves")
    d.fill(1, 2, w - 2, h - 2, "_")
    for x0, y0, x1, y1 in blocks:
        d.fill(x0, y0, x1, y1, "|")
    for n, x, y, to in warps:
        d.set(x, y, "_"); d.warp(n, x, y, to)
    for p in props:
        d.prop(*p)
    for n, x, y, role in people:
        d.person(n, x, y, role)
    d.doc["story"] = story
    d.doc["todo"] = ["Net-new area net:death-star-site (bible/NET_NEW_DESIGNS.md). Placeholder: Trainer Hill floors, tileset and elevator scripts."] + list(todo)
    link_all(d); d.save()

deck("death-star-hangar", "DEATH STAR HANGAR", 26, 16,
     "Post-game: an Imperial shuttle from Yavin 4 sets down in a half-built hangar bay of the Death Star. The lift leads into the construction decks.",
     [], [("Shuttle ramp (back to Yavin 4)", 13, 15, "yavin-4-launch-tower-1f"), ("Lift to DS-1", 13, 2, "death-star-ds-1")],
     [("Deck officer", 10, 6, "trainer"), ("Rebel infiltrator", 18, 11, "story")],
     props=[("Imperial shuttle", NEW + "imperial-shuttle", 3, 8, 6, 4), ("TIE fighter rack", NEW + "tie-rack", 18, 3, 6, 3),
            ("Cargo crates", "art:shared:cargo-crates", 21, 12, 2, 2)],
     todo=["Unlocks after the Hall of Fame (flag:sys-game-clear); the shuttle NPC in the Rebel hangar sets flag:unused-0x024."])
FLOORS = [
    ("Construction scaffolds", [(4, 4, 8, 6), (16, 4, 20, 6), (4, 10, 8, 12), (16, 10, 20, 12)]),
    ("Reactor feed corridors", [(3, 5, 21, 5), (3, 10, 21, 10)]),
    ("Detention block", [(3, 3, 7, 6), (10, 3, 14, 6), (17, 3, 21, 6), (3, 10, 21, 11)]),
    ("Turbolaser battery", [(6, 4, 7, 13), (12, 2, 13, 9), (18, 6, 19, 13)]),
    ("Command deck", [(3, 3, 9, 4), (15, 3, 21, 4)]),
]
for i, (what, blocks) in enumerate(FLOORS, 1):
    up = f"death-star-ds-{i + 1}" if i < 5 else None
    down = f"death-star-ds-{i - 1}" if i > 1 else "death-star-hangar"
    warps = [("Lift down", 12, 15, down)] + ([("Lift up", 12, 2, up)] if up else [])
    people = [("Stormtrooper", 4, 8, "trainer"), ("Imperial officer", 20, 8, "trainer"), ("Stormtrooper", 9, 13, "trainer"),
              ("Item ball", 22, 14, "item")]
    if i == 5:
        people = [("Imperial officer", 4, 8, "trainer"), ("Imperial officer", 20, 8, "trainer"), ("Stormtrooper", 9, 13, "trainer"),
                  ("Grand Moff's aide (final battle)", 12, 6, "story"), ("Item ball", 22, 14, "item")]
    deck(f"death-star-ds-{i}", f"DEATH STAR DS-{i}", 25, 16,
         f"DS-{i}: {what}. Three Imperial trainers (levels 60-70) and one item." + (" The final officer battle sets flag:unused-0x025." if i == 5 else ""),
         blocks, warps, people,
         props=[("Viewport on the half-built sphere", NEW + "death-star-viewport", 2, 2, 3, 1)] if i == 5 else [])
d = Draft.load("yavin-4-launch-tower-1f")
d.doc["travel"] = [t for t in d.doc.get("travel") or [] if t["to"] != "death-star-hangar"] + \
    [{"to": "death-star-hangar", "via": "shuttle", "name": "Imperial shuttle (post-game, after the Hall of Fame)"}]
d.save(render=False)
