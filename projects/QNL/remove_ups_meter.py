"""Remove the building-tier para:UPS_Meter from a building's ontology.

One-shot. The client eliminated this meter from both QNL and SSC on 2026-09-09:
a UPS meter sums UPS load, neither building publishes a UPS datapoint, and a
meter with no inputs validates clean, renders a tile and returns nothing.

Removes exactly nine rows per building - the eight-row meter block plus the
orphaned owl:Class declaration - and refuses to write if the count differs.

WHY THIS IS A SCRIPT AND NOT A grep -v. Rooms are named UPS, and those rooms
carry room-tier meters of their own:

    entity:SSC_B-005_UPS_CHW-Power-Thermal-Virtual-Meter
    entity:QNL_B-084_UPS-Battery-Room_Electrical-Virtual-Meter

so matching on the string "UPS" destroys them. Matching on the class
para:UPS_Meter is not enough either: the two ref:hasExternalReference rows are
subjected on the POINT, whose class column reads brick:Electrical_Energy_Usage_
Sensor, so a class match drops six rows of eight and leaves two orphans behind.
The three exact subjects are the only safe key.

    python3 projects/QNL/remove_ups_meter.py --code SSC --dry-run
"""

import argparse
import csv
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from add_virtual_meters import BUILDINGS, read_ontology, write_ontology

CLASS = "para:UPS_Meter"
SEGMENT = "UPS-Util-Electrical-Virtual-Meter"
EXPECTED = 9


def targets(code):
    """The exact subjects this removal touches. Nothing else may match."""
    meter = f"entity:{code}_{SEGMENT}"
    return {CLASS, meter, meter + "-Consumption", meter + "-Demand"}


def strip_pending(path, code, dry_run):
    """Drop the two UPS keys from the calculation engine's checklist."""
    keys = targets(code)
    with open(path, encoding="utf-8", newline="") as fh:
        rows = list(csv.reader(fh))
    keep = [rows[0]] + [r for r in rows[1:] if r[0] not in keys]
    dropped = len(rows) - len(keep)
    print(f"pending file      {dropped} rows dropped ({path.name})")
    if dropped != 2:
        raise SystemExit(f"expected 2 pending rows, found {dropped} - aborting")
    if not dry_run:
        with open(path, "w", encoding="utf-8", newline="") as fh:
            csv.writer(fh).writerows(keep)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--code", default="QNL", choices=sorted(BUILDINGS))
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    b = BUILDINGS[args.code]
    src = b["out"]
    rows = read_ontology(src)
    header, body = rows[0], rows[1:]

    keys = targets(args.code)
    doomed = [r for r in body if r[0] in keys]
    keep = [r for r in body if r[0] not in keys]

    for r in doomed:
        print(f"  remove  {r[0]}  {r[2]}  {r[3]}")
    print(f"ontology          {len(doomed)} rows removed, {len(body)} -> {len(keep)}")
    if len(doomed) != EXPECTED:
        raise SystemExit(f"expected {EXPECTED} rows, found {len(doomed)} - aborting")

    # The removal must not have reached a room that happens to be named UPS.
    survivors = sum(1 for r in keep if "UPS" in r[0])
    print(f"                  {survivors} subjects still mention UPS (rooms, kept)")

    strip_pending(b["pending"], args.code, args.dry_run)

    if args.dry_run:
        return
    write_ontology(src, header, keep)
    print(f"wrote {src}  ({len(keep)} rows)")


if __name__ == "__main__":
    main()
