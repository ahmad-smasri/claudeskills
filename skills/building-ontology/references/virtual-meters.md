# Virtual meters

A virtual meter is a calculated meter: nothing is installed, a formula sums other
points and the result is attached to a space. They are how the front end answers
"what did Level 1 cost last month", and they are the one layer that is never
derivable from a survey or an IO list - **the tiers and the meter types are the
client's decision, so both are asked for before any row is written.**

**A physical meter does not rule out a virtual one.** They answer different
questions: a physical meter reads what is actually imported or delivered at one
point in the plant, a virtual meter is a calculated roll-up over a space. The gap
between them is losses and unmetered load, and seeing that gap is useful - a
building whose physical intake reads 10% above the sum of its virtual floor
meters has something unaccounted for. So **report the overlap, do not suppress
it**: list the physical meters the sheet already carries and what each measures,
say which virtual meters land on the same subject, and let the reviewer decide.

Expect that list to need a human. Physical meters routinely arrive with no
`brick:meters` row at all - all 16 of QNL's were `brick:isPartOf
entity:Electrical_System` with points and nothing saying what they metered - so
the graph cannot answer "what does this measure?" and someone has to say. Ask at
intake, and propose adding the missing `brick:meters` rows: that is the durable
fix, and it is what makes the comparison above possible at all.

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

**This is the one test that actually removes a meter.** An overlap with a
physical meter is reported and kept; a meter with no inputs is deferred, because
it **validates clean, renders a tile, and returns nothing** - indistinguishable
from a broken sensor until someone traces the formula back.

Read this alongside `relationships.md` (the metering predicate family) and
`class-resolution.md` (the ladder, which applies to meter classes like anything
else).

## Ask first - three questions, in this order

**1. Which tiers, and which meter types at each.** Building, Floor, Room - any
one, any two, or all three, and it differs per meter type. Put it to the user as
a matrix, because that is the shape of the answer:

```
                          Building  Floor  Room
para:Utility_Meter            .
para:UPS_Meter                .
para:HW_Meter                 .       .
para:SPWR_Meter               .       .
para:Common_Util_Meter        .       .
para:CHW_Meter                .       .      .
para:HVAC_Meter               .       .      .
para:LTG_Meter                .       .      .
brick:Electrical_Meter        .       .      .
```

Those are the nine classes and the tiers each can sensibly occupy - the menu to
put in front of the client, not a set of ticks. Offer it as a starting point,
not a checklist to complete: every tick has to survive the input test above -
the points its formula would sum must exist.

**Neither delivered building ticks all nine.** QNL and SSC both eliminated
`para:UPS_Meter` (no UPS datapoint) and `para:HW_Meter` (domestic hot water,
no energy point for any), and SSC never had HW to begin with. QNL's answer is
seven classes - Utility at building; SPWR and Common-Util at building and floor;
CHW, HVAC, LTG and Electrical at all three. Once it is
answered the count is fixed arithmetic - a `B` costs 1 meter, an `F` costs one
per level, an `R` costs one per room - so **say the total back before building**:
QNL's matrix over 1 building, 5 levels and 354 rooms is 1,453 meters and 11,624
rows. A client who did not realise room tier meant 1,440 meters gets to say so while it
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

**Count the block: contributionFraction is two rows per unit, not one.** The
`brick:hasPoint` row is the container; the `ref:hasExternalReference` row is what
gives it a series. This is the same failure the meter block had - a point that is
the object of one row and the subject of nothing validates as `W-PT-1` and
nothing else, and there is no other signal that a whole family shipped inert.
Write both rows in the same pass that writes the point.

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
`ELEC_KWH_CALC`. Ask for the calculation engine's register. If it does not exist
yet that is not a reason to defer: both halves are derivable from Dar Cairo's
token and the metered space, so write the rows and hand over a checklist. See
"The telemetry keys - derive them, do not defer them" below. What is never
allowed is a reference row with a blank key.

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

## The row block - eight rows per meter

```
<meter> | <class> | brick:isPartOf       | entity:Metering | para:Metering_System | rdfs:label_en <meter label>
<meter> | <class> | brick:meters         | <metered entity> | <its rec: class>
<meter> | <class> | brick:isVirtualMeter | <blanknode> | <blanknode> | | | brick:value | TRUE
<meter> | <class> | rec:locatedIn        | <metered entity> | <its rec: class>
<meter> | <class> | brick:hasPoint       | <meter>-Consumption | <energy class> | | | rdfs:label_en … | brick:hasUnit …
<meter>-Consumption | <energy class> | ref:hasExternalReference | <blanknode> | ref:TimeseriesReference | | | ref:hasTimeseriesId | <token> | | | para:hasEntityId | <metered space>
<meter> | <class> | brick:hasPoint       | <meter>-Demand      | <power class>  | | | rdfs:label_en … | brick:hasUnit …
<meter>-Demand | <power class> | ref:hasExternalReference | <blanknode> | ref:TimeseriesReference | | | ref:hasTimeseriesId | <token> | | | para:hasEntityId | <metered space>
```

Five things about that block are easy to get wrong:

- **The two reference rows are part of the block, not an afterthought.** Leave
  them out and each point is the object of one `brick:hasPoint` row and the
  subject of nothing at all - it has no series, so the front end draws a tile
  with nothing behind it. It validates as `W-PT-1` and nothing else, which is
  easy to read past when there are thousands of them. QNL shipped 2,920 meter
  points in exactly that state because this section said "six rows"; the fix was
  2,920 rows added after the fact. Count the block: a meter with points is eight
  rows, and a family of 1,453 meters is 11,624.

- **`rdfs:label_en` on the `isPartOf` row is a SUBJECT property** - it labels the
  meter. On the `hasPoint` rows it is an OBJECT property, because it labels the
  point. Same column name, different side, same block. A build script that maps
  property names to sides globally will silently label `entity:Metering` 1,453
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

## The telemetry keys - derive them, do not defer them

Both halves of a virtual meter point's key are derivable without the calculation
engine's register, and Dar Cairo shows both:

```
entity:Dar-Cairo_UPS-Util-Electrical-Virtual-Meter-Consumption | brick:Electrical_Energy_Usage_Sensor |
ref:hasExternalReference | <blanknode> | ref:TimeseriesReference |
| | ref:hasTimeseriesId | UPS_KWH_CALC | para:hasEntityId | Smart Village
```

- **`ref:hasTimeseriesId`** is Dar Cairo's token for the meter class, the same
  literal on every meter of that class: `ELEC_KWH_CALC` / `ELEC_KW_CALC`,
  `Utility_KWH` / `Utility_KW`, `UPS_KWH_CALC` / `UPS_KW_CALC`,
  `HVAC_KWH_CALC` / `HVAC_KW_CALC`, `LTG_KWH_CALC` / `LTG_KW_CALC`,
  `SPWR_KWH_CALC` / `SPWR_KW_CALC`, `COMMON_KWH_CALC` / `COMMON_KW_CALC`,
  `CWPWR_KWTH_CALC` / `CWPWR_KWT_CALC`, `HWPWR_KWTH_CALC` / `HWPWR_KWT_CALC`.
- **`para:hasEntityId`** is the space the meter meters, taken from its own
  `brick:meters` row and written the way the telemetry database writes ids -
  underscores throughout: `QNL`, `QNL_L1`, `QNL_B_001A_Break_Out_Area`. Derive it
  with the same helper the point layer uses, so the two cannot drift.

Dar Cairo puts one **site constant** on all of them instead. That works there
because it has one meter per class; it does not generalise. A multi-tier building
has many meters sharing one class and therefore one token, so a single constant
makes every room-tier CHW consumption point identical and the historian cannot
tell 360 series apart. Use the metered space.

**Derived is not confirmed.** Write the rows, and hand the calculation-engine
team a checklist - `<Building>_virtual_meter_timeseries_pending.csv`, columns
`point, point_class, hasTimeseriesId_TO_CONFIRM, hasEntityId_TO_CONFIRM, meters`
- with both halves filled rather than the entityId blank. Say in the handover
that the keys are derived from Dar Cairo's tokens and the metered space, not read
off a register.

**Only a class Dar Cairo has no token for genuinely defers.** There, and only
there, write the point with no reference row and leave it `W-PT-1` in the pending
file. **Never write a reference row with a blank key** - it asserts a working
telemetry link, reads as finished to every reviewer, and `E-PAIR-1` is the only
thing standing between it and a dead tile.

`para:contributionFraction` is derived the other way round: its tsid is the
literal `ContributionFraction` and its entityId is the key the unit's own
existing points already carry - **read it off them rather than deriving it**, and
report any unit you had to derive.

**One more trap, once the rows exist.** A selected-datapoint reconciliation
(`prune_to_selected.py` and its kin) matches on `ref:hasTimeseriesId`. Meter
points are invisible to it only while they have no key; the moment they get one
they look like unselected points and a re-run deletes the entire metering layer.
Add every meter token to the named-exemption list in the same commit that adds
the rows.

## Removing a meter class later

Classes get eliminated - a client decides a meter has no inputs and never will.
That is a **correction**, so `corrections.md` governs it, and two traps are
specific to this layer:

- **Segments contain other segments.** `CHW-Power-Thermal-Virtual-Meter` contains
  `HW-Power-Thermal-Virtual-Meter`. Removing HW by substring deletes every
  chilled-water meter in the sheet and validates clean afterwards. Anchor on the
  separator - `subject.endswith("_" + segment)` - or name the subjects outright.
- **A class match finds six rows of eight.** The two `ref:hasExternalReference`
  rows are subjected on the POINTS, whose class column names a sensor class, not
  the meter's. Match the meter and both its points, and assert the removal is a
  whole number of eight-row blocks.

Remove the class from the tier matrix **and** from the declaration list, or the
next rebuild re-adds a class with nothing under it - `W-CLS-1`. Better: have the
generator emit only what the matrix uses, so the two cannot drift.

A meter of a class no tier uses should also come out of the pending file: a
calculation team asked to build a series for a meter that no longer exists will
build it.

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

## Report what you did not build, and what overlaps

```
Deferred - the points its formula would sum do not exist:
  brick:Water_Meter             - no potable-water point in the building
  para:Occupant-Wellbeing_Meter - temperature and humidity available; CO2, TVOC,
                                  PM, illuminance, noise and occupancy all absent

Built, and overlapping a physical meter - kept deliberately, not duplicates:
  para:Utility_Meter at building tier   vs entity:QNL_Total-Energy
  para:CHW_Meter at building tier       vs entity:QNL_CHWS-MAIN-LOOP_Energy-Meter
```

A deferred meter reopens the moment the missing points arrive, so it belongs in
the handover as pending work; say which points are missing, not just that some
are. An overlap is not pending work - it is a pairing the front end can show side
by side, and naming it stops the next reviewer raising it as a defect.

## Why not to build this by hand

The layer is a cross-product - meter types x tiers x spatial entities - and every
block is identical bar three substitutions. Generate it from the tier matrix
against the *live* ontology, never from a separately maintained room list: QNL's
first hand-built attempt took 90 minutes and none of its 353 room identifiers
matched the sheet it was meant to merge into, because it had been built before the
identifiers were normalised. `projects/QNL/add_virtual_meters.py` is the worked
example.
