# QNL ontology — session summary (2026-08-28)

Building on the Qatar National Library (QNL) PARA/Brick ontology in
`projects/QNL/`. This session added manufacturer metadata, aligned every
identifier to Dar Cairo's convention, verified and gap-filled from a BAS
document, and folded the reusable parts back into the `building-ontology` skill.

## What was delivered

### 1. Manufacturer metadata (`projects/QNL/add_metadata.py`)
- Attached the 16-predicate metadata from `QNL_Needed_For_Ontology.xlsx` onto the
  equipment, in the row shapes Dar Cairo / QF SSC / QF HQ use: **literals**
  (`rec:modelNumber`, `rec:manufacturedBy`, `rec:installationDate`) as props,
  **quantities** (capacities, flows, power, head, speed…) as `<blanknode>` +
  `brick:value` + `brick:hasUnit`.
- Component properties attach to `brick:hasPart` sub-entities (`_CHW-Coil`, `_SF`,
  `_RF`, `_Motor`, `_OD`) — all Brick 1.4 preferred classes.
- Values/units taken from the workbook's **Dar Cairo columns, not QF HQ's** (HQ's
  units are documented wrong).
- **269 datasheet tags placed across 9 families.** FCU landed via **Euroclima
  selection-sheet expansion** (`B/03,04`, `1F/04-54` → the units each names) — 94
  FCUs.
- Unmatched tags **reported, not guessed** (`QNL_metadata_join_report.csv`): closed
  control units, climate, pressurisation, out-of-range CAV/VAV/EF, and FCU 2F.

### 2. Dar Cairo identifier alignment (`align_naming.py`, `align_rooms` pass)
- Rewrote every subject/object identifier to Dar Cairo's convention: `_` between
  segments, `-` between words, **datapoints in dashed English**
  (`AvgSpcHumd_PV` → `Average-Space-Humidity`, `RunSts` → `Run-Status` via the
  point's class), no camelCase, no dots.
- Equipment/part tags **keep their industry codes** (`AHU`, `SF`, `CHW-Coil`) — as
  Dar Cairo does; the full name lives in the type column.
- **Rooms**: 277 name-words dashed, structural prefix `QNL_<level>_<number>` and
  the verbatim label kept.
- **camelCase 71% → 0%.** BMS join keys untouched (`ref:hasTimeseriesId` /
  `para:hasEntityId` keep the raw historian tag); old→new crosswalk written.

### 3. BAS valve-schedule enrichment (`add_bas_metadata.py`)
- Cross-checked against the as-built BAS instrument/valve schedule
  (`sources/BAS_QNL_Assets.pdf`).
- **Verification:** 91 of 94 shared FCU chilled-water flows agree within
  ±0.02 L/s; 3 differ (kept the Euroclima value, logged).
- **Resolved the FCU 2F numbering:** the BAS numbers 2F units `1–5, 34–62` —
  matching the ontology; the Euroclima sheet's `2F/06-33` was a different
  numbering.
- **Gap-fill:** the 43 FCUs with no flow (all of 2F 034–062, 1F 059–065) got
  `para:ratedChilledWaterFlowrate` from the BAS.
- **Control valves:** every FCU/AHU/HEX gained a `brick:Cooling_Valve` part with
  `rec:modelNumber` (FCU valves `V5862A…` + actuators `M7410C…`, Honeywell,
  actuator as a `para:Valve_Actuator` sub-part; AHU/HEX valves `ITQ-…`).

### 4. Skill improvements (`skills/building-ontology/`)
- `references/naming-and-labels.md`: the Dar Cairo naming convention as a settled
  rule (datapoints in dashed English, equipment codes kept, rooms dashed).
- `scripts/align_naming.py`: reusable one-shot retrofit that classifies entities
  from the graph and renames from label-or-class, keeping join keys.
- `SKILL.md` trimmed (~3330 → ~2790 words) and `CLAUDE.md` updated.

### 5. Assumption log (`projects/Assumption_Log.xlsx`, QNL sheet)
- Entries **QNL-023 … QNL-030** record every decision: metadata row shapes,
  Dar-Cairo-vs-HQ units, the FCU Euroclima expansion, the unmatched families left
  blank, the identifier alignment, the BAS gap-fill and control valves, and the 3
  flow discrepancies.

## Key decisions
- Equipment codes (`AHU`, `SF`) are **not** spelled out — Dar Cairo keeps them.
- Metadata a source cannot place is **left blank and reported**, never guessed.
- Closed control, climate and pressurisation units remain **without metadata** —
  no document in this session covers them.

## State at end of session
- Ontology ≈ 9,984 rows; validator **574 errors / 186 warnings throughout** — all
  the pre-existing `para:IFC_ID has no value` (BIM GUIDs never supplied); every
  addition added **zero** new errors/warnings.
- Every FCU now carries at least a flow; all 12 equipment families have metadata
  where a source exists.

## Pull requests
| PR | Contents | State |
|---|---|---|
| #14 | metadata + FCU expansion + Dar Cairo naming + skill updates | merged |
| #15 | room-identifier alignment + FCU 2F record | merged |
| #17 | assumption log QNL-023…028 | merged |
| #18 | BAS enrichment + QNL-029/030 | open |

## Open items
- Closed control units, climate control (MCG-10P) and pressurisation unit (PU/B/01)
  have no metadata source yet.
- 3 FCU flow discrepancies flagged for the supplier (Euroclima 0.27 vs BAS 0.36).
- DX units `B/03,04,08,09,14` take two condensers; only one `_OD` modelled pending
  the pipework layout.
