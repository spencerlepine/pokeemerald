#!/usr/bin/env bash
# Capture "after" screenshots of the themed UI into after/v2/<name>.png, same names as reference/v1.
#   ./capture.sh boot            restart mGBA on the current ROM with the all-unlocked save, to the overworld
#   ./capture.sh <screen>...     run one or more named sequences below (each starts from the overworld, idle)
# Needs tools/play-tester (scripts/live.sh, Xvfb, mGBA). The save is play-tester/savestates/ui-audit.sav.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
PT="$HERE/../play-tester"; L="$PT/scripts/live.sh"; OUT="$HERE/after/v2"; mkdir -p "$OUT"
k()    { for key in "$@"; do "$L" tap "$key" 6 >/dev/null; sleep 0.15; done; }   # tap keys in order
w()    { sleep "${1:-0.5}"; }
shot() { "$L" shot "$OUT/$1.png" >/dev/null; echo "shot $1"; }
lua()  { "$L" lua "$1" >/dev/null; }
tp()   { "$L" luafile "$PT/lua/emerald.lua" >/dev/null; lua "E.teleport($1,$2,$3,$4); return 1"; sleep 3; }
menu0() { lua 'emu:write8(0x0203760e, 0); return 1'; }   # start menu cursor back to the top (sStartMenuCursorPos)
town()  { tp 0 0 17 18; nopopup; k DOWN; w 0.5; }          # Petalburg City, outdoors, popup hidden
nopopup() { lua 'emu:write8(0x020375fc, emu:read8(0x020375fc) | 1); return 1'; }   # hide the map-name popup

boot() {
  "$L" down >/dev/null 2>&1 || true
  cp "$PT/savestates/ui-audit.sav" "$PT/../../game/pokeemerald.sav"
  "$L" up >/dev/null; sleep 6; k A; sleep 3; k A; sleep 3
}

# ---------- family 1: text windows, start menu, options, save ----------
s00() { python3 "$HERE/frames_sheet.py" "$OUT/00_text_window_frames_1-20.png"; echo "shot 00_text_window_frames_1-20"; }
s01() { town; menu0; k START; w; shot 01_start_menu; k B; w; }
s05() { tp 26 31 4 8; k UP A; w 1.5; shot 05_overworld_dialogue_npc; k B B B B B B; w; }
s06() { tp 0 0 17 17; nopopup; k UP; w 0.3; k A; w 1.5; shot 06_sign_box; k B B; w; }
s42() { menu0; k START DOWN DOWN DOWN DOWN DOWN DOWN A; w 1.5; shot 42_options;
        k DOWN DOWN DOWN DOWN DOWN; w 0.5; shot 42b_options_frame; k B; w 1; k B; w; }
s43() { town; menu0; k START DOWN DOWN DOWN DOWN DOWN A; w 1.5; shot 43_save_prompt; k B; w 0.5; k B B; w; }

# ---------- family 2: party menu and summary ----------
party() { town; menu0; k START DOWN A; w 1.5; }
s10() { party; shot 10_party_menu; k A; w 0.7; shot 11_party_action;
        k A; w 1.5; shot 12_summary_info; k RIGHT; w 0.8; shot 13_summary_p2; k RIGHT; w 0.8; shot 14_summary_p3;
        k RIGHT; w 0.8; shot 15_summary_p4; k LEFT; w 0.8; k DOWN; w 1; k A; w 0.8; shot 16_summary_move_detail;
        k B; w 0.5; k B; w 1.5; k B; w 0.3; k B; w 1.5; s17; }
s17() { party; k A DOWN A; w 0.8; k DOWN; w 0.5; shot 17_party_switch; k B B; w 0.5; k B; w 1.5; k B; w; }

# ---------- family 3: bag, Pokéblock case ----------
bag() {   # bag() POCKET [ROW]: open the bag on a pocket with the cursor on ROW
  town; lua "emu:write8(0x0203ce59, $1); for i=0,4 do emu:write16(0x0203ce5c+i*2,0); emu:write16(0x0203ce66+i*2,0) end; emu:write8(0x0203760e, 0); return 1"
  k START; w 0.3; k DOWN DOWN; w 0.3; k A; w 2.5; for ((i=0;i<${2:-0};i++)); do k DOWN; done; w 0.3; }
unbag() { k B B; w 2; k B; w 0.5; }
s30() { bag 0; shot 30_bag_items; k A; w 0.7; shot 35_bag_item_menu; k B; w 0.3;
        for i in 1 2 3 4 5; do k DOWN; done; w 0.3; k A; w 0.7; shot 36_bag_mail_menu; k B; w 0.3; unbag
        s31; }
s31() { bag 1; shot 31_bag_balls; unbag; bag 2; shot 32_bag_tmhm; unbag; bag 3; shot 33_bag_berries; unbag
        bag 4; shot 34_bag_keyitems; unbag; }
s61() { bag 4 9; k A; w 0.7; k A; w 3; shot 61_pokeblock_case; k A; w 0.7; shot 62_pokeblock_menu;
        k A; w 3; shot 63_pokeblock_party; k A; w 1; k A; w 4; shot 64_pokeblock_feed; w 3; shot 65_pokeblock_feed2;
        w 4; shot 66_pokeblock_condition_after; k B B B; w 2; k B B B; w 2; k B B; w 1; }

# ---------- family 4: Pokédex ----------
s20() { town; menu0; k START; w 0.4; k A; w 3; shot 20_dex_list; k A; w 2.5; shot 21_dex_entry;
        k A; w 3; shot 22_dex_area; k B; w 2.5; k RIGHT A; w 3; shot 23_dex_cry; k B; w 2.5;
        k RIGHT A; w 3; shot 24_dex_size; k B; w 2.5; k B; w 2.5; k START; w 1; shot 25_dex_start_menu; k B; w 1; k SELECT; w 2.5; shot 26_dex_search;
        k DOWN A; w 1; shot 27_dex_search_options; k B; w 0.7; k B; w 2; k B; w 2.5; k B; w 1; }

# ---------- family 5: StarNAV ----------
nav() { town; lua 'emu:write8(0x0203760e, 3); return 1'; k START; w 0.4; k A; w 4; }
unnav() { for i in 1 2 3 4 5 6; do k B; w 0.6; done; w 2; k B; w 1; }
s50() { nav; shot 50_starnav_main; k A; w 3; shot 51_starnav_map; k A; w 2; shot 52_starnav_map_zoom; unnav; s54; }
s54() { nav; k DOWN A; w 3; shot 54_starnav_condition_menu; k A; w 4; shot 55_starnav_condition_party; k B; w 3;
        k DOWN A; w 3; shot 55b_starnav_condition_search_menu; k A; w 4; shot 55c_starnav_condition_search; unnav; }
s56() { nav; k DOWN DOWN A; w 4; shot 56_starnav_matchcall; k A; w 1.5; shot 57_starnav_matchcall_menu;
        k A; w 1.5; shot 57b_starnav_matchcall_calling; w 3; shot 57c_starnav_matchcall_talk; unnav; }
s58() { nav; k DOWN DOWN DOWN A; w 4; shot 58_starnav_ribbons_list; k A; w 4; shot 59_starnav_ribbons_mon;
        k A; w 1.5; shot 59b_starnav_ribbon_detail; unnav; }

# ---------- family 6: PC ----------
pc() { tp 2 2 10 2; k UP; w 0.5; k A; w 2; shot 80_pc_boot_msg; k A; w 1.5; }
s80() { pc; shot 81_pc_menu; k A; w 2; k A; w 2; k A; w 2; shot 82_pc_storage_menu; k DOWN DOWN A; w 5; shot 83_pc_box_move;
        k A; w 1; shot 84_pc_box_mon_menu; k B; w 1; k UP; w 0.5; k A; w 1; shot 85_pc_box_options; k B; w 1;
        k UP; w 0.5; k A; w 2; shot 87_pc_party_tray; k B; w 1.5; k B; w 1; k B; w 3; k B; w 1.5; k B; w 1; k B; w 1; }
s89() { pc; k A; w 2; k A; w 2; k A; w 2; k DOWN DOWN DOWN A; w 5; shot 89_pc_move_items; k B; w 1; k B; w 3; k B; w 1; k B; w 1; }
s90() { pc; k DOWN A; w 2; k A; w 2; shot 90_pc_items_menu; k A; w 2; shot 91_pc_items_withdraw; k A; w 1; shot 91b_pc_items_quantity;
        k B; w 1; k B; w 1; k B; w 1; k B; w 1; k B; w 1; k B; w 1; }

# ---------- family 7: battle + naming ----------
cb2()  { "$L" lua 'return string.format("%08x", emu:read32(0x030022c4))' | grep -o '"result": "[0-9a-f]*"' | cut -d'"' -f4; }
wild() { tp 0 17 9 4; nopopup; for i in $(seq 1 60); do "$L" tap UP 16 >/dev/null; "$L" tap DOWN 16 >/dev/null;
         [ "$(cb2)" != "08085d15" ] && return 0; done; echo "no encounter" >&2; return 1; }
bpos() { lua "emu:write8(0x0203ce59, 1); for i=0,4 do emu:write16(0x0203ce5c+i*2,0); emu:write16(0x0203ce66+i*2,0) end; return 1"; }
sb01() { wild; w 3; shot b01_battle_intro; k A; w 4; shot b02_sendout; shot b03_action_menu; k A; w 1; shot b04_move_menu; k B; w 1;
         k DOWN; w 0.3; k A; w 2.5; shot b06_battle_party; k A; w 1; shot b07_battle_party_action; k B; w 1; k B; w 3;
         k UP RIGHT; w 0.3; bpos; k A; w 3; k DOWN DOWN DOWN; w 0.5; shot b08_battle_bag; k A; w 1; shot b09_battle_bag_use;
         k A; w 9; shot b10_caught; k A; w 2; shot b11_nickname_prompt; k A; w 4; shot b12_naming_screen;
         k SELECT; w 1.5; shot b13_naming_lower; k SELECT; w 1.5; shot b14_naming_symbols; k START; w 1; k A; w 4; }
sb16() { wild; w 3; k A; w 4; k A; w 1; k A; w 3.5; shot b17_fainted; k A; w 3; shot b20_exp_gain;
         for i in 1 2 3 4 5 6; do k B; w 1; done; w 2; }

for s in "$@"; do if declare -F "$s" >/dev/null; then "$s"; else "s$s"; fi; done
