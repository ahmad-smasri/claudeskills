# QNL equipment metadata

Manufacturer properties transcribed from the QNL equipment submittals into one
workbook, `QNL_Equipment_Metadata.xlsx` at the repo root.

One sheet per equipment type. Every row is a single property for a single unit
and carries the source PDF and the page it was read from.

## Coverage so far

| Sheet | Units | Source PDF |
|---|---|---|
| AHU | AHU-001 … AHU-015 | `Ahu_manual_1.pdf` (p1-8), `ahu_2.pdf` (p1-7) |
| Closed Control Units | CC/B/01 … CC/B/09 (5 selection sheets) | `qnl_closed_control_units_manual.pdf` |
| Climate Control Units | MCG-10P, VCB1000-AB32, AF4 filter | `climate_control_units_manual.pdf` |
| FCU | 28 positions across B, 1F, 2F | `FCU_Manual.pdf` (p2-29) |

## Rebuilding

```
python3 tools/equipment-metadata/build.py QNL_Equipment_Metadata.xlsx
```

Needs `openpyxl`. The transcribed values live in `data/*.py` — one module per
equipment type. `build.py` only formats them; to correct a value, edit the data
module and rebuild.

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
