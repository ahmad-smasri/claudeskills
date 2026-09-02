"""Crop the widget clusters of an annotated screen so the tag text beside each
numbered box can be read in as few images as possible."""
import sys, json, os
from PIL import Image

png, jsn, tag = sys.argv[1], sys.argv[2], sys.argv[3]
recs = json.load(open(jsn))
im = Image.open(png)

# cluster widgets that sit in the same column (same left edge) or the same row
boxes = [(r['n'], r['bar'][0], r['bar'][1], r['bar'][2]) for r in recs]
cols = {}
for n, l, rr, y in boxes:
    key = None
    for k in cols:
        if abs(k - l) < 12:
            key = k
            break
    cols.setdefault(key if key is not None else l, []).append((n, l, rr, y))

groups = []
for k, v in cols.items():
    v.sort(key=lambda t: t[3])
    if len(v) == 1:
        groups.append(v)
        continue
    cur = [v[0]]
    for t in v[1:]:
        if t[3] - cur[-1][3] < 130:
            cur.append(t)
        else:
            groups.append(cur)
            cur = [t]
    groups.append(cur)

# merge single-widget groups that sit on the same row (the top/bottom strips)
singles = [g[0] for g in groups if len(g) == 1]
groups = [g for g in groups if len(g) > 1]
singles.sort(key=lambda t: (t[3], t[1]))
cur = []
for t in singles:
    if cur and abs(t[3] - cur[-1][3]) < 30 and t[1] - cur[-1][2] < 400:
        cur.append(t)
    else:
        if cur:
            groups.append(cur)
        cur = [t]
if cur:
    groups.append(cur)

groups.sort(key=lambda g: (g[0][1], g[0][3]))
for i, g in enumerate(groups, 1):
    x0 = max(0, min(t[1] for t in g) - 105)
    x1 = min(im.width, max(t[2] for t in g) + 30)
    y0 = max(0, min(t[3] for t in g) - 26)
    y1 = min(im.height, max(t[3] for t in g) + 22)
    sc = 2.4 if (x1 - x0) < 400 else 1.7
    c = im.crop((x0, y0, x1, y1))
    c = c.resize((int(c.width * sc), int(c.height * sc)), Image.LANCZOS)
    out = 'crops/%s_g%d.png' % (tag, i)
    c.save(out)
    print(out, c.size, 'markers', [t[0] for t in g])
