"""Find the unit widgets on an RDC screen, and the label printed above each.

Two families are drawn, and both have to be found or a screen comes back empty.

A **slider** is a short black vertical bar with a bordered white box running to
its right. A red cross badge sits in the box when the unit is in alarm, and the
first version of this anchored on that cross - which found every unit in alarm
and no other, so the five screens whose units are all healthy reported nothing
at all. The box itself is the invariant: white inside, a thin grey rule above
and below, forty to a hundred and ten pixels long. Some sliders also carry a
grey stub left of the bar and some do not, so the stub cannot be part of the
test either - requiring one found two of the twelve widgets down the right-hand
side of the first screen tried.

An **icon** is a filled grey tile about seventy pixels square - the energy
recovery units, the exhaust fans and the plant. A fan's blade is drawn in the
same grey as the tile and splits it into two components, so tiles that abut are
merged back together.

The tag is printed in bold directly above both kinds. That is what makes RDC
easier to read than QNL, where the tag had to be recovered from a strip and
matched back to the register by position - here `strip()` crops it to be read.
"""
import numpy as np
from scipy import ndimage

BLACK = 90                    # the slider's vertical bar
BAR_H = (8, 24)               # and its height
BAR_W = 6                     # and its width
ALARM_W = 40                  # a unit in alarm is boxed in red, and that box's
                              # border joins the bar into one wide component
BOX_MIN, BOX_MAX = 38, 115    # the white box, measured from the bar
LIGHT = 225                   # inside the box
RULE = (140, 220)             # the grey rule above and below it

TILE = (120, 175)             # the fill grey of an equipment tile
TILE_SIDE = (44, 86)          # and its side, in pixels
TILE_MIN = 1200               # smallest piece of a tile worth keeping

LABEL_UP = 24
LABEL_H = 20


def _boxed(grey, y, bar):
    """is there a bordered white box right of this bar?

    Every column across the box is tested and a majority has to agree, rather
    than one or two fixed offsets. The cross badge sits at no fixed place along
    the box, so a fixed offset lands on it for some units and not others, and
    testing two offsets and requiring both rejected a third of the real sliders
    - the ones whose badge happened to fall under the probe.
    """
    h, w = grey.shape
    good = 0
    for x in range(bar + 8, min(w, bar + 38)):
        if grey[y, x] < LIGHT:
            continue
        up = any(RULE[0] <= grey[r, x] <= RULE[1]
                 for r in range(y - 1, max(-1, y - 12), -1))
        dn = any(RULE[0] <= grey[r, x] <= RULE[1]
                 for r in range(y + 1, min(h, y + 12)))
        if up and dn:
            good += 1
    return good >= 12


def _right(grey, y, bar):
    """the box's own right border - assuming a width erases what lies beyond"""
    for dx in range(BOX_MIN, BOX_MAX):
        if bar + dx + 1 >= grey.shape[1]:
            break
        if grey[y, bar + dx] < 205:
            return bar + dx
    return bar + BOX_MIN


def sliders(grey, top=58, bottom=800):
    dark = grey < BLACK
    dark[:top] = False
    dark[bottom:] = False
    lab, n = ndimage.label(dark, structure=np.ones((3, 3)))
    out = []
    for sl in ndimage.find_objects(lab):
        h, w = sl[0].stop - sl[0].start, sl[1].stop - sl[1].start
        if not BAR_H[0] <= h <= BAR_H[1]:
            continue
        if w > BAR_W and w < ALARM_W:
            continue          # a letter of the page title, or part of an icon
        y = (sl[0].start + sl[0].stop) // 2
        if not _boxed(grey, y, sl[1].start):
            continue
        out.append({'kind': 'slider', 'y': y, 'left': sl[1].start - 2,
                    'right': _right(grey, y, sl[1].start),
                    'top': sl[0].start, 'bottom': sl[0].stop})
    return out


def icons(grey, top=58, bottom=800):
    fill = (grey >= TILE[0]) & (grey <= TILE[1])
    fill[:top] = False
    fill[bottom:] = False
    lab, n = ndimage.label(fill, structure=np.ones((3, 3)))
    sizes = ndimage.sum(fill, lab, range(1, n + 1))
    boxes = []
    for i, sl in enumerate(ndimage.find_objects(lab), 1):
        h, w = sl[0].stop - sl[0].start, sl[1].stop - sl[1].start
        if sizes[i - 1] < TILE_MIN:
            continue
        if not (TILE_SIDE[0] <= h <= TILE_SIDE[1] and TILE_SIDE[0] <= w <= TILE_SIDE[1]):
            continue
        boxes.append([sl[1].start, sl[0].start, sl[1].stop, sl[0].stop])
    # a fan blade is drawn in the tile's own grey and cuts it in two
    merged = []
    for b in sorted(boxes):
        if merged and (b[0] <= merged[-1][2] + 3 and b[1] <= merged[-1][3] + 3
                       and b[3] >= merged[-1][1] - 3):
            m = merged[-1]
            merged[-1] = [min(m[0], b[0]), min(m[1], b[1]),
                          max(m[2], b[2]), max(m[3], b[3])]
        else:
            merged.append(list(b))
    return [{'kind': 'icon', 'left': x0, 'top': y0, 'right': x1, 'bottom': y1,
             'y': (y0 + y1) // 2} for x0, y0, x1, y1 in merged]


def crosses(rgb):
    """(x, y) centre of every red cross badge - a unit drawn in alarm"""
    r, g, b = rgb[:, :, 0], rgb[:, :, 1], rgb[:, :, 2]
    red = (r > 120) & (r - g > 50) & (r - b > 50)
    lab, n = ndimage.label(red, structure=np.ones((3, 3)))
    if not n:
        return []
    sizes = ndimage.sum(red, lab, range(1, n + 1))
    out = []
    for i, sl in enumerate(ndimage.find_objects(lab), 1):
        h, w = sl[0].stop - sl[0].start, sl[1].stop - sl[1].start
        if 45 <= sizes[i - 1] <= 110 and 6 <= h <= 14 and 6 <= w <= 14:
            out.append(((sl[1].start + sl[1].stop) // 2,
                        (sl[0].start + sl[0].stop) // 2))
    return out


def _from_cross(grey, x, y):
    """the widget around a cross badge, found by walking left to its bar"""
    best = None
    for dx in range(6, 70):
        col = x - dx
        if col < 2:
            break
        run = [r for r in range(max(0, y - 12), min(grey.shape[0], y + 13))
               if grey[r, col] < BLACK]
        if len(run) >= 8:
            best = (col, min(run), max(run) + 1)
    if best is None:
        return None
    col, y0, y1 = best
    mid = (y0 + y1) // 2
    return {'kind': 'slider', 'y': mid, 'left': col - 2,
            'right': _right(grey, mid, col), 'top': y0, 'bottom': y1}


def find(rgb, grey, top=58, bottom=800):
    """every unit on the screen, sorted the way a reader scans

    Two slider detectors, because neither finds them all. The structural one
    wants an unobstructed box and loses units whose box is partly covered; the
    cross one only sees units in alarm. Their union, deduplicated by position,
    finds more than either - on the ground-floor screens the union is a third
    larger than the structural pass alone.
    """
    out = sliders(grey, top, bottom)
    seen = {(w['left'] // 8, w['y'] // 8) for w in out}
    for x, y in crosses(rgb):
        if not (top <= y < bottom):
            continue
        w = _from_cross(grey, x, y)
        if w is None:
            continue
        key = (w['left'] // 8, w['y'] // 8)
        near = any(abs(w['left'] - o['left']) < 12 and abs(w['y'] - o['y']) < 10
                   for o in out)
        if near or key in seen:
            continue
        seen.add(key)
        out.append(w)
    out += icons(grey, top, bottom)
    out.sort(key=lambda w: (w['left'], w['y']))
    return out


def strip(im, w, scale=2, pad=8):
    """the label above one unit, upscaled enough to read"""
    x0 = max(0, w['left'] - pad)
    y0 = max(0, w['top'] - LABEL_UP)
    box = im.crop((x0, y0, min(im.width, x0 + 240), y0 + LABEL_H))
    return box.resize((box.width * scale, box.height * scale))
