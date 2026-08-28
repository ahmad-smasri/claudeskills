# Variable air volume boxes - six VAV schedules from the supplied drawing images.
# Each schedule is kept as its own source; where two drawings cover the same boxes
# the overlap is recorded in VAV_NOTES rather than merged away.
SRC_VAV = "MEP schedule drawing (image supplied in chat)"

VAV_COLS = ["unit_ref", "air_flow_l_s", "heating_kw", "qty", "model", "make", "page", "row_note"]

P_1F_A  = "SCHEDULE OF VAV UNITS (1F, S11/S15)"
P_1F_B  = "SCHEDULE OF VAV UNITS (1F, S15/S11 - second drawing)"
P_B15   = "SCHEDULE OF VAV UNITS (B, S10/S15 - heating capacity)"
P_B15M  = "SCHEDULE OF VAV UNITS (B, S10/S15 - model and make)"
P_B10   = "SCHEDULE OF VAV UNITS (B, S10/S13/S14)"
P_B11   = "SCHEDULE OF VAV UNITS (B, S11/S13 - TITUS)"

_G022 = ("Governs box 022. Confirmed by the user against the overlapping "
         "VAV/1F/S11/022 TO 24 row on the same schedule.")
_R022 = ("Covers boxes 023 and 024 only. Box 022 is governed by the standalone "
         "VAV/1F/S11/022 row on the same schedule, per the user's decision.")

VAV_ROWS = [
 # --- 1F schedule A: model and make, no heating capacity -------------------
 ["VAV/1F/S15/005 TO 009", 290, None, 5, "NBOQOB250", "HC BARCOL-AIR", P_1F_A, ""],
 ["VAV/1F/S11/001 TO 003", 220, None, 3, "NBOQOB200", "HC BARCOL-AIR", P_1F_A, ""],
 ["VAV/1F/S11/004 TO 005", 243, None, 2, "NBOQOB250", "HC BARCOL-AIR", P_1F_A, ""],
 ["VAV/1F/S11/022",        220, None, 1, "NBOQOB200", "HC BARCOL-AIR", P_1F_A, _G022],
 ["VAV/1F/S11/006 TO 013", 164, None, 8, "NBOQOB160", "HC BARCOL-AIR", P_1F_A, ""],
 ["VAV/1F/S11/014 TO 021", 219, None, 8, "NBOQOB200", "HC BARCOL-AIR", P_1F_A, ""],
 ["VAV/1F/S15/012",        120, None, 2, "NBOQOB200", "HC BARCOL-AIR", P_1F_A, ""],
 ["VAV/1F/S11/022 TO 24",  147, None, 3, "NBOQOB160", "HC BARCOL-AIR", P_1F_A, _R022],
 # --- 1F schedule B: second drawing over S15 and S11 -----------------------
 ["VAV/1F/S15/001 TO 002", 257, None, 2, "NBOQOB200", "HC BARCOL-AIR", P_1F_B, ""],
 ["VAV/1F/S15/003 TO 004", 257, None, 2, "NBOQOB200", "HC BARCOL-AIR", P_1F_B, ""],
 ["VAV/1F/S15/006 TO 011", 220, None, 6, None,        "HC BARCOL-AIR", P_1F_B, ""],
 ["VAV/1F/S15/012",        120, None, 1, None,        "HC BARCOL-AIR", P_1F_B, ""],
 ["VAV/1F/S15/013 TO 020", 174, None, 8, "NBOQOB200", "HC BARCOL-AIR", P_1F_B, ""],
 ["VAV/1F/S15/021 TO 024", 155, None, 4, None,        "HC BARCOL-AIR", P_1F_B, ""],
 ["VAV/1F/S15/025",         60, None, 1, "NBOQOB160", "HC BARCOL-AIR", P_1F_B, ""],
 ["VAV/1F/S15/026 TO 037", 138, None, 12, "NBOQOB160", "HC BARCOL-AIR", P_1F_B, ""],
 ["VAV/1F/S15/039 TO 040", 160, None, 2, "NBOQOB160", "HC BARCOL-AIR", P_1F_B, ""],
 ["VAV/1F/S15/014 TO 015", 240, None, 2, "NBOQOB250", "HC BARCOL-AIR", P_1F_B,
  "Overlaps VAV/1F/S15/013 TO 020 on the same schedule, which gives these boxes 174 l/s "
  "on NBOQOB200. Unresolved."],
 ["VAV/1F/S15/038",         60, None, 1, "NBOQOB160", "HC BARCOL-AIR", P_1F_B, ""],
 ["VAV/1F/S11/025",        147, None, 1, "NBOQOB160", "HC BARCOL-AIR", P_1F_B, ""],
 # --- basement S10/S15, heating capacity -----------------------------------
 ["VAV/B/S10/020 TO 023",  249, 0.75, 4, None, None, P_B15, ""],
 ["VAV/B/S15/001 TO 004",  261, 0.75, 4, None, None, P_B15,
  "The model-and-make drawing of the same schedule gives 251 l/s for these boxes. Unresolved."],
 ["VAV/B/S15/005 & 006",   240, 0.75, 2, None, None, P_B15, ""],
 ["VAV/B/S15/007",          78, 0.50, 1, None, None, P_B15, ""],
 ["VAV/B/S15/008",         227, 0.75, 1, None, None, P_B15, ""],
 ["VAV/B/S15/009",         143, 0.50, 1, None, None, P_B15, ""],
 ["VAV/B/S15/010",         179, 0.75, 1, None, None, P_B15, ""],
 ["VAV/B/S15/011 TO 012",  262, 0.75, 2, None, None, P_B15, ""],
 # --- basement S10/S15, model and make (same boxes, second drawing) --------
 ["VAV/B/S10/020 TO 023",  249, None, 4, "NBOQE03", "HC BARCOL-AIR", P_B15M, ""],
 ["VAV/B/S15/001 TO 004",  251, None, 4, "NBOQE03", "HC BARCOL-AIR", P_B15M,
  "The heating-capacity drawing of the same schedule gives 261 l/s for these boxes. Unresolved."],
 ["VAV/B/S15/005 TO 006",  240, None, 2, "NBOQE03", "HC BARCOL-AIR", P_B15M, ""],
 ["VAV/B/S15/007",          78, None, 1, None,      "HC BARCOL-AIR", P_B15M,
  "Model cell is blank on this schedule; every other row on it reads NBOQE03."],
 ["VAV/B/S15/008",         227, None, 1, "NBOQE03", "HC BARCOL-AIR", P_B15M, ""],
 ["VAV/B/S15/009",         143, None, 1, "NBOQE03", "HC BARCOL-AIR", P_B15M, ""],
 ["VAV/B/S15/010",         179, None, 1, "NBOQE03", "HC BARCOL-AIR", P_B15M, ""],
 ["VAV/B/S15/011 TO 012",  262, None, 2, "NBOQE03", "HC BARCOL-AIR", P_B15M, ""],
 # --- basement S10/S13/S14 -------------------------------------------------
 ["VAV/B/S14/001 TO 003",  230, 0.75, 3, None, None, P_B10, ""],
 ["VAV/B/S14/004 TO 006",  260, 0.75, 3, None, None, P_B10, ""],
 ["VAV/B/S14/007 & 008",   170, 0.75, 2, None, None, P_B10, ""],
 ["VAV/B/S14/009 TO 012",  260, 0.75, 2, None, None, P_B10, ""],
 ["VAV/B/S14/013 TO 016",  170, 0.75, 4, None, None, P_B10, ""],
 ["VAV/B/S14/017 TO 020",  128, 0.50, 4, None, None, P_B10, ""],
 ["VAV/B/S21",              80, 0.50, 1, None, None, P_B10, ""],
 ["VAV/B/S14/025 TO 028",  128, 0.50, 4, None, None, P_B10, ""],
 ["VAV/B/S14/029",         160, 0.50, 1, None, None, P_B10, ""],
 ["VAV/B/S14/022 TO 024",  136, 0.50, 3, None, None, P_B10, ""],
 ["VAV/B/S14/030 & 031",   136, 0.50, 2, None, None, P_B10, ""],
 ["VAV/B/S13/003 TO 005",  220, 0.50, 3, None, None, P_B10, ""],
 ["VAV/B/S13/007",          99, 0.50, 1, None, None, P_B10, ""],
 ["VAV/B/S13/008",          95, 0.50, 1, None, None, P_B10, ""],
 ["VAV/B/S10/001 & 008",   246, 0.75, 8, None, None, P_B10, ""],
 ["VAV/B/S10/009",         262, 0.75, 1, None, None, P_B10, ""],
 ["VAV/B/S10/010 & 011",   254, 0.75, 2, None, None, P_B10, ""],
 ["VAV/B/S10/012 TO 014",  224, 0.75, 3, None, None, P_B10, ""],
 ["VAV/B/S10/015",         300, 1.00, 1, None, None, P_B10, ""],
 ["VAV/B/S10/016 TO 018",  212, 0.75, 3, None, None, P_B10, ""],
 ["VAV/B/S10/019",         215, 0.75, 1, None, None, P_B10, ""],
 # --- basement S11/S13, TITUS USA -----------------------------------------
 ["VAV/B/S11/001 TO 020",  194, 0.75, 20, None, "TITUS USA", P_B11, ""],
 ["VAV/B/S11/021 TO 023",  260, 0.75, 3,  None, "TITUS USA", P_B11, ""],
 ["VAV/B/S11/024 TO 025",   86, 0.50, 2,  None, "TITUS USA", P_B11, ""],
 ["VAV/B/S11/026 TO 027",  100, 0.50, 2,  None, "TITUS USA", P_B11, ""],
 ["VAV/B/S11/028 TO 031",   90, 0.50, 4,  None, "TITUS USA", P_B11, ""],
 ["VAV/B/S11/032 TO 037",   80, 0.50, 6,  None, "TITUS USA", P_B11, ""],
 ["VAV/B/S11/038",         120, 0.50, 1,  None, "TITUS USA", P_B11, ""],
 ["VAV/B/S11/039 TO 041",   80, 0.50, 3,  None, "TITUS USA", P_B11, ""],
 ["VAV/B/S11/042",         120, 0.75, 1,  None, "TITUS USA", P_B11, ""],
 ["VAV/B/S11/043 TO 046",  224, 0.75, 4,  None, "TITUS USA", P_B11, ""],
 ["VAV/B/S13/001 TO 002",  155, 0.75, 2,  None, "TITUS USA", P_B11, ""],
]

VAV_NOTES = [
 ("Source reference", "All six VAV schedules were supplied as drawing images with the title block "
  "cropped out, so no drawing number, sheet or revision is recorded against any row."),
 ("Reference format", "The header reads VAV/FLOOR/AHU NO/BOX NO. Air flow is stated per VAV box, "
  "so a range row carries that flow on each of its boxes, not across them."),
 ("Duplicate box 022 - resolved", "VAV/1F/S11/022 appears twice on the 1F schedule. The user "
  "confirmed the standalone row governs: 220 l/s on NBOQOB200. The overlapping "
  "'VAV/1F/S11/022 TO 24' row is therefore read as covering boxes 023 and 024 only."),
 ("Rows excluded on instruction", "Five rows carrying box numbers far outside the range their "
  "schedule otherwise uses were dropped at the user's direction: VAV/1F/S15/395, VAV/1F/S11/088 "
  "and VAV/1F/S11/096-098 from the first 1F schedule, and VAV/1F/S11/088 TO 087 and "
  "VAV/1F/S15/096 TO 098 from the second."),
 ("Overlapping drawings - S10/S15", "Two drawings schedule the same basement boxes. One carries "
  "heating capacity, the other model and make, and they disagree on VAV/B/S15/001 TO 004 "
  "(261 l/s against 251 l/s). Both are recorded against their own drawing; neither was picked."),
 ("Overlapping rows - 1F/S15", "On the second 1F schedule, VAV/1F/S15/014 TO 015 (240 l/s, "
  "NBOQOB250) falls inside VAV/1F/S15/013 TO 020 (174 l/s, NBOQOB200). Both are recorded."),
 ("Box 012 disagreement", "VAV/1F/S15/012 is scheduled at 120 l/s on both 1F drawings, but the "
  "first states QTY 02 and the second QTY 01 for a single-box reference."),
 ("Missing boxes", "VAV/B/S14 runs 001-020 then 022-031, so box 021 is absent. On the second 1F "
  "schedule VAV/1F/S15 runs 001-004 then 006-011, so box 005 is absent there - though the first "
  "1F schedule does carry VAV/1F/S15/005 TO 009."),
 ("Reference shape", "VAV/B/S21 has no floor or box segment, unlike every other reference on its "
  "schedule. Kept as written - the tag is the BMS join key."),
 ("Schedule scope", "No single schedule carries every column. The 1F drawings give model and make "
  "but no heating capacity; the basement S10/S13/S14 and S11/S13 drawings give heating capacity "
  "but no model. Nothing was carried across between drawings."),
]

# Where a range must not be expanded literally. Keyed by (reference, schedule).
COVERS_OVERRIDE = {
 ("VAV/1F/S11/022 TO 24", P_1F_A): ["VAV/1F/S11/023", "VAV/1F/S11/024"],
}
