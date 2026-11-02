import os; exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "common.py")).read())
FAC = "art:grand-arena:arena-facilities"

def brains(pairs):
    """Put each facility's bounty-hunter boss beside its door: pairs of (warp target, name)."""
    def f(d):
        for to, who in pairs:
            for b in d.doc["buildings"]:
                if b.get("to") == to and "door" in b:
                    x, y = b["at"][0] + int(b["door"]) + 1, b["at"][1] + b["size"][1]
                    if d.get(x, y) in (".", ":", '"'):
                        d.person(who, x, y, "story")
                    break
    return f

# ================================================================ GRAND ARENA
retheme("grand-arena-outside-west", art_house=FAC, extra=brains([
            ("grand-arena-battle-dome-lobby", "Dengar (Dome)"), ("grand-arena-battle-factory-lobby", "IG-88 (Factory)"),
            ("grand-arena-battle-pike-lobby", "Gardulla the Hutt (Pike)"), ("grand-arena-scotts-house", "Lando")]),
        story="West half of Lando's Grand Arena island: the Dome, Factory and Pike, Lando's own villa, lounges and the supply depot. "
              "Ships dock at the reception gate in the south.",
        people=[("Arena fan", 28, 40, "npc"), ("Bounty hunter's droid", 20, 50, "npc"), ("Gambler", 34, 30, "npc")],
        props=[("Arena holo-sign", "art:shared:holo-sign", 1, 1, (26, 58)), ("Cargo crates", "art:shared:cargo-crates", 2, 2, (40, 60))],
        todo=["The reception gate (vanilla ferry dock) is the ship link: grand-arena-reception-gate becomes the hangar.",
              "Facility bosses (owner's cast): Aurra Sing Tower, Dengar Dome, Zuckuss Palace, 4-LOM Arena, IG-88 Factory, Gardulla Pike, Dexter Jettster Pyramid."])
retheme("grand-arena-outside-east", art_house=FAC, extra=brains([
            ("grand-arena-battle-tower-lobby", "Aurra Sing (Tower)"), ("grand-arena-battle-arena-lobby", "4-LOM (Arena)"),
            ("grand-arena-battle-palace-lobby", "Zuckuss (Palace)"), ("grand-arena-battle-pyramid-lobby", "Dexter Jettster (Pyramid)")]),
        story="East half of the Grand Arena: the Tower, Arena, Palace and Pyramid, the ranking hall, the exchange corner, the Bacta Center and more lounges. "
              "Artisan Cave opens in the cliffs.",
        people=[("Arena fan", 30, 30, "npc"), ("Tourist", 40, 50, "npc"), ("Ranking hall clerk", 20, 20, "npc")],
        props=[("Arena holo-sign", "art:shared:holo-sign", 1, 1, (36, 36))])
for a in ("artisan-cave-1f", "artisan-cave-b1f"):
    retheme(a, "Artisan Cave: a hidden cave under the Grand Arena cliffs, full of SMEARGLE's Star Wars twin painting the walls.")

# ================================================================ TATOOINE: Altering Cave moves home
retheme("altering-cave", "Altering Cave: a small cave off Route 103 whose single species changes with events (vanilla Mystery Gift).")

# ================================================================ FELUCIA
def felucia_south(d):
    d.warp("Reserve gate and shuttle (ships)", 32, 33, "felucia-hangar")
zones = {
    "felucia-reserve-south": ("Felucia Reserve, south: the gate where shuttles from Endor land, fungus groves and the first long grass.", felucia_south),
    "felucia-reserve-southwest": ("South-west: spore marsh with the rest house.", None),
    "felucia-reserve-northwest": ("North-west: giant fungus forest with ledges (hover-bike jumps).", None),
    "felucia-reserve-north": ("North: tall spore plants and a viewing deck (vanilla Pokéblock feeders).", None),
    "felucia-reserve-northeast": ("North-east: deep water among the fungus stalks (Surf).", None),
    "felucia-reserve-southeast": ("South-east: post-game extension with species from other planets (vanilla Emerald-only area).", None),
}
for a, (s, ex) in zones.items():
    retheme(a, s, extra=ex,
            props=[("Giant fungus", "art:felucia:giant-fungus", 2, 2, (20, 20)), ("Spore-pod plants", "art:felucia:spore-pod-plants", 1, 1, (10, 30))],
            people=[("Reserve ranger", 30, 30, "story")] if a == "felucia-reserve-south" else [], todo=["Reserve rules as vanilla Safari Zone: limited steps, bait and rocks become spore pods and pebbles."] if a == "felucia-reserve-south" else [])

# ================================================================ TYTHON
def tython(d):
    d.warp("Landing pad (ships)", 14, 22, "tython-hangar")
retheme("tython-isle-exterior", "Tython Isle: a small Force-sacred island. A path climbs from the landing pad to the standing stones where ASHLA or BOGAN appears.",
        extra=tython, props=[("Tython standing stones", "art:grand-arena:tython-standing-stones", 2, 2, (20, 9))],
        todo=["New interior: tython-hangar (vanilla Southern Island had only the ferry dock)."])
retheme("tython-isle-interior", "The standing-stone circle at the heart of the island, where ASHLA or BOGAN waits.")

# ================================================================ ATOLLON, MORTIS, ASTEROID SPIRE
retheme("atollon-exterior", "Atollon: a rocky moon where the BENDU sleeps on a stone dais. The triangle puzzle (vanilla Birth Island) wakes it.",
        todo=["Was filed as an interior; walked outdoors, so it is a landmark now."])
retheme("atollon-hangar", "Atollon landing strip (vanilla Birth Island harbor).")
retheme("mortis-gate-exterior", "Mortis Gate: a monolith in a strange sea; the doorway leads down into the realm of the FATHER and the DAUGHTER.",
        todo=["Was filed as an interior; walked outdoors, so it is a landmark now."])
retheme("mortis-gate-hangar", "Mortis landing (vanilla Navel Rock harbor).")
for a in ("mortis-gate-entrance", "mortis-gate-b1f", "mortis-gate-fork", "mortis-gate-top", "mortis-gate-bottom") + \
        tuple(f"mortis-gate-up-{i}" for i in range(1, 5)) + tuple(f"mortis-gate-down-{i:02d}" for i in range(1, 12)):
    retheme(a, "Mortis Gate: stairs up to the FATHER's peak and down to the DAUGHTER's hollow.")
retheme("wellspring-entrance", "The Wellspring: a jungle island on Mortis where the PRIMORDIAL hides in the long grass.",
        props=[("Wellspring pool", "art:grand-arena:wellspring-pool", 2, 2, (12, 30))],
        todo=["Was filed as an interior; walked outdoors, so it is a landmark now."])
retheme("wellspring-interior", "The Wellspring's heart: a clearing round the pool of life where the PRIMORDIAL plays hide and seek.")

def spire_dock(d):
    d.warp("Ship berth", 6, 16, "asteroid-spire-hangar")
retheme("asteroid-spire-entrance", "Docking hollow inside the asteroid: ships berth here and a tunnel climbs to the spire.", extra=spire_dock,
        todo=["Vanilla's door to Route 131 becomes the ship berth (new interior: asteroid-spire-hangar)."])
retheme("asteroid-spire-outside", "The asteroid's surface: a crumbling path to the spire's base.",
        props=[("Asteroid spire", "art:grand-arena:asteroid-spire", 2, 2, (14, 6))])
for a in ("asteroid-spire-1f", "asteroid-spire-2f", "asteroid-spire-3f", "asteroid-spire-4f", "asteroid-spire-5f"):
    retheme(a, "Inside the Asteroid Spire: cracked floors (hover-bike speed) and falling rubble.")
retheme("asteroid-spire-top", "Top of the Asteroid Spire, open to space: the EXOGORTH's lair.")
