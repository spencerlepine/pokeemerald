"""Every NPC and every way the player gets something, read from ../game and wired to the wiki.

Reads ../game (map.json events, map and shared scripts, the in-game trade table, the new-game fruit trees),
the Emerald tables in emerald/, the names in database/swap_map.csv and database/area_progression.csv, and two
hand-written files:

  mapping/npcs.csv          which NPC is which named character (`character_id`), and the scripts an NPC
                            delivers that no object event starts (a gift run by a map script, like OWEN's HM03)
  mapping/obtain_extra.csv  gifts the scripts do not show (the starter) and net-new gifts (HM09 from OWEN)
  mapping/obtain_order.csv  story order for a script the flags can't place (a gift run by a map script)

Writes:

  database/npcs.csv    one row per object event on every map: npc_id, map, sprite, script, character, gifts
  database/obtain.csv  one row per way to get something: gift items, TMs and HMs, item balls, hidden items,
                       fruit trees, shop stock, gift companions and eggs, in-game trades, decorations, coins,
                       with the giver, the flag that marks it received, the flags the script checks, and the
                       story order (badges held, story event)

Query examples:
  grep ',character:wallys-father,' database/obtain.csv      everything OWEN gives
  grep '^obtain:' database/obtain.csv | grep ',gift_item,'   every handed-over item, in story order
Run: python3 tools/obtain.py
"""
import csv, glob, json, re
from collections import defaultdict, deque
from pathlib import Path

WIKI = Path(__file__).resolve().parents[1]
GAME = WIKI.parent / "game"


def read(p):
    return list(csv.DictReader(open(p, newline="", encoding="utf-8")))


def write(p, rows, cols):
    with open(p, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    print(len(rows), "rows ->", p.relative_to(WIKI))


def slug(name):                 # PetalburgCity_WallysHouse -> petalburg-city-wallys-house
    return re.sub(r"(?<=[a-z0-9])(?=[A-Z])", "-", name).replace("_", "-").lower()


# ---------- wiki lookups ----------
by_const = {r["source_constant"]: r["id"] for r in read(WIKI / "emerald" / "entities.csv") if r["source_constant"]}
# net-new constants already in ../game
by_const.update({"ITEM_HM_SAND_SKIM": "net:hm09-sand-skim", "ITEM_HM09": "net:hm09-sand-skim", "MOVE_SAND_SKIM": "net:move-sand-skim"})
net_names = {r["id"]: r["sw_name"] for r in read(WIKI / "mapping" / "net_new.csv")}
swap = {r["emerald_id"]: r for r in read(WIKI / "database" / "swap_map.csv")}
prog = {r["map_id"]: r for r in read(WIKI / "database" / "area_progression.csv")}
order_hand = {r["script"] or r["map_prefix"]: r for r in read(WIKI / "mapping" / "obtain_order.csv")}


def area(map_id):
    """The map's balance row, or its parent's (an interior takes its town's): map:petalburg-city-wallys-house -> map:petalburg-city."""
    if not map_id:
        return {}
    m = map_id
    while m and m not in prog:
        m = m.rsplit("-", 1)[0] if "-" in m else ""
    out = dict(prog.get(m, {}))
    if map_id in swap:
        out["sw_map_title"] = swap[map_id]["sw_name"] or out.get("sw_map_title", "")
        out["planet"] = swap[map_id]["planet"] or out.get("planet", "")
    return out
events = read(WIKI / "emerald" / "timeline_events.csv")
ev_seq = {e["id"]: int(e["sequence"]) for e in events}
ev_by_flag = {}
for e in events:
    for f in (e["trigger_flag"], e["completion_flag"]):
        if f.startswith(("FLAG_", "VAR_")):
            ev_by_flag.setdefault(f, e["id"])
ev_by_flag.setdefault("FLAG_SYS_GAME_CLEAR", "champion-wallace")   # the post-game opens with the Hall of Fame
badge_seq = sorted(int(e["sequence"]) for e in events if re.match(r"FLAG_BADGE0\d_GET$", e["completion_flag"]))


def badges_at(ev):
    """Badges held once a story event has happened."""
    return sum(1 for q in badge_seq if q <= ev_seq.get(ev, 0))


def wiki_id(const):
    return by_const.get(const, "")


def sw_name(wid):
    r = swap.get(wid)
    return (r["sw_name"] or r["emerald_name"]) if r else net_names.get(wid, "")


# ---------- scripts ----------
LABEL = re.compile(r"^([A-Za-z_]\w*)::?\s*$")
labels = {}                     # label -> (file, first line no, [lines])
order = []
for f in sorted(glob.glob(str(GAME / "data" / "maps" / "*" / "scripts.inc"))) + sorted(glob.glob(str(GAME / "data" / "scripts" / "*.inc"))) + [str(GAME / "data" / "event_scripts.s")]:
    cur = None
    for n, line in enumerate(open(f, encoding="utf-8"), 1):
        m = LABEL.match(line)
        if m:
            cur = m.group(1)
            labels[cur] = (str(Path(f).relative_to(GAME)), n, [])
            order.append(cur)
            continue
        if cur:
            labels[cur][2].append((n, line.rstrip("\n")))

# fall-through: a label without end/return/goto at its end runs into the next one
TERMINAL = re.compile(r"^\s*(end|return|goto|releaseall\s*;?\s*end|step_end)\b")
refs = defaultdict(set)         # label -> labels it can run next
TOK = re.compile(r"[A-Za-z_]\w*")
for i, lab in enumerate(order):
    lines = labels[lab][2]
    for _, line in lines:
        code = line.split("@")[0]
        if code.strip().startswith("."):
            continue
        for t in TOK.findall(code):
            if t in labels and t != lab:
                refs[lab].add(t)
    body = [l for _, l in lines if l.strip() and not l.strip().startswith("@")]
    if i + 1 < len(order) and body and not TERMINAL.match(body[-1]) and labels[order[i + 1]][0] == labels[lab][0]:
        refs[lab].add(order[i + 1])
back = defaultdict(set)
for a, bs in refs.items():
    for b in bs:
        back[b].add(a)

# ---------- maps and NPCs ----------
npc_hand = {r["npc_id"]: r for r in read(WIKI / "mapping" / "npcs.csv")}
script_to_npc = {}              # extra scripts an NPC delivers (map-script gifts)
for r in npc_hand.values():
    for s in filter(None, r["scripts"].split("|")):
        script_to_npc[s] = r["npc_id"]

npcs, entry, var_cond = [], {}, {}            # entry script label -> list of (kind, npc_id or "", map_id)
map_of_folder, berry_tree_npc = {}, {}
berry_consts = {m.group(1): m.group(2) for m in re.finditer(r"#define (BERRY_TREE_\w+)\s+(\d+)", (GAME / "include/constants/berry.h").read_text())}
for f in sorted(glob.glob(str(GAME / "data" / "maps" / "*" / "map.json"))):
    m = json.load(open(f))
    mid = wiki_id(m["id"]) or "map:" + slug(m["name"])
    map_of_folder[m["name"]] = mid
    for i, o in enumerate(m.get("object_events") or [], 1):
        nid = f"npc:{mid[4:]}:{i}"
        gfx = o.get("graphics_id", "")
        kind = ("item_ball" if gfx == "OBJ_EVENT_GFX_ITEM_BALL" else "berry_tree" if gfx == "OBJ_EVENT_GFX_BERRY_TREE"
                else "trainer" if o.get("trainer_type", "TRAINER_TYPE_NONE") != "TRAINER_TYPE_NONE" else "person")
        if o.get("type") == "clone":
            kind = "clone"
        if kind == "berry_tree":
            t = o.get("trainer_sight_or_berry_tree_id", "0")
            berry_tree_npc[berry_consts.get(t, t)] = nid
        npcs.append({"npc_id": nid, "map_id": mid, "local_id": o.get("local_id", str(i)), "kind": kind,
                     "graphics_id": gfx, "script": o.get("script", ""), "flag": o.get("flag", "0"),
                     "x": o.get("x", ""), "y": o.get("y", "")})
        if o.get("script") and o["script"] != "0x0":
            entry.setdefault(o["script"], []).append(("npc", nid, mid))
    for b in m.get("bg_events") or []:
        if b.get("script"):
            entry.setdefault(b["script"], []).append(("sign", "", mid))
    for c in m.get("coord_events") or []:
        if c.get("script"):
            entry.setdefault(c["script"], []).append(("step", "", mid))
for lab, (f, _, lines) in labels.items():   # map-script tables start scripts too
    if lab.endswith("_MapScripts") or "OnFrame" in lab or "OnTransition" in lab or "OnLoad" in lab or "OnWarp" in lab or "OnResume" in lab:
        folder = Path(f).parent.name
        for _, l in lines:
            for t in TOK.findall(l.split("@")[0]):
                if t in labels and t != lab:
                    entry.setdefault(t, []).append(("map_script", "", map_of_folder.get(folder, "")))
                    mv = re.match(r"\s*map_script_2\s+(VAR_\w+),\s*(\w+),", l)
                    if mv:
                        var_cond[t] = f"{mv.group(1)}={mv.group(2)}"

FLAGCHK = re.compile(r"(goto_if_set|goto_if_unset|call_if_set|call_if_unset|checkflag|goto_if_eq|goto_if_ne|goto_if_lt|goto_if_ge|goto_if_le|goto_if_gt|call_if_eq|call_if_ge|call_if_lt)\s+((?:FLAG|VAR)_\w+)")


def givers(label):
    """Entry points that can run `label`: [(kind, npc_id, map_id, [labels on the path])], nearest first."""
    if label in script_to_npc:
        nid = script_to_npc[label]
        return [("npc", nid, "map:" + nid.split(":")[1], [label])]
    out, seen, q = [], {label}, deque([(label, [label])])
    while q:
        lab, path = q.popleft()
        if lab in script_to_npc and lab != label:
            nid = script_to_npc[lab]
            out.append(("npc", nid, "map:" + nid.split(":")[1], path))
        for e in entry.get(lab, []):
            out.append((*e, path))
        if len(path) > 8:
            continue
        for p in sorted(back.get(lab, ())):
            if p not in seen:
                seen.add(p)
                q.append((p, path + [p]))
    rank = {"npc": 0, "step": 1, "map_script": 2, "sign": 3}
    return sorted(out, key=lambda e: (rank[e[0]], len(e[3])))


def checks_on(path):
    flags = []
    for lab in path:
        for _, l in labels[lab][2]:
            m = FLAGCHK.search(l)
            if m and m.group(2) not in flags:
                flags.append(m.group(2))
        if lab in var_cond and var_cond[lab] not in flags:
            flags.append(var_cond[lab])
    return flags


def set_flag_after(lines, idx):
    for _, l in lines[idx + 1: idx + 8]:
        m = re.match(r"\s*setflag\s+(FLAG_\w+)", l)
        if m:
            return m.group(1)
        if re.match(r"\s*(end|return|goto)\b", l):
            break
    return ""


def story(map_id, flags):
    """(badges held, story event id) for a map and the flags its script checks or sets."""
    p = area(map_id)
    b = int(p["badges_expected"]) if p.get("badges_expected", "").isdigit() else None
    ev = p.get("first_story_event", "")
    for f in flags:
        m = re.match(r"FLAG_BADGE0(\d)_GET", f)
        if m:
            b = max(b or 0, int(m.group(1)))
        e = ev_by_flag.get(f.split("=")[0])
        if e and ev_seq.get(e, 0) > ev_seq.get(ev, 0):
            ev = e
    if ev:
        b = max(b or 0, badges_at(ev))
    for o in order_hand.values():
        if o["map_prefix"] and map_id.startswith(o["map_prefix"]) and b is None:
            b, ev = int(o["badges"]), o["story_event"]
    return b, ev


# ---------- scan ----------
rows = []
GIVE = re.compile(r"^\s*(giveitem|finditem|additem|givemon|giveegg|givedecoration|addcoins)\s+([^@]*)")


def add(kind, what_const, qty, label, line_no, flag, notes="", what_id=None, giver=None):
    f, _, _ = labels[label] if label in labels else ("", 0, [])
    gs = givers(label) if label in labels else []
    g = giver or (gs[0] if gs else ("", "", "", [label]))
    gkind, nid, mid, path = g
    if not nid and label in labels:     # a map script or step trigger: the NPC it moves or talks through
        consts = [t for lab in [label] + list(path) if lab in labels for _, l in labels[lab][2] for t in re.findall(r"\bLOCALID_\w+", l)]
        local = {n["local_id"]: n["npc_id"] for n in npcs if n["local_id"].startswith("LOCALID_") and (not mid or n["map_id"] == mid)}
        hit = next((local[c] for c in consts if c in local), "")
        if hit:
            nid = hit
            mid = mid or "map:" + hit.split(":")[1]
    if not mid and f.startswith("data/maps/"):
        mid = map_of_folder.get(Path(f).parent.name, "")
    if not nid and gkind == "" and mid == "":
        pass
    chk = checks_on(path) if path and path[0] in labels else []
    b, ev = story(mid, chk + [flag])
    if label in order_hand:
        b, ev = int(order_hand[label]["badges"]), order_hand[label]["story_event"]
    wid = what_id if what_id is not None else wiki_id(what_const)
    rows.append({"kind": kind, "what": wid or what_const, "sw_name": sw_name(wid) if wid else "", "quantity": qty,
                 "npc_id": nid, "started_by": gkind, "map_id": mid, "sw_map": area(mid).get("sw_map_title", ""),
                 "planet": area(mid).get("planet", ""), "badges": b, "story_event": ev, "flag": flag,
                 "checks": "|".join(chk), "script": label, "source": f"{f}:{line_no}" if f else "", "notes": notes})


for lab, (f, _, lines) in labels.items():
    for i, (n, l) in enumerate(lines):
        m = GIVE.match(l)
        if not m:
            continue
        cmd, args = m.group(1), [a.strip() for a in m.group(2).split("//")[0].split(",")]
        if not re.match(r"(ITEM|SPECIES|DECOR)_[A-Z0-9_]+$", args[0]) and cmd != "addcoins":
            continue            # a macro body or a variable, not one fixed gift
        if args and args[0].startswith("VAR_"):
            continue            # a variable item (lottery, fan club...); its table is not a single gift
        if cmd in ("giveitem", "additem", "finditem"):
            qty = args[1] if len(args) > 1 else "1"
            gs = givers(lab)
            ball = any(e[0] == "npc" and next((x for x in npcs if x["npc_id"] == e[1]), {}).get("kind") == "item_ball" for e in gs[:1])
            flag = ""
            if ball:
                nid = gs[0][1]
                flag = next(x for x in npcs if x["npc_id"] == nid)["flag"]
            add("item_ball" if ball else "gift_item", args[0], qty, lab, n, flag or set_flag_after(lines, i))
        elif cmd == "givemon":
            add("gift_companion", args[0], "1", lab, n, set_flag_after(lines, i), f"level {args[1]}" + (f", holds {args[2]}" if len(args) > 2 and args[2] != "ITEM_NONE" else ""))
        elif cmd == "giveegg":
            add("gift_egg", args[0], "1", lab, n, set_flag_after(lines, i))
        elif cmd == "givedecoration":
            add("gift_decoration", args[0], "1", lab, n, set_flag_after(lines, i))
        elif cmd == "addcoins":
            add("coins", "", args[0], lab, n, set_flag_after(lines, i), what_id="item:coin-case")
    # shops: pokemart <list label>
    for n, l in lines:
        m = re.match(r"\s*(pokemart|pokemartdecoration2?)\s+(\w+)", l)
        if m and m.group(2) in labels:
            dec = m.group(1) != "pokemart"
            for ln, item in labels[m.group(2)][2]:
                im = re.match(r"\s*\.2byte\s+((?:ITEM|DECOR)_\w+)", item)
                if im and im.group(1) not in ("ITEM_NONE", "DECOR_NONE"):
                    add("decoration_shop" if dec else "shop", im.group(1), "", lab, ln, "", f"stock of {m.group(2)}")

# hidden items
for f in sorted(glob.glob(str(GAME / "data" / "maps" / "*" / "map.json"))):
    m = json.load(open(f))
    mid = map_of_folder[m["name"]]
    for b in m.get("bg_events") or []:
        if b["type"] == "hidden_item":
            p = area(mid)
            wid = wiki_id(b["item"])
            bb, ev = story(mid, [])
            rows.append({"kind": "hidden_item", "what": wid or b["item"], "sw_name": sw_name(wid), "quantity": "1", "npc_id": "",
                         "started_by": "hidden", "map_id": mid, "sw_map": p.get("sw_map_title", ""), "planet": p.get("planet", ""),
                         "badges": bb, "story_event": ev, "flag": b["flag"], "checks": "", "script": "",
                         "source": f"{Path(f).relative_to(GAME)} (x {b['x']}, y {b['y']})", "notes": ""})

# fruit trees planted at new game
for n, l in enumerate(open(GAME / "data/scripts/new_game.inc"), 1):
    m = re.match(r"\s*setberrytree\s+(\w+),\s*ITEM_TO_BERRY\((ITEM_\w+)\)", l)
    if m:
        nid = berry_tree_npc.get(berry_consts.get(m.group(1), ""), "")
        mid = "map:" + nid.split(":")[1] if nid else ""
        wid = wiki_id(m.group(2))
        bb, ev = story(mid, [])
        p = area(mid)
        rows.append({"kind": "berry_tree", "what": wid, "sw_name": sw_name(wid), "quantity": "", "npc_id": nid,
                     "started_by": "tree", "map_id": mid, "sw_map": p.get("sw_map_title", ""), "planet": p.get("planet", ""),
                     "badges": bb, "story_event": ev, "flag": m.group(1), "checks": "", "script": "",
                     "source": f"data/scripts/new_game.inc:{n}", "notes": "fruit tree planted at new game; regrows"})

# in-game trades
trades = {}
src = (GAME / "src/data/trade.h").read_text()
for m in re.finditer(r"\[(INGAME_TRADE_\w+)\]\s*=\s*\{(.*?)\n\s*\},", src, re.S):
    body = m.group(2)
    g = lambda k: (re.search(rf"\.{k}\s*=\s*([^,\n]+)", body) or [None, ""])[1].strip()
    trades[m.group(1)] = (g("species"), g("requestedSpecies"), g("heldItem"), g("nickname"))
for lab, (f, _, lines) in labels.items():
    for n, l in lines:
        m = re.match(r"\s*setvar\s+VAR_0x8008,\s*(INGAME_TRADE_\w+)", l)
        if m and m.group(1) in trades:
            sp, req, held, nick = trades[m.group(1)]
            add("trade", sp, "1", lab, n, "", f"for {sw_name(wiki_id(req)) or req} ({wiki_id(req) or req}); nickname {nick}"
                + (f"; holds {sw_name(wiki_id(held)) or held}" if held and held != "ITEM_NONE" else ""))

# hand-written extras (starter, net-new gifts)
key_of = {}
for r in rows:
    r["obtain_id"] = ""
for r in read(WIKI / "mapping" / "obtain_extra.csv"):
    after = r["after_script"]
    base = after and next((x for x in rows if x["script"] == after and (not r["after_what"] or x["what"] == r["after_what"])), None)
    nid = r["npc_id"]
    mid = r["map_id"] or (base["map_id"] if base else "")
    p = area(mid)
    bb, ev = (base["badges"], base["story_event"]) if base else story(mid, [])
    rows.append({"kind": r["kind"], "what": r["what"], "sw_name": "|".join(filter(None, map(sw_name, r["what"].split("|")))) or r["sw_name"], "quantity": r["quantity"],
                 "npc_id": nid, "started_by": "npc" if nid else "", "map_id": mid, "sw_map": p.get("sw_map_title", ""),
                 "planet": p.get("planet", ""), "badges": bb, "story_event": ev, "flag": r["flag"] or (base["flag"] if base else ""),
                 "checks": base["checks"] if base else "", "script": after, "source": "mapping/obtain_extra.csv",
                 "notes": r["notes"], "obtain_id": r["obtain_id"], "_after": 1})

# ---------- characters and order ----------
npc_by_id = {n["npc_id"]: n for n in npcs}
for n in npcs:
    h = npc_hand.get(n["npc_id"], {})
    n["character_id"] = h.get("character_id", "")
    n["sw_name"] = sw_name(n["character_id"]) if n["character_id"] else ""
    n["notes"] = h.get("notes", "")
for r in rows:
    c = npc_hand.get(r["npc_id"], {}).get("character_id", "")
    r["character_id"], r["character_sw_name"] = c, (sw_name(c) if c else "")
    r["story_order"] = "" if r["badges"] in (None, "") else f"{int(r['badges']):d}.{ev_seq.get(r['story_event'], 0):02d}"
    r["badges"] = "" if r["badges"] is None else r["badges"]
KIND_RANK = {"gift_companion": 0, "gift_egg": 0, "trade": 1, "gift_item": 2, "gift_decoration": 3, "coins": 3, "item_ball": 4,
             "hidden_item": 5, "berry_tree": 6, "shop": 7, "decoration_shop": 8}
rows.sort(key=lambda r: (int(r["badges"]) if r["badges"] != "" else 99, ev_seq.get(r["story_event"], 0), r["map_id"], KIND_RANK.get(r["kind"], 9),
                         r["script"], r.get("_after", 0), r["source"]))
seen = defaultdict(int)
for r in rows:
    if not r["obtain_id"]:
        base = f"obtain:{r['kind']}:{(r['map_id'] or 'map:?')[4:]}:{(r['what'].split(':', 1)[-1]).lower()}"
        seen[base] += 1
        r["obtain_id"] = base if seen[base] == 1 else f"{base}:{seen[base]}"
cols = ["obtain_id", "story_order", "badges", "story_event", "planet", "map_id", "sw_map", "kind", "what", "sw_name", "quantity",
        "npc_id", "character_id", "character_sw_name", "started_by", "flag", "checks", "script", "source", "notes"]
write(WIKI / "database" / "obtain.csv", [{k: r[k] for k in cols} for r in rows], cols)

gives = defaultdict(list)
for r in rows:
    if r["npc_id"]:
        gives[r["npc_id"]].append(r["obtain_id"])
for n in npcs:
    p = area(n["map_id"])
    n["sw_map"], n["planet"] = p.get("sw_map_title", ""), p.get("planet", "")
    n["gives"] = "|".join(gives.get(n["npc_id"], []))
write(WIKI / "database" / "npcs.csv", npcs, ["npc_id", "map_id", "sw_map", "planet", "local_id", "kind", "graphics_id", "script",
                                             "flag", "x", "y", "character_id", "sw_name", "gives", "notes"])

# checks
missing = [r for r in rows if r["kind"] in ("gift_item", "gift_companion", "gift_egg", "gift_decoration", "trade") and not r["npc_id"]]
print(f"{len(missing)} gifts with no NPC found (a sign, a step trigger or a shared script; add the script to mapping/npcs.csv)")
chars = {r["emerald_id"] for r in read(WIKI / "mapping" / "characters.csv")}
for k, h in npc_hand.items():
    if h["character_id"] and h["character_id"] not in chars:
        print("  PROBLEM: mapping/npcs.csv names a character that is not in mapping/characters.csv:", k, h["character_id"])
bad = [k for k in npc_hand if k not in npc_by_id]
for k in bad:
    print("  PROBLEM: mapping/npcs.csv names an NPC that is not in the game:", k)
