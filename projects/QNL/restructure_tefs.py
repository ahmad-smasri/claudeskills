#!/usr/bin/env python3
"""Model the twin-fan TEFs as one unit with two fan PARTS, and restore all
131 historian TEF points.

Two changes, both TEF-only:

1. The six twin fans were typed brick:Exhaust_Fan, the same class as the unit
   they are part of, which reads as an exhaust fan containing two exhaust fans -
   two more units, not two components. They are parts of one casing sharing one
   duct and one location, so they take brick:Fan. The ladder:
   Dar Cairo has no brick:Fan (its fan parts are an AHU's supply and exhaust
   fans, a different concept); Brick 1.4 has brick:Fan as a preferred term; and
   QF HQ already uses exactly this shape - entity:HQ_CCU_B0001 brick:CRAC
   brick:hasPart entity:HQ_CCU_B0001_Fan brick:Fan, with the part carrying its
   own points. TEF-101C and TEF-102C are single standalone fans and stay
   brick:Exhaust_Fan units.

2. All 131 historian TEF points go back. This overrides the selected-datapoint
   list for the TEF family only, on client direction: the selected list carries
   45 TEF tags, and the changeover, duty-priority and runtime points it omits
   are the evidence a duty/standby pair is actually rotating. Every other family
   still matches the selection exactly.
"""
import csv, subprocess, collections, argparse

ONTO = 'projects/QNL/QNL_Ontology.csv'
PRE_PRUNE = 'c097428'
TWIN_FANS = {'entity:QNL_TEF-B01A', 'entity:QNL_TEF-B01B',
             'entity:QNL_TEF-B02A', 'entity:QNL_TEF-B02B',
             'entity:QNL_TEF-B03A', 'entity:QNL_TEF-B03B'}
CLASS_ROWS = ('para:Duty_Priority', 'para:Remote_Status',
              'para:Start_Count', 'para:Trip_Count')


def prev_lines():
    out = subprocess.run(['git', 'show', '%s:%s' % (PRE_PRUNE, ONTO)],
                         capture_output=True, text=True, check=True).stdout
    return out.splitlines()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dry-run', action='store_true')
    args = ap.parse_args()

    cur = open(ONTO, encoding='utf-8').read().splitlines()
    have = set(cur)
    prev = prev_lines()

    # --- 1. restore every TEF row the pruning dropped, in its original order
    restored = [l for l in prev
                if l not in have
                and (l.split(',', 1)[0].startswith('entity:QNL_TEF')
                     or l.split(',', 1)[0] in CLASS_ROWS)]

    # class declarations go back at the top, beside their siblings
    cls = [l for l in restored if l.split(',', 1)[0] in CLASS_ROWS]
    pts = [l for l in restored if l not in cls]

    out, seen_cls = [], False
    for line in cur:
        if not seen_cls and line.startswith('para:Chilled_Water_Loop_Network,'):
            out.extend(cls)
            seen_cls = True
        out.append(line)
    assert seen_cls, 'class-declaration anchor not found'

    # each point row goes back beside the entity it belongs to
    by_owner = collections.defaultdict(list)
    for l in pts:
        f = l.split(',')
        owner = f[0] if f[2] != 'brick:hasPoint' else f[0]
        by_owner[owner].append(l)

    merged = []
    for line in out:
        merged.append(line)
        subj = line.split(',', 1)[0]
        nxt = merged.index if False else None
    # simpler: append each owner's restored rows after that owner's last row
    merged = list(out)
    for owner, rows in by_owner.items():
        last = max((i for i, l in enumerate(merged)
                    if l.split(',', 1)[0] == owner), default=None)
        if last is None:                       # the point's own rows
            anchor = owner.rsplit('_', 1)[0]   # its parent equipment
            last = max(i for i, l in enumerate(merged)
                       if l.split(',', 1)[0] == anchor)
        merged[last + 1:last + 1] = rows

    # --- 2. retype the six twin fans as parts
    retyped = 0
    for i, line in enumerate(merged):
        f = line.split(',')
        changed = False
        if f[0] in TWIN_FANS and f[1] == 'brick:Exhaust_Fan':
            f[1] = 'brick:Fan'
            changed = True
        if f[2] == 'brick:hasPart' and f[3] in TWIN_FANS and f[4] == 'brick:Exhaust_Fan':
            f[4] = 'brick:Fan'
            changed = True
        if changed:
            merged[i] = ','.join(f)
            retyped += 1

    print('TEF rows restored     : %d  (%d point rows, %d class declarations)'
          % (len(restored), len(pts), len(cls)))
    print('rows retyped to Fan   : %d' % retyped)
    print('rows %d -> %d  (+%d)' % (len(cur) - 1, len(merged) - 1,
                                    len(merged) - len(cur)))
    if args.dry_run:
        print('dry run - nothing written')
        return
    open(ONTO, 'w', encoding='utf-8').write('\n'.join(merged) + '\n')
    print('written:', ONTO)


main()
