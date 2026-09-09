#!/usr/bin/env python3
"""One clean asset register, with the agreed room name written into column D.

    python3 build_clean_register.py --dry-run   # report, write nothing
    python3 build_clean_register.py

The working file is nine tabs deep: the registry, four source registers, three
room-name tabs carrying spilling `TRANSPOSE(FILTER(...))` formulas, and a 55-turn
`Claude Log`. The registry sheet inside it declares 16,382 columns, hides 1,141
rows behind two levels of outline grouping, and leaves two of its populated
columns without a header and two more empty between the ones that are used.

This writes the register on its own, as one flat table, with the room names
corrected. Four tabs, no formulas, nothing hidden:

  `Asset Register`      every asset, one row each, twelve headed columns
  `Room name changes`   what this pass rewrote, from what, on whose authority
  `Removed from RDC`    what the historian pass took out and what it renamed
  `Read me`             what the file is, what changed, what is still open

**The columns are contiguous now.** The working file left G and I empty and put
`ROOM PER BMS SCREEN` in J; here every column carries data and a header, so that
column is H. Column D is still column D - it is the one the correction writes
and the one the converter reads. The building is column L, so the four sections
can be filtered rather than found by scrolling to a banner row: the banner rows
are gone, because a banner row inside a filtered table sorts into the middle of
the data.

The 38 cell comments are the client's own review notes and are carried across.

Where each section's room name comes from:

  HQ, QNL, SSC   `Room_Names_4.xlsx`, column M `rdfs:label_en` - the name chosen
                 after validating column D against the BMS screens and the
                 delivered ontology. Column N records which source won. A row
                 with an empty `rdfs:label_en` keeps the room it had.

  RDC            `RDC_reviewed.xlsx`, column J, on the rows the client filled
                 green - the 32 kept out of the 215 this pass flagged. The other
                 183 readings were rejected and their column J cleared, so green
                 is the whole instruction and a column J value on a row that is
                 not green is not.

A green RDC row whose tag was a part now carries the unit's name - `AT-5280`
became `CAV5280` in the historian pass - so the reading follows the rename
rather than being dropped for naming a tag that no longer exists.
"""
import argparse
import csv
import re
import sys
from pathlib import Path

import openpyxl
from openpyxl.comments import Comment
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

HERE = Path(__file__).resolve().parent
SRC = HERE / 'Appendix_A_Asset_Register_RDC_rebuilt.xlsx'
NAMES = HERE / 'Room_Names_4.xlsx'
RDC = HERE / 'RDC_reviewed.xlsx'
LOG = HERE / 'rdc_rebuild_log.csv'
OUT = HERE / 'Appendix_A_Asset_Register_clean.xlsx'
CROSSWALK = HERE / 'clean_room_name_changes.csv'
TAG_FIXES = HERE / 'tag_corrections.csv'

SHEET = 'Controllable Asset Registry'
GREEN = 'FF00B050'

# Three AHU tags whose level segment is wrong: the register drops it on two and
# doubles it on the third. All_Buildings_Rooms_Inclusion_Status_V1.2.xlsx spells
# all three the same way, which settles what it should have been; corrected on
# the client's instruction. One map, applied as the rows are read, so the tag
# cannot drift from what the downstream sheets carry.
TAG_FIX = {
    'RDC_NB_AHU8511': 'RDC_NB_2F_AHU8511',
    'RDC_NB_AHU8512': 'RDC_NB_2F_AHU8512',
    'RDC_NB_2F_2F_AHU8513': 'RDC_NB_2F_AHU8513',
}

# the section banner rows in the source, and the block each one opens
SECTIONS = (('HQ', 3, 764), ('QNL', 765, 1316), ('SSC', 1317, 1441),
            ('RDC', 1442, 3201))

# source column -> where it lands, with the header it should always have carried
COLUMNS = [
    (1,  'Tag No.',                                  26),
    (2,  'Equipment type',                           16),
    (3,  'Included / not included',                  17),
    (4,  'Room name as per drawings',                42),
    (5,  'Room entity',                              34),
    (6,  'Note',                                     46),
    (8,  'Room name per VAV / FCU list (where different)', 40),
    (10, 'Room per BMS screen',                      34),
    (11, 'BMS screen (image file)',                  34),
    (12, 'BMS screen vs drawings',                   30),
    (13, 'Why',                                      46),
    (None, 'Building',                                9),
]

TITLE_FILL = PatternFill('solid', fgColor='FF1F4E79')
HEAD_FILL = PatternFill('solid', fgColor='FF2E75B6')
CHANGED_FILL = PatternFill('solid', fgColor='FFFFF2CC')
WHITE = Font(bold=True, color='FFFFFFFF')
THIN = Side(style='thin', color='FFBFBFBF')
GRID = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
TOP = Alignment(vertical='top', wrap_text=True)


def chosen():
    """(building, tag) -> (room, which source it came from), for HQ/QNL/SSC"""
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
                out[(name, tag)] = (room,
                                    str(ws.cell(r, why).value or '').strip()
                                    if why else '')
    return out


def renames():
    """old part tag -> the unit tag that row became in the historian pass"""
    out = {}
    for r in csv.DictReader(LOG.open()):
        if r['action'] != 'renamed in place - unit':
            continue
        m = re.search(r'was (\S+), and takes the place of (.+)$', r['detail'])
        if m:
            for old in [m.group(1)] + [t.strip() for t in m.group(2).split(',')]:
                out[old] = r['tag']
    return out


def rdc_green(alias):
    """tag -> (room, source), for the RDC rows the client filled green

    Keyed on the tag the row carries now: a green reading taken against a part
    row belongs to the unit that row became.
    """
    ws = openpyxl.load_workbook(RDC, data_only=True)[SHEET]
    out, followed = {}, []
    for r in range(3, ws.max_row + 1):
        cell = ws.cell(r, 1)
        if cell.fill.patternType != 'solid' or str(cell.fill.fgColor.rgb) != GREEN:
            continue
        room = str(ws.cell(r, 10).value or '').strip()
        tag = str(cell.value or '').strip()
        if not (tag and room):
            continue
        now = alias.get(tag, tag)
        if now != tag:
            followed.append((tag, now))
        out[now] = (room, 'BMS screen, kept green by the client')
    rdc_green.followed = followed
    return out


def read_source():
    """(building, values...) per asset row, plus the comments on the sheet"""
    wb = openpyxl.load_workbook(SRC)
    ws = wb[SHEET]
    band = {}
    for name, first, last in SECTIONS:
        for r in range(first, last + 1):
            band[r] = name
    rows, notes, read_source.fixed = [], {}, []
    for r in range(3, ws.max_row + 1):
        tag = ws.cell(r, 1).value
        if not tag or str(tag).strip() in {n for n, _, _ in SECTIONS}:
            continue                      # blank, or a section banner row
        vals = []
        for src, _, _ in COLUMNS:
            vals.append(None if src is None
                        else ws.cell(r, src).value)
        vals[-1] = band.get(r, '')
        fixed = TAG_FIX.get(str(vals[0]).strip())
        if fixed:
            read_source.fixed.append((str(vals[0]).strip(), fixed))
            vals[0] = fixed
        rows.append(vals)
        for src, _, _ in COLUMNS:
            if src is None:
                continue
            c = ws.cell(r, src)
            if c.comment:
                notes[(len(rows), src)] = (c.comment.text, c.comment.author)
    return rows, notes


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--dry-run', action='store_true')
    args = ap.parse_args()

    rows, notes = read_source()
    pick = chosen()
    alias = renames()
    green = rdc_green(alias)

    tag_i, room_i, bld_i = 0, 3, len(COLUMNS) - 1
    changes = []
    for n, v in enumerate(rows):
        tag = str(v[tag_i] or '').strip()
        old = str(v[room_i] or '').strip()
        bld = v[bld_i]
        hit = green.get(tag) if bld == 'RDC' else pick.get((bld, tag))
        if not hit:
            continue
        new, why = hit
        if new != old:
            v[room_i] = new
            changes.append((bld, tag, old, new, why, n))

    by = {}
    for bld, *_ in changes:
        by[bld] = by.get(bld, 0) + 1
    print('%d asset rows, %d section banners dropped' % (len(rows), len(SECTIONS)))
    print('room names rewritten: %d' % len(changes))
    for name, _, _ in SECTIONS:
        print('  %-4s %4d' % (name, by.get(name, 0)))
    if rdc_green.followed:
        print('  RDC readings that followed a rename:')
        for old, new in rdc_green.followed:
            print('    %s -> %s' % (old, new))
    blank = sum(1 for v in rows if not str(v[room_i] or '').strip())
    print('rows still with no room name: %d' % blank)

    with CROSSWALK.open('w', newline='') as f:
        w = csv.writer(f, lineterminator='\n')
        w.writerow(['building', 'tag', 'room before', 'room after', 'source'])
        for bld, tag, old, new, why, _ in changes:
            w.writerow([bld, tag, old, new, why])
    print('wrote %s' % CROSSWALK.name)

    with TAG_FIXES.open('w', newline='') as f:
        w = csv.writer(f, lineterminator='\n')
        w.writerow(['tag before', 'tag after', 'why'])
        for old, new in read_source.fixed:
            w.writerow([old, new, 'level segment corrected against '
                                  'All_Buildings_Rooms_Inclusion_Status_V1.2'])
    print('tags corrected: %d' % len(read_source.fixed))
    for old, new in read_source.fixed:
        print('  %s -> %s' % (old, new))

    if args.dry_run:
        return
    write(rows, notes, changes, blank)
    print('wrote %s' % OUT.name)


def header(ws, title, names, widths, width_of=None):
    ws.cell(1, 1, title).font = Font(bold=True, size=13, color='FFFFFFFF')
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=len(names))
    for c in range(1, len(names) + 1):
        ws.cell(1, c).fill = TITLE_FILL
    for c, (name, wid) in enumerate(zip(names, widths), 1):
        cell = ws.cell(2, c, name)
        cell.fill, cell.font = HEAD_FILL, WHITE
        cell.alignment = Alignment(vertical='center', wrap_text=True)
        cell.border = GRID
        ws.column_dimensions[get_column_letter(c)].width = wid
    ws.row_dimensions[1].height = 22
    ws.row_dimensions[2].height = 32
    ws.freeze_panes = 'A3'


def write(rows, notes, changes, blank):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = 'Asset Register'
    names = [n for _, n, _ in COLUMNS]
    header(ws, 'CONTROLLABLE ASSET REGISTRY', names, [w for _, _, w in COLUMNS])

    touched = {n for *_, n in changes}
    for n, v in enumerate(rows):
        r = n + 3
        for c, value in enumerate(v, 1):
            cell = ws.cell(r, c, value)
            cell.alignment = TOP
            cell.border = GRID
        if n in touched:
            ws.cell(r, 4).fill = CHANGED_FILL
    src_col = {src: c for c, (src, _, _) in enumerate(COLUMNS, 1) if src}
    for (n, src), (text, author) in notes.items():
        ws.cell(n + 2, src_col[src]).comment = Comment(text, author)
    ws.auto_filter.ref = 'A2:%s%d' % (get_column_letter(len(names)), len(rows) + 2)

    ws2 = wb.create_sheet('Room name changes')
    head2 = ['Building', 'Tag No.', 'Room before', 'Room after', 'Source']
    header(ws2, 'ROOM NAMES REWRITTEN BY THIS PASS', head2, [10, 26, 42, 42, 40])
    for n, (bld, tag, old, new, why, _) in enumerate(changes, 3):
        for c, value in enumerate((bld, tag, old, new, why), 1):
            ws2.cell(n, c, value).alignment = TOP
            ws2.cell(n, c).border = GRID
    ws2.auto_filter.ref = 'A2:E%d' % (len(changes) + 2)

    ws3 = wb.create_sheet('Removed from RDC')
    head3 = ['What happened to it', 'Tag No.', 'Equipment type',
             'Room it carried', 'Why']
    header(ws3, 'RDC ROWS THE HISTORIAN PASS REMOVED OR RENAMED',
           head3, [26, 30, 16, 40, 74])
    log = list(csv.DictReader(LOG.open()))
    for n, r in enumerate(log, 3):
        for c, value in enumerate((r['action'], r['tag'], r['type'],
                                   r['room'], r['detail']), 1):
            ws3.cell(n, c, value).alignment = TOP
            ws3.cell(n, c).border = GRID
    ws3.auto_filter.ref = 'A2:E%d' % (len(log) + 2)

    ws4 = wb.create_sheet('Read me')
    header(ws4, 'WHAT THIS FILE IS', ['', ''], [26, 116])
    ws4.cell(2, 1, 'Section').fill = HEAD_FILL
    ws4.cell(2, 2, 'What it says').fill = HEAD_FILL
    ws4.cell(2, 1).font = ws4.cell(2, 2).font = WHITE
    for n, (k, t) in enumerate(readme(rows, changes, blank), 3):
        ws4.cell(n, 1, k).font = Font(bold=True)
        ws4.cell(n, 1).alignment = TOP
        ws4.cell(n, 2, t).alignment = TOP
        ws4.row_dimensions[n].height = max(15, 13 * (len(t) // 105 + 1))
    wb.save(OUT)


def readme(rows, changes, blank):
    by = {}
    for bld, *_ in changes:
        by[bld] = by.get(bld, 0) + 1
    counts = {}
    for v in rows:
        counts[v[-1]] = counts.get(v[-1], 0) + 1
    return [
        ('What this is',
         'The controllable asset register for HQ, QNL, SSC and RDC as one flat '
         'table, with the agreed room name written into column D. %d rows.'
         % len(rows)),
        ('Rows per building',
         ', '.join('%s %d' % (k, counts.get(k, 0))
                   for k, _, _ in SECTIONS)),
        ('Room names rewritten',
         '%d in total - %s. Every one is listed on the Room name changes tab '
         'with the room it replaced and where the new name came from. The cell '
         'is shaded on the register so the change can be seen in place.'
         % (len(changes), ', '.join('%s %d' % (k, by.get(k, 0))
                                    for k, _, _ in SECTIONS))),
        ('Where the names came from',
         'HQ, QNL and SSC from Room_Names_4.xlsx column M, the name chosen '
         'after checking the drawings against the BMS screens and the delivered '
         'ontology. RDC from the BMS screen readings the client kept green in '
         'the review workbook - 32 of the 215 that were put forward; the other '
         '183 were rejected and are not applied.'),
        ('Rows left alone',
         '%d rows still carry no room name. No source settled the room for '
         'them and none has been invented; they are the rows to look at next.'
         % blank),
        ('Columns',
         'The working file left two columns empty between the ones it used and '
         'two more without a header. Every column here carries data and a '
         'header, so ROOM PER BMS SCREEN is column H rather than column J. '
         'Column D is unchanged - it is the one the converter reads.'),
        ('Building column',
         'Column L names the building on every row. The HQ / QNL / SSC / RDC '
         'banner rows are gone: a banner row inside a filtered table sorts into '
         'the middle of the data. Filter column L instead.'),
        ('RDC is smaller than it was',
         'The RDC section went from 1,759 rows to 1,141. Air terminals and '
         'valves that the historian carries only as part of an assembly are '
         'parts, not controllable assets, and belong in the ontology under '
         'brick:hasPart. Every removal and rename is on the Removed from RDC '
         'tab.'),
        ('Names that had nowhere to go',
         '74 tags in Room_Names_4.xlsx carry an agreed room name but have no '
         'row in this register - 41 SSC, 33 HQ, all of them CCU, DX, chilled '
         'water heat exchangers and pumps, exhaust fans and the MV generator. '
         'None exists in the register under any spelling, so the name could '
         'not be placed. Either the register is missing this equipment or '
         'these assets are deliberately out of scope; it has not been decided.'),
        ('Names the source did not settle',
         '90 rows in Room_Names_4.xlsx have an empty rdfs:label_en - 75 HQ, 14 '
         'QNL, 1 SSC. No source won for them, so their register rows keep the '
         'room they already had rather than being blanked or guessed.'),
        ('Three tags corrected',
         'RDC_NB_AHU8511 and RDC_NB_AHU8512 carried no level segment and '
         'RDC_NB_2F_2F_AHU8513 carried it twice. They are now '
         'RDC_NB_2F_AHU8511, 8512 and 8513, the way '
         'All_Buildings_Rooms_Inclusion_Status_V1.2.xlsx spells all three. No '
         'other tag was touched - identifiers are the join key to SCADA.'),
        ('Tags are not unique across buildings',
         '123 tags appear in two buildings at once - AHUB_0001, FCU0001 and so '
         'on. No tag repeats inside its own building, so column L tells them '
         'apart here, but only RDC prefixes its tags with the building code. '
         'The ontology needs that prefix on all four, or HQ and QNL assets '
         'collide the moment the sheets are merged.'),
        ('Still open',
         'VEV-5192a/b were renamed FEV5192A/B on the historian\'s word alone; '
         '14 assemblies disagree with their parts on the room number; 47 RDC '
         'rows carry a number the historian has never heard of and were '
         'removed rather than kept on trust.'),
        ('Not in this file',
         'The four source equipment registers, the three room-name tabs and '
         'the Claude Log stay in the working workbook. They carry live '
         'formulas that a rewrite would break, and none of them is the '
         'deliverable.'),
    ]


if __name__ == '__main__':
    main()
