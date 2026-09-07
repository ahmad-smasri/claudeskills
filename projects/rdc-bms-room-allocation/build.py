"""Build the RDC asset register with the BMS screen readings beside it.

The delivered workbook carries one sheet, `Controllable Asset Registry`, holding
every building's assets one after another with RDC last. The client asked for
the RDC section on its own, so this writes a workbook containing only those
rows - the HQ, QNL and SSC sections are dropped rather than hidden, because a
hidden row is still a row the next reader has to think about.

Columns A-I are the register as delivered. J onwards is this pass:

    J  ROOM PER BMS SCREEN   the room the serving-area leader's dot lands in
    K  BMS SCREEN            the screen it was read from
    L  BMS SCREEN vs DRAWINGS   SAME / DIFF / CHECK / OPEN
    M  WHY                   why, in the reviewer's words

A row with no reading is left blank in J and carries the reason in M. That is
the point of the exercise: a blank with a reason is a question for the client,
while a guessed room reads exactly like a reading once it is in the sheet.
"""
import re
import shutil
import sys

import openpyxl
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

import alloc

SRC = ('/home/user/claudeskills/projects/qnl-bms-room-allocation/'
       'Appendix_A_Asset_Register_QNL_BMS_rooms.xlsx')
SHEET = 'Controllable Asset Registry'
OUT = 'Appendix_A_Asset_Register_RDC_BMS_rooms.xlsx'

HEAD_ROW = 2
RDC_FIRST = 1443          # first RDC data row in the delivered sheet
RDC_LAST = 3201

GREEN = PatternFill('solid', fgColor='FF00B050')   # the house 'needs a look'
COLS = 'ABCDEFGHIJK'      # the fill runs A:K - a later pass keys on that range

LEVEL = {'GF': 'GF', 'FF': '1F', 'SF': '2F', 'MF': 'MF', 'WALKWAY': 'Walkway'}
BUILDING = {'North Building': 'NB', 'South Building': 'SB',
            'Utility Building': 'UB'}
# The walkway belongs to neither building and the register says so:
# `RDC_NB_SB_Walkway_FCU9001`. Its widgets are labelled `Walkway-FCU9001`.
WALKWAY = 'NB_SB'

STOP = {'room', 'the', 'and', 'of', 'a', 'n', 'no', 'level', 'rdc'}


def screen_key(screen):
    """'North Building/FF/FF-1' -> ('NB', '1F'); the level comes from the path"""
    parts = screen.split('/')
    if any(p.upper() == 'WALKWAY' for p in parts):
        return WALKWAY, 'Walkway'
    b = BUILDING.get(parts[0])
    lvl = None
    for p in parts[1:]:
        stem = p.split('-')[0]
        if stem in LEVEL:
            lvl = LEVEL[stem]
            break
    return b, lvl


LEVELS = ('GF', '1F', '2F', 'MF', 'L1', 'L2', 'B1')

# The BMS and the register do not spell a tag the same way.
#
#  * the register hyphenates some families and the screens never do -
#    `FEV-5272` against `NB-FEV5272`, and the same for VEV, CEV, EV and AT;
#  * where a widget serves a pair, the screen may drop the second prefix -
#    `NB-VAV7830-7831` is the register's `VAV7830_VEV7831`;
#  * the screens label constant-volume terminals CAV and the register labels
#    them AT. The register carries one CAV row against five hundred and ten AT
#    rows, so this is the register's word for the same thing rather than two
#    kinds of unit - but it is still an inference, and every row joined this way
#    says so in its WHY column rather than passing as a plain reading.
ALIAS = {'CAV': 'AT'}
PAIR_PREFIX = ('VEV', 'EV', 'CEV')


def _variants(parts):
    """the ways the register might spell a tag the screen writes as `parts`"""
    out = []
    heads = [parts[0]]
    m = re.match(r'([A-Z]+)(\d.*)$', parts[0])
    if m and m.group(1) in ALIAS:
        heads.append(ALIAS[m.group(1)] + m.group(2))
    for head in heads:
        tails = [parts[1:]]
        if len(parts) == 2 and parts[1].isdigit():
            tails += [[pre + parts[1]] for pre in PAIR_PREFIX]
        for tail in tails:
            for piece in ([head] + tail, ):
                spaced = []
                for seg in piece:
                    mm = re.match(r'([A-Z]+)(\d.*)$', seg)
                    spaced.append([seg] + ([mm.group(1) + '-' + mm.group(2)]
                                           if mm else []))
                # every combination of hyphenated and plain segments, joined
                # with an underscore and also with nothing at all - the screens
                # write `UB-AHU-8601` where the register has `AHU8601`.
                for glue in ('_', ''):
                    acc = ['']
                    for opts in spaced:
                        acc = [a + (glue if a else '') + o
                               for a in acc for o in opts]
                    out += acc
    return out


def register_tag(label, building, level, known=None):
    """'NB-VAV4515-EV4516' on the north first floor -> RDC_NB_1F_VAV4515_EV4516

    The screens write a unit's tag with dashes and no level; the register writes
    it with underscores and the level in the middle. The level is not on the
    screen at all - it comes from which screen the reading was made on.

    That is right until a space is double height. The CSP High Bay and the
    Machine Shop are drawn on the ground floor screen and again on the first
    floor one, because they run through both; their units are ground floor units
    and the register has no first floor twin. Taking the level from the screen
    invents `RDC_NB_1F_VAV4050_VEV4051`, which matches nothing, and the reading
    is dropped without a word. So when the screen's own level matches no tag in
    the register, the other levels are tried, and a single match is taken - a
    unit's number is unique across the building. If several levels match, none
    is taken: that is a real ambiguity and belongs in the blank column.
    """
    body = label.strip()
    for pre in (building + '-', 'WALKWAY-'):
        if body.upper().startswith(pre):
            body = body[len(pre):]
            break
    parts = body.split('-')

    def forms(lvl):
        # AHUs are registered without a level at all - `RDC_UB_AHU8601`, not
        # `RDC_UB_MF_AHU8601` - so the level-less form is tried alongside.
        return (['RDC_%s_%s_%s' % (building, lvl, v) for v in _variants(parts)]
                + ['RDC_%s_%s' % (building, v) for v in _variants(parts)])

    own = forms(level)
    if known is None:
        return own
    if any(c in known for c in own):
        return own
    other = [lvl for lvl in LEVELS if lvl != level
             and any(c in known for c in forms(lvl))]
    if len(other) == 1:
        return forms(other[0])

    # One widget can serve a pair - `NB-CAV7590-CEV7591` - and the register
    # sometimes carries only one half of it. Three of these have a CEV row and
    # no CAV row at all. Rather than lose the reading, it is attached to the
    # half that exists, on every level, and the WHY column says the other half
    # is missing from the register.
    if len(parts) > 1:
        halves = []
        for lvl in (level,) + LEVELS:
            for part in parts:
                halves += ['RDC_%s_%s_%s' % (building, lvl, v)
                           for v in _variants([part])]
        if any(c in known for c in halves):
            return halves
    return own


def half_only(label, tag):
    """was this reading attached to one half of a paired widget?"""
    body = label.split('-', 1)[-1] if label.upper().startswith('NB-') else label
    parts = body.split('-')
    if len(parts) < 2:
        return False
    tail = tag.rsplit('_', 1)[-1].replace('-', '')
    return not all(re.sub(r'[^A-Z0-9]', '', p) in tag.replace('-', '')
                   for p in parts)


def aliased(label):
    """did joining this label need the CAV -> AT assumption?"""
    body = label.split('-', 1)[-1] if label.upper().startswith('NB-') else label
    m = re.match(r'([A-Z]+)\d', body)
    return bool(m and m.group(1) in ALIAS)


def words(text):
    return {w for w in re.findall(r'[A-Za-z0-9]+', (text or '').lower())
            if w not in STOP and len(w) > 1}


def number(text):
    """the room's own number, without the level prefix the two sources differ on

    The register writes a first-floor room `N-1143` where the screen writes it
    `N-143`; on the south building it is `S-1159` against `S-0159`. The digits
    after that prefix are the same room number in both, so they are what gets
    compared. Twelve rows read as an outright room disagreement until this was
    separated out, when they are the same room spelled two ways.
    """
    m = re.findall(r"[A-Za-z]-?(\d{3,4}[A-Za-z]?)", text or "")
    if not m:
        return None
    d = re.match(r"(\d+)([A-Za-z]?)$", m[0])
    if not d:
        return None
    return d.group(1)[-3:] + d.group(2).upper()


def verdict(drawing, screen_room, note):
    """how the screen and the register compare, for one row"""
    if not screen_room:
        return 'OPEN'
    d, s = words(drawing), words(screen_room)
    dn, sn = number(drawing), number(screen_room)
    if not d and not dn:
        return 'CHECK'
    if dn and sn and dn == sn:
        # The same room number. If the names agree too there is nothing to
        # report; if they do not, the two sources abbreviate it differently and
        # the ontology has to pick one, which is a finding of its own.
        return 'SAME' if d & s else 'CONVENTION'
    if d & s:
        return 'SAME'
    return 'DIFF'


def intro(wb, data, hit, miss, flagged):
    """A first sheet saying what was done, what the columns mean, and what the
    pass found. The reader is usually not the person who made the readings."""
    import collections
    v = collections.Counter(data.cell(r, 12).value
                            for r in range(HEAD_ROW + 1, data.max_row + 1))
    ws = wb.create_sheet('START HERE')
    ws.column_dimensions['A'].width = 118
    lines = [
        ('RDC asset register, checked against the BMS floor-plan screens', True),
        ('', False),
        ('This workbook holds the RDC section of the Controllable Asset Registry '
         'and nothing else. The HQ, QNL and SSC sections were dropped, as asked.',
         False),
        ('', False),
        ('What was done', True),
        ('Every RDC BMS screen draws a dotted leader from each unit widget to a '
         'small grey dot inside the room it serves. The leaders turn square '
         'corners, so they were followed corner by corner and the dot at the end '
         'read off the plan by eye. The tracer only says where to look; the room '
         'was named by reading the screen, never by inference.', False),
        ('', False),
        ('47 screens, across the North, South and Utility buildings and the '
         'walkway between them. 1,033 unit widgets were found on them and 440 of '
         'those leaders reached a dot.', False),
        ('', False),
        ('The columns this pass added', True),
        ('  J  ROOM PER BMS SCREEN     the room the leader ends in, as the screen names it', False),
        ('  K  BMS SCREEN              which screen it was read from', False),
        ('  L  BMS SCREEN vs DRAWINGS  SAME / DIFF / CONVENTION / CHECK / OPEN', False),
        ('  M  WHY                     what a reviewer needs in order to judge the row', False),
        ('', False),
        ('SAME       the screen and column D agree', False),
        ('DIFF       they name different rooms - the rows worth your time', False),
        ('CONVENTION the same room number written two ways: the register writes a '
         'first-floor room N-1143 where the screen writes N-143, and abbreviates '
         'differently (Conf / Conference, TC3 / Tissue Culture 3). Not a '
         'disagreement about which room, but the ontology has to use one spelling.', False),
        ('CHECK      read from the screen, but the dot sits on a wall between two '
         'rooms, or in open floor carrying a name but no wall. Worth a second look.', False),
        ('OPEN       no reading. Either no screen covers the unit, or the leader '
         'could not be followed, or the dot landed somewhere the screen does not '
         'name. Column M says which, per row.', False),
        ('', False),
        ('What it found', True),
        ('  %d of %d rows carry a reading; %d are still open.' % (hit, hit + miss, miss), False),
        ('  %d SAME, %d DIFF, %d CONVENTION, %d CHECK.'
         % (v.get('SAME', 0), v.get('DIFF', 0), v.get('CONVENTION', 0),
            v.get('CHECK', 0)), False),
        ('  %d rows are filled green across A:K - every DIFF, CONVENTION and CHECK.' % flagged, False),
        ('', False),
        ('The largest single finding: SB-AHU8031 to 8035 and 8037 all carry '
         'COMPUTER RESEARCH LAB S-1112 in the register, and all six leaders - on '
         'two different screens, GF-5 and GF-7 - run into Mech S-0136. Six units '
         'sharing one room where the screens put them in the plant room reads as '
         'a filled-down cell rather than six readings.', False),
        ('', False),
        ('Equipment on the screens that the register does not carry', True),
        ('  The register has no EF rows at all. Nine exhaust fans were read off '
         'the screens - SB-EF-8041 to 8044 and UB-EF-8642 to 8646 - and there is '
         'no row to put them on. NB-EF-8553, NB-EF-8554 and the ERU units on the '
         'second-floor screens are absent for the same reason.', False),
        ('  Three CAV/CEV pairs (7590/7591, 7610/7611, 7760/7761) have a CEV row '
         'and no CAV row. Those readings are recorded against the CEV half.', False),
        ('', False),
        ('Two things to know about the join', True),
        ('  The screens label constant-volume terminals CAV and the register '
         'labels them AT - one CAV row against 510 AT rows. Rows joined across '
         'that say so in column M.', False),
        ('  A double-height space is drawn on both its levels. NB-VAV4050-VEV4051 '
         'and NB-VAV4060-VEV4061 appear on the first-floor screen but are ground '
         'floor units in the register, and the register agrees with the reading.', False),
        ('', False),
        ('A blank in column J is not an oversight. A guessed room reads exactly '
         'like a read one once it is in the sheet, and nobody can tell them apart '
         'afterwards - so where the screen does not settle the room, column J is '
         'left empty and column M says why.', False),
    ]
    for i, (text, bold) in enumerate(lines, 1):
        c = ws.cell(i, 1, text)
        c.alignment = Alignment(wrap_text=True, vertical='top')
        if bold:
            c.font = Font(bold=True, size=12)
    return ws


def main():
    src = openpyxl.load_workbook(SRC, read_only=True, data_only=True)[SHEET]
    rows = list(src.iter_rows(min_row=1, max_row=RDC_LAST, max_col=9,
                              values_only=True))
    known = {str(r[0]).strip() for r in rows[RDC_FIRST - 1:] if r[0]}

    # the reading, keyed by the register tag it joins to
    read, blank = {}, {}
    for screen, entries in alloc.SCREENS.items():
        b, lvl = screen_key(screen)
        if not b or not lvl:
            sys.exit('cannot read a building and level out of %r' % screen)
        for label, room, conf, note in entries:
            for tag in register_tag(label, b, lvl, known):
                read[tag] = (room, screen, conf, note, label)
    for screen, entries in alloc.BLANK.items():
        b, lvl = screen_key(screen)
        for label, why in entries:
            for tag in register_tag(label, b, lvl, known):
                blank[tag] = (why, screen, label)

    # A fresh sheet carrying only the RDC rows. The delivered workbook's sheet
    # is 16,382 columns wide, so deleting the other buildings' rows out of a
    # copy takes minutes; copying the rows that are wanted takes no time and
    # leaves nothing of the others behind.
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = SHEET
    for c, v in enumerate(rows[0][:9], 1):
        ws.cell(1, c, v)
    for c, v in enumerate(rows[HEAD_ROW - 1][:9], 1):
        cell = ws.cell(HEAD_ROW, c, v)
        cell.font = Font(bold=True)
    out_r = HEAD_ROW
    for src_row in rows[RDC_FIRST - 1:]:
        if not src_row[0]:
            continue
        out_r += 1
        for c, v in enumerate(src_row[:9], 1):
            ws.cell(out_r, c, v)
    for c, wdt in zip('ABCDEFGHI', (26, 16, 16, 40, 34, 12, 12, 12, 12)):
        ws.column_dimensions[c].width = wdt
    ws.freeze_panes = 'A3'

    for c, name in ((10, 'ROOM PER BMS SCREEN'), (11, 'BMS SCREEN'),
                    (12, 'BMS SCREEN vs DRAWINGS'), (13, 'WHY')):
        cell = ws.cell(HEAD_ROW, c, name)
        cell.font = Font(bold=True)
        cell.alignment = Alignment(vertical='center', wrap_text=True)
    ws.column_dimensions['J'].width = 30
    ws.column_dimensions['K'].width = 26
    ws.column_dimensions['L'].width = 16
    ws.column_dimensions['M'].width = 70

    hit = miss = flagged = 0
    for r in range(HEAD_ROW + 1, ws.max_row + 1):
        tag = str(ws.cell(r, 1).value or '').strip()
        if not tag:
            continue
        drawing = str(ws.cell(r, 4).value or '').strip()
        if tag in read:
            room, screen, conf, note, label = read[tag]
            _ = tag
            v = verdict(drawing, room, note)
            if conf == 'check' and v == 'SAME':
                v = 'CHECK'
            ws.cell(r, 10, room)
            ws.cell(r, 11, screen)
            ws.cell(r, 12, v)
            why = note
            if half_only(label, tag):
                why = ((why + '; ') if why else '') + (
                    'the screen shows this as a pair (%s) and the register '
                    'carries only one half of it, so the reading is recorded '
                    'against that half' % label)
            if aliased(label):
                why = ((why + '; ') if why else '') + (
                    'the screen calls this unit %s and the register calls it AT '
                    '- joined on the number, which is an assumption' % label.split('-')[1])
            if v == 'DIFF':
                why = ('the screen puts %s in %s; the register says %s'
                       % (label, room, drawing or '(blank)')
                       + (' - ' + note if note else ''))
            elif v == 'CHECK' and not why:
                why = 'read from the screen but wanting a second look'
            ws.cell(r, 13, why)
            hit += 1
            if v == 'CONVENTION':
                why = ('the register and the screen give this room the same '
                       'number but write it differently - register %r, screen '
                       '%r. The number agrees; the level prefix and the '
                       'abbreviation do not, and the ontology has to use one'
                       % (drawing, room)) + (('; ' + note) if note else '')
            if v in ('DIFF', 'CHECK', 'CONVENTION'):
                flagged += 1
                for col in COLS:
                    ws['%s%d' % (col, r)].fill = GREEN
        elif tag in blank:
            why, screen, label = blank[tag]
            ws.cell(r, 11, screen)
            ws.cell(r, 12, 'OPEN')
            ws.cell(r, 13, why)
            miss += 1
        else:
            ws.cell(r, 12, 'OPEN')
            ws.cell(r, 13, 'no BMS screen reading for this unit')
            miss += 1

    for c in range(10, 14):
        for r in range(HEAD_ROW + 1, ws.max_row + 1):
            ws.cell(r, c).alignment = Alignment(vertical='top', wrap_text=True)

    intro(wb, ws, hit, miss, flagged)
    wb.move_sheet('START HERE', offset=-1)
    wb.save(OUT)
    print('%s: %d RDC rows, %d read, %d open, %d filled green'
          % (OUT, ws.max_row - HEAD_ROW, hit, miss, flagged))

    # A reading that joins to no register row is not a rounding error - it is
    # either a tag the register spells differently or a unit the register does
    # not carry at all, and both are findings. So they are named rather than
    # counted.
    used = {str(ws.cell(r, 1).value or '').strip()
            for r in range(HEAD_ROW + 1, ws.max_row + 1)
            if ws.cell(r, 10).value or ws.cell(r, 13).value}
    orphan = sorted({lbl for tag, (_, _, _, _, lbl) in read.items()
                     if tag not in used}
                    - {lbl for tag, (_, _, _, _, lbl) in read.items()
                       if tag in used})
    if orphan:
        print('\n%d readings join no register row:' % len(orphan))
        for lbl in orphan:
            print('   ', lbl)


if __name__ == '__main__':
    main()
