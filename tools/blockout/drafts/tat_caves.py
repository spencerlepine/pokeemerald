import os; exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "common.py")).read())
CAVES = [
 ("beggars-canyon", "Narrow canyon tunnel between Route 116 and Anchorhead that Fixer is digging by hand; cartel thugs hold Chewie here until the player rescues him."),
 ("krayt-graveyard", "Tunnels under the bones of dead krayt dragons, between the Dune Sea and Route 112. Fossil companions."),
 ("tusken-ruins", "Ruined Tusken shrine in the Dune Sea; home of ROCKWARDEN. Braille-style puzzle becomes Tusken glyphs."),
 ("sandcrawler-1f", "Wrecked Jawa sandcrawler, lowest deck: scrap mazes that need Rock Smash."),
 ("sandcrawler-2f", "Sandcrawler, second deck: holes in the floor drop back to 1F."),
 ("sandcrawler-3f", "Sandcrawler, third deck: more cracked floor."),
 ("sandcrawler-4f", "Sandcrawler, top deck: the two fossils; taking one makes the crawler collapse."),
 ("espa-generator-entrance", "Hatch and stairwell down from Mos Espa into the old Espa generator."),
 ("espa-generator-inside", "The old power generator under Mos Espa: switch-floor puzzle, Watto's errand to shut it down."),
 ("terra-cave-entrance", "Hidden cave that only opens in drought (vanilla Terra Cave)."),
 ("terra-cave-end", "Terra Cave's inner chamber: a titan's resting place."),
]
for a, s in CAVES:
    retheme(a, s)
