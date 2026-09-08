#!/usr/bin/env python3
"""Write the RDC section - A1.1, A2.3, B2.2 Part1 - onto every RDC row.

    python3 add_section.py --dry-run
    python3 add_section.py

The section is printed in the title bar of the BMS screen and nowhere else, so
the only evidence for a unit's section is which screen carries its tag. The
forty-seven title bars were read into
`../rdc-bms-room-allocation/sections.csv` and every tag printed on every screen
into `screen_tags.csv`; this joins the two onto the register.

The tags do not match as strings - the register writes `RDC_NB_1F_VAV4510` and
the screen `NB-VAV4510`, `RDC_NB_AHU8511` against `NB-AHU-8511` - so the key is
the tag with its `RDC_` prefix, its level segment and every separator removed.
A row whose tag is on no screen takes the section of **its room**, where every
other unit in that room agrees on one. A section is an area of the plan, so the
units in a room are in the same section by construction - this is a second
reading of the same evidence, not an inference. Where the room gives nothing
either, the cell is left blank: the equipment numbers overlap between sections
on every floor, so a unit cannot be placed by its number, and a guess there is
indistinguishable from a reading.
"""
import argparse
import collections
import csv
import re
from pathlib import Path

import openpyxl
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

HERE = Path(__file__).resolve().parent
BMS = HERE.parent / 'rdc-bms-room-allocation'
SRC = HERE / 'All_Buildings_Rooms_Inclusion_Status_V1.3.xlsx'
OUT = HERE / 'All_Buildings_Rooms_Inclusion_Status_V1.4.xlsx'
REPORT = HERE / 'rdc_section_coverage.csv'
TAB = 'RDC Asset Registry'

HEAD_FILL = PatternFill('solid', fgColor='FF2E75B6')
GAP_FILL = PatternFill('solid', fgColor='FFFFF2CC')
WHITE = Font(bold=True, color='FFFFFFFF')
THIN = Side(style='thin', color='FFBFBFBF')
GRID = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)


def key(tag):
    """a tag reduced to what the two sources agree on"""
    t = re.sub(r'^RDC[_-]', '', str(tag).upper())
    t = re.sub(r'[_-](?:GF|1F|2F|MF|L0|B1)(?=[_-])', '', t)
    return re.sub(r'[^A-Z0-9]', '', t)


def primary(tag):
    """(family, number) of the first unit a tag names"""
    m = re.search(r'(AHU|FCU|VAV|CAV|EAV|EV|VEV|CEV|FEV|AT|ERU|EF)[-_]?(\d+)',
                  str(tag).upper())
    return m.groups() if m else None


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--dry-run', action='store_true')
    args = ap.parse_args()

    section = {r['screen']: r['section'] for r in
               csv.DictReader((BMS / 'sections.csv').open())}
    floor = {s: s.split('/')[1] if s.count('/') > 1 else 'GF' for s in section}

    by_key, by_prim = collections.defaultdict(set), collections.defaultdict(set)
    for r in csv.DictReader((BMS / 'screen_tags.csv').open()):
        s = r['screen']
        by_key[key(r['tag'])].add(s)
        p = primary(r['tag'])
        if p:
            by_prim[p].add(s)

    wb = openpyxl.load_workbook(SRC)
    ws = wb[TAB]
    col = ws.max_column + 1
    cell = ws.cell(2, col, 'Section')
    cell.fill, cell.font, cell.border = HEAD_FILL, WHITE, GRID
    cell.alignment = Alignment(vertical='center', wrap_text=True)
    ws.column_dimensions[get_column_letter(col)].width = 16
    ws.cell(1, col).fill = PatternFill('solid', fgColor='FF1F4E79')

    # pass one: the tag. pass two: the room, from what pass one settled.
    decided = {}
    for phase in (1, 2):
      room_sec = collections.defaultdict(collections.Counter)
      if phase == 2:
        for rr, (v, _) in decided.items():
            room = str(ws.cell(rr, 4).value or '').strip().upper()
            if v and room:
                room_sec[room][v] += 1
      how = collections.Counter()
      report = []
      for r in range(3, ws.max_row + 1):
        tag = str(ws.cell(r, 1).value or '').strip()
        if not tag:
            continue
        if phase == 2 and decided.get(r, ('', ''))[0]:
            v, note = decided[r]
            how['read from the screen'] += 1
            report.append([tag, str(ws.cell(r, 4).value or ''), v, note])
            continue
        if phase == 2:
            room = str(ws.cell(r, 4).value or '').strip().upper()
            got = room_sec.get(room)
            if got and len(got) == 1:
                v = next(iter(got))
                ws.cell(r, col, v)
                ws.cell(r, col).fill = PatternFill()
                how['taken from its room'] += 1
                report.append([tag, str(ws.cell(r, 4).value or ''), v,
                               'every other unit in this room is in %s' % v])
                continue
            how['left blank'] += 1
            report.append([tag, str(ws.cell(r, 4).value or ''), '',
                           decided.get(r, ('', 'no evidence'))[1]])
            continue
        screens = by_key.get(key(tag))
        route = 'tag'
        if not screens:
            p = primary(tag)
            screens = by_prim.get(p) if p else None
            route = 'first unit in the tag'
        secs = sorted({section[s] for s in screens}) if screens else []
        base = sorted({s.split(' Part')[0] for s in secs})
        if len(secs) == 1:
            value, note = secs[0], route
        elif len(base) == 1 and secs:
            value, note = base[0], '%s - on %d parts of the section' % (route, len(secs))
        elif secs:
            value, note = '', 'on %d sections: %s' % (len(secs), ', '.join(secs))
        else:
            value, note = '', 'its tag is on no screen'
        ws.cell(r, col, value or None).alignment = Alignment(vertical='top',
                                                             wrap_text=True)
        ws.cell(r, col).border = GRID
        if not value:
            ws.cell(r, col).fill = GAP_FILL
        decided[r] = (value, note)
        how['read from the screen' if value else 'left blank'] += 1
        report.append([tag, str(ws.cell(r, 4).value or ''), value, note])

    print('RDC rows %d' % sum(how.values()))
    for k, n in how.most_common():
        print('  %-24s %5d' % (k, n))
    print('  %s' % dict(collections.Counter(
        r[3] for r in report if not r[2])))
    counts = collections.Counter(r[2] for r in report if r[2])
    print('\nsections found:')
    for s, n in sorted(counts.items()):
        print('  %-18s %4d' % (s, n))

    with REPORT.open('w', newline='') as f:
        w = csv.writer(f, lineterminator='\n')
        w.writerow(['tag', 'room', 'section', 'how it was decided'])
        w.writerows(report)
    print('\nwrote %s' % REPORT.name)
    if args.dry_run:
        return
    ws.auto_filter.ref = 'A2:%s%d' % (get_column_letter(col), ws.max_row)
    wb.save(OUT)
    print('wrote %s' % OUT.name)


if __name__ == '__main__':
    main()
