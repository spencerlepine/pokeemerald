"""Procedural SVG concept paintings for the 10 world-art items with no reference."""
import math, random, os

W, H = 960, 640
OUT = os.path.dirname(os.path.abspath(__file__)) + '/svg'
os.makedirs(OUT, exist_ok=True)

DEFS = '''
<filter id="grain" x="0" y="0" width="100%" height="100%">
  <feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" seed="3" result="n"/>
  <feColorMatrix type="saturate" values="0"/>
  <feComponentTransfer><feFuncA type="linear" slope="0.10"/></feComponentTransfer>
  <feComposite in2="SourceGraphic" operator="in"/>
</filter>
<filter id="rough" x="-5%" y="-5%" width="110%" height="110%">
  <feTurbulence type="fractalNoise" baseFrequency="0.035" numOctaves="3" seed="7"/>
  <feDisplacementMap in="SourceGraphic" scale="9"/>
</filter>
<filter id="stone" x="0" y="0" width="100%" height="100%">
  <feTurbulence type="fractalNoise" baseFrequency="0.08" numOctaves="4" seed="11" result="t"/>
  <feColorMatrix in="t" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 -1.2 1.1" result="m"/>
  <feComposite in="SourceGraphic" in2="m" operator="in" result="a"/>
  <feBlend in="a" in2="SourceGraphic" mode="multiply"/>
</filter>
<filter id="blur2"><feGaussianBlur stdDeviation="2"/></filter>
<filter id="blur6"><feGaussianBlur stdDeviation="6"/></filter>
<filter id="blur14" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="14"/></filter>
<filter id="blur30" x="-80%" y="-80%" width="260%" height="260%"><feGaussianBlur stdDeviation="30"/></filter>
'''


def svg(body, extra_defs=''):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">'
            f'<defs>{DEFS}{extra_defs}</defs>{body}'
            f'<rect width="{W}" height="{H}" fill="#888" filter="url(#grain)" opacity="0.9"/></svg>')


def lg(id, stops, x2=0, y2=1):
    s = ''.join(f'<stop offset="{o}" stop-color="{c}"/>' for o, c in stops)
    return f'<linearGradient id="{id}" x1="0" y1="0" x2="{x2}" y2="{y2}">{s}</linearGradient>'


def rg(id, stops, cx=.5, cy=.5, r=.5):
    s = ''.join(f'<stop offset="{o}" stop-color="{c}" stop-opacity="{a}"/>' for o, c, a in stops)
    return f'<radialGradient id="{id}" cx="{cx}" cy="{cy}" r="{r}">{s}</radialGradient>'


def ell_shadow(x, y, rx, ry, op=.35):
    return f'<ellipse cx="{x}" cy="{y}" rx="{rx}" ry="{ry}" fill="#000" opacity="{op}" filter="url(#blur6)"/>'


def rock(x, y, s, rnd, base, light, dark, n=7):
    """Faceted rock: polygon with lit top-left facets."""
    pts = []
    for i in range(n):
        a = math.pi + i * math.pi / (n - 1)  # upper half-ish
        r = s * rnd.uniform(.75, 1.1)
        pts.append((x + math.cos(a) * r, y + math.sin(a) * r * rnd.uniform(.8, 1.2)))
    pts += [(x + s * .9, y + s * .15), (x - s * .9, y + s * .15)]
    poly = ' '.join(f'{px:.1f},{py:.1f}' for px, py in pts[:-2] + [pts[-2], pts[-1]])
    out = ell_shadow(x + s * .2, y + s * .2, s * 1.05, s * .3)
    out += f'<polygon points="{poly}" fill="{base}" filter="url(#stone)"/>'
    # facets
    top = pts[n // 2]
    out += f'<polygon points="{pts[1][0]:.1f},{pts[1][1]:.1f} {top[0]:.1f},{top[1]:.1f} {x:.1f},{y - s*.1:.1f}" fill="{light}" opacity=".85"/>'
    out += f'<polygon points="{top[0]:.1f},{top[1]:.1f} {pts[-3][0]:.1f},{pts[-3][1]:.1f} {x + s*.9:.1f},{y + s*.15:.1f} {x:.1f},{y - s*.1:.1f}" fill="{dark}" opacity=".8"/>'
    return out


# ---------------------------------------------------------------- 1 desert scrub
def desert_scrub():
    rnd = random.Random(1)
    d = lg('sky', [(0, '#f3c98b'), (1, '#f7e3bd')]) + lg('sand', [(0, '#e4b77a'), (1, '#c98f52')])
    b = '<rect width="960" height="200" fill="url(#sky)"/>'
    b += '<circle cx="700" cy="70" r="26" fill="#fff6dc"/><circle cx="770" cy="95" r="16" fill="#ffe7b0"/>'
    b += '<circle cx="735" cy="82" r="90" fill="#fff3d0" opacity=".35" filter="url(#blur30)"/>'
    b += '<path d="M0 180 Q120 150 260 175 T560 168 T960 172 L960 210 L0 210Z" fill="#d6a46a" opacity=".7"/>'
    b += '<rect y="190" width="960" height="450" fill="url(#sand)"/>'
    for i in range(14):  # dune ripples
        y = 230 + i * 30
        b += f'<path d="M0 {y} Q240 {y-12} 480 {y} T960 {y}" stroke="#f0cd96" stroke-width="2" fill="none" opacity=".45"/>'
    def tuft(x, y, s):
        o = ell_shadow(x + s * .25, y + 4, s * .9, s * .22, .3)
        for k in range(int(26 * s / 40)):
            a = -math.pi / 2 + rnd.uniform(-1.25, 1.25)
            L = s * rnd.uniform(.5, 1.1)
            x2, y2 = x + math.cos(a) * L, y + math.sin(a) * L * .9
            cx, cy = x + math.cos(a) * L * .4 + rnd.uniform(-5, 5), y + math.sin(a) * L * .6
            col = rnd.choice(['#7d8a64', '#8f9a72', '#6b7656', '#a3a77e', '#5e684b'])
            o += f'<path d="M{x+rnd.uniform(-s*.15,s*.15):.1f} {y} Q{cx:.1f} {cy:.1f} {x2:.1f} {y2:.1f}" stroke="{col}" stroke-width="{rnd.uniform(1.5,3.2):.1f}" fill="none" stroke-linecap="round"/>'
        for k in range(3):  # seed heads
            a = -math.pi / 2 + rnd.uniform(-.8, .8)
            o += f'<circle cx="{x+math.cos(a)*s*.95:.1f}" cy="{y+math.sin(a)*s*.85:.1f}" r="2.2" fill="#d8cfa4"/>'
        return o
    spots = [(140, 330, 46), (230, 300, 30), (420, 420, 64), (520, 395, 36), (760, 350, 50), (690, 520, 70),
             (300, 560, 58), (860, 470, 40), (90, 480, 38), (600, 270, 26), (380, 270, 22)]
    for x, y, s in sorted(spots, key=lambda t: t[1]):
        b += tuft(x, y, s)
    b += rock(560, 600, 30, rnd, '#b07a48', '#d9a671', '#7a4f2e') + rock(880, 300, 18, rnd, '#b07a48', '#d9a671', '#7a4f2e')
    return svg(b, d)


# ---------------------------------------------------------------- 2 office tower floors
def office_tower():
    rnd = random.Random(2)
    d = lg('wall', [(0, '#c9b393'), (1, '#a8916f')]) + lg('carpet', [(0, '#3e4a5c'), (1, '#2c3544')])
    d += lg('win', [(0, '#f6c98a'), (.6, '#f2dcb5'), (1, '#e7b57c')]) + lg('lift', [(0, '#c7cdd2'), (1, '#8d969e')], 1, 0)
    d += '<pattern id="cp" width="32" height="32" patternUnits="userSpaceOnUse"><rect width="32" height="32" fill="none"/><path d="M0 16H32M16 0V32" stroke="#56647a" stroke-width="1" opacity=".5"/></pattern>'
    b = '<rect width="960" height="220" fill="url(#wall)"/>'
    for i in range(4):  # windows with Bestine skyline
        x = 40 + i * 175
        b += f'<rect x="{x}" y="40" width="150" height="130" rx="10" fill="url(#win)" stroke="#6e5b44" stroke-width="6"/>'
        for k in range(4):
            bx = x + 10 + k * 36 + rnd.uniform(-4, 4); bh = rnd.uniform(25, 60)
            b += f'<rect x="{bx:.0f}" y="{170-bh:.0f}" width="26" height="{bh:.0f}" rx="13" fill="#d7aa72" opacity=".8"/>'
        b += f'<line x1="{x+75}" y1="40" x2="{x+75}" y2="170" stroke="#6e5b44" stroke-width="4"/>'
    b += '<rect y="214" width="960" height="10" fill="#7d6a52"/>'
    b += '<rect y="224" width="960" height="416" fill="url(#carpet)"/><rect y="224" width="960" height="416" fill="url(#cp)"/>'
    # lift lobby right
    b += '<rect x="760" y="20" width="190" height="200" fill="#9a8668"/>'
    for i in range(2):
        x = 775 + i * 90
        b += f'<rect x="{x}" y="70" width="70" height="150" fill="url(#lift)" stroke="#5c646b" stroke-width="3"/><line x1="{x+35}" y1="70" x2="{x+35}" y2="220" stroke="#5c646b" stroke-width="2"/>'
        b += f'<rect x="{x+20}" y="50" width="30" height="12" rx="3" fill="#1b2a35"/><text x="{x+35}" y="60" font-size="10" text-anchor="middle" fill="#7ff" font-family="monospace">{3+i}</text>'
    b += '<rect x="760" y="224" width="200" height="416" fill="#b9a586" opacity=".9"/>'  # stone floor lobby
    for i in range(6):
        b += f'<line x1="760" y1="{260+i*64}" x2="960" y2="{260+i*64}" stroke="#8d7a5e" stroke-width="2"/>'
    b += '<line x1="760" y1="224" x2="760" y2="640" stroke="#6b583f" stroke-width="5"/>'
    def desk(x, y):
        o = ell_shadow(x + 70, y + 72, 85, 14, .4)
        o += f'<rect x="{x}" y="{y}" width="140" height="56" rx="8" fill="#d2c3a6"/><rect x="{x}" y="{y+44}" width="140" height="22" rx="6" fill="#9c8a6c"/>'
        o += f'<rect x="{x+10}" y="{y+8}" width="40" height="18" rx="3" fill="#6d6152"/>'
        # holo screen
        o += f'<polygon points="{x+60},{y-40} {x+128},{y-40} {x+120},{y+8} {x+68},{y+8}" fill="#57e0ff" opacity=".28"/>'
        o += f'<polygon points="{x+60},{y-40} {x+128},{y-40} {x+120},{y+8} {x+68},{y+8}" fill="none" stroke="#8ff3ff" stroke-width="1.5"/>'
        for k in range(4):
            o += f'<line x1="{x+68}" y1="{y-30+k*9}" x2="{x+105-k*6}" y2="{y-30+k*9}" stroke="#bff8ff" stroke-width="2" opacity=".8"/>'
        o += f'<ellipse cx="{x+94}" cy="{y+10}" rx="34" ry="6" fill="#57e0ff" opacity=".35" filter="url(#blur6)"/>'
        # chair
        o += f'<ellipse cx="{x+70}" cy="{y+92}" rx="22" ry="14" fill="#5a3a2c"/><rect x="{x+52}" y="{y+70}" width="36" height="16" rx="6" fill="#6e4636"/>'
        return o
    for (x, y) in [(60, 290), (290, 290), (520, 290), (60, 470), (290, 470), (520, 470)]:
        b += desk(x, y)
    for (x, y) in [(730, 250), (730, 600), (20, 250)]:  # potted plants
        b += ell_shadow(x + 4, y + 18, 18, 6) + f'<rect x="{x-12}" y="{y}" width="24" height="20" rx="4" fill="#8a5a3a"/>'
        for k in range(9):
            a = -math.pi / 2 + (k - 4) * .3
            b += f'<path d="M{x} {y} Q{x+math.cos(a)*20:.0f} {y+math.sin(a)*30:.0f} {x+math.cos(a)*30:.0f} {y+math.sin(a)*26:.0f}" stroke="#5f7a45" stroke-width="5" fill="none" stroke-linecap="round"/>'
    # walkway signal: clear aisle at y~430
    return svg(b, d)


# ---------------------------------------------------------------- 3 fern clump
def frond(x, y, ang, L, rnd, cols, curl=.25):
    o = ''
    pts = []
    for i in range(21):
        t = i / 20
        a = ang + curl * t * t * 3
        pts.append((x + math.cos(ang) * L * t + math.cos(a) * 0, y + math.sin(ang) * L * t + (t * t) * L * .35))
    o += 'M' + ' L'.join(f'{px:.1f} {py:.1f}' for px, py in pts)
    leaf = ''
    for i in range(2, 20):
        t = i / 20
        px, py = pts[i]
        ll = L * .22 * (1 - t) ** .7 + 4
        for side in (-1, 1):
            a = ang + side * 1.15 + .25 * t
            leaf += f'<path d="M{px:.1f} {py:.1f} q{math.cos(a)*ll*.5:.1f} {math.sin(a)*ll*.5-4:.1f} {math.cos(a)*ll:.1f} {math.sin(a)*ll+ll*.25:.1f}" stroke="{rnd.choice(cols)}" stroke-width="{5-3*t:.1f}" fill="none" stroke-linecap="round"/>'
    return leaf + f'<path d="{o}" stroke="#3b4a24" stroke-width="2.5" fill="none"/>'


def fern_clump():
    rnd = random.Random(3)
    d = lg('jg', [(0, '#24301c'), (1, '#41512b')]) + rg('sun', [(0, '#e9f2a8', .55), (1, '#e9f2a8', 0)], .3, .1, .6)
    b = '<rect width="960" height="640" fill="url(#jg)"/>'
    # background trunks
    for x, w in [(60, 120), (820, 160), (430, 70)]:
        b += f'<rect x="{x}" y="0" width="{w}" height="330" fill="#3a2a1c" opacity=".7" filter="url(#rough)"/>'
        for k in range(8):
            b += f'<line x1="{x+10+k*w/8:.0f}" y1="0" x2="{x+5+k*w/8:.0f}" y2="330" stroke="#2a1d12" stroke-width="3" opacity=".6"/>'
    b += '<rect width="960" height="640" fill="url(#sun)"/>'
    b += '<path d="M0 300 Q480 260 960 310 L960 640 L0 640Z" fill="#4c5a2c"/>'
    for i in range(160):  # moss texture
        x, y = rnd.uniform(0, 960), rnd.uniform(300, 640)
        b += f'<ellipse cx="{x:.0f}" cy="{y:.0f}" rx="{rnd.uniform(4,14):.0f}" ry="{rnd.uniform(2,5):.0f}" fill="{rnd.choice(["#5d6d36","#3f4d24","#6b7a3c"])}" opacity=".6"/>'
    cols_main = ['#4f7a2c', '#5f8f34', '#6fa03c', '#3f6624', '#83b04a']
    cols_far = ['#3e5c24', '#47682a', '#36521f']
    def clump(cx, cy, s, cols, n=13):
        o = ell_shadow(cx, cy + 18 * s, 170 * s, 40 * s, .45)
        angs = sorted([-math.pi / 2 + rnd.uniform(-1.6, 1.6) for _ in range(n)], key=lambda a: -abs(a + math.pi / 2))
        for a in angs:
            o += frond(cx, cy, a, rnd.uniform(130, 190) * s, rnd, cols)
        # fiddleheads
        for k in range(3):
            fx, fy = cx + rnd.uniform(-25, 25) * s, cy - rnd.uniform(20, 50) * s
            o += f'<path d="M{cx:.0f} {cy:.0f} Q{fx:.0f} {fy-20*s:.0f} {fx+8*s:.0f} {fy:.0f}" stroke="#8fbf52" stroke-width="{4*s:.1f}" fill="none"/>'
            o += f'<circle cx="{fx+8*s:.0f}" cy="{fy+4*s:.0f}" r="{6*s:.1f}" fill="none" stroke="#9fcf60" stroke-width="{3*s:.1f}"/>'
        return o
    b += clump(170, 380, .55, cols_far, 9) + clump(800, 400, .6, cols_far, 9)
    b += clump(480, 470, 1.15, cols_main, 16)
    # glowing spores / light motes
    for i in range(25):
        b += f'<circle cx="{rnd.uniform(0,960):.0f}" cy="{rnd.uniform(0,400):.0f}" r="{rnd.uniform(1,2.5):.1f}" fill="#f1f7b8" opacity="{rnd.uniform(.3,.8):.2f}"/>'
    return svg(b, d)


# ---------------------------------------------------------------- 4 beach rocks
def beach_rocks():
    rnd = random.Random(4)
    d = lg('sea', [(0, '#1d6f7a'), (.6, '#2fa6a0'), (1, '#6fd6c4')]) + lg('sand2', [(0, '#d9c99a'), (1, '#c4ae78')])
    d += lg('sky2', [(0, '#a7d4c8'), (1, '#e4efd8')])
    b = '<rect width="960" height="160" fill="url(#sky2)"/>'
    # wroshyr silhouettes
    for x, w, h in [(40, 70, 160), (150, 40, 130), (780, 90, 170), (900, 50, 140)]:
        b += f'<rect x="{x}" y="{160-h}" width="{w}" height="{h}" fill="#3d5a44" opacity=".75"/>'
        b += f'<ellipse cx="{x+w/2}" cy="{160-h}" rx="{w*1.6}" ry="{w*.6}" fill="#4c7451" opacity=".8"/>'
    b += '<rect y="150" width="960" height="250" fill="url(#sea)"/>'
    for i in range(12):
        y = 170 + i * 20
        b += f'<path d="M{rnd.uniform(-50,200):.0f} {y} q60 -6 120 0 t120 0 t120 0" stroke="#bff2e6" stroke-width="1.5" fill="none" opacity=".35"/>'
    b += '<path d="M0 360 Q200 340 420 372 T960 352 L960 640 L0 640Z" fill="url(#sand2)"/>'
    b += '<path d="M0 360 Q200 340 420 372 T960 352" stroke="#f4fbf2" stroke-width="7" fill="none" opacity=".8"/>'
    b += '<path d="M0 372 Q200 352 420 384 T960 364" stroke="#9ec6b3" stroke-width="5" fill="none" opacity=".5"/>'
    for i in range(80):
        b += f'<circle cx="{rnd.uniform(0,960):.0f}" cy="{rnd.uniform(390,640):.0f}" r="{rnd.uniform(1,3):.1f}" fill="#8f7d58" opacity=".5"/>'
    # basalt: columnar hex tops + boulders
    def basalt_cluster(cx, cy, n, s):
        o = ell_shadow(cx + 20, cy + 30, 60 * s * n ** .5, 22 * s, .45)
        cols = []
        for i in range(n):
            cols.append((cx + rnd.uniform(-1, 1) * 40 * s * n ** .4, cy + rnd.uniform(-1, 1) * 18 * s, rnd.uniform(30, 90) * s))
        for x, y, h in sorted(cols, key=lambda t: t[1]):
            r = 22 * s
            hexp = lambda yy: ' '.join(f'{x+math.cos(math.pi/3*k)*r:.1f},{yy+math.sin(math.pi/3*k)*r*.5:.1f}' for k in range(6))
            o += f'<polygon points="{x-r:.1f},{y-h:.1f} {x-r:.1f},{y:.1f} {x-r/2:.1f},{y+r*.43:.1f} {x+r/2:.1f},{y+r*.43:.1f} {x+r:.1f},{y:.1f} {x+r:.1f},{y-h:.1f}" fill="#2b2f36" filter="url(#stone)"/>'
            o += f'<polygon points="{x-r:.1f},{y-h:.1f} {x-r:.1f},{y:.1f} {x-r/2:.1f},{y+r*.43:.1f} {x-r/2:.1f},{y-h+r*.43:.1f}" fill="#454b55"/>'
            o += f'<polygon points="{hexp(y-h)}" fill="#5c636e"/>'
            o += f'<polygon points="{hexp(y-h)}" fill="none" stroke="#7d8692" stroke-width="1.5"/>'
        return o
    b += basalt_cluster(150, 470, 5, 1.0) + basalt_cluster(760, 520, 7, 1.15) + basalt_cluster(470, 600, 3, .8)
    b += rock(330, 440, 34, rnd, '#30353c', '#59606b', '#1d2026') + rock(600, 430, 24, rnd, '#30353c', '#59606b', '#1d2026')
    b += rock(900, 450, 40, rnd, '#30353c', '#59606b', '#1d2026')
    # tide foam at rock bases
    return svg(b, d)


# ---------------------------------------------------------------- 5 fungus stalks
def fungus_stalks():
    rnd = random.Random(5)
    d = rg('cave', [(0, '#3a3140', 1), (1, '#110e15', 1)], .5, .55, .75) + rg('bio', [(0, '#b9f3ff', .8), (1, '#b9f3ff', 0)])
    d += lg('stalk', [(0, '#e9e2cf'), (1, '#b8ad96')], 1, 0) + rg('cap', [(0, '#f6efe0', 1), (.7, '#d8ccb3', 1), (1, '#a99c84', 1)], .4, .3, .7)
    b = '<rect width="960" height="640" fill="url(#cave)"/>'
    for i in range(30):  # cave rock blotches
        b += f'<ellipse cx="{rnd.uniform(0,960):.0f}" cy="{rnd.uniform(0,640):.0f}" rx="{rnd.uniform(30,120):.0f}" ry="{rnd.uniform(10,40):.0f}" fill="{rnd.choice(["#2a232e","#1a161e","#3a3040"])}" opacity=".6" filter="url(#blur6)"/>'
    b += '<path d="M0 420 Q300 380 620 430 T960 410 L960 640 L0 640Z" fill="#241d27"/>'
    b += '<path d="M0 0 L960 0 L960 60 Q800 120 640 70 Q500 140 380 80 Q220 130 120 70 Q60 100 0 80Z" fill="#0d0a10"/>'
    def mushroom(x, y, h, w, lean):
        o = f'<ellipse cx="{x}" cy="{y}" rx="{w*1.4:.0f}" ry="{w*.35:.0f}" fill="#000" opacity=".4" filter="url(#blur6)"/>'
        tx = x + lean
        o += f'<path d="M{x-w*.22:.1f} {y} Q{x+lean*.3-w*.3:.1f} {y-h*.5:.1f} {tx-w*.14:.1f} {y-h:.1f} L{tx+w*.14:.1f} {y-h:.1f} Q{x+lean*.3+w*.3:.1f} {y-h*.5:.1f} {x+w*.22:.1f} {y}Z" fill="url(#stalk)"/>'
        # ring
        o += f'<ellipse cx="{x+lean*.6:.1f}" cy="{y-h*.62:.1f}" rx="{w*.24:.1f}" ry="{w*.07:.1f}" fill="#d9cfb8"/>'
        # cap (conical/bell)
        o += f'<path d="M{tx-w*.6:.1f} {y-h+w*.12:.1f} Q{tx-w*.5:.1f} {y-h-w*.6:.1f} {tx:.1f} {y-h-w*.7:.1f} Q{tx+w*.5:.1f} {y-h-w*.6:.1f} {tx+w*.6:.1f} {y-h+w*.12:.1f} Q{tx:.1f} {y-h-w*.05:.1f} {tx-w*.6:.1f} {y-h+w*.12:.1f}Z" fill="url(#cap)"/>'
        for k in range(5):
            gx = tx - w * .4 + k * w * .2
            o += f'<line x1="{gx:.1f}" y1="{y-h+w*.05:.1f}" x2="{tx+(gx-tx)*.6:.1f}" y2="{y-h-w*.3:.1f}" stroke="#a89a80" stroke-width="1" opacity=".6"/>'
        # bioluminescent gill glow
        o += f'<ellipse cx="{tx:.1f}" cy="{y-h+w*.08:.1f}" rx="{w*.55:.1f}" ry="{w*.12:.1f}" fill="#9be8ff" opacity=".55" filter="url(#blur2)"/>'
        o += f'<circle cx="{tx:.1f}" cy="{y-h:.1f}" r="{w*1.1:.1f}" fill="url(#bio)" opacity=".25"/>'
        return o
    clusters = [(250, 470, 1.0), (680, 500, 1.2), (470, 590, .7), (90, 560, .6), (880, 590, .65)]
    for cx, cy, s in clusters:
        items = [(cx + rnd.uniform(-60, 60) * s, cy + rnd.uniform(-10, 25) * s, rnd.uniform(60, 170) * s, rnd.uniform(28, 55) * s, rnd.uniform(-25, 25)) for _ in range(int(5 + 3 * s))]
        for it in sorted(items, key=lambda t: t[1]):
            b += mushroom(*it)
        for k in range(8):  # small buttons
            x, y = cx + rnd.uniform(-90, 90) * s, cy + rnd.uniform(5, 35) * s
            b += f'<ellipse cx="{x:.0f}" cy="{y:.0f}" rx="{6*s:.1f}" ry="{4*s:.1f}" fill="#d8ccb3"/>'
    for i in range(70):
        b += f'<circle cx="{rnd.uniform(0,960):.0f}" cy="{rnd.uniform(60,560):.0f}" r="{rnd.uniform(.8,2.2):.1f}" fill="#c9f6ff" opacity="{rnd.uniform(.2,.7):.2f}"/>'
    return svg(b, d)


# ---------------------------------------------------------------- shared Sullust backdrop
def sullust_bg(rnd, horizon=230):
    d = lg('ssky', [(0, '#3b2a2e'), (.6, '#7a4a3a'), (1, '#c46a3a')]) + lg('ash', [(0, '#5a5452'), (1, '#3a3534')])
    b = f'<rect width="960" height="{horizon+20}" fill="url(#ssky)"/>'
    b += f'<path d="M0 {horizon} L120 {horizon-70} L190 {horizon-40} L300 {horizon-120} L360 {horizon-110} L470 {horizon-30} L620 {horizon-90} L700 {horizon-60} L820 {horizon-140} L870 {horizon-130} L960 {horizon-50} L960 {horizon+10} L0 {horizon+10}Z" fill="#2c2426"/>'
    b += f'<path d="M300 {horizon-120} L360 {horizon-110} L345 {horizon-95} L320 {horizon-100}Z" fill="#ff7a2a" opacity=".8"/>'
    b += f'<ellipse cx="330" cy="{horizon-150}" rx="90" ry="40" fill="#544248" opacity=".7" filter="url(#blur14)"/>'
    b += f'<ellipse cx="840" cy="{horizon-170}" rx="110" ry="45" fill="#544248" opacity=".6" filter="url(#blur14)"/>'
    b += f'<rect y="{horizon}" width="960" height="{640-horizon}" fill="url(#ash)"/>'
    for i in range(120):
        b += f'<ellipse cx="{rnd.uniform(0,960):.0f}" cy="{rnd.uniform(horizon,640):.0f}" rx="{rnd.uniform(4,20):.0f}" ry="{rnd.uniform(1.5,5):.0f}" fill="{rnd.choice(["#6a6360","#2e2a29","#4c4645"])}" opacity=".6"/>'
    return b, d


def ash_motes(rnd, n=60):
    return ''.join(f'<circle cx="{rnd.uniform(0,960):.0f}" cy="{rnd.uniform(0,640):.0f}" r="{rnd.uniform(.8,2):.1f}" fill="#d8cfc8" opacity="{rnd.uniform(.2,.6):.2f}"/>' for _ in range(n))


def dome(cx, cy, rx, ry, base, light, dark, bands=3):
    o = ell_shadow(cx + rx * .15, cy + 6, rx * 1.15, ry * .25, .5)
    o += f'<path d="M{cx-rx} {cy} A{rx} {ry} 0 0 1 {cx+rx} {cy}Z" fill="{base}" filter="url(#stone)"/>'
    o += f'<path d="M{cx-rx} {cy} A{rx} {ry} 0 0 1 {cx-rx*.1} {cy-ry*.99} A{rx*.7} {ry} 0 0 0 {cx-rx*.55} {cy}Z" fill="{light}" opacity=".55"/>'
    o += f'<path d="M{cx+rx} {cy} A{rx} {ry} 0 0 0 {cx+rx*.35} {cy-ry*.9} A{rx*.8} {ry} 0 0 1 {cx+rx*.55} {cy}Z" fill="{dark}" opacity=".5"/>'
    for k in range(1, bands + 1):
        t = k / (bands + 1)
        ryy = ry * (1 - t)
        rxx = rx * math.sqrt(1 - t * t) if False else rx * (1 - t * t) ** .5
        o += f'<path d="M{cx-rxx:.1f} {cy-ry*t:.1f} Q{cx:.1f} {cy-ry*t+ry*.08:.1f} {cx+rxx:.1f} {cy-ry*t:.1f}" stroke="{dark}" stroke-width="3" fill="none" opacity=".7"/>'
    return o


# ---------------------------------------------------------------- 6 hot-spring bathhouse
def bathhouse():
    rnd = random.Random(6)
    b, d = sullust_bg(rnd)
    d += rg('pool', [(0, '#9ff2e6', 1), (.6, '#3fb7b0', 1), (1, '#1f6d74', 1)]) + lg('wallb', [(0, '#7a6f6a'), (1, '#4f4643')])
    d += rg('warm', [(0, '#ffb86a', 1), (1, '#ff7a2a', .0)])
    # building: drum base + big dome + small side domes
    b += ell_shadow(380, 470, 260, 40, .5)
    b += '<rect x="170" y="330" width="420" height="140" fill="url(#wallb)" filter="url(#stone)"/>'
    b += '<rect x="170" y="330" width="420" height="16" fill="#8d837d"/>'
    b += dome(380, 335, 190, 150, '#6e6460', '#a39892', '#3a3331', 4)
    b += '<rect x="360" y="170" width="40" height="18" rx="4" fill="#4a403d"/><ellipse cx="380" cy="170" rx="26" ry="8" fill="#5a4f4b"/>'
    b += dome(175, 345, 55, 50, '#6e6460', '#a39892', '#3a3331', 1) + dome(585, 345, 55, 50, '#6e6460', '#a39892', '#3a3331', 1)
    # round door + porthole windows, warm interior light
    b += '<path d="M340 470 L340 410 A40 40 0 0 1 420 410 L420 470Z" fill="#2a1d18"/><path d="M350 470 L350 412 A30 30 0 0 1 410 412 L410 470Z" fill="#ffad5e" opacity=".85"/>'
    b += '<path d="M340 470 L340 410 A40 40 0 0 1 420 410 L420 470" stroke="#9a8f88" stroke-width="7" fill="none"/>'
    for x in (230, 290, 470, 530):
        b += f'<circle cx="{x}" cy="395" r="17" fill="#ffb86a"/><circle cx="{x}" cy="395" r="17" fill="none" stroke="#9a8f88" stroke-width="5"/><circle cx="{x}" cy="395" r="40" fill="url(#warm)" opacity=".25"/>'
    b += '<rect x="330" y="470" width="100" height="12" fill="#5c5350"/><rect x="320" y="482" width="120" height="12" fill="#6a605c"/>'
    # pool
    b += ell_shadow(760, 520, 170, 30, .4)
    b += '<ellipse cx="760" cy="500" rx="175" ry="78" fill="#3b3534"/>'
    for k in range(18):  # rim stones
        a = k / 18 * math.tau
        b += f'<ellipse cx="{760+math.cos(a)*170:.0f}" cy="{500+math.sin(a)*74:.0f}" rx="22" ry="12" fill="{rnd.choice(["#6e6460","#5a514e","#7f7570"])}"/>'
    b += '<ellipse cx="760" cy="500" rx="150" ry="62" fill="url(#pool)"/>'
    for k in range(5):
        b += f'<ellipse cx="{760+rnd.uniform(-60,60):.0f}" cy="{500+rnd.uniform(-20,20):.0f}" rx="{rnd.uniform(20,50):.0f}" ry="{rnd.uniform(6,12):.0f}" fill="none" stroke="#d6fff8" stroke-width="2" opacity=".5"/>'
    # steam
    for k in range(9):
        x = 680 + k * 20 + rnd.uniform(-10, 10)
        b += f'<ellipse cx="{x:.0f}" cy="{430-k%3*50:.0f}" rx="{rnd.uniform(40,70):.0f}" ry="{rnd.uniform(40,80):.0f}" fill="#f2ece8" opacity=".22" filter="url(#blur14)"/>'
    # path (signal) to door
    b += '<path d="M330 494 L430 494 L470 640 L290 640Z" fill="#7a716c" opacity=".55"/>'
    b += ash_motes(rnd)
    return svg(b, d)


# ---------------------------------------------------------------- 7 Sullustan home
def sullustan_home():
    rnd = random.Random(7)
    b, d = sullust_bg(rnd, 180)
    d += rg('warm', [(0, '#ffc27a', 1), (1, '#ff8a3a', 0)]) + lg('slope', [(0, '#3d3533'), (1, '#262020')])
    # slope rising to the right/back
    b += '<path d="M0 330 Q250 250 520 230 Q760 210 960 160 L960 640 L0 640Z" fill="url(#slope)" filter="url(#rough)"/>'
    for i in range(14):
        b += f'<path d="M{rnd.uniform(0,960):.0f} {rnd.uniform(240,400):.0f} l{rnd.uniform(30,90):.0f} {rnd.uniform(-10,10):.0f}" stroke="#4f4542" stroke-width="3" opacity=".6"/>'
    # house: half-dome bulging out of slope
    b += ell_shadow(470, 470, 240, 34, .55)
    b += '<path d="M240 470 Q235 300 470 270 Q705 300 700 470Z" fill="#5c514d" filter="url(#stone)"/>'
    b += '<path d="M240 470 Q235 300 470 270 Q380 320 360 470Z" fill="#8a7e78" opacity=".45"/>'
    b += '<path d="M700 470 Q705 300 470 270 Q600 330 600 470Z" fill="#2e2725" opacity=".45"/>'
    # slope covering back of roof (built into hill)
    b += '<path d="M300 300 Q470 240 650 290 Q760 250 960 200 L960 230 Q760 300 660 320 Q470 280 300 330Z" fill="#2c2524" opacity=".9"/>'
    # stone course lines
    for k in range(4):
        y = 330 + k * 35
        b += f'<path d="M{250+k*3} {y} Q470 {y-14} {690-k*3} {y}" stroke="#3a3230" stroke-width="2.5" fill="none" opacity=".7"/>'
    # round door with lintel, porthole windows (Sullustan big-eye motif)
    b += '<circle cx="470" cy="430" r="52" fill="#3c3330"/><circle cx="470" cy="430" r="42" fill="#5a3b28"/>'
    b += '<rect x="418" y="430" width="104" height="44" fill="#5c514d"/><circle cx="470" cy="430" r="42" fill="none" stroke="#a0948d" stroke-width="6" stroke-dasharray="14 4"/>'
    b += '<rect x="440" y="420" width="60" height="54" fill="#5a3b28"/><line x1="470" y1="400" x2="470" y2="474" stroke="#3c2a1c" stroke-width="3"/>'
    for x, y, r in [(330, 380, 26), (610, 380, 26), (395, 330, 16), (545, 330, 16)]:
        b += f'<circle cx="{x}" cy="{y}" r="{r+8}" fill="#776c66"/><circle cx="{x}" cy="{y}" r="{r}" fill="#ffbf74"/><circle cx="{x-r*.3:.0f}" cy="{y-r*.3:.0f}" r="{r*.3:.0f}" fill="#fff0c8" opacity=".7"/><circle cx="{x}" cy="{y}" r="{r*2.6:.0f}" fill="url(#warm)" opacity=".25"/>'
    # vent pipe and antenna
    b += '<rect x="560" y="250" width="22" height="50" fill="#6a605c"/><ellipse cx="571" cy="250" rx="16" ry="6" fill="#7d736e"/>'
    b += '<ellipse cx="575" cy="220" rx="28" ry="22" fill="#cfc8c4" opacity=".25" filter="url(#blur14)"/>'
    b += '<line x1="380" y1="290" x2="380" y2="230" stroke="#8d837d" stroke-width="3"/><circle cx="380" cy="228" r="4" fill="#ff5a3a"/>'
    # steps + path
    b += '<path d="M420 474 L520 474 L540 490 L400 490Z" fill="#6e6460"/><path d="M400 490 L540 490 L600 640 L340 640Z" fill="#5f5856" opacity=".7"/>'
    b += rock(170, 520, 36, rnd, '#3a3332', '#655b58', '#211c1b') + rock(780, 500, 30, rnd, '#3a3332', '#655b58', '#211c1b')
    b += ash_motes(rnd)
    return svg(b, d)


# ---------------------------------------------------------------- glass greenhouse dome
def glass_dome(cx, cy, rx, ry, rnd, ribs=7, plants=True):
    o = ell_shadow(cx + rx * .1, cy + 8, rx * 1.15, ry * .22, .5)
    o += f'<ellipse cx="{cx}" cy="{cy}" rx="{rx+8}" ry="{ry*.18+6:.1f}" fill="#4a4442"/>'
    o += f'<path d="M{cx-rx} {cy} A{rx} {ry} 0 0 1 {cx+rx} {cy}Z" fill="#9fd4c4" opacity=".35"/>'
    if plants:
        for i in range(int(rx / 6)):
            px = cx + rnd.uniform(-.8, .8) * rx
            ph = rnd.uniform(.2, .6) * ry * (1 - abs(px - cx) / rx)
            col = rnd.choice(['#3f7a3a', '#5f9a3e', '#7fb24a', '#2f5f34'])
            o += f'<ellipse cx="{px:.0f}" cy="{cy-ph/2:.0f}" rx="{rnd.uniform(8,20)*rx/150:.1f}" ry="{ph/2+4:.1f}" fill="{col}" opacity=".9"/>'
        for i in range(int(rx / 12)):
            px = cx + rnd.uniform(-.7, .7) * rx
            o += f'<circle cx="{px:.0f}" cy="{cy-rnd.uniform(.1,.4)*ry:.0f}" r="{3*rx/150+1:.1f}" fill="{rnd.choice(["#ffd36a","#ff8a6a","#e8f08a"])}"/>'
    o += f'<path d="M{cx-rx} {cy} A{rx} {ry} 0 0 1 {cx+rx} {cy}Z" fill="#cfeee6" opacity=".18"/>'
    for k in range(1, ribs):
        t = -1 + 2 * k / ribs
        o += f'<path d="M{cx+t*rx:.1f} {cy} Q{cx+t*rx*1.05:.1f} {cy-ry*.9:.1f} {cx:.1f} {cy-ry:.1f}" stroke="#5e6a6a" stroke-width="{2.5*rx/150+1:.1f}" fill="none"/>'
    for k in (1, 2):
        t = k / 3
        rxx = rx * (1 - t * t) ** .5
        o += f'<path d="M{cx-rxx:.1f} {cy-ry*t:.1f} Q{cx:.1f} {cy-ry*t+ry*.1:.1f} {cx+rxx:.1f} {cy-ry*t:.1f}" stroke="#5e6a6a" stroke-width="{2*rx/150+1:.1f}" fill="none"/>'
    o += f'<path d="M{cx-rx} {cy} A{rx} {ry} 0 0 1 {cx+rx} {cy}" stroke="#6f7b7b" stroke-width="{3*rx/150+1.5:.1f}" fill="none"/>'
    # specular highlight
    o += f'<path d="M{cx-rx*.7:.1f} {cy-ry*.35:.1f} Q{cx-rx*.55:.1f} {cy-ry*.85:.1f} {cx-rx*.1:.1f} {cy-ry*.95:.1f}" stroke="#ffffff" stroke-width="{6*rx/150+2:.1f}" fill="none" opacity=".45" stroke-linecap="round"/>'
    o += f'<path d="M{cx-rx*.12:.1f} {cy} L{cx-rx*.12:.1f} {cy-ry*.25:.1f} L{cx+rx*.12:.1f} {cy-ry*.25:.1f} L{cx+rx*.12:.1f} {cy}Z" fill="#6f7b7b"/>'
    return o


# ---------------------------------------------------------------- 8 ash farm
def ash_farm():
    rnd = random.Random(8)
    b, d = sullust_bg(rnd, 200)
    d += rg('warm', [(0, '#ffc27a', 1), (1, '#ff8a3a', 0)])
    # furrowed ash fields
    for i in range(10):
        y = 470 + i * 18
        b += f'<path d="M0 {y} Q480 {y-20} 960 {y}" stroke="#2c2827" stroke-width="7" fill="none" opacity=".7"/>'
        for k in range(16):
            x = rnd.uniform(0, 960)
            b += f'<path d="M{x:.0f} {y-2} l-4 -10 M{x:.0f} {y-2} l4 -11 M{x:.0f} {y-2} l0 -13" stroke="{rnd.choice(["#7c8a4a","#9aa25a","#6a7a3e"])}" stroke-width="2"/>'
    # low stone farmhouse (flat, rounded roof slab, long)
    b += ell_shadow(330, 420, 230, 30, .55)
    b += '<path d="M120 420 L120 330 Q120 310 140 310 L520 310 Q540 310 540 330 L540 420Z" fill="#5f5552" filter="url(#stone)"/>'
    b += '<path d="M105 318 Q105 282 150 280 L510 280 Q555 282 555 318 Z" fill="#7a706b"/><path d="M105 318 L555 318 L555 330 L105 330Z" fill="#3c3533"/>'
    b += '<path d="M150 280 L510 280 Q540 282 548 300 L130 300 Q135 282 150 280Z" fill="#9a908a" opacity=".5"/>'
    for k in range(6):
        b += f'<line x1="{140+k*72}" y1="330" x2="{140+k*72}" y2="420" stroke="#463e3b" stroke-width="2"/>'
    for x in (170, 250, 420, 490):
        b += f'<rect x="{x}" y="352" width="34" height="26" rx="8" fill="#ffbf74"/><rect x="{x}" y="352" width="34" height="26" rx="8" fill="none" stroke="#8d837d" stroke-width="4"/><circle cx="{x+17}" cy="365" r="40" fill="url(#warm)" opacity=".2"/>'
    b += '<rect x="315" y="345" width="56" height="75" rx="6" fill="#4a3324"/><rect x="315" y="345" width="56" height="75" rx="6" fill="none" stroke="#8d837d" stroke-width="5"/>'
    b += '<rect x="300" y="420" width="86" height="10" fill="#6e6460"/>'
    # water tank and moisture tower
    b += '<rect x="60" y="300" width="48" height="120" rx="10" fill="#6a605c"/><ellipse cx="84" cy="300" rx="24" ry="8" fill="#857a75"/>'
    b += '<line x1="84" y1="300" x2="84" y2="250" stroke="#8d837d" stroke-width="4"/><path d="M70 262 L98 262 M74 274 L94 274" stroke="#8d837d" stroke-width="3"/>'
    # greenhouse dome attached right
    b += '<rect x="540" y="370" width="60" height="40" fill="#5f5552"/>'
    b += glass_dome(720, 425, 150, 130, rnd)
    # path to door
    b += '<path d="M310 430 L376 430 L420 640 L260 640Z" fill="#6a6360" opacity=".7"/>'
    b += ash_motes(rnd)
    return svg(b, d)


# ---------------------------------------------------------------- 9 ash greenhouse close
def ash_greenhouse():
    rnd = random.Random(9)
    b, d = sullust_bg(rnd, 240)
    b += glass_dome(480, 500, 300, 290, rnd, ribs=9)
    # planter rows visible at base inside
    for k in range(5):
        b += f'<rect x="{240+k*100}" y="480" width="80" height="16" rx="3" fill="#5a3b28" opacity=".85"/>'
    # irrigation pipe + valve
    b += '<path d="M780 500 L860 500 L860 440 L900 440" stroke="#7d736e" stroke-width="10" fill="none"/><circle cx="860" cy="470" r="9" fill="#c04a2a"/>'
    b += '<rect x="880" y="380" width="50" height="120" rx="10" fill="#6a605c"/>'
    # condensation drips
    for i in range(30):
        a = rnd.uniform(math.pi * 1.05, math.pi * 1.95)
        x, y = 480 + math.cos(a) * 285, 500 + math.sin(a) * 275
        b += f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{rnd.uniform(1.5,3):.1f}" fill="#e8fffa" opacity=".6"/>'
    b += ash_motes(rnd, 90)
    return svg(b, d)


# ---------------------------------------------------------------- 10 Tython standing stones
def tython_stones():
    rnd = random.Random(10)
    d = lg('tsky', [(0, '#1d1f45'), (.55, '#5a4a86'), (1, '#e3a77a')]) + lg('grass', [(0, '#4f6b48'), (1, '#2f4430')])
    d += rg('glow', [(0, '#e6fbff', 1), (.25, '#8fd6ff', .8), (1, '#4a8fff', 0)])
    d += lg('stoneg', [(0, '#a8a395'), (1, '#6b675d')], 1, 0)
    b = '<rect width="960" height="300" fill="url(#tsky)"/>'
    for i in range(70):
        b += f'<circle cx="{rnd.uniform(0,960):.0f}" cy="{rnd.uniform(0,170):.0f}" r="{rnd.uniform(.6,1.6):.1f}" fill="#fff" opacity="{rnd.uniform(.3,.9):.2f}"/>'
    b += '<circle cx="180" cy="90" r="34" fill="#e8e4d8" opacity=".9"/><circle cx="192" cy="84" r="30" fill="#3a3a6a" opacity=".55"/>'
    # distant hills + sea
    b += '<path d="M0 270 Q160 220 330 250 T700 235 T960 255 L960 300 L0 300Z" fill="#3b3f5e"/>'
    b += '<rect y="290" width="960" height="40" fill="#5b6a8e"/>'
    b += '<path d="M0 320 Q480 280 960 320 L960 640 L0 640Z" fill="url(#grass)"/>'
    for i in range(260):
        x, y = rnd.uniform(0, 960), rnd.uniform(320, 640)
        b += f'<path d="M{x:.0f} {y:.0f} l{rnd.uniform(-3,3):.0f} -{rnd.uniform(5,12):.0f}" stroke="{rnd.choice(["#6f8f5e","#3e5a3c","#86a46e"])}" stroke-width="2"/>'
    cx, cy, R, ry = 480, 470, 300, 110
    # glow on ground
    b += f'<ellipse cx="{cx}" cy="{cy}" rx="170" ry="60" fill="url(#glow)" opacity=".7"/>'
    b += f'<ellipse cx="{cx}" cy="{cy}" rx="{R*.75:.0f}" ry="{ry*.75:.0f}" fill="none" stroke="#b9b2a0" stroke-width="10" opacity=".55"/>'
    for k in range(8):  # inlaid paving rays
        a = k / 8 * math.tau
        b += f'<line x1="{cx+math.cos(a)*60:.0f}" y1="{cy+math.sin(a)*22:.0f}" x2="{cx+math.cos(a)*R*.7:.0f}" y2="{cy+math.sin(a)*ry*.7:.0f}" stroke="#a9a290" stroke-width="5" opacity=".5"/>'
    stones = []
    for k in range(9):
        a = k / 9 * math.tau + .2
        stones.append((cx + math.cos(a) * R, cy + math.sin(a) * ry, a))
    def stone(x, y, a):
        s = .7 + .3 * (y - (cy - ry)) / (2 * ry)
        h, w = 150 * s * rnd.uniform(.85, 1.1), 46 * s
        o = ell_shadow(x + w * .5, y + 4, w * 1.2, 10 * s, .5)
        o += f'<path d="M{x-w/2:.1f} {y} L{x-w/2+3:.1f} {y-h*.85:.1f} Q{x:.1f} {y-h-8*s:.1f} {x+w/2-3:.1f} {y-h*.82:.1f} L{x+w/2:.1f} {y}Z" fill="url(#stoneg)" filter="url(#stone)"/>'
        o += f'<path d="M{x-w/2:.1f} {y} L{x-w/2+3:.1f} {y-h*.85:.1f} Q{x-w*.2:.1f} {y-h:.1f} {x-w*.1:.1f} {y-h*.9:.1f} L{x-w*.15:.1f} {y}Z" fill="#c9c4b4" opacity=".4"/>'
        # glowing carved glyph facing centre (Je'daii balance mark)
        gy = y - h * .55
        o += f'<circle cx="{x:.1f}" cy="{gy:.1f}" r="{9*s:.1f}" fill="none" stroke="#9fe4ff" stroke-width="{2.5*s:.1f}"/>'
        o += f'<line x1="{x:.1f}" y1="{gy-16*s:.1f}" x2="{x:.1f}" y2="{gy+16*s:.1f}" stroke="#9fe4ff" stroke-width="{2.5*s:.1f}"/>'
        o += f'<circle cx="{x:.1f}" cy="{gy:.1f}" r="{18*s:.1f}" fill="#8fd6ff" opacity=".25" filter="url(#blur6)"/>'
        # moss cap
        o += f'<ellipse cx="{x-w*.1:.1f}" cy="{y-h*.86:.1f}" rx="{w*.35:.1f}" ry="{5*s:.1f}" fill="#5d7a4a" opacity=".8"/>'
        return o
    back = [s for s in stones if s[1] < cy]; front = [s for s in stones if s[1] >= cy]
    for s in sorted(back, key=lambda t: t[1]):
        b += stone(*s)
    # central glowing stone / light column
    b += f'<ellipse cx="{cx}" cy="{cy-110}" rx="40" ry="170" fill="#9fdcff" opacity=".25" filter="url(#blur14)"/>'
    b += f'<path d="M{cx-26} {cy} L{cx-18} {cy-70} L{cx} {cy-95} L{cx+18} {cy-70} L{cx+26} {cy}Z" fill="#cfefff"/>'
    b += f'<path d="M{cx} {cy-95} L{cx+18} {cy-70} L{cx+26} {cy} L{cx} {cy}Z" fill="#8fc8ef"/>'
    b += f'<circle cx="{cx}" cy="{cy-50}" r="80" fill="url(#glow)" opacity=".6"/>'
    for i in range(30):
        a = rnd.uniform(0, math.tau); r = rnd.uniform(20, 150)
        b += f'<circle cx="{cx+math.cos(a)*r:.0f}" cy="{cy-60+math.sin(a)*r*.6:.0f}" r="{rnd.uniform(1,2.5):.1f}" fill="#e6fbff" opacity="{rnd.uniform(.4,.9):.2f}"/>'
    for s in sorted(front, key=lambda t: t[1]):
        b += stone(*s)
    return svg(b, d)


ITEMS = {
    'tatooine/desert-scrub': desert_scrub,
    'tatooine/office-tower-floors': office_tower,
    'kashyyyk/fern-clump': fern_clump,
    'kashyyyk/beach-rocks': beach_rocks,
    'sullust/fungus-stalks': fungus_stalks,
    'sullust/hot-spring-bathhouse': bathhouse,
    'sullust/sullustan-home': sullustan_home,
    'sullust/ash-farm': ash_farm,
    'sullust/ash-greenhouse': ash_greenhouse,
    'grand-arena/tython-standing-stones': tython_stones,
}

if __name__ == '__main__':
    for k, fn in ITEMS.items():
        open(f"{OUT}/{k.replace('/', '__')}.svg", 'w').write(fn())
    print('ok', len(ITEMS))
