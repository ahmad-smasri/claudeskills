# Choosing a predicate

## The families

| Family | Question | Predicates |
|---|---|---|
| Composition | what is this made of? | `brick:hasPart`, `rec:isPartOf` |
| Topology | where is it, what is up/downstream? | `rec:locatedIn`, `rec:feeds`, `rec:isFedBy` |
| Telemetry | what data does it produce? | `brick:hasPoint`, `brick:isPointOf` |
| Metering | what does this meter measure? | `brick:meters`, `brick:isMeteredBy`, `brick:isSubMeterOf` |

## What Dar Cairo actually uses

Counts from the primary reference, so this is the house style, not theory:

| Predicate | Rows | Used for |
|---|---|---|
| `ref:hasExternalReference` | 9,584 | timeseries and IFC links |
| `brick:hasPoint` | 9,192 | equipment to its points |
| `brick:isPartOf` | 2,290 | **equipment to its system** (`entity:HVAC`, `entity:Electrical_System`) |
| `brick:hasPart` | 802 | equipment to its components |
| `rec:locatedIn` | 784 | equipment to the room or level it sits in |
| `rec:isPartOf` | 582 | **spatial containment** |
| `brick:meters` / `isMeteredBy` | 497 | meter to what it measures |
| `rec:isFedBy` | 289 | downstream to upstream |
| `rec:feeds` | 278 | upstream to downstream |

The split to remember: **`rec:isPartOf` for spatial containment,
`brick:isPartOf` for system membership.** Both appear, and they mean different
things.

## The spatial hierarchy

As built in Dar Cairo:

```
rec:Site
  └─ rec:Building                     rec:isPartOf
       ├─ rec:Level / rec:BasementLevel / rec:RoofLevel   rec:isPartOf, + rec:levelNumber
       │    └─ rec:HVACZone           rec:isPartOf  -> the Level
       └─ rec:Zone  (parent zone)     rec:isPartOf  -> the Building or the Level
            └─ rec:Room               rec:isPartOf  -> the parent Zone
```

Note this differs from the PARA document's pre-requisite page, which says Room
`isPartOf` HVAC Zone and HVAC Zone `isPartOf` Parent Zone. Dar Cairo puts rooms
under parent zones and HVAC zones under levels. **Follow Dar Cairo; flag the
discrepancy in the handover note.** See `known-issues.md`.

Levels carry `rec:levelNumber` - `0` for ground, negatives for basements.

## Feeds

`rec:feeds` points downstream; `rec:isFedBy` points upstream. Dar Cairo uses both
and they are equivalent statements, so pick a direction per chain and hold it.

**When a piece of equipment conditions or serves a room, `rec:feeds` must name
that room.** From Dar Cairo:

```
entity:FCU-01_GF | brick:Fan_Coil_Unit | rec:feeds |
entity:Dar-Cairo_Ground-Floor_TECH-3_G007 | rec:Room
```

Where the served space is an HVAC zone rather than a single room, the zone is the
correct object:

```
entity:PIM-9 | para:Pressure_Independent_Module | rec:feeds |
entity:Dar-Cairo_Floor-1_1WA-H2 | rec:HVACZone
```

Terminal equipment - VAV, FCU, PIM, CRAC, exhaust fan, radiator, chilled beam -
must have a feeds row. The validator errors (`E-FEED-1`) when one does not.

Upstream chains use the same predicate: switchgear feeds transformer feeds main
breaker feeds distribution board.

### When the unit's level disagrees with the room's level

An asset register that names one room per asset usually means that room is both
where the unit sits and what it serves - so `rec:locatedIn` and `rec:feeds` take
the same object. Fine, until the asset's own tag says it is on a different level
from that room.

**That is not automatically an error, and it is not yours to resolve.** Ask the
user. Double-height rooms, atria, mezzanines and open-roof spaces put the
terminal unit on the level above the space it conditions, and both rows are then
correct as written. QNL had 53 of them: VAVs tagged `2F` feeding `L1` reading
areas with an open roof between the two.

The alternative reading - the room column is the served space only, and the
physical location lives in a column nobody sent - produces a different sheet
entirely. One question decides it. Ask before writing the rows, not in the
handover note afterwards.

## `hasPart` or `locatedIn`?

Brick's test: **is the containment fundamental to the container's identity?**

- A chair in a room -> `rec:locatedIn`. The room is still a room without it.
- A damper in a VAV -> `brick:hasPart`. A VAV is not a VAV without one.

Equipment sits in a room or on a level with `rec:locatedIn`. Its fan, motor, coil
and VFD hang off it with `brick:hasPart`.

## Inverses

`hasPoint`/`isPointOf`, `hasPart`/`isPartOf`, `feeds`/`isFedBy`,
`meters`/`isMeteredBy`, `controls`/`isControlledBy`. The graph is identical
either way; a sheet that mixes directions within one chain is much harder to
review.

## Spatial classes: `rec:`, not `brick:`

Brick 1.4 deprecated every `Location` class in favour of RealEstateCore.
`brick:Building`, `brick:Floor` and `brick:Room` will raise deprecation warnings
and be rewritten by Brick's own SHACL rules. Use `rec:Building`, `rec:Level`,
`rec:Room`, `rec:Zone`, `rec:HVACZone`, `rec:Site`.

Equipment, parts and points stay `brick:`. Anything the team coins is `para:`.
