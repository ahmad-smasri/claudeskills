"""Trace every leader on one RDC screen and write it up for reading by eye.

Writes three things beside each other:

  * the annotated screen - every widget boxed and numbered, every leader's far
    end ringed in red where it landed on a dot and orange where the walk ran
    out, and every dot nobody claimed ringed in blue;
  * the endpoint JSON;
  * a strip of the tag printed above each widget, in the same numbering, so the
    reading is `number -> tag -> room` rather than a guess at which widget the
    number belongs to.

One dot serves one unit. Where two widgets walk to the same dot the shorter
walk keeps it and the loser re-walks with that dot withheld, because the longer
walk is the one that has most likely wandered onto a neighbour's leader.
"""
import json
import sys

import numpy as np
from PIL import Image, ImageDraw

import rdc_dots as D
import rdc_trace as T
import rdc_widgets as W

# Widgets sit outside the floor plan and dots inside it, so every real leader
# crosses the margin and no real one is short. Without this a walk that steps a
# few pixels into the widget's own printed tag and lands on the bowl of a
# letter counts as a reading - which is what it did for seven of the widgets
# along the top row, each 'serving' its own label.
MIN_WALK = 55

src, out, jsn = sys.argv[1], sys.argv[2], sys.argv[3]
im = Image.open(src).convert('RGB')
rgb = np.array(im, dtype=int)
grey = np.array(im.convert('L'), dtype=int)

m, dark = T.masks(grey)
dots = D.find(grey)
units = W.find(rgb, grey)

# a widget's own outline is stroke; blank it so no walk climbs its own border
for u in units:
    m[u['top'] - 3:u['bottom'] + 4, u['left'] - 3:u['right'] + 4] = False


def walk(u, banned):
    """the far end of the one real leader leaving a widget

    Left-hand widgets send their leader right of the slider and right-hand ones
    send it left of the bar, and the rows along the top and bottom send theirs
    vertically, so every side is tried and the walk that reaches a dot wins.
    """
    live = T.index([p for p in dots if p not in banned])
    starts = []
    for off in (3, 5, 7):
        for yy in range(u['y'] - 3, u['y'] + 4):
            if T._on(m, yy, u['right'] + off):
                starts.append((u['right'] + off, yy, 1, 0))
                break
        for yy in range(u['y'] - 3, u['y'] + 4):
            if T._on(m, yy, u['left'] - off):
                starts.append((u['left'] - off, yy, -1, 0))
                break
    for off in (5, 8, 11):
        for dy in (1, -1):
            edge = u['bottom'] + off if dy > 0 else u['top'] - off
            for xx in range(u['left'], u['right'] + 1):
                if T._on(m, edge, xx):
                    starts.append((xx, edge, 0, dy))
                    break
    best = None
    for sx, sy, dx, dy in starts:
        ex, ey, ondot = T.follow(m, dark, sx, sy, dx, dy, dots=live)
        far = abs(ex - sx) + abs(ey - sy)
        ondot = ondot and far >= MIN_WALK
        rank = (1 if ondot else 0, far)
        if best is None or rank > best[0]:
            best = (rank, ex, ey, ondot)
    if best is None:
        return None
    return {'end': (best[1], best[2]), 'dist': best[0][1], 'dot': best[3]}


got = [walk(u, set()) for u in units]
for _ in range(5):
    owner = {}
    for i, g in enumerate(got):
        if g and g['dot']:
            owner.setdefault(g['end'], []).append(i)
    clash = {p: v for p, v in owner.items() if len(v) > 1}
    if not clash:
        break
    for p, v in clash.items():
        v.sort(key=lambda i: got[i]['dist'])
        for i in v[1:]:
            taken = {got[j]['end'] for j in range(len(units))
                     if j != i and got[j] and got[j]['dot']}
            got[i] = walk(units[i], taken | {p})

d = ImageDraw.Draw(im)
recs, placed = [], []
for i, (u, g) in enumerate(zip(units, got), 1):
    d.rectangle([u['left'] - 3, u['top'] - 3, u['right'] + 3, u['bottom'] + 3],
                outline=(0, 140, 0), width=2)
    d.text((u['left'] - 26, u['y'] - 7), str(i), fill=(0, 120, 0))
    if g is None or g['dist'] < 12:
        recs.append({'n': i, 'at': [u['left'], u['right'], u['y']], 'end': None})
        continue
    ex, ey = g['end']
    recs.append({'n': i, 'at': [u['left'], u['right'], u['y']],
                 'end': [int(ex), int(ey)], 'dot': bool(g['dot']),
                 'dist': int(g['dist'])})
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

orig = Image.open(src).convert('RGB')
S, CW, CH = 2, 240, 26
sheet = Image.new('RGB', ((CW + 40) * S, (CH * S + 6) * max(len(units), 1)), 'white')
sd = ImageDraw.Draw(sheet)
for i, u in enumerate(units):
    x0 = max(0, u['left'] - 20)
    y0 = max(0, u['top'] - W.LABEL_UP - 2)
    sheet.paste(orig.crop((x0, y0, x0 + CW, y0 + CH)).resize((CW * S, CH * S),
                Image.LANCZOS), (40 * S, (CH * S + 6) * i + 3))
    sd.text((6, (CH * S + 6) * i + 18), '%d' % (i + 1), fill=(200, 0, 0))
sheet.save(out.replace('.png', '_tags.png'))
n = sum(1 for r in recs if r.get('dot'))
print('%-58s %2d widgets, %2d on a dot, %3d dots'
      % (out.split('/')[-1], len(units), n, len(dots)))
