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
| `E-PH-1` | an unresolved `<placeholder>` cell |
| `E-PAIR-1` | a prop name with no value |
| `E-PAIR-2` | a prop value with no name - usually a pair shifted one column left |
| `E-LBL-1` | a label contains punctuation the label rule strips; the message shows the fix. Not applied under `--label-style verbatim` |
| `E-TYP-1` | one entity declared with more than one type |
| `E-TYP-2` | a `brick:`/`rec:`/`ref:` term that does not exist in Brick 1.4 - almost always a typo |
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

### QF SSC draft 0.5 review (`QF_SSC_Ontology_draft0.5_review.xlsx`, 5,119 rows)

Replaces draft 0.4, which is gone from the repo. Eleven sheets:
`SSC_Ontology_Ver0.5` holds the triples, `Claude Log` records the review
exercise that produced `check_consistency.py`, and nine `*_Comparison` /
`*_Check` sheets hold its per-family findings.

**The workbook opens on `VAV_Comparison`, not on the ontology.** Every script
here picks the sheet by the header contract rather than by `.active` for exactly
this reason. Any new tool that reads a reference model must do the same or it
will silently read a review sheet.

Much improved on 0.4 - 451 errors against 1,040, and the feeds placeholders that
made 0.4 unusable as a feeds reference are largely gone. Still not clean, so do
not copy blindly:

| Count | Code | What it is |
|---|---|---|
| 2,940 | `I-TYP-6` | valid Brick terms with no Dar Cairo precedent - advisory |
| 320 | `W-TYP-5` | alias classes |
| 260 | `E-TYP-2` | terms not in Brick 1.4, e.g. `brick:Heater`; `brick:ccupied_Air_Temperature_Setpoint` still carries its dropped leading `O` |
| 96 | `E-LBL-1` | labels carrying source punctuation - expected under SSC's verbatim label style, so run it with `--label-style verbatim` |
| 55 | `E-TYP-1` | entities typed more than one way |
| 53 | `W-DUP-1` | duplicate rows |
| 20 | `W-LBL-2` | entities with no label, `entity:CHWS-MAIN-LOOP` among them |
| 15 | `E-FEED-1` | terminal units with no feeds row, all CRACs |
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
