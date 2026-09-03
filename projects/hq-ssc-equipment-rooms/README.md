# HQ and SSC equipment and the rooms they are in

One workbook - `HQ_SSC_equipment_rooms.xlsx` - putting two sources side by side
for every piece of equipment in the HQ and SSC ontologies that is **not** an
AHU, a VAV or an FCU. Those three families were the subject of the earlier BMS
screen pass and are left out here.

| Source | Column | Where it comes from |
|---|---|---|
| BMS screens | `Room per BMS screen` | the room the dotted serving-area leader points at, harvested from `../bms-room-allocation/*_alloc.py` |
| Ontology | `Room per ontology` | `rec:locatedIn` on the equipment entity, named by that room entity's own `rdfs:label_en` |

## The screen column covers SSC only

19 units, all from the SSC screens. The HQ pass read VAVs and FCUs and never
traced the plant icons, and the HQ screen images are not in the repo to
re-read - only the readings were committed. So every HQ row here is judged on
the ontology alone.

## What counts as needing revision

85 of the 130 rows are filled green. Four reasons, spelled out per row in the
`Why` column:

| Reason | Rows |
|---|---|
| the ontology points at the placeholder `entity:<Location>` rather than a room | 52 (HQ) |
| the two sources name different rooms | 11 (SSC) |
| a CRAC - a computer-room unit - is located in a VVIP parking bay | 8 (HQ) |
| the room entity `entity:Level7_Office0367` carries no readable name | 7 (SSC) |
| the `rec:locatedIn` row carries no room at all | 6 (HQ) |
| the equipment carries points but has no `rec:locatedIn` | 2 (HQ generators) |

Rows can carry more than one reason, so those do not sum to 85.

## Two patterns worth knowing before reading the rows

**The SSC exhaust fans are all in one office.** All seven - `GEFB0001`,
`KEF0103`, `KEF0303`, `TEF0101`, `TEF0102`, `TEF0301`, `TEF0302` - are located
in `entity:Level7_Office0367`, a room entity with no name. The screens put
`KEF-1F-0103` in `01.005 KITCHEN` and `TEF-1F-0101` in `01.028 CORRIDOR`, which
is where kitchen and toilet extract fans belong.

**The SSC DX rooms look filled down.** `DXB0001` to `DXB0004` all carry
`B1.005 UPS` while the screens spread the same four units across SSP, UPS and
VENT PLANT; `DXB0007` and `DXB0008` share `B1.019 FM STORAGE` the same way.
A block of units carrying one room where the screens disagree is the signature
of a fill-down rather than of a reading - the same thing the RDC pass found in
the air terminal schedules.

## Running it

```
python3 build.py          # writes HQ_SSC_equipment_rooms.xlsx
```

`ontology.py` reads a delivered ontology - picking the sheet by its header, not
by tab name, because the HQ tab is spelled `HQ_Onotlogy_Draft_v0.4`.
`screens.py` harvests the BMS readings and normalises a tag so the two sides
spell it the same way: the screens pad a number to three digits where the
ontology pads to four, and the screens carry a level segment the ontology drops
(`KEF-1F-0103` is `entity:SSC_KEF0103`).

Green is `FF00B050`, the same fill the asset register uses for rows that want
a human eye.
