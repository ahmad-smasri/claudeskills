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

## Scope: build what was asked for, and no more

**If the user named what to create, create exactly that.** A request for the
spatial hierarchy is not an invitation to model the chiller plant; a request for
AHUs does not extend to the VAVs they feed. Extra rows are not a bonus - they are
unreviewed content in a deliverable someone has to check.

**If the user did not narrow the scope, build everything the building requires**:
the full spatial hierarchy, every asset in the register, its parts, its points,
its references and its extensions.

When the requested scope leaves an obvious gap - AHUs modelled but nothing to
receive their air - finish what was asked, then say what is missing and let the
user decide.

## 0. Intake, before writing any rows

Read every source the user supplied, then run `references/intake.md` and ask for
what is missing. Eight inputs are needed, and every one of them comes from the
user:

1. Building name, and the **site entity the client already uses**
2. Levels
3. Rooms and spaces - names, numbers, tags or IDs
4. Equipment
5. Location of each piece of equipment
6. What each piece of equipment feeds, and what feeds it
7. **IO lists** - equipment carries data points, and the IO list is where the
   point names, signal types, units and telemetry IDs come from. Ask for it
   before modelling any points. No IO list means no points for that equipment
8. **Manufacturer standards and datasheets** - the source of nameplate
   properties: rated power, voltage, phase count, capacity, flow rates, head,
   model number, manufacturer. **Leave the property out when the datasheet was
   not submitted.** An empty cell is recoverable; a guessed rating is not

Two conventions have to be settled in the same message, because both are
expensive to change once rows exist: whether **identifiers** keep the form the
source gave them or are normalised to the PARA convention, and whether **labels**
carry the source text verbatim (the QF SSC style) or are cleaned by the PARA
label rule. `references/naming-and-labels.md` has the wording for both.

## Ask. Do not resolve a confusion on your own.

**Anything you cannot settle from the sources is a question for the user, asked
before the rows are written and not explained in the handover note afterwards.**
A one-line question costs a reply; a wrong assumption silently corrupts every row
that depends on it, and the sheet still validates clean. This applies to every
confusion, not only the recurring ones below.

The ones that come up on every building, all worked through in
`references/intake.md`:

- **A packed identifier whose segment order is not obvious.** Ask the user to
  decode one example. Ask about unfamiliar abbreviations at the same time - they
  become `rdfs:label_en` values, and a wrong expansion is visible to end users.
- **Identifiers that do not all follow one shape.** Read the whole column, work
  out the majority shape, list the departures, ask whether to regularise.
- **An asset whose level disagrees with the level of the room it is tagged
  against.** Usually a double-height or open-roof space, where the unit hangs a
  level above what it conditions and `rec:locatedIn` and `rec:feeds` correctly
  name the same room - but it can equally mean the room column is the served
  space only.
- **An IO list whose point names do not obviously map onto the equipment
  entities.** Never guess the join. Ask which column is the telemetry key and
  which the point name; `scripts/check_io_list.py` stops and says so rather than
  matching on a guess.
- **A source column whose meaning is ambiguous** - one room column serving as
  both location and served space, a type prefix disagreeing with a class column,
  rooms in one sheet but not the other.

## 1. Resolve every class through the ladder

For every piece of equipment, part and point, in this order - see
`references/class-resolution.md`:

1. **Is it in Dar Cairo?** `scripts/lookup_reference.py --class "booster pump"`.
   If yes, reuse that exact class. Dar Cairo is the primary reference.
2. **Is it in Brick?** `scripts/lookup_reference.py --term Heat_Wheel`, or search
   <https://ontology.brickschema.org>. Use the preferred class, never an alias.
3. **Is it in a previous project's ontology?** Check the other delivered project
   sheets - `reference-models/QF_SSC_Ontology_*.xlsx` first. If a prior project
   already classed this concept, reuse that class. This is where a `para:` class
   the team already coined gets reused instead of minted a second time - always
   reuse the prior name rather than inventing a parallel one.
4. **Not anywhere above?** Define a `para:` subclass of the closest Brick parent.
5. **No sensible parent either?** Define a new `owl:Class` as
   `rdfs:subClassOf brick:Point`. Dar Cairo has precedent for this shape too.

**Step 5 applies to points only.** If the orphan is a piece of equipment, stop
and ask the user which root to put it under. Do not guess, and do not file
equipment under `brick:Point` to make the row validate.

Never invent a `brick:` or `rec:` term. Anything the team coins is `para:` - and
a `para:` class already used by a previous project is reused, never re-coined.

## 2. Build the sheet in layers

Each layer is complete before the next one starts. Keep rows grouped by layer so
review is tractable.

| Layer | What goes in | Detail |
|---|---|---|
| Spatial | Site, Building, Levels, Parent Zones, HVAC Zones, Rooms | `references/relationships.md` |
| Systems | the system tree the front end renders: a top-level system per discipline, sub-systems below it, and every asset pointing up | `references/relationships.md` |
| Equipment | Type, `rec:locatedIn`, `brick:isPartOf` its system, nameplate properties from the manufacturer datasheet | |
| Feeds | `rec:feeds` / `rec:isFedBy` across the distribution chain | below |
| Parts | `brick:hasPart` down to where points attach | |
| Points | `brick:hasPoint` + class + `rdfs:label_en` + `brick:hasUnit`, **from the IO list and nowhere else** | below |
| References | `ref:hasExternalReference`, one row per reference. `ref:IFCReference` on the physical thing, carrying `para:IFC_ID` and `ref:ifcName`. `ref:TimeseriesReference` **on the point, never on the equipment**, carrying `ref:hasTimeseriesId` and `para:hasEntityId` | `references/csv-contract.md` |
| Extensions | every `para:` class the sheet introduced, defined at the top | |

**The feeds rule: when equipment feeds a room, the `rec:feeds` object must be
that room.** Not a placeholder, not a representative room, not the zone when the
room is known. A terminal unit - VAV, FCU, PIM, CRAC, exhaust fan - with no
`rec:feeds` is an incomplete model, and the validator fails it (`E-FEED-1`).

**The systems layer is what the front end's tree is built from**, so it is not
optional decoration - see `references/relationships.md` for the row shapes.
Declare each system before the equipment that points at it, and **only declare a
system that earns its place**: a node whose only child is one asset costs the
user a click and tells them nothing. QNL declares `entity:HVAC` and stops,
because a `CHW-System` beneath it would hold the loop and nothing else.

**The points rule: every point traces back to a row in the IO list.** A point the
BMS does not publish resolves to an empty timeseries - the front end draws a tile
with no data behind it, and nobody can tell whether the sensor is broken or was
never real. Over-inclusion is worse than omission here. Cross-check with
`scripts/check_io_list.py` before handover, and never infer a point list from the
equipment type.

## 3. Naming and labels

**Identifiers the source supplies are kept as the source wrote them**, unless the
user asked for normalisation - see the first section of
`references/naming-and-labels.md`. Strip whitespace; change nothing else.

Identifiers this sheet has to invent - site, building, levels, systems, parts,
points - follow the PARA convention exactly. Dashes separate words inside a
segment, underscores separate segments, no spaces anywhere, case is significant.

Labels come in two styles and **the user picks one at intake** - neither
reference model settles it. `verbatim` carries the source text with underscores as spaces and
everything else untouched, the QF SSC house style: `1.001 CORRIDOR`,
`B.063 PLANT ROOM 01`. `para` applies the label
rule - **letters, digits and spaces, and a decimal point between two digits;
every other punctuation mark is removed** - so `1.001_CORRIDOR` becomes
`1.001 CORRIDOR` and `Coefficient of Performance (COP)` becomes
`Coefficient of Performance COP`. Run the validator with the matching
`--label-style` and name the choice in the handover.

## 4. Validate before handing over

Two passes, and both matter. Neither writes anything into the sheet.

```
python3 scripts/validate_ontology.py MyBuilding.xlsx --preflight
python3 scripts/validate_ontology.py MyBuilding.xlsx --label-style verbatim
python3 scripts/check_consistency.py MyBuilding.xlsx
python3 scripts/check_io_list.py MyBuilding.xlsx --io IO_List.xlsx
```

**`--preflight` first.** It prints what the sheet actually contains - prefixes,
classes by kind, predicates, properties, units - and stops. Read it and confirm
the picture before trusting a single finding: a sheet can validate clean and
still model the wrong building. Nothing downstream carries one building's facts
into another; every rule runs against what preflight found.

**`validate_ontology.py` reads one row at a time.** Header contract, prefixes,
whitespace, unresolved `<placeholder>` cells, label punctuation,
one-type-per-entity, Brick 1.4 term existence, deprecated and alias terms, units,
blank-node shape, spatial connectivity, terminal units with no feeds, points with
no external reference. Pass `--label-style verbatim` when the user chose
source-verbatim labels; it turns `E-LBL-1` off and leaves every other rule in
force.

**`check_consistency.py` puts every unit of a class beside its siblings.** That
is where the defects a row-level read cannot see live: the FCU missing a point
its 136 siblings all have, the VAV whose status is typed differently from every
other VAV, the `#N/A` a lookup formula left in an object column, the child whose
identifier drifted one separator from its parent's. It infers the families, what
a complete unit looks like in each, and what each predicate's object should be,
all from the sheet - there is no expected point list to keep up to date. Codes
are `-CON-` and are explained in `references/known-issues.md`.

Run it on a family at a time while building (`--family brick:Fan_Coil_Unit`), and
on the whole sheet before handover.

**`check_io_list.py` compares the sheet's points against the IO list they came
from**, in both directions: a point with no IO row (`E-IO-1`) would resolve to an
empty timeseries and must come out; an IO row with no point (`W-IO-2`) is usually
a scope decision worth confirming. It matches on the telemetry id, falls back to
the point name, and **stops and asks rather than guessing** when it cannot tell
which column of the IO list is which.

**Pass `--io` to the other two as well, and they use the list as evidence rather
than reporting round it.** A point with no timeseries reference is a defect if
the BMS publishes a key for it and a fact if it does not; a point on 4 of 10
units is a defect if the other 6 should have it and a fact if they never did.
With the list to hand those findings are resolved and reported as confirmed -
`E-CON-1` becomes `I-CON-1`, `E-CON-2` becomes `I-CON-2`, `W-CON-9` becomes
`I-CON-9`, `W-PT-1` becomes `I-PT-3` - and where the list says a key exists that
the sheet is missing, the finding is promoted instead (`E-PT-4`, `E-CON-18`).
Silence is not confirmation: a unit the list says nothing about leaves its
finding standing.

**When findings need a human, hand them the sheet, not a report.**

```
python3 scripts/highlight_findings.py In.xlsx --out Reviewed.xlsx --label-style verbatim
```

writes a copy with every still-flagged row filled `#FFFF00`, the finding written
into two columns past the data - `validator_code` and `validator_finding`, so it
can be read, sorted and filtered - and the full text on a cell comment for rows
carrying several. The reviewer works where the data is. **Delete both columns and
the fills before handover**: the deliverable holds triples and nothing else. File-level
findings - a type clash, a terminal unit with no feeds - are placed on the
entity's **defining row only**: marking every row an entity owns paints hundreds
of cells yellow for a handful of findings and buries the ones that point at a
single cell. It writes a copy, adds no sheet, and never touches the input. Clear
the fills before handover.

**Neither of the two checkers writes to the ontology workbook.** Findings go to stdout, or to
a file of their own with `--report findings.xlsx`. The deliverable stays one
sheet of triples: a converter that meets a second sheet has to be told which one
to read, and a reviewer diffing two versions has to skip it.

`.xlsx` input needs `openpyxl`; `.csv` input needs nothing beyond the standard
library.

Fix every `ERROR` from both scripts. Read every `WARN` and either fix it or be
able to say why it stands. `INFO` lines are advisories - a valid Brick term with
no precedent in Dar Cairo, a class with only one instance, a `rec:feeds` target
that equals `rec:locatedIn`. Worth a second look and a line in the handover, not
a defect.

## 5. Deliver

Ship the `.xlsx` with the 27-column header from `assets/ontology-template.csv`,
plus a crosswalk file (`source_identifier, ontology_identifier, label`) whenever
any identifier changed shape, plus a short note listing: whether source
identifiers were kept or normalised and which label style was used, every new `para:` class proposed for review, every
property left empty for want of a datasheet, every piece of equipment with no IO
list and therefore no points, anything deliberately left out because it was
outside the requested scope, and the validator's remaining warnings with reasons.

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
| `scripts/validate_ontology.py` | Validates a sheet row by row |
| `scripts/highlight_findings.py` | Writes a copy with unresolved findings filled yellow, for a manual pass |
| `scripts/check_consistency.py` | Compares every unit of a class against its siblings |
| `scripts/build_vocab.py` | Rebuilds the para registry after a new reference model lands |
| `scripts/build_brick_vocab.py` | Rebuilds the Brick 1.4 term list from `Brick.ttl` |
| `tests/run_tests.sh` | Checks the validator still catches what it should |

`assets/ontology-template.csv` is the empty 27-column header.
`assets/example-minimal.csv` is a small complete building - site through
building, level, zone, room, AHU, VFD, a terminal unit feeding its room, points,
timeseries references, an aggregation and two `para:` classes - that validates
clean. Copy its shapes rather than reinventing them.

`reference-models/` holds the source of truth: `DarCairo_V93.csv` (primary),
`QF_SSC_Ontology_ver02.xlsx` (the cleaned SSC delivery, 5,082 rows, 17 errors -
the step-3 previous-project reference in the class ladder) and
`Ontology_headers.xlsx` (the 9 canonical column names).
