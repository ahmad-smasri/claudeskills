"""Find the equipment icons on a QNL BMS screen, and follow their leaders.

Fans, AHUs, DX units, CCUs and pumps are drawn as solid mid-grey tiles rather
than the slider bar the VAVs and FCUs use, so `trace.find_widgets` never sees
them - which is why the roof screens came back with nothing on them. They carry
the same dotted serving-area leader, drawn out of the middle of the tile's left
or right edge.

`trace.find_icons` misses them too: it grows a bounding box by walking one row
and one column out of a seed pixel, and the fan blade drawn across the middle
of the tile stops the column walk short of its size test. This flood-fills
instead.
"""
import numpy as np
import trace as T
import qnl_trace as Q

LO, HI = 100, 155        # the tile grey
MIN, MAX = 50, 110       # a tile is about 66 px square


def find(a, ylo=60, yhi=790):
    m = (a >= LO) & (a <= HI)
    m[:ylo] = False
    m[yhi:] = False
    seen = np.zeros_like(m)
    out = []
    ys, xs = np.nonzero(m)
    for y0, x0 in zip(ys.tolist(), xs.tolist()):
        if seen[y0, x0]:
            continue
        stack, comp = [(y0, x0)], []
        seen[y0, x0] = True
        while stack:
            y, x = stack.pop()
            comp.append((y, x))
            for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                ny, nx = y + dy, x + dx
                if 0 <= ny < m.shape[0] and 0 <= nx < m.shape[1] \
                        and m[ny, nx] and not seen[ny, nx]:
                    seen[ny, nx] = True
                    stack.append((ny, nx))
        yy = [c[0] for c in comp]
        xx = [c[1] for c in comp]
        h, w = max(yy) - min(yy) + 1, max(xx) - min(xx) + 1
        if MIN <= h <= MAX and MIN <= w <= MAX and len(comp) > 0.35 * h * w:
            out.append({'left': min(xx), 'right': max(xx),
                        'top': min(yy), 'bottom': max(yy),
                        'y': (min(yy) + max(yy)) // 2})
    # the fan blade drawn across the tile splits it into two components, so
    # boxes that sit on top of each other are one icon
    merged = []
    for b in sorted(out, key=lambda z: (z['y'], z['left'])):
        for k in merged:
            if abs(k['y'] - b['y']) < 12 and b['left'] < k['right'] + 12 \
                    and k['left'] < b['right'] + 12:
                k['left'] = min(k['left'], b['left'])
                k['right'] = max(k['right'], b['right'])
                k['top'] = min(k['top'], b['top'])
                k['bottom'] = max(k['bottom'], b['bottom'])
                k['y'] = (k['top'] + k['bottom']) // 2
                break
        else:
            merged.append(b)
    return sorted(merged, key=lambda b: (b['left'], b['y']))


def leader(m, ink, icon, dots=None):
    """the far end of the leader leaving an icon, left or right"""
    # A tile can carry a status strip under it and the leader does not always
    # leave at the tile's own centre, so every row of the tile is tried on both
    # edges and the longest walk wins.
    best = None
    tried = set()
    for dx in (1, -1):
        for off in (3, 6, 10):
            x0 = icon['right'] + off if dx > 0 else icon['left'] - off
            for yy in range(icon['top'] - 6, icon['bottom'] + 7):
                if not Q._on(m, yy, x0) or (x0, yy) in tried:
                    continue
                tried.add((x0, yy))
                ex, ey, ondot = Q.follow(m, ink, x0, yy, dx, 0, dots=dots)
                rank = (1 if ondot else 0, abs(ex - x0) + abs(ey - yy))
                if rank[1] > 25 and (best is None or rank > best[0]):
                    best = (rank, ex, ey, ondot)
    if best is None:
        return None
    return {'end': (best[1], best[2]), 'dist': best[0][1], 'dot': best[3]}
