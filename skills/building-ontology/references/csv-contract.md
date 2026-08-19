# The CSV contract

## Columns

The canonical nine, from `reference-models/Ontology_headers.xlsx`:

| # | Column | Holds |
|---|---|---|
| 1 | `subject` | the thing being described |
| 2 | `subjectType` | its class - this is the `rdf:type` triple, folded into the row |
| 3 | `predicate` | the relationship or property |
| 4 | `object` | an entity, a class, or `<blanknode>` |
| 5 | `objectType` | the object's class, when the object is an entity |
| 6 | `subject_prop_name` | a metadata property **about the subject** |
| 7 | `subject_prop_val` | its value |
| 8 | `object_prop_name` | a metadata property **about the object** |
| 9 | `object_prop_val` | its value |

Columns 6-9 repeat. Both reference models use **27 columns**: the 5 core columns,
then five `subject_prop_name, subject_prop_val, object_prop_name, object_prop_val`
groups, then one final `subject_prop_name, subject_prop_val` pair. Use
`assets/ontology-template.csv` - it is that header, ready to fill.

Leave a cell blank when it does not apply. Getting subject props and object props
backwards is the single most common authoring mistake: if the row is
`Meter hasPoint Sensor`, the sensor's label and unit are **object** props.

## One row, three triples

| subject | subjectType | predicate | object | objectType |
|---|---|---|---|---|
| `entity:Dar-Cairo` | `rec:Building` | `rec:isPartOf` | `entity:Smart-Village` | `rec:Site` |

```turtle
entity:Dar-Cairo     a rec:Building .
entity:Smart-Village a rec:Site .
entity:Dar-Cairo     rec:isPartOf entity:Smart-Village .
```

## The row shapes

**A - relationship between two entities**

```
entity:Zone-A | rec:Zone | rec:isPartOf | entity:Dar-Cairo | rec:Building | rdfs:label_en | Zone A
```

**B - attaching a data point.** Label and unit describe the point, so they are
object props.

```
entity:Dar-Cairo_Electrical-Virtual-Meter | brick:Electrical_Meter | brick:hasPoint |
entity:Dar-Cairo_Electrical-Virtual-Meter_Avg-Elec-Demand | brick:Electric_Power_Sensor |
| | rdfs:label_en | Dar Cairo Avg Electricity Demand | brick:hasUnit | unit:KiloW
```

**C - a property carrying a value and a unit.** A literal cannot hold a unit, so
the pair lives in an unnamed node.

```
entity:AHU-B1-01_SF_Motor | brick:Motor | brick:ratedPowerInput | <blanknode> | <blanknode> |
| | brick:value | 5.5 | brick:hasUnit | unit:KiloW
```

```turtle
entity:AHU-B1-01_SF_Motor a brick:Motor ;
    brick:ratedPowerInput [ brick:value 5.5 ; brick:hasUnit unit:KiloW ] .
```

**D - external reference.** The blank node is anonymous but **typed**, so the
type goes in `objectType` - not `<blanknode>`.

```
entity:..._Total-Elec-Demand | brick:Electric_Power_Sensor | ref:hasExternalReference |
<blanknode> | ref:TimeseriesReference |
| | ref:hasTimeseriesId | ELEC_KW_CALC | para:hasEntityId | Smart Village
```

IFC references use the same shape with `ref:IFCReference`. **The two reference
models carry different properties on it, so decide which and hold it.** QF SSC -
the recent completed sample - carries **both**, and that is the fuller shape:

```
entity:SSC_AHUB0001 | brick:Air_Handling_Unit | ref:hasExternalReference |
<blanknode> | ref:IFCReference |
| | para:IFC_ID | <the IFC GUID> | | | ref:ifcName | SSC_AHUB0001
```

`para:IFC_ID` is the slot for the real IFC identifier from the BIM model;
`ref:ifcName` is the subject name without the `entity:` prefix and without
spaces, so it is always derivable. Dar Cairo writes `ref:ifcName` alone (535
rows) and defines `para:IFC_ID` once without using it; SSC writes both on all 167
of its IFC rows. Carry both unless the user says otherwise, and leave
`para:IFC_ID` empty rather than inventing a GUID - that is a known, accepted
`E-PAIR-1`, noted in the handover.

Dar Cairo's shorter form, still valid:

```
entity:UPS-02 | brick:Energy_Storage | ref:hasExternalReference | <blanknode> |
ref:IFCReference | | | ref:ifcName | UPS-02
```

An entity can carry more than one external reference - they are independent rows
on the same subject.

### Timeseries references go on points, never on equipment

**A `ref:TimeseriesReference` attaches to a data point.** A point is a
measurement with a key in the telemetry database; a piece of equipment is not,
so it has no timeseries to reference. Both reference models are unanimous: all
1,767 timeseries-reference rows in QF SSC have a `brick:hasPoint` object as their
subject, and not one has a piece of equipment.

```
entity:SSC_FCU0001_Room_Temperature | brick:Room_Air_Temperature_Sensor |
ref:hasExternalReference | <blanknode> | ref:TimeseriesReference |
| | ref:hasTimeseriesId | ROOMTEMP_DEGC | | | para:hasEntityId | SSC_FCU0001
```

`ref:hasTimeseriesId` is the point's key in the telemetry database and comes from
the IO list. `para:hasEntityId` is the entity those keys are grouped under - the
**parent equipment's** tag, which is how the point row carries its owner.

So no IO list means no points, and no points means no timeseries references at
all. Do not put a stub `ref:TimeseriesReference` on the equipment to stand in for
the missing points: it asserts a telemetry key the equipment does not have, and
neither reference model has a single instance of it. Record the gap in the
handover note instead.

**E - defining a new class.** The only shape where `subject` is not an `entity:`.

```
para:Pressure_Independent_Module | owl:Class | rdfs:subClassOf | brick:Terminal_Unit |
| rdfs:label_en | Pressure Independent Module
```

**F - aggregation.**

```
entity:..._Avg-Elec-Demand | brick:Electric_Power_Sensor | brick:aggregate | <blanknode> |
<blanknode> | | | brick:aggregationFunction | mean | brick:aggregationInterval | RPT1H
```

If the aggregation has its own `TimeseriesId` in the external database, it is a
**separate data point** with the same class, its own name and its own external
reference - not a property of the raw point.

## Property names in use

Observed across the reference models, most frequent first:

`rdfs:label_en`, `brick:hasUnit`, `ref:hasTimeseriesId`, `para:hasEntityId`,
`brick:value`, `ref:ifcName`, `rec:installationDate`, `rec:manufacturedBy`,
`brick:aliasOf`, `rec:modelNumber`, `para:format`, `brick:aggregationInterval`,
`brick:aggregationFunction`, `rec:grossArea`, `qudt:symbol`, `rec:levelNumber`,
`rec:seatingCapacity`.

## Units

Units come from QUDT: <https://ontology.brickschema.org/qudt/Unit.html>. The
common set is `unit:UNITLESS`, `unit:KiloW`, `unit:KiloW-HR`, `unit:DEG_C`,
`unit:M2`, `unit:PERCENT`, `unit:HR`, `unit:L-PER-SEC`, `unit:V`, `unit:A`,
`unit:PPM`, `unit:PA`, `unit:LUX`, `unit:MicroGM-PER-M3`, `unit:EPOCH`.

Where QUDT genuinely has none - tariffs, emission factors, degree-days - PARA
mints one under `para:`: `para:EGP-PER-KiloW-HR`, `para:USD-PER-EGP`,
`para:KiloGM-CO2-PER-KiloW-HR`, `para:CDD_DEGC_CALC`. Check
`references/data/units.csv` before minting another.

Use `unit:UNITLESS` for dimensionless quantities. Never leave the unit blank on
something quantitative.
