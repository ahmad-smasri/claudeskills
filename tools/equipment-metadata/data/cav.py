# Constant air volume boxes - three CAV schedules from the supplied drawing images.
# Refs are written as the schedules write them, ranges included; the build expands a
# range only when it parses cleanly and its box count matches the stated QTY.
SRC_CAV = "MEP schedule drawing (image supplied in chat)"

CAV_COLS = ["unit_ref", "air_flow_l_s", "qty", "model", "make", "page"]

P_1F   = "SCHEDULE OF CAV UNITS (1F, S11)"
P_B14  = "SCHEDULE OF CAV (B, S14/03-05)"
P_B13  = "SCHEDULE OF CAV UNITS (B, S13-S15)"

CAV_ROWS = [
 # 1F schedule - carries model and make
 ["CAV/1F/S11/001",        300, 1, "NBOQOB250", "HC BARCOL-AIR", P_1F],
 ["CAV/1F/S11/002",        175, 1, "NBOQOB200", "HC BARCOL-AIR", P_1F],
 ["CAV/1F/S11/004",        190, 1, "NBOQOB200", "HC BARCOL-AIR", P_1F],
 ["CAV/1F/S11/006 TO 007", 165, 2, "NBOQOB160", "HC BARCOL-AIR", P_1F],
 ["CAV/1F/S11/008 TO 009", 200, 2, "NBOQOB200", "HC BARCOL-AIR", P_1F],
 # basement S14 schedule - carries model and make
 ["CAV/B/S14/03",          305, 1, "NBOQOB250", "HC BARCOL-AIR", P_B14],
 ["CAV/B/S14/04",          305, 1, "NBOQOB250", "HC BARCOL-AIR", P_B14],
 ["CAV/B/S14/05",          305, 1, "NBOQOB250", "HC BARCOL-AIR", P_B14],
 # basement S13-S15 schedule - air flow and quantity only
 ["CAV/B/S13/004",         200, 1, None, None, P_B13],
 ["CAV/B/S13/005",         200, 1, None, None, P_B13],
 ["CAV/B/S14/001",         125, 1, None, None, P_B13],
 ["CAV/B/S14/002",         250, 1, None, None, P_B13],
 ["CAV/B/S15/001",         125, 1, None, None, P_B13],
 ["CAV/B/S15/002",         125, 1, None, None, P_B13],
 ["CAV/B/S15/003",         125, 1, None, None, P_B13],
]

CAV_NOTES = [
 ("Source reference", "All three CAV schedules were supplied as drawing images with the title "
  "block cropped out, so no drawing number, sheet or revision is recorded."),
 ("Reference format", "The header reads CAV/FLOOR/AHU NO/BOX NO, so CAV/1F/S11/001 is floor 1F, "
  "AHU S11, box 001."),
 ("Box number width", "The 1F and S13-S15 schedules use three-digit box numbers (001); the "
  "CAV/B/S14 schedule uses two digits (03, 04, 05). Both kept as written - the tag is the BMS "
  "join key."),
 ("Numbering gap", "CAV/1F/S11 runs 001, 002, 004, 006-007, 008-009. Box 003 and box 005 are not "
  "on the schedule. Either they are scheduled elsewhere or the list is partial."),
 ("Schedule scope", "The S13-S15 schedule states no model and no make; those columns do not exist "
  "on it. Left out rather than copied across from the other schedules."),
]
