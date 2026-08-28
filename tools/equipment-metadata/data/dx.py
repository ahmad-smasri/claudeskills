# DX split systems - read off the schematic riser supplied as an image in chat.
#
# The schematic is a system diagram, not a nameplate schedule. What it states is the
# room each group of indoor units serves, that room's design condition, and one
# cooling figure printed on the room box. That figure is a ROOM LOAD: where a room is
# served by two or three units the diagram does not split it per unit, so it must not
# be read as a per-unit capacity.
SRC_DX = "DX split system schematic (image supplied in chat)"
PAGE_DX = "DX SPLIT SYSTEM SCHEMATIC"

DX_COLS = ["indoor_ref", "standby", "room", "level", "room_temp_c", "room_rh_pct",
           "room_cooling_kw", "cooling_basis", "outdoor_ref"]

# room, level, Tr, RH, cooling kW, basis, and the indoor units serving it
_GROUPS = [
 ("MV ROOM",                                  "Lower level", 35, 50, 2.3,  "SENSIBLE",
  [("DX/B/01", False), ("DX/B/02", True)]),
 ("HV ROOM",                                  "Lower level", 22, 50, 2.30, "SENSIBLE",
  [("DX/B/05", False), ("DX/B/06", False)]),
 ("TRANSFORMER ROOM",                         "Lower level", 35, 50, 35,   "SENSIBLE",
  [("DX/B/03", False), ("DX/B/04", False), ("DX/B/14", True)]),
 ("MV ROOM 3",                                "Lower level", 22, 50, 100,  "SENSIBLE",
  [("DX/B/07", False), ("DX/B/16", True)]),
 ("UPS / EMERGENCY LIGHTING BATTERY ROOM",    "Lower level", 25, 50, 44,   "SENSIBLE",
  [("DX/B/08", False), ("DX/B/09", True)]),
 ("SECURITY EQUIPMENT ROOM",                  "Lower level", 22, 50, 10,   "SENSIBLE",
  [("DX/B/10", False)]),
 ("IRRIGATION PUMP ROOM",                     "Lower level", 35, 50, 3.5,  "SENSIBLE",
  [("DX/B/11", False)]),
 ("SECURITY STORES, SECURITY UPS",            "Lower level", 25, 50, 4,    "SENSIBLE",
  [("DX/B/12", False)]),
 ("TRASH CHAMBER",                            "Lower level", 20, 50, 12,   "SENSIBLE",
  [("DX/B/13", False), ("DX/B/15", False)]),
 ("REFRIGERATED STORAGE (KITCHEN BACK OF HOUSE)", "Lower level", 22, 50, 3.75, "SENSIBLE",
  [("DX/B/17", False), ("DX/B/18", False), ("DX/B/19", True)]),
 ("PLC 7 / IDF LOWER LEVEL ZONE 5",           "Lower level", 22, 50, 4.4,  "not stated",
  [("DX/B/20", False)]),
 ("PLC 8 / IDF ROOF PLANT",                   "Roof level",  35, 50, 6.0,  "not stated",
  [("DX/RP/21", False)]),
]

DX_ROWS = []
for room, level, tr, rh, kw, basis, units in _GROUPS:
    for ref, standby in units:
        od = "DX/OD/" + ref.rsplit("/", 1)[1]
        DX_ROWS.append([ref, standby, room, level, tr, rh, kw, basis, od])

# Outdoor units the schematic marks (ST.BY) at the condenser row.
OD_STANDBY = {"DX/OD/02", "DX/OD/05", "DX/OD/09", "DX/OD/14", "DX/OD/16", "DX/OD/19"}

DX_NOTES = [
 ("Source reference", "Read off a schematic riser supplied as an image, not from a schedule. No "
  "drawing number, sheet or revision is recorded. Ask for the sheet reference before handover."),
 ("Cooling figure is a room load", "Each cooling figure is printed on the room box, not on an "
  "indoor unit. Where a room is served by two or three units the schematic does not say how the "
  "load divides, so the figure is recorded against every unit serving that room as a room load. "
  "Do not write it as a per-unit brick:coolingCapacity without the equipment schedule."),
 ("Indoor to outdoor pairing", "The schematic numbers condensers to match their indoor units, so "
  "DX/B/nn is paired with DX/OD/nn here. That is the numbering convention, not a statement on the "
  "drawing, and the pipe routing crosses in places. Confirm against the pipework layout plan."),
 ("Standby marking disagreement", "DX/OD/05 is marked (ST.BY) at the condenser row, but DX/B/05 "
  "carries no standby marking at the indoor row. One of the two is wrong; the drawing does not "
  "say which. Recorded as printed on each side."),
 ("Room design condition", "Tr is the room design temperature and the paired figure is design "
  "relative humidity - 50% on every room on this schematic."),
 ("Drainage", "The trash chamber units carry the note 'TO NEAREST DRAIN, AS REFER TO PIPE WORK "
  "LAYOUT PLAN (TYPICAL)'. No condensate route is scheduled on this drawing."),
 ("Scope", "The schematic states no model, no make, no electrical data and no air flow for any "
  "DX unit. Those were not inferred - the equipment schedule is still needed."),
]
