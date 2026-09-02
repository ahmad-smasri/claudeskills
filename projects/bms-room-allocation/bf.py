"""Trace the basement screens and label each endpoint with the unit's own tag."""
import sys, json
from PIL import Image, ImageDraw, ImageFont
import trace as T

# icon centre -> label, read off the screenshots
BF1 = {(393,138):'AHU-B-0005', (393,263):'AHU-B-0001', (381,389):'CCU-B-0004',
       (381,519):'CCU-B-001A', (381,648):'CCU-B-002B', (189,436):'CCU-B-002A',
       (189,561):'CCU-B-001B', (189,699):'CCU-B-0003',
       (1538,111):'AHU-B-0003', (1539,243):'AHU-B-0002', (1540,374):'CCU-B-0007',
       (1541,509):'DX-B-0002', (1541,637):'DX-B-0001',
       (1719,169):'CCU-B-005B', (1719,306):'CCU-B-006B', (1719,440):'CCU-B-006A',
       (1719,565):'CCU-B-0008', (1719,692):'CCU-B-005A'}
BF2 = {(570,188):'AHU-B-0004', (573,316):'DX-B-0004', (573,433):'DX-B-0003',
       (573,556):'DX-B-0005', (573,683):'DX-B-0006',
       (1347,316):'DX-B-0008', (1347,439):'DX-B-0007',
       (1347,557):'DX-B-0010', (1347,683):'DX-B-0009'}
BARS1 = {(737,85):'VAV-0001', (672,742):'FCU-0001', (842,741):'FCU-0003', (994,742):'FCU-0002'}

src, which, out = sys.argv[1], sys.argv[2], sys.argv[3]
a = T.load(src)
im = Image.open(src).convert('RGB')
d = ImageDraw.Draw(im)
try:
    fnt = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 15)
except Exception:
    fnt = None

icons = T.find_icons(a)
want = BF1 if which == '1' else BF2
recs = []
for ic in icons:
    key = min(want, key=lambda k: abs(k[0] - ic['tick']) + abs(k[1] - ic['y']))
    if abs(key[0] - ic['tick']) > 45 or abs(key[1] - ic['y']) > 45:
        continue
    tag = want[key]
    right = ic['left'] < a.shape[1] / 2
    # the leader does not always leave at the icon's mid height - scan the band
    # just outside the icon and take whichever row runs furthest
    best = None
    for yy in range(ic['top'] - 10, ic['bottom'] + 11):
        x0 = ic['right'] + 3 if right else ic['left'] - 3
        if not T.is_line(a, yy, x0):
            continue
        ex, ey = (T.follow(a, x0, yy) if right else T.follow_left(a, x0, yy))
        dist = abs(ex - x0)
        if best is None or dist > best[0]:
            best = (dist, ex, ey)
    if best is None or best[0] < 10:
        continue
    recs.append({'tag': tag, 'icon': [ic['left'], ic['right'], ic['y']],
                 'end': [best[1], best[2]]})

if which == '1':
    for (bx, by), tag in BARS1.items():
        dy = 1 if by < 300 else -1          # top widget points down, bottom ones up
        best = None
        for xx in range(bx - 40, bx + 41):
            y0 = by + dy * 12
            if not T.is_line(a, y0, xx):
                continue
            ex, ey = T.follow_any(a, xx, y0, 0, dy)
            if abs(ey - by) > 15 and 60 < ey < 730:
                cand = (abs(ey - by), ex, ey)
                if best is None or cand[0] > best[0]:
                    best = cand
        if best:
            recs.append({'tag': tag, 'icon': [bx - 35, bx + 35, by],
                         'end': [best[1], best[2]]})

for r in recs:
    ex, ey = r['end']
    d.ellipse([ex - 6, ey - 6, ex + 6, ey + 6], outline=(220, 0, 0), width=3)
    d.rectangle([ex + 8, ey - 10, ex + 8 + 9 * len(r['tag']), ey + 8], fill=(255, 255, 255))
    d.text((ex + 10, ey - 8), r['tag'], fill=(190, 0, 0), font=fnt)

im.save(out)
json.dump(recs, open(out + '.json', 'w'), indent=1, default=int)
print(out, len(recs))
for r in recs:
    print('  %-12s -> (%d,%d)  moved %d' % (r['tag'], r['end'][0], r['end'][1],
          abs(r['end'][0] - r['icon'][1]) + abs(r['end'][1] - r['icon'][2])))
