"""Port the wiki world (wiki/world/) into ../game. See world_port/README.md.

  python3 tools/port_world.py install [PLANET|AREA ...] [-AREA ...]   write these planets or areas (all when none)
                                                       into ../game, leaving out the -AREA ones;
                                                       then fixes and checks the map seams (seams.py)
  python3 tools/port_world.py seams spots FILE         a walk across every connection, for the play-tester's
                                                       scripts/seam-check.sh
  python3 tools/port_world.py seams verify [DIR]       compare seam-check.sh's dumps with what the game should show
"""
import sys

from world_port import install as I


def main(argv):
    cmd = argv[0] if argv else "install"
    if cmd == "install":
        args = [a for a in argv[1:] if not a.startswith("-")]
        exclude = {a[1:] for a in argv[1:] if a.startswith("-")}
        scope = {p.upper() for p in args} | set(args) if args else None
        world, report = I.port(scope, exclude)
        for p in world.warp_problems + world.conn_problems + world.event_problems:
            print("note:", p)
        s = world.seams
        print(f"map seams: {dict(s.counts)}, {len(s.remaps)} remapped, {len(s.approx)} in the nearest palette")
        for p in world.seam_problems:
            print("SEAM ERROR:", p)
        if world.seam_problems:
            return 1
        print(f"{len(report)} areas written, {sum(1 for r in report if r[3])} with their own tileset")
        from world_port import paint as PA
        PA.paint(world)
        return 0
    if cmd == "paint":
        # the paint step alone, on an installed game (install runs it too)
        from world_port import paint as PA
        PA.paint(I.World())
        return 0
    if cmd == "seams":
        return seams(argv[1:])
    print(__doc__)
    return 1


def seams(argv):
    """`seams spots FILE`: one walk across every connection for tools/play-tester/scripts/seam-check.sh.
    `seams verify [DIR]`: compare its dumps (default tools/play-tester/out/seams) with what seams.py expects."""
    from world_port import seams as SM, base as B
    state = SM.GameState()
    if argv and argv[0] == "spots":
        lines, none = SM.spots(state)
        open(argv[1], "w").write("\n".join(lines) + "\n")
        print(f"{len(lines)} walks written to {argv[1]}; {len(none)} connections have no plain walk:")
        for x in none:
            print("  ", x)
        return 0
    if argv and argv[0] == "verify":
        out = argv[1] if len(argv) > 1 else B.ROOT / "tools/play-tester/out/seams"
        report, problems = SM.verify(out, SM.read_header(), state)
        print("\n".join(report))
        for p in problems:
            print("SEAM ERROR:", p)
        print(f"{len(report)} walks, {len(problems)} problems")
        return 1 if problems else 0
    print(seams.__doc__)
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
