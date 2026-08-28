# QNL equipment metadata — from submittals to an ontology-ready sheet

**Date:** 2026-08-28 (work spanned two sessions)
**Branch:** `claude/equipment-metadata-excel-coyeg4`
**Deliverables:** `QNL_Full_Metadata.xlsx`, `QNL_Needed_For_Ontology.xlsx` (repo root)
**Builder:** `tools/equipment-metadata/`

---

## What was asked

Collect manufacturer properties for Qatar National Library equipment out of the
submittals and schedules, into an Excel workbook with one sheet per equipment
type, every row naming the source document and page it came from. Then narrow it
to what an ontology actually needs.

## What was delivered

Twelve equipment types, 4,728 transcribed rows, every one carrying its source and
locator. Split at the end into two workbooks:

| Workbook | Rows | Contents |
|---|---|---|
| `QNL_Full_Metadata.xlsx` | 4,728 | Everything — 15 sheets |
| `QNL_Needed_For_Ontology.xlsx` | 1,225 | Only rows that become triples, 16 sheets |

The second is a **filtered view** of the same data, not a second transcription.
One run of `build.py` writes both from `data/*.py`, so they cannot drift.

### Coverage

| Sheet | Units | Full rows | Core rows |
|---|---|---|---|
| AHU | AHU-001 … 015 | 1,552 | 194 |
| FCU | 28 Euroclima positions | 981 | 168 |
| VAV Units | 180 boxes | 717 | 526 |
| Closed Control Units | CC/B/01 … 09 | 371 | 36 |
| Pumps | CHWP/B/01 … 04 | 329 | 28 |
| DX Units | DX/B/01–20, DX/RP/21 | 244 | 48 |
| Heat Exchangers | PHX/B/01 … 05 | 179 | 23 |
| Exhaust Fans | 39 fans | 119 | 107 |
| Climate Control Units | MCG-10P, VCB1000, AF4 | 100 | 7 |
| CAV Units | 42 boxes | 94 | 78 |
| Generators | 1 | 24 | 3 |
| Pressurization Unit | PU/B/01 (PRO1) | 18 | 7 |

---

## Key decisions

### 1. Units follow Dar Cairo, read off the model rather than assumed

Targets came from counting predicate/unit pairings in `DarCairo_V93.csv`, not from
guessing. That settled the ambiguous cases: `para:ratedSupplyAirFlowrate` and
`para:ratedChilledWaterFlowrate` both use `unit:L-PER-SEC`, so **air flow and water
flow land together**; power on `unit:KiloW`; length on `unit:M` (from
`para:ratedHead`); relative humidity on `unit:PERCENT_RH`, which Dar Cairo keeps
distinct from `unit:PERCENT`.

Every row keeps **both** pairs — `Value (as printed)` / `Unit (as printed)` for
traceability, `Value (Dar Cairo)` / `Unit (QUDT)` for `brick:hasUnit` — plus a
`Conversion` cell naming the arithmetic and any assumption.

Conversions: m³/s ×1000, m³/h ÷3.6, l/h ÷3600 → l/s; W ÷1000 → kW; kPa ×1000,
mbar ×100 → Pa; mm ÷1000, in ×0.0254 → m; lb ×0.45359237 → kg.

**One standing assumption:** `kg/s` → `l/s` treats water as 1 kg/l. Chilled water
at 7–15 °C is ~0.9997 kg/l, so converted flows are high by ~0.03%. Written into
the `Conversion` cell of every affected row.

### 2. Brick 1.4 is checked before the reference models

The class ladder puts Brick at step 2 and the delivered models at step 3. An
early pass went straight to step 3; correcting that changed several mappings.

Brick has **no water or air flow-rate entity property** and **no heat-exchanger
duty property** — which is exactly why Dar Cairo minted
`para:ratedChilledWaterFlowrate`, `para:ratedWaterFlowrate` and the air-flowrate
family. Where Brick *does* carry the term, Brick wins:

| Use | Predicate | Source |
|---|---|---|
| heat exchanger duty | `brick:coolingCapacity` | Brick 1.4 |
| full load current | `brick:ratedCurrentInput` | Brick 1.4, unused by any reference model |
| fan speed count | `brick:operationalStageCount` | Brick 1.4, unused by any reference model |
| outdoor DX unit | `brick:Condensing_Unit` entity carrying `rec:modelNumber` | Brick 1.4 |

### 3. Scope: most of the workbook is not ontology metadata

Counting predicates across Dar Cairo, QF SSC and the QF HQ v0.4 draft, equipment
metadata is ~20 predicates. Every row carries an `Ontology predicate` and a
`Scope`:

- **core** — 55 properties, **1,225 rows**, 16 predicates.
- **reference** — 517 properties, 3,418 rows. Dimensions, weights, materials,
  seal specifications, sound power levels, filter part numbers, psychrometrics,
  warranty text. Kept because engineers want them, not because they will be modelled.

The **Ontology Scope** sheet lists all of them with the predicate, its provenance
and row counts.

**A component's maker is not the equipment's manufacturer** — the pump's seal is
made by Armstrong and its motor by WEG; neither becomes `rec:manufacturedBy` on
the pump. Matched out explicitly before the general rule.

### 4. CAV/VAV split to one row per box

Schedules write ranges (`VAV/B/S11/001 TO 020`). Each is split so every box carries
its own air flow, heating capacity, model and make, plus a `Scheduled as` row
naming the line it came from. A range is only split when its box count matches the
stated QTY.

### 5. Identifiers kept verbatim

Two exhaust-fan tag families (28 slash-separated, 11 underscore) both kept — the
tag is the BMS join key. Where two documents tag the same unit differently
(`CHWP/B/01` vs `CHWP-B-01`, `PU/B/01` vs `PRO1`), the slash form is the Equipment
Tag and the other is recorded as an `Alternate reference` property.

---

## Corrections made during the work

- **DX condenser pairing.** The schematic numbers condensers to match indoor units,
  so `DX/B/nn` ↔ `DX/OD/nn` was recorded, flagged as convention. SYSTEM DETAILS
  Table 3.6 disproved it: `DX/B/03`, `04`, `14` take a `PUHZ-RP200X2` and
  `DX/B/08`, `09` a `PUHZ-RP250X2` — **X2 means two condensers per indoor unit**.
  Those five need two `DX/OD` tags each and the numbering does not say which.
- **A fifth heat exchanger.** `PHX/B/05` (300 kW M10-MFM, "Main HEX") appears on
  the Alfa Laval data and SYSTEM DETAILS but **not** on the drawing schedule.
- **Dimensionless matcher bug.** "Schedule s**cop**e" was matching the `cop`
  substring and being tagged `unit:UNITLESS`. Now matches whole words.
- **Generator list.** Initially read as truncated; the user confirmed the cropped
  row below belongs to different equipment, so the single row is complete.

---

## Open items (85 findings, on the Open Items sheet)

**Blocking-ish for handover:**

1. **No drawing references.** The HEX, pump, pressurisation, CAV, VAV and DX
   schedules all arrived as images with title blocks cropped. No drawing number,
   sheet or revision against any of those rows.
2. **DX condenser pairing** needs the pipework layout plan (see above).
   `DX/OD/05` is marked `(ST.BY)` while `DX/B/05` is not.
3. **`PHX/B/05` hot side conflict.** SYSTEM DETAILS says 15.5 °C in / 6.5 out
   across all five rows; the M10-MFM specification says 50.0 in / 20.0 out.

**Source conflicts recorded, not resolved:**

- `VAV/B/S15/001 TO 004` — 261 l/s on one drawing, 251 l/s on another.
- `VAV/1F/S15/014 TO 015` sits inside `VAV/1F/S15/013 TO 020` with a different flow and model.
- Pump weight — 843 kg on the drawing, 1874 lb (850 kg) on the submittal.
- MCG-10P size — 500×650×650 mm on the spec sheet, 475×430×400 mm on the drawing.
- CC/B/05,06,07 heading reads `M5DUA`, its own Unit row reads `M5DOA`.
- AHU-011 carries an unfilled duplicate electric-coil template block.
- 27 of 28 Euroclima sheets print air pressure drop as "Perdita di carico aria [°C]" — it is Pa.
- Three ranges whose box count disagrees with QTY: `VAV/1F/S15/012`,
  `VAV/B/S14/009 TO 012`, `VAV/B/S10/001 & 008`.

**Data still missing:**

- Models for `DX/B/17`–`20` and `DX/RP/21` (Table 3.6 stops at 16).
- Per-unit duties for DX rooms served by more than one unit — the schematic prints
  one **room load** per room and does not split it.
- No manufacturer stated for the DX units. PEAD/PCA/PUHZ is Mitsubishi Electric
  Mr. Slim naming, but nothing says so, so none was inferred.

**One reversible decision:** the expansion tank's 1000 litre capacity is written as
`para:Rated_Tank_Level` at the user's direction. `brick:volume` exists in Brick 1.4
and would outrank a `para:` term by the ladder — one line in `ontology_map.py`.

---

## Notes on the reference models

- **Dar Cairo** is the authority for units and the primary precedent.
- **QF HQ v0.4** was read for **structure only**. Several of its rows carry a wrong
  `brick:hasUnit` — an air flow of "3800 l/s" tagged `unit:V`, a cooling capacity
  tagged `unit:HZ`, blank values against `unit:UNITLESS`.
- **QF SSC** supplied `para:ratedReheatCapacity` and the VAV-specific literals
  `para:vavBoxType`, `para:inletSize`, `para:outletSize`, `para:plenumBoxSize` —
  none of which the QNL schedules state.

## Units with no Dar Cairo precedent

`unit:KiloGM`, `unit:KiloGM-PER-HR`, `unit:M-PER-SEC`, `unit:L`, `unit:K`,
`unit:CentiP`, `unit:KiloGM-PER-M3`, `unit:KiloJ-PER-KiloGM-K`, `unit:W-PER-M-K`,
`unit:W-PER-M2-K`. All genuine QUDT terms, highlighted on the Units sheet for the
PARA team to confirm. `unit:M2` and `unit:BAR` do have precedent.

---

## Where things live

```
QNL_Full_Metadata.xlsx              full transcription
QNL_Needed_For_Ontology.xlsx        core rows + Open Items
tools/equipment-metadata/
  README.md                         how it works, how to extend
  build.py                          formats and writes both workbooks
  units_map.py                      source unit -> Dar Cairo unit + factor
  ontology_map.py                   property -> predicate + scope
  data/*.py                         the transcription, one module per type
```

Rebuild:

```
python3 tools/equipment-metadata/build.py QNL_Full_Metadata.xlsx QNL_Needed_For_Ontology.xlsx
```

To correct a value, edit the data module and rebuild — `build.py` only formats.

## Suggested next step

Turn the 1,225 core rows into the 27-column CSV row shapes — value/unit ones as
blank nodes (shape C), `rec:modelNumber` and `rec:manufacturedBy` as subject
literals — then run `validate_ontology.py` and `check_consistency.py` over it.
The DX condensing units will need entities of their own first.
