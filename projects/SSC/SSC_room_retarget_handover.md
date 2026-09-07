# SSC ontology - room subjects and equipment locations

`reference-models/QF_SSC_Ontology_V03.xlsx` **is** this change: the converted
model replaced the file in place, so there is one SSC ontology. The pristine
V03 as supplied is in git history one commit earlier.

```
git show <that commit>:reference-models/QF_SSC_Ontology_V03.xlsx > /tmp/SSC_pre.xlsx
python3 projects/QNL/update_ontology_rooms.py --code SSC \
    --ontology /tmp/SSC_pre.xlsx \
    --out reference-models/QF_SSC_Ontology_V03.xlsx \
    --crosswalk /dev/null \
    --crosswalk-out projects/SSC/SSC_room_rename_crosswalk.csv \
    --log projects/SSC/SSC_room_retarget_changes.csv
```

## What changed

| | count |
|---|---|
| room subjects rewritten into the Dar Cairo shape | 162 |
| cells rewritten to follow them | 462 |
| `rec:locatedIn` retargeted | 44 |
| `rec:feeds` retargeted with them | 43 |
| `rec:feeds` deliberately left alone | 4 |
| rooms added | 4 |
| rows added | 4 |
| cells changed outside the subject and object columns | 0 |

`entity:SSC_01_024_CORRIDOR` is now `entity:SSC_01-024_Corridor`. The rename is
shape-only - every room name and every label is the one V03 already carried.
Validated with `--label-style verbatim`, which is SSC's house style: **11 errors
and 318 warnings, down from 12 and 319**, because seven exhaust fans stopped
pointing at a placeholder.

## Which predicate moved

`rec:locatedIn` for all 44 units whose room changed, and `rec:feeds` with it on
the 43 that already fed the room they sit in.

**Four units feed somewhere other than where they sit and their feeds row was
not touched** - `CHW_CHWP01` to `CHW_CHWP04`, which sit in a plant room and feed
`entity:CHWS-MAIN-LOOP`. Their locations did not need changing either: the
register agrees with the ontology on all four.

## Rooms added

Four rooms carry equipment and were not declared:

| room | why |
|---|---|
| `entity:SSC_01-206_Corridor` | `TEF0102` |
| `entity:SSC_03-006A_Room` | `VAV0062` - the ontology had one `03.006 Meeting Room` where the drawings and the screen give two |
| `entity:SSC_03-006B_Room` | `VAV0064` |
| `entity:SSC_B-033_Closet` | `DX-B-0006` |

Each is a `rec:Room`, `rec:isPartOf` the level the ontology already declares -
`entity:SSC_Level-B1`, not `entity:SSC_B`, which is what QNL calls its basement
and would have created three orphans here.

## Seven fans were pointing at nothing

`entity:Level7_Office0367` is not an SSC room - it carries no label and its name
belongs to another building. `GEFB0001`, `KEF-1F-0103`, `KEF0303`,
`TEF-1F-0101`, `TEF0102`, `TEF0301` and `TEF0302` all had `rec:locatedIn`
pointing at it. Each now names the room the register gives it, and nothing in
the file references the placeholder any more. The last two joined only after the
tag match was allowed to drop a level segment the register writes and the
ontology does not - `KEF-1F-0103` is `SSC_KEF0103` - which is safe here because
every other member of both families matches exactly.

## What needs your decision

- **`entity:Level7_Office0367` is still declared** and now has nothing pointing
  at it. Nothing was deleted; retiring it is your call.
- **`03.006A` and `03.006B`**: the drawings and the BMS screen disagree on which
  is which, and the screen was followed. Confirm the split.
- **`entity:SSC_ST-10_STAIR-10`** has no level segment, so it became
  `entity:SSC_ST-10_Stair-10` and is attached to `entity:SSC_Level-01`. If the
  stairwell spans floors, that parent is a guess worth checking.
