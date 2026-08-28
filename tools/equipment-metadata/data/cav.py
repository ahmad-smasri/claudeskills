# Constant air volume boxes - six CAV schedules from the supplied drawing images.
SRC_CAV = "MEP schedule drawing (image supplied in chat)"

CAV_COLS = ["unit_ref", "air_flow_l_s", "qty", "model", "make", "page", "row_note"]

P_1F_A = "SCHEDULE OF CAV UNITS (1F, S11)"
P_1F_B = "SCHEDULE OF CAV UNITS (1F, S15/S11)"
P_B14  = "SCHEDULE OF CAV (B, S14/03-05)"
P_B13  = "SCHEDULE OF CAV UNITS (B, S13-S15)"
P_B12  = "SCHEDULE OF CAV UNITS (B, S12/S13)"
P_B12B = "SCHEDULE OF CAV (B, S12/002-003)"

CAV_ROWS = [
 # --- 1F schedule A --------------------------------------------------------
 ["CAV/1F/S11/001",        300, 1, "NBOQOB250", "HC BARCOL-AIR", P_1F_A, ""],
 ["CAV/1F/S11/002",        175, 1, "NBOQOB200", "HC BARCOL-AIR", P_1F_A, ""],
 ["CAV/1F/S11/004",        190, 1, "NBOQOB200", "HC BARCOL-AIR", P_1F_A, ""],
 ["CAV/1F/S11/006 TO 007", 165, 2, "NBOQOB160", "HC BARCOL-AIR", P_1F_A, ""],
 ["CAV/1F/S11/008 TO 009", 200, 2, "NBOQOB200", "HC BARCOL-AIR", P_1F_A, ""],
 # --- 1F schedule B --------------------------------------------------------
 ["CAV/1F/S15/002",        151, 1, "NBOQOB160", "HC BARCOL-AIR", P_1F_B, ""],
 ["CAV/1F/S15/004",        225, 1, "NBOQOB160", "HC BARCOL-AIR", P_1F_B, ""],
 ["CAV/1F/S15/005",        185, 1, "NBOQOB200", "HC BARCOL-AIR", P_1F_B, ""],
 ["CAV/1F/S15/006",        240, 1, "NBOQOB200", "HC BARCOL-AIR", P_1F_B, ""],
 ["CAV/1F/S15/007",        315, 1, "NBOQOB200", "HC BARCOL-AIR", P_1F_B, ""],
 ["CAV/1F/S11/005",        190, 1, "NBOQOB200", "HC BARCOL-AIR", P_1F_B,
  "Box 005 is absent from the other 1F schedule, which jumps 004 to 006."],
 # --- basement S14/03-05 ---------------------------------------------------
 ["CAV/B/S14/03",          305, 1, "NBOQOB250", "HC BARCOL-AIR", P_B14, ""],
 ["CAV/B/S14/04",          305, 1, "NBOQOB250", "HC BARCOL-AIR", P_B14, ""],
 ["CAV/B/S14/05",          305, 1, "NBOQOB250", "HC BARCOL-AIR", P_B14, ""],
 # --- basement S13-S15 -----------------------------------------------------
 ["CAV/B/S13/004",         200, 1, None, None, P_B13, ""],
 ["CAV/B/S13/005",         200, 1, None, None, P_B13, ""],
 ["CAV/B/S14/001",         125, 1, None, None, P_B13, ""],
 ["CAV/B/S14/002",         250, 1, None, None, P_B13, ""],
 ["CAV/B/S15/001",         125, 1, None, None, P_B13, ""],
 ["CAV/B/S15/002",         125, 1, None, None, P_B13, ""],
 ["CAV/B/S15/003",         125, 1, None, None, P_B13, ""],
 # --- basement S12/S13 -----------------------------------------------------
 ["CAV/B/S12/001",         105, 1, None, None, P_B12, ""],
 ["CAV/B/S13/001 TO 003",  200, 3, None, None, P_B12, ""],
 ["CAV/B/S13/006 TO 008",  155, 3, None, None, P_B12, ""],
 ["CAV/B/S13/012",          50, 1, None, None, P_B12, ""],
 ["CAV/B/S13/013",          50, 1, None, None, P_B12, ""],
 ["CAV/B/S13/014",          70, 1, None, None, P_B12, ""],
 ["CAV/B/S13/015",         150, 1, None, None, P_B12, ""],
 ["CAV/B/S13/016",         285, 1, None, None, P_B12, ""],
 ["CAV/B/S13/017",         145, 1, None, None, P_B12, ""],
 ["CAV/B/S13/018",         145, 1, None, None, P_B12, ""],
 ["CAV/B/S13/019",         190, 1, None, None, P_B12, ""],
 ["CAV/B/S13/020",         150, 1, None, None, P_B12, ""],
 ["CAV/B/S13/021",          85, 1, None, None, P_B12, ""],
 # --- basement S12/002-003 -------------------------------------------------
 ["CAV/B/S12/002",         292, 1, "NBOQOB250", "HC BARCOL-AIR", P_B12B, ""],
 ["CAV/B/S12/003",         292, 1, "NBOQOB250", "HC BARCOL-AIR", P_B12B, ""],
]

CAV_NOTES = [
 ("Source reference", "All six CAV schedules were supplied as drawing images with the title block "
  "cropped out, so no drawing number, sheet or revision is recorded against any row."),
 ("Reference format", "The header reads CAV/FLOOR/AHU NO/BOX NO, so CAV/1F/S11/001 is floor 1F, "
  "AHU S11, box 001. Air flow is stated per box."),
 ("Box number width", "Most schedules use three-digit box numbers (001); the CAV/B/S14 schedule "
  "uses two digits (03, 04, 05). Both kept as written - the tag is the BMS join key."),
 ("Numbering gaps", "CAV/1F/S11 runs 001, 002, 004, 005, 006-007, 008-009 once both 1F drawings "
  "are read together - box 003 is on neither. CAV/B/S13 runs 001-008 then 012-021, so boxes "
  "009, 010 and 011 are absent."),
 ("Schedule scope", "The basement S13-S15 and S12/S13 schedules state no model and no make; those "
  "columns do not exist on them. Nothing was carried across from the schedules that do."),
]
