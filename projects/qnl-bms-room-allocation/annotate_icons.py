"""Trace the leaders leaving the equipment icons, and strip their tags.

The fans, AHUs, DX units and CCUs are icons rather than slider bars, so
`annotate_qnl.py` does not see them. This does the same two jobs for them:
a numbered copy of the screen with each leader's endpoint marked, and one
strip of the tag printed above each icon, in the same order.
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
idx = Q.index(dots)

icons = I.find(a)
for k in icons:                      # an icon's own body is not leader
    m[k['top'] - 1:k['bottom'] + 2, k['left'] - 1:k['right'] + 2] = False
    ink[k['top'] - 1:k['bottom'] + 2, k['left'] - 1:k['right'] + 2] = False

im = Image.open(src).convert('RGB')
d = ImageDraw.Draw(im)
# One dot serves one unit, the same as on the slider screens: where two icons
# converge on a dot the shorter walk keeps it and the other goes round again
# without it.
def walk(k, banned):
    return I.leader(m, ink, k, dots=Q.index([p for p in dots if p not in banned]))


got = [walk(k, set()) for k in icons]
for _ in range(3):
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
            taken = {got[j]['end'] for j in range(len(icons))
                     if j != i and got[j] and got[j].get('dot')}
            got[i] = walk(icons[i], taken | {p})

recs, placed = [], []
for i, (k, g) in enumerate(zip(icons, got), 1):
    d.rectangle([k['left'] - 2, k['top'] - 2, k['right'] + 2, k['bottom'] + 2],
                outline=(0, 140, 0), width=2)
    d.text((k['left'] - 26, k['y'] - 7), str(i), fill=(0, 120, 0))
    if g is None:
        recs.append({'n': i, 'icon': [k['left'], k['right'], k['y']], 'end': None})
        continue
    ex, ey = g['end']
    recs.append({'n': i, 'icon': [k['left'], k['right'], k['y']],
                 'end': [int(ex), int(ey)], 'dot': bool(g['dot'])})
    col = (220, 0, 0) if g['dot'] else (255, 140, 0)
    d.ellipse([ex - 7, ey - 7, ex + 7, ey + 7], outline=col, width=3)
    lx, ly = ex + 9, ey - 6
    while any(abs(lx - px) < 20 and abs(ly - py) < 11 for px, py in placed):
        ly += 12
    placed.append((lx, ly))
    d.text((lx, ly), str(i), fill=col)
for x, y in dots:
    if (x, y) not in {tuple(r['end']) for r in recs if r.get('end')}:
        d.ellipse([x - 5, y - 5, x + 5, y + 5], outline=(0, 90, 220), width=2)
im.save(out)
json.dump(recs, open(jsn, 'w'), indent=1, default=int)

# the tag strip, same order
S, CW, CH = 2, 210, 24
sheet = Image.new('RGB', ((CW + 46) * S, (CH * S + 6) * max(len(icons), 1)), 'white')
sd = ImageDraw.Draw(sheet)
orig = Image.open(src).convert('RGB')
for i, k in enumerate(icons):
    box = (max(0, k['left'] - 60), max(0, k['top'] - 30),
           max(0, k['left'] - 60) + CW, max(0, k['top'] - 30) + CH)
    sheet.paste(orig.crop(box).resize((CW * S, CH * S), Image.LANCZOS),
                (46 * S, (CH * S + 6) * i + 3))
    sd.text((6, (CH * S + 6) * i + 16), '%d' % (i + 1), fill=(200, 0, 0))
sheet.save(out.replace('.png', '_tags.png'))
n = sum(1 for r in recs if r.get('dot'))
print('%s  %d icons, %d on a dot, %d dots' % (out, len(icons), n, len(dots)))
