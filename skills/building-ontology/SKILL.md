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

0. **Two conventions to settle before any row is written: whether to keep the
   identifiers the source already carries or normalise them to the PARA
   convention, and whether labels carry the source text verbatim (the QF SSC
   style) or are cleaned by the PARA label rule.** On identifiers: Room schedules and asset registers usually
   arrive with identifiers assigned, and those strings are the join key to SCADA
   and to every other sheet on the project. Default to keeping them; ask before
   writing a row, because re-identifying a finished sheet means regenerating it.
1. Building name
2. Levels
3. Rooms and spaces - names, numbers, tags or IDs
4. Equipment
5. Location of each piece of equipment
6. What each piece of equipment feeds, and what feeds it
7. **IO lists** - equipment carries data points, and the IO list is where the
   point names, signal types, units and telemetry IDs come from. Ask for it
   before modelling any points. No IO list means no points for that equipment.
8. **Manufacturer standards and datasheets** - the source of nameplate
   properties: rated power, voltage, phase count, capacity, flow rates, head,
   model number, manufacturer. **Leave the property out when the datasheet was
   not submitted.** An empty cell is recoverable; a guessed rating is not.

Most of this arrives as spreadsheets, and several facts are usually packed into
one identifier. `entity:QNL_B_063_PLANT_ROOM_01` carries building `QNL`, level
`B` (basement), room ID `063` and room name `PLANT ROOM 01`.

**Ask about anything in the source that reads like a contradiction, before
writing rows rather than in the handover note.** The recurring one: an asset
whose level token disagrees with the level of the room it is tagged against. That
is usually a double-height or open-roof space, where the unit hangs a level above
what it conditions and `rec:locatedIn` and `rec:feeds` correctly name the same
room - but it can equally mean the room column is the served space only. One
question decides which sheet you write. See `references/intake.md`.

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

**Step 4 applies to points only.** If the orphan is a piece of equipment, stop
and ask the user which root to put it under. Do not guess, and do not file
equipment under `brick:Point` to make the row validate.

Never invent a `brick:` or `rec:` term. Anything the team coins is `para:`.

## 2. Build the sheet in layers

Each layer is complete before the next one starts. Keep rows grouped by layer so
review is tractable.

| Layer | What goes in | Detail |
|---|---|---|
| Spatial | Site, Building, Levels, Parent Zones, HVAC Zones, Rooms | `references/relationships.md` |
| Systems | HVAC, Electrical, Water - the systems equipment belongs to | |
| Equipment | Type, `rec:locatedIn`, `brick:isPartOf` its system, nameplate properties from the manufacturer datasheet | |
| Feeds | `rec:feeds` / `rec:isFedBy` across the distribution chain | below |
| Parts | `brick:hasPart` down to where points attach | |
| Points | `brick:hasPoint` + class + `rdfs:label_en` + `brick:hasUnit`, from the IO list | |
| References | `ref:hasExternalReference`, one row per reference: `ref:IFCReference` carrying `para:IFC_ID` and `ref:ifcName`, `ref:TimeseriesReference` carrying `ref:hasTimeseriesId` and `para:hasEntityId` | `references/csv-contract.md` |
| Extensions | every `para:` class the sheet introduced, defined at the top | |

**The feeds rule: when equipment feeds a room, the `rec:feeds` object must be
that room.** Not a placeholder, not a representative room, not the zone when the
room is known. A terminal unit - VAV, FCU, PIM, CRAC, exhaust fan - with no
`rec:feeds` is an incomplete model, and the validator fails it (`E-FEED-1`).
The QF SSC draft breaks this rule throughout; do not copy it.

## 3. Naming and labels

**Identifiers the source supplies are kept as the source wrote them**, unless the
user asked for normalisation - see the first section of
`references/naming-and-labels.md`. Strip whitespace; change nothing else.

Identifiers this sheet has to invent - site, building, levels, systems, parts,
points - follow the PARA convention exactly. Dashes separate words inside a
segment, underscores separate segments, no spaces anywhere, case is significant.

Labels come in two styles and **the user picks one at intake** - neither
reference model settles it. `verbatim` carries the source text as written, the
QF SSC house style: `1.001_CORRIDOR`, `SSC_FCU0001`. `para` applies the label
rule - **letters, digits and spaces, and a decimal point between two digits;
every other punctuation mark is removed** - so `1.001_CORRIDOR` becomes
`1.001 CORRIDOR` and `Coefficient of Performance (COP)` becomes
`Coefficient of Performance COP`. Run the validator with the matching
`--label-style` and name the choice in the handover.

## 4. Validate before handing over

```
python3 scripts/validate_ontology.py MyBuilding.xlsx
python3 scripts/validate_ontology.py MyBuilding.xlsx --label-style verbatim
```

Pass `--label-style verbatim` when the user chose source-verbatim labels; it
turns `E-LBL-1` off and leaves every other rule in force.

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
