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
EQUIP_HEADERS = ("equipment tag", "asset tag", "equipment", "asset", "parent",
                 "device", "equipment name", "unit name", "unit tag")
# Headers that look like equipment but are not. "Unit" is the trap: on an IO list
# it almost always means the *engineering unit* (degC, kW, Pa), not the unit of
# plant. Matching it as equipment fills known_equipment with 'bar', 'kw', 'hz',
# so has_point() answers "cannot tell" for every real unit and the IO list
# silently adjudicates nothing.
NOT_EQUIP_HEADERS = ("unit", "units", "uom", "eng unit", "engineering unit",
                     "min eu", "max eu", "minraw", "maxraw")


def norm(text: str) -> str:
    """Compare identifiers without being defeated by case or separators."""
    return re.sub(r"[^a-z0-9]", "", str(text).lower())


def find_column(header: list[str], candidates: tuple, exclude: tuple = ()) -> int | None:
    low = [h.strip().lower() for h in header]
    ok = [i for i, h in enumerate(low) if h not in exclude]
    for want in candidates:
        for i in ok:
            if low[i] == want:
                return i
    for i in ok:
        if any(want in low[i] for want in candidates):
            return i
    return None


def split_tag(tag: str):
    """A dotted historian tag -> (equipment, point), or (None, None).

    IO lists frequently carry no equipment column at all; the equipment is the
    left of the dot in the tag itself (`QNL_AHUB001_SupFan.kW` -> unit
    `QNL_AHUB001`, point `SupFan.kW`). Deriving it is what lets has_point()
    answer for real units instead of shrugging at every one of them.
    """
    if not tag or "." not in tag:
        return None, None
    left, point = tag.rsplit(".", 1)
    # A part segment (…_SupFan, …_CoolVlv) belongs to the point, not the
    # equipment. Split one off only when it actually looks like a part: it must
    # contain a letter, so a purely numeric tail stays with the equipment -
    # QNL_VAV_B_S11_026 is unit 026 of system S11, not part "026" of a unit
    # "QNL_VAV_B_S11".
    m = re.match(r"^(.*[A-Za-z]\d+)_([A-Za-z][A-Za-z0-9]*)$", left)
    if m:
        return m.group(1), m.group(2) + "." + point
    return left, point


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

    **Every sheet of a workbook is read, not just the first.** IO lists routinely
    split analog and discrete points across separate tabs (QNL ships
    `QNL analog cp2` and `QNL Descrete cp2`), and the tabs need not share a
    layout, so each is header-matched on its own. Reading only the first sheet
    silently drops the others, and every point that lived on them is then reported
    as matching no IO row - a phantom over-inclusion finding against a sheet that
    is actually correct. Sheets with no recognisable key/name column are skipped,
    which is what index and legend tabs look like.
    """
    sheets = []          # [(label, header, body)]
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
        with open(path, encoding="utf-8-sig", newline="") as fh:
            rows = [[c.strip() for c in r] for r in csv.reader(fh)]
        rows = [r for r in rows if any(r)]
        if rows:
            sheets.append((path.name, rows[0], rows[1:]))
    if not sheets:
        sys.exit(f"{path} is empty")

    out = []
    used, skipped = [], []
    first_header = sheets[0][1]
    i_id = i_name = i_eq = None
    for label, header, body in sheets:
        s_id = find_column(header, ID_HEADERS)
        s_name = find_column(header, NAME_HEADERS)
        s_eq = find_column(header, EQUIP_HEADERS, exclude=NOT_EQUIP_HEADERS)
        if s_id is None and s_name is None:
            skipped.append(label)
            continue
        if not used:                      # report the first usable sheet's columns
            i_id, i_name, i_eq = s_id, s_name, s_eq
        used.append(label)
        for n, r in enumerate(body, start=2):
            def cell(i):
                return r[i] if i is not None and i < len(r) else ""
            tsid, name = cell(s_id), cell(s_name)
            if not tsid and not name:
                continue
            if on_blank_key and s_id is not None and not tsid:
                on_blank_key(n, name)
            # No equipment column, or none that parsed: derive the unit and the
            # point from the dotted tag, which is where an IO list of this shape
            # actually carries them.
            eq = cell(s_eq)
            derived_eq, derived_point = split_tag(tsid)
            if not eq and derived_eq:
                eq = derived_eq
                if derived_point:
                    name = derived_point
            # Row numbers must be unique across sheets - they key "which IO rows
            # did the sheet account for", so a collision would mark a row on one
            # tab as matched because a same-numbered row on another tab was.
            out.append((tsid, name, eq, (label, n)))

    if not used:
        sys.exit(
            f"cannot tell which column of {path.name} holds the telemetry key or the\n"
            f"point name. Its headers are: {first_header}\n"
            f"Ask the user which column is which rather than guessing - a wrong guess\n"
            f"silently reports every point as unmatched.")

    return IOList(path, out,
                  header[i_id] if i_id is not None else None,
                  header[i_name] if i_name is not None else None,
                  header[i_eq] if i_eq is not None else None)
