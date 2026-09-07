#!/usr/bin/env python3
"""Write the agreed room name into column D of the Controllable Asset Registry.

    python3 update_rooms.py            # write the workbook
    python3 update_rooms.py --dry-run  # say what would change, write nothing

Column D is `ROOM NAME AS PER DRAWINGS`, and for three of the four buildings the
drawings were not the last word: the room was settled against the BMS screens
and the delivered ontology, and the answer is in `Room_Names_4.xlsx`. This puts
that answer back into the register so there is one room name per asset rather
than four columns disagreeing.

Where each section's name comes from:

  HQ, QNL, SSC   `Room_Names_4.xlsx`, column M `rdfs:label_en` - the name chosen
                 after validating column D against the BMS screens and the
                 existing ontology. Column N on that sheet records which source
                 won, row by row. A row whose `rdfs:label_en` is empty is left
                 exactly as it is: 90 rows across the three, where no source
                 settled the room.

  RDC            `RDC_reviewed.xlsx`, column J, on the rows filled green - the
                 32 the client kept after reviewing the 215 this pass flagged.
                 The other 183 readings were rejected and their column J
                 cleared, so green is the whole instruction and column J on a
                 row that is not green is not.

**The workbook is edited as XML inside the zip, not through openpyxl.** It
carries cell comments, a web-extension task pane, a calculation chain and
spilling formulas, and a round trip through openpyxl drops them. Only the cells
that change are touched; every other byte of the sheet is the file's own.
"""
import argparse
import collections
import csv
import re
import shutil
import sys
import zipfile
from pathlib import Path

import openpyxl

HERE = Path(__file__).resolve().parent
MASTER = (HERE.parent / 'qnl-bms-room-allocation'
          / 'Appendix_A_Asset_Register_QNL_BMS_rooms.xlsx')
NAMES = HERE / 'Room_Names_4.xlsx'
RDC = HERE / 'RDC_reviewed.xlsx'
OUT = HERE / 'Appendix_A_Asset_Register_rooms_updated.xlsx'
CROSSWALK = HERE / 'room_name_changes.csv'

SHEET = 'xl/worksheets/sheet6.xml'      # Controllable Asset Registry
GREEN = 'FF00B050'
NAME_COL, WHY_COL = 13, 14              # M rdfs:label_en, N Chosen from
SECTIONS = (('HQ', 3, 764), ('QNL', 765, 1316), ('SSC', 1317, 1441),
            ('RDC', 1442, 3201))


def chosen():
    """(building, tag) -> (room name, which source it came from)"""
    wb = openpyxl.load_workbook(NAMES, data_only=True)
    out = {}
    for name in wb.sheetnames:
        ws = wb[name]
        head = [str(ws.cell(1, c).value or '') for c in range(1, ws.max_column + 1)]
        if 'rdfs:label_en' not in head:
            sys.exit('%s sheet %s has no rdfs:label_en column' % (NAMES.name, name))
        col = head.index('rdfs:label_en') + 1
        why = head.index('Chosen from') + 1 if 'Chosen from' in head else None
        for r in range(2, ws.max_row + 1):
            tag = str(ws.cell(r, 1).value or '').strip()
            room = str(ws.cell(r, col).value or '').strip()
            if tag and room:
                out[(name, tag)] = (room, str(ws.cell(r, why).value or '').strip()
                                    if why else '')
    return out


def rdc_green():
    """tag -> room, for the RDC rows the client kept green"""
    ws = openpyxl.load_workbook(RDC, data_only=True)['Controllable Asset Registry']
    out = {}
    for r in range(3, ws.max_row + 1):
        cell = ws.cell(r, 1)
        if cell.fill.patternType != 'solid':
            continue
        if str(cell.fill.fgColor.rgb) != GREEN:
            continue
        room = str(ws.cell(r, 10).value or '').strip()
        tag = str(cell.value or '').strip()
        if tag and room:
            out[tag] = (room, 'J (green)')
    return out


def wanted():
    """row number in the registry sheet -> (tag, old room, new room, source)"""
    pick = chosen()
    green = rdc_green()
    ws = openpyxl.load_workbook(MASTER, read_only=True, data_only=True)[
        'Controllable Asset Registry']
    rows = list(ws.iter_rows(min_row=1, max_row=3202, max_col=4, values_only=True))
    out = {}
    for building, first, last in SECTIONS:
        for i, row in enumerate(rows, 1):
            if not (first < i <= last) or not row[0]:
                continue
            tag = str(row[0]).strip()
            old = str(row[3] or '').strip()
            hit = green.get(tag) if building == 'RDC' else pick.get((building, tag))
            if not hit:
                continue
            new, why = hit
            if new != old:
                out[i] = (building, tag, old, new, why)
    return out


def sheet_xml(zf):
    return zf.read(SHEET).decode('utf8')


def rewrite(xml, changes):
    """replace column D on the named rows with an inline string

    Inline rather than a shared string: the value goes in the cell itself, so
    nothing has to be added to sharedStrings.xml and no other cell that happens
    to share the old string is touched.

    The cell's attributes are not in a fixed order - this sheet writes both
    `<c r="D5" s="45">` and `<c s="45" r="D5">` - so the reference is pulled out
    of the attributes rather than matched by position. Assuming the order cost
    three rows on the first run, which reported as missing cells that were
    there all along. Every attribute except `t` is carried over, so the cell
    keeps its style.
    """
    done = set()
    ref = re.compile(r'\br="([A-Z]+)(\d+)"')

    def cell(m):
        attrs = m.group('attrs')
        got = ref.search(attrs)
        if not got or got.group(1) != 'D':
            return m.group(0)
        row = int(got.group(2))
        if row not in changes:
            return m.group(0)
        done.add(row)
        keep = re.sub(r'\st="[^"]*"', '', attrs).rstrip()
        text = (changes[row][3].replace('&', '&amp;').replace('<', '&lt;')
                .replace('>', '&gt;'))
        space = ' xml:space="preserve"' if text != text.strip() else ''
        return '<c %s t="inlineStr"><is><t%s>%s</t></is></c>' % (
            keep, space, text)

    pattern = re.compile(r'<c (?P<attrs>[^>]*?)(?:/>|>.*?</c>)', re.S)
    xml = pattern.sub(cell, xml)
    missing = set(changes) - done
    if missing:
        sys.exit('rows %s have no D cell in the sheet - nothing was written'
                 % sorted(missing)[:10])
    return xml


def room_number(text):
    """the room reference inside a name, however the two forms write it

    `B1.116 SHEIKHA LOBBY` and `HH SECURITY B.113` both carry one; it may lead
    or trail, and the level prefix may be a letter, a letter and a digit, or
    just a digit. This is only used to sort the changes into kinds for the
    crosswalk - nothing is written from it.
    """
    for pattern in (r'\b([A-Z]{1,3}\d?[.\-]\d{2,4}[A-Z]{0,3})\b',
                    r'\b(\d{1,2}[.\-]\d{2,4}[A-Z]{0,3})\b'):
        m = re.search(pattern, (text or '').upper())
        if m:
            return re.sub(r'[.\-]', '.', m.group(1))
    return None


def kind(old, new):
    """what sort of change this is, for the reviewer to sort on"""
    a, b = room_number(old), room_number(new)
    if a and b:
        if a == b:
            return 'same room, name reordered'
        if a.split('.')[-1] == b.split('.')[-1]:
            return 'same room, level prefix differs'
        return 'DIFFERENT ROOM'
    if b and not a:
        return 'room number added'
    if a and not b:
        return 'room number dropped'
    return 'no room number either side'


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--dry-run', action='store_true')
    args = ap.parse_args()

    changes = wanted()
    by_building = {}
    for building, tag, old, new, why in changes.values():
        by_building.setdefault(building, []).append((tag, old, new, why))
    for building, _, _ in [(b, 0, 0) for b, _, _ in SECTIONS]:
        rows = by_building.get(building, [])
        print('  %-4s %4d room names change' % (building, len(rows)))
    print('  %s' % ('-' * 26))
    print('  all  %4d' % len(changes))

    with CROSSWALK.open('w', newline='') as f:
        w = csv.writer(f, lineterminator='\n')
        w.writerow(['row', 'building', 'tag', 'room before', 'room after',
                    'chosen from', 'kind of change'])
        for row in sorted(changes):
            b, tag, old, new, why = changes[row]
            w.writerow([row, b, tag, old, new, why, kind(old, new)])
    kinds = collections.Counter(kind(c[2], c[3]) for c in changes.values())
    print()
    for k, n in kinds.most_common():
        print('  %-34s %4d' % (k, n))
    print('\nwrote %s' % CROSSWALK.name)

    if args.dry_run:
        return

    with zipfile.ZipFile(MASTER) as zf:
        xml = rewrite(sheet_xml(zf), changes)
        shutil.copy(MASTER, OUT)
        items = [(i, zf.read(i.filename)) for i in zf.infolist()]
    with zipfile.ZipFile(OUT, 'w', zipfile.ZIP_DEFLATED) as out:
        for info, data in items:
            out.writestr(info, xml.encode('utf8')
                         if info.filename == SHEET else data)
    print('wrote %s' % OUT.name)


if __name__ == '__main__':
    main()
