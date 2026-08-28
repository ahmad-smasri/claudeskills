# QNL manufacturer metadata — handover

Adds the manufacturer metadata from `QNL_Needed_For_Ontology.xlsx` onto the
equipment already in the QNL ontology, following the row shapes Dar Cairo, QF SSC
and QF HQ use. Built by `add_metadata.py` from the pre-metadata ontology
(`sources/QNL_Ontology_pre_metadata.xlsx`).

- **In:** 8,673 triples (no metadata) + the 16-predicate metadata workbook.
- **Out:** 9,274 triples. **+601 rows**: 95 component sub-entities
  (`brick:hasPart`), 506 quantity triples, and 324 literal properties
  (271 on equipment, 53 on components) that ride existing rows.
- **Validator:** 0 new errors, 0 new warnings. The 574 errors / 186 warnings are
  all pre-existing in the base (the accepted `para:IFC_ID has no value` state and
  the accepted `brick:CRAC` / deprecated CHW-temp-sensor aliases).

## The two row shapes (from the reference models)

- **Literal** (`rec:modelNumber`, `rec:manufacturedBy`, `rec:installationDate`) —
  a `subject_prop` on the equipment's existing `rec:locatedIn` row, or an
  `object_prop` on a component's `brick:hasPart` row. Dar Cairo writes these as
  properties, never as a standalone triple.
- **Quantity** (capacities, flows, power, current, head, speed, stage count,
  refrigerant, tank level) — its own triple whose object is a `<blanknode>`
  carrying `brick:value` and `brick:hasUnit`. Units and values are the
  workbook's `Value (Dar Cairo)` / `Unit (QUDT)` columns — **not** QF HQ's, which
  the workbook README documents as wrong (an air flow tagged `unit:V`, a cooling
  capacity tagged `unit:HZ`).

## Component sub-entities

Where a property belongs to a part, it attaches to a component sub-entity created
with `brick:hasPart`, exactly as Dar Cairo does (`entity:<AHU>_CHW-Coil`,
`entity:<fan>_Motor`). All component classes are Brick 1.4 preferred terms — no
`para:` class was minted.

| Component | Sub-entity | Class |
|---|---|---|
| AHU cooling coil | `_CHW-Coil` | `brick:Chilled_Water_Coil` |
| AHU auxiliary cooling coil | `_Aux-Coil` | `brick:Chilled_Water_Coil` |
| AHU electric (reheat) coil | `_Electric-Coil` | `brick:Heating_Coil` |
| AHU supply fan / return fan | `_SF` / `_RF` | `brick:Supply_Fan` / `brick:Return_Fan` |
| AHU / pump drive motor | `_SF_Motor`, `_RF_Motor`, `_Motor` | `brick:Motor` |
| DX outdoor unit | `_OD` | `brick:Condensing_Unit` |

Fan drive motors hang on the fan (`_SF → _SF_Motor`), not on the AHU, matching
Dar Cairo. Unit-level properties (a VAV's air flow and reheat, an FCU's capacity,
a CCU's performance, a pump's duty, a heat exchanger's duty) attach to the
equipment itself.

## Coverage — 243 datasheet tags placed, 8 families

| Family | Matched | Notes |
|---|---|---|
| AHU | 15 / 15 | coil, aux coil, electric coil, supply+return fan, both motors |
| DX | 16 / 16 | indoor model on the unit, outdoor model on `_OD`, stage count |
| Heat Exchangers | 5 / 5 | `PHX/B/0n → HEX0n` by index (prefixes differ; **confirm**) |
| Pumps | 4 / 4 | `CHWP/B/0n → CHW_P0n`; motor size/speed on `_Motor` |
| Generators | 1 / 1 | `GENERATOR SET → ELEC_Gen` |
| Exhaust Fans | 27 / 39 | `TEF_/KEF_` direct, `EF/B/n → EF_B0n` |
| CAV | 35 / 42 | `/`→`_`, last segment zero-padded |
| VAV | 140 / 178 | same |

## Left without metadata — reported, not guessed (94 tags)

Per the instruction not to assume a unit shares its siblings' metadata:

- **FCU (28)** — the datasheets are keyed by Euroclima **selection-sheet
  position** (`FCU/B/01`, `B/03,04`, `B5`), which do not correspond to the BMS
  register tags (`FCU_B_003` …). No reliable per-unit join. *If you can supply a
  position → tag map, all 137 FCUs can be filled.*
- **Closed Control Units (5)** — design tags `CC/B/01…09`; the ontology's CCUs are
  the BMS-tagged orphans `CCU_8081…8086`. Different naming systems, and counts
  differ (9 vs 6). Needs a mapping.
- **Climate Control Units (3)** and **Pressurization Unit (1)** — no matching
  equipment entity exists in the ontology (`MCG-10P`, `PU/B/01`).
- **Out-of-scope units:** CAV 7, VAV 38, EF 12 — these datasheet tags name units
  that are **not in the ontology's register** (e.g. VAV 1F/S15 runs 001–012 then
  021–025, so 013–020 have no entity; EF `RP`/`BV` fans are absent). Metadata for
  a unit that is not modelled has nowhere to attach.

Every tag and its verdict is in `QNL_metadata_join_report.csv`.

## Open points for the team

- **Heat-exchanger join** `PHX/B/0n → HEX0n` is by index; confirm the numbering
  lines up (the drawing schedule stops at `PHX/B/04`, `PHX/B/05` is the "Main HEX").
- **DX outdoor units** — five DX units (`B/03,04,08,09,14`) take an X2 (two
  condensers). Only one `_OD` per unit is modelled, carrying the single model the
  schedule gives; the pipework layout is still needed to split them.
- **Expansion tank** capacity is written `para:Rated_Tank_Level` per the
  workbook; `brick:volume` would outrank it by the ladder — reversible in one line
  if the team prefers (moot until the pressurisation unit is modelled).
- The 574 pre-existing `para:IFC_ID has no value` errors remain — the BIM GUIDs
  were never supplied.
