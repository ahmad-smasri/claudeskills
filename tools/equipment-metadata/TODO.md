# In progress — pressurization unit, CAV, VAV, DX

Picked up from the schedule images supplied in chat. The three data modules below
are transcribed and committed but **not yet wired into `build.py`**, so they do not
appear in the workbook yet. `build.py` still builds the seven finished sheets.

## Done — transcribed, needs wiring

| Module | Rows | Source |
|---|---|---|
| `data/pressurization.py` | PU/B/01 | SCHEDULE OF PRESSURIZATION UNIT (same drawing as HEX/pumps) |
| `data/cav.py` | 15 schedule rows | three CAV schedules: 1F/S11, B/S14/03-05, B/S13-S15 |
| `data/vav.py` | 40 schedule rows, 104 boxes by QTY | three VAV schedules: 1F/S11+S15, B/S10+S15, B/S10+S13+S14 |

## Not started

- `data/dx.py` — DX split systems from the schematic. 20 indoor units DX/B/01-20
  plus DX/RP/21, outdoor units DX/OD/01-21. Each group carries the room served, room
  design condition (Tr and %RH) and a cooling capacity.
  **Read the capacity as a room load, not a unit capacity** — the figure is printed on
  the room box, and where a room is served by two or three units the schematic does
  not split it per unit.
  Standby units are marked `(ST.BY)`: DX/B/02, 09, 14, 16, 19.
  Indoor-to-outdoor pairing is by matching number (DX/B/nn ↔ DX/OD/nn), which is a
  convention read off the schematic, not stated — flag it, and note that DX/OD/05 is
  marked `(ST.BY)` while DX/B/05 is not.
- Wire all four into `build.py`: a `build_*` function each, a `sheet(...)` call, README
  sheet entries, and the tool README table.
- Range expansion helper. Refs are written as ranges (`CAV/1F/S11/006 TO 007`,
  `VAV/B/S15/005 & 006`, `VAV/1F/S11/096-098`, `VAV/1F/S11/022 TO 24`). Keep the printed
  ref as the Equipment Tag, add a "Covers" property listing the expanded box tags **only**
  when the range parses and its count matches QTY, and raise a Data quality row when it
  does not. Known mismatches to catch: `VAV/1F/S15/012` (1 box, QTY 02),
  `VAV/1F/S11/096-098` (3 boxes, QTY 01), `VAV/B/S14/009 TO 012` (4 boxes, QTY 02),
  `VAV/B/S10/001 & 008` (reads as 2 boxes, QTY 08 — probably means 001 TO 008).

## Deliberately excluded

The SCHEDULE OF FIRE DAMPER and the SLG/RLG grille schedule on the same image are
struck through in red in the supplied picture, so they were read as cancelled and left
out. Confirm before adding.

## Open questions for the user

1. The duplicate `VAV/1F/S11/022` — it appears twice on the same schedule with different
   air flow and model (220 l/s NBOQOB200, and 147 l/s NBOQOB160 inside `022 TO 24`).
   Which governs?
2. `VAV/1F/S15/395`, `VAV/1F/S11/088`, `VAV/1F/S11/096-098` carry box numbers far outside
   the 001-024 range every other row uses. Typos, or a different numbering system?
3. All these schedules came as images with the title block cropped. Drawing number, sheet
   and revision are still needed before handover.
