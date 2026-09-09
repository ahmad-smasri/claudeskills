"""Remove an eliminated virtual meter class from a building's ontology.

One-shot per class. The REMOVALS table below is the record of what was taken
out and why, and it has to live here rather than be looked up from METER_TYPES:
the whole point of an elimination is that the class LEAVES that table.

Removes the class declaration plus every meter of that class and its points,
and refuses to write unless what it found is a whole number of eight-row meter
blocks plus at most one declaration.

WHY THIS IS A SCRIPT AND NOT A grep -v. Two traps, both of which validate clean
after the damage:

  1. Rooms are named after the thing being removed, and those rooms carry
     room-tier meters of their own:
         entity:SSC_B-005_UPS_CHW-Power-Thermal-Virtual-Meter
         entity:QNL_B-084_UPS-Battery-Room_Electrical-Virtual-Meter
  2. One segment CONTAINS another. "CHW-Power-Thermal-Virtual-Meter" contains
     the substring "HW-Power", so removing HW by substring deletes all 360 CHW
     meters - 2,880 rows.

Matching on the class alone is not enough either: the two
ref:hasExternalReference rows are subjected on the POINT, whose class column
reads brick:Electrical_Energy_Usage_Sensor or brick:Thermal_Power_Sensor, so a
class match drops six rows of eight and leaves two orphans behind.

The exact subjects - the class, the meter, and its two points - are the only
safe key.

    python3 projects/QNL/remove_meter_class.py --class para:HW_Meter --code SSC --dry-run
"""

import argparse
import csv
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from add_virtual_meters import BUILDINGS, read_ontology, write_ontology

# class -> (Dar Cairo name segment, why it went)
REMOVALS = {
    "para:UPS_Meter": (
        "UPS-Util-Electrical-Virtual-Meter",
        "a UPS meter sums UPS load and neither building publishes a UPS "
        "datapoint. Client direction 2026-09-09."),
    "para:HW_Meter": (
        "HW-Power-Thermal-Virtual-Meter",
        "domestic hot water. SSC's heating is electric with 0 hot-water tags in "
        "5,751 IO rows; QNL's only DHW asset is a calorifier carrying two alarms "
        "and a temperature - no power, no energy, no flow - and it sits outside "
        "the selected-datapoint scope. Client direction 2026-09-09."),
}

BLOCK = 8   # rows per meter: 4 structural + 2 hasPoint + 2 reference


def doomed_subject(code, cls, subject):
    """True for the class declaration and for every meter of that class and its
    two points, at ANY tier - building, floor or room.

    The suffix is anchored on the separator, "_" + the full segment, and that is
    what makes it safe. A bare substring test would match
    entity:QNL_L1_CHW-Power-Thermal-Virtual-Meter when removing HW, because
    "CHW-Power..." contains "HW-Power...". Anchored, it does not: the character
    before HW there is "C", not "_".
    """
    if subject == cls:
        return True
    if not subject.startswith(f"entity:{code}_"):
        return False
    tail = "_" + REMOVALS[cls][0]
    return subject.endswith(tail) or subject.endswith(tail + "-Consumption") \
        or subject.endswith(tail + "-Demand")


def strip_pending(path, code, cls, dry_run):
    """Drop this class's keys from the calculation engine's checklist."""
    with open(path, encoding="utf-8", newline="") as fh:
        rows = list(csv.reader(fh))
    keep = [rows[0]] + [r for r in rows[1:] if not doomed_subject(code, cls, r[0])]
    dropped = len(rows) - len(keep)
    print(f"pending file      {dropped} rows dropped ({path.name})")
    if not dry_run and dropped:
        with open(path, "w", encoding="utf-8", newline="") as fh:
            csv.writer(fh).writerows(keep)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--class", dest="cls", required=True, choices=sorted(REMOVALS))
    ap.add_argument("--code", default="QNL", choices=sorted(BUILDINGS))
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    b = BUILDINGS[args.code]
    src = b["out"]
    rows = read_ontology(src)
    header, body = rows[0], rows[1:]

    doomed = [r for r in body if doomed_subject(args.code, args.cls, r[0])]
    keep = [r for r in body if not doomed_subject(args.code, args.cls, r[0])]

    for r in doomed:
        print(f"  remove  {r[0]}  {r[2]}  {r[3]}")

    decls = sum(1 for r in doomed if r[0] == args.cls)
    meters = len(doomed) - decls
    print(f"ontology          {len(doomed)} rows removed "
          f"({meters // BLOCK} meters + {decls} declaration), "
          f"{len(body)} -> {len(keep)}")
    if decls > 1 or meters % BLOCK:
        raise SystemExit(f"expected whole {BLOCK}-row meter blocks plus at most one "
                         f"declaration, found {meters} meter rows and {decls} "
                         "declarations - aborting")

    # The removal must not have reached anything that merely shares a substring.
    stem = REMOVALS[args.cls][0].split("-")[0]
    survivors = sum(1 for r in keep if stem in r[0])
    print(f"                  {survivors} subjects still mention '{stem}' (kept)")

    strip_pending(b["pending"], args.code, args.cls, args.dry_run)

    if args.dry_run:
        return
    write_ontology(src, header, keep)
    print(f"wrote {src}  ({len(keep)} rows)")


if __name__ == "__main__":
    main()
