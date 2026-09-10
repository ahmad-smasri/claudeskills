"""Follow an RDC serving-area leader from its widget to the dot at its far end.

A leader here is a dashed stroke that turns square corners, sometimes several,
and finishes in a small filled grey dot inside the room it serves.

Telling the stroke from a wall is the whole problem. The screens draw leaders at
two weights - a thin one whose dashes run 154 dark against 188 light, and a
thicker one running 174 against 211 - and the thin one's dark phase is exactly
the grey the walls are drawn in, so no brightness threshold separates them. The
first cut used a band between the two and found eight leaders out of forty-three:
every thin leader had been classified as wall and erased.

What does separate them is direction. A leader is dashed *along its own length*,
so a short window laid along it spans both phases of the dash and sees a range
of about fifty grey levels. A wall is solid along its own length and that same
window sees almost nothing. So a horizontal stroke is a run of drawn pixels with
a large range measured along x, and that test passes every horizontal leader,
rejects every horizontal wall - flat along x - and rejects every vertical wall
too, since three pixels of width cannot fill the window. The vertical case is
the same test with the axes swapped.

Dropping the band also drops the need to jump dash gaps: the mask covers the
light phase as well, so a straight run reads as continuous. Gaps remain only
where a leader crosses a wall, and those are stepped over when - and only when -
the gap is dark. A gap of bare room ground is the end of the leader, and
stepping over one is how a unit ends up on the leader of the widget next door.

A corner is taken as the last point of the straight run with a long stroke
leaving it sideways, so a leader merely crossing ours is passed over in favour
of the branch further along.
"""
import numpy as np
from scipy import ndimage

DARK = 166          # wall and dot are below this
DASH = 20           # grey range along a stroke's own axis, dashed vs solid
WIN = 5             # window the range is measured over
RUN = 17            # window the dashed-pixel count is measured over
FILL = 14           # of RUN, how many must be dashed for a stroke to be a line
CROSS = 10          # dashed pixels across a stroke - above this it is text
SOFT = 5            # gap a walk bridges blindly, where two leaders cross
RESUME = 22         # how far ahead a leader may resume after crossing another
HOLD = 6            # of the 10 px beyond a resume, how many must be stroke
JUMP = 18           # widest wall a leader is drawn across
MIN_BRANCH = 12     # a perpendicular shorter than this is not a turn
REACH = 4           # how far past a run's end a corner may sit


def masks(a):
    """(stroke, dark) for a whole screen, computed once

    The walker probes far too many pixels to do this per pixel, and it needs
    both axes because RDC leaders turn corners.
    """
    a = a.astype(float)
    span_x = (ndimage.maximum_filter1d(a, WIN, axis=1)
              - ndimage.minimum_filter1d(a, WIN, axis=1))
    span_y = (ndimage.maximum_filter1d(a, WIN, axis=0)
              - ndimage.minimum_filter1d(a, WIN, axis=0))
    # a pixel is 'dashed' when a short window laid along the axis spans both
    # phases of the dash. counting those, rather than counting dark pixels,
    # is what keeps the faint leaders: their light phase is as pale as the
    # room ground, so a darkness test drops two pixels in every four and the
    # run falls below FILL. Ground has no dash and never enters either count.
    dash_x, dash_y = span_x >= DASH, span_y >= DASH
    ones = np.ones(RUN)
    fill_x = ndimage.convolve1d(dash_x.astype(int), ones, axis=1, mode='constant')
    fill_y = ndimage.convolve1d(dash_y.astype(int), ones, axis=0, mode='constant')
    # a leader is one-dimensional and text is not: a horizontal stroke fills
    # its window along x and almost nothing across it, while a letter fills
    # both. Without this the bold tag printed above each widget reads as
    # stroke, and a walk leaving the widget climbs into its own label.
    m = ((dash_x & (fill_x >= FILL) & (fill_y < CROSS))
         | (dash_y & (fill_y >= FILL) & (fill_x < CROSS)))
    m[:2] = m[-2:] = False
    m[:, :2] = m[:, -2:] = False
    return m, a < DARK


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


def _at_dot(dots, x, y, tol=5):
    if dots is None:
        return None
    for cx, cy in dots.get((x // 4, y // 4), ()):
        if abs(cx - x) <= tol and abs(cy - y) <= tol:
            return cx, cy
    return None


def _probe(m, d, x, y, dx, dy):
    """is the stroke there again ahead, and may the gap be stepped over?

    Two gaps are legitimate. A short one is where another leader crosses ours:
    the crossing point fills the window in both axes, so the text rule above
    removes it and leaves a hole a few pixels wide. A long one is a wall, which
    the leader is drawn across and which reads as dark all the way. A gap of
    bare room ground is neither - it is the end of the leader, and stepping
    over one is how a unit ends up on the leader of the widget next door.
    """
    for i in range(2, JUMP):
        if i > SOFT and not _on(d, y + dy * (i - 1), x + dx * (i - 1)):
            return None
        for s in (0, -1, 1, -2, 2):
            px = x + dx * i + (s if dx == 0 else 0)
            py = y + dy * i + (s if dy == 0 else 0)
            if _on(m, py, px):
                return px, py
    return None


def _resume(m, x, y, dx, dy):
    """does this same leader carry on straight, beyond something crossing it?

    Every screen carries a dashed line marking where the section was cut, run
    the full height of the plan just inside the outer wall, and most leaders
    cross it. At the crossing the stroke fills its window in both axes, so the
    text rule removes it and leaves a hole; the walk then ends there, finds
    that long vertical stroke sideways and turns down it. Five of the twelve
    widgets down the right-hand side finished on the cut line that way.

    So carrying straight on is tried before any turn, and it is only accepted
    when the stroke is still there several pixels later - which a stray mark
    beside the path is not.
    """
    for i in range(SOFT, RESUME):
        for s in (0, -1, 1):
            px = x + dx * i + (s if dx == 0 else 0)
            py = y + dy * i + (s if dy == 0 else 0)
            if not _on(m, py, px):
                continue
            held = sum(1 for j in range(1, 11)
                       if _on(m, py + dy * j, px + dx * j)
                       or _on(m, py + dy * j + (1 if dy == 0 else 0),
                              px + dx * j + (1 if dx == 0 else 0)))
            if held >= HOLD:
                return px, py
    return None


def _straight(m, d, x, y, dx, dy, dots=None, limit=1900):
    """advance along one straight segment, returning every stroke pixel walked"""
    h, w = m.shape
    path = [(x, y)]
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
            hit = _at_dot(dots, x, y)
            if hit and len(path) > 4:
                return hit, path, True
            continue
        # the stroke stopped. a dot sitting just beyond it is the end
        for i in range(1, 8):
            hit = _at_dot(dots, x + dx * i, y + dy * i)
            if hit and len(path) > 4:
                return hit, path, True
        j = _probe(m, d, x, y, dx, dy) or _resume(m, x, y, dx, dy)
        if j is None:
            break
        x, y = j
        path.append((x, y))
    return path[-1], path, False


def _branch(m, x, y, dx, dy, span=28, lead=4):
    """length of the stroke leaving (x,y) sideways, 0 if there is none

    The two strokes of a corner meet at their centres and each is a couple of
    pixels wide, so the perpendicular usually starts two or three pixels away
    rather than immediately. Counting from the first pixel and stopping at the
    first miss therefore scored every real corner zero.
    """
    run = 0
    for i in range(1, span + 1):
        if _on(m, y + dy * i, x + dx * i) or _on(
                m, y + dy * i + (1 if dy == 0 else 0),
                x + dx * i + (1 if dx == 0 else 0)):
            run += 1
        elif run == 0:
            if i > lead:
                break              # nothing leaves here at all
        else:
            break                  # the stroke started and has now ended
    return run


def follow(m, d, x0, y0, dx, dy, dots=None, max_jogs=16):
    """walk a leader from (x0,y0) heading (dx,dy), taking every turn it makes"""
    x, y = x0, y0
    head = (dx, dy)
    for _ in range(max_jogs):
        (x, y), path, done = _straight(m, d, x, y, *head, dots=dots)
        if done:
            return x, y, True
        turn = None
        for px, py in reversed(path):
            best = None
            # the corner sits a pixel or two beyond where the run gave out -
            # the two strokes meet at their centres, not at their ends - so the
            # branch is looked for slightly ahead as well as at the run itself.
            # Without this every leader that turns immediately after leaving its
            # widget was read as having no turn at all, which is most of the top
            # and bottom rows.
            for k in range(REACH):
                qx, qy = px + head[0] * k, py + head[1] * k
                for t in ((head[1], head[0]), (-head[1], -head[0])):
                    n = _branch(m, qx, qy, *t)
                    if n >= MIN_BRANCH and (best is None or n > best[0]):
                        best = (n, t, qx, qy)
                if best:
                    break
            if best:
                turn = (best[2], best[3], best[1])
                break
        if turn is None:
            return x, y, False
        x, y, head = turn
    return x, y, False
