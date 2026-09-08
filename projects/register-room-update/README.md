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

## Auditing the correction from the source side

Checking that the changes I made landed is not the same as checking that
nothing in the sources was skipped, so the audit runs the other way round:
every non-empty `rdfs:label_en` in `Room_Names_4.xlsx` and every green row in
`RDC_reviewed.xlsx`, looked up in the finished register.

| | |
|---|---|
| SSC names placed | 123 of 123 with a register row |
| HQ names placed | 760 of 760 with a register row |
| QNL names placed | 537 of 537 |
| RDC green readings placed | 32 of 32 |
| mismatches | 0 |
| column D changed without a crosswalk row | 0 |
| crosswalk rows that did not actually change | 0 |

Two gaps, neither of them a failure of the correction:

- **74 source names had no register row** - 41 SSC, 33 HQ, every one a CCU, DX,
  chilled-water heat exchanger or pump, exhaust fan, or the MV generator. None
  of them exists in the register under any spelling either, so the name had
  nowhere to go. Either the register is missing this equipment or it is out of
  scope, and that has not been decided.
- **90 source rows have an empty `rdfs:label_en`** - 75 HQ, 14 QNL, 1 SSC. No
  source settled the room, so those register rows keep what they had.

50 RDC rows that are not green carry a column J reading equal to column D. That
is the reviewer leaving J filled where the screen and the drawings agreed, not
a rejected reading leaking in - the crosswalk carries 32 RDC rows and no more.

---

# The reading copy: equipment and its room

`build_equipment_rooms.py` writes `Appendix_A_Equipment_Rooms.xlsx` - three
columns, four tabs, nothing else.

```
python3 build_equipment_rooms.py
```

| tab | assets | no agreed room |
|---|---|---|
| HQ | 761 | 1 |
| QNL | 551 | 14 |
| SSC | 124 | 0 |
| RDC | 1,141 | 3 |
| **total** | **2,577** | **18** |

Tag, equipment type, room. Every other column of the register is provenance -
which source won, what the BMS screen said, which drawing it came from - and
that belongs in the working file, not in the sheet somebody opens to find out
where a unit is.

Row order is the register's own, not alphabetical: the register groups by
equipment family and level, and sorting by tag scatters every family.

The 18 assets with no agreed room keep an empty cell, shaded, rather than a
guess. Verified row-for-row against the clean register: all four tabs match
exactly.

---

# Carrying the old registry's columns E onward across

`merge_old_columns.py` writes `All_Buildings_Rooms_Inclusion_Status_V1.3.xlsx`:
columns A-D from the corrected register, columns E onward from
`All_Buildings_Rooms_Inclusion_Status_V1.2.xlsx`, matched on the tag, four tabs.

```
python3 merge_old_columns.py --dry-run
python3 merge_old_columns.py
```

| tab | assets | old columns | filled from the old file | no old row |
|---|---|---|---|---|
| HQ | 761 | E-K (7) | 761 | 0 |
| QNL | 551 | E-L (8) | 451 | 100 |
| SSC | 124 | E-S (15) | 124 | 0 |
| RDC | 1,141 | E-K (7) | 1,141 | 0 |

Each building carries a different set - HQ has occupied and unoccupied
setpoints, SSC fifteen columns including room unit setpoints and an occupancy
status, RDC outside and exhaust air - so the headers are per tab, exactly as the
old file names them. Only `ZONES SERVED` is retyped, as `Zones Served`.

## The RDC match is not a string match

The historian pass renamed 111 part rows into the unit they belong to, so the
old file's `AT-1005` row carries the zones and readings that are now
`CAV1005`'s. `rdc_rebuild_log.csv` supplies the map. Where several old part rows
land on one unit the row that became the unit wins and the others are compared
against it rather than trusted - on this data all 14 such cases agree exactly.

1,030 RDC rows matched on the tag and 111 through the rename. Nothing needed a
loose match, because the three AHU tags that would have are now corrected.

## Three tags corrected

| before | after |
|---|---|
| `RDC_NB_AHU8511` | `RDC_NB_2F_AHU8511` |
| `RDC_NB_AHU8512` | `RDC_NB_2F_AHU8512` |
| `RDC_NB_2F_2F_AHU8513` | `RDC_NB_2F_AHU8513` |

The register dropped the level segment on two of these and doubled it on the
third; V1.2 spells all three the same way and settles what it should have been.
Corrected on the client's instruction, from one map in `build_clean_register.py`
applied as the rows are read, so the tag cannot drift between the register, the
equipment list and V1.3. The crosswalk is `tag_corrections.csv`. No other tag
was touched - identifiers are the join key to SCADA.

## What did not match

**100 QNL assets have no row in the old file** - 24 DX units, 19 exhaust fans,
23 CCUs, 5 heat exchangers, 6 chilled-water pumps, the generator and the rest.
The old QNL tab carries 451 rows against the register's 551. Their E-onward
cells are empty and shaded; nothing was carried over from a neighbour.

**604 old rows had no unit to land on** - the RDC air terminals and valves the
historian carries only as part of an assembly, and the 47 it has never heard of.

Every one of these is in `old_column_merge_coverage.csv`, row by row.

---

# How "Included / Not included" is set, as a rule

`inclusion_rule.py` reads the four registers, states the rule they follow, and
measures itself against them.

```
python3 inclusion_rule.py          # measure
python3 inclusion_rule.py --fill   # propose a verdict for every blank row
```

## The register I started from had RDC's column C wrong

`All_Buildings_Rooms_Inclusion_Status_V1.2.xlsx` and
`Appendix_A_Asset_Register_QNL_BMS_rooms.xlsx` disagree about column C on **439
rows**, 277 of them RDC and 264 of those naming the same room in both files. The
register excludes every RDC laboratory; V1.2 includes them.

V1.2 is right, and it is measurable rather than a matter of opinion. Against the
rule "exclude technical rooms and executive offices":

| RDC column C from | agreement |
|---|---|
| V1.2 | **98.5%** |
| the register | 85.4% |

So **RDC's column C is taken from V1.2**, on 276 rows.

HQ, QNL and SSC keep the register's. **99 of the 108 rows where those three
disagree are the same room** - the two files just write the name differently,
`FINANCE AUDITOR 1.115` against `1.115 FINANCE AUDITOR` - so they are genuine
reversals, not a room that has been renamed. 76 go Not Included -> Included and
23 the other way. They are kept because the rule backs the register on **83 of
the 99** (HQ 72 of 81, QNL 11 of 18), not because they are a formatting
artefact. Only 9 of the 108 are a different room, and those are rows where V1.2
carried a zone or a bare number - `NORTH EAST ZONE`, `HQ RF`, `ROOM B.014`.

All 108 are in `inclusion_column_c_conflicts.csv` with both room names, a
same-room flag, both verdicts and the rule's own reading, for a decision.

## The rule

**The verdict belongs to the room, not to the equipment.** 1,683 of the 1,692
rooms that carry a verdict give the same answer for every unit serving them. The
9 that do not - `RF.001 ROOF`, `B.063 PLANT ROOM 01`, `1.039 IDF 2` and six more
- are register errors, not a second rule.

A room is **Not included** when it is one of:

| class | what it covers | buildings |
|---|---|---|
| technical | plant, mechanical, electrical, IT and security - IDF, MDF, MCC, UPS, BMS, server, control rooms, AHU and plant rooms, pumps, penthouses, the roof, and RDC's flammable, cylinder and recycling stores | all four |
| executive | the room of someone senior, or the en-suite, waiting or meeting room attached to one - director, manager, head of, VP, president, executive, VIP, the Sheikha and HH wings | all four |
| common area | corridors, lobbies, lounges, the spa, prayer and ablution rooms, toilets, terraces, the cafeteria, the visitors' centre | **HQ only** |

**Laboratories are Included.** RDC's 144 lab rows are all Included in V1.3. The
only two rooms with "Lab" in the name that V1.2 still excludes are the Cyber
Electrical Lab and the Cyber SOC/NOC Lab, which are technical rooms by nature.

## HQ names a room `<department> <role>`, and the role decides

`STR PL DIR EXEC SECRE` is the strategic planning director's secretary and is
Included; `STR PL DIR MANAGER` is not. The department in front is not the
signal, so a junior role - secretary, assistant, analyst, clerical, archive,
print, staff - overrides the senior department, except an en-suite, which is
always the senior's own.

## How close the rule gets

| | rooms | agrees | rows | agrees |
|---|---|---|---|---|
| HQ | 599 | 93.5% | 759 | 91.6% |
| QNL | 168 | 95.2% | 449 | 96.4% |
| SSC | 69 | 97.1% | 123 | 96.7% |
| RDC | 856 | **98.6%** | 1,138 | **98.6%** |
| **all** | **1,692** | **96.1%** | **2,469** | **95.9%** |

The ceiling for any rule read off the room name is 97.8% for HQ, because the
register gives the same room name both verdicts that often - `VP EDU OFFICERS`
excluded 8 times and included 4, `FINANCE AUDITOR` excluded once and included
twice. The 61 rooms where the rule and the register differ are in
`inclusion_rule_report.csv`; several look like the register is wrong rather than
the rule.

## Filling the blanks

105 rows carried no verdict. `--fill` proposes one and writes
`inclusion_proposed.csv`; `merge_old_columns.py` writes them into V1.3 **only
where column C is blank**, shaded, touching nothing already decided. The
proposals are excluded from the measurement above - scoring the rule against its
own output would only measure it against itself.

| | rows | verdict |
|---|---|---|
| QNL plant equipment - DX 24, CCU 22, EF 18, SEF 12, TEF 8, CHW pump 6, HEX 5, KEF 4, generator 1 | 100 | Not included |
| HQ `FCU0097`, in `B1.512 IDF ROOM` | 1 | Not included - technical |
| 4 rows with no room name | 4 | left blank |

The 100 QNL rows are plant serving plant, not a room, and every unit of those
types already in the four registers is Not included. The four with no room name
keep their blank: there is nothing to decide them on.
