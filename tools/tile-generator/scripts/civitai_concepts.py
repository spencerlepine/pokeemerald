"""Concept paintings for world-art rows with Civitai's hosted SDXL generator (paid in Buzz).

    python scripts/civitai_concepts.py --whatif          # price it, spend nothing
    python scripts/civitai_concepts.py [--only slug,..]  # generate, save to wiki/art/concept/<planet>/<slug>__civ_<n>.jpg

Key: CIVITAI_API_TOKEN in the environment (never commit it).
"""
import argparse, io, json, os, random, sys, time
from pathlib import Path
import requests
from PIL import Image

REPO = Path(__file__).resolve().parents[3]
OUT = REPO / "wiki/art/concept"
URL = "https://orchestration.civitai.com/v2/consumer/workflows"
MODEL = "urn:air:sdxl:checkpoint:civitai:133005@782002"  # Juggernaut XL XI

STYLE = ("Star Wars concept art, matte painting in the style of Ralph McQuarrie and Doug Chiang, "
         "cinematic lighting, painterly, detailed environment, high angle three-quarter view")
NEG = ("text, watermark, signature, logo, people, crowd, characters, blurry, lowres, deformed, "
       "photo frame, border, cartoon, anime")

JOBS = {
    "tatooine/desert-scrub": "low grey-green desert scrub bushes and dry grass tufts on rippled orange sand dunes, Tatooine, twin suns low in the sky",
    "tatooine/office-tower-floors": "interior of a sandstone office floor in Bestine on Tatooine, rounded adobe walls, carpeted floor, desks with blue holographic screens, a turbolift lobby, arched windows onto desert city",
    "kashyyyk/fern-clump": "giant lush fern bush on the jungle floor of Kashyyyk, huge wroshyr tree trunks behind, shafts of green light, mossy ground",
    "kashyyyk/beach-rocks": "dark hexagonal basalt rocks on a pale sand lagoon beach of Kashyyyk, turquoise water, giant wroshyr trees on the shore",
    "sullust/fungus-stalks": "cluster of tall pale bioluminescent cave mushrooms in a dark volcanic lava tube on Sullust, faint blue glow, floating spores",
    "sullust/hot-spring-bathhouse": "domed volcanic-stone bathhouse with round windows beside a steaming turquoise hot spring pool, ash plains and smoking volcanoes of Sullust, orange sky",
    "sullust/sullustan-home": "rounded volcanic-stone Sullustan house half built into a dark hillside, big round porthole windows glowing warm, round door, ash sky with volcanoes",
    "sullust/ash-farm": "low stone farmhouse with a glass greenhouse dome beside it, furrowed grey ash fields with sparse green crops, volcanoes of Sullust glowing behind",
    "sullust/ash-greenhouse": "glass geodesic greenhouse dome full of green plants and flowers standing on a grey volcanic ash plain, Sullust, smoky orange sky",
    "grand-arena/tython-standing-stones": "ring of ancient carved standing stones with glowing blue Je'daii glyphs on a grassy island, glowing kyber crystal monolith in the centre, Tython at dusk, sea behind",
}


def http(method, url, **kw):
    h = {"Authorization": f"Bearer {os.environ['CIVITAI_API_TOKEN']}"}
    for a in range(4):
        r = requests.request(method, url, headers=h, timeout=60, **kw)
        if r.status_code in (429, 502, 503, 504) and a < 3:
            time.sleep(2 ** (a + 1)); continue
        if r.status_code >= 400:
            sys.exit(f"HTTP {r.status_code}: {r.text[:1500]}")
        return r.json()


def workflow(prompt, seed, n):
    return {"steps": [{"$type": "textToImage", "input": {
        "model": MODEL, "prompt": f"{prompt}, {STYLE}", "negativePrompt": NEG,
        "scheduler": "DPM2MKarras", "steps": 30, "cfgScale": 5.5, "width": 1216, "height": 832,
        "seed": seed, "clipSkip": 2, "quantity": n, "outputFormat": "jpeg"}}],
        "currencies": ["green"]}


def cost(r):
    return ", ".join(f"{t['amount']} {t['accountType']}" for t in (r.get("transactions") or {}).get("list", [])) or "?"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--whatif", action="store_true")
    ap.add_argument("--only")
    ap.add_argument("-n", type=int, default=2, help="images per concept")
    a = ap.parse_args()
    jobs = {k: v for k, v in JOBS.items() if not a.only or k.split("/")[1] in a.only.split(",")}
    pending = {}
    for k, p in jobs.items():
        wf = workflow(p, random.randrange(1, 2**31 - 1), a.n)
        if a.whatif:
            print(k, cost(http("POST", URL, params={"whatif": "true"}, json=wf))); continue
        r = http("POST", URL, json=wf)
        pending[k] = r["id"]; print("submitted", k, cost(r))
    while pending:
        time.sleep(4)
        for k, wid in list(pending.items()):
            s = http("GET", f"{URL}/{wid}")
            imgs = (s.get("steps") or [{}])[0].get("output", {}).get("images", [])
            if s.get("status") in ("failed", "expired", "canceled"):
                print("FAILED", k, s.get("status")); del pending[k]; continue
            if s.get("status") == "succeeded" and imgs and all(i.get("available") for i in imgs):
                planet, slug = k.split("/")
                for i, im in enumerate(imgs, 1):
                    img = Image.open(io.BytesIO(requests.get(im["url"], timeout=120).content)).convert("RGB")
                    img.thumbnail((1024, 1024))
                    p = OUT / planet / f"{slug}__civ_{i}.jpg"
                    img.save(p, quality=88); print("saved", p.relative_to(REPO))
                del pending[k]


if __name__ == "__main__":
    main()
