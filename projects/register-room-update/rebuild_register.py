#!/usr/bin/env python3
"""Rebuild the RDC section around the units the historian actually carries.

    python3 rebuild_register.py --dry-run
    python3 rebuild_register.py

Three changes, all confined to the RDC section:

**Rows the historian has never heard of are removed** and tabulated on their own
in `RDC_removed_not_in_historian.xlsx`. Neither a unit nor part of one - the
historian knows nothing of the number - so there is nothing to put in the
registry and nothing to hang off a parent.

**Part rows are removed.** An `AT-4110` is the air terminal of the assembly the
historian carries whole as `VAV4110_EV4111`; it has no object, no points and no
widget on any screen. It belongs in the ontology as `brick:hasPart` of its unit,
not as a controllable asset.

**A part whose unit is not in the register puts that unit in.** The register
lists the terminals of 62 CAVs and 48 EAVs without listing the CAV or EAV, so
removing the parts alone would lose the equipment entirely. The new row is named
as the historian names it, and takes the room its parts agreed on - or no room
at all, said plainly, where they did not.

Whether a unit is already in the register is decided on the set of families and
numbers it names, not on the string: the historian writes
`RDC_NB_1F_VAV7830_7831` where the register writes `RDC_NB_1F_VAV7830_VEV7831`,
and comparing strings reports a unit as missing that is already there.
"""
import argparse
import collections
import csv
import re
import shutil
import zipfile
from pathlib import Path

import openpyxl
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

import classify_parts as C

HERE = Path(__file__).resolve().parent
MASTER = (HERE.parent / 'qnl-bms-room-allocation'
          / 'Appendix_A_Asset_Register_QNL_BMS_rooms.xlsx')
CLASS = HERE / 'rdc_unit_or_part.csv'
RDC_REVIEWED = HERE / 'RDC_reviewed.xlsx'
OUT = HERE / 'Appendix_A_Asset_Register_RDC_rebuilt.xlsx'
DROPPED = HERE / 'RDC_removed_not_in_historian.xlsx'
LOG = HERE / 'rdc_rebuild_log.csv'

SHEET = 'Controllable Asset Registry'
RDC_FIRST, RDC_LAST = 1443, 3201
HEAD_FILL = PatternFill('solid', fgColor='FF1F4E79')
NEW_FILL = PatternFill('solid', fgColor='FFFFF2CC')   # a row this pass added


def signature(tag):
    """the families and numbers a tag names, as a set - its identity"""
    return frozenset(C.numbers(tag))


def register_style(obj, sample):
    """the historian's object name, written the way the register writes tags

    The register keeps a level segment the historian drops, so the new row is
    given the level of the parts it replaces rather than none at all.
    """
    m = re.match(r'RDC_(NB_SB|NB|SB|UB)_(.+)$', obj)
    if not m:
        return obj
    rest = m.group(2)
    if re.match(r'(?:GF|1F|2F|MF|L0|B1)_', rest):
        return obj                       # the historian already names the level
    lvl = re.match(r'RDC_(?:NB_SB|NB|SB|UB)_((?:GF|1F|2F|MF|L0|B1)_)', sample or '')
    return 'RDC_%s_%s%s' % (m.group(1), lvl.group(1) if lvl else '', rest)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--dry-run', action='store_true')
    args = ap.parse_args()

    verdict = {r['tag']: r for r in csv.DictReader(CLASS.open())}
    src = openpyxl.load_workbook(MASTER, read_only=True, data_only=True)[SHEET]
    rows = list(src.iter_rows(min_row=1, max_row=3202, max_col=9, values_only=True))

    # the BMS reading for a tag, so a part's reading follows it to its unit
    read = {}
    ws2 = openpyxl.load_workbook(RDC_REVIEWED, data_only=True)[SHEET]
    for r in range(3, ws2.max_row + 1):
        tag = str(ws2.cell(r, 1).value or '').strip()
        room = str(ws2.cell(r, 10).value or '').strip()
        if tag and room:
            read[tag] = room

    keep, parts, gone = [], [], []
    for i, row in enumerate(rows, 1):
        if not row[0] or not (RDC_FIRST <= i <= RDC_LAST):
            continue
        tag = str(row[0]).strip()
        v = verdict.get(tag, {}).get('verdict', '')
        if v.startswith('neither'):
            gone.append((i, row, v))
        elif v.startswith('part'):
            parts.append((i, row, verdict[tag]))
        else:
            keep.append((i, row))

    kept_sig = {signature(str(r[0]).strip()) for _, r in keep}
    kept_sig.discard(frozenset())

    # a unit that only its parts point to, and which no kept row already is
    wanted = collections.OrderedDict()
    for i, row, v in parts:
        hosts = [h.strip() for h in
                 v['historian object it belongs to'].split(' / ') if h.strip()]
        if len(hosts) != 1:
            continue
        host = hosts[0]
        if signature(host) & frozenset() or signature(host) in kept_sig:
            continue
        entry = wanted.setdefault(host, {'rooms': [], 'from': [], 'sample': ''})
        entry['rooms'].append(str(row[3] or '').strip())
        entry['from'].append(str(row[0]).strip())
        entry['sample'] = entry['sample'] or str(row[0]).strip()

    added = []
    for host, e in wanted.items():
        tag = register_style(host, e['sample'])
        fams = {f for f, _ in C.numbers(host)}
        kind = ('CAV' if 'CAV' in fams else 'EAV' if 'EAV' in fams
                else 'VAV' if 'VAV' in fams else sorted(fams)[0] if fams else '')
        rooms = {r for r in e['rooms'] if r}
        room = rooms.pop() if len(rooms) == 1 else ''
        note = ('room taken from its %d part row(s)' % len(e['from']) if room
                else 'its parts named %d different rooms - left blank'
                     % len(set(e['rooms'])))
        added.append((tag, kind, room, note, e['from'],
                      read.get(e['from'][0], '')))

    print('RDC section: %d rows in' % (len(keep) + len(parts) + len(gone)))
    print('  kept as units                 %4d' % len(keep))
    print('  removed - parts of a unit     %4d' % len(parts))
    print('  removed - not in the historian%4d' % len(gone))
    print('  units added, named by their parts %4d' % len(added))
    print('  RDC section out               %4d' % (len(keep) + len(added)))

    with LOG.open('w', newline='') as f:
        w = csv.writer(f, lineterminator='\n')
        w.writerow(['action', 'tag', 'type', 'room', 'detail'])
        for i, row, v in gone:
            w.writerow(['removed - not in historian', row[0], row[1], row[3], v])
        for i, row, v in parts:
            w.writerow(['removed - part', row[0], row[1], row[3],
                        'part of %s' % v['historian object it belongs to']])
        for tag, kind, room, note, frm, _ in added:
            w.writerow(['added - unit', tag, kind, room,
                        '%s; replaces %s' % (note, ' '.join(frm))])
    print('\nwrote %s' % LOG.name)

    if args.dry_run:
        return

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = 'Not in the historian'
    for c, name in enumerate(['Tag No.', 'Equipment Type', 'Included/Not',
                              'Room name as per drawings', 'Why it was removed'], 1):
        cell = ws.cell(1, c, name)
        cell.fill, cell.font = HEAD_FILL, Font(bold=True, color='FFFFFFFF')
        ws.column_dimensions[get_column_letter(c)].width = (28, 16, 16, 40, 62)[c - 1]
    for n, (i, row, v) in enumerate(gone, 2):
        for c in range(4):
            ws.cell(n, c + 1, row[c])
        ws.cell(n, 5, 'the historian has no object for this number, and no '
                      'assembly it could be part of - it is neither a '
                      'controllable asset nor a part of one')
        for c in range(1, 6):
            ws.cell(n, c).alignment = Alignment(vertical='top', wrap_text=True)
    ws.freeze_panes = 'A2'
    wb.save(DROPPED)
    print('wrote %s (%d rows)' % (DROPPED.name, len(gone)))

    rewrite(keep, added, parts, gone)
    print('wrote %s' % OUT.name)


SHEET_XML = 'xl/worksheets/sheet6.xml'
COMMENTS = 'xl/comments1.xml'
VML = 'xl/drawings/vmlDrawing1.vml'


def cell_xml(row, values, fill_style=None):
    """one <row> of inline-string cells"""
    out = ['<row r="%d">' % row]
    for c, v in enumerate(values, 1):
        if v is None or str(v) == '':
            continue
        ref = '%s%d' % (get_column_letter(c), row)
        text = (str(v).replace('&', '&amp;').replace('<', '&lt;')
                .replace('>', '&gt;'))
        style = ' s="%s"' % fill_style if fill_style else ''
        out.append('<c r="%s"%s t="inlineStr"><is><t xml:space="preserve">%s'
                   '</t></is></c>' % (ref, style, text))
    out.append('</row>')
    return ''.join(out)


def renumber(row_xml, old, new):
    """the same <row>, moved to a different row number"""
    row_xml = re.sub(r'(<row[^>]*\sr=")%d(")' % old, r'\g<1>%d\g<2>' % new,
                     row_xml, count=1)
    return re.sub(r'(\sr="[A-Z]+)%d(")' % old, r'\g<1>%d\g<2>' % new, row_xml)


def rewrite(keep, added, parts=(), gone=()):
    """the master workbook with the RDC section rebuilt, everything else intact

    Done as XML inside the zip. The RDC section is the last block of rows, so
    the rows above it are copied through untouched and only the tail is
    rebuilt - no earlier row moves.

    The twenty cell comments on RDC rows are the client's own review notes
    ("Corrected from...", "Resolved by elimination..."), every one of them on a
    row that survives, so their anchors are moved with their rows in both
    comments1.xml and the VML that positions them. An openpyxl round trip drops
    them outright, and renumbering without touching them leaves each note on
    whatever row happens to land at its old number.
    """
    with zipfile.ZipFile(MASTER) as zf:
        parts_ = [(i, zf.read(i.filename)) for i in zf.infolist()]
    blob = {i.filename: d for i, d in parts_}
    xml = blob[SHEET_XML].decode('utf8')

    rows_xml = {}
    # a row is either self-closing or has a </row>. Matching `.*?(?:/>|</row>)`
    # instead stops at the first self-closing *cell* inside the row and cuts it
    # in half, which silently dropped two thirds of the sheet.
    for m in re.finditer(r'<row\b[^>]*/>|<row\b[^>]*>.*?</row>', xml, re.S):
        rows_xml[int(re.search(r'\sr="(\d+)"', m.group(0)).group(1))] = m.group(0)
    head = xml[:xml.index('<sheetData>') + len('<sheetData>')]
    tail = xml[xml.index('</sheetData>'):]

    body, moved = [], {}
    for r in sorted(rows_xml):
        if r < RDC_FIRST:
            body.append(rows_xml[r])
    at = RDC_FIRST
    for old_row, _ in keep:
        body.append(renumber(rows_xml[old_row], old_row, at))
        moved[old_row] = at
        at += 1
    added_at = {}
    for tag, kind, room, note, frm, screen in added:
        body.append(cell_xml(at, [tag, kind, 'Included', room, None, None, None,
                                  None, None, screen, None, None,
                                  'added by the historian pass - %s. Replaces %s'
                                  % (note, ', '.join(frm))]))
        for f in frm:
            added_at[f] = at
        at += 1
    last = at - 1

    # A comment sitting on a row that has gone still has to land somewhere. The
    # client's notes are about the unit, so a note on a part follows the part to
    # its unit; a note on a row removed as unknown to the historian has no unit
    # to follow and is dropped, which is said out loud rather than left to be
    # noticed.
    tag_row = {}
    for old_row, row in keep:
        tag_row[str(row[0]).strip()] = moved[old_row]
    sig_row = {}
    for old_row, row in keep:
        sig_row[signature(str(row[0]).strip())] = moved[old_row]
    dropped_note = []
    for old_row, row, v in parts:
        tag = str(row[0]).strip()
        hosts = [h.strip() for h in
                 v['historian object it belongs to'].split(' / ') if h.strip()]
        dest = added_at.get(tag)
        if dest is None and len(hosts) == 1:
            dest = sig_row.get(signature(hosts[0]))
        if dest:
            moved[old_row] = dest
        else:
            dropped_note.append((old_row, tag))
    for old_row, row, v in gone:
        dropped_note.append((old_row, str(row[0]).strip()))
    rewrite.dropped = dropped_note

    xml = head + ''.join(body) + tail
    xml = re.sub(r'(<dimension ref="A1:[A-Z]+)\d+(")', r'\g<1>%d\g<2>' % last, xml)
    xml = re.sub(r'(<autoFilter ref="A2:[A-Z]+)\d+(")', r'\g<1>%d\g<2>' % last, xml)
    blob[SHEET_XML] = xml.encode('utf8')

    if COMMENTS in blob:
        c = blob[COMMENTS].decode('utf8')

        lost = {r for r, _ in getattr(rewrite, 'dropped', ())}
        keep_c, drop_c = [], []
        for m in re.finditer(r'<comment ref="([A-Z]+)(\d+)".*?</comment>', c, re.S):
            row = int(m.group(2))
            if row in moved:
                keep_c.append(re.sub(r'(<comment ref="[A-Z]+)\d+(")',
                                     r'\g<1>%d\g<2>' % moved[row], m.group(0)))
            elif row < RDC_FIRST:
                keep_c.append(m.group(0))
            else:
                drop_c.append(row)
        body_c = re.sub(r'<commentList>.*</commentList>',
                        '<commentList>%s</commentList>' % ''.join(keep_c), c, flags=re.S)
        blob[COMMENTS] = body_c.encode('utf8')
        if drop_c:
            print('  %d comment(s) dropped - they sat on rows that are gone'
                  % len(drop_c))
    if VML in blob:
        v = blob[VML].decode('utf8')

        def move_anchor(m):
            row = int(m.group(1)) + 1          # the VML counts from zero
            return '<x:Row>%d</x:Row>' % (moved.get(row, row) - 1)
        blob[VML] = re.sub(r'<x:Row>(\d+)</x:Row>', move_anchor, v).encode('utf8')

    with zipfile.ZipFile(OUT, 'w', zipfile.ZIP_DEFLATED) as out:
        for info, data in parts_:
            out.writestr(info, blob[info.filename])


if __name__ == '__main__':
    main()
