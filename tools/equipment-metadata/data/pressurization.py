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
