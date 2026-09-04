#!/usr/bin/env python3
"""Prune QNL_Ontology to the client's selected datapoint list.

Selected_PARA_OS_Data_Points_v4.0.xlsx is the scope authority for points:
a point whose timeseries id is not on that list resolves to a series the
integration was never asked to deliver, so the front end draws a tile with
nothing behind it. The one deliberate exception is ContributionFraction,
which is an internal container the backend fills by calculation and so is
correctly absent from a list of BMS tags.

Removes the point's own rows and the brick:hasPoint row that declares it,
then drops any para: class declaration left with no user.
"""
import csv, sys, collections, argparse, openpyxl

SEL = 'projects/QNL/sources/Selected_PARA_OS_Data_Points_v4.0.xlsx'
ONTO = 'projects/QNL/QNL_Ontology.csv'
SUBJ = [5, 9, 13, 17, 21, 25]
OBJ = [7, 11, 15, 19, 23]
# Unlisted ids that stay in the sheet, each with the reason it is exempt.
KEEP_UNLISTED = {
    # An internal container the backend fills by calculation, so its absence
    # from a list of BMS tags is expected rather than a selection gap.
    'ContributionFraction',
    # QNL-050: a real box in the asset register, serving L1-048 Staff Office -
    # a room no other box serves. The selection omits it while selecting the
    # near-identical 039, which the client confirmed was an omission in their
    # document rather than a decision. Restored 2026-09-04.
    'QNL_VAV_1F_S15_039S.DmprPos',
    'QNL_VAV_1F_S15_039S.DuctAirFlow',
    'QNL_VAV_1F_S15_039S.EffectiveSP',
}


def selected_tags():
    ws = openpyxl.load_workbook(SEL, read_only=True)['Sheet1']
    return {str(r[0]).strip() for r in ws.iter_rows(min_row=2, values_only=True) if r[0]}


def props(row):
    for i in SUBJ + OBJ:
        if row[i].strip():
            yield row[i].strip(), row[i + 1].strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dry-run', action='store_true')
    args = ap.parse_args()

    sel = selected_tags()
    rows = list(csv.reader(open(ONTO, encoding='utf-8-sig')))
    hdr, body = rows[0], [r + [''] * (27 - len(r)) for r in rows[1:]]

    # 1. which point entities carry an unselected timeseries id
    doomed, why = set(), {}
    for r in body:
        for name, val in props(r):
            if name == 'ref:hasTimeseriesId' and val and val not in sel \
                    and val not in KEEP_UNLISTED:
                doomed.add(r[0])
                why[r[0]] = val

    # 2. drop the point's own rows and the hasPoint row that declares it
    kept = [r for r in body
            if r[0] not in doomed
            and not (r[2] == 'brick:hasPoint' and r[3] in doomed)]

    # 3. drop para: class declarations left with no user
    used = set()
    for r in kept:
        used.add(r[1])
        used.add(r[4])
        for _, val in props(r):
            used.add(val)
    orphans = {r[0] for r in kept
               if r[2] == 'rdfs:subClassOf' and r[1] == 'owl:Class'
               and r[0] not in used}
    kept = [r for r in kept if r[0] not in orphans]

    fam = collections.Counter(why[e].split('_')[1] if '_' in why[e] else '?'
                              for e in doomed)
    print('selected tags            : %d' % len(sel))
    print('points removed           : %d' % len(doomed))
    for k, c in fam.most_common():
        print('    %-12s %d' % (k, c))
    print('orphaned para: classes   : %d  %s' % (len(orphans), sorted(orphans)))
    print('rows %d -> %d  (-%d)' % (len(body), len(kept), len(body) - len(kept)))

    with open('projects/QNL/QNL_pruned_points.csv', 'w', newline='') as fh:
        w = csv.writer(fh)
        w.writerow(['point_entity', 'timeseries_id', 'reason'])
        for e in sorted(doomed):
            w.writerow([e, why[e], 'not on Selected_PARA_OS_Data_Points_v4.0'])

    if args.dry_run:
        print('dry run - nothing written to the ontology')
        return
    with open(ONTO, 'w', newline='') as fh:
        w = csv.writer(fh)
        w.writerow(hdr)
        w.writerows(kept)
    print('written:', ONTO)


main()
