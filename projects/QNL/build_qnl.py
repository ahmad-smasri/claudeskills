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
LEDGER_XLSX = os.path.dirname(os.path.abspath(__file__)) + "/QNL_datapoint_ledger_v2.xlsx"
OUT = os.path.dirname(os.path.abspath(__file__)) + "/"

HEADER = ["subject", "subjectType", "predicate", "object", "objectType"] + \
    ["subject_prop_name", "subject_prop_val", "object_prop_name", "object_prop_val"] * 5 + \
    ["subject_prop_name", "subject_prop_val"]
assert len(HEADER) == 27


def label(text):
    """Label style: QF SSC. The source text, with underscores as spaces.

    The current SSC sheet labels rooms `1.001 CORRIDOR` and its own assets
    `SSC_CHW_CHWP01 Motor` - the raw schedule and register strings with `_`
    read as a word break, and every other mark left alone: the dot between
    level and room number survives, and so do dashes and slashes (`A / V ROOM`).
    That is the difference from the PARA label rule, which strips punctuation
    outright.
    """
    return " ".join(text.replace("_", " ").split())


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

# The room schedule was typed by hand and carries misspellings that would
# otherwise ride into both the identifier and the label a user reads. Each
# entry below was settled against the rest of the schedule, not guessed: the
# correct spelling appears on a sibling room, or the token is a run-together
# pair whose separator convention every other room follows. The map is applied
# to the underscore-separated tokens of the room *name* only - never to the
# level or the room number, which are the join key back to the drawings.
#
# Whole-word misspellings; the evidence for each is in QNL_handover-note.md.
TYPO_FIXES = {
    "CARRLES": "CARRELS",              # CARRELS on 15 other rooms
    "CTRCULATION": "CIRCULATION",
    "GREEM": "GREEN",
    "SPRIMKLERS": "SPRINKLERS",
    "ITTIGATION": "IRRIGATION",
    "WASING": "WASHING",
    "CONTOL": "CONTROL",               # CONTROL on 8 other rooms
    "LEVLEL": "LEVEL",
    "LOBY": "LOBBY",                   # L1_042_LOBBY
    "VENTILATON": "VENTILATION",
    "VENTLATON": "VENTILATION",
    "LIBRARIA": "LIBRARIAN",           # 14 LIBRARIAN rooms
    "PANKING": "PARKING",
    "WATING": "WAITING",
    "MULTPURPOSE": "MULTIPURPOSE",
    "ANGUAGE": "LANGUAGE",
    "BIBLIOGRANHER1": "BIBLIOGRAPHER1",   # L1_082_BIBLIOGRAPHER2 next door
    "PUBLIS": "PUBLIC",                # L1_080_PUBLIC_SERVICE
    "CSECURITY": "SECURITY",           # 8 SECURITY rooms, stray leading C
    "TRANSH": "TRASH",                 # only waste room in the building
    "PRESEARCHERS": "RESEARCHERS",     # stray leading P; B_151 RESEARCH
    # Run-together pairs. The separator, not the wording, is what is restored -
    # every sibling room writes these two tokens apart.
    "ROOMMEN": "ROOM_MEN",             # 9 x REST_ROOM_MEN
    "ABLUTIONMEN": "ABLUTION_MEN",
    "ABLUTIONWOMEN": "ABLUTION_WOMEN",
    "ADPUBLIC": "AD_PUBLIC",           # AD_COLLECTIONS, AD_OFFICE, AD_ADMIN
    "LIBDIRECTORS": "LIB_DIRECTORS",
    "INDIVISTUDY": "INDIVI_STUDY",     # sibling shape is GROUP_STUDY_ROOM
}


def fix_spelling(name):
    """Correct the schedule's typing errors in a room name, token by token.

    Whole tokens only, so a correction can never fire inside a longer word,
    and abbreviations the schedule uses deliberately - AD, SEC, RES, LIBR,
    PERS, ITT and the rest - are left exactly as the source wrote them.
    """
    return "_".join(TYPO_FIXES.get(t, t) for t in name.split("_"))

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
    #   label             <level>.<num> <name>          B.063 PLANT ROOM 01
    #
    # The dot between level and room number is the QF SSC label shape - SSC
    # writes 1.001 CORRIDOR for room 001 on level 1 - and label() turns the
    # remaining underscores into spaces. Nothing inside <num> or <name> is
    # touched; only the join between the segments is regularised.
    if not num:
        sys.exit("room %r has a level but no room number" % number)
    fixed = fix_spelling(name)
    if fixed != name:
        notes.append(f"room name {name!r} corrected to {fixed!r}")
    name = fixed
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
# QF SSC 0.5 names its loop entity:CHWS-MAIN-LOOP, types it
# para:Chilled_Water_Loop_Network and gives it two subject rows - rec:locatedIn
# the building, and an IFC reference. QNL follows that shape.
#
# The building code is the one departure. SSC's loop carries none, but it is
# rec:locatedIn entity:SSC, so a QNL loop under the same bare name would be one
# entity located in two buildings once the converter loads both sheets into one
# graph. Site-level systems - entity:HVAC, entity:QF - are genuinely shared and
# rightly bare; a per-building main loop is not. Flagged in the handover note.
LOOP = "entity:QNL_CHWS-MAIN-LOOP"

# The systems layer, which is what the front end's system tree is built from.
#
# Dar Cairo's shape: a top-level system is a subject carrying brick:isPartOf the
# SITE and a label; a sub-system is declared only as the object of its parent's
# brick:hasPart row, with its class in objectType and its label in an object
# prop; equipment points up with brick:isPartOf. No link is ever stated twice.
# QF SSC 0.5 agrees - entity:HVAC brick:isPartOf entity:QF.
#
# entity:CHW-System is not a node QNL invents - QF SSC 0.5 already declares it,
# bare and site-level under entity:HVAC, holding SSC's four chilled water booster
# pumps and five heat exchangers. QNL reusing it puts its loop in that same
# group rather than creating a one-child node, the same way both buildings share
# entity:QF and entity:HVAC. SSC leaves its own loop outside CHW-System, which
# looks like an oversight: a distribution loop is part of the chilled water
# system by any reading.
# brick:HVAC_System is a Brick 1.4 alias for
# brick:Heating_Ventilation_Air_Conditioning_System, and the ladder would take the
# preferred term. The house overrides that: both reference models write
# brick:HVAC_System and the front end keys off it, so consistency across the
# estate wins over the preferred spelling. The W-TYP-5 alias warning is accepted
# and recorded in the handover.
HVAC = "entity:HVAC"
CHW = "entity:CHW-System"
CHW_CLASS = "brick:Chilled_Water_System"
HVAC_CLASS = "brick:HVAC_System"
LOOP_CLASS = "para:Chilled_Water_Loop_Network"


def equip_id(tag):
    """Prefix the register tag with the building code, QF SSC style.

    SSC subjects read entity:SSC_FCU0001 - building code, then the register tag.
    QNL follows: FCU_1F_056 becomes entity:QNL_FCU_1F_056. Tags are otherwise not
    touched, so they stay the BMS join key.

    The one exception is the AHUB family, at the user's direction. AHUB002 packs
    type and level into a single token and carries no separators, where VAV, CAV
    and FCU are all TYPE_LEVEL_COUNT; it is rewritten AHU_B_002 so all four
    families parse by one rule.
    """
    m = re.match(r"^AHUB(\d+)$", tag)
    if m:
        tag = "AHU_B_%s" % m.group(1)
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

# --------------------------------------------------------------------------- points
# The point layer joins three sources:
#   - Selected_PARA_OS_Data_Points_v4.0.xlsx : which points are selected, per unit
#     (the per-unit membership - one row per unit x point, "Must Have")
#   - QNL_Historian_IO_list_CP2.xlsx         : each tag's engineering unit, historian
#     SourceTag and analog/discrete kind (the authority on units and series ids)
#   - QNL_datapoint_ledger_v2.xlsx           : the reviewed class decision and a clean
#     descriptor (match_phrase) per point signature
#
# Only the four families already in the sheet are built (AHU, VAV, CAV, FCU); the
# selected list also covers CCU, EF, DX, HEX, KEF, SEF, TEF and GEN, whose equipment
# is not in the asset register, so those points are out of scope here.
#
# Engineering units come from the IO list, not the Selected sheet: the Selected sheet
# has 30 analog rows with humidity/temperature units swapped (e.g. AvgSpcHumd as degC),
# which the IO list gets right.
SEL_XLSX = SRC + "Selected_PARA_OS_Data_Points_v4.0.xlsx"
IO_XLSX = SRC + "QNL_Historian_IO_list_CP2.xlsx"
POINT_FAMILIES = {"AHU": "AHUB", "VAV": "VAV", "CAV": "CAV", "FCU": "FCU"}

# IO-list engineering unit -> Brick unit term. Discrete points and blanks carry
# unit:UNITLESS, as QF SSC does for its status and mode points.
UNIT_URI = {
    "°c": "unit:DEG_C", "%": "unit:PERCENT", "l/s": "unit:L-PER-SEC",
    "hrs": "unit:HR", "%rh": "unit:PERCENT_RH", "pa": "unit:PA",
    "m/s": "unit:M-PER-SEC", "kwh": "unit:KiloW-HR", "kw": "unit:KiloW",
}

# The class is the authority on the physical quantity, and it outranks the IO list.
#
# The IO list gets units right far more often than the Selected sheet, but it is not
# infallible: 20 of the 24 `.kW` tags carry `%` against a description that reads
# "Power" - the same defect the datapoint ledger caught and corrected. Taking the IO
# unit verbatim put unit:PERCENT on 20 brick:Electric_Power_Sensor points, which says
# a power sensor reads a percentage.
#
# So where the resolved class names the quantity unambiguously, the class decides and
# the override is logged. Only classes whose quantity admits exactly one unit here are
# listed: air flow deliberately is not, because the IO list distinguishes volumetric
# flow (l/s, on the VAV/CAV boxes) from velocity (m/s, on the AHU ducts) and both are
# real measurements.
CLASS_UNIT = {
    "brick:Electric_Power_Sensor": "unit:KiloW",
    "brick:Electrical_Energy_Usage_Sensor": "unit:KiloW-HR",
    # Air flow is settled by precedent, not by the IO list. Dar Cairo writes
    # unit:L-PER-SEC on all 51 of its air-flow sensors (supply 18, return 15,
    # outside 15, exhaust 3) and SSC on all 118 of its own; unit:M-PER-SEC does
    # not occur once in either reference model, and neither has any air-velocity
    # concept at all. The m/s on QNL's 22 AHU flow points comes only from the IO
    # list's unit column - the same column that puts % on 20 of its 24 .kW tags.
    # A velocity is also not a flow, so the class and the unit disagreed.
    "brick:Supply_Air_Flow_Sensor": "unit:L-PER-SEC",
    "brick:Return_Air_Flow_Sensor": "unit:L-PER-SEC",
}

# Part -> the words that give a generic point descriptor its context. Fans, dampers
# and the cooling valve carry generic descriptors ("position feedback", "electric
# power") that need the part to disambiguate; the air/water sensors already carry it
# in their descriptor, so they are left out.
PART_PREFIX = {
    "SupFan": "Supply Fan", "RtnFan": "Return Fan",
    "SupFan1": "Supply Fan 1", "SupFan2": "Supply Fan 2",
    "RtnFan1": "Return Fan 1", "RtnFan2": "Return Fan 2",
    "IntrnlEADmpr": "Exhaust Air Damper", "IntrnlFADmpr": "Fresh Air Damper",
    "CoolVlv": "Cooling Valve",
}


def point_label(part, match_phrase):
    """A readable label from the ledger descriptor, disambiguated by part.

    The descriptor is the ledger's match_phrase (parenthetical stripped, title case).
    A fan/damper/valve part prepends its context; a numbered sensor part (SpcHumd01)
    appends its number, so the eleven space-humidity sensors read apart.
    """
    base = re.sub(r"\s*\([^)]*\)\s*$", "", str(match_phrase)).strip().title()
    if part in PART_PREFIX:
        return PART_PREFIX[part] + " " + base
    m = re.search(r"(\d+)$", part or "")
    if m:
        return base + " " + str(int(m.group(1)))
    return base


def parse_tag(tag):
    """A historian tag -> (unit, part, point). Only AHU units carry a part."""
    left, point = (tag.rsplit(".", 1) + [""])[:2] if "." in tag else (tag, "")
    m = re.match(r"(QNL_AHUB\d+)_(.+)$", left)
    if m:
        return m.group(1), m.group(2), point
    m = re.match(r"(QNL_AHUB\d+)$", left)
    if m:
        return m.group(1), "", point
    return left, "", point


def load_point_layer():
    """Build {bms_unit: [point dicts]} for the four in-scope families.

    Each point dict is {part, point, cls, unit, label, tsid, bms_unit}. Also returns
    the units selected but absent from the asset register, for the handover note.
    """
    # ledger: (family, part, point) -> (class, match_phrase)
    lw = openpyxl.load_workbook(LEDGER_XLSX, data_only=True)
    ls = lw["Ledger"]
    lc = {ls.cell(1, c).value: c for c in range(1, ls.max_column + 1)}
    ledger = {}
    for r in range(2, ls.max_row + 1):
        fam = ls.cell(r, lc["family"]).value
        part = "" if ls.cell(r, lc["part"]).value in (None, "None") \
            else str(ls.cell(r, lc["part"]).value)
        point = str(ls.cell(r, lc["point"]).value)
        ledger[(fam, part, point)] = (ls.cell(r, lc["final_class"]).value,
                                      ls.cell(r, lc["match_phrase"]).value)

    # IO list: tag -> (engineering unit, historian SourceTag)
    io = {}
    iw = openpyxl.load_workbook(IO_XLSX, data_only=True, read_only=True)
    for rw in iw["QNL analog cp2"].iter_rows(min_row=2, values_only=True):
        if rw[0]:
            io[str(rw[0])] = ((rw[4] or "").strip(), rw[7])
    for rw in iw["QNL Descrete cp2"].iter_rows(min_row=2, values_only=True):
        if rw[0]:
            io[str(rw[0])] = ("", rw[4])          # discrete: unitless, SourceTag col E
    iw.close()

    known_units = {"QNL_" + a["tag"] for a in assets}
    by_unit = {}
    orphans = set()
    unit_overrides = []
    # The Selected sheet lists 15 tags twice (RtnAirDuctPrs.PV, once per AHU). A tag
    # names one physical point, so the repeat is a source defect: emitting it twice
    # would put two identical rows in the sheet (W-DUP-1) and two points on one
    # timeseries id. First occurrence wins; the repeats are counted for the note.
    seen_tags = set()
    duplicate_tags = []
    sw = openpyxl.load_workbook(SEL_XLSX, data_only=True, read_only=True)
    for rw in sw["Sheet1"].iter_rows(min_row=2, values_only=True):
        tag = str(rw[0])
        if tag in seen_tags:
            duplicate_tags.append(tag)
            continue
        seen_tags.add(tag)
        fam_ref = rw[4]
        unit, part, point = parse_tag(tag)
        fam_key = fam_ref if fam_ref in POINT_FAMILIES else \
            (re.match(r"QNL_(AHUB|VAV|CAV|FCU)", tag) and
             {"AHUB": "AHU"}.get(re.match(r"QNL_(AHUB|VAV|CAV|FCU)", tag).group(1),
                                 re.match(r"QNL_(AHUB|VAV|CAV|FCU)", tag).group(1)))
        if fam_key not in POINT_FAMILIES:
            continue                               # other families: out of scope
        if unit not in known_units:
            orphans.add(unit)
            continue
        fam = POINT_FAMILIES[fam_key]
        sig = (fam, part, point)
        if sig not in ledger:
            sys.exit("selected point %r has no ledger class (%s)" % (tag, sig))
        cls, mp = ledger[sig]
        io_unit, tsid = io.get(tag, ("", tag))
        unit_uri = UNIT_URI.get(io_unit.lower(), "unit:UNITLESS")
        forced = CLASS_UNIT.get(cls)
        if forced and forced != unit_uri:
            unit_overrides.append((tag, cls, unit_uri, forced))
            unit_uri = forced
        by_unit.setdefault(unit, []).append({
            "part": part, "point": point, "cls": cls, "unit": unit_uri,
            "label": point_label(part, mp), "tsid": tsid or tag, "bms_unit": unit})
    sw.close()
    return by_unit, sorted(orphans), sorted(set(duplicate_tags)), unit_overrides


points_by_unit, orphan_units, duplicate_selected, unit_overrides = load_point_layer()


def point_rows(a):
    """The point rows for one asset, each as the QF SSC two-row shape -

        equipment brick:hasPoint point   (class, label, unit)
        point     ref:hasExternalReference <blanknode> ref:TimeseriesReference
                  (ref:hasTimeseriesId = historian SourceTag, para:hasEntityId = unit)

    Points are ordered by their identifier so the sheet is stable across builds.
    """
    rows = []
    bms_unit = "QNL_" + a["tag"]
    pts = sorted(points_by_unit.get(bms_unit, []),
                 key=lambda p: (p["part"], p["point"]))
    for p in pts:
        seg = (p["part"] + "_" if p["part"] else "") + p["point"]
        pid = a["id"] + "_" + seg
        rows.append(row(a["id"], a["cls"], "brick:hasPoint", pid, p["cls"],
                        [("o", "rdfs:label_en", p["label"]),
                         ("o", "brick:hasUnit", p["unit"])]))
        rows.append(row(pid, p["cls"], "ref:hasExternalReference",
                        "<blanknode>", "ref:TimeseriesReference",
                        [("o", "ref:hasTimeseriesId", p["tsid"]),
                         ("o", "para:hasEntityId", bms_unit)]))
    return rows


# --------------------------------------------------------------------------- rows
out = []

# Extensions -----------------------------------------------------------------
out.append(row(LOOP_CLASS, "owl:Class", "rdfs:subClassOf", "brick:HVAC_Equipment", "",
               [("s", "rdfs:label_en", "Chilled Water Loop Network")]))
# para:Trip_Alarm is the one class the datapoint layer coins. brick:Alarm is
# reserved for a point literally named a general/summary alarm, so the fan trip
# alarms get a class of their own rather than the bare root - SSC types its own
# _TripAlm points brick:Alarm, which makes trips indistinguishable from every
# other alarm. It follows SSC's own para:Fail_Start_Alarm / para:Fail_Stop_Alarm
# pattern (both reused here as-is) and goes to the PARA team for review.
out.append(row("para:Trip_Alarm", "owl:Class", "rdfs:subClassOf", "brick:Alarm", "",
               [("s", "rdfs:label_en", "Trip Alarm")]))

# Spatial --------------------------------------------------------------------
# The site is the organisation's code, not its spelled-out name, and the current
# QF SSC sheet writes exactly this row for its own building:
#   entity:SSC | rec:Building | rec:isPartOf | entity:QF | rec:Site
#              | rdfs:label_en | SSC Building | rdfs:label_en | Qatar Foundation
# QNL sits under the same site, so it reuses entity:QF rather than minting a
# second name for it - that is what lets the two buildings' sheets join.
out.append(row("entity:QNL", "rec:Building", "rec:isPartOf",
               "entity:QF", "rec:Site",
               [("s", "rdfs:label_en", "QNL Building"),
                ("o", "rdfs:label_en", "Qatar Foundation")]))

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
out.append(row(HVAC, HVAC_CLASS, "brick:isPartOf", "entity:QF", "rec:Site",
               [("s", "rdfs:label_en", "HVAC System")]))

out.append(row(CHW, CHW_CLASS, "brick:isPartOf", HVAC, HVAC_CLASS,
               [("s", "rdfs:label_en", "Chilled Water System")]))
out.append(row(LOOP, LOOP_CLASS, "brick:isPartOf", CHW, CHW_CLASS))
out.append(row(LOOP, LOOP_CLASS, "rec:locatedIn", "entity:QNL", "rec:Building",
               [("s", "rdfs:label_en", label(LOOP.replace("entity:", "")))]))
out.append(row(LOOP, LOOP_CLASS, "ref:hasExternalReference",
               "<blanknode>", "ref:IFCReference",
               [("o", "para:IFC_ID", ""),
                ("o", "ref:ifcName", LOOP.replace("entity:", ""))]))

# Equipment ------------------------------------------------------------------
for kind in ("AHUB", "VAV", "CAV", "FCU"):
    for a in [x for x in assets if x["kind"] == kind]:
        bare = a["id"].replace("entity:", "")
        out.append(row(a["id"], a["cls"], "rec:locatedIn", a["room"], "rec:Room",
                       [("s", "rdfs:label_en", label(bare))]))
        out.append(row(a["id"], a["cls"], "brick:isPartOf", HVAC, HVAC_CLASS))
        out.append(row(a["id"], a["cls"], "rec:isFedBy", a["src"], a["src_cls"]))
        if kind in TERMINAL:
            out.append(row(a["id"], a["cls"], "rec:feeds", a["room"], "rec:Room"))
        # SSC shape: the IFC reference carries both properties. para:IFC_ID is the
        # slot for the real IFC GUID and is left empty until BIM supplies it;
        # ref:ifcName is the entity name, which is derivable.
        out.append(row(a["id"], a["cls"], "ref:hasExternalReference",
                       "<blanknode>", "ref:IFCReference",
                       [("o", "para:IFC_ID", ""), ("o", "ref:ifcName", bare)]))
        # Points, from the ledger's universal signatures for this family. Each is a
        # brick:hasPoint row plus its ref:TimeseriesReference row (empty id for now).
        # A ref:TimeseriesReference belongs to the POINT, never to the equipment -
        # every one of QF SSC's hangs off a brick:hasPoint object.
        out.extend(point_rows(a))

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

n_points = sum(1 for r in out if r[2] == "brick:hasPoint")
per_fam = {}
for a in assets:
    per_fam[a["kind"]] = per_fam.get(a["kind"], 0) + len(points_by_unit.get("QNL_" + a["tag"], []))
print("rows      :", len(out))
print("rooms     :", len(rooms), "levels:", levels_used)
print("assets    :", len(assets), {k: sum(1 for a in assets if a["kind"] == k) for k in CLASS})
print("points    :", n_points, "per family:", per_fam)
if orphan_units:
    print("orphans   :", len(orphan_units),
          "selected units absent from the asset register:", orphan_units)
if unit_overrides:
    from collections import Counter as _C
    print("units     :", len(unit_overrides),
          "class-driven unit overrides (IO list contradicted the class):",
          dict(_C(f"{c}: {was}->{now}" for _, c, was, now in unit_overrides)))
if duplicate_selected:
    print("dupes     :", len(duplicate_selected),
          "tags listed twice in the Selected sheet, emitted once:",
          duplicate_selected[:3], "...")
for n in sorted(set(notes)):
    print("note      :", n)
