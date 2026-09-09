#!/usr/bin/env python3
"""Find every tag printed on a screen from the text itself, not from its widget.

    python3 tag_text.py out/missed

`rdc_widgets.py` finds a unit by its box - a red alarm badge or a bordered white
rectangle - and a box that another graphic overlaps is a box it does not find.
That cost 108 of the register's 1,141 RDC units their section.

The tag does not depend on the box. It is near-black text on the light screen
background, one line, always above its unit, and every one begins `NB-`, `SB-`,
`UB-` or `Walkway-`. So this thresholds the dark pixels, closes them
horizontally into words and then into lines, and keeps every line shaped like a
tag. Lines already accounted for by a detected widget are dropped, and what is
left is packed into sheets to be read - the tags the box detector missed.
"""
import glob
import os
import sys

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

import rdc_widgets as W

OUT = sys.argv[1] if len(sys.argv) > 1 else 'out/missed'
DARK = 110              # the tag is near-black; the plan is grey
GAP = 9                 # close this far to join letters into a word, words into a line
MINW, MAXW = 55, 340    # a tag line, in pixels
MINH, MAXH = 7, 17
ROWS, COLS = 26, 3
CW, CH, S, HEAD = 250, 24, 2, 22


TOP, BOT = 88, 842      # the plan area, between the menu bar and the alarm pane


def lines(grey, rgb):
    """bounding boxes of every dark neutral text line inside the plan area

    Neutral because the alarm pane below the plan is blue on yellow and the
    Wonderware mark is teal; a tag is black on the grey plan.
    """
    spread = (rgb.max(axis=2) - rgb.min(axis=2))
    dark = (grey < DARK) & (spread < 40)
    closed = ndimage.binary_closing(dark, np.ones((1, GAP)))
    lab, n = ndimage.label(closed, np.ones((3, 3)))
    out = []
    for y, x in ndimage.find_objects(lab):
        h, w = y.stop - y.start, x.stop - x.start
        if (MINH <= h <= MAXH and MINW <= w <= MAXW
                and TOP <= y.start and y.stop <= BOT):
            out.append((y.start, x.start, y.stop, x.stop))
    return out


def main():
    os.makedirs(OUT, exist_ok=True)
    columns = []
    for n, path in enumerate(sorted(glob.glob('screens/RDC/**/*.jpg', recursive=True)), 1):
        im = Image.open(path).convert('RGB')
        rgb = np.array(im, dtype=int)
        grey = np.array(im.convert('L'), dtype=int)
        known = [(u['top'] - W.LABEL_UP, u['left']) for u in W.find(rgb, grey)]
        found = lines(grey, rgb)
        new = []
        for y0, x0, y1, x1 in found:
            if any(abs(ky - y0) < 12 and x0 - 90 < kx < x1 + 90 for ky, kx in known):
                continue
            new.append((y0, x0, y1, x1))
        label = path[len('screens/RDC/'):-4]
        print('  %2d  %-42s %3d widgets, %3d text lines, %3d not on a widget'
              % (n, label, len(known), len(found), len(new)))
        tiles = [im.crop((max(0, x0 - 6), max(0, y0 - 5),
                          max(0, x0 - 6) + CW, max(0, y0 - 5) + CH))
                   .resize((CW * S, CH * S), Image.LANCZOS)
                 for y0, x0, y1, x1 in sorted(new)]
        for i in range(0, len(tiles), ROWS):
            columns.append(('%d. %s [%d-%d]'
                            % (n, label, i + 1, min(i + ROWS, len(tiles))),
                            tiles[i:i + ROWS], i))

    W_COL = CW * S + 34
    for s in range(0, len(columns), COLS):
        grp = columns[s:s + COLS]
        tall = max(len(t) for _, t, _ in grp)
        sheet = Image.new('RGB', (W_COL * len(grp), HEAD + tall * (CH * S + 4) + 4),
                          'white')
        d = ImageDraw.Draw(sheet)
        for c, (label, tiles, off) in enumerate(grp):
            x = c * W_COL
            d.text((x + 4, 6), label, fill=(0, 0, 160))
            for r, t in enumerate(tiles):
                y = HEAD + r * (CH * S + 4)
                sheet.paste(t, (x + 34, y))
                d.text((x + 4, y + 16), '%d' % (off + r + 1), fill=(200, 0, 0))
        sheet.save('%s/sheet%02d.png' % (OUT, s // COLS))
    print('wrote %d sheets to %s' % ((len(columns) + COLS - 1) // COLS, OUT))


if __name__ == '__main__':
    main()
