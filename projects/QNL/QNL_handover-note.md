# QNL ontology — handover note

**Deliverable:** `QNL_Ontology.xlsx` (also `QNL_Ontology.csv`) — 2,124 rows on the
27-column PARA header. Supporting file: `QNL_identifier_crosswalk.csv`, mapping every
source identifier to the identifier used in the sheet.

**Sources:** `QNL_Room_Names_for_Ontology.xlsx` (336 rooms),
`QNL_Assets_Location_Relationships.xlsx` (449 assets across AHUB / VAV / CAV / FCU).

## What is in the sheet

| Layer | Rows | Content |
|---|---|---|
| Extensions | 1 | `para:Chilled_Water_Loop_Network` |
| Site + Building | 1 | `entity:QNL` `rec:isPartOf` `entity:Qatar-Foundation` |
| Levels | 4 | `QNL_B` (`rec:BasementLevel`), `QNL_L1`, `QNL_L2`, `QNL_T1` (`rec:Level`) |
| Rooms | 336 | each `rec:isPartOf` its level |
| Chilled water loop | 1 | `rec:locatedIn` the building |
| Equipment | 1,781 | 15 AHU, 246 VAV, 51 CAV, 137 FCU |

Per asset: `rec:locatedIn` → its room, `rec:isFedBy` → its upstream source,
`ref:hasExternalReference` → an `ref:IFCReference` blank node, and for the terminal
units (VAV, CAV, FCU) `rec:feeds` → the room it serves. AHUs get no `rec:feeds` row —
see "one direction" below.

## Decisions taken, per your answers

**Predicate direction — one direction, held throughout.** Equipment-to-equipment links
are always stated as `rec:isFedBy` (downstream names its source); equipment-to-space
links are always stated as `rec:feeds` (terminal unit names the room it serves). No link
is stated twice. The AHU → VAV/CAV chain therefore appears once, on the VAV/CAV row:
`entity:VAV-B-S11-024 rec:isFedBy entity:AHU-B-011`. AHUs have no `rec:feeds` row
because they do not serve a room directly — the 297 VAV/CAV rows carry that chain.

**Room Tag used for both `rec:locatedIn` and `rec:feeds`** on terminal units; for AHUs
it is a plant room, so `rec:locatedIn` only. Note this means 53 VAVs are recorded as
located in a room on a different level from their own tag (e.g. `VAV-2F-S12-001` is
located in `QNL_L1_OPEN-READING-AREA_001`). That follows directly from the single Room
Tag column in the source; if the tag is the space served rather than the physical
location, the `rec:locatedIn` rows for those 53 need a second source column to correct.

**Level codes kept as-is** — `B`, `L1`, `L2`, `T1`, with those exact strings as labels.
No `rec:levelNumber` is asserted. `B` is typed `rec:BasementLevel` (every asset on it
sits in a plant, riser or storage room); the other three are `rec:Level`.

**Room identifiers normalised to the PARA convention, names unchanged.**
`QNL_<Level>_<Room-Name>_<Number>`, words inside a segment joined by dashes, segments by
underscores. The name text itself is untouched — no typo fixes, no expanded
abbreviations. So `entity:QNL_B_063_PLANT_ROOM_01` becomes
`entity:QNL_B_PLANT-ROOM-01_063`, and `SPRIMKLERS`, `DISH_WASING`, `ITTIGATION`,
`CTRCULATION`, `GREEM`, `CARRLES` all survive as written. `&` is dropped, matching how
the label rule treats it: `TRANSL_SPC_&_EDI_PUBLICATIONS_SPC` →
`TRANSL-SPC-EDI-PUBLICATIONS-SPC`. Room labels are `<number> <name>` cleaned per the
label rule — `B 063 PLANT ROOM 01` — which keeps the 30-odd corridors distinguishable in
the front end.

**Equipment identifiers** follow the same convention: `AHUB002` → `entity:AHU-B-002`,
`VAV_B_S11_024` → `entity:VAV-B-S11-024`. Level tokens inside asset tags (`B`, `1F`,
`2F`) are left exactly as the source wrote them, so they do not match the level codes
`B` / `L1` / `L2` used for the level entities. `QNL_identifier_crosswalk.csv` maps every
old identifier to the new one, both directions of the join.

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

## Validator result

```
2124 rows, 792 typed entities, 1 para: definitions
449 errors, 0 warnings
```

**All 449 errors are the same rule, `E-PAIR-1`, and all of them are deliberate.** Each
is a `ref:ifcName` property with an empty value, on the IFC reference row of one asset —
exactly what you asked for: create the reference row, leave the ID blank until the real
IFC values are available. Paste the IFC names into `object_prop_val` on those rows and
the sheet validates clean. Nothing else is outstanding: zero warnings, so every entity
is labelled, every terminal unit has a feeds row and a location, and every spatial
entity connects up to `rec:Building`.

## Left out, and why

- **Points.** No IO list was supplied, so no equipment carries a `brick:hasPoint` row.
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
