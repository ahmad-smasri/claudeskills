"""Follow a QNL serving-area leader from its widget to the dot at its far end.

The QNL screens differ from the HQ and SSC ones in two ways that break the
original walker.

Every leader ends in a small solid dot inside the room it serves, so reaching
one is the end of the walk - `qnl_dots` finds them and they are passed in here.
Without that the walker runs on through the junction where the next leader
crosses and finishes in somebody else's room.

And a leader turns its corners in the middle of the plan, among walls, doors
and other leaders. Deciding the corner at the point where the straight run
happens to stop is what put six of the thirty-one units on the first basement
screen in the wrong place: the run does not stop at the corner, it carries a
few pixels further onto whatever wall stub sits beyond it. So the corner is
chosen instead as the last point along the run that has a long dashed stroke
leaving it sideways - walls and duct outlines are solid and are refused, and a
leader merely crossing ours is passed over because a later branch exists.
"""
import numpy as np
import trace as T

JUMP = 16          # widest thing a leader is drawn under (the outer wall)
MIN_BRANCH = 14    # a perpendicular shorter than this is not a turn
DASH_GAPS = 4      # gaps in 32 px below which a stroke counts as solid


def _below_at(a, axis, contrast):
    lo = np.median(np.stack([np.roll(a, s, axis) for s in range(4, 11)]), axis=0)
    hi = np.median(np.stack([np.roll(a, -s, axis) for s in range(5, 12)]), axis=0)
    return a < np.maximum(lo, hi) - contrast


def _below(a, axis):
    """pixels sitting below the background measured along one axis

    `trace.is_line` reads the background off the column above and below the
    pixel, which is flat under a horizontal stroke and is the stroke itself
    under a vertical one - so a vertical leader reads as background and
    vanishes. Both axes are needed here because QNL leaders turn corners.
    """
    return _below_at(a, axis, T.CONTRAST)


def inked(a, contrast=7):
    """anything drawn at all - used to tell a wall drawn over a leader from
    empty space, so the walker crosses the first and stops at the second."""
    m = _below_at(a, 0, contrast) | _below_at(a, 1, contrast)
    m[:2] = m[-2:] = False
    m[:, :2] = m[:, -2:] = False
    return m


def mask(a):
    """stroke mask, done once for the whole screen.

    The walker probes far too many pixels for the per-pixel form in `trace` to
    be affordable, and it needs both axes anyway.
    """
    m = _below(a, 0) | _below(a, 1)
    m[:2] = m[-2:] = False
    m[:, :2] = m[:, -2:] = False
    return m


def _on(m, y, x):
    return 0 <= y < m.shape[0] and 0 <= x < m.shape[1] and bool(m[y, x])


def index(dots, cell=4):
    """bucket the dots so the walker can ask 'am I on one' in constant time"""
    g = {}
    for x, y in dots:
        for ox in (-1, 0, 1):
            for oy in (-1, 0, 1):
                g.setdefault((x // cell + ox, y // cell + oy), []).append((x, y))
    return g


def _at_dot(dots, x, y):
    if dots is None:
        return None
    for cx, cy in dots.get((x // 4, y // 4), ()):
        if abs(cx - x) <= 4 and abs(cy - y) <= 4:
            return cx, cy
    return None


def _probe(m, ink, x, y, dx, dy):
    """is the stroke there again within JUMP px on this heading?

    Only across something: a leader crossing the building's outer wall goes
    quiet for up to ten pixels because the wall supplies its own background,
    and that gap has to be stepped over. A gap of bare screen is the end of
    the leader, and stepping over that is how a unit ends up on the leader of
    the widget next door.
    """
    for i in range(2, JUMP):
        if not _on(ink, y + dy * (i - 1), x + dx * (i - 1)):
            return None
        for s in (0, -1, 1, -2, 2):
            px = x + dx * i + (s if dx == 0 else 0)
            py = y + dy * i + (s if dy == 0 else 0)
            if _on(m, py, px):
                return px, py
    return None


def _straight(m, ink, x, y, dx, dy, dots=None, limit=1700):
    """advance along one straight segment, returning every stroke pixel walked"""
    h, w = m.shape
    path = [(x, y)]
    gap = 0
    for _ in range(limit):
        if not (1 < x < w - 2 and 1 < y < h - 2):
            break
        nxt = None
        for s in (0, -1, 1, -2, 2):
            px = x + dx + (s if dx == 0 else 0)
            py = y + dy + (s if dy == 0 else 0)
            if _on(m, py, px):
                nxt = (px, py)
                break
        if nxt:
            x, y = nxt
            path.append((x, y))
            gap = 0
            d = _at_dot(dots, x, y)
            if d and len(path) > 4:
                return d, path, True
        else:
            gap += 1
            if gap > T.DASH_GAP:
                j = _probe(m, ink, path[-1][0], path[-1][1], dx, dy)
                if j is None:
                    break
                x, y = j
                path.append((x, y))
                gap = 0
            else:
                x, y = x + dx, y + dy
    return path[-1], path, False


def _branch(m, x, y, dx, dy, span=32):
    """length of the dashed stroke leaving (x,y) sideways, 0 if there is none"""
    on = [_on(m, y + dy * i, x + dx * i) or
          _on(m, y + dy * i + (1 if dy == 0 else 0), x + dx * i + (1 if dx == 0 else 0))
          for i in range(1, span + 1)]
    if not on[0] and not on[1]:
        return 0
    if on.count(False) < DASH_GAPS:
        return 0                      # solid: a wall, a duct, a room outline
    run = 0
    gap = 0
    for v in on:
        if v:
            run += gap + 1
            gap = 0
        else:
            gap += 1
            if gap > T.DASH_GAP:
                break
    return run


def follow(m, ink, x0, y0, dx, dy, dots=None, max_jogs=14):
    """walk a leader from (x0,y0) heading (dx,dy), taking every turn it makes"""
    x, y = x0, y0
    d = (dx, dy)
    for _ in range(max_jogs):
        (x, y), path, done = _straight(m, ink, x, y, *d, dots=dots)
        if done:
            return x, y, True
        turn = None
        for px, py in reversed(path):
            best = None
            for t in ((d[1], d[0]), (-d[1], -d[0])):
                n = _branch(m, px, py, *t)
                if n >= MIN_BRANCH and (best is None or n > best[0]):
                    best = (n, t)
            if best:
                turn = (px, py, best[1])
                break
        if turn is None:
            return x, y, False
        x, y, d = turn
    return x, y, False


def leader(m, ink, w, dots=None):
    """the far end of the one real leader leaving a slider widget

    A widget has a leader on one side only, but the bar's own border reads as
    stroke, so all four sides are tried and the walk that reaches a dot wins.
    """
    starts = []
    for off in (2, 4, 6):
        for yy in range(w['y'] - 2, w['y'] + 3):
            if _on(m, yy, w['right'] + off):
                starts.append((w['right'] + off, yy, 1, 0))
                break
        for yy in range(w['y'] - 2, w['y'] + 3):
            if _on(m, yy, w['left'] - off):
                starts.append((w['left'] - off, yy, -1, 0))
                break
    for off in (11, 13):
        for dy in (1, -1):
            for xx in range(w['left'], w['right'] + 1):
                if _on(m, w['y'] + dy * off, xx):
                    starts.append((xx, w['y'] + dy * off, 0, dy))
                    break
    best = None
    for sx, sy, dx, dy in starts:
        ex, ey, ondot = follow(m, ink, sx, sy, dx, dy, dots=dots)
        rank = (1 if ondot else 0, abs(ex - sx) + abs(ey - sy))
        if best is None or rank > best[0]:
            best = (rank, ex, ey, (dx, dy), ondot)
    if best is None:
        return None
    return {'end': (best[1], best[2]), 'dist': best[0][1], 'dir': best[3],
            'dot': best[4]}
