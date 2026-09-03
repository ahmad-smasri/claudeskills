# QNL ontology v2 - room subjects and equipment locations

`QNL_Ontology_v2.xlsx`, built from `QNL_Ontology.xlsx` by
`update_ontology_rooms.py`. 9,985 rows, one more than v1.

```
python3 projects/QNL/update_ontology_rooms.py \
    --out projects/QNL/QNL_Ontology_v2.xlsx \
    --crosswalk-out projects/QNL/QNL_room_crosswalk_v2.csv \
    --log projects/QNL/QNL_ontology_v2_changes.csv
```

## What changed

| | count |
|---|---|
| room subjects rewritten into the Dar Cairo shape | 353 |
| cells rewritten to follow them | 1,398 |
| `rec:locatedIn` retargeted | 21 |
| `rec:feeds` retargeted with them | 21 |
| `rec:feeds` deliberately left alone | 22 |
| rooms added | 1 |
| rows added | 1 |
| cells changed outside the subject and object columns | 0 |

`entity:QNL_B_063_PLANT-ROOM-01` is now `entity:QNL_B-063_Plant-Room-01`.
Every room used as an object is declared; no subject is malformed; the
validator reports the same 887 errors and 186 warnings as v1, and the
consistency checker the same 590 and 552, so nothing was broken on the way.
Advisories fell from 35 to 9.

## The shape changed; the names did not

The first cut took each room's name from the naming sheet, and that was wrong.
The sheet's names come from the asset register, which carries typos the
delivered ontology does not: it would have written `ARABIC SUDIES` over `ARABIC
STUDIES`, `TRANSH CHAMBER` over `TRASH CHAMBER`, `SHIPPING CLIRK` over
`SHIPPING CLERK`, across 62 labels. The sheet's authority is **which room a
unit is in**, not what the room is called. So the rename is shape-only, every
name and every label is the one already delivered, and the sheet supplies a
name only for a room the ontology does not have.

## Which predicate moved

`rec:locatedIn` moved for all 21 units whose room changed. `rec:feeds` moved
with it only where the unit already fed the room it sits in - that is every
VAV, FCU, CAV, DX and CCU here.

**22 units feed somewhere other than where they sit and their feeds row was not
touched**: exhaust fans, toilet exhaust fans, kitchen exhaust fans and the five
chilled-water pumps. `TEF_B01A` sits in `B.110 Plant Room 03` and serves
`B.046 Rest Room Men`; `CHW_P01` sits in `B.220 Plant Room 04` and feeds
`entity:QNL_CHWS-MAIN-LOOP`. The naming sheet gives one room per unit and on
every one of these it is the location, so it has nothing to say about what they
serve. The full list is in `QNL_ontology_v2_changes.csv`.

## What needs your decision

- **11 references carry more than one room in the ontology**, and five of those
  pairs look like the same room declared twice - `B_044_BOH-B-O-H-KITCHEN` and
  `B_044_BOH-KITCHEN`, `B_214_IDF-IDF-ROOM` and `B_214_IDF-ROOM`,
  `L1_067_RES-RESTAURANT` and `L1_067_RESTAURANT`, `L1_104_FEM-PRAYER-ROOM-FEMALE`
  and `L1_104_PRAYER-ROOM-FEMALE`, `B_057_AD-OFFICE-AD-FOR-LIT` and
  `B_057_OFFICE-AD-FOR-LIT`. Nothing was merged - merging rooms is destructive
  and `L1.104` really does hold a male and a female prayer room. They are all in
  the crosswalk.
- **11 units keep a room the sheet disagrees with**, because the ontology is more
  specific than the sheet at that reference: four FCUs stay in
  `L2-088_Lounge-Area` where the sheet says `Bridge-Raised-Floor`, and four VAVs
  stay in `L1-023_2-Corridor` where the sheet says just `Corridor`. Coarsening
  them would lose a distinction the sheet cannot express.
- **`B.203`** is `Storage-Room` in the ontology and `Technical-Services` in the
  sheet. `VAV_B_S10_009` moved to the ontology's room; the name disagreement
  stands.
- **`L1-144_ILL-Director` now has no equipment.** `FCU_1F_058` moved to
  `L1-145_ILL-Director`, which the drawings give and the ontology did not have.
  If 144 and 145 are one room, 144 should be retired.
- The 13 QNL rows with no room at all are unchanged and still carry no
  `rec:locatedIn` from this sheet.
