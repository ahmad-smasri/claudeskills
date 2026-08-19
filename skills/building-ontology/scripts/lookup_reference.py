#!/usr/bin/env python3
"""Look up precedent in the reference models before inventing anything.

Step 1 of the class-resolution ladder is "is it already in Dar Cairo?". This
makes that mechanical instead of a memory exercise.

    # what Brick/para class did we use for something like a booster pump?
    lookup_reference.py --class "booster pump"

    # what does a complete AHU look like: parts, points, properties
    lookup_reference.py --template brick:Air_Handling_Unit

    # every row mentioning one entity
    lookup_reference.py --entity entity:AHU-B1-02

    # does this term exist in Brick 1.4, and is it preferred?
    lookup_reference.py --term Air_Handling_Unit
"""
from __future__ import annotations

import argparse
import collections
import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MODELS = ROOT.parent.parent / "reference-models"
DATA = ROOT / "references" / "data"
PRIMARY = MODELS / "DarCairo_V93.csv"


def load(path: Path):
    if path.suffix.lower() in (".xlsx", ".xlsm"):
        import openpyxl

        ws = openpyxl.load_workbook(path, data_only=True).active
        rows = [["" if c is None else str(c).strip() for c in r]
                for r in ws.iter_rows(values_only=True)]
    else:
        with open(path, encoding="utf-8-sig", newline="") as fh:
            rows = [[c.strip() for c in r] for r in csv.reader(fh)]
    rows = [r for r in rows if any(r)]
    return rows[0], rows[1:]


def render(header, row, limit=None):
    cells = [f"{h}={v}" for h, v in zip(header, row) if v]
    text = "  |  ".join(cells)
    return text if limit is None or len(text) <= limit else text[: limit - 1] + "…"


def cmd_class(rows, needle: str):
    """Classes whose name or label looks like the search term."""
    needle = needle.lower().replace(" ", "_")
    hits = collections.Counter()
    for r in rows:
        for t in (r[1], r[4]):
            if t and needle in t.lower():
                hits[t] += 1
    if not hits:
        print(f"no class in the reference models matches {needle!r}")
        print("-> next step: search ontology.brickschema.org, then extend under para:")
        return
    for term, n in hits.most_common(30):
        print(f"{n:6d}  {term}")


def cmd_template(header, rows, cls: str):
    """The parts, points and properties a class of equipment normally carries."""
    instances = {r[0] for r in rows if r[1] == cls}
    if not instances:
        print(f"no instance of {cls} in the reference models")
        return
    print(f"{len(instances)} instances of {cls} in the reference model\n")

    parts, points, props = collections.Counter(), collections.Counter(), collections.Counter()
    for r in rows:
        if r[0] not in instances:
            continue
        if r[2] == "brick:hasPart":
            parts[r[4]] += 1
        elif r[2] == "brick:hasPoint":
            points[r[4]] += 1
        elif r[3] == "<blanknode>":
            props[r[2]] += 1

    for title, counter in (("PARTS (brick:hasPart)", parts),
                           ("POINTS (brick:hasPoint)", points),
                           ("PROPERTIES (blank node)", props)):
        if not counter:
            continue
        print(f"--- {title}")
        for term, n in counter.most_common(40):
            coverage = f"{n / len(instances):.0%}" if instances else ""
            print(f"  {coverage:>5} of instances   {term}")
        print()

    example = sorted(instances)[0]
    print(f"--- a worked example: {example}")
    for r in rows:
        if r[0] == example:
            print("   " + render(header, r, 200))


def cmd_entity(header, rows, name: str):
    hits = [r for r in rows if name in (r[0], r[3])]
    if not hits:
        print(f"{name} is not in the reference models")
        return
    for r in hits:
        print(render(header, r))


def cmd_term(term: str):
    vocab = DATA / "brick-vocab.txt"
    needle = term.lower()
    found = False
    if vocab.exists():
        for line in vocab.read_text().splitlines():
            if line.startswith("#") or needle not in line.lower():
                continue
            parts = line.split("\t")
            status = parts[1] if len(parts) > 1 else ""
            note = parts[2] if len(parts) > 2 else ""
            print(f"  {parts[0]:60} {status} {note}")
            found = True
    for name in ("para-classes.csv", "para-properties.csv"):
        path = DATA / name
        if not path.exists():
            continue
        with open(path, newline="") as fh:
            for row in list(csv.reader(fh))[1:]:
                if row and needle in row[0].lower():
                    print(f"  {row[0]:60} PARA  subClassOf {row[1]}")
                    found = True
    if not found:
        print(f"{term!r} matches nothing in Brick 1.4 or the para registry")
        print("-> it needs a new para: subclass; pick the closest Brick parent")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--model", type=Path, default=PRIMARY, help="reference model to search")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--class", dest="klass", help="find a class by fuzzy name")
    g.add_argument("--template", help="show the standard shape of one equipment class")
    g.add_argument("--entity", help="show every row mentioning one entity")
    g.add_argument("--term", help="check a term against Brick 1.4 and the para registry")
    args = ap.parse_args()

    if args.term:
        cmd_term(args.term)
        return 0

    if not args.model.exists():
        sys.exit(f"reference model not found: {args.model}")
    header, rows = load(args.model)

    if args.klass:
        cmd_class(rows, args.klass)
    elif args.template:
        cmd_template(header, rows, args.template)
    else:
        cmd_entity(header, rows, args.entity)
    return 0


if __name__ == "__main__":
    sys.exit(main())
