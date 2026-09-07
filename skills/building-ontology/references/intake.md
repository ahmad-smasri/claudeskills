# Intake: what to request, and how to ask for it

Ask once, in one message, for everything missing. Chasing inputs one at a time
is the slowest way to build a sheet.

## Ask the scope question first

> Do you want the whole building modelled, or a specific part of it?

If the answer names a part - "just the spatial hierarchy", "the AHUs on level 3",
"electrical only" - build exactly that. If there is no answer, build everything
the building requires.

## Ask the identifier question next

> Your source sheets already carry identifiers. Keep them exactly as they are, or
> normalise them to the PARA naming convention?

Default to keeping them - they are the join key to SCADA, the assets register and
the room schedule. See `naming-and-labels.md`. Ask before writing a single row;
re-identifying a finished sheet means regenerating all of it.

### Which site entity, exactly

> Which site does this building sit under, and does that site already have an
> identifier in another building's sheet? QF SSC uses `entity:QF` labelled
> Qatar Foundation.

The site is the one identifier shared across projects. Two sheets that spell it
differently do not join when the converter loads them into one graph, and
nothing in either sheet reveals the clash. Ask rather than mint.

## And the label question, in the same breath

> Labels: strip the punctuation per the PARA label rule (`1.001 CORRIDOR`), or
> carry the source text verbatim the way QF SSC does (`1.001_CORRIDOR` - a dot
> between level and room number, an underscore before the name)?

Neither reference model settles it - SSC is verbatim, Dar Cairo is a third style,
and the label rule is newer than both. Ask, then run the validator with the
matching `--label-style` and name the choice in the handover note.

## And whether to correct the schedule's spelling

Keeping the source text verbatim keeps its typing errors too, and they do not
stay hidden in the identifier - the same string becomes the label a user reads:

> Your room schedule has misspellings - `STUDENT_CARRLES` for CARRELS,
> `LOBY_&_CSECURITY` for LOBBY & SECURITY, `REST_ROOMMEN` run together. They
> will show on screen as written. Correct the ones the schedule itself proves,
> or keep every name exactly as typed and take the list in the handover note?

Ask it separately from the identifier question - the answers are often different,
and were on QNL, where the shape was kept and the spelling corrected. Default to
keeping and reporting. `naming-and-labels.md` has the rules that apply once the
answer is to correct, and the reason asset tags stay untouched either way.

## The mandatory inputs

| # | Input | Usually arrives as | Blocks |
|---|---|---|---|
| 1 | Building name, and **the site entity the client already uses** | a sentence, or an existing sheet | every row |
| 2 | Levels - full list, including basements and roof | floor schedule | spatial layer |
| 3 | Rooms and spaces - name, number, and any tag or ID | room schedule / BIM export | spatial layer |
| 4 | Equipment - the asset register | equipment schedule | equipment layer |
| 5 | Location of each asset - room or level | asset register column | equipment layer |
| 6 | Feeds / fed-by for each asset | single-line diagram, schematic, or a schedule column | feeds layer |
| 7 | **IO lists** | BMS/controls IO schedule | every point |
| 7b | **The selected-datapoint list, if one exists** | integration scope sheet, "Must Have" columns | which points survive |
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

### 7b. The selected-datapoint list

An IO list is an inventory of what the BMS publishes. A **selected-datapoint
list** - a scope sheet, an integration schedule, a column reading "Must Have" -
is what the project agreed to *deliver*, and it is always the smaller of the two.
Where both exist, the selected list is the scope authority and the IO list is
evidence beneath it. Ask for it in the same message as the IO list, because
finding it late means deleting points rather than never writing them.

> Is there a selected-datapoint or integration-scope list for this project - the
> agreed subset of BMS tags we are delivering, as opposed to everything the
> historian carries? If there is, please send it, and tell me which column marks
> a tag as in scope.

Two failure modes, both of which validate clean:

- **A tag the historian carries and the selection omits is not a gap.** It is a
  decision someone already made. Adding it back because the IO list evidences it
  puts a point in the sheet that the integration will never populate.
- **A point the sheet invents on purpose is not an overrun.** A `para:` container
  the backend fills by calculation is correctly absent from a list of BMS tags.
  Exempt it by name in the reconciliation and name it in the handover note.

Reconcile both directions before handover: every selected tag present in the
sheet, and no timeseries id in the sheet that is not selected, bar the named
exemptions. Where the selection omits something the asset register proves is
real - a box serving a room no other box serves - flag it to the client as a
probable omission in *their* document rather than quietly restoring it.

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
- **Which meters the building physically has, and what each one measures.** A
  virtual meter only fills a gap, so this list decides which ones to build - and
  it usually cannot be read off the sheet, because physical meters routinely
  carry no `brick:meters` row
- **Virtual meters: which tiers (Building, Floor, Room) and which meter types at
  each.** Ask as a matrix; the count follows as arithmetic and is worth saying
  back before building. Ask in the same breath whether the terminal units get
  `para:contributionFraction`, and where the calculation engine's telemetry keys
  come from - a field IO list never carries them. `virtual-meters.md` has the
  wording and the default matrix
- Virtual meter formulas, and which physical meters feed them

**Scope**
- Which applications must this model support? Completeness is defined by the
  applications, not in the abstract. Ask this early - it decides how deep the
  point list has to go.

## Confirm anything that looks like a contradiction in the source

Source data throws up combinations that read as errors and are not. **Ask; do not
resolve them silently, and do not resolve them in the handover note after the
fact.** A one-line question before writing rows is cheaper than a reviewer
re-deriving your reasoning afterwards.

The one that comes up on every building:

**Equipment whose level does not match the level of the room it serves.** On QNL,
53 VAVs tagged `2F` served `L1` rooms. That is not a data error - the rooms are
double-height with an open roof, so the box hangs at level 2 over a level 1 space
and `rec:locatedIn` and `rec:feeds` legitimately name the same room. Mezzanines,
atria, voids and plant platforms all produce it.

> 53 of your VAVs carry a level token that differs from the level of the room in
> the Room Tag column - e.g. `VAV_2F_S12_001` against `QNL_L1_001_OPEN_READING_AREA`.
> Are those double-height or open-roof spaces, so the unit is genuinely located in
> and feeding the same room? Or is the Room Tag the space served only, with the
> physical location held somewhere else?

**Identifiers that do not all follow the same shape** is the other recurring one,
and it is why "keep the source verbatim" is not the end of the identifier
question. Read the whole column, work out the majority shape, list the
departures, and ask. On QNL, 51 of 336 room identifiers ran the level into the
room number (`QNL_B036_REST_...`) where the other 285 kept them as separate
segments (`QNL_B_034_MEETING_ROOM`).

> 51 of your 336 room identifiers use a different shape from the other 285 -
> `QNL_B036_REST_REST_ROOM_WOMEN`, `QNL_B-ST-01_ST-01`, `QNL_L1023_1_CORRIDOR`.
> Regularise them to the majority shape, or keep them exactly as the schedule
> has them?

Others in the same family, all worth one question rather than one assumption:

- one room column in an asset register, when the model needs both a location and
  a served space - is it one, the other, or both?
- an asset whose type prefix disagrees with its class column
- rooms present in the asset register but absent from the room schedule, or the
  reverse
- a room number carrying no level prefix when every sibling has one

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
