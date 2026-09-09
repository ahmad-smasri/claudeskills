"""Finish what add_thermal_layer.py started: collapse the electrical meter nodes.

Three changes, all client direction 2026-09-09.

1. COLLAPSE the 25 remaining electrical meter nodes. The thermal pass was scoped
   to thermal, which left the sheet holding two shapes: thermal points on their
   host, electrical points still behind a meter entity. After this there is one
   shape - every meter point hangs off the equipment it measures.

   Electrical points stay on their host (FCU, Motor, CHW pump) and are NOT
   pushed down to a sub-part: an FCU's electrical draw is the whole unit, not
   its coil.

2. RE-SUBJECT the 22 FCU cooling load points onto their CHW-Coil_Valve. An AHU's
   cooling load already hangs off ..._CHW-Coil_Valve while an FCU's hung off the
   FCU, though both have the identical CHW-Coil -> CHW-Coil_Valve structure -
   an artefact of where the delivered meters were attached, which the thermal
   collapse preserved faithfully rather than created. One rule now holds
   everywhere: the cooling load lives on the valve that meters it.

   Those 11 valve entities exist today only as the object of their coil's
   hasPart row - subjects of nothing. This gives them their first content.

   Point IDENTIFIERS do not change. They are already named off the unit, and
   renaming them would break the para:hasEntityId join for no gain.

3. FIX unit:KiloWHR -> unit:KiloW-HR on 12 rows: the 11 FCU ElectricalConsumption
   points plus entity:SSC_MV_Generator_Energy. KiloWHR is not a QUDT unit, so it
   resolves to nothing. The 10 unit:MegaW-HR rows in the same W-CON-19 finding
   are a separate question and are NOT touched here.

    python3 projects/SSC/finish_meter_collapse.py --dry-run
"""

import argparse
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "projects/QNL"))
from add_virtual_meters import read_ontology, write_ontology, SUBJ_SLOTS, OBJ_SLOTS

SHEET = ROOT / "reference-models/QF_SSC_Ontology_V04.xlsx"
METER = "brick:Electrical_Meter"
VALVE = "brick:Cooling_Valve"
BAD_UNIT, GOOD_UNIT = "unit:KiloWHR", "unit:KiloW-HR"


def prop_slots(r):
    for slots in (SUBJ_SLOTS, OBJ_SLOTS):
        for i in slots:
            if i + 1 < len(r) and r[i]:
                yield i


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    rows = read_ontology(SHEET)
    header, body = rows[0], rows[1:]

    # --- 1. the electrical meter nodes and their hosts -----------------------
    owner = {r[3]: (r[0], r[1]) for r in body
             if r[2] == "brick:hasPart" and r[4] == METER}
    if not owner:
        raise SystemExit("no electrical meter nodes found - already collapsed?")

    # --- 2. the FCU cooling points and the valves they move to ---------------
    #     Valves are objects of their coil's hasPart row and subjects of nothing,
    #     so they have to be found on the object side.
    valves = {r[3] for r in body if r[2] == "brick:hasPart" and r[4] == VALVE}
    move = {}
    for r in body:
        if r[2] == "brick:hasPoint" and r[1] == "brick:Fan_Coil_Unit" \
                and r[4].startswith("para:Cooling_Thermal"):
            valve = f"{r[0]}_CHW-Coil_Valve"
            if valve not in valves:
                raise SystemExit(f"{r[0]} has no {VALVE} at {valve} - aborting "
                                 "rather than inventing one")
            move[r[3]] = valve

    out, dropped, rehosted, resubjected, units = [], 0, 0, 0, 0
    for r in body:
        if r[2] == "brick:hasPart" and r[3] in owner:
            dropped += 1
            continue                                   # the meter node's own row
        r = list(r)
        if r[2] == "brick:hasPoint" and r[0] in owner:
            r[0], r[1] = owner[r[0]]                   # point moves onto the host
            rehosted += 1
        if r[2] == "brick:hasPoint" and r[3] in move:
            r[0], r[1] = move[r[3]], VALVE             # cooling point onto its valve
            resubjected += 1
        for i in prop_slots(r):
            if r[i] == "brick:hasUnit" and r[i + 1] == BAD_UNIT:
                r[i + 1] = GOOD_UNIT
                units += 1
        out.append(r)

    # --- guards --------------------------------------------------------------
    # No NEW orphan, rather than none at all. The delivered sheet already carries
    # 6: entity:SSC_AHUB000N_SA_P-Static-1/-2 on AHUB0002/3/4 are the subjects of
    # a ref:hasExternalReference row and of no brick:hasPoint row, so each AHU's
    # second remote supply-air pressure tag names a point that is never declared.
    # That is the mirror of the QNL-056 defect and is not this script's to fix -
    # but it must not grow.
    def orphaned(rowset):
        points = {r[3] for r in rowset if r[2] == "brick:hasPoint"}
        return {r[0] for r in rowset if r[2] == "ref:hasExternalReference"
                and r[4] != "ref:IFCReference"} - points

    before, after = orphaned(body), orphaned(out)
    if after - before:
        raise SystemExit(f"{len(after - before)} points would be NEWLY left with a "
                         f"reference row and no hasPoint row: "
                         f"{sorted(after - before)[:5]} - aborting")
    left = [r[4] for r in out if r[2] == "brick:hasPart" and "Meter" in r[4]]
    if left:
        raise SystemExit(f"{len(left)} meter nodes still in a hasPart chain - aborting")

    print(f"meter nodes       {dropped} collapsed, {rehosted} electrical points rehosted")
    print(f"cooling points    {resubjected} re-subjected onto their CHW-Coil_Valve")
    print(f"units             {units} {BAD_UNIT} -> {GOOD_UNIT}")
    print(f"pre-existing      {len(before)} orphan reference rows, unchanged "
          f"(delivered defect: {sorted(before)[:2]} ...)")
    print(f"ontology          {len(body)} -> {len(out)}")

    if args.dry_run:
        return
    write_ontology(SHEET, header, out)
    print(f"wrote {SHEET}  ({len(out)} rows)")


if __name__ == "__main__":
    main()
