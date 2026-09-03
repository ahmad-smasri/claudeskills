# Virtual meters

A virtual meter is a calculated meter: nothing is installed, a formula sums other
points and the result is attached to a space. They are how the front end answers
"what did Level 1 cost last month", and they are the one layer that is never
derivable from a survey or an IO list - **the tiers and the meter types are the
client's decision, so both are asked for before any row is written.**

**A virtual meter exists only where a physical one does not.** That is the whole
point of the layer - it fills the gaps in the metering the building actually has.
Where a real meter already measures the thing, a virtual meter beside it is a
second answer to the same question with no data behind it, and the front end has
no way to choose. So before generating a tier, **list the meters the sheet
already carries and what each one measures**, and suppress every pair a physical
meter covers. On QNL that removed the building-tier `para:Utility_Meter`, because
`entity:QNL_Total-Energy` was already one and had a live historian tag.

Expect this to need a list rather than a query. Physical meters routinely arrive
with no `brick:meters` row at all - all 16 of QNL's were `brick:isPartOf
entity:Electrical_System` with points and nothing saying what they metered - so
the graph cannot answer "is this already metered?" and a human has to say. Ask
for the answer at intake, name each suppression against the physical meter that
justifies it, and log it. Adding the missing `brick:meters` rows to the physical
meters is the durable fix, and worth proposing.

**And only where the points it would sum actually exist.** A virtual meter is a
formula; a formula with no inputs returns nothing, forever. This is the failure
the tier matrix invites, because a matrix is a grid and a grid tempts you to fill
it. So for each meter type the client ticks, **check the sheet carries the points
its formula would draw on**, and where it does not, say so rather than building
the meter. On QNL that ruled out two families the matrix never asked for:
`brick:Water_Meter`, because the building has no potable-water point at all -
every "water" match was a chilled-water temperature or an air flow - and
`para:Occupant-Wellbeing_Meter`, whose eight-sensor bundle had temperature and
humidity available and no CO2, TVOC, PM, illuminance, noise or occupancy.

This is the more dangerous of the two tests. A meter that duplicates a physical
one is a duplicate a reviewer can see; **a meter with no inputs validates clean,
renders a tile, and returns nothing** - indistinguishable from a broken sensor
until someone traces the formula back. Keep the two reasons apart when you report
them, because they need different answers: a duplicate is dropped, a meter with
no inputs is deferred until the points exist.

Read this alongside `relationships.md` (the metering predicate family) and
`class-resolution.md` (the ladder, which applies to meter classes like anything
else).

## Ask first - three questions, in this order

**1. Which tiers, and which meter types at each.** Building, Floor, Room - any
one, any two, or all three, and it differs per meter type. Put it to the user as
a matrix, because that is the shape of the answer:

```
                          Building  Floor  Room
para:Utility_Meter            x
para:UPS_Meter                x
para:HW_Meter                 x       x
para:SPWR_Meter               x       x
para:Common_Util_Meter        x       x
para:CHW_Meter                x       x      x
para:HVAC_Meter               x       x      x
para:LTG_Meter                x       x      x
brick:Electrical_Meter        x       x      x
```

That matrix is QNL's, and it is a reasonable default to offer - but offer it as a
starting point, not a checklist to complete: every tick has to survive both tests
above, a physical meter already covering it and the points its formula needs
being absent. Once it is
answered the count is fixed arithmetic - a `B` costs 1 meter, an `F` costs one
per level, an `R` costs one per room - so **say the total back before building**:
QNL's matrix over 1 building, 5 levels and 354 rooms is 1,460 meters and 8,760
rows, less whatever the physical-meter rule above suppresses - 1,459 in the end.
A client who did not realise room tier meant 1,440 meters gets to say so while it
is still a sentence rather than a sheet.

**Utility Meter is a building-tier class.** It measures the supply the government
or municipality delivers, and a building has one incoming supply. Electrical
Meters are the sum across sources - UPS, panels, generator - so they belong at
every tier the client wants. *Dar Cairo does not follow this*: it puts a
`para:Utility_Meter` on every floor, chained with `brick:isSubMeterOf`. The rule
above is the house rule and it overrides the reference model here - see
`known-issues.md`.

**2. Whether the terminal units get `para:contributionFraction`.** It is a
**container point for the chilled water consumption of a unit fed by an AHU**,
declared because buildings rarely meter a VAV or CAV's own CHW load. The
`ContributionFraction` series is a placeholder: the backend replaces it with an
internal calculation that apportions the AHU's load across the units it feeds.
So the point is real in the model before any telemetry exists for it - that is
what it is for.

If yes, it goes on **every unit an AHU feeds** - VAV, CAV, PIM, whatever the
building uses - with `ref:hasTimeseriesId` fixed at the literal
`ContributionFraction` and `para:hasEntityId` derived exactly as every other
datapoint on that unit derives it. **Read the entityId off the unit's existing
points rather than deriving it from the identifier**, and report any unit you had
to derive because it has no points to read.

**Skip any unit sitting in a shaft, riser or ceiling void.** Those are cable and
duct spaces; a contribution fraction for one is a number about nothing. Test
`rec:locatedIn` against the room identifier, not the unit's name.

Offer the rest of the Dar Cairo block at the same time, so the user knows it
exists: each PIM there carries the fraction *plus* four derived points -
`_Cooling-Load-Demand-Contribution` (`brick:Thermal_Power_Sensor`),
`_Cooling-Load-Consumption-Contribution` (`brick:Thermal_Energy_Usage_Sensor`),
`_Electrical-Demand-Contribution` (`brick:Electric_Power_Sensor`) and
`_Electrical-Consumption-Contribution` (`brick:Electrical_Energy_Usage_Sensor`).
They only work where the calculation engine publishes those four series.

**3. Where the telemetry keys come from.** Virtual meter points are calculated,
so **the IO-list rule does not reach them** - a field IO list will never list
`ELEC_KWH_CALC`. Their keys come from the calculation engine's register instead.
Ask for it. If it does not exist yet, see "When the keys do not exist" below;
do not write a reference row with a blank key.

## Resolve the meter class through the ladder

Same four steps as anything else, and Dar Cairo answers most of them. These
already exist - reuse, never re-coin:

| Class | Parent | Measures |
|---|---|---|
| `brick:Electrical_Meter` | *(Brick)* | electricity summed across all sources |
| `para:Utility_Meter` | `brick:Electrical_Meter` | the incoming municipal supply |
| `para:UPS_Meter` | `brick:Electrical_Meter` | UPS load |
| `para:HVAC_Meter` | `brick:Electrical_Meter` | electricity drawn by HVAC |
| `para:LTG_Meter` | `brick:Electrical_Meter` | electricity drawn by lighting |
| `para:SPWR_Meter` | `brick:Electrical_Meter` | small power |
| `para:Common_Util_Meter` | `brick:Electrical_Meter` | common-area utilities |
| `para:General_Util_Meter` | `brick:Electrical_Meter` | general utilities |
| `para:Data-Center_Meter` | `brick:Electrical_Meter` | data centre load |
| `para:Generator_Meter`, `para:Solar_Meter` | `brick:Electrical_Meter` | generation |
| `para:CHW_Meter` | `brick:Thermal_Power_Meter` | chilled water thermal |
| `para:HW_Meter` | `brick:Thermal_Power_Meter` | hot water thermal |
| `brick:Water_Meter` | *(Brick)* | water volume |
| `para:Occupant-Wellbeing_Meter` | `brick:Meter` | the IEQ sensor bundle |
| `para:Metering_System` | `brick:System` | the system node all meters hang off |
| `para:contributionFraction` | `brick:Point` | the split fraction (note: lower-case, as Dar Cairo coined it) |

Dar Cairo's labels for `para:Generator_Meter` and `para:Solar_Meter` are swapped -
each carries the other's text. Use the class name, not the reference label.

## Identifiers and labels

**`<metered entity>_<Meter-Type-Segment>`.** The meter's identifier extends the
identifier of the thing it meters, so it sorts beside it and reads without a
lookup. The segments are Dar Cairo's, verbatim:

```
entity:QNL_UPS-Util-Electrical-Virtual-Meter                           building
entity:QNL_L1_HVAC-Util-Electrical-Virtual-Meter                       floor
entity:QNL_B-002_Kitchen_LTG-Util-Electrical-Virtual-Meter             room
entity:QNL_L1_CHW-Power-Thermal-Virtual-Meter                          floor, thermal
```

| Class | Segment |
|---|---|
| `brick:Electrical_Meter` | `Electrical-Virtual-Meter` |
| `para:Utility_Meter` | `Utility-Virtual-Meter` |
| `para:UPS_Meter` | `UPS-Util-Electrical-Virtual-Meter` |
| `para:HVAC_Meter` | `HVAC-Util-Electrical-Virtual-Meter` |
| `para:LTG_Meter` | `LTG-Util-Electrical-Virtual-Meter` |
| `para:SPWR_Meter` | `SPWR-Util-Electrical-Virtual-Meter` |
| `para:Common_Util_Meter` | `Common-Util-Electrical-Virtual-Meter` |
| `para:General_Util_Meter` | `General-Util-Electrical-Virtual-Meter` |
| `para:CHW_Meter` | `CHW-Power-Thermal-Virtual-Meter` |
| `para:HW_Meter` | `HW-Power-Thermal-Virtual-Meter` |
| `brick:Water_Meter` | `Water-Virtual-Meter` |
| `para:Occupant-Wellbeing_Meter` | `Occupant-Wellbeing-Virtual-Meter` |

**Points on a space-tier meter join with a dash**, not a new `_` segment:
`<meter>-Consumption`, `<meter>-Demand`, `<meter>-Target`. This is the one place
the general rule ("a point opens a new `_` segment") does not apply, and it is
Dar Cairo's shape for exactly these meters - 418 rows against the 492 that use
`_` on equipment-tier meters. **`para:contributionFraction` follows the general
rule**, because it hangs off a piece of equipment rather than a space meter:
`entity:QNL_VAV-B-S11-021_Contribution-Fraction`.

Derive the label from the identifier in the build script, one map, so the two
cannot drift: strip the prefix, `_` and `-` become spaces. Point labels are the
meter's label plus the point word.

## The row block - six rows per meter

```
<meter> | <class> | brick:isPartOf       | entity:Metering | para:Metering_System | rdfs:label_en <meter label>
<meter> | <class> | brick:meters         | <metered entity> | <its rec: class>
<meter> | <class> | brick:isVirtualMeter | <blanknode> | <blanknode> | | | brick:value | TRUE
<meter> | <class> | rec:locatedIn        | <metered entity> | <its rec: class>
<meter> | <class> | brick:hasPoint       | <meter>-Consumption | <energy class> | | | rdfs:label_en … | brick:hasUnit …
<meter> | <class> | brick:hasPoint       | <meter>-Demand      | <power class>  | | | rdfs:label_en … | brick:hasUnit …
```

Four things about that block are easy to get wrong:

- **`rdfs:label_en` on the `isPartOf` row is a SUBJECT property** - it labels the
  meter. On the `hasPoint` rows it is an OBJECT property, because it labels the
  point. Same column name, different side, same block. A build script that maps
  property names to sides globally will silently label `entity:Metering` 1,460
  times and leave every meter unlabelled.
- **`brick:isVirtualMeter` carries `brick:value TRUE` and no unit.** It fires
  `W-BN-4`, which suggests `unit:UNITLESS`. Do not add one - a boolean is not a
  dimensionless quantity, and Dar Cairo writes it bare. Name the warning in the
  handover.
- **`rec:locatedIn` on a virtual meter is a house choice, not a Dar Cairo one.**
  Only 124 of its ~5,000 virtual-meter rows carry it and its building electrical
  meter has none, because a calculation does not sit in a room. QNL writes it on
  every meter, pointing at the same entity as `brick:meters`. Ask; either answer
  is defensible, neither is free to change later.
- **`entity:Metering` must be declared before the first meter points at it**, as
  a subject of its own: `entity:Metering | para:Metering_System | brick:isPartOf
  | <site> | rec:Site | rdfs:label_en | Metering System`. Same for every `para:`
  meter class and for the two thermal units. A dangling `entity:Metering` is
  `W-REF-1` and costs the front end its whole metering branch.

Where the client wants a tier chain rather than independent meters, add
`brick:isSubMeterOf` from each child meter to its parent - Dar Cairo's floor
Utility Meters do this. Only add it when asked; it is a claim about how the
formulas nest.

## Units - the trap

| Point | Class | Unit |
|---|---|---|
| Consumption, electrical | `brick:Electrical_Energy_Usage_Sensor` | `unit:KiloW-HR` |
| Demand, electrical | `brick:Electric_Power_Sensor` | `unit:KiloW` |
| Consumption, thermal | `brick:Thermal_Energy_Usage_Sensor` | `para:KiloWt-HR` |
| Demand, thermal | `brick:Thermal_Power_Sensor` | `para:KiloWt` |
| Target | `para:Electric_Power_Target` / `para:Thermal_Power_Target` | as its kind |
| Contribution fraction | `para:contributionFraction` | `unit:UNITLESS` |

**Thermal takes `para:KiloWt`, not `unit:KiloW`.** Written as `unit:KiloW`, a
chilled-water demand point is indistinguishable from an electrical one, and any
dashboard that sums demand across a building's meters double-counts. Dar Cairo is
split on this - its `brick:Thermal_Power_Meter` uses `para:KiloWt` on 81 rows, its
own `para:CHW_Meter` uses `unit:KiloW` on 70 against `para:KiloWt` on 2 - so the
majority is not the authority here; the consequence is. Declare both units, as
Dar Cairo does:

```
para:KiloWt    | qudt:Unit | rdf:type | qudt:Unit | | qudt:symbol | kWt
para:KiloWt-HR | qudt:Unit | rdf:type | qudt:Unit | | qudt:symbol | kWt·hr
```

## When the telemetry keys do not exist

Common, because the calculation engine is usually commissioned after the
ontology. **Do not write a reference row with blank keys.** The row asserts a
working telemetry link, reads as finished to every reviewer, and the validator's
`E-PAIR-1` is the only thing standing between it and a front-end tile with no
data behind it.

Write the points with no reference row, and put every one in a pending file -
`<Building>_virtual_meter_timeseries_pending.csv`, columns
`point, point_class, proposed_hasTimeseriesId, hasEntityId_TO_CONFIRM, meters`.
The points show up as `W-PT-1`, which is the honest state. Propose the
`hasTimeseriesId` from Dar Cairo's token per class - `ELEC_KWH_CALC` /
`ELEC_KW_CALC`, `Utility_KWH` / `Utility_KW`, `UPS_KW_CALC`, `HVAC_KW_CALC`,
`LTG_KW_CALC`, `SPWR_KW_CALC`, `CWPWR_KWT_CALC` / `CWPWR_KWTH_CALC` - and leave
`hasEntityId` blank, because it is the historian's key for the *space* and
nothing in the ontology can derive it.

`para:contributionFraction` is the exception: both halves of its key are known
without the register. The tsid is the literal `ContributionFraction`, and the
entityId is the key the unit's own existing points already carry - **read it off
them rather than deriving it**, and report any unit you had to derive.

## Check it before handover

Beyond the standard passes:

- **`brick:meters`, `brick:isMeteredBy` and `brick:isSubMeterOf` are in
  `check_consistency.py`'s `VARYING_PREDICATES`**, because every meter names a
  different target. If a run reports "`{U} brick:meters entity:X` is on 1/360
  units" hundreds of times, that list has been edited.
- **A virtual meter family should come back with zero `E-CON` findings** - the
  block is identical for every unit by construction, so a finding is a real
  divergence.
- **Mixing physical and virtual meters in one class is expected.** Dar Cairo
  files both under `brick:Electrical_Meter`, so a building with real MFMs will
  report `E-CON-1`/`E-CON-2` between the two populations. Name it in the handover
  rather than minting a `para:` subclass to quiet the checker.
- **Look for a meter that already exists**, per the rule at the top. The
  consistency checker finds the overlap only when the classes happen to match -
  `entity:QNL_Total-Energy` and the proposed `entity:QNL_Utility-Virtual-Meter`
  were both `para:Utility_Meter`, so it did. A physical `brick:Water_Meter`
  against a virtual `para:CHW_Meter` measuring the same loop would pass silently.
  Read the existing meter list yourself; do not wait for the checker.

## Report what you did not build, and which reason

Two different reasons, two different answers, so name them separately in the
handover:

```
Suppressed - a physical meter already covers it:
  para:Utility_Meter at building tier - entity:QNL_Total-Energy is one already,
  with a live historian tag.

Deferred - the points its formula would sum do not exist:
  brick:Water_Meter          - no potable-water point in the building
  para:Occupant-Wellbeing_Meter - temperature and humidity available; CO2, TVOC,
                               PM, illuminance, noise and occupancy all absent
```

A suppressed meter is a closed question. A deferred one reopens the moment the
missing points arrive, so it belongs in the handover as pending work rather than
as a decision. Say which points are missing, not just that some are.

## Why not to build this by hand

The layer is a cross-product - meter types x tiers x spatial entities - and every
block is identical bar three substitutions. Generate it from the tier matrix
against the *live* ontology, never from a separately maintained room list: QNL's
first hand-built attempt took 90 minutes and none of its 353 room identifiers
matched the sheet it was meant to merge into, because it had been built before the
identifiers were normalised. `projects/QNL/add_virtual_meters.py` is the worked
example.
