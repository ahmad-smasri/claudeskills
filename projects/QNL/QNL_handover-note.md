# QNL ontology — handover note

**Deliverable:** `QNL_Ontology.xlsx` (also `QNL_Ontology.csv`) — 2,573 rows on the
27-column PARA header. Validate with
`validate_ontology.py QNL_Ontology.xlsx --label-style verbatim`. Supporting file: `QNL_identifier_crosswalk.csv`, listing every
source identifier against the identifier used in the sheet and its label.

**Sources:** `QNL_Room_Names_for_Ontology.xlsx` (336 rooms),
`QNL_Assets_Location_Relationships.xlsx` (449 assets across AHUB / VAV / CAV / FCU).

## What is in the sheet

| Layer | Rows | Content |
|---|---|---|
| Extensions | 1 | `para:Chilled_Water_Loop_Network` |
| Site + Building | 1 | `entity:QNL` `rec:isPartOf` `entity:Qatar-Foundation` |
| Levels | 4 | `entity:QNL_B` (`rec:BasementLevel`), `_L1`, `_L2`, `_T1` (`rec:Level`) |
| Rooms | 336 | each `rec:isPartOf` its level |
| Chilled water loop | 1 | `rec:locatedIn` the building |
| Equipment | 2,230 | 15 AHU, 246 VAV, 51 CAV, 137 FCU |

Per asset: `rec:locatedIn` → its room, `rec:isFedBy` → its upstream source, two
`ref:hasExternalReference` rows (one `ref:IFCReference`, one `ref:TimeseriesReference`),
and for the terminal units (VAV, CAV, FCU) `rec:feeds` → the room it serves. AHUs get no
`rec:feeds` row — see "one direction" below.

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

**Level codes kept as-is** — `B`, `L1`, `L2`, `T1`, with those exact strings as labels.
No `rec:levelNumber` is asserted. `B` is typed `rec:BasementLevel` (every asset on it
sits in a plant, riser or storage room); the other three are `rec:Level`.

**Identifiers taken from the source verbatim.** Every room keeps the entity name your
room schedule assigned — `entity:QNL_B_063_PLANT_ROOM_01` — and every asset keeps its
register tag: `entity:AHUB011`, `entity:VAV_B_S11_024`, `entity:FCU_1F_055`. Nothing is
reordered, respelled or re-cased, `&` survives, and the typos survive with it. The only
edit anywhere is stripping the trailing space from
`entity:QNL_L2_018_GROUP_STUDY_ROOM_8`, which the validator rejects outright
(`E-WS-1`). The sheet therefore joins directly to SCADA, to the assets register and to
the room schedule with no mapping step.

Seven identifiers had to be invented, because no source supplies them:
`entity:Qatar-Foundation`, `entity:QNL`, the four levels `entity:QNL_B` / `_L1` / `_L2`
/ `_T1` (matching the level segment inside your room tags), and
`entity:QNL_CHILLED_WATER_LOOP` for the `CHILLED WATER LOOP` value in the Fed By column.

**Labels follow QF SSC — the source text, verbatim.** SSC labels rooms
`1.001_CORRIDOR` and equipment `SSC_FCU0001`; QNL now does the same. Rooms read
`<number>_<name>` — `B_063_PLANT_ROOM_01`, `B_237_CORRIDOR` — and assets read their raw
register tag, `AHUB011`, `VAV_B_S11_024`. No punctuation is stripped and no typo is
fixed. This is not the PARA label rule, which would give `B 063 PLANT ROOM 01`; the
validator's `E-LBL-1` is therefore switched off with `--label-style verbatim`, and every
other rule stays in force.

`QNL_identifier_crosswalk.csv` lists every source identifier against the identifier used
in the sheet and its label. They are identical apart from that one trailing space; the
file is there so the join is documented rather than assumed.

## Classes used

| Source | Class | Basis |
|---|---|---|
| AHUB | `brick:Air_Handling_Unit` | Dar Cairo, 697 rows |
| FCU | `brick:Fan_Coil_Unit` | Dar Cairo, 936 rows |
| VAV | `brick:Variable_Air_Volume_Box` | Brick 1.4 preferred term; no Dar Cairo precedent |
| CAV | `brick:Constant_Air_Volume_Box` | Brick 1.4 preferred term; no Dar Cairo precedent |
| CHILLED WATER LOOP | `para:Chilled_Water_Loop_Network` | Dar Cairo, 127 rows; already in the para registry |

No new `para:` class is proposed. `para:Chilled_Water_Loop_Network` is defined in row 2
of the sheet for readability, but it is an existing registry class, not a new coinage.
1,188 `I-TYP-6` info lines are the VAV and CAV classes — valid Brick 1.4, simply the
first time this house has used them.

## External references — the SSC shape

Each asset carries two `ref:hasExternalReference` rows, matching QF SSC:

```
entity:AHUB011 | brick:Air_Handling_Unit | ref:hasExternalReference | <blanknode> |
ref:IFCReference        | | | para:IFC_ID          |         | | | ref:ifcName      | AHUB011
entity:AHUB011 | brick:Air_Handling_Unit | ref:hasExternalReference | <blanknode> |
ref:TimeseriesReference | | | ref:hasTimeseriesId  |         | | | para:hasEntityId | AHUB011
```

`para:IFC_ID` is the slot for the real BIM GUID and is empty, as you asked.
`ref:ifcName` is filled with the entity name, which is derivable and is what both
reference models put there. `ref:hasTimeseriesId` is empty because point-level telemetry
IDs come from the IO list, which has not been supplied; `para:hasEntityId` is filled with
the asset's own tag, which is what both reference models use.

## Validator result

```
python3 validate_ontology.py QNL_Ontology.xlsx --label-style verbatim
2573 rows, 792 typed entities, 1 para: definitions
898 errors, 0 warnings
```

**All 898 errors are the same rule, `E-PAIR-1`, and all of them are deliberate** — the
two empty ID slots on each of the 449 assets, `para:IFC_ID` and `ref:hasTimeseriesId`.
Paste the IFC GUIDs and the telemetry IDs into `object_prop_val` on those rows and the
sheet validates clean. Nothing else is outstanding: zero warnings, so every entity is
labelled, every terminal unit has a feeds row and a location, and every spatial entity
connects up to `rec:Building`.

Without `--label-style verbatim` you also get 771 `E-LBL-1` — that is the PARA label
rule objecting to the SSC label style, and it is expected.

## Left out, and why

- **Points.** No IO list was supplied, so no equipment carries a `brick:hasPoint` row.
  Note that in both reference models the timeseries reference belongs on the *point*,
  not on the equipment — the per-asset `ref:TimeseriesReference` rows here are stubs
  registering each asset's SCADA entity, ready for the point rows to hang off once the
  IO list lands.
- **Nameplate properties.** No manufacturer datasheets were supplied, so no rated power,
  flow, capacity, model number or manufacturer appears. Nothing is guessed.
- **System membership.** No `brick:isPartOf entity:HVAC` rows — you asked for site,
  building, floors, rooms and equipment, and a systems layer was not part of that. It is
  five rows plus one per asset whenever you want it.
- **Zones.** No `rec:Zone` or `rec:HVACZone` layer; no zone data was supplied. Rooms sit
  directly under their level, which satisfies the spatial-connectivity rule. Dar Cairo
  normally interposes a per-floor parent zone — worth adding if the QNL zoning drawings
  turn up.
- **IFC references on rooms.** Requested for equipment only, so rooms have none.
- **Parts.** No `brick:hasPart` breakdown (fans, coils, VFDs) — not requested, and no
  part-level source was supplied.

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
