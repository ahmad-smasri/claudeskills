"""Trace every leader on a screen, choosing the exit direction from where the
widget sits: the top and bottom rows leave vertically, the side columns
horizontally. Falls back to the other directions if the first finds nothing."""
import sys, json
from PIL import Image, ImageDraw
import trace as T

src, out, jsn = sys.argv[1], sys.argv[2], sys.argv[3]
a = T.load(src)
im = Image.open(src).convert('RGB')
d = ImageDraw.Draw(im)
H, W = a.shape

def probe(w, dx, dy):
    """best endpoint leaving the widget in one direction, or None"""
    best = None
    if dy == 0:
        x0 = w['right'] + 3 if dx > 0 else w['left'] - 3
        for yy in range(w['y'] - 9, w['y'] + 10):
            if not T.is_line(a, yy, x0):
                continue
            ex, ey = (T.follow(a, x0, yy) if dx > 0 else T.follow_left(a, x0, yy))
            dist = abs(ex - x0) + abs(ey - yy)
            if best is None or dist > best[0]:
                best = (dist, ex, ey)
    else:
        y0 = w['y'] + dy * 11
        for xx in range(w['left'] - 4, w['right'] + 5):
            if not T.is_line(a, y0, xx):
                continue
            ex, ey = T.follow_any(a, xx, y0, 0, dy)
            dist = abs(ey - y0) + abs(ex - xx)
            if best is None or dist > best[0]:
                best = (dist, ex, ey)
    return best

bars = [w for w in T.find_widgets(a) if 60 < w['y'] < 790]
recs = []
for i, w in enumerate(sorted(bars, key=lambda b: (b['left'], b['y'])), 1):
    if w['y'] < 215:
        order = [(0, 1), (1, 0), (-1, 0), (0, -1)]
    elif w['y'] > 690:
        order = [(0, -1), (1, 0), (-1, 0), (0, 1)]
    elif w['left'] < W / 2 - 150:
        order = [(1, 0), (0, 1), (0, -1), (-1, 0)]
    else:
        order = [(-1, 0), (0, 1), (0, -1), (1, 0)]
    got = None
    for dx, dy in order:
        b = probe(w, dx, dy)
        if b and b[0] > 12:
            got = b
            break
    if got is None:
        continue
    ex, ey = got[1], got[2]
    recs.append({'n': i, 'bar': [w['left'], w['right'], w['y']], 'end': [int(ex), int(ey)]})
    d.rectangle([w['left'] - 2, w['y'] - 9, w['right'] + 2, w['y'] + 9], outline=(0, 140, 0), width=2)
    d.text((w['left'] - 26, w['y'] - 7), str(i), fill=(0, 120, 0))
    d.ellipse([ex - 7, ey - 7, ex + 7, ey + 7], outline=(220, 0, 0), width=3)
    d.text((ex + 9, ey - 6), str(i), fill=(200, 0, 0))

im.save(out)
json.dump(recs, open(jsn, 'w'), indent=1, default=int)
print(out, len(recs), 'of', len(bars), 'widgets traced')
