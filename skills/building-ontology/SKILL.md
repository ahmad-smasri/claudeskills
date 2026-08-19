---
name: building-ontology
description: Author a PARA/Brick building ontology spreadsheet - the 9-column CSV/Excel of triples that the backend converts to .ttl. Use when asked to build, extend, review or validate a building ontology, a Brick model, a BrickSchema CSV, or an ontology sheet for a building, and when turning room schedules, asset registers, or BMS point lists into ontology rows.
---

# Building an ontology sheet

The deliverable is one spreadsheet. **Every row is one RDF triple**, plus optional
metadata attached to the subject and the object. The backend team converts it to
Turtle; the front end reads the labels; the 3D viewer reads the IFC references.

Work in this order. Do not skip the intake step - most bad sheets come from
guessing at inputs rather than from getting the modelling wrong.

## 0. Intake, before writing any rows

Read every source the user supplied, then run `references/intake.md` and ask for
what is missing. Six things are always needed:

1. Building name
2. Levels
3. Rooms and spaces - names, numbers, tags or IDs
4. Equipment
5. Location of each piece of equipment
6. What each piece of equipment feeds, and what feeds it

Most of this arrives as spreadsheets, and several facts are usually packed into
one identifier. `entity:QNL_B_063_PLANT_ROOM_01` carries building `QNL`, level
`B` (basement), room ID `063` and room name `PLANT ROOM 01`.

**When an identifier's structure is not obvious, ask the user to decode one
example rather than guessing.** Guessing the segment order silently corrupts
every room row. Ask about unfamiliar abbreviations at the same time - they become
`rdfs:label_en` values, and a wrong expansion is visible to end users.

## 1. Resolve every class through the ladder

For every piece of equipment, part and point, in this order - see
`references/class-resolution.md`:

1. **Is it in Dar Cairo?** `scripts/lookup_reference.py --class "booster pump"`.
   If yes, reuse that exact class. Dar Cairo is the primary reference.
2. **Is it in Brick?** `scripts/lookup_reference.py --term Heat_Wheel`, or search
   <https://ontology.brickschema.org>. Use the preferred class, never an alias.
3. **Not in Brick?** Define a `para:` subclass of the closest Brick parent.
4. **No sensible parent either?** Define a new `owl:Class` as
   `rdfs:subClassOf brick:Point`. Dar Cairo has precedent for this shape too.
   If the orphan is equipment rather than a point, stop and ask - `brick:Point`
   is the wrong root for it.

Never invent a `brick:` or `rec:` term. Anything the team coins is `para:`.

## 2. Build the sheet in layers

Each layer is complete before the next one starts. Keep rows grouped by layer so
review is tractable.

| Layer | What goes in | Detail |
|---|---|---|
| Spatial | Site, Building, Levels, Parent Zones, HVAC Zones, Rooms | `references/relationships.md` |
| Systems | HVAC, Electrical, Water - the systems equipment belongs to | |
| Equipment | Type, `rec:locatedIn`, `brick:isPartOf` its system, nameplate properties | |
| Feeds | `rec:feeds` / `rec:isFedBy` across the distribution chain | below |
| Parts | `brick:hasPart` down to where points attach | |
| Points | `brick:hasPoint` + class + `rdfs:label_en` + `brick:hasUnit` | |
| References | `ref:hasExternalReference` for timeseries IDs and IFC names | |
| Extensions | every `para:` class the sheet introduced, defined at the top | |

**The feeds rule: when equipment feeds a room, the `rec:feeds` object must be
that room.** Not a placeholder, not a representative room, not the zone when the
room is known. A terminal unit - VAV, FCU, PIM, CRAC, exhaust fan - with no
`rec:feeds` is an incomplete model, and the validator fails it (`E-FEED-1`).
The QF SSC draft breaks this rule throughout; do not copy it.

## 3. Naming and labels

Identifiers follow the PARA convention exactly - `references/naming-and-labels.md`.
Dashes separate words inside a segment, underscores separate segments, no spaces
anywhere, case is significant.

Labels are the one place spaces are allowed. **A label may contain letters,
digits and spaces, and a decimal point between two digits. Every other
punctuation mark is removed.** `1.001_CORRIDOR` becomes `1.001 CORRIDOR`;
`Coefficient of Performance (COP)` becomes `Coefficient of Performance COP`.

## 4. Validate before handing over

```
python3 scripts/validate_ontology.py MyBuilding.xlsx
```

`.xlsx` input needs `openpyxl`; `.csv` input needs nothing beyond the standard
library.

Fix every `ERROR`. Read every `WARN` and either fix it or be able to say why it
stands. `INFO` lines flag valid Brick terms with no precedent in Dar Cairo -
worth a second look, not a defect. Rule codes are explained in
`references/known-issues.md`.

The validator checks the header contract, prefixes, whitespace, unresolved
`<placeholder>` cells, label punctuation, one-type-per-entity, Brick 1.4 term
existence, deprecated and alias terms, units, blank-node shape, spatial
connectivity, terminal units with no feeds, and points with no external
reference.

## 5. Deliver

Ship the `.xlsx` with the 27-column header from `assets/ontology-template.csv`,
plus a short note listing: every new `para:` class proposed for review, every
input that was assumed rather than supplied, and the validator's remaining
warnings with reasons.

New `para:` classes are reviewed by the PARA team before they enter the shared
extension `.ttl`. Flag them explicitly - do not let them arrive unannounced.

## Reference files

| File | Read it when |
|---|---|
| `references/intake.md` | Starting a building; deciding what to request |
| `references/csv-contract.md` | Unsure which column a value belongs in |
| `references/naming-and-labels.md` | Naming an entity or writing a label |
| `references/relationships.md` | Choosing a predicate |
| `references/class-resolution.md` | A class is missing or ambiguous |
| `references/known-issues.md` | A rule code needs explaining, or the sources disagree |

| Script | Does |
|---|---|
| `scripts/lookup_reference.py` | Finds precedent in Dar Cairo; checks a term against Brick 1.4 |
| `scripts/validate_ontology.py` | Validates a sheet |
| `scripts/build_vocab.py` | Rebuilds the para registry after a new reference model lands |
| `scripts/build_brick_vocab.py` | Rebuilds the Brick 1.4 term list from `Brick.ttl` |
| `tests/run_tests.sh` | Checks the validator still catches what it should |

`assets/ontology-template.csv` is the empty 27-column header.
`assets/example-minimal.csv` is a small complete building - site through
building, level, zone, room, AHU, VFD, a terminal unit feeding its room, points,
timeseries references, an aggregation and two `para:` classes - that validates
clean. Copy its shapes rather than reinventing them.

`reference-models/` holds the source of truth: `DarCairo_V93.csv` (primary),
`QF_SSC_Ontology_draft0.4.xlsx` (recent sample, has known defects) and
`Ontology_headers.xlsx` (the 9 canonical column names).
