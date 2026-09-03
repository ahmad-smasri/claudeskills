# The assumption log

One CSV per building. `build.py` turns them into `../Assumption_Log.xlsx`.

```
python3 build.py                # rebuild the workbook from the CSVs
python3 build.py --check        # is the workbook stale? non-zero exit if so
python3 build.py --add RDC2     # start a CSV for a new building
```

## The CSVs are the source

Edit `QNL.csv`, then rebuild. An edit made in the workbook is overwritten by the
next build, and nothing warns you first - `--check` is what tells you the two
have drifted apart.

This is the way round it is for one reason. The workbook used to be the source,
formatted in place by `format_assumption_log.py`. Git cannot merge a binary
`.xlsx`: whichever side wins takes the whole file, with no conflict and no diff
that shows what went. That nearly cost thirteen QNL entries when a branch built
on an older copy was about to be merged over a newer one. A CSV merges line by
line, and a conflict in one looks like a conflict.

## The columns

`ID · Date · Category · Layer · Entity / Scope · What the source says ·
What we did · Why / basis · Rows affected`

The header is checked on every build, so a renamed or reordered column is an
error rather than a silently blank sheet.

Everything is text in the CSV. `Rows affected` comes back as a number where the
whole field is an integer, and stays text otherwise - seven entries legitimately
say things like `n/a`, `8 dropped` and `564 (574 errors -> 10)`.

`Category` drives the fill colour on that cell: `Identifier`, `Location`,
`Units`, `Spelling`, `Class`, `Structure`, `Scope`, `Source defect`. A category
outside that set simply gets no fill.

## Sheets

`ORDER` in `build.py` fixes the sheet order - SSC, HQ, QNL, RDC. A CSV whose
name is not in that list is appended after them, so dropping in a file is enough
to add a building.

A CSV with a header and no rows becomes a sheet carrying the italic
`(no entries yet)` placeholder. RDC stands that way: it has never had BMS
screens or drawings supplied.
