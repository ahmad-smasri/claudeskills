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

---

# RDC: one unit, several register rows

`match_terminals.py` and `build_assembly_review.py` group the RDC register's
rows back into the physical units the BMS screens draw.

```
python3 match_terminals.py          # the matching, and the conflicts it exposes
python3 build_assembly_review.py    # RDC_assembly_review.xlsx
```

The RDC register lists one air-terminal assembly across several rows: a VAV box
is `VAV4110_EV4111` - the box and its valve - and the air terminal it feeds is a
row of its own, `AT-4110`. The screens draw the assembly as one widget labelled
the way the register writes the box, `NB-VAV4110-EV4111`. **No widget is ever
labelled `AT-`**, which is why 644 AT rows came back with no reading: they have
no widget to click, not no service.

This is RDC only. HQ, QNL and SSC have no AT rows at all.

## What ties the rows together, and what must not

The unit number, within one building, one level and one zone, across the
air-terminal families only - `AT`, `EV`, `VEV`, `CEV`, `FEV`, `VAV`, `CAV`,
`EAV`. Four things that grouping has to get right, each found by checking the
groups it produced rather than by reasoning about it first:

- **FCU and AHU are excluded.** `FCU1004` and `VAV1004` share a number and are
  different units - both are drawn as their own widget on South GF-6.
- **`L0` and `GF` are the same floor** in the south building, which registers
  terminals on one and boxes on the other. Every other level is kept apart, or
  `NB_1F_AT-5930` merges with `NB_2F_AT-5930`.
- **The trailing letter is part of the number.** `VEV-5192a` and `VEV-5192b` are
  two units; a regex that only accepted an upper-case suffix read both as 5192.
- **The zone segment counts.** `SB_L0_A1.2_AT-2001` and `SB_L0_A1.3_AT-2001` are
  two terminals in two zones.

Groups are the connected components of the shares-a-number relation, not each
row's own neighbours. Sharing a number is not transitive: `AT-1002` sees only
the box `VAV1003_VEV1002`, while that box sees four rows, so taking each row's
neighbours listed ten rows twice under two different groups.

## What the grouping is worth

**It corroborates itself.** On most AT rows the register's own column D already
equals the room the screen gives the box - `AT-4110` says `Conference Room
N-0227` and so does the reading for `VAV4110_EV4111`. The grouping was derived
from the tag numbers alone, so the room names agreeing is independent evidence
that it is right.

**49 terminal rows inherit a reading** they could not have had otherwise.

**28 assemblies contradict themselves** about the room - 14 on the room number
and 14 on wording alone (`Conf` against `Conference`, and a `Director Ofice`
typo). Those are register defects, found without reference to any screen.

A box feeding several terminals is not a contradiction: `AT-7120` runs to nine
of them, `-N1` to `-N9`, in nine different rooms. Those rows keep their own room
and are never given the box's.
