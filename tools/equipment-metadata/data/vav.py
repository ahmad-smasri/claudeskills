# Variable air volume boxes - three VAV schedules from the supplied drawing images.
SRC_VAV = "MEP schedule drawing (image supplied in chat)"

VAV_COLS = ["unit_ref", "air_flow_l_s", "heating_kw", "qty", "model", "make", "page"]

P_1F  = "SCHEDULE OF VAV UNITS (1F, S11/S15)"
P_B15 = "SCHEDULE OF VAV UNITS (B, S10/S15)"
P_B10 = "SCHEDULE OF VAV UNITS (B, S10/S13/S14)"

VAV_ROWS = [
 # 1F schedule - model and make, no heating capacity column
 ["VAV/1F/S15/005 TO 009", 290, None, 5, "NBOQOB250", "HC BARCOL-AIR", P_1F],
 ["VAV/1F/S11/001 TO 003", 220, None, 3, "NBOQOB200", "HC BARCOL-AIR", P_1F],
 ["VAV/1F/S11/004 TO 005", 243, None, 2, "NBOQOB250", "HC BARCOL-AIR", P_1F],
 ["VAV/1F/S11/022",        220, None, 1, "NBOQOB200", "HC BARCOL-AIR", P_1F],
 ["VAV/1F/S11/006 TO 013", 164, None, 8, "NBOQOB160", "HC BARCOL-AIR", P_1F],
 ["VAV/1F/S11/014 TO 021", 219, None, 8, "NBOQOB200", "HC BARCOL-AIR", P_1F],
 ["VAV/1F/S15/012",        120, None, 2, "NBOQOB200", "HC BARCOL-AIR", P_1F],
 ["VAV/1F/S11/022 TO 24",  147, None, 3, "NBOQOB160", "HC BARCOL-AIR", P_1F],
 ["VAV/1F/S15/395",        120, None, 1, "NBOQOB200", "HC BARCOL-AIR", P_1F],
 ["VAV/1F/S11/088",        120, None, 1, "NBOQOB200", "HC BARCOL-AIR", P_1F],
 ["VAV/1F/S11/096-098",    120, None, 1, "NBOQOB200", "HC BARCOL-AIR", P_1F],
 # basement S10/S15 schedule - heating capacity, no model or make
 ["VAV/B/S10/020 TO 023",  249, 0.75, 4, None, None, P_B15],
 ["VAV/B/S15/001 TO 004",  261, 0.75, 4, None, None, P_B15],
 ["VAV/B/S15/005 & 006",   240, 0.75, 2, None, None, P_B15],
 ["VAV/B/S15/007",          78, 0.50, 1, None, None, P_B15],
 ["VAV/B/S15/008",         227, 0.75, 1, None, None, P_B15],
 ["VAV/B/S15/009",         143, 0.50, 1, None, None, P_B15],
 ["VAV/B/S15/010",         179, 0.75, 1, None, None, P_B15],
 ["VAV/B/S15/011 TO 012",  262, 0.75, 2, None, None, P_B15],
 # basement S10/S13/S14 schedule - heating capacity, no model or make
 ["VAV/B/S14/001 TO 003",  230, 0.75, 3, None, None, P_B10],
 ["VAV/B/S14/004 TO 006",  260, 0.75, 3, None, None, P_B10],
 ["VAV/B/S14/007 & 008",   170, 0.75, 2, None, None, P_B10],
 ["VAV/B/S14/009 TO 012",  260, 0.75, 2, None, None, P_B10],
 ["VAV/B/S14/013 TO 016",  170, 0.75, 4, None, None, P_B10],
 ["VAV/B/S14/017 TO 020",  128, 0.50, 4, None, None, P_B10],
 ["VAV/B/S21",              80, 0.50, 1, None, None, P_B10],
 ["VAV/B/S14/025 TO 028",  128, 0.50, 4, None, None, P_B10],
 ["VAV/B/S14/029",         160, 0.50, 1, None, None, P_B10],
 ["VAV/B/S14/022 TO 024",  136, 0.50, 3, None, None, P_B10],
 ["VAV/B/S14/030 & 031",   136, 0.50, 2, None, None, P_B10],
 ["VAV/B/S13/003 TO 005",  220, 0.50, 3, None, None, P_B10],
 ["VAV/B/S13/007",          99, 0.50, 1, None, None, P_B10],
 ["VAV/B/S13/008",          95, 0.50, 1, None, None, P_B10],
 ["VAV/B/S10/001 & 008",   246, 0.75, 8, None, None, P_B10],
 ["VAV/B/S10/009",         262, 0.75, 1, None, None, P_B10],
 ["VAV/B/S10/010 & 011",   254, 0.75, 2, None, None, P_B10],
 ["VAV/B/S10/012 TO 014",  224, 0.75, 3, None, None, P_B10],
 ["VAV/B/S10/015",         300, 1.00, 1, None, None, P_B10],
 ["VAV/B/S10/016 TO 018",  212, 0.75, 3, None, None, P_B10],
 ["VAV/B/S10/019",         215, 0.75, 1, None, None, P_B10],
]

VAV_NOTES = [
 ("Source reference", "All three VAV schedules were supplied as drawing images with the title "
  "block cropped out, so no drawing number, sheet or revision is recorded."),
 ("Reference format", "The header reads VAV/FLOOR/AHU NO/BOX NO. Air flow is stated per VAV box, "
  "not per range, so a range row is that flow on each of its boxes."),
 ("Duplicate box", "VAV/1F/S11/022 appears twice on the 1F schedule with different data: once "
  "alone at 220 l/s on model NBOQOB200, and once inside 'VAV/1F/S11/022 TO 24' at 147 l/s on "
  "model NBOQOB160. Both rows are recorded; the schedule does not say which governs."),
 ("Out-of-range box numbers", "On the 1F schedule VAV/1F/S15/395, VAV/1F/S11/088 and "
  "VAV/1F/S11/096-098 carry box numbers far outside the 001-024 range used by every other row. "
  "Recorded as printed - they may be typos, or boxes numbered on another system."),
 ("Missing box", "VAV/B/S14 runs 001-020, then 022-031. Box 021 is not on the schedule."),
 ("Reference shape", "VAV/B/S21 has no floor or box segment, unlike every other reference on the "
  "same schedule. Kept as written."),
 ("Schedule scope", "The 1F schedule gives model and make but no heating capacity. The two "
  "basement schedules give heating capacity but no model or make. Nothing was carried across."),
]
