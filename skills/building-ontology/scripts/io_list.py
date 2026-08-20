#!/usr/bin/env python3
"""Load an IO list and answer questions about it.

Shared by `check_io_list.py`, `validate_ontology.py --io` and
`check_consistency.py --io`.

**The IO list is evidence, not just a comparison target.** Several findings are
suspicious only until the IO list adjudicates them: a point with no timeseries
reference is a defect if the BMS publishes one and a fact if it does not; a point
present on 4 of 10 units is a defect if the other 6 should have it and a fact if
they never did. When an IO list is supplied, those findings are resolved against
it and reported as confirmed rather than flagged - which is the pass a human
would otherwise do by hand.
"""
from __future__ import annotations

import collections
import csv
import re
import sys
from pathlib import Path

# Column headers an IO list might use, matched case-insensitively.
ID_HEADERS = ("hastimeseriesid", "timeseriesid", "timeseries id", "timeseries_id",
              "tsid", "ts id", "telemetry id", "telemetryid", "bacnet name",
              "object name", "point id", "pointid", "tag", "key")
NAME_HEADERS = ("point name", "pointname", "point", "description", "point description",
                "name", "signal", "signal name")
EQUIP_HEADERS = ("equipment", "asset", "equipment tag", "asset tag", "parent",
                 "device", "unit")


def norm(text: str) -> str:
    """Compare identifiers without being defeated by case or separators."""
    return re.sub(r"[^a-z0-9]", "", str(text).lower())


def find_column(header: list[str], candidates: tuple) -> int | None:
    low = [h.strip().lower() for h in header]
    for want in candidates:
        if want in low:
            return low.index(want)
    for i, h in enumerate(low):
        if any(want in h for want in candidates):
            return i
    return None


class IOList:
    """The IO list, indexed for the questions the checks actually ask."""

    def __init__(self, path: Path, rows, id_col, name_col, eq_col):
        self.path = path
        self.rows = rows                      # [(tsid, name, equipment, rownum)]
        self.id_col, self.name_col, self.eq_col = id_col, name_col, eq_col
        self.by_id = {norm(t): r for r in rows if (t := r[0])}
        self.by_name = collections.defaultdict(list)
        for r in rows:
            if r[1]:
                self.by_name[norm(r[1])].append(r)
        # equipment -> the set of point names the IO list gives it
        self.points_of = collections.defaultdict(set)
        self.known_equipment = set()
        for tsid, name, eq, _ in rows:
            if eq:
                self.known_equipment.add(norm(eq))
                if name:
                    self.points_of[norm(eq)].add(norm(name))

    # -- the questions the checks ask -------------------------------------

    def has_point(self, equipment: str, point: str) -> bool | None:
        """Does this unit have this point?  True / False / None for "cannot tell".

        None whenever the IO list says nothing about the equipment at all - an
        absent unit is not evidence of an absent point, and treating it as such
        would resolve findings the IO list never spoke to.
        """
        eq = norm(equipment)
        if eq not in self.known_equipment:
            return None
        return norm(point) in self.points_of[eq]

    def timeseries_id(self, equipment: str, point: str) -> str | None:
        """The telemetry key for a point, '' when the list has the point but no
        key for it, None when the list does not have the point."""
        eq = norm(equipment)
        if eq in self.known_equipment:
            for tsid, name, e, _ in self.rows:
                if norm(e) == eq and norm(name) == norm(point):
                    return tsid
        hit = self.by_name.get(norm(point))
        return hit[0][0] if hit else None

    def describe(self) -> str:
        return (f"{self.path.name}: {len(self.rows)} rows, "
                f"{len(self.known_equipment)} equipment tags, "
                f"{sum(len(v) for v in self.points_of.values())} points")


def load(path: Path, on_blank_key=None) -> IOList:
    """Read an IO list from .xlsx or .csv.

    Exits with an explanation rather than guessing when it cannot tell which
    column holds the telemetry key or the point name: a wrong guess silently
    reports every point as unmatched, which reads exactly like a broken sheet.
    """
    if path.suffix.lower() in (".xlsx", ".xlsm"):
        try:
            import openpyxl
        except ImportError:
            sys.exit("openpyxl is needed to read .xlsx - pip install openpyxl")
        ws = openpyxl.load_workbook(path, data_only=True).worksheets[0]
        rows = [["" if c is None else str(c).strip() for c in r]
                for r in ws.iter_rows(values_only=True)]
    else:
        with open(path, encoding="utf-8-sig", newline="") as fh:
            rows = [[c.strip() for c in r] for r in csv.reader(fh)]
    rows = [r for r in rows if any(r)]
    if not rows:
        sys.exit(f"{path} is empty")

    header, body = rows[0], rows[1:]
    i_id = find_column(header, ID_HEADERS)
    i_name = find_column(header, NAME_HEADERS)
    i_eq = find_column(header, EQUIP_HEADERS)
    if i_id is None and i_name is None:
        sys.exit(
            f"cannot tell which column of {path.name} holds the telemetry key or the\n"
            f"point name. Its headers are: {header}\n"
            f"Ask the user which column is which rather than guessing - a wrong guess\n"
            f"silently reports every point as unmatched.")

    out = []
    for n, r in enumerate(body, start=2):
        def cell(i):
            return r[i] if i is not None and i < len(r) else ""
        tsid, name = cell(i_id), cell(i_name)
        if not tsid and not name:
            continue
        if on_blank_key and i_id is not None and not tsid:
            on_blank_key(n, name)
        out.append((tsid, name, cell(i_eq), n))

    return IOList(path, out,
                  header[i_id] if i_id is not None else None,
                  header[i_name] if i_name is not None else None,
                  header[i_eq] if i_eq is not None else None)
