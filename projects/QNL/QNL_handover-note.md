# QNL ontology — handover note

**Deliverable:** `QNL_Ontology.xlsx` (also `QNL_Ontology.csv`) — 7,030 rows on the
27-column PARA header. Validate with
`validate_ontology.py QNL_Ontology.xlsx --label-style verbatim`. Supporting files:
`QNL_identifier_crosswalk.csv`, listing every source identifier against the
identifier used in the sheet and its label; `QNL_datapoint_ledger_v2.xlsx`, the
reviewed class decision behind every point signature; and the **QNL sheet of
`Assumption_Log.xlsx`**, the itemised record of every departure from what the
sources literally say. This note summarises; the log is the register, and the two
must not disagree.

**Sources:** `QNL_Room_Names_for_Ontology.xlsx` (336 rooms),
`QNL_Assets_Location_Relationships.xlsx` (449 assets across AHUB / VAV / CAV / FCU),
`Selected_PARA_OS_Data_Points_v4.0.xlsx` (the selected points, per unit) and
`QNL_Historian_IO_list_CP2.xlsx` (engineering units and historian ids). All four are in
`sources/`; the build reads them directly, so it is reproducible with `build_qnl.py`.

## What is in the sheet

| Layer | Rows | Content |
|---|---|---|
| Extensions | 1 | `para:Chilled_Water_Loop_Network` |
| Site + Building | 1 | `entity:QNL` `rec:isPartOf` `entity:QF` |
| Levels | 4 | `entity:QNL_B` → "Basement", `_L1` → "Level 1", `_L2` → "Level 2", `_T1` → "Terrace 1" |
| Rooms | 336 | each `rec:isPartOf` its level |
| Systems | 2 | `entity:HVAC` `brick:isPartOf` `entity:QF`; `entity:CHW-System` under it |
| Chilled water loop | 3 | `entity:QNL_CHWS-MAIN-LOOP` — `brick:isPartOf` CHW-System, `rec:locatedIn` the building, + IFC reference |
| Equipment | 2,230 | 15 AHU, 246 VAV, 51 CAV, 137 FCU |
| Points | 4,448 | 2,224 points (each a `brick:hasPoint` row + its `ref:TimeseriesReference` row) — every selected point on AHU, VAV, CAV and FCU |

Per asset: `rec:locatedIn` → its room, `brick:isPartOf` → `entity:HVAC`,
`rec:isFedBy` → its upstream source,
`ref:hasExternalReference` → an `ref:IFCReference` blank node, and for the terminal units
(VAV, CAV, FCU) `rec:feeds` → the room it serves. AHUs get no `rec:feeds` row — see "one
direction" below.

Per point: a `brick:hasPoint` row on the equipment carrying the point's class,
`rdfs:label_en` and `brick:hasUnit`; and a `ref:TimeseriesReference` row on the point
carrying `para:hasEntityId` (its unit's BMS tag) and `ref:hasTimeseriesId` (the
historian SourceTag) — see "The point layer" below.

## Decisions taken, per your answers

**Predicate direction — one direction, held throughout.** Equipment-to-equipment links
are always stated as `rec:isFedBy` (downstream names its source); equipment-to-space
links are always stated as `rec:feeds` (terminal unit names the room it serves). No link
is stated twice. The AHU → VAV/CAV chain therefore appears once, on the VAV/CAV row:
`entity:VAV_B_S11_024 rec:isFedBy entity:AHUB011`. AHUs have no `rec:feeds` row
because they do not serve a room directly — the 297 VAV/CAV rows carry that chain.

**Room Tag used for both `rec:locatedIn` and `rec:feeds`** on terminal units; for AHUs
it is a plant room, so `rec:locatedIn` only. 53 VAVs carry a level token that differs
from the level of their room — e.g. `entity:VAV_2F_S12_001` against
`entity:QNL_L1_001_OPEN_READING_AREA`. You confirmed these are open-roof spaces running
from the served level up to the level the box sits on, so the unit is genuinely located
in and feeding the same volume. Both rows stand as written.

**Level identifiers keep the source codes; labels spell them out.** The identifiers stay
`entity:QNL_B` / `_L1` / `_L2` / `_T1`, matching the level segment your room tags carry,
but `rdfs:label_en` reads "Basement", "Level 1", "Level 2", "Terrace 1" — `T1` confirmed
by you as the terrace level. No
`rec:levelNumber` is asserted. `B` is typed `rec:BasementLevel`; the other three are
`rec:Level`.

**Identifiers taken from the source, regularised to one shape.** Every asset carries the
building code in front of its register tag, QF SSC style — SSC subjects read
`entity:SSC_FCU0001`, so QNL reads `entity:QNL_FCU_1F_056` and
`entity:QNL_VAV_B_S11_024`. **Tags are otherwise untouched**; only `QNL_` was added, so
they remain the BMS join key.

The one exception is the AHUB family, at your direction: `AHUB002` becomes
`entity:QNL_AHU_B_002`, so all four families now parse as `TYPE_LEVEL_COUNT`. All 15 are
in the crosswalk, and the 297 VAV and CAV `rec:isFedBy` rows point at the new form. `ref:ifcName` and `rdfs:label_en` carry the same prefixed form,
as SSC does with `SSC_AHUB0001`.

Rooms keep their name text but are rebuilt to a single shape,
`entity:QNL_<level>_<number>_<name>`, because the schedule was not consistent about it.
285 of the 336 rooms already wrote the level and the room number as separate segments
(`QNL_B_034_MEETING_ROOM`); **51 did not** and have been brought into line:

| Source | In the sheet |
|---|---|
| `entity:QNL_B036_REST_REST_ROOM_WOMEN` | `entity:QNL_B_036_REST_REST_ROOM_WOMEN` |
| `entity:QNL_B-ST-01_ST-01` | `entity:QNL_B_ST-01_ST-01` |
| `entity:QNL_L1023_1_CORRIDOR` | `entity:QNL_L1_023_1_CORRIDOR` |
| `entity:QNL_L2-L-1_1_L-1` | `entity:QNL_L2_L-1_1_L-1` |
| `entity:QNL_ST-04_ST-04` | `entity:QNL_B_ST-04_ST-04` |

Only the join between segments changed — no name text, no room number, no disambiguating
tag (`REST`, `COR`, `BOH`) was altered, and no typo was fixed. The other edit anywhere is
stripping the trailing space from `entity:QNL_L2_018_GROUP_STUDY_ROOM_8`, which the
validator rejects outright (`E-WS-1`).

**Only one of the 51 is referenced by your assets sheet** —
`entity:QNL_L1023_2_CORRIDOR`, now `entity:QNL_L1_023_2_CORRIDOR` — so the join to the
register survives almost untouched. All 51 are listed in
`QNL_identifier_crosswalk.csv`, which is where the source→ontology mapping lives.

Seven identifiers had to be invented, because no source supplies them:
`entity:QF`, `entity:QNL`, the four levels `entity:QNL_B` / `_L1` / `_L2`
/ `_T1` (matching the level segment inside your room tags), and `entity:QNL_CHWS-MAIN-LOOP` for
the `CHILLED WATER LOOP` value in the Fed By column.

**The site is `entity:QF`, the same entity QF SSC uses**, not a second name for the
same place — SSC's current sheet writes
`entity:SSC rec:Building rec:isPartOf entity:QF rec:Site`, labelled `SSC Building` and
`Qatar Foundation`. QNL follows exactly: `entity:QNL` labelled `QNL Building`, pointing
at the same `entity:QF`. Sharing the site entity is what lets the two buildings' sheets
join when the converter loads them into one graph; spelling it differently in each would
silently produce two unrelated sites.

**The chilled water loop follows SSC 0.5's shape, with one deliberate departure.** 0.5
writes `entity:CHWS-MAIN-LOOP`, types it `para:Chilled_Water_Loop_Network`, gives it a
`rec:locatedIn` row pointing at the building and an IFC reference, and has terminal units
name it with `rec:isFedBy`. QNL copies all of that.

The departure is the building code. **SSC's loop carries none, yet is
`rec:locatedIn entity:SSC`** — so if QNL reused the bare name, the converter would load
one loop located in two buildings the moment both sheets went into the same graph. Site
level systems like `entity:HVAC` and `entity:QF` are genuinely shared and rightly bare; a
per building main loop is not. QNL therefore writes `entity:QNL_CHWS-MAIN-LOOP`. **If QF
treats this as one shared district loop rather than one per building, say so and I will
drop the prefix** — but then SSC's `rec:locatedIn entity:SSC` row needs revisiting too.

**Labels follow QF SSC: the source text with underscores read as word breaks.** SSC
writes `1.001 CORRIDOR` — the dot between level and room number survives, and so do
dashes and slashes; only `_` becomes a space. QNL rooms read `<level>.<number> <name>`:
`B.063 PLANT ROOM 01`, `B.237 CORRIDOR`, `L1.023 1 CORRIDOR`, `B.ST-01 ST-01`. Assets
read their register tag under the same rule: `QNL AHU B 011`, `QNL VAV B S11 024`.

Label and identifier are built from the same parsed `(level, number, name)` triple, so
they cannot drift apart. No punctuation is stripped and no typo is fixed. This is not the
PARA label rule, which would give `B 063 PLANT ROOM 01`; `E-LBL-1` is therefore switched
off with `--label-style verbatim`, and every other rule stays in force.

`QNL_identifier_crosswalk.csv` lists every source identifier against the identifier used
in the sheet and its label — 336 rooms and 449 assets. 51 room identifiers differ; every
asset identifier is unchanged.

## Classes used

| Source | Class | Basis |
|---|---|---|
| AHUB | `brick:Air_Handling_Unit` | Dar Cairo, 697 rows |
| FCU | `brick:Fan_Coil_Unit` | Dar Cairo, 936 rows |
| VAV | `brick:Variable_Air_Volume_Box` | Brick 1.4 preferred term; no Dar Cairo precedent |
| CAV | `brick:Constant_Air_Volume_Box` | Brick 1.4 preferred term; no Dar Cairo precedent |
| CHILLED WATER LOOP | `para:Chilled_Water_Loop_Network` | Dar Cairo, 127 rows; already in the para registry |

`para:Chilled_Water_Loop_Network` is defined in row 2 of the sheet for readability,
but it is an existing registry class, not a new coinage. 1,188 `I-TYP-6` info lines
are the VAV and CAV classes — valid Brick 1.4, simply the first time this house has
used them.

### New `para:` class proposed for PARA-team review

Introduced by the datapoint layer (see the datapoint ledger), one genuinely new class:

| Class | Parent | Label | Why it is new |
|---|---|---|---|
| `para:Trip_Alarm` | `brick:Alarm` | Trip Alarm | The fan `TripAlm` points (`SupFan`/`RtnFan` trip alarms on the AHUs). No Dar Cairo, Brick 1.4 or SSC precedent for a trip-specific alarm class. It follows SSC's own alarm-splitting pattern — SSC coined `para:Fail_Start_Alarm` and `para:Fail_Stop_Alarm` under `brick:Alarm`, and QNL reuses both of those — but SSC types its own `_TripAlm` points as the bare `brick:Alarm`, which the reviewer has ruled out for anything but a literal general/summary alarm. `para:Trip_Alarm` gives the trip alarms a class of their own so they are distinguishable by point rather than lumped in with every other alarm. |

Everything else in the datapoint layer resolves to an existing Dar Cairo, Brick 1.4
or SSC class — including the reused SSC classes `para:Fail_Start_Alarm`,
`para:Fail_Stop_Alarm`, `para:Scheduled_Hrs_Duration` and
`para:UnScheduled_Hrs_Duration`, which are taken as-is rather than re-coined.

## The systems layer

`entity:HVAC` `brick:isPartOf` `entity:QF`, labelled "HVAC System", and all 449 assets
plus the chilled water loop `brick:isPartOf` it. This is what the front end builds its
system tree from — the `brick:isPartOf` chain here, plus Brick's own class hierarchy for
the layer below, since `brick:Air_Handling_Unit` is already declared under
`brick:HVAC_Equipment` in the ontology the viewer loads. No `entity:Air_Handling_Unit`
was minted between the two: neither reference model has one, and it would restate what
Brick already says.

**The loop sits under `entity:CHW-System`.** I said last round that a CHW-System node
would hold only the loop and so would not earn its place. That was wrong on a fact I
should have checked: **QF SSC 0.5 already declares `entity:CHW-System`**, bare and
site-level under `entity:HVAC`, holding its four chilled water booster pumps and five
heat exchangers. QNL is not creating a node — it is joining one that has nine members,
the same way both buildings already share `entity:QF` and `entity:HVAC`. Once the
converter loads both sheets, the group has ten.

Worth flagging back to the SSC side: **SSC leaves its own `entity:CHWS-MAIN-LOOP` outside
`CHW-System`**, attached only by `rec:locatedIn`. A distribution loop is part of the
chilled water system by any reading, so that looks like an oversight rather than a
decision.

**The system is typed `brick:HVAC_System`**, matching both reference models. Brick 1.4
lists it as an alias for `brick:Heating_Ventilation_Air_Conditioning_System` and the class
ladder would take the preferred term, but consistency across the estate wins: the front
end keys off `HVAC_System`. The override is recorded in
`references/data/accepted-terms.txt` with its reason, so the alias no longer raises a
warning on every system row.

## External references — the SSC shape

Each asset carries one `ref:hasExternalReference` row, matching QF SSC's IFC shape:

```
entity:AHUB011 | brick:Air_Handling_Unit | ref:hasExternalReference | <blanknode> |
ref:IFCReference | | | para:IFC_ID | <empty> | | | ref:ifcName | AHUB011
```

`para:IFC_ID` is the slot for the real BIM GUID and is empty, as you asked.
`ref:ifcName` is filled with the entity name, which is derivable and is what both
reference models put there.

**`ref:TimeseriesReference` rows sit on the points, not the equipment** — every one
of SSC's 1,767 does the same. Each point carries one, with `ref:hasTimeseriesId` set
to the historian `SourceTag` from the IO list (e.g. `QNL_AHUB001_CHWRtnTemp.PV`) and
`para:hasEntityId` naming its unit. All 2,215 are filled; none is a placeholder.

## Validator result

```
python3 validate_ontology.py  QNL_Ontology.xlsx --label-style verbatim
7030 rows, 3020 typed entities, 2 para: definitions
454 errors, 66 warnings, 3803 advisories

python3 check_io_list.py      QNL_Ontology.xlsx --io sources/QNL_Historian_IO_list_CP2.xlsx
0 errors, 9386 warnings          <- every point traces to a real IO row

python3 check_consistency.py  QNL_Ontology.xlsx --io sources/QNL_Historian_IO_list_CP2.xlsx
78 errors, 0 warnings, 245 advisories
```

**452 of the 454 errors are `E-PAIR-1`, the deliberate empty `para:IFC_ID`** on the
451 assets and the loop. The other 2 are `E-FEED-1` on the unregistered units above,
accepted in the assumption log. Paste the IFC GUIDs into `object_prop_val` and the sheet
validates clean. The timeseries placeholders are gone — every point now carries a real
historian id.

**66 warnings: 64 `W-TYP-4`, all deliberate** — the deprecated CHW temperature classes
kept per your decision. Each carries Brick's own mitigation text; the ledger note names
the entering/leaving replacement.

**`check_io_list.py` reports 0 `E-IO-1`**: not one point in the sheet is invented. The
9,386 `W-IO-2` are IO rows with no point here — the out-of-scope families and the
unselected points, both covered under "Left out".

**The 78 consistency errors are real per-unit variance, confirmed against the IO list**,
not defects: `E-CON-1`/`E-CON-2` are the 44 VAVs that genuinely carry `RmTemp` where the
other 202 do not, and the pointless `VAV_1F_S15_039S` described above. Passing `--io`
resolved 209 of the original 287 findings into `I-CON-2` advisories — the IO list
adjudicating what a row-level read could not. An earlier version of this note said `W-REF-1` flagged `entity:QF` as
undeclared. That was my check being too strict, not a defect in the sheet: `entity:QF` is
typed `rec:Site` and labelled "Qatar Foundation" on QNL's building row, which is exactly
how the house style declares a site, a sub-system or a part — on the row that references
it, class in `objectType` and label in an object prop. The rule now flags only an entity
that is never given a class anywhere, which is a real dangling reference. Apart from
the 60 deliberate `W-TYP-4` deprecation warnings covered above, nothing is outstanding:
every entity is labelled, every terminal unit has a feeds row and a location, and every
spatial entity connects up to `rec:Building`.

Without `--label-style verbatim` you also get 771 `E-LBL-1` — that is the PARA label
rule objecting to the SSC label style, and it is expected.

## The point layer

Points join three sources, all in `sources/`:

| Source | What it supplies |
|---|---|
| `Selected_PARA_OS_Data_Points_v4.0.xlsx` | **which** points are selected, per unit — one row per unit × point, all "Must Have" |
| `QNL_Historian_IO_list_CP2.xlsx` | each tag's engineering unit, historian `SourceTag` and analog/discrete kind |
| `QNL_datapoint_ledger_v2.xlsx` | the reviewed **class** decision per point signature, and a clean descriptor |

**All 2,215 selected points on the four families are in.** Per-unit membership now
comes from the Selected sheet rather than being inferred, so the partial-coverage
signatures that waited for this data are placed exactly where they belong: 509 on the
15 AHUs, 779 on the 246 VAVs, 156 on the 51 CAVs, 771 on the 137 FCUs. Every one of the
2,236 selected 4-family tags mapped to a ledger class with nothing left over, and every
point traces back to a real IO row (`check_io_list.py`: **0 `E-IO-1`**).

**Timeseries ids are filled.** `ref:hasTimeseriesId` carries the IO list's `SourceTag`
for all 2,215 points — no placeholders remain in the point layer.

**Scope: AHU, VAV, CAV and FCU only, at your direction.** The Selected sheet also covers
CCU, EF, DX, HEX, KEF, SEF, TEF and GEN — 533 further points on equipment that is not in
the asset register and so not in this sheet. Those are the bulk of the 9,386 `W-IO-2`
warnings (IO rows with no point here), together with the unselected points; both are
deliberate scope, not omissions.

**Engineering units: the IO list beats the Selected sheet, and the class beats both.**
The Selected sheet has **30 analog rows with humidity and temperature units transposed**
— e.g. `QNL_AHUB001_AvgSpcHumd.PV` given `°C` and `AvgSpcTemp.PV` given `%rH`. The IO
list has those right, so it supplies `brick:hasUnit`.

But the IO list is not infallible either: **20 of its 24 `.kW` tags carry `%`** against a
description that reads "Power" — the same defect the datapoint ledger caught and
corrected on its own rows. Taking the IO unit verbatim would put `unit:PERCENT` on 20
`brick:Electric_Power_Sensor` points, i.e. a power sensor reading a percentage.

So where the resolved class names the quantity unambiguously, **the class decides**
(`CLASS_UNIT` in `build_qnl.py`) and each override is logged at build time. This build
applies 20, all `brick:Electric_Power_Sensor: unit:PERCENT → unit:KiloW`. Air flow is
deliberately excluded from that rule: the IO list distinguishes volumetric flow (`l/s`,
on the VAV/CAV boxes) from velocity (`m/s`, on the AHU ducts), and both are real.

After the pass, **no class in the sheet carries more than one unit**. That invariant is
now a permanent rule in the shared checker (`W-CON-19`), so any future project gets it
automatically rather than relying on someone thinking to look.

A full audit of the remaining units came back clean: no analog point silently defaulted
to unitless, every engineering-unit string in the IO list mapped to a Brick term (none
fell through), all 88 discrete points are `unit:UNITLESS`, and the ontology now agrees
with the ledger's `unit_of_measure` on **every** signature — the power rows were the only
correction that had been lost.

**The 22 AHU air-flow points now read `unit:L-PER-SEC`, settled by precedent.**
`QNL_AHU*_SupAirFlow.PV` (15) and `RtnAirFlow.PV` (7) arrived from the IO list carrying
`m/s` — a velocity, on a class that names a flow. The class ladder settles it at step 1:

| Reference | `Supply_Air_Flow_Sensor` | `Return_Air_Flow_Sensor` |
|---|---|---|
| Dar Cairo (primary) | `unit:L-PER-SEC` ×18 | `unit:L-PER-SEC` ×15 |
| QF SSC (previous project) | `unit:L-PER-SEC` ×113 | `unit:L-PER-SEC` ×5 |

Dar Cairo writes `unit:L-PER-SEC` on **all 51** of its air-flow sensors (supply, return,
outside, exhaust) and SSC on **all 118** of its own. **`unit:M-PER-SEC` does not occur
once in either reference model**, and neither carries any air-velocity concept at all —
Brick 1.4 has no air-velocity sensor class either, only `*_Velocity_Pressure_Sensor`,
which is a pressure quantity. The `m/s` came solely from the IO list's unit column, the
same column that puts `%` on 20 of its 24 `.kW` tags. `MinEU`/`MaxEU` cannot arbitrate:
they read 0–100 on every tag, m/s and l/s alike, so they are unpopulated defaults.

With this, all 317 air-flow points in the sheet — the 295 VAV/CAV `DuctAirFlow` plus
these 22 — carry `unit:L-PER-SEC`, and no `unit:M-PER-SEC` remains anywhere.

**Still worth raising at source:** if those 22 transmitters genuinely output air velocity,
the IO list's unit column is right and its *scaling* needs stating, because the ontology
now declares them as volumetric flow in line with the whole estate. Either way the IO
list needs a pass — it is wrong about the power tags regardless.

**Classes are taken straight from the ledger's `final_class`**, including the four
reused SSC classes (`para:Fail_Start_Alarm`, `para:Fail_Stop_Alarm`,
`para:Scheduled_Hrs_Duration`, `para:UnScheduled_Hrs_Duration`) and the one new class,
`para:Trip_Alarm`, which is now **defined in row 3 of the sheet** as
`rdfs:subClassOf brick:Alarm` — new `para:` classes are defined before first use.

**The CHW temperature points keep their deprecated class, at your direction.** The
`Chilled_Water_Supply/Return_Temperature_Sensor` classes are deprecated in Brick 1.4;
you chose to keep the Dar Cairo class as the join key and record the replacement, so
each such point raises the expected `W-TYP-4` and the ledger note names the
entering/leaving class that supersedes it.

### Units cross-checked against Dar Cairo, class by class

Every point class in the sheet was compared with the unit Dar Cairo gives that class,
falling back to QF SSC where Dar Cairo has no instance. **23 of 34 classes match a
reference model outright, 7 have no precedent in either, and 4 differ deliberately.**

The two corrections already described — power to `unit:KiloW`, AHU air flow to
`unit:L-PER-SEC` — were both *made* to bring the sheet into line with Dar Cairo. What
follows are the four places the sheet still departs from it, each on purpose:

| Class | QNL | Dar Cairo | Why QNL differs |
|---|---|---|---|
| `brick:Air_Flow_Sensor` (295) | `unit:L-PER-SEC` | `unit:UNITLESS` ×23 | A flow is not dimensionless, so Dar Cairo's value is a **missing unit, not a convention** — and its own specific flow classes (supply, return, outside, exhaust: 51 points) all carry `unit:L-PER-SEC`. QNL has a real unit from the IO list and follows the specific-class convention. |
| `brick:Damper_Position_Command` (14) | `unit:PERCENT` | `unit:UNITLESS` ×28, `unit:PERCENT` ×1 | Dar Cairo is mixed here, and the unitless ones read as binary open/close commands. Its analog commands do carry percent — `brick:Speed_Command` is `unit:PERCENT` on all 88 — and its `Damper_Position_Sensor` is `unit:PERCENT` on all 74. QNL's `PositionCtrl` points are analog and pair with `PositionFbk` in percent. |
| `brick:Relative_Humidity_Sensor` (64) | `unit:PERCENT` ×110 | **Dar Cairo contradicts itself**: its `Return_Air_Humidity_Sensor` (20) and `Supply_Air_Humidity_Sensor` (3) both use `unit:PERCENT_RH`, only the generic class uses bare `unit:PERCENT`. SSC uses `unit:PERCENT_RH` (18), and the IO list says `%rH`. Taking `PERCENT_RH` keeps every humidity point in the sheet on one unit. |
| `brick:Speed_Sensor` (22) | none; SSC `unit:RPM` ×14 | SSC's are named `..._Motor_Speed_Fbk` — motor shaft speed, genuinely RPM. QNL's are fan VFD `SpeedFbk`, which the IO list gives as `%` (speed as a fraction of maximum). Dar Cairo has no `Speed_Sensor`, but its `brick:Speed_Command` is `unit:PERCENT` on all 88, so percent for a speed point is house precedent. |

The 7 classes with no precedent in either model are
`Average_Zone_Air_Temperature_Sensor`, `Effective_Air_Temperature_Setpoint`,
`Return_Air_Differential_Pressure_Sensor`, `Return_Air_Humidity_Setpoint`,
`Return_Air_Temperature_Setpoint`, `Supply_Air_Differential_Pressure_Sensor` and
`para:Trip_Alarm`. Each was checked dimensionally instead — temperature in `unit:DEG_C`,
pressure in `unit:PA`, humidity in `unit:PERCENT_RH`, the alarm `unit:UNITLESS` — and
each agrees with the unit its sibling classes use in the same sheet.

### The three exception assets — handled under rule 1

Rule 1 is that a source disagreement is modelled and logged, never silently dropped:
an omission is invisible, an assumption in the log is reviewable. All three are in the
assumption log.

| Asset | The disagreement | What was written |
|---|---|---|
| `entity:QNL_CAV_1F_S15_001`<br>`entity:QNL_VAV_B_S13_005` | Named in the Selected sheet, **absent from the asset register** — so no room and no Fed By | Both units and their 3 points each are in the sheet, with **no `rec:locatedIn`, no `rec:feeds`, no `rec:isFedBy`**. Nothing about their position is asserted. |
| `entity:QNL_VAV_1F_S15_039S` | In the register **and** the historian, but the Selected sheet lists **no** points for it | Given the 3 points its 245 siblings carry (`DmprPos`, `DuctAirFlow`, `EffectiveSP`), taken from the historian, which publishes all three for it. |

For `039S` the family's own selected signature decided which points to take, so the
unit matches its siblings rather than carrying a set nothing else in the family has.
Its other five historian points (`CommAlm`, `ElectHtrSts`, `FltRst`, `HtrHiTempAlm`,
`SupAirTemp`) are not selected on any sibling either, so they were not added.

The two unregistered units raise **2 `E-FEED-1`** and **2 `W-GR-2`** findings. Those
are the correct result of asserting nothing about position, and are accepted in the
log rather than suppressed.

**A validator gap this exposed:** `brick:Constant_Air_Volume_Box` was missing from the
validator's `TERMINAL_EQUIPMENT` set, so **all 51 QNL CAVs had been escaping the
`E-FEED-1` and `W-GR-2` checks entirely** — a class missing from that set is not a
passing check, it is an unasked one. Fixed, along with `brick:Induction_Unit`. The 51
registered CAVs all pass; only the unregistered one is flagged, correctly.

### What the point data showed up — for the register's owner

1. **Two selected units are not in the asset register:** `QNL_CAV_1F_S15_001` and
   `QNL_VAV_B_S13_005`. Their 6 selected points are therefore not in the sheet. Either
   the register is missing two units, or the Selected sheet names two that do not exist.
2. **`VAV_1F_S15_039` and `VAV_1F_S15_039S` are two real units, not a typo.** The
   handover previously flagged the trailing `S` as a possible typing error; the IO list
   settles it — both carry a full, separate point set. But the Selected sheet selects
   points only for `039`, so **`039S` is in the sheet with no points at all**. Confirm
   whether `039S` should have been selected too.
3. **15 tags are listed twice in the Selected sheet** (`RtnAirDuctPrs.PV`, once per AHU).
   A tag names one physical point, so each is emitted once; the repeats would otherwise
   produce duplicate rows and two points sharing one timeseries id.

## Left out, and why

- **Equipment outside AHU / VAV / CAV / FCU.** The Selected sheet also lists points for
  CCU, EF, DX, HEX, KEF, SEF, TEF and GEN. That equipment is not in the asset register,
  so neither it nor its points are in this sheet — scoped out at your direction. Send an
  asset register for those families and both layers land together.
- **IO-list points that were not selected.** Only the "Must Have" points in
  `Selected_PARA_OS_Data_Points_v4.0.xlsx` are modelled. The IO list carries 11,601 rows
  in total; the rest are deliberately out of scope, and show as `W-IO-2` warnings.
- **Nameplate properties.** No manufacturer datasheets were supplied, so no rated power,
  flow, capacity, model number or manufacturer appears. Nothing is guessed.
- **Zones.** No `rec:Zone` or `rec:HVACZone` layer; no zone data was supplied. Rooms sit
  directly under their level, which satisfies the spatial-connectivity rule. Dar Cairo
  normally interposes a per-floor parent zone — worth adding if the QNL zoning drawings
  turn up.
- **IFC references on rooms.** Requested for equipment only, so rooms have none.
- **Parts.** No `brick:hasPart` breakdown (fans, coils, VFDs) — not requested, and no
  part-level source was supplied.

## The asset register is not internally consistent

You asked me not to change the tags, so nothing below has been changed — this is the
audit, for the register's owner to decide on. All 449 tags are unique.

| Family | Shape | n |
|---|---|---|
| VAV | `VAV_<level>_S<system>_<count>` | 246 |
| CAV | `CAV_<level>_S<system>_<count>` | 51 |
| FCU | `FCU_<level>_<count>` | 137 |
| AHUB | `AHUB<count>` → written `AHU_B_<count>` | 15 |

1. ~~**AHUB is the odd family out.**~~ **Fixed at your direction** — `AHUB011` is now
   `QNL_AHU_B_011`, matching the `TYPE_LEVEL_COUNT` shape of the other three. This is the
   only asset tag that was reshaped. Your BMS still knows these units as `AHUB011`, so
   the crosswalk is the join for them.
2. **FCU has no system segment** where VAV and CAV do. That may be correct — FCUs are fed
   by the chilled water loop, not by an AHU, so there is no `S##` to name — but it means
   the four families cannot be parsed by one rule.
3. **One tag breaks its own family: `VAV_1F_S15_039S`** — a trailing `S` that no other
   tag carries. Either a variant marker that should be a separate segment, or a typo.
4. **Level tokens use a different vocabulary from the rooms.** Assets say `B`, `1F`, `2F`;
   the room schedule and the level entities say `B`, `L1`, `L2`, `T1`. Nothing joins on
   them today, so nothing breaks, but the two vocabularies will need reconciling if a
   query ever tries.

## Things to check in the source data

1. **`ST-04` has no level prefix.** Every other stair is `B-ST-nn` or `L1-ST-nn`. It is
   modelled on level `B` alongside `ST-01`, `ST-02`, `ST-03`, `ST-05`. Confirm.
2. **`entity:QNL_L2_018_GROUP_STUDY_ROOM_8` has a trailing space** in the room list.
   Matched on the stripped value; the space is gone from the ontology identifier.
3. **`T1` has 7 rooms and no equipment** — 2 open terraces and 5 IDF rooms. Confirm
   nothing is missing rather than the level being genuinely unserved.
4. **Typos preserved as instructed** — `SPRIMKLERS_PUMPS_&_ZONES_VALVES`, `DISH_WASING`,
   `ITTIGATION_CONTROL_ROOM`, `CTRCULATION_OFFICE`, `GREEM_ROOM`, `STUDENT_CARRLES`,
   `L1_002A_GREEM_ROOM`. These reach end users through `rdfs:label_en`. Say the word and
   they are a one-line change.
5. **172 rooms carry no equipment.** They are in the sheet because rooms were in scope;
   whether they should have terminal units is a question for the mechanical drawings.

## Spelling corrections to room names

The room schedule was typed by hand and carries misspellings. Left alone they
ride into both the identifier and the label a user reads on screen, so at your
request they are corrected. The corrections live in `TYPO_FIXES` in
`build_qnl.py` and are applied to the underscore-separated tokens of the room
**name** only — never to the level or the room number, which are the join key
back to the drawings. Identifier and label are still built from the same
corrected string, so they cannot drift.

Every entry was settled against the rest of the schedule rather than guessed:
either the correct spelling already appears on a sibling room, or the token is
a run-together pair whose separator every other room writes.

**Misspelled words, 24 rooms**

| Room | Was | Now | Evidence |
|---|---|---|---|
| `L1_007` | `STUDENT_CARRLES` | `STUDENT_CARRELS` | `CARRELS` on 15 other rooms |
| `L2_011` | `CTRCULATION_OFFICE` | `CIRCULATION_OFFICE` | |
| `L1_002A` | `GREEM_ROOM` | `GREEN_ROOM` | |
| `B_072` | `SPRIMKLERS_PUMPS…` | `SPRINKLERS_PUMPS…` | |
| `B046_ITT` | `ITTIGATION_CONTROL_ROOM` | `IRRIGATION_CONTROL_ROOM` | |
| `B_231` | `DISH_WASING` | `DISH_WASHING` | |
| `B_105` | `SECURITY_CONTOL_ROOM` | `SECURITY_CONTROL_ROOM` | `CONTROL` on 8 other rooms |
| `L2_087` | `…HIGH_LEVLEL_IN_CEILING_VOID` | `…HIGH_LEVEL_IN_CEILING_VOID` | |
| `B_145` | `LOBY_&_CSECURITY` | `LOBBY_&_SECURITY` | `L1_042_LOBBY`; 8 `SECURITY` rooms |
| `B_223`, `B_225` | `VENTILATON` | `VENTILATION` | |
| `B_065`, `B_067`, `B_114`, `B_116` | `VENTLATON` | `VENTILATION` | |
| `L2_022` | `ACADEMIC_PERS_LIBRARIA` | `…_LIBRARIAN` | 14 `LIBRARIAN` rooms |
| `B_0924` | `…CHERRY_PICKER_PANKING` | `…CHERRY_PICKER_PARKING` | |
| `L2_048` | `VIP_WATING` | `VIP_WAITING` | |
| `L1_041` | `MULTPURPOSE_ROOM` | `MULTIPURPOSE_ROOM` | |
| `B_029` | `LITERATURE_&_ANGUAGE` | `LITERATURE_&_LANGUAGE` | |
| `L1_081` | `BIBLIOGRANHER1` | `BIBLIOGRAPHER1` | `L1_082_BIBLIOGRAPHER2` next door |
| `L1_130` | `PUBLIS_SPACE` | `PUBLIC_SPACE` | `L1_080_PUBLIC_SERVICE` |
| `B_093` | `TRANSH_CHAMBER` | `TRASH_CHAMBER` | only waste room in the building |
| `B_207` | `PRESEARCHERS_READING_AREA` | `RESEARCHERS_READING_AREA` | stray leading `P`; `B_151_RESEARCH…` |

**Run-together words, 11 rooms.** The separator is restored, the wording is not
changed:

| Room | Was | Now | Evidence |
|---|---|---|---|
| `L1_101` | `REST_ROOMMEN` | `REST_ROOM_MEN` | 9 × `REST_ROOM_MEN` |
| `L1_105`, `L1_106` | `ABLUTIONMEN`, `ABLUTIONWOMEN` | `ABLUTION_MEN`, `ABLUTION_WOMEN` | the `_MEN` / `_WOMEN` split is universal here |
| `L1_085` | `ADPUBLIC_SERVICE` | `AD_PUBLIC_SERVICE` | `AD_COLLECTIONS`, `AD_OFFICE`, `AD_ADMIN` |
| `L2_044` | `LIBDIRECTORS_ROOM` | `LIB_DIRECTORS_ROOM` | |
| `L2_070`–`L2_075` | `INDIVISTUDY_ROOM` | `INDIVI_STUDY_ROOM` | sibling shape is `GROUP_STUDY_ROOM` |

**Two things I did not do, because they are your call, not a typing error.**

1. `INDIVI` almost certainly stands for **INDIVIDUAL** — those six rooms sit
   beside `GROUP_STUDY_ROOM` on the same floor. Expanding an abbreviation is a
   rewrite rather than a correction, and the schedule's other abbreviations
   (`AD`, `SEC`, `RES`, `LIBR`, `PERS`) are all kept as written, so only the
   missing separator was restored. Say the word and it becomes
   `INDIVIDUAL_STUDY_ROOM`.
2. Room `B046_ITT` becomes `entity:QNL_B_046_ITT_IRRIGATION_CONTROL_ROOM`. The
   word was corrected; the `ITT` sitting in the *room number* segment was left
   alone, because a segment like that is usually a drawing code and may be a
   join key. If it is just the same misspelling abbreviated, it should read
   `IRR` — your call.

**What this costs.** These are subjects, so the raw room strings in the source
schedule no longer match the ontology character for character.
`QNL_identifier_crosswalk.csv` carries the mapping — its `source_identifier`
column is still the schedule's own text — so the join is documented rather than
lost. This reverses the earlier *names cannot be changed* instruction for room
names only; **asset tags were left untouched**, since they are the BMS join key.

Validator after the spelling pass: unchanged by it — the room-name corrections
introduce no findings of their own. Current totals are in "Validator result" above.

---

## Virtual metering layer — added 2026-09-03

The sheet now carries a metering layer: **1,459 virtual meters, 8,754 rows**, plus
`para:contributionFraction` on 297 terminal units. Ontology grew 9,985 → 19,345 rows.
Regenerate it with `python3 projects/QNL/add_virtual_meters.py` (`--dry-run` to count first).

**Where it came from.** `sources/VirtualMeters_QNL_manual_v1.xlsm`, the hand-built
workbook, supplied the tier matrix on its `Sheet1` — 9 meter classes against
Building / Floor / Room. That matrix is now encoded in the generator. The
workbook's own 11,648 rows were **not** imported: none of its 353 room
identifiers matched the live sheet, because it was built before `align_naming`
normalised them. The layer is regenerated from the matrix against the live
ontology instead, so identifiers agree by construction and `L1-145_ILL-Director`
— added later by the room-retarget pass — is picked up automatically.

**A virtual meter is only created where a physical meter does not exist** — that
is what the layer is for. `entity:QNL_Utility-Virtual-Meter` was therefore *not*
written: `entity:QNL_Total-Energy` is already a `para:Utility_Meter` with a live
historian tag. The suppression lives in `ALREADY_METERED` in the generator, each
entry naming the physical meter that justifies it.

| Tier | Meter classes | Count |
|---|---|---|
| Building only | `para:UPS_Meter` (Utility suppressed, see above) | 1 |
| Building + floor | `para:HW_Meter`, `para:SPWR_Meter`, `para:Common_Util_Meter` | 18 |
| Building + floor + room | `para:CHW_Meter`, `para:HVAC_Meter`, `para:LTG_Meter`, `brick:Electrical_Meter` | 1,440 |

Each meter carries six rows: `brick:isPartOf entity:Metering`, `brick:meters`,
`brick:isVirtualMeter` (`brick:value TRUE`), `rec:locatedIn`, and a
Consumption/Demand point pair. Name segments are Dar Cairo's verbatim; the one
coinage is `HW-Power-Thermal-Virtual-Meter`, mirroring the CHW segment.

**Thermal points take `para:KiloWt` / `para:KiloWt-HR`**, not `unit:KiloW`, on all
732 CHW and HW points — client decision, so that a building demand rollup cannot
add chilled-water kW to electrical kW. Both units are declared as `qudt:Unit`
rows. Note the 7 pre-existing QNL thermal rows still on `unit:KiloW`; they were
left alone and want a separate pass.

**Early declarations added:** `para:Metering_System`, `para:UPS_Meter`,
`para:SPWR_Meter`, `para:Common_Util_Meter`, `para:HVAC_Meter`, `para:LTG_Meter`,
`para:CHW_Meter`, `para:HW_Meter`, `para:contributionFraction`, `para:KiloWt`,
`para:KiloWt-HR`, and the `entity:Metering` system node under `entity:QF`.
`para:Utility_Meter` was already declared. All sort ahead of first use.

**`para:contributionFraction` — 297 units** (246 VAV + 51 CAV), every unit an AHU
feeds. It is a container point for the unit's chilled water consumption, which
QNL has no point for; the backend replaces the `ContributionFraction` series with
its own calculation apportioning the AHU's load across the units it feeds. Written
with `ref:hasTimeseriesId` `ContributionFraction` and `para:hasEntityId`
read off the unit's existing points, the same way every other datapoint on that
unit derives it. The skip-if-in-a-shaft rule matched nothing:
QNL's shaft-dwelling assets are 62 FCUs and 2 exhaust fans, and no AHU feeds any
of them. `entity:QNL_CAV-B-S13-050` carries no points, so its entityId was
derived — the derivation matches all 296 units that do have one.

### Open — needs your decision

1. **`entity:QNL_CHWS-MAIN-LOOP_Energy-Meter` may make the building-tier
   `para:CHW_Meter` redundant.** It is a `brick:Building_Chilled_Water_Meter` on
   the main loop with 7 live points, including `CHW-Consumption-KW` and
   `CHW-CHW-Energy-PV`. By the same rule that removed the Utility virtual meter,
   `entity:QNL_CHW-Power-Thermal-Virtual-Meter` looks like a duplicate — but the
   classes differ, so no checker will flag it. Confirm whether the loop meter
   covers the whole building and I will add it to `ALREADY_METERED`.
2. **None of the 16 physical meters carries a `brick:meters` row.** They are all
   `brick:isPartOf entity:Electrical_System` with points, and nothing says what
   any of them measures — so "is this already metered?" cannot be answered from
   the sheet, and the suppression list has to be maintained by hand. Adding those
   rows would make the rule self-checking. Worth a small pass.
3. **2,918 meter points ship with no `ref:TimeseriesReference`.** The historian
   (`QNL_Historian_IO_list_CP2.xlsx`) carries no calculated tags — zero `*_CALC`,
   zero `ContributionFraction`. Every point is listed in
   `QNL_virtual_meter_timeseries_pending.csv` with the Dar Cairo `hasTimeseriesId`
   proposed and `hasEntityId` blank, because that half is the historian's key for
   the space and nothing in the ontology derives it. Hand back the filled file and
   the rows go in in one pass. They show as `W-PT-1` until then — deliberately, a
   blank reference row would read as a working link.
4. **`entity:QNL_L1-144` / `L1-145_ILL-Director` both carry meters.** If the
   retarget pass was right that these are one room, 144 should be retired and its
   four meters with it.

### Validator result after the layer

| | Before | After |
|---|---|---|
| Errors | 574 | **10** — the layer added none, and filling `para:IFC_ID` cleared 564 |
| `W-BN-4` | 0 | 1,459 — `brick:value TRUE` with no unit, one per meter. Dar Cairo writes it bare; a boolean is not a dimensionless quantity, so do not "fix" it with `unit:UNITLESS` |
| `W-PT-1` | 0 | 2,918 — the pending timeseries above |
| `check_consistency` errors | 590 | 608 |

The 18 new consistency errors are the 14 pre-existing physical meters (MFM, VCB)
sharing `brick:Electrical_Meter` with the 360 new virtual ones. Dar Cairo files
both under that class too, so this is named rather than fixed — minting a `para:`
subclass to quiet the checker would depart from the primary reference. Every
pure-virtual family (`para:HVAC_Meter`, `para:LTG_Meter`, `para:CHW_Meter`) comes
back with **0 errors**.

`check_consistency.py` needed one fix to support this layer: `brick:meters`,
`brick:isMeteredBy` and `brick:isSubMeterOf` joined `VARYING_PREDICATES`. Without
it every meter reads as missing the 359 targets its siblings carry — 1,440 phantom
errors. Covered by `tests/virtual-meters-sample.csv`.


## IFC references filled — 2026-09-03

All 564 `ref:IFCReference` rows declared `para:IFC_ID` with no value, which was
**564 of the sheet's 574 errors**. Filled with the entity identifier — the same
string `ref:ifcName` already carried on every one of them, which is QF SSC's
shape (both columns, same value, on all 165 of its IFC rows).

**The sheet now validates at 10 errors**, all `E-FEED-1`, all visible:

| Entity | Class |
|---|---|
| `QNL_CAV-1F-S15-001` | `brick:Constant_Air_Volume_Box` |
| `QNL_CCU-8081` … `QNL_CCU-8086` | `brick:CRAC` (6 units) |
| `QNL_CR-DX-EWRC500`, `QNL_DX-RP21` | `para:DXUnit` |
| `QNL_VAV-B-S13-005` | `brick:Variable_Air_Volume_Box` |

Each is a terminal unit with no `rec:feeds`. Two are the unregistered units
already recorded above; the other eight want checking against the drawings.

**Caveat on `para:IFC_ID`.** No delivered model carries a real IFC GUID — across
Dar Cairo, SSC, HQ and QNL, none of 2,133 values matches the 22-character
`IfcGloballyUniqueId` shape, and the three reference models disagree on which
column to use at all (Dar Cairo `ref:ifcName` only, HQ `para:IFC_ID` primary, SSC
both). `CLAUDE.md` describes `para:IFC_ID` as the BIM GUID; in practice it holds
the asset tag. If the BIM team can export real GUIDs they overwrite these 564 in
one pass. Worth putting to the PARA team.


## Equipment with no room placed at the building — 2026-09-03

**A QNL project assumption, not a house rule** — the skill still says to write no
location at all when the register gives none. For this building the decision was
that an asset with no room is still certainly in the building and certainly on
its system, so **assert both rather than nothing**; a building-level location
invents nothing that a survey would contradict.

**27 rows added**, at the most specific level the evidence supports — the **floor**
where the floor is identifiable, the **building** where it is not. All 27 already
carried `brick:isPartOf` their system, so no second row was needed. Clears 27
`W-GR-2`.

**Three resolved to a floor:**

| Asset | Level | Evidence |
|---|---|---|
| `CAV-1F-S15-001` | `entity:QNL_L1` | the `1F` tag token — resolves to Level 1 on 134 of the 135 located assets carrying it |
| `VAV-B-S13-005` | `entity:QNL_B` | the `B` token — 202 of 202 |
| `DX-RP21` | `entity:QNL_P` | `QNL_Full_Metadata.xlsx` states Level "Roof level", room served "PLC 8 / IDF ROOF PLANT"; `entity:QNL_P` is labelled "Roof Plant" |

`CHWPU-P02` was considered and **deliberately left at the building**. The only
basis for the basement was that its pair `CHWPU-P01` sits in
`B-220_Plant-Room-04` — inference from a sibling, not a source. Held at the
building until the floor is confirmed on site.

**Twenty-four stayed at the building**, because no source names a floor: the 6
CRACs `CCU-8081`–`8086` (a numeric tag family the Closed Control Units metadata,
which covers `CC/B/01`–`09`, does not reach), `CR-DX-EWRC500`, the 15 electrical
meters, `CHWS-MAIN-LOOP_Energy-Meter`, and `CHWPU-P02` pending site confirmation. The MV, HV and transformer rooms are
all in the basement and `ELEC-Gen` sits in `B-080_Generator`, which makes the
basement likely for the switchgear meters — but likely is not evidence, and the
electrical review will settle it along with what each meter measures.

**`rec:feeds` is still not written.** The served space is the part nobody knows,
and the feeds rule forbids a placeholder. The 10 `E-FEED-1` errors stand — they
are the sheet's only remaining errors and want checking against the drawings.

**The 173 parts that still lack a location were excluded** — 137 CHW valves, 22
supply/return fans, 10 HEX valves, 2 circuit breakers, 2 fuel transfer pumps.
A part inherits its parent's location; Dar Cairo locates only 19 of its 801
parts separately. Locating a valve at the building would add noise, not fact.


## Virtual meter families not built, and why

Two reasons, and they need different follow-up.

**Suppressed — a physical meter already covers it.** Closed.

- `para:Utility_Meter` at building tier. `entity:QNL_Total-Energy` is already one,
  with a live historian tag `QNL_TotalEnergy.Energy`.

**Deferred — the points the formula would sum do not exist.** Reopens if the
points arrive.

- `brick:Water_Meter` — QNL carries no potable-water point at all. Every "water"
  match in the sheet is a chilled-water temperature or an air flow. Dar Cairo has
  34 of these at building, level and zone tier.
- `para:Occupant-Wellbeing_Meter` — its eight-sensor bundle has temperature (310
  points) and relative humidity (115) available, and **no** CO2, TVOC, PM2.5/10,
  illuminance, noise or occupancy points anywhere in the building. Dar Cairo's
  largest virtual meter family, 901 rows.

**Not asked for, and buildable from data QNL already has** — no new site data
needed, a matrix row each if wanted:

- `para:*_Target` points alongside Consumption and Demand (Dar Cairo attaches 34
  per class)
- forecast and KPI points, derived from the series the layer already declares
- `brick:isSubMeterOf`, chaining the floor and room meters up to the building one
- `para:General_Util_Meter`, `para:Data-Center_Meter`, `para:Generator_Meter`,
  `para:Solar_Meter` — 2,335 electric power points to draw on, and
  `entity:QNL_ELEC-Gen` already exists as a `para:Generator`


## Toilet exhaust fans modelled as twin-fan units — 2026-09-03

`TEF/B/01`, `B02` and `B03` are **twin-fan units**: one casing, two fans, one
duct, duty/standby with automatic changeover. The sheet previously modelled the
six fans as independent equipment, each feeding one toilet.

Four sources agree, and the fourth was already in the sheet:

1. The O&M manual states twin fans A and B.
2. The HVAC drawing shows **one duct** reaching `TEF/B/01`, one riser splitting
   to serve both toilet blocks.
3. The BMS carries `ChOverSel` and `ChOverHrsSP` on the base tag — changeover
   between the twins.
4. One Nuaire model number per pair and **identical rated flow within each pair**
   — 1538/1538, 970/970, 400/400. Each fan sized for the full duty is
   duty/standby; two fans serving two differently sized rooms would not match.

**What changed, per set** — 8 rows added, 8 removed:

```
entity:QNL_TEF-B01 | brick:Exhaust_Fan | brick:isPartOf | entity:HVAC       + label
entity:QNL_TEF-B01 | brick:Exhaust_Fan | rec:locatedIn  | B-110 Plant Room 03
entity:QNL_TEF-B01 | brick:Exhaust_Fan | rec:feeds      | B-046 Rest Room Men
entity:QNL_TEF-B01 | brick:Exhaust_Fan | rec:feeds      | B-047 Rest Room Women
entity:QNL_TEF-B01 | brick:Exhaust_Fan | brick:hasPart  | TEF-B01A
entity:QNL_TEF-B01 | brick:Exhaust_Fan | brick:hasPart  | TEF-B01B
entity:QNL_TEF-B01 | brick:Exhaust_Fan | brick:hasPoint | TEF-B01_Local-Status
TEF-B01_Local-Status | para:Local_Status | ref:hasExternalReference | QNL_TEF_B01.LocSts
```

The fans lost `brick:isPartOf`, `rec:locatedIn` and their single wrong
`rec:feeds` — they inherit from the unit — and kept their five run/trip/command
points and their own `para:ratedExhaustAirFlowrate`. **Rated flow stays on the
fans only**, so nothing restates the unit's duty and the old 2× double-count
risk is gone: A and B are no longer sibling equipment each rated 1538 l/s.

The three `entity:QNL_TEF_B01/_B02/_B03` rows typed `para:Local_Status` — a point
class masquerading as equipment under `entity:HVAC` — are gone.

**Validator: still 10 errors, none added.** That needed a fix to
`validate_ontology.py`: a part is now exempt from `E-FEED-1` and `W-GR-2`,
because a twin fan's two halves share one casing, one duct and one location, and
the unit already answers both questions. Without it the six fans reported six
phantom "never declares what it feeds" errors. Covered by
`tests/twin-fan-sample.csv`.

**`check_consistency.py` for `brick:Exhaust_Fan` went 31 → 70 errors, and they are
correct observations rather than defects:** the three units have 8 rows where
15 is typical (their points live on their fans), they lack the per-fan
Run-Status / Trip / Auto-Manual / Start-Stop the other 24 fans carry, and they
each have 2 `rec:feeds` triples (`E-CON-6`). That last one is worth a look at the
checker: a terminal unit legitimately serving two rooms will always trip it, so
`E-CON-6` may be too strict as an ERROR.

### The 36 group points and 50 per-fan points — added, then removed

Both sets were built, and both are gone again. They are recorded here because
the class work behind them stands and would be reused verbatim if the scope
changes.

The group set was 12 points per twin-fan node (changeover setpoint, duty
priority 1 and 2, enable command, fire alarm, lead/lag command, local status,
occupancy status, remote status, reset command, run time, start count, trip
count). The per-fan set was 50 points across the eight fans, on seven suffixes,
all of which resolved on the ladder without coining anything new:

| Suffix | Historian description | Class |
|---|---|---|
| `FTSP` | Fail to Stop Alarm | `para:Fail_Stop_Alarm` |
| `FTST` | Fail to Start Alarm | `para:Fail_Start_Alarm` |
| `FltRst` | Alarm Reset Command | `brick:Fault_Reset_Command` |
| `RuntimeMtr` | Runtime Meter | `brick:On_Timer_Sensor`, `unit:HR` |
| `StartsCtr` | Starts Counter | `para:Start_Count` |
| `TripCtr` | Trip Counter | `para:Trip_Count` |
| `RemSts` | Remote status | `para:Remote_Status` |

They were removed because none of them is on
`Selected_PARA_OS_Data_Points_v4.0.xlsx`. That list carries **45 TEF tags**; the
sheet had grown to 131. The selected shape is `.LocSts` at the twin-fan set and
five tags on each fan — `AutoManCmd`, `RunSts`, `StartStopCmd`,
`StartStopCmdSts`, `TripAlm` — which is what the sheet now carries.

The twin-fan structure itself is unaffected, and the selected list is the
strongest confirmation of it yet: it names `QNL_TEF_B01A` and `QNL_TEF_B01B` as
separate tag sets with `QNL_TEF_B01.LocSts` sitting at the set. What the pruning
costs is the group node's content — `TEF-B01`, `-B02` and `-B03` now carry one
point each, and the consistency checker flags them as thin against their 24
single-fan siblings. That is a real structural difference, not a defect.

Logged as **QNL-046** and **QNL-047**, both marked reversed.

## The sheet now matches the selected datapoint list exactly

`Selected_PARA_OS_Data_Points_v4.0.xlsx` — 2,769 rows, 2,754 unique tags, every
one marked "Must Have" — is the scope authority for points. The historian is an
inventory of what the BMS publishes; the selected list is what the integration
was asked to deliver, and it is the smaller of the two. Reconciled both ways:

| | |
|---|---|
| Selected tags present in the sheet | **2,754 of 2,754** |
| Selected tags missing | **0** |
| Timeseries ids in the sheet that are not selected | **1** — `ContributionFraction`, by design |

Getting there removed **149 points, 302 rows**:

| Group | Points | Why |
|---|---|---|
| TEF | 86 | The group and per-fan sets above |
| ELEC MFM | 60 | `KWDaily`, `KWMonthly`, `MWDaily`, `MWMonthly`, `kWhpreviousdatadaily`, `kWhpreviousdatamonthly` on 10 MFM units. The list selects only `.KW` and `.KWh` |
| VAV | 3 | `VAV_1F_S15_039S` — see below |

Plus four `para:` class declarations left with no user: `para:Duty_Priority`,
`para:Remote_Status`, `para:Start_Count`, `para:Trip_Count`.

The MFM rollups deserve their own line, because dropping them is right on two
counts rather than one. Daily and monthly kW/kWh are derived from the `.KW` and
`.KWh` the list does select, and the virtual metering layer computes exactly
those rollups — so carrying them as raw points would have put two answers to the
same question in the graph, which is the failure the virtual meter layer exists
to avoid.

`ContributionFraction` is the one deliberate exemption. It is an internal
container the backend fills by calculation, so its absence from a list of BMS
tags is expected, not a selection gap.

Removals are itemised in `QNL_pruned_points.csv`, and the pruning is
reproducible: `python3 projects/QNL/prune_to_selected.py`. Logged as
**QNL-049**.

### One point where the selection looks wrong — `VAV-1F-S15-039S`

The asset register lists `VAV_1F_S15_039S` as a box in its own right, serving
**L1-048 Staff Office** — a different room from `VAV_1F_S15_039`, which serves
L1-002A Green Room. The historian carries five tags for it. The selected list
carries none: it selects `QNL_VAV_1F_S15_039.DmprPos`, `.DuctAirFlow` and
`.EffectiveSP` but has no `039S` equivalent.

Its three points were dropped with the rest. The equipment entity is kept, with
its location, feeds, isFedBy and IFC reference intact.

This reads as an omission in the selection rather than a decision: the box is
real, it serves a room no other box serves, and the near-identical `039` is
selected. As it stands, Staff Office L1-048 has no VAV telemetry in the
delivered graph. Restoring the three points is a one-line change if you confirm.
Logged as **QNL-050**, open.

### The 1,314 historian tags — closed, not needed

The earlier finding of 1,314 unmodelled tags across 28 equipment families
(VAV 247, AHU 146, ELE 145, FCU 137, EF 136, DX 120, and the rest) is now
settled: **none of them is on the selected list**, so none is in scope and no
rows were added. Logged as **QNL-048**, closed.

## Sheet state

**19,244 rows. 10 errors**, all pre-existing `E-FEED-1` on terminal units whose
served room the asset register does not give. All tests pass.
