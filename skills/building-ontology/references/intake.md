# Intake: what to request, and how to ask for it

Ask once, in one message, for everything missing. Chasing inputs one at a time
is the slowest way to build a sheet.

## The six mandatory inputs

| # | Input | Usually arrives as | Blocks |
|---|---|---|---|
| 1 | Building name (and site, if the building sits under one) | a sentence | every row |
| 2 | Levels - full list, including basements and roof | floor schedule | spatial layer |
| 3 | Rooms and spaces - name, number, and any tag or ID | room schedule / BIM export | spatial layer |
| 4 | Equipment - the asset register | equipment schedule | equipment layer |
| 5 | Location of each asset - room or level | asset register column | equipment layer |
| 6 | Feeds / fed-by for each asset | single-line diagram, schematic, or a schedule column | feeds layer |

Without 6 the model is not deliverable. A terminal unit that does not say what
room it serves cannot drive any of the applications the model exists for.

## Everything else worth asking for

**Spatial**
- Parent-zone map: which rooms group into which zone, per level
- HVAC-zone map: which rooms belong to which HVAC zone
- Gross area and seating capacity per building and level
- IFC names for anything that must appear in the 3D viewer

**Equipment**
- Nameplate data: model number, manufacturer, rated power, voltage, phase count,
  cooling capacity, flow rates, head, speed
- Installation dates
- System membership: which system each asset belongs to
- Part breakdown, where the points hang off a sub-component (fan, motor, VFD, coil)

**Points and telemetry**
- The BMS/telemetry point list with the exact `TimeseriesId` strings
- The `EntityId` each telemetry key belongs to in the external database
- Units per point
- Which points are aggregations, with function and interval
- Virtual meter formulas, and which physical meters feed them

**Scope**
- Which applications must this model support? Completeness is defined by the
  applications, not in the abstract. Ask this early - it decides how deep the
  point list has to go.

## Decoding packed identifiers

Source spreadsheets almost always pack several facts into one string:

```
entity:QNL_B_063_PLANT_ROOM_01
        |   |  |   |
        |   |  |   room name  PLANT ROOM 01
        |   |  room id        063
        |   level             B  (basement)
        building              QNL
```

**Do not infer the segment order from one example.** Ask:

> Your room identifiers look like `QNL_B_063_PLANT_ROOM_01`. Can you confirm the
> segments: building `QNL`, level `B` = basement, room ID `063`, room name
> `PLANT ROOM 01`? And how are upper levels encoded - `01`, `L01`, `F1`?

Ask about abbreviations in the same message. They end up in `rdfs:label_en`,
where end users read them:

> Please expand these so the labels are right: SSS, TECH, VEST, USDP, UPP, HRAHU.

## When an input is missing and cannot be obtained

Do not invent a value and do not leave a `<placeholder>` in the sheet - the
validator rejects those (`E-PH-1`), and the QF SSC draft shows what happens when
they survive to handover: `entity:<FCU_Serving_Location>` on eleven FCUs, and one
dummy room standing in for nine different exhaust fans.

Instead: omit the row, and list the omission in the handover note under
"blocked on input". A missing row is recoverable; a wrong row that looks
finished is not.
