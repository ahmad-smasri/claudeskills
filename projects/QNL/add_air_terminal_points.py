#!/usr/bin/env python3
"""Add the six calculated Air Terminal contribution points to every VAV and CAV.

The backend apportions a building's cooling, heating and electrical load down to
the terminals that caused it. These six points are the containers it writes into
- calculated, not published by the BMS, so they carry a fixed timeseries id per
point and the terminal's own entity id, exactly as para:contributionFraction
already does.

The cooling pair is thermal, not electrical. The client's spec typed
AT_CWPWR_KWT_CALC as brick:Electric_Power_Sensor and AT_CWPWR_KWHT_CALC as
brick:Electrical_Energy_Usage_Sensor while giving both a thermal unit; the tag
names themselves say chilled water and thermal kW, and the heating pair beside
them uses the thermal classes. Left as specified, a rollup filtering on class
would have summed every terminal's chilled-water demand into the building's
electrical demand and been wrong with nothing to flag it. Corrected on client
direction 2026-09-07 to match the heating pair.
"""
import csv, argparse

ONTO = 'projects/QNL/QNL_Ontology.csv'
WIDTH = 27
TERMINALS = ('brick:Variable_Air_Volume_Box', 'brick:Constant_Air_Volume_Box')

# (id segment, label, class, unit, timeseries id)
POINTS = [
    ('Cooling-Power-Demand-Contribution', 'Cooling Power Demand Contribution',
     'brick:Thermal_Power_Sensor', 'para:KiloWt', 'AT_CWPWR_KWT_CALC'),
    ('Cooling-Energy-Consumption-Contribution',
     'Cooling Energy Consumption Contribution',
     'brick:Thermal_Energy_Usage_Sensor', 'para:KiloWt-HR', 'AT_CWPWR_KWHT_CALC'),
    ('Heating-Power-Demand-Contribution', 'Heating Power Demand Contribution',
     'brick:Thermal_Power_Sensor', 'para:KiloWt', 'AT_HEATPWR_KWT_CALC'),
    ('Heating-Energy-Consumption-Contribution',
     'Heating Energy Consumption Contribution',
     'brick:Thermal_Energy_Usage_Sensor', 'para:KiloWt-HR', 'AT_HEATPWR_KWHT_CALC'),
    ('Electrical-Power-Demand-Contribution',
     'Electrical Power Demand Contribution',
     'brick:Electric_Power_Sensor', 'unit:KiloW', 'AT_ELEC_KW_CALC'),
    ('Electrical-Energy-Consumption-Contribution',
     'Electrical Energy Consumption Contribution',
     'brick:Electrical_Energy_Usage_Sensor', 'unit:KiloW-HR', 'AT_ELEC_KWH_CALC'),
]


def row(subject, stype, predicate, obj, otype, oprops):
    r = [subject, stype, predicate, obj, otype] + [''] * (WIDTH - 5)
    for i, (name, value) in zip([7, 11, 15, 19, 23], oprops):
        r[i], r[i + 1] = name, value
    return r


def entity_id(entity):
    """the id the timeseries database uses - underscores throughout

    Taken the same way para:contributionFraction takes it, so the two agree:
    entity:QNL_VAV-1F-S11-001 -> QNL_VAV_1F_S11_001
    """
    return entity.split(':', 1)[-1].replace('-', '_')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dry-run', action='store_true')
    args = ap.parse_args()

    rows = list(csv.reader(open(ONTO, encoding='utf-8-sig')))
    hdr, body = rows[0], [r + [''] * (WIDTH - len(r)) for r in rows[1:]]

    terminals, klass = [], {}
    for r in body:
        if r[1] in TERMINALS and r[0] not in klass:
            klass[r[0]] = r[1]
            terminals.append(r[0])
    have = {(r[0], r[3]) for r in body if r[2] == 'brick:hasPoint'}

    # the existing contributionFraction row is the anchor: the new six sit with
    # it, so a terminal's calculated points read as one block
    new = {}
    for ent in terminals:
        block = []
        for seg, label, cls, unit, ts in POINTS:
            point = '%s_%s' % (ent, seg)
            if (ent, point) in have:
                continue
            block.append(row(ent, klass[ent], 'brick:hasPoint', point, cls,
                             [('rdfs:label_en', label), ('brick:hasUnit', unit)]))
            block.append(row(point, cls, 'ref:hasExternalReference',
                             '<blanknode>', 'ref:TimeseriesReference',
                             [('ref:hasTimeseriesId', ts),
                              ('para:hasEntityId', entity_id(ent))]))
        if block:
            new[ent] = block

    out = []
    for r in body:
        out.append(r)
        if r[2] == 'brick:hasPoint' and r[4] == 'para:contributionFraction' \
                and r[0] in new:
            out.extend(new.pop(r[0]))
    # a terminal with no contributionFraction row gets its block after its last row
    for ent, block in list(new.items()):
        last = max(i for i, r in enumerate(out) if r[0] == ent)
        out[last + 1:last + 1] = block
        del new[ent]

    n = sum(len(b) for b in ()) or (len(out) - len(body))
    print('terminals            : %d VAV, %d CAV'
          % (sum(1 for e in terminals if klass[e] == TERMINALS[0]),
             sum(1 for e in terminals if klass[e] == TERMINALS[1])))
    print('points added         : %d' % (n // 2))
    print('rows %d -> %d  (+%d)' % (len(body), len(out), n))
    if args.dry_run:
        print('dry run - nothing written')
        return
    with open(ONTO, 'w', newline='') as fh:
        w = csv.writer(fh); w.writerow(hdr); w.writerows(out)
    print('written:', ONTO)


main()
