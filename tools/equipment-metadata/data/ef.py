# Exhaust fans - transcribed from the supplied schedule spreadsheet.
# Source: Book1.xlsx, Sheet1. The Page column carries the spreadsheet row.
#
# Columns as the source writes them: Equip. | Model | Manufacturer | Air Flow.
# The sheet gives nothing else - no location, no motor rating, no static pressure.
SRC_EF = "Book1.xlsx"

EF_COLS = ["unit_ref", "row", "model", "manufacturer", "air_flow"]

EF_ROWS = [
 ['EF/2/01', 2, 'S6-315', 'NUAIRE', '200 l/s'],
 ['KEF_B020', 3, None, None, '300 L/S'],
 ['TEF_B01A', 4, 'AXT80P-413A', 'NUAIRE', '1538 L/S'],
 ['TEF_B01B', 5, 'AXT80P-413A', 'NUAIRE', '1538 L/S'],
 ['TEF_B02A', 6, 'AXT71P-413A', 'NUAIRE', '970 L/S'],
 ['TEF_B02B', 7, 'AXT71P-413A', 'NUAIRE', '970 L/S'],
 ['TEF_B03A', 8, 'AXT35M-211A', 'NUAIRE', '400 L/S'],
 ['TEF_B03B', 9, 'AXT35M-211A', 'NUAIRE', '400 L/S'],
 ['EF/RP/1', 10, 'AX71P-453A1', 'NUAIRE', '5000 L/S'],
 ['EF/RP/2', 11, 'AX71P-453A1', 'NUAIRE', '5000 L/S'],
 ['EF/RP/3', 12, 'AX71P-453A1', 'NUAIRE', '5000 L/S'],
 ['TEF_101C', 13, 'S - Squrbo', 'NUAIRE', None],
 ['TEF_102C', 14, 'S - Squrbo', 'NUAIRE', None],
 ['EF/BV/01', 15, 'AX719-41AKZ+0WE', 'NUAIRE', '330L/S'],
 ['EF/BV/02', 16, 'AX719-41AKZ+0WE', 'NUAIRE', '330L/S'],
 ['KEF_B019', 17, None, None, '1800 L/S'],
 ['KEF_101', 18, None, None, '1500 L/S'],
 ['EF/RP/4', 19, 'AX125CX-463A7-45', 'NUAIRE', '35000 L/S'],
 ['EF/RP/5', 20, 'AX125CX-463A7-45', 'NUAIRE', '35000 L/S'],
 ['EF/RP/6', 21, 'AX125CX-463A7-45', 'NUAIRE', '35000 L/S'],
 ['EF/RP/7', 22, 'AX125CX-463A7-45', 'NUAIRE', '35000 L/S'],
 ['EF/RP/8', 23, 'AX125CX-463A7-45', 'NUAIRE', '35000 L/S'],
 ['EF/RP/9', 24, 'AX125CX-463A7-45', 'NUAIRE', '35000 L/S'],
 ['EF/RP/10', 25, 'AX125CX-463A7-45', 'NUAIRE', '35000 L/S'],
 ['EF/RP/11', 26, 'AX125CX-463A7-45', 'NUAIRE', '35000 L/S'],
 ['EF/RP/12', 27, 'AX125CX-463A7-45', 'NUAIRE', '35000 L/S'],
 ['EF/B/4', 28, 'SQFA41-1', 'NUAIRE', '200 L/S'],
 ['EF/B/5', 29, 'NALAF-150', 'NUAIRE', '70 L/S'],
 ['EF/B/6', 30, 'AX63F-413AFG1', 'NUAIRE', '250 L/S'],
 ['EF/B/7', 31, 'AX100CX-4H3A7I', 'NUAIRE', '11000 L/S'],
 ['EF/B/8', 32, 'AX100CX-4H3A7I', 'NUAIRE', '11000 L/S'],
 ['EF/B/9', 33, 'AX80P-423A', 'NUAIRE', '2800 L/S'],
 ['EF/B/10', 34, 'AX40I-411A', 'NUAIRE', '475 L/S'],
 ['EF/B/11', 35, 'EZPLATES 315-41', 'NUAIRE', '90 L/S'],
 ['EF/B/12', 36, 'S6-315', 'NUAIRE', '200 L/S'],
 ['EF/B/13', 37, 'AX63F-411A', 'NUAIRE', '810L/S'],
 ['EF/B/14', 38, 'AX63D-411A', 'NUAIRE', '260 L/S'],
 ['EF/B/15', 39, 'Cmveco 315/315', 'COLASIT', None],
 ['EF/B/16', 40, 'Cmveco 125/125', 'COLASIT', None],]

# Identifier audit, per the repo rule to find the majority shape and report every
# departure rather than silently normalising a BMS join key.
EF_NOTES = [
 ("Identifier shapes", "Two families are in use and neither is a typo: 28 tags are slash "
  "separated (EF/B/nn, EF/RP/n, EF/BV/nn, EF/2/01) and 11 are underscore separated "
  "(TEF_B01A, KEF_B020, TEF_101C, KEF_101). Tags are the BMS join key, so both were kept "
  "exactly as written. Confirm which shape the BMS actually uses before the ontology is built."),
 ("Whitespace", "'EF/2/01 ' carries a trailing space in the source. Stripped, per the rule that "
  "whitespace is the only thing changed on a supplied identifier."),
 ("Numbering gap", "EF/B numbering runs 4 to 16; there is no EF/B/1, EF/B/2 or EF/B/3 in the "
  "sheet. Either they are scheduled elsewhere or the list is partial - worth confirming."),
 ("Air flow spelling", "The source writes the unit as both 'l/s' and 'L/S', and sometimes with no "
  "space ('330L/S'). All are litres per second; the value was parsed and the unit normalised."),
 ("Missing data", "KEF_B020, KEF_B019 and KEF_101 have no model and no manufacturer. TEF_101C, "
  "TEF_102C, EF/B/15 and EF/B/16 have no air flow. Those properties are left out rather than "
  "filled with a typical value."),
]
