"""Make the AHU duct-pressure points a 1:1 map onto the SSC IO list.

The IO list carries 14 duct static-pressure PV tags. The sheet carried 18
points, 13 of them covering a tag - so nothing was missing except one, and four
points stood for nothing.

    IO TAG                              was covered by
    SSC_AHUB0001_RtnAirDuctPrs.PV       AHUB0001_RA_P-Static
    SSC_AHUB0001_SupAirDuctPrsRmt1.PV   AHUB0001_SA_P-Static
    SSC_AHUB0002_RtnAirDuctPrs.PV       AHUB0002_RA_P-Static
    SSC_AHUB0002_SupAirDuctPrsRmt1.PV   AHUB0002_SA_P-Static-1
    SSC_AHUB0002_SupAirDuctPrsRmt2.PV   AHUB0002_SA_P-Static-2
    SSC_AHUB0003_RtnAirDuctPrs.PV       *** NOTHING ***   <- the one gap
    SSC_AHUB0003_SupAirDuctPrsRmt1.PV   AHUB0003_SA_P-Static-1
    SSC_AHUB0003_SupAirDuctPrsRmt2.PV   AHUB0003_SA_P-Static-2
    SSC_AHUB0004_RtnAirDuctPrs1.PV      AHUB0004_RA_P-Static_01
    SSC_AHUB0004_RtnAirDuctPrs2.PV      AHUB0004_RA_P-Static_02
    SSC_AHUB0004_SupAirDuctPrsRmt1.PV   AHUB0004_SA_P-Static-1
    SSC_AHUB0004_SupAirDuctPrsRmt2.PV   AHUB0004_SA_P-Static-2
    SSC_AHUB0005_RtnAirDuctPrs.PV       AHUB0005_RA_P-Static
    SSC_AHUB0005_SupAirDuctPrsRmt1.PV   AHUB0005_SA_P-Static

THE GAP IS A WRONG VALUE, NOT A MISSING POINT. AHUB0003's only return point,
entity:SSC_AHUB0003_RA_P-Static, carried SSC_AHUB0001_RtnAirDuctPrs.PV - another
AHU's sensor - so AHUB0003 displayed AHUB0001's return pressure as its own and
its real tag reached nothing. Repointing it covers the 14th tag.

THE FOUR SURPLUS POINTS carry nothing of their own and go:
  AHUB0002_SA_P-Static, AHUB0003_SA_P-Static, AHUB0004_SA_P-Static
      no reference row at all - leftovers from before the numbered pair existed
  AHUB0004_RA_P-Static
      also carried AHUB0001's tag, and AHUB0004 has NO plain RtnAirDuctPrs tag;
      its _01 and _02 already cover both of its real return sensors

TWO TRAPS, both of which validate clean afterwards:
  1. entity:SSC_AHUB0004_RA_P-Static is a PREFIX of ..._RA_P-Static_01 and _02,
     which are correct. A startswith match deletes all three.
  2. AHUB0001 and AHUB0005 have a bare _SA_P-Static too and theirs are CORRECT -
     one supply sensor each, reference row present. Removal names its targets.

    python3 projects/SSC/reconcile_duct_pressure.py --dry-run
"""

import argparse
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "projects/QNL"))
from add_virtual_meters import read_ontology, write_ontology, SUBJ_SLOTS, OBJ_SLOTS

SHEET = ROOT / "reference-models/QF_SSC_Ontology_V04.xlsx"

IO_TAGS = [
    "SSC_AHUB0001_RtnAirDuctPrs.PV",      "SSC_AHUB0001_SupAirDuctPrsRmt1.PV",
    "SSC_AHUB0002_RtnAirDuctPrs.PV",      "SSC_AHUB0002_SupAirDuctPrsRmt1.PV",
    "SSC_AHUB0002_SupAirDuctPrsRmt2.PV",  "SSC_AHUB0003_RtnAirDuctPrs.PV",
    "SSC_AHUB0003_SupAirDuctPrsRmt1.PV",  "SSC_AHUB0003_SupAirDuctPrsRmt2.PV",
    "SSC_AHUB0004_RtnAirDuctPrs1.PV",     "SSC_AHUB0004_RtnAirDuctPrs2.PV",
    "SSC_AHUB0004_SupAirDuctPrsRmt1.PV",  "SSC_AHUB0004_SupAirDuctPrsRmt2.PV",
    "SSC_AHUB0005_RtnAirDuctPrs.PV",      "SSC_AHUB0005_SupAirDuctPrsRmt1.PV",
]

REPOINT = {"entity:SSC_AHUB0003_RA_P-Static":
           ("SSC_AHUB0001_RtnAirDuctPrs.PV", "SSC_AHUB0003_RtnAirDuctPrs.PV")}
DROP = {"entity:SSC_AHUB0002_SA_P-Static",
        "entity:SSC_AHUB0003_SA_P-Static",
        "entity:SSC_AHUB0004_SA_P-Static",
        "entity:SSC_AHUB0004_RA_P-Static"}
KEEP = {"entity:SSC_AHUB0004_RA_P-Static_01", "entity:SSC_AHUB0004_RA_P-Static_02",
        "entity:SSC_AHUB0001_SA_P-Static",    "entity:SSC_AHUB0005_SA_P-Static"}


def slots(r):
    for group in (SUBJ_SLOTS, OBJ_SLOTS):
        for i in group:
            if i + 1 < len(r) and r[i]:
                yield i


def coverage(rowset):
    """IO tag -> the point that carries it."""
    out = {}
    for r in rowset:
        if r[2] == "ref:hasExternalReference":
            kv = {r[i]: r[i + 1] for i in slots(r)}
            t = kv.get("ref:hasTimeseriesId", "")
            if t in IO_TAGS:
                out[t] = r[0]
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    rows = read_ontology(SHEET)
    header, body = rows[0], rows[1:]

    before = coverage(body)
    print(f"coverage before   {len(before)} of {len(IO_TAGS)} IO tags"
          f"  (missing: {[t for t in IO_TAGS if t not in before]})")

    out, dropped, repointed = [], 0, 0
    for r in body:
        # exact equality in BOTH columns - never a prefix
        if r[0] in DROP or r[3] in DROP:
            dropped += 1
            print(f"  drop     {r[0] if r[0] in DROP else r[3]}  ({r[2]})")
            continue
        r = list(r)
        if r[0] in REPOINT:
            old, new = REPOINT[r[0]]
            for i in slots(r):
                if r[i] == "ref:hasTimeseriesId" and r[i + 1] == old:
                    r[i + 1] = new
                    repointed += 1
                    print(f"  repoint  {r[0]}  {old} -> {new}")
        out.append(r)

    after = coverage(out)
    missing = [t for t in IO_TAGS if t not in after]
    points = {r[3] for r in out if r[2] == "brick:hasPoint" and "P-Static" in r[3]}
    stray = sorted(p for p in points if p not in set(after.values()))

    print(f"\ncoverage after    {len(after)} of {len(IO_TAGS)} IO tags")
    print(f"points removed    {dropped} rows, {repointed} tag corrected")
    print(f"P-Static points   {len(points)}  (with no IO tag: {stray or 'none'})")
    print(f"ontology          {len(body)} -> {len(out)}")

    if missing:
        raise SystemExit(f"IO tags still uncovered: {missing} - aborting")
    if stray:
        raise SystemExit(f"points with no IO tag remain: {stray} - aborting")
    for e in KEEP:
        if not any(r[3] == e or r[0] == e for r in out):
            raise SystemExit(f"{e} was destroyed - it must survive - aborting")
    for tag, point in after.items():
        ahu = "_".join(point.split(":")[1].split("_")[:2])
        if not tag.startswith(ahu + "_"):
            raise SystemExit(f"{point} still names {tag} - aborting")
    print("guards ok: 14 tags, 14 points, each naming its own AHU")

    if args.dry_run:
        return
    write_ontology(SHEET, header, out)
    print(f"wrote {SHEET}  ({len(out)} rows)")


if __name__ == "__main__":
    main()
