"""What the SSC and HQ BMS screens said, for equipment other than AHU/VAV/FCU.

The readings live in `../bms-room-allocation/*_alloc.py`, written by the pass
that followed the serving-area leaders on those screens. This only harvests
them; the screen images themselves are not in the repo.
"""
import glob
import importlib
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, '..', 'bms-room-allocation')
SKIP = re.compile(r'^(VAV|FCU|AHU)', re.I)


def readings():
    """{tag: (building, room, screen, confidence)} for the non AHU/VAV/FCU units

    The building matters: `DX-B-0001` exists in both ontologies, so a reading
    taken off an SSC screen must not be matched against an HQ entity.
    """
    sys.path.insert(0, SRC)
    out = {}
    for f in sorted(glob.glob(os.path.join(SRC, '*_alloc.py'))):
        name_ = os.path.basename(f)[:-3]
        building = 'SSC' if name_.startswith('ssc') else 'HQ'
        mod = importlib.import_module(name_)
        for name in dir(mod):
            v = getattr(mod, name)
            if not (isinstance(v, list) and v and isinstance(v[0], tuple)):
                continue
            for row in v:
                if len(row) < 3 or SKIP.match(str(row[0])):
                    continue
                tag = str(row[0])
                # a tag can appear in two lists; the more confident wins
                conf = row[3] if len(row) > 3 else ''
                if tag in out and out[tag][3] == 'ok':
                    continue
                out[tag] = (building, str(row[1]), str(row[2]), conf)
    return out


def key(tag):
    """normalise a tag so the screen and the ontology spell it the same way

    `DX-B-0001` is `DXB0001`, `CCU-B-005B` is `CCUB0005B` - the screens pad
    the number to three digits and the ontology to four - and `KEF-1F-0103`
    is `KEF0103`, the ontology having dropped the level segment.
    """
    def pad(segs):
        out = []
        for s in segs:
            out.append(''.join(p if p.isalpha() else '%04d' % int(p)
                               for p in re.findall(r'[A-Z]+|\d+', s)))
        return ''.join(out)

    segs = [s for s in re.split(r'[^A-Za-z0-9]+', tag.upper()) if s]
    # the level segment is written on the screen and dropped in the ontology
    thin = [s for s in segs if not re.fullmatch(r'B|\d+F|L\d+', s)]
    return pad(segs), pad(thin)
