"""Hyperlanes (wiki/mapping/hyperlanes.csv): the pilot of each hangar room flies the player.

Two kinds of room:

- A shared cabin (from_room == to_room) has a door to each planet. The player walks in one side; a trigger in
  front of the other side's exit stops them until the pilot has flown (VAR_TEMP_1: 1 came in by the from door,
  2 by the to door, 0 flown). The pilot flies to the to side only once the lane's unlock is met; back is always open.
- A room with one door: its pilot lists every lane that touches the room and asks, one by one, which to fly.
  A trip from the lane's from side needs the unlock; the trip back is always open. The player lands on the
  destination room's first warp, as if they had walked in.

Lanes the vanilla game already flies (Han's first hop, the cable car, the S.S. Tidal and its ticket islands) are
left to their vanilla scripts; a new room at their far end still gets a pilot that flies back.
"""
import csv

from . import base as B


# vanilla scripts fly these (the boat, the cable car, the ferry)
VANILLA = {"hl-tatooine-kashyyyk-han", "hl-tatooine-mustafar", "hl-endor-felucia", "hl-bespin-grand-arena",
           "hl-tatooine-grand-arena", "hl-bespin-tython", "hl-bespin-wellspring", "hl-bespin-atollon",
           "hl-bespin-mortis"}

UNLOCK = {
    "flag:returned-devon-goods": "FLAG_RETURNED_DEVON_GOODS",
    "flag:sys-game-clear": "FLAG_SYS_GAME_CLEAR",
    "item:hm-surf": "FLAG_RECEIVED_HM_SURF",
    "item:hm-dive": "FLAG_RECEIVED_HM_DIVE",
    "event:devon-scope": "FLAG_RECEIVED_DEVON_SCOPE",
    "event:sootopolis-crisis": "FLAG_WALLACE_GOES_TO_SKY_PILLAR",
    "event:mt-pyre-orbs": "FLAG_RECEIVED_RED_OR_BLUE_ORB",
    "event:meteor-falls-meteorite": "FLAG_MET_ARCHIE_METEOR_FALLS",
}


def unlock_flag(tok):
    if not tok:
        return None
    if tok in UNLOCK:
        return UNLOCK[tok]
    if tok.startswith("flag:badge"):
        return "FLAG_" + tok[5:].upper().replace("-", "_")
    raise ValueError(f"hyperlane unlock {tok!r} has no game flag in lanes.UNLOCK")


def load():
    path = B.MAPPING / "hyperlanes.csv"
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def planet_name(p):
    return p.strip().upper()


class Lanes:
    def __init__(self, world):
        self.world = world
        self.shared = {}          # room -> lane
        self.trips = {}           # room -> [(dest planet, dest room, unlock flag or None)]
        for ln in load():
            fr, to = ln["from_room"], ln["to_room"]
            if not fr or not to:
                continue
            if fr == to:
                self.shared[fr] = ln
                continue
            if ln["id"] not in VANILLA:
                flag = unlock_flag(ln["unlock"])
                self.trips.setdefault(fr, []).append((planet_name(ln["to_planet"]), to, flag))
            self.trips.setdefault(to, []).append((planet_name(ln["from_planet"]), fr, None))

    def has_pilot(self, a):
        return a.id in self.shared or a.id in self.trips

    def installed(self, room):
        return room in self.world.areas and self.world.installed(room)

    # ---------------------------------------------------------------- one-door rooms
    def pilot_script(self, blk, a, key):
        label = blk.label("EventScript", key)
        if a.id in self.shared:
            return self.cabin_pilot(blk, a, key)
        trips = [t for t in self.trips[a.id] if self.installed(t[1])]
        body = ["\tlock", "\tfaceplayer"]
        if not trips:
            body += [f"\tmsgbox {blk.text(key, 1, 'PILOT: Strap in. ...Once we have somewhere to go.')}, "
                     "MSGBOX_DEFAULT", "\trelease", "\tend"]
            blk.script(label, "\n".join(body) + "\n")
            return label
        body.append(f"\tmsgbox {blk.text(key, 1, 'PILOT: Strap in. Where are we headed?')}, MSGBOX_DEFAULT")
        for i, (planet, room, flag) in enumerate(trips, 1):
            skip = f"{label}_Next{i}"
            if flag:
                body.append(f"\tgoto_if_unset {flag}, {skip}")
            ask = blk.text(key, 10 + i, f"PILOT: {planet}?")
            body += [f"\tmsgbox {ask}, MSGBOX_YESNO", f"\tgoto_if_eq VAR_RESULT, YES, {label}_Fly{i}", f"{skip}:"]
        body += [f"\tmsgbox {blk.text(key, 2, 'PILOT: No clearance for anywhere else yet. I will be right here.')}"
                 ", MSGBOX_DEFAULT", "\trelease", "\tend", ""]
        go = blk.text(key, 3, "PILOT: Punch it!")
        for i, (planet, room, flag) in enumerate(trips, 1):
            dest = self.world.areas[room]
            body += [f"{label}_Fly{i}:", f"\tmsgbox {go}, MSGBOX_DEFAULT", "\tclosemessage",
                     "\tplayse SE_HYPERSPACE_JUMP", "\twaitse", f"\twarp {dest.map_const}, 0", "\twaitstate",
                     "\trelease", "\tend", ""]
        blk.script(label, "\n".join(body))
        return label

    # ---------------------------------------------------------------- shared cabins
    def cabin_warps(self, a):
        """(from door, to door): the room's warps to the lane's from and to areas."""
        ln = self.shared[a.id]
        ws = self.world.warps[a.id]
        fr = next(w for w in ws if w.to == ln["from_area"])
        to = next(w for w in ws if w.to == ln["to_area"])
        return fr, to

    def inside(self, a, w):
        """The one open cell next to warp w, and the step that walks back from it into the room."""
        for dx, dy, back in ((0, -1, "walk_up"), (-1, 0, "walk_left"), (1, 0, "walk_right"), (0, 1, "walk_down")):
            x, y = w.x + dx, w.y + dy
            if 0 <= x < a.w and 0 <= y < a.h and a.grid[y][x] == "_":
                return x, y, back
        raise ValueError(f"{a.id}: no open cell next to the warp at ({w.x},{w.y})")

    def cabin_pilot(self, blk, a, key):
        ln = self.shared[a.id]
        label = blk.label("EventScript", key)
        flag = unlock_flag(ln["unlock"])
        to_p, fr_p = planet_name(ln["to_planet"]), planet_name(ln["from_planet"])
        flown = blk.text(key, 1, "PILOT: We are here. Off you go, the hatch is open.")
        locked = blk.text(key, 2, f"PILOT: No clearance for {to_p} yet. Come back when you have it.")
        go = blk.text(key, 3, "PILOT: Strap in. Punch it!")
        ask_to = blk.text(key, 4, f"PILOT: {to_p}?")
        ask_fr = blk.text(key, 5, f"PILOT: Back to {fr_p}?")
        body = ["\tlock", "\tfaceplayer", f"\tgoto_if_eq VAR_TEMP_1, 0, {label}_Flown",
                f"\tgoto_if_eq VAR_TEMP_1, 2, {label}_Back"]
        if flag:
            body.append(f"\tgoto_if_unset {flag}, {label}_Locked")
        body += [f"\tmsgbox {ask_to}, MSGBOX_YESNO", f"\tgoto_if_eq VAR_RESULT, YES, {label}_Fly", "\trelease",
                 "\tend", "", f"{label}_Back:", f"\tmsgbox {ask_fr}, MSGBOX_YESNO",
                 f"\tgoto_if_eq VAR_RESULT, YES, {label}_Fly", "\trelease", "\tend", "",
                 f"{label}_Fly:", f"\tmsgbox {go}, MSGBOX_DEFAULT", "\tclosemessage", "\tplayse SE_HYPERSPACE_JUMP",
                 "\tfadescreen FADE_TO_BLACK", "\twaitse", "\tsetvar VAR_TEMP_1, 0", "\tfadescreen FADE_FROM_BLACK",
                 "\trelease", "\tend", "", f"{label}_Flown:", f"\tmsgbox {flown}, MSGBOX_DEFAULT", "\trelease", "\tend",
                 ""]
        if flag:
            body += [f"{label}_Locked:", f"\tmsgbox {locked}, MSGBOX_DEFAULT", "\trelease", "\tend", ""]
        blk.script(label, "\n".join(body))
        return label

    def cabin_map_scripts(self, a):
        """The map script header of a shared cabin: which side the player came in by."""
        fr, to = self.cabin_warps(a)
        m = a.map_name
        return (f"{m}_MapScripts::\n\tmap_script MAP_SCRIPT_ON_TRANSITION, {m}_OnTransition\n\t.byte 0\n\n"
                f"{m}_OnTransition:\n\tsetvar VAR_TEMP_1, 1\n\tgetplayerxy VAR_TEMP_2, VAR_TEMP_3\n"
                f"\tgoto_if_ne VAR_TEMP_2, {to.x}, {m}_OnTransitionEnd\n"
                f"\tgoto_if_ne VAR_TEMP_3, {to.y}, {m}_OnTransitionEnd\n\tsetvar VAR_TEMP_1, 2\n"
                f"{m}_OnTransitionEnd:\n\tend\n\n")

    def cabin_triggers(self, blk, a):
        """Coord events in front of each exit: the side the player did not come in by is shut until they fly."""
        fr, to = self.cabin_warps(a)
        out = []
        text = blk.text("CabinHatch", 1, "PILOT: Hold on! Talk to me before you go out that hatch.")
        for w, val in ((to, 1), (fr, 2)):
            x, y, back = self.inside(a, w)
            lab = blk.label("EventScript", f"CabinHatch{val}")
            blk.script(lab, f"\tlockall\n\tmsgbox {text}, MSGBOX_DEFAULT\n\tclosemessage\n"
                            f"\tapplymovement OBJ_EVENT_ID_PLAYER, {lab}_Back\n\twaitmovement 0\n\treleaseall\n\tend\n\n"
                            f"{lab}_Back:\n\t{back}\n\tstep_end\n")
            out.append({"type": "trigger", "x": x, "y": y, "elevation": 0, "var": "VAR_TEMP_1",
                        "var_value": str(val), "script": lab})
        return out
