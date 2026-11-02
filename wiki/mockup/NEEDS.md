# What every area needs, in words

Owner's rule (2026-11-02): write down what an area needs before drawing it. This is that list, planet by planet,
for all 528 areas in [`wiki/world/`](../world/README.md). It says what each place is made of, what bounds it and
what is unique there. No art decisions: shapes come second, one category at a time, reviewed before the next.

How to read an entry: **area** (kind, size in cells): what is there · what borders it · what is unique.
"Have" means today's greybox tools cover it (buildings, kit categories, relief terrain, landforms).
"Need" names the missing thing. The summary of missing tools is at the end.

Facts come from each area's story text and grid. Reference art and planet facts:
[starwars-db wiki](https://github.com/spencerlepine/starwars-db/tree/main/wiki).

---

## Tatooine (20 overworld, 12 cave rooms, 98 interiors)

Desert: sand, sandstone mesas and canyons, no trees ever. Borders are cliffs, rock spires and dune ridges.
Round Tatooine shapes are allowed here (domes, sunken homesteads) because that is the planet's look.

### Towns

- **mos-pelgo** (town, 20x20): the starting moisture farm. Player's homestead dome, Korr family home, Prof. Korr's
  lab with a dish, the family freighter on a pad, vaporators · bordered by dune ridges and rock · unique: the
  freighter is a landed ship, wedge-shaped, needs the hull primitive. Have: domes, lab, pad, vaporator.
- **tosche-station** (town, 30x26): crossroads trading post. Power station with stacks and tanks, first bacta
  center and supply depot, a few homes, power converters stacked outside · bordered by rock and scrub · have all.
- **anchorhead** (town, 34x26): quiet farm town. Farm co-op (also the Showcase hall), homes, Luke's friends'
  skyhopper parked · bordered by farmland and low berms · need: the skyhopper (small wedge craft with a fin).
- **mos-entha** (town, 38x32): farm town with the first gym (Normal, Doran) and the Lars homestead on the west.
  Market square at the crossroads with stalls · bordered by farm plots · need: market stalls with awnings,
  the homestead's sunken courtyard (sunken kit now covers it).
- **bestine** (town, 48x62): capital, one long main street. House Organa office tower (tall), the academy
  (winged), Biggs's Rock gym, market plaza, many homes · bordered by cliffs north and the Dune Sea road south ·
  unique: a real skyline, two or three tall towers of different heights, the only "city" on Tatooine.
- **mos-eisley** (town, 50x50): spaceport. Cantina (two domes), Spacer Museum, Ric Olie's shipyard, two
  docking bays, bazaar stalls, parked landspeeders, crates · bordered by rock · need: stalls, landspeeders
  (low wedge with a canopy), a freighter sitting in a docking bay.
- **mos-espa** (town, 56x36): podracing city. Watto's junk shop with the Electric gym, Wald's speeder-bike
  rental, the podrace grandstand on the east side, a hatch down to the generator · bordered by rock and the
  grandstand · need: grandstand (tiered seating facing the course), speeder bikes, podracer engines on display,
  junk piles.

### Routes and landmarks

- **route-101** (route, 20x20): short track, scrub patches, a ledge · rock spires · have.
- **route-102** (route, 50x20): scrubland, dry oasis pond with a rim, first trainers · rock · have.
- **route-103** (route, 80x22): road along a salt lake (flat white water with a crust edge), the podrace course
  opens east, Altering Cave mouth · need: salt flat as a water kind, a cave mouth in a cliff.
- **route-104** (route, 40x80): coast road with a real sea on the west, Han's hangar hut on the shore where the
  Falcon leaves · cliffs east · need: sea with a beach edge, a landed freighter beside a hut.
- **route-110** (route, 40x100): the Boonta Eve course: a raised speeder road on pylons running the whole map
  over a canyon, side paths underneath, Garindan's Trick House · need: the raised-road layer (walk under it),
  course markers, lap banners, a long elevated structure with supports.
- **route-111** (route, 40x140): the Dune Sea: open sand with dune ridges, sandstorm zone, Krayt Graveyard
  tunnel mouths, Tusken Ruins entrance, the wandering Sandcrawler, Pit of Carkoon, sail barge wreck ·
  need: dunes as soft berms, the sandcrawler (a huge tracked wedge, true scale, partly seen), the sarlacc pit
  (sunken, with a mouth), the barge wreck (tilted hull), krayt bones (rib arcs).
- **route-112** (route, 40x60): canyon road, the shuttle station to Mustafar (a landing pad with a terminal
  building and a parked shuttle) · cliffs both sides · need: shuttle (folded wings, wedge).
- **route-115** (route, 40x80): coastal cliffs, a beach of wrecked pod parts, Starfall Cavern mouth, long
  grass · need: beach, scattered wreck parts (small tilted boxes and rings).
- **route-116** (route, 100x20): east road to Beggar's Canyon, Fixer's tunnel mouth with digging gear, the
  tunnellers' rest house · need: a tunnel mouth under a cliff with a timber frame, a digging rig.
- **route-117** (route, 60x20): farm road, the Creature Nursery ranch with pens and a dewback trough · need:
  fences and pens (low rails), trough. Fences are a general need for every farm.
- **jundland-wastes** (route, 48x44): canyon badlands, Tusken territory, a side path climbing to Ben's hut ·
  need: multi-level canyon (relief already gives two levels), Tusken camp (tents from hides on poles, banthas).
- **bens-hut** (landmark, 26x20): a hermit's hut on a ridge over the wastes · have (dome-porch) · unique:
  nothing else nearby, so the border is all rock and sky.
- **jabbas-palace** (landmark, 44x34): the palace at the far edge of the Dune Sea: a huge rounded fortress
  with a gate guarded by thugs, outer walls, the barge dock · unique landmark set piece: the palace is bigger
  than the map and partly seen, with its gate as the only way in. Need: a one-off model.

### Caves and dungeons

- **altering-cave** (32x24): small sandstone cave · need: cave mode (walls on all sides, a dark margin).
- **beggars-canyon** (36x24): a narrow open canyon rather than a cave: high walls, a dug tunnel · relief covers
  the walls; need: the hand-dug tunnel mouth and cartel camp.
- **espa-generator-entrance** and **-inside** (9x9, 41x41): a hatch and stairwell down, then a machine hall:
  switch-floor puzzle, generator cores, cable runs · need: an Imperial-style machine interior (metal floor
  plates, consoles, cores from the doorless kit, cable trunks).
- **krayt-graveyard** (139x23): long tunnels under krayt bones, fossils · need: cave mode plus huge rib arcs
  crossing the tunnel, a skull.
- **sandcrawler-1f to 4f** (21x17 x3, 13x10): inside a wrecked sandcrawler, four decks, scrap mazes, holes in
  the floor, the top deck collapses · need: rusted metal interior, scrap piles, floor holes (sunken kit), and a
  tilted feel.
- **terra-cave-entrance** and **-end** (20x20, 27x30): a cave that opens only in drought, a titan's chamber
  with a pool · need: cave mode, a large pool, a raised dais.
- **tusken-ruins** (17x33): a ruined shrine, glyph puzzle, ROCKWARDEN · need: ruined walls (broken boxes),
  glyph wall, a sealed stone door.

### Interiors (98)

Grouped by room type. All need the room kit (walls, doors, floors) first.
- Homes, about 30: sandstone walls, round-cornered rooms, low beds, a cooking unit, a table. Luke's homestead
  rooms, Owen Lars's, Camie's, the Korr home, the player's home with upstairs.
- Bacta centers and supply depots (one per town): a counter, bacta tanks, shelves, a StarNAV-style terminal.
- Gyms: Doran's Normal gym (plain hall), Biggs's Rock gym (boulders inside), Watto's Electric gym in a junk
  shop (junk piles, cages). Each is a different room.
- Cantina: bar, booths, band stage, the fan club room upstairs.
- Spacer Museum: display stands, a podracer on display, a ship model.
- Shipyard, docking bays and hangars (6): open hangar floors with a parked freighter or the Falcon, fuel
  hoses, crates, a StarNAV console in the ship room.
- Prof. Korr's lab: benches, a scanner, companion pods.
- Academy, House Organa office tower (several floors), Trick House, podrace grandstand interior, Tosche power
  room (generator), Jabba's throne room (dais, rancor pit hatch, steps), Jabba's barge dock, Ben's hut.
- Caves listed above also count as rooms.

---

## Kashyyyk (6 overworld, 1 landmark, 19 cave and wreck rooms, 11 interiors)

Lagoon coast under giant wroshyr trees. Water everywhere. Trees are the border, but as trunks: the canopy
is off the top of the map. Wookiee buildings are wood on stilts and platforms in the trees.

- **kachirho** (town, 46x38): lagoon city at the foot of the trees. The Falcon lands on the beach, Tarfful's
  gym and the great hall sit up on tree platforms reached by ladders, Wookiee huts on stilts, a hangar bay ·
  unique: two levels, beach below and platforms above · need: the raised-walkway layer, giant trunks that run
  off the top, ladders between levels, a beached freighter.
- **rwookrrorro** (landmark, 36x28): a whole village on one high platform level in the treetops, rope bridges
  and plank decks, hunters' lodge, bowcaster maker · need: platforms over a void (you see the forest floor far
  below), rope bridges, decks ringed around trunks.
- **route-105** (route, 40x80): open lagoon with wroshyr islets, the Ice Grotto islet · need: sea mode, islets
  with one trunk each.
- **route-106** (route, 80x20): shore path to the Shadowlands, roots as walls · need: root arches.
- **route-107** (route, 60x20): lagoon crossing on the water, a trail up a trunk to Rwookrrorro · need: a
  climbable trunk (stairs cut into bark, a spiral).
- **route-108** (route, 60x20): open water around the Republic Wreck: a cruiser hull sticking out of the sea ·
  need: the wreck as a giant tilted hull, partly seen, breaking the water.
- **route-109** (route, 40x63): the southern beach and a seaside hut · need: beach.
- **ice-grotto** (17x33): a cold cave on an islet, ICEWARDEN · need: ice cave mode (blue walls, frost).
- **republic-wreck** (14 rooms): the inside of a sunken Republic cruiser: tilted deck above water, crew
  corridors, cabins, flooded lower decks, the sealed hold, two underwater rooms · need: ship interior kit
  (bulkheads, blast doors, grating), flooded floor (shallow water in a room), tilt.
- **shadowlands-1f, b1f, b2f, leias-room**: the dark forest floor under the roots: hollow trunks, root walls,
  cracked floors that drop a level · need: root walls instead of rock, darkness, floor holes.
- **underwater-route-105**: under the lagoon · need: underwater mode (blue tint, bubbles, seaweed, rock).
- Interiors (11): Wookiee huts and the great hall (wood, carved posts, hanging hides), Tarfful's gym (a
  fighting ring), the Falcon hangar room, bacta center and depot.

---

## Sullust (2 towns, 2 routes, 6 cave rooms, 19 interiors)

Volcanic: black ash fields, basalt columns, steam vents, hot springs, lava. Sullustan homes are half-buried.
No trees.

- **inyusu-tor** (town, 40x28): ash farm town, greenhouses, Dr. Tien's observatory with a dome, ash falling
  like snow · need: greenhouses (glass boxes, have glass-dome), observatory dome with a slit, ash drifts.
- **pirin** (town, 42x34): hot-spring town in a volcanic bowl: the bowl's cliff rim is the border, spaceport pad,
  Sabine's Fire gym, bathhouse, the steaming spring pool · need: steam (a prop effect), the bowl rim with the
  town sunk inside (relief does this).
- **route-113** (route, 100x20): ash fields, the glassblower's hut, ash drifts, Magma Tunnel mouths · need:
  ash as a ground kind, drifts as berms.
- **route-114** (route, 40x80): rocky road down to Starfall Cavern, Tess's workshop, fossil collector's home,
  a river · need: basalt columns (hexagonal prisms, have oct), a waterfall where the cavern starts.
- **magma-tunnels** (35x38): volcanic tunnels · need: cave mode with a lava glow variant.
- **starfall-cavern** (5 rooms): a cavern where a meteorite fell: waterfalls inside, pools, ledges, the
  meteorite crater, a hidden post-game room · need: cave waterfalls, pools, the meteorite (a half-buried
  sphere, glowing).
- Interiors (19): Sullustan half-buried homes (round rooms dug down), bathhouse (pools inside), Sabine's gym
  (fire pits), observatory (telescope), greenhouse interiors, Tess's workshop (the storage system terminal),
  spaceport hangar.

---

## Mustafar (2 routes, 1 landmark, 8 fortress rooms, 2 interiors)

Lava world: black rock, rivers of lava, ash, Imperial machinery. No trees. Everything glows from below.

- **mustafar-peak** (route, 40x47): the summit: the shuttle pad, the Empire's drill rig boring into the
  volcano, the first Vader fight · need: lava as liquid with glow on nearby faces, the drill rig (a tall
  Imperial machine, giant, partly seen), the crater rim.
- **ashen-pass** (route, 30x46): steep ash trail down the mountain with many ledges, to the fortress gate ·
  relief and ledges cover it · need: ash ground.
- **mustafar-mining-facility** (landmark, 40x30): the old Separatist facility on a lava river: collector arms
  reaching over the lava, catwalks, control center · need: catwalk layer over lava, collector arms (long
  horizontal booms on pylons), a lava river with banks.
- **fortress-vader** (8 rooms): Vader's castle cut into the cliff: gate hall, halls, lava conduits (lava
  channels inside the rooms), guard rooms, barracks, the meditation chamber over the lava · need: Imperial
  dark interior kit (black walls, red light strips), lava channels indoors, a raised dais, the fortress
  exterior as a landmark set piece (two tuning-fork towers, giant).
- Interiors (2): shuttle station, control center.

---

## Endor (1 town, 5 routes, 1 landmark, 2 dungeon rooms, 16 interiors)

Redwood forest: giant trunks, ferns, rivers, Ewok villages in the treetops, Imperial bunkers. The canopy is
off the top of the map; trunks are the border.

- **bright-tree** (town, 40x20): Ewok treetop village: a forest-floor trail, ladders up to two rows of tree
  platforms joined by rope bridges, huts on the platforms, Chief Chirpa's gym · need: the raised-walkway layer
  with two platform rows, rope bridges, trunks, cone huts on decks (have cone).
- **route-118** (route, 80x20): forest edge, Rebel shuttle pad, a river east · need: river banks, a parked
  shuttle.
- **route-119** (route, 40x140): the long treewalk climb through redwoods and ferns, Endor Station (an
  Imperial research bunker, have bunker), raised walkways · need: trunks, walkways, ferns as wild ground.
- **route-120** (route, 40x100): deep forest, the Ancient Tomb and Scorched Hollow entrances, a path to the
  battlefield · need: tomb door in a mound.
- **route-121** (route, 80x20): forest road, the reserve shuttle stop · have.
- **route-123** (route, 140x20): river valley, the berry grower's lodge · need: river, orchard rows (plants).
- **endor-battlefield** (landmark, 40x30): the clearing: AT-ST wrecks, log traps hanging from trees, the
  abandoned shield bunker · need: AT-ST (two-legged walker, wedge head, needs hull and rotated boxes), log
  traps (logs on ropes), fallen logs.
- **ancient-tomb** (17x33): a stone tomb, DURAWARDEN · need: cave mode with cut stone walls.
- **scorched-hollow** (15x20): a sun-baked hollow with a pool · need: cave mode, open to the sky.
- Interiors (16): Ewok huts (round, hides, totems), Chirpa's gym (a fighting ring on a platform), Endor
  Station (Imperial bunker interior), the lodge, the shield bunker.

---

## Bespin (1 town, 1 landmark, 27 interiors)

A city floating in the clouds. The ground is a platform over sky. Clean white and bronze.

- **cloud-city** (town, 70x46): the floating city: central plaza, Galleria (winged), museum, Showcase hall,
  Lando's flat, round towers, west landing platform, the east lift down to the under-levels, skybridges ·
  unique: every edge is a drop into cloud · need: floating-platform mode (fascia and underside at the edge,
  clouds below instead of ground), skybridges, cloud cars parked.
- **tibanna-refinery** (landmark, 40x26): a separate platform north, reached by cloud car or skybridge: gas
  tanks, pipes, Ugnaught work sheds · need: the platform mode, big tanks (have), pipe runs.
- Interiors (27): Galleria floors (1 to 4 plus rooftop, a lift), museum floors, Showcase hall, Lando's flat,
  bacta center, sky motel, Tibanna trader, Cloud car pilot's, Ugnaught family, the under-levels (dark
  industrial corridors where the Cartel hide, the carbon-freezing chamber with its glow and steam, a hidden
  stash). Need: a clean white interior kit and a dark industrial one.

---

## Jedha (1 town, 3 routes, 11 interiors)

A holy desert moon: cold sand, cut stone, pilgrims, the ruined Temple. No trees.

- **nijedha** (town, 44x34): the holy city: dense stone houses in a wall, the Temple of the Kyber (stepped),
  prayer candles, the toppled Jedi statue · need: a walled city edge (giant wall, partly seen), the fallen
  statue (a tilted giant figure, one-off), candle clusters.
- **route-122** (route, 40x40): holy waters around the Temple island, the pilgrim pad, a causeway · need: sea
  mode, a causeway over water.
- **jedha-temple-exterior** (route, 38x51): outer terraces with graves of companions, pilgrims climbing ·
  relief covers terraces · need: grave markers (small stones), stairs between levels.
- **jedha-temple-summit** (route, 50x37): the summit with the Guardians and the red and blue kyber shrines ·
  need: glowing crystals, a shrine dais.
- Interiors (11): the Temple of the Kyber hall (long nave), pilgrim houses, the Guardians' quarters, bacta
  center, depot, a hangar.

---

## Yavin 4 (1 town, 2 routes, 2 underwater rooms, 14 interiors)

Jungle moon with the Massassi temples. Trees and vines, river delta, Rebel base.

- **yavin-4** (town, 70x44): the Rebel base: the Massassi Temple (huge stepped pyramid, the gym, taller than
  the map, partly seen), the hangar with X-wings outside, Leia's quarters · need: the temple as a landmark set
  piece (giant), X-wings (wedge with four wings), jungle trunks.
- **route-124** and **route-125** (80x80, 80x40): the river delta and jungle lakes, deep channels to dive, the
  treasure divers' hut · need: river and lake mode, dive spots (dark patches).
- **underwater-route-124, -125**: under the river · need: underwater mode.
- Interiors (14): temple interior (the gym: a great hall with pillars and a throne-like dais), hangar
  (X-wings inside), Leia's quarters, briefing room (a holotable), barracks, bacta center.

---

## Hoth (1 route, 7 cave rooms, 3 interiors)

Ice world: snow plains, ice cliffs, a frozen lake, caves. No trees. Everything is white and blue.

- **hoth-tundra** (route, 48x40): the only overworld: the survey shuttle on the tundra, the Rebel survey outpost
  (hex hangar), the tauntaun shelter, the Wampa Cave mouth in an ice cliff, a frozen lake to walk or surf ·
  need: snow as ground, frozen lake (ice with cracks, a water kind), ice cliffs (relief with ice colours),
  snowdrifts as berms.
- **wampa-cave** (7 rooms): ice tunnels with meltwater pools that rise and fall (two versions of the same
  rooms), a slippery ice-floor puzzle room, the wampa's lair with bones and an old scout's pack · need: ice
  cave mode (translucent walls), pools, ice floor, bones.
- Interiors (3): the survey outpost, tauntaun shelter (stalls), the shuttle pad room.

---

## Dagobah (1 town, 5 routes, 1 landmark, 22 cave and underwater rooms, 16 interiors)

Swamp: bog lakes, mist, gnarltrees with huge roots, mud islets. The town is a hidden hollow.

- **dagobah** (town, 60x60): the hollow: Yoda's hut (half-buried, the gym), the Cave of Evil mouth under the
  roots in the north-west, a bog lagoon in the middle, the bog landing in the south-east, a surf channel ·
  need: swamp mode (shallow water mixed with mud and roots), gnarltrees (twisted trunks with root arches),
  hanging moss, mist.
- **route-126 to route-130** (80x80, 80x80, 120x40, 80x40, 80x40): bog lakes, misty channels, deep swamp with
  dive spots, a wide lake with drifting logs and trainers on rafts, the far bog where Mirage Isle rises ·
  need: swamp mode, drifting logs and rafts (floating props), fog.
- **mirage-isle** (landmark, 80x40): the islet that only sometimes appears, a rare berry tree · need: an islet
  that reads as unreal (pale, glowing edge).
- **cave-of-evil** (3 rooms): a dark-side vergence under the roots: visions on the walls, the deepest room
  where the titans clash · need: root-cave mode, a vision effect (ghost shapes on walls), a big open floor.
- **drowned-cavern** (10 rooms): flooded caves where SANDO wakes: pools, ledges, currents, the final chamber ·
  need: cave mode with water, current arrows, a huge chamber for a titan.
- **marine-cave** (2 rooms) and **underwater-** rooms (7): optional flooded cave and the murky water under the
  swamp: roots, silt · need: underwater mode in brown.
- Interiors (16): Yoda's hut (tiny, round, a cooking pot, the gym fight happens outside?), bog landing hangar,
  trainers' rafts, the berry hut, bacta center.

---

## Kamino (1 town, 4 routes, 4 vault and underwater rooms, 10 interiors)

Storm sea: endless rain, grey waves, white domes on stilts, rocky stacks.

- **tipoca-city** (town, 50x36): domes on stilts joined by walkways round the great cloning hall; nothing but
  sea around it · unique: the whole town is a raised-walkway layer over water · need: sea mode with rain
  (streaks), stilt platforms (have stilts-flat, stilt-dome), walkways between them, the cloning hall as a
  landmark set piece (a huge dome cluster, partly seen), the landing platform.
- **route-131 to route-134** (60x40, 80x40, 80x40, 80x40): storm sea east and west with swimmers, clone cadets
  on training rigs, currents that push the player, rocky stacks, Boba's waters with the Sealed Vault dive spot
  · need: sea mode, current arrows, rock stacks (have spire), training rigs (small platforms on pylons).
- **sealed-vault** (2 rooms) and **underwater-** (2): the sunken door and the vault with Aurebesh carvings ·
  need: underwater mode, a carved-wall room, a sealed door.
- Interiors (10): clean white Kaminoan rooms: the cloning hall (rows of growth pods, have tank), labs, the
  Prime Minister's office, cadet barracks, bacta center, landing platform room.

---

## Ilum (1 town, 3 cave rooms, 17 interiors)

Ice world of the kyber caves. Blue-white cliffs, a basin, the north plateau, the Jedi temple gate.

- **ilum** (town, 44x60): ships land in the south basin by the bacta center; the Crystal Caves cut through a
  cliff band to the north plateau where the gate warden checks the eight badges; the Jedi temple gate
  (stepped) · need: ice cliffs (relief in ice colours), snow, the cave mouths, the temple gate cut into the
  cliff (giant door, partly seen).
- **crystal-caves** (3 rooms): kyber-lit ice tunnels, the final rival fight, Boba's rematch, a lake on B2F ·
  need: ice cave mode with glowing crystal clusters (shard kit plus glow), a dark lake.
- Interiors (17): the Elite Four halls (five linked rooms, each a different Force master's hall: stone, ice,
  dark, light, the champion's), the temple gate hall, bacta center, depot, lodging.

---

## Felucia (6 routes, 2 interiors)

Fungus jungle in purple and orange: giant mushrooms, spore pods, marsh, a wildlife reserve with a gate.

- **felucia-reserve** (6 zones, 40x40 each): the reserve gate where shuttles land, fungus groves, spore marsh
  with the rest house, giant fungus forest with ledges, deep water among the stalks, a viewing deck, and the
  post-game zone with off-world species · need: giant fungus (have), spore pods (spheres on stalks), a marsh
  ground kind, the viewing deck (have pad), the reserve gate building.
- Interiors (2): the gate house, the rest house.

---

## Tython (2 routes, 1 interior)

A small Force-sacred island: a landing pad, a climbing path, standing stones where ASHLA or BOGAN appears.

- **tython-isle-exterior** and **-interior** (33x30, 27x24): the island in the sea, a path up cliffs, the
  stone circle in a grove · need: sea mode, standing stones (tall tapered prisms, have), a circle layout.

---

## Atollon (1 landmark, 1 interior)

A rocky moon where the BENDU sleeps on a stone dais; the triangle puzzle wakes it.

- **atollon-exterior** (landmark, 30x30): a rock islet in a strange sea with a dais · need: sea mode, a stone
  dais with glyphs.

---

## Mortis (3 landmarks, 20 dungeon rooms, 1 interior)

A realm outside normal space: a monolith in a strange sea, floating stone, a jungle island with a pool of life.

- **mortis-gate-exterior** (landmark, 21x24): the monolith rising from the sea with a doorway · need: a giant
  monolith (one-off), a sea in an odd colour.
- **mortis-gate** (20 rooms): stairs up to the FATHER's peak and down to the DAUGHTER's hollow: an entrance,
  a long fork, eleven short descending rooms, four ascending, the bottom with a pool, the top open to the sky ·
  need: stone-stair rooms (sunken stairwell kit covers steps), a peak room open to a strange sky, a hollow with
  a glowing pool.
- **wellspring-entrance** and **-interior** (34x46, 29x26): a jungle island, long grass, a clearing round the
  pool of life · need: jungle trunks, a glowing pool.

---

## Asteroid Field (2 routes, 6 spire rooms, 1 interior)

Rock in space: the Asteroid Spire, open to the stars.

- **asteroid-spire-outside** (route, 28x23): the asteroid's surface, a crumbling path, star void instead of
  sea · need: void as the water kind (have "void"), floating-platform edges (no cliff below, just stars).
- **asteroid-spire-top** (route, 27x24): the open summit, EXOGORTH's lair · need: a void edge all round.
- **asteroid-spire** (6 rooms): the docking hollow where ships berth, then five floors of cracked floors
  (hover-bike speed) and falling rubble · need: cave mode in grey, cracked floor tiles, rubble piles.
- Interior (1): the docking hollow's berth room.

---

## Death Star (6 rooms)

Post-game: a half-built hangar bay and five construction decks, all interiors: scaffolds, reactor feed
corridors, the detention block, a turbolaser battery, the command deck · need: the Imperial interior kit
(black floor grating, white corridor panels, blast doors, consoles, cell doors, scaffold frames), the trench
wall giant for the hangar's open side (have).

---

## Grand Arena (2 routes, 2 cave rooms, 61 interiors)

Lando's battle island (the Battle Frontier): seven facilities on a cliff-ringed island, lounges, the
reception gate where ships dock.

- **grand-arena-outside-west** and **-east** (56x72, 72x72): the Dome, Factory, Pike, Lando's villa, the
  Tower, Arena, Palace, Pyramid, ranking hall, exchange corner, bacta center, lounges, the reception gate ·
  need: seven distinct big facilities (each a landmark-sized building with its own silhouette: a dome, a
  factory with stacks, a long pike hall, a tall tower, a palace, a pyramid), sea all round, cliffs.
- **artisan-cave** (2 rooms): a hidden cave full of a painter companion's wall paintings · need: cave mode
  with painted walls.
- Interiors (61): the facility lobbies, corridors and battle rooms (Tent, Arena, Dome), sixteen Pyramid
  floors (dark, a torch-light radius), lounges, the ranking hall, the exchange corner, Lando's villa.

---

## Shared (18 interiors)

Rooms used on several planets: the ship rooms (one per route between planets, each with a StarNAV console
and the ship's cockpit or hold), the standard bacta center, supply depot and arena interiors.

---

## What this list implies

The missing tools, in the order they unlock the most areas. Counts are areas that need the item.

| Missing tool | Areas | Where it matters most |
| --- | --- | --- |
| Room kit (walls, doors, floors) and furniture | 329 interiors + 60 dungeon rooms | Every interior |
| Cave mode (walls all round, dark margin, floor style per planet: sand, ice, root, basalt, stone, painted) | about 90 rooms | Hoth, Ilum, Dagobah, Sullust, Tatooine, Mortis |
| Sea and lake mode (deep water with a shore, currents, rain) | about 30 | Kamino, Kashyyyk, Dagobah, Yavin 4, Jedha, Tython, Atollon |
| Raised-walkway layer (platforms over the ground or water, bridges, ladders) | 8 | Kachirho, Rwookrrorro, Bright Tree, Tipoca City, Route 110, Route 119, the mining facility |
| Floating-platform mode (edges over sky or space) | 5 | Cloud City, the refinery, the asteroid spire |
| Giant trunks (wroshyr, redwood, gnarltree) with the canopy off the map | about 15 | Kashyyyk, Endor, Dagobah, Yavin 4 |
| Lava mode (liquid with glow, indoor channels) | about 12 | Mustafar, Sullust |
| Swamp and marsh ground | about 10 | Dagobah, Felucia |
| Snow, ash, salt and sand drifts as ground kinds and berms | about 10 | Hoth, Ilum, Sullust, Mustafar, Tatooine |
| Underwater mode | 12 | Dagobah, Yavin 4, Kashyyyk, Kamino |
| Hull primitive (wedges) for ships, walkers, wrecks, crystals | about 25 | Every landed ship and wreck |
| Glow pass (crystals, lava, pools, holograms) | about 15 | Ilum, Mustafar, Jedha, Mortis |
| Landmark set pieces, one-off models | 12 | Jabba's palace, Massassi temple, Fortress Vader, cloning hall, Jedha statue, Mortis monolith, drill rig, Ilum gate, the seven Grand Arena facilities |
| Market and farm props (stalls, fences, pens, troughs) | about 10 | Tatooine towns, Route 117 |

Done so far: buildings, doorless structures, sunken pieces, Imperial military, nature (pine, boulder, shard,
fungus), landforms, hangars and bays, gyms, relief terrain with cliffs and ledges, the scene composer.
