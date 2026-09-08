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

---

# Which RDC rows are units, and which are parts of one

`classify_parts.py` decides, against the historian.

```
python3 classify_parts.py   # writes rdc_unit_or_part.csv
```

The test is the historian, not the tag family. A row is a controllable asset if
the historian carries an object for it - that is what controllable means, and
what the Controllable Asset Registry is for. A row with no historian object has
no points, cannot be commanded and cannot be read.

`RDC_Historian_IO_list_CP2.xlsx` holds 30,197 tags over 5,993 objects, and
**not one of them is an AT**. The historian names the whole assembly the way the
register writes the box - `RDC_NB_GF_VAV4110_EV4111`, ten points - and the
register's `AT-4110` has no object at all.

## The result, air handling units aside

| | rows |
|---|---|
| unit - its own historian object | 992 |
| part - the historian carries the whole assembly | 683 |
| nothing in the historian knows the number | 47 |

By family, and this is the point: **the rule cannot be a family rule.**

| family | unit | part | unknown |
|---|---|---|---|
| AT | 0 | 607 | 37 |
| EV | 80 | 64 | 1 |
| VEV | 114 | 3 | 5 |
| CEV | 5 | 9 | 0 |
| FEV | **73** | 0 | 0 |
| VAV | 584 | 0 | 1 |
| FCU | 135 | 0 | 3 |

Every FEV, and 114 of 122 VEV, have their own historian object and their own
points. Treating those families as parts would delete 192 real controllable
assets.

## What the matching has to be careful about

Each of these was found by checking the output, not by reasoning first:

- **Feed `numbers()` the raw object name, not the key.** Stripping the
  separators first turns `VAV4110_EV4111` into one unit numbered `4110E`, and
  every AT then finds no host.
- **Key the host index on the building.** `RDC_NB_1F_FCU2004` was matched to
  `RDC_SB_GF_VAV2004`, a unit in the other building.
- **Strip level segments before comparing.** The register writes
  `RDC_NB_2F_2F_AHU8513` and the historian `RDC_NB_AHU8513`; comparing whole
  strings called 26 air handling units unknown when every one is present.
- **FCU and AHU cannot host a part.** Letting them gave 31 rows two candidate
  hosts, because `FCU1004` and `VAV1004` share a number and are different units.

---

# Rebuilding the RDC section around the units the historian carries

`rebuild_register.py` does the three changes, all confined to RDC.

```
python3 rebuild_register.py --dry-run
python3 rebuild_register.py
```

| | rows |
|---|---|
| RDC section in | 1,759 |
| kept as units | 1,029 |
| kept - already the whole assembly | 1 |
| part rows renamed into their unit | 111 |
| removed - parts of a unit | 571 |
| removed - not in the historian | 47 |
| **RDC section out** | **1,141** |

The 47 removed are tabulated on their own in
`RDC_removed_not_in_historian.xlsx`; every removal, rename and retention is in
`rdc_rebuild_log.csv`.

## The unit a part points at takes the part's own row

The register lists the terminals of 62 CAVs and 48 EAVs without listing the CAV
or EAV itself, so removing the parts alone would lose the equipment. **The first
of those part rows becomes the unit, where it sits** - same row, same position in
the section, same review note, same highlight - renamed as the historian names
it and keeping the room its parts agreed on, or no room and a note saying so
where they did not. Its siblings are removed.

The first pass did this the other way round: it deleted every part row and
appended 112 fresh unit rows at the end of the section. That threw away the
review already done on those rows and filed the new equipment 200 rows away from
the units it belongs beside. Renaming in place is what the instruction asked for
- *replace it with it* - and it is why the note on `AT-0503` needs no special
handling to end up on `CAV0503`: it never moves.

## A row that is already the whole assembly is not a part of one

`RDC_NB_1F_VAV7830_VEV7831` names both halves of the assembly the historian
carries as `RDC_NB_1F_VAV7830_7831`. The two differ on spelling, not on what
they name, so the register's row is the unit and stays exactly as it is - the
first pass removed it as a part and wrote the historian's spelling back as a new
row, which is a rename dressed up as a deletion.

The test is the **leading family and number**, not the whole set: `AT-1005` and
`CAV1005` share a number but not a family, so the AT is a part; `VAV7830_VEV7831`
and `VAV7830_7831` share `(VAV, 7830)`, so they are one unit. Comparing the full
set of `(family, number)` pairs gets the first case right and the second wrong,
because the historian drops the family from the second number.

## Editing the workbook without breaking it

The RDC section is the last block of rows, so the rows above it are copied
through untouched and only the tail is rebuilt. Everything is done as XML inside
the zip - after a run, only `sheet6.xml`, `comments1.xml` and the VML that
positions the comments differ, and the HQ, QNL and SSC rows are identical.

**The 38 cell comments are the client's own review notes** and had to survive.
They are moved with their rows in both `comments1.xml` and the VML anchors,
which count rows from zero. A note on a part row follows the part to its unit -
the note on `AT-0503` sits on the `CAV0503` that row became. 37 of the 38 end on
exactly the tag they started on, and the 38th is that one.

Two bugs worth naming, both found by checking the output rather than the code:

- A row is `<row .../>` or `<row ...>...</row>`. Matching `.*?(?:/>|</row>)`
  stops at the first self-closing *cell* inside the row and cuts it in half,
  which silently dropped two thirds of the sheet.
- `register_style` must not add a level segment the historian's name already
  carries, or `CAV0503` becomes `RDC_SB_1F_1F_CAV0503`.

The one tag left with a doubled level, `RDC_NB_2F_2F_AHU8513`, is the register's
own typo and is left as it is.

---

# One clean register, with the room names written in

`build_clean_register.py` writes the register on its own, as one flat table,
with the agreed room name in column D.

```
python3 build_clean_register.py --dry-run
python3 build_clean_register.py
```

| | |
|---|---|
| asset rows | 2,577 |
| HQ / QNL / SSC / RDC | 761 / 551 / 124 / 1,141 |
| room names rewritten | 1,446 (HQ 755, QNL 537, SSC 122, RDC 32) |
| rows still with no room | 18 |
| cell comments carried across | 38 |

Four tabs: `Asset Register`, `Room name changes` (the crosswalk, also written to
`clean_room_name_changes.csv`), `Removed from RDC` (all 730 removals and
renames from the historian pass) and `Read me`.

## What "clean" meant

The working file's registry sheet declared **16,382 columns**, hid **1,141 rows**
behind two levels of outline grouping, left columns G and I empty between the
ones it used, and gave columns E and F no header at all. Here every column
carries data and a header, nothing is hidden, and there is no grouping.

The columns are contiguous, so `ROOM PER BMS SCREEN` is **column H, not column
J**. Column D is unchanged - it is the one the correction writes and the
converter reads.

The **HQ / QNL / SSC / RDC banner rows are gone** and the building is column L
instead. A banner row inside a filtered table sorts into the middle of the data;
a column filters.

## Following a rename

The RDC readings were taken against the tags the register carried before the
historian pass, and one of the 32 green rows was a part: `AT-5280`. Its reading
follows the rename to `CAV5280` rather than being dropped for naming a tag that
no longer exists.

## What the flat table exposed

**123 tags appear in two buildings at once** - `AHUB_0001`, `FCU0001` and so on.
None repeats inside its own building, and the banner-row layout hid the
collision because the two rows were 800 apart. Only RDC prefixes its tags with
the building code. The ontology needs that prefix on all four.

## What is not in the file

The four source equipment registers, the three room-name tabs and the 55-turn
`Claude Log` stay in the working workbook. They carry spilling
`TRANSPOSE(FILTER(...))` formulas and dynamic-array metadata that an openpyxl
rewrite drops, and none of them is the deliverable.
