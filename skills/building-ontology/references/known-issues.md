# Rule codes, source conflicts, and defects in the reference models

Two scripts report codes. `validate_ontology.py` reads one row at a time and
carries the `E-`/`W-`/`I-` codes below. `check_consistency.py` compares every
unit of a class against its siblings and carries the `-CON-` codes further down.

## Validator rule codes

### Errors - fix before handover

| Code | Means |
|---|---|
| `E-HDR-1` | the first five headers are not `subject, subjectType, predicate, object, objectType` |
| `E-HDR-2` | a column past the fifth is not one of the four prop-column names |
| `E-CORE-1` | subject, predicate or object is empty |
| `E-WS-1` | a cell has leading or trailing whitespace, or an embedded tab |
| `E-SPACE-1` | an identifier contains a space |
| `E-PFX-1` | a prefix outside `entity brick rec ref unit qudt para rdf rdfs owl xsd skos bacnet` |
| `E-PFX-2` | a type or predicate with no prefix at all |
| `E-PH-1` | an unresolved `<placeholder>` cell. `<AliasOf>` is exempt - it is deliberate, and reported as `I-PH-2` |
| `E-PAIR-1` | a prop name with no value |
| `E-PAIR-2` | a prop value with no name - usually a pair shifted one column left |
| `E-LBL-1` | a label contains punctuation the label rule strips; the message shows the fix. Not applied under `--label-style verbatim` |
| `E-TYP-1` | one entity declared with more than one type. Each type is annotated with whether Dar Cairo uses it, which usually settles which one is right |
| `E-TYP-2` | a `brick:`/`rec:`/`ref:` term that does not exist in Brick 1.4 - almost always a typo. **Where Dar Cairo has a near-miss term, the message names it**, since step 1 of the ladder is the primary reference, not brickschema.org |
| `E-TYP-3` | a `para:` term used but never defined here and absent from the registry |
| `E-EXT-1` | a `rdfs:subClassOf` row whose `subjectType` is not `owl:Class` |
| `E-EXT-2` | a new class with no `brick:`/`rec:`/`para:` parent |
| `E-EXT-3` | a class declared as its own parent |
| `E-CELL-1` | a namespaced cell holds a control character or an invisible space (non-breaking, zero-width, BOM) |
| `E-CELL-2` | a namespaced cell has more than one colon; a term is `prefix:localName` |
| `E-CELL-3` | a prefix is not lower case |
| `E-BN-1` | a `<blanknode>` object with no object prop pairs to hold |
| `E-FEED-1` | a terminal unit that never says what it feeds |
| `E-GR-1` | a spatial entity whose containment chain never reaches a `rec:Building` |

### Warnings - fix or justify

| Code | Means |
|---|---|
| `W-TYP-4` | the term is deprecated in Brick 1.4; the message carries Brick's mitigation text |
| `W-TYP-5` | the term is an alias; use the preferred class named in the message |
| `W-BN-2` | a blank-node `objectType` that is neither `<blanknode>` nor a `ref:` class |
| `W-BN-3` | an external reference whose `objectType` is not a `ref:` class |
| `W-UNIT-2` | a unit in no known list - confirm at ontology.brickschema.org/qudt/Unit.html |
| `W-LBL-2` | an entity that never gets an `rdfs:label_en` |
| `W-GR-2` | terminal equipment with no `rec:locatedIn` |
| `W-PT-1` | a data point with no `ref:hasExternalReference` |
| `W-DUP-1` | a row identical to an earlier one |
| `W-EXT-4` | a property declared as its own super-property |
| `W-EXT-5` | a property related with `rdfs:subClassOf`; properties take `rdfs:subPropertyOf` |
| `W-BN-4` | `brick:value` with no `brick:hasUnit` - use `unit:UNITLESS` if the quantity really is dimensionless |
| `W-BN-5` | `ref:hasTimeseriesId` with no `para:hasEntityId` - the key has nothing saying which entity it groups under |
| `W-AGG-1` | `brick:aggregate` with no `brick:aggregationFunction` or no `brick:aggregationInterval` |
| `W-REF-1` | an entity referenced as an object but never given a row of its own - a dangling reference, or an entity another sheet declares |
| `E-PT-4` | a point with no `ref:hasExternalReference` that the IO list gives a timeseries id - only with `--io` |

The `E-CELL-` rules apply to **namespaced cells only** - subject, subjectType,
predicate, object, objectType - and never to a `*_prop_val` literal. A label may
contain anything a label may contain.

### Info

`I-TYP-6` - a valid Brick term with no precedent in Dar Cairo. Not a defect;
worth checking that no existing house class covers the same thing.

## Consistency rule codes

From `check_consistency.py`. Everything it reports is inferred from the sheet -
the families, what a complete unit looks like in each, and what each predicate's
object is supposed to be. There is no expected point list to maintain.

### Errors

| Code | Means |
|---|---|
| `E-CON-1` | a unit has more or fewer rows than the modal count for its class |
| `E-CON-2` | a relation most units of the class carry is absent on the rest |
| `E-CON-3` | a relation appears more than once on the same unit |
| `E-CON-4` | an object's shape contradicts what the family does with that predicate - a number where the family writes `<blanknode>`, an `#N/A` where it writes an entity. **The check a row count cannot make**: a unit can carry every row its siblings carry and still be broken because a value was pasted over the object column |
| `E-CON-5` | the same relation is typed differently across units - one VAV's status is `brick:On_Off_Status`, another's is `brick:Fan_Status` |
| `E-CON-6` | a unit has two `rec:locatedIn`, two `rec:feeds` or two `rec:isFedBy` rows |
| `E-CON-10` | one point carries more than one external reference |
| `E-CON-18` | a declared point with no external reference that the IO list gives a timeseries id - only with `--io` |
| `E-CON-17` | a child's identifier differs from its parent's only in separators - `Floor-1_A` owning a point named `Floor-1A_...`, so nothing that keys off the parent will find it |

### Warnings

| Code | Means |
|---|---|
| `W-CON-7` | every unit in a class shares one `rec:locatedIn` or `rec:feeds` target - usually placeholder data rather than 137 FCUs serving one room |
| `W-CON-9` | a declared point has no `ref:hasExternalReference`. Points only; a part needs no reference of its own |
| `W-CON-11` | something carries an external reference but is never declared with `brick:hasPoint` or `brick:hasPart` |
| `W-CON-12` | a unit's rows are scattered instead of sitting together; the stray rows are named |

### Info

| Code | Means |
|---|---|
| `I-CON-8` | every unit's `rec:feeds` target equals its `rec:locatedIn` target - right for a unit that conditions the room it sits in, wrong when one source column was reused for two questions |
| `I-CON-13` | an identifier repeats a token, `..._REST_REST_ROOM_WOMEN` |
| `I-CON-14` | two children of the same class whose names differ only by a trailing token |
| `I-CON-15` | a class with one instance, so no cross-unit comparison is possible. Said explicitly rather than reported as a vacuous pass |
| `I-PH-2` | a `<AliasOf>` placeholder: the point is modelled, and its database entity name is still to come. Open work, not a defect - see `csv-contract.md` |
| `I-CON-16` | an entity reference that lacks the prefix every subject in its family carries. Objects of `brick:isPartOf` and `rec:isFedBy` are exempt - they name shared plant, which both reference models deliberately write without a building code |

### How it decides what is expected

- **Units** are entities that are the subject of triples and never the object of
  `brick:hasPoint` or `brick:hasPart`. Working it out this way rather than from
  the identifier means non-sequential ids, mixed naming schemes and prefix
  collisions all handle themselves. Class-definition rows are excluded, or they
  appear as phantom units.
- **Structure** is compared by replacing the unit's own id with `{U}` and
  collapsing non-entity objects to a shape token. Without the second collapse,
  per-unit literals - rated flow rates, room names - each become their own
  single-unit "pattern" and the comparison is worthless.
- **Object shapes** are learned per family from the majority of its rows, at 60%
  confidence. The same predicate legitimately differs between families, so it is
  never inferred globally.
- `rec:locatedIn`, `rec:feeds`, `rec:isFedBy`, `rec:isPartOf` and
  `brick:isPartOf` are excluded from the structural comparison, because their
  objects are meant to differ per unit. They are checked separately for
  cardinality and placeholder smells.

## The IO list is evidence, not just a comparison target

Several findings are suspicious only until the IO list adjudicates them. A point
with no timeseries reference is a defect if the BMS publishes a key for it and a
fact if it does not. A point present on 4 of 10 units is a defect if the other 6
should have it and a fact if they never did. **Pass `--io` and the checks resolve
those findings instead of flagging them** - which is the pass a reviewer would
otherwise do by hand, and is exactly how the QF SSC review exercise cleared its
own findings.

| Without `--io` | With `--io`, when the list confirms the absence |
|---|---|
| `E-CON-1` a unit is short some rows | `I-CON-1` short, and the IO list accounts for all of them |
| `E-CON-2` a relation absent on some units | `I-CON-2` absent, and the IO list confirms none of them has it |
| `W-CON-9` a declared point with no reference | `I-CON-9` no reference, and no timeseries id in the list either |
| `W-PT-1` a point with no reference | `I-PT-3` same, confirmed by the list |

And it cuts the other way. Where the IO list says a point **does** have a key
that the sheet is missing, the finding is promoted rather than dismissed:
`E-PT-4` and `E-CON-18` both say "the IO list gives it `<id>`, and the sheet has
no reference row".

**A unit the IO list says nothing about is not evidence.** One unknown unit is
enough to leave a finding standing - silence is not confirmation, and resolving
on silence would quietly clear the findings the list never spoke to.

## IO cross-check rule codes

From `check_io_list.py`, which compares the points in a sheet against the IO list
they came from. A point the BMS does not publish resolves to an empty timeseries,
so over-inclusion is the failure mode this exists to catch.

| Code | Means |
|---|---|
| `E-IO-1` | a point in the sheet matches no IO row - it would resolve empty |
| `W-IO-2` | an IO row with no point in the sheet - usually a scope decision, worth confirming |
| `E-IO-3` | two points claiming the same timeseries id |
| `W-IO-4` | a point whose `ref:hasTimeseriesId` differs from the IO list's id for the same point name |
| `W-IO-5` | an IO row whose timeseries id is blank, so nothing can match it |

Matching is on the timeseries id first - the only value both sides genuinely
share - falling back to the point name. **When it cannot tell which column of the
IO list is the telemetry key, it stops and says so** rather than matching on a
guess and reporting every point as unmatched.

## Accepting a term the Brick extract rejects

`brick-vocab.txt` is generated from a pinned `Brick.ttl`, so it cannot carry a
decision: a term added to Brick after the pin reads as `E-TYP-2`, and a term the
house keeps deliberately reads as `W-TYP-5` on every row that uses it.
`references/data/accepted-terms.txt` overrides the extract for named terms, one
per line with the reason it is there. It survives regeneration.

Two entries today, both settled by the PARA team on 2026-08-20:

- **`brick:Apparent_Power_Sensor`** - confirmed on ontology.brickschema.org.
  Absent from the pinned 1.4 extract, which has `brick:Active_Power_Sensor` and
  `brick:Power_Sensor` but no apparent-power sibling. Dar Cairo's own precedent
  is `para:Apparent_Power_Usage_Sensor`, so revisit if the pin moves and the
  term is still missing.
- **`brick:HVAC_System`** - a Brick 1.4 alias for
  `brick:Heating_Ventilation_Air_Conditioning_System`, kept because both
  reference models write it and the front end keys off it. Consistency across
  the estate beats the preferred spelling here. Without the override, QNL alone
  carries 451 `W-TYP-5` rows, which buries the alias warnings that do matter.

**Never add a line without a reason.** The file is the only thing standing
between an accepted term and a typo somebody waved through.

## How the SSC findings were resolved

The review pass on the finalized SSC sheet, 2026-08-20. These are worth copying
because each is a *shape* of fix, not a one-off:

| Finding | What it turned out to be | The fix |
|---|---|---|
| `E-CON-10` one point, two external references | two different sensors sharing one identifier | **split the entity**: `_SA_P-Static` became `_SA_P-Static-1` and `-2`, typed `para:Static_Pressure_Sensor_01` / `_02`. Two keys means two points |
| `E-TYP-1` `_RA_P-Static` typed two ways | the generic and the specific class both in use | **keep the more specific one everywhere**: `para:Return_Air_Static_Pressure_Sensor`, not `para:Static_Pressure_Sensor` |
| `E-CON-5` `_RF` point typed under two fans | a return fan modelled as a supply fan | retyped `brick:Return_Fan`. The suffix in the identifier was right and the class was wrong |
| `E-FEED-1` on 14 CRACs | genuinely missing rows | added `rec:feeds` to the room each serves |
| `E-TYP-2` `brick:Heater` | not a Brick term, and Dar Cairo has no heaters at all | `brick:Heating_Coil` - the entity is a `brick:hasPart` of an AHU carrying a `brick:Heating_Command`, SCADA key `..._SupHtr.HtrCtrl`. That is a heating element inside an air handler, and the sibling of the `brick:Chilled_Water_Coil` the same AHUs use on the cooling side. `brick:Space_Heater` is a standalone room heater and `brick:Water_Heater` is domestic hot water |

**One lesson from the pass itself.** Two search-and-replace turns resolved
`brick:Alarm` and `brick:Fault_Status` on the CRAC alarm points, but each ran
over one column at a time: the `_General_Fault` entities ended up
`brick:Alarm` in `subjectType` and `brick:Communication_Loss_Alarm` in
`objectType` - a new `E-TYP-1` on 14 entities, created by the fix. **A class
change has to move every cell that names the entity, subject side and object
side together**, and `check_consistency.py` is what catches it when it does not.

## Where the sources disagree

The PARA document is Rev 0.0 and contradicts itself and Dar Cairo in several
places. Resolutions below are what this skill follows; each is worth confirming
with the PARA team.

| # | Conflict | Followed here |
|---|---|---|
| 1 | Chapter Two's CSV says `para:Pressure_Independent_Module` `subClassOf` `brick:Terminal_Unit`; the prose says `brick:PIM` under `brick:HVAC_Equipment` | the CSV - and Dar Cairo agrees, using `para:Pressure_Independent_Module` 1,142 times |
| 2 | The pre-requisite page says Room `isPartOf` HVAC Zone and HVAC Zone `isPartOf` Parent Zone, with `brick:isPartOf` | Dar Cairo: Room `rec:isPartOf` parent Zone, HVAC Zone `rec:isPartOf` Level |
| 3 | Equipment format written `<Type>_<Floor>_<ID>` with underscores; every example uses dashes | dashes |
| 4 | The equipment example types `Dar-Cairo_Basement-1` as `rec:Room`, but it is a level | type levels as `rec:Level` / `rec:BasementLevel` / `rec:RoofLevel` |
| 5 | Site section uses `brick:hasPart` Site to Building; Building section uses `rec:isPartOf` Building to Site | either, but hold one direction per chain |
| 6 | `rdfs:label_en` is not standard RDFS - standard practice is `rdfs:label "x"@en` | `rdfs:label_en`, as both reference models and the converter use it |
| 7 | The doc targets Brick 1.4; some terms in circulation are 1.5 | Brick 1.4 - the term list is generated from the 1.4 ontology |
| 8 | `rec:feeds` is referenced by Brick 1.4 but not defined as a REC term in it | `rec:feeds`, following Dar Cairo's 278 rows |
| 9 | Dar Cairo's header row starts `Subject`; `Ontology_headers.xlsx` says `subject` | lowercase `subject`; the validator compares case-insensitively |
| 10 | The label rule strips punctuation (`1.001 CORRIDOR`); QF SSC carries the source text verbatim (`1.001_CORRIDOR`, `SSC_FCU0001`); Dar Cairo is a third style again (`Mechanical-Area-2-R014`) | **ask the user** - `naming-and-labels.md` documents both, and `validate_ontology.py --label-style verbatim` turns `E-LBL-1` off for the SSC style. QNL was built `verbatim` at the user's direction |
| 12 | Draft 0.4 had no `rec:Site` and no `rec:Building` row, which read as a convention. It was not - it was an unfinished sheet. Draft 0.5 carries `entity:SSC rec:Building rec:isPartOf entity:QF rec:Site`, labelled `SSC Building` and `Qatar Foundation` | build the full chain, as 0.5 and Dar Cairo both do. **The lesson: an absence in a reference model is not a convention until a current export confirms it** |
| 11 | The IFC reference property: Dar Cairo writes `ref:ifcName` (535 rows) and defines `para:IFC_ID` once without using it; QF SSC writes **both** `para:IFC_ID` and `ref:ifcName` on all 167 of its IFC rows | both, the SSC shape - `para:IFC_ID` for the BIM GUID, `ref:ifcName` for the derivable entity name |

## Units: the class outranks every source column

A source's unit column is a free-text field nobody validates, and every QNL source got
some of it wrong in a different way:

| Source | Defect |
|---|---|
| `Selected_PARA_OS_Data_Points_v4.0.xlsx` | 30 analog rows with humidity and temperature units transposed (`AvgSpcHumd` as `°C`, `AvgSpcTemp` as `%rH`) |
| `QNL_Historian_IO_list_CP2.xlsx` | 20 of its 24 `.kW` tags carry `%`, against a description reading "Power" |

Preferring one column over another only moves the error around. The reliable rule is
that **the resolved class names the physical quantity, so where the class admits exactly
one unit, the class decides and the source is overridden** - `brick:Electric_Power_Sensor`
takes `unit:KiloW` no matter what the IO list says. Log every override at build time;
a silent correction is as hard to review as a silent error.

Do not extend this to classes whose quantity genuinely admits more than one unit. Air
flow is the QNL example: the IO list distinguishes volumetric flow (`l/s`, on VAV/CAV
boxes) from velocity (`m/s`, on AHU ducts), and both are real measurements, so forcing
one would destroy information.

**The cheap invariant that catches this whole class of defect: no class should carry
more than one unit across the sheet.** Group `brick:hasUnit` by `objectType` and look for
a class with two. On QNL that surfaced `brick:Electric_Power_Sensor` split 20 `PERCENT` /
4 `KiloW` - the split itself was the tell, before anyone read a single tag.

## Reading an IO list: two traps the QNL list exposed

Both were live bugs in the shared loader, fixed 2026-08-24 against
`QNL_Historian_IO_list_CP2.xlsx`. They matter because both fail *silently* -
the checks still run and still report, they just report the wrong thing.

**1. An IO list can span several sheets.** QNL splits its points across
`QNL analog cp2` (5,574 rows) and `QNL Descrete cp2` (6,027), with different
column layouts. `io_list.py` and `check_io_list.py` both read only
`worksheets[0]`, so every discrete point vanished - and each one then reported as
`E-IO-1`, "in the sheet but matches no IO row", against a sheet that was correct.
88 phantom errors. Both loaders now read every sheet, header-match each on its
own, and skip (by name) any tab with no key/name column.

**2. "Unit" on an IO list means the engineering unit, not the unit of plant.**
`EQUIP_HEADERS` matched the analog tab's `Unit` column, so `known_equipment`
filled with `bar`, `kw`, `hz`, `degC` - 31 "equipment tags", none of them real.
`has_point()` answers `None` for equipment it does not know, so every finding the
IO list should have adjudicated came back "cannot tell", and `--io` silently
changed nothing. `NOT_EQUIP_HEADERS` now excludes unit/uom columns, and where
there is no usable equipment column the unit is derived from the dotted tag
(`QNL_AHUB001_SupFan.kW` -> unit `QNL_AHUB001`, point `SupFan.kW`). Watch the
part heuristic: a trailing numeric segment is a unit counter, not a part -
`QNL_VAV_B_S11_026` is unit 026 of system S11.

The tell for both: `check_consistency.py --io` reporting exactly what it reported
without `--io`. If the IO list resolves nothing, check what `IOList.describe()`
says it found before trusting any finding - on QNL the fixes took equipment tags
from 31 to 1,755 and consistency errors from 287 to 78.

## Known defects in the reference models

### Dar Cairo (`DarCairo_V93.csv`, 26,173 rows)

Still the primary reference - but it is not clean, so do not copy patterns
blindly. Current validator output:

| Count | Code | What it is |
|---|---|---|
| 3,181 | `E-LBL-1` | labels with dashes, underscores, brackets - the label rule is newer than the file |
| 698 | `W-TYP-5` | alias classes, mostly `brick:VFD` and `brick:HVAC_System` |
| 300 | `W-LBL-2` | entities with no label |
| 203 | `W-UNIT-2` | `unit:MicroGM-PER-M4` through `M27` - a fill-down accident; every one should be `unit:MicroGM-PER-M3` |
| 104 | `E-WS-1` | padded cells, including one with an embedded tab |
| 82 | `W-DUP-1` | duplicate rows |
| 74 | `E-TYP-1` | entities with two types, e.g. `entity:FCU-01_GF_SF-Motor` typed both `brick:Fan_Coil_Unit` and `brick:Motor` |
| 71 | `E-PAIR-2` | prop values with no name |
| 64 | `E-FEED-1` | equipment with no feeds row, mostly exhaust fans |
| 3 | `E-EXT-3` | `para:HighPowerFan`, `para:MediumPowerFan`, `para:LowPowerFan` declared as their own parents |
| 1 | `E-TYP-2` | `brick:Water_PUMP` - should be `brick:Water_Pump` |

`check_consistency.py` adds 3,966 errors and 3,836 warnings on top, dominated by
`E-CON-1` and `E-CON-2` - Dar Cairo's families genuinely differ unit to unit. The
15 `E-CON-17` findings are unambiguous though: `entity:Dar-Cairo_Floor-1_A_Occupancy-Virtual-Sensor`
owns a point named `entity:Dar-Cairo_Floor-1A_Occupancy-Virtual-Sensor_Arrival-Time`,
one underscore apart, on every one of the A/B/C zone sensors.

Also: `unit:KiloWHR` (12 rows) should be `unit:KiloW-HR`; `unit:REV-PER-MIN` and
`unit:RPM` are used interchangeably.

Because of the mistyped motors, `--template` percentages can read "50% of
instances" where the real figure is 100% of the equipment and 0% of the
mistyped parts. Read the worked example at the bottom of the template output,
not just the percentages.

### Not a conflict: where timeseries references live

Worth stating because it is easy to get wrong. `ref:TimeseriesReference` belongs
to a **point**, never to equipment - all 1,767 in QF SSC have a `brick:hasPoint`
object as their subject and none has a piece of equipment. `ref:IFCReference` is
the opposite: it goes on the physical thing, equipment or room. Where no IO list
was supplied there are no points and therefore no timeseries references; do not
add equipment-level stubs to fill the gap.

### QF SSC ver02 (`QF_SSC_Ontology_ver02.xlsx`, 5,082 rows)

The cleaned SSC delivery, replacing `draft0.5_review` (gone from the repo). Two
sheets: `SSC_Ontology_Ver0.6` holds the triples and `Claude Log` records the
last two correction turns (the CCU alarm-typing fixes of 2026-08-20). The nine
`*_Comparison` / `*_Check` review sheets that draft 0.5 carried are gone - this
is a delivery sheet, not a review workbook.

The workbook now opens on the ontology sheet, but every script here still picks
the sheet by the header contract rather than by `.active` - keep that habit, and
any new tool that reads a reference model must do the same.

This is the step-3 previous-project reference in the class ladder. Much cleaner
than draft 0.5 - **17 errors against 451** under `--label-style verbatim`:

| Count | Code | What it is |
|---|---|---|
| 2,799 | `I-TYP-6` | valid Brick terms with no Dar Cairo precedent - advisory |
| 309 | `W-TYP-5` | alias classes, mostly `brick:CRAC` (prefer `brick:Computer_Room_Air_Conditioning`) |
| 8 | `W-LBL-2` | entities with no label, `entity:CHWS-MAIN-LOOP` among them |
| 8 | `E-WS-1` | padded cells - leading/trailing whitespace |
| 7 | `I-PH-2` | `<AliasOf>` placeholders - open work, not defects |
| 4 | `E-TYP-3` | a `para:` term used but not defined in-sheet and absent from the registry |
| 3 | `E-PAIR-1` | a prop name with no value |
| 3 | `W-PT-1` | a data point with no external reference, the `SA_P-Static` statics |
| 1 | `E-GR-1` | a spatial entity whose containment never reaches a `rec:Building` |
| 1 | `E-FEED-1` | a terminal unit with no feeds row |

Reusable `para:` classes it coins, to take at step 3 rather than re-mint:
`para:Fail_Start_Alarm`, `para:Fail_Stop_Alarm`, `para:Summary_Alarm` (all
`rdfs:subClassOf brick:Alarm`), and `para:Scheduled_Hrs_Duration` /
`para:UnScheduled_Hrs_Duration` (`rdfs:subClassOf brick:Duration_Sensor`). Note
SSC still types its `_TripAlm` points as generic `brick:Alarm` - it did not coin
a Trip alarm class, so distinguishing those by name is new work.
| 9 | `E-PH-1` | surviving placeholders, all `<AliasOf>` |
| 8 | `E-WS-1` | padded cells |
| 4 | `E-TYP-3` | `para:inletSize`, `para:outletSize` and two others used but never defined |
| 3 | `E-PAIR-1` | prop names with no value |
| 1 | `E-GR-1` | `entity:Level7_Office0367` still hanging off nothing |

`check_consistency.py` adds 174 errors and 123 warnings over the same ground the
review sheets cover: 75 `E-CON-2` missing relations, 27 `E-CON-4` corrupted
object cells, 25 `E-CON-3` duplicated relations, 23 `E-CON-10` points with two
external references, and 116 `W-CON-12` units whose rows are split across the
sheet rather than sitting together.

### What 0.5 settles

The top of its spatial and system hierarchy, which is the current house shape:

```
entity:SSC             | rec:Building                    | rec:isPartOf   | entity:QF             | rec:Site
entity:HVAC            | brick:HVAC_System               | brick:isPartOf | entity:QF             | rec:Site
entity:CHWS-MAIN-LOOP  | para:Chilled_Water_Loop_Network | rec:locatedIn  | entity:SSC            | rec:Building
entity:SSC_FCU0001     | brick:Fan_Coil_Unit             | rec:isFedBy    | entity:CHWS-MAIN-LOOP | para:Chilled_Water_Loop_Network
```

- the site is the organisation's code, `entity:QF`, labelled Qatar Foundation
- the building is labelled `<code> Building`
- site-level systems (`entity:HVAC`, `entity:Electrical_System`) are
  `brick:isPartOf` the **site**, not the building
- the chilled water loop is `para:Chilled_Water_Loop_Network`, `rec:locatedIn`
  the building, carries an IFC reference, and terminal units name it with
  `rec:isFedBy`

**One open question it raises.** `entity:CHWS-MAIN-LOOP` carries no building code
yet is `rec:locatedIn entity:SSC`. A second building reusing that bare name
yields one loop located in two buildings the moment both sheets load into one
graph. Site-level systems are genuinely shared and rightly bare; a per-building
main loop is not. QNL therefore writes `entity:QNL_CHWS-MAIN-LOOP`, and the
question is on the open list for the PARA team.
