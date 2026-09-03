"""Add the virtual metering layer to the QNL ontology.

Regenerates the layer from the tier matrix against the *live* ontology rather
than patching the hand-built workbook, so the room identifiers agree by
construction and rooms added after that workbook was made (L1-145) are picked
up for free.

Emits, in order:

  1. early declarations  - the para: classes, the two thermal units and the
     entity:Metering system node, all of which are referenced by later rows
  2. one virtual meter per (meter class x spatial entity) the tier matrix
     selects, each carrying the Dar Cairo five-predicate block
  3. para:contributionFraction on every unit fed by an AHU, except units sitting
     in a shaft, riser or ceiling void

Timeseries references for the meter points are NOT written - the historian
carries no calculated tags yet (checked: zero *_CALC, zero ContributionFraction).
They go to a pending file instead, with the Dar Cairo tsid proposed and the
entityId left for the calculation-engine team. contributionFraction *is*
referenced, because both halves of its key are known: the tsid is fixed at
"ContributionFraction" and the entityId is the one the unit's existing points
already carry.

    python3 projects/QNL/add_virtual_meters.py
"""

import argparse
import collections
import csv
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[2]
ONTOLOGY = ROOT / "projects/QNL/QNL_Ontology.csv"
WIDTH = 27

SITE = "entity:QF"
METERING = "entity:Metering"

# A room whose identifier matches this holds plant or cabling, not people. The
# rule is Dar Cairo's own reading of what a space meter is for; QNL matches
# nothing here today (its shaft-dwelling assets are FCUs, which no AHU feeds)
# but the rule travels to the next building.
SHAFT = re.compile(r"(Shaft|Riser|Ceiling-Void|Raised-Floor)", re.I)

# --- the tier matrix, from Sheet1 of the hand-built workbook -----------------
# B building, F floor, R room. Segment names are Dar Cairo's verbatim, except
# HW-Power-Thermal-Virtual-Meter, coined here to mirror the CHW one.
ELEC, THERMAL = "elec", "thermal"
METER_TYPES = [
    # class,                    segment,                               tiers,   kind
    ("para:Utility_Meter",      "Utility-Virtual-Meter",               "B",     ELEC),
    ("para:UPS_Meter",          "UPS-Util-Electrical-Virtual-Meter",   "B",     ELEC),
    ("para:HW_Meter",           "HW-Power-Thermal-Virtual-Meter",      "BF",    THERMAL),
    ("para:SPWR_Meter",         "SPWR-Util-Electrical-Virtual-Meter",  "BF",    ELEC),
    ("para:Common_Util_Meter",  "Common-Util-Electrical-Virtual-Meter","BF",    ELEC),
    ("para:CHW_Meter",          "CHW-Power-Thermal-Virtual-Meter",     "BFR",   THERMAL),
    ("para:HVAC_Meter",         "HVAC-Util-Electrical-Virtual-Meter",  "BFR",   ELEC),
    ("para:LTG_Meter",          "LTG-Util-Electrical-Virtual-Meter",   "BFR",   ELEC),
    ("brick:Electrical_Meter",  "Electrical-Virtual-Meter",            "BFR",   ELEC),
]

# Consumption is energy, Demand is power. Thermal carries para:KiloWt so a
# building rollup cannot silently add chilled-water kW to electrical kW.
POINTS = {
    ELEC: [
        ("Consumption", "brick:Electrical_Energy_Usage_Sensor", "unit:KiloW-HR"),
        ("Demand",      "brick:Electric_Power_Sensor",          "unit:KiloW"),
    ],
    THERMAL: [
        ("Consumption", "brick:Thermal_Energy_Usage_Sensor", "para:KiloWt-HR"),
        ("Demand",      "brick:Thermal_Power_Sensor",        "para:KiloWt"),
    ],
}

# Dar Cairo's timeseries token per (meter class, point kind). Proposed only -
# the entityId half is the historian's key for the metered space and does not
# exist for QNL yet, so these go to the pending file, not into the sheet.
TSID = {
    ("para:Utility_Meter",     "Consumption"): "Utility_KWH",
    ("para:Utility_Meter",     "Demand"):      "Utility_KW",
    ("para:UPS_Meter",         "Consumption"): "UPS_KWH_CALC",
    ("para:UPS_Meter",         "Demand"):      "UPS_KW_CALC",
    ("para:SPWR_Meter",        "Consumption"): "SPWR_KWH_CALC",
    ("para:SPWR_Meter",        "Demand"):      "SPWR_KW_CALC",
    ("para:Common_Util_Meter", "Consumption"): "COMMON_KWH_CALC",
    ("para:Common_Util_Meter", "Demand"):      "COMMON_KW_CALC",
    ("para:HVAC_Meter",        "Consumption"): "HVAC_KWH_CALC",
    ("para:HVAC_Meter",        "Demand"):      "HVAC_KW_CALC",
    ("para:LTG_Meter",         "Consumption"): "LTG_KWH_CALC",
    ("para:LTG_Meter",         "Demand"):      "LTG_KW_CALC",
    ("brick:Electrical_Meter", "Consumption"): "ELEC_KWH_CALC",
    ("brick:Electrical_Meter", "Demand"):      "ELEC_KW_CALC",
    ("para:CHW_Meter",         "Consumption"): "CWPWR_KWTH_CALC",
    ("para:CHW_Meter",         "Demand"):      "CWPWR_KWT_CALC",
    ("para:HW_Meter",          "Consumption"): "HWPWR_KWTH_CALC",
    ("para:HW_Meter",          "Demand"):      "HWPWR_KWT_CALC",
}

# Everything a later row points at has to be declared before it. para:Utility_Meter
# is already in the sheet, so it is not repeated here.
DECLARATIONS = [
    ("para:Metering_System",     "brick:System",              "Metering System"),
    ("para:UPS_Meter",           "brick:Electrical_Meter",    "UPS Electrical Meter"),
    ("para:SPWR_Meter",          "brick:Electrical_Meter",    "Small Power Electrical Meter"),
    ("para:Common_Util_Meter",   "brick:Electrical_Meter",    "Common Utilities Electrical Meter"),
    ("para:HVAC_Meter",          "brick:Electrical_Meter",    "HVAC Electrical Meter"),
    ("para:LTG_Meter",           "brick:Electrical_Meter",    "Lighting Electrical Meter"),
    ("para:CHW_Meter",           "brick:Thermal_Power_Meter", "Chilled Water Thermal Power Meter"),
    ("para:HW_Meter",            "brick:Thermal_Power_Meter", "Hot Water Thermal Power Meter"),
    ("para:contributionFraction", "brick:Point",              "Contribution Fraction"),
]
UNIT_DECLARATIONS = [("para:KiloWt", "kWt"), ("para:KiloWt-HR", "kWt·hr")]


# Which side a property belongs on is a property of the ROW, not of the property
# name: rdfs:label_en labels the meter on `meter isPartOf Metering` and labels the
# point on `meter hasPoint point`. Getting this backwards is the commonest
# authoring mistake here, so each caller names the side rather than sharing a
# lookup that cannot tell the two rows apart.
SUBJ_SLOTS = [5, 9, 13, 17, 21, 25]
OBJ_SLOTS = [7, 11, 15, 19, 23]


def row(subject, stype, predicate, obj="", otype="", sprops=(), oprops=()):
    """One sheet row. sprops describe the subject, oprops the object; each is a
    sequence of (column_name, value) pairs laid into the prop groups in order."""
    r = [subject, stype, predicate, obj, otype] + [""] * (WIDTH - 5)
    for slots, props in ((SUBJ_SLOTS, sprops), (OBJ_SLOTS, oprops)):
        for i, (name, value) in zip(slots, props):
            r[i], r[i + 1] = name, value
    return r


def label_of(identifier):
    """Label from the identifier, mechanically - one map so the two cannot drift."""
    return identifier.split(":", 1)[1].replace("_", " ").replace("-", " ")


def read_ontology(path):
    with open(path, encoding="utf-8-sig", newline="") as fh:
        return list(csv.reader(fh))


def index(rows):
    """Everything the generator needs to know about the existing sheet."""
    etype, located, fedby, owner = {}, {}, collections.defaultdict(list), {}
    entity_id = collections.defaultdict(set)
    declared = set()
    for r in rows[1:]:
        if len(r) < 5:
            continue
        if r[0] and r[1]:
            etype.setdefault(r[0], r[1])
        if r[3] and r[4]:
            etype.setdefault(r[3], r[4])
        if r[1] == "owl:Class":
            declared.add(r[0])
        if r[2] == "rec:locatedIn":
            located[r[0]] = r[3]
        if r[2] == "rec:isFedBy":
            fedby[r[0]].append(r[3])
        if r[2] == "brick:hasPoint":
            owner[r[3]] = r[0]
    for r in rows[1:]:
        for i in range(5, len(r) - 1, 2):
            if r[i] == "para:hasEntityId" and r[i + 1] and r[0] in owner:
                entity_id[owner[r[0]]].add(r[i + 1])
    return etype, located, fedby, entity_id, declared


def spatial_targets(etype):
    """The building, its levels and its rooms, each with the type to write in
    the objectType column."""
    tiers = {"B": [], "F": [], "R": []}
    for e, t in etype.items():
        if t == "rec:Building":
            tiers["B"].append((e, t))
        elif t in ("rec:Level", "rec:BasementLevel", "rec:RoofLevel", "rec:GroundLevel"):
            tiers["F"].append((e, t))
        elif t == "rec:Room":
            tiers["R"].append((e, t))
    return {k: sorted(v) for k, v in tiers.items()}


def build_meters(tiers):
    """The metering layer. Returns (rows, pending timeseries)."""
    out, pending = [], []
    for cls, segment, applies, kind in METER_TYPES:
        for tier in applies:
            for target, target_type in tiers[tier]:
                meter = f"{target}_{segment}"
                mlabel = label_of(meter)
                out.append(row(meter, cls, "brick:isPartOf", METERING, "para:Metering_System",
                               sprops=[("rdfs:label_en", mlabel)]))
                out.append(row(meter, cls, "brick:meters", target, target_type))
                out.append(row(meter, cls, "brick:isVirtualMeter", "<blanknode>", "<blanknode>",
                               oprops=[("brick:value", "TRUE")]))
                out.append(row(meter, cls, "rec:locatedIn", target, target_type))
                for kindname, pcls, unit in POINTS[kind]:
                    point = f"{meter}-{kindname}"
                    out.append(row(meter, cls, "brick:hasPoint", point, pcls,
                                   oprops=[("rdfs:label_en", f"{mlabel} {kindname}"),
                                           ("brick:hasUnit", unit)]))
                    pending.append((point, pcls, TSID.get((cls, kindname), ""), "", target))
    return out, pending


def build_contribution(etype, located, fedby, entity_id):
    """para:contributionFraction on every AHU-fed unit outside a shaft."""
    out, skipped, derived = [], [], []
    fed = sorted(u for u, sources in fedby.items()
                 if any(etype.get(s) == "brick:Air_Handling_Unit" for s in sources))
    for unit in fed:
        room = located.get(unit, "")
        if room and SHAFT.search(room):
            skipped.append((unit, room))
            continue
        ids = entity_id.get(unit) or set()
        if len(ids) == 1:
            eid = next(iter(ids))
        else:
            # The rule is proven by every one of the 296 units that do carry a
            # key, so deriving the 297th is safe - but it is reported, not silent.
            eid = unit.split(":", 1)[1].replace("-", "_")
            derived.append((unit, eid))
        point = f"{unit}_Contribution-Fraction"
        out.append(row(unit, etype[unit], "brick:hasPoint", point, "para:contributionFraction",
                       oprops=[("rdfs:label_en", "Contribution Fraction"),
                               ("brick:hasUnit", "unit:UNITLESS")]))
        out.append(row(point, "para:contributionFraction", "ref:hasExternalReference",
                       "<blanknode>", "ref:TimeseriesReference",
                       oprops=[("ref:hasTimeseriesId", "ContributionFraction"),
                               ("para:hasEntityId", eid)]))
    return out, fed, skipped, derived


def build_declarations(declared):
    out = []
    for cls, parent, label in DECLARATIONS:
        if cls in declared:
            continue
        out.append(row(cls, "owl:Class", "rdfs:subClassOf", parent,
                       sprops=[("rdfs:label_en", label)]))
    for unit, symbol in UNIT_DECLARATIONS:
        out.append(row(unit, "qudt:Unit", "rdf:type", "qudt:Unit",
                       sprops=[("qudt:symbol", symbol)]))
    out.append(row(METERING, "para:Metering_System", "brick:isPartOf", SITE, "rec:Site",
                   sprops=[("rdfs:label_en", "Metering System")]))
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--ontology", default=str(ONTOLOGY))
    ap.add_argument("--out", default=str(ROOT / "projects/QNL/QNL_Ontology.csv"))
    ap.add_argument("--pending", default=str(ROOT / "projects/QNL/QNL_virtual_meter_timeseries_pending.csv"))
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    rows = read_ontology(args.ontology)
    header = rows[0]
    etype, located, fedby, entity_id, declared = index(rows)

    if any("Virtual-Meter" in r[0] for r in rows[1:]):
        raise SystemExit("sheet already carries a metering layer - rerun on a clean ontology")

    tiers = spatial_targets(etype)
    decls = build_declarations(declared)
    meters, pending = build_meters(tiers)
    contrib, fed, skipped, derived = build_contribution(etype, located, fedby, entity_id)

    print(f"spatial targets   building {len(tiers['B'])}  levels {len(tiers['F'])}  rooms {len(tiers['R'])}")
    print(f"declarations      {len(decls)} rows")
    print(f"virtual meters    {len(meters) // 6} meters, {len(meters)} rows")
    print(f"contributionFraction  {len(contrib) // 2} of {len(fed)} AHU-fed units"
          f"  (skipped in shafts: {len(skipped)})")
    if derived:
        print(f"  entityId derived rather than reused for: {[u for u, _ in derived]}")
    if skipped:
        for u, r in skipped:
            print(f"  skipped {u} in {r}")

    if args.dry_run:
        return

    body = rows[1:] + decls + meters + contrib
    # Declarations have to precede their first use, and the converter reads the
    # sheet top to bottom.
    body.sort(key=lambda r: 0 if r[1] in ("owl:Class", "qudt:Unit") else 1)
    with open(args.out, "w", encoding="utf-8-sig", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(header)
        w.writerows(body)
    print(f"wrote {args.out}  ({len(body)} rows, was {len(rows) - 1})")

    with open(args.pending, "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["point", "point_class", "proposed_hasTimeseriesId",
                    "hasEntityId_TO_CONFIRM", "meters"])
        w.writerows(pending)
    print(f"wrote {args.pending}  ({len(pending)} points awaiting telemetry keys)")


if __name__ == "__main__":
    main()
