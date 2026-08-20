# CLAUDE.md

Read this file first. It maps everything in the repo and states the rules that
are already settled, so a session does not have to re-read the source documents
to start work.

## What this repo is for

Building ontologies. The deliverable for any project is **one spreadsheet of RDF
triples** - the PARA/Brick CSV or Excel that the backend team converts to `.ttl`,
the front end reads labels from, and the 3D viewer reads IFC references from.
Every row is one triple.

The work is done through `skills/building-ontology`. Invoke that skill for any
ontology task; this file is the index, the skill is the procedure.

## File map

### The skill - `skills/building-ontology/`

| Path | What it holds | Open it when |
|---|---|---|
| `SKILL.md` | the workflow, scope rule, class ladder, feeds rule, label rule | always, first |
| `references/intake.md` | the 8 mandatory inputs, how to ask for them, decoding packed identifiers | starting a building, or something is missing |
| `references/csv-contract.md` | the 9 columns, the 27-column layout, six row shapes, property names, units | unsure which column a value belongs in |
| `references/naming-and-labels.md` | identifier patterns per level, character rules, the label rule, IFC references | naming anything |
| `references/relationships.md` | predicate families, what Dar Cairo actually uses and how often, the spatial hierarchy, feeds, hasPart vs locatedIn | choosing a predicate |
| `references/class-resolution.md` | the four-step ladder, extension rules, where the vocabularies come from | a class is missing or ambiguous |
| `references/known-issues.md` | all 30 validator rule codes, 9 source conflicts with the resolution taken, defect inventories for both reference models | a code needs explaining, or the sources disagree |
| `references/data/brick-vocab.txt` | 2,587 Brick 1.4 / REC / ref terms with deprecation and alias status | generated - do not hand-edit |
| `references/data/brick-rec-vocab.txt` | the 193 terms with actual precedent in Dar Cairo | generated |
| `references/data/para-classes.csv` | 228 `para:` classes and their parents | generated |
| `references/data/para-properties.csv` | 13 `para:` entity properties | generated |
| `references/data/units.csv` | 41 units seen with `brick:hasUnit`, with usage counts | generated |
| `assets/ontology-template.csv` | the empty 27-column header | starting a sheet |
| `assets/example-minimal.csv` | a small complete building that validates clean - copy its shapes | writing any row shape for the first time |
| `scripts/lookup_reference.py` | precedent search over Dar Cairo; Brick 1.4 term check | before inventing any class |
| `scripts/validate_ontology.py` | the row-level validator, 30 rule codes | before every handover |
| `scripts/io_list.py` | shared IO-list loader; answers "does this unit have this point" and "what is its key" for all three checkers | changing how an IO list is read |
| `scripts/check_io_list.py` | the point cross-check, 5 `-IO-` codes: every point in the sheet must trace back to a row in the IO list, or its timeseries resolves empty | whenever an IO list exists |
| `scripts/check_consistency.py` | the cross-unit checker, 17 `-CON-` codes: compares every unit of a class against its siblings and finds what a row-level read cannot - a missing point, a divergent class, a `#N/A` in an object cell, a child whose separators drifted from its parent's | before every handover, and per family while building |
| `scripts/build_vocab.py` | regenerates the para registry and unit list from `reference-models/` | a new reference model lands |
| `scripts/build_brick_vocab.py` | regenerates the Brick term list from `Brick.ttl` | targeting a new Brick release |
| `tests/run_tests.sh` | checks both scripts still catch what they should | after touching either |

### Reference models - `reference-models/`

| File | What it is |
|---|---|
| `DarCairo_V93.csv` | **the primary reference for any ontology we build.** 26,173 rows, 27 columns. Site → building → levels → zones → rooms → HVAC, electrical, water systems → equipment → parts → points → timeseries. When in doubt, match Dar Cairo. |
| `QF_SSC_Ontology_draft0.5_review.xlsx` | the current SSC sheet, 5,119 rows, plus the `Claude Log` and nine `*_Comparison` sheets from the consistency review. **Opens on `VAV_Comparison`, not on the ontology** - pick the sheet by its header, never by `.active`. 451 validator errors, so still not a model of correctness, but its site, building, systems and chilled-water-loop rows are the current house shape. |
| `Ontology_headers.xlsx` | the nine canonical column names, nothing else |

### Source documents - repo root

| File | What it is |
|---|---|
| `PARA Ontology Workflow Documentation 11.pdf` | the in-house spec, Rev 0.0, June 2025, 19 pages. Prepared by Sara A. Medhat, reviewed by Majdi Saadeddine, approved by Faysal Shair. Background, the 9-column CSV structure, BIM naming, Ch.1 site/building/zones/equipment, Ch.2 extending Brick, Ch.3 properties and data points. Rev 0.0 contradicts itself in several places - see `known-issues.md` before trusting a passage. |
| `Ontology Webinar.pdf` | 2 pages of notes from the Brick webinar: OWL to SHACL, semantic sufficiency, BuildingMOTIF templates. Context, no rules. |
| `BrickSchema.md` | 3,117 lines of brickschema.org docs: concepts, the four relationship families, units, aliases, inference, external references, tooling |
| `ontologyprimer.md` | 657-line primer distilled from the three above. `docs/ontology-primer.md` is an identical copy. |

The skill's reference files supersede all four documents where they disagree -
they carry the resolutions.

## The settled rules

Each rule appears once. If you need the reasoning or the worked examples, the
skill's reference file named beside it carries them.

**Scope.** If the user named what to create, create exactly that and nothing
more. If they did not narrow it, build everything the building requires. Say
what was left out rather than filling it in.

**Ask; do not resolve a confusion on your own.** Anything that cannot be settled
from the sources is a question for the user, asked before the rows are written -
not explained in the handover note afterwards. A wrong assumption silently
corrupts every row that depends on it and still validates clean. The recurring
ones, all in `references/intake.md`: a packed identifier whose segment order is
not obvious (`entity:QNL_B_063_PLANT_ROOM_01` is building, level, room ID, room
name - confirm it, and get the abbreviations expanded while you are asking, since
they become labels users read); identifiers that do not all follow one shape; an
asset whose level disagrees with the level of the room it is tagged against
(usually a double-height or open-roof space, so `rec:locatedIn` and `rec:feeds`
correctly name the same room); an IO list whose point names do not obviously map
onto the equipment; any source column whose meaning is ambiguous.

**Class resolution ladder**, for every equipment, part and point:

1. Is it in Dar Cairo? `lookup_reference.py --class "..."` - reuse that exact class.
2. Is it in Brick? `lookup_reference.py --term ...` or ontology.brickschema.org -
   use the preferred class, never an alias.
3. Not in Brick? Define a `para:` subclass of the closest Brick parent.
4. No sensible parent either? For a **point**, `owl:Class rdfs:subClassOf brick:Point`.
   For **equipment, ask the user which root to use** - never guess, never file
   equipment under `brick:Point`.

Never invent a `brick:` or `rec:` term. Everything the team coins is `para:`.

**Identifiers** - `references/naming-and-labels.md`:

- Identifiers the source supplies are kept as the source wrote them; they are the
  join key to SCADA and to every other sheet. Strip whitespace, change nothing
  else. Ask at intake whether to keep or normalise; default to keeping.
- Verbatim assumes the source is internally consistent. **Audit the whole column,
  rooms and assets alike, find the majority shape, and report every departure
  before writing rows.** On QNL, 51 of 336 rooms ran the level into the room
  number where 285 kept them separate, and one asset family of four carried
  neither separators nor a level segment. Asset tags are the BMS join key, so
  expect to report rather than change them.
- **Every subject carries the building code in front** - `entity:SSC_FCU0001`,
  so `entity:QNL_FCU_1F_056`. Add the code; leave the tag itself alone.
- **The site is the organisation's code, and buildings share it** -
  `entity:SSC rec:isPartOf entity:QF`, so `entity:QNL rec:isPartOf entity:QF`,
  the building labelled `<code> Building`. Ask which site entity the client
  already uses; it is the one identifier shared across projects.
- **Systems and shared plant carry no building code** - `entity:HVAC`,
  `entity:CHW-System`, `entity:CHWS-LOOP-1` - because they serve the site or the
  building rather than sitting in it. Where a per-building asset would collide
  across sheets, prefix it and say why.
- For identifiers the sheet has to invent: dashes separate words inside a
  segment, underscores separate segments, no spaces, case is significant.
  `Dar-Cairo_Basement-3_Pump-Room_B331`.

**Labels.** Two styles; ask at intake, because neither reference model settles it.
`verbatim` keeps the source text as written - the QF SSC house style, whose room
shape is `<level>.<number>_<name>`: `1.001_CORRIDOR`, `SSC_FCU0001`. `para`
applies the label rule: letters, digits and spaces only, plus a decimal point
between two digits, every other punctuation mark removed. Pass the matching
`--label-style` to the validator; `verbatim` turns `E-LBL-1` off.

**Feeds.** When equipment feeds a room, the `rec:feeds` object is that room. Not
a placeholder, not a representative room, not the zone when the room is known.
Terminal units - VAV, FCU, PIM, CRAC, exhaust fan - must have a feeds row.

**Systems** - `references/relationships.md`. The front end's tree is built from
the `brick:isPartOf` chain here plus Brick's own class hierarchy below it. Supply
the system chain; let Brick supply the class layer - do not mint an
`entity:Air_Handling_Unit` between the two. A top-level system is a subject
carrying `brick:isPartOf` the site and a label; a sub-system is declared only as
the object of its parent's `brick:hasPart` row; equipment points up with
`brick:isPartOf`. **Only declare a system that earns its place** - a node whose
only child is one asset costs a click and tells the user nothing.

**Spatial vs system.** `rec:isPartOf` for spatial containment, `brick:isPartOf`
for system membership. Both appear in Dar Cairo and they mean different things.
Spatial classes are `rec:`, never the deprecated `brick:` location classes.

**External references.** One row per reference, and an entity can carry several.
IFC: `ref:IFCReference` with both `para:IFC_ID` (the BIM GUID) and `ref:ifcName`
(the entity name, derivable) - the QF SSC shape. Timeseries:
`ref:TimeseriesReference` with `ref:hasTimeseriesId` and `para:hasEntityId` -
**on the point, never on the equipment.**

**Points come from IO lists, and only from IO lists.** Never infer a point list
from the equipment type. No IO list means no points for that equipment, and a
line in the handover note. **Cross-check both directions before handover** with
`check_io_list.py`: a point with no IO row resolves to an empty timeseries, so
the front end draws a tile with no data behind it and nobody can tell whether the
sensor is broken or was never real. Over-inclusion is worse than omission.
**The IO list is also evidence for the other two checkers** - pass `--io` and
findings it can adjudicate are resolved rather than flagged, which is the pass a
reviewer would otherwise do by hand. Silence is not confirmation: a unit the list
says nothing about leaves its finding standing.

**Nameplate properties come from manufacturer datasheets.** Ask for them. If a
datasheet was not submitted, leave the property out - never a typical value,
never a placeholder.

**One sheet out.** The deliverable workbook holds the triples and nothing else.
Validation output never goes into it - findings print to stdout, or to a file of
their own via `--report`. A second sheet means the converter has to be told which
one to read.

## Commands worth remembering

```
# what does a complete FCU look like in Dar Cairo - parts, points, properties
python3 skills/building-ontology/scripts/lookup_reference.py --template brick:Fan_Coil_Unit

# does this term exist in Brick 1.4, and is it preferred
python3 skills/building-ontology/scripts/lookup_reference.py --term Heat_Wheel

# discover and show first - confirm the picture before trusting any finding
python3 skills/building-ontology/scripts/validate_ontology.py MyBuilding.xlsx --preflight

# validate before handover - row by row, then unit against unit, then the points
python3 skills/building-ontology/scripts/validate_ontology.py MyBuilding.xlsx
python3 skills/building-ontology/scripts/check_consistency.py MyBuilding.xlsx
python3 skills/building-ontology/scripts/check_io_list.py MyBuilding.xlsx --io IO_List.xlsx

# with an IO list to hand, let it settle the findings it can adjudicate
python3 skills/building-ontology/scripts/check_consistency.py MyBuilding.xlsx --io IO_List.xlsx

# one family at a time while building, and findings to their own file
python3 skills/building-ontology/scripts/check_consistency.py MyBuilding.xlsx \
    --family brick:Fan_Coil_Unit --report findings.xlsx

# after touching any script
skills/building-ontology/tests/run_tests.sh
```

`.xlsx` input needs `openpyxl`. `.csv` input needs nothing beyond the standard
library.

## Open questions for the PARA team

Recorded with the resolution currently followed in
`references/known-issues.md`. The ones most likely to change rows:

1. The PARA doc puts Room under HVAC Zone; Dar Cairo puts Room under a per-floor
   parent Zone and HVAC Zone under the Level. Dar Cairo is followed.
2. Chapter Two's PIM example disagrees with its own prose on prefix, name and
   parent class. The CSV form is followed, and Dar Cairo agrees.
3. `rdfs:label_en` is not standard RDFS. It is used anyway, as both reference
   models and the converter do.
4. Brick version target is 1.4; the term list is generated from the 1.4 ontology.
5. The shared `para:` extension `.ttl` has not been supplied - new classes are
   listed in the handover note for review instead.
