import sys
from PIL import Image
# usage: crop.py <img> <x1> <y1> <x2> <y2> <scale> <out>
src, x1, y1, x2, y2, sc, out = sys.argv[1:8]
im = Image.open(src).crop((int(x1), int(y1), int(x2), int(y2)))
sc = float(sc)
im = im.resize((int(im.width * sc), int(im.height * sc)), Image.LANCZOS)
im.save(out)
print(out, im.size)
