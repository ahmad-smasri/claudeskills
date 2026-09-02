"""Find the solid dots that terminate the serving-area leaders on a QNL screen.

Every leader ends in a filled disc about four pixels across sitting inside the
room the unit serves. The disc is drawn about 50 grey levels below the room
fill where the leader itself is only about 25 below, so darkness separates the
two, and a 3x3 erosion drops the one-pixel-wide leaders and the two-pixel room
walls. What survives besides the discs is the bold room text, which is thrown
out by its company: letters come in runs, a disc stands alone.
"""
import numpy as np
import trace as T

DARK = 32          # how far below local background a disc sits
BOX = 7            # widest a disc may be
NEAR = 8           # two discs are never this close - letters are


def _cores(a):
    """dark and solid: the leaders themselves sit only ~25 below background,
    so this threshold drops them and keeps the discs and the room text."""
    up = np.median(np.stack([np.roll(a, s, 0) for s in range(5, 13)]), axis=0)
    dn = np.median(np.stack([np.roll(a, -s, 0) for s in range(5, 13)]), axis=0)
    base = np.maximum(up, dn)
    return a < base - DARK


def _blobs(core):
    pts = set(zip(*[c.tolist() for c in np.nonzero(core)]))
    seen, out = set(), []
    for p in sorted(pts):
        if p in seen:
            continue
        stack, comp = [p], []
        seen.add(p)
        while stack:
            y, x = stack.pop()
            comp.append((y, x))
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    q = (y + dy, x + dx)
                    if q in pts and q not in seen:
                        seen.add(q)
                        stack.append(q)
        out.append(comp)
    return out


def _arms(m, x, y, lo=5, hi=10):
    """how many of the four headings still carry stroke away from (x,y)

    A leader ends at its dot, so a dot has one arm. Where a leader turns a
    corner the bend reads as a small solid blob too, but it has two.
    """
    n = 0
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        hits = 0
        for r in range(lo, hi + 1):
            px, py = x + dx * r, y + dy * r
            if not (0 <= py < m.shape[0] and 0 <= px < m.shape[1]):
                continue
            if m[py - (1 if dy == 0 else 0):py + (2 if dy == 0 else 1),
                 px - (1 if dx == 0 else 0):px + (2 if dx == 0 else 1)].any():
                hits += 1
        # a dash is three on and one off, so a real arm is there at most radii;
        # one hit is a speck of JPEG noise
        if hits >= (hi - lo) // 2 + 1:
            n += 1
    return n


def find(a, ylo=80, yhi=765):
    import qnl_trace as QT
    soft = QT.mask(a)
    core = _cores(a)
    core[:ylo] = False
    core[yhi:] = False
    blobs = _blobs(core)
    cand = []
    for comp in blobs:
        yy = [c[0] for c in comp]
        xx = [c[1] for c in comp]
        h, w = max(yy) - min(yy) + 1, max(xx) - min(xx) + 1
        c = (int(round(sum(xx) / len(xx))), int(round(sum(yy) / len(yy))))
        if 3 <= h <= BOX and 3 <= w <= BOX and len(comp) >= 0.5 * h * w:
            cand.append(c)
    out = []
    for x, y in cand:
        if any(abs(x - qx) <= NEAR and abs(y - qy) <= NEAR
               for qx, qy in cand if (qx, qy) != (x, y)):
            continue                      # a letter among its neighbours
        if _arms(soft, x, y) > 1:
            continue                      # a bend in the leader, not its end
        out.append((x, y))
    return out


if __name__ == '__main__':
    import sys
    from PIL import Image, ImageDraw
    a = T.load(sys.argv[1])
    d = find(a)
    im = Image.open(sys.argv[1]).convert('RGB')
    dr = ImageDraw.Draw(im)
    for x, y in d:
        dr.ellipse([x - 6, y - 6, x + 6, y + 6], outline=(255, 0, 0), width=2)
    im.save(sys.argv[2])
    print(len(d), 'dots')
