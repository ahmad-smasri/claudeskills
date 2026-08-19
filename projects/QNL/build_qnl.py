#!/usr/bin/env python3
"""Build the QNL (Qatar National Library) PARA/Brick ontology sheet.

Inputs  : QNL_Room_Names_for_Ontology.xlsx, QNL_Assets_Location_Relationships.xlsx
Outputs : QNL_Ontology.xlsx (27-column triple sheet), QNL_identifier_crosswalk.csv
"""
import csv, os, re, sys
from collections import OrderedDict
import openpyxl

SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sources") + "/"
ROOMS_XLSX = SRC + "QNL_Room_Names_for_Ontology.xlsx"
ASSETS_XLSX = SRC + "QNL_Assets_Location_Relationships.xlsx"
OUT = os.path.dirname(os.path.abspath(__file__)) + "/"

HEADER = ["subject", "subjectType", "predicate", "object", "objectType"] + \
    ["subject_prop_name", "subject_prop_val", "object_prop_name", "object_prop_val"] * 5 + \
    ["subject_prop_name", "subject_prop_val"]
assert len(HEADER) == 27


def label(text):
    """Label style: QF SSC. The source text survives verbatim, punctuation and all.

    SSC labels rooms `1.001_CORRIDOR` and equipment `SSC_FCU0001` - the raw
    schedule and register strings, not the cleaned form the PARA label rule
    produces. Whitespace is stripped because the validator rejects it (E-WS-1);
    nothing else is touched.
    """
    return " ".join(text.split())


def row(subject, stype, pred, obj, otype="", props=()):
    """props is a sequence of (side, name, value); side is 's' or 'o'."""
    cells = [subject, stype, pred, obj, otype] + [""] * 22
    slots = [(5, 6, "s"), (7, 8, "o"), (9, 10, "s"), (11, 12, "o"),
             (13, 14, "s"), (15, 16, "o"), (17, 18, "s"), (19, 20, "o"),
             (21, 22, "s"), (23, 24, "o"), (25, 26, "s")]
    used = set()
    for side, name, val in props:
        for idx, (n, v, sd) in enumerate(slots):
            if idx in used or sd != side:
                continue
            cells[n], cells[v] = name, val
            used.add(idx)
            break
        else:
            raise RuntimeError(f"no free {side} prop slot for {name}")
    return cells


# --------------------------------------------------------------------------- rooms
LEVEL_RE = re.compile(r"^(B|L1|L2|T1)[_-]?(.*)$")
LEVEL_TYPE = {"B": "rec:BasementLevel", "L1": "rec:Level",
              "L2": "rec:Level", "T1": "rec:Level"}
# Identifiers keep the source level codes - they are the segment the room tags
# carry. Labels spell the level out, because that is what the front end shows.
LEVEL_LABEL = {"B": "Basement", "L1": "Level 1", "L2": "Level 2",
               "T1": "Terrace 1"}

wb = openpyxl.load_workbook(ROOMS_XLSX, read_only=True, data_only=True)
room_src = []
for r in list(wb.worksheets[0].iter_rows(values_only=True))[1:]:
    if not r[0]:
        continue
    room_src.append((str(r[0]).strip(), str(r[1]).strip(), str(r[2]).strip()))

rooms = OrderedDict()      # source entity name -> dict
notes = []
for src_entity, number, name in room_src:
    m = LEVEL_RE.match(number)
    if m:
        level, num = m.group(1), m.group(2)
    else:
        level, num = "B", number
        notes.append(f"room number {number!r} carries no level prefix; placed on level B "
                     f"because its ST-nn siblings are all basement rooms")
    # The source room schedule is inconsistent about how the level is joined to
    # the room number: most rows write B_034, a minority write B036_REST,
    # B-ST-01, L1023_1. The user asked for one shape throughout, so both the
    # identifier and the label are rebuilt from the same (level, num, name)
    # triple and cannot drift apart:
    #
    #   identifier  entity:QNL_<level>_<num>_<name>     QNL_B_063_PLANT_ROOM_01
    #   label             <level>.<num>_<name>          B.063_PLANT_ROOM_01
    #
    # The dot between level and room number is the QF SSC label shape - SSC
    # writes 1.001_CORRIDOR for room 001 on level 1. Nothing inside <num> or
    # <name> is touched; only the join between the segments is regularised.
    if not num:
        sys.exit("room %r has a level but no room number" % number)
    ident = "entity:QNL_%s_%s_%s" % (level, num, name)
    rooms[src_entity] = {
        "id": ident, "level": level,
        "label": label("%s.%s_%s" % (level, num, name)),
        "number": number, "name": name,
    }

dupes = [i for i in rooms if list(x["id"] for x in rooms.values()).count(rooms[i]["id"]) > 1]
if dupes:
    sys.exit("duplicate room identifiers: %s" % dupes[:10])

# --------------------------------------------------------------------------- assets
CLASS = {"AHUB": "brick:Air_Handling_Unit",
         "VAV": "brick:Variable_Air_Volume_Box",
         "CAV": "brick:Constant_Air_Volume_Box",
         "FCU": "brick:Fan_Coil_Unit"}
TERMINAL = {"VAV", "CAV", "FCU"}
LOOP = "entity:QNL_CHILLED_WATER_LOOP"
LOOP_CLASS = "para:Chilled_Water_Loop_Network"


def equip_id(tag):
    """Prefix the register tag with the building code, QF SSC style.

    SSC subjects read entity:SSC_FCU0001 - building code, then the register tag.
    QNL follows: FCU_1F_056 becomes entity:QNL_FCU_1F_056. The tag itself is not
    touched, so it stays the BMS join key; only the building code is added.
    """
    return "QNL_" + tag


wb = openpyxl.load_workbook(ASSETS_XLSX, read_only=True, data_only=True)
assets = []
unknown_rooms = set()
for ws in wb.worksheets:
    kind = ws.title.strip()
    for r in list(ws.iter_rows(values_only=True))[1:]:
        if not r[0]:
            continue
        tag, room_tag, fed_by = str(r[0]).strip(), str(r[1]).strip(), str(r[2]).strip()
        if room_tag not in rooms:
            # the room list carries one entry with a trailing space
            match = [k for k in rooms if k.strip() == room_tag.strip()]
            if not match:
                unknown_rooms.add(room_tag)
                continue
            room_tag = match[0]
        assets.append({"kind": kind, "tag": tag, "id": "entity:" + equip_id(tag),
                       "cls": CLASS[kind], "room": rooms[room_tag]["id"],
                       "fed_by": fed_by})
if unknown_rooms:
    sys.exit("assets reference rooms absent from the room list: %s" % sorted(unknown_rooms))

by_tag = {a["tag"]: a for a in assets}
for a in assets:
    if a["fed_by"].upper() == "CHILLED WATER LOOP":
        a["src"], a["src_cls"] = LOOP, LOOP_CLASS
    elif a["fed_by"] in by_tag:
        a["src"], a["src_cls"] = by_tag[a["fed_by"]]["id"], by_tag[a["fed_by"]]["cls"]
    else:
        sys.exit("unresolved Fed By value %r on %s" % (a["fed_by"], a["tag"]))

ids = [a["id"] for a in assets]
if len(set(ids)) != len(ids):
    sys.exit("duplicate equipment identifiers")

# --------------------------------------------------------------------------- rows
out = []

# Extensions -----------------------------------------------------------------
out.append(row(LOOP_CLASS, "owl:Class", "rdfs:subClassOf", "brick:HVAC_Equipment", "",
               [("s", "rdfs:label_en", "Chilled Water Loop Network")]))

# Spatial --------------------------------------------------------------------
out.append(row("entity:QNL", "rec:Building", "rec:isPartOf",
               "entity:Qatar-Foundation", "rec:Site",
               [("s", "rdfs:label_en", "QNL"), ("o", "rdfs:label_en", "Qatar Foundation")]))

levels_used = sorted({d["level"] for d in rooms.values()})
for lvl in levels_used:
    out.append(row("entity:QNL_%s" % lvl, LEVEL_TYPE[lvl], "rec:isPartOf",
                   "entity:QNL", "rec:Building",
                   [("s", "rdfs:label_en", LEVEL_LABEL[lvl])]))

for d in rooms.values():
    out.append(row(d["id"], "rec:Room", "rec:isPartOf",
                   "entity:QNL_%s" % d["level"], LEVEL_TYPE[d["level"]],
                   [("s", "rdfs:label_en", d["label"])]))

# Chilled water loop ---------------------------------------------------------
out.append(row(LOOP, LOOP_CLASS, "rec:locatedIn", "entity:QNL", "rec:Building",
               [("s", "rdfs:label_en", "QNL_CHILLED_WATER_LOOP")]))

# Equipment ------------------------------------------------------------------
for kind in ("AHUB", "VAV", "CAV", "FCU"):
    for a in [x for x in assets if x["kind"] == kind]:
        bare = a["id"].replace("entity:", "")
        out.append(row(a["id"], a["cls"], "rec:locatedIn", a["room"], "rec:Room",
                       [("s", "rdfs:label_en", label(bare))]))
        out.append(row(a["id"], a["cls"], "rec:isFedBy", a["src"], a["src_cls"]))
        if kind in TERMINAL:
            out.append(row(a["id"], a["cls"], "rec:feeds", a["room"], "rec:Room"))
        # SSC shape: the IFC reference carries both properties. para:IFC_ID is the
        # slot for the real IFC GUID and is left empty until BIM supplies it;
        # ref:ifcName is the entity name, which is derivable.
        out.append(row(a["id"], a["cls"], "ref:hasExternalReference",
                       "<blanknode>", "ref:IFCReference",
                       [("o", "para:IFC_ID", ""), ("o", "ref:ifcName", bare)]))
        # No timeseries reference row here. A ref:TimeseriesReference belongs to a
        # POINT, never to the equipment: all 1,767 of them in QF SSC hang off a
        # brick:hasPoint object and none off a piece of equipment. QNL has no
        # points because no IO list was supplied, so it has no timeseries refs.

# --------------------------------------------------------------------------- write
wbo = openpyxl.Workbook()
ws = wbo.active
ws.title = "Ontology"
ws.append(HEADER)
for r in out:
    ws.append(r)
wbo.save(OUT + "QNL_Ontology.xlsx")

with open(OUT + "QNL_Ontology.csv", "w", newline="") as fh:
    w = csv.writer(fh)
    w.writerow(HEADER)
    w.writerows(out)

with open(OUT + "QNL_identifier_crosswalk.csv", "w", newline="") as fh:
    w = csv.writer(fh)
    w.writerow(["kind", "source_identifier", "ontology_identifier", "rdfs:label_en"])
    for src_entity, d in rooms.items():
        w.writerow(["room", src_entity, d["id"], d["label"]])
    for a in assets:
        w.writerow([a["kind"], a["tag"], a["id"],
                    label(a["id"].replace("entity:", ""))])

print("rows      :", len(out))
print("rooms     :", len(rooms), "levels:", levels_used)
print("assets    :", len(assets), {k: sum(1 for a in assets if a["kind"] == k) for k in CLASS})
for n in sorted(set(notes)):
    print("note      :", n)
