#!/usr/bin/env python3
"""Crop and upscale a region of a screen, to check a leader by eye."""
import sys
from PIL import Image

src, out = sys.argv[1], sys.argv[2]
x, y, w, h = map(int, sys.argv[3:7])
scale = int(sys.argv[7]) if len(sys.argv) > 7 else 3
im = Image.open(src).crop((x, y, x + w, y + h))
im = im.resize((im.width * scale, im.height * scale), Image.LANCZOS)
im.save(out)
print(out, im.size)
