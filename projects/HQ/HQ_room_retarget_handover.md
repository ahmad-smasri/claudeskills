# HQ ontology - room subjects, equipment locations and virtual meters

`reference-models/QF_HQ_Ontology_V02.xlsx` **is** this change: the converted
model replaced the file in place, so there is one HQ ontology. The pristine V02
as supplied is in git history one commit earlier.

```
git show <that commit>:reference-models/QF_HQ_Ontology_V02.xlsx > /tmp/HQ_pre.xlsx
python3 projects/QNL/update_ontology_rooms.py --code HQ \
    --ontology /tmp/HQ_pre.xlsx \
    --out reference-models/QF_HQ_Ontology_V02.xlsx \
    --crosswalk /dev/null \
    --crosswalk-out projects/HQ/HQ_room_rename_crosswalk.csv \
    --log projects/HQ/HQ_room_retarget_changes.csv
```

## What changed

| | count |
|---|---|
| room subjects rewritten into the Dar Cairo shape | 1,046 |
| cells rewritten to follow them | 8,064 |
| `rec:locatedIn` retargeted | 41 |
| `rec:feeds` retargeted with them | 32 |
| `rec:feeds` deliberately left alone | 19 |
| rooms added | 4 |
| virtual meters added | 4 rooms x 24 rows |
| rows added | 100 |
| cells changed outside the subject and object columns | 0 |

`entity:HQ_10_002C_OFFICE_SPACE` is now `entity:HQ_10-002C_Office-Space`. The
rename is shape-only - every room name and every label is the one V02 carried.

Validated in HQ's verbatim label style: **11,887 errors and 18,189 advisories,
identical to V02**, and every warning code identical but one - `W-BN-4` goes
from 3,200 to 3,212, which is three per new room, the `brick:isVirtualMeter`
blank-node row that all 1,045 existing rooms already produce. The new rooms are
indistinguishable from the old ones to the validator, which is the point.

Those figures are the validator as it stands after the merge with `main`; an
earlier cut of this note quoted 11,884 / 3,212 -> 3,224, which was the same
comparison under the older validator. The relationship is what matters and it
did not change: errors and advisories identical, warnings up by exactly twelve.

## The virtual meters

Every HQ room carries three: HVAC, CHW and LTG. Each is eight rows - part of
`entity:Metering`, `brick:meters` and `rec:locatedIn` the room, flagged
`brick:isVirtualMeter` with `brick:value True`, and a Consumption and a Demand
point each carrying a timeseries reference. 24 rows a room.

The four rooms added here carry the same 24. **They were not hand-written**: one
complete room is read out of the ontology and used as the pattern, with its
subject and label prefix swapped for the new room's, so a class, a predicate or
a timeseries id cannot drift from house style. The donor is the first room in
sorted order with a complete block, so a re-run picks the same one.

Worth knowing: the room timeseries ids are `AT_HVAC_PWR_KWH_CALC` and
`AT_HVAC_DEMAND_KW_CALC`, which is what all 1,045 rooms use. The building and
the fourteen levels use `HVAC_KWH_CALC` / `HVAC_KW_CALC` instead. Copying from a
room rather than from a level keeps the new rooms on the room form.

| room added | for | meters |
|---|---|---|
| `entity:HQ_3-630_Corridor-Bridge` | `FCU0067`-`FCU0070` | 3 |
| `entity:HQ_11-208_Sheikha-Wing-Sheikha-Ensuit` | `VAV0584`-`VAV0587` | 3 |
| `entity:HQ_B1-105_Support-Space-Loading` | `GEFB_0010` | 3 |
| `entity:HQ_RF-001_Roof` | the roof AHUs | 3 |

## Which predicate moved

`rec:locatedIn` for all 41 units whose room changed, and `rec:feeds` with it on
the 32 that already fed the room they sit in.

**19 units feed somewhere other than where they sit and their feeds rows were
not touched.** None of their locations needed changing either.

## What was deliberately left alone

- **`4.105`** is declared twice in V02 - `4.105 JAN JANITORS CLOSET` and
  `4.105 PAN PANTRY`. The register gives `FCU0072` the reference but not which
  of the two, and its own name matches neither, so the unit keeps the room it
  had. Picking one would be a guess.
- **`10.03` / `10.030 PANTRY` and `4.11` / `4.110 PRINT COPY`** are each the
  same room declared twice, once with the trailing zero Excel ate off the
  reference. Nothing was merged: the truncated one keeps its own reference so
  both survive, and the pair is in the crosswalk for you to retire one.
- **Three roof exhaust fans** - `GEFB_0007`, `GEFB_0010`, `GEFB_0011` - are
  `rec:locatedIn entity:HQ-Level-Roof`, a level rather than a room. That is a
  modelling choice, not something to reinterpret.
- **`entity:HQ_PLANT_ROOM` and an empty room object on three `rec:feeds` rows**
  were already undeclared in V02 and still are.
