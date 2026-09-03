# Dar Cairo-shaped room subjects for SSC and HQ

One workbook out, one sheet per building, derived from the BMS room-allocation
registers by `build_room_names.py`.

```
python3 build_room_names.py \
    --src SSC=sources/SSC_rooms.xlsx,sources/SSC_remaining_equipment.xlsx \
    --src HQ=sources/HQ_rooms_B-2F.xlsx,sources/HQ_rooms_3F-Roof.xlsx,\
sources/HQ_remaining_equipment.xlsx \
    --src QNL=sources/QNL_rooms.xlsx \
    --out Room_Names.xlsx \
    --rooms-xlsx Rooms_with_Equipment.xlsx \
    --rooms-csv rooms_distinct.csv
```

Two workbooks come out. `--out` is the register, one sheet per building, one
row per asset, carrying the room subject the row resolved to.
`--rooms-xlsx` is the room roll-up, one sheet per building, one row per room,
carrying the equipment that serves it - the tags from column A, how many, what
types, and how many of them are in scope.

SSC: 165 asset rows, 85 rooms, 1 unresolved.
HQ: 868 asset rows, 610 rooms, 75 unresolved.
QNL: 551 asset rows, 197 rooms, 14 unresolved.

That is the whole controllable estate for the three buildings: the AHU/VAV/FCU
pass plus the remaining equipment. `RDC`, a fourth building of 1,759 rows in the
same source workbook, is not in scope.

**HQ's 74 unresolved rows are a client question, not a gap in this build.** The
delivered HQ ontology points 48 of them at the placeholder `entity:<Location>`
and gives 26 no room at all, and no BMS screen reading names one either. There
is nothing to name them from, so they are left blank with that reason in the
notes. Four more placeholder rows *do* have a screen reading and are named from
it.

A building split across several workbooks is given as one comma-separated
`--src`; see **Merging HQ's two workbooks**.

## The shape

Building, then the room reference, then the name - three segments:

```
entity:SSC_01-014_Shell-Space
entity:SSC_B-016_Sprinkler-And-Water
entity:SSC_01-ST-4_Stair-4
```

The reference segment already carries the level (`01-014`, `B-016`), so a
separate level segment would only repeat it. Dar Cairo likewise ends up with the
level inside its number (`B331`); it just orders the segments the other way,
`entity:Dar-Cairo_Basement-3_Pump-Room_B331`.

Dashes separate words inside a segment, underscores separate segments, and
nothing else survives into a name: `VISITOR'S CUBICLE` -> `Visitors-Cubicle`,
`SPRINKLER & WATER` -> `Sprinkler-And-Water` (Dar Cairo spells the ampersand out
in `Boiler-And-Heat-Exchange`), `ASSOC. DIR. OFFICE` -> `Assoc-Directors-Office`,
`MAIN SEC. CONTROL ROOM` -> `Main-Sec-Control-Room`. Ordinary words are title
case; the tokens in `ACRONYMS` stay upper - `AV-Room`, `IDF-1`,
`IT-Managers-Office`. The dot in the reference becomes a dash, so `01.014` is
the segment `01-014`.

The building code is `SSC`, not the Dar Cairo-style long form. The four level
entities the delivered SSC ontology already ships - `entity:SSC_Level-01`
through `entity:SSC_Level-B1` - are unchanged and are what these rooms hang off
with `rec:isPartOf`; the level no longer appears in the room subject itself.
One thing to note: the basement reference reads `B` where the level entity reads
`B1`, because `B.013` is what the drawings print.

## Which column the name comes from

In source-column order: **D** room name as per drawings, **E** the existing
ontology name, **H** room per the VAV/FCU list, **J** room per the BMS screen.

1. **Green row** - the BMS screen overruled the drawings, which is why the row
   was traced in the first place. Take the last of D, H, J that carries a name;
   on every green SSC row that is J. E is not consulted, because green means E
   is what turned out to be wrong. Where the screen names the room but not its
   number (`ST-4 STAIR 4`), the number still comes from E - only the name was
   in dispute.
2. **Otherwise, D or J on whether H carries a room number** - H carries one, D
   stands; H does not and J has both a number and a name, J stands; no usable
   J, D stands.
3. **E arbitrates the name.** If the picked column disagrees with E and D
   agrees with E, D wins - this is what keeps `ROOM NO 42`, `43` and `44` apart
   from the `SHELL SPACE` they all sit inside, where the screen prints
   `01.029 SHELL SPACE` for all four. If neither agrees with E, the name comes
   from E, which is what corrects the screen's `VISITORS CUBIDE` and
   `RESEARCHER OFFICE`.
4. **One reference, one spelling.** After the row pass, room references
   carrying two spellings of the same name are collapsed onto the fuller one -
   `ASSOC.DIR OFFICE` and `ASSOC. DIRECTORS OFFICE` are one room. Only
   abbreviation variants collapse (token-prefix match); `01.029` keeps its four
   genuinely different names.
5. **References are padded to the building's own width.** SSC prints
   `<level>.<3 digits>`, so `1.027` and `3.041` become `01.027` and `03.041`.
   Nothing else in SSC needed padding - every room number was already three
   digits. The rule bites on HQ if HQ prints two-digit numbers.

Every row carries the column it was taken from and a note saying why, and the
notes also flag where the result parts company with the delivered SSC ontology.

## Two source layouts

The BMS register covers the AHU, VAV and FCU pass. Everything else - CRACs, DX
units, heat exchangers, pumps, control panels, exhaust fans - comes on an
equipment review sheet with its own column names, mapped onto the same six
fields:

| register | equipment review |
|---|---|
| `Tag No.` | `Tag` |
| `Equipment Type` | `Equipment class` |
| room per drawings | `Room per ontology` |
| ontology name | `Ontology room entity` |
| room per BMS screen | `Room per BMS screen` |
| green fill | `Needs revision` = `YES` |

The layout is picked off the header row, so either file can be passed to any
`--src`. Merging is keyed on the tag rather than the row number: HQ's two
register halves hold the same tags and are reconciled against each other, while
an equipment review sheet holds different equipment entirely and simply adds
its rows.

## Merging HQ's two workbooks

HQ arrived as two files holding the same 761 rows, each with the BMS screen read
for its own levels - `B-2F` for B1, G, 1 and 2, `3F-Roof` for 3 to 12 and the
roof. No row carries a screen reading in both, and the level ranges the file
names state match where the readings actually are on all 591 of them, so:

- **column J is a union** - whichever file has it;
- **green is a union** - each file only marked its own range;
- **D, E and H**: the file that owns the row's level wins, and every
  disagreement is written into that row's notes rather than dropped.

Twelve rows disagree. Nine are one file leaving a cell blank. Three are real,
and all three are in the notes and highlighted:

| rows | `B-2F` says | `3F-Roof` says | taken |
|---|---|---|---|
| VAV0039-41, VAV0052-53 | `PR & MARKET STAFF G.029/030`, `G.108 CONSULTANT SPACE` | `SENSORY G.029`, `SOFT PLAY & CREATIVE LEARNING G.108` | `B-2F` |
| VAV0090 | `G.104 LOBBY` | `CONFERENCE ROOM 1.110` | `B-2F` |
| VAV0092-93 | cashier in 1.116, secure room in 1.106 | the two swapped | `3F-Roof` |
| VAV0584-87 | `SHEIKHA ENSUIT 11.202` | `11.208` | `3F-Roof` |

VAV0092-93 is the one exception to the level rule. Level 1 belongs to `B-2F`,
but `3F-Roof`'s own column H and the delivered HQ draft both put the cashier in
1.106 and the secure room in 1.116 - two sources against one. The client read
the three flagged conflicts and chose `3F-Roof` here and `B-2F` for the other
two, so the pair sits in `OWNER_OVERRIDE` with that reason written into both
rows' notes. Every other row still follows the level rule.

## A name without a number is numbered by name, not by its neighbour

The BMS screen names a room without numbering it - on QNL it never numbers one -
so a screen-sourced name has no reference of its own. Borrowing one from the
drawings on the same row is wrong whenever the two columns name different rooms.
`DX_B01`'s drawings say `MV ROOM B.081` and its screen says `Corridor 4`, and
gluing them together gave `B.081 Corridor 4` - a room that does not exist. The
register numbers `Corridor 4` `B.035` three hundred rows away, on `CAV_B_S13_006`.

So a name that arrives without a reference is looked up in a register-wide index
of room name to reference, built from every source string that carried both.
Matching tolerates spacing and abbreviation (`Plant Rm 2` finds `Plant Room 2`,
`Emergency Lighting Battery Rm` finds the room spelled `...Room`) but refuses a
match where one name is the other plus something on the end: `BRIDGE BR-3` and
`BRIDGE BR-3B` are one letter and two floors apart, and numbering one after the
other moved four HQ units to the wrong level before the guard went in.

Eight QNL rows are renumbered by this. Two of them were doubly wrong before:
once the borrowed reference pulled the row into an existing room, column E
arbitrated that reference's name and overwrote the screen's, so `DX_B03` came
out as `Transformer-Room` with no trace of the `Emergency Lighting Battery Rm`
the screen actually read.

Where the register does not know the name, or knows it at more than one
reference, the borrowed reference is kept and the row says so: 24 rows on HQ and
23 on QNL. SSC has none - its screen readings all carry their own number.

## QNL's own quirks

**The BMS screen never carries a room number.** 146 of QNL's 147 screen
readings are a bare name - `IDF Rm`, `Plant Rm 1`, `Restaurant`. So where a
screen reading wins the name, the reference comes from the drawings. That is
also why rule 5 hands every non-green row to column D: J can never satisfy
"has both a number and a name".

**The drawings own the reference outright** (`ref_from_drawings`). Column E and
the drawings disagree on 15 of QNL's references, and the drawings are right on
13: E writes `L1023_2` for `L1.023`, `B046_ITT` for `B.046_ITT`, `L1-E2` for
`L1.E2`, `B141_VAU` for `B.141_VAU` - the level and room ran together or the
separator became a dash. The other two are genuine conflicts, both flagged:
`FCU_1F_058` (drawings `L1.145`, E `L1.144`) and `VAV_B_S10_009`
(drawings `B.203`, E `B.204`).

**Room codes are not all numeric.** `L1.BR6`, `L1.BC1`, `L1.L-3`, `L1.E2`,
`B.045A`, `B.046_ITT`. Padding applies to purely numeric codes only, so
`B.58` becomes `B.058` among its three-digit siblings and `BR6` is left alone.

**Levels are `B`, `L1`, `L2`, `P`, `T1` verbatim** - which is what
`projects/QNL/QNL_Ontology.xlsx` already calls them (`entity:QNL_B`,
`entity:QNL_L1`).

**Not every asset tag ends in a number.** `CCU_MDFRm`, `ELEC_Gen`,
`CCU_Server_Rm`. A row is now recognised by having an equipment type beside
the tag rather than by the tag's shape; matching the shape silently dropped
nine QNL rows.

## HQ's own quirks

**Rule 3 finally bites.** HQ's references reached the sheet as decimals, so
Excel dropped the trailing zero: `1.020` came back as `1.02`, `3.360` as `3.36`,
`11.110` as `11.11`. 155 references pad on the **right**, and D or H spells the
full three digits on every one of them. SSC pads on the left and never lost a
digit, so the direction is a per-building setting.

**Levels print two ways.** The drawings write `04.110` and `B.001` where the
ontology name writes `4.110` and `B1.001`. Numeric levels are normalised to no
leading zero and `B` to `B1` - the opposite of SSC, whose drawings and BMS both
print `B.013`.

**Column E runs the department into the room name.** E writes
`EXECDIRLEGAL_ADVISOR` where the drawings write `LEGAL ADVISOR`, and that prefix
is not noise: it is what tells 11.017 from 11.018, both of which the drawings
call `LEGAL ADVISOR`. So E still wins the name. Two passes make it readable:

- spellings are compared with spacing ignored, so `STR. PL. DIR. TECH. STAFF`
  and `STRPLDIRTECHNSTAFF` are recognised as one name and the spaced one is
  kept;
- where another column spells the tail out, the prefix is split off it -
  `Execdir-Legal-Advisor`, not `Execdirlegal-Advisor`.

That leaves 18 names where no column spells the tail out and the prefix cannot
be split without guessing. They are listed under the open questions.

## What is still open

- `VAV0063` has no room in any column - D reads `(NOT FOUND ON DRAWING LEVEL 3)`
  and E is `#N/A`. Left blank rather than guessed.
- `03.006A` and `03.006B` are not in the delivered SSC ontology, which has one
  `03.006 MEETING ROOM`. The drawings and the screen also disagree on which of
  the two is A: D calls VAV0062's room `03.006B`, the screen calls it `03.006A`.
  Both rows are green, so the screen was followed; the split needs confirming.
  Neither room has a name beyond `ROOM` on the drawings or the screen, so the
  subjects read `entity:SSC_03-006A_Room`.
- Abbreviations are kept as the source wrote them - `Main-Sec-Control-Room`,
  `Assoc-Directors-Office`, `Vent-Plant`. `SEC.` is ambiguous (security or
  secondary) and these become labels users read, so they want expanding once
  the client says what they stand for.
- **HQ, 18 run-together names.** `Suppservadminist`, `Execdirexecassist`,
  `Vice-Chairsecretary`, `Policy-Dirresanalyst` and 14 like them. The
  department prefix is real and has to stay, but no column spells the boundary
  out, so splitting it means guessing where one word ends. The prefixes look
  like a small closed set (`SUPPSERV`, `EXECDIR`, `SHSERVDIR`, `COMMUNICDIR`,
  `POLICYDIR`, `PLANNINGDIR`, `FACILITYMANAG`, `VICECHAIR`, `VPEDUCHP`,
  `HREDUADV`, `PROCANDCONTRLDIR`, `LEGALLEGADV`); one list of their expansions
  settles all 18 at once.
- **HQ, VAV0558** has no room in any column. Left blank.
- **QNL, 14 rows** have no room in any column: `VAV0001`, `VAV_B_S13_005`,
  `CCU_8081` to `CCU_8086`, `CCU_MDFRm`, `CCU_Qtel`, `CCU_Server_Rm`,
  `CCU_AVServer_Rm`, `CCU_HeritageVault`, `CHWPU_P02`. Left blank.
- **QNL is part 1 of its register.** A second part drops in as another
  comma-separated path on the same `--src`, but the merge policy is HQ's
  level-range rule; if QNL's parts split some other way, that rule needs
  telling how.
- **QNL room names are respelled from the delivered QNL ontology.** Where it
  names a reference, names it once, and the two are the same name spelled two
  ways, its spelling wins - `SPRIMKLERS` becomes `Sprinklers`, `TRANSH CHAMBER`
  `Trash-Chamber`, `SHIPPING CLIRK` `Shipping-Clerk`, `ARABIC SUDIES`
  `Arabic-Studies`. Two guards keep it honest: a genuinely different name is
  left alone (`B.203` is Technical Services here and Storage Room there, which
  is a disagreement about the room, not its spelling), and a respelling may
  never lose a word, or `BINDING & PRESERVATION SPACE` would quietly become
  `Binding-Preservation-Space`.

  **SSC and HQ are deliberately excluded.** SSC's names are reviewed and are
  not to be disturbed; HQ's ontology is a draft that carries `SPA FITNESS
  DTUDIO` and `VACILITY MANAGDIRENSUIT` and runs the department into the room
  name, so letting it respell would import its typos and undo the readability
  work. Two QNL tokens no ontology can prove are in `SPELLING_FIXES`, applied to
  the identifier and the label from one map so the two cannot drift.
- **42 spelling clashes** across the three buildings, where a name is the same
  in two columns but the letters differ - `SPA FITNESS DTUDIO`, `SECURITY
  CONTOL ROOM`, `STUDENT CARRLES`, `CHAUFFER`/`CHAUFFEUR`. Every one is in
  the row's notes. Nothing is corrected: a room name is also the label a user
  reads, so the client decides.
- **The HQ draft disagrees on 64 names.** Advisory only - it never changes a
  name, it only writes a note. Most are typos in the draft (`SPA FITNESS
  DTUDIO`, `VACILITY MANAGDIRENSUIT`, `SH. SERV. DIR. ACCOUNUT.`), but a few
  are real: `CHAUFFER`/`CHAUFFEUR ROOM`, `CONTROL CENTER`/`EMERGENCY CONTROL
  CENTER`, `MCC/ELEC ROOM`/`ELECTRICAL ROOM`. The VAV0092-93 swap is settled -
  the sheet and the draft now agree.
  Three HQ rooms are not in the draft at all: `3-630 Corridor-Bridge`,
  `11-208 Sheikha-Wing-Sheikha-Ensuit`, `B1-124 Waste-Bin-Wash-Up`.
- Three room names in HQ carry a qualifier the VAV/FCU list adds and the
  drawings do not - `SHEIKA WING DINING AREA SE`, `HH-WING CORRIDOR SW`,
  `VISITORS CENTER 08`. These read as zones inside one room rather than room
  names, so the room keeps the plain name and the qualifier is dropped. Three
  or four VAVs share each of those rooms, which is consistent with them being
  zones; confirm if the compass split is meant to be real.
- Labels are written in the QF SSC house style (`1.024 CORRIDOR`), which is what
  the delivered SSC sheet uses. Dar Cairo instead labels a room with its own
  identifier tail (`Corridor-02-B112`).
