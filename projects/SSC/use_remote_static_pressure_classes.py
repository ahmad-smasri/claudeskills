"""Switch AHUB0002/3/4's supply duct pressure points to the Remote classes.

SSC coined para:Static_Pressure_Sensor_Remote_01 / _Remote_02 - labelled
"Static Pressure Remote Sensor 01 / 02" - specifically for the second supply
air duct pressure sensor those three AHUs carry, and then nothing ever used
them: the six points were typed para:Static_Pressure_Sensor_01 / _02 instead,
which are Dar Cairo's non-remote classes.

The points ARE remote sensors - the IO tag is SupAirDuctPrsRmt1/2 and the label
reads "Supply Air Duct REMOTE Pressure" - so the Remote classes are the correct
ones and the coined pair gets the purpose it was created for.

Both old classes are declared in this sheet and used by nothing else once the
six points move, so their declarations go with them. That does not remove them
from anywhere else: they are Dar Cairo classes (para-classes.csv, sourced from
DarCairo_V98.csv) and stay available to any other building.

BOTH CELLS PER POINT, or the point ends up with two classes. The class appears
as the objectType of the brick:hasPoint row and as the subjectType of the
ref:hasExternalReference row - 6 points, 12 cells.

    python3 projects/SSC/use_remote_static_pressure_classes.py --dry-run
"""

import argparse
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "projects/QNL"))
from add_virtual_meters import read_ontology, write_ontology

SHEET = ROOT / "reference-models/QF_SSC_Ontology_V04.xlsx"
SWAP = {
    "para:Static_Pressure_Sensor_01": "para:Static_Pressure_Sensor_Remote_01",
    "para:Static_Pressure_Sensor_02": "para:Static_Pressure_Sensor_Remote_02",
}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    rows = read_ontology(SHEET)
    header, body = rows[0], rows[1:]

    declared = {r[0] for r in body if r[1] == "owl:Class"}
    for new in SWAP.values():
        if new not in declared:
            raise SystemExit(f"{new} is not declared in the sheet - aborting "
                             "rather than pointing rows at an undeclared class")

    out, swapped, dropped = [], 0, 0
    for r in body:
        # the old class's own declaration row goes
        if r[0] in SWAP and r[1] == "owl:Class":
            dropped += 1
            print(f"  drop declaration  {r[0]}")
            continue
        r = list(r)
        for i, v in enumerate(r):
            if v in SWAP:
                r[i] = SWAP[v]
                swapped += 1
        out.append(r)

    # guards
    left = [v for r in out for v in r if v in SWAP]
    if left:
        raise SystemExit(f"{len(left)} cells still name an old class - aborting")
    for r in out:
        if r[2] == "brick:hasPoint" and r[4] in SWAP.values():
            ref = [q for q in out if q[0] == r[3] and q[2] == "ref:hasExternalReference"]
            if len(ref) != 1 or ref[0][1] != r[4]:
                raise SystemExit(f"{r[3]}: hasPoint says {r[4]} but its reference "
                                 f"row says {ref[0][1] if ref else 'NOTHING'} - aborting")
    used = {r[4] for r in out if r[2] == "brick:hasPoint"} | \
           {r[1] for r in out if r[2] == "ref:hasExternalReference"}
    for new in SWAP.values():
        if new not in used:
            raise SystemExit(f"{new} is still used by nothing - aborting")

    print(f"\ncells swapped     {swapped}  (2 per point, both sides agree)")
    print(f"declarations      {dropped} removed")
    print(f"ontology          {len(body)} -> {len(out)}")

    if args.dry_run:
        return
    write_ontology(SHEET, header, out)
    print(f"wrote {SHEET}  ({len(out)} rows)")


if __name__ == "__main__":
    main()
