"""Port the wiki world (wiki/world/) into ../game. See world_port/README.md.

  python3 tools/port_world.py install [PLANET|AREA ...] [-AREA ...]   write these planets or areas (all when none)
                                                       into ../game, leaving out the -AREA ones
"""
import sys

from world_port import install as I


def main(argv):
    cmd = argv[0] if argv else "install"
    if cmd == "install":
        args = [a for a in argv[1:] if not a.startswith("-")]
        exclude = {a[1:] for a in argv[1:] if a.startswith("-")}
        scope = {p.upper() for p in args} | set(args) if args else None
        world, report = I.install(scope, exclude)
        for p in world.warp_problems + world.conn_problems + world.event_problems:
            print("note:", p)
        print(f"{len(report)} areas written, {sum(1 for r in report if r[3])} with their own tileset")
        return 0
    print(__doc__)
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
