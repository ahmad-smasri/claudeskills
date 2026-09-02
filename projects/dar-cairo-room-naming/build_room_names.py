#!/usr/bin/env python3
"""Derive Dar Cairo-shaped room subjects from the BMS room-allocation registers.

One source workbook per building in ``sources/``; one output workbook with one
sheet per building.  The rules the client set out, in the order they are applied:

  R1  a green-filled row is a row the BMS screen overruled - take the last of
      the three name columns (D drawings, H VAV/FCU list, J BMS screen).
  R5  otherwise pick between D and J on which of them carries a room number:
      H carries one            -> D
      H does not, J has num+name -> J
      H does not, J is empty     -> D
  R4  when the pick is D (or when D and the pick disagree), reconcile against
      the ontology name already in E: if the pick would lead to E, keep the
      pick's spelling; otherwise take the name from E.
  R2  same room number, different names -> the distinctive one wins.  E is what
      makes a name distinctive: where D matches E's name and the rule-5 pick
      does not, D wins (this is what keeps ROOM NO 42/43/44 apart from the
      SHELL SPACE they all sit in).
  R3  pad the room reference to the building's own width - SSC prints
      <level>.<3 digits>, so 1.027 and 3.041 become 01.027 and 03.041.

Green rows are the one place E is not consulted: green means the drawings and
therefore E were wrong, which is why the BMS screen was traced in the first
place.
"""
import argparse
import csv
import os
import re
import sys

import openpyxl
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

GREEN = "FF00B050"

# Tokens that stay upper case in an identifier segment, the way Dar Cairo keeps
# TECH, UPS, RMU and MDB upper case while spelling Pump-Room in title case.
ACRONYMS = {
    "AV", "AVR", "BMS", "IDF", "MDF", "IT", "ST", "UPS", "LV", "HV", "MEP",
    "AHU", "FCU", "VAV", "WC", "TV", "CCTV", "ELV", "MV", "DB", "MDB", "EMDB",
    "RMU", "TECH", "MECH", "ELEC", "HVAC", "PABX", "SMATV", "AC",
}

# Dar Cairo writes Boiler-And-Heat-Exchange, so an ampersand becomes a word.
WORD_FIXES = {"&": "And", "AND": "And"}


# --------------------------------------------------------------------------
# building profiles - room-reference shape, level segment, building code
# --------------------------------------------------------------------------
class Building:
    def __init__(self, code, sheet_hint, level_width, room_width, level_names):
        self.code = code
        self.sheet_hint = sheet_hint
        self.level_width = level_width      # digits in the level part of a ref
        self.room_width = room_width        # digits in the room part of a ref
        self.level_names = level_names      # raw level token -> id segment

    def level_segment(self, raw):
        return self.level_names.get(raw, "Level-%s" % raw)


BUILDINGS = {
    "SSC": Building(
        code="SSC",
        sheet_hint="SSC",
        level_width=2,
        room_width=3,
        level_names={
            "B": "Level-B1",
            "B1": "Level-B1",
            "01": "Level-01",
            "02": "Level-02",
            "03": "Level-03",
        },
    ),
}

# A room reference is a level token, a dot, and a room number with an optional
# letter suffix: B.013, 01.024, 03.006A, 1.027.
REF_RE = re.compile(r"\b(B\d?|\d{1,2})\.(\d{1,3})([A-Z])?\b")
# Some sources print the reference with no dot at all (ST-4, ROOM NO 42).
BARE_NUM_RE = re.compile(r"\b(\d{2,3})([A-Z])?\b")


def norm_ref(building, level, num, suffix):
    """R3 - pad to the building's own width."""
    if level.startswith("B"):
        lvl = level
    else:
        lvl = level.zfill(building.level_width)
    return lvl, num.zfill(building.room_width) + (suffix or "")


def split_ref(building, text):
    """Return (level, room, name) for a source cell, or (None, None, name)."""
    if text is None:
        return None, None, None
    s = str(text).strip()
    if not s:
        return None, None, None
    m = REF_RE.search(s)
    if not m:
        return None, None, s.strip()
    lvl, room = norm_ref(building, m.group(1), m.group(2), m.group(3))
    name = (s[: m.start()] + " " + s[m.end():]).strip()
    return lvl, room, name


def strip_ref(name, ref):
    """Drop a bare reference token the source ran into the name (ST-4 STAIR 4)."""
    if not name or not ref:
        return name
    out = re.sub(r"(?<![A-Za-z0-9])%s(?![A-Za-z0-9])" % re.escape(ref), " ", name)
    out = " ".join(out.split())
    return out or name


def parse_entity(building, text):
    """entity:SSC_01_024_CORRIDOR -> ('01', '024', 'CORRIDOR')."""
    if text is None:
        return None, None, None
    s = str(text).strip()
    if not s.startswith("entity:"):
        return None, None, None
    parts = s[len("entity:"):].split("_")
    if len(parts) < 3 or parts[0] != building.code:
        return None, None, None
    lvl, room, name = parts[1], parts[2], "_".join(parts[3:])
    if lvl == "B1":
        lvl = "B"
    if room.isdigit():
        room = room.zfill(building.room_width)
    if not lvl.startswith("B"):
        lvl = lvl.zfill(building.level_width)
    return lvl, room, name.replace("_", " ").strip()


def key(name):
    """Comparison form - case and punctuation are not differences."""
    if not name:
        return ""
    s = str(name).upper().replace("&", " AND ")
    s = re.sub(r"[^A-Z0-9]+", " ", s)
    return " ".join(s.split())


def to_segment(name):
    """'VISITOR'S CUBICLE' -> 'Visitors-Cubicle'; keeps acronyms upper case."""
    if not name:
        return ""
    s = str(name).replace("&", " And ").replace("/", " ")
    s = s.replace("'", "").replace("’", "")
    s = re.sub(r"[^A-Za-z0-9\- ]+", " ", s)      # drops . , ( ) : etc.
    s = re.sub(r"\s*-\s*", "-", s)               # IDF - 1 -> IDF-1
    words = [w for w in re.split(r"\s+", s) if w]
    out = []
    for w in words:
        parts = []
        for p in w.split("-"):
            if not p:
                continue
            up = p.upper()
            if up in WORD_FIXES:
                parts.append(WORD_FIXES[up])
            elif up in ACRONYMS:
                parts.append(up)
            elif p.isdigit():
                parts.append(p)
            else:
                parts.append(p.capitalize())
        out.append("-".join(parts))
    return "-".join(out)


def cell_fill(c):
    try:
        if c.fill is not None and c.fill.fill_type == "solid":
            return str(c.fill.start_color.rgb)
    except Exception:
        pass
    return ""


# --------------------------------------------------------------------------
# the decision
# --------------------------------------------------------------------------
def decide(building, row):
    """Return (level, room, name, source, notes[])."""
    notes = []
    d_l, d_r, d_n = split_ref(building, row["D"])
    h_l, h_r, h_n = split_ref(building, row["H"])
    j_l, j_r, j_n = split_ref(building, row["J"])
    e_l, e_r, e_n = parse_entity(building, row["E"])

    if d_r is None and h_r is None and j_r is None and e_r is None:
        notes.append("no room reference in D, H, J or E - left unresolved")
        return None, None, None, "", notes

    if row["green"]:
        # R1 - last of the three names that is present.
        for tag, (l, r, n) in (("J", (j_l, j_r, j_n)),
                               ("H", (h_l, h_r, h_n)),
                               ("D", (d_l, d_r, d_n))):
            if n:
                notes.append("green row: took the last populated name (%s)" % tag)
                if e_n and key(n) != key(e_n):
                    notes.append("overrides column E (%s)" % e_n)
                if r is None and e_r:
                    # the screen names the room but not its number - only the
                    # name was in dispute, so E still supplies the reference.
                    l, r = e_l, e_r
                    n = strip_ref(n, e_r)
                    notes.append("no reference on the screen - taken from E "
                                 "(%s.%s)" % (e_l, e_r))
                return l, r, n, tag, notes
        notes.append("green row with no name in D, H or J")
        return None, None, None, "", notes

    # R5 - D or J, on whether H carries a room number.
    if h_r is not None:
        pick, tag = (d_l, d_r, d_n), "D"
        notes.append("H carries a room number, so column D stands")
    elif j_r is not None and j_n:
        pick, tag = (j_l, j_r, j_n), "J"
        notes.append("H has no room number and J has both, so column J stands")
    else:
        pick, tag = (d_l, d_r, d_n), "D"
        notes.append("no usable J, so column D stands")

    lvl, room, name = pick

    # R2 + R4 - E arbitrates the name.
    if e_n:
        if name and key(name) != key(e_n):
            if d_n and key(d_n) == key(e_n):
                notes.append("column D matches E (%s) and %s does not - D wins"
                             % (e_n, tag))
                lvl, room, name, tag = d_l, d_r, d_n, "D"
            else:
                notes.append("%s (%s) does not match E - name taken from E"
                             % (tag, name))
                name = e_n
                tag = tag + "->E"
        if room is None:
            notes.append("no room number in the picked column - taken from E")
        if e_r and room != e_r:
            if room is None:
                lvl, room = e_l, e_r
            else:
                notes.append("room number %s.%s disagrees with E (%s.%s)"
                             % (lvl, room, e_l, e_r))
        if lvl is None:
            lvl = e_l
    return lvl, room, name, tag, notes


# --------------------------------------------------------------------------
# R2 across rows - one room reference must not end up with two spellings
# --------------------------------------------------------------------------
def is_variant(a, b):
    """'ASSOC DIR OFFICE' and 'ASSOC DIRECTORS OFFICE' name the same room."""
    ta, tb = a.split(), b.split()
    if len(ta) != len(tb) or not ta:
        return False
    for x, y in zip(ta, tb):
        if x == y:
            continue
        lo, hi = (x, y) if len(x) < len(y) else (y, x)
        if len(lo) >= 3 and hi.startswith(lo):
            continue
        return False
    return True


def reconcile(rows):
    """Collapse abbreviation variants sharing one room reference.

    Only variants collapse.  01.029 really does hold ROOM NO 42, 43, 44 and a
    SHELL SPACE, and those stay four rooms; what must not survive is the same
    room spelled two ways.
    """
    groups = {}
    for r in rows:
        if r["name"] and r["ref"]:
            groups.setdefault((r["level"], r["ref"]), []).append(r)
    collapsed, split = [], []
    for (lvl, ref), grp in sorted(groups.items()):
        names = {}
        for r in grp:
            names.setdefault(key(r["name"]), r["name"])
        if len(names) < 2:
            continue
        ks = list(names)
        canon = dict()
        for i, a in enumerate(ks):
            for b in ks[i + 1:]:
                if is_variant(a, b):
                    win = a if len(a) >= len(b) else b
                    canon[a] = win
                    canon[b] = win
        if canon:
            for r in grp:
                k = key(r["name"])
                if k in canon and canon[k] != k:
                    was = r["name"]
                    r["name"] = names[canon[k]]
                    r["notes"].append(
                        "same room as another row spelled %r - taken to the "
                        "fuller spelling %r" % (was, r["name"]))
                    collapsed.append((lvl, ref, was, r["name"]))
        left = {key(r["name"]) for r in grp}
        if len(left) > 1:
            split.append((lvl, ref, sorted(names[k] for k in left)))
    return collapsed, split


def subject(building, lvl, room, name):
    if not name:
        return ""
    seg_name = to_segment(name)
    if not seg_name:
        return ""
    parts = ["entity:%s" % building.code, building.level_segment(lvl or "")]
    parts.append(seg_name)
    if room:
        parts.append("%s-%s" % (lvl, room) if lvl else room)
    return "_".join(parts)


def label(lvl, room, name):
    """Reading form in the QF SSC house style - '1.024 CORRIDOR'."""
    n = key(name)
    if not (lvl and room):
        return n
    if not room[:1].isdigit():          # ST-4 and the like carry no level
        return "%s %s" % (room, n)
    shown = lvl if lvl.startswith("B") else lvl.lstrip("0") or "0"
    return "%s.%s %s" % (shown, room, n)


# --------------------------------------------------------------------------
def load(path, building):
    wb = openpyxl.load_workbook(path)
    ws = None
    for cand in wb:
        if building.sheet_hint.lower() in cand.title.lower() and "log" not in cand.title.lower():
            ws = cand
            break
    if ws is None:
        raise SystemExit("no sheet matching %r in %s" % (building.sheet_hint, path))
    rows = []
    for r in ws.iter_rows(min_row=1, max_row=ws.max_row):
        tag = r[0].value
        if not tag or not isinstance(tag, str):
            continue
        if not re.match(r"^[A-Z]+[A-Z_]*\d", tag.strip()):
            continue
        rows.append({
            "excel_row": r[0].row,
            "A": tag.strip(),
            "B": r[1].value,
            "C": r[2].value,
            "D": r[3].value,
            "E": r[4].value,
            "H": r[7].value,
            "J": r[9].value,
            "green": cell_fill(r[0]) == GREEN,
        })
    return rows


def load_delivered(code):
    """Room reference -> name, from the previously delivered ontology."""
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "..", "..", "reference-models",
                        {"SSC": "QF_SSC_Ontology_ver02.xlsx"}.get(code, ""))
    if not os.path.exists(path):
        return None
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    # Pick the ontology sheet by its header, never by name or position -
    # "SSC_Ontology_Ver0.6" contains "log" and the log tab is sheet one.
    ws = None
    for cand in wb:
        head = next(cand.iter_rows(min_row=1, max_row=1, values_only=True), ())
        if head and str(head[0]).strip().lower() == "subject":
            ws = cand
            break
    if ws is None:
        return None
    building = BUILDINGS[code]
    exact, refs = set(), {}
    for r in ws.iter_rows(values_only=True):
        if not r or len(r) < 5:
            continue
        for subj, typ in ((r[0], r[1]), (r[3], r[4])):
            if typ != "rec:Room":
                continue
            lvl, room, name = parse_entity(building, subj)
            if not room:
                continue
            exact.add((lvl, room, key(name)))
            refs.setdefault((lvl, room), name)
    return {"exact": exact, "refs": refs}


HEADERS = [
    "Tag No.", "Equipment Type", "Included/Not Included",
    "D - room per drawings", "E - existing ontology name",
    "H - room per VAV/FCU list", "J - room per BMS screen",
    "Green", "Level", "Room ref", "Room name",
    "Subject (Dar Cairo shape)", "rdfs:label_en", "Chosen from", "Notes",
]


def write(out_path, sheets):
    wb = openpyxl.Workbook()
    wb.remove(wb.active)
    hdr_fill = PatternFill("solid", start_color="FF1F4E79")
    hdr_font = Font(color="FFFFFFFF", bold=True)
    warn = PatternFill("solid", start_color="FFFFF2CC")
    bad = PatternFill("solid", start_color="FFF8CBAD")
    for name, rows in sheets:
        ws = wb.create_sheet(name)
        ws.append(HEADERS)
        for c in ws[1]:
            c.fill = hdr_fill
            c.font = hdr_font
            c.alignment = Alignment(wrap_text=True, vertical="center")
        for r in rows:
            ws.append([
                r["A"], r["B"], r["C"], r["D"], r["E"], r["H"], r["J"],
                "green" if r["green"] else "",
                r["level"] or "", r["ref"] or "", r["name"] or "",
                r["subject"], r["label"], r["source"], "; ".join(r["notes"]),
            ])
            row = ws.max_row
            if not r["subject"]:
                for c in ws[row]:
                    c.fill = bad
            elif r["green"] or "disagrees" in "; ".join(r["notes"]):
                for c in ws[row]:
                    c.fill = warn
        widths = [12, 8, 12, 32, 40, 32, 30, 7, 9, 10, 28, 46, 34, 12, 70]
        for i, w in enumerate(widths, start=1):
            ws.column_dimensions[get_column_letter(i)].width = w
        ws.freeze_panes = "A2"
        ws.auto_filter.ref = "A1:%s%d" % (get_column_letter(len(HEADERS)), ws.max_row)
    wb.save(out_path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", action="append", default=[],
                    metavar="CODE=PATH", help="e.g. SSC=sources/SSC_rooms.xlsx")
    ap.add_argument("--out", required=True)
    ap.add_argument("--rooms-csv", help="distinct room list")
    args = ap.parse_args()

    sheets, all_rooms = [], []
    for spec in args.src:
        code, path = spec.split("=", 1)
        building = BUILDINGS[code]
        rows = load(path, building)
        for r in rows:
            lvl, room, name, src, notes = decide(building, r)
            r["level"], r["ref"], r["name"] = lvl, room, name
            r["source"], r["notes"] = src, notes

        collapsed, split = reconcile(rows)
        for lvl, ref, was, now in collapsed:
            print("  collapsed %s.%s  %r -> %r" % (lvl, ref, was, now))
        for lvl, ref, names in split:
            print("  %s.%s carries %d distinct names: %s"
                  % (lvl, ref, len(names), ", ".join(names)))

        known = load_delivered(code)
        for r in rows:
            r["subject"] = subject(building, r["level"], r["ref"], r["name"])
            r["label"] = label(r["level"], r["ref"], r["name"]) if r["name"] else ""
            if known and r["ref"]:
                k = (r["level"], r["ref"], key(r["name"]))
                if k not in known["exact"]:
                    if (r["level"], r["ref"]) in known["refs"]:
                        r["notes"].append(
                            "delivered SSC ontology calls %s.%s %r"
                            % (r["level"], r["ref"],
                               known["refs"][(r["level"], r["ref"])]))
                    else:
                        r["notes"].append(
                            "%s.%s is not in the delivered SSC ontology"
                            % (r["level"], r["ref"]))
            if r["subject"]:
                all_rooms.append((code, r["subject"], r["label"],
                                  building.level_segment(r["level"] or ""),
                                  "%s.%s" % (r["level"], r["ref"])
                                  if r["ref"] else "", r["A"]))
        sheets.append((code, rows))
        blank = [r["A"] for r in rows if not r["subject"]]
        print("%s: %d asset rows, %d distinct rooms, %d unresolved%s"
              % (code, len(rows), len({r['subject'] for r in rows if r['subject']}),
                 len(blank), (" (%s)" % ", ".join(blank)) if blank else ""))

    write(args.out, sheets)
    print("wrote %s" % args.out)

    if args.rooms_csv:
        seen, out = set(), []
        for code, subj, lab, lvl, ref, tag in all_rooms:
            if subj in seen:
                continue
            seen.add(subj)
            out.append((code, subj, lab, lvl, ref))
        out.sort()
        with open(args.rooms_csv, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["building", "subject", "rdfs:label_en",
                        "level segment", "room ref"])
            w.writerows(out)
        print("wrote %s (%d rooms)" % (args.rooms_csv, len(out)))


if __name__ == "__main__":
    main()
