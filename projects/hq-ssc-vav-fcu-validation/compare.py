import re
from collections import Counter, defaultdict
from load import *

def norm_ref(x):
    x = str(x or '').strip().upper().replace(' ', '')
    m = re.match(r'^(VAV|FCU|AHU)/([A-Z0-9]+)/(\d+)$', x)
    return (m.group(1), m.group(2).lstrip('0') or '0', int(m.group(3))) if m else None

src = sources()
reg = registry()

sbytag = {}
sbyref = {}
for s in src:
    sbytag[(s['building'], norm_tag(s['tag']))] = s
    if norm_ref(s['ref']):
        sbyref[(s['building'], norm_ref(s['ref']))] = s

# level style per section, for formatting a new number
def fmt_num(sec, num):
    """render the source room number in the registry's style, digits kept verbatim"""
    n = ' '.join(str(num or '').split()).upper()
    if '.' not in n:
        return re.sub(r'^L(?=(\d+|G)$)', '', n)
    lvl, rest = n.split('.', 1)
    lvl = lvl.lstrip('L') or lvl
    if lvl.startswith('B'):
        lvl = 'B'
    return '%s.%s' % (lvl, rest)

results = []
for r in reg:
    if r['type'] not in ('VAV', 'FCU') or r['sec'] not in ('HQ', 'SSC'):
        continue
    s = sbytag.get((r['sec'], norm_tag(r['tag'])))
    via = 'tag'
    if s is None:
        s = sbyref.get((r['sec'], norm_ref(r['tag'])))
        via = 'ref'
    rec = dict(r); rec['via'] = via; rec['src'] = s
    if s is None:
        rec['status'] = 'NO_SOURCE_ROW'
        results.append(rec); continue
    d = '' if r['D'] is None else str(r['D']).strip()
    dname, dnum = split_D(d) if d else ('', None)
    snum, sname = s['room_no'].strip(), ' '.join(s['room_name'].split())
    rec.update(d=d, dname=dname, dnum=dnum, snum=snum, sname=sname)
    if not snum and not sname:
        rec['status'] = 'SOURCE_BLANK'
    elif not d:
        rec['status'] = 'REGISTRY_BLANK'
    else:
        num_same = (norm_num(dnum) == norm_num(snum)) if (dnum and snum) else None
        name_same = norm_name(dname) == norm_name(sname) if sname else None
        rec['num_same'], rec['name_same'] = num_same, name_same
        if num_same is False and name_same is False:
            rec['status'] = 'DIFF_BOTH'
        elif num_same is False:
            rec['status'] = 'DIFF_NUMBER'
        elif name_same is False:
            rec['status'] = 'DIFF_NAME'
        elif num_same is None and name_same is False:
            rec['status'] = 'DIFF_NAME'
        elif num_same is None or name_same is None:
            rec['status'] = 'PARTIAL_MATCH'
        else:
            rec['status'] = 'MATCH'
    results.append(rec)

def new_value(rec):
    """the corrected column-D value, written in the registry's own format.

    The room number is only re-rendered when it actually changed; otherwise the
    token already in column D is kept, so H differs from D in the name alone."""
    s = rec['src']
    name = ' '.join(s['room_name'].split()).upper()
    if not name:
        name = rec.get('dname') or ''        # source gives only a number - keep the existing name
    if rec.get('num_same') and rec.get('dnum'):
        num = rec['dnum']
    elif s['room_no'].strip():
        num = fmt_num(rec['sec'], s['room_no'])
    else:
        num = rec.get('dnum') or ''
    if num and norm_name(num) and norm_name(num) in norm_name(name):
        num = ''          # source room 'number' is really the name again (e.g. PLANT ROOM SE)
    return (name + ' ' + num).strip() if (name or num) else ''
