"""Add the six calculated Air Terminal contribution points to SSC's VAVs.

The same six containers QNL carries, on the same classes, tokens and units, so
one front-end template serves both buildings. The POINTS table and the entity-id
derivation are imported from the QNL script rather than copied, because a second
copy is a second thing to keep in step.

SSC needs none of QNL's exceptions: all 108 terminals are VAVs (there is no CAV),
every one carries exactly one para:hasEntityId on its existing points, so no id
is derived.

Worth stating in the handover and not hiding here: SSC's VAVs carry no
electrical point of any kind - air flow, temperature, setpoints, on/off,
occupancy, operation hours and contributionFraction, and nothing else - so the
Electrical pair are containers with nothing behind them until the backend
calculates them. They are on the sheet by client direction 2026-09-09, for
parity with QNL, which is in the same position.

    python3 projects/SSC/add_air_terminal_points.py --dry-run
"""

import argparse
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "projects/QNL"))
from add_virtual_meters import read_ontology, write_ontology, row, index
from add_air_terminal_points import POINTS, entity_id

SHEET = ROOT / "reference-models/QF_SSC_Ontology_V04.xlsx"
TERMINALS = ("brick:Variable_Air_Volume_Box", "brick:Constant_Air_Volume_Box")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    rows = read_ontology(SHEET)
    header, body = rows[0], rows[1:]
    etype, located, fedby, eids, declared = index(rows)

    units = sorted(u for u, t in etype.items() if t in TERMINALS)
    segments = tuple("_" + seg for seg, *_ in POINTS)
    existing = {r[0] for r in body
                if r[2] == "brick:hasPoint" and r[3].endswith(segments)}
    if existing:
        raise SystemExit(f"{len(existing)} units already carry Air Terminal points "
                         "- nothing to add")

    out, derived = [], []
    for u in units:
        ids = eids.get(u) or set()
        if len(ids) == 1:
            eid = next(iter(ids))
        else:
            eid = entity_id(u)
            derived.append(u)
        for seg, label, cls, unit, tsid in POINTS:
            point = f"{u}_{seg}"
            out.append(row(u, etype[u], "brick:hasPoint", point, cls,
                           oprops=[("rdfs:label_en", label),
                                   ("brick:hasUnit", unit)]))
            out.append(row(point, cls, "ref:hasExternalReference",
                           "<blanknode>", "ref:TimeseriesReference",
                           oprops=[("ref:hasTimeseriesId", tsid),
                                   ("para:hasEntityId", eid)]))

    print(f"terminals         {len(units)} ({len(POINTS)} points each)")
    print(f"rows              {len(out)}  ({len(out)//2} points, each with its reference row)")
    print(f"entityId derived  {len(derived)}" + (f": {derived}" if derived else ""))
    print(f"ontology          {len(body)} -> {len(body) + len(out)}")

    if args.dry_run:
        return
    write_ontology(SHEET, header, body + out)
    print(f"wrote {SHEET}  ({len(body) + len(out)} rows)")


if __name__ == "__main__":
    main()
