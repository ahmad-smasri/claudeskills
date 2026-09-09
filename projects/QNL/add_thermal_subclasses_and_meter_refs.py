#!/usr/bin/env python3
"""Two migrations on the QNL sheet, both one-shot.

1. Four para: subclasses so cooling and heating stop sharing a class.
   Brick gives both the same two - brick:Thermal_Power_Sensor and
   brick:Thermal_Energy_Usage_Sensor - so on the air terminals the distinction
   survives only in the entity name and the timeseries id, where no query can
   reach it. PROJECT OVERRIDE FOR QNL ONLY, on client direction 2026-09-09, and
   deliberately not a house rule: the reference models all use the plain Brick
   classes and the skill is left saying so. Scope is the 299 VAV/CAV air
   terminals; the CHW/HW virtual meters and the CHWS main-loop meter keep the
   Brick classes.

2. The ref:hasExternalReference row every virtual meter point was missing.
   2,920 points existed carrying no reference at all - they were not the subject
   of any row - because the skill documented the meter block as six rows and
   parked the keys in a pending file. Dar Cairo writes the row: see
   entity:Dar-Cairo_UPS-Util-Electrical-Virtual-Meter-Consumption, which carries
   ref:hasTimeseriesId UPS_KWH_CALC and para:hasEntityId "Smart Village". Both
   halves are derivable - the tsid from Dar Cairo's token per meter class, the
   entityId from the space the meter meters.
"""
import csv, argparse, collections, sys, os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from add_air_terminal_points import entity_id          # one derivation, not two

ONTO = 'projects/QNL/QNL_Ontology.csv'
PENDING = 'projects/QNL/QNL_virtual_meter_timeseries_pending.csv'
WIDTH = 27
OBJ_SLOTS = [7, 11, 15, 19, 23]

# air-terminal point suffix -> the class that replaces the Brick one
RETYPE = {
    'Air-Terminal-Cooling-Power-Demand-Contribution':
        ('brick:Thermal_Power_Sensor', 'para:Cooling_Thermal_Power_Sensor'),
    'Air-Terminal-Heating-Power-Demand-Contribution':
        ('brick:Thermal_Power_Sensor', 'para:Heating_Thermal_Power_Sensor'),
    'Air-Terminal-Cooling-Energy-Consumption-Contribution':
        ('brick:Thermal_Energy_Usage_Sensor', 'para:Cooling_Thermal_Energy_Usage_Sensor'),
    'Air-Terminal-Heating-Energy-Consumption-Contribution':
        ('brick:Thermal_Energy_Usage_Sensor', 'para:Heating_Thermal_Energy_Usage_Sensor'),
}
DECLARE = [
    ('para:Cooling_Thermal_Power_Sensor', 'brick:Thermal_Power_Sensor',
     'Cooling Thermal Power Sensor'),
    ('para:Heating_Thermal_Power_Sensor', 'brick:Thermal_Power_Sensor',
     'Heating Thermal Power Sensor'),
    ('para:Cooling_Thermal_Energy_Usage_Sensor', 'brick:Thermal_Energy_Usage_Sensor',
     'Cooling Thermal Energy Usage Sensor'),
    ('para:Heating_Thermal_Energy_Usage_Sensor', 'brick:Thermal_Energy_Usage_Sensor',
     'Heating Thermal Energy Usage Sensor'),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dry-run', action='store_true')
    args = ap.parse_args()

    rows = list(csv.reader(open(ONTO, encoding='utf-8-sig')))
    hdr, body = rows[0], [r + [''] * (WIDTH - len(r)) for r in rows[1:]]

    # --- 1a. retype the air terminal points, both sides
    retyped = collections.Counter()
    for r in body:
        for col in (0, 3):
            seg = r[col].rsplit('_', 1)[-1]
            if seg in RETYPE:
                old, new = RETYPE[seg]
                tcol = 1 if col == 0 else 4
                if r[tcol] == old:
                    r[tcol] = new
                    retyped[new] += 1

    # --- 1b. declare the four, beside the existing owl:Class block
    last_cls = max(i for i, r in enumerate(body)
                   if r[1] == 'owl:Class' and r[2] == 'rdfs:subClassOf')
    decl = []
    have = {r[0] for r in body if r[1] == 'owl:Class'}
    for name, parent, label in DECLARE:
        if name in have:
            continue
        d = [name, 'owl:Class', 'rdfs:subClassOf', parent, ''] + [''] * (WIDTH - 5)
        d[5], d[6] = 'rdfs:label_en', label          # subject slot, as its siblings
        decl.append(d)
    body[last_cls + 1:last_cls + 1] = decl

    # --- 2. the missing reference row on every virtual meter point
    tsid = {}
    for r in csv.DictReader(open(PENDING, encoding='utf-8-sig')):
        tsid[r['point']] = (r['proposed_hasTimeseriesId'], r['meters'])

    have_ref = {r[0] for r in body if r[2] == 'ref:hasExternalReference'}
    out, added, missing = [], 0, []
    for r in body:
        out.append(r)
        if r[2] != 'brick:hasPoint' or '-Virtual-Meter-' not in r[3]:
            continue
        point = r[3]
        if point in have_ref:
            continue
        if point not in tsid:
            missing.append(point)
            continue
        key, target = tsid[point]
        ref = [point, r[4], 'ref:hasExternalReference', '<blanknode>',
               'ref:TimeseriesReference'] + [''] * (WIDTH - 5)
        for i, (n, v) in zip(OBJ_SLOTS, [('ref:hasTimeseriesId', key),
                                         ('para:hasEntityId', entity_id(target))]):
            ref[i], ref[i + 1] = n, v
        out.append(ref)
        added += 1

    print('air-terminal points retyped:')
    for k, n in sorted(retyped.items()):
        print('    %-45s %d cells' % (k, n))
    print('class declarations added   : %d' % len(decl))
    print('meter reference rows added : %d' % added)
    if missing:
        print('NO KEY, left alone         : %d  %s' % (len(missing), missing[:3]))
    print('rows %d -> %d  (+%d)' % (len(body), len(out), len(out) - len(body)))

    if args.dry_run:
        print('dry run - nothing written')
        return
    with open(ONTO, 'w', newline='') as fh:
        w = csv.writer(fh); w.writerow(hdr); w.writerows(out)
    print('written:', ONTO)


main()
