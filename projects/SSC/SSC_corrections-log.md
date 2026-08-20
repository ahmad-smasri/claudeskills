# QF SSC ontology — what was corrected, and by whom

The finalized SSC sheet (`QF_SSC_Ontology_ver01.xlsx`, 5,068 rows) came in with
**354 row-level errors and 50 cross-unit errors**. It now stands at **17 and 44**.
This is the record of how, split by who made each change.

The three files, all in `projects/SSC/`:

| File | What it is |
|---|---|
| `sources/QF_SSC_Ontology_ver01.xlsx` | the finalized sheet as received, untouched |
| `QF_SSC_Ontology_ver01_fixed.xlsx` | after the five agreed term fixes, with the rest highlighted for review |
| `QF_SSC_Ontology_ver01_reviewed.xlsx` | **current** — after your review pass and the follow-up fixes below |

---

## 1. Agreed term fixes, applied by script

Five decisions taken after the first validation run. `projects/SSC/fix_ssc.py`
reproduces them from `sources/`, so the pass can be re-run and audited.

| # | Change | Cells | Why |
|---|---|---|---|
| 1 | `brick:Supply_Air_Flow` → `brick:Supply_Air_Flow_Sensor` | 216 | not a Brick 1.4 term. Dar Cairo uses the `_Sensor` form 38 times, so this was house precedent rather than a spelling hint |
| 2 | `brick:ccupied_Air_Temperature_Setpoint` → `brick:Occupied_Air_Temperature_Setpoint` | 32 | a dropped leading `O`, present since draft 0.4 |
| 3 | `brick:Fan_Status` → `brick:On_Off_Status` | 27 | `Fan_Status` has no Dar Cairo precedent; `On_Off_Status` has 435 rows |
| 4 | `brick:Apparent_Power_Sensor` — **kept** | — | confirmed on brickschema.org by you. Absent from our pinned Brick 1.4 extract, so it is recorded in `accepted-terms.txt` rather than substituted. Dar Cairo's own precedent is `para:Apparent_Power_Usage_Sensor` if the pin moves and the term is still missing |
| 5 | `entity:HVAC` retyped `brick:HVAC_System` | 148 | it carried both `brick:HVAC_System` and `brick:System`. `HVAC_System` is the house term; `brick:System` stays on `entity:Electrical_System`, which is correct there |

**354 → 84 errors.** The remaining 84 were filled `#FFFF00` across 100 rows, with
the finding written into `validator_code` / `validator_finding` columns.

---

## 2. Your review pass

Worked through the highlighted rows, clearing the highlight from everything
fixed or accepted, and adding rows where a fix needed them. Four shapes of fix,
each now recorded in `references/known-issues.md` because they generalise:

| Finding | What it turned out to be | Your fix |
|---|---|---|
| `E-CON-10` — one point carrying two external references, on `AHUB0002/3/4` | two different sensors sharing one identifier | **split the entity.** `_SA_P-Static` became `_SA_P-Static-1` and `-2`, typed `para:Static_Pressure_Sensor_01` and `_02`. Two telemetry keys means two points |
| `E-TYP-1` — `_RA_P-Static` typed two ways across the 5 AHUs | the generic and the specific class both in circulation | **kept the specific one everywhere**: `para:Return_Air_Static_Pressure_Sensor` |
| `E-CON-5` — `AHUB0004_RF` point typed under two different fans | a return fan modelled as a supply fan | retyped `brick:Return_Fan`. The `_RF` in the identifier was right; the class was wrong |
| `E-FEED-1` — 14 CRACs with no `rec:feeds` | genuinely missing rows | added `rec:feeds` to the room each CRAC serves |

Also in this pass: `brick:Alarm` → `brick:Communication_Loss_Alarm` on the CCU
communication points, and `brick:Fault_Status` → `brick:Alarm` on the CCU general
fault points. Both are logged on the `Claude Log` sheet in that workbook.

**Net: 5,068 → 5,082 rows, and 84 → 57 errors.**

---

## 3. Follow-up fixes

### `brick:Heater` → `brick:Heating_Coil` — 10 cells

The last highlighted finding. Not a Brick 1.4 term, and Dar Cairo has no heaters
at all, so neither step of the class ladder answered it. The entity did: it is a
`brick:hasPart` of an AHU carrying a `brick:Heating_Command`, SCADA key
`SSC_AHUB0001_SupHtr.HtrCtrl` — a heating element inside an air handler.
`brick:Heating_Coil` is the Brick class for exactly that, and the sibling of the
`brick:Chilled_Water_Coil` these same AHUs already use on the cooling side.
`brick:Space_Heater` is a standalone room heater and `brick:Water_Heater` is
domestic hot water; neither fits.

### `_General_Fault` object type → `brick:Alarm` — 14 cells

**A defect the fix pass itself introduced**, and one your own `Claude Log` flagged
in its outcome note. The two search-and-replace turns each ran over a single
column: turn 1 changed the `_General_Fault` **objects** to
`brick:Communication_Loss_Alarm`, turn 2 changed the same entities' **subjects**
to `brick:Alarm`. The result was 14 entities typed one way in `subjectType` and
another in `objectType` — a fresh `E-TYP-1` created by the repair.

Turn 2 was the later decision and a general fault is a fault alarm rather than a
comms-loss one, so `objectType` was aligned to `brick:Alarm`.

**The generalisable lesson, now in `known-issues.md`: a class change has to move
every cell that names the entity, subject side and object side together.**
`check_consistency.py` is what catches it when it does not.

### `<AliasOf>` reclassified from error to open work — 14 rows

Not a change to the sheet, a change to the validator. `<AliasOf>` had been
failing as an unresolved placeholder (`E-PH-1`). It is deliberate: a point's
identifier here is invented when the equipment is modelled, the telemetry
database stores its own entity names, and `brick:aliasOf` maps between them. They
cannot match from the start because the ontology is built before the data lands —
sometimes long before — and waiting would stop the work. It now reports as
`I-PH-2`, open work rather than a defect, with the reasoning in
`references/csv-contract.md`. Every other `<placeholder>` is still an error.

### Labels: underscores to spaces — 17 stragglers

Your pass replaced `_` with a space in label values — `1.001_CORRIDOR` became
`1.001 CORRIDOR` — but 17 labels were missed, all in the CHWP and generator
blocks plus four `Return Fan AutoMan_Status`. Finished on the same rule.

**Net: 57 → 17 errors.**

---

## What is still open — 17 row-level, 44 cross-unit

| Count | Code | What |
|---|---|---|
| 31 | `E-CON-2` | AHU point sets still differ unit to unit — `_RA_P-Static_01`/`_02` on one of five, `_SAP_Setpoint` on three of five. **An IO list would settle these**: pass `--io` and the ones it confirms are reported as facts instead of defects |
| 12 | `E-CON-1` | the same gaps seen as row counts: 127–134 rows against a typical 129 |
| 8 | `E-WS-1` | padded cells, including `'brick:Air_Static_Pressure_Sensor '` in an object column |
| 4 | `E-TYP-3` | `para:vavBoxType`, `para:inletSize`, `para:outletSize`, `para:plenumBoxSize` — used 108 times each, never defined |
| 3 | `E-PAIR-1` | `brick:value` with an empty value |
| 1 | `E-FEED-1` | `SSC_VAV0063` declares no `rec:feeds` |
| 1 | `E-GR-1` | `entity:Level7_Office0367` connects up to nothing |
| 1 | `E-CON-4` | `#N/A` sitting in a `rec:locatedIn` object cell on a VAV |

The 319 warnings are almost entirely `W-TYP-5` on `brick:HVAC_System`, which is
the accepted house term, and `I-PH-2` open aliases.

## Reproducing any of it

```
python3 projects/SSC/fix_ssc.py                     # section 1, from sources/
python3 skills/building-ontology/scripts/validate_ontology.py \
    projects/SSC/QF_SSC_Ontology_ver01_reviewed.xlsx --label-style verbatim
python3 skills/building-ontology/scripts/check_consistency.py \
    projects/SSC/QF_SSC_Ontology_ver01_reviewed.xlsx
```
