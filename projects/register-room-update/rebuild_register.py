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

**A part whose unit is not in the register renames itself into that unit, where
it sits.** The register lists the terminals of 62 CAVs and 48 EAVs without
listing the CAV or EAV, so removing the parts alone would lose the equipment
entirely. The first of those part rows becomes the unit - same row, same
position, same review note, same highlight - named as the historian names it and
taking the room its parts agreed on, or no room at all, said plainly, where they
did not. Its siblings are removed. Deleting the part rows and appending fresh
unit rows at the end of the section would throw away the review that had already
been done on them and file the equipment away from the units it sits beside.

**A row the register already writes as the whole assembly is the unit, not a
part of it.** `RDC_NB_1F_VAV7830_VEV7831` names both halves of the assembly the
historian carries as `RDC_NB_1F_VAV7830_7831`; the two differ on spelling, not
on what they name, so the register's row stays exactly as it is. The test is the
leading family and number, which is what makes `AT-1005` a part of `CAV1005` -
same number, different family - and leaves `VAV7830_VEV7831` alone.
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
from openpyxl.utils import column_index_from_string, get_column_letter

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


def signature(tag):
    """the families and numbers a tag names, as a set - its identity"""
    return frozenset(C.numbers(tag))


def primary(tag):
    """the leading (family, number) a tag names - the thing the row is about"""
    n = C.numbers(tag)
    return n[0] if n else None


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

    total_in = len(keep) + len(parts) + len(gone)

    # A row that already names the whole assembly is that assembly, however the
    # historian spells it. Removing it and writing the historian's spelling back
    # as a fresh row throws away a row that was right to begin with.
    same, rest = [], []
    for i, row, v in parts:
        hosts = [h.strip() for h in
                 v['historian object it belongs to'].split(' / ') if h.strip()]
        tag = str(row[0]).strip()
        if len(hosts) == 1 and primary(tag) == primary(hosts[0]):
            same.append((i, row, hosts[0]))
            keep.append((i, row))
        else:
            rest.append((i, row, v))
    parts = rest
    keep.sort()

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
        if signature(host) in kept_sig:
            continue
        entry = wanted.setdefault(host, {'rooms': [], 'from': [], 'rows': []})
        entry['rooms'].append(str(row[3] or '').strip())
        entry['from'].append(str(row[0]).strip())
        entry['rows'].append(i)

    # the first of those part rows becomes the unit, in place
    promote = {}
    for host, e in wanted.items():
        tag = register_style(host, e['from'][0])
        fams = {f for f, _ in C.numbers(host)}
        kind = ('CAV' if 'CAV' in fams else 'EAV' if 'EAV' in fams
                else 'VAV' if 'VAV' in fams else sorted(fams)[0] if fams else '')
        rooms = {r for r in e['rooms'] if r}
        room = rooms.pop() if len(rooms) == 1 else ''
        note = ('room kept from its %d part row(s)' % len(e['from']) if room
                else 'its parts named %d different rooms - left blank'
                     % len(set(e['rooms'])))
        promote[e['rows'][0]] = (tag, kind, room, note, e['from'])

    keep.extend((i, row) for i, row, v in parts if i in promote)
    keep.sort()
    parts = [(i, row, v) for i, row, v in parts if i not in promote]

    print('RDC section: %d rows in' % total_in)
    print('  kept as units                     %4d' % (len(keep) - len(promote)
                                                       - len(same)))
    print('  kept - already the whole assembly %4d' % len(same))
    print('  part rows renamed into their unit %4d' % len(promote))
    print('  removed - parts of a unit         %4d' % len(parts))
    print('  removed - not in the historian    %4d' % len(gone))
    print('  RDC section out                   %4d' % len(keep))

    with LOG.open('w', newline='') as f:
        w = csv.writer(f, lineterminator='\n')
        w.writerow(['action', 'tag', 'type', 'room', 'detail'])
        for i, row, v in gone:
            w.writerow(['removed - not in historian', row[0], row[1], row[3], v])
        for i, row, v in parts:
            w.writerow(['removed - part', row[0], row[1], row[3],
                        'part of %s' % v['historian object it belongs to']])
        for i, row, host in same:
            w.writerow(['kept - already the assembly', row[0], row[1], row[3],
                        'the register already names the whole assembly; the '
                        'historian spells it %s' % host])
        for i in sorted(promote):
            tag, kind, room, note, frm = promote[i]
            w.writerow(['renamed in place - unit', tag, kind, room,
                        '%s; was %s, and takes the place of %s'
                        % (note, frm[0], ', '.join(frm))])
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

    rewrite(keep, promote, parts, gone)
    print('wrote %s' % OUT.name)


SHEET_XML = 'xl/worksheets/sheet6.xml'
COMMENTS = 'xl/comments1.xml'
VML = 'xl/drawings/vmlDrawing1.vml'


def set_cell(row_xml, row, col, value):
    """the same <row> with one cell replaced, added or cleared

    The cell keeps whatever style it had, so a row the client highlighted stays
    highlighted through a rename. An empty value clears the cell rather than
    writing a blank string, because a blank string reads as a room name of one
    space to anything that only tests for a value.
    """
    ref = '%s%d' % (col, row)
    pat = re.compile(r'<c\b[^>]*\sr="%s"(?:[^>]*/>|[^>]*>.*?</c>)' % ref, re.S)
    m = pat.search(row_xml)
    if value is None or str(value) == '':
        return pat.sub('', row_xml) if m else row_xml
    style = ''
    if m:
        s = re.search(r'\ss="(\d+)"', m.group(0))
        style = ' s="%s"' % s.group(1) if s else ''
    text = (str(value).replace('&', '&amp;').replace('<', '&lt;')
            .replace('>', '&gt;'))
    cell = ('<c r="%s"%s t="inlineStr"><is><t xml:space="preserve">%s</t></is>'
            '</c>' % (ref, style, text))
    if m:
        return row_xml[:m.start()] + cell + row_xml[m.end():]
    n = column_index_from_string(col)
    for c in re.finditer(r'<c\b[^>]*\sr="([A-Z]+)%d"' % row, row_xml):
        if column_index_from_string(c.group(1)) > n:
            return row_xml[:c.start()] + cell + row_xml[c.start():]
    return row_xml.replace('</row>', cell + '</row>')


def fix_spans(row_xml, row):
    """the row's declared span, recomputed from the cells it actually holds"""
    cols = [column_index_from_string(m.group(1)) for m in
            re.finditer(r'<c\b[^>]*\sr="([A-Z]+)%d"' % row, row_xml)]
    if not cols:
        return row_xml
    return re.sub(r'\sspans="\d+:\d+"',
                  ' spans="%d:%d"' % (min(cols), max(cols)), row_xml)


def renumber(row_xml, old, new):
    """the same <row>, moved to a different row number"""
    row_xml = re.sub(r'(<row[^>]*\sr=")%d(")' % old, r'\g<1>%d\g<2>' % new,
                     row_xml, count=1)
    return re.sub(r'(\sr="[A-Z]+)%d(")' % old, r'\g<1>%d\g<2>' % new, row_xml)


def rewrite(keep, promote, parts=(), gone=()):
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
    promoted_at = {}
    for old_row, _ in keep:
        x = renumber(rows_xml[old_row], old_row, at)
        if old_row in promote:
            tag, kind, room, note, frm = promote[old_row]
            x = set_cell(x, at, 'A', tag)
            x = set_cell(x, at, 'B', kind)
            x = set_cell(x, at, 'D', room)
            x = set_cell(x, at, 'M', 'was %s - the historian carries the '
                                     'assembly, not the terminal; %s'
                                     % (frm[0], note))
            x = fix_spans(x, at)
            for f in frm:
                promoted_at[f] = at
        body.append(x)
        moved[old_row] = at
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
        dest = promoted_at.get(tag)
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
