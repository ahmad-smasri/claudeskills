# Intake: what to request, and how to ask for it

Ask once, in one message, for everything missing. Chasing inputs one at a time
is the slowest way to build a sheet.

## Ask the scope question first

> Do you want the whole building modelled, or a specific part of it?

If the answer names a part - "just the spatial hierarchy", "the AHUs on level 3",
"electrical only" - build exactly that. If there is no answer, build everything
the building requires.

## The mandatory inputs

| # | Input | Usually arrives as | Blocks |
|---|---|---|---|
| 1 | Building name (and site, if the building sits under one) | a sentence | every row |
| 2 | Levels - full list, including basements and roof | floor schedule | spatial layer |
| 3 | Rooms and spaces - name, number, and any tag or ID | room schedule / BIM export | spatial layer |
| 4 | Equipment - the asset register | equipment schedule | equipment layer |
| 5 | Location of each asset - room or level | asset register column | equipment layer |
| 6 | Feeds / fed-by for each asset | single-line diagram, schematic, or a schedule column | feeds layer |
| 7 | **IO lists** | BMS/controls IO schedule | every point |
| 8 | **Manufacturer standards and datasheets** | catalogue extracts, submittals | nameplate properties |

Without 6 the model is not deliverable. A terminal unit that does not say what
room it serves cannot drive any of the applications the model exists for.

### 7. IO lists

Equipment carries data points, and the IO list is where they come from: point
names, signal type, units, and the telemetry IDs that become
`ref:hasTimeseriesId`. **Ask for it - never infer a point list from the
equipment type.** Dar Cairo can suggest which points an FCU *usually* has
(`lookup_reference.py --template brick:Fan_Coil_Unit`), and that is useful for
sanity-checking the IO list, not for replacing it.

> Please send the IO list for these assets. I need, per point: the point name,
> whether it is AI/AO/DI/DO or a calculated value, the unit, and the
> TimeseriesId in the telemetry database. Also the EntityId each key sits under.

Equipment with no IO list gets modelled without points, and goes in the handover
note under "no IO list supplied".

### 8. Manufacturer standards and datasheets

Nameplate properties come from the manufacturer, and only from the manufacturer:
`rec:modelNumber`, `rec:manufacturedBy`, `brick:ratedPowerInput`,
`brick:ratedVoltageInput`, `brick:electricalPhaseCount`, `brick:coolingCapacity`,
`para:ratedSupplyAirFlowrate`, `para:ratedChilledWaterFlowrate`,
`para:ratedHead`, `para:ratedSpeed`.

**If the datasheet was not submitted, leave the property out.** Do not write a
typical value, a design value from a different unit, or a placeholder. An empty
property is a known gap someone can fill later; an invented rating silently
corrupts every calculation downstream of it.

## Everything else worth asking for

**Spatial**
- Parent-zone map: which rooms group into which zone, per level
- HVAC-zone map: which rooms belong to which HVAC zone
- Gross area and seating capacity per building and level
- IFC names for anything that must appear in the 3D viewer

**Equipment**
- Installation dates
- System membership: which system each asset belongs to
- Part breakdown, where the points hang off a sub-component (fan, motor, VFD, coil)

**Points and telemetry** - beyond the IO list itself
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

The same holds for a missing property: leave the cell empty rather than filling
it with something plausible.
