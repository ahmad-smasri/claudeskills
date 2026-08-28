# QNL datapoint layer, unit audit and the estate assumption log

**Date:** 2026-08-28
**Branch:** `claude/qnl-ontology-ledger-review-7yrldg`
**Commits:** `82dfce9` … `7250e5a` (11 commits)
**Starting point:** QNL sheet at 2,577 rows — spatial, systems and equipment complete, **no points**
**Ending point:** 7,030 rows, 2,224 points, all validated and reproducible from source

---

## What this session produced

| File | State |
|---|---|
| `projects/QNL/QNL_Ontology.xlsx` / `.csv` | 7,030 rows, 27-column PARA header |
| `projects/QNL/QNL_datapoint_ledger_v2.xlsx` | reviewed class decision per point signature, + Legend sheet |
| `projects/QNL/QNL_handover-note.md` | rewritten throughout |
| `projects/Assumption_Log.xlsx` | **new** — SSC / HQ / QNL / RDC, 15 QNL entries after your edit |
| `projects/format_assumption_log.py` | **new** — formats the log, never writes rows |
| `projects/QNL/check_units_vs_reference.py` | **new** — repeatable unit cross-check |
| `reference-models/QF_SSC_Ontology_ver02.xlsx` | **replaced** `draft0.5_review` (451 errors → 17) |

Sources added to `projects/QNL/sources/`: `Selected_PARA_OS_Data_Points_v4.0.xlsx`,
`QNL_Historian_IO_list_CP2.xlsx`. The whole sheet regenerates with `build_qnl.py` —
nothing is hand-edited.

---

## Session narrative

### 1. Ledger review questions

Answered four questions on the datapoint ledger. The `runner_up` column is the
second-best class from the same Dar Cairo precedent search that produced the winner.
Corrected two rows where `unit_of_measure` read `%` on `SupFan/kW` and `RtnFan/kW`
(rows 21 and 33) — **this correction was later silently undone and had to be restored,
see §5.**

Established that a **Brick deprecation is not a reason to coin `para:`** — deprecations
ship functional replacements, so you migrate. `para:` is forced only by genuine absence.

### 2. Class ladder gained a rung

The ladder is now **Dar Cairo → Brick 1.4 → previous-project ontologies → `para:`**.
A `para:` class a prior project already coined is reused, never re-minted. Updated in
`CLAUDE.md`, `SKILL.md` and `references/class-resolution.md`.

SSC `ver02` replaced the old review workbook as the step-3 reference; the para/unit
registry was regenerated from it, which is what surfaced `para:Scheduled_Hrs_Duration`
and `para:UnScheduled_Hrs_Duration` for reuse.

### 3. `brick:Alarm` reserved

**`brick:Alarm` is only for a point literally named a general/summary/common alarm.**
Every other alarm runs the full ladder. Same for `brick:Sensor`, `Setpoint`, `Status`,
`Command`, `Point`. The anti-pattern is in SSC itself, which types its `_TripAlm` points
as bare `brick:Alarm` — QNL splits them out as `para:Trip_Alarm`, defined in row 3.

### 4. Datapoint layer built, in two passes

First pass placed only the 18 *universal* signatures (758 points) because the ledger
records point **coverage**, not per-unit membership.

The **Selected Points sheet** then supplied the missing membership, and all
**2,236 four-family selected tags mapped to a ledger class with nothing left over**.
Every point traces to a real IO row — `check_io_list.py` reports **0 `E-IO-1`**.

Points follow the QF SSC two-row shape: `brick:hasPoint` on the equipment (class,
label, unit) plus a `ref:TimeseriesReference` row on the point carrying
`para:hasEntityId` and `ref:hasTimeseriesId`.

### 5. The unit corrections — three rounds

This was the most involved thread, and each round was found by you, not by me.

1. **Power units.** I had made the IO list the unit authority. It carries `%` on
   **20 of its 24 `.kW` tags**, so the build silently overwrote the ledger's `kW`
   correction. Fixed at the root with `CLASS_UNIT`: where the class names the quantity
   unambiguously, **the class outranks every source column**, and each override is logged.
2. **The rest of the units.** Full audit: no analog point defaulted to unitless, every
   IO unit string mapped, all 88 discrete points unitless, and the ontology agrees with
   the ledger on **every** signature. One finding left open — 22 AHU air-flow points
   carrying `m/s`.
3. **Air flow, settled by precedent.** I had called it ambiguous; you asked whether I'd
   checked Dar Cairo. **I hadn't**, and it settles the question outright:

   | Reference | air-flow sensors | unit |
   |---|---|---|
   | Dar Cairo | 51 (supply/return/outside/exhaust) | all `unit:L-PER-SEC` |
   | QF SSC | 118 | all `unit:L-PER-SEC` |
   | either model | `unit:M-PER-SEC` | **0 occurrences** |

   No point in 11,601 IO rows is named "velocity"; all 22 are named `*AirFlow.PV`.
   All 317 air-flow points now read `unit:L-PER-SEC`.

**Lesson recorded in `known-issues.md`: run the ladder on the *unit*, not just the class.
A unit with no precedent anywhere in the estate is a finding in itself.**

Final cross-check of all 34 point classes: **23 match a reference model, 7 have no
precedent (checked dimensionally), 4 differ deliberately** — `Air_Flow_Sensor`,
`Damper_Position_Command`, `Relative_Humidity_Sensor`, `Speed_Sensor`. Two of those four
are Dar Cairo's own defects (a `UNITLESS` flow sensor is a missing unit, not a
convention), not conventions to copy.

### 6. Rule 1 and the assumption log

Your advisor's rule: **every assumption, correction or departure from what a source
literally says is recorded, and a source disagreement is modelled rather than dropped —
an omission is invisible, an assumption in the log is reviewable.**

Applied to the three exception assets:

| Asset | Disagreement | Handling |
|---|---|---|
| `CAV_1F_S15_001`, `VAV_B_S13_005` | in Selected sheet, absent from register | modelled with points, **no `rec:locatedIn` / `feeds` / `isFedBy`** |
| `VAV_1F_S15_039S` | in register + historian, Selected sheet omits it | took the 3 points its 245 siblings carry, from the historian |

`Assumption_Log.xlsx` created with a sheet per building. You then edited the QNL sheet
(dropped `Status` and `Raised with client`, 11 → 9 columns; kept 15 of 33 entries), and
the other three sheets were brought to match. The generator was replaced with
`format_assumption_log.py`, which only applies formatting — a generator would have
destroyed the hand edit on any re-run.

### 7. Virtual meters — researched, not built

Two distinct patterns exist:

- **Dar Cairo** — 409 spatial virtual meters. `brick:isVirtualMeter` TRUE, `brick:meters`
  a *space* (Zone 252, Level 60, HVACZone 46, Building 13), `brick:isPartOf entity:Metering`.
  **Created for every space × utility category regardless of equipment** — 34 spaces × 8
  categories, uniform. Carries Consumption / Demand / Target, plus KPI and Forecast layers.
- **SSC** — 45 per-equipment meters, attached `equipment brick:hasPart meter`.
  **Strictly conditional: a meter exists where its source data exists.** Electrical meters
  wrap points that already exist (tsid = a real BMS tag); thermal meters are genuinely
  computed (`CWPWR_KWTH_CALC`). That rule explains the coverage exactly — the 10 metered
  motors are precisely the AHU supply/return fan motors, the only motors with `.kW`.

**You chose the SSC per-equipment pattern.** QNL supports only part of it: ~24 AHU fan
electrical meters are buildable; FCU electrical meters are not (**FCU `.kW` = 0**) and
cooling thermal meters are not (**no per-AHU CHW flow**).

### 8. Calculated points — parked

918 calculated point instances exist in the historian across 7 types:

| Point | n | Unit | Sits on | Proposed class |
|---|---|---|---|---|
| `CalcAvailability` | 207 | `%` | 152 units + parts/modes | `para:Availability_KPI` ⚠ new |
| `CalcReliability` | 207 | `%` | same | `para:Reliability_KPI` ⚠ new |
| `CalcEntryScheduledHrs` | 207 | `Hrs` | same | `para:Scheduled_Hrs_Duration` ✅ SSC |
| `CalcEntryUnscheduledHrs` | 207 | `Hrs` | same | `para:UnScheduled_Hrs_Duration` ✅ SSC |
| `RuntimeMtr` | 24 | `Hrs` | AHU fan parts | `para:Operation_Hours` ✅ Dar Cairo |
| `StartsCtr` | 24 | — | AHU fan parts | `para:Start_Count` ⚠ new |
| `TripCtr` | 24 | — | AHU fan parts | `para:Trip_Count` ⚠ new |

**On hold.** Calc points are driven by prebuilt FDD rules and must map to real platform
widgets — an invented class produces a point with no widget behind it. Awaiting the FDD
documents.

Also unresolved: 155 calc points hang off `*Mode` pseudo-parts (`SandStmMode` 75,
`AvgSpcHumdMode` 40, `RtnAirHumdMode` 40). Neither reference model models an operating
mode as an entity.

### 9. SSC predicates for the other equipment families

Requested at the end of the session, for families QNL may add later. Common backbone on
all of them: `brick:isPartOf` · `rec:locatedIn` · `ref:hasExternalReference` · points
(direct or via parts).

| Family | Class | Distinctive predicates |
|---|---|---|
| DX (10) | `para:DXUnit` | `feeds`; **no `isFedBy`** (direct expansion) |
| CCU (14) | `brick:CRAC` ⚠ alias | `isFedBy` the loop, `feeds` its room, 17 points |
| EF (7) | `brick:Exhaust_Fan` | `hasPart` → `_Motor`; **`brick:ratedPowerInput`** |
| HEX (5) | `brick:Heat_Exchanger` | `hasPart` only, **no `feeds`, no direct points** |
| CHWP (4) | `brick:Chilled_Water_Booster_Pump` | `feeds` the **loop**; parts = Motor + Electrical_Meter + Thermal_Meter |
| CHW (2) | `brick:Chilled_Water_System`, `para:Chilled_Water_Loop_Network` | system → HVAC; loop → building |
| Generator (1) | `para:Generator` | `isPartOf` `Electrical_System`; `para:ratedFrequency` / `ratedPower` / `ratedVoltage` |

`brick:CRAC` is a **Brick alias** (prefer `brick:Computer_Room_Air_Conditioning`) and is
the single largest source of SSC's `W-TYP-5` warnings.

---

## Source defects found

Reported rather than absorbed — each needs correcting at source.

| Source | Defect | Count |
|---|---|---|
| Historian IO list | `.kW` tags carrying `%` against a "Power" description | 20 of 24 |
| Historian IO list | AHU air-flow tags carrying `m/s` on a flow class | 22 |
| Selected Points | humidity/temperature units transposed | 30 |
| Selected Points | column C (DP Name) misaligned from row 17, degrading into IO descriptions | — |
| Selected Points | tags listed twice (`RtnAirDuctPrs.PV`, once per AHU) | 15 |
| Asset register | units referenced by the point sources but absent | 2 |

**Overturned:** `VAV_1F_S15_039` / `039S` were earlier flagged as a possible typo. The IO
list gives each a full separate point set — two real units, both now modelled.

---

## Toolchain hardened

Four defects in the shared skill, all of which failed **silently**:

1. **Multi-sheet IO lists.** `io_list.py` and `check_io_list.py` read only
   `worksheets[0]`, so a two-tab IO list lost all 6,027 discrete rows and every discrete
   point reported as phantom over-inclusion. **88 false errors → 0.**
2. **"Unit" matched as an equipment column.** `known_equipment` filled with `bar`, `kw`,
   `hz`; `has_point()` answered "cannot tell" for every real unit, so `--io` adjudicated
   nothing. Equipment tags **31 → 1,755**; QNL consistency errors **287 → 78**.
3. **`brick:Constant_Air_Volume_Box` missing from `TERMINAL_EQUIPMENT`.** All 51 QNL CAVs
   escaped `E-FEED-1` and `W-GR-2` entirely. A class missing from that set is not a
   passing check, it is an unasked one. Added, with `brick:Induction_Unit`.
4. **New rule `W-CON-19`** — one point class carries one unit across the sheet.
   File-wide, not per-family. This is the check that caught defect §5.1.

---

## Validation state at session end

```
validate_ontology.py  QNL_Ontology.xlsx --label-style verbatim
  7030 rows, 3020 typed entities, 2 para: definitions
  454 errors · 66 warnings · 3803 advisories

check_io_list.py      --io QNL_Historian_IO_list_CP2.xlsx     0 errors
check_consistency.py  --io QNL_Historian_IO_list_CP2.xlsx    73 errors
run_tests.sh                                            all passing
```

- **452 of 454 errors** are the deliberate empty `para:IFC_ID`; the other 2 are accepted
  `E-FEED-1` on the unregistered units.
- **64 of 66 warnings** are `W-TYP-4` on the deprecated CHW classes kept by your direction.
- **73 consistency errors** are real per-unit variance, IO-confirmed — chiefly the 44 VAVs
  that genuinely carry `RmTemp`.

---

## Open items

| Item | Status | Blocked on |
|---|---|---|
| Calculated points (7 types, 918 instances) | On hold | FDD rule documents |
| `*Mode` pseudo-parts (155 calc points) | Open | modelling decision |
| Virtual meters — ~24 AHU fan electrical | Next | your go-ahead; SSC attaches to `brick:Motor` parts QNL does not yet have |
| IFC GUIDs | Open | BIM |
| 2 units missing from the asset register | Open | client |
| `039S` has no selected points | Open | client — confirm whether it should |
| Zones (`rec:Zone` layer) | Open | zoning drawings |
| Nameplate properties | Open | manufacturer datasheets |
| SSC / HQ / RDC assumption-log sheets | Empty | SSC's `Claude Log` tab has 2 turns that could be backfilled |

---

## Rules established this session

1. **Class ladder step 3** — check previous-project ontologies before minting `para:`.
2. **`brick:Alarm` and other root classes are not catch-alls** — only a literal
   general/summary alarm gets `brick:Alarm`.
3. **The class outranks every source column on units** where the quantity is
   unambiguous; log each override.
4. **Run the ladder on the unit too** — a unit with no estate precedent is a finding.
5. **`W-CON-19`** — one point class, one unit, file-wide.
6. **The assumption log** — every departure recorded, one sheet per building.
7. **Rule 1** — model what the sources disagree about, then log it. Missing location →
   model without asserting position. Selected sheet omits a unit the historian has →
   take the family's signature from the historian.

All seven are in `SKILL.md`, `CLAUDE.md` or `references/`, so they carry to the next
building without depending on this transcript.
