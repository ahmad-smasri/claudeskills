#!/usr/bin/env python3
"""Lay the tag printed above each unit out in a numbered grid, to be read.

The strips annotate.py writes are one per row, which for a screen carrying
forty units is a picture two thousand pixels tall - awkward to read and easy to
lose your place in. This puts them in columns instead, in the same numbering as
the annotated screen, so the number a marker carries can be turned into a tag
without counting rows.
"""
import json
import sys

from PIL import Image, ImageDraw

import numpy as np
import rdc_widgets as W

src, out = sys.argv[1], sys.argv[2]
cols = int(sys.argv[3]) if len(sys.argv) > 3 else 3

im = Image.open(src).convert('RGB')
rgb = np.array(im, dtype=int)
grey = np.array(im.convert('L'), dtype=int)
units = W.find(rgb, grey)

S, CW, CH, GUT = 2, 232, 26, 34
rows = (len(units) + cols - 1) // cols
sheet = Image.new('RGB', (cols * (CW * S + GUT), rows * (CH * S + 6) + 4), 'white')
d = ImageDraw.Draw(sheet)
for i, u in enumerate(units):
    cx, cy = i // rows, i % rows
    x0 = max(0, u['left'] - 18)
    y0 = max(0, u['top'] - W.LABEL_UP - 2)
    tile = im.crop((x0, y0, x0 + CW, y0 + CH)).resize((CW * S, CH * S),
                                                      Image.LANCZOS)
    px = cx * (CW * S + GUT)
    py = cy * (CH * S + 6) + 2
    sheet.paste(tile, (px + GUT, py))
    d.text((px + 4, py + 18), '%d' % (i + 1), fill=(200, 0, 0))
sheet.save(out)
print(out, sheet.size, len(units), 'units')
