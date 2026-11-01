"""Batch 1, second pass: each character hand-drawn with its own silhouette (owner: v1 looked too
alike and blocky). Run from the tool folder: python batches/batch1.py"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from walker_sprite.template import write_spec

P = "graphics/object_events/pics/people/"
SKIN = {".": 0, "K": 15, "S": 1, "s": 2, "t": 3}

def legs_steps(base_down, base_up, base_left, down_a, down_b, left_a, left_b, py=29):
    return {"down_a": (base_down, py, down_a), "down_b": (base_down, py, down_b),
            "up_a": (base_up, py, down_a), "up_b": (base_up, py, down_b),
            "left_a": (base_left, py, left_a), "left_b": (base_left, py, left_b)}

black_belt = dict(
    name="black_belt", gi="BlackBelt", pal="npc_3", replaces=P + "black_belt.png",
    desc="Teras Kasi brawler in a training wrap (replaces the Emerald BLACK BELT walker).",
    note="NPC_3. Broad bare-armed brawler: shaved head with a topknot, green wrap top, white forearm wraps, wide stance.",
    legend={**SKIN, "o": 4, "H": 12, "D": 13, "A": 8, "a": 9, "c": 10, "P": 12, "p": 13, "E": 14, "w": 6},
    frames={
        "down": [
            "......KHDK......", ".....KKDDKK.....", "....KSSSSSStK...", "...KSSSSSSSStK..",
            "...KStKKSKKSsK..", "...KSSKSSSKSsK..", "...KsSKSSSKStK..", "...KtsSStSSstK..",
            "....KtsoootK....", ".....KtttttK....", "..KKKKttttKKKK..", ".KSSKAAAAAaKSSK.",
            "KSSsKAEAAAaKSstK", "KSssKAAEAAaKsstK", "KtssKcAAEAcKsttK", "KEEEKPPPPPpKEEEK",
            "KEwEKPPPPPpKEwEK", "KSStKPPKKPpKSStK", ".KKKKPPpKPPpKKK.", "....KPPpKPPpK...",
            "...KDDDK.KDDDK..", "................"],
        "up": [
            "......KHDK......", ".....KKDDKK.....", "....KSSSSSStK...", "...KSSSSSSSStK..",
            "...KSSSSSSSstK..", "...KSSSSSSSstK..", "...KsSSSSSSstK..", "...KtsSSSSsstK..",
            "....KtssssttK...", ".....KtttttK....", "..KKKKttttKKKK..", ".KSSKAAAAAaKSSK.",
            "KSSsKAAAAEaKSstK", "KSssKAAAEAaKsstK", "KtssKcAEAAcKsttK", "KEEEKPPPPPpKEEEK",
            "KEwEKPPPPPpKEwEK", "KSStKPPKKPpKSStK", ".KKKKPPpKPPpKKK.", "....KPPpKPPpK...",
            "...KDDDK.KDDDK..", "................"],
        "left": [
            ".......KHDK.....", "......KKDDKK....", ".....KSSSSSSK...", "....KSSSSSSSStK.",
            "...KSKKSSSSSStK.", "...KSKSSSSSSstK.", "..KSSKSSSSSSstK.", "...KSSSSSSSttK..",
            "...KooSSSSttK...", "....KttttttK....", ".....KKttKKK....", "....KAAAAAAaK...",
            "....KASSsAAaK...", "....KASssAAaK...", "....KcSstAccK...", "....KPEEEPPpK...",
            "....KPEwEPPpK...", "....KPSStPPpK...", "....KPPpKPPpK...", "...KPPpK.KPPpK..",
            "..KDDDK...KDDDK.", "................"],
    },
    steps=legs_steps("down", "up", "left",
        [".KKKKPPpKPPpKKK.", "....KPPpKKDDDK..", "...KDDDK........"],
        [".KKKKPPpKPPpKKK.", "...KDDDKKPPpK...", ".........KDDDK.."],
        ["...KPPpK.KPPpK..", "..KPPpK...KPPpK.", ".KDDDK.....KDDDK"],
        ["....KPPpKPPpK...", ".....KPPPpK.....", ".....KDDDDK....."]),
)

boy_1 = dict(
    name="boy_1", gi="Boy1", pal="npc_3", replaces=P + "boy_1.png",
    desc="Moisture-farm kid in a desert tunic and goggles (replaces the Emerald BOY 1 walker).",
    note="NPC_3. Small kid: spiky auburn hair, goggles on the brow, off-white tunic flaring to a hem, belt, boots.",
    legend={**SKIN, "h": 11, "b": 12, "d": 13, "E": 14, "v": 7, "W": 5, "w": 6, "c": 12, "o": 13},
    frames={
        "down": [
            ".....K.KK.K.....", "....KhKhhKhK....", "...KhhbhhbbhbK..", "..KhbbbbbbbbbdK.",
            "..KvEEvvvvEEvdK.", "..KbvvSSSSvvbdK.", "..KbSKSSSSKSbdK.", "..KdSKSSSSKStdK.",
            "...KtsSSSSstK...", "....KKttttKK....", "...KWWWKKWWwK...", "..KWWwWWWWWwwK..",
            "..KWKWWWWWWKwK..", "..KWKccccccKwK..", "..KSKWWWWWwKSK..", ".KWWWWWWWWWwwvK.",
            ".KvvvvvvvvvvvvK.", "...KooK..KooK...", "...KKKK..KKKK...", "................"],
        "up": [
            ".....K.KK.K.....", "....KhKhhKhK....", "...KhhbhhbbhbK..", "..KhbbbbbbbbbdK.",
            "..KvvvvvvvvvvdK.", "..KbbbbbbbbbbdK.", "..KbhbbbbbbbbdK.", "..KdbbbbbbbbddK.",
            "...KddbbbbddK...", "....KKttttKK....", "...KWWWWWWWwK...", "..KWWWWWWWWwwK..",
            "..KWKWWWWWWKwK..", "..KWKccccccKwK..", "..KSKWWWWWwKSK..", ".KWWWWWWWWWwwvK.",
            ".KvvvvvvvvvvvvK.", "...KooK..KooK...", "...KKKK..KKKK...", "................"],
        "left": [
            "......K.KK......", ".....KhKhhK.....", "....KhhbhhbbK...", "...KhbbbbbbbbdK.",
            "..KEEvvvvbbbbdK.", "..KvvSSSbbbbbdK.", "..KSKSSSSbhbdK..", ".KSSKSSStbbbdK..",
            "..KtsSSttbddK...", "...KKKttKKKK....", "....KWWWWwK.....", "....KWWWWwK.....",
            "....KWKWWwK.....", "....KcKccvK.....", "....KSSKWwK.....", "...KWWWWWWwvK...",
            "...KvvvvvvvvK...", "....KooKooK.....", "....KKKKKKK.....", "................"],
    },
    steps=legs_steps("down", "up", "left",
        [".KvvvvvvvvvvvvK.", "...KooK..KKKK...", "...KKKK........."],
        [".KvvvvvvvvvvvvK.", "...KKKK..KooK...", ".........KKKK..."],
        ["...KvvvvvvvvK...", "..KooK..KooK....", "..KKKK..KKKK...."],
        ["...KvvvvvvvvK...", ".....KooK.......", ".....KKKK......."]),
)

boy_2 = dict(
    name="boy_2", gi="Boy2", pal="npc_1", replaces=P + "boy_2.png",
    desc="Spaceport kid in a padded flight jacket (replaces the Emerald BOY 2 walker).",
    note="NPC_1. Puffy quilted olive flight jacket with a white fur collar (wide torso), swept hair with a cowlick, blue trousers.",
    legend={**SKIN, "h": 6, "b": 7, "d": 4, "E": 14, "A": 11, "a": 12, "c": 13, "P": 9, "p": 10, "o": 10},
    frames={
        "down": [
            "........KK......", "....KKKKhK......", "...KhhhhhbbKK...", "..KhhbbbbbbbbK..",
            "..KbhbbbbbbbdK..", "..KbbSbSbbSbdK..", "..KbSSSSSSSSdK..", "..KdSKSSSSKSdK..",
            "..KdSKsSSsKtdK..", "...KtssSSsstK...", "...KEEKttKEEK...", ".KAAAEEEEEEAaaK.",
            "KAAKAAAAAAAaKacK", "KAaKaaaaaaaaKccK", "KAAKAAAAAAAaKacK", ".KSKccccccccKSK.",
            "...KPPpKKPPpK...", "...KooK..KooK...", "...KKKK..KKKK...", "................"],
        "up": [
            "........KK......", "....KKKKhK......", "...KhhhhhbbKK...", "..KhhbbbbbbbbK..",
            "..KbhbbbbbbbdK..", "..KbbbbbbbbbdK..", "..KbhbbbbbbbdK..", "..KdbbbbbbbddK..",
            "..KddbbbbbdddK..", "...KddddddddK...", "...KEEEEEEEEK...", ".KAAAAAAAAAaaaK.",
            "KAAKAAAAAAAaKacK", "KAaKaaaaaaaaKccK", "KAAKAAAAAAAaKacK", ".KSKccccccccKSK.",
            "...KPPpKKPPpK...", "...KooK..KooK...", "...KKKK..KKKK...", "................"],
        "left": [
            ".........KK.....", ".....KKKKhK.....", "....KhhhhhbbK...", "...KhhbbbbbbbK..",
            "..KbbbbbbbbbbdK.", "..KbSSbbbbbbbdK.", "..KSSSSSSbbbbdK.", "..KSKSSSSbhbdK..",
            ".KSSKSSStbbdK...", "..KtsSStKddK....", "....KEEKEEK.....", "...KAAAAAAaK....",
            "...KAKAAAAaK....", "...KAKaaaacK....", "...KAKAAAAaK....", "...KSKccccK.....",
            "....KPPpPpK.....", "....KooKooK.....", "....KKKKKKK.....", "................"],
    },
    steps=legs_steps("down", "up", "left",
        ["...KPpK..KooK...", "...KooK..KKKK...", "...KKKK........."],
        ["...KooK..KPpK...", "...KKKK..KooK...", ".........KKKK..."],
        ["....KPpKPpK.....", "...KooK.KooK....", "...KKKK.KKKK...."],
        ["....KPpPpK......", "....KoooK.......", "....KKKKK......."]),
)

boy_3 = dict(
    name="boy_3", gi="Boy3", pal="npc_4", replaces=P + "boy_3.png",
    desc="Market-town kid with a toy blaster (replaces the Emerald BOY 3 walker).",
    note="NPC_4. Smallest kid: pink cap with a dark brim, grey vest over a white shirt, shorts, toy blaster (pink muzzle) in hand.",
    legend={**SKIN, "p": 8, "r": 9, "R": 10, "b": 6, "d": 7, "E": 14, "e": 11, "g": 12, "G": 13, "o": 13},
    frames={
        "down": [
            ".....KKKKKK.....", "....KpprrrrK....", "...KpprrrrrrK...", "...KrrrrrrrRK...",
            "..KRRRRRRRRRRK..", "..KbSSSSSSSSbK..", "..KbSKSSSSKSbK..", "..KdSKSSSSKSdK..",
            "...KtsStSSstK...", "....KKttttKK....", "...KgEEEEEEgK...", "..KEKgEEEEgKeK..",
            "..KeKgEEEEgKeK..", "..KSKGeeeeGKSK..", "...KbbbKKbdKgK..", "...KSSK..KSSKpK.",
            "...KooK..KooK...", "...KKKK..KKKK...", "................"],
        "up": [
            ".....KKKKKK.....", "....KrrrrrrK....", "...KrrrrrrrrK...", "...KrrrKKrrRK...",
            "..KbbbbbbbbbbK..", "..KbbbbbbbbbbK..", "..KbbbbbbbbbdK..", "..KdbbbbbbbddK..",
            "...KddbbbbddK...", "....KKttttKK....", "...KgggggggGK...", "..KEKgggggGKeK..",
            "..KeKgggggGKeK..", "..KSKGGGGGGKSK..", "...KbbbKKbdK....", "...KSSK..KSSK...",
            "...KooK..KooK...", "...KKKK..KKKK...", "................"],
        "left": [
            "......KKKKK.....", ".....KpprrrK....", "....KpprrrrrK...", "....KrrrrrrRK...",
            ".KRRRRRbbbbbK...", "..KSSSSbbbbbK...", "..KSKSSSbbbbK...", ".KSSKSSSbbbdK...",
            "..KtsSStKddK....", "....KKttKKK.....", ".KKKKKEEgK......", ".KpggggSKgK.....",
            ".KKKKGKSKgK.....", ".....KeegK......", ".....KbbdK......", ".....KSSK.......",
            "....KoooK.......", "....KKKKK.......", "................"],
    },
    steps=legs_steps("down", "up", "left",
        ["...KSSK..KooK...", "...KooK..KKKK...", "...KKKK........."],
        ["...KooK..KSSK...", "...KKKK..KooK...", ".........KKKK..."],
        ["....KSSKSSK.....", "...KooK.KooK....", "...KKKK.KKKK...."],
        [".....KSSK.......", "....KoooK.......", "....KKKKK......."]),
)

bug_catcher = dict(
    name="bug_catcher", gi="BugCatcher", pal="npc_1", replaces=P + "bug_catcher.png",
    desc="Kid with a bug net and specimen jar (replaces the Emerald BUG CATCHER walker).",
    note="NPC_1. Wide straw-hat brim, net raised on a pole above the hat, specimen jar in the other hand, blue shirt, navy shorts.",
    legend={**SKIN, "h": 11, "b": 12, "d": 13, "H": 7, "A": 8, "a": 9, "c": 10, "n": 10, "N": 13, "o": 13, "E": 14, "e": 8},
    frames={
        "down": [
            ".............KKK", "............KEeK", "............KeEK", ".....KKKKK...KbK",
            "....KhhhbbK..KbK", "...KhhbbbbbK.KbK", "KhhhhhbbbbbbbbdK", ".KKKKKKKKKKKKKbK",
            "..KHSSSSSSSHKKbK", "..KSKSSSSKSSKKbK", "..KsKSSSSKStKKbK", "...KtsSSSstK.KbK",
            "....KKttttKK.KbK", "...KAAAAAAaK.KbK", "..KAKAAAAAKaKKbK", ".KKAKAAAAaKcKSSK",
            ".KaEKAAAAaKcKKbK", ".KEaKnnnnNK.KKK.", ".KKKSSK.KSSK....", "...KooK.KooK....",
            "...KKKK.KKKK....", "................"],
        "up": [
            ".............KKK", "............KEeK", "............KeEK", ".....KKKKK...KbK",
            "....KhhhbbK..KbK", "...KhhbbbbbK.KbK", "KhhhhhbbbbbbbbdK", ".KKKKKKKKKKKKKbK",
            "..KHHHHHHHHHKKbK", "..KHHHHHHHHHKKbK", "..KHHHHHHHHHKKbK", "...KHHHHHHHK.KbK",
            "....KKttttKK.KbK", "...KAAAAAAaK.KbK", "..KAKAAAAAKaKKbK", "..KAKAAAAaKcKSSK",
            "..KSKAAAAaKcKKbK", "..KKKnnnnNK.KKK.", "...KSSK.KSSK....", "...KooK.KooK....",
            "...KKKK.KKKK....", "................"],
        "left": [
            "KKK.............", "KEeK............", "KeEK............", "KbK...KKKKK.....",
            "KbK..KhhhbbK....", "KbK.KhhbbbbbK...", "KhhhhhbbbbbbbbdK", "KbKKKKKKKKKKKKK.",
            "KbK.KSSSHHHHHK..", "KbKKSKSSHHHHHK..", "KbKSSKSStHHHHK..", "KbK.KtsSSHHHK...",
            "KbK..KKttKKK....", "KbK...KAAaK.....", "KSSKKKAAAaK.....", "KKK...KAKaK.....",
            "......KAAcK.....", "......KnnNK.....", "......KSSK......", "......KooK......",
            "......KKKK......", "................"],
    },
    steps=legs_steps("down", "up", "left",
        ["...KSSK.KooK....", "...KooK.KKKK....", "...KKKK........."],
        ["...KooK.KSSK....", "...KKKK.KooK....", "........KKKK...."],
        ["......KSSKSK....", ".....KooKKooK...", ".....KKKKKKKK..."],
        ["......KSSK......", "......KooK......", "......KKKK......"]),
)

for c in (black_belt, boy_1, boy_2, boy_3, bug_catcher):
    write_spec(c)
print("ok")
