# QNL equipment metadata

Manufacturer properties transcribed from the QNL equipment submittals into one
workbook, `QNL_Equipment_Metadata.xlsx` at the repo root.

One sheet per equipment type. Every row is a single property for a single unit,
and carries the source PDF and the page it was read from, plus the same quantity
converted to the unit Dar Cairo uses for it.

## Coverage so far

| Sheet | Units | Source PDF |
|---|---|---|
| AHU | AHU-001 … AHU-015 | `Ahu_manual_1.pdf` (p1-8), `ahu_2.pdf` (p1-7) |
| Closed Control Units | CC/B/01 … CC/B/09 (5 selection sheets) | `qnl_closed_control_units_manual.pdf` |
| Climate Control Units | MCG-10P, VCB1000-AB32, AF4 filter | `climate_control_units_manual.pdf` |
| FCU | 28 positions across B, 1F, 2F | `FCU_Manual.pdf` (p2-29) |
| Heat Exchangers | PHX/B/01 … PHX/B/05 | schedule drawing + Alfa Laval data + SYSTEM DETAILS |
| Pumps | CHWP/B/01 … CHWP/B/04 | schedule drawing + Armstrong submittal + SYSTEM DETAILS |
| Generators | 1 row (source cropped) | GENERATOR ASSET LIST |
| Exhaust Fans | 39 fans, EF/ TEF_ KEF_ families | `Book1.xlsx` Sheet1 |
| Pressurization Unit | PU/B/01 | same drawing as the heat exchangers and pumps |
| CAV Units | 36 schedule rows, 6 schedules | drawing images supplied in chat |
| VAV Units | 60 schedule rows, 6 schedules | drawing images supplied in chat |
| DX Units | DX/B/01-20, DX/RP/21 | DX split system schematic riser |
| Units | the source-unit to Dar-Cairo-unit mapping | `reference-models/DarCairo_V93.csv` |

## Ontology scope

Most of this workbook is engineering reference, not ontology metadata. Counting
predicates across the three delivered reference models, equipment metadata is a
short vocabulary — about twenty predicates:

| Predicate | Dar Cairo | QF SSC | QF HQ v0.4 |
|---|---|---|---|
| `para:ratedSupplyAirFlowrate` | 81 | 113 | 628 |
| `para:ratedReheatCapacity` | — | 108 | 602 |
| `brick:coolingCapacity` | 76 | 16 | 158 |
| `brick:ratedPowerInput` | 108 | 7 | 113 |
| `para:ratedChilledWaterFlowrate` | 83 | — | — |
| `brick:ratedVoltageInput` / `electricalPhaseCount` | 106 / 106 | — | 71 / 71 |
| `para:ratedHead` | 41 | — | — |
| `para:ratedWaterFlowrate` | 34 | — | — |
| `para:ratedExhaustAirFlowrate` / `ratedOutsideAirFlowrate` | 18 / 18 | — / 5 | — / 26 |
| `para:ratedSpeed`, `para:refrigerant`, `para:Rated_Tank_Level` | 7, 2, 3 | — | — |

plus the subject literals `rec:modelNumber`, `rec:manufacturedBy`,
`rec:installationDate`, and SSC/HQ's VAV-specific `para:vavBoxType`,
`para:inletSize`, `para:outletSize`, `para:plenumBoxSize`.

**Brick 1.4 is checked first**, per the class ladder — it is step 2 and the
reference models are step 3. Its entity-property list is short, and two gaps in it
explain the `para:` terms above: Brick has **no water or air flow-rate entity
property** and **no heat-exchanger duty property**, which is why Dar Cairo minted
`para:ratedChilledWaterFlowrate`, `para:ratedWaterFlowrate` and the air-flowrate
family. Where Brick does carry the term, Brick wins:

| Use | Predicate | Source |
|---|---|---|
| heat exchanger duty | `brick:coolingCapacity` | Brick 1.4 |
| full load current | `brick:ratedCurrentInput` | Brick 1.4, unused by any reference model |
| fan speed count | `brick:operationalStageCount` | Brick 1.4, unused by any reference model |
| outdoor DX unit | `brick:Condensing_Unit` entity carrying `rec:modelNumber` | Brick 1.4 |

`ontology_map.py` classifies every transcribed property into two states, written
into the `Ontology predicate` and `Scope` columns:

- **core** — maps unambiguously to Brick or a reference-model predicate.
  55 distinct properties, 1,225 rows, 16 predicates.
- **reference** — no precedent in Brick or any reference model. 517 properties,
  3,418 rows. Dimensions,
  weights, materials, seal specifications, sound power levels, filter part
  numbers, psychrometrics, warranty text. Kept because engineers want them, not
  because they will be modelled.

The **Ontology Scope** sheet lists all of them with the predicate, where that
predicate comes from, row counts and which sheets they appear on.

One deliberate exception to the ladder: the expansion tank's capacity is written
as `para:Rated_Tank_Level` at the user's direction. `brick:volume` exists in
Brick 1.4 and would outrank a `para:` term — reversible in one line here.

A component's own maker is not the equipment's manufacturer — the pump's seal is
made by Armstrong and its motor by WEG, and neither becomes `rec:manufacturedBy`
on the pump. Those are matched out explicitly before the general rule.

The QF HQ v0.4 draft was read for **structure**, not for units: several of its
rows carry a wrong `brick:hasUnit` (an air flow tagged `unit:V`, a cooling
capacity tagged `unit:HZ`, blank values against `unit:UNITLESS`). Dar Cairo
remains the authority for unit choice.

## Air terminal references

CAV and VAV schedules write references as ranges — `CAV/1F/S11/006 TO 007`,
`VAV/B/S15/005 & 006`, `VAV/1F/S11/022 TO 24`. `expand_ref()` in `build.py`
expands one into individual box tags **only** when the box count matches the
stated QTY; otherwise it emits a Data quality row rather than an expansion nobody
checked. Three currently disagree: `VAV/1F/S15/012` (1 box, QTY 2),
`VAV/B/S14/009 TO 012` (4 boxes, QTY 2), `VAV/B/S10/001 & 008` (2 boxes, QTY 8).

Each schedule line is **split into one row per box** — every box carries its own
air flow, heating capacity, model and make, plus a `Scheduled as` row naming the
line it came from. That gives 42 CAV boxes and 180 VAV boxes as individual
entities. A range that cannot be split with confidence keeps the printed
reference as its tag and raises a Data quality row instead.

`COVERS_OVERRIDE` in `data/vav.py` handles a range that must not expand literally.
It currently holds one entry: `VAV/1F/S11/022 TO 24` covers 023 and 024 only,
because the user confirmed the standalone `VAV/1F/S11/022` row governs box 022.

Each schedule is its own source, named in the Page column. Overlapping drawings
are recorded side by side, never merged — two drawings schedule the same basement
S10/S15 VAV boxes and disagree on one air flow.

## Units with no Dar Cairo precedent

The manufacturer submittals brought quantities Dar Cairo has never carried:
`unit:KiloGM`, `unit:KiloGM-PER-HR`, `unit:M-PER-SEC`, `unit:L`, `unit:K`,
`unit:CentiP`, `unit:KiloGM-PER-M3`, `unit:KiloJ-PER-KiloGM-K`, `unit:W-PER-M-K`,
`unit:W-PER-M2-K`. All are genuine QUDT terms, highlighted on the Units sheet for
the PARA team to confirm. `unit:M2` and `unit:BAR` do have precedent.

The Armstrong submittal is imperial — `in` converts at ×0.0254 to `unit:M`, `lb`
at ×0.45359237 to `unit:KiloGM`.

## Multiple sources per unit

Several units are now described by more than one document, and the sources
disagree in places. Nothing is merged: each property row names the document it came
from, and the disagreement becomes a `Data quality` row.

- **Pumps** — drawing schedule, Armstrong submittal, SYSTEM DETAILS Table 3.1.
  Weight is 843 kg on the drawing and 1874 lb (850 kg) on the submittal.
- **Heat exchangers** — drawing schedule, Alfa Laval construction data, the M10-MFM
  thermal specification, SYSTEM DETAILS Table 3.3. `PHX/B/05` appears on everything
  except the drawing schedule. Hot-side temperature conflicts between SYSTEM DETAILS
  and the M10-MFM sheet.
- **Pressurisation unit** — drawing schedule and SYSTEM DETAILS Table 3.2, which
  resolves the drawing's odd `SYSTEM VOLUME` cell into two components.

Where two documents tag the same unit differently (`CHWP/B/01` vs `CHWP-B-01`,
`PU/B/01` vs `PRO1`), the slash form is the Equipment Tag because it matches the
rest of the workbook, and the other is recorded as an `Alternate reference`
property rather than dropped.

## DX schematic and equipment schedule

The cooling figure is printed on the **room** box, so it is a room load, not a
per-unit capacity — a room served by three units carries one figure the schematic
does not split. It is recorded as "Room cooling load" against each unit serving
the room, and must not become `brick:coolingCapacity` without a per-unit duty.

**The matching-number pairing is not reliable.** The schematic numbers condensers
to match their indoor units, which suggested `DX/B/nn` ↔ `DX/OD/nn`. SYSTEM DETAILS
Table 3.6 disproves that for five units: `DX/B/03`, `04` and `14` take a
`PUHZ-RP200X2`, and `DX/B/08` and `09` take a `PUHZ-RP250X2` — the `X2` suffix
means two condensers per indoor unit. Those five need two `DX/OD` tags each and the
numbering does not say which two. `DX/OD/05` is also marked `(ST.BY)` while
`DX/B/05` is not.

Table 3.6 covers `DX/B/01`–`DX/B/16`, so `DX/B/17`–`20` and `DX/RP/21` still carry
no model. `DX/B/08` reads `PUHZ-RP2S0X2` where its twin `DX/B/09` reads
`PUHZ-RP250X2` — recorded as printed. The `PEAD`, `PCA` and `PUHZ` prefixes are
Mitsubishi Electric Mr. Slim naming, but no document names a manufacturer, so none
was created from the prefix.

## Rebuilding

```
python3 tools/equipment-metadata/build.py QNL_Equipment_Metadata.xlsx
```

Needs `openpyxl`. The transcribed values live in `data/*.py` — one module per
equipment type. `build.py` only formats them and applies the unit conversion; to
correct a value, edit the data module and rebuild.

## Units

Each row carries four value/unit cells: `Value (as printed)` / `Unit (as printed)`
hold the transcription, `Value (Dar Cairo)` / `Unit (QUDT)` hold the same quantity
in Dar Cairo's unit, and `Conversion` names the arithmetic applied.

`units_map.py` holds the mapping. Every target was read off `DarCairo_V93.csv`
rather than assumed — the predicate/unit pairings that settled it:

| Dar Cairo predicate | Unit | Rows |
|---|---|---|
| `brick:ratedPowerInput`, `brick:coolingCapacity` | `unit:KiloW` | 108, 76 |
| `para:ratedSupplyAirFlowrate` and siblings | `unit:L-PER-SEC` | 81 |
| `para:ratedChilledWaterFlowrate`, `para:ratedWaterFlowrate` | `unit:L-PER-SEC` | 83, 34 |
| `para:ratedHead` | `unit:M` | 41 |
| `brick:ratedVoltageInput` | `unit:V` | 106 |
| `brick:electricalPhaseCount`, `rec:capacity` | `unit:UNITLESS` | 106, 64 |

So air flow and water flow both land on `unit:L-PER-SEC`, power on `unit:KiloW`,
length on `unit:M`. Relative humidity takes `unit:PERCENT_RH` (79 rows in Dar
Cairo), not `unit:PERCENT`.

Four QUDT units have no precedent in Dar Cairo — `unit:KiloGM`, `unit:KiloGM-PER-HR`,
`unit:M-PER-SEC` — because Dar Cairo carries no mass, mass-flow or velocity
quantity at all. They are genuine QUDT terms, not minted ones, and are highlighted
on the Units sheet for the PARA team to confirm.

One conversion rests on an assumption: `kg/s` to `l/s` treats water as 1 kg/l.
Chilled water at 7-15 °C is about 0.9997 kg/l, so the converted flow is high by
roughly 0.03%. The assumption is written into the `Conversion` cell of every row
it touches.

Values that are designations rather than quantities — BSP thread sizes, IEC motor
frame numbers, composite `V-ph-Hz` nameplate strings, drawing revisions — carry no
unit in either pair, by design.

Dimensionless quantities (SHR, EER, COP, fan speed setting) are matched on whole
words, not substrings — "Schedule scope" contains "cop" and must not be treated as
a ratio.

## Source quality

Two sources are weaker than the submittal PDFs, and the sheets say so on the row:

- The heat exchanger and pump schedules were supplied as an image with the title
  block cropped out, so no drawing number, sheet or revision is recorded.
- The exhaust fan spreadsheet carries model, manufacturer and air flow only, uses
  two identifier shapes (28 slash-separated, 11 underscore-separated), and leaves
  model/manufacturer blank on three fans and air flow blank on four.

## Adding an equipment type

1. Add a `data/<type>.py` module holding the transcribed values, keeping the
   source file and page against each unit.
2. Add a `build_<type>(rows)` function in `build.py` that appends rows in the
   nine-column shape (`Equipment Tag, Model, Component, Property, Value, Unit,
   Source File, Page, Note`).
3. Call `sheet(wb, "<name>", rows, "<subtitle>")` and add the type to the README
   sheet's table.

## Rules followed

- Values are transcribed as printed — nothing converted, rounded or inferred.
- Where a document contradicts itself the conflict is written as a `Data quality`
  row rather than resolved; those need the supplier's answer.
- The source PDFs are submittals, not nameplate photographs. Where the installed
  plant differs from the selection, the installed plant governs.
