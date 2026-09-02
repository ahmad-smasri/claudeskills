"""Crop the tag printed above each widget into one numbered strip.

Reading thirty tags off a full screen means thirty separate zooms; reading them
off one tall strip, in the same order the annotated image numbers them, means
one. The numbering matches `annotate_qnl.py` exactly - both sort the widgets by
(left, y) - so the strip binds widget number to tag and the annotated image
binds widget number to room.
"""
import sys
from PIL import Image, ImageDraw
import trace as T

SCALE = 2
CROP_W, CROP_H = 200, 22


def strips(path, out, per_col=20):
    a = T.load(path)
    im = Image.open(path).convert('RGB')
    bars = sorted([w for w in T.find_widgets(a) if 60 < w['y'] < 770],
                  key=lambda b: (b['left'], b['y']))
    cw, ch = (CROP_W + 46) * SCALE, CROP_H * SCALE + 6
    cols = (len(bars) + per_col - 1) // per_col or 1
    sheet = Image.new('RGB', (cw * cols, ch * min(per_col, len(bars))), 'white')
    d = ImageDraw.Draw(sheet)
    for i, w in enumerate(bars):
        box = (max(0, w['left'] - 24), max(0, w['y'] - 34),
               max(0, w['left'] - 24) + CROP_W, max(0, w['y'] - 34) + CROP_H)
        crop = im.crop(box).resize((CROP_W * SCALE, CROP_H * SCALE), Image.LANCZOS)
        x, y = cw * (i // per_col), ch * (i % per_col)
        sheet.paste(crop, (x + 46 * SCALE, y + 3))
        d.text((x + 6, y + 12), '%d' % (i + 1), fill=(200, 0, 0))
    sheet.save(out)
    print(out, len(bars), 'widgets')


if __name__ == '__main__':
    strips(sys.argv[1], sys.argv[2])
