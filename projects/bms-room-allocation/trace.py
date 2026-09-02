"""Follow the dotted 'serving area' leader lines on an AVEVA/Wonderware BMS screen.

The lines are a 3-on/1-off dotted stroke drawn ~25 grey levels below whatever
the local background is, so a fixed threshold fails inside the colour-filled
rooms. Background is estimated per pixel from the column above and below the
line, which is flat wherever a room fill is.
"""
import numpy as np
from PIL import Image

DASH_GAP = 6          # a dash may be up to this many px from the next one
CONTRAST = 18         # how far below local background a stroke pixel sits


def load(path):
    return np.array(Image.open(path).convert('L')).astype(int)


def bg(a, y, x):
    h = a.shape[0]
    lo = a[max(0, y - 11):max(1, y - 4), x]
    hi = a[min(h - 1, y + 5):min(h, y + 12), x]
    col = np.concatenate([lo, hi])
    return np.median(col) if col.size else 255


def is_line(a, y, x):
    if not (0 <= y < a.shape[0] and 0 <= x < a.shape[1]):
        return False
    return a[y, x] < bg(a, y, x) - CONTRAST


def hit(a, y, x, spread=2):
    """is the stroke present at column x, near row y - returns the row"""
    for dy in range(0, spread + 1):
        for s in ((0,) if dy == 0 else (-dy, dy)):
            if is_line(a, y + s, x):
                return y + s
    return None


def run_right(a, y, x, limit):
    """walk right along a horizontal stroke, tolerating the dot gaps"""
    gap = 0
    while x < limit:
        r = hit(a, y, x + 1)
        if r is not None:
            x, y, gap = x + 1, r, 0
        else:
            gap += 1
            if gap > DASH_GAP:
                return x - gap + 1, y
            x += 1
    return x, y


def run_vert(a, y, x, direction, limit=420):   # leaders turn 90 deg and can run a long way
    gap, moved = 0, 0
    while moved < limit:
        r = None
        for dx in (0, -1, 1):
            if is_line(a, y + direction, x + dx):
                r = x + dx
                break
        if r is not None:
            y, x, gap = y + direction, r, 0
        else:
            gap += 1
            if gap > DASH_GAP:
                return y - direction * gap, x, moved - gap
            y += direction
        moved += 1
    return y, x, moved


def follow(a, x0, y0, xlimit=None):
    """from the right edge of a widget, follow the leader to where it stops"""
    xlimit = xlimit or a.shape[1] - 2
    x, y = x0, y0
    for _ in range(24):                       # leaders can jog several times
        nx, ny = run_right(a, y, x, xlimit)
        if nx <= x + 1:                       # no horizontal progress
            pass
        x, y = nx, ny
        best = None
        for d in (1, -1):                     # try a vertical jog
            vy, vx, moved = run_vert(a, y, x, d)
            if moved > 4:
                cand = (moved, vy, vx)
                if best is None or cand[0] > best[0]:
                    best = cand
        if best is None:
            break
        _, y, x = best
        nx2, _ = run_right(a, y, x, xlimit)
        if nx2 <= x + 2:                      # jog led nowhere - stop here
            break
    return x, y


def stroke_mask(a):
    """True where a pixel sits well below the local vertical background"""
    h, w = a.shape
    up = np.median(np.stack([np.roll(a, s, 0) for s in range(4, 11)]), axis=0)
    dn = np.median(np.stack([np.roll(a, -s, 0) for s in range(4, 11)]), axis=0)
    base = np.maximum(up, dn)
    return a < base - CONTRAST


def dotted(seg):
    """a leader is a dashed stroke: ~75% duty with a gap every ~4 px.
    Room walls and widget borders are solid, so they fail this."""
    n = len(seg)
    if n < 12:
        return False
    duty = seg.sum() / n
    gaps = 0
    run = 0
    for v in seg:
        if v:
            run = 0
        else:
            run += 1
            if run == 1:
                gaps += 1
    return 0.55 <= duty <= 0.92 and gaps >= n / 9


def find_starts(a, min_len=34, xlo=0, xhi=None, ylo=0, yhi=None):
    """left ends of the long horizontal dotted runs - the leader origins"""
    m = stroke_mask(a)
    h, w = a.shape
    xhi = xhi or w
    yhi = yhi or h
    out = []
    for y in range(ylo, yhi):
        x = xlo
        while x < xhi:
            if not m[y, x]:
                x += 1
                continue
            s = x
            gap = 0
            while x < xhi and gap <= DASH_GAP:
                if m[y, x]:
                    gap = 0
                    e = x
                else:
                    gap += 1
                x += 1
            if e - s >= min_len and dotted(m[y, s:e + 1]):
                out.append((s, y, e))
    # collapse the 2-3 rows each stroke covers, and near-duplicate starts
    out.sort(key=lambda t: (t[0], t[1]))
    keep = []
    for s, y, e in out:
        if any(abs(s - ks) < 12 and abs(y - ky) < 6 for ks, ky, _ in keep):
            continue
        keep.append((s, y, e))
    return sorted(keep, key=lambda t: (t[1], t[0]))


def find_widgets(a):
    """Locate the VAV/FCU slider widgets.

    Each is a 71x12 outlined bar carrying a solid black position tick that
    overhangs the bar top and bottom - the tick is what we key on, since it is
    the only near-black vertical stroke of that height on these screens.
    """
    h, w = a.shape
    dark = a < 120
    # a leader crossing the tick lightens a single row and splits the run, so
    # close one-pixel holes before measuring
    dark = dark | (np.roll(dark, 1, 0) & np.roll(dark, -1, 0))
    out = []
    for x in range(2, w - 2):
        y = 0
        while y < h:
            if not dark[y, x]:
                y += 1
                continue
            s = y
            while y < h and dark[y, x]:
                y += 1
            # the tick is 2-3 px wide - on the JPEG screens the outer column is
            # blurred above the threshold, so one solid neighbour is enough
            if 13 <= y - s <= 20 and (dark[s:y, x - 1].all() or dark[s:y, x + 1].all()):
                out.append((x, (s + y) // 2))
            y += 1
    # one hit per tick (the tick is 3 px wide)
    out.sort(key=lambda t: (t[1], t[0]))
    keep = []
    for x, y in out:
        if any(abs(x - kx) < 6 and abs(y - ky) < 6 for kx, ky in keep):
            continue
        keep.append((x, y))
    # The tick slides inside the bar and the bar is part-filled, so neither edge
    # can be found by walking out from the tick. Measure the bar's own top
    # border instead - one long horizontal run straddling the tick.
    bars = []
    for x, y in keep:
        best = None
        for r in range(y - 10, y + 11):
            if not (0 <= r < h) or a[r, x] > 210:
                continue
            l0 = x
            while l0 > 1 and a[r, l0 - 1] <= 210:
                l0 -= 1
            r0 = x
            while r0 < w - 2 and a[r, r0 + 1] <= 210:
                r0 += 1
            # the leader leaves the bar at its vertical centre, so that row
            # reads as one long run - keep the widest run that is still a bar
            if not (45 <= r0 - l0 <= 110):
                continue
            if best is None or r0 - l0 > best[2] - best[1]:
                best = (r, l0, r0)
        if best is None:
            continue
        # an equipment icon is a filled box of about the same width, so check
        # the height too: a slider bar is 12-13 px deep, an icon 60 or more
        rb, l0, r0 = best
        mid = (l0 + r0) // 2
        d = 1
        while rb + d < h and a[rb + d, mid] <= 210 and d < 30:
            d += 1
        if d > 22:
            continue
        bars.append({'tick': x, 'y': y, 'left': l0, 'right': r0})
    return bars


def run_left(a, y, x, limit):
    gap = 0
    while x > limit:
        r = hit(a, y, x - 1)
        if r is not None:
            x, y, gap = x - 1, r, 0
        else:
            gap += 1
            if gap > DASH_GAP:
                return x + gap - 1, y
            x -= 1
    return x, y


def follow_left(a, x0, y0, xlimit=2):
    x, y = x0, y0
    for _ in range(24):
        nx, ny = run_left(a, y, x, xlimit)
        x, y = nx, ny
        best = None
        for dd in (1, -1):
            vy, vx, moved = run_vert(a, y, x, dd)
            if moved > 4:
                cand = (moved, vy, vx)
                if best is None or cand[0] > best[0]:
                    best = cand
        if best is None:
            break
        _, y, x = best
        nx2, _ = run_left(a, y, x, xlimit)
        if nx2 >= x - 2:
            break
    return x, y


def _walk(a, x, y, dx, dy):
    """advance along one straight dotted segment; returns the last stroke pixel"""
    h, w = a.shape
    gap = 0
    lx, ly = x, y
    while 1 < x < w - 2 and 1 < y < h - 2:
        found = None
        for s in (0, -1, 1, -2, 2):
            nx = x + dx + (s if dx == 0 else 0)
            ny = y + dy + (s if dy == 0 else 0)
            if is_line(a, ny, nx):
                found = (nx, ny)
                break
        if found:
            x, y = found
            lx, ly = x, y
            gap = 0
        else:
            gap += 1
            if gap > DASH_GAP:
                break
            x, y = x + dx, y + dy
    return lx, ly


def follow_any(a, x0, y0, dx, dy, max_jogs=16):
    """follow a leader from (x0,y0) heading (dx,dy), taking any turn it makes"""
    x, y = x0, y0
    d = (dx, dy)
    for _ in range(max_jogs):
        nx, ny = _walk(a, x, y, *d)
        moved = abs(nx - x) + abs(ny - y)
        x, y = nx, ny
        turns = [(d[1], d[0]), (-d[1], -d[0])] if d[0] or d[1] else []
        best = None
        for t in turns:
            tx, ty = _walk(a, x, y, *t)
            m = abs(tx - x) + abs(ty - y)
            if m > 5 and (best is None or m > best[0]):
                best = (m, tx, ty, t)
        if best is None:
            break
        _, x, y, d = best
    return x, y


def leader_from(a, w):
    """try all four ways out of a widget; the real leader is the long one"""
    cands = [
        (w['right'] + 2, w['y'], 1, 0),
        (w['left'] - 2, w['y'], -1, 0),
        (w['tick'], w['y'] + 11, 0, 1),
        (w['tick'], w['y'] - 11, 0, -1),
    ]
    best = (0, w['right'], w['y'], None)
    for sx, sy, dx, dy in cands:
        if not is_line(a, sy, sx) and not is_line(a, sy + dy, sx + dx):
            continue
        ex, ey = follow_any(a, sx, sy, dx, dy)
        dist = abs(ex - sx) + abs(ey - sy)
        if dist > best[0]:
            best = (dist, ex, ey, (dx, dy))
    return best[1], best[2], best[0], best[3]


def find_icons(a, lo=105, hi=145, minsize=45):
    """Locate the equipment icons - solid mid-grey rounded squares."""
    m = (a >= lo) & (a <= hi)
    h, w = a.shape
    seen = np.zeros_like(m, dtype=bool)
    out = []
    ys, xs = np.nonzero(m)
    for y0, x0 in zip(ys, xs):
        if seen[y0, x0]:
            continue
        # flood the row-run block by simple bounding-box growth
        y1 = y0
        while y1 + 1 < h and m[y1 + 1, x0]:
            y1 += 1
        xa = x0
        while xa - 1 >= 0 and m[y0, xa - 1]:
            xa -= 1
        xb = x0
        while xb + 1 < w and m[y0, xb + 1]:
            xb += 1
        if (y1 - y0) >= minsize and (xb - xa) >= minsize:
            seen[y0:y1 + 1, xa:xb + 1] = True
            out.append({'left': xa, 'right': xb, 'top': y0, 'bottom': y1,
                        'y': (y0 + y1) // 2, 'tick': (xa + xb) // 2})
        else:
            seen[y0, xa:xb + 1] = True
    # de-duplicate overlapping boxes
    keep = []
    for b in sorted(out, key=lambda z: -( (z['right']-z['left'])*(z['bottom']-z['top']) )):
        if any(abs(b['tick'] - k['tick']) < 40 and abs(b['y'] - k['y']) < 40 for k in keep):
            continue
        keep.append(b)
    return sorted(keep, key=lambda z: (z['left'], z['y']))


def wall_suspect(a, x, y, dx, dy, span=60):
    """True if the stroke ending at (x,y) arrived along an unbroken run.

    Leaders are dashed; walls are not. A walker that steps off the end of a
    leader onto a wall it touches will follow the wall, and the give-away is
    that the last stretch has no gaps in it. Used to mark an endpoint for a
    manual zoom rather than to change where the walk stops.
    """
    gaps = 0
    for i in range(1, span):
        px, py = x - dx * i, y - dy * i
        if not (0 <= py < a.shape[0] and 0 <= px < a.shape[1]):
            break
        if not is_line(a, py, px):
            gaps += 1
    return gaps == 0


def refine_endpoint(a, ex, ey, dx, dy, back=420):
    """Back a wall-following endpoint up to where the leader actually stopped.

    Walks back along the arrival direction looking for the last place the
    stroke was still dashed - i.e. had a gap within the preceding few pixels.
    Everything beyond that was wall the walker had climbed onto.
    """
    if not (dx or dy):
        return ex, ey
    run = 0
    last_gap = None
    for i in range(0, back):
        px, py = ex - dx * i, ey - dy * i
        if not (0 <= py < a.shape[0] and 0 <= px < a.shape[1]):
            break
        if is_line(a, py, px):
            run += 1
        else:
            run = 0
            last_gap = (px, py)
        if run == 0 and last_gap is not None and i > 4:
            # first genuine gap coming back from the endpoint: the dashed part
            # of the stroke starts here
            return last_gap
    return ex, ey


# NOTE: an automatic "trim the wall off the end of the path" pass was tried and
# removed. hit() searches two rows either side, and these leaders are drawn
# along a room wall for their first 40-150 px, so the path reads as solid from
# the very start and the trim fires at the widget. wall_suspect() flags the bad
# endpoints reliably; resolving them needs a zoom, not more heuristics.
