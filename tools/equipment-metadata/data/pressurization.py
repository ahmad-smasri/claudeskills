# Pressurization unit - SCHEDULE OF PRESSURIZATION UNIT
# Same drawing image as the heat exchanger and pump schedules.
SRC_PU = "MEP schedule drawing (image supplied in chat)"
PAGE_PU = "SCHEDULE OF PRESSURIZATION UNIT"

PU_COLS = ["unit_ref", "model", "location", "system_volume", "make", "qty"]

PU_ROWS = [
 ["PU/B/01", "3750 2 EM-S", "PLANT ROOM-4",
  "WITH 10BAR PRESSURE & 1000L TANK", "ARMSTRONG", 1],
]

PU_NOTES = [
 ("Source reference", "The supplied image crops the drawing title block, so the drawing number, "
  "sheet number and revision are not recorded. Ask for the sheet reference before handover."),
 ("Column mismatch", "The column is headed SYSTEM VOLUME but holds the text 'WITH 10BAR PRESSURE "
  "& 1000L TANK' - a pressure and a tank size, not a system volume. Recorded verbatim; the "
  "system volume the header asks for is not stated anywhere on the schedule."),
]


# ---------------------------------------------------------------------------
# SYSTEM DETAILS Table 3.2 splits PU/B/01 into two components and names the
# expansion tank the drawing schedule only alluded to.
SRC_SYS = "SYSTEM DETAILS (image supplied in chat)"
PAGE_SYS = "Table 3.2 - Pressurisation Unit Equipment Schedule"

PU_ALT_TAG = "PRO1"

# (component, property, value, unit, note)
PU_COMPONENTS = [
 ("Expansion tank", "Make", "Armstrong", "", ""),
 ("Expansion tank", "Model", "Reflex DE10", "", ""),
 ("Expansion tank", "Capacity", 1000, "litre", ""),
 ("Expansion tank", "Quantity", 1, "n", ""),
 ("Pressurisation unit", "Make", "Armstrong", "", ""),
 ("Pressurisation unit", "Model", "3750 2 EM-S", "", ""),
 ("Pressurisation unit", "Capacity", 10, "bar", ""),
 ("Pressurisation unit", "Quantity", 1, "n", ""),
]

PU_EXTRA_NOTES = [
 ("Column mismatch resolved", "The drawing schedule's SYSTEM VOLUME cell reads 'WITH 10BAR "
  "PRESSURE & 1000L TANK'. SYSTEM DETAILS Table 3.2 explains it: the assembly is an Armstrong "
  "3750 2 EM-S pressurisation unit rated 10 bar plus a Reflex DE10 expansion tank of 1000 litre. "
  "Those are now recorded as two components. The system volume the column header asks for is "
  "still not stated on either document."),
 ("Alternate tag", "SYSTEM DETAILS tags the assembly PRO1 where the drawing schedule tags it "
  "PU/B/01. The drawing form is used here because it matches the rest of the workbook; PRO1 is "
  "recorded as an alternate reference. Confirm which the BMS uses."),
]
