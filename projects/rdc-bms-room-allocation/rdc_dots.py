"""Find the grey dot that ends an RDC serving-area leader.

Every leader on the RDC screens finishes in a small filled grey circle inside
the room it serves. The circle is drawn at the same grey as the walls - about
152 on a room ground of 239 - so brightness alone cannot tell the two apart and
the discriminator has to be shape: a dot is a compact blob four to thirty pixels
across, inside a bounding box no bigger than 6x6, and reasonably round.

That test alone also matches the dot on an `i`, the bulbs of the lighting icons
and any small piece of a room name, so this returns candidates rather than
answers. A candidate only becomes a reading when a leader actually walks into
it - `rdc_trace.follow` is what confirms it.
"""
import numpy as np
from scipy import ndimage

DARK = 166         # below this is wall, dot, text - above is ground or leader
BOX = 6            # widest bounding box a dot is drawn in
MIN, MAX = 4, 30   # pixel count of the blob itself
ROUND = 0.45       # filled fraction of the bounding box


def dark(a):
    return a < DARK


def find(a):
    """(x, y) centres of every dot-shaped dark blob on the screen"""
    d = dark(a)
    lab, n = ndimage.label(d, structure=np.ones((3, 3)))
    if not n:
        return []
    sizes = ndimage.sum(d, lab, range(1, n + 1))
    out = []
    for i, sl in enumerate(ndimage.find_objects(lab), 1):
        size = sizes[i - 1]
        if not (MIN <= size <= MAX):
            continue
        h = sl[0].stop - sl[0].start
        w = sl[1].stop - sl[1].start
        if h > BOX or w > BOX:
            continue
        if size < ROUND * h * w:
            continue
        ys, xs = np.nonzero(lab[sl] == i)
        out.append((int(sl[1].start + xs.mean().round()),
                    int(sl[0].start + ys.mean().round())))
    return out
