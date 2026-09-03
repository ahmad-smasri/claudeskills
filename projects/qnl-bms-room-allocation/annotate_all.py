"""Trace every leader on a QNL screen - slider widgets and equipment icons -
against one pool of dots.

The two families were traced separately at first, which let a VAV and an
exhaust fan both claim the same dot: on BF-4 CAV-S14-001 and EF-B0007 came
back with the same endpoint, and only one of them can have walked it. One dot
serves one unit, so the claim has to be settled across both families at once.

Writes the annotated screen, the endpoint JSON, and one strip of the tag
printed above each unit in the same order - sliders first, then icons.
"""
import sys, json
from PIL import Image, ImageDraw
import trace as T
import qnl_trace as Q
import qnl_dots as D
import qnl_icons as I

src, out, jsn = sys.argv[1], sys.argv[2], sys.argv[3]
a = T.load(src)
m = Q.mask(a)
ink = Q.inked(a)
dots = D.find(a)

bars = sorted([w for w in T.find_widgets(a) if 60 < w['y'] < 770],
              key=lambda b: (b['left'], b['y']))
icons = I.find(a)
for w in bars:                    # a bar's own outline is stroke, not leader
    m[max(0, w['y'] - 9):w['y'] + 10, max(0, w['left'] - 1):w['right'] + 2] = False
    ink[max(0, w['y'] - 9):w['y'] + 10, max(0, w['left'] - 1):w['right'] + 2] = False
for k in icons:
    m[k['top'] - 1:k['bottom'] + 2, k['left'] - 1:k['right'] + 2] = False
    ink[k['top'] - 1:k['bottom'] + 2, k['left'] - 1:k['right'] + 2] = False

units = [('bar', w) for w in bars] + [('icon', k) for k in icons]


def walk(kind, u, banned):
    live = Q.index([p for p in dots if p not in banned])
    if kind == 'bar':
        return Q.leader(m, ink, u, dots=live)
    return I.leader(m, ink, u, dots=live)


got = [walk(k, u, set()) for k, u in units]
for _ in range(5):
    owner = {}
    for i, g in enumerate(got):
        if g and g.get('dot'):
            owner.setdefault(g['end'], []).append(i)
    clash = {p: v for p, v in owner.items() if len(v) > 1}
    if not clash:
        break
    for p, v in clash.items():
        v.sort(key=lambda i: got[i]['dist'])
        for i in v[1:]:
            taken = {got[j]['end'] for j in range(len(units))
                     if j != i and got[j] and got[j].get('dot')}
            got[i] = walk(units[i][0], units[i][1], taken | {p})

im = Image.open(src).convert('RGB')
d = ImageDraw.Draw(im)
recs, placed = [], []
for i, ((kind, u), g) in enumerate(zip(units, got), 1):
    box = ([u['left'] - 2, u['y'] - 9, u['right'] + 2, u['y'] + 9] if kind == 'bar'
           else [u['left'] - 2, u['top'] - 2, u['right'] + 2, u['bottom'] + 2])
    d.rectangle(box, outline=(0, 140, 0), width=2)
    d.text((u['left'] - 26, u['y'] - 7), str(i), fill=(0, 120, 0))
    if g is None or g['dist'] < 12:
        recs.append({'n': i, 'kind': kind, 'at': [u['left'], u['right'], u['y']],
                     'end': None})
        continue
    ex, ey = g['end']
    recs.append({'n': i, 'kind': kind, 'at': [u['left'], u['right'], u['y']],
                 'end': [int(ex), int(ey)], 'dot': bool(g['dot'])})
    col = (220, 0, 0) if g['dot'] else (255, 140, 0)
    d.ellipse([ex - 7, ey - 7, ex + 7, ey + 7], outline=col, width=3)
    lx, ly = ex + 9, ey - 6
    while any(abs(lx - px) < 20 and abs(ly - py) < 11 for px, py in placed):
        ly += 12
    placed.append((lx, ly))
    d.text((lx, ly), str(i), fill=col)
claimed = {tuple(r['end']) for r in recs if r.get('end')}
for x, y in dots:
    if (x, y) not in claimed:
        d.ellipse([x - 5, y - 5, x + 5, y + 5], outline=(0, 90, 220), width=2)
im.save(out)
json.dump(recs, open(jsn, 'w'), indent=1, default=int)

S, CW, CH = 2, 210, 24
sheet = Image.new('RGB', ((CW + 46) * S, (CH * S + 6) * max(len(units), 1)), 'white')
sd = ImageDraw.Draw(sheet)
orig = Image.open(src).convert('RGB')
for i, (kind, u) in enumerate(units):
    if kind == 'bar':
        x0, y0 = max(0, u['left'] - 24), max(0, u['y'] - 34)
    else:
        x0, y0 = max(0, u['left'] - 60), max(0, u['top'] - 30)
    sheet.paste(orig.crop((x0, y0, x0 + CW, y0 + CH)).resize((CW * S, CH * S),
                Image.LANCZOS), (46 * S, (CH * S + 6) * i + 3))
    sd.text((6, (CH * S + 6) * i + 16), '%d' % (i + 1), fill=(200, 0, 0))
sheet.save(out.replace('.png', '_tags.png'))
n = sum(1 for r in recs if r.get('dot'))
print('%s  %d units (%d bars, %d icons), %d on a dot, %d dots'
      % (out, len(units), len(bars), len(icons), n, len(dots)))
