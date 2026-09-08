#!/usr/bin/env python3
"""Carry the old registry's columns E onward onto the corrected equipment list.

    python3 merge_old_columns.py --dry-run
    python3 merge_old_columns.py

`All_Buildings_Rooms_Inclusion_Status_V1.2.xlsx` holds what the corrected
register does not: the zones each unit serves and its BMS readings and
setpoints. Each building carries a different set of those columns - HQ has
occupied and unoccupied setpoints, SSC has nineteen columns including room unit
setpoints and an occupancy status, RDC has outside and exhaust air. They are
copied per building, under their own headers, exactly as the old file names
them.

Columns A to D are the corrected register's: tag, equipment type, whether it is
included, and the room name settled against the BMS screens and the ontology.
Column E onward is the old file's, matched on the tag.

**RDC tags moved, so the match is not a string match.** The historian pass
renamed 111 part rows into the unit they are part of, so the old file's
`AT-1005` row carries the zones and readings that now belong to `CAV1005`. The
rename map from `rdc_rebuild_log.csv` carries them across; where several old
part rows land on one unit the row that became the unit wins, and the others are
checked against it rather than trusted. Two AHUs are matched with the level
segment ignored, because the two files disagree about whether the tag carries
one - see the coverage report.

A unit with no row in the old file gets empty cells from E on. Nothing is
carried across from a neighbouring row, and no value is invented.
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
NEW = HERE / 'Appendix_A_Asset_Register_clean.xlsx'
OLD = HERE / 'All_Buildings_Rooms_Inclusion_Status_V1.2.xlsx'
LOG = HERE / 'rdc_rebuild_log.csv'
OUT = HERE / 'All_Buildings_Rooms_Inclusion_Status_V1.3.xlsx'
REPORT = HERE / 'old_column_merge_coverage.csv'

TABS = (('HQ', 'HQ Asset Registry'), ('QNL', 'QNL Asset Registry'),
        ('SSC', 'SSC Asset Registry'), ('RDC', 'RDC Asset Registry'))
HEAD_AD = (('Tag No.', 30), ('Equipment Type', 16),
           ('Included / Not included', 17), ('Room (final)', 46))

TITLE_FILL = PatternFill('solid', fgColor='FF1F4E79')
HEAD_FILL = PatternFill('solid', fgColor='FF2E75B6')
OLD_FILL = PatternFill('solid', fgColor='FF8EA9DB')     # columns E onward
GAP_FILL = PatternFill('solid', fgColor='FFFFF2CC')
WHITE = Font(bold=True, color='FFFFFFFF')
THIN = Side(style='thin', color='FFBFBFBF')
GRID = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
TOP = Alignment(vertical='top', wrap_text=True)


def rename_map():
    """old RDC tag -> the tag that row carries now, and which one is the anchor"""
    alias, anchor = {}, {}
    for r in csv.DictReader(LOG.open()):
        if r['action'] != 'renamed in place - unit':
            continue
        m = re.search(r'was (\S+), and takes the place of (.+)$', r['detail'])
        if not m:
            continue
        anchor[m.group(1)] = r['tag']
        for o in [m.group(1)] + [t.strip() for t in m.group(2).split(',')]:
            alias[o] = r['tag']
    return alias, anchor


def no_level(tag):
    """the tag with every level segment dropped

    Removes each one rather than collapsing a pair, so the register's own typo
    `RDC_NB_2F_2F_AHU8513` reduces to the same key as the old file's
    `RDC_NB_2F_AHU8513`.
    """
    return re.sub(r'_(?:GF|1F|2F|MF|L0|B1)(?=_)', '', str(tag))


def old_block(ws):
    """(headers from E on, tag -> its values from E on)"""
    last = max(c for c in range(1, 60) if ws.cell(2, c).value)
    head = [ws.cell(2, c).value for c in range(5, last + 1)]
    head = ['Zones Served' if h == 'ZONES SERVED' else h for h in head]
    vals = {}
    for r in range(3, ws.max_row + 1):
        tag = ws.cell(r, 1).value
        if tag:
            vals[str(tag).strip()] = [ws.cell(r, c).value
                                      for c in range(5, last + 1)]
    return head, vals


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--dry-run', action='store_true')
    args = ap.parse_args()

    reg = openpyxl.load_workbook(NEW, data_only=True)['Asset Register']
    assets = collections.defaultdict(list)
    for r in range(3, reg.max_row + 1):
        assets[reg.cell(r, 12).value].append(
            [reg.cell(r, c).value for c in (1, 2, 3, 4)])

    ob = openpyxl.load_workbook(OLD, data_only=True)
    alias, anchor = rename_map()

    out, report = {}, []
    for bld, tab in TABS:
        head, vals = old_block(ob[tab])
        tags = {str(a[0]).strip() for a in assets[bld]}

        rows, filled, checked, gap = [], 0, 0, []
        for tag, kind, inc, room in assets[bld]:
            tag = str(tag).strip()
            src = None
            if tag in vals:
                src = tag
            elif bld == 'RDC':
                cands = [t for t, u in alias.items() if u == tag and t in vals]
                if cands:
                    src = next((t for t in cands if t in anchor), cands[0])
                    for other in cands:
                        if other != src and vals[other] != vals[src]:
                            checked += 1
                            report.append([bld, tag, other,
                                           'ignored - disagrees with %s' % src])
                if src is None:
                    hit = [t for t in vals if no_level(t) == no_level(tag)]
                    if len(hit) == 1:
                        src = hit[0]
                        report.append([bld, tag, src,
                                       'matched with the level segment ignored'])
            if src:
                rows.append([tag, kind, inc, room] + vals[src])
                filled += 1
            else:
                rows.append([tag, kind, inc, room] + [None] * len(head))
                gap.append(tag)
                report.append([bld, tag, '', 'no row in the old file'])
        for t in vals:
            u = t if t in tags else alias.get(t)
            if u not in tags and not (
                    bld == 'RDC' and sum(1 for x in tags
                                         if no_level(x) == no_level(t)) == 1):
                report.append([bld, '', t, 'old row with no unit to land on'])
        out[bld] = (head, rows, filled, gap)
        print('%-4s %5d assets | columns E-%s from the old file | filled %5d | '
              'no old row %4d'
              % (bld, len(rows), get_column_letter(4 + len(head)), filled,
                 len(gap)))

    orphan = sum(1 for r in report if r[3] == 'old row with no unit to land on')
    print('old rows with nowhere to land: %d (RDC parts and rows the historian '
          'does not carry)' % orphan)
    with REPORT.open('w', newline='') as f:
        w = csv.writer(f, lineterminator='\n')
        w.writerow(['building', 'tag in the register', 'tag in the old file',
                    'what happened'])
        w.writerows(report)
    print('wrote %s' % REPORT.name)
    if args.dry_run:
        return

    wb = openpyxl.Workbook()
    wb.remove(wb.active)
    for bld, tab in TABS:
        head, rows, _, gap = out[bld]
        sheet(wb.create_sheet(tab), bld, head, rows, set(gap))
    wb.save(OUT)
    print('wrote %s' % OUT.name)


def sheet(ws, building, extra, rows, gap):
    ncol = 4 + len(extra)
    ws.cell(1, 1, '%s - CONTROLLABLE ASSET REGISTRY' % building).font = Font(
        bold=True, size=13, color='FFFFFFFF')
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=ncol)
    for c in range(1, ncol + 1):
        ws.cell(1, c).fill = TITLE_FILL
    for c, (name, width) in enumerate(HEAD_AD, 1):
        cell = ws.cell(2, c, name)
        cell.fill, cell.font, cell.border = HEAD_FILL, WHITE, GRID
        cell.alignment = Alignment(vertical='center', wrap_text=True)
        ws.column_dimensions[get_column_letter(c)].width = width
    for n, name in enumerate(extra, 5):
        cell = ws.cell(2, n, name)
        cell.fill, cell.font, cell.border = OLD_FILL, WHITE, GRID
        cell.alignment = Alignment(vertical='center', wrap_text=True)
        ws.column_dimensions[get_column_letter(n)].width = (
            56 if str(name).lower().startswith(('zones', 'source')) else 15)
    ws.row_dimensions[1].height = 22
    ws.row_dimensions[2].height = 34

    for n, row in enumerate(rows, 3):
        for c, value in enumerate(row, 1):
            cell = ws.cell(n, c, value)
            cell.alignment, cell.border = TOP, GRID
        if not row[3]:
            ws.cell(n, 4).fill = GAP_FILL
        if str(row[0]).strip() in gap:
            for c in range(5, ncol + 1):
                ws.cell(n, c).fill = GAP_FILL
    ws.freeze_panes = 'E3'
    ws.auto_filter.ref = 'A2:%s%d' % (get_column_letter(ncol), len(rows) + 2)


if __name__ == '__main__':
    main()
