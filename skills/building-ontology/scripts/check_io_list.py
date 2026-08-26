#!/usr/bin/env python3
"""Cross-check the points in an ontology sheet against the IO list they came from.

    python3 check_io_list.py MyBuilding.xlsx --io IO_List.xlsx
    python3 check_io_list.py MyBuilding.xlsx --io IO.csv --report findings.xlsx

Points are the one layer of a building ontology that must not be inferred. Every
point in the sheet has to trace back to a row in the IO list, because a point the
BMS does not publish resolves to an **empty timeseries**: the front end shows a
tile, the tile has no data, and nobody can tell whether the sensor is broken or
was never real. Over-inclusion is worse than omission here.

The check runs in both directions:

  E-IO-1  a point in the sheet with no matching IO row - over-inclusion, and the
          reason this script exists
  W-IO-2  an IO row with no point in the sheet - under-inclusion; usually a
          deliberate scope decision, so it is a warning, not an error
  E-IO-3  two points in the sheet claiming the same timeseries id
  W-IO-4  a point whose ref:hasTimeseriesId differs from the IO list's id for
          the same point name
  W-IO-5  an IO row whose timeseries id is blank, so nothing can match it

Matching is on the timeseries id first, because that is the only value both
sides genuinely share. Where the sheet has no id yet, it falls back to the point
name. **Where neither matches cleanly, the script reports the pair rather than
guessing** - ask the user which column of their IO list is the telemetry key.

Exit status: 0 clean, 1 errors found, 2 with --strict if anything was reported,
3 if a file could not be read.
"""
from __future__ import annotations

import argparse
import collections
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from validate_ontology import Report, read_sheet, pick_ontology_sheet   # noqa: E402

# Column headers an IO list might use for the telemetry key and the point name.
# Matched case-insensitively against the header row, longest first.
ID_HEADERS = ("hastimeseriesid", "timeseriesid", "timeseries id", "timeseries_id",
              "tsid", "ts id", "telemetry id", "telemetryid", "bacnet name",
              "object name", "point id", "pointid", "tag", "key")
NAME_HEADERS = ("point name", "pointname", "point", "description", "point description",
                "name", "signal", "signal name")
EQUIP_HEADERS = ("equipment", "asset", "equipment tag", "asset tag", "parent",
                 "device", "unit")


def norm(text: str) -> str:
    """Compare identifiers without being defeated by case or separators."""
    return re.sub(r"[^a-z0-9]", "", text.lower())


def find_column(header: list[str], candidates: tuple) -> int | None:
    low = [h.strip().lower() for h in header]
    for want in candidates:
        if want in low:
            return low.index(want)
    for i, h in enumerate(low):
        if any(want in h for want in candidates):
            return i
    return None


def load_io_list(path: Path, report: Report):
    """Read the IO list and return [(timeseries_id, point_name, equipment, row)].

    **Every sheet is read, not just the first.** IO lists routinely split analog
    and discrete points across separate tabs (QNL ships `QNL analog cp2` and
    `QNL Descrete cp2`), and the tabs need not share a layout, so each is
    header-matched on its own. Reading only the first sheet silently drops the
    others and reports every point that lived on them as matching no IO row -
    a phantom over-inclusion finding against a sheet that is in fact correct.
    Sheets with no recognisable key/name column are skipped and named, which is
    what index and legend tabs look like.

    `row` is "<sheet>!<n>" so a finding points at the tab it came from and
    two tabs cannot collide on a row number.
    """
    sheets = []
    if path.suffix.lower() in (".xlsx", ".xlsm"):
        try:
            import openpyxl
        except ImportError:
            sys.exit("openpyxl is needed to read .xlsx - pip install openpyxl")
        for ws in openpyxl.load_workbook(path, data_only=True).worksheets:
            rows = [["" if c is None else str(c).strip() for c in r]
                    for r in ws.iter_rows(values_only=True)]
            rows = [r for r in rows if any(r)]
            if len(rows) > 1:
                sheets.append((ws.title, rows[0], rows[1:]))
    else:
        import csv
        with open(path, encoding="utf-8-sig", newline="") as fh:
            rows = [[c.strip() for c in r] for r in csv.reader(fh)]
        rows = [r for r in rows if any(r)]
        if rows:
            sheets.append((path.name, rows[0], rows[1:]))
    if not sheets:
        sys.exit(f"{path} is empty")

    print(f"IO list  : {path.name}")
    out, used, skipped = [], [], []
    for label, header, body in sheets:
        i_id = find_column(header, ID_HEADERS)
        i_name = find_column(header, NAME_HEADERS)
        i_eq = find_column(header, EQUIP_HEADERS)
        if i_id is None and i_name is None:
            skipped.append(label)
            continue
        used.append(label)
        print(f"  sheet {label!r}: id={header[i_id] if i_id is not None else '(none)'}"
              f", name={header[i_name] if i_name is not None else '(none)'}"
              f", equipment={header[i_eq] if i_eq is not None else '(none)'}")
        for n, r in enumerate(body, start=2):
            def cell(i):
                return r[i] if i is not None and i < len(r) else ""
            tsid, name = cell(i_id), cell(i_name)
            if not tsid and not name:
                continue
            where = f"{label}!{n}"
            if i_id is not None and not tsid:
                report.add("WARN", "W-IO-5", where,
                           f"IO row for {name!r} has no timeseries id, so nothing in "
                           f"the sheet can be matched to it")
            out.append((tsid, name, cell(i_eq), where))
    if skipped:
        print(f"  skipped (no key/name column): {', '.join(skipped)}")
    if not used:
        sys.exit(
            f"cannot tell which column of {path.name} holds the telemetry key or the\n"
            f"point name. Its headers are: {sheets[0][1]}\n"
            f"Ask the user which column is which rather than guessing - a wrong guess\n"
            f"silently reports every point as unmatched.")
    return out


def load_points(path: Path, report: Report):
    """Return [(entity, timeseries_id, row)] for every brick:hasPoint object."""
    header, body = read_sheet(path)
    low = [h.strip().lower() for h in header]
    idx = {c: low.index(c) for c in
           ("subject", "subjecttype", "predicate", "object", "objecttype") if c in low}
    if len(idx) < 5:
        sys.exit(f"{path} is not an ontology sheet")

    points, tsid = {}, {}
    for rownum, r in body:
        def cell(name):
            i = idx[name]
            return r[i].strip() if i < len(r) else ""
        pred, subj, obj = cell("predicate"), cell("subject"), cell("object")
        if pred == "brick:hasPoint" and obj.startswith("entity:"):
            points.setdefault(obj, rownum)
        if pred == "ref:hasExternalReference" and cell("objecttype") == "ref:TimeseriesReference":
            for i in range(5, len(header) - 1, 2):
                if i + 1 < len(r) and r[i].strip() == "ref:hasTimeseriesId":
                    tsid[subj] = r[i + 1].strip()
    return points, tsid


def run(sheet: Path, io_path: Path, report: Report):
    io_rows = load_io_list(io_path, report)
    points, tsid = load_points(sheet, report)
    print(f"ontology : {sheet.name}")
    print(f"  {len(points)} points declared with brick:hasPoint, "
          f"{len(tsid)} carrying a ref:hasTimeseriesId")
    print(f"  {len(io_rows)} IO rows\n")

    io_by_id = {norm(t): (t, n, e, r) for t, n, e, r in io_rows if t}
    io_by_name = collections.defaultdict(list)
    for t, n, e, r in io_rows:
        if n:
            io_by_name[norm(n)].append((t, n, e, r))

    # E-IO-3: two points claiming one telemetry key
    for key, owners in collections.Counter(
            norm(v) for v in tsid.values() if v).items():
        if owners > 1:
            names = [e for e, v in tsid.items() if norm(v) == key]
            report.add("ERROR", "E-IO-3", 0,
                       f"{owners} points share one timeseries id: {sorted(names)[:4]}")

    # E-IO-1 / W-IO-4: every point in the sheet must trace back to an IO row
    matched_io = set()
    for entity, rownum in sorted(points.items()):
        local = entity.split(":", 1)[-1]
        their_id = tsid.get(entity, "")
        hit = io_by_id.get(norm(their_id)) if their_id else None
        if hit is None:
            by_name = io_by_name.get(norm(local.rsplit("_", 1)[-1])) or \
                io_by_name.get(norm(local))
            hit = by_name[0] if by_name else None
            if hit and their_id and norm(hit[0]) != norm(their_id):
                report.add("WARN", "W-IO-4", rownum,
                           f"{entity} carries timeseries id {their_id!r} but the IO "
                           f"list gives {hit[0]!r} for {hit[1]!r}")
        if hit is None:
            report.add("ERROR", "E-IO-1", rownum,
                       f"{entity} is in the sheet but matches no IO row - its "
                       f"timeseries would resolve empty. Remove it, or confirm the "
                       f"IO list is incomplete")
        else:
            matched_io.add(hit[3])

    # W-IO-2: IO rows the sheet never modelled
    for t, n, e, rownum in io_rows:
        if rownum not in matched_io:
            report.add("WARN", "W-IO-2", rownum,
                       f"IO row {n or t!r}{f' on {e}' if e else ''} has no point in "
                       f"the sheet - in scope, or deliberately left out?")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("sheet", type=Path)
    ap.add_argument("--io", type=Path, required=True, metavar="PATH",
                    help="the IO list, .xlsx or .csv")
    ap.add_argument("--max", type=int, default=15, help="max findings shown per rule code")
    ap.add_argument("--strict", action="store_true", help="fail on warnings too")
    ap.add_argument("--ignore", default="", help="comma-separated rule codes to suppress")
    ap.add_argument("--report", type=Path, metavar="PATH",
                    help="also write every finding to PATH (.xlsx or .csv), a file of "
                         "its own. Nothing is ever written into the ontology sheet.")
    args = ap.parse_args()

    for f in (args.sheet, args.io):
        if not f.exists():
            print(f"no such file: {f}", file=sys.stderr)
            return 3

    report = Report(args.max)
    run(args.sheet, args.io, report)
    ignore = {c.strip() for c in args.ignore.split(",") if c.strip()}
    errors, warns = report.emit(ignore)
    infos = sum(n for c, n in report.counts.items()
                if c not in ignore and c.startswith("I-"))
    print(f"\n{errors} errors, {warns} warnings, {infos} advisories")
    if args.report:
        n = report.write(args.report, args.sheet, ignore)
        print(f"{n} findings written to {args.report}" if n
              else "nothing to report, no file written")
    if errors:
        return 1
    if args.strict and warns:
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
