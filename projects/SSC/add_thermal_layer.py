"""SSC's thermal layer: subclasses, the meter-node collapse, and heating points.

Four changes in one pass, because they all touch the same 36 thermal points and
splitting them would leave the sheet inconsistent between runs.

1. DECLARE the four para: thermal subclasses, copied verbatim from QNL. Brick
   has one Thermal_Power_Sensor and one Thermal_Energy_Usage_Sensor; with both
   cooling and heating in one sheet, a reader cannot tell which a point is.

2. COLLAPSE the 20 delivered thermal meter nodes. Today each is a three-level
   chain - host --hasPart--> meter --hasPoint--> load point. The middle node
   goes and the host carries the points directly. The reference rows are
   subjected on the POINTS, so they carry over untouched and every point keeps
   its series. Point identifiers are already named off the coil, not the meter,
   so nothing is renamed.

3. RETYPE those 36 points to the para: cooling subclasses. All 20 delivered
   thermal meters are cooling - 5 on AHU cooling valves, 4 on CHW pumps, 11 on
   FCUs.

4. ADD heating points on the 5 brick:Heating_Coil entities, built in the
   collapsed shape from the start so no heating meter node is ever created.
   Two points, each with its reference row.

Also corrects CWPWR_KWTH_CALC to CWPWR_KWHT_CALC on the 16 delivered rows that
carry it. The sheet held both spellings: Dar Cairo and the delivered rows write
KWTH, the space-tier layer generated here writes KWHT. Client direction is KWHT
everywhere.

Two asymmetries in the delivered data are preserved, not tidied: the 4 CHW-pump
meters carry a power point only with no energy point, and their power points sit
on live historian tags (SSC_CHW_CHWP0N.ThermLoadFan) rather than _CALC keys.

    python3 projects/SSC/add_thermal_layer.py --dry-run
"""

import argparse
import collections
import csv
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "projects/QNL"))
from add_virtual_meters import read_ontology, write_ontology, row, SUBJ_SLOTS, OBJ_SLOTS

SHEET = ROOT / "reference-models/QF_SSC_Ontology_V04.xlsx"
PENDING = ROOT / "projects/SSC/SSC_virtual_meter_timeseries_pending.csv"

SUBCLASSES = [
    ("para:Cooling_Thermal_Power_Sensor", "brick:Thermal_Power_Sensor",
     "Cooling Thermal Power Sensor"),
    ("para:Heating_Thermal_Power_Sensor", "brick:Thermal_Power_Sensor",
     "Heating Thermal Power Sensor"),
    ("para:Cooling_Thermal_Energy_Usage_Sensor", "brick:Thermal_Energy_Usage_Sensor",
     "Cooling Thermal Energy Usage Sensor"),
    ("para:Heating_Thermal_Energy_Usage_Sensor", "brick:Thermal_Energy_Usage_Sensor",
     "Heating Thermal Energy Usage Sensor"),
]

COOLING = {
    "brick:Thermal_Power_Sensor": "para:Cooling_Thermal_Power_Sensor",
    "brick:Thermal_Energy_Usage_Sensor": "para:Cooling_Thermal_Energy_Usage_Sensor",
}

# Dar Cairo has no heating token at all - no HEATPWR, no HWPWR. These mirror the
# client's own Air Terminal tags (AT_HEATPWR_KWT_CALC / AT_HEATPWR_KWHT_CALC)
# minus the AT_ prefix, and keep heating distinct from the hot water removed on
# the same day. Derived, not confirmed against a register: both go in the
# pending file for the calculation engine.
HEATING_POINTS = [
    ("Heating-Load-Consumption", "Heating Load Consumption",
     "para:Heating_Thermal_Energy_Usage_Sensor", "para:KiloWt-HR", "HEATPWR_KWHT_CALC"),
    ("Heating-Load-Demand", "Heating Load Demand",
     "para:Heating_Thermal_Power_Sensor", "para:KiloWt", "HEATPWR_KWT_CALC"),
]

KWTH, KWHT = "CWPWR_KWTH_CALC", "CWPWR_KWHT_CALC"


def props(r):
    """(slot, name, value) for every property pair carrying a name."""
    for slots in (SUBJ_SLOTS, OBJ_SLOTS):
        for i in slots:
            if i + 1 < len(r) and r[i]:
                yield i, r[i], r[i + 1]


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    rows = read_ontology(SHEET)
    header, body = rows[0], rows[1:]
    etype = {}
    for r in body:
        etype.setdefault(r[0], r[1])
    declared = {r[0] for r in body if r[1] == "owl:Class"}

    # --- 2/3. collapse the thermal meter nodes and retype their points --------
    #     host -> meter, from the hasPart rows we are about to drop
    owner = {r[3]: (r[0], r[1]) for r in body
             if r[2] == "brick:hasPart" and r[4] == "brick:Thermal_Power_Meter"}
    if not owner:
        raise SystemExit("no thermal meter nodes found - already collapsed?")

    # The 36 points those meters own, and ONLY those. Scoping the retype to this
    # set matters: the 342 space-tier CHW meter points carry the same two Brick
    # classes and are also cooling, but they are a different family with its own
    # class (para:CHW_Meter) already saying so. Retyping by class alone caught
    # them and rewrote their reference rows while leaving their hasPoint rows
    # untouched - half-typed, which is worse than either end state.
    delivered_points = {r[3] for r in body
                        if r[2] == "brick:hasPoint" and r[0] in owner}

    out, dropped, rehosted, retyped = [], 0, 0, 0
    for r in body:
        if r[2] == "brick:hasPart" and r[3] in owner:
            dropped += 1
            continue                                  # the meter node's own row
        r = list(r)
        if r[2] == "brick:hasPoint" and r[0] in owner:
            host, host_type = owner[r[0]]
            r[0], r[1] = host, host_type              # point moves onto the host
            rehosted += 1
        if r[2] == "brick:hasPoint" and r[3] in delivered_points and r[4] in COOLING:
            r[4] = COOLING[r[4]]
            retyped += 1
        elif r[0] in delivered_points and r[1] in COOLING:
            r[1] = COOLING[r[1]]
            retyped += 1
        for i, name, value in list(props(r)):
            if name == "ref:hasTimeseriesId" and value == KWTH:
                r[i + 1] = KWHT
        out.append(r)

    # --- 1. the four subclasses ---------------------------------------------
    decls = [row(cls, "owl:Class", "rdfs:subClassOf", parent,
                 sprops=[("rdfs:label_en", label)])
             for cls, parent, label in SUBCLASSES if cls not in declared]

    # --- 4. heating points on the coils --------------------------------------
    coils = sorted(u for u, t in etype.items() if t == "brick:Heating_Coil")
    heating, pending = [], []
    for coil in coils:
        ahu = coil.rsplit("_", 1)[0]                  # entity:SSC_AHUB0001_Heater
        eid = ahu.split(":", 1)[1]
        for seg, label, cls, unit, tsid in HEATING_POINTS:
            point = f"{coil}_{seg}"
            heating.append(row(coil, "brick:Heating_Coil", "brick:hasPoint", point, cls,
                               oprops=[("rdfs:label_en", label),
                                       ("brick:hasUnit", unit)]))
            heating.append(row(point, cls, "ref:hasExternalReference",
                               "<blanknode>", "ref:TimeseriesReference",
                               oprops=[("ref:hasTimeseriesId", tsid),
                                       ("para:hasEntityId", eid)]))
            pending.append([point, cls, tsid, eid, coil])

    tok = collections.Counter()
    for r in out:
        for _, name, value in props(r):
            if name == "ref:hasTimeseriesId" and "KW" in value:
                tok[value] += 1

    print(f"subclasses        {len(decls)} declared")
    print(f"meter nodes       {dropped} collapsed, {rehosted} points rehosted onto their coil/unit")
    print(f"retyped           {retyped} cells to the para: cooling subclasses")
    print(f"heating           {len(coils)} coils, {len(heating)//2} points, {len(heating)} rows")
    print(f"tokens            KWTH left {tok[KWTH]}, KWHT now {tok[KWHT]}")
    print(f"ontology          {len(body)} -> {len(out) + len(decls) + len(heating)}")

    if args.dry_run:
        return

    body_out = out + decls + heating
    body_out.sort(key=lambda r: 0 if r[1] in ("owl:Class", "qudt:Unit") else 1)
    write_ontology(SHEET, header, body_out)
    print(f"wrote {SHEET}  ({len(body_out)} rows)")

    with open(PENDING, "a", encoding="utf-8", newline="") as fh:
        csv.writer(fh).writerows(pending)
    print(f"appended {len(pending)} derived heating keys to {PENDING.name}")


if __name__ == "__main__":
    main()
