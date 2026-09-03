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
   sheets - `reference-models/QF_SSC_Ontology_*.xlsx` and `QF_HQ_Ontology_*.xlsx`.
   If a prior project
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
| Metering | virtual meters, if the client asked for them: the tier matrix, the six-row block per meter, `para:contributionFraction` on AHU-fed terminal units | `references/virtual-meters.md` |
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

**Virtual meters are asked for, never assumed** - see
`references/virtual-meters.md`. Which tiers (Building, Floor, Room) and which
meter types at each is the client's call, and the count follows from it as
arithmetic: room tier on a 354-room building is 1,440 meters, so say the total
back before building. Their points are *calculated*, so the IO-list rule below
does not reach them - the keys come from the calculation engine's register, and
where that does not exist yet the points ship with no reference row and a pending
file, never with a blank one.

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

**Datapoints are named in dashed English, the Dar Cairo way** - `_Trip-Status`,
`_Room-Air-Temperature-Setpoint`, never the BMS token `_TripAlm` or `_RmTempSP`.
Take the name from the point's `rdfs:label_en` when it is clean English, else from
its Brick/para class (`brick:Run_Status` → `Run-Status`); no camelCase, no dots.
A part of a part extends the parent segment with `-` (`_SF-Motor`); a point opens
a new `_` segment. Name ids this way as you emit them - see
`references/naming-and-labels.md`. When a sheet was already built with raw/BMS
identifiers, `scripts/align_naming.py` retrofits the whole sheet in one pass,
keeping the timeseries join keys and writing an old → new crosswalk.

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

**`--preflight` first.** It prints what the sheet contains - prefixes, classes by
kind, predicates, properties, units - and stops. Confirm the picture before
trusting a finding: a sheet can validate clean and still model the wrong building.

- **`validate_ontology.py`** reads one row at a time - header contract, prefixes,
  whitespace, placeholders, label punctuation, one-type-per-entity, Brick 1.4
  term existence, deprecation, units, blank-node shape, spatial connectivity,
  terminal units with no feeds, points with no reference. `--label-style verbatim`
  turns `E-LBL-1` off, every other rule stays.
- **`check_consistency.py`** puts every unit of a class beside its siblings and
  finds what a row read cannot - a missing point, a divergent type, a `#N/A` in an
  object cell, a child whose separators drifted. Run it per family while building
  (`--family ...`) and whole before handover. Codes `-CON-`.
- **`check_io_list.py`** compares the sheet's points against the IO list both ways:
  a point with no IO row (`E-IO-1`) must come out; an IO row with no point
  (`W-IO-2`) is a scope call. It stops and asks rather than guess the join column.
- **Pass `--io` to the other two** and they use the list as evidence - a finding
  the list settles is downgraded to `I-`, one the list contradicts is promoted.
  Silence is not confirmation.

Every rule code is explained in `references/known-issues.md`. Fix every `ERROR`;
read every `WARN` and fix it or say why it stands; `INFO` lines are advisories
worth a handover line, not defects.

**When findings need a human, hand them the sheet:**
`scripts/highlight_findings.py In.xlsx --out Reviewed.xlsx --label-style verbatim`
writes a copy with each still-flagged row filled yellow and the finding in two
columns past the data (file-level findings on the entity's defining row only).
**Delete those columns and the fills before handover** - the deliverable holds
triples and nothing else. Neither checker writes to the workbook; findings go to
stdout or `--report`. `.xlsx` needs `openpyxl`; `.csv` needs nothing extra.

## 4b. The assumption log - every departure from the source is recorded

**Every assumption, correction or departure from what a source literally says goes
in the assumption log** - a deliverable in its own right, what lets a reviewer see
months later why the sheet differs from the register they hold.

One workbook for the estate, `Assumption_Log.xlsx`, **one sheet per building**
(`SSC`, `HQ`, `QNL`, …), columns `ID · Date · Category · Layer · Entity/Scope ·
What the source says · What we did · Why/basis · Rows affected`. Categories:
`Identifier`, `Location`, `Units`, `Spelling`, `Class`, `Structure`, `Scope`,
`Source defect`. It is **hand-maintained** in Excel; `projects/format_assumption_log.py`
only propagates the shared format (`--add <NAME>` scaffolds a new building's sheet),
never row content.

Log anything where the sheet and the source diverge: a unit changed and why the
class outranked it; a spelling/separator corrected with the sibling that proves
it; an identifier reshaped, prefixed or invented; a class chosen against precedent
or a `para:` coined; a deprecated term kept; anything left out and what it waits
on; a defect found in a source even where it changed nothing.

### Rule 1: model what the sources disagree about, then log it

A source disagreement is never a reason to silently drop an entity. Model it, assert
only what is actually known, and record the gap:

| The source says | What to do |
|---|---|
| The asset has datapoints but **no location** (in the point sources, absent from the asset register) | Write `rec:locatedIn` the **building** and `brick:isPartOf` its **system** - two rows that assert only what is actually known, since the asset is certainly in the building and certainly on that system. Write **no** `rec:feeds` and no room-level location: the served space is the part nobody knows, and a guess there is invented survey. Dar Cairo has precedent for building-level location (36 entities). Log it; the remaining `E-FEED-1` is an accepted finding. **Applies to standalone equipment only** - a part inherits its parent's location, and Dar Cairo locates only 19 of its 801 parts separately. |
| The asset is **in the register and the historian but the selected-points sheet omits it** | Take its points from the historian. Let the family's own selected signature decide which ones, so the unit matches its siblings rather than carrying a set nothing else in the family has. Log it. |
| A source column is **internally inconsistent or misaligned** | Use the columns that agree with each other, say so in the log, and tell the source owner. Never reconstruct a corrupted column by guesswork. |

The principle underneath all three: **omission is invisible, an assumption in the log
is reviewable.** A dropped asset looks identical to an asset that never existed.

## 5. Deliver

Ship the `.xlsx` with the 27-column header from `assets/ontology-template.csv`,
plus a crosswalk file (`source_identifier, ontology_identifier, label`) whenever
any identifier changed shape, plus a short note listing: whether source
identifiers were kept or normalised and which label style was used, every new `para:` class proposed for review, every
property left empty for want of a datasheet, every piece of equipment with no IO
list and therefore no points, anything deliberately left out because it was
outside the requested scope, and the validator's remaining warnings with reasons.

Ship the building's sheet of `Assumption_Log.xlsx` with it. The handover note
summarises; the log is the itemised record, and the two must not disagree.

New `para:` classes are reviewed by the PARA team before they enter the shared
extension `.ttl`. Flag them explicitly - do not let them arrive unannounced.

## Reference files

| File | Read it when |
|---|---|
| `references/intake.md` | Starting a building; deciding what to request |
| `references/csv-contract.md` | Unsure which column a value belongs in |
| `references/naming-and-labels.md` | Naming an entity or writing a label |
| `references/relationships.md` | Choosing a predicate |
| `references/virtual-meters.md` | Adding a virtual metering layer, or `para:contributionFraction` |
| `references/class-resolution.md` | A class is missing or ambiguous |
| `references/known-issues.md` | A rule code needs explaining, or the sources disagree |

| Script | Does |
|---|---|
| `scripts/lookup_reference.py` | Finds precedent in Dar Cairo; checks a term against Brick 1.4 |
| `scripts/align_naming.py` | Retrofits a sheet's identifiers to Dar Cairo's convention (dashed-English datapoints, `_`-segments/`-`-words), keeping the timeseries join keys; one-shot |
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

`reference-models/` holds the source of truth: `DarCairo_V98.csv` (primary),
`QF_SSC_Ontology_ver02.xlsx` and `QF_HQ_Ontology_draft0.4.xlsx` (the two
delivered previous-project ontologies - the step-3 reference in the class ladder;
read HQ for structure, not units, and pick its sheet by header not by its
misspelled tab name) and `Ontology_headers.xlsx` (the 9 canonical column names).
