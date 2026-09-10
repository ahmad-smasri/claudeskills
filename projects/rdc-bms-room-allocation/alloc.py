"""What each RDC screen shows, read off the annotated images by eye.

The readings live in `readings.csv` and `blanks.csv` beside this module, one row
each, because they are data and they grow a screen at a time. They were held in
a Python literal at first and edited by patching the text of this file, which
put one screen's readings into both dictionaries at once - a `str.replace` hits
every occurrence, and the screen key appears in both. A CSV row cannot land in
the wrong table.

readings.csv  screen, tag, room, confidence, note
    tag         the label printed above the widget, as the screen writes it
    room        the room the leader's dot lands in, as the screen names it
    confidence  'ok'    the dot sits clearly inside one named room
                'check' the endpoint is inside the room but the walk ran out
                        before reaching a dot, or the dot sits on a boundary
    note        anything a reviewer needs in order to judge the reading

blanks.csv    screen, tag, reason
    The other half, and it matters as much: a unit whose room could not be read,
    and why. A blank row with a reason is a question for the client; a guessed
    room is indistinguishable from a reading once it is in the sheet.

The screen key is the path under `screens/RDC/`, which also gives the level:
`North Building/FF` is the north building's first floor, so a tag read there
joins the register as `RDC_NB_1F_<tag>`.
"""
import collections
import csv
import pathlib

HERE = pathlib.Path(__file__).resolve().parent


def _load(name, fields):
    path = HERE / name
    if not path.exists():
        return {}
    out = collections.defaultdict(list)
    with path.open(newline='') as f:
        r = csv.DictReader(f)
        missing = set(fields) - set(r.fieldnames or ())
        if missing:
            raise SystemExit('%s is missing columns %s' % (name, sorted(missing)))
        for row in r:
            if not row['tag'].strip():
                continue
            out[row['screen']].append(tuple(row[k].strip() for k in fields))
    return dict(out)


SCREENS = _load('readings.csv', ('tag', 'room', 'confidence', 'note'))
BLANK = _load('blanks.csv', ('tag', 'reason'))
