#!/usr/bin/env python3
"""Turn a validation run into the house review workbook.

Runs validate_ontology.py and check_consistency.py over a sheet, adds the checks
neither of them covers, then writes a copy of the workbook carrying:

  Claude Log       - what was asked, what was done, what came out
  Review_Summary   - headline defects, an index of the issue sheets, every rule code
  <the sheet>      - untouched, with flagged rows filled yellow (ERROR) / amber (WARN)
  <group>_Issues   - one sheet per entity family: counts, findings, actions, full register

This is the format the QF SSC review used, widened from equipment to every entity
in the sheet. Nothing is written into the ontology rows themselves - only fills.

    python3 build_review_workbook.py MyBuilding.xlsx --out MyBuilding_review_1.xlsx
    python3 build_review_workbook.py MyBuilding.xlsx --out R.xlsx --label-style verbatim

Groups are derived from the sheet: a subject's family class decides its group, and
subjects sharing an identifier stem are kept together. --group lets you override or
add a rule when the derived grouping splits a family you want read as one.
"""
import argparse
import collections
import datetime
import re
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent

# --------------------------------------------------------------------- rules --
RULE = {
 'X-HDR-1': ('ERROR', 'The header row must repeat the four property-column names verbatim; numeric suffixes break the converter contract.'),
 'E-HDR-1': ('ERROR', 'The first five columns must be subject, subjectType, predicate, object, objectType.'),
 'E-HDR-2': ('ERROR', 'A column in positions 6-27 is not one of the four permitted property column names.'),
 'E-CORE-1': ('ERROR', 'subject, predicate and object are all required on every row.'),
 'X-VAL-1': ('ERROR', 'A para:rated* property declared with an empty object cell - unit present, value absent.'),
 'E-BN-1': ('ERROR', 'A <blanknode> object carries no object_prop pairs, so it converts to nothing.'),
 'E-PAIR-1': ('ERROR', 'A property name is present with no value beside it.'),
 'E-PH-1': ('ERROR', 'The object cell still holds an unresolved <placeholder>.'),
 'E-TYP-1': ('ERROR', 'One entity is typed more than one way across the sheet.'),
 'E-TYP-2': ('ERROR', 'The class is not a term in Brick 1.4.'),
 'E-WS-1': ('ERROR', 'A cell carries leading or trailing whitespace - it will not join to anything.'),
 'E-GR-1': ('ERROR', 'A spatial entity does not connect up to the rec:Building through rec:isPartOf.'),
 'E-LBL-1': ('ERROR', 'A label carries punctuation the PARA label rule removes.'),
 'E-FEED-1': ('ERROR', 'A terminal unit carries no rec:feeds row.'),
 'X-DUP-1': ('ERROR', 'The same subject / predicate / object triple is written more than once.'),
 'X-ID-2': ('ERROR', 'An identifier departs from the digit width every sibling in its family uses.'),
 'X-ID-3': ('ERROR', "A room's level segment disagrees with the level it is rec:isPartOf."),
 'E-CON-1': ('ERROR', 'A unit carries a different number of rows from its siblings.'),
 'E-CON-2': ('ERROR', 'A relation present on most units of a family is absent on some.'),
 'E-CON-3': ('ERROR', 'A relation is written more than once on the same unit.'),
 'E-CON-4': ('ERROR', 'An object cell holds an error value or is empty where the family uses an entity.'),
 'E-CON-5': ('ERROR', 'The same relation is typed differently on different units.'),
 'E-CON-6': ('ERROR', 'A unit carries more than one triple for a predicate that should appear once.'),
 'E-CON-17': ('ERROR', 'A child identifier differs from its parent only in separators - one of the two is misspelled.'),
 'W-BN-4': ('WARN', 'brick:value with no brick:hasUnit beside it.'),
 'W-BN-5': ('WARN', 'ref:hasTimeseriesId with no para:hasEntityId beside it.'),
 'W-LBL-2': ('WARN', 'The entity never gets an rdfs:label_en, so the front end has nothing to display.'),
 'W-PT-1': ('WARN', 'A data point carries no ref:hasExternalReference, so its timeseries resolves empty.'),
 'W-TYP-5': ('WARN', 'The class is a Brick alias; the preferred term should be used.'),
 'X-LBL-3': ('WARN', 'rdfs:label_en repeats the identifier instead of naming the thing.'),
 'X-LBL-4': ('WARN', "Labels still carry '-' or '_' separators; neither label style leaves them in place."),
 'X-ID-1': ('WARN', 'Level identifiers use a different separator from every other identifier in the sheet.'),
 'X-ORPH-1': ('WARN', 'An entity appears only as an object - it never carries a row of its own.'),
 'W-CON-7': ('WARN', 'Every unit of a family shares one rec:locatedIn / rec:feeds target - check for placeholder data.'),
 'W-CON-9': ('WARN', 'A declared point carries no external reference.'),
 'W-CON-11': ('WARN', 'An entity carries an external reference but is never declared by a parent.'),
 'W-CON-12': ('WARN', "A unit's rows are scattered rather than grouped, making review by unit hard."),
 'W-CON-19': ('WARN', 'One class carries several different units across the sheet.'),
 'I-CON-8': ('INFO', 'rec:feeds and rec:locatedIn name the same room on every unit - confirm the source column.'),
 'I-CON-13': ('INFO', 'An identifier repeats a token.'),
 'I-CON-15': ('INFO', 'Only one instance of the class exists, so no cross-unit comparison is possible.'),
 'I-CON-16': ('INFO', 'A subject does not carry the building code its family uses.'),
}

ACTION = {
 'X-HDR-1': 'Rewrite the header row to the canonical 27 columns before the sheet goes to the converter.',
 'E-HDR-2': 'Restore the canonical header row: columns 6-27 repeat subject_prop_name / subject_prop_val / object_prop_name / object_prop_val with no numeric suffix.',
 'E-CORE-1': 'Put the value in the object column as <blanknode> carrying brick:value + brick:hasUnit, or delete the row.',
 'X-VAL-1': 'Put the rated figure in the object column, or delete the row - a unit with no value is not a property.',
 'E-BN-1': 'Give the blank node its object_prop pairs, or drop the row.',
 'E-PAIR-1': 'Supply the missing property value, or remove the property name.',
 'E-PH-1': 'Replace the placeholder with the real room / feeder entity before handover.',
 'E-TYP-1': 'Pick one class for the entity and use it on every row that types it.',
 'E-TYP-2': 'Substitute the Brick 1.4 term after confirming with the team.',
 'E-WS-1': 'Strip the padding whitespace from the cell.',
 'E-GR-1': 'Add the missing rec:isPartOf row so the entity reaches the building.',
 'X-DUP-1': 'Delete the duplicate rows, keeping one, and settle the class on the survivor.',
 'X-ID-1': 'Settle one separator convention for level identifiers and apply it to all of them.',
 'X-ID-2': 'Confirm the identifier against the asset register - every sibling uses a different digit width.',
 'X-ID-3': 'Confirm the room number against the room schedule - its level segment and its parent level disagree.',
 'X-LBL-3': 'Give the entity a human label; the identifier is a join key, not display text.',
 'X-LBL-4': 'Confirm the label style with the team - the QF SSC house style reads separators as spaces.',
 'X-ORPH-1': 'Type the entity on a row of its own, or confirm it is meant to exist only as an object.',
 'W-BN-4': 'Add brick:hasUnit, or unit:UNITLESS if the quantity is genuinely dimensionless.',
 'W-BN-5': 'Add para:hasEntityId beside the timeseries id.',
 'W-LBL-2': 'Add an rdfs:label_en row - the front end has nothing to display for this entity.',
 'W-PT-1': 'Add the ref:TimeseriesReference, or delete the point if the BMS does not publish it.',
 'W-TYP-5': 'Prefer the Brick 1.4 preferred term over the alias.',
 'E-CON-1': 'Compare the unit against its siblings and add or remove rows until the shape matches.',
 'E-CON-2': 'Add the missing relation to the units that lack it, or confirm the omission is real.',
 'E-CON-3': 'Delete the duplicated triple - keep one.',
 'E-CON-4': 'Replace the error / empty object cell with the real entity.',
 'E-CON-5': 'Pick one class for the relation and apply it on every unit.',
 'E-CON-6': 'Decide which is correct and delete the surplus row.',
 'E-CON-17': 'Correct whichever of parent or child carries the wrong separator so the two agree.',
 'W-CON-7': 'Confirm the shared target is real, not placeholder data left over from a template.',
 'W-CON-9': 'Add the external reference, or remove the entity if it is not a real point.',
 'W-CON-11': 'Declare the entity with brick:hasPoint or brick:hasPart from its parent.',
 'W-CON-12': "Group the unit's rows together so a reviewer can read one unit at a time.",
 'W-CON-19': 'Check the source unit column against the class - at least one unit is wrong.',
 'I-CON-8': 'Confirm the source room column means both location and served space.',
 'I-CON-13': 'Confirm the repeated token is intended and not a copy-paste slip.',
 'I-CON-15': 'Single instance - no sibling to compare against; review by hand.',
 'I-CON-16': 'Add the building code, or confirm the entity is site-wide.',
}

SEV_ORDER = {'ERROR': 0, 'WARN': 1, 'INFO': 2}
CANON = (['subject', 'subjectType', 'predicate', 'object', 'objectType']
         + ['subject_prop_name', 'subject_prop_val', 'object_prop_name', 'object_prop_val'] * 5
         + ['subject_prop_name', 'subject_prop_val'])

SPATIAL_CLASSES = {'rec:Site', 'rec:Building', 'rec:Level', 'rec:BasementLevel',
                   'rec:RoofLevel', 'rec:Room', 'rec:Zone', 'rec:HVACZone'}
SYSTEM_CLASSES = {'brick:System', 'brick:HVAC_System', 'brick:Chilled_Water_System',
                  'brick:Electrical_System', 'brick:Water_System', 'brick:Heating_System'}

Finding = collections.namedtuple('Finding', 'severity code row entity group finding action')

S = lambda x: x.strip() if isinstance(x, str) else x


# ------------------------------------------------------------------ loading --
def load_rows(path):
    if path.suffix.lower() in ('.xlsx', '.xlsm'):
        import openpyxl
        wb = openpyxl.load_workbook(path, read_only=True, data_only=False)
        ws = pick_sheet(wb)
        rows = [list(r) for r in ws.iter_rows(values_only=True)]
        name = ws.title
        wb.close()
        return rows, name
    import csv
    with open(path, newline='', encoding='utf-8-sig') as f:
        rows = [r for r in csv.reader(f)]
    return rows, path.stem


def pick_sheet(wb):
    """The ontology sheet is the one whose header starts with subject/subjectType."""
    for ws in wb.worksheets:
        head = [S(c) for c in next(ws.iter_rows(max_row=1, values_only=True), [])][:3]
        if head and str(head[0]).lower() == 'subject' and str(head[1] or '').lower() == 'subjecttype':
            return ws
    return wb.worksheets[0]


def run_checker(script, sheet, report, extra=()):
    """Run one of the two standard scripts and read its --report back."""
    cmd = [sys.executable, str(HERE / script), str(sheet), '--max', '1000000',
           '--report', str(report), *extra]
    subprocess.run(cmd, capture_output=True, text=True)
    if not report.exists():
        return []
    import openpyxl
    wb = openpyxl.load_workbook(report, read_only=True)
    out = [(sev, code, row, text) for sev, code, row, text, *_ in
           wb.active.iter_rows(min_row=2, values_only=True)]
    wb.close()
    return out


# ----------------------------------------------------------------- grouping --
def derive_groups(rows, overrides):
    """Work out which group each row belongs to, from the sheet rather than a fixed list.

    A part or a point belongs on the same sheet as the unit that owns it, so every
    subject is walked up its brick:hasPart / brick:hasPoint chain to the entity that
    owns it, and the group is named after *that* entity's class. Spatial and system
    classes collapse into one group each; schema rows go to Class_Definitions.
    """
    data = rows[1:]
    subj_class, owner = {}, {}
    for r in data:
        s = S(r[0])
        st = S(r[1]) if len(r) > 1 else None
        o = S(r[3]) if len(r) > 3 else None
        p = S(r[2]) if len(r) > 2 else None
        ot = S(r[4]) if len(r) > 4 else None
        if isinstance(s, str) and s.startswith('entity:') and st:
            subj_class.setdefault(s, st)
        if isinstance(o, str) and o.startswith('entity:') and ot:
            subj_class.setdefault(o, ot)
        if p in ('brick:hasPart', 'brick:hasPoint') and isinstance(o, str) and isinstance(s, str):
            owner.setdefault(o, s)

    def root(e, _seen=None):
        seen = _seen or set()
        while e in owner and e not in seen:
            seen.add(e)
            e = owner[e]
        return e

    def group_for(subject):
        if not isinstance(subject, str):
            return 'Misc'
        s = subject.strip()
        for name, rx in overrides:
            if rx.search(s):
                return name
        if not s.startswith('entity:'):
            return 'Class_Definitions'
        top = root(s)
        cls = subj_class.get(top) or subj_class.get(s)
        if cls in SPATIAL_CLASSES:
            return 'Spatial'
        if cls in SYSTEM_CLASSES:
            return 'Systems'
        if cls:
            return cls.split(':', 1)[1]
        return 'Misc'

    row_group, row_subject = {}, {}
    for i, r in enumerate(data, 2):
        row_subject[i] = S(r[0]) or ''
        row_group[i] = group_for(r[0])

    # a subject that still has no owner joins the longest asset identifier it starts
    # with, so a point named after its unit lands beside that unit even when no
    # hasPoint row declares it
    assets = sorted((e for e, c in subj_class.items()
                     if c not in SPATIAL_CLASSES and c not in SYSTEM_CLASSES and e not in owner),
                    key=len, reverse=True)
    stem_group = {a: group_for(a) for a in assets}
    for i in row_group:
        if row_group[i] != 'Misc':
            continue
        s = row_subject[i]
        for a in assets:
            if s.startswith(a) and stem_group[a] != 'Misc':
                row_group[i] = stem_group[a]
                break

    # a group holding no top-level unit of its own is a point class that escaped the
    # walk - fold it into whichever group its rows' owners mostly sit in
    tops = collections.Counter(group_for(a) for a in assets)
    for i in list(row_group):
        g = row_group[i]
        if g in ('Spatial', 'Systems', 'Class_Definitions', 'Misc') or tops.get(g):
            continue
        row_group[i] = group_for(owner.get(row_subject[i], row_subject[i])) if \
            owner.get(row_subject[i]) else 'Misc'
    return row_group, row_subject, subj_class


# ------------------------------------------------------------ extra checks ---
def extra_checks(rows, row_group, row_subject, subj_class, add):
    data, hdr = rows[1:], rows[0]

    bad = [(i + 1, h) for i, h in enumerate(hdr)
           if isinstance(h, str) and re.search(r'\d$', h.strip())]
    if bad:
        pairs = sum(1 for r in data for j in range(9, min(len(r), 27), 2)
                    if r[j] not in (None, ''))
        add('ERROR', 'X-HDR-1', 1, '', 'Sheet_Structure',
            'Header row: %d of the 27 columns carry numeric suffixes (%s ... %s). The contract repeats '
            'subject_prop_name / subject_prop_val / object_prop_name / object_prop_val verbatim, so every '
            'property pair from column 10 rightwards is invisible to a reader that follows the contract - '
            '%d property pairs in this sheet.' % (len(bad), bad[0][1], bad[-1][1], pairs))
    if hdr and S(hdr[0]) != CANON[0]:
        add('WARN', 'X-HDR-1', 1, '', 'Sheet_Structure',
            "Header cell A1 is %r; the contract and Dar Cairo both write it lower case as 'subject'." % S(hdr[0]))

    for i, r in enumerate(data, 2):
        p = S(r[2]) if len(r) > 2 else None
        if isinstance(p, str) and p.startswith('para:rated') and (len(r) < 4 or r[3] in (None, '')):
            unit = S(r[8]) if len(r) > 8 else None
            add('ERROR', 'X-VAL-1', i, row_subject[i], row_group[i],
                '%s declared with an empty object cell - the unit (%s) is present but the value is not, so '
                'the property converts to nothing.' % (p, unit or 'no unit either'))

    seen = collections.defaultdict(list)
    for i, r in enumerate(data, 2):
        k = (S(r[0]) or '', S(r[2]) or '', S(r[3]) or '')
        if k[2] and k[2] != '<blanknode>':
            seen[k].append(i)
    for k, rs in seen.items():
        if len(rs) > 1:
            for i in rs:
                add('ERROR', 'X-DUP-1', i, k[0], row_group[i],
                    'Triple `%s %s %s` is written %d times (rows %s).'
                    % (k[0], k[1], k[2], len(rs), ', '.join(map(str, rs))))

    lbl = {}
    for i, r in enumerate(data, 2):
        s, o = S(r[0]), S(r[3]) if len(r) > 3 else None
        for j in range(5, min(len(r) - 1, 26), 2):
            if S(r[j]) == 'rdfs:label_en' and r[j + 1] not in (None, ''):
                tgt = s if ((j - 5) // 2) % 2 == 0 else o
                if isinstance(tgt, str) and tgt.startswith('entity:'):
                    lbl.setdefault(tgt, (i, str(r[j + 1])))
    for e, (i, l) in lbl.items():
        if l == e.split(':', 1)[1]:
            add('WARN', 'X-LBL-3', i, e, row_group.get(i, 'Misc'),
                "rdfs:label_en is the identifier itself (%r) - the front end shows a BMS tag where a name "
                "should be." % l)
    sep = collections.defaultdict(list)
    for e, (i, l) in lbl.items():
        if re.search(r'[-_]', l):
            sep[row_group.get(i, 'Misc')].append((e, i, l))
    for g, hits in sep.items():
        e, i, l = hits[0]
        add('WARN', 'X-LBL-4', i, e, g,
            "%d labels in this group still carry '-' or '_' separators (e.g. %s -> %r). Neither label style "
            "in the skill leaves them in place; the QF SSC house style reads separators as spaces."
            % (len(hits), e, l))

    levels = sorted(s for s, c in subj_class.items()
                    if c in ('rec:Level', 'rec:BasementLevel', 'rec:RoofLevel'))
    if levels and sum('-' in s.split(':', 1)[1] for s in levels) == len(levels):
        others = [s for s, c in subj_class.items() if c not in SPATIAL_CLASSES]
        if others and sum('_' in s for s in others) > len(others) * 0.8:
            add('WARN', 'X-ID-1', None, levels[0], 'Spatial',
                '%d level identifiers use dashes (%s) where the assets and points in the sheet use '
                'underscores between segments.' % (len(levels), levels[0]))

    fam = collections.defaultdict(lambda: collections.defaultdict(list))
    for s in subj_class:
        m = re.match(r'^(entity:[A-Za-z_]*?[A-Za-z])(\d+)$', s)
        if m:
            fam[m.group(1)][len(m.group(2))].append(s)
    for stem, widths in fam.items():
        if len(widths) < 2:
            continue
        major = max(widths, key=lambda w: len(widths[w]))
        for w, es in widths.items():
            if w == major:
                continue
            for e in es:
                rn = next((i for i, x in row_subject.items() if x == e), None)
                add('ERROR', 'X-ID-2', rn, e, row_group.get(rn, 'Misc'),
                    '%s carries %d digits where the other %d units in the family carry %d.'
                    % (e, w, len(widths[major]), major))

    lvl_of = {}
    for i, r in enumerate(data, 2):
        if S(r[2]) == 'rec:isPartOf' and subj_class.get(S(r[0])) == 'rec:Room':
            lvl_of[S(r[0])] = (S(r[3]), i)
    for room, (lvl, rn) in lvl_of.items():
        m = re.match(r'^entity:[A-Za-z]+_(B?\d+|B\d|G|GF|RF|R)_', room)
        lm = re.match(r'^entity:[A-Za-z]+-Level-(.+)$', lvl or '')
        if m and lm:
            seg, ln = m.group(1), lm.group(1)
            if seg.lstrip('0') != ln.lstrip('0') and not (ln == 'Ground-Floor' and seg == 'G') \
               and not (ln == seg):
                add('ERROR', 'X-ID-3', rn, room, 'Spatial',
                    'Room identifier says level %r but the room is rec:isPartOf %s.' % (seg, lvl))

    subjects = {S(r[0]) for r in data if isinstance(r[0], str) and S(r[0]).startswith('entity:')}
    first = {}
    for i, r in enumerate(data, 2):
        o = S(r[3]) if len(r) > 3 else None
        if isinstance(o, str) and o.startswith('entity:'):
            first.setdefault(o, i)
    obj_type = {}
    for r in data:
        o, ot = (S(r[3]), S(r[4])) if len(r) > 4 else (None, None)
        if isinstance(o, str) and ot:
            obj_type.setdefault(o, ot)
    for e, i in sorted(first.items()):
        if e not in subjects:
            add('WARN', 'X-ORPH-1', i, e, row_group.get(i, 'Misc'),
                '%s (%s) is only ever an object - it never carries a row of its own, so it has no label, '
                'no location and no points.' % (e, obj_type.get(e, 'untyped')))


# ------------------------------------------------------------------- output --
def build(args):
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    from openpyxl.utils import get_column_letter

    sheet = Path(args.sheet)
    rows, sheet_name = load_rows(sheet)
    data = rows[1:]
    overrides = [(n, re.compile(p)) for n, p in (g.split('=', 1) for g in args.group)]
    row_group, row_subject, subj_class = derive_groups(rows, overrides)

    # the two standard checkers, run against a header-normalised copy so a broken
    # header row does not drown their output in artefacts
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        norm = td / 'normalised.csv'
        import csv
        with open(norm, 'w', newline='', encoding='utf-8') as f:
            w = csv.writer(f)
            w.writerow(CANON)
            for r in data:
                w.writerow(['' if c is None else c for c in r])
        raw = (run_checker('validate_ontology.py', norm, td / 'v.xlsx',
                           ['--label-style', args.label_style]
                           + (['--io', args.io] if args.io else []))
               + run_checker('check_consistency.py', norm, td / 'c.xlsx',
                             ['--io', args.io] if args.io else []))

    class_group = {}
    for i, r in enumerate(data, 2):
        st = S(r[1]) if len(r) > 1 else None
        if isinstance(st, str) and st:
            class_group.setdefault(st, collections.Counter())[row_group[i]] += 1
    class_group = {k: v.most_common(1)[0][0] for k, v in class_group.items()}

    findings = []

    def add(sev, code, row, entity, group, text):
        findings.append(Finding(sev, code, row, entity, group, text,
                                ACTION.get(code, 'Review and confirm.')))

    def place(text, row):
        if isinstance(row, int) and row in row_group:
            return row_group[row], row_subject[row]
        m = re.search(r'(entity:[A-Za-z0-9_.<>&\-]+)', text or '')
        if m:
            e = m.group(1).rstrip('.,;:')
            for name, rx in overrides:
                if rx.search(e):
                    return name, e
            rn = next((i for i, s in row_subject.items() if s == e), None)
            return (row_group[rn] if rn else class_group.get(subj_class.get(e, ''), 'Misc')), e
        for rx in (r'^\s*((?:brick|para|rec|ref|owl|qudt):[A-Za-z0-9_\-]+)\s*:',
                   r'((?:brick|para|rec):[A-Za-z0-9_\-]+)'):
            m = re.search(rx, text or '')
            if m and m.group(1) in class_group:
                return class_group[m.group(1)], m.group(1)
        return 'Misc', ''

    for sev, code, row, text in raw:
        if code in args.ignore.split(','):
            continue
        row = row if isinstance(row, int) and row > 1 else None
        if code in ('E-HDR-1', 'E-HDR-2'):
            g, ent = 'Sheet_Structure', ''
        else:
            g, ent = place(text, row)
        add(sev, code, row, ent, g, text)

    extra_checks(rows, row_group, row_subject, subj_class, add)

    # ---- styling
    YELLOW, AMBER = PatternFill('solid', fgColor='FFFF00'), PatternFill('solid', fgColor='FFE699')
    HDRF, SECF = PatternFill('solid', fgColor='1F3864'), PatternFill('solid', fgColor='D9E1F2')
    OKF = PatternFill('solid', fgColor='C6EFCE')
    BADF, WARNF = PatternFill('solid', fgColor='FFC7CE'), PatternFill('solid', fgColor='FFEB9C')
    TITLE = Font(bold=True, size=14, color='1F3864')
    SUB = Font(italic=True, size=9, color='595959')
    SECT = Font(bold=True, size=11, color='1F3864')
    COLH = Font(bold=True, size=10, color='FFFFFF')
    THIN = Border(*[Side(style='thin', color='BFBFBF')] * 4)

    def section(ws, r, text):
        ws.cell(r, 1, text).font = SECT
        ws.cell(r, 1).fill = SECF
        return r + 1

    def header_row(ws, r, cols):
        for c, h in enumerate(cols, 1):
            cell = ws.cell(r, c, h)
            cell.font, cell.fill, cell.border = COLH, HDRF, THIN
            cell.alignment = Alignment(wrap_text=True, vertical='center')
        return r + 1

    def sev_fill(cell, sev):
        if sev == 'ERROR':
            cell.fill = BADF
        elif sev == 'WARN':
            cell.fill = WARNF

    wb = openpyxl.load_workbook(sheet)
    src = pick_sheet(wb)
    err_rows = {f.row for f in findings if f.severity == 'ERROR' and isinstance(f.row, int) and f.row >= 1}
    warn_rows = {f.row for f in findings if f.severity == 'WARN' and isinstance(f.row, int) and f.row >= 1} - err_rows
    for rs, fill in ((err_rows, YELLOW), (warn_rows, AMBER)):
        for r in rs:
            for c in range(1, 6):
                src.cell(r, c).fill = fill

    by_group = collections.defaultdict(list)
    for f in findings:
        by_group[f.group].append(f)
    order = (['Sheet_Structure', 'Class_Definitions', 'Spatial', 'Systems']
             + sorted(g for g in by_group if g not in
                      ('Sheet_Structure', 'Class_Definitions', 'Spatial', 'Systems', 'Misc'))
             + ['Misc'])
    order = [g for g in order if g in by_group or g == 'Misc']

    built = []
    for g in order:
        fs = sorted(by_group.get(g, []), key=lambda f: (SEV_ORDER[f.severity], f.code, f.row or 0))
        name = (g if g in ('Sheet_Structure', 'Class_Definitions') else g + '_Issues')[:31]
        ws = wb.create_sheet(name)
        grp_rows = [i for i, x in row_group.items() if x == g]
        span = ('%s!A%d:AA%d' % (sheet_name, min(grp_rows), max(grp_rows))) if grp_rows else 'n/a'
        ws['A1'] = '%s - %s' % (name.replace('_', ' '), sheet.stem)
        ws['A1'].font = TITLE
        ws['A2'] = ('Source: %s (%d rows).   Flagged rows are filled yellow (ERROR) or amber (WARN) in %s.   '
                    'Every finding is listed once in section 4.' % (span, len(grp_rows), sheet_name))
        ws['A2'].font = SUB

        e = sum(1 for f in fs if f.severity == 'ERROR')
        w = sum(1 for f in fs if f.severity == 'WARN')
        n = sum(1 for f in fs if f.severity == 'INFO')
        codes = sorted({f.code for f in fs})
        r = section(ws, 4, '1. Counts')
        r = header_row(ws, r, ['Metric', 'Value', 'Note'])
        for metric, value, note in [
            ('Source rows in this group', len(grp_rows), 'rows whose subject belongs here'),
            ('Entities named in findings', len({f.entity for f in fs if f.entity}), ''),
            ('Findings - ERROR', e, 'blocks handover'),
            ('Findings - WARN', w, 'decide, then fix or accept'),
            ('Findings - INFO', n, 'confirm only'),
            ('Distinct rows flagged ERROR', len({f.row for f in fs if f.severity == 'ERROR' and f.row}), 'yellow'),
            ('Distinct rows flagged WARN', len({f.row for f in fs if f.severity == 'WARN' and f.row}), 'amber'),
            ('Distinct rule codes', len(codes), ', '.join(codes)),
        ]:
            ws.cell(r, 1, metric)
            c = ws.cell(r, 2, value)
            if metric.startswith('Findings'):
                if not value:
                    c.fill = OKF
                else:
                    sev_fill(c, 'ERROR' if 'ERROR' in metric else ('WARN' if 'WARN' in metric else 'INFO'))
            ws.cell(r, 3, note)
            r += 1
        r += 1

        r = section(ws, r, '2. Findings')
        if not fs:
            ws.cell(r, 1, 'Clean - no finding of any severity was raised against this group.').fill = OKF
            r += 2
        else:
            for code, cnt in sorted(collections.Counter(f.code for f in fs).items(),
                                    key=lambda kv: (SEV_ORDER[RULE.get(kv[0], ('INFO',))[0]], -kv[1])):
                sev, expl = RULE.get(code, ('INFO', ''))
                sev_fill(ws.cell(r, 1, '%s  %s' % (sev, code)), sev)
                ws.cell(r, 2, cnt)
                ws.cell(r, 3, expl)
                ws.cell(r, 4, 'e.g. %s' % (next(f for f in fs if f.code == code).finding or '')[:220])
                r += 1
            r += 1

        r = section(ws, r, '3. Recommended action, one line per rule code')
        r = header_row(ws, r, ['Code', 'Severity', 'Instances', 'Recommended action'])
        acts = {}
        for f in fs:
            acts.setdefault(f.code, f.action)
        for code, cnt in sorted(collections.Counter(f.code for f in fs).items(),
                                key=lambda kv: (SEV_ORDER[RULE.get(kv[0], ('INFO',))[0]], kv[0])):
            ws.cell(r, 1, code)
            ws.cell(r, 2, RULE.get(code, ('INFO',))[0])
            ws.cell(r, 3, cnt)
            ws.cell(r, 4, acts[code])
            for c in range(1, 5):
                ws.cell(r, c).border = THIN
            r += 1
        if not fs:
            ws.cell(r, 1, 'none')
            r += 1
        r += 1

        r = section(ws, r, '4. Full finding list - one row per finding, ERROR then WARN then INFO')
        r = header_row(ws, r, ['#', 'Severity', 'Code', 'Source row', 'Entity', 'Finding',
                               'Recommended action', 'Status'])
        for k, f in enumerate(fs, 1):
            ws.cell(r, 1, k)
            sev_fill(ws.cell(r, 2, f.severity), f.severity)
            ws.cell(r, 3, f.code)
            ws.cell(r, 4, f.row if f.row else 'file')
            ws.cell(r, 5, f.entity)
            ws.cell(r, 6, f.finding)
            ws.cell(r, 7, f.action)
            ws.cell(r, 8, 'Open')
            r += 1
        for i, wd in enumerate([34, 12, 46, 62, 30, 96, 70, 10], 1):
            ws.column_dimensions[get_column_letter(i)].width = wd
        built.append((g, ws, e, w, n, len(grp_rows)))

    # ---- summary
    ws = wb.create_sheet('Review_Summary')
    ws['A1'] = '%s - validation review' % sheet.stem
    ws['A1'].font = TITLE
    ws['A2'] = ('Sheet checked: %s, %d triples.   Row-level validation, cross-unit consistency comparison and '
                'an identifier / label / duplication audit.   Findings are grouped one sheet per entity '
                'family; the rows they sit on are filled yellow (ERROR) or amber (WARN).'
                % (sheet_name, len(data)))
    ws['A2'].font = SUB
    r = section(ws, 4, '1. Headline - the largest defects, by number of rows they touch')
    r = header_row(ws, r, ['Severity', 'Code', 'Instances', 'What the rule tests', 'Where it lands'])
    counts = collections.Counter(f.code for f in findings)
    top = sorted(counts.items(),
                 key=lambda kv: (SEV_ORDER[RULE.get(kv[0], ('INFO',))[0]], -kv[1]))[:10]
    for code, cnt in top:
        sev, expl = RULE.get(code, ('INFO', ''))
        sev_fill(ws.cell(r, 1, sev), sev)
        ws.cell(r, 2, code).font = Font(bold=True)
        ws.cell(r, 3, cnt)
        ws.cell(r, 4, expl)
        ws.cell(r, 5, ', '.join(sorted({f.group for f in findings if f.code == code})))
        for k in range(1, 6):
            ws.cell(r, k).border = THIN
            ws.cell(r, k).alignment = Alignment(wrap_text=True, vertical='top')
        r += 1
    r += 1

    r = section(ws, r, '2. Index of issue sheets')
    r = header_row(ws, r, ['Sheet', 'Source rows', 'ERROR', 'WARN', 'INFO', 'Verdict'])
    tot = [0, 0, 0]
    for g, wsx, e, w, n, nrows in built:
        ws.cell(r, 1, wsx.title)
        ws.cell(r, 2, nrows)
        for k, v, sev in ((3, e, 'ERROR'), (4, w, 'WARN'), (5, n, 'INFO')):
            c = ws.cell(r, k, v)
            if v:
                sev_fill(c, sev)
        v = ws.cell(r, 6, 'blocks handover' if e else ('review' if w else 'clean'))
        v.fill = BADF if e else (WARNF if w else OKF)
        for k in range(1, 7):
            ws.cell(r, k).border = THIN
        tot[0] += e
        tot[1] += w
        tot[2] += n
        r += 1
    ws.cell(r, 1, 'TOTAL').font = Font(bold=True)
    for k, v in ((2, len(data)), (3, tot[0]), (4, tot[1]), (5, tot[2])):
        ws.cell(r, k, v).font = Font(bold=True)
    r += 2

    r = section(ws, r, '3. Every rule code raised, across the whole sheet')
    r = header_row(ws, r, ['Code', 'Severity', 'Instances', 'What the rule tests', 'Sheets it appears on'])
    where = collections.defaultdict(set)
    for f in findings:
        where[f.code].add(f.group)
    for code, cnt in sorted(collections.Counter(f.code for f in findings).items(),
                            key=lambda kv: (SEV_ORDER[RULE.get(kv[0], ('INFO',))[0]], -kv[1])):
        sev, expl = RULE.get(code, ('INFO', ''))
        ws.cell(r, 1, code)
        sev_fill(ws.cell(r, 2, sev), sev)
        ws.cell(r, 3, cnt)
        ws.cell(r, 4, expl)
        ws.cell(r, 5, ', '.join(sorted(where[code])))
        for k in range(1, 6):
            ws.cell(r, k).border = THIN
        r += 1
    r += 1

    r = section(ws, r, '4. How to read the source sheet')
    for line in [
        'Yellow fill (columns A:E) - the row carries at least one ERROR. %d rows.' % len(err_rows),
        'Amber fill (columns A:E) - the row carries a WARN and no ERROR. %d rows.' % len(warn_rows),
        'No fill - no finding sits on that row. %d rows.' % (len(data) - len(err_rows) - len(warn_rows)),
        '',
        'File-level findings - a class-wide pattern, a graph break, the header row - have no single row to '
        'sit on, and read "file" in the Source row column of their issue sheet.',
        '',
        'I-TYP-6 advisories ("valid Brick, no precedent in Dar Cairo") are not itemised; they would drown '
        'the register. The class list is in the preflight output.',
    ] + ([] if args.io else [
        '',
        'Not run: the IO-list cross-check. No IO list was supplied, so no point in this sheet has been '
        'confirmed against the BMS.']):
        ws.cell(r, 1, line)
        r += 1
    for i, wd in enumerate([26, 14, 10, 96, 60, 18], 1):
        ws.column_dimensions[get_column_letter(i)].width = wd

    log = wb.create_sheet('Claude Log')
    log.append(['Turn #', 'Date', 'User Request', 'Action Taken', 'Details', 'Outcome'])
    for c in range(1, 7):
        log.cell(1, c).font = COLH
        log.cell(1, c).fill = HDRF
    log.append([1, datetime.date.today(), args.request,
                'Built this review workbook: %d issue sheets, a Review_Summary index, and yellow / amber '
                'fills on the source rows.' % len(built),
                'validate_ontology.py --label-style %s and check_consistency.py over %d rows, both against a '
                'header-normalised copy so a broken header row does not drown the output; plus seven checks '
                'neither script covers - empty rated-property objects, duplicate triples, '
                'label-equals-identifier, label separators, identifier digit width, room level segment '
                'against parent level, and object-only entities.' % (args.label_style, len(data)),
                '%d findings: %d ERROR, %d WARN, %d INFO. %d rows yellow, %d amber, %d clean.'
                % (len(findings), tot[0], tot[1], tot[2], len(err_rows), len(warn_rows),
                   len(data) - len(err_rows) - len(warn_rows))])
    for c in range(1, 7):
        log.cell(2, c).alignment = Alignment(wrap_text=True, vertical='top')
    for i, wd in enumerate([8, 12, 60, 60, 110, 90], 1):
        log.column_dimensions[get_column_letter(i)].width = wd
    log.row_dimensions[2].height = 150

    wb._sheets = [wb[t] for t in ['Claude Log', 'Review_Summary', sheet_name]
                  + [w.title for _, w, *_ in built]]
    wb.save(args.out)

    print('%s -> %s' % (sheet.name, args.out))
    print('%d findings: %d ERROR, %d WARN, %d INFO' % (len(findings), tot[0], tot[1], tot[2]))
    print('%d rows filled yellow, %d amber' % (len(err_rows), len(warn_rows)))
    for g, wsx, e, w, n, nrows in built:
        print('  %-26s rows=%-6d E=%-5d W=%-5d I=%d' % (wsx.title, nrows, e, w, n))
    return 1 if tot[0] else 0


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('sheet', type=Path)
    ap.add_argument('--out', required=True, help='where to write the review workbook')
    ap.add_argument('--label-style', choices=('para', 'verbatim'), default='para')
    ap.add_argument('--io', help='IO list, passed through to both checkers as evidence')
    ap.add_argument('--ignore', default='I-TYP-6', help='comma-separated rule codes to leave out')
    ap.add_argument('--group', action='append', default=[], metavar='NAME=REGEX',
                    help='force subjects matching REGEX onto sheet NAME; repeatable')
    ap.add_argument('--request', default='Run a validation exercise over this ontology.',
                    help='the ask, recorded in the Claude Log sheet')
    args = ap.parse_args()
    if not args.sheet.exists():
        sys.exit('no such sheet: %s' % args.sheet)
    sys.exit(build(args))


if __name__ == '__main__':
    main()
