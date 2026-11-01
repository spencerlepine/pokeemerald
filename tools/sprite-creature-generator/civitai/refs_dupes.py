#!/usr/bin/env python3
"""List reference images picked by more than one species (refs/picks/*.json)."""
import json, re
from collections import defaultdict
from pathlib import Path
g = defaultdict(list)
for p in sorted((Path(__file__).parent / "refs" / "picks").glob("*.json")):
    src = json.loads(p.read_text()).get("init_source")
    if src:
        g[re.sub(r"/revision.*|#.*", "", src).rsplit("/", 1)[-1]].append(p.stem)
for k, v in sorted(g.items()):
    if len(v) > 1:
        print(f"{k}: {' '.join(v)}")
