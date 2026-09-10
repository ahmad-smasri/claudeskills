"""Declare the SA_P-Static-1 / -2 points on AHUB0002, 0003 and 0004.

SSC-019: those three AHUs each publish two remote supply-air duct pressure
sensors and the sheet declared neither. Each carries a ref:hasExternalReference
row subjected on entity:SSC_AHUB000N_SA_P-Static-1 and -2, with a real historian
tag - and no brick:hasPoint row anywhere declares those points, so the tag is
attached to nothing the graph can show. The mirror of QNL-056.

The IO list settles which AHUs have two and which have one:

    AHUB0001  SupAirDuctPrsRmt1                      one sensor  - correct today
    AHUB0002  SupAirDuctPrsRmt1 + SupAirDuctPrsRmt2  two         - fixed here
    AHUB0003  SupAirDuctPrsRmt1 + SupAirDuctPrsRmt2  two         - fixed here
    AHUB0004  SupAirDuctPrsRmt1 + SupAirDuctPrsRmt2  two         - fixed here
    AHUB0005  SupAirDuctPrsRmt1                      one sensor  - correct today

CLASS CHOICE. The point takes the class its own reference row already names -
para:Static_Pressure_Sensor_01 / _02 - because the hasPoint row's objectType and
the reference row's subjectType are the same point's class, and disagreeing
would give it two. Both are declared in the sheet already, both come from
Dar Cairo.

Note for the client, not acted on here: SSC also declares
para:Static_Pressure_Sensor_Remote_01 / _Remote_02, labelled "Static Pressure
Remote Sensor 01 / 02", and NOTHING uses them. Those look like what these remote
points were meant to carry - the point labels read "Supply Air Duct REMOTE
Pressure" - but switching to them means editing the subjectType on six delivered
reference rows, which is a client call, not one to slip in here.

    python3 projects/SSC/add_missing_static_pressure_points.py --dry-run
"""

import argparse
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "projects/QNL"))
from add_virtual_meters import read_ontology, write_ontology, row

SHEET = ROOT / "reference-models/QF_SSC_Ontology_V04.xlsx"
AHUS = ("entity:SSC_AHUB0002", "entity:SSC_AHUB0003", "entity:SSC_AHUB0004")
POINTS = [
    ("SA_P-Static-1", "para:Static_Pressure_Sensor_01",
     "Supply Air Duct Remote Pressure 01"),
    ("SA_P-Static-2", "para:Static_Pressure_Sensor_02",
     "Supply Air Duct Remote Pressure 02"),
]


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    rows = read_ontology(SHEET)
    header, body = rows[0], rows[1:]
    declared_points = {r[3] for r in body if r[2] == "brick:hasPoint"}
    declared_classes = {r[0] for r in body if r[1] == "owl:Class"}
    refs = {r[0]: r[1] for r in body if r[2] == "ref:hasExternalReference"}

    out = []
    for ahu in AHUS:
        for seg, cls, label in POINTS:
            point = f"{ahu}_{seg}"
            # Only declare what a reference row is already waiting for, and only
            # with the class that row names - anything else invents a point or
            # gives an existing one a second class.
            if point not in refs:
                raise SystemExit(f"{point} has no reference row - refusing to "
                                 "invent a point nothing is waiting for")
            if refs[point] != cls:
                raise SystemExit(f"{point}'s reference row says {refs[point]}, "
                                 f"not {cls} - aborting rather than creating a "
                                 "point with two classes")
            if point in declared_points:
                raise SystemExit(f"{point} is already declared - nothing to add")
            if cls not in declared_classes:
                raise SystemExit(f"{cls} is not declared in the sheet - aborting")
            out.append(row(ahu, "brick:Air_Handling_Unit", "brick:hasPoint",
                           point, cls,
                           oprops=[("rdfs:label_en", label),
                                   ("brick:hasUnit", "unit:PA")]))
            print(f"  declare  {point}  [{cls}]  {label}")

    # the whole point of the exercise: no reference row left without a point
    points = declared_points | {r[3] for r in out}
    orphans = {r[0] for r in body if r[2] == "ref:hasExternalReference"
               and r[4] != "ref:IFCReference"} - points
    print(f"\npoints            {len(out)} declared, {len(out)} rows")
    print(f"orphan refs       {len(orphans)} left" + (f": {sorted(orphans)}" if orphans else ""))
    print(f"ontology          {len(body)} -> {len(body) + len(out)}")

    if args.dry_run:
        return
    write_ontology(SHEET, header, body + out)
    print(f"wrote {SHEET}  ({len(body) + len(out)} rows)")


if __name__ == "__main__":
    main()
