"""Trace every leader on a QNL BMS screen and write a numbered copy to read.

The tracer only says where to look. Which room an endpoint landed in is a
question for the eye, on the annotated image, at a zoom where a marker sitting
on a wall and a marker sitting just inside a room look different.
"""
import sys, json
from PIL import Image, ImageDraw
import trace as T
import qnl_trace as Q
import qnl_dots as D

src, out, jsn = sys.argv[1], sys.argv[2], sys.argv[3]
a = T.load(src)
m = Q.mask(a)
ink = Q.inked(a)
dots = D.find(a)
idx = Q.index(dots)

im = Image.open(src).convert('RGB')
d = ImageDraw.Draw(im)

bars = [w for w in T.find_widgets(a) if 60 < w['y'] < 770]
# A slider bar's own outline is stroke, so a walker that reaches one climbs on
# to it and finishes inside somebody else's widget - six of the thirty-one on
# the first basement screen did exactly that. Take the bars out of the mask.
for w in bars:
    m[max(0, w['y'] - 9):w['y'] + 10, max(0, w['left'] - 1):w['right'] + 2] = False
    ink[max(0, w['y'] - 9):w['y'] + 10, max(0, w['left'] - 1):w['right'] + 2] = False
recs = []
placed = []
for i, w in enumerate(sorted(bars, key=lambda b: (b['left'], b['y'])), 1):
    g = Q.leader(m, ink, w, dots=idx)
    d.rectangle([w['left'] - 2, w['y'] - 9, w['right'] + 2, w['y'] + 9],
                outline=(0, 140, 0), width=2)
    d.text((w['left'] - 26, w['y'] - 7), str(i), fill=(0, 120, 0))
    if g is None or g['dist'] < 12:
        recs.append({'n': i, 'bar': [w['left'], w['right'], w['y']], 'end': None})
        continue
    ex, ey = g['end']
    recs.append({'n': i, 'bar': [w['left'], w['right'], w['y']],
                 'end': [int(ex), int(ey)], 'dist': int(g['dist']),
                 'dot': bool(g['dot'])})
    colour = (220, 0, 0) if g['dot'] else (255, 140, 0)
    d.ellipse([ex - 7, ey - 7, ex + 7, ey + 7], outline=colour, width=3)
    lx, ly = ex + 9, ey - 6
    while any(abs(lx - px) < 20 and abs(ly - py) < 11 for px, py in placed):
        ly += 12
    placed.append((lx, ly))
    d.text((lx, ly), str(i), fill=colour)

# any dot nobody claimed - drawn hollow blue, so an unread leader is visible
claimed = {tuple(r['end']) for r in recs if r.get('end')}
for x, y in dots:
    if (x, y) not in claimed:
        d.ellipse([x - 5, y - 5, x + 5, y + 5], outline=(0, 90, 220), width=2)

im.save(out)
json.dump(recs, open(jsn, 'w'), indent=1, default=int)
ends = [tuple(r['end']) for r in recs if r.get('dot')]
uniq = len(set(ends))
print('%s  %d widgets, %d on a dot (%d distinct), %d dots found' % (
    out, len(bars), len(ends), uniq, len(dots)))
