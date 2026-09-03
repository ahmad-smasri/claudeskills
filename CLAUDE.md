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
| `references/virtual-meters.md` | the virtual metering layer - the tier matrix to ask for, the nine meter classes and their Dar Cairo name segments, the six-row block, the thermal-unit trap, `para:contributionFraction`, and what to do when the calculation engine's telemetry keys do not exist yet | adding virtual meters, or `para:contributionFraction` |
| `references/known-issues.md` | all 30 validator rule codes, 9 source conflicts with the resolution taken, defect inventories for both reference models | a code needs explaining, or the sources disagree |
| `references/data/brick-vocab.txt` | 2,587 Brick 1.4 / REC / ref terms with deprecation and alias status | generated - do not hand-edit |
| `references/data/brick-rec-vocab.txt` | the 193 terms with actual precedent in Dar Cairo | generated |
| `references/data/para-classes.csv` | 242 `para:` classes and their parents | generated |
| `references/data/para-properties.csv` | 20 `para:` properties - 13 `brick:EntityProperty` and the 7 `owl:DatatypeProperty` C&C properties V98 added | generated |
| `references/data/units.csv` | 41 units seen with `brick:hasUnit`, with usage counts | generated |
| `assets/ontology-template.csv` | the empty 27-column header | starting a sheet |
| `assets/example-minimal.csv` | a small complete building that validates clean - copy its shapes | writing any row shape for the first time |
| `scripts/lookup_reference.py` | precedent search over Dar Cairo; Brick 1.4 term check | before inventing any class |
| `scripts/align_naming.py` | retrofits a sheet's identifiers to Dar Cairo's convention - dashed-English datapoints, `_`-segments/`-`-words, no camelCase - keeping the timeseries join keys and writing an old → new crosswalk; one-shot | a sheet built with raw/BMS ids needs Dar-Cairo naming |
| `scripts/validate_ontology.py` | the row-level validator, 30 rule codes | before every handover |
| `scripts/io_list.py` | shared IO-list loader; answers "does this unit have this point" and "what is its key" for all three checkers | changing how an IO list is read |
| `scripts/highlight_findings.py` | writes a copy of a workbook with unresolved findings filled yellow and written into `validator_code` / `validator_finding` columns past the data, for a manual pass | findings need a human |
| `references/data/accepted-terms.txt` | terms that override the generated Brick extract, each with the reason it is there | a real term reads as a typo, or a deliberate alias floods the warnings |
| `scripts/check_io_list.py` | the point cross-check, 5 `-IO-` codes: every point in the sheet must trace back to a row in the IO list, or its timeseries resolves empty | whenever an IO list exists |
| `scripts/check_consistency.py` | the cross-unit checker, 17 `-CON-` codes: compares every unit of a class against its siblings and finds what a row-level read cannot - a missing point, a divergent class, a `#N/A` in an object cell, a child whose separators drifted from its parent's | before every handover, and per family while building |
| `scripts/build_review_workbook.py` | runs both checkers plus eight checks neither covers, then writes the client review workbook - a `START HERE` tab, the ontology sheet with flagged rows filled yellow/orange, one plain-English tab per entity family, and a `Technical detail` tab holding the coded findings. Findings are collapsed to one line per kind of problem and every rule code is rewritten in ordinary English, because the reader is usually not the person who built the sheet. The tabs and the data sheet are cross-linked: clickable row numbers on every tab, and review columns AB-AD past the data naming each flagged row's problem with a link back to its tab | a delivered sheet needs reviewing, or a client asks what is wrong with a draft |
| `scripts/build_vocab.py` | regenerates the para registry and unit list from `reference-models/` | a new reference model lands - drop the file in and rerun, the scripts resolve `DarCairo_V*.csv` by version |
| `scripts/build_brick_vocab.py` | regenerates the Brick term list from `Brick.ttl` | targeting a new Brick release |
| `tests/run_tests.sh` | checks both scripts still catch what they should | after touching either |

### Reference models - `reference-models/`

| File | What it is |
|---|---|
| `DarCairo_V98.csv` | **the primary reference for any ontology we build.** 25,722 rows, 33 columns (V93's 27 plus two more property groups). Site → building → levels → zones → rooms → HVAC, electrical, water systems → equipment → parts → points → timeseries. When in doubt, match Dar Cairo. |
| `QF_SSC_Ontology_ver02.xlsx` | the current SSC sheet (cleaned), 5,082 rows on `SSC_Ontology_Ver0.6`, plus a `Claude Log` tab. This is a delivered previous-project ontology and is step 3 of the class ladder - check it for precedent before minting `para:`. Pick the ontology sheet by its header, never by `.active`. It already coins reusable `para:` classes (`para:Fail_Start_Alarm`, `para:Fail_Stop_Alarm`, `para:Summary_Alarm`, `para:Scheduled_Hrs_Duration`, `para:UnScheduled_Hrs_Duration`) - reuse them rather than re-coining. |
| `QF_HQ_Ontology_draft0.4.xlsx` | the QF HQ draft, 28,929 rows on `HQ_Onotlogy_Draft_v0.4` (note the misspelled tab - pick the sheet by its header, never by name). A third delivered-project ontology and another step-3 precedent alongside SSC. Read for structure, not for units: several rows carry a wrong `brick:hasUnit` (air flow tagged `unit:V`, cooling capacity `unit:HZ`), so Dar Cairo stays the unit authority. |
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
3. Is it in a previous project's ontology? Check the delivered sheets in
   `reference-models/` (`QF_SSC_Ontology_ver02.xlsx` and `QF_HQ_Ontology_draft0.4.xlsx`) - reuse the class a
   prior project already gave the concept, and reuse a `para:` class it already
   coined rather than minting a parallel one.
4. Not anywhere above? Define a `para:` subclass of the closest Brick parent.
5. No sensible parent either? For a **point**, `owl:Class rdfs:subClassOf brick:Point`.
   For **equipment, ask the user which root to use** - never guess, never file
   equipment under `brick:Point`.

Never invent a `brick:` or `rec:` term. Everything the team coins is `para:`, and a
`para:` class a previous project already uses is reused, never re-coined.

**Never use a root class as a catch-all.** `brick:Alarm` is only for a point whose
name or label is literally a general/summary/common alarm; every other alarm (trip,
fail-to-start, overload, …) runs the full ladder and gets its specific class - so
`para:Trip_Alarm`, not a bare `brick:Alarm`. Same for `brick:Sensor`,
`brick:Setpoint`, `brick:Status`, `brick:Command`. See `class-resolution.md`.

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
- **Misspellings are a separate question from shape, asked separately at
  intake**, because a source name is also the label a user reads. Default to
  keeping and reporting. When the answer is to correct: only where a sibling row
  proves the correction, whole tokens only, on the name segment and never on an
  asset tag or a database key, from one map in the build script so identifier
  and label cannot drift, and listed in the handover note with the crosswalk
  regenerated. On QNL the shape was kept and 35 room names corrected.
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
- **Datapoints are named in dashed English, the Dar Cairo way** - `_Trip-Status`,
  `_Room-Air-Temperature-Setpoint`, never the BMS token `_TripAlm`/`_RmTempSP`.
  Take the name from the point's `rdfs:label_en` when it is clean English, else
  from its Brick/para class (`brick:Run_Status` → `Run-Status`); no camelCase, no
  dots. A part of a part extends the parent segment with `-` (`_SF-Motor`); a
  point opens a new `_` segment. Name ids this way as they are emitted. When a
  client asks to normalise to Dar Cairo, or a sheet was already built with
  raw/BMS ids, `scripts/align_naming.py` retrofits the whole sheet in one pass -
  a bijection over both identifier columns that keeps `ref:hasTimeseriesId` /
  `para:hasEntityId` untouched and writes an old → new crosswalk. QNL was
  normalised this way (`QNL_AHU_B_001_AvgSpcHumd_PV` →
  `QNL_AHU-B-001_Average-Space-Humidity`, camelCase 71% → 0%; rooms/levels kept).

**Labels.** Two styles; ask at intake, because neither reference model settles it.
`verbatim` is the source text with underscores read as word breaks and every
other mark left alone - the QF SSC house style, whose room shape is
`<level>.<number> <name>`: `1.001 CORRIDOR`, `B.063 PLANT ROOM 01`. `para`
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

**A virtual meter exists only where a physical one does not** - it fills the gaps
in the metering the building has, so a virtual meter beside a real one is a second
answer with no data behind it. List the meters the sheet already carries and what
each measures before generating a tier, and suppress every pair a physical meter
covers. Expect to need a hand-written list: physical meters routinely carry no
`brick:meters` row, so the graph cannot answer the question.

**Virtual meters are asked for, never assumed** - `references/virtual-meters.md`.
Which tiers (Building, Floor, Room) and which meter types at each is the client's
decision, put to them as a matrix; the count then follows as arithmetic, so say
the total back before building. `para:Utility_Meter` is building-tier only - it
measures the incoming municipal supply - while Electrical Meters sum across UPS,
panels and generator and belong at any tier. Thermal meter points take
`para:KiloWt` / `para:KiloWt-HR`, never `unit:KiloW`, or a demand rollup adds
chilled-water kW to electrical kW. **Their points are calculated, so the IO-list
rule below does not reach them** - the keys come from the calculation engine's
register, and where that does not exist the points ship with no reference row and
a pending file, never a blank one.

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

**Equipment with no location is placed at the building, not left bare.** Write
`rec:locatedIn` the building and `brick:isPartOf` its system - both are known even
when the room is not - and still no `rec:feeds`, because the served space is the
part nobody knows. Standalone equipment only: a part inherits its parent's
location, and Dar Cairo locates just 19 of its 801 parts separately.

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

# retrofit a sheet's identifiers to Dar Cairo's convention (one-shot)
python3 skills/building-ontology/scripts/align_naming.py --in MyBuilding.xlsx

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

# add the virtual metering layer to a building (worked example)
python3 projects/QNL/add_virtual_meters.py --dry-run

# hand the remaining findings to a human, in the sheet itself
python3 skills/building-ontology/scripts/highlight_findings.py In.xlsx \
    --out Reviewed.xlsx --label-style verbatim --severity ERROR

# the full review workbook - grouped issue sheets plus highlighted source rows
python3 skills/building-ontology/scripts/build_review_workbook.py MyBuilding.xlsx \
    --out MyBuilding_review_1.xlsx --label-style verbatim

# force a grouping when the derived one splits a family you want read as one
python3 skills/building-ontology/scripts/build_review_workbook.py MyBuilding.xlsx \
    --out R.xlsx --group 'AHU=^entity:HQ_AHU' --group 'ExhaustFan=^entity:HQ_(CEF|GEF|TEF)'

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
