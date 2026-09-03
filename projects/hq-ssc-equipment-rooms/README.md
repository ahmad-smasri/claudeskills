# HQ and SSC equipment and the rooms they are in

One workbook - `HQ_SSC_equipment_rooms.xlsx` - putting two sources side by side
for every piece of equipment in the HQ and SSC ontologies that is **not** an
AHU, a VAV or an FCU. Those three families were the subject of the earlier BMS
screen pass and are left out here.

| Source | Column | Where it comes from |
|---|---|---|
| BMS screens | `Room per BMS screen` | the room the dotted serving-area leader points at, harvested from `../bms-room-allocation/*_alloc.py` |
| Ontology | `Room per ontology` | `rec:locatedIn` on the equipment entity, named by that room entity's own `rdfs:label_en` |

## The screen column

28 readings: 19 harvested from the earlier SSC pass, and 9 traced fresh off the
HQ screens with `annotate_all.py` from the QNL project - the HQ pass had only
ever read VAVs and FCUs, so its plant icons had never been followed.

The HQ car park screens carry no room names at all - parking bay numbers,
`Exit`, `Public Vehicle Out` and nothing else - so the twenty-seven CEF fans
get the deck they are drawn on and no room. The ontology's `entity:<Location>`
placeholder cannot be resolved from those screens.

## What counts as needing revision

85 of the 130 rows are filled green. Four reasons, spelled out per row in the
`Why` column:

| Reason | Rows |
|---|---|
| the ontology points at the placeholder `entity:<Location>` rather than a room | 52 (HQ) |
| the car park deck the screen shows carries no room names, so the placeholder cannot be resolved from it | 25 (HQ) |
| the unit is drawn on a BMS screen and the ontology has no entity for it at all | 18 (HQ) |
| the two sources name different rooms | 14 (11 SSC, 3 HQ) |
| the room entity `entity:Level7_Office0367` carries no readable name | 7 (SSC) |
| the `rec:locatedIn` row carries no room at all | 6 (HQ) |
| the equipment carries points but has no `rec:locatedIn` | 2 (HQ generators) |

Rows can carry more than one reason, so those do not sum to 99.

## A flag the screens took back

An earlier build flagged eight HQ CRACs because the ontology put them in VVIP
parking bays and a computer-room unit in a car park reads like a fill error.
The screens say otherwise: `CCU-B-0005` to `CCU-B-0008` all lead into
`VIP Parking B.115` on `Basment Floor/BF-2`, which is what the ontology says
for three of them and fills the placeholder for the fourth. That flag was my
inference and it was wrong, so it is gone. Only `CCU-B-0003A` survives it - its
dot is in the Chauffer Room band, one wall north of the VIP parking.

## Equipment the ontology does not have

Ten jet fans (`JF-B-0001` to `JF-B-0010`) and eight induction fans
(`IF-B-0001` to `IF-B-0008`) are drawn on the HQ car park screens and the HQ
ontology has no entity for any of them - not a wrong room, no entity at all.

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
