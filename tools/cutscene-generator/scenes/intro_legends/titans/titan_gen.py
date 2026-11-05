"""Intro scene 3 titans: wide image-to-image on Civitai at the scene's own pixel grid.

The scene window is 240x96. A titan fits in 144x96 native pixels; the creature LoRA draws on an
8 px grid but the API caps a side at 1024, so the canvas is 1008x672 (144x96 x 7). The start image is the creature's in-game
battle sprite (or a canon picture) fitted into that box on white. Uses the creature tool's key
handling and HTTP helpers (../../../../sprite-creature-generator/civitai/civitai_creature.py).

  python3 titan_gen.py prep groudon [--src FILE] [--flip] [--h 88] -> prep/groudon.png
  python3 titan_gen.py gen groudon --desc "..." --denoise 0.5 -n 2 [--whatif]
"""
import argparse, base64, io, json, random, sys, time, datetime as dt
from pathlib import Path
import requests
from PIL import Image
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[3] / 'sprite-creature-generator' / 'civitai'))
import civitai_creature as cc  # noqa: E402

GAME = HERE.parents[4] / 'game' / 'graphics' / 'pokemon'
NW, NH, GRID = 144, 96, 7  # 1008x672: the API caps width at 1024
NEG = ("human, person, multiple creatures, text, watermark, signature, frame, border, scenery, "
       "background, ground, shadow, cropped, cut off, blurry, 3d, photo, realistic, painting, smooth shading")
PROMPT = ("{style}, ({subject}:1.1), ({desc}:1.2), pokemon, single giant creature, full body, side view facing left, "
          "({colour} body:1.3), limited palette, pixel art, game sprite, crisp dark outlines, white background, simple background")


def cut(im):
    a = np.array(im.convert('RGBA'))
    key = a[0, 0, :3]
    m = ~np.all(a[..., :3] == key, axis=-1) & (a[..., 3] > 0)
    a[..., 3] = np.where(m, 255, 0)
    ys, xs = np.where(m)
    return Image.fromarray(a[ys.min():ys.max() + 1, xs.min():xs.max() + 1])


def prep(species, src=None, flip=False, h=88, w=136, resample=Image.NEAREST, out=None):
    im = cut(Image.open(src) if src else Image.open(GAME / species / 'front.png'))
    if flip:
        im = im.transpose(Image.FLIP_LEFT_RIGHT)
    k = min(w / im.width, h / im.height)
    im = im.resize((round(im.width * k), round(im.height * k)), resample)
    can = Image.new('RGBA', (NW, NH), (255, 255, 255, 255))
    can.alpha_composite(im, ((NW - im.width) // 2, NH - 4 - im.height))
    big = can.convert('RGB').resize((NW * GRID, NH * GRID), Image.NEAREST)
    out = Path(out or HERE / 'prep' / f'{species}.png')
    out.parent.mkdir(exist_ok=True)
    big.save(out)
    return out


def data_uri(p):
    buf = io.BytesIO(); Image.open(p).convert('RGB').save(buf, 'PNG')
    return 'data:image/png;base64,' + base64.b64encode(buf.getvalue()).decode()


def gen(a):
    v = cc.pick_version(None)
    lora = v.get('air') or f"urn:air:sd1:lora:civitai:{cc.LORA_MODEL_ID}@{v['id']}"
    prompt = a.prompt or PROMPT.format(style=a.style, subject=a.subject, desc=a.desc, colour=a.colour)
    seed = a.seed or random.randrange(1, 2**31 - 1)
    step = {"$type": "imageGen", "input": {
        "engine": "comfy", "ecosystem": "sd1", "operation": "createVariant",
        "checkpointModel": cc.CHECKPOINTS['sd1'], "loras": {lora: a.strength},
        "image": data_uri(a.init), "denoiseStrength": a.denoise, "prompt": prompt,
        "negativePrompt": a.negative or NEG, "sampler": "euler_ancestral", "scheduler": "normal",
        "steps": a.steps, "cfgScale": a.cfg, "seed": seed, "clipSkip": 2,
        "width": NW * GRID, "height": NH * GRID, "quantity": a.n, "outputFormat": "jpeg"}}
    wf = {"steps": [step], "currencies": a.currency.split(',')}
    url = f"{cc.ORCHESTRATOR}/v2/consumer/workflows"
    if a.whatif:
        r = cc.http('POST', url, params={'whatif': 'true'}, json=wf).json(); print('whatif', cc._cost(r)); return
    r = cc.http('POST', url, json=wf).json(); wid = r['id']
    print('submitted', wid, cc._cost(r), 'seed', seed, flush=True)
    t0 = time.time()
    while True:
        s = cc.http('GET', f'{url}/{wid}').json(); st = s.get('status')
        imgs = (s.get('steps') or [{}])[0].get('output', {}).get('images', [])
        if st in ('failed', 'expired', 'canceled'):
            sys.exit(f'{wid} {st}: {json.dumps(s)[:1500]}')
        if st == 'succeeded' and imgs and all(i.get('available') for i in imgs):
            break
        if time.time() - t0 > 600:
            sys.exit('timeout ' + wid)
        time.sleep(3)
    out = HERE / 'runs' / a.species / 'raw'; out.mkdir(parents=True, exist_ok=True)
    stamp = dt.datetime.now().strftime('%Y%m%d-%H%M%S')
    for i, im in enumerate(imgs):
        d = requests.get(im['url'], timeout=120); d.raise_for_status()
        p = out / f"{stamp}_{a.tag}_d{a.denoise}_s{im.get('seed') or seed + i}.png"
        Image.open(io.BytesIO(d.content)).convert('RGB').save(p)
        p.with_suffix('.json').write_text(json.dumps({'prompt': prompt, 'init': str(a.init), 'denoise': a.denoise,
                                                      'cfg': a.cfg, 'seed': im.get('seed') or seed + i,
                                                      'strength': a.strength, 'workflow': wid}, indent=1))
        print(p, flush=True)


if __name__ == '__main__':
    ap = argparse.ArgumentParser(); sub = ap.add_subparsers(dest='cmd', required=True)
    p = sub.add_parser('prep'); p.add_argument('species'); p.add_argument('--src'); p.add_argument('--flip', action='store_true')
    p.add_argument('--h', type=int, default=88); p.add_argument('--w', type=int, default=136); p.add_argument('--out'); p.add_argument('--smooth', action='store_true')
    g = sub.add_parser('gen'); g.add_argument('species'); g.add_argument('--init'); g.add_argument('--subject', default='')
    g.add_argument('--desc', default=''); g.add_argument('--colour', default=''); g.add_argument('--prompt'); g.add_argument('--negative')
    g.add_argument('--style', default='gen3'); g.add_argument('--denoise', type=float, default=0.5); g.add_argument('--cfg', type=float, default=5)
    g.add_argument('--steps', type=int, default=25); g.add_argument('--strength', type=float, default=0.9); g.add_argument('--seed', type=int)
    g.add_argument('-n', type=int, default=2); g.add_argument('--tag', default='x'); g.add_argument('--currency', default='blue')
    g.add_argument('--whatif', action='store_true')
    a = ap.parse_args()
    if a.cmd == 'prep':
        print(prep(a.species, a.src, a.flip, a.h, a.w, Image.LANCZOS if a.smooth else Image.NEAREST, a.out))
    else:
        a.init = Path(a.init) if a.init else HERE / 'prep' / f'{a.species}.png'
        gen(a)


def t2i(species, prompt, negative, n=4, w=1024, h=576, seed=None, currency='green', tag='t2i', model=None, whatif=False):
    """Text to image on SDXL, no sprite LoRA: a clean reference picture on white to pixelate."""
    seed = seed or random.randrange(1, 2**31 - 1)
    step = {"$type": "textToImage", "input": {"model": model or cc.CHECKPOINTS['sdxl'], "prompt": prompt,
            "negativePrompt": negative, "scheduler": "EulerA", "steps": 30, "cfgScale": 6, "width": w,
            "height": h, "seed": seed, "clipSkip": 2, "quantity": n, "outputFormat": "jpeg"}}
    wf = {"steps": [step], "currencies": currency.split(',')}
    url = f"{cc.ORCHESTRATOR}/v2/consumer/workflows"
    if whatif:
        r = cc.http('POST', url, params={'whatif': 'true'}, json=wf).json(); print('whatif', cc._cost(r)); return []
    r = cc.http('POST', url, json=wf).json(); wid = r['id']; print('submitted', wid, cc._cost(r), flush=True)
    t0 = time.time()
    while True:
        s = cc.http('GET', f'{url}/{wid}').json(); st = s.get('status')
        imgs = (s.get('steps') or [{}])[0].get('output', {}).get('images', [])
        if st in ('failed', 'expired', 'canceled'):
            sys.exit(f'{wid} {st}: {json.dumps(s)[:1500]}')
        if st == 'succeeded' and imgs and all(i.get('available') for i in imgs):
            break
        if time.time() - t0 > 600:
            sys.exit('timeout ' + wid)
        time.sleep(3)
    out = HERE / 'runs' / species / 'raw'; out.mkdir(parents=True, exist_ok=True)
    stamp = dt.datetime.now().strftime('%Y%m%d-%H%M%S'); paths = []
    for i, im in enumerate(imgs):
        d = requests.get(im['url'], timeout=120); d.raise_for_status()
        p = out / f"{stamp}_{tag}_s{im.get('seed') or seed + i}.png"
        Image.open(io.BytesIO(d.content)).convert('RGB').save(p)
        p.with_suffix('.json').write_text(json.dumps({'prompt': prompt, 'negative': negative, 'seed': im.get('seed') or seed + i, 'workflow': wid}, indent=1))
        print(p, flush=True); paths.append(p)
    return paths
