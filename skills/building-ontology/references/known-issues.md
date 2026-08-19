# Rule codes, source conflicts, and defects in the reference models

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

### Info

`I-TYP-6` - a valid Brick term with no precedent in Dar Cairo. Not a defect;
worth checking that no existing house class covers the same thing.

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

### QF SSC draft 0.4 (`QF_SSC_Ontology_draft0.4.xlsx`, 4,994 rows)

A recent sample, useful for point-set patterns on VAVs and CRACs. It has 1,040
errors and should not be treated as a model of correctness. Specifically:

- **Feeds are placeholders.** Eleven FCUs feed `entity:<FCU_Serving_Location>`;
  nine exhaust fans all feed the same dummy room `entity:Level7_Office0367`;
  `<FedByASSET>` and `entity:<Fedby>` survive on AHUs and CRACs. The user's
  instruction is explicit: disregard this and point `rec:feeds` at the real room.
- `brick:ccupied_Air_Temperature_Setpoint` - a dropped leading `O`.
- `entity:HVAC` typed three ways, including `entity:Electrical_System` used as a
  class.
- 343 labels carrying the raw source punctuation (`1.001_CORRIDOR`).
- `brick:Air_Static_Pressure_Sensor ` with a trailing space.
- 1,512 VAV rows and not one `rec:feeds` row among them.
