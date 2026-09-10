#!/usr/bin/env python3
"""Match RDC's separately-registered air terminals and valves to the widget the
BMS screens draw them under.

The RDC register lists one assembly across several rows. A variable-air-volume
box appears as `VAV4110_EV4111` - the box and its valve - and the air terminal
it feeds is a row of its own, `AT-4110`. The screens draw the assembly as one
widget, labelled the way the register writes the box half: `NB-VAV4110-EV4111`.
No widget is ever labelled `AT-`; there is no such thing to click on.

So a reading made against the box belongs to the terminal too, and the terminal
rows were being left open for want of a widget of their own - 644 of them.
The number is what ties them together: `AT-4110` and `VAV4110_EV4111` share
4110, in the same building.

Three things this has to be careful about, each of which would otherwise put a
room on the wrong row:

**Only the air-terminal families.** `FCU1004` and `VAV1004` share a number and
are different units - both are drawn as their own widget on South GF-6. Fan coil
units, air handling units and the rest are matched on their own tag only.

**Building, not level.** The south building registers its terminals under `L0`
and its boxes under `GF`, so `SB_L0_AT-1004` and `SB_GF_VAV1004` are the same
assembly written under two names for the ground floor. Matching on the level
segment loses them.

**A group with two readings that disagree is not resolved.** It is reported and
left alone; nothing is written from a guess about which of the two is right.
"""
import argparse
import collections
import csv
import re
import sys
from pathlib import Path

import openpyxl

HERE = Path(__file__).resolve().parent
MASTER = (HERE.parent / 'qnl-bms-room-allocation'
          / 'Appendix_A_Asset_Register_QNL_BMS_rooms.xlsx')
RDC = HERE / 'RDC_reviewed.xlsx'
OUT = HERE / 'rdc_terminal_matches.csv'

RDC_FIRST, RDC_LAST = 1443, 3201

# The families the screens draw as one widget and the register may split up.
# FCU, AHU, ERU and EF are deliberately absent: they are their own units and
# share a number with a terminal only by coincidence.
TERMINAL = {'AT', 'EV', 'VEV', 'CEV', 'FEV', 'VAV', 'CAV', 'EAV'}
LEVELS = ('GF', '1F', '2F', 'MF', 'L0', 'B1')
# The south building registers its terminals on L0 and its boxes on GF, which
# are the same floor under two names. Everything else keeps its own level: two
# rows on different floors that happen to share a number are two units.
SAME_LEVEL = {'L0': 'GF'}


def building(tag):
    m = re.match(r'RDC_(NB_SB|NB|SB|UB)_?', tag)
    return m.group(1) if m else None


def split(tag):
    """(building, level, zone, rest) - everything the key is built from

    The zone segment matters: `SB_L0_A1.2_AT-2001` and `SB_L0_A1.3_AT-2001` are
    two terminals with the same number in two zones, and dropping the zone
    merges them into one assembly.
    """
    rest = re.sub(r'^RDC_(NB_SB|NB|SB|UB)_', '', tag)
    level = None
    while True:
        m = re.match(r'(%s)_(.+)$' % '|'.join(LEVELS), rest)
        if not m:
            break
        level = level or SAME_LEVEL.get(m.group(1), m.group(1))
        rest = m.group(2)
    zone = ''
    m = re.match(r'([A-Z]\d+(?:\.\d+)?)_(.+)$', rest)
    if m and not re.match(r'^(%s)' % '|'.join(TERMINAL), m.group(1)):
        zone, rest = m.group(1), m.group(2)
    return building(tag), level, zone, rest


def body(tag):
    return split(tag)[3]


def members(tag):
    """(family, number) for each unit named in a tag, terminals only

    The trailing letter is part of the number and is compared case-blind but
    not discarded: `VEV-5192a` and `VEV-5192b` are two units, and a regex that
    only accepted an upper-case suffix read both as 5192 and merged them.
    """
    return [(f, n.upper())
            for f, n in re.findall(r'([A-Z]+)-?(\d+[A-Za-z]?)', body(tag))
            if f in TERMINAL]


def load():
    ws = openpyxl.load_workbook(MASTER, read_only=True, data_only=True)[
        'Controllable Asset Registry']
    rows = []
    for i, r in enumerate(ws.iter_rows(min_row=1, max_row=3202, max_col=4,
                                       values_only=True), 1):
        if r[0] and RDC_FIRST <= i <= RDC_LAST:
            rows.append((i, str(r[0]).strip(), str(r[1] or '').strip(),
                         str(r[3] or '').strip()))
    ws2 = openpyxl.load_workbook(RDC, data_only=True)['Controllable Asset Registry']
    read = {}
    for r in range(3, ws2.max_row + 1):
        tag = str(ws2.cell(r, 1).value or '').strip()
        room = str(ws2.cell(r, 10).value or '').strip()
        green = (ws2.cell(r, 1).fill.patternType == 'solid'
                 and str(ws2.cell(r, 1).fill.fgColor.rgb) == 'FF00B050')
        if tag and room:
            read[tag] = (room, ws2.cell(r, 11).value or '', green)
    return rows, read


def assemblies(rows):
    """the register rows grouped into one group per physical unit

    Sharing a number is not transitive on its own: `AT-1002` names only 1002
    and sees the box `VAV1003_VEV1002`, while that box names 1002 and 1003 and
    sees four rows. Taking each row's own neighbours as the group therefore
    produced two different groups over the same unit and listed ten rows twice.
    The groups are the connected components of the shares-a-number relation.
    """
    parent = {}

    def find(x):
        parent.setdefault(x, x)
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb

    for members_ in groups(rows).values():
        tags = sorted({m[1] for m in members_})
        for other in tags[1:]:
            union(tags[0], other)
    for _, tag, _, _ in rows:
        find(tag)
    out = collections.defaultdict(set)
    for tag in parent:
        out[find(tag)].add(tag)
    return {frozenset(v) for v in out.values()}


def groups(rows):
    """(building, number) -> the register rows that name that number"""
    idx = collections.defaultdict(list)
    for i, tag, kind, room in rows:
        b, level, zone, _ = split(tag)
        for fam, num in members(tag):
            idx[(b, level, zone, num)].append((i, tag, kind, room, fam))
    return idx


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.parse_args()
    rows, read = load()
    idx = groups(rows)

    # every register row, and the rest of its assembly
    partner = collections.defaultdict(set)
    for group in assemblies(rows):
        for t in group:
            partner[t] = group - {t}

    out, tally = [], collections.Counter()
    for i, tag, kind, room, in ((a, b, c, d) for a, b, c, d in rows):
        fams = {f for f, _ in members(tag)}
        if not fams:
            tally['not an air terminal family'] += 1
            continue
        mine = read.get(tag)
        sib = {p: read[p] for p in partner[tag] if p in read}
        rooms = {v[0] for v in sib.values()}
        if mine:
            verdict, proposed, src = 'has its own reading', mine[0], tag
        elif not sib:
            verdict, proposed, src = 'no reading anywhere in the assembly', '', ''
        elif len(rooms) == 1:
            verdict = 'inherits from the assembly'
            src = sorted(sib)[0]
            proposed = sib[src][0]
        else:
            verdict = 'SIBLINGS DISAGREE - not resolved'
            proposed, src = '', ' / '.join(sorted(sib))
        tally[verdict] += 1
        out.append([i, tag, kind, room, verdict, proposed, src,
                    ' '.join(sorted(partner[tag]))])

    with OUT.open('w', newline='') as f:
        w = csv.writer(f, lineterminator='\n')
        w.writerow(['row', 'tag', 'type', 'room in column D', 'verdict',
                    'room proposed', 'from which row', 'assembly'])
        w.writerows(out)

    for k, n in tally.most_common():
        print('  %-38s %d' % (k, n))
    print('\nwrote %s (%d rows)' % (OUT.name, len(out)))
    disagree(rows, partner)


ROOM_REF = re.compile(
    r'\b([A-Z]{1,2}\d?[.\-]\d{2,4}[A-Z]{0,3}|\d{1,2}\.\d{2,4}[A-Z]{0,3})\b')


def norm(room):
    """the room reference inside a name, and the words around it

    The reference has to be picked out by its shape, not by being the first
    thing with a digit in it: `Office 05 -8WS- N-0250` carries three numbers and
    only `N-0250` is the room. Taking the first one reported sixteen assemblies
    as disagreeing about the room when they agree exactly.
    """
    text = (room or '').upper()
    m = ROOM_REF.search(text)
    ref = re.sub(r'[.\-]', '.', m.group(1)) if m else ''
    ref = re.sub(r'^([A-Z]{0,2}\d?)\.0*', r'\1.', ref)
    words = {w for w in re.sub(r'[^A-Z0-9]', ' ', text).split()
             if w not in ('ROOM', 'RM', 'THE', 'AND', 'OF')
             and not any(c.isdigit() for c in w)}
    return ref, frozenset(words)


def disagree(rows, partner):
    """assemblies whose rows do not agree on the room in column D

    Each assembly is one physical unit split across several register rows, so
    its rows should carry one room between them. Where they do not, the
    register contradicts itself - and it does so independently of anything read
    off a screen, which is why this is worth running over all of them and not
    just the ones a leader reached.
    """
    room = {tag: d for _, tag, _, d in rows}
    seen, bad = set(), []
    for _, tag, _, _ in rows:
        group = frozenset({tag} | partner[tag])
        if len(group) < 2 or group in seen:
            continue
        seen.add(group)
        named = {t: room[t] for t in group if room.get(t)}
        # A box can feed several terminals in several rooms - AT-7120 runs to
        # nine of them - so an assembly whose terminals are numbered -N1, -N2
        # and so on is expected to name more than one room and is not a
        # conflict. Only the rows that are not one of those are compared.
        if sum(1 for t in named if re.search(r'-N\d+$', t)) > 1:
            continue
        keys = {norm(v) for v in named.values()}
        if len(keys) > 1:
            nums = {norm(v)[0] for v in named.values()}
            bad.append((len(nums) > 1, sorted(named.items())))
    hard = [b for b in bad if b[0]]
    print('\n%d assemblies of %d disagree with themselves about the room'
          % (len(bad), len(seen)))
    print('   of those, %d disagree on the room NUMBER, not just its wording'
          % len(hard))
    with (HERE / 'rdc_assembly_conflicts.csv').open('w', newline='') as f:
        w = csv.writer(f, lineterminator='\n')
        w.writerow(['different room number', 'tag', 'room in column D'])
        for isnum, items in sorted(bad, key=lambda b: not b[0]):
            for tag, r in items:
                w.writerow(['yes' if isnum else 'wording only', tag, r])
            w.writerow([])
    print('   wrote rdc_assembly_conflicts.csv')


if __name__ == '__main__':
    main()
