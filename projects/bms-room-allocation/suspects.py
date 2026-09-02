import json, sys, trace as T
img, jsn = sys.argv[1], sys.argv[2]
a = T.load(img)
out = []
for x in json.load(open(jsn)):
    ex, ey = x['end']; l, r, by = x['bar']
    dx = 1 if ex > r else (-1 if ex < l else 0)
    dy = 0 if dx else (1 if ey > by else -1)
    if T.wall_suspect(a, ex, ey, dx, dy):
        out.append(x['n'])
print(len(out), out)
