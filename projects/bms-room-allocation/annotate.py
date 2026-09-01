"""Trace every leader on a screen and drop a numbered marker where it lands."""
import sys, json
from PIL import Image, ImageDraw
import trace as T

src, out, jsn = sys.argv[1], sys.argv[2], sys.argv[3]
a = T.load(src)
im = Image.open(src).convert('RGB')
d = ImageDraw.Draw(im)

W = a.shape[1]
bars = [w for w in T.find_widgets(a) if 150 < w['y'] < 745]
recs = []
for i, w in enumerate(sorted(bars, key=lambda b: (b['left'], b['y'])), 1):
    mid = W / 2
    if w['left'] < mid - 200:
        ex, ey = T.follow(a, w['right'] + 1, w['y'])
    else:
        ex, ey = T.follow_left(a, w['left'] - 1, w['y'])
    # a leader that never left the widget probably exits vertically instead
    if abs(ex - w['right']) < 8 and abs(ex - w['left']) < 8 or abs(ey - w['y']) + abs(ex - w['right']) < 10:
        for dy in (1, -1):
            vx, vy = T.follow_any(a, w['tick'], w['y'] + dy * 11, 0, dy)
            if abs(vy - w['y']) > 14:
                ex, ey = vx, vy
                break
    recs.append({'n': i, 'bar': [w['left'], w['right'], w['y']], 'end': [ex, ey]})
    d.rectangle([w['left'] - 2, w['y'] - 9, w['right'] + 2, w['y'] + 9], outline=(0, 140, 0), width=2)
    d.text((w['left'] - 26, w['y'] - 7), str(i), fill=(0, 120, 0))
    d.ellipse([ex - 7, ey - 7, ex + 7, ey + 7], outline=(220, 0, 0), width=3)
    d.text((ex + 9, ey - 6), str(i), fill=(200, 0, 0))

im.save(out)
json.dump(recs, open(jsn, 'w'), indent=1)
print(out, len(recs), 'leaders')
