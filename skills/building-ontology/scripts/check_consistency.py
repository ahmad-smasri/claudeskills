#!/usr/bin/env python3
"""Cross-unit consistency checks for a PARA Brick ontology sheet.

    python3 check_consistency.py MyBuilding.xlsx
    python3 check_consistency.py MyBuilding.xlsx --family brick:Fan_Coil_Unit
    python3 check_consistency.py MyBuilding.csv --strict --max 5

`validate_ontology.py` reads one row at a time: it catches a bad prefix, a
missing label, a term that is not in Brick. It cannot see the defect that only
shows up when you put two units of the same class side by side - the FCU that
is missing a point its 136 siblings all have, the VAV whose supply-air setpoint
is typed differently from every other VAV, the row where someone pasted a flow
rate over an external reference. This script does that comparison.

Everything is inferred from the sheet. No per-family configuration, no expected
point list, no naming scheme: give it any building and it works out what the
families are, what a complete unit looks like in each, and who departs from it.

Findings carry `-CON-` codes, explained in references/known-issues.md.

Exit status: 0 clean, 1 errors found, 2 with --strict if anything was reported,
3 if the file could not be read.
"""
from __future__ import annotations

import argparse
import collections
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from validate_ontology import Report, read_sheet   # noqa: E402

# Predicates that hang a child entity off a parent. Anything that appears as the
# object of one of these is a part or a point, never a unit in its own right.
CHILD_PREDICATES = ("brick:hasPoint", "brick:hasPart")

# Predicates whose object is *meant* to differ from unit to unit. Excluded from
# the structural comparison - otherwise every room a VAV feeds reads as a
# missing relation on the other 245 VAVs - but checked separately for
# cardinality and placeholder smells.
# The metering three belong here for the same reason: a virtual meter names the
# one space it measures, so a 360-meter family otherwise reports 720 errors
# saying each meter is missing the 359 targets its siblings carry.
VARYING_PREDICATES = ("rec:locatedIn", "rec:feeds", "rec:isFedBy",
                      "rec:isPartOf", "brick:isPartOf",
                      "brick:meters", "brick:isMeteredBy", "brick:isSubMeterOf")

# Share of a family's rows that must agree before a predicate's object shape is
# taken as the expected shape.
SHAPE_CONFIDENCE = 0.6

# A unit's rows should sit together. Flag when the span is this many times the
# number of rows the unit actually has.
CONTIGUITY_RATIO = 3

# Predicates where every unit sharing one target is a placeholder smell. Not
# every varying predicate qualifies: levels all being part of one building, or
# every FCU being fed by one chilled water loop, is how buildings work. A room
# serving as the location or the served space of every unit in a family is not.
SHARED_TARGET_PREDICATES = ("rec:locatedIn", "rec:feeds")

# Below this, "every unit points at the same target" is unremarkable rather than
# a sign of placeholder data.
SHARED_TARGET_MIN_UNITS = 3

# Predicates whose object is shared plant rather than something inside the
# building - a system, a loop, a riser. Both reference models write those
# without a building code: QF SSC has entity:HVAC and entity:CHW-System, Dar
# Cairo has entity:CHWS-LOOP-1 and entity:Water_System. So the missing-prefix
# check does not apply to them.
SHARED_PLANT_PREDICATES = ("brick:isPartOf", "rec:isFedBy")


# Excel error literals, which reach the sheet when a formula is saved as values.
EXCEL_ERRORS = frozenset((
    "#N/A", "#REF!", "#VALUE!", "#DIV/0!", "#NAME?", "#NULL!", "#NUM!",
    "#SPILL!", "#CALC!", "#GETTING_DATA",
))


@dataclass
class Triple:
    row: int
    subject: str
    subject_type: str
    predicate: str
    obj: str
    object_type: str
    props: dict = field(default_factory=dict)


@dataclass
class Family:
    """Every entity of one class, with the triples that belong to each."""
    cls: str
    units: list[str]
    triples: dict[str, list[Triple]] = field(default_factory=dict)

    @property
    def rows(self) -> list[int]:
        return sorted(t.row for rows in self.triples.values() for t in rows)


# --------------------------------------------------------------------- loading

def load_triples(path: Path) -> list[Triple]:
    header, body = read_sheet(path)
    low = [h.strip().lower() for h in header]
    for want in ("subject", "subjecttype", "predicate", "object", "objecttype"):
        if want not in low:
            sys.exit(f"{path} has no {want!r} column - is this an ontology sheet?")
    idx = [low.index(c) for c in
           ("subject", "subjecttype", "predicate", "object", "objecttype")]

    # Prop pairs live past the fifth column as (name, value) couples. They carry
    # brick:hasUnit, which W-CON-19 needs.
    prop_cols = [i for i in range(5, len(header) - 1)
                 if low[i].endswith("prop_name")]

    out = []
    for rownum, r in body:
        cells = [r[i].strip() if i < len(r) else "" for i in idx]
        if not cells[0]:
            continue
        props = {}
        for i in prop_cols:
            if i + 1 < len(r):
                name, val = r[i].strip(), r[i + 1].strip()
                if name:
                    props.setdefault(name, val)
        out.append(Triple(rownum, *cells, props=props))
    return out


def object_shape(value: str) -> str:
    """Classify an object cell - the basis of corruption detection.

    A sheet read from .xlsx arrives as text, so a number is recognised by
    parsing rather than by type.
    """
    if not value:
        return "empty"
    if value in EXCEL_ERRORS:
        return "error"           # #REF!, #N/A, #VALUE! saved as a value
    if value == "<blanknode>":
        return "blanknode"
    if value.startswith("entity:"):
        return "entity"
    try:
        float(value)
        return "number"
    except ValueError:
        return "text"


# ----------------------------------------------------------------- discovery

def discover_families(triples: list[Triple]) -> list[Family]:
    """Group entities into families by class.

    A unit is an entity that is the subject of triples and is never the object
    of a containment predicate. Working it out this way rather than from the
    identifier means non-sequential ids, mixed naming schemes and prefix
    collisions all handle themselves.
    """
    children = {t.obj for t in triples if t.predicate in CHILD_PREDICATES}
    schema = {t.row for t in triples
              if t.subject_type == "owl:Class" or t.predicate == "rdfs:subClassOf"}

    unit_class: dict[str, str] = {}
    for t in triples:
        if t.row in schema or t.subject in children:
            continue
        if t.subject_type and not t.subject_type.startswith("<"):
            unit_class.setdefault(t.subject, t.subject_type)

    by_class: dict[str, list[str]] = collections.defaultdict(list)
    for entity, cls in unit_class.items():
        by_class[cls].append(entity)

    # subject -> owning unit, resolved once. Longest first so that a unit whose
    # name is a prefix of another does not swallow it.
    owner: dict[str, str] = {}
    units_by_len = sorted(unit_class, key=len, reverse=True)
    subjects = {t.subject for t in triples}
    for subj in subjects:
        for u in units_by_len:
            if subj == u or (subj.startswith(u) and subj[len(u)] in "_-."):
                owner[subj] = u
                break

    families = []
    for cls, entities in sorted(by_class.items()):
        units = sorted(entities)
        fam = Family(cls=cls, units=units, triples={u: [] for u in units})
        member = set(units)
        for t in triples:
            if t.row in schema:
                continue
            u = owner.get(t.subject)
            if u in member:
                fam.triples[u].append(t)
        families.append(fam)
    return families


def infer_expected_shapes(fam: Family) -> dict[str, str]:
    """Learn what each predicate's object is supposed to look like.

    Per family, never globally: `ref:hasExternalReference` takes a blank node,
    `para:ratedSupplyAirFlowrate` takes a number, and the same predicate can
    legitimately differ between families. A shape only counts as expected when a
    clear majority of the family's rows agree on it.
    """
    dist: dict[str, collections.Counter] = collections.defaultdict(collections.Counter)
    for rows in fam.triples.values():
        for t in rows:
            dist[t.predicate][object_shape(t.obj)] += 1

    expected = {}
    for pred, counter in dist.items():
        shape, n = counter.most_common(1)[0]
        if n / sum(counter.values()) >= SHAPE_CONFIDENCE:
            expected[pred] = shape
    return expected


def pattern(t: Triple, unit: str) -> tuple[str, str, str]:
    """Reduce a triple to a shape that is identical across units when the
    modelling is identical.

    Two collapses do the work. The unit's own id becomes `{U}`, so per-unit
    entity names line up. An object that is a value rather than an entity
    becomes a shape token, so per-unit literals - rated flow rates, room names -
    do not each become their own single-unit "pattern".
    """
    subj = t.subject.replace(unit, "{U}")
    if unit in t.obj:
        obj = t.obj.replace(unit, "{U}")
    elif object_shape(t.obj) == "entity":
        obj = t.obj             # a shared target, or a cross-wiring bug
    else:
        obj = f"<{object_shape(t.obj)}>"
    return (subj, t.predicate, obj)


def show(pat: tuple[str, str, str]) -> str:
    return f"{pat[0]} {pat[1]} {pat[2]}"


def units_phrase(units: list[str], limit: int = 3) -> str:
    names = [u.split(":", 1)[-1] for u in sorted(units)]
    if len(names) <= limit:
        return ", ".join(names)
    return f"{', '.join(names[:limit])} and {len(names) - limit} more"


# -------------------------------------------------------------------- checks

# Populated by check_pattern_presence when an IO list resolves a missing point,
# and read by check_row_counts so a row-count gap the IO list already explained
# is not reported a second time in another shape. Reset per family.
io_explained: dict[str, set] = collections.defaultdict(set)


def io_confirms_absent(io, units, pat) -> bool:
    """True only when the IO list positively says none of these units has the
    point. A unit the list says nothing about is not evidence, so one unknown
    unit is enough to leave the finding standing.

    The point is named by the object on a `brick:hasPoint` row and by the subject
    on the rows that hang off it - a confirmed-absent point takes its external
    reference and its own property rows with it, and all of them show up here as
    separate missing patterns.
    """
    subj, pred, obj = pat
    src = obj if pred == "brick:hasPoint" else subj
    point = src.replace("{U}", "").lstrip("_-.")
    if not point or "{U}" not in src:
        return False
    for u in units:
        if io.has_point(u.split(":", 1)[-1], point) is not False:
            return False
    return True


def check_row_counts(fam, expected, report, io=None):
    """A unit with fewer rows than its siblings is missing something - unless the
    IO list already explained every one of the relations it is missing."""
    counts = {u: len(rows) for u, rows in fam.triples.items()}
    modal = collections.Counter(counts.values()).most_common(1)[0][0]
    for u, n in sorted(counts.items()):
        if n == modal:
            continue
        short = modal - n
        if short > 0 and len(io_explained.get(u, ())) >= short:
            report.add("INFO", "I-CON-1", 0,
                       f"{fam.cls}: {u} has {n} rows against the typical {modal}, and "
                       f"the IO list accounts for all {short} - confirmed, not a defect")
        else:
            report.add("ERROR", "E-CON-1", fam.triples[u][0].row if fam.triples[u] else 0,
                       f"{fam.cls}: {u} has {n} rows, {modal} is typical ({n - modal:+d})")


def check_pattern_presence(fam, expected, report, io=None):
    """Relations present on most units and absent - or doubled - on the rest.

    With an IO list, a missing point is adjudicated rather than flagged: if the
    list confirms none of the units has that point, the gap is a fact about the
    building and reported as one. This is what turns a per-family review from a
    list of questions into a list of answers.
    """
    per_unit = {u: collections.Counter(pattern(t, u) for t in rows)
                for u, rows in fam.triples.items()}
    seen = {p for c in per_unit.values() for p in c}

    for pat in sorted(seen):
        if pat[1] in VARYING_PREDICATES:
            continue
        counts = {u: per_unit[u][pat] for u in fam.units}
        if set(counts.values()) == {1}:
            continue
        missing = [u for u, n in counts.items() if n == 0]
        dupes = [u for u, n in counts.items() if n > 1]
        if missing and len(missing) < len(fam.units):
            resolved = io is not None and io_confirms_absent(io, missing, pat)
            if resolved:
                report.add("INFO", "I-CON-2", 0,
                           f"{fam.cls}: `{show(pat)}` is absent on "
                           f"{len(missing)} unit(s) and the IO list confirms none of "
                           f"them has it - {units_phrase(missing)}")
                for u in missing:
                    io_explained[u].add(pat)
            else:
                report.add("ERROR", "E-CON-2", 0,
                           f"{fam.cls}: `{show(pat)}` is on "
                           f"{len(fam.units) - len(missing)}/{len(fam.units)} units, "
                           f"absent on {units_phrase(missing)}")
        if dupes:
            report.add("ERROR", "E-CON-3", 0,
                       f"{fam.cls}: `{show(pat)}` appears more than once on "
                       f"{units_phrase(dupes)}")


def check_object_corruption(fam, expected, report, io=None):
    """The check a row count cannot make.

    A unit can carry every row its siblings carry and still be broken, because a
    value was pasted over the object column. Flag every object whose shape
    contradicts what the rest of the family does with that predicate.
    """
    for u, rows in sorted(fam.triples.items()):
        for t in rows:
            want = expected.get(t.predicate)
            got = object_shape(t.obj)
            if want and got != want:
                report.add("ERROR", "E-CON-4", t.row,
                           f"{fam.cls}: object of {t.predicate} is {got} "
                           f"({t.obj!r}), the family uses {want}")


def check_type_consistency(fam, expected, report, io=None):
    """The same relation must carry the same classes on every unit."""
    seen: dict[tuple, set] = collections.defaultdict(set)
    for u, rows in fam.triples.items():
        for t in rows:
            seen[pattern(t, u)].add((t.subject_type, t.object_type))
    for pat, pairs in sorted(seen.items()):
        if len(pairs) > 1:
            report.add("ERROR", "E-CON-5", 0,
                       f"{fam.cls}: `{show(pat)}` is typed "
                       f"{len(pairs)} different ways: {sorted(pairs)}")


def check_varying_predicates(fam, expected, report, io=None):
    """Excluded from the structural comparison, still worth checking.

    Each unit should carry exactly one of each; and when every unit in a family
    points at a single target, that is usually placeholder data rather than a
    building where 137 FCUs all serve one room.
    """
    for pred in VARYING_PREDICATES:
        targets = {}
        for u, rows in sorted(fam.triples.items()):
            vals = [t for t in rows if t.predicate == pred]
            if vals:
                targets[u] = [t.obj for t in vals]
            if len(vals) > 1:
                report.add("ERROR", "E-CON-6", vals[1].row,
                           f"{fam.cls}: {u} has {len(vals)} {pred} triples")
        if pred not in SHARED_TARGET_PREDICATES:
            continue
        distinct = {v[0] for v in targets.values()}
        if len(targets) >= SHARED_TARGET_MIN_UNITS and len(distinct) == 1:
            report.add("WARN", "W-CON-7", 0,
                       f"{fam.cls}: all {len(targets)} units share the same "
                       f"{pred} target {next(iter(distinct))} - check for "
                       f"placeholder data")


def check_feeds_equals_located(fam, expected, report, io=None):
    """Worth confirming rather than fixing: it is right for a unit that
    conditions the room it sits in, and wrong when the room column was reused
    for two different questions."""
    same = []
    for u, rows in fam.triples.items():
        loc = [t.obj for t in rows if t.predicate == "rec:locatedIn"]
        fed = [t.obj for t in rows if t.predicate == "rec:feeds"]
        if loc and fed and loc[0] == fed[0]:
            same.append(u)
    if same and len(same) == len(fam.units) > 1:
        report.add("INFO", "I-CON-8", 0,
                   f"{fam.cls}: every unit's rec:feeds target equals its "
                   f"rec:locatedIn target - confirm the source column means both")


def check_reference_pairing(fam, expected, report, io=None):
    """Every declared point should have one external reference, and every
    reference should belong to something the sheet declares.

    Points only for the missing-reference check: a point is a key in the
    telemetry database and is useless without the id that reaches it, whereas a
    part - a fan, a coil, a VFD - is a physical thing that carries points and
    needs no reference of its own.
    """
    for u, rows in sorted(fam.triples.items()):
        declared = sorted({t.obj for t in rows
                           if t.predicate in CHILD_PREDICATES
                           and object_shape(t.obj) == "entity"})
        points = {t.obj for t in rows
                  if t.predicate == "brick:hasPoint" and object_shape(t.obj) == "entity"}
        refs = collections.Counter(t.subject for t in rows
                                   if t.predicate == "ref:hasExternalReference")
        for child in declared:
            if refs.get(child, 0) == 0 and child in points:
                local = child.split(":", 1)[-1]
                parent, _, suffix = local.rpartition("_")
                key = io.timeseries_id(parent, suffix) if io is not None else None
                if key == "":
                    report.add("INFO", "I-CON-9", 0,
                               f"{fam.cls}: {child} has no ref:hasExternalReference and "
                               f"the IO list has no timeseries id for it - confirmed")
                elif key:
                    report.add("ERROR", "E-CON-18", 0,
                               f"{fam.cls}: {child} has no ref:hasExternalReference but "
                               f"the IO list gives it {key!r}")
                else:
                    report.add("WARN", "W-CON-9", 0,
                               f"{fam.cls}: {child} is declared but has no "
                               f"ref:hasExternalReference")
            elif refs[child] > 1:
                report.add("ERROR", "E-CON-10", 0,
                           f"{fam.cls}: {child} has {refs[child]} external references")
        for subj in sorted(refs):
            if subj != u and subj not in declared:
                report.add("WARN", "W-CON-11", 0,
                           f"{fam.cls}: {subj} carries an external reference but is "
                           f"never declared with {' or '.join(CHILD_PREDICATES)}")


def check_contiguity(fam, expected, report, io=None):
    """A unit's rows should sit together. One stranded row hundreds of rows from
    the rest is easy to lose on the next edit."""
    for u, rows in sorted(fam.triples.items()):
        nums = sorted(t.row for t in rows)
        if len(nums) < 2:
            continue
        span = nums[-1] - nums[0] + 1
        if span > len(nums) * CONTIGUITY_RATIO:
            block = collections.Counter(n // 100 for n in nums).most_common(1)[0][0]
            strays = [n for n in nums if n // 100 != block]
            report.add("WARN", "W-CON-12", strays[0] if strays else nums[0],
                       f"{fam.cls}: {u} spans {span} rows for {len(nums)} triples; "
                       f"stray rows {strays[:8]}")


def check_naming(fam, expected, report, io=None):
    """Naming hygiene inside a family. Advisory - it never blocks a handover."""
    suffix_class: dict[str, set[str]] = collections.defaultdict(set)
    for u, rows in sorted(fam.triples.items()):
        for t in rows:
            local = t.subject.split(":", 1)[-1]
            parts = local.split("_")
            for a, b in zip(parts, parts[1:]):
                if a == b and a:
                    report.add("INFO", "I-CON-13", t.row,
                               f"{fam.cls}: {t.subject} repeats the token {a!r}")
                    break
            # Children are usually declared as the object of hasPoint/hasPart
            # and may never appear as a subject, so read both sides.
            for name, cls in ((t.subject, t.subject_type), (t.obj, t.object_type)):
                if cls and name.startswith(u) and len(name) > len(u):
                    suffix_class[name[len(u):]].add(cls)

    # Two children whose names differ only by a trailing token - Voltage against
    # Voltage_Reading - are usually the same thing named twice. Only when they
    # carry the same class: a Supply_Fan and its Motor, or a Temperature_Sensor
    # and a Temperature_Setpoint, share a stem and are genuinely different.
    keys = sorted(suffix_class)
    for a in keys:
        for b in keys:
            if a == b or not b.startswith(a + "_") or "_" in b[len(a) + 1:]:
                continue
            shared = suffix_class[a] & suffix_class[b]
            if shared:
                report.add("INFO", "I-CON-14", 0,
                           f"{fam.cls}: child names {a!r} and {b!r} differ only by a "
                           f"trailing token and are both {sorted(shared)[0]} - "
                           f"confirm they are different things")


def squash(name: str) -> str:
    """Drop every separator, so identifiers that differ only in punctuation
    compare equal."""
    return re.sub(r"[^A-Za-z0-9]", "", name)


def check_child_separator_drift(fam, expected, report, io=None):
    """A child whose name matches its parent's except for the separators.

    `Dar-Cairo_Floor-1_A_Occupancy-Virtual-Sensor` owns a point named
    `Dar-Cairo_Floor-1A_Occupancy-Virtual-Sensor_Arrival-Time` - one underscore
    apart, so nothing that keys off the parent's identifier will ever find it.
    Requiring the child to carry the parent's prefix outright would be too
    blunt: a system legitimately has parts named nothing like itself. Requiring
    it only when the two are already the same string modulo punctuation is not.
    """
    for u, rows in sorted(fam.triples.items()):
        for t in rows:
            if t.predicate not in CHILD_PREDICATES or object_shape(t.obj) != "entity":
                continue
            if t.obj.startswith(t.subject):
                continue
            if squash(t.obj).startswith(squash(t.subject)):
                report.add("ERROR", "E-CON-17", t.row,
                           f"{fam.cls}: child {t.obj} differs from its parent "
                           f"{t.subject} only in separators - one of the two is "
                           f"misspelled")


def check_single_instance(fam, expected, report, io=None):
    """With one unit there is no peer to compare against. Say so rather than
    reporting a vacuous pass."""
    if len(fam.units) == 1:
        report.add("INFO", "I-CON-15", 0,
                   f"{fam.cls}: only one instance ({fam.units[0]}), so no cross-unit "
                   f"comparison is possible - integrity checks still applied")


def check_prefix(fam, expected, report, io=None):
    """Entity references that lack the building code every subject carries.

    Objects of `brick:isPartOf` and `rec:isFedBy` are exempt: those name shared
    plant that serves the building rather than something inside it, and both
    reference models deliberately leave the building code off them.
    """
    prefixes = {u.split("_", 1)[0] for u in fam.units if "_" in u}
    if len(prefixes) != 1:
        return
    prefix = next(iter(prefixes))
    seen = set()
    for rows in fam.triples.values():
        for t in rows:
            if t.predicate in SHARED_PLANT_PREDICATES:
                continue
            if object_shape(t.obj) == "entity" and not t.obj.startswith(prefix) \
                    and t.obj not in seen:
                seen.add(t.obj)
                report.add("INFO", "I-CON-16", t.row,
                           f"{fam.cls}: {t.obj} does not carry the {prefix}_ prefix "
                           f"every subject in this family uses")


def check_unit_per_class(triples, report):
    """W-CON-19: one point class should carry one unit across the whole sheet.

    A file-wide check, not a per-family one - a point class routinely spans
    families (`brick:Room_Air_Temperature_Sensor` sits on VAV, CAV and FCU), and
    a split that only shows when the families are read together is exactly the
    one a per-family pass would miss.

    The unit belongs to the physical quantity, and the class names that quantity,
    so one class reading in two units means at least one of them is wrong. On QNL
    this caught `brick:Electric_Power_Sensor` split 20 `unit:PERCENT` / 4
    `unit:KiloW`: the IO list carried `%` on 20 of its 24 `.kW` tags, against a
    description reading "Power". The split was the tell, before anyone read a tag.

    A warning rather than an error: a class whose quantity genuinely admits more
    than one unit is possible, and the reviewer is the one who can say so.
    """
    by_class = collections.defaultdict(collections.Counter)
    where = {}
    for t in triples:
        unit = t.props.get("brick:hasUnit")
        if not unit or not t.object_type:
            continue
        by_class[t.object_type][unit] += 1
        where.setdefault((t.object_type, unit), t.row)
    for cls, units in sorted(by_class.items()):
        if len(units) > 1:
            spread = ", ".join(f"{u} on {n}" for u, n in units.most_common())
            report.add("WARN", "W-CON-19", where[(cls, units.most_common()[0][0])],
                       f"{cls} carries {len(units)} different units - {spread}. "
                       f"The class names the quantity, so at least one is wrong; "
                       f"check the source's unit column against the class")


# check_pattern_presence runs before check_row_counts: it is what fills
# io_explained, which check_row_counts then reads.
CHECKS = (check_single_instance, check_pattern_presence, check_row_counts,
          check_child_separator_drift,
          check_object_corruption, check_type_consistency,
          check_varying_predicates, check_feeds_equals_located,
          check_reference_pairing, check_contiguity, check_naming, check_prefix)


# --------------------------------------------------------------------- driver

def run(path: Path, report: Report, only: str | None = None, io=None):
    triples = load_triples(path)
    families = [f for f in discover_families(triples)
                if only is None or f.cls == only]
    if only and not families:
        sys.exit(f"no family typed {only!r} in {path}")

    families.sort(key=lambda f: (-len(f.units), f.cls))
    print(f"\n{len(triples)} triples, {len(families)} families\n")
    print(f"  {'class':<45} {'units':>6} {'triples':>8}  rows")
    for fam in families:
        rows = fam.rows
        span = f"{rows[0]}-{rows[-1]}" if rows else "-"
        print(f"  {fam.cls:<45} {len(fam.units):>6} {len(rows):>8}  {span}")
    print()

    for fam in families:
        expected = infer_expected_shapes(fam)
        io_explained.clear()
        for check in CHECKS:
            check(fam, expected, report, io)

    # File-wide checks run once, after the per-family pass.
    if only is None:
        check_unit_per_class(triples, report)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("sheet", type=Path)
    ap.add_argument("--family", help="check only this class, e.g. brick:Fan_Coil_Unit")
    ap.add_argument("--max", type=int, default=15, help="max findings shown per rule code")
    ap.add_argument("--strict", action="store_true", help="fail on warnings too")
    ap.add_argument("--ignore", default="", help="comma-separated rule codes to suppress")
    ap.add_argument("--io", type=Path, metavar="PATH",
                    help="the IO list. Supplied, it is used as evidence: a missing "
                         "point the list confirms is reported as a fact, not a defect.")
    ap.add_argument("--report", type=Path, metavar="PATH",
                    help="also write every finding to PATH (.xlsx or .csv), a file of "
                         "its own. Nothing is ever written into the ontology sheet.")
    args = ap.parse_args()

    if not args.sheet.exists():
        print(f"no such file: {args.sheet}", file=sys.stderr)
        return 3

    io = None
    if args.io:
        if not args.io.exists():
            print(f"no such file: {args.io}", file=sys.stderr)
            return 3
        import io_list
        io = io_list.load(args.io)
        print(f"IO list: {io.describe()}")

    report = Report(args.max)
    run(args.sheet, report, args.family, io)
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
