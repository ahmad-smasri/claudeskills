#!/usr/bin/env python3
"""Every tag printed on every RDC screen, packed into sheets to be read.

    python3 tag_sheets.py out/sections

The section a unit sits in - A1.1, A2.3, B2.2 Part1 - is printed in the title
bar of the screen it appears on and nowhere else, so the only way to give a
register row its section is to know which screen carries its tag. `tags.py`
lays one screen out at a time; this lays all forty-seven out together, narrow
enough that three screens fit side by side, so the whole building is a dozen
reads rather than forty-seven.

Each column is one screen, numbered down the left, with the screen's own number
in the header so a tag can be traced back to the image it came from.
"""
import glob
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

import rdc_widgets as W

OUT = sys.argv[1] if len(sys.argv) > 1 else 'out/sections'
CW, CH, S = 250, 24, 2          # crop width, height, and the scale to read at
LEFT = 62                       # the tag is centred over the widget and runs left of it
ROWS, COLS = 26, 3              # per sheet
HEAD = 22

os.makedirs(OUT, exist_ok=True)
screens = sorted(glob.glob('screens/RDC/**/*.jpg', recursive=True))
print('%d screens' % len(screens))

columns = []                    # (label, [tag crops])
for n, path in enumerate(screens, 1):
    im = Image.open(path).convert('RGB')
    units = W.find(np.array(im, dtype=int), np.array(im.convert('L'), dtype=int))
    tiles = []
    for u in units:
        x0 = max(0, u['left'] - LEFT)
        y0 = max(0, u['top'] - W.LABEL_UP - 2)
        tiles.append(im.crop((x0, y0, x0 + CW, y0 + CH))
                       .resize((CW * S, CH * S), Image.LANCZOS))
    label = path[len('screens/RDC/'):-4]
    print('  %2d  %-42s %3d units' % (n, label, len(tiles)))
    for i in range(0, len(tiles), ROWS):
        columns.append(('%d. %s [%d-%d]' % (n, label, i + 1, min(i + ROWS, len(tiles))),
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
