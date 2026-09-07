# One room name per asset, written back into the register

`update_rooms.py` writes the agreed room into column D of the
`Controllable Asset Registry` sheet, for all four building sections.

```
python3 update_rooms.py --dry-run   # say what would change, write nothing
python3 update_rooms.py             # write the workbook and the crosswalk
```

Column D is headed `ROOM NAME AS PER DRAWINGS`, and for three of the four
buildings the drawings were not the last word: the room was settled against the
BMS floor-plan screens and the delivered ontology. This puts that answer back
into the register, so an asset has one room name rather than four columns
disagreeing about it.

## Where each section's name comes from

| Section | Source |
|---|---|
| HQ, QNL, SSC | `Room_Names_4.xlsx`, column M `rdfs:label_en` - the name chosen after validating column D against the BMS screens and the existing ontology. Column N on that sheet records which source won, row by row. |
| RDC | `RDC_reviewed.xlsx`, column J, on the rows filled green - the 32 the client kept after reviewing the 215 this project flagged. |

Two rules follow from that and are worth stating, because both were nearly got
wrong:

**An empty `rdfs:label_en` means leave the row alone.** 90 rows across the three
buildings have one - no source settled the room - and they keep the name they
have rather than being blanked.

**On RDC, green is the whole instruction.** The client cleared column J on the
183 readings they rejected and corrected it on 11 more, so a column J value on a
row that is not green is not an instruction to change anything.

## Tags are not unique across buildings

`AHUB_0001` is a room in HQ and a different room in SSC; so is `FCU0004`. The
join is scoped to each section's row range rather than done on the tag alone,
or half the HQ names would have been written from SSC's answers.

## The workbook is edited as XML, not through openpyxl

It carries cell comments, a web-extension task pane, a calculation chain and
spilling formulas, and a round trip through openpyxl drops them. `update_rooms`
rewrites `xl/worksheets/sheet6.xml` inside the zip and copies every other part
through untouched - after a run, 35 of the 36 parts are byte-identical to the
original and only column D differs.

Two things about that sheet caught the first attempt out. Its cells do not write
their attributes in a fixed order - both `<c r="D5" s="45">` and
`<c s="45" r="D5">` appear - so the cell reference is read out of the attributes
rather than matched by position. And the new value is written as an inline
string rather than a shared one, so nothing is added to `sharedStrings.xml` and
no other cell that happened to share the old string is affected.

## What comes out

`room_name_changes.csv` - every change, one row each, with the source it came
from and what kind of change it is:

| Kind | Rows |
|---|---|
| same room, name reordered | 1,015 |
| same room, level prefix differs | 216 |
| **DIFFERENT ROOM** | **103** |
| room number added | 57 |
| no room number either side | 55 |

The bulk is the register's `NAME B.013` becoming the ontology's
`B.013 NAME`, and `B.001` becoming `B1.001`. The 103 in bold are the ones that
change which room an asset is in - those are the rows worth reading.

The `kind of change` column is a reading aid derived from the two strings, not
something the written value depends on, and it is coarse in one place: HQ's
`CORRIDOR BRIDGE 3.63` -> `3.630 CORRIDOR BRIDGE` is counted as a different room
because 63 and 630 are different numbers, when it is the same room with the
reference written out in full.
