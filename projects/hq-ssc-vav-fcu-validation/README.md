# HQ & SSC VAV / FCU location validation

Checks the room names in **column D** of the `Controllable Asset Registry`
(Appendix A) against the room the new commissioning lists put each unit in, and
writes the new name into **column H** wherever the two disagree.

## Sources

| Source | Sheet | Key |
|---|---|---|
| `HQ_&_SSC_VAV_LIST_2058.xls` | `HQ & SSC VAV LIST` | col D `VAV CONTROLLER TAG` |
| `HQ_&_SSC_FCU_LIST_1397.xls` | `HQ FCU LIST` | col D `FCU CONTROLLER TAG` |
| `HQ_&_SSC_FCU_LIST_1397.xls` | `SSC FCU LIST` | col D `FCU CONTROLLER TAG` |

Target: `Appendix A - Asset Register`, sheet `Controllable Asset Registry`,
HQ rows 4-777 and SSC rows 1331-1454, `Equipment Type` of `VAV` or `FCU`.

## How the join works

Controller tags are written differently on each side, so both are reduced to
`(type, number)`:

- `0050-VAV-0001` (HQ) and `0051-VAV-0001` (SSC) -> `('VAV', 1)`
- `FCU0001`, `VAV0001` in the register -> `('FCU', 1)`, `('VAV', 1)`

The 13 HQ register rows whose column A holds an IFC ref (`VAV/12/01` ...) have
no controller number, so those fall back to matching on the list's
`VAV Ref.` column. 864 of 867 register rows join; the 3 that do not are listed
on the `Exceptions` tab.

Room numbers are compared after normalising the level segment only - `B1.103`
in the lists is `B.103` in the register, `LG.008` is `G.008`, `L02.029` is
`2.029` or `02.029`. Digits are never rewritten.

## What is written

Column H is filled only where the new list actually disagrees with column D.
The value is written in the register's own format, `<ROOM NAME> <ROOM NUMBER>`,
and the room number token already in column D is reused whenever the number
itself did not change, so H differs from D in the name alone. Column D is never
touched.

Where the new list leaves the room blank, H is left blank - silence in the list
is not evidence.

## Running it

```
pip install openpyxl xlrd
python3 write_h.py     # writes Appendix_A_Asset_Register_VAV_FCU_validated.xlsx
python3 report.py      # writes VAV_FCU_validation_findings.xlsx
```

Both read the upload paths at the top of `load.py`; point those at the current
copies before re-running. `write_h.py` edits `xl/worksheets/sheet6.xml` in place
inside the workbook zip rather than round-tripping through openpyxl, so the
cell comments, the web-extension task pane and the formulas on the other eight
sheets survive untouched.
