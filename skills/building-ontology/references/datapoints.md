# Datapoints: from the IO list to point triples

Equipment carries points; points carry a timeseries. This is the procedure for
turning a *selected datapoint list* plus a *historian / IO list* into the
`brick:hasPoint`, `brick:hasPart` and `ref:TimeseriesReference` rows, resolving
every point's class the same disciplined way a room or an asset is resolved.

Two source files drive it, and they play different roles:

- **The selected list** (e.g. `Selected_PARA_OS_Data_Points`) - the points the
  client chose for this building. This is *what to model*.
- **The historian / IO list** (e.g. `..._Historian_IO_list`) - every point the
  BMS can actually serve. This is *what exists*. A historian export routinely
  splits analog and discrete points across two sheets; both are read (see
  `known-issues.md`).

A selected point that is **not** in the historian resolves to an empty
timeseries - the front end draws a tile with no data behind it. So the first
move is always to confirm the selected list against the historian, and only ever
model the intersection. Over-inclusion is worse than omission.

A word on a real hazard, taken from a live file: the selected-points workbook
had **two independent lists side by side** - a clean `TagName` column and a
separate, differently-sorted block of `DP Name`/`Point-Name` columns that agreed
with it on 15 of 2,434 rows. Take the tag column as the authority and derive the
equipment/part/point split from the tag itself; never trust a parallel
descriptive column to name or decompose a point.

## The tag is the structure

A datapoint tag reads `<BUILDING>_<equipment>[_<part>].<point>`, e.g.
`QNL_AHUB001_SupFan.kW` (part `SupFan`, point `kW`) or `QNL_AHUB001.EnableDisableCmd`
(a point directly on the equipment). The equipment token is the join key back to
the register - match it against the register's own tags, longest first, so an
asset tag that itself contains an underscore is not mistaken for a part. It is
also the join to the ontology identifier, which may differ (QNL's AHUs are
`entity:QNL_AHU_B_001` but the telemetry says `QNL_AHUB001`); the crosswalk
carries that mapping.

## Collapse to signatures, resolve once

Hundreds or thousands of selected rows collapse to a few dozen distinct
`(family, part, point)` **signatures**. Resolve each signature once - its class,
its unit - and apply it to every unit that carries it. This turns the class
ladder from thousands of lookups into a reviewable table of ~100 rows, and it is
the artefact a human checks: one row per signature, its proposed class, and which
source settled it (the *ledger*).

## Part, or point?

A token before the dot is a **part** only when it resolves to an *equipment*
class; if it resolves to a *point* class it is part of the point's name and the
point hangs directly on the equipment.

- `SupFan` → `brick:Supply_Fan` (equipment) → a part; `SupFan.kW` is a power
  point *under the part*.
- `MixAirTemp` → `brick:Mixed_Air_Temperature_Sensor` (point) → not a part;
  `MixAirTemp.PV` is a point *on the equipment*, named for the whole token.

Curate the part tokens per family rather than guessing - on one building the 65
AHU tokens split cleanly into 9 components and 56 measurements with no borderline
cases. A part gets `brick:hasPart` with its own class (resolved through the same
ladder), and its points hang under it: `HEX → hasPart IsoVlv (Isolation_Valve) →
hasPoint OpenSts`. A **subpart** is a part's part; declare the part before the
subpart, the subpart before its points. Do not decompose past where a point
actually attaches.

## The class ladder, for every point and part

Same shape as the class ladder for equipment (`class-resolution.md`), in this
priority:

1. **Dar Cairo** - the point/part class its own `brick:hasPoint` / `brick:hasPart`
   objects use. This is the primary reference; match on the class name *and* on
   the English `rdfs:label_en` its entities carry, because Dar Cairo names points
   in dashed English while the BMS names them in abbreviated camelCase.
2. **Brick 1.4** - the preferred term, never a deprecated one or an alias unless
   the estate has standardised on it and it is recorded in `accepted-terms.txt`
   (as `brick:CRAC`, `brick:HVAC_System` and the deprecated CHW temperature
   sensors are).
3. **QF SSC** - the sister sheet, for a term the first two lack but SSC coined.
4. **`para:`** - mint a subclass of the closest Brick parent, and list it in the
   handover. A point with no sensible parent is `owl:Class rdfs:subClassOf
   brick:Point`; use the kind to pick the parent (`Sensor`→`brick:Sensor`,
   `Setpoint`→`brick:Setpoint`, `Status`→`brick:Status`, `Command`→`brick:Command`,
   `Alarm`→`brick:Alarm`).

`scripts/point_class_ledger.py` walks this ladder automatically and always
returns a class with its provenance. Three guards stop it from confidently
returning the wrong one - each earned its place by catching a real mistake:

- **Kind.** A token's suffix fixes what *kind* of point it is, and the Brick
  class name ends in the same word. `RtnHumiditySP` is a setpoint, so it cannot
  match `Return_Air_Humidity_Sensor` however the words overlap. Order the suffix
  table so `FTSP` reads as fail-to-stop, not as an `SP` setpoint.
- **Device.** A point on a damper cannot be a valve point. Dar Cairo uses
  `Valve_Position_Command` far more than `Damper_Position_Command`, so on
  "position command" alone the valve wins on usage - the part's device has to
  agree with the class's device.
- **Generic descriptions.** `"Process Value"` passes an is-it-English test and
  identifies nothing; a quarter of historian descriptions merely repeat the
  equipment name. When the description is generic or self-referential, expand the
  tag instead.

The automatic result is a first pass. A curated override map (the project's
`CANON`) fixes the handful the fuzzy ladder mis-maps or names clumsily, keyed by
the point token, each entry tagged with the ladder step it represents. Inspect
every `auto` decision by hand - on one building three of the first twenty-four
were wrong before the guards went in.

## Units come from the IO list, mapped to the estate's codes

The historian gives a unit string (`°C`, `%`, `kWh`, `%rH`); map it to the code
the estate already uses (`unit:DEG_C`, `unit:PERCENT`, `unit:KiloW-HR`,
`unit:PERCENT_RH`), and a discrete point with no unit to `unit:UNITLESS`. Where
the IO list's unit is physically wrong, override it and log the assumption - a
power sensor reading `%`, an air-flow sensor reading `m/s` (a velocity), a
humidity sensor reading `%` where the estate uses `%rH`, a "flow" reading
`UNITLESS`. The estate's own usage on that class is the arbiter, not the one
number in the IO cell.

## Every point carries three things

`rdfs:label_en`, `brick:hasUnit`, and a `ref:TimeseriesReference` blank node with
`ref:hasTimeseriesId` (the historian tag) and `para:hasEntityId` - **on the
point, never on the equipment.** The IFC reference stays on the physical thing;
the timeseries reference is the point's own external reference.

## Orphans: a selected point whose equipment the register never named

A selected datapoint whose equipment has no register row is not dropped - it is
an **orphan**, modelled with everything the sources actually say and nothing they
do not (assumption-log rule; see the QNL-021/023/024/025 entries for worked
cases). The register is the only source for position and feeds, so an orphan gets
its class, a label, an IFC reference and its points, but **no `rec:locatedIn` /
`rec:isFedBy`**, and no `rec:feeds` unless the feed is a function rather than a
place (a chilled-water pump feeds the loop wherever it sits; a CRAC feeds a
specific room the register would have named, so its feeds is left unasserted).
Each orphan is one row in the assumption log. It raises accepted `E-FEED-1` /
`W-GR-2` findings, which the log documents.

Distinguish three shapes of orphan:

- **An orphan unit** - a real asset the register omits (a roof DX, an extra CCU,
  a second pump). Model it like any equipment of its family, minus location and
  feeds.
- **An orphan sensor** - the tag *is* the point (`QNL_CCU_QTelRmTemp.PV`, a room
  monitor with no owning unit). The entity is the sensor, typed as its
  measurement class, `brick:isPartOf` the system it belongs to, carrying its
  timeseries. Do not invent an equipment to hang it on, and do not assume it
  belongs to a register unit that merely shares its room.
- **A building- or system-level point** - a single loop/plant/metering
  measurement (`CHW_BldgSupTemp`, `ELEC_MFM_MVP1`, `TotalEnergy`). Attach it to
  the parent its Dar Cairo / SSC counterpart uses, not to a unit:
  - CHW plant instrumentation → the chilled-water loop entity, with a
    `brick:Building_Chilled_Water_Meter` sub-part for the energy points (Dar
    Cairo's `CHWS-MAIN-LOOP_Energy-Meter` shape).
  - Electrical metering → one `brick:Electrical_Meter` per meter under the
    electrical system, each carrying its power/energy points; a building total is
    a `para:Utility_Meter`. Both Dar Cairo (1,456 meters) and SSC (46) model
    electrical measurement this way.
  - A loose room/space point with no equipment → an orphan point `isPartOf` the
    HVAC system.

  When even the parent is unclear, ask - a point's parent is normally its
  equipment; only when there is genuinely no equipment is it a building-level
  point.

## Validate the points, both directions

- **Forward** (`scripts/check_io_list.py --io`): every point written to the sheet
  must trace back to a historian tag - `E-IO-1` is over-inclusion, an empty
  timeseries. Drive this to **zero**.
- **Reverse**: the historian has far more tags than were selected; those unmatched
  rows (`W-IO-2`) are expected, not a defect.
- **Consistency** (`scripts/check_consistency.py`): points genuinely differ per
  unit - not every VAV has a room-temperature sensor, not every DX conditions a
  space. The checker flags the divergence; confirm from the historian that it is
  real, and do not force uniformity, because a phantom point is exactly the
  over-inclusion this whole workflow exists to prevent.

## The order of operations

1. Confirm the selected list against the historian; carry only the intersection.
2. Collapse to `(family, part, point)` signatures.
3. Resolve each signature's class through the ladder; curate the few the
   automatic pass gets wrong; record the ledger with provenance.
4. Emit `hasPart` (with its class) then `hasPoint`, each point with label, mapped
   unit, and a timeseries reference on the point.
5. Model orphans - units, sensors, building-level points - and log each.
6. Validate forward (0 `E-IO-1`), read the consistency findings as genuine
   heterogeneity, and confirm every selected+historian tag is now in the sheet.
